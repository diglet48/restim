from enum import Enum
import logging

from PyQt5.QtWidgets import QWizard
from qt_ui.device_wizard.type_select import WizardPageDeviceType
from qt_ui.device_wizard.waveform_select import WizardPageWaveformType
from qt_ui.device_wizard.safety_limits import WizardPageSafetyLimits
from qt_ui.device_wizard.enums import DeviceType, WaveformType, DeviceConfiguration


logger = logging.getLogger('restim.device_wizard')


class WizardPage(Enum):
    Page_device = 1
    Page_waveform = 2
    Page_limits = 3


class DeviceSelectionWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Device configuration wizard')

        self.setWizardStyle(QWizard.ClassicStyle)
        self.setFixedSize(500, 500)
        self.setOption(QWizard.NoCancelButton)

        self.page_device_type = WizardPageDeviceType()
        self.setPage(WizardPage.Page_device.value, self.page_device_type)
        self.page_waveform_type = WizardPageWaveformType()
        self.setPage(WizardPage.Page_waveform.value, self.page_waveform_type)
        self.page_safety_limits = WizardPageSafetyLimits()
        self.setPage(WizardPage.Page_limits.value, self.page_safety_limits)

        self.set_configuration(DeviceConfiguration.from_settings())

        self.accepted.connect(self.save_config)

    def save_config(self):
        config = self.get_configuration()
        logger.info(f'saving config {config}')
        config.save()

    def exec(self) -> None:
        self.restart()
        config = DeviceConfiguration.from_settings()
        logger.info(f'load config {config}')
        self.set_configuration(config)
        super(DeviceSelectionWizard, self).exec()

    # def nextId(self) -> int:
    #     if self.currentId() == WizardPage.Page_device.value:
    #         if self.page_device_type.three_phase_radio.isChecked():
    #             return WizardPage.Page_waveform.value
    #         else:
    #             return WizardPage.Page_limits.value
    #     elif self.currentId() == WizardPage.Page_waveform.value:
    #         return WizardPage.Page_limits.value
    #     return -1

    def validateCurrentPage(self) -> bool:
        # disable 'pulse-based' option when 4/5-phase is selected
        selection_is_threephase = self.page_device_type.three_phase_radio.isChecked()
        self.page_waveform_type.pulse_based_radio.setEnabled(selection_is_threephase)
        if not selection_is_threephase:
            self.page_waveform_type.pulse_based_radio.setChecked(False)
        self.page_waveform_type.a_b_radio.setEnabled(selection_is_threephase)
        if not selection_is_threephase:
            self.page_waveform_type.a_b_radio.setChecked(False)

        return super(DeviceSelectionWizard, self).validateCurrentPage()

    def get_configuration(self) -> DeviceConfiguration:
        min_freq = self.page_safety_limits.min_frequency_spinbox.value()
        max_freq = self.page_safety_limits.max_frequency_spinbox.value()

        if self.page_device_type.three_phase_radio.isChecked():
            if self.page_waveform_type.continuous_radio.isChecked():
                alg = WaveformType.CONTINUOUS
            elif self.page_waveform_type.pulse_based_radio.isChecked():
                alg = WaveformType.PULSE_BASED
            elif self.page_waveform_type.a_b_radio.isChecked():
                alg = WaveformType.A_B_TESTING
            else:
                assert False
            return DeviceConfiguration(
                DeviceType.THREE_PHASE,
                alg,
                min_freq, max_freq
            )
        elif self.page_device_type.four_phase_radio.isChecked():
            return DeviceConfiguration(
                DeviceType.FOUR_PHASE,
                WaveformType.CONTINUOUS,
                min_freq, max_freq
            )
        elif self.page_device_type.five_phase_radio.isChecked():
            return DeviceConfiguration(
                DeviceType.FIVE_PHASE,
                WaveformType.CONTINUOUS,
                min_freq, max_freq
            )
        else:
            assert(False)

    def set_configuration(self, config: DeviceConfiguration):
        if config.device_type == DeviceType.THREE_PHASE:
            self.page_device_type.three_phase_radio.setChecked(True)
        if config.device_type == DeviceType.FOUR_PHASE:
            self.page_device_type.four_phase_radio.setChecked(True)
        if config.device_type == DeviceType.FIVE_PHASE:
            self.page_device_type.five_phase_radio.setChecked(True)

        if config.waveform_type == WaveformType.CONTINUOUS:
            self.page_waveform_type.continuous_radio.setChecked(True)
        elif config.waveform_type == WaveformType.PULSE_BASED:
            self.page_waveform_type.pulse_based_radio.setChecked(True)
        elif config.waveform_type == WaveformType.A_B_TESTING:
            self.page_waveform_type.a_b_radio.setChecked(True)

        self.page_safety_limits.min_frequency_spinbox.setValue(config.min_frequency)
        self.page_safety_limits.max_frequency_spinbox.setValue(config.max_frequency)
