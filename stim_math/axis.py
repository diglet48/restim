from abc import ABC, abstractmethod
import time
import numpy as np
import collections.abc


class Axis(ABC):
    @abstractmethod
    def add(self, value, interval=0.0):
        ...

    @abstractmethod
    def interpolate(self, timestamp):
        ...

    @abstractmethod
    def last_value(self):
        ...


class Timeline:
    def __init__(self, init_value, dtype=None, trim_min_size=10, trim_min_age=5, cleanup_interval=100):
        self.data = np.array([[0, init_value]], dtype=dtype)
        self.trim_min_size = trim_min_size
        self.trim_min_age = trim_min_age
        self.nonce = 0
        self.cleanup_interval = cleanup_interval

    def x(self):
        return self.data[:, 0]

    def y(self):
        return self.data[:, 1]

    def add(self, value, interval=0.0):
        ts = time.time() + interval

        # make sure data stays sorted
        if len(self.data[-1]) > 0:
            if self.data[-1, 0] == ts:
                # overwrite last value
                self.data[-1, 1] = value
            elif self.data[-1, 0] > ts:
                # delete any values >= interval
                i = np.searchsorted(self.data[:, 0], ts)
                self.data = self.data[:i]
                self.data = np.vstack((self.data, [ts, value]))
            else:
                # just insert
                self.data = np.vstack((self.data, [ts, value]))
        else:
            # just insert
            self.data = np.vstack((self.data, [ts, value]))

        self.cleanup_if_needed()

    def cleanup_if_needed(self):
        self.nonce += 1
        if self.nonce >= self.cleanup_interval:
            if self.data.shape[0] > self.trim_min_size and self.data[0][0] < (time.time() - self.trim_min_age):
                cutoff = time.time() - self.trim_min_age
                self.data = self.data[self.data[:, 0] > cutoff]


class LinearInterpolatedAxis(Axis):
    def __init__(self, init_value):
        self.timeline = Timeline(init_value)

    def add(self, value, interval=0.0):
        self.timeline.add(value, interval)

    def interpolate(self, timestamp):
        return np.interp(timestamp, self.timeline.x(), self.timeline.y())

    def last_value(self):
        return self.timeline.y()[-1]


class StairStepAxis(Axis):
    def __init__(self, init_value):
        self.timeline = Timeline(init_value)

    def add(self, value, interval=0.0):
        self.timeline.add(value, interval)

    def interpolate(self, timestamp):
        index = np.searchsorted(self.timeline.x(), timestamp)
        return self.timeline.y()[index]

    def last_value(self):
        return self.timeline.y()[-1]


class ConstantAxis(Axis):
    def __init__(self, init_value):
        self.value = init_value

    def add(self, value, interval=0.0):
        self.value = value

    def interpolate(self, timestamp):
        if isinstance(timestamp, collections.abc.Sequence):
            return np.full_like(timestamp, self.value)
        return self.value

    def last_value(self):
        return self.value
