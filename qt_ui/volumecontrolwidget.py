from __future__ import unicode_literals

import time
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings

from qt_ui.volume_control_widget_ui import Ui_VolumeControlForm
from stim_math.threephase_parameter_manager import ThreephaseParameterManager

SETTING_INACTIVITY_RAMP_TIME = 'volume/inactivity_ramp_time'
SETTING_INACTIVITY_INACTIVE_THRESHOLD = 'volume/inactivity_inactive_threshold'


class VolumeControlWidget(QtWidgets.QWidget, Ui_VolumeControlForm):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.settings = QSettings()

        self.config: ThreephaseParameterManager = None

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timeout)
        timer.start(int(1000 / 10.0))
        self.last_update_time = time.time()
        self.remainder = 0

        self.doubleSpinBox_volume.valueChanged.connect(self.updateVolume)

        self.last_axis_update_time = time.time()
        self.last_axis_values = (0, 0)
        self.inactivity_volume_progress = 0

        self.doubleSpinBox_inactivity_threshold.setValue(
            self.settings.value(SETTING_INACTIVITY_INACTIVE_THRESHOLD, 2.0, float)
        )
        self.doubleSpinBox_inactivity_ramp_time.setValue(
            self.settings.value(SETTING_INACTIVITY_RAMP_TIME, 3.0, float)
        )

        self.doubleSpinBox_inactivity_threshold.valueChanged.connect(self.settings_changed)
        self.doubleSpinBox_inactivity_ramp_time.valueChanged.connect(self.settings_changed)

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def timeout(self):
        t = time.time()
        dt = max(0.0, t - self.last_update_time)
        self.last_update_time = t

        self.timeout_ramp(dt)
        self.timeout_inactivity(dt)

    def timeout_ramp(self, dt: float):
        if not self.checkBox_ramp_enabled.isChecked():
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

    def timeout_inactivity(self, dt: float):
        if not self.config:
            return

        axis_values = (self.config.alpha.interpolate(time.time()),
                       self.config.beta.interpolate(time.time()),
                       self.config.e1.interpolate(time.time()),
                       self.config.e2.interpolate(time.time()),
                       self.config.e3.interpolate(time.time()),
                       self.config.e4.interpolate(time.time()),
                       self.config.e5.interpolate(time.time()),
                       )

        if axis_values != self.last_axis_values:
            self.last_axis_update_time = time.time()
        self.last_axis_values = axis_values
        active = self.last_axis_update_time >= (time.time() - self.doubleSpinBox_inactivity_threshold.value())

        if not active:
            try:
                self.inactivity_volume_progress = np.clip(
                    self.inactivity_volume_progress + (dt / self.doubleSpinBox_inactivity_ramp_time.value()),
                    0, 1
                )
            except ZeroDivisionError:
                self.inactivity_volume_progress = 1
        else: # active
            try:
                self.inactivity_volume_progress = np.clip(
                    self.inactivity_volume_progress - (dt / self.doubleSpinBox_inactivity_ramp_time.value()),
                    0, 1
                )
            except ZeroDivisionError:
                self.inactivity_volume_progress = 0

        self.inactivityVolumeChanged.emit(1 - self.inactivity_volume_progress * self.doubleSpinBox_inactivity_volume.value() / 100)

    def updateVolume(self, _=None):
        self.rampVolumeChanged.emit(
            np.clip(self.doubleSpinBox_volume.value() / 100, 0.0, 1.0)
        )

    def settings_changed(self):
        self.settings.setValue(SETTING_INACTIVITY_INACTIVE_THRESHOLD, self.doubleSpinBox_inactivity_threshold.value())
        self.settings.setValue(SETTING_INACTIVITY_RAMP_TIME, self.doubleSpinBox_inactivity_ramp_time.value())

    rampVolumeChanged = QtCore.pyqtSignal(float)
    inactivityVolumeChanged = QtCore.pyqtSignal(float)