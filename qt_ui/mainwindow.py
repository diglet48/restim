import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)

from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.motion_generation
import qt_ui.audiogenerationwidget
import qt_ui.websocketserver
import qt_ui.funscriptconversiondialog


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

        # trigger updates
        self.tab_calibration.settings_changed()
        self.tab_carrier.settings_changed()
        self.tab_transform_calibration.settings_changed()

        self.startStopAudioButton.clicked.connect(self.audioStartStop)

        for device in self.audio_gen.list_devices():
            self.comboBoxAudioDevice.addItem(device.device_name, device)
        self.comboBoxAudioDevice.setStyleSheet("QComboBox QAbstractItemView {min-width: 400px;}"),
        self.comboBoxAudioDevice.currentIndexChanged.connect(self.audioDeviceSelectionChanged)


        dialog = qt_ui.funscriptconversiondialog.FunscriptConversionDialog()
        self.dialog = dialog

        self.actionFunscript_conversion_2.triggered.connect(self.openFunscriptConversionDialog)

    def audioStartStop(self):
        if self.audio_gen.stream is None:
            self.startStopAudioButton.setText("Stop audio")
            self.audio_gen.start()
        else:
            self.startStopAudioButton.setText("Start audio")
            self.audio_gen.stop()

    def audioStop(self):
        if self.audio_gen.stream is not None:
            self.startStopAudioButton.setText("Start audio")
            self.audio_gen.stop()

    def openFunscriptConversionDialog(self):
        self.audioStop()
        self.dialog.exec()

    def audioDeviceSelectionChanged(self, index):
        self.audio_gen.select_device_index(self.comboBoxAudioDevice.currentData().device_index)

    def closeEvent(self, event):
        print('closeEvent')
        self.audio_gen.stop()
        event.accept()


def run():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()