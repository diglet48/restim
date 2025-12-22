"""
Panning Pattern 2
"""

import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="basic")
class PanningPattern2(ThreephasePattern):
    display_name = "Tri-Phase panning (∧)"
    description = ""

    def __init__(
        self, amplitude: float = 1.0, velocity: float = 0.5, linger_power: float = 1.0
    ):
        super().__init__(amplitude, velocity)
        self.time = 0.0
        self.linger_power = max(1.0, linger_power)

    def update(self, dt: float):
        self.time += dt * self.velocity

        base = np.sin(2.0 * np.pi * self.time)

        alpha = 1 - np.abs(base) * 1.5
        beta = np.sqrt(3) * base / 2

        return alpha, beta
