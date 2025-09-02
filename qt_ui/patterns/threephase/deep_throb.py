"""
Deep Throb Pattern - Slow, deep pulsing with powerful rhythm
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="experimental")
class DeepThrobPattern(ThreephasePattern):
    display_name = "Deep Throb"
    description = "Slow, deep pulsing with powerful rhythm"
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0

    def update(self, dt: float):
        self.time += dt * self.velocity * 0.4  # Slow, powerful rhythm
        
        # Primary throbbing motion - slow, deep, penetrating
        throb_cycle = (self.time * 0.8) % (2 * np.pi)
        
        # Create a powerful, smooth throbbing motion
        if throb_cycle < np.pi:
            # Rising phase - building intensity
            throb_progress = throb_cycle / np.pi
            throb_intensity = np.sin(throb_progress * np.pi) ** 2  # Smooth curve
        else:
            # Falling phase - gradual release
            throb_progress = (throb_cycle - np.pi) / np.pi
            throb_intensity = (1.0 - throb_progress) ** 2  # Smooth decay
        
        # Apply throbbing to Alpha (primary penetration axis)
        # Extended range to go negative on downward motion
        base_alpha = -0.2 + 1.3 * throb_intensity  # -0.2 to 1.1 range (extends to negative)
        
        # Add depth variation - occasionally goes deeper
        depth_cycle = (self.time * 0.2) % (2 * np.pi)
        if depth_cycle < np.pi * 0.3:  # 30% of cycle
            depth_modifier = 1.0 + 0.4 * np.sin(depth_cycle / (np.pi * 0.3) * np.pi)
        else:
            depth_modifier = 1.0
        
        alpha = base_alpha * depth_modifier
        
        # Minimal Beta movement - focused penetration
        beta = 0.1 * np.sin(self.time * 0.6) + 0.05 * np.sin(self.time * 1.1)
        
        # Add powerful pulses during peak intensity
        if throb_intensity > 0.8:
            pulse_strength = (throb_intensity - 0.8) / 0.2  # 0 to 1
            pulse_alpha = 0.2 * pulse_strength * np.sin(self.time * 8.0)
            pulse_beta = 0.1 * pulse_strength * np.cos(self.time * 6.5)
            alpha += pulse_alpha
            beta += pulse_beta
        
        # Ensure powerful but controlled movement - extended negative range
        alpha = np.clip(alpha, -0.5, 1.3)  # Now extends to -0.5 as requested
        beta = np.clip(beta, -0.3, 0.3)
        
        return alpha * self.amplitude, beta * self.amplitude

