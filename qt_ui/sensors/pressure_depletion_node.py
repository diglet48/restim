import time

from PySide6.QtWidgets import QWidget,QFormLayout, QVBoxLayout, QGroupBox, QLabel

import pyqtgraph as pg
import numpy as np

from qt_ui.sensors import styles
from stim_math.sensors.pressure import PressureData
from stim_math.sensors.eom import EOMController

from qt_ui.sensors.sensor_node_interface import SensorNodeInterface


class PressureDepletionSensorNode(QWidget, SensorNodeInterface):
    TITLE = "depletion"
    DESCRIPTION = "Implements the Edge-o-Matic 3000 depletion mode.\r\n"

    def __init__(self, /):
        super().__init__()

        # setup UI
        self.verticalLayout = QVBoxLayout(self)
        self.groupbox = QGroupBox(self)
        self.groupbox.setTitle("Settings")
        self.verticalLayout.addWidget(self.groupbox)
        self.formLayout = QFormLayout(self.groupbox)

        self.spinbox_arousal_threshold = pg.SpinBox(None, 1300, compactHeight=False, suffix='Pa', siPrefix=True, dec=True, minStep=100)
        self.spinbox_ramp_time = pg.SpinBox(None, 30, compactHeight=False, suffix='s', int=True, bounds=(1, 10000))
        self.spinbox_start_volume = pg.SpinBox(None, 100, compactHeight=False, suffix='%', step=0.1, bounds=(0, 100))
        self.label_volume = pg.ValueLabel(None, formatStr="{value:.0f} %")

        self.spinbox_arousal_threshold.valueChanged.connect(self.update_lines)

        self.formLayout.addRow('arousal threshold', self.spinbox_arousal_threshold)
        self.formLayout.addRow('ramp time', self.spinbox_ramp_time)
        self.formLayout.addRow('start volume', self.spinbox_start_volume)
        self.formLayout.addRow('effective volume', self.label_volume)

        self.graph = pg.GraphicsLayoutWidget()
        self.verticalLayout.addWidget(self.graph)

        # setup plots
        self.p1 = self.graph.addPlot()
        self.graph.nextRow()
        self.p2 = self.graph.addPlot()
        self.p2.setXLink(self.p1)

        self.p1.setLabels(left=('Pressure', 'Pa'))
        self.p2.setLabels(left=('Arousal', 'Pa'))

        self.p1.addLegend(offset=(30, 5))
        self.p2.addLegend(offset=(30, 5))

        self.pressure_plot_item = pg.PlotDataItem(name='pressure')
        self.pressure_plot_item.setPen(styles.blue_line)
        self.p1.addItem(self.pressure_plot_item)

        self.arousal_plot_item = pg.PlotDataItem(name='arousal')
        self.arousal_plot_item.setPen(styles.orange_line)
        self.p2.addItem(self.arousal_plot_item)


        self.arousal_threshold_marker = pg.InfiniteLine(1, 0, movable=False)
        self.p2.addItem(self.arousal_threshold_marker)

        self.p1.setXRange(-10, 0, padding=0.05)

        # setup algorithm variables
        self.pressure = 0

        self.eom_controller = EOMController()

        # setup plot variables
        self.x = []
        self.y_pressure = []
        self.y_arousal = []

        self.update_lines()

    def new_pressure_sensor_data(self, data: PressureData):
        if not self.is_node_enabled():
            return

        self.eom_controller.min_speed = self.spinbox_start_volume.value() / 100
        self.eom_controller.ramp_time = self.spinbox_ramp_time.value()
        self.eom_controller.sensitivity_threshold = self.spinbox_arousal_threshold.value()

        self.eom_controller.update(data.pressure)

        self.label_volume.setValue(self.eom_controller.speed * 100)

        self.x.append(time.time())
        self.y_pressure.append(data.pressure)
        self.y_arousal.append(self.eom_controller.arousal)

        threshold = time.time() - 10
        while len(self.x) and self.x[0] < threshold:
            del self.x[0]
            del self.y_pressure[0]
            del self.y_arousal[0]

        self.update_graph_data()

    def process(self, parameters):
        if 'volume' in parameters:
            adjustment = np.clip(self.eom_controller.speed, 0, 1)
            parameters['volume'] *= adjustment

    def update_graph_data(self):
        x = np.array(self.x) - self.x[-1]
        y = np.array(self.y_pressure)
        self.pressure_plot_item.setData(x=x, y=y)

        y2 = np.array(self.y_arousal)
        self.arousal_plot_item.setData(x=x, y=y2)

    def update_lines(self, *args, **kwargs):
        self.arousal_threshold_marker.setValue(self.spinbox_arousal_threshold.value())

