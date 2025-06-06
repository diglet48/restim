from __future__ import unicode_literals

import time
import numpy as np
import math
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDoubleSpinBox

from qt_ui.axis_controller import AxisController
from qt_ui.volume_control_widget_ui import Ui_VolumeControlForm
from stim_math.audio_gen.params import VolumeParams
from stim_math.axis import create_temporal_axis, AbstractAxis, create_constant_axis
from qt_ui import settings


class VolumeControlWidget(QtWidgets.QWidget, Ui_VolumeControlForm):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.api_volume = create_temporal_axis(1.0)
        self.inactivity_volume = create_temporal_axis(1.0)
        self.master_volume = create_temporal_axis(settings.volume_default_level.get())
        self.external_volume = create_temporal_axis(1.0)
        self.axis_tau = create_constant_axis(settings.tau_us.get())
        self.volume = VolumeParams(
            api=self.api_volume,
            master=self.master_volume,
            inactivity=self.inactivity_volume,
            external=self.external_volume,
        )
        self.monitor_axis = []

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timeout)
        timer.start(int(1000 / 10.0))
        self.last_update_time = time.time()
        self.remainder = 0

        self.doubleSpinBox_volume = None
        self.doubleSpinBox_tau.setValue(settings.tau_us.get())

        self.last_axis_update_time = time.time()
        self.last_axis_values = (0, 0)
        self.inactivity_volume_progress = 0

        self.doubleSpinBox_inactivity_threshold.setValue(settings.volume_inactivity_threshold.get())
        self.doubleSpinBox_inactivity_ramp_time.setValue(settings.volume_ramp_time.get())
        self.doubleSpinBox_rate.setValue(settings.volume_increment_rate.get())

        self.doubleSpinBox_inactivity_threshold.valueChanged.connect(self.settings_changed)
        self.doubleSpinBox_inactivity_ramp_time.valueChanged.connect(self.settings_changed)
        self.doubleSpinBox_rate.valueChanged.connect(self.settings_changed)

        self.doubleSpinBox_target_volume.valueChanged.connect(self.refresh_message)
        self.doubleSpinBox_rate.valueChanged.connect(self.refresh_message)

        self.tau_controller = AxisController(self.doubleSpinBox_tau)
        self.tau_controller.link_axis(self.axis_tau)

    def link_volume_control(self, volume_control: QDoubleSpinBox):
        self.doubleSpinBox_volume = volume_control

        self.doubleSpinBox_volume.valueChanged.connect(self.updateVolume)
        self.doubleSpinBox_volume.valueChanged.connect(self.refresh_message)


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

        rate_per_second = self.doubleSpinBox_rate.value() / 60

        # linear. volume = v0 + r * t
        # change = rate_per_second * dt

        # exponential. volume = v0 * exp(r * t)
        change = self.doubleSpinBox_volume.value() * rate_per_second * dt / 100

        value = self.doubleSpinBox_volume.value()
        target = self.doubleSpinBox_target_volume.value()

        if target >= value:
            change += self.remainder
            change = np.clip(change, None, target - value)  # don't overshoot
        else:
            change *= -1
            change += self.remainder
            change = np.clip(change, target - value, None)  # don't overshoot

        self.doubleSpinBox_volume.setValue(value + change)
        self.remainder = change - (self.doubleSpinBox_volume.value() - value)

        self.refresh_message()

    def set_monitor_axis(self, axis: list[AbstractAxis]):
        self.monitor_axis = axis

    def timeout_inactivity(self, dt: float):
        axis_values = []
        for axis in self.monitor_axis:
            axis_values.append(axis.interpolate(time.time()))
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

        self.inactivity_volume.add(1 - self.inactivity_volume_progress * self.doubleSpinBox_inactivity_volume.value() / 100)

    def updateVolume(self, _=None):
        self.master_volume.add(np.clip(self.doubleSpinBox_volume.value() / 100, 0.0, 1.0))

    def refresh_message(self, _=None):
        try:
            target = self.doubleSpinBox_target_volume.value()
            volume = self.doubleSpinBox_volume.value()
            rate_per_second = self.doubleSpinBox_rate.value() / 60
            if target / volume:
                time_left = math.log(target / volume) / rate_per_second * 100
            else:
                time_left = np.inf
            time_left = np.abs(time_left)
            time_left = np.min((time_left, 9001 * 60))
            message = f"time until target: {np.round(time_left / 60, 1)} minutes."
        except (ZeroDivisionError, ValueError):
            message = f"time until target: never."
        self.checkBox_ramp_enabled.setText(message)

    def settings_changed(self):
        self.refresh_message()

    def save_settings(self):
        settings.volume_inactivity_threshold.set(self.doubleSpinBox_inactivity_threshold.value())
        settings.volume_ramp_time.set(self.doubleSpinBox_inactivity_ramp_time.value())
        settings.volume_increment_rate.set(self.doubleSpinBox_rate.value())
        settings.tau_us.set(self.doubleSpinBox_tau.value())