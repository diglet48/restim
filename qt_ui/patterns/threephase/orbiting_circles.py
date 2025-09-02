"""
Orbiting Circles Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="complex")
class OrbitingCirclesPattern(ThreephasePattern):
    display_name = "Orbiting Circles"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        self.time = self.time + dt * self.velocity
        
        # Moving origin along Alpha axis
        origin_base_freq = 0.4
        origin_alpha = 0.7 * np.sin(self.time * origin_base_freq)
        
        # Add "lingering" at the sensitive spot (Alpha=1, Beta=0)
        linger_freq = 0.15
        linger_pull = 0.4 * np.exp(-((origin_alpha - 1.0)**2) * 5) * (1 + np.sin(self.time * linger_freq * 10))
        origin_alpha += linger_pull
        
        # Slight horizontal drift
        origin_beta = 0.15 * np.sin(self.time * 0.7) + 0.1 * np.cos(self.time * 1.3)
        
        # Varying diameter circles around the moving origin
        circle_freq = 3.0
        base_radius = 0.3
        
        # Radius varies with multiple harmonics
        radius_variation = 0.6 * (1 + 0.5 * np.sin(self.time * 0.8) + 0.3 * np.sin(self.time * 2.1))
        current_radius = base_radius * radius_variation
        
        # Circle motion
        circle_alpha = current_radius * np.cos(self.time * circle_freq)
        circle_beta = current_radius * np.sin(self.time * circle_freq)
        
        # Combine origin movement with circle
        final_alpha = origin_alpha + circle_alpha
        final_beta = origin_beta + circle_beta
        
        # Favor positive Alpha (sensitive area)
        final_alpha = np.clip(final_alpha, -1.2, 1.5)
        final_beta = np.clip(final_beta, -1.0, 1.0)
        
        return final_alpha * self.amplitude, final_beta * self.amplitude

