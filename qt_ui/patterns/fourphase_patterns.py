from abc import ABC, abstractmethod

import numpy as np
import time

from PySide6 import QtCore

import qt_ui.settings
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
    def __init__(self, alpha: AbstractAxis, beta: AbstractAxis, gamma: AbstractAxis):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.x = 0.00001    # hack to force display update on load
        self.y = 0
        self.z = 0

    def name(self):
        return "mouse"

    def mouse_event(self, x, y, z):
        self.alpha.add(x)
        self.beta.add(y)
        self.gamma.add(z)
        self.x = x
        self.y = y
        self.z = z

    def update(self, dt: float):
        return self.x, self.y, self.z

    def last_position_is_mouse_position(self):
        return (self.x, self.y) == (self.alpha.last_value(), self.beta.last_value())


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

        self.mouse_pattern = MousePattern(alpha, beta, gamma)
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
        self.refreshSettings()

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
            if issubclass(self.pattern.__class__, MousePattern):
                if self.pattern.last_position_is_mouse_position():
                    # mouse position, display update already handled.
                    pass
                else:
                    # tcode position, send lagged position
                    a = self.alpha.interpolate(time.time() - self.latency)
                    b = self.beta.interpolate(time.time() - self.latency)
                    c = self.gamma.interpolate(time.time() - self.latency)
                    self.position_updated.emit(a, b, c)
            else:
                # update pattern, display lagged position
                a, b, c = self.pattern.update(dt * self.velocity)
                self.alpha.add(a)
                self.beta.add(b)
                self.gamma.add(c)
                a = self.alpha.interpolate(time.time() - self.latency)
                b = self.beta.interpolate(time.time() - self.latency)
                c = self.gamma.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b, c)
        else:
            # update display with data from funscript
            if self.script_alpha:
                a = self.script_alpha.interpolate(time.time() - self.latency)
            else:
                a = self.alpha.interpolate(time.time() - self.latency)
            if self.script_beta:
                b = self.script_beta.interpolate(time.time() - self.latency)
            else:
                b = self.beta.interpolate(time.time() - self.latency)
            if self.script_gamma:
                c = self.script_gamma.interpolate(time.time() - self.latency)
            else:
                c = self.gamma.interpolate(time.time() - self.latency)
            self.position_updated.emit(a, b, c)

    def mouse_event(self, a, b, c):
        if self.pattern == self.mouse_pattern and not self.any_scripts_loaded():
            self.mouse_pattern.mouse_event(a, b, c)
            self.alpha.add(a)
            self.beta.add(b)
            self.gamma.add(c)
            self.position_updated.emit(a, b, c)

    def refreshSettings(self):
        self.timer.setInterval(int(1000 // np.clip(qt_ui.settings.display_fps.get(), 1.0, 500.0)))
        self.latency = qt_ui.settings.display_latency.get() / 1000.0

    position_updated = QtCore.Signal(float, float, float)  # a, b, c
