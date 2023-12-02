import matplotlib
import time
import math

from PyQt5.QtCore import QSettings, QPoint, QPointF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsEllipseItem

from qt_ui.preferencesdialog import KEY_DISPLAY_FPS, KEY_DISPLAY_LATENCY
from qt_ui import resources
from stim_math.threephase_parameter_manager import ThreephaseParameterManager
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform, \
    ThreePhaseCoordinateTransformMapToEdge

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QColor, QMouseEvent, QPainterPath
from PyQt5 import QtCore, QtWidgets, QtSvg, QtGui
from PyQt5.QtCore import Qt

from qt_ui.stim_config import PositionParameters


class Mode:
    MouseMode = 1
    TCodeMode = 2


def item_pos_to_ab(x, y):
    return y / -83, x / -83


def ab_to_item_pos(a, b):
    return b * -83, a * -83


class PhaseWidgetBase(QtWidgets.QGraphicsView):
    """
    A QGraphicsView that displays an SVG of the phase diagram in the background, with mouse support.
    """
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.setAlignment(Qt.AlignCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scene = QtWidgets.QGraphicsScene()
        self.setScene(scene)
        svg = QtSvg.QGraphicsSvgItem(resources.phase_diagram_bg)
        scene.addItem(svg)
        svg.setPos(-svg.boundingRect().width()/2, -svg.boundingRect().height()/2)
        self.svg = svg
        self.scene = scene

        #mouse tracking
        self.setMouseTracking(True)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(int(1000 / 60.0))
        self.refreshSettings()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.fitInView(-100, -100, 200, 200, Qt.KeepAspectRatio)

    def mousePressEvent(self, event: QMouseEvent):
        self.mouse_event_screen_pos(event.x(), event.y(), event.buttons())

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_event_screen_pos(event.x(), event.y(), event.buttons())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_event_screen_pos(event.x(), event.y(), event.buttons())

    def mouseMoveEvent(self, event: QMouseEvent):
        self.mouse_event_screen_pos(event.x(), event.y(), event.buttons())

    def mouse_event_screen_pos(self, mouse_x, mouse_y, buttons: QtCore.Qt.MouseButtons):
        view_pos = QPoint(mouse_x, mouse_y)
        scene_pos = self.mapToScene(view_pos)
        item_pos = self.svg.mapToItem(self.svg, scene_pos)
        a, b = item_pos_to_ab(item_pos.x(), item_pos.y())
        return self.mouse_event(a, b, buttons)

    def mouse_event(self, alpha, beta, buttons: QtCore.Qt.MouseButtons):
        # overload me
        # if buttons & QtCore.Qt.MouseButton.LeftButton:
        #     do stuff
        pass


class PhaseWidgetWithPoint(PhaseWidgetBase):
    def __init__(self, parent):
        super(PhaseWidgetWithPoint, self).__init__(parent)

        self.config: ThreephaseParameterManager = None
        self.mode = Mode.TCodeMode
        self.stored_tcode_position = PositionParameters(0, 0)

        self.dot = QtWidgets.QGraphicsEllipseItem(0, 0, 10, 10)
        self.dot.setBrush(QColor.fromRgb(62, 201, 65))
        self.dot.setPen(QColor.fromRgb(62, 201, 65))
        self.scene.addItem(self.dot)

    def refreshSettings(self):
        settings = QSettings()
        self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 60.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def mouse_event(self, alpha, beta, buttons: QtCore.Qt.MouseButtons):
        if buttons & QtCore.Qt.MouseButton.LeftButton:
            pass
        else:
            return

        norm = (alpha ** 2 + beta ** 2) ** .5
        if norm >= 1:
            alpha /= norm
            beta /= norm
        self.mode = Mode.MouseMode
        self.stored_tcode_position.alpha = alpha
        self.stored_tcode_position.beta = beta
        self.mousePositionChanged.emit(alpha, beta)

    mousePositionChanged = QtCore.pyqtSignal(float, float)


class PhaseWidgetAlphaBeta(PhaseWidgetWithPoint):
    def __init__(self, parent):
        super(PhaseWidgetAlphaBeta, self).__init__(parent)

        a, b = (1, 0)
        x, y = ab_to_item_pos(a, b)
        self.arrow = Path(source=QtCore.QPointF(x, y),
                          destination=QtCore.QPointF(0, 0))
        self.scene.addItem(self.arrow)

        self.border = QGraphicsEllipseItem(0, 0, 83, 83)
        self.border.setPen(QColor.fromRgb(0, 0, 0))
        self.scene.addItem(self.border)

        self.arc = ArcSegment(center=QPointF(*ab_to_item_pos(0, 0)), radius=80)
        self.scene.addItem(self.arc)

        self.setRenderHint(QtGui.QPainter.Antialiasing)

        self.dot.setZValue(10)

        self.last_state = None

    def mouse_event(self, alpha, beta, buttons: QtCore.Qt.MouseButtons):
        if buttons & QtCore.Qt.MouseButton.LeftButton:
            pass
        else:
            return

        norm = (alpha ** 2 + beta ** 2) ** .5
        if norm >= 1:
            alpha /= norm
            beta /= norm

        if self.config.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.config.transform_rotation_degrees.last_value(),
                self.config.transform_mirror.last_value(),
                self.config.transform_top_limit.last_value(),
                self.config.transform_bottom_limit.last_value(),
                self.config.transform_left_limit.last_value(),
                self.config.transform_right_limit.last_value(),
            )
            alpha, beta = transform.inverse_transform(alpha, beta)
        if self.config.map_to_edge_enabled.last_value():
            transform = ThreePhaseCoordinateTransformMapToEdge(
                self.config.map_to_edge_start.last_value(),
                self.config.map_to_edge_length.last_value(),
                self.config.map_to_edge_invert.last_value(),
            )
            alpha, beta = transform.inverse_transform(alpha, beta)
        norm = (alpha ** 2 + beta ** 2) ** .5
        if norm >= 1:
            alpha /= norm
            beta /= norm

        self.mode = Mode.MouseMode
        self.stored_tcode_position.alpha = alpha
        self.stored_tcode_position.beta = beta
        self.mousePositionChanged.emit(alpha, beta)

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

        if self.config.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.config.transform_rotation_degrees.last_value(),
                self.config.transform_mirror.last_value(),
                self.config.transform_top_limit.last_value(),
                self.config.transform_bottom_limit.last_value(),
                self.config.transform_left_limit.last_value(),
                self.config.transform_right_limit.last_value(),
            )
        elif self.config.map_to_edge_enabled.last_value():
            transform = ThreePhaseCoordinateTransformMapToEdge(
                self.config.map_to_edge_start.last_value(),
                self.config.map_to_edge_length.last_value(),
                self.config.map_to_edge_invert.last_value(),
            )
        else:
            transform = ThreePhaseCoordinateTransform(0, 0, 1, -1, -1, 1)

        state = (a, b, transform)
        if state == self.last_state:
            return  # skip drawing to save cpu cycles
        self.last_state = state

        a, b = transform.transform(a, b)
        norm = (a ** 2 + b ** 2) ** .5
        if norm >= 1:
            a /= norm
            b /= norm

        # draw dot
        x, y = ab_to_item_pos(a, b)
        self.dot.setPos(x - 5, y - 5)

        # draw arrow
        self.arrow.setEnabled(self.config.transform_enabled.last_value() and self.config.transform_rotation_degrees.last_value())
        tip_a, tip_b = transform.transform(1, 0)
        base_a, base_b = transform.transform(0, 0)
        base_a = base_a + (tip_a - base_a) * 0.7
        base_b = base_b + (tip_b - base_b) * 0.7
        self.arrow.setSource(QPointF(*ab_to_item_pos(tip_a, tip_b)))
        self.arrow.setDestination(QPointF(*ab_to_item_pos(base_a, base_b)))

        # draw circle
        self.border.setRect(
            self.config.transform_left_limit.last_value() * 83,
            -self.config.transform_bottom_limit.last_value() * 83,
            (self.config.transform_right_limit.last_value() - self.config.transform_left_limit.last_value()) * 83,
            (self.config.transform_bottom_limit.last_value() - self.config.transform_top_limit.last_value()) * 83,
        )
        self.border.setVisible(bool(self.config.transform_enabled.last_value()))

        self.arc.setStart(self.config.map_to_edge_start.last_value())
        self.arc.setLength(self.config.map_to_edge_length.last_value())
        self.arc.setVisible(bool(self.config.map_to_edge_enabled.last_value()))


class PhaseWidgetFocus(PhaseWidgetWithPoint):
    def __init__(self, parent):
        super(PhaseWidgetFocus, self).__init__(parent)

        self.dot.setBrush(QColor.fromRgb(201, 62, 65))
        self.dot.setPen(QColor.fromRgb(201, 62, 65))

        self.last_state = None

    def refresh(self):
        a = self.config.focus_alpha.last_value()
        b = self.config.focus_beta.last_value()

        state = (a, b)
        if state == self.last_state:
            return  # skip drawing to save cpu cycles
        self.last_state = state

        x, y = ab_to_item_pos(a, b)
        self.dot.setPos(x - 5, y - 5)


class Path(QtWidgets.QGraphicsPathItem):
    """
    https://stackoverflow.com/questions/44246283/how-to-add-a-arrow-head-to-my-line-in-pyqt4
    """
    def __init__(self, source: QtCore.QPointF = None, destination: QtCore.QPointF = None, *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)

        self._sourcePoint = source
        self._destinationPoint = destination

        self._arrow_height = 5
        self._arrow_width = 4

        self._enabled = True

    def setSource(self, point: QtCore.QPointF):
        self._sourcePoint = point
        self.update()

    def setDestination(self, point: QtCore.QPointF):
        self._destinationPoint = point
        self.update()

    def directPath(self):
        path = QtGui.QPainterPath(self._sourcePoint)
        path.lineTo(self._destinationPoint)
        return path

    def setEnabled(self, enabled):
        self._enabled = enabled

    def arrowCalc(self, start_point=None, end_point=None):  # calculates the point where the arrow should be drawn
        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self._sourcePoint

            if endPoint is None:
                endPoint = self._destinationPoint

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx ** 2 + dy ** 2)
            normX, normY = dx / leng, dy / leng  # normalize

            # perpendicular vector
            perpX = -normY
            perpY = normX

            leftX = endPoint.x() + self._arrow_height * normX + self._arrow_width * perpX
            leftY = endPoint.y() + self._arrow_height * normY + self._arrow_width * perpY

            rightX = endPoint.x() + self._arrow_height * normX - self._arrow_width * perpX
            rightY = endPoint.y() + self._arrow_height * normY - self._arrow_width * perpY

            point2 = QtCore.QPointF(leftX, leftY)
            point3 = QtCore.QPointF(rightX, rightY)

            return QtGui.QPolygonF([point2, endPoint, point3])

        except (ZeroDivisionError, Exception):
            return None

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        if not self._enabled:
            return

        painter.setRenderHint(painter.Antialiasing)

        painter.pen().setWidth(2)
        painter.setBrush(QtCore.Qt.NoBrush)

        path = self.directPath()
        painter.drawPath(path)
        self.setPath(path)

        triangle_source = self.arrowCalc(path.pointAtPercent(0.1), self._sourcePoint)  # change path.PointAtPercent() value to move arrow on the line

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)


class ArcSegment(QtWidgets.QGraphicsPathItem):
    def __init__(self, center: QtCore.QPointF, radius: int, *args, **kwargs):
        super(ArcSegment, self).__init__(*args, **kwargs)

        self._center = center
        self._radius = radius
        self._start = 0
        self._length = 0

        self._arrow_height = 5
        self._arrow_width = 4

        self._enabled = True

    def setStart(self, start: float):
        self._start = start
        self.update()

    def setLength(self, length: float):
        self._length = length
        self.update()

    def setEnabled(self, enabled):
        self._enabled = enabled

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        if not self._enabled:
            return

        painter.drawArc(
            int(self._center.x()) - self._radius,
            int(self._center.y()) - self._radius,
            2 * self._radius,
            2 * self._radius,
            int(16 * (-self._start + 90)), int(16 * -self._length))


class PhaseWidgetCalibration(PhaseWidgetBase):
    def __init__(self, parent):
        super(PhaseWidgetCalibration, self).__init__(parent)

        self.config: ThreephaseParameterManager = None
        self.path = Path(source=QtCore.QPointF(1, 0),
                         destination=QtCore.QPointF(0, 0))

        self.scene.addItem(self.path)

        self.last_state = None

    def refreshSettings(self):
        settings = QSettings()
        self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 60.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def mouse_event(self, alpha, beta, buttons: QtCore.Qt.MouseButtons):
        if buttons & QtCore.Qt.MouseButton.LeftButton:
            pass
        else:
            return

        norm = (alpha ** 2 + beta ** 2) ** .5
        if norm > 0:
            alpha /= norm
            beta /= norm

        old_neutral = self.config.calibration_neutral.last_value()
        old_right = self.config.calibration_right.last_value()

        neutral_adj = alpha * 0.1
        right_adj = -beta * 0.1

        neutral = old_neutral + neutral_adj
        right = old_right + right_adj

        self.calibrationParametersChanged.emit(neutral, right)

    def refresh(self):
        a = self.config.calibration_neutral.last_value()
        b = -self.config.calibration_right.last_value()

        state = (a, b)
        if state == self.last_state:
            return  # skip drawing to save cpu cycles
        self.last_state = state

        norm = (a ** 2 + b ** 2) ** .5
        if norm > 0:
            a /= norm
            b /= norm

        arrow_length = min((norm / 5) ** 1, 1)
        a *= arrow_length
        b *= arrow_length

        x, y = ab_to_item_pos(a, b)
        self.path.setSource(QtCore.QPointF(x, y))

    calibrationParametersChanged = QtCore.pyqtSignal(float, float)
