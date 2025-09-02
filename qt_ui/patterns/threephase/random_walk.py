"""
Random Walk Pattern - Unpredictable wandering motion with center-pull
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="experimental")
class RandomWalkPattern(ThreephasePattern):
    display_name = "Random Walk"
    description = "Unpredictable wandering motion with pseudo-random direction changes. Includes center-pull to prevent drift. Creates natural, organic, unpredictable movement patterns."
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.alpha_pos = 0.0
        self.beta_pos = 0.0
        self.center_pull_strength = 0.003
        self.noise_strength = 0.8  # Reduced from 3.5 to prevent excessive buildup

    def _pseudo_random(self, t):
        """Simple pseudo-random function based on time"""
        x = np.sin(t * 37.12345) * np.cos(t * 23.67891)
        y = np.sin(t * 41.98765) * np.cos(t * 19.43210)
        return x, y

    def update(self, dt: float):
        self.time = self.time + dt * self.velocity
        
        # Get pseudo-random direction
        rand_x, rand_y = self._pseudo_random(self.time)
        
        # Random walk with gentle drift
        self.alpha_pos += rand_x * self.noise_strength * dt
        self.beta_pos += rand_y * self.noise_strength * dt
        
        # Pull towards center to prevent drift away
        self.alpha_pos -= self.alpha_pos * self.center_pull_strength
        self.beta_pos -= self.beta_pos * self.center_pull_strength
        
        # Clamp to bounds that work well with amplitude scaling
        self.alpha_pos = np.clip(self.alpha_pos, -1.0, 1.0)
        self.beta_pos = np.clip(self.beta_pos, -1.0, 1.0)
        
        return self.alpha_pos * self.amplitude, self.beta_pos * self.amplitude

