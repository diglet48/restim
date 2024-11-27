import time

import numpy as np

from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm
from stim_math.audio_gen.params import SafetyParams, FOCStimParams
from stim_math.audio_gen.various import ThreePhasePosition
from stim_math.axis import AbstractMediaSync


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
            np.clip(self.params.volume.inactivity.last_value(), 0, 1)

        alpha, beta = self.position_params.get_position(t)

        return {
            'L0': remap(alpha, -1, 1),
            'L1': remap(beta, -1, 1),
            'V0': remap(volume, 0, 1),
            'A0': remap(self.params.carrier_frequency.interpolate(t), 500, 1000),
            'A1': remap(self.params.pulse_frequency.interpolate(t), 1, 100),
            'A2': remap(self.params.pulse_width.interpolate(t), 3, 20),
            'A3': remap(self.params.pulse_rise_time.interpolate(t), 2, 10),
            'A4': remap(self.params.pulse_interval_random.interpolate(t), 0, 1),
            'C0': remap(self.params.calibrate.center.interpolate(t), -10, 10),
            'C1': remap(self.params.calibrate.neutral.interpolate(t), -10, 10),
            'C2': remap(self.params.calibrate.right.interpolate(t), -10, 10),
        }
