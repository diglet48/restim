from abc import ABC, abstractmethod
import numpy as np


class AudioGenerationAlgorithm(ABC):
    def preferred_channel_count(self):
        pass

    def channel_mapping(self, channel_count):
        pass

    @abstractmethod
    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        """
        :param samplerate: samplerate of the audio stream, like 44100 samples/s
        :param steady_clock: time since the start of the stream, guaranteed to increase at monotonic rate
        :param system_time_estimate: best-guess of the system time of the output sample. Guaranteed to increase
            but not necessary at monotonic rate.
        :return: tuple of audio channels
        """
        pass


class AudioModifyAlgorithm(ABC):
    def preferred_channel_count(self):
        pass

    def channel_mapping(self, channel_count):
        pass

    @abstractmethod
    def modify_audio(self, in_data: np.array):
        """
        :param in_data: Audio channel data (np.array of float)
        :return: modified audio channel data
        """
        pass
