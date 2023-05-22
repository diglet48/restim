from __future__ import unicode_literals

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings

from qt_ui.five_phase_settings_widget_ui import Ui_FivePhaseSettingsWidget
from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from qt_ui.stim_config import FivePhaseResistanceParameters, FivePhaseCurrentParameters


class FivePhaseSettingsWidget(QtWidgets.QWidget, Ui_FivePhaseSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.settings = QSettings()

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

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def power_changed(self):
        params = FivePhaseCurrentParameters(
            self.slider_e1.value() / 100,
            self.slider_e2.value() / 100,
            self.slider_e3.value() / 100,
            self.slider_e4.value() / 100,
            self.slider_e5.value() / 100,
        )
        self.fivePhaseCurrentChanged.emit(params)

    def resistance_changed(self):
        params = FivePhaseResistanceParameters(
            self.spinBox_t.value(),
            self.spinBox_s1.value(),
            self.spinBox_s2.value(),
            self.spinBox_s3.value(),
            self.spinBox_s4.value(),
            self.spinBox_s5.value(),
        )
        self.fivePhaseResistanceChanged.emit(params)

    fivePhaseCurrentChanged = QtCore.pyqtSignal(FivePhaseCurrentParameters)
    fivePhaseResistanceChanged = QtCore.pyqtSignal(FivePhaseResistanceParameters)
