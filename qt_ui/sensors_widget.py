import functools
import os
import pathlib

from PySide6.QtCore import Qt, Signal
from pyqtgraph import GraphicsLayoutWidget

from funscript.collect_funscripts import Resource
from net.media_source.vlc import VLC
from net.media_source.kodi import Kodi
from qt_ui.additional_search_paths_dialog import AdditionalSearchPathsDialog
from qt_ui.device_wizard.axes import AxisEnum

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QAbstractItemView, QFileDialog, QWidget, QTreeWidgetItem, QFormLayout, QVBoxLayout, \
    QGroupBox, QLabel

from net.media_source.heresphere import HereSphere
from net.media_source.interface import MediaConnectionState
from qt_ui.file_dialog import FileDialog
from qt_ui.sensors.as5311_absolute_node import AS5311AbsoluteSensorNode
from qt_ui.sensors.as5311_highpass_node import AS5311HighPassNode
from qt_ui.sensors.as5311_edging_node import AS5311EdgingNode
from qt_ui.sensors.as5311_velocity_node import AS5311VelocitySensorNode
from qt_ui.sensors.imu_hip_thrust_node import IMUHipThrustNode
from qt_ui.sensors.imu_velocity_node import IMUVelocityNode
from qt_ui.sensors.pressure_absolute_node import PressureAbsoluteSensorNode
from qt_ui.sensors.pressure_depletion_node import PressureDepletionSensorNode
from qt_ui.sensors.sensor_node_interface import SensorNodeInterface
from qt_ui.sensors_widget_ui import Ui_SensorsWidget


from stim_math.sensors.as5311 import AS5311Data
from stim_math.sensors.imu import IMUData
from stim_math.sensors.pressure import PressureData


class Category:
    pass


# TODO: subclass from widget to display.. stuff
class CategoryIMU(Category):
    TITLE = "IMU"
    DESCRIPTION = "Requires FOC-Stim V4.2"


class CategoryAS5311(Category):
    TITLE = "AS5311"
    DESCRIPTION = "Requires FOC-Stim V4 with optional AS5311 sensor module"

class CategoryPressure(Category):
    TITLE = "Pressure"
    DESCRIPTION = "Requires FOC-Stim V4 with optional sparkfun micropressure sensor module"



class SensorsWidget(QWidget, Ui_SensorsWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.treeWidget.header().resizeSection(0, 120)
        self.treeWidget.header().resizeSection(1, 40)

        # remove any useless pages
        while self.stackedWidget.count():
            self.stackedWidget.removeWidget(self.stackedWidget.currentWidget())

        self.page_empty = QWidget()
        self.stackedWidget.addWidget(self.page_empty)
        self.stackedWidget.setCurrentIndex(0)

        larger_font = QFont()
        larger_font.setPointSize(12)

        self.structure = {
            CategoryIMU() : [
                IMUHipThrustNode(),
                IMUVelocityNode(),
            ],
            CategoryAS5311(): [
                AS5311AbsoluteSensorNode(),
                AS5311HighPassNode(),
                AS5311VelocitySensorNode(),
                # AS5311EdgingNode(),
            ],
            CategoryPressure(): [
                PressureAbsoluteSensorNode(),
                PressureDepletionSensorNode(),
            ]
        }

        self.treeWidget.clear()
        for category_class, nodes in self.structure.items():
            category_item = QTreeWidgetItem()
            category_item.setData(0, Qt.ItemDataRole.UserRole, category_class)
            category_item.setData(0, Qt.ItemDataRole.DisplayRole, category_class.TITLE)
            category_item.setFont(0, larger_font)
            self.treeWidget.addTopLevelItem(category_item)
            # TODO: add category class to stacked widget

            for node_class in nodes:
                node_item = QTreeWidgetItem()
                node_item.setData(0, Qt.ItemDataRole.UserRole, node_class)
                node_item.setData(0, Qt.ItemDataRole.DisplayRole, node_class.TITLE)
                category_item.addChild(node_item)
                self.stackedWidget.addWidget(node_class)

                try:
                    self.new_as5311_sensor_data.connect(node_class.new_as5311_sensor_data)
                except AttributeError:
                    pass

                try:
                    self.new_imu_sensor_data.connect(node_class.new_imu_sensor_data)
                except AttributeError:
                    pass

                try:
                    self.new_pressure_sensor_data.connect(node_class.new_pressure_sensor_data)
                except AttributeError:
                    pass

        self.treeWidget.expandAll()
        self.treeWidget.itemSelectionChanged.connect(self.index_changed)
        self.checkBox.clicked.connect(self.checkbox_clicked)

        self.index_changed()
        self.refresh_labels()

    def index_changed(self):
        # Update the description, enabled button and display widget
        # to those of the currently selected tree item.
        index = self.treeWidget.currentIndex()
        widget = index.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
        if isinstance(widget, QWidget) and self.stackedWidget.indexOf(widget) != -1:
            # switch to the corresponding widget
            self.stackedWidget.setCurrentWidget(widget)
            self.checkBox.setChecked(widget.is_node_enabled())
        else:
            self.stackedWidget.setCurrentWidget(self.page_empty)
            self.checkBox.setChecked(False)

        try:
            self.textBrowser.setText(widget.DESCRIPTION)
        except AttributeError:
            self.textBrowser.setText('')

    def refresh_labels(self):
        # update all the enabled labels in the tree
        for category_index in range(self.treeWidget.topLevelItemCount()):
            category = self.treeWidget.topLevelItem(category_index)
            # category_widget = category.data(0, Qt.ItemDataRole.UserRole)
            for node_index in range(category.childCount()):
                node = category.child(node_index)
                node_widget: SensorNodeInterface = node.data(0, Qt.ItemDataRole.UserRole)
                if node_widget.is_node_enabled():
                    node.setData(1, Qt.ItemDataRole.DisplayRole, 'enabled')
                else:
                    node.setData(1, Qt.ItemDataRole.DisplayRole, '')

    def checkbox_clicked(self):
        items = self.treeWidget.selectedItems()
        if len(items):
            node = items[0].data(0, Qt.ItemDataRole.UserRole)
            try:
                if self.checkBox.isChecked():
                    node.enable_node()
                else:
                    node.disable_node()
            except AttributeError:
                self.checkBox.setChecked(False)

        self.refresh_labels()

    def process(self, parameters):
        for category_label, nodes in self.structure.items():
            for node in nodes:
                if node.is_node_enabled():
                    node.process(parameters)

    new_as5311_sensor_data = Signal(AS5311Data)
    new_imu_sensor_data = Signal(IMUData)
    new_pressure_sensor_data = Signal(PressureData)