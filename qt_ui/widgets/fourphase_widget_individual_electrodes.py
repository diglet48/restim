import sys
import time

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsRectItem
from PySide6.QtCore import QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QTransform, QPen, Qt, QPainter, QFont, QMouseEvent

import numpy as np

from stim_math.transforms_4 import constrain_4p_amplitudes

COLOR_LINE = QColor.fromRgb(50, 50, 50)
LINE_WIDTH = .08
COLOR_DOT = QColor.fromRgb(180, 140, 220)
DOT_WIDTH = .15

## SSBU colors.
COLOR_A = QColor.fromRgb(0xFE, 0x2E, 0x2E)   # red
COLOR_B = QColor.fromRgb(0x54, 0x63, 0xFF)   # blue
COLOR_C = QColor.fromRgb(0xFF, 0xC7, 0x17)   # yellow
COLOR_D = QColor.fromRgb(0x1F, 0x9E, 0x40)   # green

COLOR_A_BG = COLOR_A.lighter(140)
COLOR_B_BG = COLOR_B.lighter(130)
COLOR_C_BG = COLOR_C.lighter(150)
COLOR_D_BG = COLOR_D.lighter(190)

COLOR_A_ACCENT = COLOR_A.darker(115)
COLOR_B_ACCENT = COLOR_B.darker(115)
COLOR_C_ACCENT = COLOR_C.darker(115)
COLOR_D_ACCENT = COLOR_D.darker(115)



class FourphaseWidgetIndividualElectrodes(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.sensor_widget = None

        self.setScene(QGraphicsScene())

        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMouseTracking(True)

        # prevent auto-scrolling the view by Qt
        self.setSceneRect(0, 0, 4, 4)

        self.setup_intensities()

        self._last_a = 1.0
        self._last_b = 1.0
        self._last_c = 1.0
        self._last_d = 1.0
        self.set_electrode_intensities(1, 1, 1, 1)

    def set_sensor_widget(self, sensor_widget):
        self.sensor_widget = sensor_widget

    def set_electrode_intensities(self, a, b, c, d):
        if self.sensor_widget:
            params = {'e1': a, 'e2': b, 'e3': c, 'e4': d}
            self.sensor_widget.process(params)
            a = params['e1']
            b = params['e2']
            c = params['e3']
            d = params['e4']

        a, b, c, d = constrain_4p_amplitudes(a, b, c, d)
        self._last_a = a
        self._last_b = b
        self._last_c = c
        self._last_d = d
        self.level_1_rect.setRect(0, 1 - a, 1, a)
        self.level_2_rect.setRect(1, 1 - b, 1, b)
        self.level_3_rect.setRect(2, 1 - c, 1, c)
        self.level_4_rect.setRect(3, 1 - d, 1, d)

    def setup_intensities(self):
        def add_square(x0, color):
            rect = QGraphicsRectItem(x0, 0, 1, 1)
            rect.setBrush(color)
            rect.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(rect)

        add_square(0, COLOR_A_BG)
        add_square(1, COLOR_B_BG)
        add_square(2, COLOR_C_BG)
        add_square(3, COLOR_D_BG)

        def add_water_level(x0, color):
            rect = QGraphicsRectItem(x0, 0, 1, 1)
            rect.setBrush(color)
            rect.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(rect)
            return rect

        self.level_1_rect = add_water_level(0, COLOR_A)
        self.level_2_rect = add_water_level(1, COLOR_B)
        self.level_3_rect = add_water_level(2, COLOR_C)
        self.level_4_rect = add_water_level(3, COLOR_D)

        def add_text(x0, text, color):
            x = x0 + 0.5
            y = 0.5

            font = QFont()
            font.setPointSizeF(3)
            item = self.scene().addText(text, font)
            item.setDefaultTextColor(color)
            item.setX(x)
            item.setY(y)

            # funny transformation because font sizes below 1 don't work
            t = QTransform()
            rect = item.boundingRect()
            t.scale(0.1, 0.1)
            t.translate(rect.width() * -0.5, rect.height() * -0.5)
            item.setTransform(t)

        add_text(0, "A", COLOR_A_ACCENT)
        add_text(1, "B", COLOR_B_ACCENT)
        add_text(2, "C", COLOR_C_ACCENT)
        add_text(3, "D", COLOR_D_ACCENT)

    def resizeEvent(self, event, /):
        width_in_pixels = self.viewport().width()
        width_of_scene = 4
        scale = width_in_pixels / width_of_scene
        self.resetTransform()
        self.scale(scale, scale)

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_event_any(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_event_any(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Show vertical drag cursor when over a bar
        point = self.mapToScene(event.position().toPoint())
        over_bar = 0 <= point.x() <= 4 and 0 <= point.y() <= 1
        if over_bar:
            if self.cursor().shape() != Qt.CursorShape.SplitVCursor:
                self.setCursor(Qt.CursorShape.SplitVCursor)
        else:
            if self.cursor().shape() != Qt.CursorShape.ArrowCursor:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        self.mouse_event_any(event)

    def mouse_event_any(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        point = self.mapToScene(event.position().toPoint())
        x, y = point.x(), point.y()

        # Scene is 4 wide (columns 0-3), 1 tall.
        # X selects which electrode, Y sets its intensity.
        col = int(np.clip(x, 0, 3.999))  # 0=A, 1=B, 2=C, 3=D
        intensity = float(np.clip(1.0 - y, 0, 1))  # y=0 is top (1.0), y=1 is bottom (0.0)

        values = [self._last_a, self._last_b, self._last_c, self._last_d]
        values[col] = intensity

        self.mousePositionChanged.emit(*values)

    mousePositionChanged = QtCore.Signal(float, float, float, float)  # a, b, c, d
