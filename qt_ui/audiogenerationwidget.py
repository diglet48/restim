from dataclasses import dataclass
import time

import numpy as np
import pyaudio
from qt_ui.stim_config import ModulationParameters, TransformParameters, CalibrationParameters, PositionParameters

from PyQt5 import QtCore, QtWidgets

from stim_math import hardware_calibration, point_calibration, generate, amplitude_modulation, trig


@dataclass
class AudioDevice:
    device_index: int
    device_name: str
    is_default: bool


def audio_to_bytes(L, R):
    data = np.vstack((L, R)).transpose()
    data = np.clip(data * 2 ** 15, -32768, 32767).astype(np.int16)
    return data.tobytes()


class ContinuousParameter:
    def __init__(self, init_value):
        self.data = np.array([[0, init_value]])

    def add(self, value):
        ts = time.time()
        self.data = np.vstack((self.data, [ts, value]))

        # regularly cleanup stale data
        if self.data.shape[0] > 100 and self.data[0][0] < (time.time() - 10):
            cutoff = time.time() - 2
            self.data = self.data[self.data[:, 0] > cutoff]

    def interpolate(self, timeline):
        return np.interp(timeline, self.data[:, 0], self.data[:, 1])


class AudioGenerationWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.p = pyaudio.PyAudio()
        self.sample_rate = 44100
        self.frame_number = 0
        self.audio_latency = 0

        self.preferred_host_api = self.p.get_default_host_api_info()['index']
        # prefer windows directsound
        for i in range(self.p.get_host_api_count()):
            if self.p.get_host_api_info_by_index(i)['name'].lower() == 'windows directsound':
                self.preferred_host_api = i
        self.device_index = self.p.get_host_api_info_by_index(self.preferred_host_api)['defaultOutputDevice']

        self.stream = None

        self.modulation_parameters: ModulationParameters = None
        self.calibration_parameters: CalibrationParameters = None
        self.transform_parameters: TransformParameters = None
        self.position_parameters: PositionParameters = PositionParameters(0, 0)

        self.alpha = ContinuousParameter(0)
        self.beta = ContinuousParameter(0)

        self.offset = 0
        self.last_dac_time = 0

    def start(self):
        self.stream = self.p.open(
            format=self.p.get_format_from_width(2),
            channels=2,
            rate=self.sample_rate,
            output=True,
            stream_callback=self.callback,
            frames_per_buffer=1000,  # 1000 ~= 20ms
            output_device_index=self.device_index,
        )

    def stop(self):
        if self.stream is not None:
            self.stream.close()
        self.stream = None

    def list_devices(self):
        devices = []
        default_index = self.p.get_host_api_info_by_index(self.preferred_host_api)['defaultOutputDevice']
        for device_index in range(self.p.get_device_count()):
            device = self.p.get_device_info_by_index(device_index)
            if device['hostApi'] != self.preferred_host_api:
                continue
            if device['maxOutputChannels'] == 0:
                continue
            devices.append(
                AudioDevice(device['index'], device['name'], device['index'] == default_index)
            )
        return devices

    def select_device_index(self, index):
        self.device_index = index

    def list_host_api(self):
        for api_index in range(self.p.get_host_api_count()):
            api = self.p.get_host_api_info_by_index(api_index)
            print(api)

    def callback(self, in_data, frame_count, time_info, status):
        timeline = np.linspace(self.frame_number / self.sample_rate,
                               (self.frame_number + frame_count) / self.sample_rate,
                               frame_count, endpoint=False)
        self.frame_number += frame_count

        new_audio_latency = time_info['output_buffer_dac_time'] - time_info['current_time']
        self.audio_latency += 0.2 * (new_audio_latency - self.audio_latency)

        L, R = self.generate_audio(timeline, time_info['output_buffer_dac_time'])
        return audio_to_bytes(L, R), pyaudio.paContinue

    def updatePositionParameters(self, position_params: PositionParameters):
        self.updateAlpha(position_params.alpha)
        self.updateBeta(position_params.beta)

    def updateAlpha(self, value):
        self.alpha.add(value)

    def updateBeta(self, value):
        self.beta.add(value)

    def updateCalibrationParameters(self, calibration_params: CalibrationParameters):
        self.calibration_parameters = calibration_params

    def updateModulationParameters(self, modulation_params: ModulationParameters):
        self.modulation_parameters = modulation_params

    def updateTransformParameters(self, transform_parameters: TransformParameters):
        self.transform_parameters = transform_parameters

    def generate_audio(self, timeline, dac_time):
        latency = 0.04
        system_time = time.time()
        offset = system_time - timeline[-1] - latency

        if abs(self.offset - offset) > 1:
            self.offset = offset
        else:
            self.offset = self.offset + 0.01 * (offset - self.offset)

        # synchronize the frame counter to the system time
        command_timeline = timeline + self.offset

        # newest_data_ts = self.alpha.data[-1][0]
        # newest_cmd_ts = command_timeline[-1]
        # print('ahead by:', newest_data_ts - newest_cmd_ts)

        x = self.alpha.interpolate(command_timeline)
        y = self.beta.interpolate(command_timeline)

        # TODO: volume control

        frequency = self.modulation_parameters.carrier_frequency
        # safety: clamp the carrier frequency
        frequency = np.clip(frequency, 400.0, 1000.0)

        # normalize (x, y) to be within the unit circle.
        norm = np.clip(trig.norm(x, y), 1.0, None)
        x /= norm
        y /= norm

        point_calib = point_calibration.ThirteenPointCalibration([
            self.calibration_parameters.edge_0_3pi,
            self.calibration_parameters.edge_1_3pi,
            self.calibration_parameters.edge_2_3pi,
            self.calibration_parameters.edge_3_3pi,
            self.calibration_parameters.edge_4_3pi,
            self.calibration_parameters.edge_5_3pi,
            self.calibration_parameters.mid_0_3pi,
            self.calibration_parameters.mid_1_3pi,
            self.calibration_parameters.mid_2_3pi,
            self.calibration_parameters.mid_3_3pi,
            self.calibration_parameters.mid_4_3pi,
            self.calibration_parameters.mid_5_3pi,
            self.calibration_parameters.center,
        ])

        # modulation 1
        modulation_1 = None
        if self.modulation_parameters.modulation_1_enabled:
            modulation_1 = amplitude_modulation.SineModulation(
                self.modulation_parameters.modulation_1_freq,
                self.modulation_parameters.modulation_1_modulation)

        # modulation 2
        modulation_2 = None
        if self.modulation_parameters.modulation_2_enabled:
            modulation_2 = amplitude_modulation.SineModulation(
                self.modulation_parameters.modulation_2_freq,
                self.modulation_parameters.modulation_2_modulation)

        # center scaling
        center_calib = point_calibration.CenterCalibration(self.transform_parameters.center)

        # hardware calibration
        hw = hardware_calibration.HardwareCalibration(self.transform_parameters.up_down,
                                                      self.transform_parameters.left_right)

        L, R = generate.generate_audio(timeline, x, y, frequency,
                                       modulation_1=modulation_1,
                                       modulation_2=modulation_2,
                                       point_calibration=point_calib,
                                       point_calibration_2=center_calib,
                                       hardware_calibration=hw)
        return L, R
