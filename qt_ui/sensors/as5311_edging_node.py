
from PySide6.QtWidgets import QWidget,QFormLayout, QVBoxLayout, QGroupBox, QLabel

import pyqtgraph as pg

from qt_ui.sensors.sensor_node_interface import SensorNodeInterface
from stim_math.sensors.as5311 import AS5311Data


class AS5311EdgingNode(QWidget, SensorNodeInterface):
    TITLE = "edging"
    DESCRIPTION = """todo todo"""

    def __init__(self, /):
        super().__init__()

    def new_as5311_sensor_data(self, data: AS5311Data):
        pass

    def process(self, parameters):
        pass