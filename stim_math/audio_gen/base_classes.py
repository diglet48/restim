from abc import ABC, abstractmethod
import numpy as np


class AudioGenerationAlgorithm(ABC):
    @abstractmethod
    def channel_count(self) -> int:
        """
        :return: The number of audio channels actually generated
        2 for 3-phase
        3 for 4-phase
        4 for 5-phase
        """
        pass

    @abstractmethod
    def generate_audio(self, samplerate, steady_clock: np.ndarray, system_time_estimate: np.ndarray):
        """
        :param samplerate: samplerate of the audio stream, like 44100 samples/s
        :param steady_clock: time since the start of the stream, guaranteed to increase at monotonic rate.
            May increase slightly slower of faster (expected tolerance <0.01%) than actual time.
        :param system_time_estimate: best-guess of the system time of the output sample.
            May have large jumps, decrease between calls, etc.
        :return: tuple of audio channels
        """
        pass


class AudioModifyAlgorithm(ABC):
    @abstractmethod
    def channel_count(self) -> int:
        """
        :return: The number of audio channels actually generated
        2 for 3-phase
        3 for 4-phase
        4 for 5-phase
        """
        pass

    @abstractmethod
    def modify_audio(self, in_data: np.array):
        """
        :param in_data: Audio channel data (np.array of float)
        :return: modified audio channel data
        """
        pass


class RemoteGenerationAlgorithm(ABC):
    @abstractmethod
    def parameter_dict(self) -> dict:
        """
        :return: the tcode axis and values, range 0-1
        """
        pass