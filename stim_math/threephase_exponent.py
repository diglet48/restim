import numpy as np


class ThreePhaseExponentAdjustment:
    """
    TODO: need additional testing to determine if useful
    Adjust signals for nerve sensitivity
    exponent 0 = nerve sensitivity linear with voltage (intensity = voltage)
    exponent 0.5 = nerve sensitivity quadratic with voltage (intensity = voltage^2)
    exponent 1 = nerve sensitivity more-than-quadratic with voltage (intensity = voltage^inf)
    """
    def __init__(self, exponent):
        self._exponent = np.clip(exponent, 0, 1)

    def get_scale(self, alpha, beta):
        # TODO: can optimize
        r = np.sqrt(np.power(alpha, 2) + np.power(beta, 2))
        complex_points = np.array([
            [1, 0],
            [-0.5, np.sqrt(3) / 2],
            [-0.5, -np.sqrt(3) / 2]
        ]) @ np.array([
            [2 - r + alpha, beta],
            [beta, 2 - r - alpha],
        ]) * 0.5
        norm = np.linalg.norm(complex_points, axis=0)
        z = np.max(norm, axis=0)

        scaling_factor = np.power(z, -self._exponent) * (np.sqrt(3)/2)
        # print(scaling_factor[0])
        return scaling_factor
        # return L*scaling_factor, R*scaling_factor


