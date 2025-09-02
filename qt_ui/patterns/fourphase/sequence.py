"""
Sequence Pattern for Fourphase
"""
import numpy as np
from qt_ui.patterns.fourphase.base import FourphasePattern

class SequencePattern(FourphasePattern):
    def __init__(self, name, sequence: list):
        super().__init__()
        self._name = name
        self.sequence = np.vstack((sequence, sequence, sequence[0]))
        self.index = 0

        for i in range(1, len(self.sequence)):
            dist_1 = np.linalg.norm(self.sequence[i] - self.sequence[i-1])
            dist_2 = np.linalg.norm(self.sequence[i] + self.sequence[i-1])
            if dist_2 < dist_1:
                self.sequence[i] *= -1

    def name(self):
        return self._name

    def update(self, dt: float):
        self.index = (self.index + dt / 2) % (len(self.sequence) - 1)
        index = self.index
        x = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 0])
        y = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 1])
        z = np.interp(index, np.arange(len(self.sequence)), self.sequence[:, 2])

        xyz = np.array([x, y, z])
        xyz /= np.linalg.norm(xyz)
        return xyz
