import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStyle
)

import stim_math.audio_gen.continuous
import stim_math.audio_gen.pulse_based
import stim_math.audio_gen.modify
from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.motion_generation
import qt_ui.audiogenerationwidget
import net.websocketserver
import net.tcpudpserver
import qt_ui.funscriptconversiondialog
import qt_ui.preferencesdialog
import net.serialproxy
import net.buttplug_wsdm_client
from qt_ui import resources

from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from qt_ui.threephase_configuration import ThreephaseConfiguration

from qt_ui.preferencesdialog import KEY_AUDIO_API, KEY_AUDIO_OUTPUT_DEVICE, KEY_AUDIO_INPUT_DEVICE, KEY_AUDIO_LATENCY
import sounddevice as sd

from qt_ui.device_selection_wizard import DeviceSelectionWizard, DeviceType


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # set the first tab as active tab, in case we forgot to set it in designer
        self.tabWidget.setCurrentIndex(0)
        # hide the focus tab
        self.tabWidget.setTabVisible(self.tabWidget.indexOf(self.tab_focus), False)
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_focus), False)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources.favicon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.threephase_parameters = ThreephaseParameterManager(ThreephaseConfiguration())

        self.motion_generator = qt_ui.motion_generation.MotionGenerator(self)

        self.motion_generator.positionChanged.connect(self.threephase_parameters.set_position_parameters)
        self.graphicsView.set_config_manager(self.threephase_parameters)
        self.graphicsView.mousePositionChanged.connect(self.motion_generator.updateMousePosition)
        self.graphicsView_2.set_config_manager(self.threephase_parameters)
        self.graphicsView_2.mousePositionChanged.connect(self.threephase_parameters.set_focus_parameters)

        self.tab_details.set_config_manager(self.threephase_parameters)
        self.progressBar_volume.set_config_manager(self.threephase_parameters)

        self.comboBox.currentTextChanged.connect(self.motion_generator.patternChanged)
        self.motion_generator.patternChanged(self.comboBox.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_generator.velocityChanged)
        self.motion_generator.velocityChanged(self.doubleSpinBox.value())

        self.audio_gen = qt_ui.audiogenerationwidget.AudioGenerationWidget(None)
        self.motion_generator.positionChanged.connect(self.threephase_parameters.set_position_parameters)
        self.tab_carrier.carrierSettingsChanged.connect(self.threephase_parameters.set_mk312_parameters)
        self.tab_pulse_settings.pulseSettingsChanged.connect(self.threephase_parameters.set_pulse_parameters)
        self.tab_threephase.threePhaseSettingsChanged.connect(self.threephase_parameters.set_calibration_parameters)
        self.tab_threephase.threePhaseTransformChanged.connect(self.threephase_parameters.set_three_phase_transform_parameters)
        self.tab_vibrate.vibrationSettingsChanged.connect(self.threephase_parameters.set_vibration_parameters)
        self.tab_threephase.set_config_manager(self.threephase_parameters)

        self.tab_fivephase.fivePhaseCurrentChanged.connect(self.threephase_parameters.set_five_phase_current_parameters)
        self.tab_fivephase.fivePhaseResistanceChanged.connect(self.threephase_parameters.set_five_phase_resistance_parameters)

        self.websocket_server = net.websocketserver.WebSocketServer(self)
        self.websocket_server.new_tcode_command.connect(self.threephase_parameters.parse_tcode_command)

        self.tcpudp_server = net.tcpudpserver.TcpUdpServer(self)
        self.tcpudp_server.new_tcode_command.connect(self.threephase_parameters.parse_tcode_command)

        self.serial_proxy = net.serialproxy.SerialProxy(self)
        self.serial_proxy.new_tcode_command.connect(self.threephase_parameters.parse_tcode_command)

        self.buttplug_wsdm_client = net.buttplug_wsdm_client.ButtplugWsdmClient(self)
        self.buttplug_wsdm_client.new_tcode_command.connect(self.threephase_parameters.parse_tcode_command)

        self.volumeWidget.rampVolumeChanged.connect(self.threephase_parameters.set_ramp_volume)
        self.volumeWidget.inactivityVolumeChanged.connect(self.threephase_parameters.set_inactivity_volume)
        self.volumeWidget.set_config_manager(self.threephase_parameters)

        # trigger updates
        self.tab_carrier.settings_changed()
        self.tab_pulse_settings.settings_changed()
        self.tab_threephase.settings_changed()
        self.volumeWidget.updateVolume()
        self.tab_fivephase.power_changed()
        self.tab_fivephase.resistance_changed()
        self.tab_vibrate.settings_changed()

        self.startStopAudioButton.clicked.connect(self.audioStartStop)
        self.audioStop() # update button icon/label

        self.wizard = DeviceSelectionWizard(self)
        self.actionDevice_selection_wizard.triggered.connect(self.show_setup_wizard)

        self.dialog = qt_ui.funscriptconversiondialog.FunscriptConversionDialog()
        self.actionFunscript_conversion.triggered.connect(self.openFunscriptConversionDialog)

        self.settings_dialog = qt_ui.preferencesdialog.PreferencesDialog()
        self.actionPreferences.triggered.connect(self.openPreferencesDialog)

        self.refresh_device_type()
        if self.wizard.device_type() == DeviceType.NONE:
            self.show_setup_wizard()

    def show_setup_wizard(self):
        self.audioStop()
        self.wizard.exec()
        self.refresh_device_type()

    def refresh_device_type(self):
        def set_visible(widget, state):
            self.tabWidget.setTabVisible(self.tabWidget.indexOf(widget), state)
            self.tabWidget.setTabEnabled(self.tabWidget.indexOf(widget), state)

        all_tabs = {self.tab_threephase,
                    self.tab_fivephase,
                    self.tab_pulse_settings,
                    self.tab_carrier,
                    self.tab_volume,
                    self.tab_vibrate,
                    self.tab_details,
                    self.tab_focus}

        visible = {self.tab_threephase, self.tab_volume, self.tab_vibrate, self.tab_details}

        if self.wizard.device_type() == DeviceType.THREE_PHASE:
            visible |= {self.tab_pulse_settings}
        elif self.wizard.device_type() == DeviceType.FOUR_PHASE:
            visible |= {self.tab_carrier, self.tab_fivephase}
        elif self.wizard.device_type() == DeviceType.FIVE_PHASE:
            visible |= {self.tab_carrier, self.tab_fivephase}
        elif self.wizard.device_type() == DeviceType.MK312:
            visible |= {self.tab_carrier}
        elif self.wizard.device_type() == DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO:
            visible -= {self.tab_volume, self.tab_vibrate, self.tab_details}

        for tab in all_tabs:
            set_visible(tab, tab in visible)

    def audioStartStop(self):
        if self.audio_gen.stream is None:
            self.audioStart()
        else:
            self.audioStop()

    def audioStart(self):
        settings = QSettings()
        api_name = settings.value(KEY_AUDIO_API, sd.query_hostapis(sd.default.hostapi)['name'])
        input_device_name = settings.value(KEY_AUDIO_INPUT_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        output_device_name = settings.value(KEY_AUDIO_OUTPUT_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        latency = settings.value(KEY_AUDIO_LATENCY, 'high')
        try:
            latency = float(latency)
        except ValueError:
            pass

        device_selection = self.wizard.device_type()
        if device_selection == DeviceType.MK312:
            algorithm = stim_math.audio_gen.continuous.ThreePhaseAlgorithm(self.threephase_parameters)
        elif device_selection == DeviceType.THREE_PHASE:
            algorithm = stim_math.audio_gen.pulse_based.DefaultThreePhasePulseBasedAlgorithm(self.threephase_parameters)
        elif device_selection == DeviceType.FOUR_PHASE:
            algorithm = stim_math.audio_gen.continuous.FourPhaseAlgorithm(self.threephase_parameters)
        elif device_selection == DeviceType.FIVE_PHASE:
            algorithm = stim_math.audio_gen.continuous.FivePhaseAlgorithm(self.threephase_parameters)
        elif device_selection == DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO:
            algorithm = stim_math.audio_gen.modify.ThreePhaseModifyAlgorithm(self.threephase_parameters)
        else:
            raise RuntimeError('unknown device type')

        if device_selection in [DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO]:
            self.audio_gen.start_modify(api_name, input_device_name, output_device_name, latency, algorithm)
        else:
            self.audio_gen.start(api_name, output_device_name, latency, algorithm)
        if self.audio_gen.stream is not None:
            pixmapi = getattr(QStyle, 'SP_MediaStop')
            icon = self.style().standardIcon(pixmapi)
            self.startStopAudioButton.setIcon(icon)
            self.startStopAudioButton.setText("Stop audio")

    def audioStop(self):
        self.audio_gen.stop()
        pixmapi = getattr(QStyle, 'SP_MediaPlay')
        icon = self.style().standardIcon(pixmapi)
        self.startStopAudioButton.setIcon(icon)
        self.startStopAudioButton.setText("Start audio")

    def openFunscriptConversionDialog(self):
        self.audioStop()
        self.dialog.exec()

    def openPreferencesDialog(self):
        self.audioStop()
        self.settings_dialog.exec()
        self.threephase_parameters.set_configuration(ThreephaseConfiguration())
        self.graphicsView.refreshSettings()
        self.progressBar_volume.refreshSettings()

    def closeEvent(self, event):
        print('closeEvent')
        self.audio_gen.stop()
        event.accept()


def run():
    QApplication.setApplicationName("restim")
    QApplication.setOrganizationName("restim")
    QSettings.setDefaultFormat(QSettings.IniFormat)

    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()