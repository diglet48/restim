from dataclasses import dataclass
import time

import numpy as np
import sounddevice as sd

from PyQt5 import QtCore, QtWidgets


TCODE_LATENCY = 0.04  # delay tcode command. Worst-case command interval from multifunplayer

# measured latency on my machine, excluding tcode latency
# wdm-ks,
# latency='low'     50ms      frames: 441 or 7
# latency='high'   100ms      frames: 1764 or 28
# latency=0.1, 160-180ms
# wasapi:
# latency='low'  70-90ms      frames: 448
# latency='high' 220-240ms    frames: 448
# mme:
# latency='low'    130ms      frames: 576
# latency='high' 220-240ms    frames: 1136


class AudioGenerationWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.sample_rate = 44100
        self.frame_number = 0
        self.audio_latency = 0
        self.audio_channels = 2

        self.stream = None

        self.offset = 0
        self.last_dac_time = 0
        self.algorithm = None

    def start(self, host_api_name, audio_device_name, latency, algorithm):
        device_index = -1
        for device in sd.query_devices():
            if sd.query_hostapis(device['hostapi'])['name'] == host_api_name:
                if device['name'] == audio_device_name:
                    device_index = device['index']

        if device_index == -1:
            print("Audio device no longer exists?")
            return

        device_info = sd.query_devices(device_index)
        samplerate = device_info['default_samplerate']
        self.sample_rate = int(samplerate)
        device_channels = device_info['max_output_channels']

        print('Selected audio device:', host_api_name, audio_device_name, latency, samplerate)
        for channel_count in algorithm.preferred_channel_count():
            print(f"attempting to open audio device with {channel_count} channels.")
            if device_channels < channel_count:
                print(f"Device only has {device_channels} channels, so this won't work....")
                continue

            try:
                self.stream = sd.OutputStream(
                    samplerate=samplerate,
                    device=device_index,
                    channels=channel_count,
                    dtype=np.int16,
                    callback=self.callback,
                    latency=latency,
                )
                self.algorithm = algorithm
                self.stream.start()
            except sd.PortAudioError as e:
                print("Portaudio says:", e)
                continue

            print("Portaudio says: Success!")
            return

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.stream = None

    def callback(self, outdata: np.ndarray, frames: int, patime, status: sd.CallbackFlags):
        outdata.fill(0)
        current_time = patime.currentTime
        output_dac_time = patime.outputBufferDacTime

        # generate timeline for carrier frequency, increasing at a consistent rate
        timeline = np.linspace(self.frame_number / self.sample_rate,
                               (self.frame_number + frames) / self.sample_rate,
                               frames, endpoint=False)
        self.frame_number += frames

        # generate timeline for tcode, try to synchronize to system timer...
        system_time = time.time()
        offset = system_time - timeline[-1] - TCODE_LATENCY
        if abs(self.offset - offset) > 1:
            self.offset = offset
        else:
            self.offset = self.offset + 0.01 * (offset - self.offset)
        command_timeline = timeline + self.offset

        # audio latency for debugging purposes
        new_audio_latency = output_dac_time - current_time
        self.audio_latency += 0.2 * (new_audio_latency - self.audio_latency)

        # generate and save the audio
        in_data_float = np.array(self.algorithm.generate_audio(self.sample_rate, timeline, command_timeline)).T
        in_data_int16 = np.clip(in_data_float * 2**15, -32768, 32767).astype(np.int16)
        for in_channel, out_channel in enumerate(self.algorithm.channel_mapping(outdata.shape[1])):
            outdata[:, out_channel] = in_data_int16[:, in_channel]


