import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStyle
)


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

from qt_ui.preferencesdialog import KEY_AUDIO_API, KEY_AUDIO_DEVICE, KEY_AUDIO_LATENCY
import sounddevice as sd
import stim_math.generate


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources.favicon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.comboBox_phase_selection.addItem("Three-phase", 3)
        self.comboBox_phase_selection.addItem("Four-phase", 4)
        self.comboBox_phase_selection.addItem("Five-phase", 5)

        self.threephase_parameters = ThreephaseParameterManager(ThreephaseConfiguration())

        self.motion_generator = qt_ui.motion_generation.MotionGenerator(self)

        self.motion_generator.positionChanged.connect(self.threephase_parameters.set_position_parameters)
        self.graphicsView.set_config_manager(self.threephase_parameters)
        self.graphicsView.mousePositionChanged.connect(self.motion_generator.updateMousePosition)
        self.tab_details.set_config_manager(self.threephase_parameters)
        self.progressBar_volume.set_config_manager(self.threephase_parameters)

        self.comboBox.currentTextChanged.connect(self.motion_generator.patternChanged)
        self.motion_generator.patternChanged(self.comboBox.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_generator.velocityChanged)
        self.motion_generator.velocityChanged(self.doubleSpinBox.value())

        self.audio_gen = qt_ui.audiogenerationwidget.AudioGenerationWidget(None)
        self.motion_generator.positionChanged.connect(self.threephase_parameters.set_position_parameters)
        self.tab_carrier.modulationSettingsChanged.connect(self.threephase_parameters.set_modulation_parameters)
        self.tab_transform_calibration.transformCalibrationSettingsChanged.connect(self.threephase_parameters.set_calibration_parameters)

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
        self.tab_transform_calibration.settings_changed()
        self.volumeWidget.updateVolume()
        self.tab_fivephase.power_changed()
        self.tab_fivephase.resistance_changed()

        self.startStopAudioButton.clicked.connect(self.audioStartStop)
        self.audioStop() # update button icon/label

        self.dialog = qt_ui.funscriptconversiondialog.FunscriptConversionDialog()
        self.actionFunscript_conversion_2.triggered.connect(self.openFunscriptConversionDialog)

        self.settings_dialog = qt_ui.preferencesdialog.PreferencesDialog()
        self.actionPreferences.triggered.connect(self.openPreferencesDialog)

    def audioStartStop(self):
        if self.audio_gen.stream is None:
            self.audioStart()
        else:
            self.audioStop()

    def audioStart(self):
        settings = QSettings()
        api_name = settings.value(KEY_AUDIO_API, sd.query_hostapis(sd.default.hostapi)['name'])
        device_name = settings.value(KEY_AUDIO_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        latency = settings.value(KEY_AUDIO_LATENCY, 'high')
        try:
            latency = float(latency)
        except ValueError:
            pass
        phases = int(self.comboBox_phase_selection.currentData())
        if phases == 3:
            algorithm = stim_math.generate.ThreePhaseAlgorithm(self.threephase_parameters)
        elif phases == 4:
            algorithm = stim_math.generate.FourPhaseAlgorithm(self.threephase_parameters)
        else:
            algorithm = stim_math.generate.FivePhaseAlgorithm(self.threephase_parameters)

        self.audio_gen.start(api_name, device_name, latency, algorithm)
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