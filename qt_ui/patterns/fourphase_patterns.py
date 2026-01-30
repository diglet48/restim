import time
import logging
import numpy as np
from PySide6 import QtCore
import qt_ui.settings
from stim_math.axis import AbstractAxis, WriteProtectedAxis
from qt_ui.patterns.fourphase.mouse import MousePattern
from qt_ui.patterns.fourphase.orbit import OrbitPattern
from qt_ui.patterns.fourphase.sequence import SequencePattern
from qt_ui.patterns.fourphase.spiral import SpiralPattern
from qt_ui.widgets.fourphase_widget_stereographic import v1, v2, v3, v4

logger = logging.getLogger('restim.motion_generation')


class FourphaseMotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis, gamma: AbstractAxis):
        super().__init__(parent)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.script_alpha = None
        self.script_beta = None
        self.script_gamma = None

        # Instantiate MousePattern with axes
        self.mouse_pattern = MousePattern(alpha, beta, gamma)

        # Create patterns like the original implementation
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
        if isinstance(pattern, MousePattern):
            self.pattern = self.mouse_pattern
        elif pattern in self.patterns:
            self.pattern = pattern

    def set_scripts(self, alpha, beta, gamma):
        self.script_alpha = alpha if isinstance(alpha, WriteProtectedAxis) else None
        self.script_beta = beta if isinstance(beta, WriteProtectedAxis) else None
        self.script_gamma = gamma if isinstance(gamma, WriteProtectedAxis) else None

    def any_scripts_loaded(self):
        return (self.script_alpha, self.script_beta, self.script_gamma) != (None, None, None)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def timeout(self):
        dt = time.time() - self.last_update_time
        self.last_update_time = time.time()

        if not self.any_scripts_loaded():
            if isinstance(self.pattern, MousePattern):
                if self.pattern.last_position_is_mouse_position():
                    a = self.alpha.last_value()
                    b = self.beta.last_value()
                    c = self.gamma.last_value()
                else:
                    a = self.alpha.interpolate(time.time() - self.latency)
                    b = self.beta.interpolate(time.time() - self.latency)
                    c = self.gamma.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b, c)
            else:
                a, b, c = self.pattern.update(dt * self.velocity)
                self.alpha.add(a)
                self.beta.add(b)
                self.gamma.add(c)
                a = self.alpha.interpolate(time.time() - self.latency)
                b = self.beta.interpolate(time.time() - self.latency)
                c = self.gamma.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b, c)
        else:
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
