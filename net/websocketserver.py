import re
import logging

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QSettings
from PyQt5.QtNetwork import QHostAddress

from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui.preferences_dialog import KEY_WEBSOCKET_ENABLED, KEY_WEBSOCKET_PORT, KEY_WEBSOCKET_LOCALHOST_ONLY

logger = logging.getLogger('restim.websocket')


class WebSocketServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.connections = []

        settings = QSettings()
        enabled = settings.value(KEY_WEBSOCKET_ENABLED, True, bool)
        port = settings.value(KEY_WEBSOCKET_PORT, 12346, int)
        localhost_only = settings.value(KEY_WEBSOCKET_LOCALHOST_ONLY, False, bool)

        if not enabled:
            logger.info("Not starting websocket server because disabled in settings.")
            return

        address = QHostAddress.LocalHost if localhost_only else QHostAddress.Any
        self.server = QtWebSockets.QWebSocketServer("restim t-code server", 1)  #not secure
        b = self.server.listen(address, port)
        if b:
            logger.info(f"websocket server active at localhost:{port}")
        else:
            logger.error(f"Unable to start websocket server: {self.server.errorString()}")

        self.server.newConnection.connect(self.new_connection)

    def new_connection(self):
        conn = self.server.nextPendingConnection()
        conn.textMessageReceived.connect(self.textMessageReceived)
        conn.disconnected.connect(self.clientDisconnected)
        self.connections.append(conn)

    def textMessageReceived(self, msg):
        for cmd in re.split('\\s|\n|\r', msg):
            try:
                tcode = TCodeCommand.parse_command(cmd)
                self.new_tcode_command.emit(tcode)
            except InvalidTCodeException:
                pass

    def clientDisconnected(self):
        self.connections = [con for con in self.connections if con.state() == QtNetwork.QAbstractSocket.UnconnectedState]

    new_tcode_command = QtCore.pyqtSignal(TCodeCommand)
