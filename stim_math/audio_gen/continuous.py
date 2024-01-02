from abc import ABC

import numpy as np
from PyQt5.QtCore import QSettings

import stim_math.threephase
from qt_ui.preferencesdialog import KEY_AUDIO_CHANNEL_COUNT, KEY_AUDIO_CHANNEL_MAP
from stim_math import limits, threephase, fourphase, fivephase
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from stim_math.audio_gen.various import VibrationAlgorithm, ThreePhasePositionParameters
from stim_math.sine_generator import AngleGenerator
from stim_math.threephase_exponent import ThreePhaseExponentAdjustment
from stim_math.threephase_parameter_manager import ThreephaseParameterManager


class MultiPhaseAlgorithm(AudioGenerationAlgorithm, ABC):
    def __init__(self):
        super(MultiPhaseAlgorithm, self).__init__()
        settings = QSettings()
        self.channel_count = settings.value(KEY_AUDIO_CHANNEL_COUNT, 8, int)
        try:
            map = settings.value(KEY_AUDIO_CHANNEL_MAP, '0, 1, 2, 3', str)
            self.channel_map = [int(x) for x in map.split(',')]
        except ValueError:
            self.channel_map = [0, 1, 2, 3]


class ThreePhaseAlgorithm(AudioGenerationAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__()
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()
        self.position_params = ThreePhasePositionParameters(params)

    def preferred_channel_count(self):
        return [2]

    def channel_mapping(self, channel_count):
        return [0, 1]

    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(steady_clock))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312CarrierFrequency.min, limits.Mk312CarrierFrequency.max)
        theta_carrier = self.carrier_angle.generate(len(steady_clock), frequency, samplerate)

        alpha, beta = self.position_params.get_position(system_time_estimate)

        # center scaling
        center_calib = stim_math.threephase.ThreePhaseCenterCalibration(self.params.calibration_center.last_value())
        volume *= center_calib.get_scale(alpha, beta)

        # exponent transform
        transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        volume *= transform.get_scale(alpha, beta)

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibration_neutral.last_value(),
                                                      self.params.calibration_right.last_value())

        tp = threephase.ThreePhaseSignalGenerator()
        L, R = tp.generate(theta_carrier, alpha, beta)
        L, R = hw.apply_transform(L, R)
        L *= volume
        R *= volume
        return L, R


class FourPhaseAlgorithm(MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__()
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [3, 4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:3]
        # return [0, 1, 2]

    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(steady_clock))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312CarrierFrequency.min, limits.Mk312CarrierFrequency.max)
        theta_carrier = self.carrier_angle.generate(len(steady_clock), frequency, samplerate)

        e1 = self.params.e1.interpolate(system_time_estimate)
        e2 = self.params.e2.interpolate(system_time_estimate)
        e3 = self.params.e3.interpolate(system_time_estimate)
        e4 = self.params.e4.interpolate(system_time_estimate)
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


class FivePhaseAlgorithm(MultiPhaseAlgorithm):
    def __init__(self, params: ThreephaseParameterManager):
        super().__init__()
        self.params = params
        self.vibration = VibrationAlgorithm(params)
        self.carrier_angle = AngleGenerator()

    def preferred_channel_count(self):
        return [self.channel_count]
        # return [4, 6, 8]

    def channel_mapping(self, channel_count):
        return self.channel_map[:4]
        # return [0, 1, 6, 7]

    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        volume = \
            np.clip(self.params.ramp_volume.last_value(), 0, 1) * \
            np.clip(self.params.volume.last_value(), 0, 1) * \
            np.clip(self.params.inactivity_volume.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(samplerate, len(steady_clock))

        frequency = self.params.mk312_carrier_frequency.last_value()
        frequency = np.clip(frequency, limits.Mk312CarrierFrequency.min, limits.Mk312CarrierFrequency.max)
        theta_carrier = self.carrier_angle.generate(len(steady_clock), frequency, samplerate)

        e1 = self.params.e1.interpolate(system_time_estimate)
        e2 = self.params.e2.interpolate(system_time_estimate)
        e3 = self.params.e3.interpolate(system_time_estimate)
        e4 = self.params.e4.interpolate(system_time_estimate)
        e5 = self.params.e5.interpolate(system_time_estimate)
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
