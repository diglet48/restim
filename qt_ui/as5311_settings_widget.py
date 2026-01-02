import time

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import QTimer
import pyqtgraph as pg

from qt_ui.as5311_settings_widget_ui import Ui_AS5311SettingsWidget
from qt_ui.axis_controller import AxisController, PercentAxisController
from stim_math.axis import create_constant_axis

from stim_math.sensors.as5311 import AS5311Data, AS5311Algorithm


class AS5311SettingsWidget(QtWidgets.QWidget, Ui_AS5311SettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        ## Switch to using white background and black foreground
        # pg.setConfigOption('background', 'w')
        # pg.setConfigOption('foreground', 'k')

        self.setupUi(self)

        self.axis_range = create_constant_axis(0)
        self.axis_reduction = create_constant_axis(0)

        self.range_controller = AxisController(self.doubleSpinBox_range)
        self.range_controller.link_axis(self.axis_range)

        self.reduction_controller = PercentAxisController(self.doubleSpinBox_reduction)
        self.reduction_controller.link_axis(self.axis_reduction)


        self.as5311: AS5311Algorithm = None
        self.update_timer = QTimer(singleShot=False, interval=1000//60)
        self.update_timer.timeout.connect(self.update_triggered)

        self.checkBox.clicked.connect(self.update_checkbox_changed)

        self.p1 = self.graph.addPlot()
        self.graph.nextRow()
        self.p2 = self.graph.addPlot()
        self.p2.setXLink(self.p1)

        self.p1.setLabels(left=('Position', 'm'))
        self.p2.setLabels(left=('low-pass', 'm'))


        self.p1.addLegend(offset=(30, 5))
        self.p2.addLegend(offset=(30, 5))

        self.position_plot_item = pg.PlotDataItem(name='position')
        self.position_plot_item.setPen(pg.mkPen({'color': "blue", 'width': 1}))
        self.p1.addItem(self.position_plot_item)

        self.position_filtered_plot_item = pg.PlotDataItem(name='position (high-pass)')
        self.position_filtered_plot_item.setPen(pg.mkPen({'color': "orange", 'width': 1}))
        self.p2.addItem(self.position_filtered_plot_item)

        self.p1.setXRange(-10, 0, padding=0.05)

        self.x = []
        self.y_pos = []
        self.y_pos_filtered = []

    def set_as5311(self, as5311):
        self.as5311 = as5311

    def update_checkbox_changed(self):
        if self.checkBox.isChecked():
            self.update_timer.start()
        else:
            self.update_timer.stop()

    def update_triggered(self):
        if self.as5311 is None:
            return

        self.x.append(time.time())
        self.y_pos.append(self.as5311.position)
        self.y_pos_filtered.append(self.as5311.position_filterd)
        threshold = self.x[-1] - 10
        while len(self.x) and self.x[0] <= threshold:
            del self.x[0]
            del self.y_pos[0]
            del self.y_pos_filtered[0]

        if len(self.x):
            x = np.array(self.x) - self.x[-1]
            self.position_plot_item.setData(x=x, y=np.array(self.y_pos))
            self.position_filtered_plot_item.setData(x=x, y=np.array(self.y_pos_filtered))

