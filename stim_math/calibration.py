import numpy as np
import scipy

from stim_math import trig


class SevenPointCalibration:
    def __init__(self, params):
        """
        :param params: 7 values. Scale at [0/3pi, 1/3pi, 2/3pi, 3/3pi, 4/3pi, 5/3pi, center]
        """
        assert len(params) == 7
        self.center_param = params[6]
        radial_params = params[:6]
        radial_angles = np.linspace(0, 2*np.pi, 6, endpoint=False)

        x = np.hstack((radial_angles - 2 * np.pi, radial_angles, radial_angles + 2 * np.pi)).astype(np.float32)
        y = np.hstack((radial_params, radial_params, radial_params)).astype(np.float32)

        self.interpolator = scipy.interpolate.PchipInterpolator(x, y)

    def get_scale(self, x, y):
        norm = trig.norm(x, y)
        norm = np.clip(norm, 0, 1)
        angle = np.arctan2(y, x)
        return (1 - norm) * self.center_param + norm * self.interpolator(angle).astype(np.float32)