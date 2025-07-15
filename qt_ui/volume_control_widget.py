from __future__ import unicode_literals

import time
import numpy as np
import math
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDoubleSpinBox

from qt_ui.axis_controller import AxisController
from qt_ui.volume_control_widget_ui import Ui_VolumeControlForm
from qt_ui.widgets.volume_widget import VolumeWidget
from stim_math.audio_gen.params import VolumeParams
from stim_math.axis import create_temporal_axis, AbstractAxis, create_constant_axis, WriteProtectedAxis
from qt_ui import settings

update_interval_seconds = 0.1


class VolumeControlWidget(QtWidgets.QWidget, Ui_VolumeControlForm):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        # volume set by tcode
        self.axis_api_volume = create_temporal_axis(1.0)
        # volume set by funscript
        self.axis_funscript_volume = create_temporal_axis(1.0)
        # volume multiplier for the 'inactivity' feature
        self.axis_inactivity_volume = create_temporal_axis(1.0)
        # master volume, volume set in application. Slowly increases if ramp is used.
        self.axis_master_volume = create_temporal_axis(settings.volume_default_level.get())
        # volume set by tcode, used by external applications
        self.axis_external_volume = create_temporal_axis(1.0)

        self.axis_tau = create_constant_axis(settings.tau_us.get())

        self.monitor_axis = []

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.timeout)
        timer.start(int(update_interval_seconds * 1000))
        self.last_update_time = time.time()
        self.remainder = 0
        self.latency = 0

        self.doubleSpinBox_volume = None
        self.volume_widget: VolumeWidget = None
        self.doubleSpinBox_tau.setValue(settings.tau_us.get())

        self.last_axis_update_time = time.time()
        self.last_axis_values = (0, 0)
        self.inactivity_multiplier = 1
        self.slow_start_multiplier = 0
        self.playing = False

        self.doubleSpinBox_inactivity_threshold.setValue(settings.volume_inactivity_threshold.get())
        self.doubleSpinBox_inactivity_ramp_time.setValue(settings.volume_inactivity_time.get())
        self.doubleSpinBox_ramp_rate.setValue(settings.volume_ramp_increment_rate.get())
        self.doubleSpinBox_ramp_target.setValue(settings.volume_ramp_target.get() * 100)

        self.doubleSpinBox_slow_start.setValue(settings.volume_slow_start_time.get())

        self.doubleSpinBox_ramp_target.valueChanged.connect(self.refresh_message)
        self.doubleSpinBox_ramp_rate.valueChanged.connect(self.refresh_message)

        self.tau_controller = AxisController(self.doubleSpinBox_tau)
        self.tau_controller.link_axis(self.axis_tau)

    def link_volume_controls(self, volume_spinbox: QDoubleSpinBox, volume_bar: VolumeWidget):
        self.doubleSpinBox_volume = volume_spinbox

        self.doubleSpinBox_volume.valueChanged.connect(self.refresh_master_volume)
        self.doubleSpinBox_volume.valueChanged.connect(self.refresh_message)

        self.volume_widget = volume_bar

    def timeout(self):
        t = time.time()
        dt = max(0.0, t - self.last_update_time)
        self.last_update_time = t

        self.timeout_ramp(dt)
        self.timeout_inactivity(dt)

        master_volume = self.axis_master_volume.last_value()
        if self.playing:
            inactivity_volume = self.inactivity_multiplier * self.slow_start_multiplier
        else:
            # when not playing, fake the display so the user sees the volume after the start ramp
            inactivity_volume = self.inactivity_multiplier

        if issubclass(self.axis_funscript_volume.__class__, WriteProtectedAxis):
            api_volume = self.axis_funscript_volume.interpolate(time.time() - self.latency)
        else:
            api_volume = self.axis_api_volume.interpolate(time.time() - self.latency)
        external_volume = self.axis_external_volume.interpolate(time.time() - self.latency)
        self.volume_widget.set_value_and_tooltip(
            int(master_volume * api_volume * inactivity_volume * external_volume * 100),
            f"master volume: {master_volume * 100:.0f}%\n" +
            f"tcode/funscript volume: {api_volume * 100:.0f}%\n" +
            f"inactivity volume: {inactivity_volume * 100:.0f}%\n" +
            f"external volume: {external_volume * 100:.0f}%"
        )

    def timeout_ramp(self, dt: float):
        if not self.checkBox_ramp_enabled.isChecked():
            self.remainder = 0
            return

        rate_per_second = self.doubleSpinBox_ramp_rate.value() / 60

        # linear. volume = v0 + r * t
        # change = rate_per_second * dt

        # exponential. volume = v0 * exp(r * t)
        change = self.doubleSpinBox_volume.value() * rate_per_second * dt / 100

        value = self.doubleSpinBox_volume.value()
        target = self.doubleSpinBox_ramp_target.value()

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

    def set_play_state(self, play_state):
        from qt_ui.mainwindow import PlayState

        if play_state == PlayState.PLAYING:
            if self.playing == False:
                self.slow_start_multiplier = 0
                self.playing = True
        else:
            self.slow_start_multiplier = 0
            self.playing = False

    def timeout_inactivity(self, dt: float):
        axis_values = []
        for axis in self.monitor_axis:
            axis_values.append(axis.interpolate(time.time()))
        if axis_values != self.last_axis_values:
            self.last_axis_update_time = time.time()
        self.last_axis_values = axis_values
        active = self.last_axis_update_time >= (time.time() - self.doubleSpinBox_inactivity_threshold.value())

        try:
            inactivity_dy = self.doubleSpinBox_inactivity_volume.value() / 100.0 / self.doubleSpinBox_inactivity_ramp_time.value()
        except ZeroDivisionError:
            inactivity_dy = 1
        if active:
            self.inactivity_multiplier = np.clip(
                self.inactivity_multiplier + inactivity_dy * dt,
                1 - self.doubleSpinBox_inactivity_volume.value() / 100,
                1.0)
        else:
            self.inactivity_multiplier = np.clip(
                self.inactivity_multiplier - inactivity_dy * dt,
                1 - self.doubleSpinBox_inactivity_volume.value() / 100,
                1.0)

        try:
            slow_start_dy = 1 / self.doubleSpinBox_slow_start.value()
        except ZeroDivisionError:
            slow_start_dy = 100
        if self.playing:
            self.slow_start_multiplier = np.clip(
                self.slow_start_multiplier + slow_start_dy * dt,
                0,
                1
            )
        else:
            self.slow_start_multiplier = 0

        self.axis_inactivity_volume.add(self.inactivity_multiplier * self.slow_start_multiplier)

    def refresh_master_volume(self, _=None):
        self.axis_master_volume.add(np.clip(self.doubleSpinBox_volume.value() / 100, 0.0, 1.0))

    def refresh_message(self, _=None):
        try:
            target = self.doubleSpinBox_ramp_target.value()
            volume = self.doubleSpinBox_volume.value()
            rate_per_second = self.doubleSpinBox_ramp_rate.value() / 60
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

    def refreshSettings(self):
        self.latency = settings.display_latency.get() / 1000.0

    def save_settings(self):
        settings.volume_inactivity_threshold.set(self.doubleSpinBox_inactivity_threshold.value())
        settings.volume_ramp_target.set(self.doubleSpinBox_ramp_target.value() / 100)
        settings.volume_inactivity_time.set(self.doubleSpinBox_inactivity_ramp_time.value())
        settings.volume_ramp_increment_rate.set(self.doubleSpinBox_ramp_rate.value())
        settings.volume_slow_start_time.set(self.doubleSpinBox_slow_start.value())
        settings.tau_us.set(self.doubleSpinBox_tau.value())


