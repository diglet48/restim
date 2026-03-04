from __future__ import unicode_literals
import time

from PySide6 import QtCore, QtWidgets

from stim_math.axis import AbstractAxis, WriteProtectedAxis

# Timeout in seconds: if no TCode update for this long, release control back to user
TCODE_RELEASE_TIMEOUT = 2.0


class AxisController(QtCore.QObject):
    def __init__(self, control: QtWidgets.QDoubleSpinBox):
        super(AxisController, self).__init__()
        self.control = control
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.script_axis: AbstractAxis = None
        self.internal_axis: AbstractAxis = None
        self.timer.timeout.connect(self.timeout)
        self.control.valueChanged.connect(self.value_changed)
        self.last_user_entered_value = self.get_control_value()

        # TCode tracking
        self._tcode_active = False
        self._tcode_last_update = 0.0

    def timeout(self):
        if self.script_axis:
            self.set_control_value(self.script_axis.interpolate(time.time()))
        elif self._tcode_active:
            # Check if TCode has timed out
            if time.time() - self._tcode_last_update > TCODE_RELEASE_TIMEOUT:
                self._exit_tcode_mode()
            else:
                # Update spinbox to show current axis value
                self.set_control_value(self.internal_axis.interpolate(time.time()))

    def value_changed(self):
        if not self.script_axis and not self._tcode_active:
            self.internal_axis.add(self.get_control_value())
            self.last_user_entered_value = self.get_control_value()
            self.modified_by_user.emit()

    def set_control_value(self, value):
        self.control.setValue(value)

    def get_control_value(self):
        return self.control.value()

    def link_axis(self, axis):
        if isinstance(axis, WriteProtectedAxis):    # HACK: is funcript axis?
            self.link_to_funscript(axis)
        else:
            self.link_to_internal_axis(axis)

    def link_to_funscript(self, script_axis):
        """
        Behavior: the control gets disables. Periodically, the value shown in the control updates.
        """
        self._tcode_active = False
        self.control.setEnabled(False)
        self.script_axis = script_axis
        self.timer.start()

    def link_to_internal_axis(self, internal_axis):
        """
        Behavior: control enabled. Whenever user modifies the control, value is inserted in axis.
        """
        self._tcode_active = False
        self.timer.stop()
        self.script_axis = None
        self.internal_axis = internal_axis
        self.set_control_value(self.internal_axis.interpolate(time.time()))
        self.control.setEnabled(True)

    def on_tcode_axis_updated(self, axis):
        """Called when TCode writes to any axis. Check if it's ours."""
        if axis is not self.internal_axis:
            return
        if self.script_axis:
            return  # funscript mode takes priority
        self._tcode_last_update = time.time()
        if not self._tcode_active:
            self._enter_tcode_mode()

    def _enter_tcode_mode(self):
        """Enter TCode override mode: disable spinbox, start polling axis."""
        self._tcode_active = True
        self.control.setEnabled(False)
        self.timer.start()

    def _exit_tcode_mode(self):
        """Exit TCode mode: restore user's last value, re-enable spinbox."""
        self._tcode_active = False
        self.timer.stop()
        # Restore the user's last manually-entered value
        self.internal_axis.add(self.last_user_entered_value)
        self.set_control_value(self.last_user_entered_value)
        self.control.setEnabled(True)

    modified_by_user = QtCore.Signal()


class PercentAxisController(AxisController):
    def __init__(self, control):
        super(PercentAxisController, self).__init__(control)

    def set_control_value(self, value):
        self.control.setValue(value * 100)

    def get_control_value(self):
        return self.control.value() / 100


class GroupboxAxisController(QtCore.QObject):
    def __init__(self, control: QtWidgets.QGroupBox):
        super(GroupboxAxisController, self).__init__()
        self.control = control
        self.script_axis: AbstractAxis = None
        self.internal_axis: AbstractAxis = None
        self.control.toggled.connect(self.value_changed)
        self.last_user_entered_value = self.control.isChecked()

        # TCode tracking
        self._tcode_active = False
        self._tcode_last_update = 0.0
        self._tcode_timer = QtCore.QTimer()
        self._tcode_timer.setInterval(100)
        self._tcode_timer.timeout.connect(self._tcode_timeout)

    def _tcode_timeout(self):
        if self._tcode_active and time.time() - self._tcode_last_update > TCODE_RELEASE_TIMEOUT:
            self._exit_tcode_mode()

    def value_changed(self):
        if self.internal_axis is not None and not self._tcode_active:
            self.internal_axis.add(self.control.isChecked())
            self.last_user_entered_value = self.control.isChecked()
            self.modified_by_user.emit()

    def link_axis(self, axis):
        if isinstance(axis, WriteProtectedAxis):    # HACK: is funcript axis?
            self.link_to_funscript(axis)
        else:
            self.link_to_internal_axis(axis)

    def link_to_funscript(self, script_axis):
        """
        Behavior: the control gets disables. Periodically, the value shown in the control updates.
        """
        self._tcode_active = False
        self._tcode_timer.stop()
        self.internal_axis = None
        self.control.setCheckable(False)
        self.script_axis = script_axis

    def link_to_internal_axis(self, internal_axis):
        """
        Behavior: control enabled. Whenever user modifies the control, value is inserted in axis.
        """
        self._tcode_active = False
        self._tcode_timer.stop()
        self.script_axis = None
        self.internal_axis = None
        self.control.setCheckable(True)
        self.control.setChecked(self.last_user_entered_value)
        self.internal_axis = internal_axis

    def on_tcode_axis_updated(self, axis):
        """Called when TCode writes to any axis. Check if it's ours."""
        if axis is not self.internal_axis:
            return
        if self.script_axis:
            return
        self._tcode_last_update = time.time()
        if not self._tcode_active:
            self._enter_tcode_mode()

    def _enter_tcode_mode(self):
        self._tcode_active = True
        self.control.setCheckable(False)
        self._tcode_timer.start()

    def _exit_tcode_mode(self):
        self._tcode_active = False
        self._tcode_timer.stop()
        self.control.setCheckable(True)
        self.control.setChecked(self.last_user_entered_value)
        if self.internal_axis:
            self.internal_axis.add(self.last_user_entered_value)

    modified_by_user = QtCore.Signal()
