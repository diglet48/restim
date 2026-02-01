import pyqtgraph as pg
from PySide6.QtCore import Qt

# used for horizontal lines
yellow_line_solid = pg.mkPen(width=1, style=Qt.PenStyle.SolidLine, color='yellow')
yellow_line_dash  = pg.mkPen(width=1, style=Qt.PenStyle.DashLine, color='yellow')

# plot item 1, 2, 3...
blue_line = pg.mkPen(color="blue", width=1)
orange_line = pg.mkPen(color="orange", width=1)
green_line = pg.mkPen(color="green", width=1)
