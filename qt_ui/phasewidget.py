from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets, QtSvg


from qt_ui.stim_config import PositionParameters




class PhaseWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        scene = QtWidgets.QGraphicsScene()
        scene.addItem(QtSvg.QGraphicsSvgItem("resources/phase diagram bg.svg"))
        self.setScene(scene)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.circle = QtWidgets.QGraphicsEllipseItem(100, 100, 10, 10)
        self.circle.setBrush(QColor.fromRgb(255, 0, 0))
        pen = QPen()
        pen.setColor(QColor.fromRgb(255, 0, 0))
        self.circle.setPen(pen)
        scene.addItem(self.circle)

        #mouse tracking
        self.setMouseTracking(True)
        self.buttonPressed = False

    def updatePositionParameters(self, position_params: PositionParameters):
        self.circle.setPos(position_params.alpha * 75 - 5, -position_params.beta * 75 - 5)

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

    def updateMousePosition(self, pixel_x, pixel_y):
        x = (pixel_x - 100) / 75.0
        y = (pixel_y - 100) / -75.0
        norm = (x**2 + y**2)**.5
        if norm >= 1:
            x /= norm
            y /= norm
        self.mousePositionChanged.emit(x, y)

    mousePositionChanged = QtCore.pyqtSignal(float, float)
