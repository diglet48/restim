import pyaudio
import asyncio
import time

import numpy as np

from stim_math import calibration, threephase, trig
from net import tcode_server

AUDIO_DEVICE_NAME = 'MY AUDIO DEVICE NAME'

tcode = tcode_server.TCodeWebsocketServer('localhost', 12346)

frequency = 900.0  # hz
latency = .150


def generate_more(timeline):
    x = tcode.funscript_emulator.interpolate('L0', timeline) * 2 - 1
    y = tcode.funscript_emulator.interpolate('L1', timeline) * 2 - 1
    # TODO: use as volume?
    L2 = tcode.funscript_emulator.interpolate('L2', timeline)

    calib_params = [
        tcode.funscript_emulator.last_value('C0'),
        tcode.funscript_emulator.last_value('C1'),
        tcode.funscript_emulator.last_value('C2'),
        tcode.funscript_emulator.last_value('C3'),
        tcode.funscript_emulator.last_value('C4'),
        tcode.funscript_emulator.last_value('C5'),
        tcode.funscript_emulator.last_value('C6'),
    ]
    calib = calibration.SevenPointCalibration(calib_params)

    # normalize (x, y) to be within the unit circle.
    norm = np.clip(trig.norm(x, y), 1.0, None)
    x /= norm
    y /= norm

    volume = calib.get_scale(x, y)

    L, R = threephase.generate_3_dof(timeline, frequency, volume, x, y)
    return L, R


# todo: crap code
t0 = [None, None]

# Define callback for playback (1)
def callback(in_data, frame_count, time_info, status):
    current_dac_time = time_info['output_buffer_dac_time']
    global t0
    if t0[0] is None:
        t0[0] = current_dac_time
        t0[1] = time.time()

    timeline = (current_dac_time - t0[0] + t0[1]) + np.arange(0, frame_count) * (1.0 / 44100) - latency
    # timeline = timeline.astype(np.float32)
    L, R = generate_more(timeline)
    data = np.vstack((L, R)).transpose()
    data = np.clip(data * 2**15, -32768, 32767).astype(np.int16)
    data = data.tobytes()

    return (data, pyaudio.paContinue)


# Instantiate PyAudio and initialize PortAudio system resources (2)
p = pyaudio.PyAudio()

output_device_index = None

print('searching for audio device: {}'.format(AUDIO_DEVICE_NAME))
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    if device_info['name'] == AUDIO_DEVICE_NAME:
        output_device_index = i
        break

if output_device_index is None:
    print("unable to find audio device, fallback to default output".format(AUDIO_DEVICE_NAME))


# Open stream using callback (3)
stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=44100,
                output=True,
                stream_callback=callback,
                frames_per_buffer=5000, # 1000 ~= 20ms
                output_device_index=output_device_index
                )

print('audio stream started')

asyncio.run(tcode.start())

# Wait for stream to finish (4)
while stream.is_active():
    time.sleep(0.1)

# Close the stream (5)
stream.close()

# Release PortAudio system resources (6)
p.terminate()