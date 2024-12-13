import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import SafetyParams, FOCStimParams
from stim_math.audio_gen.various import ThreePhasePosition
from stim_math.axis import AbstractMediaSync

FOC_MIN_FREQUENCY = 500
FOC_MAX_FREQUENCY = 1000


class FOCStimAlgorithm(RemoteGenerationAlgorithm):
    def __init__(self, media: AbstractMediaSync, params: FOCStimParams, safety_limits: SafetyParams):
        super().__init__()
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self.position_params = ThreePhasePosition(params.position, params.transform)

    def parameter_dict(self) -> dict:
        def remap(value, min_value, max_value):
            p = (value - min_value) / (max_value - min_value)
            return np.clip(p, 0, 1)

        t = time.time()

        volume = \
            np.clip(self.params.volume.master.last_value(), 0, 1) * \
            np.clip(self.params.volume.api.interpolate(t), 0, 1) * \
            np.clip(self.params.volume.inactivity.last_value(), 0, 1) * \
            np.clip(self.params.volume.external.last_value(), 0, 1)

        maximum_frequency = np.clip(FOC_MAX_FREQUENCY,
                                    self.safety_limits.minimum_carrier_frequency,
                                    self.safety_limits.maximum_carrier_frequency)
        minimum_frequency = np.clip(FOC_MIN_FREQUENCY,
                                    self.safety_limits.minimum_carrier_frequency,
                                    self.safety_limits.maximum_carrier_frequency)
        tau = self.params.tau.last_value() * 1e-6

        carrier_frequency = self.params.carrier_frequency.interpolate(t)
        carrier_frequency = np.clip(carrier_frequency, minimum_frequency, maximum_frequency)
        derating = self.frequency_derating_factor(maximum_frequency, carrier_frequency, tau)
        volume *= np.clip(derating, 0, 1)

        alpha, beta = self.position_params.get_position(t)

        return {
            'L0': remap(alpha, -1, 1),
            'L1': remap(beta, -1, 1),
            'V0': remap(volume, 0, 1),
            'A0': remap(self.params.carrier_frequency.interpolate(t), FOC_MIN_FREQUENCY, FOC_MAX_FREQUENCY),
            'A1': remap(self.params.pulse_frequency.interpolate(t), 1, 100),
            'A2': remap(self.params.pulse_width.interpolate(t), 3, 20),
            'A3': remap(self.params.pulse_rise_time.interpolate(t), 2, 10),
            'A4': remap(self.params.pulse_interval_random.interpolate(t), 0, 1),
            'C0': remap(self.params.calibrate.center.interpolate(t), -10, 10),
            'C1': remap(self.params.calibrate.neutral.interpolate(t), -10, 10),
            'C2': remap(self.params.calibrate.right.interpolate(t), -10, 10),
        }

    def frequency_derating_factor(self, max_frequency, frequency, tau):
        """
        :param max_frequency:   carrier frequency at which derating = 1 (i.e. no derating)
        :param frequency:       carrier frequency of the pulse
        :param tau:             time constant of the nerves, ~355e-6
        :return:                volume of the pulse, such that it has equal subjective intensity as a pulse at max carrier frequency.
        """
        # this formula follows from Qt = Q0 * (1 + pw/tau)
        return (frequency * tau + 0.5) / (max_frequency * tau + 0.5)
