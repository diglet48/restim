from dataclasses import dataclass
import numpy as np

from stim_math.sensors.imu import HighPass

@dataclass
class AS5311Data:
    x: float    # position in meters


class AS5311Algorithm:
    def __init__(self, axis_range, axis_reduction):
        self.axis_range = axis_range
        self.axis_reduction = axis_reduction

        self.position = 0
        self.position_hi = HighPass(0.1, 50)
        self.position_filterd = 0

    def update(self, data: AS5311Data):
        self.position = data.x
        self.position_filterd = self.position_hi.update(data.x)

    def transform_threephase(self, volume: float, alpha: float, beta: float):
        reduction = self.axis_reduction.last_value()
        max_range = self.axis_range.last_value() * 1e-6
        if max_range >= 1e-6 and reduction >= 0.01:

            f = np.clip(self.position_filterd / max_range, 0, 1)
            f = np.interp(f, [0, 1], [1 - reduction, 1])

            volume = volume * f

        return volume, alpha, beta


