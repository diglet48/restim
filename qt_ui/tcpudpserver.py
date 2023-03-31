import re

from PyQt5 import QtCore, QtNetwork
from PyQt5.QtNetwork import QHostAddress

from net.tcode import TCodeCommand, InvalidTCodeException
from functools import partial


class TcpUdpServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.tcp_connections = []

        self.tcp_server = QtNetwork.QTcpServer()
        b = self.tcp_server.listen(QHostAddress.Any, 12347)
        if b:
            print("TCP server active at localhost:12347")
        else:
            print("Unable to start TCP server:", self.tcp_server.errorString())

        self.tcp_server.newConnection.connect(self.new_tcp_connection)

        self.udp_socket = QtNetwork.QUdpSocket()
        b = self.udp_socket.bind(QHostAddress.Any, 12347)
        if b:
            print("UDP server active at localhost:12347")
        else:
            print("Unable to start UDP server:", self.udp_socket.errorString())
        self.udp_socket.readyRead.connect(self.udp_data_received)

    def new_tcp_connection(self):
        socket = self.tcp_server.nextPendingConnection()
        socket.readyRead.connect(partial(self.tcp_message_received, socket))
        socket.disconnected.connect(self.clientDisconnected)
        self.tcp_connections.append(socket)

    def tcp_message_received(self, socket: QtNetwork.QTcpSocket):
        while socket.canReadLine():
            msg = socket.readLine()
            msg = msg.data().decode('utf-8')
            for cmd in re.split('\\s|\n|\r', msg):
                if len(cmd) < 3:
                    continue
                try:
                    tcode = TCodeCommand.parse_command(cmd)
                    self.add_cmd(tcode)
                except InvalidTCodeException as e:
                    pass

    def udp_data_received(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram = self.udp_socket.receiveDatagram()
            msg = datagram.data()
            msg = msg.data().decode('utf-8')
            for cmd in re.split('\\s|\n|\r', msg):
                if len(cmd) < 3:
                    continue
                try:
                    tcode = TCodeCommand.parse_command(cmd)
                    self.add_cmd(tcode)
                except InvalidTCodeException as e:
                    pass

    def add_cmd(self, cmd: TCodeCommand):
        if cmd.axis_identifier == 'L0':
            self.alphaChanged.emit(cmd.value * 2 - 1)
        if cmd.axis_identifier == 'L1':
            self.betaChanged.emit(cmd.value * 2 - 1)
        if cmd.axis_identifier == 'L2':
            self.volumeChanged.emit(cmd.value)

    def clientDisconnected(self):
        self.tcp_connections = [con for con in self.tcp_connections if con.state() == QtNetwork.QAbstractSocket.UnconnectedState]

    alphaChanged = QtCore.pyqtSignal(float)
    betaChanged = QtCore.pyqtSignal(float)
    volumeChanged = QtCore.pyqtSignal(float)
