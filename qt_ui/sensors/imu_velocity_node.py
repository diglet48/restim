import time

import numpy as np
from PySide6 import QtWidgets
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLabel
from PySide6.QtCore import Qt

from qt_ui.sensors.sensor_node_interface import SensorNodeInterface
from qt_ui.sensors import styles

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
        self.formLayout = QFormLayout(self.groupbox)

        self.spinbox_threshold = pg.SpinBox(None, 0.0, compactHeight=False, suffix='deg/s', int=True)
        self.spinbox_range = pg.SpinBox(None, 0.0, compactHeight=False, suffix='deg/s', int=True, bounds=[0, None])
        self.spinbox_volume = pg.SpinBox(None, 0.0, compactHeight=False, suffix='%', step=0.1)
        self.checkbox = QCheckBox()
        self.spinbox_decay = pg.SpinBox(None, 50, compactHeight=False, suffix='samples', step=1, bounds=[1, 1000])

        self.spinbox_threshold.valueChanged.connect(self.update_lines)
        self.spinbox_range.valueChanged.connect(self.update_lines)

        self.formLayout.addRow('threshold', self.spinbox_threshold)
        self.formLayout.addRow('threshold range', self.spinbox_range)
        label = QLabel('volume change (?)')
        label.setToolTip(
            "positive: increase volume when moving\r\n"
            "negative: decrease volume when moving")
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
        self.position_plot_item.setPen(styles.blue_line)
        self.p1.addItem(self.position_plot_item)

        self.low_marker = pg.InfiniteLine(1, 0, movable=False, pen=styles.yellow_line_solid)
        self.p1.addItem(self.low_marker)

        self.high_marker = pg.InfiniteLine(10, 0, movable=False, pen=styles.yellow_line_dash)
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
            low = self.spinbox_threshold.value()
            high = low + self.spinbox_range.value()
            xp = [low, high]
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
        low = self.spinbox_threshold.value()
        high = low + self.spinbox_range.value()
        self.low_marker.setValue(low)
        self.high_marker.setValue(high)