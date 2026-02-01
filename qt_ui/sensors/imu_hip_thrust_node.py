import time

import numpy as np
from PySide6 import QtWidgets
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QFormLayout

from device.focstim.proto_device import LSM6DSOX_SAMPLERATE_HZ
from qt_ui.sensors import styles
from qt_ui.sensors.sensor_node_interface import SensorNodeInterface

from stim_math.sensors.imu import IMUData, IMUForwardPositionFilter


class IMUHipThrustNode(QtWidgets.QWidget, SensorNodeInterface):
    TITLE = "hip thrust"
    DESCRIPTION = ("Detect box movement in the Z direction, use that to change "
                   "position and intensity.\r\n"
                   "\r\n"
                   "position -> alpha\r\n"
                   "velocity -> volume")

    def __init__(self):
        super().__init__()

        # setup UI
        self.verticalLayout = QVBoxLayout(self)
        self.groupbox = QGroupBox(self)
        self.groupbox.setTitle("Movement")
        self.verticalLayout.addWidget(self.groupbox)
        self.formLayout = QFormLayout(self.groupbox)

        self.groupbox2 = QGroupBox(self)
        self.groupbox2.setTitle("Velocity")
        self.verticalLayout.addWidget(self.groupbox2)
        self.formLayout2 = QFormLayout(self.groupbox2)

        self.spinbox_position = pg.SpinBox(None, 0.0, compactHeight=False, suffix='m', siPrefix=True, dec=True, minStep=1e-4)
        self.spinbox_alpha = pg.SpinBox(None, 0.0, compactHeight=False, suffix='', dec=True, minStep=0.01)

        self.spinbox_velocity = pg.SpinBox(None, 0.0, compactHeight=False, suffix='m/s', siPrefix=True, dec=True, minStep=1e-3)
        self.spinbox_volume = pg.SpinBox(None, 0.0, compactHeight=False, suffix='%', dec=True, minStep=0.1)

        self.formLayout.addRow('position amplitude', self.spinbox_position)
        self.formLayout.addRow('alpha amplitude', self.spinbox_alpha)
        self.formLayout2.addRow('velocity amplitude', self.spinbox_velocity)
        self.formLayout2.addRow('volume amplitude', self.spinbox_volume)

        self.graph = pg.GraphicsLayoutWidget()
        self.verticalLayout.addWidget(self.graph)

        # setup plots
        self.p1 = self.graph.addPlot()
        self.graph.nextRow()
        self.p2 = self.graph.addPlot()
        self.p2.setXLink(self.p1)

        self.p1.setLabels(left=('Position', 'm'))
        self.p2.setLabels(left=('Speed', 'm/s'))

        self.p1.addLegend(offset=(30, 5))
        self.p2.addLegend(offset=(30, 5))

        self.position_plot_item = pg.PlotDataItem(name='position')
        self.position_plot_item.setPen(styles.blue_line)
        self.p1.addItem(self.position_plot_item)

        self.velocity_plot_item = pg.PlotDataItem(name='velocity')
        self.velocity_plot_item.setPen(styles.orange_line)
        self.p2.addItem(self.velocity_plot_item)

        self.p1.setXRange(-10, 0, padding=0.05)

        # setup algorithm variables
        self.filter = IMUForwardPositionFilter(LSM6DSOX_SAMPLERATE_HZ)

        # setup graph variables
        self.x = []
        self.y_pos = []
        self.y_velo = []

    def new_imu_sensor_data(self, data: IMUData):
        if not self.is_node_enabled():
            return

        self.filter.update(data)

        self.x.append(time.time())
        self.y_pos.append(self.filter.last_position())
        self.y_velo.append(self.filter.last_velocity())
        threshold = self.x[-1] - 10
        while len(self.x) and self.x[0] <= threshold:
            del self.x[0]
            del self.y_pos[0]
            del self.y_velo[0]

        self.update_graph_data()

    def process(self, parameters):
        if 'volume' in parameters:
            xp = [0, self.spinbox_velocity.value()]
            if self.spinbox_volume.value() >= 0:
                yp = [1 - self.spinbox_volume.value() / 100, 1]
            else:
                yp = [1, 1 + self.spinbox_volume.value() / 100]
            adjustment = np.clip(np.interp(np.abs(self.filter.last_velocity()), xp, yp), 0, 1)
            parameters['volume'] *= adjustment
        if 'alpha' in parameters:
            if self.spinbox_alpha.value() and self.spinbox_position.value():
                diff = self.filter.last_position() / self.spinbox_position.value()
                diff = np.clip(diff, -1, 1)
                change = diff * self.spinbox_alpha.value()
                parameters['alpha'] += change

    def update_graph_data(self):
        x = np.array(self.x) - self.x[-1]
        y = np.array(self.y_pos)
        self.position_plot_item.setData(x=x, y=y)

        y2 = np.array(self.y_velo)
        self.velocity_plot_item.setData(x=x, y=y2)
