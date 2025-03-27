from __future__ import unicode_literals

from PySide6 import QtWidgets

from qt_ui.neostim_settings_widget_ui import Ui_NeoStimSettingsWidget
from stim_math.axis import create_constant_axis, create_temporal_axis
from device.neostim import limits
from stim_math.audio_gen.params import NeoStimDebugParams

from qt_ui.axis_controller import AxisController, PercentAxisController



class NeoStimSettingsWidget(QtWidgets.QWidget, Ui_NeoStimSettingsWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.carrier_frequency.setMinimum(limits.CarrierFrequency.min)
        self.carrier_frequency.setMaximum(limits.CarrierFrequency.max)
        self.duty_cycle_at_max_power.setMinimum(limits.DutyCycle.min * 100)
        self.duty_cycle_at_max_power.setMaximum(limits.DutyCycle.max * 100)

        self.axis_voltage = create_temporal_axis(self.voltage.value())
        self.axis_carrier_frequency = create_temporal_axis(self.carrier_frequency.value())
        self.axis_inversion_time = create_temporal_axis(self.inversion_time.value())
        self.axis_switch_time = create_temporal_axis(self.switch_time.value())
        self.axis_pulse_frequency = create_temporal_axis(self.pulse_frequency.value())
        self.axis_duty_cycle_at_max_power = create_temporal_axis(self.duty_cycle_at_max_power.value() / 100)
        self.axis_debug = create_constant_axis(self.get_debug_params())


        self.voltage_controller = AxisController(self.voltage)
        self.voltage_controller.link_axis(self.axis_voltage)

        self.carrier_frequency_controller = AxisController(self.carrier_frequency)
        self.carrier_frequency_controller.link_axis(self.axis_carrier_frequency)

        self.inversion_time_controller = AxisController(self.inversion_time)
        self.inversion_time_controller.link_axis(self.axis_inversion_time)

        self.switch_time_controller = AxisController(self.switch_time)
        self.switch_time_controller.link_axis(self.axis_switch_time)

        self.pulse_frequency_controller = AxisController(self.pulse_frequency)
        self.pulse_frequency_controller.link_axis(self.axis_pulse_frequency)

        self.duty_cycle_at_max_power_controller = PercentAxisController(self.duty_cycle_at_max_power)
        self.duty_cycle_at_max_power_controller.link_axis(self.axis_duty_cycle_at_max_power)



        self.voltage_controller.modified_by_user.connect(self.settings_changed)
        self.carrier_frequency_controller.modified_by_user.connect(self.settings_changed)
        self.inversion_time_controller.modified_by_user.connect(self.settings_changed)
        self.switch_time_controller.modified_by_user.connect(self.settings_changed)
        self.pulse_frequency_controller.modified_by_user.connect(self.settings_changed)
        self.duty_cycle_at_max_power_controller.modified_by_user.connect(self.settings_changed)

        self.use_a.stateChanged.connect(self.settings_changed)
        self.use_b.stateChanged.connect(self.settings_changed)
        self.use_ab.stateChanged.connect(self.settings_changed)
        self.use_ac.stateChanged.connect(self.settings_changed)
        self.use_bc.stateChanged.connect(self.settings_changed)
        self.defeat_randomization.stateChanged.connect(self.settings_changed)
        self.triplet_power.valueChanged.connect(self.settings_changed)
        self.emulation_power.valueChanged.connect(self.settings_changed)
        self.emulate_ab_c.stateChanged.connect(self.settings_changed)

        self.settings_changed()

    def get_debug_params(self):
        return NeoStimDebugParams(
            self.use_a.isChecked(),
            self.use_b.isChecked(),
            self.use_ab.isChecked(),
            self.use_ac.isChecked(),
            self.use_bc.isChecked(),
            self.defeat_randomization.isChecked(),
            self.triplet_power.value(),
            self.emulate_ab_c.isChecked(),
            self.emulation_power.value(),
        )

    def settings_changed(self):
        self.axis_debug.add(self.get_debug_params())

    def save_settings(self):
        pass