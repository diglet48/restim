import numpy as np

class Interpolator:
    def __init__(self, xp, yp):
        self.x = xp
        self.y = yp

    def __call__(self, t):
        """
        :param t:   if negative: before note. if positive: after note
        :return:
        """
        return np.interp(t, self.x, self.y)


interpolator_slow = Interpolator(
    np.array([-1, 0, 1, 3]) / 4,
    np.array([0, 1, .9, 0])
)

interpolator_normal = Interpolator(
    np.array([-.5, 0, .5, 1.5]) / 4,
    np.array([0, 1, .9, 0])
)

interpolator_fast = Interpolator(
    np.array([-.25, 0, .25, .25 + .5]) / 4,
    np.array([0, 1, .9, 0])
)

interpolator_very_fast = Interpolator(
    np.array([-.128, 0, .128, .128 + .25]) / 4,
    np.array([0, 1, .9, 0])
)

interpolators = [
    ('slow (1, 1, 2)', interpolator_slow),
    ('normal (1/2, 1/2, 1)', interpolator_normal),
    ('fast (1/4, 1/4, 1/2)', interpolator_fast),
    ('very fast (1/8, 1/8, 1/4)', interpolator_very_fast),
]