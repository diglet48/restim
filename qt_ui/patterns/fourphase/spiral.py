"""
Spiral Pattern for Fourphase
"""
import numpy as np
from qt_ui.patterns.fourphase.base import FourphasePattern

class SpiralPattern(FourphasePattern):
    def __init__(self, name, axis):
        super().__init__()
        self._name = name
        self.axis = axis / np.linalg.norm(axis)
        self.dir1 = np.linalg.cross(axis, [.5, .7, .999])
        self.dir2 = np.linalg.cross(axis, self.dir1)
        self.dir1 /= np.linalg.norm(self.dir1)
        self.dir2 /= np.linalg.norm(self.dir2)
        self.angle = 0
        self.angle2 = 0

    def name(self):
        return self._name

    def update(self, dt: float):
        self.angle = self.angle + dt * 4
        self.angle2 = self.angle2 + dt * .23
        radius = np.sin(self.angle2) * 0.6
        vec = (self.axis +
               self.dir1 * np.cos(self.angle) * radius +
               self.dir2 * np.sin(self.angle) * radius)
        return vec / np.linalg.norm(vec)
