"""
Mouse Pattern for Fourphase
"""
from qt_ui.patterns.fourphase.base import FourphasePattern
from stim_math.axis import AbstractAxis

class MousePattern(FourphasePattern):
    def __init__(self, alpha: AbstractAxis, beta: AbstractAxis, gamma: AbstractAxis):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.x = 0.00001    # hack to force display update on load
        self.y = 0
        self.z = 0

    def name(self):
        return "mouse"

    def mouse_event(self, x, y, z):
        self.alpha.add(x)
        self.beta.add(y)
        self.gamma.add(z)
        self.x = x
        self.y = y
        self.z = z

    def update(self, dt: float):
        return self.x, self.y, self.z

    def last_position_is_mouse_position(self):
        return (self.x, self.y, self.z) == (self.alpha.last_value(), self.beta.last_value(), self.gamma.last_value())
