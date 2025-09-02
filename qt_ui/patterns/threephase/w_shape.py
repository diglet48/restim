"""
W Shape Pattern - Complex W-shaped movement with multiple peaks and valleys
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="complex")
class WShapePattern(ThreephasePattern):
    display_name = "W Shape"
    description = "Complex W-shaped pattern with multiple peaks and valleys. Higher base speed with intricate path changes. Provides varied, unpredictable stimulation with multiple transition points."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        self.time = self.time + dt * 2 * self.velocity  # Base speed doubled
        
        # Create a full W cycle (4π for complete W with two V shapes)
        cycle_time = self.time % (4 * np.pi)
        phase = int(cycle_time / np.pi)  # 0, 1, 2, 3
        phase_progress = (cycle_time % np.pi) / np.pi  # 0 to 1 within each phase
        
        if phase == 0:
            # First V forward: center (0,1) → right valley (0.5,0) → right peak (1,1)
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = 0.5 + t * 0.5
                alpha = t
        elif phase == 1:
            # First V backward: right peak (1,1) → right valley (0.5,0) → center (0,1)
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = 1 - t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = 0.5 - t * 0.5
                alpha = t
        elif phase == 2:
            # Second V forward: center (0,1) → left valley (-0.5,0) → left peak (-1,1)
            if phase_progress <= 0.5:
                t = phase_progress * 2
                beta = -t * 0.5
                alpha = 1 - t
            else:
                t = (phase_progress - 0.5) * 2
                beta = -0.5 - t * 0.5
                alpha = t
        else:  # phase == 3
            # Second V backward: left peak (-1,1) → left valley (-0.5,0) → center (0,1)
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
