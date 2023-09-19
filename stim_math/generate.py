from PyQt5.QtCore import QSettings

import numpy as np

from stim_math import amplitude_modulation, limits, trig, point_calibration, threephase, fourphase, fivephase
from stim_math.sine_generator import AngleGenerator, AngleGeneratorWithVaryingIPI
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform
from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from qt_ui.preferencesdialog import KEY_AUDIO_CHANNEL_COUNT, KEY_AUDIO_CHANNEL_MAP



def generate_audio(alpha, beta, theta_carrier,
                   point_calibration=None,
                   point_calibration_2=None,
                   modulation_1=None,
                   modulation_2=None,
                   hardware_calibration=None):
    # TODO: normalize norm(alpha, beta) <= 1

    L, R = threephase.ThreePhaseSignalGenerator.generate(theta_carrier, alpha, beta)

    volume = 1
    if point_calibration is not None:
        volume *= point_calibration.get_scale(alpha, beta)
    if point_calibration_2 is not None:
        volume *= point_calibration_2.get_scale(alpha, beta)
    L *= volume
    R *= volume

    if modulation_1 is not None:
        L, R = modulation_1.modulate(L, R)
    if modulation_2 is not None:
        L, R = modulation_2.modulate(L, R)

    if hardware_calibration is not None:
        L, R = hardware_calibration.apply_transform(L, R)

    return L, R


class VolumeManagementAlgorithm:
    def __init__(self, params: ThreephaseParameterManager):
        super(VolumeManagementAlgorithm, self).__init__()
        self.params = params

        self.modulation_1_angle = AngleGeneratorWithVaryingIPI()
        self.modulation_2_angle = AngleGeneratorWithVaryingIPI()

    def generate_modulation_signal(self, samplerate, timeline: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)

        volume *= self.calculate_modulation(
            samplerate, timeline,
            self.params.modulation_1_enabled.last_value(),
            self.params.modulation_1_frequency.last_value(),
            self.params.modulation_1_strength.last_value(),
            self.params.modulation_1_left_right_bias.last_value(),
            self.params.modulation_1_high_low_bias.last_value(),
            self.params.modulation_1_random.last_value(),
            self.modulation_1_angle,
        )

        volume *= self.calculate_modulation(
            samplerate, timeline,
            self.params.modulation_2_enabled.last_value(),
            self.params.modulation_2_frequency.last_value(),
            self.params.modulation_2_strength.last_value(),
            self.params.modulation_2_left_right_bias.last_value(),
            self.params.modulation_2_high_low_bias.last_value(),
            self.params.modulation_2_random.last_value(),
            self.modulation_2_angle
        )

        return volume

    def calculate_modulation(self, samplerate, timeline, is_enabled,
                             modulation_frequency, modulation_strength,
                             modulation_left_right_bias, modulation_high_low_bias,
                             modulation_random,
                             angle_generator):
        if not is_enabled or modulation_frequency == 0:
            return 1

        modulation_frequency = np.clip(modulation_frequency,
                                       limits.ModulationFrequency.min,
                                       limits.ModulationFrequency.max)
        theta = angle_generator.generate(len(timeline), modulation_frequency, samplerate, modulation_random)
        # safety: every modulation cycle must have at least X cycles 'on' and 'off'
        maximum_on_off_time = np.clip(1 - limits.minimum_amplitude_modulation_feature_length /
                                      (self.params.carrier_frequency.last_value() / modulation_frequency), 0, None)
        modulation = amplitude_modulation.SineModulation(
            theta,
            modulation_strength,
            modulation_left_right_bias,
            np.clip(modulation_high_low_bias, -maximum_on_off_time, maximum_on_off_time)
        )
        return modulation.get_modulation_signal()


class MultiPhaseAlgorithm:
    def __init__(self):
        settings = QSettings()
        self.channel_count = settings.value(KEY_AUDIO_CHANNEL_COUNT, 8, int)
        try:
            map = settings.value(KEY_AUDIO_CHANNEL_MAP, '0, 1, 2, 3', str)
            self.channel_map = [int(x) for x in map.split(',')]
        except ValueError:
            self.channel_map = [0, 1, 2, 3]


class ThreePhaseAlgorithm(VolumeManagementAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)

        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [2]

    def channel_mapping(self, channel_count):
        return [0, 1]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = self.generate_modulation_signal(samplerate, timeline)

        frequency = self.params.carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Carrier.min, limits.Carrier.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        alpha = self.params.alpha.interpolate(command_timeline)
        beta = self.params.beta.interpolate(command_timeline)

        # normalize (alpha, beta) to be within the unit circle.
        norm = np.clip(trig.norm(alpha, beta), 1.0, None)
        alpha /= norm
        beta /= norm

        # # mobius transform...
        # z = alpha + beta * 1j
        # a = self.params.focus_alpha.last_value() + self.params.focus_beta.last_value() * 1j
        # z = (z - a) / (1 - np.conj(a) * z)
        # alpha = z.real
        # beta = z.imag

        if self.params.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.params.transform_rotation_degrees.last_value(),
                self.params.transform_mirror.last_value(),
                self.params.transform_top_limit.last_value(),
                self.params.transform_bottom_limit.last_value(),
                self.params.transform_left_limit.last_value(),
                self.params.transform_right_limit.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm

        # center scaling
        center_calib = point_calibration.CenterCalibration(self.params.calibration_center.last_value())
        volume *= center_calib.get_scale(alpha, beta)

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibration_neutral.last_value(),
                                                      self.params.calibration_right.last_value())

        tp = threephase.ThreePhaseSignalGenerator()
        L, R = tp.generate(theta_carrier, alpha, beta)
        L, R = hw.apply_transform(L, R)
        L *= volume
        R *= volume
        return L, R


class FourPhaseAlgorithm(VolumeManagementAlgorithm, MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)

        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [3, 4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:3]
        # return [0, 1, 2]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = self.generate_modulation_signal(samplerate, timeline)

        frequency = self.params.carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Carrier.min, limits.Carrier.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        e1 = self.params.e1.interpolate(command_timeline)
        e2 = self.params.e2.interpolate(command_timeline)
        e3 = self.params.e3.interpolate(command_timeline)
        e4 = self.params.e4.interpolate(command_timeline)
        fp = fourphase.FourPhaseSignalGenerator()
        a, b, c, d = fp.generate_from_electrode_amplitudes(theta_carrier, e1, e2, e3, e4)
        fpc = fourphase.FourPhaseHardwareCalibration(
            self.params.resistance_t.last_value(),
            self.params.resistance_s1.last_value(),
            self.params.resistance_s2.last_value(),
            self.params.resistance_s3.last_value(),
            self.params.resistance_s4.last_value(),
        )
        c1, c2, c3 = fpc.transform(a, b, c, d)
        c1 *= volume
        c2 *= volume
        c3 *= volume
        return c1, c2, c3


class FivePhaseAlgorithm(VolumeManagementAlgorithm, MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__(params)

        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:4]
        # return [0, 1, 6, 7]

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = self.generate_modulation_signal(samplerate, timeline)

        frequency = self.params.carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Carrier.min, limits.Carrier.max)
        theta_carrier = self.carrier_angle.generate(len(timeline), frequency, samplerate)

        e1 = self.params.e1.interpolate(command_timeline)
        e2 = self.params.e2.interpolate(command_timeline)
        e3 = self.params.e3.interpolate(command_timeline)
        e4 = self.params.e4.interpolate(command_timeline)
        e5 = self.params.e5.interpolate(command_timeline)
        fp = fivephase.FivePhaseSignalGenerator()
        a, b, c, d, e = fp.generate_from_electrode_amplitudes(theta_carrier, e1, e2, e3, e4, e5)
        fpc = fivephase.FivePhaseHardwareCalibration(
            self.params.resistance_t.last_value(),
            self.params.resistance_s1.last_value(),
            self.params.resistance_s2.last_value(),
            self.params.resistance_s3.last_value(),
            self.params.resistance_s4.last_value(),
            self.params.resistance_s5.last_value(),
        )

        c1, c2, c3, c4 = fpc.transform(a, b, c, d, e)
        c1 *= volume
        c2 *= volume
        c3 *= volume
        c4 *= volume
        return c1, c2, c3, c4





