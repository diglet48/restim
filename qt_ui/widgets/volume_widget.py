from PySide6 import QtWidgets
from PySide6.QtWidgets import QStyleFactory
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPolygon


class VolumeWidget(QtWidgets.QProgressBar):
    def __init__(self, parent):
        QtWidgets.QProgressBar.__init__(self, parent)

        # use fusion style on Windows 11 because the
        # default progress bar styling is awful.
        if self.style().name() == 'windows11':
            self.setStyle(QStyleFactory.create("Fusion"))
        
        self.master_volume = 0  # Red line for master volume setting

    def set_value_and_tooltip(self, value: int, tooltip: str):
        self.setValue(value)
        self.setToolTip(tooltip)

    def set_master_volume_indicator(self, master_volume: int):
        """Set the red line position for master volume setting"""
        self.master_volume = master_volume
        self.update()  # Trigger repaint

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
            master_pos = int((self.master_volume / 100.0) * width)
            
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
