from abc import ABC, abstractmethod

import numpy as np
import time

from PySide6 import QtCore

from stim_math.axis import AbstractAxis, WriteProtectedAxis

from qt_ui.widgets.fourphase_widget_stereographic import v1, v2, v3, v4


class FourphasePattern(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def update(self, dt: float):
        ...


class MousePattern(FourphasePattern):
    def __init__(self):
        super().__init__()
        self.x = 1
        self.y = 0
        self.z = 0

    def name(self):
        return "mouse"

    def mouse_event(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def update(self, dt: float):
        return self.x, self.y, self.z


class OrbitPattern(FourphasePattern):
    def __init__(self, name, axis):
        super().__init__()
        self._name = name
        self.axis = axis
        self.dir1 = np.linalg.cross(axis, [.5, .7, .999])
        self.dir2 = np.linalg.cross(axis, self.dir1)
        self.dir1 /= np.linalg.norm(self.dir1)
        self.dir2 /= np.linalg.norm(self.dir2)
        self.angle = 0

    def name(self):
        return self._name

    def update(self, dt: float):
        self.angle = self.angle + dt * 1
        return self.dir1 * np.cos(self.angle) + self.dir2 * np.sin(self.angle)


class SequencePattern(FourphasePattern):
    def __init__(self, name, sequence: list):
        super().__init__()
        self._name = name
        self.sequence = np.vstack((sequence, sequence, sequence[0]))
        self.index = 0

        for i in range(1, len(self.sequence)):
            dist_1 = np.linalg.norm(self.sequence[i] - self.sequence[i-1])
            dist_2 = np.linalg.norm(self.sequence[i] + self.sequence[i-1])
            if dist_2 < dist_1:
                self.sequence[i] *= -1

    def name(self):
        return self._name

    def update(self, dt: float):
        self.index = (self.index + dt / 2) % (len(self.sequence) - 1)
        index = self.index
        x = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 0])
        y = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 1])
        z = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 2])

        xyz = np.array([x, y, z])
        xyz /= np.linalg.norm(xyz)
        return xyz


class SpiralPattern(FourphasePattern):
    def __init__(self, name, axis):
        super().__init__()
        self._name = name
        self.axis = axis / np.linalg.norm(axis)
        self.dir1 = np.linalg.cross(axis, [.5, .7, .999])
        self.dir2 = np.linalg.cross(axis, self.dir1)
        self.dir1 /= np.linalg.norm(self.dir1)
        self.dir2 /= np.linalg.norm(self.dir2)
        self.angle = 0
        self.angle2 = 0

    def name(self):
        return self._name

    def update(self, dt: float):
        self.angle = self.angle + dt * 4
        self.angle2 = self.angle2 + dt * .23
        radius = np.sin(self.angle2) * 0.6
        vec = (self.axis +
               self.dir1 * np.cos(self.angle) * radius +
               self.dir2 * np.sin(self.angle) * radius)
        return vec / np.linalg.norm(vec)


class FourphaseMotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis, gamma: AbstractAxis):
        super().__init__(parent)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.script_alpha = None
        self.script_beta = None
        self.script_gamma = None

        self.mouse_pattern = MousePattern()
        self.patterns = [
            self.mouse_pattern,
            SequencePattern('seq ABCD', [v1, v2, v3, v4]),
            SequencePattern('seq ABDC', [v1, v2, v4, v3]),
            SequencePattern('seq ADBC', [v1, v4, v2, v3]),
            SpiralPattern('spiral A', v1),
            SpiralPattern('spiral B', v2),
            SpiralPattern('spiral C', v3),
            SpiralPattern('spiral D', v4),
            OrbitPattern('not A', v1),
            OrbitPattern('not B', v2),
            OrbitPattern('not C', v3),
            OrbitPattern('not D', v4),
            OrbitPattern('orbit CW', v2 + v4 - v1 - v3),
            OrbitPattern('orbit CCW', v1 + v3 - v2 - v4),
            OrbitPattern('orbit right', v1 - v3 - v2 + v4),
            OrbitPattern('orbit up', v1 - v3 + v2 - v4),
        ]
        self.pattern = self.mouse_pattern

        self.velocity = 1
        self.last_update_time = time.time()
        self.latency = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(int(1000 / 60.0))

    def set_enable(self, enable):
        if enable:
            self.timer.start()
        else:
            self.timer.stop()

    def set_pattern(self, pattern):
        if issubclass(pattern.__class__, FourphasePattern):
            self.pattern = pattern

    def set_scripts(self, alpha, beta, gamma):
        self.script_alpha = alpha if issubclass(alpha.__class__, WriteProtectedAxis) else None
        self.script_beta = beta if issubclass(beta.__class__, WriteProtectedAxis) else None
        self.script_gamma = gamma if issubclass(gamma.__class__, WriteProtectedAxis) else None

    def any_scripts_loaded(self):
        return (self.script_alpha, self.script_beta, self.script_gamma) != (None, None, None)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def timeout(self):
        dt = time.time() - self.last_update_time
        self.last_update_time = time.time()

        if not self.any_scripts_loaded():
            # update pattern, update display
            a, b, c = self.pattern.update(dt * self.velocity)
            self.alpha.add(a)
            self.beta.add(b)
            self.gamma.add(c)
            # TODO: latency?
            self.position_updated.emit(a, b, c)
        else:
            # update display with data from funscript
            a = self.script_alpha.interpolate(time.time() - self.latency)
            b = self.script_beta.interpolate(time.time() - self.latency)
            c = self.script_gamma.interpolate(time.time() - self.latency)
            self.position_updated.emit(a, b, c)


    def mouse_event(self, a, b, c):
        if self.pattern == self.mouse_pattern and not self.any_scripts_loaded():
            self.mouse_pattern.mouse_event(a, b, c)
            self.alpha.add(a)
            self.beta.add(b)
            self.gamma.add(c)
            self.position_updated.emit(a, b, c)

    position_updated = QtCore.Signal(float, float, float)  # a, b, c
