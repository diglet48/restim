import time

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import QTimer
import pyqtgraph as pg

from qt_ui.imu_settings_widget_ui import Ui_IMUSettingsWidget
from qt_ui.axis_controller import AxisController, PercentAxisController

from stim_math.axis import create_constant_axis
from stim_math.sensors.imu import IMUAlgorithm


class IMUSettingsWidget(QtWidgets.QWidget, Ui_IMUSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.axis_movement_amplitude_in = create_constant_axis(0)
        self.axis_movement_amplitude_out = create_constant_axis(0)

        self.axis_velocity_amplitude = create_constant_axis(0)
        self.axis_intensity_increase = create_constant_axis(0)


        self.device_movement_amplitude_in_controller = AxisController(self.doubleSpinBox_movement_in)
        self.device_movement_amplitude_in_controller.link_axis(self.axis_movement_amplitude_in)

        self.device_movement_amplitude_out_controller = AxisController(self.doubleSpinBox_movement_out)
        self.device_movement_amplitude_out_controller.link_axis(self.axis_movement_amplitude_out)

        self.device_velocity_controller = AxisController(self.doubleSpinBox_velocity_in)
        self.device_velocity_controller.link_axis(self.axis_velocity_amplitude)

        self.device_intensity_controller = PercentAxisController(self.doubleSpinBox_intensity_increase)
        self.device_intensity_controller.link_axis(self.axis_intensity_increase)

        self.imu: IMUAlgorithm = None
        self.update_timer = QTimer(singleShot=False, interval=1000//60)
        self.update_timer.timeout.connect(self.update_triggered)

        self.checkBox.clicked.connect(self.update_checkbox_changed)

        self.p1 = self.graph.addPlot()
        self.graph.nextRow()
        self.p2 = self.graph.addPlot()
        self.p2.setXLink(self.p1)

        self.p1.setLabels(left=('Position', 'm'))
        self.p2.setLabels(left=('Speed', 'm/s'))

        self.p1.addLegend(offset=(30, 5))
        self.p2.addLegend(offset=(30, 5))

        self.position_plot_item = pg.PlotDataItem(name='position')
        self.position_plot_item.setPen(pg.mkPen({'color': "blue", 'width': 1}))
        self.p1.addItem(self.position_plot_item)

        self.velocity_plot_item = pg.PlotDataItem(name='velocity')
        self.velocity_plot_item.setPen(pg.mkPen({'color': "orange", 'width': 1}))
        self.p2.addItem(self.velocity_plot_item)

        self.p1.setXRange(-10, 0, padding=0.05)

        self.x = []
        self.y_pos = []
        self.y_velo = []

    def set_imu(self, imu):
        self.imu = imu

    def update_checkbox_changed(self):
        if self.checkBox.isChecked():
            self.update_timer.start()
        else:
            self.update_timer.stop()

    def update_triggered(self):
        if self.imu is None:
            return

        self.x.append(time.time())
        self.y_pos.append(self.imu.last_position())
        self.y_velo.append(self.imu.last_velocity())
        threshold = self.x[-1] - 10
        while len(self.x) and self.x[0] <= threshold:
            del self.x[0]
            del self.y_pos[0]
            del self.y_velo[0]

        if len(self.x):
            x = np.array(self.x) - self.x[-1]
            self.position_plot_item.setData(x=x, y=np.array(self.y_pos))
            self.velocity_plot_item.setData(x=x, y=np.array(self.y_velo))

