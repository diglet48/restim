"""
Lightning Strike Pattern - Sudden intense strikes with quiet periods
"""
import numpy as np
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern


@register_pattern(category="experimental")
class LightningStrikePattern(ThreephasePattern):
    display_name = "Lightning Strike"
    description = "Sudden intense strikes with quiet periods"
    
    def __init__(self, amplitude=1.0, velocity=1.0):
        super().__init__(amplitude, velocity)
        self.time = 0
        self.last_strike_time = 0
        self.strike_duration = 0.15  # Quick strikes
        self.strike_interval = 2.5   # Random interval between strikes
        self.in_strike = False

    def update(self, dt: float):
        self.time += dt * self.velocity
        
        # Determine if we should start a new strike
        if not self.in_strike and (self.time - self.last_strike_time) > self.strike_interval:
            self.in_strike = True
            self.last_strike_time = self.time
            # Randomize next interval using pseudo-random based on time
            pseudo_rand = abs(np.sin(self.time * 17.543)) * abs(np.cos(self.time * 23.891))
            self.strike_interval = 1.0 + pseudo_rand * 3.0
        
        # End strike after duration
        if self.in_strike and (self.time - self.last_strike_time) > self.strike_duration:
            self.in_strike = False
        
        if self.in_strike:
            # Sharp, fast, erratic movements during strike
            strike_progress = (self.time - self.last_strike_time) / self.strike_duration
            intensity = np.sin(strike_progress * np.pi) * 2.0  # Peak in middle
            
            # Jagged, unpredictable motion
            alpha = intensity * (0.5 + 0.8 * np.sin(self.time * 45))
            beta = intensity * 0.4 * np.cos(self.time * 38 + np.pi/3)
            
            # Add sharp directional changes
            if int(self.time * 50) % 3 == 0:  # Change direction rapidly
                alpha *= -0.7
            if int(self.time * 43) % 4 == 0:
                beta *= -0.9
                
        else:
            # Calm between strikes - minimal movement
            alpha = 0.1 * np.sin(self.time * 0.8)
            beta = 0.05 * np.cos(self.time * 0.6)
        
        return alpha * self.amplitude, beta * self.amplitude

