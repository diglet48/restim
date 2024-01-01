from PyQt5.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QRadioButton
from enum import Enum
from qt_ui import settings


class DeviceType(Enum):
    NONE = 0
    THREE_PHASE = 1
    FOUR_PHASE = 2
    FIVE_PHASE = 3
    MK312 = 4
    MODIFY_EXISTING_THREEPHASE_AUDIO = 5


class PhaseSelectionWizardPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Select device type')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.stereo_p3_radio = QRadioButton("Stereostim, Three phase")
        self.stereo_p4_radio = QRadioButton("Stereostim, Four phase (experimental)")
        self.stereo_p5_radio = QRadioButton("Stereostim, Five phase (experimental)")
        self.mk312_radio = QRadioButton("312 or 2B")
        self.modify_existing_radio = QRadioButton("Modify (calibrate) existing three phase audio")

        selection = DeviceType(settings.device_type.get())
        self.stereo_p3_radio.setChecked(selection == DeviceType.THREE_PHASE)
        self.stereo_p4_radio.setChecked(selection == DeviceType.FOUR_PHASE)
        self.stereo_p5_radio.setChecked(selection == DeviceType.FIVE_PHASE)
        self.mk312_radio.setChecked(selection == DeviceType.MK312)
        self.modify_existing_radio.setChecked((selection == DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO))

        layout.addWidget(self.stereo_p3_radio)
        layout.addWidget(self.stereo_p4_radio)
        layout.addWidget(self.stereo_p5_radio)
        layout.addWidget(self.mk312_radio)
        layout.addWidget(self.modify_existing_radio)

        self.stereo_p3_radio.toggled.connect(self.settings_changed)
        self.stereo_p4_radio.toggled.connect(self.settings_changed)
        self.stereo_p5_radio.toggled.connect(self.settings_changed)
        self.mk312_radio.toggled.connect(self.settings_changed)
        self.modify_existing_radio.toggled.connect(self.settings_changed)

    def device_type(self) -> DeviceType:
        if self.stereo_p3_radio.isChecked():
            return DeviceType.THREE_PHASE
        elif self.stereo_p4_radio.isChecked():
            return DeviceType.FOUR_PHASE
        elif self.stereo_p5_radio.isChecked():
            return DeviceType.FIVE_PHASE
        elif self.mk312_radio.isChecked():
            return DeviceType.MK312
        elif self.modify_existing_radio.isChecked():
            return DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO
        else:
            return DeviceType.NONE

    def settings_changed(self):
        settings.device_type.set(self.device_type().value)


class DeviceSelectionWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup wizard")
        self.page1 = PhaseSelectionWizardPage(self)
        self.addPage(self.page1)

        # self.setWizardStyle(QWizard.ClassicStyle)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage)
        self.setOption(QWizard.NoCancelButton)

        self.button(QWizard.FinishButton).setEnabled(True)

    def device_type(self):
        return self.page1.device_type()