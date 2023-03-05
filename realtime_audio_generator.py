import pyaudio
import asyncio
import time

import numpy as np

from stim_math import point_calibration, threephase, trig, amplitude_modulation, hardware_calibration
from net import tcode_server

AUDIO_DEVICE_NAME = 'MY AUDIO DEVICE NAME'

tcode = tcode_server.TCodeWebsocketServer('localhost', 12346)

latency = .1


def generate_more(timeline):
    # todo: need better latency adjustment
    command_timeline = timeline + (-timeline[-1] + time.time() - latency)

    x = tcode.funscript_emulator.interpolate('L0', command_timeline) * 2 - 1
    y = tcode.funscript_emulator.interpolate('L1', command_timeline) * 2 - 1

    # TODO: use as volume?
    # L2 = tcode.funscript_emulator.interpolate('L2', command_timeline)
    # L2 = np.clip(L2, 0.0, 1.0)

    frequency = tcode.funscript_emulator.last_value('M0') * 1000.0
    # safety: clamp the carrier frequency
    frequency = np.clip(frequency, 400.0, 1000.0)

    # normalize (x, y) to be within the unit circle.
    norm = np.clip(trig.norm(x, y), 1.0, None)
    x /= norm
    y /= norm

    L, R = threephase.ContinuousSineWaveform.generate(timeline, frequency, x, y)
    # intensity = threephase.ContinuousSineWaveform.intensity(x, y)
    # L /= intensity
    # R /= intensity

    # calibration (fine tuning)
    calib_params = [
        tcode.funscript_emulator.last_value('C0'),
        tcode.funscript_emulator.last_value('C1'),
        tcode.funscript_emulator.last_value('C2'),
        tcode.funscript_emulator.last_value('C3'),
        tcode.funscript_emulator.last_value('C4'),
        tcode.funscript_emulator.last_value('C5'),

        tcode.funscript_emulator.last_value('D0'),
        tcode.funscript_emulator.last_value('D1'),
        tcode.funscript_emulator.last_value('D2'),
        tcode.funscript_emulator.last_value('D3'),
        tcode.funscript_emulator.last_value('D4'),
        tcode.funscript_emulator.last_value('D5'),

        tcode.funscript_emulator.last_value('C6'), # center
    ]
    calib = point_calibration.ThirteenPointCalibration(calib_params)
    volume = calib.get_scale(x, y)
    L *= volume
    R *= volume

    # modulation 1
    modulation_hz = tcode.funscript_emulator.last_value('M1') * 150
    modulation_strength = tcode.funscript_emulator.last_value('M2')
    modulation = amplitude_modulation.SineModulation(modulation_hz, modulation_strength)
    L, R = modulation.modulate(timeline, L, R)

    # modulation 2
    modulation_hz = tcode.funscript_emulator.last_value('M3') * 150
    modulation_strength = tcode.funscript_emulator.last_value('M4')
    modulation = amplitude_modulation.SineModulation(modulation_hz, modulation_strength)
    L, R = modulation.modulate(timeline, L, R)

    # center scaling
    center_db = (tcode.funscript_emulator.last_value('H2') - 0.5) * 30
    center_calibration = point_calibration.CenterCalibration(center_db)
    scale = center_calibration.get_scale(x, y)
    L *= scale
    R *= scale

    # apply hardware calibration
    u_d = (tcode.funscript_emulator.last_value('H0') - 0.5) * 30
    l_r = (tcode.funscript_emulator.last_value('H1') - 0.5) * 30

    hw = hardware_calibration.HardwareCalibration(u_d, l_r)
    L, R = hw.apply_transform(L, R)

    return L, R


class Generator:
    def __init__(self):
        self.frame_number = 0
        self.sample_rate = 44100
        self.audio_latency = 0  # best guess of audio latency

    def callback(self, in_data, frame_count, time_info, status):
        timeline = np.linspace(self.frame_number / self.sample_rate,
                               (self.frame_number + frame_count) / self.sample_rate,
                               frame_count, endpoint=False)
        self.frame_number += frame_count

        new_audio_latency = time_info['output_buffer_dac_time'] - time_info['current_time']
        self.audio_latency += 0.2 * (new_audio_latency - self.audio_latency)

        # command_time_offset = time.time() - timeline[0] - .03

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


g = Generator()

# Open stream using callback (3)
stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=44100,
                output=True,
                stream_callback=g.callback,
                frames_per_buffer=1000, # 1000 ~= 20ms
                output_device_index=output_device_index,
                )
# note: audio latency = frames_per_buffer / 44100 * 2 + driver dependant latency

print('audio stream started')

asyncio.run(tcode.start())

# Wait for stream to finish (4)
while stream.is_active():
    time.sleep(0.1)

# Close the stream (5)
stream.close()

# Release PortAudio system resources (6)
p.terminate()