"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'messages.proto')
_sym_db = _symbol_database.Default()
from . import constants_pb2 as constants__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\x12\x0bfocstim_rpc\x1a\x0fconstants.proto"\x18\n\x16RequestFirmwareVersion"f\n\x17ResponseFirmwareVersion\x12+\n\x05board\x18\x01 \x01(\x0e2\x1c.focstim_rpc.BoardIdentifier\x12\x1e\n\x16stm32_firmware_version\x18\x02 \x01(\t"\x18\n\x16RequestCapabilitiesGet"\xa3\x01\n\x17ResponseCapabilitiesGet\x12\x12\n\nthreephase\x18\x01 \x01(\x08\x12\x11\n\tfourphase\x18\x02 \x01(\x08\x12\x0f\n\x07battery\x18\x03 \x01(\x08\x12\x15\n\rpotentiometer\x18\x04 \x01(\x08\x12\'\n\x1fmaximum_waveform_amplitude_amps\x18\x05 \x01(\x02\x12\x10\n\x08lsm6dsox\x18\x06 \x01(\x08";\n\x12RequestSignalStart\x12%\n\x04mode\x18\x01 \x01(\x0e2\x17.focstim_rpc.OutputMode"\x15\n\x13ResponseSignalStart"\x13\n\x11RequestSignalStop"\x14\n\x12ResponseSignalStop"\x10\n\x0eRequestModeSet"\x11\n\x0fResponseModeSet"Y\n\x11RequestAxisMoveTo\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\r\n\x05value\x18\x03 \x01(\x02\x12\x10\n\x08interval\x18\x04 \x01(\r"\x14\n\x12ResponseAxisMoveTo"i\n\x0eRequestAxisSet\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\x14\n\x0ctimestamp_ms\x18\x02 \x01(\x07\x12\r\n\x05value\x18\x03 \x01(\x02\x12\r\n\x05clear\x18\x04 \x01(\x08"\x11\n\x0fResponseAxisSet"+\n\x13RequestTimestampSet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x04"N\n\x14ResponseTimestampSet\x12\x11\n\toffset_ms\x18\x01 \x01(\x03\x12\x11\n\tchange_ms\x18\x02 \x01(\x12\x12\x10\n\x08error_ms\x18\x03 \x01(\x12"\x15\n\x13RequestTimestampGet"G\n\x14ResponseTimestampGet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x07\x12\x19\n\x11unix_timestamp_ms\x18\x02 \x01(\x04":\n\x18RequestWifiParametersSet\x12\x0c\n\x04ssid\x18\x01 \x01(\x0c\x12\x10\n\x08password\x18\x02 \x01(\x0c"\x1b\n\x19ResponseWifiParametersSet"\x12\n\x10RequestWifiIPGet"\x1f\n\x11ResponseWifiIPGet\x12\n\n\x02ip\x18\x01 \x01(\r"\\\n\x14RequestLSM6DSOXStart\x12\x16\n\x0eimu_samplerate\x18\x01 \x01(\x02\x12\x15\n\racc_fullscale\x18\x02 \x01(\x02\x12\x15\n\rgyr_fullscale\x18\x03 \x01(\x02"I\n\x15ResponseLSM6DSOXStart\x12\x17\n\x0facc_sensitivity\x18\x01 \x01(\x02\x12\x17\n\x0fgyr_sensitivity\x18\x02 \x01(\x02"\x15\n\x13RequestLSM6DSOXStop"\x16\n\x14ResponseLSM6DSOXStop"\x1c\n\x1aRequestDebugStm32DeepSleep"\x1d\n\x1bResponseDebugStm32DeepSleep"\x1d\n\x1bRequestDebugEnterBootloaderb\x06proto3')
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
    _globals['_RESPONSECAPABILITIESGET']._serialized_end = 368
    _globals['_REQUESTSIGNALSTART']._serialized_start = 370
    _globals['_REQUESTSIGNALSTART']._serialized_end = 429
    _globals['_RESPONSESIGNALSTART']._serialized_start = 431
    _globals['_RESPONSESIGNALSTART']._serialized_end = 452
    _globals['_REQUESTSIGNALSTOP']._serialized_start = 454
    _globals['_REQUESTSIGNALSTOP']._serialized_end = 473
    _globals['_RESPONSESIGNALSTOP']._serialized_start = 475
    _globals['_RESPONSESIGNALSTOP']._serialized_end = 495
    _globals['_REQUESTMODESET']._serialized_start = 497
    _globals['_REQUESTMODESET']._serialized_end = 513
    _globals['_RESPONSEMODESET']._serialized_start = 515
    _globals['_RESPONSEMODESET']._serialized_end = 532
    _globals['_REQUESTAXISMOVETO']._serialized_start = 534
    _globals['_REQUESTAXISMOVETO']._serialized_end = 623
    _globals['_RESPONSEAXISMOVETO']._serialized_start = 625
    _globals['_RESPONSEAXISMOVETO']._serialized_end = 645
    _globals['_REQUESTAXISSET']._serialized_start = 647
    _globals['_REQUESTAXISSET']._serialized_end = 752
    _globals['_RESPONSEAXISSET']._serialized_start = 754
    _globals['_RESPONSEAXISSET']._serialized_end = 771
    _globals['_REQUESTTIMESTAMPSET']._serialized_start = 773
    _globals['_REQUESTTIMESTAMPSET']._serialized_end = 816
    _globals['_RESPONSETIMESTAMPSET']._serialized_start = 818
    _globals['_RESPONSETIMESTAMPSET']._serialized_end = 896
    _globals['_REQUESTTIMESTAMPGET']._serialized_start = 898
    _globals['_REQUESTTIMESTAMPGET']._serialized_end = 919
    _globals['_RESPONSETIMESTAMPGET']._serialized_start = 921
    _globals['_RESPONSETIMESTAMPGET']._serialized_end = 992
    _globals['_REQUESTWIFIPARAMETERSSET']._serialized_start = 994
    _globals['_REQUESTWIFIPARAMETERSSET']._serialized_end = 1052
    _globals['_RESPONSEWIFIPARAMETERSSET']._serialized_start = 1054
    _globals['_RESPONSEWIFIPARAMETERSSET']._serialized_end = 1081
    _globals['_REQUESTWIFIIPGET']._serialized_start = 1083
    _globals['_REQUESTWIFIIPGET']._serialized_end = 1101
    _globals['_RESPONSEWIFIIPGET']._serialized_start = 1103
    _globals['_RESPONSEWIFIIPGET']._serialized_end = 1134
    _globals['_REQUESTLSM6DSOXSTART']._serialized_start = 1136
    _globals['_REQUESTLSM6DSOXSTART']._serialized_end = 1228
    _globals['_RESPONSELSM6DSOXSTART']._serialized_start = 1230
    _globals['_RESPONSELSM6DSOXSTART']._serialized_end = 1303
    _globals['_REQUESTLSM6DSOXSTOP']._serialized_start = 1305
    _globals['_REQUESTLSM6DSOXSTOP']._serialized_end = 1326
    _globals['_RESPONSELSM6DSOXSTOP']._serialized_start = 1328
    _globals['_RESPONSELSM6DSOXSTOP']._serialized_end = 1350
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_start = 1352
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_end = 1380
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_start = 1382
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_end = 1411
    _globals['_REQUESTDEBUGENTERBOOTLOADER']._serialized_start = 1413
    _globals['_REQUESTDEBUGENTERBOOTLOADER']._serialized_end = 1442