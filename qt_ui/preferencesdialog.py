from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QAbstractButton, QDialogButtonBox

from qt_ui.preferences_dialog_ui import Ui_PreferencesDialog

import sounddevice as sd

KEY_WEBSOCKET_ENABLED = "network/websocket-enabled"
KEY_WEBSOCKET_PORT = "network/websocket-port"
KEY_WEBSOCKET_LOCALHOST_ONLY = "network/websocket-localhost-only"
KEY_TCP_ENABLED = "network/tcp-enabled"
KEY_TCP_PORT = "network/tcp-port"
KEY_TCP_LOCALHOST_ONLY = "network/tcp-localhost-only"
KEY_UDP_ENABLED = "network/udp-enabled"
KEY_UDP_PORT = "network/udp-port"
KEY_UDP_LOCALHOST_ONLY = "network/udp-localhost-only"

KEY_AUDIO_API = "audio/api-name"
KEY_AUDIO_DEVICE = "audio/device-name"
KEY_AUDIO_LATENCY = "audio/latency"


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.settings = QSettings()
        self.loadSettings()

        self.audio_api.currentIndexChanged.connect(self.repopulate_audio_devices)
        self.buttonBox.clicked.connect(self.buttonClicked)
        
    def exec(self):
        self.loadSettings()
        return super(PreferencesDialog, self).exec()

    def buttonClicked(self, button: QAbstractButton):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.AcceptRole:
            self.saveSettings()
            self.accept()
        if role == QDialogButtonBox.ApplyRole:
            self.saveSettings()
        if role == QDialogButtonBox.RejectRole:
            self.reject()

    def loadSettings(self):
        # network settings
        self.gb_websocket_server.setChecked(self.settings.value(KEY_WEBSOCKET_ENABLED, True, bool))
        self.websocket_port.setValue(self.settings.value(KEY_WEBSOCKET_PORT, 12346, int))
        self.websocket_localhost_only.setChecked(self.settings.value(KEY_WEBSOCKET_LOCALHOST_ONLY, False, bool))

        self.gb_tcp_server.setChecked(self.settings.value(KEY_TCP_ENABLED, True, bool))
        self.tcp_port.setValue(self.settings.value(KEY_TCP_PORT, 12347, int))
        self.tcp_localhost_only.setChecked(self.settings.value(KEY_TCP_LOCALHOST_ONLY, False, bool))

        self.gb_udp_server.setChecked(self.settings.value(KEY_UDP_ENABLED, True, bool))
        self.udp_port.setValue(self.settings.value(KEY_UDP_PORT, 12347, int))
        self.udp_localhost_only.setChecked(self.settings.value(KEY_UDP_LOCALHOST_ONLY, False, bool))

        # audio settings
        hostapi_name = self.settings.value(KEY_AUDIO_API, sd.query_hostapis(sd.default.hostapi)['name'])
        self.audio_api.clear()
        for host_api in sd.query_hostapis():
            self.audio_api.addItem(host_api['name'])
            if host_api['name'] == hostapi_name:
                self.audio_api.setCurrentIndex(self.audio_api.count()-1)

        self.repopulate_audio_devices()

        self.audio_latency.setCurrentText(self.settings.value(KEY_AUDIO_LATENCY, 'high'))

        # display settings

    def repopulate_audio_devices(self):
        self.audio_device.clear()
        default_audio_device_name = self.settings.value(KEY_AUDIO_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        api_index = self.audio_api.currentIndex()
        for device in sd.query_devices():
            if (
                    device['hostapi'] == api_index and
                    device['max_output_channels'] >= 2
            ):
                self.audio_device.addItem(device['name'])
                if device['name'] == default_audio_device_name:
                    self.audio_device.setCurrentIndex(self.audio_device.count() - 1)

    def saveSettings(self):
        # network
        self.settings.setValue(KEY_WEBSOCKET_ENABLED, self.gb_websocket_server.isChecked())
        self.settings.setValue(KEY_WEBSOCKET_PORT, self.websocket_port.value())
        self.settings.setValue(KEY_WEBSOCKET_LOCALHOST_ONLY, self.websocket_localhost_only.isChecked())

        self.settings.setValue(KEY_TCP_ENABLED, self.gb_tcp_server.isChecked())
        self.settings.setValue(KEY_TCP_PORT, self.tcp_port.value())
        self.settings.setValue(KEY_TCP_LOCALHOST_ONLY, self.tcp_localhost_only.isChecked())

        self.settings.setValue(KEY_UDP_ENABLED, self.gb_udp_server.isChecked())
        self.settings.setValue(KEY_UDP_PORT, self.udp_port.value())
        self.settings.setValue(KEY_UDP_LOCALHOST_ONLY, self.udp_localhost_only.isChecked())

        # audio devices
        self.settings.setValue(KEY_AUDIO_API, self.audio_api.currentText())
        self.settings.setValue(KEY_AUDIO_DEVICE, self.audio_device.currentText())
        self.settings.setValue(KEY_AUDIO_LATENCY, self.audio_latency.currentText())




