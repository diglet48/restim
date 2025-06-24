import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PySide6.QtCore import QPointF, QRectF, QTimer
from PySide6.QtGui import QColor, QTransform, QPen, Qt, QPainter, QFont, QMouseEvent

import numpy as np

COEF_1 = 1
COEF_2 = np.sqrt(8) / 3           # sqrt(1 - coef_1**2/3)
COEF_3 = np.sqrt(2) / np.sqrt(3)  # sqrt(1 - coef_1**2/3 - coef_2**2/2)

O = np.array([0, 0, 0])
v1 = np.array([COEF_1, 0, 0])
v2 = np.array([-COEF_1 / 3, COEF_2, 0])
v3 = np.array([-COEF_1 / 3, -COEF_2 / 2, COEF_3])
v4 = np.array([-COEF_1 / 3, -COEF_2 / 2, -COEF_3])

COLOR_LINE = QColor.fromRgb(50, 50, 50)
LINE_WIDTH = .08
COLOR_DOT = QColor.fromRgb(180, 140, 220)
DOT_WIDTH = .15

## SSBU colors.
COLOR_A = QColor.fromRgb(0xFE, 0x2E, 0x2E)   # red
COLOR_B = QColor.fromRgb(0x54, 0x63, 0xFF)   # blue
COLOR_C = QColor.fromRgb(0xFF, 0xC7, 0x17)   # yellow
COLOR_D = QColor.fromRgb(0x1F, 0x9E, 0x40)   # green

COLOR_A_ACCENT = COLOR_A.darker(115)
COLOR_B_ACCENT = COLOR_B.darker(115)
COLOR_C_ACCENT = COLOR_C.darker(115)
COLOR_D_ACCENT = COLOR_D.darker(115)

PROJECTION_ORIGIN = v1 + v3
PROJECTION_ORIGIN = PROJECTION_ORIGIN / np.linalg.norm(PROJECTION_ORIGIN)
PROJECTION_UP = -np.cross(v1 + v4, PROJECTION_ORIGIN)
PROJECTION_UP = PROJECTION_UP / np.linalg.norm(PROJECTION_UP)
PROJECTION_RIGHT = np.cross(PROJECTION_UP, PROJECTION_ORIGIN)
PROJECTION_RIGHT = PROJECTION_RIGHT / np.linalg.norm(PROJECTION_RIGHT)

MATRIX_ABC_TO_XYZ = np.vstack((PROJECTION_UP, PROJECTION_RIGHT, PROJECTION_ORIGIN))
MATRIX_XYZ_TO_ABC = np.linalg.inv(MATRIX_ABC_TO_XYZ)


class StereographicProjection:
    def __init__(self, normal_vector, x_vector, y_vector):
        self.normal_vector = normal_vector
        self.x_vector = x_vector
        self.y_vector = y_vector

    def abc_to_xyz(self, abc):
        x, y, z = (MATRIX_ABC_TO_XYZ @ abc)
        return x, y, z

    def abc_to_xy(self, abc):
        norm = np.linalg.norm(abc)
        if norm:
            abc = abc / norm
        return self.xyz_to_xy(self.abc_to_xyz(abc))

    def xy_to_abc(self, xy):
        return MATRIX_XYZ_TO_ABC @ self.xy_to_xyz(xy)

    def xyz_to_xy(self, xyz):
        x, y, z = xyz
        if z == 1:
            return np.inf, np.inf
        return x / (1 - z), y / (1 - z)

    def xy_to_xyz(self, xy):
        x, y = xy
        r_squared = x * x + y * y
        return (
            2 * x / (1 + r_squared),
            2 * y / (1 + r_squared),
            (-1 + r_squared) / (1 + r_squared)
        )

    def scale(self, xy):
        x, y = xy
        r_squared = x * x + y * y
        z = (-1 + r_squared) / (1 + r_squared)
        return 1 / max((1 - z), .01)


projection = StereographicProjection(PROJECTION_ORIGIN, PROJECTION_UP, PROJECTION_RIGHT)


class FourphaseWidgetStereographic(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setScene(QGraphicsScene())

        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setup_background()
        self.setup_cursor()

    def setup_background(self):
        def fill_outer(start_angle, color):
            ellipse = QGraphicsEllipseItem(-5, -5, 10, 10)
            ellipse.setStartAngle(start_angle * 16)
            ellipse.setSpanAngle(90 * 16)
            ellipse.setBrush(color)
            ellipse.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(ellipse)

        fill_outer(270, COLOR_A)
        fill_outer(180, COLOR_B)
        fill_outer(90, COLOR_C)
        fill_outer(0, COLOR_D)

        def fill_inner(start_angle, color):
            ellipse = QGraphicsEllipseItem(-1, -1, 2, 2)
            ellipse.setStartAngle(start_angle * 16)
            ellipse.setSpanAngle(90 * 16)
            ellipse.setBrush(color)
            ellipse.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(ellipse)

        fill_inner(90, COLOR_A)
        fill_inner(0, COLOR_B)
        fill_inner(270, COLOR_C)
        fill_inner(180, COLOR_D)

        def add_point(abc, color):
            x, y = projection.abc_to_xy(abc)
            r = .03
            dot = QGraphicsEllipseItem(x - r, y - r, r * 2, r * 2)
            dot.setBrush(color)
            dot.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(dot)

        add_point(v1, COLOR_A_ACCENT)
        add_point(-v2, COLOR_B_ACCENT)
        add_point(v3, COLOR_C_ACCENT)
        add_point(-v4, COLOR_D_ACCENT)

        def add_straight_line(dir: QPointF):
            half_width = LINE_WIDTH / 2
            lineDir = QPointF(dir.y(), dir.x()) * half_width
            poly_left = []
            poly_right = []
            for i in np.linspace(0, 5, 40):
                scale = projection.scale((i, 0))
                poly_left.append(dir * i + lineDir * scale)
                poly_right.append(dir * i - lineDir * scale)
            poly = poly_left + poly_right[::-1]
            self.scene().addPolygon(poly, Qt.PenStyle.NoPen, COLOR_LINE)

        add_straight_line(QPointF(1, 0))
        add_straight_line(QPointF(0, 1))
        add_straight_line(QPointF(-1, 0))
        add_straight_line(QPointF(0, -1))

        # add circle
        r = 1
        xy = (r, 0)
        pen = QPen()
        pen.setWidthF(LINE_WIDTH * projection.scale(xy))
        pen.setColor(COLOR_LINE)
        self.scene().addEllipse(
            QRectF(-r, -r, 2 * r, 2 * r),
            pen
        )

        def add_text(abc, text, color):
            x, y = projection.abc_to_xy(abc)
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

        add_text(-v1, "A", COLOR_A_ACCENT)
        add_text(v2, "B", COLOR_B_ACCENT)
        add_text(-v3, "C", COLOR_C_ACCENT)
        add_text(v4, "D", COLOR_D_ACCENT)

    def setup_cursor(self):
        pen = QPen()
        pen.setWidthF(LINE_WIDTH * .2)
        pen.setColor(QColor.fromRgb(255, 255, 255))
        self.cursor_1 = QGraphicsEllipseItem(0, 0, DOT_WIDTH, DOT_WIDTH)
        self.cursor_1.setPen(pen)
        self.cursor_1.setBrush(COLOR_DOT)
        self.cursor_2 = QGraphicsEllipseItem(0, 0, DOT_WIDTH, DOT_WIDTH)
        self.cursor_2.setPen(pen)
        self.cursor_2.setBrush(COLOR_DOT)
        self.scene().addItem(self.cursor_1)
        self.scene().addItem(self.cursor_2)

    def resizeEvent(self, event, /):
        w = 3.0
        self.fitInView(-w/2, -w/2, w, w, Qt.AspectRatioMode.KeepAspectRatio)
        pass

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_event_any(event)

    # def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
    #     self.mouse_event_any(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_event_any(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_event_any(event)

    def mouse_event_any(self, event: QMouseEvent):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        point = self.mapToScene(event.position().toPoint())
        xy = point.x(), point.y()
        a, b, c = projection.xy_to_abc(xy)
        self.mousePositionChanged.emit(a, b, c)

    def set_cursor_position_abc(self, a, b, c):
        abc = a, b, c
        xy = projection.abc_to_xy(abc)
        norm = np.clip(np.linalg.norm(abc), 0, 1)
        self.set_cursor_position_xy(xy)
        self.set_cursor_visibility(norm)

    def set_cursor_position_xy(self, xy):
        xyz = projection.xy_to_xyz(xy)
        size = projection.scale(xy) * 2
        self.cursor_1.setVisible(size < 10)
        self.cursor_1.setScale(size)
        self.cursor_1.setX(xy[0] - DOT_WIDTH/2 * size)
        self.cursor_1.setY(xy[1] - DOT_WIDTH/2 * size)
        xy = projection.xyz_to_xy(-np.array(xyz))
        size = projection.scale(xy) * 2
        self.cursor_2.setVisible(size < 10)
        self.cursor_2.setScale(size)
        self.cursor_2.setX(xy[0] - DOT_WIDTH/2 * size)
        self.cursor_2.setY(xy[1] - DOT_WIDTH/2 * size)
        self.update()

    def set_cursor_visibility(self, alpha=1.0):
        pen = self.cursor_1.pen()
        color = pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)

        brush = self.cursor_1.brush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)

        self.cursor_1.setPen(pen)
        self.cursor_1.setBrush(brush)
        self.cursor_2.setPen(pen)
        self.cursor_2.setBrush(brush)

    mousePositionChanged = QtCore.Signal(float, float, float)  # a, b, c
