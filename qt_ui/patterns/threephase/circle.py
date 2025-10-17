"""
Circle Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern

@register_pattern(category="mathematical")
class CirclePattern(ThreephasePattern):
    display_name = "Circle"
    description = ""
    category = "mathematical"
    def __init__(self, amplitude: float = 1.0, velocity: float = 1.0):
        super().__init__(amplitude=amplitude, velocity=velocity)
        self.angle = 0
    def update(self, dt: float):
        self.angle += dt * self.velocity
        x = np.cos(self.angle) * self.amplitude
        y = np.sin(self.angle) * self.amplitude
        return x, y
