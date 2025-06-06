import time
import logging
from dataclasses import dataclass

import numpy as np
import sounddevice as sd

from stim_math.audio_gen.base_classes import AudioGenerationAlgorithm
from qt_ui import settings
from device.output_device import OutputDevice

logger = logging.getLogger('restim.audio')

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


@dataclass
class ChannelMappingParameters:
    device_audio_channels: int
    device_channel_map: list[int]


class AudioStimDevice(OutputDevice):
    def __init__(self, parent):
        OutputDevice.__init__(self)

        self.sample_rate = 44100
        self.frame_number = 0
        self.channel_map = None

        self.stream = None

        self.offset = 0
        self.algorithm = None
        self.previous_error = []

    def start(self, host_api_name, audio_device_name, latency, algorithm: AudioGenerationAlgorithm,
              mapping_parameters: list[ChannelMappingParameters]):
        device_index = -1
        for device in sd.query_devices():
            if sd.query_hostapis(device['hostapi'])['name'] == host_api_name:
                if device['name'] == audio_device_name:
                    device_index = device['index']

        if device_index == -1:
            logger.error("Audio device no longer exists?")
            return

        device_info = sd.query_devices(device_index)
        samplerate = device_info['default_samplerate']
        self.sample_rate = int(samplerate)
        device_channels = device_info['max_output_channels']

        logger.info(f'Selected audio device: {host_api_name}, {audio_device_name}, {latency}, {samplerate}')
        for mapping_parameter in mapping_parameters:
            logger.info(f"attempting to open audio device with {mapping_parameter.device_audio_channels} channels.")
            if device_channels < mapping_parameter.device_audio_channels:
                logger.error(f"Device only has {device_channels} channels, so this won't work....")
                continue

            try:
                self.frame_number = 0
                self.stream = sd.OutputStream(
                    samplerate=samplerate,
                    device=device_index,
                    channels=mapping_parameter.device_audio_channels,
                    dtype=np.float32,
                    callback=self.callback,
                    latency=latency,
                )
                self.sample_rate = self.stream.samplerate
                self.algorithm = algorithm
                self.channel_map = mapping_parameter.device_channel_map
                self.offset = time.time()
                self.stream.start()
            except sd.PortAudioError as e:
                logger.error(f"Portaudio says: {e}")
                continue

            logger.info("Portaudio says: Success!")
            return

    def start_modify(self, host_api_name, audio_input_device_name, audio_output_device_name, latency, algorithm,
                     mapping_parameters: list[ChannelMappingParameters]):
        output_device_index = -1
        input_device_index = -1
        for device in sd.query_devices():
            if sd.query_hostapis(device['hostapi'])['name'] == host_api_name:
                if device['name'] == audio_input_device_name:
                    input_device_index = device['index']
                if device['name'] == audio_output_device_name:
                    output_device_index = device['index']

        if output_device_index == -1 or input_device_index == -1:
            logger.error("Audio device no longer exists?")
            return

        device_info = sd.query_devices(output_device_index)
        samplerate = device_info['default_samplerate']
        self.sample_rate = int(samplerate)
        device_channels = device_info['max_output_channels']

        logger.info(f'Selected audio device: {host_api_name}, {audio_input_device_name}, {audio_output_device_name}, {latency}, {samplerate}')
        for mapping_parameter in mapping_parameters:
            logger.info(f"attempting to open audio device with {mapping_parameter.device_audio_channels} channels.")
            if device_channels < mapping_parameter.device_audio_channels:
                logger.error(f"Device only has {device_channels} channels, so this won't work....")
                continue

            try:
                self.frame_number = 0
                self.stream = sd.Stream(
                    samplerate=samplerate,
                    device=(input_device_index, output_device_index),
                    channels=mapping_parameter.device_audio_channels,
                    dtype=np.float32,
                    callback=self.callback_rw,
                    latency=latency,
                )
                self.channel_map = mapping_parameter.device_channel_map
                self.algorithm = algorithm
                self.stream.start()
            except sd.PortAudioError as e:
                logger.error(f"Portaudio says: {e}")
                continue

            logger.info("Portaudio says: Success!")
            return

    def stop(self):
        if self.stream is not None:
            self.stream.stop()  # blocks
            self.stream.close()
        self.stream = None

    def is_connected_and_running(self) -> bool:
        return self.stream is not None

    def auto_detect_channel_mapping_parameters(self, algorithm: AudioGenerationAlgorithm) -> [ChannelMappingParameters]:
        if algorithm.channel_count() == 2:
            return [ChannelMappingParameters(2, [0, 1])]
        raise RuntimeError('Invalid audio algorithm')

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
        # use equation: steady_clock[-1] + offset = system_time
        # minimize error to 0
        system_time = time.time()
        offset = system_time - steady_clock[-1]
        if abs(self.offset - offset) > 1:
            logger.error('audio output desync (>1s). Stopping...')
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
        for in_channel, out_channel in enumerate(self.channel_map):
            outdata[:, out_channel] = data[:, in_channel]

    def callback_rw(self, indata, outdata, frames, time, status):
        data = np.array(self.algorithm.modify_audio(np.array(indata))).T
        for in_channel, out_channel in enumerate(self.channel_map):
            outdata[:, out_channel] = data[:, in_channel]

