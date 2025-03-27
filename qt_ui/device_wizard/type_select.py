from PySide6.QtWidgets import QWizardPage

from qt_ui.device_wizard.type_select_ui import Ui_WizardPageDeviceType


class WizardPageDeviceType(QWizardPage, Ui_WizardPageDeviceType):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.three_phase_radio.toggled.connect(self.completeChanged)
        self.focstim_radio.toggled.connect(self.completeChanged)
        self.neostim_radio.toggled.connect(self.completeChanged)

    def isComplete(self) -> bool:
        return any([
                self.three_phase_radio.isChecked(),
                self.focstim_radio.isChecked(),
                self.neostim_radio.isChecked()
        ])
