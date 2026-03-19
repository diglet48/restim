import logging

from PySide6 import QtCore, QtWebSockets
from PySide6.QtCore import Signal
from PySide6.QtNetwork import QHostAddress

from net.tcode import TCodeCommand
from net.websocket_as5311 import WebsocketAS5311Handler
from net.websocket_imu import WebsocketIMUHandler
from net.websocket_pressure import WebsocketPressureHandler
from net.websocket_tcode import WebsocketTCodeHandler
from qt_ui import settings
from stim_math.sensors.as5311 import AS5311Data
from stim_math.sensors.imu import IMUData
from stim_math.sensors.pressure import PressureData

logger = logging.getLogger('restim.websocket')


class WebSocketServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.handlers = []

        enabled = settings.websocket_enabled.get()
        port = settings.websocket_port.get()
        localhost_only = settings.websocket_localhost_only.get()

        if not enabled:
            logger.info("Not starting websocket server because disabled in settings.")
            return

        address = QHostAddress.SpecialAddress.LocalHost if localhost_only else QHostAddress.SpecialAddress.Any
        self.server = QtWebSockets.QWebSocketServer("restim", QtWebSockets.QWebSocketServer.SslMode.NonSecureMode)  #not secure
        b = self.server.listen(address, port)
        if b:
            logger.info(f"websocket server active at localhost:{port}")
        else:
            logger.error(f"Unable to start websocket server: {self.server.errorString()}")

        self.server.newConnection.connect(self.new_connection)

    def new_connection(self):
        websocket = self.server.nextPendingConnection()
        request = websocket.requestUrl()
        path = request.path()

        if path == '/tcode':
            handler = WebsocketTCodeHandler(websocket)
            handler.new_tcode_command.connect(self.new_tcode_command)
            handler.disconnected.connect(self.clientDisconnected)
            self.handlers.append(handler)
        elif path == '/sensors/as5311':
            handler = WebsocketAS5311Handler(websocket)
            handler.new_as5311_data.connect(self.incoming_as5311_data)
            self.transmit_as5311_data.connect(handler.transmit_as5311_data)
            handler.disconnected.connect(self.clientDisconnected)
            self.handlers.append(handler)
        elif path == '/sensors/pressure':
            handler = WebsocketPressureHandler(websocket)
            handler.new_pressure_data.connect(self.incoming_pressure_data)
            self.transmit_pressure_data.connect(handler.transmit_pressure_data)
            handler.disconnected.connect(self.clientDisconnected)
            self.handlers.append(handler)
        elif path == '/sensors/imu':
            handler = WebsocketIMUHandler(websocket)
            handler.new_imu_data.connect(self.incoming_imu_data)
            self.transmit_imu_data.connect(handler.transmit_imu_data)
            handler.disconnected.connect(self.clientDisconnected)
            self.handlers.append(handler)
        else:
            logger.warning(f"404 not found: {path}")
            websocket.close()

    def clientDisconnected(self):
        self.handlers = [handler for handler in self.handlers if handler.is_connected()]

    new_tcode_command = QtCore.Signal(TCodeCommand)

    transmit_as5311_data = Signal(AS5311Data)
    incoming_as5311_data = Signal(AS5311Data)

    transmit_pressure_data = Signal(PressureData)
    incoming_pressure_data = Signal(PressureData)

    transmit_imu_data = Signal(IMUData)
    incoming_imu_data = Signal(IMUData)
