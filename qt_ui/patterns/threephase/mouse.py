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
