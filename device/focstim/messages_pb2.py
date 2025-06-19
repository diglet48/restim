"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'messages.proto')
_sym_db = _symbol_database.Default()
from . import constants_pb2 as constants__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\x12\x0bfocstim_rpc\x1a\x0fconstants.proto"\x18\n\x16RequestFirmwareVersion"f\n\x17ResponseFirmwareVersion\x12+\n\x05board\x18\x01 \x01(\x0e2\x1c.focstim_rpc.BoardIdentifier\x12\x1e\n\x16stm32_firmware_version\x18\x02 \x01(\t"\x18\n\x16RequestCapabilitiesGet"\x91\x01\n\x17ResponseCapabilitiesGet\x12\x12\n\nthreephase\x18\x01 \x01(\x08\x12\x11\n\tfourphase\x18\x02 \x01(\x08\x12\x0f\n\x07battery\x18\x03 \x01(\x08\x12\x15\n\rpotentiometer\x18\x04 \x01(\x08\x12\'\n\x1fmaximum_waveform_amplitude_amps\x18\x05 \x01(\x02";\n\x12RequestSignalStart\x12%\n\x04mode\x18\x01 \x01(\x0e2\x17.focstim_rpc.OutputMode"\x15\n\x13ResponseSignalStart"\x13\n\x11RequestSignalStop"\x14\n\x12ResponseSignalStop"\x10\n\x0eRequestModeSet"\x11\n\x0fResponseModeSet"Y\n\x11RequestAxisMoveTo\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\r\n\x05value\x18\x03 \x01(\x02\x12\x10\n\x08interval\x18\x04 \x01(\r"\x14\n\x12ResponseAxisMoveTo"i\n\x0eRequestAxisSet\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\x14\n\x0ctimestamp_ms\x18\x02 \x01(\x07\x12\r\n\x05value\x18\x03 \x01(\x02\x12\r\n\x05clear\x18\x04 \x01(\x08"\x11\n\x0fResponseAxisSet"+\n\x13RequestTimestampSet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x04"N\n\x14ResponseTimestampSet\x12\x11\n\toffset_ms\x18\x01 \x01(\x03\x12\x11\n\tchange_ms\x18\x02 \x01(\x12\x12\x10\n\x08error_ms\x18\x03 \x01(\x12"\x15\n\x13RequestTimestampGet"G\n\x14ResponseTimestampGet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x07\x12\x19\n\x11unix_timestamp_ms\x18\x02 \x01(\x04"\x1c\n\x1aRequestDebugStm32DeepSleep"\x1d\n\x1bResponseDebugStm32DeepSleepb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messages_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_REQUESTFIRMWAREVERSION']._serialized_start = 48
    _globals['_REQUESTFIRMWAREVERSION']._serialized_end = 72
    _globals['_RESPONSEFIRMWAREVERSION']._serialized_start = 74
    _globals['_RESPONSEFIRMWAREVERSION']._serialized_end = 176
    _globals['_REQUESTCAPABILITIESGET']._serialized_start = 178
    _globals['_REQUESTCAPABILITIESGET']._serialized_end = 202
    _globals['_RESPONSECAPABILITIESGET']._serialized_start = 205
    _globals['_RESPONSECAPABILITIESGET']._serialized_end = 350
    _globals['_REQUESTSIGNALSTART']._serialized_start = 352
    _globals['_REQUESTSIGNALSTART']._serialized_end = 411
    _globals['_RESPONSESIGNALSTART']._serialized_start = 413
    _globals['_RESPONSESIGNALSTART']._serialized_end = 434
    _globals['_REQUESTSIGNALSTOP']._serialized_start = 436
    _globals['_REQUESTSIGNALSTOP']._serialized_end = 455
    _globals['_RESPONSESIGNALSTOP']._serialized_start = 457
    _globals['_RESPONSESIGNALSTOP']._serialized_end = 477
    _globals['_REQUESTMODESET']._serialized_start = 479
    _globals['_REQUESTMODESET']._serialized_end = 495
    _globals['_RESPONSEMODESET']._serialized_start = 497
    _globals['_RESPONSEMODESET']._serialized_end = 514
    _globals['_REQUESTAXISMOVETO']._serialized_start = 516
    _globals['_REQUESTAXISMOVETO']._serialized_end = 605
    _globals['_RESPONSEAXISMOVETO']._serialized_start = 607
    _globals['_RESPONSEAXISMOVETO']._serialized_end = 627
    _globals['_REQUESTAXISSET']._serialized_start = 629
    _globals['_REQUESTAXISSET']._serialized_end = 734
    _globals['_RESPONSEAXISSET']._serialized_start = 736
    _globals['_RESPONSEAXISSET']._serialized_end = 753
    _globals['_REQUESTTIMESTAMPSET']._serialized_start = 755
    _globals['_REQUESTTIMESTAMPSET']._serialized_end = 798
    _globals['_RESPONSETIMESTAMPSET']._serialized_start = 800
    _globals['_RESPONSETIMESTAMPSET']._serialized_end = 878
    _globals['_REQUESTTIMESTAMPGET']._serialized_start = 880
    _globals['_REQUESTTIMESTAMPGET']._serialized_end = 901
    _globals['_RESPONSETIMESTAMPGET']._serialized_start = 903
    _globals['_RESPONSETIMESTAMPGET']._serialized_end = 974
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_start = 976
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_end = 1004
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_start = 1006
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_end = 1035