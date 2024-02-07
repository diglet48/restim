from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QIconEngine, QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QWidget


class IconWithConnectionStatus(QIconEngine):
    NOT_CONNECTED = 0
    CONNECTED = 1
    PLAYING = 2

    def __init__(self, base_icon: QIcon, parent_widget: QWidget):
        super(IconWithConnectionStatus, self).__init__()
        self.base = base_icon
        self.parent_widget = parent_widget

        self.icon_1 = QIcon(":/restim/stop-circle_poly.svg")
        self.icon_2 = QIcon(":/restim/pause-circle_poly.svg")
        self.icon_3 = QIcon(":/restim/play-circle_poly.svg")
        self.state = self.NOT_CONNECTED

    def set_not_connected(self):
        self.state = self.NOT_CONNECTED
        self.parent_widget.update()

    def set_connected(self):
        self.state = self.CONNECTED
        self.parent_widget.update()

    def set_playing(self):
        self.state = self.PLAYING
        self.parent_widget.update()

    def pixmap(self, size: QtCore.QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pix = QPixmap(size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        return pix

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        self.base.paint(painter, rect, Qt.AlignCenter, mode, state)
        s = 24
        overlay = [self.icon_1, self.icon_2, self.icon_3][self.state]
        overlay.paint(painter, QRect(rect.width() - s, rect.height() - s, s, s), Qt.AlignCenter, mode, state)
