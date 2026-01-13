import time

import numpy as np
from PySide6 import QtWidgets
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLabel

from qt_ui.sensors.sensor_node_interface import SensorNodeInterface

from stim_math.sensors.imu import IMUData


class IMUVelocityNode(QtWidgets.QWidget, SensorNodeInterface):
    TITLE = "velocity"
    DESCRIPTION = ("Adjust signal intensity based on rotation/shaking of the box.\r\n"
                   "gyroscope-based\r\n"
                   "\r\n"
                   "example: reward/punish staying still\r\n")

    def __init__(self):
        super().__init__()

        # setup UI
        self.verticalLayout = QVBoxLayout(self)
        self.groupbox = QGroupBox(self)
        self.groupbox.setTitle("Settings")
        self.verticalLayout.addWidget(self.groupbox)
        self.formLayout = QFormLayout(self)
        self.groupbox.setLayout(self.formLayout)

        self.spinbox_high = pg.SpinBox(None, 0.0, compactHeight=False, suffix='deg/s', int=True)
        self.spinbox_low = pg.SpinBox(None, 0.0, compactHeight=False, suffix='deg/s', int=True)
        self.spinbox_volume = pg.SpinBox(None, 0.0, compactHeight=False, suffix='%', step=0.1)
        self.checkbox = QCheckBox()
        self.spinbox_decay = pg.SpinBox(None, 50, compactHeight=False, suffix='samples', step=1, bounds=[1, 1000])

        self.spinbox_low.valueChanged.connect(self.update_lines)
        self.spinbox_high.valueChanged.connect(self.update_lines)

        self.formLayout.addRow('high threshold', self.spinbox_high)
        self.formLayout.addRow('low threshold', self.spinbox_low)
        label = QLabel('volume change (?)')
        label.setToolTip(
            "Increase volume when near 'high threshold'\r\n"
            "Reduce volume when near 'low threshold'\r\n"
            "Negative value to reverse")
        self.formLayout.addRow(label, self.spinbox_volume)
        self.formLayout.addRow('decay', self.spinbox_decay)

        self.graph = pg.GraphicsLayoutWidget()
        self.verticalLayout.addWidget(self.graph)

        # setup plots
        self.p1 = self.graph.addPlot()
        self.graph.nextRow()

        self.p1.setLabels(left=('Movement', 'degrees/s'))

        self.p1.addLegend(offset=(30, 5))

        self.position_plot_item = pg.PlotDataItem(name='movement')
        self.position_plot_item.setPen(pg.mkPen({'color': "blue", 'width': 1}))
        self.p1.addItem(self.position_plot_item)

        self.low_marker = pg.InfiniteLine(1, 0, movable=False)
        self.p1.addItem(self.low_marker)

        self.high_marker = pg.InfiniteLine(10, 0, movable=False)
        self.p1.addItem(self.high_marker)

        self.p1.setXRange(-10, 0, padding=0.05)

        # setup algorithm variables
        self.value = 0

        # setup graph variables
        self.x = []
        self.y = []

        self.update_lines()

    def new_imu_sensor_data(self, data: IMUData):
        if not self.is_node_enabled():
            return

        new_value = np.abs(data.gyr_x) + np.abs(data.gyr_y) + np.abs(data.gyr_z)
        new_value = new_value / 1000 # convert to degrees-per-second
        self.value = self.value + (new_value - self.value) / self.spinbox_decay.value()

        self.x.append(time.time())
        self.y.append(self.value)
        threshold = self.x[-1] - 10
        while len(self.x) and self.x[0] <= threshold:
            del self.x[0]
            del self.y[0]

        self.update_graph_data()

    def process(self, parameters):
        if 'volume' in parameters:
            xp = [self.spinbox_low.value(), self.spinbox_high.value()]
            if self.spinbox_volume.value() >= 0:
                yp = [1 - self.spinbox_volume.value() / 100, 1]
            else:
                yp = [1, 1 + self.spinbox_volume.value() / 100]
            adjustment = np.clip(np.interp(self.value, xp, yp), 0, 1)
            parameters['volume'] *= adjustment

    def update_graph_data(self):
        x = np.array(self.x) - self.x[-1]
        y = np.array(self.y)
        self.position_plot_item.setData(x=x, y=y)

    def update_lines(self, *args, **kwargs):
        self.low_marker.setValue(self.spinbox_low.value())
        self.high_marker.setValue(self.spinbox_high.value())