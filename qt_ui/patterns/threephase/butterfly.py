"""
Butterfly Curve Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="mathematical")
class ButterflyPattern(ThreephasePattern):
    display_name = "Butterfly Curve"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        """Update butterfly pattern"""
        self.time = self.time + dt * self.velocity * 0.5
        
        # Butterfly curve parametric equations
        t = self.time
        exp_cos = np.exp(np.cos(t))
        alpha = np.sin(t) * (exp_cos - 2 * np.cos(4 * t) - np.sin(t/12)**5)
        beta = np.cos(t) * (exp_cos - 2 * np.cos(4 * t) - np.sin(t/12)**5)
        
        # Normalize to range
        scale = 0.15
        alpha = alpha * scale
        beta = beta * scale
        
        return alpha * self.amplitude, beta * self.amplitude

