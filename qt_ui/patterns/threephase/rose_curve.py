"""
Rose Curve Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="mathematical")
class RoseCurvePattern(ThreephasePattern):
    display_name = "Rose Curve"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.n = 5  # Number of petals

    def update(self, dt: float):
        """Update rose curve position using polar rose equations"""
        self.time = self.time + dt * self.velocity
        
        # Rose curve equation: r = cos(n*θ)
        theta = self.time
        r = abs(np.cos(self.n * theta))
        
        alpha = r * np.cos(theta)
        beta = r * np.sin(theta)
        
        return alpha * self.amplitude, beta * self.amplitude

