import functools
import logging

import google.protobuf.text_format
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QDialog, QAbstractButton, QDialogButtonBox, QAbstractItemView, QHeaderView, QComboBox, QTableWidgetItem, QCheckBox, QApplication
from PySide6.QtCore import Qt, Signal, QTimer

from qt_ui.preferences_dialog_ui import Ui_PreferencesDialog
from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.services.pattern_service import PatternControlService
from device.focstim.helpers import WifiUploadHelper, GrabIpHelper
import qt_ui.settings

import sounddevice as sd

logger = logging.getLogger('restim.preferences')


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.tabWidget.setCurrentIndex(0)

        # Initialize pattern service and cache pattern data immediately
        self.pattern_service = PatternControlService()
        self._cached_patterns = None
        self._cache_patterns_data()

        # Setup AS5311 Sensor Data Sharing UI before loading settings
        self.setup_as5311_sensor_ui()

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

        # patterns setup - do this immediately during initialization
        self.setup_patterns_tab()

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
        self.focstim_refresh_serial_devices.clicked.connect(self.repopulate_serial_devices)
        self.neostim_refresh_serial_devices.clicked.connect(self.repopulate_serial_devices)

        # focstim buttons
        self.focstim_read_ip.clicked.connect(self.read_focstim_ip)
        self.focstim_sync.clicked.connect(self.upload_focstim_ssid)

    def setup_as5311_sensor_ui(self):
        """Setup AS5311 Sensor Data Sharing UI controls"""
        from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QRadioButton, QLabel, QSpinBox, QLineEdit, QHBoxLayout, QCheckBox

        # Create group box for AS5311 sensor data settings
        self.as5311_groupbox = QGroupBox("AS5311 Sensor Data", self.tab_foc)
        layout = QVBoxLayout(self.as5311_groupbox)

        # Radio button 1: From the box (Default)
        self.as5311_radio_from_box = QRadioButton("From the box (Default)")
        layout.addWidget(self.as5311_radio_from_box)

        # Sub-options for "From the box"
        self.as5311_serve_checkbox = QCheckBox("Serve data for other instances")
        self.as5311_serve_checkbox.setContentsMargins(20, 0, 0, 0)
        layout.addWidget(self.as5311_serve_checkbox)

        # Port spinbox for serving
        port_layout = QHBoxLayout()
        port_layout.addSpacing(40)
        port_label = QLabel("Port:")
        self.as5311_serve_port = QSpinBox()
        self.as5311_serve_port.setMinimum(1024)
        self.as5311_serve_port.setMaximum(65535)
        self.as5311_serve_port.setValue(55534)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.as5311_serve_port)
        port_layout.addStretch()
        layout.addLayout(port_layout)

        # Radio button 2: From the server
        self.as5311_radio_from_server = QRadioButton("From the server")
        layout.addWidget(self.as5311_radio_from_server)

        # Sub-options for "From the server" - using FormLayout for alignment
        from PySide6.QtWidgets import QFormLayout
        server_form_layout = QFormLayout()
        server_form_layout.setContentsMargins(40, 0, 0, 0)

        # IP address
        self.as5311_server_address = QLineEdit()
        self.as5311_server_address.setText("127.0.0.1")
        server_form_layout.addRow("IP:", self.as5311_server_address)

        # Port
        self.as5311_server_port = QSpinBox()
        self.as5311_server_port.setMinimum(1024)
        self.as5311_server_port.setMaximum(65535)
        self.as5311_server_port.setValue(55534)
        server_form_layout.addRow("Port:", self.as5311_server_port)

        layout.addLayout(server_form_layout)

        # Add to the FOC-Stim tab layout
        self.verticalLayout_5.addWidget(self.as5311_groupbox)

        # Connect signals for enabling/disabling controls
        self.as5311_radio_from_box.toggled.connect(self.update_as5311_controls)
        self.as5311_radio_from_server.toggled.connect(self.update_as5311_controls)

        # Set default selection
        self.as5311_radio_from_box.setChecked(True)

    def update_as5311_controls(self):
        """Update AS5311 control states based on radio button selection"""
        from_box = self.as5311_radio_from_box.isChecked()
        from_server = self.as5311_radio_from_server.isChecked()

        # Enable/disable "From the box" sub-options
        self.as5311_serve_checkbox.setEnabled(from_box)
        self.as5311_serve_port.setEnabled(from_box)

        # Enable/disable "From the server" sub-options
        self.as5311_server_address.setEnabled(from_server)
        self.as5311_server_port.setEnabled(from_server)

    def _cache_patterns_data(self):
        """Cache pattern data at startup to avoid late discovery issues"""
        try:
            # Pre-load all pattern data immediately
            self._cached_patterns = self.pattern_service.get_available_patterns(respect_user_preferences=False)
        except Exception as e:
            self._cached_patterns = []

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

        self.focstim_radio_serial.setChecked(qt_ui.settings.focstim_communication_serial.get())
        self.focstim_radio_wifi.setChecked(qt_ui.settings.focstim_communication_wifi.get())
        self.focstim_ssid.setText(qt_ui.settings.focstim_ssid.get())
        self.focstim_password.setText(qt_ui.settings.focstim_password.get())
        self.focstim_ip.setText(qt_ui.settings.focstim_ip.get())

        # AS5311 sensor data settings
        as5311_source = qt_ui.settings.focstim_as5311_source.get()
        if as5311_source == 0:
            self.as5311_radio_from_box.setChecked(True)
        else:
            self.as5311_radio_from_server.setChecked(True)
        self.as5311_serve_checkbox.setChecked(qt_ui.settings.focstim_as5311_serve.get())
        self.as5311_serve_port.setValue(qt_ui.settings.focstim_as5311_serve_port.get())
        self.as5311_server_address.setText(qt_ui.settings.focstim_as5311_server_address.get())
        self.as5311_server_port.setValue(qt_ui.settings.focstim_as5311_server_port.get())
        self.update_as5311_controls()

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
        
        # refresh pattern preferences (just reload checkboxes from settings)
        self.refresh_pattern_preferences()

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

    def upload_focstim_ssid(self):
        helper = WifiUploadHelper()
        fut = helper.upload(
            self.focstim_port.currentData(),
            self.focstim_ssid.text().encode("utf-8"),
            self.focstim_password.text().encode("utf-8"),
        )
        if fut is None:
            return
        self.focstim_sync.setEnabled(False)

        def timeout():
            helper.close()
            logger.error("timeout uploading wifi settings")
            self.focstim_sync.setEnabled(True)

        def result(result):
            helper.close()
            s = google.protobuf.text_format.MessageToString(result, as_one_line=True)
            logger.info(f"response: {s}")
            self.focstim_sync.setEnabled(True)

        fut.on_timeout.connect(timeout)
        fut.on_result.connect(result)

    def read_focstim_ip(self):
        helper = GrabIpHelper()
        fut = helper.get_ip(
            self.focstim_port.currentData(),
        )
        if fut is None:
            return
        self.focstim_read_ip.setEnabled(False)

        def timeout():
            helper.close()
            logger.error("timeout grabbing IP")
            self.focstim_read_ip.setEnabled(True)

        def result(result):
            helper.close()
            s = google.protobuf.text_format.MessageToString(result, as_one_line=True)
            logger.info(f"response: {s}")
            ip = result.response_wifi_ip_get.ip
            ip_string = f"{(ip >> 24) & 0xFF}.{(ip >> 16) & 0xFF}.{(ip >> 8) & 0xFF}.{ip & 0xFF}"
            self.focstim_read_ip.setEnabled(True)
            self.focstim_ip.setText(ip_string)

        fut.on_timeout.connect(timeout)
        fut.on_result.connect(result)

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
        qt_ui.settings.focstim_communication_serial.set(self.focstim_radio_serial.isChecked())
        qt_ui.settings.focstim_communication_wifi.set(self.focstim_radio_wifi.isChecked())
        qt_ui.settings.focstim_ssid.set(self.focstim_ssid.text())
        qt_ui.settings.focstim_password.set(self.focstim_password.text())
        qt_ui.settings.focstim_ip.set(self.focstim_ip.text())

        # AS5311 sensor data settings
        if self.as5311_radio_from_box.isChecked():
            qt_ui.settings.focstim_as5311_source.set(0)
        else:
            qt_ui.settings.focstim_as5311_source.set(1)
        qt_ui.settings.focstim_as5311_serve.set(self.as5311_serve_checkbox.isChecked())
        qt_ui.settings.focstim_as5311_serve_port.set(self.as5311_serve_port.value())
        qt_ui.settings.focstim_as5311_server_address.set(self.as5311_server_address.text())
        qt_ui.settings.focstim_as5311_server_port.set(self.as5311_server_port.value())

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

        # patterns
        for row in range(self.patterns_table.rowCount()):
            checkbox = self.patterns_table.cellWidget(row, 1)
            if isinstance(checkbox, QCheckBox):
                pattern_name = checkbox.property("pattern_name")
                if pattern_name:
                    # Update checkbox state from settings
                    was_enabled = self.pattern_service.is_pattern_enabled(pattern_name)
                    is_enabled = checkbox.isChecked()
                    if was_enabled != is_enabled:
                        self.pattern_service.set_pattern_enabled(pattern_name, is_enabled)

    def funscript_reset_defaults(self):
        self.tableView.model().reset_to_defaults()
    
    def setup_patterns_tab(self):
        """Setup the patterns tab with cached pattern data"""
        # Use cached patterns data to avoid late discovery
        patterns = self._cached_patterns or []
        
        if not patterns:
            return
        
        # Set up table with known size
        self.patterns_table.setRowCount(len(patterns))
        
        # Populate table rows
        for row, pattern in enumerate(patterns):
            # Column 0: Pattern name
            name_item = QTableWidgetItem(pattern['name'])
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.patterns_table.setItem(row, 0, name_item)
            
            # Column 1: Enabled checkbox (only for non-priority patterns)
            if pattern['class_name'] in ['MousePattern', 'CirclePattern']:
                # For Mouse and Circle patterns, show blank cell
                enabled_item = QTableWidgetItem("")
                enabled_item.setFlags(Qt.ItemIsEnabled)
                self.patterns_table.setItem(row, 1, enabled_item)
            else:
                # For other patterns, create checkbox
                checkbox = QCheckBox()
                pattern_enabled = self.pattern_service.is_pattern_enabled(pattern['name'])
                checkbox.setChecked(pattern_enabled)
                checkbox.setProperty("pattern_name", pattern['name'])
                checkbox.setProperty("class_name", pattern['class_name'])

                # Add checkbox to table
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsEnabled)
                self.patterns_table.setItem(row, 1, checkbox_item)
                self.patterns_table.setCellWidget(row, 1, checkbox)
        
        # Simple, single layout update
        self.patterns_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.patterns_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.patterns_table.resizeRowsToContents()
        
        # Connect buttons
        self.button_patterns_enable_all.clicked.connect(self.enable_all_patterns)
        self.button_patterns_disable_all.clicked.connect(self.disable_all_patterns)
    
    def refresh_pattern_preferences(self):
        """Refresh checkbox states from current settings without rebuilding the UI"""
        if not hasattr(self, 'patterns_table'):
            return
            
        for row in range(self.patterns_table.rowCount()):
            checkbox = self.patterns_table.cellWidget(row, 1)
            if isinstance(checkbox, QCheckBox):
                pattern_name = checkbox.property("pattern_name")
                if pattern_name:
                    # Update checkbox state from settings
                    enabled = self.pattern_service.is_pattern_enabled(pattern_name)
                    checkbox.setChecked(enabled)
    
    def enable_all_patterns(self):
        """Enable all patterns with checkboxes"""
        for row in range(self.patterns_table.rowCount()):
            widget = self.patterns_table.cellWidget(row, 1)
            if isinstance(widget, QCheckBox):
                widget.setChecked(True)

    def disable_all_patterns(self):
        """Disable all patterns with checkboxes"""
        for row in range(self.patterns_table.rowCount()):
            widget = self.patterns_table.cellWidget(row, 1)
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

