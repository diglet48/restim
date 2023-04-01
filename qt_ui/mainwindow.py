import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStyle
)


from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.motion_generation
import qt_ui.audiogenerationwidget
import qt_ui.websocketserver
import qt_ui.tcpudpserver
import qt_ui.funscriptconversiondialog
import qt_ui.preferencesdialog

from qt_ui.preferencesdialog import KEY_AUDIO_API, KEY_AUDIO_DEVICE, KEY_AUDIO_LATENCY
import sounddevice as sd


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.motion_generator = qt_ui.motion_generation.MotionGenerator(self)

        self.tab_calibration.calibrationSettingsChanged.connect(self.tab_details.updateCalibrationParameters)

        self.motion_generator.positionChanged.connect(self.graphicsView.updatePositionParameters)
        self.motion_generator.positionChanged.connect(self.tab_details.updatePositionParameters)
        self.graphicsView.mousePositionChanged.connect(self.motion_generator.updateMousePosition)

        self.comboBox.currentTextChanged.connect(self.motion_generator.patternChanged)
        self.motion_generator.patternChanged(self.comboBox.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_generator.velocityChanged)
        self.motion_generator.velocityChanged(self.doubleSpinBox.value())

        self.audio_gen = qt_ui.audiogenerationwidget.AudioGenerationWidget(None)
        self.motion_generator.positionChanged.connect(self.audio_gen.updatePositionParameters)
        self.tab_carrier.modulationSettingsChanged.connect(self.audio_gen.updateModulationParameters)
        self.tab_transform_calibration.transformCalibrationSettingsChanged.connect(self.audio_gen.updateTransformParameters)
        self.tab_calibration.calibrationSettingsChanged.connect(self.audio_gen.updateCalibrationParameters)

        self.websocket_server = qt_ui.websocketserver.WebSocketServer(self)
        self.websocket_server.alphaChanged.connect(self.graphicsView.updateAlphaPosition)
        self.websocket_server.betaChanged.connect(self.graphicsView.updateBetaPosition)
        self.websocket_server.alphaChanged.connect(self.audio_gen.updateAlpha)
        self.websocket_server.betaChanged.connect(self.audio_gen.updateBeta)
        # self.websocket_server.volumeChanged.connect(self.audio_gen.updateVolume)

        self.tcpudp_server = qt_ui.tcpudpserver.TcpUdpServer(self)
        self.tcpudp_server.alphaChanged.connect(self.graphicsView.updateAlphaPosition)
        self.tcpudp_server.betaChanged.connect(self.graphicsView.updateBetaPosition)
        self.tcpudp_server.alphaChanged.connect(self.audio_gen.updateAlpha)
        self.tcpudp_server.betaChanged.connect(self.audio_gen.updateBeta)
        # self.tcpudp_server.volumeChanged.connect(self.audio_gen.updateVolume)

        self.volumeWidget.volumeChanged.connect(self.audio_gen.updateGuiVolume)

        # trigger updates
        self.tab_calibration.settings_changed()
        self.tab_carrier.settings_changed()
        self.tab_transform_calibration.settings_changed()
        self.volumeWidget.updateVolume()

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
        self.audio_gen.start(api_name, device_name, latency)
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

    def audioDeviceSelectionChanged(self, index):
        self.audio_gen.select_device_index(self.comboBoxAudioDevice.currentData().device_index)

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