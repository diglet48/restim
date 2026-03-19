import logging
import re

from PySide6 import QtNetwork
from PySide6.QtCore import Signal, QObject
from PySide6.QtWebSockets import QWebSocket

from net.tcode import TCodeCommand, InvalidTCodeException

logger = logging.getLogger('restim.websocket')


class WebsocketTCodeHandler(QObject):
    def __init__(self, websocket: QWebSocket):
        super().__init__()
        self.websocket = websocket

        self.websocket.textMessageReceived.connect(self.textMessageReceived)
        self.websocket.disconnected.connect(self.disconnected)

    def textMessageReceived(self, msg):
        # print(msg)
        for cmd in re.split('\\s|\n|\r', msg):
            try:
                tcode = TCodeCommand.parse_command(cmd)
                self.new_tcode_command.emit(tcode)
            except InvalidTCodeException:
                pass

    def is_connected(self):
        return self.websocket.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState

    new_tcode_command = Signal(TCodeCommand)
    disconnected = Signal()