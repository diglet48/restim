import sys
import os
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg

from qt_ui.stim_config import PositionParameters


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
    return os.path.join(base_path, relative_path)


class PhaseWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

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

        self.updatePositionParameters(PositionParameters(0, 0))

    def xy_to_ab(self, x, y):
        a = (y - 6) / -77
        b = (x - 0) / -77
        return a, b

    def ab_to_xy(self, a, b):
        x = (b * -77)
        y = (a * -77) + 6
        return x, y

    def updateAlphaPosition(self, value):
        self.position_params.alpha = value
        self.updatePositionParameters(self.position_params)

    def updateBetaPosition(self, value):
        self.position_params.beta = value
        self.updatePositionParameters(self.position_params)

    def updatePositionParameters(self, position_params: PositionParameters):
        self.position_params = position_params
        x, y = self.ab_to_xy(position_params.alpha, position_params.beta)
        self.circle.setPos(x - 5, y - 5)
        self.update()

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
        self.mousePositionChanged.emit(a, b)

    mousePositionChanged = QtCore.pyqtSignal(float, float)
