from abc import ABC, abstractmethod
import numpy as np
import time
import logging

from PySide6 import QtCore

from stim_math.axis import AbstractAxis, WriteProtectedAxis

logger = logging.getLogger('restim.motion_generation')


class ThreephasePattern(ABC):
    def __init__(self):
        ...

    def name(self):
        ...

    @abstractmethod
    def update(self, dt: float):
        ...


class MousePattern(ThreephasePattern):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0

    def name(self):
        return "mouse"

    def mouse_event(self, x, y):
        self.x = x
        self.y = y

    def update(self, dt: float):
        return self.x, self.y


class CirclePattern(ThreephasePattern):
    def __init__(self):
        super().__init__()
        self.angle = 0

    def name(self):
        return "Circle"

    def update(self, dt: float):
        self.angle = self.angle + dt * 1
        return np.cos(self.angle), np.sin(self.angle)


class ThreephaseMotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis):
        super().__init__(parent)
        self.alpha = alpha
        self.beta = beta

        self.script_alpha = None
        self.script_beta = None

        self.mouse_pattern = MousePattern()
        self.patterns = [
            self.mouse_pattern,
            CirclePattern(),
        ]
        self.pattern = self.mouse_pattern

        self.velocity = 1
        self.last_update_time = time.time()
        self.latency = 0    # TODO

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(int(1000 / 60.0))

        # def refreshSettings(self):
        #     self.timer.setInterval(int(1000 // np.clip(settings.display_fps.get(), 1.0, 500.0)))
        #     self.latency = settings.display_latency.get() / 1000.0

    def set_enable(self, enable):
        if enable:
            self.timer.start()
        else:
            self.timer.stop()

    def set_pattern(self, pattern):
        if issubclass(pattern.__class__, ThreephasePattern):
            self.pattern = pattern

    def set_scripts(self, alpha, beta):
        self.script_alpha = alpha if issubclass(alpha.__class__, WriteProtectedAxis) else None
        self.script_beta = beta if issubclass(beta.__class__, WriteProtectedAxis) else None

    def any_scripts_loaded(self):
        return (self.script_alpha, self.script_beta) != (None, None)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def timeout(self):
        dt = time.time() - self.last_update_time
        self.last_update_time = time.time()

        if not self.any_scripts_loaded():
            # update pattern, update display
            a, b = self.pattern.update(dt * self.velocity)
            self.alpha.add(a)
            self.beta.add(b)
            # TODO: latency?
            self.position_updated.emit(a, b)
        else:
            # update display with data from funscript
            a = self.script_alpha.interpolate(time.time() - self.latency)
            b = self.script_beta.interpolate(time.time() - self.latency)
            self.position_updated.emit(a, b)

    def mouse_event(self, a, b):
        if self.pattern == self.mouse_pattern and not self.any_scripts_loaded():
            self.mouse_pattern.mouse_event(a, b)
            self.alpha.add(a)
            self.beta.add(b)
            self.position_updated.emit(a, b)

    position_updated = QtCore.Signal(float, float)  # a, b

# TODO: re-instate old patterns and add more
"""
        if self.pattern == Pattern.A:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta), 0)
        elif self.pattern == Pattern.B:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta) * 0.5, np.cos(self.theta) * 3**.5/2)
        elif self.pattern == Pattern.C:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta) * 0.5, -np.cos(self.theta) * 3**.5/2)
        elif self.pattern == Pattern.LARGE_CIRCLE:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta), np.sin(self.theta))
        elif self.pattern == Pattern.MOUSE:
            return
"""