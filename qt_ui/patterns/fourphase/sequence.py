"""
Sequence Pattern for Fourphase
"""
import numpy as np
from qt_ui.patterns.fourphase.base import FourphasePattern

class SequencePattern(FourphasePattern):
    def __init__(self, name, sequence: list):
        super().__init__()
        self._name = name
        self.sequence = np.vstack((sequence, sequence[0]))
        self.index = 0

    def name(self):
        return self._name

    def update(self, dt: float):
        self.index = (self.index + dt / 2) % (len(self.sequence) - 1)
        xp = np.arange(len(self.sequence))
        index = self.index
        a = np.interp(index, xp, self.sequence[:, 0])
        b = np.interp(index, xp, self.sequence[:, 1])
        c = np.interp(index, xp, self.sequence[:, 2])
        d = np.interp(index, xp, self.sequence[:, 3])

        return np.array([a, b, c, d])
