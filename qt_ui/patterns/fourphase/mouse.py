"""
Mouse Pattern for Fourphase
"""
from qt_ui.patterns.fourphase.base import FourphasePattern
from stim_math.axis import AbstractAxis

class MousePattern(FourphasePattern):
    def __init__(self,
                 intensity_a: AbstractAxis,
                 intensity_b: AbstractAxis,
                 intensity_c: AbstractAxis,
                 intensity_d: AbstractAxis):
        super().__init__()
        self.intensity_a = intensity_a
        self.intensity_b = intensity_b
        self.intensity_c = intensity_c
        self.intensity_d = intensity_d
        self.a = 0.9999    # hack to force display update on load
        self.b = 1
        self.c = 1
        self.d = 1

    def name(self):
        return "mouse (TODO)"

    def mouse_event(self, a, b, c, d):
        self.intensity_a.add(a)
        self.intensity_b.add(b)
        self.intensity_c.add(c)
        self.intensity_d.add(d)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def update(self, dt: float):
        return self.a, self.b, self.c, self.d

    def last_position_is_mouse_position(self):
        pos = (self.a, self.b, self.c, self.d)
        axis = (self.intensity_a.last_value(), self.intensity_b.last_value(),
                self.intensity_c.last_value(), self.intensity_d.last_value())
        return pos == axis
