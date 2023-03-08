import numpy as np
from funscript.funscript import Funscript


def convert_1d_to_2d(funscript: Funscript):
    at, pos = funscript.x, funscript.y

    t_out = []
    x_out = []
    y_out = []

    for i in range(len(pos) - 1):
        start_t, end_t = at[i:i + 2]
        start_p, end_p = pos[i:i + 2]

        points_per_second = 25
        n = int(np.clip(float((end_t - start_t) * points_per_second), 1, None))
        t = np.linspace(0.0, end_t - start_t, n, endpoint=False)
        theta = np.linspace(0, np.pi, n, endpoint=False)
        center = (end_p + start_p) / 2
        r = (start_p - end_p) / 2

        x = center + r * np.cos(theta)
        y = r * np.sin(theta) + 0.5
        t_out += list(t + start_t)
        x_out += list(x)
        y_out += list(y)

    return t_out, x_out, y_out
