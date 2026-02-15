import logging
import random
import time

from PySide6.QtCore import QObject, Signal, QTimer
from google.protobuf.message import DecodeError

from device.focstim.constants_pb2 import AxisType, OutputMode
from device.focstim.focstim_rpc_pb2 import Request, RpcMessage, Response
from device.focstim.hdlc import HDLC
from device.focstim.messages_pb2 import RequestFirmwareVersion, RequestAxisSet, RequestAxisMoveTo, RequestTimestampSet, \
    RequestSignalStart, RequestSignalStop, RequestCapabilitiesGet, RequestDebugStm32DeepSleep, \
    RequestDebugEnterBootloader, RequestWifiParametersSet, RequestWifiIPGet, RequestLSM6DSOXStart, \
    RequestLSM6DSOXStop
from device.focstim.notifications_pb2 import NotificationBoot, NotificationPotentiometer, NotificationCurrents, \
    NotificationModelEstimation, NotificationSystemStats, NotificationSignalStats, NotificationBattery, \
    NotificationLSM6DSOX, NotificationPressure, NotificationDebugString, NotificationDebugAS5311

logger = logging.getLogger('restim.focstim')


class Future(QObject):
    def __init__(self, id):
        super().__init__(None)
        self.completed = False
        self.timer = None
        self.id = id

    def complete(self, response: Response):
        if not self.completed:
            self.timer.stop()
            self.completed = True
            self.on_result.emit(response)

    def timeout(self):
        if not self.completed:
            self.completed = True
            self.on_timeout.emit(self.id)

    def set_timeout(self, timeout_ms):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(timeout_ms)
        self.timer.setSingleShot(True)
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.stop()
        self.timer = None

    on_result = Signal(Response)
    on_timeout = Signal(int)


class FOCStimProtoAPI(QObject):
    def __init__(self, parent, transport, notification_log_target=None):
        super().__init__(parent)
        self.transport = transport
        self.notification_log_target = notification_log_target
        self.bytes_written = 0
        self.bytes_read = 0

        self.hdlc = HDLC()
        self.request_id = random.randint(1, 4096)
        self.pending_requests = {}

        self.transport.readyRead.connect(self.ready_read)

    def cancel_outstanding_requests(self):
        for k, v in self.pending_requests.items():
            v.cancel()
        self.pending_requests.clear()

    def send_request(self, request: Request) -> Future:
        fut = Future(request.id)
        message = RpcMessage(
            request=request
        )
        message_serialized = message.SerializeToString()
        stream = self.hdlc.encode(message_serialized)
        bytes_written = self.transport.write(stream)
        self.bytes_written += bytes_written
        if bytes_written != len(stream):
            if self.transport.isOpen():
                logger.error("error writing to device")
            self.transport.close()
        else:
            # print('write message of length', bytes_written, stream)
            self.pending_requests[message.request.id] = fut
        return fut

    def receive_protobuf_message(self, message: RpcMessage):
        if message.HasField('request'):
            pass

        elif message.HasField('response'):
            try:
                fut = self.pending_requests.pop(message.response.id)
                if fut:
                    fut.complete(message.response)
            except KeyError:
                logger.warning(f"no cb registered for {message.response}")

        elif message.HasField('notification'):
            message.notification.timestamp = time.time_ns()
            if self.notification_log_target:
                try:
                    self.notification_log_target.write(message.notification)
                except ValueError:
                    pass

            if message.notification.HasField('notification_boot'):
                self.on_notification_boot.emit(message.notification.notification_boot)
            elif message.notification.HasField('notification_potentiometer'):
                self.on_notification_potentiometer.emit(message.notification.notification_potentiometer)
            elif message.notification.HasField('notification_currents'):
                self.on_notification_currents.emit(message.notification.notification_currents)
            elif message.notification.HasField('notification_model_estimation'):
                self.on_notification_model_estimation.emit(message.notification.notification_model_estimation)
            elif message.notification.HasField('notification_system_stats'):
                self.on_notification_system_stats.emit(message.notification.notification_system_stats)
            elif message.notification.HasField('notification_signal_stats'):
                self.on_notification_signal_stats.emit(message.notification.notification_signal_stats)
            elif message.notification.HasField('notification_battery'):
                self.on_notification_battery.emit(message.notification.notification_battery)
            elif message.notification.HasField('notification_lsm6dsox'):
                self.on_notification_lsm6dsox.emit(message.notification.notification_lsm6dsox)
            elif message.notification.HasField('notification_pressure'):
                self.on_notification_pressure.emit(message.notification.notification_pressure)
            elif message.notification.HasField('notification_debug_string'):
                self.on_notification_debug_string.emit(message.notification.notification_debug_string)
            elif message.notification.HasField('notification_debug_as5311'):
                self.on_notification_debug_as5311.emit(message.notification.notification_debug_as5311)
            else:
                logger.warning(f'unhandled notification: {message.notification}')

    def ready_read(self):
        while self.transport.bytesAvailable():
            block = bytes(self.transport.read(256))
            self.bytes_read += len(block)
            # logger.info(f'incoming bytes: {block}')
            for frame in self.hdlc.parse(block):
                # logger.info(f'parsed frame ({len(frame)} bytes): {frame}')
                try:
                    msg = RpcMessage.FromString(frame)
                    # logger.info(f'{msg}')
                    self.receive_protobuf_message(msg)
                except DecodeError:
                    logger.error('protobuf decode error')
                    continue

    def next_request_id(self):
        self.request_id = (self.request_id + 1) % 4096
        if self.request_id == 0:
            self.request_id = 1
        return self.request_id

    def request_firmware_version(self) -> Future:
        return self.send_request(Request(
                id=self.next_request_id(),
                request_firmware_version=RequestFirmwareVersion()
            )
        )

    # def request_axis_set(self, axis: AxisType, value, clear: bool) -> Future:
    #     return self.send_request(Request(
    #         id=self.next_request_id(),
    #         request_axis_set=RequestAxisSet(
    #             timestamp_ms=int(time.time_ns() // 1000 // 1000) & 0xFFFFFFFF,  # TODO
    #             axis=axis,
    #             value=value,
    #             clear=clear
    #             )
    #         )
    #     )

    def request_axis_move_to(self, axis: AxisType, value, interval) -> Future:
        return self.send_request(Request(
                id=self.next_request_id(),
                request_axis_move_to=RequestAxisMoveTo(
                    axis=axis,
                    value=value,
                    interval=interval
                )
            )
        )

    def request_set_timestamp(self) -> Future:
        return self.send_request(Request(
                id=self.next_request_id(),
                request_timestamp_set=RequestTimestampSet(
                    timestamp_ms=int(time.time_ns() // 1000 // 1000)
                )
            )
        )

    def request_start_signal(self, mode: OutputMode) -> Future:
        return self.send_request(Request(
                id=self.next_request_id(),
                request_signal_start=RequestSignalStart(
                    mode=mode
                )
            )
        )

    def request_stop_signal(self) -> Future:
        return self.send_request(Request(
                id=self.next_request_id(),
                request_signal_stop=RequestSignalStop()
            )
        )

    def request_capabilities_get(self) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_capabilities_get=RequestCapabilitiesGet()
        ))

    def request_wifi_parameters_set(self, ssid: bytes, password: bytes) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_wifi_parameters_set=RequestWifiParametersSet(
                ssid=ssid,
                password=password
            )
        ))

    def request_wifi_ip_get(self) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_wifi_ip_get=RequestWifiIPGet()
        ))

    def request_lsm6dsox_start(self, imu_samplerate, acc_fullscale, gyr_fullscale) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_lsm6dsox_start=RequestLSM6DSOXStart(
                imu_samplerate=imu_samplerate,
                acc_fullscale=acc_fullscale,
                gyr_fullscale=gyr_fullscale,
            )
        ))

    def request_lsm6dsox_stop(self) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_lsm6dsox_stop=RequestLSM6DSOXStop()
        ))

    def request_debug_stm32_deep_sleep(self) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_debug_stm32_deep_sleep=RequestDebugStm32DeepSleep()
        ))

    def request_debug_enter_bootloader(self) -> Future:
        return self.send_request(Request(
            id=self.next_request_id(),
            request_debug_enter_bootloader=RequestDebugEnterBootloader()
        ))

    on_notification_boot = Signal(NotificationBoot)
    on_notification_potentiometer = Signal(NotificationPotentiometer)
    on_notification_currents = Signal(NotificationCurrents)
    on_notification_model_estimation = Signal(NotificationModelEstimation)
    on_notification_system_stats = Signal(NotificationSystemStats)
    on_notification_signal_stats = Signal(NotificationSignalStats)
    on_notification_battery = Signal(NotificationBattery)
    on_notification_lsm6dsox = Signal(NotificationLSM6DSOX)
    on_notification_pressure = Signal(NotificationPressure)
    on_notification_debug_string = Signal(NotificationDebugString)
    on_notification_debug_as5311 = Signal(NotificationDebugAS5311)
