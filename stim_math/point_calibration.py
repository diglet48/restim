import numpy as np

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

        self.xp = radial_angles
        self.yp = radial_params

    def get_scale(self, x, y):
        norm = trig.norm(x, y)
        norm = np.clip(norm, 0, 1)
        angle = np.arctan2(y, x)
        return (1 - norm) * self.center_param + norm * np.interp(angle, self.xp, self.yp, period=np.pi * 2).astype(np.float32)


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
        self.xp_edge = radial_angles
        self.yp_edge = radial_params

        radial_params = params[6:12]
        radial_angles = np.linspace(0, 2 * np.pi, 6, endpoint=False)
        self.xp_half = radial_angles
        self.yp_half = radial_params

    def get_scale(self, x, y):
        norm = trig.norm(x, y)
        norm = np.clip(norm, 0, 1)
        angle = np.arctan2(y, x)

        a = np.clip(1 - norm * 2, 0, 1)
        c = np.clip(norm * 2 - 1, 0, 1)
        b = 1 - a - c

        return a * self.center_param + \
               b * np.interp(angle, self.xp_half, self.yp_half, period=np.pi * 2) + \
               c * np.interp(angle, self.xp_half, self.yp_edge, period=np.pi * 2)


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
