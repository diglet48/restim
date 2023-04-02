import numpy as np


class SineGenerator1D:
    def __init__(self):
        self.theta = 0

    def generate(self, n, frequency: float, samplerate: float):
        begin = self.theta
        end = self.theta + 2 * np.pi * frequency * (n / samplerate)
        self.theta = end

        t = np.linspace(begin, end, n, endpoint=False)
        return np.sin(t).astype(np.float32)


class SineGenerator2D:
    def __init__(self):
        self.theta = 0

    def generate(self, n, frequency: float, samplerate: float):
        begin = self.theta
        end = self.theta + 2 * np.pi * frequency * (n / samplerate)
        self.theta = end

        t = np.linspace(begin, end, n, endpoint=False)
        return np.sin(t).astype(np.float32), np.cos(t).astype(np.float32)
