"""
Jerky Stroke Pattern - Vertical stroking with sudden jerky interruptions
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="complex")
class JerkyStrokePattern(ThreephasePattern):
    display_name = "Jerky Stroke"
    description = "Vertical stroking with sudden jerky interruptions. Combines slow buildup with quick return phases and micro-jerk overlays. Irregular, surprising motion."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.jerk_timer = 0

    def update(self, dt: float):
        self.time = self.time + dt * self.velocity
        self.jerk_timer += dt * self.velocity * 5
        
        # Main vertical stroking motion
        stroke_cycle = 3.0
        stroke_progress = (self.time % stroke_cycle) / stroke_cycle
        
        # Create jerky, non-linear stroke progression
        if stroke_progress < 0.6:
            smooth_progress = (stroke_progress / 0.6) ** 0.3
            alpha = smooth_progress * 2 - 1
        else:
            return_progress = 1 - (1 - (stroke_progress - 0.6) / 0.4) ** 2
            alpha = 1 - return_progress * 2
        
        # Add jerky micro-movements
        jerk_intensity = 0.08
        if (self.jerk_timer % 1.0) < 0.15:
            jerk_modifier = np.sin(self.jerk_timer * 30) * jerk_intensity
            alpha += jerk_modifier
        
        # Horizontal positioning with variation
        beta = 0.3 * np.sin(self.time * 1.3) + 0.1 * np.sin(self.time * 7.1)
        
        alpha = np.clip(alpha, -1, 1)
        beta = np.clip(beta, -1, 1)
        
        return alpha * self.amplitude, beta * self.amplitude

