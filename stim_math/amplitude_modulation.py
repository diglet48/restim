import numpy as np


class SineModulation:
    def __init__(self, sine, modulation):
        self.sine = sine
        self.modulation = modulation

    def modulate(self, L, R):
        modulation = (self.sine - 1) * 0.5 * self.modulation + 1.0
        return L * modulation, R * modulation
