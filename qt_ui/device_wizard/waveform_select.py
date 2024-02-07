from PyQt5.QtWidgets import QWizardPage

from qt_ui.device_wizard.waveform_select_ui import Ui_WizardPageWaveformType


class WizardPageWaveformType(QWizardPage, Ui_WizardPageWaveformType):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pulse_based_radio.toggled.connect(self.completeChanged)
        self.continuous_radio.toggled.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return any([
            self.pulse_based_radio.isChecked() and self.pulse_based_radio.isEnabled(),
            self.continuous_radio.isChecked() and self.continuous_radio.isEnabled()
        ])

