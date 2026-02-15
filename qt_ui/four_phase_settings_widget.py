from __future__ import unicode_literals
import numpy as np


from PySide6 import QtCore, QtWidgets
from qt_ui import settings
from qt_ui.axis_controller import AxisController

from qt_ui.four_phase_settings_widget_ui import Ui_FourPhaseSettingsWidget


from stim_math.audio_gen.params import FourphaseCalibrationParams
from stim_math.audio_gen.params import ThreephasePositionTransformParams
from stim_math.axis import create_temporal_axis, create_constant_axis

class FourPhaseSettingsWidget(QtWidgets.QWidget, Ui_FourPhaseSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        # create axis
        self.calibrate_params = FourphaseCalibrationParams(
            center=create_constant_axis(settings.fourphase_calibration_center.get()),
            a=create_constant_axis(settings.fourphase_calibration_a.get()),
            b=create_constant_axis(settings.fourphase_calibration_b.get()),
            c=create_constant_axis(settings.fourphase_calibration_c.get()),
            d=create_constant_axis(settings.fourphase_calibration_d.get()),
        )

        self.a_power.setValue(self.calibrate_params.a.last_value())
        self.b_power.setValue(self.calibrate_params.b.last_value())
        self.c_power.setValue(self.calibrate_params.c.last_value())
        self.d_power.setValue(self.calibrate_params.d.last_value())
        self.center_power.setValue(self.calibrate_params.center.last_value())

        self.a_controller = AxisController(self.a_power)
        self.a_controller.link_axis(self.calibrate_params.a)

        self.b_controller = AxisController(self.b_power)
        self.b_controller.link_axis(self.calibrate_params.b)

        self.c_controller = AxisController(self.c_power)
        self.c_controller.link_axis(self.calibrate_params.c)

        self.d_controller = AxisController(self.d_power)
        self.d_controller.link_axis(self.calibrate_params.d)

        # self.center_controller = AxisController(self.center_power)
        # self.center_controller.link_axis(self.calibrate_params.center)

    def save_settings(self):
        settings.fourphase_calibration_a.set(self.a_controller.last_user_entered_value)
        settings.fourphase_calibration_b.set(self.b_controller.last_user_entered_value)
        settings.fourphase_calibration_c.set(self.c_controller.last_user_entered_value)
        settings.fourphase_calibration_d.set(self.d_controller.last_user_entered_value)
        # settings.fourphase_calibration_center.set(self.center_controller.last_user_entered_value)
