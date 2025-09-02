"""
Butterfly Curve Pattern - Artistic butterfly wing mathematical pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="mathematical")
class ButterflyPattern(ThreephasePattern):
    display_name = "Butterfly Curve"
    description = "Artistic butterfly wing pattern based on mathematical curves. Complex, elegant motion with wing-like symmetry. Creates sophisticated, artistic stimulation paths."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        """Update butterfly pattern using classic butterfly curve equations"""
        self.time = self.time + dt * self.velocity * 0.5  # Slower for detail
        
        # Classic butterfly curve parametric equations
        t = self.time
        exp_cos = np.exp(np.cos(t))
        alpha = np.sin(t) * (exp_cos - 2 * np.cos(4 * t) - np.sin(t/12)**5)
        beta = np.cos(t) * (exp_cos - 2 * np.cos(4 * t) - np.sin(t/12)**5)
        
        # Normalize to fit in -1 to 1 range
        scale = 0.15
        alpha = alpha * scale
        beta = beta * scale
        
        return alpha * self.amplitude, beta * self.amplitude

