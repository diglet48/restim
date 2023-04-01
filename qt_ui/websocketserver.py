import re

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QSettings
from PyQt5.QtNetwork import QHostAddress

from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui.preferencesdialog import KEY_WEBSOCKET_ENABLED, KEY_WEBSOCKET_PORT, KEY_WEBSOCKET_LOCALHOST_ONLY


class WebSocketServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.connections = []

        settings = QSettings()
        enabled = settings.value(KEY_WEBSOCKET_ENABLED, True, bool)
        port = settings.value(KEY_WEBSOCKET_PORT, 12346, int)
        localhost_only = settings.value(KEY_WEBSOCKET_LOCALHOST_ONLY, False, bool)

        if not enabled:
            print("Not starting websocket server because disabled in settings.")
            return

        address = QHostAddress.LocalHost if localhost_only else QHostAddress.Any
        self.server = QtWebSockets.QWebSocketServer("restim t-code server", 1)  #not secure
        b = self.server.listen(address, port)
        if b:
            print(f"websocket server active at localhost:{port}")
        else:
            print("Unable to start websocket server:", self.server.errorString())

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
                self.add_cmd(tcode)
            except InvalidTCodeException:
                pass

    def add_cmd(self, cmd: TCodeCommand):
        if cmd.axis_identifier == 'L0':
            self.alphaChanged.emit(cmd.value * 2 - 1)
        if cmd.axis_identifier == 'L1':
            self.betaChanged.emit(cmd.value * 2 - 1)
        if cmd.axis_identifier == 'L2':
            self.volumeChanged.emit(cmd.value)

    def clientDisconnected(self):
        self.connections = [con for con in self.connections if con.state() == QtNetwork.QAbstractSocket.UnconnectedState]

    alphaChanged = QtCore.pyqtSignal(float)
    betaChanged = QtCore.pyqtSignal(float)
    volumeChanged = QtCore.pyqtSignal(float)
