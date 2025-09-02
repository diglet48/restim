"""
Micro Circles Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="basic")
class MicroCirclesPattern(ThreephasePattern):
    display_name = "Micro Circles"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.origin_alpha = 0
        self.origin_beta = 0
        self.circle_radius = 0.15  # Small circles

    def update(self, dt: float):
        self.time += dt * self.velocity
        
        # Slowly drift the origin of the micro circles
        self.origin_alpha = 0.4 * np.sin(self.time * 0.1) + 0.3 * np.sin(self.time * 0.07)
        self.origin_beta = 0.3 * np.cos(self.time * 0.08) + 0.2 * np.cos(self.time * 0.12)
        
        # Create small circular motion around the drifting origin
        circle_alpha = self.circle_radius * np.cos(self.time * 4.0)
        circle_beta = self.circle_radius * np.sin(self.time * 4.0)
        
        # Add subtle variations in circle size
        size_mod = 0.8 + 0.4 * np.sin(self.time * 0.3)
        circle_alpha *= size_mod
        circle_beta *= size_mod
        
        # Occasionally add micro-tremors
        if int(self.time * 2) % 7 == 0:
            tremor_alpha = 0.02 * np.sin(self.time * 25)
            tremor_beta = 0.02 * np.cos(self.time * 27)
        else:
            tremor_alpha = tremor_beta = 0
        
        alpha = self.origin_alpha + circle_alpha + tremor_alpha
        beta = self.origin_beta + circle_beta + tremor_beta
        
        return alpha * self.amplitude, beta * self.amplitude
