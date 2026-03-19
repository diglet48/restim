import json
import logging

from PySide6 import QtNetwork
from PySide6.QtCore import Signal, QObject
from PySide6.QtWebSockets import QWebSocket

from stim_math.sensors.pressure import PressureData

logger = logging.getLogger('restim.websocket')


class WebsocketPressureHandler(QObject):
    def __init__(self, websocket: QWebSocket):
        super().__init__()
        self.websocket = websocket

        self.websocket.textMessageReceived.connect(self.textMessageReceived)
        self.websocket.disconnected.connect(self.disconnected)

    def textMessageReceived(self, msg):
        try:
            js = json.loads(msg)
            data = PressureData(pressure=js['pressure'])
            # print('received', data)
            self.new_pressure_data.emit(data)
        except json.decoder.JSONDecodeError:
            pass
        except KeyError:
            pass

    def transmit_pressure_data(self, data: PressureData):
        self.websocket.sendTextMessage(f'{{"pressure": {data.pressure:.2f}}}')

    def is_connected(self):
        return self.websocket.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState

    new_pressure_data = Signal(PressureData)
    disconnected = Signal()