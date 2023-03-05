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


class ThirteenPointCalibration:
    def __init__(self, params):
        """
        :param params: 13 values. Scale at
        r1:   [0/3pi, 1/3pi, 2/3pi, 3/3pi, 4/3pi, 5/3pi] +
        r0.5: [0/3pi, 1/3pi, 2/3pi, 3/3pi, 4/3pi, 5/3pi] +
              [center]
        """
        assert len(params) == 13
        self.center_param = params[12]

        radial_params = params[:6]
        radial_angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)

        x = np.hstack((radial_angles - 2 * np.pi, radial_angles, radial_angles + 2 * np.pi)).astype(np.float32)
        y = np.hstack((radial_params, radial_params, radial_params)).astype(np.float32)

        self.edge_interpolator = scipy.interpolate.PchipInterpolator(x, y)

        radial_params = params[6:12]
        radial_angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)

        x = np.hstack((radial_angles - 2 * np.pi, radial_angles, radial_angles + 2 * np.pi)).astype(np.float32)
        y = np.hstack((radial_params, radial_params, radial_params)).astype(np.float32)

        self.half_interpolator = scipy.interpolate.PchipInterpolator(x, y)

    def get_scale(self, x, y):
        norm = trig.norm(x, y)
        norm = np.clip(norm, 0, 1)
        angle = np.arctan2(y, x)

        a = np.clip(1 - norm * 2, 0, 1)
        c = np.clip(norm * 2 - 1, 0, 1)
        b = 1 - a - c

        return a * self.center_param + b * self.half_interpolator(angle) + c * self.edge_interpolator(angle)


class CenterCalibration:
    def __init__(self, db_in_center):
        self.db_in_center = db_in_center

    def get_scale(self, x, y):
        ratio = 10 ** (self.db_in_center / 10)
        norm = trig.norm(x, y).clip(min=None, max=1)

        if ratio <= 1:
            edge = 1
            center = ratio
        else:
            edge = 1/ratio
            center = 1

        return center + norm * (edge - center)
