import numpy as np
import time
import logging

from PySide6 import QtCore

from stim_math.axis import AbstractAxis

logger = logging.getLogger('restim.motion_generation')


class Pattern:
    MOUSE = 0
    A = 1
    B = 2
    C = 3
    LARGE_CIRCLE = 4


class MotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis):
        super().__init__(parent)

        self.alpha = alpha
        self.beta = beta

        self.theta = 0
        self.velocity = 1.0
        self.pattern = Pattern.MOUSE
        self.last_update_time = time.time()

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_position)
        timer.start(int(1000 / 60.0))

    def patternChanged(self, pattern):
        new_pattern = {
            'Mouse': Pattern.MOUSE,
            'Circle': Pattern.LARGE_CIRCLE,
            'A': Pattern.A,
            'B': Pattern.B,
            'C': Pattern.C,
        }
        self.pattern = new_pattern[pattern]
        pass

    def velocityChanged(self, velocity):
        self.velocity = velocity

    def update_position(self):
        elapsed = time.time() - self.last_update_time
        self.last_update_time = time.time()

        xy = None

        if self.pattern == Pattern.A:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta), 0)
        elif self.pattern == Pattern.B:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta) * 0.5, np.cos(self.theta) * 3**.5/2)
        elif self.pattern == Pattern.C:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta) * 0.5, -np.cos(self.theta) * 3**.5/2)
        elif self.pattern == Pattern.LARGE_CIRCLE:
            self.theta += elapsed * self.velocity
            xy = (np.cos(self.theta), np.sin(self.theta))
        elif self.pattern == Pattern.MOUSE:
            return
        else:
            logger.error(f'unrecognized pattern: {self.pattern}')
            return

        self.alpha.add(xy[0])
        self.beta.add(xy[1])

    def updateMousePosition(self, x, y):
        if self.pattern == Pattern.MOUSE:
            self.alpha.add(x)
            self.beta.add(y)

