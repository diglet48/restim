import numpy as np

from stim_math.limits import ModulationBias


class SineModulation:
    def __init__(self, theta, modulation, left_right_bias, high_low_bias):
        self.theta = theta
        self.modulation = modulation
        self.left_right_bias = np.clip(left_right_bias, -1, 1)
        self.high_low_bias = np.clip(high_low_bias, -1, 1)

    def modulate(self, L, R):
        e = self.envelope()
        return L * e, R * e

    def get_modulation_signal(self):
        return self.envelope()

    def envelope(self):
        # clip to safety limits
        strength = np.clip(self.modulation, 0.0, 1.0)
        l_r = np.clip(self.left_right_bias, ModulationBias.min, ModulationBias.max)
        h_l = np.clip(self.high_low_bias, ModulationBias.min, ModulationBias.max)

        high_time = np.clip(h_l, 0, 1)
        low_time = np.clip(-h_l, 0, 1)
        rise_time = (1 - high_time - low_time) * (1 - l_r) / 2
        fall_time = (1 - high_time - low_time) * (1 + l_r) / 2

        t_startrise = low_time
        t_endrise = t_startrise + rise_time
        t_startdrop = t_endrise + high_time
        t_enddrop = t_startdrop + fall_time

        remap = np.array([
            [2 * np.pi * t_startrise, 0],
            [2 * np.pi * t_endrise, np.pi],
            [2 * np.pi * t_startdrop, np.pi],
            [2 * np.pi * t_enddrop, 2 * np.pi],
        ])
        theta = np.interp(self.theta % (np.pi * 2), remap[:, 0], remap[:, 1])
        a = 1 - strength / 2
        b = -strength / 2
        return a + b * np.cos(theta)