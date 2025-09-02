"""
W Shape Pattern
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="complex")
class WShapePattern(ThreephasePattern):
    display_name = "W Shape"
    description = ""
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        self.time = self.time + dt * 2 * self.velocity  # Base speed doubled
        
        # Create a full W cycle
        cycle_time = self.time % (4 * np.pi)
        phase = int(cycle_time / np.pi)  # 0, 1, 2, 3
        phase_progress = (cycle_time % np.pi) / np.pi  # 0 to 1
        
        if phase == 0:
            # First V forward
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = 0.5 + t * 0.5
                alpha = t
        elif phase == 1:
            # First V backward
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = 1 - t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = 0.5 - t * 0.5
                alpha = t
        elif phase == 2:
            # Second V forward
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = -t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = -0.5 - t * 0.5
                alpha = t
        else:  # phase == 3
            # Second V backward
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = -1 + t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = -0.5 + t * 0.5
                alpha = t
        
        alpha = np.clip(alpha, 0, 1)
        beta = np.clip(beta, -1, 1)
        return alpha * self.amplitude, beta * self.amplitude
