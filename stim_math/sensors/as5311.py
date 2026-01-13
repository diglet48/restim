from dataclasses import dataclass
import numpy as np

from stim_math.sensors.imu import HighPass

@dataclass
class AS5311Data:
    x: float    # position in meters
