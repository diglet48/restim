import numpy as np
import json
import argparse


def parse_funscript(path):
    x = []
    y = []
    with open(path) as f:
        js = json.load(f)
        for action in js['actions']:
            at = float(action['at']) / 1000
            pos = float(action['pos']) * 0.01
            x.append(at)
            y.append(pos)
    return x, y


def write_funscript(path, funscript):
    x, y = funscript
    actions = [{"at": int(at*1000), "pos": int(pos * 100)} for at, pos in zip(x, y)]
    js = {"actions": actions}
    with open(path, 'w') as f:
        json.dump(js, f)


def convert_funscript_radial(funscript):
    at, pos = funscript

    t_out = []
    x_out = []
    y_out = []

    for i in range(len(pos)-1):
        start_t, end_t = at[i:i+2]
        start_p, end_p = pos[i:i+2]

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='funscript conversion',
        description='convert 1d funscript into 2d')

    parser.add_argument('filename')

    args = parser.parse_args()
    in_filename = args.filename
    alpha_filename = in_filename.replace('.funscript', '.alpha.funscript')
    beta_filename = in_filename.replace('.funscript', '.beta.funscript')

    print('in   : {}'.format(in_filename))
    print('out a: {}'.format(alpha_filename))
    print('out b: {}'.format(beta_filename))

    funscript = parse_funscript(in_filename)
    print('convert...')
    a, b, c = convert_funscript_radial(funscript)
    print('write...')
    write_funscript(alpha_filename, (a, b))
    write_funscript(beta_filename, (a, c))
    print('done')
