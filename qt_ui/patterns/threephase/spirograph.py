"""
Spirograph Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="mathematical")
class SpirographPattern(ThreephasePattern):
    display_name = "Spirograph"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.R = 3.0  # Radius of fixed circle
        self.r = 1.0  # Radius of rolling circle
        self.d = 0.7  # Distance from center of rolling circle to drawing point

    def update(self, dt: float):
        """Update spirograph position using classic cycloid equations"""
        self.time = self.time + dt * self.velocity
        
        # Classic spirograph/cycloid equations
        t = self.time
        alpha = (self.R + self.r) * np.cos(t) - self.d * np.cos((self.R + self.r) / self.r * t)
        beta = (self.R + self.r) * np.sin(t) - self.d * np.sin((self.R + self.r) / self.r * t)
        
        # Normalize to -1 to 1 range
        max_val = (self.R + self.r + self.d)
        alpha = alpha / max_val * 0.8
        beta = beta / max_val * 0.8
        
        return alpha * self.amplitude, beta * self.amplitude
