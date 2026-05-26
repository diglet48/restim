from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtWidgets import QDoubleSpinBox

import numpy as np


class SpinBoxWithProgressIndicator(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.indicator_brush = Qt.BrushStyle.NoBrush
        self.indicator_brush = QBrush(QColor.fromRgb(100, 100, 100, 200))
        self.indicator_height = 4
        self.indicator_range = (0, 100)

    def setIndicatorRange(self, lo, hi):
        self.indicator_range = (lo, hi)
        self.update()

    def setIndicatorColor(self, color):
        self.indicator_brush.setColor(color)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        width = int(np.interp(
            self.value(),
            self.indicator_range,
            (0, self.width())
        ))
        height = self.height()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.indicator_brush)
        painter.drawRect(0, height - self.indicator_height + 1, width, height)

        painter.end()


