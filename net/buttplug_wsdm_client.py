import json

from PyQt5 import QtCore, QtWebSockets
from PyQt5.QtCore import QSettings, QUrl

from net.serialproxy import FunscriptExpander
from net.tcode import TCodeCommand, InvalidTCodeException
from qt_ui.preferencesdialog import KEY_BUTTPLUG_WSDM_ENABLED, KEY_BUTTPLUG_WSDM_ADDRESS, KEY_BUTTPLUG_WSDM_AUTO_EXPAND

DEVICE_ADDRESS = "00000000"


class ButtplugWsdmClient(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.connections = []

        settings = QSettings()
        enabled = settings.value(KEY_BUTTPLUG_WSDM_ENABLED, False, bool)
        address = settings.value(KEY_BUTTPLUG_WSDM_ADDRESS, 'ws://127.0.0.1:54817', str)
        self.do_auto_expand = settings.value(KEY_BUTTPLUG_WSDM_AUTO_EXPAND, True, bool)
        self.expander = FunscriptExpander()

        if not enabled:
            print("Not starting buttplug WSDM client because disabled in settings.")
            return

        self.client = QtWebSockets.QWebSocket("restim")
        self.client.error.connect(self.error)
        self.client.connected.connect(self.connected)
        self.client.textMessageReceived.connect(self.textMessageReceived)
        self.client.binaryMessageReceived.connect(self.binaryMessageReceived)
        self.client.open(QUrl(address))

    def error(self):
        print('buttplug WSDM error:', self.client.errorString())

    def connected(self):
        print('Connected to buttplug WSDM.')
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

    new_tcode_command = QtCore.pyqtSignal(TCodeCommand)
