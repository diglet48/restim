import re

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtNetwork import QHostAddress

from net.tcode import TCodeCommand, InvalidTCodeException


class WebSocketServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.connections = []

        self.server = QtWebSockets.QWebSocketServer("restim t-code server", 1)  #not secure
        b = self.server.listen(QHostAddress.Any, 12346)
        if b:
            print("websocket server active at localhost:12346")
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
