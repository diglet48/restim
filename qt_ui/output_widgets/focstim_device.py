import logging
import socket

from PyQt5.Qt import QObject
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QIODevice, QTimer

from net.tcode import TCodeCommand
from qt_ui.output_widgets.output_device import OutputDevice
from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm

logger = logging.getLogger('restim.focstim')

teleplotAddr = ("127.0.0.1", 47269)

FOCSTIM_BOOT_MARKER = b'Device ready. Awaiting DSTART.'
FOCSTIM_VERSION_STRING = b'FOC-Stim 0.2'


class FOCStimDevice(QObject, OutputDevice):
    def __init__(self):
        super().__init__()
        self.port = None
        self.algorithm = None
        self.old_dict = {}
        self.boot_marker_detected = False
        self.version_string_detected = False
        self.sock = None

        self.update_timer = QTimer()
        self.update_timer.setInterval(int(1000 / 60))
        self.update_timer.timeout.connect(self.transmit_dirty_params)

        self.ping_timer = QTimer()
        self.ping_timer.setInterval(1000)
        self.ping_timer.timeout.connect(self.send_ping)

    def start(self, com_port, use_teleplot, algorithm: RemoteGenerationAlgorithm):
        self.algorithm = algorithm
        if use_teleplot:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.port = QSerialPort(self)
        self.port.setPortName(com_port)
        self.port.setBaudRate(115200)
        self.port.readyRead.connect(self.new_serial_data)
        success = self.port.open(QIODevice.ReadWrite)
        if success:
            logger.info(f"Successfully opened: {self.port.portName()}")
            self.stop_device()
            self.request_version_string()
        else:
            logger.error(f"Unable to open serial port: {self.port.errorString()}")

    def stop(self):
        self.stop_device()
        self.port.flush()
        self.port.close()

    def is_connected_and_running(self) -> bool:
        return self.port and self.port.isOpen()

    def request_version_string(self):
        self.port.write(b'D0\r\n')

    def start_device(self):
        self.old_dict = {}
        self.port.write(b'\r\n')
        self.transmit_dirty_params(0)    # re-transmit all params.
        self.port.write(b'DSTART\r\n')
        self.ping_timer.start()
        self.update_timer.start()

    def stop_device(self):
        self.port.write(b'DSTOP\r\n')
        self.ping_timer.stop()
        self.update_timer.stop()

    def send_ping(self):
        self.port.write(b'DPING\r\n')

    def new_serial_data(self):
        while self.port.canReadLine():
            line = bytes(self.port.readLine()).rstrip()
            if len(line) == 0:
                continue

            if line.startswith(b'$') and line.count(b'$') == 1:
                parts = line[1:].split(b' ')
                self.sock.sendto(b'\r\n'.join(parts), teleplotAddr)
                break

            logger.info(line.decode('utf-8'))
            if line == FOCSTIM_BOOT_MARKER:
                self.boot_marker_detected = True
                self.version_string_detected = False
                self.request_version_string()

            if line == FOCSTIM_VERSION_STRING:
                if not self.version_string_detected:
                    self.version_string_detected = True
                    self.start_device()

    def transmit_dirty_params(self, interval=30):
        new_dict = self.algorithm.parameter_dict()

        # send only dirty values
        commands = []
        for id, value in new_dict.items():
            if id not in self.old_dict or value != self.old_dict[id]:
                commands.append(TCodeCommand(id, value, interval))

        if len(commands):
            self.push_commands(commands)
        self.old_dict = new_dict

    def push_commands(self, commands: list[TCodeCommand]):
        buf = b'\r\n'.join([c.format_cmd().encode('ascii') for c in commands]) + b'\r\n'
        bytes_written = self.port.write(buf)
        if len(buf) != bytes_written:
            logger.error(f"Attempting to write {len(buf)} bytes, but only wrote {bytes_written}")
            self.port.close()
