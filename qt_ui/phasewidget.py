import sys
import os
import matplotlib
import numpy as np
import time

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QGraphicsView

from qt_ui.preferencesdialog import KEY_DISPLAY_FPS, KEY_DISPLAY_LATENCY
from stim_math.threephase_parameter_manager import ThreephaseParameterManager

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg, QtGui

from qt_ui.stim_config import PositionParameters


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
    return os.path.join(base_path, relative_path)


class Mode:
    MouseMode = 1
    TCodeMode = 2


class PhaseWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.config: ThreephaseParameterManager = None
        self.mode = Mode.TCodeMode
        self.stored_tcode_position = PositionParameters(0, 0)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSceneRect(-100, -100, 200, 200)
        self.centerOn(0, 0)

        scene = QtWidgets.QGraphicsScene()
        self.setScene(scene)
        svg = QtSvg.QGraphicsSvgItem(resource_path("resources/phase diagram bg.svg"))
        svg.setPos(-svg.boundingRect().width()/2, -svg.boundingRect().height()/2)
        svg.moveBy(0, 6)
        scene.addItem(svg)

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

    def refreshSettings(self):
        settings = QSettings()
        self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 60.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def xy_to_ab(self, x, y):
        a = (y - 6) / -77
        b = (x - 0) / -77
        return a, b

    def ab_to_xy(self, a, b):
        x = (b * -77)
        y = (a * -77) + 6
        return x, y

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
        a, b = self.xy_to_ab(mouse_x - 100, mouse_y - 100)
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

        x, y = self.ab_to_xy(a, b)
        self.circle.setPos(x - 5, y - 5)

    mousePositionChanged = QtCore.pyqtSignal(float, float)
