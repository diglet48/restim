from __future__ import unicode_literals

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings

from qt_ui.five_phase_settings_widget_ui import Ui_FivePhaseSettingsWidget
from stim_math.audio_gen.params import FivephaseCalibrationParams, FivephasePositionParams
from stim_math.axis import create_temporal_axis, create_constant_axis


class FivePhaseSettingsWidget(QtWidgets.QWidget, Ui_FivePhaseSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.settings = QSettings()

        self.position = FivephasePositionParams(
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
        )
        self.calibration = FivephaseCalibrationParams(
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
            create_constant_axis(0.0),
        )

        self.slider_e1.setValue(100)
        self.slider_e2.setValue(0)
        self.slider_e3.setValue(30)
        self.slider_e4.setValue(60)
        self.slider_e5.setValue(100)

        self.slider_e1.valueChanged.connect(self.power_changed)
        self.slider_e2.valueChanged.connect(self.power_changed)
        self.slider_e3.valueChanged.connect(self.power_changed)
        self.slider_e4.valueChanged.connect(self.power_changed)
        self.slider_e5.valueChanged.connect(self.power_changed)

        self.spinBox_t.setValue(1000)
        self.spinBox_s1.setValue(500)
        self.spinBox_s2.setValue(500)
        self.spinBox_s3.setValue(500)
        self.spinBox_s4.setValue(500)
        self.spinBox_s5.setValue(500)

        self.spinBox_t.valueChanged.connect(self.resistance_changed)
        self.spinBox_s1.valueChanged.connect(self.resistance_changed)
        self.spinBox_s2.valueChanged.connect(self.resistance_changed)
        self.spinBox_s3.valueChanged.connect(self.resistance_changed)
        self.spinBox_s4.valueChanged.connect(self.resistance_changed)
        self.spinBox_s5.valueChanged.connect(self.resistance_changed)

        self.power_changed()
        self.resistance_changed()

    def power_changed(self):
        self.position.e1.add(self.slider_e1.value() / 100),
        self.position.e2.add(self.slider_e2.value() / 100),
        self.position.e3.add(self.slider_e3.value() / 100),
        self.position.e4.add(self.slider_e4.value() / 100),
        self.position.e5.add(self.slider_e5.value() / 100),

    def resistance_changed(self):
        self.calibration.t.add(self.spinBox_t.value())
        self.calibration.s1.add(self.spinBox_s1.value())
        self.calibration.s2.add(self.spinBox_s2.value())
        self.calibration.s3.add(self.spinBox_s3.value())
        self.calibration.s4.add(self.spinBox_s4.value())
        self.calibration.s5.add(self.spinBox_s5.value())

    def save_settings(self):
        # TODO
        pass