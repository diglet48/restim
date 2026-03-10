import sys
from PySide6.QtWidgets import QApplication, QWidget, QProgressBar, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen


class BatteryProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(30)
        self.setFixedWidth(60)

    def battery_style(self, value):
        if value > 60:
            color = "#4CAF50"  # Green
        elif value > 30:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red

        return f"""
        QProgressBar {{
            border: 3px solid #333;
            border-radius: 8px;
            background-color: #ddd;
            text-align: center;
            font-weight: bold;
            margin-right: 4px;
        }}

        QProgressBar::chunk {{
            background-color: {color};
            border-radius: 5px;
        }}
        """

    def setValue(self, value):
        super().setValue(value)
        self.setStyleSheet(self.battery_style(value))

    def paintEvent(self, event):
        super().paintEvent(event)

        # Draw battery cap
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cap_width = 4
        cap_height = self.height() // 2
        cap_x = self.width() - 5
        # cap_x = self.width() - 15
        cap_y = (self.height() - cap_height) // 2

        painter.setBrush(QColor("#333"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(cap_x, cap_y, cap_width, cap_height)

        painter.end()