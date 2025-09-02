"""
Vertical Oscillation Pattern - Layered movement with slow vertical and rapid oscillations
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="basic")
class VerticalOscillationPattern(ThreephasePattern):
    display_name = "Vertical Oscillation"
    description = "Combines slow vertical movement (2-second cycles) with rapid oscillations (5Hz). Creates complex layered stimulation with both rhythmic and vibrational components."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        """Update position with layered vertical movement and oscillations"""
        self.time = self.time + dt * self.velocity
        # Alpha: slow vertical movement, 2 second cycles (0.5 Hz)
        alpha = np.sin(2 * np.pi * 0.5 * self.time)  # 0.5 Hz = 2 second cycle
        # Beta: rapid oscillations, 5 oscillations per second (5 Hz)
        beta = 0.2 * np.sin(2 * np.pi * 5 * self.time)  # 5 Hz oscillations
        return alpha * self.amplitude, beta * self.amplitude
