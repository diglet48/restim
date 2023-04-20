import re
import numpy as np

from PyQt5 import QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QIODevice

from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui.preferencesdialog import KEY_SERIAL_ENABLED, KEY_SERIAL_PORT, KEY_SERIAL_AUTO_EXPAND


class FunscriptExpander:
    def __init__(self):
        self.alpha = 0

    def expand(self, cmd: TCodeCommand):
        if cmd.interval < 10:
            return [0], [cmd.value * 2 - 1], [0]

        alpha_start = self.alpha
        alpha_end = cmd.value * 2 - 1
        duration = cmd.interval

        center = (alpha_start + alpha_end) / 2
        radius = abs(center - alpha_start)
        n = max(2, int(duration / 10))
        interval = np.linspace(0, cmd.interval, n)
        theta = np.linspace(0, np.pi, n)
        beta = radius * np.sin(theta)
        alpha = center + radius * np.cos(theta)
        if alpha_start < alpha_end:
            beta *= -1
            alpha = center - (alpha - center)

        self.alpha = alpha_end
        return interval, alpha, beta


class SerialProxy(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        settings = QSettings()

        self.expander = FunscriptExpander()
        self.do_auto_expand = settings.value(KEY_SERIAL_AUTO_EXPAND, True, bool)

        self.port = QSerialPort(self)
        self.port.setPortName(settings.value(KEY_SERIAL_PORT, "COM20", str))
        self.port.setBaudRate(115200)
        self.port.readyRead.connect(self.new_serial_data)
        if settings.value(KEY_SERIAL_ENABLED, False, bool):
            b = self.port.open(QIODevice.ReadOnly)
            if b:
                print(f"Serial listener active on port: {self.port.portName()}")
            else:
                print("Unable to listen to serial post:", self.port.errorString())

        self.data = b''

    def new_serial_data(self):
        self.data += bytes(self.port.readAll())
        while 1:
            match = re.search(b'[\n\r ]', self.data)
            if match is None:
                return
            cmd = self.data[0:match.regs[0][0]]
            self.data = self.data[match.regs[0][1]:]
            if len(cmd) < 3:
                continue
            try:
                tcode = TCodeCommand.parse_command(cmd)
                if self.do_auto_expand:
                    interval, alpha, beta = self.expander.expand(tcode)
                    for i, a, b in zip(interval, alpha, beta):
                        self.new_tcode_command.emit(TCodeCommand('L0', a / 2 + 0.5, i))
                        self.new_tcode_command.emit(TCodeCommand('L1', b / 2 + 0.5, i))
                else:
                    self.new_tcode_command.emit(tcode)
            except InvalidTCodeException as e:
                pass

    new_tcode_command = QtCore.pyqtSignal(TCodeCommand)
