import json
import logging

from PySide6 import QtNetwork
from PySide6.QtCore import Signal, QObject
from PySide6.QtWebSockets import QWebSocket

from stim_math.sensors.as5311 import AS5311Data

logger = logging.getLogger('restim.websocket')


class WebsocketAS5311Handler(QObject):
    def __init__(self, websocket: QWebSocket):
        super().__init__()
        self.websocket = websocket

        self.websocket.textMessageReceived.connect(self.textMessageReceived)
        self.websocket.disconnected.connect(self.disconnected)

    def textMessageReceived(self, msg):
        # print('as5311 data received over websocket:', msg)
        try:
            js = json.loads(msg)
            data = AS5311Data(x=js['x'])
            # print('received', data)
            self.new_as5311_data.emit(data)
        except json.decoder.JSONDecodeError:
            pass
        except KeyError:
            pass

    def transmit_as5311_data(self, data: AS5311Data):
        self.websocket.sendTextMessage(f'{{"x": {data.x:.6f}}}')

    def is_connected(self):
        return self.websocket.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState

    new_as5311_data = Signal(AS5311Data)
    disconnected = Signal()