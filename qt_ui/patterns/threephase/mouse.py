"""
Mouse Pattern
"""
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern
from stim_math.axis import AbstractAxis
from PySide6.QtCore import Qt
import time
import numpy as np

@register_pattern(category="manual")
class MousePattern(ThreephasePattern):
    display_name = "Mouse"
    description = ""
    category = "manual"
    def __init__(self, alpha: AbstractAxis = None, beta: AbstractAxis = None, amplitude: float = 1.0, velocity: float = 1.0):
        super().__init__(amplitude=amplitude, velocity=velocity)
        self.alpha = alpha
        self.beta = beta
        self.x = 0.00001
        self.y = 0

        self.last_position_is_mouse_position = False
        self.is_drawing = False
        self.drawn_coordinates = []
        self.drawn_timestamps = []
        self.progress = 0

    def mouse_event(self, x, y, buttons, modifiers):
        dirty = False

        if self.is_drawing:
            if not buttons & Qt.MouseButton.LeftButton:
                # stop drawing
                self.is_drawing = False
                self.progress = 0
                dirty = True
        else:
            if buttons & Qt.MouseButton.LeftButton:
                # start drawing
                self.is_drawing = True
                self.drawn_coordinates = []
                self.drawn_timestamps = []

        if buttons & Qt.MouseButton.LeftButton:
            self.drawn_coordinates.append((x, y))
            self.drawn_timestamps.append(time.time())
            self.x = x
            self.y = y
            if self.alpha is not None:
                self.alpha.add(x)
            if self.beta is not None:
                self.beta.add(y)
            self.last_position_is_mouse_position = True
            dirty = True

        return dirty

    def update(self, dt: float):
        if self.is_drawing:
            return self.x, self.y
        if len(self.drawn_coordinates) <= 1:
            return self.x, self.y

        self.progress += dt
        self.progress = self.progress % (self.drawn_timestamps[-1] - self.drawn_timestamps[0])
        t = self.drawn_timestamps[0] + self.progress
        x = np.interp(t, self.drawn_timestamps, np.array(self.drawn_coordinates)[:, 0])
        y = np.interp(t, self.drawn_timestamps, np.array(self.drawn_coordinates)[:, 1])
        return x, y

    def has_tcode_updates(self):
        if self.last_position_is_mouse_position:
            p = (self.x, self.y)
            q = (self.alpha.last_value(), self.beta.last_value())
            self.last_position_is_mouse_position = p == q
        return not self.last_position_is_mouse_position

    def has_pattern(self):
        if self.is_drawing:
            return True
        if len(self.drawn_coordinates) <= 1:
            return False
        return True

    def path(self):
        return self.drawn_coordinates

    def clear_path(self):
        self.drawn_coordinates = []
        self.drawn_timestamps = []