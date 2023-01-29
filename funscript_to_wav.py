import numpy as np
import argparse
import scipy
import json
import time

from stim_math import calibration, threephase, trig
import funscript_1d_to_2d


def generate_more(timeline, frequency, alpha, beta):
    # TODO: choose your own calibration parameters
    calib = calibration.SevenPointCalibration([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

    # normalize (a, b) to be within the unit circle.
    norm = np.clip(trig.norm(alpha, beta), 1.0, None)
    alpha /= norm
    beta /= norm
    volume = calib.get_scale(alpha, beta)

    L, R = threephase.generate_3_dof(timeline, frequency, volume, alpha, beta)
    return L, R


def parse_funscript(path):
    x = []
    y = []
    with open(path) as f:
        js = json.load(f)
        for action in js['actions']:
            pos = float(action['pos']) * 0.01
            at = float(action['at']) / 1000
            x.append(at)
            y.append(pos)

    return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32)


def export_wav(filename, sample_rate, channel1, channel2=None):
    if channel2 is None:
        a = channel1.astype(np.float32)
    else:
        a = np.vstack((channel1.astype(np.float32), channel2.astype(np.float32))).transpose()

    scipy.io.wavfile.write(filename, sample_rate, a)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='funscript conversion',
        description='convert 1d funscript into 2d')

    parser.add_argument('-a', help='input funscript (alpha axis)', required=True)
    parser.add_argument('-b', help='input funsciript (beta axis, optional)')
    parser.add_argument('-c')

    parser.add_argument('-o', '--out', required=True)
    parser.add_argument('--sample_rate', default=44100)
    parser.add_argument('--frequency', default=900)

    args = parser.parse_args()
    start_time = time.time()

    print('parsing funscripts')
    print(args.a)
    x1, y1 = parse_funscript(args.a)
    if args.b:
        print(args.b)
        x2, y2 = parse_funscript(args.b)
    else:
        print("1d-to-2d funscript conversion")
        x1, y1, y2 = funscript_1d_to_2d.convert_funscript_radial((x1, y1))
        x2 = x1
        # dummy funscript
        # x2, y2 = np.array([0, np.max(x1)], dtype=np.float32), np.array([0.5, 0.5], dtype=np.float32)

    print('generating coords')
    duration = np.max((np.max(x1), np.max(x2)))
    timeline = np.linspace(0, duration, int(duration * args.sample_rate + 1))
    alpha = np.interp(timeline, x1, y1).astype(np.float32)
    beta = np.interp(timeline, x2, y2).astype(np.float32)
    alpha = (alpha - 0.5) * 2
    beta = (beta - 0.5) * 2

    print('generate audio (may take a while)')
    L, R = generate_more(timeline, args.frequency, alpha, beta)

    print('export {}'.format(args.out))
    export_wav(args.out, args.sample_rate, L, R)

    print('took {:.2f} seconds'.format(time.time() - start_time))