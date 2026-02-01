import logging
import time
import datetime
import os

import stream # pystream-protobuf

import google.protobuf.text_format
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODevice, QTimer, QObject, Signal
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtNetwork import QTcpSocket

import qt_ui.settings
from device.focstim.proto_api import FOCStimProtoAPI
from device.focstim.notifications_pb2 import NotificationBoot, NotificationPotentiometer, NotificationCurrents, \
    NotificationModelEstimation, NotificationSystemStats, NotificationSignalStats, NotificationBattery, \
    NotificationLSM6DSOX, NotificationDebugString, NotificationDebugAS5311, NotificationPressure
from net.teleplot import Teleplot
from device.output_device import OutputDevice
from stim_math.audio_gen.base_classes import RemoteGenerationAlgorithm

from device.focstim.focstim_rpc_pb2 import Response
from device.focstim.messages_pb2 import ResponseCapabilitiesGet, ResponseFirmwareVersion
from device.focstim.constants_pb2 import OutputMode
from stim_math.sensors.as5311 import AS5311Data

from stim_math.sensors.imu import IMUData
from stim_math.sensors.pressure import PressureData

logger = logging.getLogger('restim.focstim')

FOCSTIM_VERSION = "1.0"

TIMEOUT_SETUP = 2000    # ms
TIMEOUT_UPDATE = 4000   # ms

LSM6DSOX_SAMPLERATE_HZ = 104
LSM6DSOX_ACC_FULLSCALE = 4
LSM6DSOX_GYR_FULLSCALE = 500


class FOCStimProtoDevice(QObject, OutputDevice):
    def __init__(self):
        super().__init__()
        self.transport = None
        self.algorithm = None
        self.old_dict = {}
        self.teleplot = None
        self.notification_log = None
        self.dump_notifications = False

        self.firmware = ResponseFirmwareVersion()
        self.capabilities = ResponseCapabilitiesGet()

        self.updates_sent = 0
        self.last_update = time.time()

        self.update_timer = QTimer()
        self.update_timer.setInterval(int(1000 // 60))
        self.update_timer.timeout.connect(self.transmit_dirty_params)

        self.max_latency = 0.2

        # self.set_timestamp_timer = QTimer()
        # self.set_timestamp_timer.setInterval(1000 // 10)
        # self.set_timestamp_timer.timeout.connect(self.timeout_set_timestamp)

        self.clear_dirty_params_timer = QTimer()
        self.clear_dirty_params_timer.setInterval(1000)
        self.clear_dirty_params_timer.timeout.connect(self.clear_dirty_params)

        self.acc_sensitivity = 0
        self.gyr_sensitivity = 0

        def print_data_rate():
            if self.api and self.teleplot:
                self.teleplot.write_metrics(
                   bytes_out=self.api.bytes_written,
                   bytes_in=self.api.bytes_read,
                   updates_sent=self.updates_sent
                )
                self.api.bytes_read = 0
                self.api.bytes_written = 0
                self.updates_sent = 0

        self.print_data_rate_timer = QTimer()
        self.print_data_rate_timer.setInterval(1000)
        self.print_data_rate_timer.timeout.connect(print_data_rate)
        self.print_data_rate_timer.start()

        self.delayed_start_timer = QTimer()

        self.api: FOCStimProtoAPI = None

    def start_teleplot(self, use_teleplot):
        if use_teleplot:
            prefix = qt_ui.settings.focstim_teleplot_prefix.get()
            self.teleplot = Teleplot(prefix)

    def start_tcp(self, host_address, port, use_teleplot, dump_notifications, algorithm: RemoteGenerationAlgorithm):
        assert self.api is None
        self.algorithm = algorithm
        self.start_teleplot(use_teleplot)
        self.dump_notifications = dump_notifications

        logger.info(f"connecting to FOC-Stim at {host_address}:{port}")
        self.transport = QTcpSocket(self)
        self.transport.setSocketOption(QAbstractSocket.SocketOption.LowDelayOption, 1)
        self.transport.connected.connect(self.on_transport_connected)
        self.transport.errorOccurred.connect(self.on_connection_error)
        self.transport.connectToHost(host_address, port)

    def start_serial(self, com_port, use_teleplot, dump_notifications, algorithm: RemoteGenerationAlgorithm):
        assert self.api is None
        self.algorithm = algorithm
        self.start_teleplot(use_teleplot)
        self.dump_notifications = dump_notifications

        logger.info(f"Connecting to FOC-Stim at {com_port}")
        self.transport = QSerialPort(self)
        self.transport.setPortName(com_port)
        self.transport.setBaudRate(115200)
        success = self.transport.open(QIODevice.OpenModeFlag.ReadWrite)
        # self.transport.setFlowControl(QSerialPort.FlowControl.NoFlowControl)
        # self.transport.setRequestToSend(False)
        # self.transport.setDataTerminalReady(False)
        self.transport.setSettingsRestoredOnClose(False)
        if success:
            def delayed_start():
                # read all buffered data and discard it.
                self.transport.readAll()
                self.on_transport_connected()

            t = QTimer()
            t.timeout.connect(delayed_start)
            t.setSingleShot(True)
            t.setInterval(100)
            t.start()
            self.delayed_start_timer = t
        else:
            self.on_connection_error()

    def stop(self):
        self.update_timer.stop()
        # self.set_timestamp_timer.stop()
        self.clear_dirty_params_timer.stop()
        self.print_data_rate_timer.stop()
        self.delayed_start_timer.stop()

        if self.transport and self.transport.isOpen():
            logger.info("closing connection to FOC-Stim")
            connected = True
            try:
                # tcp
                connected = self.transport.state() == QAbstractSocket.SocketState.ConnectedState
            except AttributeError:
                pass

            if self.api and connected:
                self.api.request_stop_signal()
                self.api.cancel_outstanding_requests()
                self.transport.flush()
            self.transport.close()
        if self.notification_log:
            self.notification_log.close()

    def is_connected_and_running(self) -> bool:
        return self.transport and self.transport.isOpen()

    def on_transport_connected(self):
        logger.info("connection established")

        if self.dump_notifications:
            now = datetime.datetime.now()
            datestr = now.strftime("%Y-%m-%d %H%M%S")
            try:
                os.mkdir('trace/')
            except FileExistsError:
                pass
            self.notification_log = stream.open(f'trace/focstim-notifications {datestr}.binpb', 'wb')
        else:
            self.notification_log = None

        self.api = FOCStimProtoAPI(self, self.transport, self.notification_log)
        self.api.on_notification_boot.connect(self.handle_notification_boot)
        self.api.on_notification_potentiometer.connect(self.handle_notification_potentiometer)
        self.api.on_notification_currents.connect(self.handle_notification_currents)
        self.api.on_notification_model_estimation.connect(self.handle_notification_model_estimation)
        self.api.on_notification_system_stats.connect(self.handle_notification_system_stats)
        self.api.on_notification_signal_stats.connect(self.handle_notification_signal_stats)
        self.api.on_notification_battery.connect(self.handle_notification_battery)
        self.api.on_notification_lsm6dsox.connect(self.handle_notification_lsm6dsox)
        self.api.on_notification_pressure.connect(self.handle_notification_pressure)
        self.api.on_notification_debug_string.connect(self.handle_notification_debug_string)
        self.api.on_notification_debug_as5311.connect(self.handle_notification_debug_as5311)

        # Notify that API is ready for external connections
        self.api_ready.emit()

        # grab firmware version
        self.get_firmware_version()

    def get_firmware_version(self):
        logger.info("get firmware version...")
        def on_firmware_timeout(id):
            logger.error("timeout requesting firmware version")
            self.stop()

        def on_firmware_response(response: Response):
            # TODO: check error
            s = google.protobuf.text_format.MessageToString(response.response_firmware_version, as_one_line=True)
            logger.info(s)

            version = response.response_firmware_version.stm32_firmware_version
            if version == FOCSTIM_VERSION:
                self.get_capabilities()
            else:
                logger.error(f"incompatible FOC-Stim version. Found '{version}' Needs '{FOCSTIM_VERSION}'.")
                self.stop()

        fut = self.api.request_firmware_version()
        fut.set_timeout(TIMEOUT_SETUP)
        fut.on_timeout.connect(on_firmware_timeout)
        fut.on_result.connect(on_firmware_response)

    def get_capabilities(self):
        logger.info("get device capabilities...")
        def on_capabilities_timeout(id):
            logger.error("timeout requesting capabilities")
            self.stop()

        def on_capabilities_response(response: Response):
            # TODO: check error
            s = google.protobuf.text_format.MessageToString(response.response_capabilities_get, as_one_line=True, print_unknown_fields=True)
            logger.info(s)
            if response.response_capabilities_get.lsm6dsox:
                self.start_lsm6dsox()
            else:
                self.start_signal_generation()

        fut = self.api.request_capabilities_get()
        fut.set_timeout(TIMEOUT_SETUP)
        fut.on_timeout.connect(on_capabilities_timeout)
        fut.on_result.connect(on_capabilities_response)

    def start_lsm6dsox(self):
        logger.info("starting IMU datastream...")

        def on_lsm6dsox_timeout(id):
            logger.error("timeout requesting capabilities")
            self.stop()

        def on_lsm6dsox_response(response: Response):
            s = google.protobuf.text_format.MessageToString(response.response_lsm6dsox_start, as_one_line=True,
                                                            print_unknown_fields=True)
            logger.info(s)
            self.acc_sensitivity = response.response_lsm6dsox_start.acc_sensitivity
            self.gyr_sensitivity = response.response_lsm6dsox_start.gyr_sensitivity
            self.start_signal_generation()

        fut = self.api.request_lsm6dsox_start(LSM6DSOX_SAMPLERATE_HZ, LSM6DSOX_ACC_FULLSCALE, LSM6DSOX_GYR_FULLSCALE)
        fut.set_timeout(TIMEOUT_SETUP)
        fut.on_timeout.connect(on_lsm6dsox_timeout)
        fut.on_result.connect(on_lsm6dsox_response)

    def start_signal_generation(self):
        logger.info("start signal...")
        # send initial parameters
        self.transmit_dirty_params(0)

        def on_signal_start_timeout(id):
            logger.error("timeout starting signal")
            self.stop()

        def on_signal_start_response(response: Response):
            if response.HasField("error"):
                s = google.protobuf.text_format.MessageToString(response.error, as_one_line=True, print_unknown_fields=True)
                logger.error(s)
                self.stop()
            else:
                logger.info("signal generation started!")
                self.start_transmit_loop()

        if self.algorithm.outputs() == 3:
            mode = OutputMode.OUTPUT_THREEPHASE
        elif self.algorithm.outputs() == 4:
            mode = OutputMode.OUTPUT_FOURPHASE
        else:
            assert False
        fut = self.api.request_start_signal(mode)
        fut.set_timeout(TIMEOUT_SETUP)
        fut.on_timeout.connect(on_signal_start_timeout)
        fut.on_result.connect(on_signal_start_response)

    def start_transmit_loop(self):
        # start the set timestamp loop
        # self.set_timestamp_timer.start()
        # self.timeout_set_timestamp()
        self.clear_dirty_params_timer.start()
        self.update_timer.start()

    def on_connection_error(self):
        logger.error(f"connection error: {self.transport.errorString()}")
        self.stop()

    def generic_timeout(self, id):
        if self.transport.isOpen():
            logger.error(f"FOC-Stim request {id} timed out")
            logger.error(f"pending requests: f{self.api.pending_requests.keys()}")
            self.stop()

    def transmit_dirty_params(self, interval=30):
        if self.teleplot:
            self.teleplot.write_metrics(
                event_loop_latency=(time.time() - self.last_update) * 1000
            )
        self.last_update = time.time()

        if len(self.api.pending_requests) > 20:
            # avoid spamming updates during minor connection interruptions
            return

        new_dict = self.algorithm.parameter_dict()

        transmit_time = time.time()
        def completed(_):
            elapsed = time.time() - transmit_time
            # self.teleplot.write_metrics(latency=elapsed)
            if elapsed > self.max_latency:
                self.max_latency = elapsed
                logger.warning(f"max command latency: {elapsed} seconds")

        # send only dirty values
        for axis, value in new_dict.items():
            if axis not in self.old_dict or value != self.old_dict[axis]:
                # self.request_axis_set(axis, value, False)
                fut = self.api.request_axis_move_to(axis, value, interval)
                fut.set_timeout(TIMEOUT_UPDATE)
                fut.on_timeout.connect(self.generic_timeout)
                fut.on_result.connect(completed)

                self.updates_sent += 1

        self.old_dict = new_dict

    def clear_dirty_params(self):
        self.old_dict = {}

    # def timeout_set_timestamp(self):
    #     transmit_time = time.time()
    #     def completed(response):
    #         # print(response)
    #         # if self.teleplot_socket:
    #         #     msg = f"""
    #         #              latency3:{(time.time() - transmit_time) * 1000}
    #         #              change_ms:{response.response_timestamp_set.change_ms}
    #         #          """
    #         #     self.teleplot_socket.write(msg.encode('utf-8'))
    #         pass
    #
    #     fut = self.api.request_set_timestamp()
    #     fut.set_timeout(2000)
    #     fut.on_timeout.connect(self.generic_timeout)
    #     fut.on_result.connect(completed)

    def handle_notification_boot(self, notif: NotificationBoot):
        logger.error('boot notification received')
        self.stop()

    def handle_notification_potentiometer(self, notif: NotificationPotentiometer):
        if self.teleplot:
            self.teleplot.write_metrics(
                pot=notif.value
            )

    def handle_notification_currents(self, notif: NotificationCurrents):
        # print(notif)
        if self.teleplot:
            self.teleplot.write_metrics(
                rms_a=notif.rms_a,
                rms_b=notif.rms_b,
                rms_c=notif.rms_c,
                rms_d=notif.rms_d,
                max_a=notif.peak_a,
                max_b=notif.peak_b,
                max_c=notif.peak_c,
                max_d=notif.peak_d,
                max_cmd=notif.peak_cmd,
                power_total=notif.output_power,
                power_skin=notif.output_power_skin,
            )

    def handle_notification_model_estimation(self, notif: NotificationModelEstimation):
        if self.teleplot:
            self.teleplot.write_metrics(
                R_a=f"{notif.resistance_a}",
                R_b=f"{notif.resistance_b}",
                R_c=f"{notif.resistance_c}",
                R_d=f"{notif.resistance_d}",
                Z_a=f"{notif.resistance_a}:{notif.reluctance_a}|xy",
                Z_b=f"{notif.resistance_b}:{notif.reluctance_b}|xy",
                Z_c=f"{notif.resistance_c}:{notif.reluctance_c}|xy",
                Z_d=f"{notif.resistance_d}:{notif.reluctance_d}|xy"
            )

    def handle_notification_system_stats(self, notif: NotificationSystemStats):
        if notif.HasField('esc1'):
            if self.teleplot:
                self.teleplot.write_metrics(
                    temp_stm32=notif.esc1.temp_stm32,
                    temp_board=notif.esc1.temp_board,
                    v_bus=notif.esc1.v_bus
                )
        elif notif.HasField('focstimv3'):
            if self.teleplot:
                self.teleplot.write_metrics(
                    temp_stm32=notif.focstimv3.temp_stm32,
                    boost_duty_cycle=notif.focstimv3.boost_duty_cycle,
                    v_boost_min=notif.focstimv3.v_boost_min,
                    v_boost_max=notif.focstimv3.v_boost_max,
                    v_sys_min=notif.focstimv3.v_sys_min,
                    v_sys_max=notif.focstimv3.v_sys_max,
                )

    def handle_notification_signal_stats(self, notif: NotificationSignalStats):
        if self.teleplot:
            self.teleplot.write_metrics(
                pulse_frequency=notif.actual_pulse_frequency,
                v_drive=notif.v_drive
            )

    def handle_notification_battery(self, notif: NotificationBattery):
        if self.teleplot:
            self.teleplot.write_metrics(
                battery_voltage=notif.battery_voltage,
                battery_charge_rate=notif.battery_charge_rate_watt,
                battery_soc=notif.battery_soc,
                temp_bq27411=notif.chip_temperature,
            )

    def handle_notification_lsm6dsox(self, notif: NotificationLSM6DSOX):
        if self.acc_sensitivity and self.gyr_sensitivity:
            self.new_imu_sensor_data.emit(
                IMUData(
                    LSM6DSOX_SAMPLERATE_HZ,
                    notif.acc_x * self.acc_sensitivity,
                    notif.acc_y * self.acc_sensitivity,
                    notif.acc_z * self.acc_sensitivity,
                    notif.gyr_x * self.gyr_sensitivity,
                    notif.gyr_y * self.gyr_sensitivity,
                    notif.gyr_z * self.gyr_sensitivity,
                )
            )

    def handle_notification_pressure(self, notif: NotificationPressure):
        self.new_pressure_sensor_data.emit(
            PressureData(notif.pressure)
        )

    def handle_notification_debug_string(self, notif: NotificationDebugString):
        logger.warning(notif.message)

    def handle_notification_debug_as5311(self, notif: NotificationDebugAS5311):
        if self.teleplot:
            self.teleplot.write_metrics(
                as5311_raw=notif.raw,
                as5311_um=notif.tracked * (2000.0 / 4096),
                as5311_flags=notif.flags,
            )
        m = notif.tracked * (2000.0 / 4096) * 1e-6
        self.new_as5311_sensor_data.emit(AS5311Data(m))

    new_imu_sensor_data = Signal(IMUData)
    new_as5311_sensor_data = Signal(AS5311Data)
    new_pressure_sensor_data = Signal(PressureData)
    api_ready = Signal()