import json
import logging

from PyQt5 import QtCore, QtWebSockets
from PyQt5.QtCore import QSettings, QUrl, QTimer
from PyQt5.QtNetwork import QAbstractSocket

from net.serialproxy import FunscriptExpander
from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui.preferences_dialog import KEY_BUTTPLUG_WSDM_ENABLED, KEY_BUTTPLUG_WSDM_ADDRESS, KEY_BUTTPLUG_WSDM_AUTO_EXPAND

logger = logging.getLogger('restim.buttplug')

DEVICE_ADDRESS = "00000000"


class ButtplugWsdmClient(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.connections = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.reconnect_timeout)
        self.timer.start(1000)

        self.retry_count = 0

        settings = QSettings()
        self.enabled = settings.value(KEY_BUTTPLUG_WSDM_ENABLED, False, bool)
        self.address = settings.value(KEY_BUTTPLUG_WSDM_ADDRESS, 'ws://127.0.0.1:54817', str)
        self.do_auto_expand = settings.value(KEY_BUTTPLUG_WSDM_AUTO_EXPAND, True, bool)

        self.expander = FunscriptExpander()

        self.client = QtWebSockets.QWebSocket("restim")
        self.client.error.connect(self.error)
        self.client.connected.connect(self.connected)
        self.client.textMessageReceived.connect(self.textMessageReceived)
        self.client.binaryMessageReceived.connect(self.binaryMessageReceived)


    def reconnect_timeout(self):
        self.timer.setInterval(10 * 1000)
        if self.enabled and self.client.state() == QAbstractSocket.UnconnectedState:
            self.retry_count += 1
            # avoid log spam
            if self.retry_count <= 1:
                logger.info(f'attempting to connect to buttplug WSDM')
            self.client.open(QUrl(self.address))

    def error(self):
        # avoid log spam
        if self.client.error() != QAbstractSocket.ConnectionRefusedError or self.retry_count <= 1:
            logger.error(f'buttplug error: {self.client.errorString()}')

    def connected(self):
        logger.info('Connected to buttplug.')
        self.client.sendTextMessage(
                json.dumps({"identifier": "restim", "address": DEVICE_ADDRESS, "version": 0})
        )

    def textMessageReceived(self, msg):
        pass

    def binaryMessageReceived(self, msg):
        try:
            tcode = TCodeCommand.parse_command(bytes(msg))
            if self.do_auto_expand:
                interval, alpha, beta = self.expander.expand(tcode)
                for i, a, b in zip(interval, alpha, beta):
                    self.new_tcode_command.emit(TCodeCommand('L0', a / 2 + 0.5, i))
                    self.new_tcode_command.emit(TCodeCommand('L1', b / 2 + 0.5, i))
            else:
                self.new_tcode_command.emit(tcode)
        except InvalidTCodeException:
            pass

    def refreshSettings(self):
        self.retry_count = 0
        settings = QSettings()
        self.enabled = settings.value(KEY_BUTTPLUG_WSDM_ENABLED, False, bool)
        self.address = settings.value(KEY_BUTTPLUG_WSDM_ADDRESS, 'ws://127.0.0.1:54817', str)
        self.do_auto_expand = settings.value(KEY_BUTTPLUG_WSDM_AUTO_EXPAND, True, bool)

        self.timer.setInterval(10)

    new_tcode_command = QtCore.pyqtSignal(TCodeCommand)
