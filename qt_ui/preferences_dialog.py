import functools

from PyQt5.QtCore import QSettings, QModelIndex
from PyQt5.QtWidgets import QDialog, QAbstractButton, QDialogButtonBox, QAbstractItemView, QHeaderView

from qt_ui.preferences_dialog_ui import Ui_PreferencesDialog
from qt_ui.audio_test_dialog import AudioTestDialog
from qt_ui.models.funscript_kit import FunscriptKitModel
import qt_ui.settings

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
KEY_SERIAL_ENABLED = "network/serial-enabled"
KEY_SERIAL_PORT = "network/serial-port"
KEY_SERIAL_AUTO_EXPAND = "network/serial-auto-expand"
KEY_BUTTPLUG_WSDM_ENABLED = "network/buttplug-wsdm-enabled"
KEY_BUTTPLUG_WSDM_ADDRESS = "network/buttplug-wsdm-address"
KEY_BUTTPLUG_WSDM_AUTO_EXPAND = "network/buttplug-wsdm-auto-expand"

KEY_AUDIO_API = "audio/api-name"
KEY_AUDIO_OUTPUT_DEVICE = "audio/device-name"
KEY_AUDIO_LATENCY = "audio/latency"


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.tabWidget.setCurrentIndex(0)

        self.settings = QSettings()
        self.loadSettings()

        self.audio_api.currentIndexChanged.connect(self.repopulate_audio_devices)
        self.audio_output_device.currentIndexChanged.connect(self.refresh_audio_device_info)
        self.buttonBox.clicked.connect(self.buttonClicked)
        self.commandLinkButton.clicked.connect(self.open_test_audio_dialog)

        # funscript mapping
        self.button_funscript_reset_defaults.clicked.connect(self.funscript_reset_defaults)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tableView.setModel(FunscriptKitModel.load_from_settings())
        self.tableView.setEditTriggers(
            # QAbstractItemView.AllEditTriggers
            QAbstractItemView.CurrentChanged |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )

        # media sync reset buttons
        self.mpc_reload.clicked.connect(
            functools.partial(self.mpc_address.setText, qt_ui.settings.media_sync_mpc_address.default_value)
        )
        self.heresphere_reload.clicked.connect(
            functools.partial(self.heresphere_address.setText, qt_ui.settings.media_sync_heresphere_address.default_value)
        )
        self.vlc_reload.clicked.connect(
            functools.partial(self.vlc_address.setText, qt_ui.settings.media_sync_vlc_address.default_value)
        )
        self.kodi_reload.clicked.connect(
            functools.partial(self.kodi_address.setText, qt_ui.settings.media_sync_kodi_address.default_value)
        )

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

        self.gb_serial.setChecked(self.settings.value(KEY_SERIAL_ENABLED, False, bool))
        self.serial_port.setText(self.settings.value(KEY_SERIAL_PORT, "COM20", str))
        self.serial_auto_expand.setChecked(self.settings.value(KEY_SERIAL_AUTO_EXPAND, True, bool))

        self.gb_buttplug_wsdm.setChecked(self.settings.value(KEY_BUTTPLUG_WSDM_ENABLED, False, bool))
        self.buttplug_wsdm_address.setText(self.settings.value(KEY_BUTTPLUG_WSDM_ADDRESS, "ws://127.0.0.1:54817", str))
        self.buttplug_wsdm_auto_expand.setChecked(self.settings.value(KEY_BUTTPLUG_WSDM_AUTO_EXPAND, True, bool))

        # audio settings
        hostapi_name = self.settings.value(KEY_AUDIO_API, sd.query_hostapis(sd.default.hostapi)['name'])
        self.audio_api.clear()
        for host_api in sd.query_hostapis():
            self.audio_api.addItem(host_api['name'])
            if host_api['name'] == hostapi_name:
                self.audio_api.setCurrentIndex(self.audio_api.count()-1)

        self.repopulate_audio_devices()

        self.audio_latency.setCurrentText(self.settings.value(KEY_AUDIO_LATENCY, 'high'))
        self.channel_count.setValue(qt_ui.settings.audio_channel_count.get())
        self.channel_map.setText(qt_ui.settings.audio_channel_map.get())

        # media sync settings
        self.mpc_address.setText(qt_ui.settings.media_sync_mpc_address.get())
        self.heresphere_address.setText(qt_ui.settings.media_sync_heresphere_address.get())
        self.vlc_address.setText(qt_ui.settings.media_sync_vlc_address.get())
        self.vlc_username.setText(qt_ui.settings.media_sync_vlc_username.get())
        self.vlc_password.setText(qt_ui.settings.media_sync_vlc_password.get())
        self.kodi_address.setText(qt_ui.settings.media_sync_kodi_address.get())

        # display settings

        self.display_fps.setValue(int(qt_ui.settings.display_fps.get()))
        self.display_latency_ms.setValue(qt_ui.settings.display_latency.get())

        # funscript mapping
        self.tableView.setModel(FunscriptKitModel.load_from_settings())

    def repopulate_audio_devices(self):
        self.audio_output_device.clear()
        default_audio_output_device_name = self.settings.value(KEY_AUDIO_OUTPUT_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        api_index = self.audio_api.currentIndex()
        for device in sd.query_devices():
            if (
                    device['hostapi'] == api_index and
                    device['max_output_channels'] >= 2
            ):
                self.audio_output_device.addItem(device['name'])
                if device['name'] == default_audio_output_device_name:
                    self.audio_output_device.setCurrentIndex(self.audio_output_device.count() - 1)

    def refresh_audio_device_info(self):
        api_index = self.audio_api.currentIndex()
        device_name = self.audio_output_device.currentText()
        for device in sd.query_devices():
            if device['hostapi'] == api_index and device['name'] == device_name:
                out_channels = device['max_output_channels']
                samplerate = device['default_samplerate']
                self.audio_info.setText(f"channels: {out_channels}, samplerate: {samplerate}")

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

        self.settings.setValue(KEY_SERIAL_ENABLED, self.gb_serial.isChecked())
        self.settings.setValue(KEY_SERIAL_PORT, self.serial_port.text())
        self.settings.setValue(KEY_SERIAL_AUTO_EXPAND, self.serial_auto_expand.isChecked())

        self.settings.setValue(KEY_BUTTPLUG_WSDM_ENABLED, self.gb_buttplug_wsdm.isChecked())
        self.settings.setValue(KEY_BUTTPLUG_WSDM_ADDRESS, self.buttplug_wsdm_address.text())
        self.settings.setValue(KEY_BUTTPLUG_WSDM_AUTO_EXPAND, self.buttplug_wsdm_auto_expand.isChecked())

        # audio devices
        self.settings.setValue(KEY_AUDIO_API, self.audio_api.currentText())
        self.settings.setValue(KEY_AUDIO_OUTPUT_DEVICE, self.audio_output_device.currentText())
        self.settings.setValue(KEY_AUDIO_LATENCY, self.audio_latency.currentText())
        qt_ui.settings.audio_channel_count.set(self.channel_count.value())
        qt_ui.settings.audio_channel_map.set(self.channel_map.text())

        # media sync settings
        qt_ui.settings.media_sync_mpc_address.set(self.mpc_address.text())
        qt_ui.settings.media_sync_heresphere_address.set(self.heresphere_address.text())
        qt_ui.settings.media_sync_vlc_address.set(self.vlc_address.text())
        qt_ui.settings.media_sync_vlc_username.set(self.vlc_username.text())
        qt_ui.settings.media_sync_vlc_password.set(self.vlc_password.text())
        qt_ui.settings.media_sync_kodi_address.set(self.kodi_address.text())

        # display
        qt_ui.settings.display_fps.set(self.display_fps.value())
        qt_ui.settings.display_latency.set(self.display_latency_ms.value())

        # funscript mapping
        self.tableView.model().save_to_settings()

    def open_test_audio_dialog(self):
        api_index = self.audio_api.currentIndex()
        device_name = self.audio_output_device.currentText()
        device_index = -1
        for device in sd.query_devices():
            if device['hostapi'] == api_index and device['name'] == device_name:
                device_index = device['index']

        dialog = AudioTestDialog(self, device_index)
        dialog.exec()

    def funscript_reset_defaults(self):
        self.tableView.model().reset_to_defaults()
