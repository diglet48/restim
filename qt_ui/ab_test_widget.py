from __future__ import unicode_literals

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer

from qt_ui.ab_test_widget_ui import Ui_ABTestWidget

from stim_math import limits
from stim_math.axis import create_constant_axis

from qt_ui import settings
from qt_ui.axis_controller import AxisController, PercentAxisController


class ABTestWidget(QtWidgets.QWidget, Ui_ABTestWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.display_latency = settings.display_latency.get()

        self.a_pulse_frequency.setMinimum(limits.PulseFrequency.min)
        self.a_pulse_frequency.setMaximum(limits.PulseFrequency.max)
        self.b_pulse_frequency.setMinimum(limits.PulseFrequency.min)
        self.b_pulse_frequency.setMaximum(limits.PulseFrequency.max)

        self.a_pulse_width.setMinimum(limits.PulseWidth.min)
        self.a_pulse_width.setMaximum(limits.PulseWidth.max)
        self.b_pulse_width.setMinimum(limits.PulseWidth.min)
        self.b_pulse_width.setMaximum(limits.PulseWidth.max)

        self.a_rise_time.setMinimum(limits.PulseRiseTime.min)
        self.a_rise_time.setMaximum(limits.PulseRiseTime.max)
        self.b_rise_time.setMinimum(limits.PulseRiseTime.min)
        self.b_rise_time.setMaximum(limits.PulseRiseTime.max)

        self.axis_a_volume = create_constant_axis(settings.ab_test_volume.get())
        self.axis_a_pulse_count = create_constant_axis(settings.ab_test_pulse_count.get())
        self.axis_a_carrier_frequency = create_constant_axis(settings.ab_test_carrier.get())
        self.axis_a_pulse_frequency = create_constant_axis(settings.ab_test_pulse_frequency.get())
        self.axis_a_pulse_width = create_constant_axis(settings.ab_test_pulse_width.get())
        self.axis_a_pulse_interval_random = create_constant_axis(settings.ab_test_pulse_interval_random.get())
        self.axis_a_pulse_rise_time = create_constant_axis(settings.ab_test_pulse_rise_time.get())
        self.axis_b_volume = create_constant_axis(settings.ab_test_volume.get())
        self.axis_b_pulse_count = create_constant_axis(settings.ab_test_pulse_count.get())
        self.axis_b_carrier_frequency = create_constant_axis(settings.ab_test_carrier.get())
        self.axis_b_pulse_frequency = create_constant_axis(settings.ab_test_pulse_frequency.get())
        self.axis_b_pulse_width = create_constant_axis(settings.ab_test_pulse_width.get())
        self.axis_b_pulse_interval_random = create_constant_axis(settings.ab_test_pulse_interval_random.get())
        self.axis_b_pulse_rise_time = create_constant_axis(settings.ab_test_pulse_rise_time.get())

        self.axis_a_volume_controller = PercentAxisController(self.a_volume)
        self.axis_a_volume_controller.link_axis(self.axis_a_volume)
        self.axis_a_pulse_count_controller = AxisController(self.a_pulse_count)
        self.axis_a_pulse_count_controller.link_axis(self.axis_a_pulse_count)
        self.axis_a_carrier_controller = AxisController(self.a_carrier)
        self.axis_a_carrier_controller.link_axis(self.axis_a_carrier_frequency)
        self.axis_a_pulse_frequency_controller = AxisController(self.a_pulse_frequency)
        self.axis_a_pulse_frequency_controller.link_axis(self.axis_a_pulse_frequency)
        self.axis_a_pulse_width_controller = AxisController(self.a_pulse_width)
        self.axis_a_pulse_width_controller.link_axis(self.axis_a_pulse_width)
        self.axis_a_pulse_interval_random_controller = PercentAxisController(self.a_pulse_interval_random)
        self.axis_a_pulse_interval_random_controller.link_axis(self.axis_a_pulse_interval_random)
        self.axis_a_rise_time_controller = AxisController(self.a_rise_time)
        self.axis_a_rise_time_controller.link_axis(self.axis_a_pulse_rise_time)
        self.axis_b_volume_controller = PercentAxisController(self.b_volume)
        self.axis_b_volume_controller.link_axis(self.axis_b_volume)
        self.axis_b_pulse_count_controller = AxisController(self.b_pulse_count)
        self.axis_b_pulse_count_controller.link_axis(self.axis_b_pulse_count)
        self.axis_b_carrier_controller = AxisController(self.b_carrier)
        self.axis_b_carrier_controller.link_axis(self.axis_b_carrier_frequency)
        self.axis_b_pulse_frequency_controller = AxisController(self.b_pulse_frequency)
        self.axis_b_pulse_frequency_controller.link_axis(self.axis_b_pulse_frequency)
        self.axis_b_pulse_width_controller = AxisController(self.b_pulse_width)
        self.axis_b_pulse_width_controller.link_axis(self.axis_b_pulse_width)
        self.axis_b_pulse_interval_random_controller = PercentAxisController(self.b_pulse_interval_random)
        self.axis_b_pulse_interval_random_controller.link_axis(self.axis_b_pulse_interval_random)
        self.axis_b_rise_time_controller = AxisController(self.b_rise_time)
        self.axis_b_rise_time_controller.link_axis(self.axis_b_pulse_rise_time)

        self.axis_a_volume_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_pulse_count_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_carrier_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_pulse_frequency_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_pulse_width_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_pulse_interval_random_controller.modified_by_user.connect(self.settings_changed)
        self.axis_a_rise_time_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_volume_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_pulse_count_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_carrier_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_pulse_frequency_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_pulse_width_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_pulse_interval_random_controller.modified_by_user.connect(self.settings_changed)
        self.axis_b_rise_time_controller.modified_by_user.connect(self.settings_changed)

        self.settings_changed()
        self.test_waveform_changed_triggered.connect(self.highlight_text_with_delay)

    def set_safety_limits(self, min_carrier, max_carrier):
        self.a_carrier.setRange(min_carrier, max_carrier)
        self.b_carrier.setRange(min_carrier, max_carrier)

    def settings_changed(self):
        def set_duty_cycle(control, duty_cycle):
            if duty_cycle <= 1:
                control.setStyleSheet('')
                control.setText(f'{duty_cycle:.0%}')
            else:
                control.setStyleSheet('color: red')
                control.setText(f'{1:.0%}')

        set_duty_cycle(
            self.a_duty_cycle,
            self.a_pulse_frequency.value() * self.a_pulse_width.value() / self.a_carrier.value())
        set_duty_cycle(
            self.b_duty_cycle,
            self.b_pulse_frequency.value() * self.b_pulse_width.value() / self.b_carrier.value())

    def save_settings(self):
        # TODO: call me
        pass

    def refreshSettings(self):
        self.display_latency = settings.display_latency.get()

    test_waveform_changed_triggered = QtCore.pyqtSignal(bool)

    def test_waveform_changed(self, is_a: bool):
        self.test_waveform_changed_triggered.emit(is_a)

    def highlight_text_with_delay(self, is_a: bool):
        def highlight_text():
            if is_a:
                self.a_signal_label.setStyleSheet('background-color: green')
                self.b_signal_label.setStyleSheet('')
            else:
                self.a_signal_label.setStyleSheet('')
                self.b_signal_label.setStyleSheet('background-color: green')

        QTimer.singleShot(int(self.display_latency), highlight_text)