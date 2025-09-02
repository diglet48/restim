"""
Figure Eight Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="basic")
class FigureEightPattern(ThreephasePattern):
    display_name = "Figure 8"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.angle = 0

    def update(self, dt: float):
        """Update figure-8 position"""
        self.angle = self.angle + dt * self.velocity
        # Parametric equations for figure-8
        alpha = np.sin(self.angle)  # Y component
        beta = 0.5 * np.sin(2 * self.angle)  # X component
        return alpha * self.amplitude, beta * self.amplitude
