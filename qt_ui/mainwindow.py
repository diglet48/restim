import pathlib
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import QSettings, QTimer, QUrl, QStandardPaths
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSizePolicy, QFrame
)
import logging

import stim_math.audio_gen.continuous
import stim_math.audio_gen.pulse_based
import stim_math.audio_gen.modify
from net.media_source.interface import MediaConnectionState
from qt_ui.algorithm_factory import AlgorithmFactory
from qt_ui.audio_write_dialog import AudioWriteDialog
from qt_ui.device_wizard.axes import AxisEnum
from qt_ui.main_window_ui import Ui_MainWindow
import qt_ui.motion_generation
import qt_ui.audio_generation_widget
import net.websocketserver
import net.tcpudpserver
import qt_ui.funscript_conversion_dialog
import qt_ui.preferences_dialog
import net.serialproxy
import net.buttplug_wsdm_client
from qt_ui import resources
from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.widgets.icon_with_connection_status import IconWithConnectionStatus
from stim_math.audio_gen.params import ThreephaseContinuousAlgorithmParams, ThreephasePositionParams, \
    ThreephasePulsebasedAlgorithmParams, FivephaseContinuousAlgorithmParams, SafetyParams, VolumeParams
from stim_math.axis import create_temporal_axis, create_precomputed_axis, WriteProtectedAxis

from qt_ui.preferences_dialog import KEY_AUDIO_API, KEY_AUDIO_OUTPUT_DEVICE, KEY_AUDIO_LATENCY
import sounddevice as sd

# from qt_ui.device_selection_wizard_1 import DeviceSelectionWizard1, DeviceType
# from qt_ui.device_selection_wizard import DeviceSelectionWizard
from qt_ui.device_wizard.wizard import DeviceSelectionWizard
from qt_ui.device_wizard.enums import DeviceConfiguration, DeviceType, WaveformType

from qt_ui.tcode_command_router import TCodeCommandRouter

logger = logging.getLogger('restim.main')


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # set the first tab as active tab, in case we forgot to set it in designer
        self.tabWidget.setCurrentIndex(0)
        # hide the focus tab
        self.tabWidget.setTabVisible(self.tabWidget.indexOf(self.tab_focus), False)
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_focus), False)

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

        # default alpha/beta axis. Used by:
        # pattern generator
        # network stuff (intiface, tcode)
        self.alpha = create_temporal_axis(0.0)
        self.beta = create_temporal_axis(0.0)

        self.tcode_command_router = TCodeCommandRouter(
            self.alpha,
            self.beta,
            self.tab_volume.api_volume,

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

            self.tab_fivephase.position
        )

        self.graphicsView.set_axis(self.alpha, self.beta, self.tab_threephase.transform_params)
        self.motion_generator = qt_ui.motion_generation.MotionGenerator(self, self.alpha, self.beta)

        self.graphicsView.mousePositionChanged.connect(self.motion_generator.updateMousePosition)

        self.tab_details.set_axis(
            self.alpha,
            self.beta,
            self.tab_threephase.calibrate_params,
            self.tab_threephase.transform_params,
        )
        # self.tab_details.set_config_manager(self.threephase_parameters)
        self.progressBar_volume.set_axis(self.tab_volume.volume)

        self.comboBox_patternSelect.currentTextChanged.connect(self.motion_generator.patternChanged)
        self.motion_generator.patternChanged(self.comboBox_patternSelect.currentText())
        self.doubleSpinBox.valueChanged.connect(self.motion_generator.velocityChanged)
        self.motion_generator.velocityChanged(self.doubleSpinBox.value())

        self.audio_gen = qt_ui.audio_generation_widget.AudioGenerationWidget(None)

        self.websocket_server = net.websocketserver.WebSocketServer(self)
        self.websocket_server.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.tcpudp_server = net.tcpudpserver.TcpUdpServer(self)
        self.tcpudp_server.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.serial_proxy = net.serialproxy.SerialProxy(self)
        self.serial_proxy.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.buttplug_wsdm_client = net.buttplug_wsdm_client.ButtplugWsdmClient(self)
        self.buttplug_wsdm_client.new_tcode_command.connect(self.tcode_command_router.route_command)

        self.tab_volume.set_monitor_axis([
            self.alpha,
            self.beta,
            self.tab_fivephase.position.e1,
            self.tab_fivephase.position.e2,
            self.tab_fivephase.position.e3,
            self.tab_fivephase.position.e4,
            self.tab_fivephase.position.e5,
        ])

        # stop audio when user modifies settings in media tab
        self.page_media.dialogOpened.connect(self.audio_stop)
        self.page_media.funscriptMappingChanged.connect(self.funscript_mapping_changed)
        self.page_media.connectionStatusChanged.connect(self.media_connection_status_changed)
        self.page_media.bake_audio_button.clicked.connect(self.open_write_audio_dialog)

        # trigger updates.... maybe not all needed?
        # self.tab_carrier.settings_changed()
        self.tab_pulse_settings.settings_changed()
        self.tab_threephase.settings_changed()
        self.tab_volume.updateVolume()
        self.tab_fivephase.power_changed()
        self.tab_fivephase.resistance_changed()
        self.tab_vibrate.settings_changed()

        self.set_play_button_state(False)

        self.wizard = DeviceSelectionWizard(self)
        self.actionDevice_selection_wizard.triggered.connect(self.open_setup_wizard)

        self.dialog = qt_ui.funscript_conversion_dialog.FunscriptConversionDialog()
        self.actionFunscript_conversion.triggered.connect(self.open_funscript_conversion_dialog)

        self.settings_dialog = qt_ui.preferences_dialog.PreferencesDialog()
        self.actionPreferences.triggered.connect(self.open_preferences_dialog)

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

    def connect_signals_slots_actionbar(self):
        def uncheck():
            self.actionControl.setChecked(False)
            self.actionMedia.setChecked(False)
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
        # self.actionDevice.triggered.connect(show_device)
        # self.actionLog.triggered.connect(show_log)
        self.actionStart.triggered.connect(self.audio_start_stop)

    def media_connection_status_changed(self, status: MediaConnectionState):
        """
        Called whenever the media connection status changes.
        """
        if status.is_playing():
            self.iconMedia.set_playing()
        elif status.is_connected():
            self.iconMedia.set_connected()
        else:
            self.iconMedia.set_not_connected()

    def funscript_mapping_changed(self):
        """
        Called whenever the user modifies the loaded funscripts
        """
        logger.info('funscript mapping changed, re-linking scripts.')
        self.audio_stop()

        device = DeviceConfiguration.from_settings()
        algorithm_factory = AlgorithmFactory(
            self,
            FunscriptKitModel.load_from_settings(),
            self.page_media.model,
            self.page_media.current_media_sync(),
            self.page_media.current_media_sync(),
            load_funscripts=not self.page_media.is_internal(),
        )

        # main pane
        self.graphicsView.alpha = algorithm_factory.get_axis_alpha()
        self.graphicsView.beta = algorithm_factory.get_axis_beta()
        self.progressBar_volume.volume.api = algorithm_factory.get_axis_volume_api()

        # volume tab
        self.tab_volume.set_monitor_axis([
            algorithm_factory.get_axis_alpha(),
            algorithm_factory.get_axis_beta(),
            self.tab_fivephase.position.e1,
            self.tab_fivephase.position.e2,
            self.tab_fivephase.position.e3,
            self.tab_fivephase.position.e4,
            self.tab_fivephase.position.e5,
        ])

        # continuous tab
        self.tab_carrier.carrier_controller.link_axis(algorithm_factory.get_axis_carrier_frequency(device))

        # pulse tab
        self.tab_pulse_settings.carrier_controller.link_axis(algorithm_factory.get_axis_carrier_frequency(device))
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

    def refresh_device_type(self):
        def set_visible(widget, state):
            self.tabWidget.setTabVisible(self.tabWidget.indexOf(widget), state)
            self.tabWidget.setTabEnabled(self.tabWidget.indexOf(widget), state)

        all_tabs = {self.tab_threephase,
                    self.tab_fivephase,
                    self.tab_pulse_settings,
                    self.tab_carrier,
                    self.tab_volume,
                    self.tab_vibrate,
                    self.tab_details,
                    self.tab_focus}

        visible = {self.tab_threephase, self.tab_volume, self.tab_vibrate, self.tab_details}

        config = DeviceConfiguration.from_settings()

        if config.device_type == DeviceType.THREE_PHASE:
            pass
        if config.device_type == DeviceType.FOUR_PHASE:
            visible |= {self.tab_fivephase}
        if config.device_type == DeviceType.FIVE_PHASE:
            visible |= {self.tab_fivephase}

        if config.waveform_type == WaveformType.CONTINUOUS:
            visible |= {self.tab_carrier}
        if config.waveform_type == WaveformType.PULSE_BASED:
            visible |= {self.tab_pulse_settings}

        # if config.device_type == DeviceType.MODIFY_EXISTING_THREEPHASE_AUDIO:
        #     visible -= {self.tab_volume, self.tab_vibrate, self.tab_details}

        for tab in all_tabs:
            set_visible(tab, tab in visible)

        self.tab_carrier.set_safety_limits(config.min_frequency, config.max_frequency)
        self.tab_pulse_settings.set_safety_limits(config.min_frequency, config.max_frequency)
        if config.waveform_type == WaveformType.CONTINUOUS:
            self.tcode_command_router.set_carrier_axis(self.tab_carrier.axis_carrier)
        if config.waveform_type == WaveformType.PULSE_BASED:
            self.tcode_command_router.set_carrier_axis(self.tab_pulse_settings.axis_carrier_frequency)

    def audio_start_stop(self):
        if self.audio_gen.stream is None:
            self.audio_start()
        else:
            self.audio_stop()

    def audio_start(self):
        settings = QSettings()
        api_name = settings.value(KEY_AUDIO_API, sd.query_hostapis(sd.default.hostapi)['name'])
        output_device_name = settings.value(KEY_AUDIO_OUTPUT_DEVICE, sd.query_devices(sd.default.device[1])['name'])
        latency = settings.value(KEY_AUDIO_LATENCY, 'high')
        try:
            latency = float(latency)
        except ValueError:
            pass

        algorithm_factory = AlgorithmFactory(
            self,
            FunscriptKitModel.load_from_settings(),
            self.page_media.model,
            self.page_media.current_media_sync(),
            self.page_media.current_media_sync(),
            load_funscripts=not self.page_media.is_internal(),
        )
        device = DeviceConfiguration.from_settings()
        algorithm = algorithm_factory.create_algorithm(device)
        mapping_parameters = self.audio_gen.auto_detect_channel_mapping_parameters(algorithm)

        self.audio_gen.start(api_name, output_device_name, latency, algorithm, mapping_parameters)
        if self.audio_gen.stream is not None:
            self.set_play_button_state(True)

    def audio_stop(self):
        self.audio_gen.stop()
        self.set_play_button_state(False)

    def set_play_button_state(self, playing: bool):
        if playing:
            self.actionStart.setIcon(QtGui.QIcon(":/restim/stop-sign_poly.svg"))
            self.actionStart.setText("Stop")
        else:
            self.actionStart.setIcon(QtGui.QIcon(":/restim/play_poly.svg"))
            self.actionStart.setText("Start")

    def open_setup_wizard(self):
        self.audio_stop()
        self.wizard.exec()
        self.refresh_device_type()

    def open_funscript_conversion_dialog(self):
        self.audio_stop()
        self.dialog.exec()

    def open_preferences_dialog(self):
        self.audio_stop()
        self.settings_dialog.exec()
        self.reload_settings()

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
        self.graphicsView.refreshSettings()
        self.progressBar_volume.refreshSettings()
        self.buttplug_wsdm_client.refreshSettings()
        self.funscript_mapping_changed()  # reload funscript axis

    def save_settings(self):
        """
        Save everything that is stored in settings but isn't immediately saved
        for performance reasons.
        """
        self.tab_threephase.save_settings()
        self.tab_carrier.save_settings()
        self.tab_vibrate.save_settings()
        self.tab_pulse_settings.save_settings()
        self.tab_volume.save_settings()
        self.tab_fivephase.save_settings()

    def closeEvent(self, event):
        logger.warning('Shutting down')
        self.audio_gen.stop()
        self.save_settings()
        event.accept()


def run():
    QApplication.setApplicationName("restim")
    QApplication.setOrganizationName("restim")
    QSettings.setDefaultFormat(QSettings.IniFormat)

    log_path = pathlib.Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / 'logs'
    log_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=(log_path / 'restim.log'), filemode='w')
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
    win = Window()
    win.show()
    sys.exit(app.exec())