from dataclasses import dataclass
import time

import numpy as np
import sounddevice as sd

from PyQt5 import QtCore, QtWidgets

from stim_math import hardware_calibration, point_calibration, generate, amplitude_modulation, trig, limits
from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from stim_math.sine_generator import SineGenerator1D, AngleGenerator

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


class AudioGenerationWidget(QtWidgets.QWidget):
    def __init__(self, parent, threephase_parameters: ThreephaseParameterManager):
        QtWidgets.QWidget.__init__(self, parent)
        self.threephase_parameters = threephase_parameters

        self.sample_rate = 44100
        self.frame_number = 0
        self.audio_latency = 0

        self.stream = None

        self.carrier_angle = AngleGenerator()
        self.modulation_1_angle = AngleGenerator()
        self.modulation_2_angle = AngleGenerator()

        self.offset = 0
        self.last_dac_time = 0

    def start(self, host_api_name, audio_device_name, latency):
        try:
            device_index = sd.default.device[1]
            for device in sd.query_devices():
                if sd.query_hostapis(device['hostapi'])['name'] == host_api_name:
                    if device['name'] == audio_device_name:
                        device_index = device['index']

            samplerate = sd.query_devices(device_index)['default_samplerate']
            print('start audio:', host_api_name, audio_device_name, latency, samplerate)
            self.sample_rate = int(samplerate)
            self.stream = sd.OutputStream(
                samplerate=samplerate,
                device=device_index,
                channels=2,
                dtype=np.int16,
                callback=self.callback,
                latency=latency,
            )
            self.stream.start()
        except Exception as e:
            self.stream = None
            import traceback
            traceback.print_exception(e)

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = None

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

        alpha = self.threephase_parameters.alpha.interpolate(command_timeline)
        beta = self.threephase_parameters.beta.interpolate(command_timeline)

        # normalize (alpha, beta) to be within the unit circle.
        norm = np.clip(trig.norm(alpha, beta), 1.0, None)
        alpha /= norm
        beta /= norm

        # modulation 1
        modulation_1 = None
        if self.threephase_parameters.modulation_1_enabled.last_value():
            frequency = self.threephase_parameters.modulation_1_frequency.last_value()
            frequency = np.clip(frequency, limits.ModulationFrequency.min, limits.ModulationFrequency.max)
            theta = self.modulation_1_angle.generate(len(timeline), frequency, self.sample_rate)
            # safety: every modulation cycle must have at least 3 cycles 'on' and 'off'
            maximum_on_off_time = np.clip(1 - 3 / (self.threephase_parameters.carrier_frequency.last_value() / frequency), 0, None)
            modulation_1 = amplitude_modulation.SineModulation(
                theta,
                self.threephase_parameters.modulation_1_strength.last_value(),
                self.threephase_parameters.modulation_1_left_right_bias.last_value(),
                np.clip(self.threephase_parameters.modulation_1_high_low_bias.last_value(), -maximum_on_off_time, maximum_on_off_time)
            )

        # modulation 2
        modulation_2 = None
        if self.threephase_parameters.modulation_2_enabled.last_value():
            frequency = self.threephase_parameters.modulation_2_frequency.last_value()
            frequency = np.clip(frequency, limits.ModulationFrequency.min, limits.ModulationFrequency.max)
            theta = self.modulation_2_angle.generate(len(timeline), frequency, self.sample_rate)
            # safety: every modulation cycle must have at least 3 cycles 'on' or 'off'
            maximum_on_off_time = np.clip(1 - 3 / (self.threephase_parameters.carrier_frequency.last_value() / frequency), 0, None)
            modulation_2 = amplitude_modulation.SineModulation(
                theta,
                self.threephase_parameters.modulation_2_strength.last_value(),
                self.threephase_parameters.modulation_2_left_right_bias.last_value(),
                np.clip(self.threephase_parameters.modulation_2_high_low_bias.last_value(), -maximum_on_off_time, maximum_on_off_time)
            )

        # center scaling
        center_calib = point_calibration.CenterCalibration(self.threephase_parameters.calibration_center.last_value())

        # hardware calibration
        hw = hardware_calibration.HardwareCalibration(self.threephase_parameters.calibration_neutral.last_value(),
                                                      self.threephase_parameters.calibration_right.last_value())

        frequency = self.threephase_parameters.carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Carrier.min, limits.Carrier.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, self.sample_rate)
        L, R = generate.generate_audio(alpha, beta, theta_carrier,
                                       modulation_1=modulation_1,
                                       modulation_2=modulation_2,
                                       point_calibration=center_calib,
                                       hardware_calibration=hw)

        volume = \
            np.clip(self.threephase_parameters.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.threephase_parameters.volume.last_value(), 0, 1)
        L *= volume
        R *= volume
        return L, R
