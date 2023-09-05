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


class AngleGenerator:
    def __init__(self):
        self.theta = 0

    def generate(self, n, frequency: float, samplerate: float):
        begin = self.theta
        end = self.theta + 2 * np.pi * frequency * (n / samplerate)
        self.theta = end

        return np.linspace(begin, end, n, endpoint=False)


class AngleGeneratorWithVaryingIPI:
    def __init__(self):
        self.theta = 0

        pivots = np.arange(0, 101)
        interval = np.random.uniform(0, 2, 101)
        interval[0] = 0
        endpoints = np.cumsum(interval)
        endpoints /= endpoints[-1] / 100

        pivots = pivots * 2 * np.pi
        random_endpoints = endpoints * 2 * np.pi

        self.random_points = random_endpoints
        self.fixed_points = pivots

    def randomize(self, x, random: float):
        xp = self.random_points * random + self.fixed_points * (1 - random)
        yp = self.fixed_points
        return np.interp(x % (100*2*np.pi), xp, yp)

    def generate(self, n, frequency: float, samplerate: float, random: float):
        begin = self.theta
        end = self.theta + 2 * np.pi * frequency * (n / samplerate)
        self.theta = end

        x = np.linspace(begin, end, n, endpoint=False)
        return self.randomize(x, random)