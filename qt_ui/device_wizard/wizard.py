from enum import Enum
import logging

from PySide6.QtWidgets import QWizard

from qt_ui.device_wizard.focstim_waveform_select import WizardPageFocStimWaveformSelect
from qt_ui.device_wizard.safety_limits_foc import WizardPageSafetyLimitsFOC
from qt_ui.device_wizard.type_select import WizardPageDeviceType
from qt_ui.device_wizard.waveform_select import WizardPageWaveformType
from qt_ui.device_wizard.safety_limits import WizardPageSafetyLimits
from qt_ui.device_wizard.neostim_waveform_select import WizardPageNeoStimWaveformSelect
from qt_ui.device_wizard.coyote_waveform_select import WizardPageCoyoteWaveformSelect
from qt_ui.device_wizard.enums import DeviceType, WaveformType, DeviceConfiguration
from qt_ui.settings import device_config_waveform_amplitude_amps
from device.coyote import constants as coyote_constants


logger = logging.getLogger('restim.device_wizard')


class WizardPage(Enum):
    Page_device = 1
    Page_waveform = 2
    Page_limits = 3
    Page_limits_foc = 6
    Page_neostim_waveform = 4
    Page_focstim_waveform = 5
    Page_coyote_waveform = 7


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
        self.page_safety_limits.setFinalPage(True)
        self.setPage(WizardPage.Page_limits.value, self.page_safety_limits)
        self.page_safety_limits_foc = WizardPageSafetyLimitsFOC()
        self.page_safety_limits_foc.setFinalPage(True)
        self.setPage(WizardPage.Page_limits_foc.value, self.page_safety_limits_foc)
        self.page_neostim_waveform_select = WizardPageNeoStimWaveformSelect()
        self.setPage(WizardPage.Page_neostim_waveform.value, self.page_neostim_waveform_select)
        self.page_focstim_waveform_select = WizardPageFocStimWaveformSelect()
        self.setPage(WizardPage.Page_focstim_waveform.value, self.page_focstim_waveform_select)
        self.page_coyote_waveform_select = WizardPageCoyoteWaveformSelect()
        self.page_coyote_waveform_select.setFinalPage(True)
        self.setPage(WizardPage.Page_coyote_waveform.value, self.page_coyote_waveform_select)

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

    def nextId(self):
        if self.currentId() is None:
            return WizardPage.Page_device.value

        if self.currentId() == WizardPage.Page_device.value:
            if self.page_device_type.audio_based_radio.isChecked():
                return WizardPage.Page_waveform.value
            elif self.page_device_type.focstim_radio.isChecked():
                return WizardPage.Page_focstim_waveform.value
            elif self.page_device_type.neostim_radio.isChecked():
                return WizardPage.Page_neostim_waveform.value
            elif self.page_device_type.coyote_radio.isChecked():
                return WizardPage.Page_coyote_waveform.value
            else:
                raise RuntimeError("unknown device type")

        if self.currentId() == WizardPage.Page_waveform.value:
            return WizardPage.Page_limits.value
        elif self.currentId() == WizardPage.Page_focstim_waveform.value:
            return WizardPage.Page_limits_foc.value
        return -1

    def validateCurrentPage(self) -> bool:
        if self.currentId() == WizardPage.Page_device.value:
            # Enable/disable the relevant waveform types.
            if self.page_device_type.audio_based_radio.isChecked():
                self.page_waveform_type.pulse_based_radio.setEnabled(True)
                self.page_waveform_type.continuous_radio.setEnabled(True)
                self.page_waveform_type.a_b_radio.setEnabled(True)
            elif self.page_device_type.focstim_radio.isChecked():
                pass
            elif self.page_device_type.neostim_radio.isChecked():
                pass
            elif self.page_device_type.coyote_radio.isChecked():
                pass

        return super(DeviceSelectionWizard, self).validateCurrentPage()

    def get_configuration(self) -> DeviceConfiguration:
        min_freq = self.page_safety_limits.min_frequency_spinbox.value()
        max_freq = self.page_safety_limits.max_frequency_spinbox.value()

        min_freq_foc = self.page_safety_limits_foc.min_frequency_spinbox.value()
        max_freq_foc = self.page_safety_limits_foc.max_frequency_spinbox.value()
        waveform_ampltiude_amps = self.page_safety_limits_foc.waveform_ampltiude_ma_spinbox.value() * 0.001

        if self.page_device_type.audio_based_radio.isChecked():
            if self.page_waveform_type.continuous_radio.isChecked():
                alg = WaveformType.CONTINUOUS
            elif self.page_waveform_type.pulse_based_radio.isChecked():
                alg = WaveformType.PULSE_BASED
            elif self.page_waveform_type.a_b_radio.isChecked():
                alg = WaveformType.A_B_TESTING
            else:
                assert False
            return DeviceConfiguration(
                DeviceType.AUDIO_THREE_PHASE,
                alg,
                min_freq, max_freq,
                waveform_ampltiude_amps
            )
        elif self.page_device_type.focstim_radio.isChecked():
            if self.page_focstim_waveform_select.three_phase_radio.isChecked():
                return DeviceConfiguration(
                    DeviceType.FOCSTIM_THREE_PHASE,
                    WaveformType.PULSE_BASED,
                    min_freq_foc, max_freq_foc,
                    waveform_ampltiude_amps
                )
            elif self.page_focstim_waveform_select.four_phase_radio.isChecked():
                return DeviceConfiguration(
                    DeviceType.FOCSTIM_FOUR_PHASE,
                    WaveformType.PULSE_BASED,
                    min_freq_foc, max_freq_foc,
                    waveform_ampltiude_amps
                )
            else:
                assert False
        elif self.page_device_type.neostim_radio.isChecked():
            return DeviceConfiguration(
                DeviceType.NEOSTIM_THREE_PHASE,
                None,
                None, None,
                None
            )
        elif self.page_device_type.coyote_radio.isChecked():
            return DeviceConfiguration(
                DeviceType.COYOTE_THREE_PHASE,
                WaveformType.PULSE_BASED,
                coyote_constants.HARDWARE_MIN_FREQ_HZ,
                coyote_constants.HARDWARE_MAX_FREQ_HZ,
                None
            )
        else:
            assert(False)

    def set_configuration(self, config: DeviceConfiguration):
        if config.device_type == DeviceType.AUDIO_THREE_PHASE:
            self.page_device_type.audio_based_radio.setChecked(True)
        if config.device_type == DeviceType.FOCSTIM_THREE_PHASE:
            self.page_device_type.focstim_radio.setChecked(True)
            self.page_focstim_waveform_select.three_phase_radio.setChecked(True)
        if config.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            self.page_device_type.focstim_radio.setChecked(True)
            self.page_focstim_waveform_select.four_phase_radio.setChecked(True)
        if config.device_type == DeviceType.NEOSTIM_THREE_PHASE:
            self.page_device_type.neostim_radio.setChecked(True)
        if config.device_type == DeviceType.COYOTE_THREE_PHASE:
            self.page_device_type.coyote_radio.setChecked(True)

        self.page_waveform_type.continuous_radio.setChecked(config.waveform_type == WaveformType.CONTINUOUS)
        self.page_waveform_type.pulse_based_radio.setChecked(config.waveform_type == WaveformType.PULSE_BASED)
        self.page_waveform_type.a_b_radio.setChecked(config.waveform_type == WaveformType.A_B_TESTING)

        self.page_safety_limits.min_frequency_spinbox.setValue(config.min_frequency)
        self.page_safety_limits.max_frequency_spinbox.setValue(config.max_frequency)

        self.page_safety_limits_foc.min_frequency_spinbox.setValue(config.min_frequency)
        self.page_safety_limits_foc.max_frequency_spinbox.setValue(config.max_frequency)
        self.page_safety_limits_foc.waveform_ampltiude_ma_spinbox.setValue(config.waveform_amplitude_amps * 1000)

