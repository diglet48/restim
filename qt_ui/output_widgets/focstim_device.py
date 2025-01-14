import logging
import socket
from dataclasses import dataclass
import re

from PyQt5.Qt import QObject
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import QIODevice, QTimer

import qt_ui.settings
from net.tcode import TCodeCommand
from qt_ui.output_widgets.output_device import OutputDevice
from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm

logger = logging.getLogger('restim.focstim')

teleplotAddr = ("127.0.0.1", 47269)

FOCSTIM_VERSION_STRING = '0.4'


@dataclass
class FocStatus:
    booted: bool
    vbus: bool
    estop: bool
    playing: bool

    @staticmethod
    def from_bytes(b):
        try:
            match = re.match(b'status: (\\d+)', b)
            status = int(match[1])
            return FocStatus(
                booted=bool(status & 0x01),
                vbus=bool(status & 0x02),
                estop=bool(status & 0x04),
                playing=bool(status & 0x08),
            )
        except TypeError:
            return None

@dataclass
class FocVersion:
    version: str

    @staticmethod
    def from_bytes(b):
        match = re.match(b'version: FOC-Stim (.+)$', b)
        try:
            return FocVersion(match[1].decode('ascii'))
        except (UnicodeDecodeError, TypeError):
            return None


class FOCStimDevice(QObject, OutputDevice):
    def __init__(self):
        super().__init__()
        self.port = None
        self.algorithm = None
        self.old_dict = {}
        self.sock = None
        self.version_string_detected = False
        self.under_voltage_detected = False
        self.status = FocStatus(False, False, False, False)
        self.teleplot_prefix = qt_ui.settings.focstim_teleplot_prefix.get().encode('ascii')

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

    def handle_version_message(self, version: FocVersion):
        if version.version == FOCSTIM_VERSION_STRING:
            if not self.version_string_detected:
                self.version_string_detected = True
                if not self.under_voltage_detected:
                    self.start_device()
        else:
            logger.warning(f'incompatible FOC-Stim version: {version.version}')

    def handle_status_message(self, status: FocStatus):
        # device boot
        if (self.status.booted, status.booted) == (False, True):
            self.request_version_string()

        # device restart, request version string again.
        if (self.status.booted, status.booted) == (True, False):
            self.version_string_detected = False
            self.request_version_string()

        # device running, but vbus dropped out.
        # force user to stop/start in restim to continue playing.
        if (self.status.booted, self.status.vbus, status.booted, status.vbus) == (True, True, True, False):
            self.under_voltage_detected = True

        # device running, vbus just came online.
        # start signal
        if (self.status.booted, self.status.vbus, status.booted, status.vbus) == (True, False, True, True):
            if self.version_string_detected:
                if not self.under_voltage_detected:
                    self.start_device()

        self.status = status

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
        self.old_dict = dict()  # re-transmit all params every second to handle packet loss
        self.port.write(b'DPING\r\n')

    def new_serial_data(self):
        while self.port.canReadLine():
            line = bytes(self.port.readLine()).rstrip()
            if len(line) == 0:
                continue

            # line is teleplot message?
            if line.startswith(b'$') and line.count(b'$') == 1:
                if self.sock is not None:
                    parts = line[1:].split(b' ')
                    parts = [self.teleplot_prefix + part for part in parts]
                    try:
                        self.sock.sendto(b'\r\n'.join(parts), teleplotAddr)
                    except OSError:
                        pass
                break

            # line is status message?
            status = FocStatus.from_bytes(line)
            if status is not None:
                self.handle_status_message(status)
                break

            # line is version message?
            version = FocVersion.from_bytes(line)
            if version is not None:
                self.handle_version_message(version)
                break

            # not any known message, just log.
            try:
                logger.info(line.decode('utf-8'))
            except UnicodeDecodeError:
                pass

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
