from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWizardPage

from qt_ui.device_wizard.focstim_waveform_select_ui import Ui_WizardPageFocStim


class WizardPageFocStimWaveformSelect(QWizardPage, Ui_WizardPageFocStim):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.three_phase_radio.toggled.connect(self.completeChanged)
        self.four_phase_radio.toggled.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return any([
            self.three_phase_radio.isChecked(),
            self.four_phase_radio.isChecked(),
        ])
