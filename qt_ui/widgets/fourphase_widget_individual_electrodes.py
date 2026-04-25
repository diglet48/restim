import numpy as np
from PySide6.QtCore import QPointF, Signal, QObject
from PySide6.QtGui import QColor, QTransform, Qt, QPainter, QFont, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsRectItem, \
    QGraphicsPolygonItem, QGraphicsSceneMouseEvent

from stim_math.transforms_4 import constrain_4p_amplitudes

## SSBU colors.
COLOR_A = QColor.fromRgb(0xFE, 0x2E, 0x2E)   # red
COLOR_B = QColor.fromRgb(0x54, 0x63, 0xFF)   # blue
COLOR_C = QColor.fromRgb(0xFF, 0xC7, 0x17)   # yellow
COLOR_D = QColor.fromRgb(0x1F, 0x9E, 0x40)   # green

COLOR_DOT = QColor.fromRgb(0, 0, 0)
DOT_RADIUS = .1

COLOR_A_BG = COLOR_A.lighter(140)
COLOR_B_BG = COLOR_B.lighter(130)
COLOR_C_BG = COLOR_C.lighter(150)
COLOR_D_BG = COLOR_D.lighter(190)

COLOR_A_ACCENT = COLOR_A.darker(115)
COLOR_B_ACCENT = COLOR_B.darker(115)
COLOR_C_ACCENT = COLOR_C.darker(115)
COLOR_D_ACCENT = COLOR_D.darker(115)

COLORS = [COLOR_A, COLOR_B, COLOR_C, COLOR_D]

TRIANGLE_SCALE = 1.3

TRIANGLE_UP = TRIANGLE_SCALE * np.array([0, -1])                    # up
TRIANGLE_LEFT = TRIANGLE_SCALE * np.array([np.sqrt(3) / 2, 0.5])    # left
TRIANGLE_RIGHT = TRIANGLE_SCALE * np.array([-np.sqrt(3) / 2, 0.5])  # right

GRID_ORIGIN = np.array([0.5, 1.5])
GRID_RIGHT = np.array([1, 0])
GRID_SKEWED_UP = np.array([0.5, -np.sqrt(3)/2])
GRID_BASIS = np.array([GRID_RIGHT, GRID_SKEWED_UP]).T * TRIANGLE_SCALE

def triangle_center(index):
    u, v, is_pointing_up = index
    if is_pointing_up:
        return GRID_ORIGIN + GRID_BASIS @ (u + 1/3, v + 1/3)
    else:
        return GRID_ORIGIN + GRID_BASIS @ (u + 2/3, v + 2/3)

def triangle_basis(index):
    u, v, is_pointing_up = index
    if v % 2:   # odd row
        basis = np.array([
            TRIANGLE_LEFT,
            TRIANGLE_UP,
            TRIANGLE_RIGHT,
        ]) / np.sqrt(3)
        if is_pointing_up:
            return basis
        return np.multiply(basis, (1, -1))
    else:
        basis = np.array([
            TRIANGLE_RIGHT,
            TRIANGLE_UP,
            TRIANGLE_LEFT
        ]) / np.sqrt(3)
        if is_pointing_up:
            return basis
        return np.multiply(basis, (1, -1))

def triangle_color_index(index):
    u, v, is_pointing_up = index
    if v % 2:  # odd:
        return (u * 2 + 2 + is_pointing_up) % 4
    return (u * 2 + 1 - is_pointing_up) % 4

def triangle_color(index):
    u, v, is_pointing_up = index
    if v % 2:   # odd:
        return COLORS[(u * 2 + 2 + is_pointing_up) % 4]
    return COLORS[(u * 2 + 1 - is_pointing_up) % 4]

def screen_pos_to_index(xy):
    basis_inv = np.linalg.inv(GRID_BASIS)
    u, v = basis_inv @ (xy - GRID_ORIGIN)
    is_pointing_up = (u % 1) + (v % 1) <= 1
    index = (int(np.floor(u)), int(np.floor(v)), is_pointing_up)
    return index

def intensity_to_barycentric(intensity_triplet):
    bary = 1 - np.array(intensity_triplet)
    return bary / np.clip(np.sum(bary), .01, None)

def barycentric_to_intensity(barycentric):
    # expand
    intens = barycentric / np.max(barycentric)
    # invert
    intens = 1 - intens
    # repair (if needed)
    if np.sum(intens) < 1:
        intens += (1 - np.sum(intens)) / 3
    return intens

def barycentric_coords(P, A, B, C):
    x, y = P
    x1, y1 = A
    x2, y2 = B
    x3, y3 = C

    denom = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)

    if denom == 0:
        raise ValueError("Triangle is degenerate (area = 0)")

    alpha = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denom
    beta  = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denom
    gamma = 1 - alpha - beta

    return np.array((alpha, beta, gamma))


class Triangle:
    def __init__(self, scene, index):
        self.center = triangle_center(index)
        self.basis = triangle_basis(index)
        self.color_index = triangle_color_index(index)
        print(index, self.color_index)
        color = COLORS[self.color_index]

        poly = QPolygonF()
        poly.append(QPointF(*(self.center + self.basis[0])))
        poly.append(QPointF(*(self.center + self.basis[1])))
        poly.append(QPointF(*(self.center + self.basis[2])))
        self.geometry = QGraphicsPolygonItem(poly)
        self.geometry.setBrush(color)
        self.geometry.setPen(Qt.PenStyle.NoPen)
        scene.addItem(self.geometry)

    def intensity_to_scene(self, intensity_triplet):
        barycentric = intensity_to_barycentric(intensity_triplet)
        return self.center + self.basis.T @ barycentric

    def distance_from_center(self, intensity_triplet):
        # TODO: not 100% correct
        return 1 - (np.sum(intensity_triplet) - 1) / 2


class SquaresMouseGrabber(QGraphicsRectItem, QObject):
    def __init__(self, x, y, w, h):
        QGraphicsRectItem.__init__(self, x, y, w, h)
        QObject.__init__(self)
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setPen(Qt.PenStyle.NoPen)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.SplitVCursor)

        self.color_index = 0

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent, /):
        self.color_index = event.scenePos().x() // 1
        self.mouse_click.emit()
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent, /):
        vol = np.clip(4 - event.scenePos().y(), 0, 1)
        if self.color_index == 0:
            self.mouse_update_e1.emit(vol)
        elif self.color_index == 1:
            self.mouse_update_e2.emit(vol)
        elif self.color_index == 2:
            self.mouse_update_e3.emit(vol)
        elif self.color_index == 3:
            self.mouse_update_e4.emit(vol)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent, /):
        pass

    mouse_click = Signal()
    mouse_update_e1 = Signal(float)
    mouse_update_e2 = Signal(float)
    mouse_update_e3 = Signal(float)
    mouse_update_e4 = Signal(float)


class TrianglesMouseGrabber(QGraphicsRectItem, QObject):
    def __init__(self, x, y, w, h):
        QGraphicsRectItem.__init__(self, x, y, w, h)
        QObject.__init__(self)
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setPen(Qt.PenStyle.NoPen)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent, /):
        xy = np.array([event.scenePos().x(), event.scenePos().y()])
        self.update_pos(xy)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent, /):
        xy = np.array([event.scenePos().x(), event.scenePos().y()])
        self.update_pos(xy)

    # def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent, /):
    #     pass

    def update_pos(self, xy):
        # find the index of the triangle under the cursor
        index = screen_pos_to_index(xy)

        # compute the barycentric coordinates inside the triangle
        center = triangle_center(index)
        basis = triangle_basis(index)
        color_index = triangle_color_index(index)
        barycentric = barycentric_coords(xy - center, basis[0], basis[1], basis[2])
        barycentric = np.array(barycentric)
        # print('bary', barycentric)

        # convert to intensity
        intens = barycentric_to_intensity(barycentric)
        # print('intens', intens)

        if color_index == 0:
            self.update_all.emit(1.0, intens[0], intens[1], intens[2])
        elif color_index == 1:
            self.update_all.emit(intens[2], 1.0, intens[0], intens[1])
        elif color_index == 2:
            self.update_all.emit(intens[1], intens[2], 1.0, intens[0])
        elif color_index == 3:
            self.update_all.emit(intens[0], intens[1], intens[2], 1.0)

    update_all = Signal(float, float, float, float)


class FourphaseWidgetIndividualElectrodes(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.sensor_widget = None
        self.triangles = []
        self.last_intensity = (1, 1, 1, 1)

        self.setScene(QGraphicsScene())

        self.setRenderHint(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # prevent auto-scrolling the view by Qt
        self.setSceneRect(0, 0, 4, 4)

        self.init_squares()
        self.init_triangles()

        self.set_electrode_intensities(1, 1, 1, 1)

        self.setMouseTracking(True)

    def set_sensor_widget(self, sensor_widget):
        self.sensor_widget = sensor_widget

    def set_electrode_intensities(self, a, b, c, d):
        self.last_intensity = (a, b, c, d)
        if self.sensor_widget:
            params = {'e1': a, 'e2': b, 'e3': c, 'e4': d}
            self.sensor_widget.process(params)
            a = params['e1']
            b = params['e2']
            c = params['e3']
            d = params['e4']

        a, b, c, d = constrain_4p_amplitudes(a, b, c, d)

        # update water level
        self.level_1_rect.setRect(0, 4 - a, 1, a)
        self.level_2_rect.setRect(1, 4 - b, 1, b)
        self.level_3_rect.setRect(2, 4 - c, 1, c)
        self.level_4_rect.setRect(3, 4 - d, 1, d)

        # update triangles
        triplet = (0, 0, 0)
        if a == 1:
            color_index = 0
            triplet = (b, c, d)
        elif b == 1:
            color_index = 1
            triplet = (c, d, a)
        elif c == 1:
            color_index = 2
            triplet = (d, a, b)
        elif d == 1:
            color_index = 3
            triplet = (a, b, c)

        # update dots
        selected_triangles = [tri for tri in self.triangles if tri.color_index == color_index]
        for tri, dot in zip(selected_triangles, self.dots):
            pos = tri.intensity_to_scene(triplet)
            dot.setPos(QPointF(*pos))
            dot.setOpacity(tri.distance_from_center(triplet))


    def init_squares(self):
        def add_square(x0, color):
            rect = QGraphicsRectItem(x0, 3, 1, 1)
            rect.setBrush(color)
            rect.setPen(Qt.PenStyle.NoPen)
            self.scene().addItem(rect)

        add_square(0, COLOR_A_BG)
        add_square(1, COLOR_B_BG)
        add_square(2, COLOR_C_BG)
        add_square(3, COLOR_D_BG)

        def add_water_level(x0, color):
            rect = QGraphicsRectItem(x0, 3, 1, 1)
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
            y = 0.5 + 3.0

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

        self.grabber = SquaresMouseGrabber(0, 3, 4, 1)
        self.scene().addItem(self.grabber)
        self.grabber.mouse_click.connect(self.refresh_boxes)
        self.grabber.mouse_update_e1.connect(self.mouse_update_e1)
        self.grabber.mouse_update_e2.connect(self.mouse_update_e2)
        self.grabber.mouse_update_e3.connect(self.mouse_update_e3)
        self.grabber.mouse_update_e4.connect(self.mouse_update_e4)

    def init_triangles(self):
        self.triangles = [
            # half visible top row
            Triangle(self.scene(), (-2, 1, False)),  # yellow
            Triangle(self.scene(), (-1, 1, True)),  # blue
            Triangle(self.scene(), (-1, 1, False)),  # red
            Triangle(self.scene(), (0, 1, True)),  # green
            Triangle(self.scene(), (0, 1, False)),  # yellow
            Triangle(self.scene(), (1, 1, True)),  # blue
            Triangle(self.scene(), (1, 1, False)),  # red
            Triangle(self.scene(), (2, 1, True)),  # green
            # middle row
            Triangle(self.scene(),  (-1, 0, True)),     # yellow
            Triangle(self.scene(),  (-1, 0, False)),    # green
            Triangle(self.scene(), (0, 0, True)),       # red
            Triangle(self.scene(), (0, 0, False)),      # blue
            Triangle(self.scene(), (1, 0, True)),       # yellow
            Triangle(self.scene(), (1, 0, False)),      # green
            Triangle(self.scene(),  (2, 0, True)),      # red
            Triangle(self.scene(),  (2, 0, False)),     # blue
            # bottom row
            Triangle(self.scene(),  (-1, -1, False)),   # red
            Triangle(self.scene(), (0, -1, True)),      # green
            Triangle(self.scene(), (0, -1, False)),     # yellow
            Triangle(self.scene(), (1, -1, True)),      # blue
            Triangle(self.scene(), (1, -1, False)),     # red
            Triangle(self.scene(),  (2, -1, True)),     # green
            Triangle(self.scene(),  (2, -1, False)),    # yellow
            Triangle(self.scene(),  (3, -1, True)),    # blue
        ]

        def create_dot():
            r = DOT_RADIUS
            dot = QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            dot.setPos(0, 0)
            dot.setBrush(COLOR_DOT)
            dot.setPen(Qt.PenStyle.NoPen)
            dot.setZValue(100)
            self.scene().addItem(dot)
            return dot

        # one dot for each triangle color
        n_dots = len(self.triangles) // 4
        self.dots = [create_dot() for _ in range(n_dots)]

        self.triangle_grabber = TrianglesMouseGrabber(0, 0, 4, 2.7)
        self.scene().addItem(self.triangle_grabber)

        self.triangle_grabber.update_all.connect(self.mouse_update_all)

    def resizeEvent(self, event, /):
        width_in_pixels = 200
        width_of_scene = 4
        scale = width_in_pixels / width_of_scene
        self.resetTransform()
        self.scale(scale, scale)

    def refresh_boxes(self):
        # update the funscript axis with the constrained
        # coordinates to prevent strange drag-move behavior
        self.mouse_update_all.emit(*constrain_4p_amplitudes(*self.last_intensity))


    mouse_update_e1 = Signal(float)
    mouse_update_e2 = Signal(float)
    mouse_update_e3 = Signal(float)
    mouse_update_e4 = Signal(float)
    mouse_update_all = Signal(float, float, float, float)
