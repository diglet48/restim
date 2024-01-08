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


def float_to_int16(float_data):
    return np.clip(np.array(float_data) * 2**15, -32768, 32767).astype(np.int16)


def int16_to_float(int16_data):
    return int16_data.astype(np.float32) / 2 ** 15


class AudioGenerationWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.sample_rate = 44100
        self.frame_number = 0
        self.audio_channels = 2

        self.stream = None

        self.offset = 0
        self.algorithm = None
        self.previous_error = []

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
                self.frame_number = 0
                self.stream = sd.OutputStream(
                    samplerate=samplerate,
                    device=device_index,
                    channels=channel_count,
                    dtype=np.float32,
                    callback=self.callback,
                    latency=latency,
                )
                self.sample_rate = self.stream.samplerate
                self.algorithm = algorithm
                self.offset = time.time() - TCODE_LATENCY
                self.stream.start()
            except sd.PortAudioError as e:
                print("Portaudio says:", e)
                continue

            print("Portaudio says: Success!")
            return

    def start_modify(self, host_api_name, audio_input_device_name, audio_output_device_name, latency, algorithm):
        output_device_index = -1
        input_device_index = -1
        for device in sd.query_devices():
            if sd.query_hostapis(device['hostapi'])['name'] == host_api_name:
                if device['name'] == audio_input_device_name:
                    input_device_index = device['index']
                    print(device)
                if device['name'] == audio_output_device_name:
                    output_device_index = device['index']
                    print(device)

        if output_device_index == -1 or input_device_index == -1:
            print("Audio device no longer exists?")
            return

        device_info = sd.query_devices(output_device_index)
        samplerate = device_info['default_samplerate']
        self.sample_rate = int(samplerate)
        device_channels = device_info['max_output_channels']

        print('Selected audio device:', host_api_name, audio_input_device_name, audio_output_device_name, latency, samplerate)
        for channel_count in algorithm.preferred_channel_count():
            print(f"attempting to open audio device with {channel_count} channels.")
            if device_channels < channel_count:
                print(f"Device only has {device_channels} channels, so this won't work....")
                continue

            try:
                self.frame_number = 0
                self.stream = sd.Stream(
                    samplerate=samplerate,
                    device=(input_device_index, output_device_index),
                    channels=channel_count,
                    dtype=np.float32,
                    callback=self.callback_rw,
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
            self.stream.stop()  # blocks
            self.stream.close()
        self.stream = None

    def callback(self, outdata: np.ndarray, frames: int, patime, status: sd.CallbackFlags):
        outdata.fill(0.0)

        # generate timeline that is guaranteed to increase at a steady rate.
        # not referenced to any system clock
        steady_clock = np.linspace(self.frame_number / self.sample_rate,
                                   (self.frame_number + frames) / self.sample_rate,
                                   frames, endpoint=False)
        self.frame_number += frames

        # generate timestamp of output samples
        # slowly sync the timestamp to the actual audio rate.
        # use equation: steady_clock[-1] + offset = system_time - TCODE_LATENCY
        # minimize error to 0
        # TODO: move tcode latency somewhere else.
        system_time = time.time()
        offset = system_time - steady_clock[-1] - TCODE_LATENCY
        if abs(self.offset - offset) > 1:
            print('audio output desync (>1s). Stopping...')
            # todo: set error flag, somewhere
            self.previous_error = []
            raise sd.CallbackAbort()
        else:
            dt = frames / self.sample_rate
            error = offset - self.offset
            self.previous_error.append(error)
            self.previous_error = self.previous_error[-8:]
            error = np.average(self.previous_error)  # very poor low-pass filter
            max_adjustment = dt * 0.02   # adjust maximally 0.02 s/s
            adjustment = np.clip(-max_adjustment, error * dt, max_adjustment)
            # print(error * 1000, adjustment * 1000, adjustment * 44100 / frames * 100, self.previous_error)
            old_offset = self.offset
            self.offset += adjustment
            command_timeline = steady_clock + np.linspace(old_offset, self.offset, frames, endpoint=False)

        # generate audio
        data = np.array(self.algorithm.generate_audio(self.sample_rate, steady_clock, command_timeline)).T
        for in_channel, out_channel in enumerate(self.algorithm.channel_mapping(outdata.shape[1])):
            outdata[:, out_channel] = data[:, in_channel]

    def callback_rw(self, indata, outdata, frames, time, status):
        data = np.array(self.algorithm.modify_audio(np.array(indata))).T
        for in_channel, out_channel in enumerate(self.algorithm.channel_mapping(outdata.shape[1])):
            outdata[:, out_channel] = data[:, in_channel]

