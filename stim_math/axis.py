from abc import ABC, abstractmethod
import time
import numpy as np
import collections.abc


class AbstractAxis(ABC):
    @abstractmethod
    def interpolate(self, timestamp):
        pass

    @abstractmethod
    def last_value(self):
        pass

    @abstractmethod
    def add(self, value):
        pass


class AbstractMediaSync(ABC):
    @abstractmethod
    def is_playing(self) -> bool:
        pass


class DummyMediaSync(AbstractMediaSync):
    def is_playing(self) -> bool:
        return True


class AbstractTimestampMapper(ABC):
    @abstractmethod
    def map_timestamp(self, timestamp):
        pass


class DummyTimestampMapper(AbstractTimestampMapper):
    def map_timestamp(self, timestamp):
        return timestamp


# general class for series of x y values.
class Timeline:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


# series of X, Y values, intended for realtime updates.
# Old data is regularly removed
class ShortMemoryTimeline:
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
        assert interval >= 0
        interval = np.clip(interval, 1.0/30, None)    # Optimal value depends on tcode update frequency. Assume 30hz
        begin_ts = time.time()
        end_ts = begin_ts + interval

        begin_index = np.searchsorted(self.data[:, 0], begin_ts)
        end_index = np.searchsorted(self.data[:, 0], end_ts)
        current_value = np.interp(begin_ts, self.x(), self.y())

        if begin_index == 0:
            # insert at very beginning, must be a bug?
            self.data = np.array([[end_ts, value]], dtype=self.data.dtype)
        elif begin_index == end_index:
            # strip away future data, add linear segment at end
            # to avoid changing current data
            self.data = np.vstack((self.data[:end_index],
                                   [[begin_ts, current_value],
                                    [end_ts, value]]))
        else:
            # strip away future data, add single data point at end
            self.data = np.vstack((self.data[:end_index], [[end_ts, value]]))

        self.cleanup_if_needed()

    def cleanup_if_needed(self):
        self.nonce += 1
        if self.nonce >= self.cleanup_interval:
            if self.data.shape[0] > self.trim_min_size and self.data[0][0] < (time.time() - self.trim_min_age):
                cutoff = time.time() - self.trim_min_age
                self.data = self.data[self.data[:, 0] > cutoff]


class Interpolator(ABC):
    @abstractmethod
    def interpolate(self, timeline: Timeline, timestamps):
        pass


class LinearInterpolator(Interpolator):
    def interpolate(self, timeline: Timeline, timestamp):
        return np.interp(timestamp, timeline.x(), timeline.y())


class StairStepInterpolator(Interpolator):
    def interpolate(self, timeline: Timeline, timestamp):
        index = np.clip(np.searchsorted(timeline.x(), timestamp, side='right') - 1, 0, None)
        return timeline.y()[index]


class Axis(AbstractAxis):
    def __init__(self, timeline, interpolator: Interpolator, timestamp_mapper: AbstractTimestampMapper):
        self.timeline = timeline
        self.interpolator = interpolator
        self.timestamp_mapper = timestamp_mapper

    def add(self, value, interval=0.0):
        self.timeline.add(value, interval)

    def interpolate(self, timestamp):
        return self.interpolator.interpolate(self.timeline, self.timestamp_mapper.map_timestamp(timestamp))

    def last_value(self):
        return self.timeline.y()[-1]


class WriteProtectedAxis(Axis):
    def __init__(self, timeline, interpolator: Interpolator, timestamp_mapper: AbstractTimestampMapper):
        super(WriteProtectedAxis, self).__init__(timeline, interpolator, timestamp_mapper)

    def add(self, value, interval=0.0):
        pass


class ConstantAxis(AbstractAxis):
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


def create_temporal_axis(init_value, interpolation='linear'):
    if interpolation == 'linear':
        interpolator = LinearInterpolator()
    elif interpolation == 'step':
        interpolator = StairStepInterpolator()
    else:
        raise RuntimeError('unknown interpolation type')
    return Axis(ShortMemoryTimeline(init_value), interpolator, DummyTimestampMapper())


def create_constant_axis(init_value):
    return ConstantAxis(init_value)


def create_precomputed_axis(x, y, timestamp_mapper: AbstractTimestampMapper, interpolation='linear'):
    return WriteProtectedAxis(
        Timeline(x, y),
        LinearInterpolator(),
        timestamp_mapper
    )


