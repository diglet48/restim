from __future__ import unicode_literals
import time

from PyQt5 import QtCore, QtWidgets

from stim_math.axis import AbstractAxis, WriteProtectedAxis


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

    def timeout(self):
        if self.script_axis:
            self.set_control_value(self.script_axis.interpolate(time.time()))

    def value_changed(self):
        # TODO: what happens on tcode control?
        if not self.script_axis:    # if: not funscript control
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
        self.control.setEnabled(False)
        self.script_axis = script_axis
        self.timer.start()

    def link_to_internal_axis(self, internal_axis):
        """
        Behavior: control enabled. Whenever user modifies the control, value is inserted in axis.
        """
        self.timer.stop()
        self.script_axis = None
        self.internal_axis = internal_axis
        self.set_control_value(self.internal_axis.interpolate(time.time()))
        self.control.setEnabled(True)

    modified_by_user = QtCore.pyqtSignal()


class PercentAxisController(AxisController):
    def __init__(self, control):
        super(PercentAxisController, self).__init__(control)

    def set_control_value(self, value):
        self.control.setValue(value * 100)

    def get_control_value(self):
        return self.control.value() / 100
