import numpy as np


class SineModulation:
    def __init__(self, hz, modulation):
        self.hz = hz
        self.modulation = modulation

    def modulate(self, timeline, L, R):
        modulation = (np.sin(timeline * (2 * np.pi * self.hz)) - 1) * 0.5 * self.modulation + 1.0
        return L * modulation, R * modulation
