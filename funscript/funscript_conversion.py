import numpy as np
from funscript.funscript import Funscript


def convert_1d_to_2d(funscript: Funscript):
    at, pos = funscript.x, funscript.y

    dir = 1

    t_out = []
    x_out = []
    y_out = []

    for i in range(len(pos) - 1):
        start_t, end_t = at[i:i + 2]
        start_p, end_p = pos[i:i + 2]

        duration = end_t - start_t
        if start_p == end_p:
            n = 1
        else:
            if duration <= .100:
                n = 2
            elif duration <= .200:
                n = 3
            elif duration <= .300:
                n = 4
            elif duration <= .400:
                n = 5
            else:
                n = 6

        t = np.linspace(0.0, duration, n, endpoint=False)
        theta = np.linspace(0, np.pi, n, endpoint=False)
        center = (end_p + start_p) / 2
        r = (start_p - end_p) / 2

        if np.random.random() > 0.9:
            dir = dir * -1

        x = center + r * np.cos(theta)
        y = r * dir * np.sin(theta) + 0.5
        t_out += list(t + start_t)
        x_out += list(x)
        y_out += list(y)

    return t_out, x_out, y_out
