from __future__ import unicode_literals
import time

from PySide6 import QtCore, QtWidgets

from stim_math.axis import AbstractAxis

# provides a link between the user interface control
# and the stim parameter (or funscript) axis
class AxisController(QtCore.QObject):
    def __init__(self, control: QtWidgets.QDoubleSpinBox, axis: AbstractAxis = None):
        super(AxisController, self).__init__()
        self.control = control
        self.axis = None
        self.reload_timer = QtCore.QTimer()
        self.reload_timer.setInterval(100)
        self.reload_timer.timeout.connect(self.reload_display_value)
        self.reload_timer.start()

        self.tcode_idle_timer = QtCore.QTimer()
        self.tcode_idle_timer.setInterval(2000)
        self.tcode_idle_timer.timeout.connect(self.tcode_idle)
        self.tcode_idle_timer.setSingleShot(True)

        try:
            # QSpinbox-like
            self.control.valueChanged.connect(self.value_changed)
        except AttributeError:
            # QGroupBox
            self.control.toggled.connect(self.value_changed)

        self.last_user_entered_value = self.get_control_value()
        self.tcode_update_connection = None

        if axis:
            self.link_axis(axis)

    def reload_display_value(self):
        if self.axis is None:
            return

        if self.axis.is_funscript() or self.tcode_idle_timer.isActive():
            # display the live funscript value
            self.set_control_value(self.axis.interpolate(time.time()))

    def tcode_update(self):
        self.tcode_idle_timer.start()
        self.control.setEnabled(False)

    def tcode_idle(self):
        if not self.axis.is_funscript():
            self.control.setEnabled(True)

    def value_changed(self):
        if self.axis is None:
            return
        if self.tcode_idle_timer.isActive():
            return
        if self.axis.is_funscript():
            return

        # control modified by user in UI
        val = self.get_control_value()
        self.axis.add(val)
        self.last_user_entered_value = val
        self.modified_by_user.emit()

    def link_axis(self, axis):
        self.axis = axis
        if axis.is_funscript():
            self.control.setEnabled(False)
        else:
            self.control.setEnabled(True)
            self.set_control_value(self.axis.interpolate(time.time()))
            if self.tcode_update_connection:
                self.disconnect(self.tcode_update_connection)
                self.tcode_update_connection = None
            self.tcode_update_connection = axis.notify_tcode_update.connect(self.tcode_update)

    def set_control_value(self, value):
        self.control.setValue(value)

    def get_control_value(self):
        return self.control.value()

    modified_by_user = QtCore.Signal()


class PercentAxisController(AxisController):
    def __init__(self, control, axis: AbstractAxis = None):
        super(PercentAxisController, self).__init__(control, axis)

    def set_control_value(self, value):
        self.control.setValue(value * 100)

    def get_control_value(self):
        return self.control.value() / 100


class GroupboxAxisController(AxisController):
    def __init__(self, control: QtWidgets.QGroupBox, axis: AbstractAxis = None):
        super(GroupboxAxisController, self).__init__(control, axis)
        # TODO: did not test if funscript/tcode control works, because it's not used anywhere yet

    def set_control_value(self, value):
        self.control.setChecked(bool(value > 0.5))

    def get_control_value(self):
        return self.control.isChecked()

    modified_by_user = QtCore.Signal()
