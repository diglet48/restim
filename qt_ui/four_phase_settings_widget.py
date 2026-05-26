from __future__ import unicode_literals
import numpy as np


from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QColor

from qt_ui import settings
from qt_ui.axis_controller import AxisController, PercentAxisController

from qt_ui.four_phase_settings_widget_ui import Ui_FourPhaseSettingsWidget

from stim_math.audio_gen.params import FourphaseCalibrationParams
from stim_math.audio_gen.params import ThreephasePositionTransformParams
from stim_math.axis import create_temporal_axis, create_constant_axis

COLOR_A = QColor.fromRgb(0xFE, 0x2E, 0x2E, 200)  # red
COLOR_B = QColor.fromRgb(0x54, 0x63, 0xFF, 200)  # blue
COLOR_C = QColor.fromRgb(0xFF, 0xC7, 0x17, 200)  # yellow
COLOR_D = QColor.fromRgb(0x1F, 0x9E, 0x40, 200)  # green


class FourPhaseSettingsWidget(QtWidgets.QWidget, Ui_FourPhaseSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        # create axis
        self.calibrate_params = FourphaseCalibrationParams(
            a=create_constant_axis(settings.fourphase_calibration_a.get()),
            b=create_constant_axis(settings.fourphase_calibration_b.get()),
            c=create_constant_axis(settings.fourphase_calibration_c.get()),
            d=create_constant_axis(settings.fourphase_calibration_d.get()),
            center_reduction=create_constant_axis(settings.fourphase_calibration_center_reduction.get()),
        )

        self.a_power.setValue(self.calibrate_params.a.last_value())
        self.b_power.setValue(self.calibrate_params.b.last_value())
        self.c_power.setValue(self.calibrate_params.c.last_value())
        self.d_power.setValue(self.calibrate_params.d.last_value())
        self.center_reduction.setValue(self.calibrate_params.center_reduction.last_value() * 100)

        self.a_controller = AxisController(self.a_power)
        self.a_controller.link_axis(self.calibrate_params.a)

        self.b_controller = AxisController(self.b_power)
        self.b_controller.link_axis(self.calibrate_params.b)

        self.c_controller = AxisController(self.c_power)
        self.c_controller.link_axis(self.calibrate_params.c)

        self.d_controller = AxisController(self.d_power)
        self.d_controller.link_axis(self.calibrate_params.d)

        self.center_reduction_controller = PercentAxisController(self.center_reduction)
        self.center_reduction_controller.link_axis(self.calibrate_params.center_reduction)

        self.center_reduction_reset.clicked.connect(self.reset_center_reduction)

        self.a_power.setIndicatorColor(COLOR_A)
        self.b_power.setIndicatorColor(COLOR_B)
        self.c_power.setIndicatorColor(COLOR_C)
        self.d_power.setIndicatorColor(COLOR_D)
        self.refresh_indicator_range()

        # self.center_reduction.setIndicatorColor(QColor.fromRgb(100, 100, 100, 200))
        self.center_reduction.setIndicatorRange(0, 20)

        self.a_power.valueChanged.connect(self.refresh_indicator_range)
        self.b_power.valueChanged.connect(self.refresh_indicator_range)
        self.c_power.valueChanged.connect(self.refresh_indicator_range)
        self.d_power.valueChanged.connect(self.refresh_indicator_range)

    def refresh_indicator_range(self):
        hi = max([
            self.a_power.value(),
            self.b_power.value(),
            self.c_power.value(),
            self.d_power.value(),
        ])
        lo = hi - 2

        self.a_power.setIndicatorRange(lo, hi)
        self.b_power.setIndicatorRange(lo, hi)
        self.c_power.setIndicatorRange(lo, hi)
        self.d_power.setIndicatorRange(lo, hi)

    def save_settings(self):
        settings.fourphase_calibration_a.set(self.a_controller.last_user_entered_value)
        settings.fourphase_calibration_b.set(self.b_controller.last_user_entered_value)
        settings.fourphase_calibration_c.set(self.c_controller.last_user_entered_value)
        settings.fourphase_calibration_d.set(self.d_controller.last_user_entered_value)
        settings.fourphase_calibration_center_reduction.set(self.center_reduction_controller.last_user_entered_value)

    def reset_center_reduction(self):
        self.center_reduction.setValue(
            settings.fourphase_calibration_center_reduction.default_value * 100
        )