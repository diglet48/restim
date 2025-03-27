from __future__ import unicode_literals
import numpy as np


from PySide6 import QtCore, QtWidgets
from qt_ui import settings

from qt_ui.three_phase_settings_widget_ui import Ui_ThreePhaseSettingsWidget


from stim_math.audio_gen.params import ThreephaseCalibrationParams
from stim_math.audio_gen.params import ThreephasePositionTransformParams
from stim_math.axis import create_temporal_axis, create_constant_axis

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

            exponent=create_temporal_axis(0.0),
        )
        self.phase_widget_calibration.set_axis(
            self.calibrate_params.neutral,
            self.calibrate_params.right
        )

        self.combobox_type.setCurrentIndex(settings.threephase_transform_combobox_selection.get())

        self.neutral.setValue(settings.threephase_calibration_neutral.get())
        self.right.setValue(settings.threephase_calibration_right.get())
        self.center.setValue(settings.threephase_calibration_center.get())

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

        self.groupBox_3.setVisible(False)
        self.exponent.setValue(settings.threephase_exponent.get())

        self.settings_changed()

        # connect edit boxes signals/slots
        self.neutral.valueChanged.connect(self.settings_changed)
        self.right.valueChanged.connect(self.settings_changed)
        self.center.valueChanged.connect(self.settings_changed)

        self.groupBox_2.clicked.connect(self.settings_changed)
        self.combobox_type.currentIndexChanged.connect(self.settings_changed)
        self.rotation.valueChanged.connect(self.settings_changed)
        self.mirror.stateChanged.connect(self.settings_changed)
        self.limit_top.valueChanged.connect(self.settings_changed)
        self.limit_bottom.valueChanged.connect(self.settings_changed)
        self.limit_right.valueChanged.connect(self.settings_changed)
        self.limit_left.valueChanged.connect(self.settings_changed)
        self.mapToEdge_start.valueChanged.connect(self.settings_changed)
        self.mapToEdge_length.valueChanged.connect(self.settings_changed)
        self.mapToEdge_invert.toggled.connect(self.settings_changed)

        self.exponent.valueChanged.connect(self.settings_changed)

        # connect clicks on calibration diagram
        self.phase_widget_calibration.calibrationParametersChanged.connect(self.calibration_phase_diagram_changed)

        # connect buttons signals/slots
        self.reset_defaults_button.clicked.connect(self.reset_defaults)

    threePhaseTransformChanged = QtCore.Signal()

    def settings_changed(self):
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

        self.calibrate_params.neutral.add(self.neutral.value())
        self.calibrate_params.right.add(self.right.value())
        self.calibrate_params.center.add(self.center.value())

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

        self.transform_params.exponent.add(self.exponent.value())

    def reset_defaults(self):
        self.rotation.setValue(0)
        self.mirror.setChecked(False)
        self.limit_top.setValue(1)
        self.limit_bottom.setValue(-1)
        self.limit_left.setValue(-1)
        self.limit_right.setValue(1)
        self.settings_changed()

    def calibration_phase_diagram_changed(self, neutral, right):
        self.neutral.setValue(neutral)
        self.right.setValue(right)

    def save_settings(self):
        settings.threephase_transform_combobox_selection.set(self.combobox_type.currentIndex())

        settings.threephase_calibration_neutral.set(self.neutral.value())
        settings.threephase_calibration_right.set(self.right.value())
        settings.threephase_calibration_center.set(self.center.value())

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

        settings.threephase_exponent.set(self.exponent.value())

