from dataclasses import dataclass
import time

import numpy as np
import sounddevice as sd
from qt_ui.stim_config import ModulationParameters, TransformParameters, CalibrationParameters, PositionParameters

from PyQt5 import QtCore, QtWidgets

from stim_math import hardware_calibration, point_calibration, generate, amplitude_modulation, trig


MME = 'MME'
DIRECTSOUND = 'Windows DirectSound'
ASIO = 'ASIO'
WASAPI = 'Windows WASAPI'
WDMKS = 'Windows WDM-KS'


# MME and directsound with high latency seems most stable.
# wdm-ks 'low' has lowest latency
PREFERRED_HOST_API = DIRECTSOUND
PREFERRED_LATENCY = 'high'     # 'low', 'high' or a float

TCODE_LATENCY = 0.04  # delay tcode command. Worst-case command interval from multifunplayer

# measured latency on my machine, excluding tcode latency
# wdm-ks,
# latency='low'     50ms      frames: 441 or 7
# latency='high'   100ms      frames: 1764 or 28
# latency=0.1, 160-180ms
# wasapi:
# latency='low'  70-90ms      frames: 448
# latency='high' 220-240ms    frames: 448
# mme:
# latency='low'    130ms      frames: 576
# latency='high' 220-240ms    frames: 1136


@dataclass
class AudioDevice:
    device_index: int
    device_name: str
    is_default: bool


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

        self.sample_rate = 44100
        self.frame_number = 0
        self.audio_latency = 0

        self.preferred_host_api = sd.default.hostapi
        self.device_index = sd.default.device[1]
        for i, hostapi in enumerate(sd.query_hostapis()):
            if hostapi['name'] == PREFERRED_HOST_API:
                self.preferred_host_api = i
                self.device_index = hostapi['default_output_device']

        self.stream = None

        self.modulation_parameters: ModulationParameters = None
        self.calibration_parameters: CalibrationParameters = None
        self.transform_parameters: TransformParameters = None
        self.position_parameters: PositionParameters = PositionParameters(0, 0)

        self.alpha = ContinuousParameter(0)
        self.beta = ContinuousParameter(0)
        self.volume = None

        self.offset = 0
        self.last_dac_time = 0

    def start(self):
        try:
            samplerate = sd.query_devices(self.device_index)['default_samplerate']
            self.sample_rate = int(samplerate)
            self.stream = sd.OutputStream(
                samplerate=samplerate,
                device=self.device_index,
                channels=2,
                dtype=np.int16,
                callback=self.callback,
                latency=PREFERRED_LATENCY
            )
            self.stream.start()
        except Exception as e:
            import traceback
            traceback.print_exception(e)

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = None

    def list_devices(self):
        devices = []
        default_index = self.device_index
        for device in sd.query_devices():
            if device['hostapi'] != self.preferred_host_api:
                continue
            if device['max_output_channels'] <= 1:
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

    def callback(self, outdata: np.ndarray, frames: int, time, status: sd.CallbackFlags):
        outdata.fill(0)
        current_time = time.currentTime
        output_dac_time = time.outputBufferDacTime

        timeline = np.linspace(self.frame_number / self.sample_rate,
                               (self.frame_number + frames) / self.sample_rate,
                               frames, endpoint=False)
        self.frame_number += frames
        new_audio_latency = output_dac_time - current_time
        self.audio_latency += 0.2 * (new_audio_latency - self.audio_latency)

        L, R = self.generate_audio(timeline, output_dac_time)
        outdata[:, 0] = np.clip(L * 2 ** 15, -32768, 32767).astype(np.int16)
        outdata[:, 1] = np.clip(R * 2 ** 15, -32768, 32767).astype(np.int16)

    def updatePositionParameters(self, position_params: PositionParameters):
        self.updateAlpha(position_params.alpha)
        self.updateBeta(position_params.beta)

    def updateAlpha(self, value):
        self.alpha.add(value)

    def updateBeta(self, value):
        self.beta.add(value)

    def updateGuiVolume(self, volume):
        self.volume = np.clip(volume, 0, 1)

    def updateCalibrationParameters(self, calibration_params: CalibrationParameters):
        self.calibration_parameters = calibration_params

    def updateModulationParameters(self, modulation_params: ModulationParameters):
        self.modulation_parameters = modulation_params

    def updateTransformParameters(self, transform_parameters: TransformParameters):
        self.transform_parameters = transform_parameters

    def generate_audio(self, timeline, dac_time):
        system_time = time.time()
        offset = system_time - timeline[-1] - TCODE_LATENCY

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
        frequency = np.clip(frequency, 400.0, 1500.0)

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
        L *= self.volume
        R *= self.volume
        return L, R
