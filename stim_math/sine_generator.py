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


class PulseGenerator:
    def __init__(self):
        self.cache = np.array([])

    def gen_single_pulse(self, low_level, high_level, width_in_samples):
        return high_level - (high_level - low_level) / 2 * (np.cos(np.linspace(0, 2 * np.pi, width_in_samples)) + 1)

    def gen_idle(self, low_level, width_in_samples):
        return np.full(width_in_samples, low_level)

    def gen_more(self, samplerate, carrier_freq, pulse_width_in_carrier_cycles, frequency, strength, random):
        pulse_width = int(samplerate / carrier_freq * pulse_width_in_carrier_cycles)

        interval_min = pulse_width
        interval_avg = int(samplerate / frequency)
        interval_max = int(interval_avg * 2 - interval_min)
        if interval_min < interval_max:
            interval = np.random.randint(interval_min, interval_max)
            interval = interval * random + interval_avg * (1 - random)
            samples_silence = int(interval - pulse_width)
        else:
            samples_silence = 0

        pulse = self.gen_single_pulse(1 - strength, 1, pulse_width)
        silence = self.gen_idle(1 - strength, samples_silence)

        self.cache = np.hstack((self.cache, pulse, silence))

    def generate(self, n, samplerate, carrier_freq, pulse_width_in_carrier_cycles, frequency, strength, random):
        if n <= len(self.cache):
            output = self.cache[:n]
            self.cache = self.cache[n:]
            return output

        output = np.array([])
        while n > 0:
            self.gen_more(samplerate, carrier_freq, pulse_width_in_carrier_cycles, frequency, strength, random)

            more = min(n, len(self.cache))
            output = np.hstack((output, self.cache[:more]))
            self.cache = self.cache[more:]
            n -= more
        return output
