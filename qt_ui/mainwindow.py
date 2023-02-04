import sys

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QGraphicsScene, QGraphicsEllipseItem
)
from PyQt5 import QtCore
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.uic import loadUi

from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.websocket_client
import qt_ui.motion_generation



class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # self.connectSignalsSlots()

        self.motion_generator = qt_ui.motion_generation.MotionGenerator(self)
        self.ws_client = qt_ui.websocket_client.WebsocketClient(self)

        self.tab_2.calibrationSettingsChanged.connect(self.ws_client.updateCalibrationParameters)
        self.tab_3.modulationSettingsChanged.connect(self.ws_client.updateModulationParameters)
        self.motion_generator.positionChanged.connect(self.ws_client.updatePositionParameters)

        self.motion_generator.positionChanged.connect(self.graphicsView.updatePositionParameters)
        self.graphicsView.mousePositionChanged.connect(self.motion_generator.updateMousePosition)

        self.comboBox.currentTextChanged.connect(self.motion_generator.patternChanged)
        self.motion_generator.patternChanged(self.comboBox.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_generator.velocityChanged)
        self.motion_generator.velocityChanged(self.doubleSpinBox.value())

        # trigger updates
        self.tab_2.settings_changed()
        self.tab_3.settings_changed()



def connectSignalsSlots(self):
    self.action_Exit.triggered.connect(self.close)
    self.action_Find_Replace.triggered.connect(self.findAndReplace)
    self.action_About.triggered.connect(self.about)


def findAndReplace(self):
    dialog = FindReplaceDialog(self)
    dialog.exec()


def about(self):
    QMessageBox.about(
        self,
        "About Sample Editor",
        "<p>A sample text editor app built with:</p>"
        "<p>- PyQt</p>"
        "<p>- Qt Designer</p>"
        "<p>- Python</p>",
    )


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/find_replace.ui", self)


def run():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()