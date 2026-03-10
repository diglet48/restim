from PySide6 import QtWidgets
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtCore import Qt, QPoint, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QPolygon

import numpy as np


class VolumeWidget(QtWidgets.QProgressBar):
    def __init__(self, parent):
        QtWidgets.QProgressBar.__init__(self, parent)

        # use fusion style on Windows 11 because the
        # default progress bar styling is awful.
        if self.style().name() == 'windows11':
            self.setStyle(QStyleFactory.create("Fusion"))

        self.setMouseTracking(True)
        
        self.master_volume = 0  # Red line for master volume setting
        self._dragging_master_volume = False

    masterVolumeChanged = Signal(float)

    def _set_master_from_pos(self, pos: QPointF):
        offset = 1  # magic number for perfect visual alignment (on windows?)
        new_value = ((pos.x() + offset) / self.width()) * 100.0
        new_value = np.clip(np.round(new_value * 2) / 2, 0, 100)  # round to nearest 0.5
        if new_value != self.master_volume:
            self.master_volume = new_value
            self.update()
            self.masterVolumeChanged.emit(new_value)

    def _is_near_master_line(self, pos: QPointF) -> bool:
        width = max(1, self.width())
        master_pos = int((self.master_volume / 100.0) * width)
        return abs(pos.x() - master_pos) <= 8

    def set_value_and_tooltip(self, value: int, tooltip: str):
        self.setValue(value)
        self.setToolTip(tooltip)

    def set_master_volume_indicator(self, master_volume: float):
        """Set the red line position for master volume setting"""
        master_volume = np.clip(master_volume, 0, 100)
        if np.abs(self.master_volume - master_volume) >= .1:
            self.master_volume = master_volume
            self.update()  # Trigger repaint

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._is_near_master_line(event.position()):
            self._dragging_master_volume = True
            self._set_master_from_pos(event.position())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # change cursor shape on mouseover
        if self._is_near_master_line((event.position())):
            if self.cursor().shape() != Qt.CursorShape.SplitHCursor:
                self.setCursor(Qt.CursorShape.SplitHCursor)
        else:
            if self.cursor().shape() == Qt.CursorShape.SplitHCursor:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        if self._dragging_master_volume:
            self._set_master_from_pos(event.position())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_master_volume and event.button() == Qt.MouseButton.LeftButton:
            self._dragging_master_volume = False
            self._set_master_from_pos(event.position())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        # First paint the normal progress bar
        super().paintEvent(event)
        
        # Then paint the red line with notch for master volume
        if self.master_volume > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Calculate position for the red line
            width = self.width()
            height = self.height()
            master_pos = int(round((self.master_volume / 100.0) * width))
            
            # Draw red vertical line
            painter.setPen(QColor(255, 0, 0, 200))  # Red line with transparency
            painter.drawLine(master_pos, 0, master_pos, height)
            
            # Draw notch at the top
            notch_size = 6
            painter.setBrush(QColor(255, 0, 0, 220))
            painter.setPen(QColor(180, 0, 0, 255))  # Darker red outline
            
            # Create triangular notch pointing down
            notch_points = [
                QPoint(master_pos - notch_size, 0),
                QPoint(master_pos + notch_size, 0),
                QPoint(master_pos, notch_size)
            ]
            notch = QPolygon(notch_points)
            painter.drawPolygon(notch)
            
            painter.end()
