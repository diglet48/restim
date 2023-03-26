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

        self.doubleSpinBox_volume.valueChanged.connect(self.updateVolume)

    volumeChanged = QtCore.pyqtSignal(float)

    def timeout(self):
        t = time.time()
        dt = max(0.0, t - self.last_update_time)

        if not self.radioButton_enabled.isChecked():
            self.last_update_time = t
            return

        max_change = self.doubleSpinBox_rate.value() * dt / 60
        value = self.doubleSpinBox_volume.value()
        target = self.doubleSpinBox_target_volume.value()
        self.doubleSpinBox_volume.setValue(
            np.clip(
                target,
                value - max_change,
                value + max_change,
            )
        )

        if value != self.doubleSpinBox_volume.value():
            self.last_update_time = t

    def updateVolume(self, _=None):
        self.volumeChanged.emit(
            np.clip(self.doubleSpinBox_volume.value() / 100, 0.0, 1.0)
        )
