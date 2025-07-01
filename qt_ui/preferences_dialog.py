import functools

from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QDialog, QAbstractButton, QDialogButtonBox, QAbstractItemView, QHeaderView, QComboBox

from qt_ui.preferences_dialog_ui import Ui_PreferencesDialog
from qt_ui.models.funscript_kit import FunscriptKitModel
import qt_ui.settings

import sounddevice as sd


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.tabWidget.setCurrentIndex(0)

        self.loadSettings()

        self.audio_api.currentIndexChanged.connect(self.repopulate_audio_devices)
        self.audio_output_device.currentIndexChanged.connect(self.refresh_audio_device_info)
        self.buttonBox.clicked.connect(self.buttonClicked)

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

        # focstim/neostim reload serial devices
        self.refresh_serial_devices.clicked.connect(self.repopulate_serial_devices)
        self.neostim_refresh_serial_devices.clicked.connect(self.repopulate_serial_devices)

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
        self.gb_websocket_server.setChecked(qt_ui.settings.websocket_enabled.get())
        self.websocket_port.setValue(qt_ui.settings.websocket_port.get())
        self.websocket_localhost_only.setChecked(qt_ui.settings.websocket_localhost_only.get())

        self.gb_tcp_server.setChecked(qt_ui.settings.tcp_enabled.get())
        self.tcp_port.setValue(qt_ui.settings.tcp_port.get())
        self.tcp_localhost_only.setChecked(qt_ui.settings.tcp_localhost_only.get())

        self.gb_udp_server.setChecked(qt_ui.settings.udp_enabled.get())
        self.udp_port.setValue(qt_ui.settings.udp_port.get())
        self.udp_localhost_only.setChecked(qt_ui.settings.udp_localhost_only.get())

        self.gb_serial.setChecked(qt_ui.settings.serial_enabled.get())
        self.serial_port.setText(qt_ui.settings.serial_port.get())
        self.serial_auto_expand.setChecked(qt_ui.settings.serial_auto_expand.get())

        self.gb_buttplug_wsdm.setChecked(qt_ui.settings.buttplug_wsdm_enabled.get())
        self.buttplug_wsdm_address.setText(qt_ui.settings.buttplug_wsdm_address.get())
        self.buttplug_wsdm_auto_expand.setChecked(qt_ui.settings.buttplug_wsdm_auto_expand.get())

        # audio settings
        hostapi_name = qt_ui.settings.audio_api.get()
        if not hostapi_name:
            hostapi_name = sd.query_hostapis(sd.default.hostapi)['name']

        self.audio_api.clear()
        for host_api in sd.query_hostapis():
            self.audio_api.addItem(host_api['name'])
            if host_api['name'] == hostapi_name:
                self.audio_api.setCurrentIndex(self.audio_api.count()-1)

        self.repopulate_audio_devices()

        self.audio_latency.setCurrentText(qt_ui.settings.audio_latency.get())

        # focstim settings
        self.repopulate_serial_devices()
        self.focstim_port.setCurrentIndex(self.focstim_port.findData(qt_ui.settings.focstim_serial_port.get()))
        self.focstim_use_teleplot.setChecked(qt_ui.settings.focstim_use_teleplot.get())
        self.focstim_teleplot_prefix.setText(qt_ui.settings.focstim_teleplot_prefix.get())
        self.focstim_dump_notifications.setChecked(qt_ui.settings.focstim_dump_notifications_to_file.get())

        # neostim settings
        self.neostim_port.setCurrentIndex(self.neostim_port.findData(qt_ui.settings.neostim_serial_port.get()))

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
        default_audio_output_device_name = qt_ui.settings.audio_output_device.get()
        if not default_audio_output_device_name:
            default_audio_output_device_name = sd.query_devices(sd.default.device[1])['name']
        api_index = self.audio_api.currentIndex()
        for device in sd.query_devices():
            if (
                    device['hostapi'] == api_index and
                    device['max_output_channels'] >= 2
            ):
                self.audio_output_device.addItem(device['name'])
                if device['name'] == default_audio_output_device_name:
                    self.audio_output_device.setCurrentIndex(self.audio_output_device.count() - 1)

    def repopulate_serial_devices(self):
        def refresh(control: QComboBox, setting: qt_ui.settings.Setting):
            selected_port_name = control.currentData()
            if selected_port_name is None:
                selected_port_name = setting.get()

            control.clear()
            for port in QSerialPortInfo.availablePorts():
                control.addItem(
                    f"{port.portName()} {port.description()}",
                    port.portName()
                )

            if selected_port_name:
                index = control.findData(selected_port_name)
                if index != -1:
                    control.setCurrentIndex(index)
                else:
                    # if the port is no longer available, create a dummy port and add that.
                    control.addItem(
                        f"{selected_port_name}",
                        selected_port_name
                    )
                    control.setCurrentIndex(self.focstim_port.count() - 1)

        refresh(self.focstim_port, qt_ui.settings.focstim_serial_port)
        refresh(self.neostim_port, qt_ui.settings.neostim_serial_port)


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
        qt_ui.settings.websocket_enabled.set(self.gb_websocket_server.isChecked())
        qt_ui.settings.websocket_port.set(self.websocket_port.value())
        qt_ui.settings.websocket_localhost_only.set(self.websocket_localhost_only.isChecked())

        qt_ui.settings.tcp_enabled.set(self.gb_tcp_server.isChecked())
        qt_ui.settings.tcp_port.set(self.tcp_port.value())
        qt_ui.settings.tcp_localhost_only.set(self.tcp_localhost_only.isChecked())

        qt_ui.settings.udp_enabled.set(self.gb_udp_server.isChecked())
        qt_ui.settings.udp_port.set(self.udp_port.value())
        qt_ui.settings.udp_localhost_only.set(self.udp_localhost_only.isChecked())

        qt_ui.settings.serial_enabled.set(self.gb_serial.isChecked())
        qt_ui.settings.serial_port.set(self.serial_port.text())
        qt_ui.settings.serial_auto_expand.set(self.serial_auto_expand.isChecked())

        qt_ui.settings.buttplug_wsdm_enabled.set(self.gb_buttplug_wsdm.isChecked())
        qt_ui.settings.buttplug_wsdm_address.set(self.buttplug_wsdm_address.text())
        qt_ui.settings.buttplug_wsdm_auto_expand.set(self.buttplug_wsdm_auto_expand.isChecked())

        # audio devices
        qt_ui.settings.audio_api.set(self.audio_api.currentText())
        qt_ui.settings.audio_output_device.set(self.audio_output_device.currentText())
        qt_ui.settings.audio_latency.set(self.audio_latency.currentText())

        # focstim
        qt_ui.settings.focstim_serial_port.set(str(self.focstim_port.currentData()))
        qt_ui.settings.focstim_use_teleplot.set(self.focstim_use_teleplot.isChecked())
        qt_ui.settings.focstim_teleplot_prefix.set(self.focstim_teleplot_prefix.text())
        qt_ui.settings.focstim_dump_notifications_to_file.set(self.focstim_dump_notifications.isChecked())

        # neoStim
        qt_ui.settings.neostim_serial_port.set(str(self.neostim_port.currentData()))

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

    def funscript_reset_defaults(self):
        self.tableView.model().reset_to_defaults()
