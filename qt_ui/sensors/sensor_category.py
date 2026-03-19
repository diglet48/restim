from PySide6 import QtNetwork
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QWidget, QButtonGroup
from PySide6.QtCore import Signal, QTimer, QUrl, Qt
from PySide6.QtWebSockets import QWebSocket

from net.websocket_as5311 import WebsocketAS5311Handler
from net.websocket_imu import WebsocketIMUHandler
from net.websocket_pressure import WebsocketPressureHandler
from qt_ui import settings
from qt_ui.sensors.sensor_category_ui import Ui_SensorCategory



class SensorCategory(QWidget, Ui_SensorCategory):
    URL_FORMAT_STRING = ""

    def __init__(self):
        super().__init__(None)
        self.setupUi(self)

        self.buttonGroup.setId(self.radio_device, 1)
        self.buttonGroup.setId(self.radio_external, 2)
        self.buttonGroup.setId(self.radio_pull_data, 3)

        self.reload_settings()

        self.label_device_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_device_url.setCursor(QCursor(Qt.CursorShape.IBeamCursor))
        self.label_external_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label_external_url.setCursor(QCursor(Qt.CursorShape.IBeamCursor))

        self.line_restim_url.textChanged.connect(self.url_changed)
        self.buttonGroup.buttonToggled.connect(self.url_changed)

        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(1000)
        self.reconnect_timer.timeout.connect(self.timeout)
        self.reconnect_timer.start()

        self.handler = None
        self.websocket = None
        self.refresh_label()

    def reload_settings(self):
        label_url = self.URL_FORMAT_STRING.format(port=settings.websocket_port.get())
        self.label_external_url.setText(f"Send data to {label_url}")
        self.label_device_url.setText(f"Data available at {label_url}")

    def refresh_label(self):
        if self.websocket is None:
            self.label_status.setText("Not connected")
        elif self.websocket.state() == QtNetwork.QAbstractSocket.SocketState.UnconnectedState:
            self.label_status.setText("Not connected")
        elif self.websocket.state() == QtNetwork.QAbstractSocket.SocketState.ConnectedState:
            self.label_status.setText("Connected")
        else:
            self.label_status.setText("Connecting...")

    def sensor_data_from_device(self, data):
        if self.radio_device.isChecked():
            self.new_sensor_data.emit(data)

    def sensor_data_from_network(self, data):
        if self.radio_external.isChecked():
            self.new_sensor_data.emit(data)

    def sensor_data_from_other_restim_instance(self, data):
        if self.radio_pull_data.isChecked():
            self.new_sensor_data.emit(data)

    def url_changed(self):
        self.websocket = None
        self.handler = None
        self.refresh_label()
        self.timeout()

    def timeout(self):
        if not self.radio_pull_data.isChecked():
            return

        if self.websocket is None or self.websocket.state() == QtNetwork.QAbstractSocket.SocketState.UnconnectedState:
            self.websocket = QWebSocket()
            url = QUrl(self.line_restim_url.text())
            if url.isValid():
                self.websocket.open(url)
                self.websocket.connected.connect(self.websocket_connected)
                self.websocket.disconnected.connect(self.websocket_disconnected)
                self.websocket.stateChanged.connect(self.refresh_label)

    def websocket_disconnected(self):
        self.refresh_label()

    def websocket_connected(self):
        self.handler = self.create_handler(self.websocket)

    def create_handler(self, websocket):
        return WebsocketAS5311Handler(websocket)

    # can be AS5311Data or IMUData...
    new_sensor_data = Signal(object)


class SensorCategoryIMU(SensorCategory):
    TITLE = "IMU"
    DESCRIPTION = "Requires FOC-Stim V4.2"
    URL_FORMAT_STRING = "ws://localhost:{port}/sensors/imu"

    def __init__(self):
        super().__init__()

    def create_handler(self, websocket):
        handler = WebsocketIMUHandler(websocket)
        handler.new_imu_data.connect(self.new_sensor_data)
        return handler

    def reload_settings(self):
        button_id = settings.sensor_imu_source_index.get()
        button = self.buttonGroup.button(button_id)
        if button is None:
            button = self.radio_device
        button.setChecked(True)
        self.line_restim_url.setText(settings.sensor_imu_pull_url.get())

        super().reload_settings()

    def save_settings(self):
        settings.sensor_imu_source_index.set(self.buttonGroup.checkedId())
        settings.sensor_imu_pull_url.set(self.line_restim_url.text())


class SensorCategoryAS5311(SensorCategory):
    TITLE = "AS5311"
    DESCRIPTION = "Requires FOC-Stim V4 with optional AS5311 sensor module"
    URL_FORMAT_STRING = "ws://localhost:{port}/sensors/as5311"

    def __init__(self):
        super().__init__()

    def create_handler(self, websocket):
        handler = WebsocketAS5311Handler(websocket)
        handler.new_as5311_data.connect(self.new_sensor_data)
        return handler

    def reload_settings(self):
        button_id = settings.sensor_as5311_source_index.get()
        button = self.buttonGroup.button(button_id)
        if button is None:
            button = self.radio_device
        button.setChecked(True)
        self.line_restim_url.setText(settings.sensor_as5311_pull_url.get())

        super().reload_settings()

    def save_settings(self):
        settings.sensor_as5311_source_index.set(self.buttonGroup.checkedId())
        settings.sensor_as5311_pull_url.set(self.line_restim_url.text())


class SensorCategoryPressure(SensorCategory):
    TITLE = "Pressure"
    DESCRIPTION = "Requires FOC-Stim V4 with optional sparkfun micropressure sensor module"
    URL_FORMAT_STRING = "ws://localhost:{port}/sensors/pressure"

    def __init__(self):
        super().__init__()

    def create_handler(self, websocket):
        handler = WebsocketPressureHandler(websocket)
        handler.new_pressure_data.connect(self.new_sensor_data)
        return handler

    def reload_settings(self):
        button_id = settings.sensor_pressure_source_index.get()
        button = self.buttonGroup.button(button_id)
        if button is None:
            button = self.radio_device
        button.setChecked(True)
        self.line_restim_url.setText(settings.sensor_pressure_pull_url.get())

        super().reload_settings()

    def save_settings(self):
        settings.sensor_pressure_source_index.set(self.buttonGroup.checkedId())
        settings.sensor_pressure_pull_url.set(self.line_restim_url.text())
