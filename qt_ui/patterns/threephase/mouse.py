"""
Mouse Pattern
"""
from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern
from stim_math.axis import AbstractAxis

@register_pattern(category="manual")
class MousePattern(ThreephasePattern):
    display_name = "Mouse"
    description = ""
    category = "manual"
    def __init__(self, alpha: AbstractAxis = None, beta: AbstractAxis = None, amplitude: float = 1.0, velocity: float = 1.0):
        super().__init__(amplitude=amplitude, velocity=velocity)
        self.alpha = alpha
        self.beta = beta
        self.x = 0.00001
        self.y = 0
    def mouse_event(self, x, y):
        if self.alpha is not None:
            self.alpha.add(x)
        if self.beta is not None:
            self.beta.add(y)
        self.x = x
        self.y = y
    def update(self, dt: float):
        return self.x * self.amplitude, self.y * self.amplitude
    def last_position_is_mouse_position(self):
        if self.alpha is not None and self.beta is not None:
            return (self.x, self.y) == (self.alpha.last_value(), self.beta.last_value())
        return False
