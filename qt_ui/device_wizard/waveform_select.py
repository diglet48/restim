from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWizardPage, QSizePolicy

from qt_ui.device_wizard.waveform_select_ui import Ui_WizardPageWaveformType



class WizardPageWaveformType(QWizardPage, Ui_WizardPageWaveformType):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pulse_based_radio.toggled.connect(self.completeChanged)
        self.continuous_radio.toggled.connect(self.completeChanged)
        self.a_b_radio.toggled.connect(self.completeChanged)

        self.svg_continuous.load(":/restim/wizard/continuous.svg")
        self.svg_continuous.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.svg_pulse.load(":/restim/wizard/pulse_based.svg")
        self.svg_pulse.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def isComplete(self) -> bool:
        return any([
            self.pulse_based_radio.isChecked() and self.pulse_based_radio.isEnabled(),
            self.continuous_radio.isChecked() and self.continuous_radio.isEnabled(),
            self.a_b_radio.isChecked() and self.a_b_radio.isEnabled()
        ])
