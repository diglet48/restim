"""
3D wireframe tetrahedron visualization for 4-phase electrode display.

Shows the regular tetrahedron whose 4 vertices correspond to the 4 electrodes
(A, B, C, D). A cursor dot indicates the current position in abc space.

Auto-rotates slowly; drag with the mouse to rotate manually.
"""

import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPolygonF, QMouseEvent

# e1234_to_abc is designed for sequences and has sign ambiguity with single
# samples, so we use barycentric interpolation on the tetrahedron vertices.

# ---------- tetrahedron geometry (same coefficients as transforms_4) ----------

COEF_1 = 1
COEF_2 = np.sqrt(8) / 3
COEF_3 = np.sqrt(2) / np.sqrt(3)

VERTICES = np.array([
    [ COEF_1,           0,          0       ],   # A  (electrode 1)
    [-COEF_1 / 3,       COEF_2,     0       ],   # B  (electrode 2)
    [-COEF_1 / 3,      -COEF_2 / 2, COEF_3 ],   # C  (electrode 3)
    [-COEF_1 / 3,      -COEF_2 / 2,-COEF_3 ],   # D  (electrode 4)
])

EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

# Face i is the face OPPOSITE vertex i (contains the other 3 vertices).
FACES = [
    (1, 2, 3),   # opposite A
    (0, 2, 3),   # opposite B
    (0, 1, 3),   # opposite C
    (0, 1, 2),   # opposite D
]

# ----------------------------- colours ----------------------------------------

# SSBU-style electrode colours
VERTEX_COLORS = [
    QColor(0xFE, 0x2E, 0x2E),   # A – red
    QColor(0x54, 0x63, 0xFF),    # B – blue
    QColor(0xFF, 0xC7, 0x17),    # C – yellow
    QColor(0x1F, 0x9E, 0x40),    # D – green
]
LABELS = ['A', 'B', 'C', 'D']

CURSOR_COLOR = QColor(180, 140, 220)

# ----------------------------- helpers ----------------------------------------

def _rotation_matrix(yaw: float, pitch: float) -> np.ndarray:
    """Rotation: pitch around X, then yaw around Y."""
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    Ry = np.array([[ cy, 0, sy],
                    [  0, 1,  0],
                    [-sy, 0, cy]])
    Rx = np.array([[1,  0,   0],
                    [0, cp, -sp],
                    [0, sp,  cp]])
    return Ry @ Rx


# ==============================================================================

class FourphaseWidgetTetrahedron(QWidget):
    """Rotating 3-D wireframe tetrahedron with a cursor dot."""

    mousePositionChanged = Signal(float, float, float)   # a, b, c  (compat)

    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)

        # rotation state
        self._yaw   =  0.4
        self._pitch = -0.3

        # auto-rotation
        self._auto_rotate       = True
        self._auto_rotate_speed = 0.008          # rad / frame

        # mouse drag
        self._dragging       = False
        self._last_mouse_pos = None

        self._idle_timer = QTimer()
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._resume_auto_rotate)

        # repaint timer (~30 fps)
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

        # cursor
        self._cursor_abc   = None
        self._cursor_alpha = 1.0

        from qt_ui.dark_mode import is_dark_mode
        self._dark = is_dark_mode()

        self.setMinimumSize(100, 100)

    # ------------------------------------------------------------------
    #  public API
    # ------------------------------------------------------------------

    def set_electrode_intensities(self, a, b, c, d):
        """Convert electrode intensities (a,b,c,d) → abc and update cursor.

        Uses barycentric interpolation: the position is the weighted average
        of the tetrahedron vertices, which always lands inside the shape.
        """
        total = a + b + c + d
        if total > 0:
            self._cursor_abc = (a * VERTICES[0] + b * VERTICES[1]
                                + c * VERTICES[2] + d * VERTICES[3]) / total
        else:
            self._cursor_abc = np.zeros(3)
        self._cursor_alpha = float(np.clip(np.linalg.norm(self._cursor_abc),
                                           0, 1))

    def set_cursor_position_abc(self, a, b, c):
        self._cursor_abc   = np.array([a, b, c])
        self._cursor_alpha = float(np.clip(np.linalg.norm(self._cursor_abc),
                                           0, 1))

    # ------------------------------------------------------------------
    #  timers
    # ------------------------------------------------------------------

    def _tick(self):
        if self._auto_rotate:
            self._yaw += self._auto_rotate_speed
        self.update()

    def _resume_auto_rotate(self):
        self._auto_rotate = True

    # ------------------------------------------------------------------
    #  mouse interaction  (rotate the view)
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging       = True
            self._last_mouse_pos = event.position()
            self._auto_rotate    = False
            self._idle_timer.stop()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging       = False
            self._last_mouse_pos = None
            self._idle_timer.start(5000)          # resume after 5 s idle

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and self._last_mouse_pos is not None:
            pos = event.position()
            dx = pos.x() - self._last_mouse_pos.x()
            dy = pos.y() - self._last_mouse_pos.y()
            self._yaw  += dx * 0.005
            self._pitch = float(np.clip(self._pitch + dy * 0.005,
                                        -np.pi / 2 + 0.1,
                                         np.pi / 2 - 0.1))
            self._last_mouse_pos = pos
            self.update()

    # ------------------------------------------------------------------
    #  painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):                               # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # background
        bg = QColor(30, 30, 30) if self._dark else QColor(240, 240, 240)
        p.fillRect(self.rect(), bg)

        w, h   = self.width(), self.height()
        cx, cy = w / 2, h / 2
        scale  = min(w, h) * 0.42

        rot     = _rotation_matrix(self._yaw, self._pitch)
        rotated = (rot @ VERTICES.T).T          # (4, 3)
        proj    = rotated[:, :2]                # xy on screen
        depth   = rotated[:, 2]                 # z  (larger → closer)

        # cursor in screen space
        cur_scr = None
        if self._cursor_abc is not None:
            rc      = rot @ self._cursor_abc
            cur_scr = (cx + rc[0] * scale,
                       cy - rc[1] * scale,
                       rc[2])

        # ---- faces (painter's algorithm: back first) --------------------
        face_info = []
        for fi, fv in enumerate(FACES):
            vs = rotated[list(fv)]
            cz = float(np.mean(vs[:, 2]))
            n  = np.cross(vs[1] - vs[0], vs[2] - vs[0])
            front = n[2] > 0
            face_info.append((cz, fi, fv, front))
        face_info.sort(key=lambda x: x[0])

        for _, fi, fv, front in face_info:
            poly = QPolygonF()
            for vi in fv:
                poly.append(QPointF(cx + proj[vi, 0] * scale,
                                    cy - proj[vi, 1] * scale))
            alpha = 35 if front else 15
            fc = QColor(255, 255, 255, alpha) if self._dark \
                 else QColor(0, 0, 0, alpha)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(fc)
            p.drawPolygon(poly)

        # ---- edges (depth-based alpha & width) --------------------------
        for i, j in EDGES:
            x1 = cx + proj[i, 0] * scale
            y1 = cy - proj[i, 1] * scale
            x2 = cx + proj[j, 0] * scale
            y2 = cy - proj[j, 1] * scale

            az = (depth[i] + depth[j]) / 2
            a  = int(np.interp(az, [-1.2, 1.2], [60, 200]))
            ew = float(np.interp(az, [-1.2, 1.2], [1.0, 2.2]))

            ec = QColor(180, 180, 180, a) if self._dark \
                 else QColor(80, 80, 80, a)
            pen = QPen(ec)
            pen.setWidthF(ew)
            p.setPen(pen)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # ---- cursor dot -------------------------------------------------
        if cur_scr is not None:
            sx, sy, _ = cur_scr
            r   = 7
            a   = int(255 * self._cursor_alpha)
            cc  = QColor(CURSOR_COLOR)
            cc.setAlpha(a)
            oc  = QColor(255, 255, 255, int(200 * self._cursor_alpha))
            pen = QPen(oc)
            pen.setWidthF(2)
            p.setPen(pen)
            p.setBrush(cc)
            p.drawEllipse(QPointF(sx, sy), r, r)

        # ---- vertices (back to front) -----------------------------------
        sorted_vi = sorted(range(4), key=lambda i: depth[i])
        for vi in sorted_vi:
            sx = cx + proj[vi, 0] * scale
            sy = cy - proj[vi, 1] * scale

            df = float(np.interp(depth[vi], [-1.2, 1.2], [0.7, 1.2]))
            af = float(np.interp(depth[vi], [-1.2, 1.2], [0.4, 1.0]))

            r  = 6 * df
            vc = QColor(VERTEX_COLORS[vi]);  vc.setAlpha(int(255 * af))
            oc = QColor(255, 255, 255, int(180 * af))
            pen = QPen(oc);  pen.setWidthF(1.5)
            p.setPen(pen)
            p.setBrush(vc)
            p.drawEllipse(QPointF(sx, sy), r, r)

        p.end()
