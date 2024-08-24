import re
import logging

from PyQt5 import QtCore, QtNetwork
from PyQt5.QtNetwork import QHostAddress

from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui import settings

from functools import partial

logger = logging.getLogger('restim.tcp_udp')


class TcpUdpServer(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.tcp_connections = []

        self.start_tcp_server()
        self.start_udp_server()

    def start_tcp_server(self):
        enabled = settings.tcp_enabled.get()
        port = settings.tcp_port.get()
        localhost_only = settings.tcp_localhost_only.get()

        self.tcp_server = QtNetwork.QTcpServer()
        address = QHostAddress.LocalHost if localhost_only else QHostAddress.Any
        if enabled:
            b = self.tcp_server.listen(address, port)
            if b:
                logger.info(f"TCP server active at localhost:{port}")
            else:
                logger.error(f"Unable to start TCP server: {self.tcp_server.errorString()}")
            self.tcp_server.newConnection.connect(self.new_tcp_connection)

    def start_udp_server(self):
        enabled = settings.udp_enabled.get()
        port = settings.udp_port.get()
        localhost_only = settings.udp_localhost_only.get()

        self.udp_socket = QtNetwork.QUdpSocket()
        address = QHostAddress.LocalHost if localhost_only else QHostAddress.Any
        if enabled:
            b = self.udp_socket.bind(address, port)
            if b:
                logger.info(f"UDP server active at localhost:{port}")
            else:
                logger.error(f"Unable to start UDP server: {self.udp_socket.errorString()}")
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
                    self.new_tcode_command.emit(tcode)
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
                    self.new_tcode_command.emit(tcode)
                except InvalidTCodeException as e:
                    pass

    def clientDisconnected(self):
        self.tcp_connections = [con for con in self.tcp_connections if con.state() == QtNetwork.QAbstractSocket.UnconnectedState]

    new_tcode_command = QtCore.pyqtSignal(TCodeCommand)
