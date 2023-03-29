from __future__ import unicode_literals

import time
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtSvg

from qt_ui.volume_control_widget_ui import Ui_VolumeControlForm


class VolumeControlWidget(QtWidgets.QWidget, Ui_VolumeControlForm):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timeout)
        timer.start(int(1000 / 10.0))
        self.last_update_time = time.time()
        self.remainder = 0

        self.doubleSpinBox_volume.valueChanged.connect(self.updateVolume)

    volumeChanged = QtCore.pyqtSignal(float)

    def timeout(self):
        t = time.time()
        dt = max(0.0, t - self.last_update_time)
        self.last_update_time = t

        if not self.radioButton_enabled.isChecked():
            self.remainder = 0
            return

        change = self.doubleSpinBox_rate.value() * dt / 60
        value = self.doubleSpinBox_volume.value()
        target = self.doubleSpinBox_target_volume.value()
        if target < value:
            change *= -1

        change += self.remainder
        if change > 0:
            change = np.clip(change, 0, target - value)
        else:
            change = np.clip(change, target - value, 0)

        self.doubleSpinBox_volume.setValue(value + change)
        self.remainder = change - (self.doubleSpinBox_volume.value() - value)

    def updateVolume(self, _=None):
        self.volumeChanged.emit(
            np.clip(self.doubleSpinBox_volume.value() / 100, 0.0, 1.0)
        )
