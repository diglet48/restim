from PySide6.QtWidgets import QWizardPage

from qt_ui.device_wizard.safety_limits_foc_ui import Ui_WizardPageSafetyLimitsFOC

from stim_math import limits


class WizardPageSafetyLimitsFOC(QWizardPage, Ui_WizardPageSafetyLimitsFOC):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.waveform_ampltiude_ma_spinbox.setMinimum(limits.WaveformAmpltiudeFOC.min * 1000)
        self.waveform_ampltiude_ma_spinbox.setMaximum(limits.WaveformAmpltiudeFOC.max * 1000)

    def validatePage(self) -> bool:
        return self.min_frequency_spinbox.value() < self.max_frequency_spinbox.value()