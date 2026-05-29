from __future__ import unicode_literals
import numpy as np
from enum import Enum

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QColor

from qt_ui import settings

from qt_ui.three_phase_settings_widget_ui import Ui_ThreePhaseSettingsWidget


from stim_math.audio_gen.params import ThreephaseCalibrationParams
from stim_math.audio_gen.params import ThreephasePositionTransformParams
from stim_math.axis import create_temporal_axis, create_constant_axis
from stim_math.threephase import intensity_ratio_to_ud_lr, ud_lr_to_intensity_ratio

SETTING_CALIBRATION_NEUTRAL = 'hw_calibration/neutral'
SETTING_CALIBRATION_RIGHT = 'hw_calibration/right'
SETTING_CALIBRATION_CENTER = 'hw_calibration/center'

SETTING_TRANSFORM_ENABLED = 'threephase_transform/enabled'
SETTING_TRANSFORM_ROTATE = 'threephase_transform/rotate'
SETTING_TRANSFORM_MIRROR = 'threephase_transform/mirror'
SETTING_TRANSFORM_LIMIT_TOP = 'threephase_transform/limit_top'
SETTING_TRANSFORM_LIMIT_BOTTOM = 'threephase_transform/limit_bottom'
SETTING_TRANSFORM_LIMIT_LEFT = 'threephase_transform/limit_left'
SETTING_TRANSFORM_LIMIT_RIGHT = 'threephase_transform/limit_right'

SETTING_THREEPHASE_EXPONENT = 'threephase_transform/exponent'

COLOR_A = QColor.fromRgb(0xFE, 0x2E, 0x2E, 200)  # red
COLOR_B = QColor.fromRgb(0x54, 0x63, 0xFF, 200)  # blue
COLOR_C = QColor.fromRgb(0xFF, 0xC7, 0x17, 200)  # yellow


class Interface(Enum):
    Classic = 0
    Modern = 1

def center_calib_to_reduction(calib):
    power = 10 ** (calib / 10)
    return (1 - power) * 100

def center_reduction_to_calib(reduction):
    power = 1 - reduction / 100
    return np.log10(power) * 10

class ThreePhaseSettingsWidget(QtWidgets.QWidget, Ui_ThreePhaseSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.page.layout().setContentsMargins(0, 0, 0, 0)
        self.page_2.layout().setContentsMargins(0, 0, 0, 0)

        # create axis
        self.calibrate_params = ThreephaseCalibrationParams(
            neutral=create_temporal_axis(0.0),
            right=create_temporal_axis(0.0),
            center=create_temporal_axis(0.0),
        )
        self.transform_params = ThreephasePositionTransformParams(
            transform_enabled=create_temporal_axis(False, interpolation='step'),
            transform_rotation_degrees=create_temporal_axis(0.0),
            transform_mirror=create_temporal_axis(False, interpolation='step'),
            transform_top_limit=create_temporal_axis(0.0),
            transform_bottom_limit=create_temporal_axis(0.0),
            transform_left_limit=create_temporal_axis(0.0),
            transform_right_limit=create_temporal_axis(0.0),

            map_to_edge_enabled=create_temporal_axis(False, interpolation='step'),
            map_to_edge_start=create_temporal_axis(0.0),
            map_to_edge_length=create_temporal_axis(0.0),
            map_to_edge_invert=create_temporal_axis(0.0),
        )
        self.phase_widget_calibration.set_axis(
            self.calibrate_params.neutral,
            self.calibrate_params.right
        )


        # load settings, classic interface
        self.neutral.setValue(settings.threephase_calibration_neutral.get())
        self.right.setValue(settings.threephase_calibration_right.get())
        self.center_reduction.setValue(center_calib_to_reduction(settings.threephase_calibration_center.get()))

        # load settings, adjust limits
        self.combobox_type.setCurrentIndex(settings.threephase_transform_combobox_selection.get())
        self.groupBox_2.setChecked(settings.threephase_transform_enabled.get())
        self.rotation.setValue(settings.threephase_transform_rotate.get())
        self.mirror.setChecked(settings.threephase_transform_mirror.get())
        self.limit_top.setValue(settings.threephase_transform_limit_top.get())
        self.limit_bottom.setValue(settings.threephase_transform_limit_bottom.get())
        self.limit_left.setValue(settings.threephase_transform_limit_left.get())
        self.limit_right.setValue(settings.threephase_transform_limit_right.get())

        self.mapToEdge_start.setValue(settings.threephase_map_to_edge_start.get())
        self.mapToEdge_length.setValue(settings.threephase_map_to_edge_length.get())
        self.mapToEdge_invert.setChecked(settings.threephase_map_to_edge_invert.get())

        self.comboBox_interface.addItem("Classic", Interface.Classic)
        self.comboBox_interface.addItem("Modern", Interface.Modern)
        self.comboBox_interface.currentIndexChanged.connect(self.reload_calibration_interface)
        self.comboBox_interface.setCurrentIndex(1)


        # connect edit boxes signals/slots
        self.neutral.valueChanged.connect(self.classic_calibration_params_changed)
        self.right.valueChanged.connect(self.classic_calibration_params_changed)

        self.a_power.valueChanged.connect(self.modern_calibration_params_changed)
        self.b_power.valueChanged.connect(self.modern_calibration_params_changed)
        self.c_power.valueChanged.connect(self.modern_calibration_params_changed)

        self.center_reduction.valueChanged.connect(self.center_reduction_changed)

        self.a_power.valueChanged.connect(self.refresh_indicator_range)
        self.b_power.valueChanged.connect(self.refresh_indicator_range)
        self.c_power.valueChanged.connect(self.refresh_indicator_range)

        self.groupBox_2.clicked.connect(self.adjust_limits_changed)
        self.combobox_type.currentIndexChanged.connect(self.adjust_limits_changed)
        self.rotation.valueChanged.connect(self.adjust_limits_changed)
        self.mirror.stateChanged.connect(self.adjust_limits_changed)
        self.limit_top.valueChanged.connect(self.adjust_limits_changed)
        self.limit_bottom.valueChanged.connect(self.adjust_limits_changed)
        self.limit_right.valueChanged.connect(self.adjust_limits_changed)
        self.limit_left.valueChanged.connect(self.adjust_limits_changed)
        self.mapToEdge_start.valueChanged.connect(self.adjust_limits_changed)
        self.mapToEdge_length.valueChanged.connect(self.adjust_limits_changed)
        self.mapToEdge_invert.toggled.connect(self.adjust_limits_changed)

        # connect clicks on calibration diagram
        self.phase_widget_calibration.clicked.connect(self.clicked_on_calibration_widget)

        # connect buttons signals/slots
        self.reset_defaults_button.clicked.connect(self.reset_defaults)
        self.center_reduction_reset.clicked.connect(self.reset_center_reduction)

        self.center_reduction.setIndicatorRange(0, 20)
        self.a_power.setIndicatorColor(COLOR_A)
        self.b_power.setIndicatorColor(COLOR_B)
        self.c_power.setIndicatorColor(COLOR_C)

        self.phase_widget_calibration.refresh()
        self.reload_calibration_interface()
        self.classic_calibration_params_changed()
        self.modern_calibration_params_changed()
        self.center_reduction_changed()

    def reload_calibration_interface(self):
        if self.comboBox_interface.currentData() == Interface.Classic:
            self.stackedWidget_2.setCurrentIndex(0)
        else:
            self.stackedWidget_2.setCurrentIndex(1)

            # convert ud/lr to a/b/c and fill into the interface
            a, b, c = ud_lr_to_intensity_ratio(
                self.neutral.value(),
                self.right.value()
            )
            a = np.log10(a) * 10
            b = np.log10(b) * 10
            c = np.log10(c) * 10

            self.a_power.blockSignals(True)
            self.b_power.blockSignals(True)
            self.c_power.blockSignals(True)
            self.a_power.setValue(a)
            self.b_power.setValue(b)
            self.c_power.setValue(c)
            self.a_power.blockSignals(False)
            self.b_power.blockSignals(False)
            self.c_power.blockSignals(False)
            self.modern_calibration_params_changed()
            self.refresh_indicator_range()


    def adjust_limits_changed(self):
        # update ui
        self.stackedWidget.setCurrentIndex(self.combobox_type.currentIndex())

        # normalize angle
        self.rotation.setValue(self.rotation.value() % 360)

        # check limits
        if self.limit_top.value() < self.limit_bottom.value():
            avg = np.average([self.limit_top.value(), self.limit_bottom.value()])
            self.limit_bottom.blockSignals(True)
            self.limit_top.blockSignals(True)
            self.limit_bottom.setValue(avg)
            self.limit_top.setValue(avg)
            self.limit_bottom.blockSignals(False)
            self.limit_top.blockSignals(False)

        # check limits
        if self.limit_right.value() < self.limit_left.value():
            avg = np.average([self.limit_right.value(), self.limit_left.value()])
            self.limit_left.blockSignals(True)
            self.limit_right.blockSignals(True)
            self.limit_right.setValue(avg)
            self.limit_left.setValue(avg)
            self.limit_left.blockSignals(False)
            self.limit_right.blockSignals(False)

        self.transform_params.transform_enabled.add(self.groupBox_2.isChecked() and self.combobox_type.currentIndex() == 0)
        self.transform_params.transform_rotation_degrees.add(self.rotation.value())
        self.transform_params.transform_mirror.add(self.mirror.isChecked())
        self.transform_params.transform_top_limit.add(self.limit_top.value())
        self.transform_params.transform_bottom_limit.add(self.limit_bottom.value())
        self.transform_params.transform_left_limit.add(self.limit_left.value())
        self.transform_params.transform_right_limit.add(self.limit_right.value())

        self.transform_params.map_to_edge_enabled.add(self.groupBox_2.isChecked() and self.combobox_type.currentIndex() == 1)
        self.transform_params.map_to_edge_start.add(self.mapToEdge_start.value())
        self.transform_params.map_to_edge_length.add(self.mapToEdge_length.value())
        self.transform_params.map_to_edge_invert.add(self.mapToEdge_invert.isChecked())

    def classic_calibration_params_changed(self):
        if self.comboBox_interface.currentData() != Interface.Classic:
            return

        self.calibrate_params.neutral.add(self.neutral.value())
        self.calibrate_params.right.add(self.right.value())
        self.phase_widget_calibration.refresh()

    def modern_calibration_params_changed(self):
        if self.comboBox_interface.currentData() != Interface.Modern:
            return

        a = self.a_power.value()
        b = self.b_power.value()
        c = self.c_power.value()
        a = 10**(a/10)
        b = 10**(b/10)
        c = 10**(c/10)
        # maximum = np.max([a, b, c])
        # a = a - maximum# + 100
        # b = b - maximum# + 100
        # c = c - maximum# + 100

        ud, lr = intensity_ratio_to_ud_lr(a, b, c)
        self.neutral.setValue(ud)
        self.right.setValue(lr)

        self.calibrate_params.neutral.add(self.neutral.value())
        self.calibrate_params.right.add(self.right.value())
        self.phase_widget_calibration.refresh()

    def center_reduction_changed(self):
        self.calibrate_params.center.add(center_reduction_to_calib(self.center_reduction.value()))
        print('center calib:', self.calibrate_params.center.last_value())

    def refresh_indicator_range(self):
        values = np.array([
            self.a_power.value(),
            self.b_power.value(),
            self.c_power.value(),
        ])
        hi = np.max(values)
        lo = hi - 3

        self.a_power.setIndicatorRange(lo, hi)
        self.b_power.setIndicatorRange(lo, hi)
        self.c_power.setIndicatorRange(lo, hi)

    def reset_defaults(self):
        self.rotation.setValue(0)
        self.mirror.setChecked(False)
        self.limit_top.setValue(1)
        self.limit_bottom.setValue(-1)
        self.limit_left.setValue(-1)
        self.limit_right.setValue(1)
        self.classic_calibration_params_changed()

    def clicked_on_calibration_widget(self, neutral, right):
        if self.comboBox_interface.currentData() == Interface.Classic:
            self.neutral.setValue(self.neutral.value() + neutral * 0.1)
            self.right.setValue(self.right.value() - right * 0.1)
            self.phase_widget_calibration.refresh()
        else:
            vecs = np.array([
                [1, 0],
                [0.5, np.sqrt(3)/2],
                [-0.5, np.sqrt(3)/2],
                [-1, 0],
                [-0.5, -np.sqrt(3)/2],
                [0.5, -np.sqrt(3)/2],
            ])
            deltas = np.array([
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 1, 1],
                [0, 0, 1],
                [1, 0, 1],
            ]) * 0.1
            delta = deltas[np.argmax(np.dot(vecs, (neutral, right)))]

            values = np.array([self.a_power.value(), self.b_power.value(), self.c_power.value()])
            values += delta
            a, b, c = values - np.max(values) # + 100

            self.a_power.blockSignals(True)
            self.b_power.blockSignals(True)
            self.c_power.blockSignals(True)
            self.a_power.setValue(a)
            self.b_power.setValue(b)
            self.c_power.setValue(c)
            self.a_power.blockSignals(False)
            self.b_power.blockSignals(False)
            self.c_power.blockSignals(False)
            self.modern_calibration_params_changed()
            self.refresh_indicator_range()

    def reset_center_reduction(self):
        self.center_reduction.setValue(center_calib_to_reduction(settings.threephase_calibration_center.default_value))

    def settings_changed(self):
        pass

    def save_settings(self):
        settings.threephase_transform_combobox_selection.set(self.combobox_type.currentIndex())

        settings.threephase_calibration_neutral.set(self.neutral.value())
        settings.threephase_calibration_right.set(self.right.value())
        settings.threephase_calibration_center.set(float(center_reduction_to_calib(self.center_reduction.value())))

        settings.threephase_transform_enabled.set(self.groupBox_2.isChecked())
        settings.threephase_transform_rotate.set(self.rotation.value())
        settings.threephase_transform_mirror.set(self.mirror.isChecked())
        settings.threephase_transform_limit_top.set(self.limit_top.value())
        settings.threephase_transform_limit_bottom.set(self.limit_bottom.value())
        settings.threephase_transform_limit_left.set(self.limit_left.value())
        settings.threephase_transform_limit_right.set(self.limit_right.value())

        settings.threephase_map_to_edge_start.set(self.mapToEdge_start.value())
        settings.threephase_map_to_edge_length.set(self.mapToEdge_length.value())
        settings.threephase_map_to_edge_invert.set(self.mapToEdge_invert.isChecked())
