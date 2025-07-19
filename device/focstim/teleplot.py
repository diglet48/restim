from PySide6.QtCore import QIODevice
from PySide6.QtNetwork import QUdpSocket, QAbstractSocket

teleplot_addr = "127.0.0.1"
teleplot_port = 47269


class Teleplot:
    def __init__(self, prefix=''):
        self.prefix = prefix
        self.teleplot_socket = QUdpSocket()
        self.teleplot_socket.connectToHost(teleplot_addr, teleplot_port, QIODevice.OpenModeFlag.WriteOnly)

    def write_metrics(self, **kwargs):
        lines = []
        for k, v in kwargs.items():
            lines.append(f"{self.prefix}{k}:{v}")
        msg = "\r\n".join(lines)
        self.teleplot_socket.write(msg.encode('utf-8'))

