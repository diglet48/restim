from __future__ import unicode_literals
import numpy as np

from stim_math.threephase_parameter_manager import ThreephaseParameterManager

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings

from qt_ui.three_phase_settings_widget import Ui_ThreePhaseSettingsWidget
from qt_ui.stim_config import ThreePhaseCalibrationParameters, ThreePhaseTransformParameters


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
        self.settings = QSettings()

        self.neutral.setValue(self.settings.value(SETTING_CALIBRATION_NEUTRAL, 0.0, float))
        self.right.setValue(self.settings.value(SETTING_CALIBRATION_RIGHT, 0.0, float))
        self.center.setValue(self.settings.value(SETTING_CALIBRATION_CENTER, 0.0, float))

        self.groupBox_2.setChecked(self.settings.value(SETTING_TRANSFORM_ENABLED, False, bool))
        self.rotation.setValue(self.settings.value(SETTING_TRANSFORM_ROTATE, 0.0, float))
        self.mirror.setChecked(self.settings.value(SETTING_TRANSFORM_MIRROR, False, bool))
        self.limit_top.setValue(self.settings.value(SETTING_TRANSFORM_LIMIT_TOP, 1.0, float))
        self.limit_bottom.setValue(self.settings.value(SETTING_TRANSFORM_LIMIT_BOTTOM, -1.0, float))
        self.limit_left.setValue(self.settings.value(SETTING_TRANSFORM_LIMIT_LEFT, -1.0, float))
        self.limit_right.setValue(self.settings.value(SETTING_TRANSFORM_LIMIT_RIGHT, 1.0, float))

        self.groupBox_3.setVisible(False)
        self.exponent.setValue(self.settings.value(SETTING_THREEPHASE_EXPONENT, 0.0, float))

        self.settings_changed()

        self.neutral.valueChanged.connect(self.settings_changed)
        self.right.valueChanged.connect(self.settings_changed)
        self.center.valueChanged.connect(self.settings_changed)

        self.groupBox_2.clicked.connect(self.settings_changed)
        self.rotation.valueChanged.connect(self.settings_changed)
        self.mirror.stateChanged.connect(self.settings_changed)
        self.limit_top.valueChanged.connect(self.settings_changed)
        self.limit_bottom.valueChanged.connect(self.settings_changed)
        self.limit_right.valueChanged.connect(self.settings_changed)
        self.limit_left.valueChanged.connect(self.settings_changed)

        self.exponent.valueChanged.connect(self.settings_changed)

        self.phase_widget_calibration.calibrationParametersChanged.connect(self.calibration_phase_diagram_changed)

        self.reset_defaults_button.clicked.connect(self.reset_defaults)

    threePhaseSettingsChanged = QtCore.pyqtSignal(ThreePhaseCalibrationParameters)
    threePhaseTransformChanged = QtCore.pyqtSignal(ThreePhaseTransformParameters)

    def settings_changed(self):
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

        params = ThreePhaseCalibrationParameters(
            self.neutral.value(),
            self.right.value(),
            self.center.value()
        )
        self.threePhaseSettingsChanged.emit(params)

        self.settings.setValue(SETTING_CALIBRATION_NEUTRAL, self.neutral.value())
        self.settings.setValue(SETTING_CALIBRATION_RIGHT, self.right.value())
        self.settings.setValue(SETTING_CALIBRATION_CENTER, self.center.value())

        self.settings.setValue(SETTING_TRANSFORM_ENABLED, self.groupBox_2.isChecked())
        self.settings.setValue(SETTING_TRANSFORM_ROTATE, self.rotation.value())
        self.settings.setValue(SETTING_TRANSFORM_MIRROR, self.mirror.isChecked())
        self.settings.setValue(SETTING_TRANSFORM_LIMIT_TOP, self.limit_top.value())
        self.settings.setValue(SETTING_TRANSFORM_LIMIT_BOTTOM, self.limit_bottom.value())
        self.settings.setValue(SETTING_TRANSFORM_LIMIT_LEFT, self.limit_left.value())
        self.settings.setValue(SETTING_TRANSFORM_LIMIT_RIGHT, self.limit_right.value())
        self.settings.setValue(SETTING_THREEPHASE_EXPONENT, self.exponent.value())

        params = ThreePhaseTransformParameters(
            self.groupBox_2.isChecked(),
            self.rotation.value(),
            self.mirror.isChecked(),
            self.limit_top.value(),
            self.limit_bottom.value(),
            self.limit_left.value(),
            self.limit_right.value(),
            self.exponent.value()
        )
        self.threePhaseTransformChanged.emit(params)

    def reset_defaults(self):
        self.rotation.setValue(0)
        self.mirror.setChecked(False)
        self.limit_top.setValue(1)
        self.limit_bottom.setValue(-1)
        self.limit_left.setValue(-1)
        self.limit_right.setValue(1)

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config
        self.phase_widget_calibration.set_config_manager(config)

    def calibration_phase_diagram_changed(self, neutral, right):
        self.neutral.setValue(neutral)
        self.right.setValue(right)
