"""
Figure Eight Pattern - Lemniscate motion
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="basic")
class FigureEightPattern(ThreephasePattern):
    display_name = "Figure 8"
    description = "Lemniscate (figure-8) pattern creating flowing, dynamic motion. Medium speed with crossing loops. Provides varied stimulation with changing directions and intensities."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.angle = 0

    def update(self, dt: float):
        """Update figure-8 position using parametric lemniscate equations"""
        self.angle = self.angle + dt * self.velocity
        # Parametric equations for figure-8 (lemniscate)
        alpha = np.sin(self.angle)  # Y component: -1 to 1
        beta = 0.5 * np.sin(2 * self.angle)  # X component: -0.5 to 0.5
        return alpha * self.amplitude, beta * self.amplitude
