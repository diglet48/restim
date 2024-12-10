from abc import ABC

import numpy as np

from stim_math import threephase
from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from stim_math.audio_gen.various import VibrationAlgorithm, ThreePhasePosition
from stim_math.axis import AbstractMediaSync
from stim_math.sine_generator import AngleGenerator

from stim_math.audio_gen.params import *


class MultiPhaseAlgorithm(AudioGenerationAlgorithm, ABC):
    def __init__(self):
        super(MultiPhaseAlgorithm, self).__init__()


class ThreePhaseAlgorithm(AudioGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, params: ThreephaseContinuousAlgorithmParams, safety_limits: SafetyParams):
        super().__init__()
        self.media = media
        self.params = params
        self.vibration = VibrationAlgorithm(params.vibration_1, params.vibration_2)
        self.position = ThreePhasePosition(params.position, params.transform)
        self.safety_limits = safety_limits

        self.carrier_angle = AngleGenerator()

    def channel_count(self) -> int:
        return 2

    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        volume = \
            np.clip(self.params.volume.master.last_value(), 0, 1) * \
            np.clip(self.params.volume.api.interpolate(system_time_estimate), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)
        volume *= self.vibration.generate_vibration_signal(system_time_estimate[0], samplerate, len(steady_clock))
        if not self.media.is_playing():
            volume *= 0

        frequency = self.params.carrier_frequency.interpolate(system_time_estimate[0])
        frequency = np.clip(frequency,
                            self.safety_limits.minimum_carrier_frequency,
                            self.safety_limits.maximum_carrier_frequency)
        theta_carrier = self.carrier_angle.generate(len(steady_clock), frequency, samplerate)

        alpha, beta = self.position.get_position(system_time_estimate)

        # center scaling
        center_calib = threephase.ThreePhaseCenterCalibration(self.params.calibrate.center.last_value())
        volume *= center_calib.get_scale(alpha, beta)

        # exponent transform
        # transform = ThreePhaseExponentAdjustment(self.params.threephase_exponent.last_value())
        # volume *= transform.get_scale(alpha, beta)

        # hardware calibration
        hw = threephase.ThreePhaseHardwareCalibration(self.params.calibrate.neutral.last_value(),
                                                      self.params.calibrate.right.last_value())

        tp = threephase.ThreePhaseSignalGenerator()
        L, R = tp.generate(theta_carrier, alpha, beta)
        L, R = hw.apply_transform(L, R)

        L *= volume
        R *= volume
        return L, R
