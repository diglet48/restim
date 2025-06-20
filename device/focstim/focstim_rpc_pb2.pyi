import notifications_pb2 as _notifications_pb2
import messages_pb2 as _messages_pb2
import constants_pb2 as _constants_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Notification(_message.Message):
    __slots__ = ('notification_boot', 'notification_potentiometer', 'notification_currents', 'notification_model_estimation', 'notification_system_stats', 'notification_signal_stats', 'notification_battery', 'notification_debug_string')
    NOTIFICATION_BOOT_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_POTENTIOMETER_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_CURRENTS_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_MODEL_ESTIMATION_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_SYSTEM_STATS_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_SIGNAL_STATS_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_BATTERY_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_DEBUG_STRING_FIELD_NUMBER: _ClassVar[int]
    notification_boot: _notifications_pb2.NotificationBoot
    notification_potentiometer: _notifications_pb2.NotificationPotentiometer
    notification_currents: _notifications_pb2.NotificationCurrents
    notification_model_estimation: _notifications_pb2.NotificationModelEstimation
    notification_system_stats: _notifications_pb2.NotificationSystemStats
    notification_signal_stats: _notifications_pb2.NotificationSignalStats
    notification_battery: _notifications_pb2.NotificationBattery
    notification_debug_string: _notifications_pb2.NotificationDebugString

    def __init__(self, notification_boot: _Optional[_Union[_notifications_pb2.NotificationBoot, _Mapping]]=..., notification_potentiometer: _Optional[_Union[_notifications_pb2.NotificationPotentiometer, _Mapping]]=..., notification_currents: _Optional[_Union[_notifications_pb2.NotificationCurrents, _Mapping]]=..., notification_model_estimation: _Optional[_Union[_notifications_pb2.NotificationModelEstimation, _Mapping]]=..., notification_system_stats: _Optional[_Union[_notifications_pb2.NotificationSystemStats, _Mapping]]=..., notification_signal_stats: _Optional[_Union[_notifications_pb2.NotificationSignalStats, _Mapping]]=..., notification_battery: _Optional[_Union[_notifications_pb2.NotificationBattery, _Mapping]]=..., notification_debug_string: _Optional[_Union[_notifications_pb2.NotificationDebugString, _Mapping]]=...) -> None:
        ...

class Request(_message.Message):
    __slots__ = ('id', 'request_firmware_version', 'request_capabilities_get', 'request_signal_start', 'request_signal_stop', 'request_axis_move_to', 'request_timestamp_set', 'request_timestamp_get', 'request_debug_stm32_deep_sleep', 'request_debug_enter_bootloader')
    ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIRMWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_CAPABILITIES_GET_FIELD_NUMBER: _ClassVar[int]
    REQUEST_SIGNAL_START_FIELD_NUMBER: _ClassVar[int]
    REQUEST_SIGNAL_STOP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_AXIS_MOVE_TO_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIMESTAMP_SET_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIMESTAMP_GET_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DEBUG_STM32_DEEP_SLEEP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DEBUG_ENTER_BOOTLOADER_FIELD_NUMBER: _ClassVar[int]
    id: int
    request_firmware_version: _messages_pb2.RequestFirmwareVersion
    request_capabilities_get: _messages_pb2.RequestCapabilitiesGet
    request_signal_start: _messages_pb2.RequestSignalStart
    request_signal_stop: _messages_pb2.RequestSignalStop
    request_axis_move_to: _messages_pb2.RequestAxisMoveTo
    request_timestamp_set: _messages_pb2.RequestTimestampSet
    request_timestamp_get: _messages_pb2.RequestTimestampGet
    request_debug_stm32_deep_sleep: _messages_pb2.RequestDebugStm32DeepSleep
    request_debug_enter_bootloader: _messages_pb2.RequestDebugEnterBootloader

    def __init__(self, id: _Optional[int]=..., request_firmware_version: _Optional[_Union[_messages_pb2.RequestFirmwareVersion, _Mapping]]=..., request_capabilities_get: _Optional[_Union[_messages_pb2.RequestCapabilitiesGet, _Mapping]]=..., request_signal_start: _Optional[_Union[_messages_pb2.RequestSignalStart, _Mapping]]=..., request_signal_stop: _Optional[_Union[_messages_pb2.RequestSignalStop, _Mapping]]=..., request_axis_move_to: _Optional[_Union[_messages_pb2.RequestAxisMoveTo, _Mapping]]=..., request_timestamp_set: _Optional[_Union[_messages_pb2.RequestTimestampSet, _Mapping]]=..., request_timestamp_get: _Optional[_Union[_messages_pb2.RequestTimestampGet, _Mapping]]=..., request_debug_stm32_deep_sleep: _Optional[_Union[_messages_pb2.RequestDebugStm32DeepSleep, _Mapping]]=..., request_debug_enter_bootloader: _Optional[_Union[_messages_pb2.RequestDebugEnterBootloader, _Mapping]]=...) -> None:
        ...

class Response(_message.Message):
    __slots__ = ('id', 'response_firmware_version', 'response_capabilities_get', 'response_signal_start', 'response_signal_stop', 'response_axis_move_to', 'response_timestamp_set', 'response_timestamp_get', 'response_debug_stm32_deep_sleep', 'error')
    ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIRMWARE_VERSION_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_CAPABILITIES_GET_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_SIGNAL_START_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_SIGNAL_STOP_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_AXIS_MOVE_TO_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TIMESTAMP_SET_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TIMESTAMP_GET_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_DEBUG_STM32_DEEP_SLEEP_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: int
    response_firmware_version: _messages_pb2.ResponseFirmwareVersion
    response_capabilities_get: _messages_pb2.ResponseCapabilitiesGet
    response_signal_start: _messages_pb2.ResponseSignalStart
    response_signal_stop: _messages_pb2.ResponseSignalStop
    response_axis_move_to: _messages_pb2.ResponseAxisMoveTo
    response_timestamp_set: _messages_pb2.ResponseTimestampSet
    response_timestamp_get: _messages_pb2.ResponseTimestampGet
    response_debug_stm32_deep_sleep: _messages_pb2.ResponseDebugStm32DeepSleep
    error: Error

    def __init__(self, id: _Optional[int]=..., response_firmware_version: _Optional[_Union[_messages_pb2.ResponseFirmwareVersion, _Mapping]]=..., response_capabilities_get: _Optional[_Union[_messages_pb2.ResponseCapabilitiesGet, _Mapping]]=..., response_signal_start: _Optional[_Union[_messages_pb2.ResponseSignalStart, _Mapping]]=..., response_signal_stop: _Optional[_Union[_messages_pb2.ResponseSignalStop, _Mapping]]=..., response_axis_move_to: _Optional[_Union[_messages_pb2.ResponseAxisMoveTo, _Mapping]]=..., response_timestamp_set: _Optional[_Union[_messages_pb2.ResponseTimestampSet, _Mapping]]=..., response_timestamp_get: _Optional[_Union[_messages_pb2.ResponseTimestampGet, _Mapping]]=..., response_debug_stm32_deep_sleep: _Optional[_Union[_messages_pb2.ResponseDebugStm32DeepSleep, _Mapping]]=..., error: _Optional[_Union[Error, _Mapping]]=...) -> None:
        ...

class Error(_message.Message):
    __slots__ = ('code',)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: _constants_pb2.Errors

    def __init__(self, code: _Optional[_Union[_constants_pb2.Errors, str]]=...) -> None:
        ...

class RpcMessage(_message.Message):
    __slots__ = ('request', 'response', 'notification')
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    request: Request
    response: Response
    notification: Notification

    def __init__(self, request: _Optional[_Union[Request, _Mapping]]=..., response: _Optional[_Union[Response, _Mapping]]=..., notification: _Optional[_Union[Notification, _Mapping]]=...) -> None:
        ...