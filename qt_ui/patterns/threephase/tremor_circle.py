"""
Tremor Circle Pattern - Circular motion with tremor-like micro-shakes
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="complex")
class TremorCirclePattern(ThreephasePattern):
    display_name = "Tremor Circle"
    description = "Circular motion overlaid with fine tremor-like micro-shakes. Base circular movement modulated by high-frequency oscillations. Natural, subtle vibratory motion."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        self.time = self.time + dt * self.velocity
        
        # Base circular motion
        circle_period = 6.0
        circle_angle = (self.time / circle_period) * 2 * np.pi
        
        base_alpha = 0.6 * np.cos(circle_angle)
        base_beta = 0.6 * np.sin(circle_angle)
        
        # Tremor modulation - high frequency, low amplitude
        tremor_freq1 = 25.0
        tremor_freq2 = 31.5
        tremor_intensity = 0.08
        
        tremor_alpha = tremor_intensity * (
            np.sin(self.time * tremor_freq1) * 0.6 +
            np.sin(self.time * tremor_freq2 * 1.3) * 0.4
        )
        tremor_beta = tremor_intensity * (
            np.cos(self.time * tremor_freq1 * 1.1) * 0.6 +
            np.cos(self.time * tremor_freq2 * 0.9) * 0.4
        )
        
        # Amplitude modulation for tremor realism
        tremor_envelope = 0.8 + 0.2 * np.sin(self.time * 0.7)
        tremor_alpha *= tremor_envelope
        tremor_beta *= tremor_envelope
        
        alpha = base_alpha + tremor_alpha
        beta = base_beta + tremor_beta
        
        alpha = np.clip(alpha, -1, 1)
        beta = np.clip(beta, -1, 1)
        
        return alpha * self.amplitude, beta * self.amplitude
