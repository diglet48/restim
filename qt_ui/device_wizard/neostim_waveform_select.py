from PyQt5 import Qt
from PyQt5.QtWidgets import QWizardPage

from qt_ui.device_wizard.neostim_waveform_select_ui import Ui_WizardPageNeoStim


class WizardPageNeoStimWaveformSelect(QWizardPage, Ui_WizardPageNeoStim):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.three_phase_radio.toggled.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return any([
            self.three_phase_radio.isChecked() and self.three_phase_radio.isEnabled(),
        ])
