import numpy as np
import argparse
import re
import pydub
import json
import time

import stim_math.threephase
from stim_math import sine_generator, threephase
import funscript_1d_to_2d


def generate_more(theta, alpha, beta):
    # TODO: choose your own calibration parameters
    center_calibration = stim_math.threephase.ThreePhaseCenterCalibration(-0.7)
    hw_calibration = threephase.ThreePhaseHardwareCalibration(-5.3, -0.7)

    L, R = threephase.ThreePhaseSignalGenerator.generate(theta, alpha, beta)

    volume = 1
    volume *= center_calibration.get_scale(alpha, beta)
    L *= volume
    R *= volume

    L, R = hw_calibration.apply_transform(L, R)

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


def export_audio_to_file(filename, samplerate, channel1, channel2, format):
    def audio_to_bytes(L, R):
        data = np.vstack((L, R)).transpose()
        data = np.clip(data * 2 ** 15, -32768, 32767).astype(np.int16)
        return data.tobytes()

    segment = pydub.AudioSegment(data=audio_to_bytes(channel1, channel2),
                                 sample_width=2, frame_rate=samplerate, channels=2)
    segment.export(filename, format=format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='funscript conversion',
        description='convert 1d funscript into 2d')

    parser.add_argument('-a', '--alpha', help='input funscript (alpha axis)', required=True)
    parser.add_argument('-b', '--beta', help='input funsciript (beta axis, optional)')
    parser.add_argument('-v', '--volume', help='input funsciript (volume axis, optional)')

    parser.add_argument('-o', '--out', help='output sound file, default same as funscript')
    parser.add_argument('--format', help='mp3 (default) or wav')
    parser.add_argument('--sample_rate', default=44100)
    parser.add_argument('--frequency', default=900)

    args = parser.parse_args()
    start_time = time.time()

    # determine format
    format = args.format
    if format is None:
        if args.out is not None:
            format = re.search('\.(.+)$', args.out).group(1)  # detect format from output
        else:
            format = 'mp3'  # default to mp3

    # determine output path
    output = args.out
    if output is None:
        output = re.sub('(\.alpha)?\.funscript$', '', args.alpha) # strip extension
        output = output + '.' + format

    print('parsing funscripts')
    print(args.alpha)
    x1, y1 = parse_funscript(args.alpha)
    if args.beta:
        print(args.beta)
        x2, y2 = parse_funscript(args.beta)
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

    volume = 1
    if args.volume:
        print('parsing volume')
        x3, y3 = parse_funscript(args.volume)
        volume = np.interp(timeline, x3, y3).astype(np.float32)

    print('generate audio (may take a while)')
    angle_generator = sine_generator.AngleGenerator()
    theta = angle_generator.generate(len(timeline), args.frequency, args.sample_rate)
    L, R = generate_more(theta, alpha, beta)
    L *= volume
    R *= volume

    print('export {}'.format(output))
    export_audio_to_file(output, args.sample_rate, L, R, format=format)

    print('took {:.2f} seconds'.format(time.time() - start_time))
