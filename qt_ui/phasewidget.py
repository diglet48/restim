import matplotlib
import time

from PyQt5.QtCore import QSettings, QPoint
from PyQt5.QtWidgets import QGraphicsView

from qt_ui.preferencesdialog import KEY_DISPLAY_FPS, KEY_DISPLAY_LATENCY
from qt_ui import resources
from stim_math.threephase_parameter_manager import ThreephaseParameterManager

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QColor, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg, QtGui
from PyQt5.QtCore import Qt

from qt_ui.stim_config import PositionParameters


class Mode:
    MouseMode = 1
    TCodeMode = 2


def item_pos_to_ab(x, y):
    return y / -77, x / -77


def ab_to_item_pos(a, b):
    return b * -77, a * -77


class PhaseWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.config: ThreephaseParameterManager = None
        self.mode = Mode.TCodeMode
        self.stored_tcode_position = PositionParameters(0, 0)

        self.setAlignment(Qt.AlignCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scene = QtWidgets.QGraphicsScene()
        self.setScene(scene)
        svg = QtSvg.QGraphicsSvgItem(resources.phase_diagram_bg)
        scene.addItem(svg)
        svg.setPos(-svg.boundingRect().width()/2, -svg.boundingRect().height()/2)
        self.svg = svg

        self.circle = QtWidgets.QGraphicsEllipseItem(0, 0, 10, 10)
        self.circle.setBrush(QColor.fromRgb(62, 201, 65))
        self.circle.setPen(QColor.fromRgb(62, 201, 65))
        scene.addItem(self.circle)

        #mouse tracking
        self.setMouseTracking(True)
        self.buttonPressed = False

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(int(1000 / 60.0))
        self.refreshSettings()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.fitInView(-100, -100, 200, 200, Qt.KeepAspectRatio)

    def refreshSettings(self):
        settings = QSettings()
        self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 60.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def mousePressEvent(self, event: QMouseEvent):
        self.buttonPressed = True
        self.updateMousePosition(event.x(), event.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.buttonPressed = False

    def mouseMoveEvent(self, event: QMouseEvent):
        buttons: QtCore.Qt.MouseButtons = event.buttons()
        if not buttons == QtCore.Qt.MouseButton.LeftButton: # sanity check
            self.buttonPressed = False

        if self.buttonPressed:
            self.updateMousePosition(event.x(), event.y())

    def updateMousePosition(self, mouse_x, mouse_y):
        view_pos = QPoint(mouse_x, mouse_y)
        scene_pos = self.mapToScene(view_pos)
        item_pos = self.svg.mapToItem(self.svg, scene_pos)
        a, b = item_pos_to_ab(item_pos.x(), item_pos.y())

        norm = (a**2 + b**2)**.5
        if norm >= 1:
            a /= norm
            b /= norm
        self.mode = Mode.MouseMode
        self.stored_tcode_position.alpha = a
        self.stored_tcode_position.beta = b
        self.mousePositionChanged.emit(a, b)

    def refresh(self):
        # if position has changed since last mouse event, transition to TCodeMode
        if self.mode == Mode.MouseMode:
            if (self.stored_tcode_position.alpha != self.config.alpha.last_value() or
                    self.stored_tcode_position.beta != self.config.beta.last_value()):
                self.mode = Mode.TCodeMode

        if self.mode == Mode.TCodeMode:
            # delay visualization in tcode mode
            a = self.config.alpha.interpolate(time.time() - self.latency)
            b = self.config.beta.interpolate(time.time() - self.latency)
        else:
            # display immediately in mouse mode
            a = self.config.alpha.last_value()
            b = self.config.beta.last_value()

        x, y = ab_to_item_pos(a, b)
        self.circle.setPos(x - 5, y - 5)

    mousePositionChanged = QtCore.pyqtSignal(float, float)
