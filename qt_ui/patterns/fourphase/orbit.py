"""
Orbit Pattern for Fourphase
"""
import numpy as np
from qt_ui.patterns.fourphase.base import FourphasePattern

class OrbitPattern(FourphasePattern):
    def __init__(self, name, axis):
        super().__init__()
        self._name = name
        self.axis = axis
        self.dir1 = np.linalg.cross(axis, [.5, .7, .999])
        self.dir2 = np.linalg.cross(axis, self.dir1)
        self.dir1 /= np.linalg.norm(self.dir1)
        self.dir2 /= np.linalg.norm(self.dir2)
        self.angle = 0

    def name(self):
        return self._name

    def update(self, dt: float):
        self.angle = self.angle + dt * 1
        return self.dir1 * np.cos(self.angle) + self.dir2 * np.sin(self.angle)
