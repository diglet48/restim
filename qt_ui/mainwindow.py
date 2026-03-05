import os
import sys
from enum import Enum

from PySide6 import QtGui
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSizePolicy, QFrame, QStyleFactory,
    QGroupBox, QFormLayout, QDoubleSpinBox, QLabel, QVBoxLayout
)
import logging

from net.media_source.interface import MediaConnectionState
from qt_ui.algorithm_factory import AlgorithmFactory
from qt_ui.audio_write_dialog import AudioWriteDialog
from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.patterns.threephase_patterns
import qt_ui.patterns.fourphase_patterns
from device.audio.audio_stim_device import AudioStimDevice
import net.websocketserver
import net.tcpudpserver
import qt_ui.funscript_conversion_dialog
import qt_ui.simfile_conversion_dialog
import qt_ui.focstim_flash_dialog
import qt_ui.funscript_decomposition_dialog
import qt_ui.preferences_dialog
import qt_ui.about_dialog
import qt_ui.pulse_auto_derive_dialog
import qt_ui.settings
import net.serialproxy
import net.buttplug_wsdm_client
from qt_ui import resources
from qt_ui.models.funscript_kit import FunscriptKitModel
from device.focstim.proto_device import FOCStimProtoDevice, LSM6DSOX_SAMPLERATE_HZ
from device.neostim.neostim_device import NeoStim
from qt_ui.widgets.icon_with_connection_status import IconWithConnectionStatus
from stim_math.axis import create_temporal_axis


import sounddevice as sd

from qt_ui.device_wizard.wizard import DeviceSelectionWizard
from qt_ui.device_wizard.enums import DeviceConfiguration, DeviceType, WaveformType

from qt_ui.tcode_command_router import TCodeCommandRouter

logger = logging.getLogger('restim.main')


class PlayState(Enum):
    STOPPED = 0
    PLAYING = 1
    WAITING_ON_LOAD = 2  # the audio is stopped, but is ready to be auto-started once funscripts are loaded.


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.playstate = PlayState.STOPPED
        self.tab_volume.set_play_state(self.playstate)
        self.refresh_play_button_icon()

        # set the first tab as active tab, in case we forgot to set it in designer
        self.tabWidget.setCurrentIndex(0)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources.favicon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # TODO: credit https://glyphs.fyi/ for icons
        spacer = QWidget()
        spacer.sizePolicy()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.insertWidget(self.actionStart, spacer)
        line = QFrame()
        # line->setObjectName(QString::fromUtf8("line"));
        # line->setGeometry(QRect(320, 150, 118, 3));
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.toolBar.insertWidget(self.actionStart, line)

        self.doubleSpinBox_volume.setValue(qt_ui.settings.volume_default_level.get())
        self.tab_volume.link_volume_controls(self.doubleSpinBox_volume, self.progressBar_volume)

        self.groupBox_media_offset = QGroupBox('Media sync', self.left_frame)
        self.formLayout_media_offset = QFormLayout(self.groupBox_media_offset)
        self.spinBox_media_offset_ms = QDoubleSpinBox(self.groupBox_media_offset)
        self.spinBox_media_offset_ms.setKeyboardTracking(False)
        self.spinBox_media_offset_ms.setDecimals(0)
        self.spinBox_media_offset_ms.setRange(-999, 999)
        self.spinBox_media_offset_ms.setSingleStep(5)
        self.spinBox_media_offset_ms.setValue(qt_ui.settings.media_sync_time_offset_ms.get())
        self.formLayout_media_offset.addRow(QLabel('time offset [ms]'), self.spinBox_media_offset_ms)
        self.verticalLayout.insertWidget(self.verticalLayout.indexOf(self.groupBox_volume) + 1, self.groupBox_media_offset)
        self.spinBox_media_offset_ms.valueChanged.connect(self.media_offset_changed)
        self.refresh_media_offset_visibility()

        # default alpha/beta axis. Used by:
        # pattern generator
        # network stuff (intiface, tcode)
        self.alpha = create_temporal_axis(0.0)
        self.beta = create_temporal_axis(0.0)

        self.intensity_a = create_temporal_axis(0.0)
        self.intensity_b = create_temporal_axis(0.0)
        self.intensity_c = create_temporal_axis(0.0)
        self.intensity_d = create_temporal_axis(0.0)

        self.tcode_command_router = TCodeCommandRouter(
            self.alpha,
            self.beta,

            self.tab_volume.axis_api_volume,
            self.tab_volume.axis_external_volume,

            self.tab_carrier.axis_carrier,  # this gets set to the device-specific axis later

            self.tab_pulse_settings.axis_pulse_frequency,
            self.tab_pulse_settings.axis_pulse_width,
            self.tab_pulse_settings.axis_pulse_interval_random,
            self.tab_pulse_settings.axis_pulse_rise_time,

            self.tab_vibrate.vibration_1.frequency,
            self.tab_vibrate.vibration_1.strength,
            self.tab_vibrate.vibration_1.left_right_bias,
            self.tab_vibrate.vibration_1.high_low_bias,
            self.tab_vibrate.vibration_1.random,

            self.tab_vibrate.vibration_2.frequency,
            self.tab_vibrate.vibration_2.strength,
            self.tab_vibrate.vibration_2.left_right_bias,
            self.tab_vibrate.vibration_2.high_low_bias,
            self.tab_vibrate.vibration_2.random,

            self.intensity_a,
            self.intensity_b,
            self.intensity_c,
            self.intensity_d,

            # TODO: neostim
        )

        # threephase view
        self.motion_3 = qt_ui.patterns.threephase_patterns.ThreephaseMotionGenerator(self, self.alpha, self.beta)

        # Wire extra axes for YAML event patterns
        self.motion_3.set_extra_axis('volume', self.tab_volume.axis_api_volume)
        self.motion_3.set_extra_axis('pulse_frequency', self.tab_pulse_settings.axis_pulse_frequency)
        self.motion_3.set_extra_axis('pulse_width', self.tab_pulse_settings.axis_pulse_width)
        self.motion_3.set_extra_axis('carrier_frequency', self.tab_pulse_settings.axis_carrier_frequency)

        # Wire 3-phase → 4-phase bridge (uses same gamma modes as TCode input)
        self.motion_3.set_fourphase_axes(
            self.intensity_a, self.intensity_b,
            self.intensity_c, self.intensity_d)

        self.graphicsView_threephase.set_transform_params(self.tab_threephase.transform_params)
        self.graphicsView_threephase.mousePositionChanged.connect(self.motion_3.mouse_event)
        self.motion_3.position_updated.connect(self.graphicsView_threephase.set_cursor_position_ab)
        self.graphicsView_threephase.set_sensor_widget(self.page_sensors)

        # fourphase view: 3D tetrahedron (display-only) + bar chart (interactive)
        from qt_ui.widgets.fourphase_widget_tetrahedron import FourphaseWidgetTetrahedron
        self.graphicsView_fourphase_3d = FourphaseWidgetTetrahedron(self.page_fourphase)

        # lay out both widgets in page_fourphase: stereographic on top, bars below
        fourphase_layout = QVBoxLayout(self.page_fourphase)
        fourphase_layout.setContentsMargins(0, 0, 0, 0)
        fourphase_layout.setSpacing(0)
        self.graphicsView_fourphase_3d.setMinimumSize(150, 150)
        self.graphicsView_fourphase.setFixedHeight(50)
        fourphase_layout.addWidget(self.graphicsView_fourphase_3d, stretch=1)
        fourphase_layout.addWidget(self.graphicsView_fourphase, stretch=0)

        self.motion_4 = qt_ui.patterns.fourphase_patterns.FourphaseMotionGenerator(
            self, self.intensity_a, self.intensity_b, self.intensity_c, self.intensity_d)
        self.graphicsView_fourphase.mousePositionChanged.connect(self.motion_4.mouse_event)
        self.motion_4.position_updated.connect(self.graphicsView_fourphase.set_electrode_intensities)
        self.motion_4.position_updated.connect(self.graphicsView_fourphase_3d.set_electrode_intensities)
        self.graphicsView_fourphase.set_sensor_widget(self.page_sensors)

        # 3-phase details tab
        self.tab_details.set_axis(
            self.alpha,
            self.beta,
            self.tab_threephase.calibrate_params,
            self.tab_threephase.transform_params,
        )
        # 4-phase details tab
        self.tab_details_fourphase.set_intensity_axes(
            self.intensity_a, self.intensity_b,
            self.intensity_c, self.intensity_d,
        )
        # self.tab_details.set_config_manager(self.threephase_parameters)

        self.comboBox_patternSelect.currentIndexChanged.connect(self.pattern_selection_changed)
        self.motion_3.set_pattern(self.comboBox_patternSelect.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_3.set_velocity)
        self.doubleSpinBox.valueChanged.connect(self.motion_4.set_velocity)
        self.motion_3.set_velocity(self.doubleSpinBox.value())

        self.output_device = None

        self.websocket_server = net.websocketserver.WebSocketServer(self)
        self.websocket_server.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.tcpudp_server = net.tcpudpserver.TcpUdpServer(self)
        self.tcpudp_server.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.serial_proxy = net.serialproxy.SerialProxy(self)
        self.serial_proxy.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.buttplug_wsdm_client = net.buttplug_wsdm_client.ButtplugWsdmClient(self)
        self.buttplug_wsdm_client.new_tcode_command.connect(self.tcode_command_router.route_command)

        # Wire TCode axis updates to all AxisControllers so spinboxes update during TCode control
        # and revert to user values when TCode disconnects
        self._connect_tcode_to_axis_controllers()

        self.tab_volume.set_monitor_axis([
            self.alpha,
            self.beta,
            self.intensity_a,
            self.intensity_b,
            self.intensity_c,
            self.intensity_d,
        ])

        # stop audio when user modifies settings in media tab
        self.page_media.dialogOpened.connect(self.signal_stop)
        self.page_media.funscriptMappingChanged.connect(self.funscript_mapping_changed)
        self.page_media.connectionStatusChanged.connect(self.media_connection_status_changed)
        self.page_media.bake_audio_button.clicked.connect(self.open_write_audio_dialog)

        # trigger updates.... maybe not all needed?
        # self.tab_carrier.settings_changed()
        self.tab_pulse_settings.settings_changed()
        self.tab_threephase.settings_changed()
        self.tab_volume.refresh_master_volume()
        self.tab_vibrate.settings_changed()

        self.wizard = DeviceSelectionWizard(self)
        self.actionDevice_selection_wizard.triggered.connect(self.open_setup_wizard)

        self.dialog = qt_ui.funscript_conversion_dialog.FunscriptConversionDialog()
        self.actionFunscript_conversion.triggered.connect(self.open_funscript_conversion_dialog)

        self.simfile_conversion_dialog = qt_ui.simfile_conversion_dialog.SimfileConversionDialog()
        self.actionSimfile_conversion.triggered.connect(self.open_simfile_conversion_dialog)

        self.focstim_flash_dialog = qt_ui.focstim_flash_dialog.FocStimFlashDialog()
        self.actionFirmware_updater.triggered.connect(self.open_focstim_flash_dialog)

        self.funscript_decomposition_dialog = qt_ui.funscript_decomposition_dialog.FunscriptDecompositionDialog()
        self.actionFunscript_decomposition.triggered.connect(self.open_funscript_decomposition_dialog)

        self.pulse_auto_derive_dialog = qt_ui.pulse_auto_derive_dialog.PulseAutoSettingsDialog(self)
        self.pulse_auto_derive_dialog.settings_applied.connect(self.funscript_mapping_changed)
        # Add menu action for pulse auto-derive settings
        from PySide6.QtGui import QAction
        self.actionPulseAutoDerive = QAction("Pulse auto-derive settings...", self)
        self.menuTools.addAction(self.actionPulseAutoDerive)
        self.actionPulseAutoDerive.triggered.connect(self.open_pulse_auto_derive_dialog)
        # Wire the button on the Pulse Settings tab
        self.tab_pulse_settings.btn_auto_derive.clicked.connect(self.open_pulse_auto_derive_dialog)

        self.settings_dialog = qt_ui.preferences_dialog.PreferencesDialog()
        self.actionPreferences.triggered.connect(self.open_preferences_dialog)

        # Dark mode toggle in Setup menu
        from PySide6.QtGui import QAction
        self.actionDarkMode = QAction("Dark Mode", self)
        self.actionDarkMode.setCheckable(True)
        self.actionDarkMode.setChecked(qt_ui.settings.dark_mode.get())
        self.actionDarkMode.triggered.connect(self._toggle_dark_mode)
        self.menuSetup.addSeparator()
        self.menuSetup.addAction(self.actionDarkMode)

        # 4-phase 3D axis mode submenu in Setup menu
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QActionGroup
        self.menu3DAxis = QMenu("3D axis (4-phase gamma)", self)
        self.actionGroup3DAxis = QActionGroup(self)
        self.actionGroup3DAxis.setExclusive(True)

        gamma_mode = qt_ui.settings.fourphase_gamma_mode.get()

        self.action3DAxisSpeed = QAction("Speed-derived", self)
        self.action3DAxisSpeed.setCheckable(True)
        self.action3DAxisSpeed.setChecked(gamma_mode == 'speed')
        self.actionGroup3DAxis.addAction(self.action3DAxisSpeed)
        self.menu3DAxis.addAction(self.action3DAxisSpeed)

        self.action3DAxisPosition = QAction("Position bell-curve", self)
        self.action3DAxisPosition.setCheckable(True)
        self.action3DAxisPosition.setChecked(gamma_mode == 'position')
        self.actionGroup3DAxis.addAction(self.action3DAxisPosition)
        self.menu3DAxis.addAction(self.action3DAxisPosition)

        self.action3DAxisCycle = QAction("Cycle A→B→C→D", self)
        self.action3DAxisCycle.setCheckable(True)
        self.action3DAxisCycle.setChecked(gamma_mode == 'cycle')
        self.actionGroup3DAxis.addAction(self.action3DAxisCycle)
        self.menu3DAxis.addAction(self.action3DAxisCycle)

        self.menu3DAxis.addSeparator()
        info_action = QAction("(overridden by gamma/pitch/roll/sway/surge funscript)", self)
        info_action.setEnabled(False)
        self.menu3DAxis.addAction(info_action)

        self.action3DAxisSpeed.triggered.connect(lambda: self._set_gamma_mode('speed'))
        self.action3DAxisPosition.triggered.connect(lambda: self._set_gamma_mode('position'))
        self.action3DAxisCycle.triggered.connect(lambda: self._set_gamma_mode('cycle'))

        self.menuSetup.addAction(self.menu3DAxis.menuAction())

        # Electrode response curves submenu
        self.menuElectrodeCurves = QMenu("Electrode curves (4-phase)", self)
        self.actionGroupElectrodeCurves = QActionGroup(self)
        self.actionGroupElectrodeCurves.setExclusive(True)

        from stim_math.transforms_4 import ELECTRODE_CURVE_PACKS
        current_pack = qt_ui.settings.fourphase_electrode_curves.get()

        curve_labels = {
            'off':           'Off (linear passthrough)',
            'edger_default': 'Edger-style (linear, ease-in, ease-out, bell)',
            'crossover':     'Crossover (ease-out, ease-in, ease-in, ease-out)',
            'emphasis_cd':   'Emphasis C/D (linear, linear, s-curve, s-curve)',
        }
        for pack_name in ELECTRODE_CURVE_PACKS:
            label = curve_labels.get(pack_name, pack_name)
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(pack_name == current_pack)
            self.actionGroupElectrodeCurves.addAction(action)
            self.menuElectrodeCurves.addAction(action)
            action.triggered.connect(lambda checked, n=pack_name: self._set_electrode_curve_pack(n))

        self.menuSetup.addAction(self.menuElectrodeCurves.menuAction())

        self.about_dialog = qt_ui.about_dialog.AboutDialog(self)
        self.actionAbout.triggered.connect(self.open_about_dialog)

        # ----- Patterns menu -----
        self._setup_patterns_menu()
        self._restore_pattern_settings()

        # ----- Arm Finish button (above Start/Stop in toolbar) -----
        self._setup_finish_button()

        # ----- Hotkey state (foreground fallback + global) -----
        self._space_press_time = None
        self._space_held = False
        self._SPACE_HOLD_MS = 800  # ms to hold for long-press

        # Global hotkey listener (starts disabled)
        from qt_ui.global_hotkeys import GlobalHotkeyListener
        self._global_hotkeys = GlobalHotkeyListener(hold_ms=self._SPACE_HOLD_MS, parent=self)
        self._global_hotkeys.long_press_triggered.connect(self._on_global_long_press)
        self._global_hotkeys.short_press_triggered.connect(self._on_global_short_press)

        self.iconMedia = IconWithConnectionStatus(self.actionMedia.icon(), self.toolBar.widgetForAction(self.actionMedia))
        self.actionMedia.setIcon(QIcon(self.iconMedia))
        # self.iconDevice = IconWithConnectionStatus(self.actionDevice.icon(), self.toolBar.widgetForAction(self.actionDevice))
        # self.actionDevice.setIcon(QIcon(self.iconDevice))

        self.connect_signals_slots_actionbar()

        self.refresh_device_type()

        config = DeviceConfiguration.from_settings()
        if config.device_type == DeviceType.NONE:
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.open_setup_wizard)
            self.timer.start(0)

        self.autostart_timer = QTimer()
        self.autostart_timer.setSingleShot(True)
        self.autostart_timer.timeout.connect(self.autostart_timeout)
        self.autostart_timer.setInterval(5000)

    def connect_signals_slots_actionbar(self):
        def uncheck():
            self.actionControl.setChecked(False)
            self.actionMedia.setChecked(False)
            self.actionSensors.setChecked(False)
            # self.actionDevice.setChecked(False)
            # self.actionLog.setChecked(False)

        def show_control():
            uncheck()
            self.actionControl.setChecked(True)
            self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.page_control))

        def show_media():
            uncheck()
            self.actionMedia.setChecked(True)
            self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.page_media))

        def show_sensors():
            uncheck()
            self.actionSensors.setChecked(True)
            self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.page_sensors))

        # def show_device():
        #     uncheck()
        #     self.actionDevice.setChecked(True)
        #     self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.page_device))

        # def show_log():
        #     uncheck()
        #     self.actionLog.setChecked(True)
        #     self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.page_log))

        self.actionControl.triggered.connect(show_control)
        self.actionMedia.triggered.connect(show_media)
        self.actionSensors.triggered.connect(show_sensors)
        # self.actionDevice.triggered.connect(show_device)
        # self.actionLog.triggered.connect(show_log)
        self.actionStart.triggered.connect(self.signal_start_stop)

    def media_connection_status_changed(self, status: MediaConnectionState):
        """
        Called whenever the media connection status changes.
        """
        self.refresh_media_offset_visibility()
        if status.is_playing():
            self.iconMedia.set_playing()
        elif status.is_connected():
            self.iconMedia.set_connected()
        else:
            self.iconMedia.set_not_connected()

    def media_offset_changed(self, value):
        qt_ui.settings.media_sync_time_offset_ms.set(int(value))

    def refresh_media_offset_visibility(self):
        self.groupBox_media_offset.setVisible(not self.page_media.is_internal())

    def funscript_mapping_changed(self):
        """
        Called whenever the loaded funscripts change
        """
        logger.info('funscript mapping changed, re-linking scripts.')
        if self.page_media.autostart_enabled():
            if self.playstate == PlayState.PLAYING:
                self.signal_stop(PlayState.WAITING_ON_LOAD)
                self.autostart_timer.start()
        else:
            self.signal_stop(PlayState.STOPPED)

        device = DeviceConfiguration.from_settings()
        algorithm_factory = AlgorithmFactory(
            self,
            FunscriptKitModel.load_from_settings(),
            self.page_media.model,
            self.page_media.current_media_sync(),
            self.page_media.current_media_sync(),
            load_funscripts=not self.page_media.is_internal(),
        )

        # 3-phase visualization
        self.motion_3.set_scripts(
            algorithm_factory.get_axis_alpha(),
            algorithm_factory.get_axis_beta(),
        )

        # 4-phase visualization
        self.motion_4.set_scripts(
            algorithm_factory.get_axis_intensity_a(),
            algorithm_factory.get_axis_intensity_b(),
            algorithm_factory.get_axis_intensity_c(),
            algorithm_factory.get_axis_intensity_d(),
        )

        # volume tab
        self.tab_volume.set_monitor_axis([
            algorithm_factory.get_axis_alpha(),
            algorithm_factory.get_axis_beta(),
        ])
        self.tab_volume.axis_funscript_volume = algorithm_factory.get_axis_volume_api()

        # continuous tab
        self.tab_carrier.carrier_controller.link_axis(algorithm_factory.get_axis_continuous_carrier_frequency())

        # pulse tab
        self.tab_pulse_settings.carrier_controller.link_axis(algorithm_factory.get_axis_pulse_carrier_frequency())
        self.tab_pulse_settings.pulse_frequency_controller.link_axis(algorithm_factory.get_axis_pulse_frequency())
        self.tab_pulse_settings.pulse_width_controller.link_axis(algorithm_factory.get_axis_pulse_width())
        self.tab_pulse_settings.pulse_interval_random_controller.link_axis(algorithm_factory.get_axis_pulse_interval_random())
        self.tab_pulse_settings.pulse_rise_time_controller.link_axis(algorithm_factory.get_axis_pulse_rise_time())

        # vibration tab
        self.tab_vibrate.vib1_enabled_controller.link_axis(algorithm_factory.get_axis_vib1_enabled())
        self.tab_vibrate.vib1_freq_controller.link_axis(algorithm_factory.get_axis_vib1_frequency())
        self.tab_vibrate.vib1_strength_controller.link_axis(algorithm_factory.get_axis_vib1_strength())
        self.tab_vibrate.vib1_left_right_bias_controller.link_axis(algorithm_factory.get_axis_vib1_left_right_bias())
        self.tab_vibrate.vib1_high_low_bias_controller.link_axis(algorithm_factory.get_axis_vib1_high_low_bias())
        self.tab_vibrate.vib1_random_controller.link_axis(algorithm_factory.get_axis_vib1_random())
        self.tab_vibrate.vib2_enabled_controller.link_axis(algorithm_factory.get_axis_vib2_enabled())
        self.tab_vibrate.vib2_freq_controller.link_axis(algorithm_factory.get_axis_vib2_frequency())
        self.tab_vibrate.vib2_strength_controller.link_axis(algorithm_factory.get_axis_vib2_strength())
        self.tab_vibrate.vib2_left_right_bias_controller.link_axis(algorithm_factory.get_axis_vib2_left_right_bias())
        self.tab_vibrate.vib2_high_low_bias_controller.link_axis(algorithm_factory.get_axis_vib2_high_low_bias())
        self.tab_vibrate.vib2_random_controller.link_axis(algorithm_factory.get_axis_vib2_random())

        # neostim tab
        # TODO

        if all((not self.page_media.is_internal(),
                self.page_media.has_media_file_loaded(),
                self.page_media.autostart_enabled(),
                self.playstate == PlayState.WAITING_ON_LOAD)):
            logger.info("autostart audio")
            self.signal_start()

    def refresh_device_type(self):
        def set_visible(widget, state):
            self.tabWidget.setTabVisible(self.tabWidget.indexOf(widget), state)
            self.tabWidget.setTabEnabled(self.tabWidget.indexOf(widget), state)

        all_tabs = {self.tab_threephase,
                    self.tab_fourphase,
                    self.tab_pulse_settings,
                    self.tab_carrier,
                    self.tab_volume,
                    self.tab_vibrate,
                    self.tab_details,
                    self.tab_details_fourphase,
                    self.tab_a_b_testing,
                    self.tab_neostim}

        visible = {self.tab_threephase, self.tab_volume, self.tab_vibrate, self.tab_details}

        config = DeviceConfiguration.from_settings()

        # determine tab visibility
        if config.device_type == DeviceType.AUDIO_THREE_PHASE:
            if config.waveform_type == WaveformType.CONTINUOUS:
                visible |= {self.tab_carrier}
            if config.waveform_type == WaveformType.PULSE_BASED:
                visible |= {self.tab_pulse_settings}
            if config.waveform_type == WaveformType.A_B_TESTING:
                visible |= {self.tab_a_b_testing}
        if config.device_type == DeviceType.FOCSTIM_THREE_PHASE:
            visible |= {self.tab_pulse_settings}
            visible -= {self.tab_vibrate}
        if config.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            visible |= {self.tab_pulse_settings, self.tab_fourphase, self.tab_details_fourphase}
            visible -= {self.tab_vibrate, self.tab_threephase, self.tab_details}
        if config.device_type == DeviceType.NEOSTIM_THREE_PHASE:
            visible |= {self.tab_neostim}
            visible -= {self.tab_vibrate, self.tab_details}

        for tab in all_tabs:
            set_visible(tab, tab in visible)

        # set safety limits
        self.tab_carrier.set_safety_limits(config.min_frequency, config.max_frequency)
        self.tab_pulse_settings.set_safety_limits(config.min_frequency, config.max_frequency)
        self.tab_a_b_testing.set_safety_limits(config.min_frequency, config.max_frequency)

        # configure tcode router
        if config.waveform_type == WaveformType.CONTINUOUS:
            self.tcode_command_router.set_carrier_axis(self.tab_carrier.axis_carrier)
        if config.waveform_type == WaveformType.PULSE_BASED:
            self.tcode_command_router.set_carrier_axis(self.tab_pulse_settings.axis_carrier_frequency)

        # populate motion generator and patterns combobox
        if config.device_type in (DeviceType.AUDIO_THREE_PHASE, DeviceType.NEOSTIM_THREE_PHASE, DeviceType.FOCSTIM_THREE_PHASE):
            self.motion_3.set_enable(True)
            self.motion_3.set_write_position(True)
            self.motion_4.set_enable(False)
            self.stackedWidget_visual.setCurrentIndex(
                self.stackedWidget_visual.indexOf(self.page_threephase)
            )

        if config.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            # motion_3 stays enabled for YAML extended-axis writes (pulse params)
            # but position output is suppressed — motion_4 owns electrode intensities
            self.motion_3.set_enable(True)
            self.motion_3.set_write_position(False)
            self.motion_4.set_enable(True)
            self.stackedWidget_visual.setCurrentIndex(
                self.stackedWidget_visual.indexOf(self.page_fourphase)
            )

        if config.device_type == DeviceType.AUDIO_THREE_PHASE:
            self.graphicsView_threephase.set_background(stereo=True)
            self.tab_threephase.phase_widget_calibration.set_background(stereo=True)
        else:
            self.graphicsView_threephase.set_background(foc=True)
            self.tab_threephase.phase_widget_calibration.set_background(foc=True)

        self.refresh_pattern_combobox()

    def pattern_selection_changed(self, index):
        pattern = self.comboBox_patternSelect.currentData()
        self.motion_3.set_pattern(pattern)
        self.motion_4.set_pattern(pattern)

    def signal_start_stop(self):
        if self.playstate == PlayState.STOPPED:
            self.signal_start()
        else:
            self.signal_stop(PlayState.STOPPED)

    def signal_start(self):
        assert self.output_device is None

        self.autostart_timer.stop()
        device = DeviceConfiguration.from_settings()
        algorithm_factory = AlgorithmFactory(
            self,
            FunscriptKitModel.load_from_settings(),
            self.page_media.model,
            self.page_media.current_media_sync(),
            self.page_media.current_media_sync(),
            load_funscripts=not self.page_media.is_internal(),
        )
        algorithm = algorithm_factory.create_algorithm(device)

        if device.device_type in [
            DeviceType.AUDIO_THREE_PHASE,
        ]: # is audio device
            api_name = qt_ui.settings.audio_api.get() or sd.query_hostapis(sd.default.hostapi)['name']
            output_device_name = qt_ui.settings.audio_output_device.get() or sd.query_devices(sd.default.device[1])['name']
            latency = qt_ui.settings.audio_latency.get() or 'high'
            try:
                latency = float(latency)
            except ValueError:
                pass

            output_device = AudioStimDevice(None)
            mapping_parameters = output_device.auto_detect_channel_mapping_parameters(algorithm)
            output_device.start(api_name, output_device_name, latency, algorithm, mapping_parameters)
            if output_device.is_connected_and_running():
                self.output_device = output_device
                self.playstate = PlayState.PLAYING
                self.tab_volume.set_play_state(self.playstate)
                self.refresh_play_button_icon()
        elif device.device_type in (DeviceType.FOCSTIM_THREE_PHASE, DeviceType.FOCSTIM_FOUR_PHASE):
            output_device = FOCStimProtoDevice()
            use_teleplot = qt_ui.settings.focstim_use_teleplot.get()
            dump_notifications = qt_ui.settings.focstim_dump_notifications_to_file.get()
            comms_wifi = qt_ui.settings.focstim_communication_wifi.get()
            if not comms_wifi:
                serial_port_name = qt_ui.settings.focstim_serial_port.get()
                output_device.start_serial(serial_port_name, use_teleplot, dump_notifications, algorithm)
            else:
                ip = qt_ui.settings.focstim_ip.get()
                output_device.start_tcp(ip, 55533, use_teleplot, dump_notifications, algorithm)

            if output_device.is_connected_and_running():
                self.output_device = output_device
                self.playstate = PlayState.PLAYING
                self.tab_volume.set_play_state(self.playstate)
                self.refresh_play_button_icon()

                output_device.new_as5311_sensor_data.connect(self.page_sensors.new_as5311_sensor_data)
                output_device.new_imu_sensor_data.connect(self.page_sensors.new_imu_sensor_data)
                output_device.new_pressure_sensor_data.connect(self.page_sensors.new_pressure_sensor_data)
                output_device.new_currents_data.connect(self.tab_details_fourphase.update_currents)
                output_device.new_model_estimation_data.connect(self.tab_details_fourphase.update_impedance)
                algorithm.sensor_node = self.page_sensors


        elif device.device_type == DeviceType.NEOSTIM_THREE_PHASE:
            output_device = NeoStim()
            serial_port_name = qt_ui.settings.neostim_serial_port.get()
            output_device.start(serial_port_name, algorithm)
            if output_device.is_connected_and_running():
                self.output_device = output_device
                self.playstate = PlayState.PLAYING
                self.tab_volume.set_play_state(self.playstate)
                self.refresh_play_button_icon()
        else:
            raise RuntimeError("Unknown device type")

    def signal_stop(self, new_playstate: PlayState = PlayState.STOPPED):
        if self.output_device is not None:
            self.output_device.stop()
            self.output_device = None
        self.playstate = new_playstate
        self.tab_volume.set_play_state(self.playstate)
        self.refresh_play_button_icon()

    def autostart_timeout(self):
        print('autostart timeout')
        if self.playstate == PlayState.WAITING_ON_LOAD:
            logger.info("autostart timeout reached. No longer starting audio on file load")
            self.signal_stop(PlayState.STOPPED)

    def refresh_play_button_icon(self):
        if self.playstate in (PlayState.PLAYING, PlayState.WAITING_ON_LOAD):
            self.actionStart.setIcon(QtGui.QIcon(":/restim/stop-sign_poly.svg"))
            self.actionStart.setText("Stop")
        else:
            self.actionStart.setIcon(QtGui.QIcon(":/restim/play_poly.svg"))
            self.actionStart.setText("Start")

    def open_setup_wizard(self):
        self.signal_stop(PlayState.STOPPED)
        self.wizard.exec()
        self.refresh_device_type()
        self.reload_settings()

    def open_funscript_conversion_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.dialog.exec()

    def open_simfile_conversion_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.simfile_conversion_dialog.exec()

    def open_focstim_flash_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.focstim_flash_dialog.exec()

    def open_funscript_decomposition_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.funscript_decomposition_dialog.exec()

    def open_pulse_auto_derive_dialog(self):
        """Open the pulse auto-derive settings window and feed it the currently loaded funscript."""
        from qt_ui.device_wizard.axes import AxisEnum
        from qt_ui.models.script_mapping import FunscriptTreeItem

        # Try to find the currently loaded funscript for preview
        main_t = main_p = alpha_t = alpha_p = None

        # Look for bare 1D funscript
        for item in self.page_media.model.funscript_conifg():
            if isinstance(item, FunscriptTreeItem) and item.funscript_type == '' and not item.has_broken_script():
                if item.script is not None:
                    main_t = item.script.x
                    main_p = item.script.y
                    break

        # Look for alpha
        alpha_item = self.page_media.model.get_config_for_axis(AxisEnum.POSITION_ALPHA)
        if alpha_item and alpha_item.script is not None:
            alpha_t = alpha_item.script.x
            alpha_p = alpha_item.script.y
            # If no bare 1D, use alpha as main too
            if main_t is None:
                main_t = alpha_t
                main_p = alpha_p

        if main_t is not None:
            self.pulse_auto_derive_dialog.set_demo_funscript(main_t, main_p, alpha_t, alpha_p)

        self.pulse_auto_derive_dialog.show()
        self.pulse_auto_derive_dialog.raise_()
        self.pulse_auto_derive_dialog.activateWindow()

    def open_preferences_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.settings_dialog.exec()
        self.reload_settings()

    def open_about_dialog(self):
        self.signal_stop(PlayState.STOPPED)
        self.about_dialog.exec()

    def _toggle_dark_mode(self, checked):
        qt_ui.settings.dark_mode.set(checked)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Dark Mode",
                                "Dark mode setting saved. Please restart restim for the change to take full effect.")

    def _set_gamma_mode(self, mode):
        qt_ui.settings.fourphase_gamma_mode.set(mode)
        logger.info(f'4-phase gamma mode set to: {mode}')

    def _set_electrode_curve_pack(self, pack_name):
        qt_ui.settings.fourphase_electrode_curves.set(pack_name)
        logger.info(f'4-phase electrode curve pack set to: {pack_name}')

    # ------------------------------------------------------------------
    # Patterns menu
    # ------------------------------------------------------------------

    def _setup_patterns_menu(self):
        """Create the Patterns menu in the menu bar with category submenus
        and axis-control toggles for YAML event categories."""
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction, QActionGroup
        from qt_ui.patterns.threephase.base import get_all_categories, get_patterns_by_category

        self.menuPatterns = QMenu("Patterns", self)
        self.menuBar.insertMenu(self.menuHelp.menuAction(), self.menuPatterns)

        # Category action group — exclusive, selecting one filters the dropdown
        self._pattern_category_group = QActionGroup(self)
        self._pattern_category_group.setExclusive(True)

        # Built-in categories (always present)
        builtin_cats = ['manual', 'mathematical', 'basic', 'complex', 'experimental', 'oscillation']
        yaml_cats = []

        all_cats = get_all_categories()
        for cat in sorted(all_cats):
            if cat.lower() in builtin_cats:
                continue
            yaml_cats.append(cat)

        # Add built-in categories first
        for cat in builtin_cats:
            if cat in all_cats:
                action = QAction(cat.capitalize(), self)
                action.setCheckable(True)
                if cat == 'manual':
                    action.setChecked(True)
                    self._current_pattern_category = cat
                self._pattern_category_group.addAction(action)
                self.menuPatterns.addAction(action)
                action.triggered.connect(lambda checked, c=cat: self._select_pattern_category(c))

        if yaml_cats:
            self.menuPatterns.addSeparator()

        # Add YAML categories
        for cat in yaml_cats:
            action = QAction(cat, self)
            action.setCheckable(True)
            self._pattern_category_group.addAction(action)
            self.menuPatterns.addAction(action)
            action.triggered.connect(lambda checked, c=cat: self._select_pattern_category(c))

        # Separator before axis toggles
        self._axis_toggle_separator = self.menuPatterns.addSeparator()
        self._axis_toggle_separator.setVisible(False)

        # Axis control toggles (only visible when YAML category selected)
        self._axis_toggle_actions = {}
        axis_labels = {
            'volume': 'Volume',
            'pulse_frequency': 'Pulse Frequency',
            'pulse_width': 'Pulse Width',
            'carrier_frequency': 'Carrier Frequency',
        }
        for axis_name, label in axis_labels.items():
            action = QAction(f"Control: {label}", self)
            action.setCheckable(True)
            action.setChecked(self.motion_3.is_extra_axis_enabled(axis_name))
            action.setVisible(False)
            self.menuPatterns.addAction(action)
            action.triggered.connect(
                lambda checked, an=axis_name: self._toggle_axis_control(an, checked))
            self._axis_toggle_actions[axis_name] = action

        # Separator before loop speed
        self._loop_speed_separator = self.menuPatterns.addSeparator()
        self._loop_speed_separator.setVisible(False)

        # Loop Speed spinbox (visible when YAML category active)
        from PySide6.QtWidgets import QWidgetAction, QWidget, QHBoxLayout, QLabel, QDoubleSpinBox as QDSpinBox
        loop_speed_widget = QWidget()
        loop_speed_layout = QHBoxLayout(loop_speed_widget)
        loop_speed_layout.setContentsMargins(20, 2, 10, 2)
        loop_speed_label = QLabel("Loop Speed:")
        self._loop_speed_spinbox = QDSpinBox()
        self._loop_speed_spinbox.setRange(0.1, 10.0)
        self._loop_speed_spinbox.setSingleStep(0.1)
        self._loop_speed_spinbox.setDecimals(1)
        self._loop_speed_spinbox.setValue(qt_ui.settings.patterns_loop_speed.get())
        self._loop_speed_spinbox.setSuffix("x")
        loop_speed_layout.addWidget(loop_speed_label)
        loop_speed_layout.addWidget(self._loop_speed_spinbox)
        self._loop_speed_action = QWidgetAction(self)
        self._loop_speed_action.setDefaultWidget(loop_speed_widget)
        self._loop_speed_action.setVisible(False)
        self.menuPatterns.addAction(self._loop_speed_action)
        self._loop_speed_spinbox.valueChanged.connect(self._on_loop_speed_changed)

        # Separator before global hotkeys toggle
        self.menuPatterns.addSeparator()

        # Global Hotkeys toggle
        from qt_ui.global_hotkeys import GlobalHotkeyListener
        self._global_hotkey_action = QAction("Global Hotkeys (space / middle-click)", self)
        self._global_hotkey_action.setCheckable(True)
        self._global_hotkey_action.setChecked(False)
        self._global_hotkey_action.setEnabled(GlobalHotkeyListener.is_available())
        if not GlobalHotkeyListener.is_available():
            self._global_hotkey_action.setText("Global Hotkeys (pynput not installed)")
        self._global_hotkey_action.triggered.connect(self._toggle_global_hotkeys)
        self.menuPatterns.addAction(self._global_hotkey_action)

    def _restore_pattern_settings(self):
        """Restore persisted Patterns menu settings from restim.ini."""
        # Restore category selection
        saved_cat = qt_ui.settings.patterns_category.get()
        if saved_cat:
            for action in self._pattern_category_group.actions():
                if action.text().lower() == saved_cat.lower() or action.text() == saved_cat:
                    action.setChecked(True)
                    self._select_pattern_category(saved_cat)
                    break

        # Restore axis toggles
        axis_settings = {
            'volume': qt_ui.settings.patterns_axis_volume,
            'pulse_frequency': qt_ui.settings.patterns_axis_pulse_frequency,
            'pulse_width': qt_ui.settings.patterns_axis_pulse_width,
            'carrier_frequency': qt_ui.settings.patterns_axis_carrier_frequency,
        }
        for axis_name, setting in axis_settings.items():
            enabled = setting.get()
            self.motion_3.set_extra_axis_enabled(axis_name, enabled)
            if axis_name in self._axis_toggle_actions:
                self._axis_toggle_actions[axis_name].setChecked(enabled)

        # Restore finish armed state
        if qt_ui.settings.patterns_finish_armed.get():
            self.actionArmFinish.setChecked(True)
            self._on_arm_finish_toggled(True)

        # Restore global hotkeys
        if qt_ui.settings.patterns_global_hotkeys.get() and self._global_hotkey_action.isEnabled():
            self._global_hotkey_action.setChecked(True)
            self._global_hotkeys.start()

        # Restore loop speed
        speed = qt_ui.settings.patterns_loop_speed.get()
        self.motion_3.set_loop_speed(speed)
        self._loop_speed_spinbox.setValue(speed)

    def _select_pattern_category(self, category: str):
        """Called when user selects a pattern category from the Patterns menu."""
        self._current_pattern_category = category
        qt_ui.settings.patterns_category.set(category)
        self.refresh_pattern_combobox()

        # Show/hide axis toggles based on whether this is a YAML category
        is_yaml = self._is_yaml_category(category)
        self._axis_toggle_separator.setVisible(is_yaml)
        for action in self._axis_toggle_actions.values():
            action.setVisible(is_yaml)
        self._loop_speed_separator.setVisible(is_yaml)
        self._loop_speed_action.setVisible(is_yaml)

        # Disable pattern dropdown when funscripts are loaded (unless finish mode)
        self._update_pattern_interaction_state()

    def _toggle_axis_control(self, axis_name: str, enabled: bool):
        """Toggle whether a pattern is allowed to control this axis."""
        self.motion_3.set_extra_axis_enabled(axis_name, enabled)
        # Persist
        axis_settings = {
            'volume': qt_ui.settings.patterns_axis_volume,
            'pulse_frequency': qt_ui.settings.patterns_axis_pulse_frequency,
            'pulse_width': qt_ui.settings.patterns_axis_pulse_width,
            'carrier_frequency': qt_ui.settings.patterns_axis_carrier_frequency,
        }
        if axis_name in axis_settings:
            axis_settings[axis_name].set(enabled)

    def _on_loop_speed_changed(self, value: float):
        """Update motion generator loop speed and persist."""
        self.motion_3.set_loop_speed(value)
        qt_ui.settings.patterns_loop_speed.set(value)

    def _is_yaml_category(self, category: str) -> bool:
        builtin = {'manual', 'mathematical', 'basic', 'complex', 'experimental', 'oscillation'}
        return category.lower() not in builtin

    def _is_yaml_category_active(self) -> bool:
        """Check if the currently selected pattern category is YAML-based."""
        cat = getattr(self, '_current_pattern_category', 'manual')
        return self._is_yaml_category(cat)

    # ------------------------------------------------------------------
    # Arm Finish button
    # ------------------------------------------------------------------

    def _setup_finish_button(self):
        """Add the 'Arm Finish' toggle button above Start/Stop in the toolbar."""
        from PySide6.QtGui import QAction
        self.actionArmFinish = QAction("Arm\nFinish", self)
        self.actionArmFinish.setCheckable(True)
        self.actionArmFinish.setChecked(False)
        self.actionArmFinish.triggered.connect(self._on_arm_finish_toggled)
        # Insert before the Start action in the toolbar
        self.toolBar.insertAction(self.actionStart, self.actionArmFinish)

        # Connect finish state changes to update button appearance
        self.motion_3.finish_state_changed.connect(self._on_finish_state_changed)

    def _on_arm_finish_toggled(self, checked):
        self.motion_3.arm_finish(checked)
        qt_ui.settings.patterns_finish_armed.set(checked)
        if checked:
            self.actionArmFinish.setText("Finish\nArmed")
        else:
            self.actionArmFinish.setText("Arm\nFinish")

    def _on_finish_state_changed(self, active):
        """Update UI when finish mode activates/deactivates."""
        if active:
            self.actionArmFinish.setText("Finish\nACTIVE")
            pattern_name = getattr(self.motion_3, '_finish_pattern', None)
            pattern_name = pattern_name.name() if pattern_name else 'pattern'
            self.statusBar().showMessage(f"Finish ACTIVE — {pattern_name}")
        elif self.motion_3.is_finish_armed():
            self.actionArmFinish.setText("Finish\nArmed")
            self.statusBar().showMessage("Finish deactivated — returning to funscript", 3000)
        else:
            self.actionArmFinish.setText("Arm\nFinish")
            self.statusBar().clearMessage()

    # ------------------------------------------------------------------
    # Spacebar / middle-click long-press for Finish
    # ------------------------------------------------------------------

    def keyPressEvent(self, event):
        """Detect spacebar long-press to activate Finish mode (foreground fallback)."""
        if self._global_hotkeys.is_running():
            # Global listener handles it — don't double-fire
            super().keyPressEvent(event)
            return
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            if self.motion_3.is_finish_active():
                self.motion_3.deactivate_finish()
                self._space_press_time = None
                return
            if self.motion_3.is_finish_armed() and self.motion_3.any_scripts_loaded():
                import time as _time
                self._space_press_time = _time.time()
                self._space_held = False
                if not hasattr(self, '_space_timer'):
                    self._space_timer = QTimer(self)
                    self._space_timer.setSingleShot(True)
                    self._space_timer.timeout.connect(self._space_hold_timeout)
                self._space_timer.start(self._SPACE_HOLD_MS)
                return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Cancel long-press if spacebar released too early (foreground fallback)."""
        if self._global_hotkeys.is_running():
            super().keyReleaseEvent(event)
            return
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            if self._space_press_time is not None and not self._space_held:
                self._space_press_time = None
                if hasattr(self, '_space_timer'):
                    self._space_timer.stop()
        super().keyReleaseEvent(event)

    def _space_hold_timeout(self):
        """Called when spacebar has been held long enough → activate Finish."""
        if self._space_press_time is not None:
            self._space_held = True
            self._space_press_time = None
            self.motion_3.activate_finish()

    # ------------------------------------------------------------------
    # Global hotkeys (pynput)
    # ------------------------------------------------------------------

    def _toggle_global_hotkeys(self, checked: bool):
        """Toggle global hotkey listener on/off from Patterns menu."""
        qt_ui.settings.patterns_global_hotkeys.set(checked)
        if checked:
            self._global_hotkeys.start()
        else:
            self._global_hotkeys.stop()

    def _on_global_long_press(self):
        """Global spacebar or middle-click held long enough → activate Finish."""
        if self.motion_3.is_finish_armed() and self.motion_3.any_scripts_loaded():
            self.motion_3.activate_finish()

    def _on_global_short_press(self):
        """Global spacebar or middle-click short tap → deactivate Finish."""
        if self.motion_3.is_finish_active():
            self.motion_3.deactivate_finish()

    # ------------------------------------------------------------------
    # Pattern / funscript interaction
    # ------------------------------------------------------------------

    def _update_pattern_interaction_state(self):
        """Disable/enable pattern controls based on funscript state."""
        has_scripts = self.motion_3.any_scripts_loaded()
        is_yaml = self._is_yaml_category_active()

        # Pattern combobox: disabled when funscripts loaded AND not in finish mode
        # (user can still arm finish via button)
        if has_scripts and not self.motion_3.is_finish_active():
            self.comboBox_patternSelect.setEnabled(False)
            self.doubleSpinBox.setEnabled(False)
        else:
            self.comboBox_patternSelect.setEnabled(True)
            self.doubleSpinBox.setEnabled(True)

    def _connect_tcode_to_axis_controllers(self):
        """Connect TCode axis_updated signal to all AxisControllers across all settings widgets.
        This makes spinboxes update in real-time during TCode control and revert on disconnect."""
        signal = self.tcode_command_router.axis_updated

        # Pulse settings controllers
        signal.connect(self.tab_pulse_settings.carrier_controller.on_tcode_axis_updated)
        signal.connect(self.tab_pulse_settings.pulse_frequency_controller.on_tcode_axis_updated)
        signal.connect(self.tab_pulse_settings.pulse_width_controller.on_tcode_axis_updated)
        signal.connect(self.tab_pulse_settings.pulse_interval_random_controller.on_tcode_axis_updated)
        signal.connect(self.tab_pulse_settings.pulse_rise_time_controller.on_tcode_axis_updated)

        # YAML pattern axis writes → same spinbox update mechanism
        pat_signal = self.motion_3.extra_axis_updated
        pat_signal.connect(self.tab_pulse_settings.carrier_controller.on_tcode_axis_updated)
        pat_signal.connect(self.tab_pulse_settings.pulse_frequency_controller.on_tcode_axis_updated)
        pat_signal.connect(self.tab_pulse_settings.pulse_width_controller.on_tcode_axis_updated)

        # Carrier settings controller (continuous waveform mode)
        signal.connect(self.tab_carrier.carrier_controller.on_tcode_axis_updated)

        # Vibration settings controllers
        signal.connect(self.tab_vibrate.vib1_enabled_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib1_freq_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib1_strength_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib1_left_right_bias_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib1_high_low_bias_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib1_random_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_enabled_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_freq_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_strength_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_left_right_bias_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_high_low_bias_controller.on_tcode_axis_updated)
        signal.connect(self.tab_vibrate.vib2_random_controller.on_tcode_axis_updated)

    def open_write_audio_dialog(self):
        device = DeviceConfiguration.from_settings()
        kit = FunscriptKitModel.load_from_settings()
        filename = self.page_media.loaded_media_path
        dialog = AudioWriteDialog(self, kit, self.page_media.model, device, filename)
        dialog.exec()

    def reload_settings(self):
        """
        Reload everything that is stored in settings and may be changed
        by the preferences dialog
        """
        self.tcode_command_router.reload_kit()
        self.tab_volume.refreshSettings()
        self.buttplug_wsdm_client.refreshSettings()
        self.funscript_mapping_changed()  # reload funscript axis
        self.tab_a_b_testing.refreshSettings()
        self.motion_3.refreshSettings()
        self.motion_4.refreshSettings()
        self.refresh_pattern_combobox()

    def refresh_pattern_combobox(self):
        config = DeviceConfiguration.from_settings()
        currently_selected_text = self.comboBox_patternSelect.currentText()
        category = getattr(self, '_current_pattern_category', None)

        if config.device_type in (DeviceType.AUDIO_THREE_PHASE, DeviceType.NEOSTIM_THREE_PHASE, DeviceType.FOCSTIM_THREE_PHASE):
            self.comboBox_patternSelect.clear()
            for pattern in self.motion_3.patterns:
                # Filter by selected category if set
                pat_cat = getattr(pattern, 'category', 'manual')
                if category and pat_cat.lower() != category.lower():
                    continue
                self.comboBox_patternSelect.addItem(pattern.name(), pattern)
        elif config.device_type == DeviceType.FOCSTIM_FOUR_PHASE:
            # Show both native 4-phase patterns AND threephase/YAML patterns
            # (motion_3 is still ticking for YAML extended-axis writes & alpha/beta bridge)
            self.comboBox_patternSelect.clear()
            for pattern in self.motion_4.patterns:
                self.comboBox_patternSelect.addItem(pattern.name(), pattern)
            for pattern in self.motion_3.patterns:
                pat_cat = getattr(pattern, 'category', 'manual')
                if category and pat_cat.lower() != category.lower():
                    continue
                # Skip mouse pattern — motion_4 already has its own
                from qt_ui.patterns.threephase.mouse import MousePattern as ThreephaseMousePattern
                if isinstance(pattern, ThreephaseMousePattern):
                    continue
                self.comboBox_patternSelect.addItem(pattern.name(), pattern)
        else:
            self.comboBox_patternSelect.clear()
            for pattern in self.motion_4.patterns:
                self.comboBox_patternSelect.addItem(pattern.name(), pattern)

        # try to select pattern with similar name as was previously selected
        index = self.comboBox_patternSelect.findText(currently_selected_text)
        if index == -1:
            index = 0
        self.comboBox_patternSelect.setCurrentIndex(index)


    def save_settings(self):
        """
        Save everything that is stored in settings but isn't immediately saved
        for performance reasons.
        """
        self.tab_threephase.save_settings()
        self.tab_fourphase.save_settings()
        self.tab_carrier.save_settings()
        self.tab_vibrate.save_settings()
        self.tab_pulse_settings.save_settings()
        self.tab_volume.save_settings()
        self.page_media.save_settings()

    def closeEvent(self, event):
        logger.warning('Shutting down')
        if self.output_device is not None:
            self.output_device.stop()
        self.save_settings()
        event.accept()


def run():
    log_path = os.getcwd()
    logging.basicConfig(filename=os.path.join(log_path, 'restim.log'), filemode='w')
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger('restim')
    logger.setLevel(logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.WARN)

    def excepthook(exc_type, exc_value, exc_tb):
        exc_info = (exc_type, exc_value, exc_tb)
        logger.critical('Exception occurred', exc_info=exc_info)
        QApplication.quit()

    sys.excepthook = excepthook

    app = QApplication(sys.argv)

    if qt_ui.settings.dark_mode.get():
        from qt_ui.dark_mode import apply_dark_mode
        apply_dark_mode(app)

    win = Window()
    win.show()
    sys.exit(app.exec())