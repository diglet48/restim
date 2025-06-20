"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'focstim_rpc.proto')
_sym_db = _symbol_database.Default()
from . import notifications_pb2 as notifications__pb2
from . import messages_pb2 as messages__pb2
from . import constants_pb2 as constants__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11focstim_rpc.proto\x12\x0bfocstim_rpc\x1a\x13notifications.proto\x1a\x0emessages.proto\x1a\x0fconstants.proto"\xe3\x04\n\x0cNotification\x12:\n\x11notification_boot\x18\x01 \x01(\x0b2\x1d.focstim_rpc.NotificationBootH\x00\x12L\n\x1anotification_potentiometer\x18\x02 \x01(\x0b2&.focstim_rpc.NotificationPotentiometerH\x00\x12B\n\x15notification_currents\x18\x03 \x01(\x0b2!.focstim_rpc.NotificationCurrentsH\x00\x12Q\n\x1dnotification_model_estimation\x18\x04 \x01(\x0b2(.focstim_rpc.NotificationModelEstimationH\x00\x12I\n\x19notification_system_stats\x18\x05 \x01(\x0b2$.focstim_rpc.NotificationSystemStatsH\x00\x12I\n\x19notification_signal_stats\x18\x06 \x01(\x0b2$.focstim_rpc.NotificationSignalStatsH\x00\x12@\n\x14notification_battery\x18\x07 \x01(\x0b2 .focstim_rpc.NotificationBatteryH\x00\x12J\n\x19notification_debug_string\x18\xe8\x07 \x01(\x0b2$.focstim_rpc.NotificationDebugStringH\x00B\x0e\n\x0cnotification"\xa6\x05\n\x07Request\x12\n\n\x02id\x18\x01 \x01(\r\x12H\n\x18request_firmware_version\x18\xf4\x03 \x01(\x0b2#.focstim_rpc.RequestFirmwareVersionH\x00\x12H\n\x18request_capabilities_get\x18\xf5\x03 \x01(\x0b2#.focstim_rpc.RequestCapabilitiesGetH\x00\x12@\n\x14request_signal_start\x18\xf6\x03 \x01(\x0b2\x1f.focstim_rpc.RequestSignalStartH\x00\x12>\n\x13request_signal_stop\x18\xf7\x03 \x01(\x0b2\x1e.focstim_rpc.RequestSignalStopH\x00\x12>\n\x14request_axis_move_to\x18\x05 \x01(\x0b2\x1e.focstim_rpc.RequestAxisMoveToH\x00\x12B\n\x15request_timestamp_set\x18\xf8\x03 \x01(\x0b2 .focstim_rpc.RequestTimestampSetH\x00\x12B\n\x15request_timestamp_get\x18\xf9\x03 \x01(\x0b2 .focstim_rpc.RequestTimestampGetH\x00\x12R\n\x1erequest_debug_stm32_deep_sleep\x18\xe8\x07 \x01(\x0b2\'.focstim_rpc.RequestDebugStm32DeepSleepH\x00\x12S\n\x1erequest_debug_enter_bootloader\x18\xe9\x07 \x01(\x0b2(.focstim_rpc.RequestDebugEnterBootloaderH\x00B\x08\n\x06params"\x85\x05\n\x08Response\x12\n\n\x02id\x18\x01 \x01(\r\x12J\n\x19response_firmware_version\x18\xf4\x03 \x01(\x0b2$.focstim_rpc.ResponseFirmwareVersionH\x00\x12J\n\x19response_capabilities_get\x18\xf5\x03 \x01(\x0b2$.focstim_rpc.ResponseCapabilitiesGetH\x00\x12B\n\x15response_signal_start\x18\xf6\x03 \x01(\x0b2 .focstim_rpc.ResponseSignalStartH\x00\x12@\n\x14response_signal_stop\x18\xf7\x03 \x01(\x0b2\x1f.focstim_rpc.ResponseSignalStopH\x00\x12@\n\x15response_axis_move_to\x18\x05 \x01(\x0b2\x1f.focstim_rpc.ResponseAxisMoveToH\x00\x12D\n\x16response_timestamp_set\x18\xf8\x03 \x01(\x0b2!.focstim_rpc.ResponseTimestampSetH\x00\x12D\n\x16response_timestamp_get\x18\xf9\x03 \x01(\x0b2!.focstim_rpc.ResponseTimestampGetH\x00\x12T\n\x1fresponse_debug_stm32_deep_sleep\x18\xe8\x07 \x01(\x0b2(.focstim_rpc.ResponseDebugStm32DeepSleepH\x00\x12!\n\x05error\x18\x03 \x01(\x0b2\x12.focstim_rpc.ErrorB\x08\n\x06result"*\n\x05Error\x12!\n\x04code\x18\x01 \x01(\x0e2\x13.focstim_rpc.Errors"\x9e\x01\n\nRpcMessage\x12\'\n\x07request\x18\x02 \x01(\x0b2\x14.focstim_rpc.RequestH\x00\x12)\n\x08response\x18\x04 \x01(\x0b2\x15.focstim_rpc.ResponseH\x00\x121\n\x0cnotification\x18\x05 \x01(\x0b2\x19.focstim_rpc.NotificationH\x00B\t\n\x07messageb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'focstim_rpc_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_NOTIFICATION']._serialized_start = 89
    _globals['_NOTIFICATION']._serialized_end = 700
    _globals['_REQUEST']._serialized_start = 703
    _globals['_REQUEST']._serialized_end = 1381
    _globals['_RESPONSE']._serialized_start = 1384
    _globals['_RESPONSE']._serialized_end = 2029
    _globals['_ERROR']._serialized_start = 2031
    _globals['_ERROR']._serialized_end = 2073
    _globals['_RPCMESSAGE']._serialized_start = 2076
    _globals['_RPCMESSAGE']._serialized_end = 2234