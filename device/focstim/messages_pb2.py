"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'messages.proto')
_sym_db = _symbol_database.Default()
from . import constants_pb2 as constants__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\x12\x0bfocstim_rpc\x1a\x0fconstants.proto"b\n\x0fFirmwareVersion\x12\r\n\x05major\x18\x01 \x01(\r\x12\r\n\x05minor\x18\x02 \x01(\r\x12\x10\n\x08revision\x18\x03 \x01(\r\x12\x0e\n\x06branch\x18\x04 \x01(\t\x12\x0f\n\x07comment\x18\x05 \x01(\t"\x18\n\x16RequestFirmwareVersion"\x86\x01\n\x17ResponseFirmwareVersion\x12+\n\x05board\x18\x01 \x01(\x0e2\x1c.focstim_rpc.BoardIdentifier\x12>\n\x18stm32_firmware_version_2\x18\x03 \x01(\x0b2\x1c.focstim_rpc.FirmwareVersion"\x18\n\x16RequestCapabilitiesGet"\xa3\x01\n\x17ResponseCapabilitiesGet\x12\x12\n\nthreephase\x18\x01 \x01(\x08\x12\x11\n\tfourphase\x18\x02 \x01(\x08\x12\x0f\n\x07battery\x18\x03 \x01(\x08\x12\x15\n\rpotentiometer\x18\x04 \x01(\x08\x12\'\n\x1fmaximum_waveform_amplitude_amps\x18\x05 \x01(\x02\x12\x10\n\x08lsm6dsox\x18\x06 \x01(\x08";\n\x12RequestSignalStart\x12%\n\x04mode\x18\x01 \x01(\x0e2\x17.focstim_rpc.OutputMode"\x15\n\x13ResponseSignalStart"\x13\n\x11RequestSignalStop"\x14\n\x12ResponseSignalStop"\x10\n\x0eRequestModeSet"\x11\n\x0fResponseModeSet"Y\n\x11RequestAxisMoveTo\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\r\n\x05value\x18\x03 \x01(\x02\x12\x10\n\x08interval\x18\x04 \x01(\r"\x14\n\x12ResponseAxisMoveTo"i\n\x0eRequestAxisSet\x12#\n\x04axis\x18\x01 \x01(\x0e2\x15.focstim_rpc.AxisType\x12\x14\n\x0ctimestamp_ms\x18\x02 \x01(\x07\x12\r\n\x05value\x18\x03 \x01(\x02\x12\r\n\x05clear\x18\x04 \x01(\x08"\x11\n\x0fResponseAxisSet"+\n\x13RequestTimestampSet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x04"N\n\x14ResponseTimestampSet\x12\x11\n\toffset_ms\x18\x01 \x01(\x03\x12\x11\n\tchange_ms\x18\x02 \x01(\x12\x12\x10\n\x08error_ms\x18\x03 \x01(\x12"\x15\n\x13RequestTimestampGet"G\n\x14ResponseTimestampGet\x12\x14\n\x0ctimestamp_ms\x18\x01 \x01(\x07\x12\x19\n\x11unix_timestamp_ms\x18\x02 \x01(\x04":\n\x18RequestWifiParametersSet\x12\x0c\n\x04ssid\x18\x01 \x01(\x0c\x12\x10\n\x08password\x18\x02 \x01(\x0c"\x1b\n\x19ResponseWifiParametersSet"\x12\n\x10RequestWifiIPGet"\x1f\n\x11ResponseWifiIPGet\x12\n\n\x02ip\x18\x01 \x01(\r"\\\n\x14RequestLSM6DSOXStart\x12\x16\n\x0eimu_samplerate\x18\x01 \x01(\x02\x12\x15\n\racc_fullscale\x18\x02 \x01(\x02\x12\x15\n\rgyr_fullscale\x18\x03 \x01(\x02"I\n\x15ResponseLSM6DSOXStart\x12\x17\n\x0facc_sensitivity\x18\x01 \x01(\x02\x12\x17\n\x0fgyr_sensitivity\x18\x02 \x01(\x02"\x15\n\x13RequestLSM6DSOXStop"\x16\n\x14ResponseLSM6DSOXStop"\x1c\n\x1aRequestDebugStm32DeepSleep"\x1d\n\x1bResponseDebugStm32DeepSleep"\x1d\n\x1bRequestDebugEnterBootloaderb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messages_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_FIRMWAREVERSION']._serialized_start = 48
    _globals['_FIRMWAREVERSION']._serialized_end = 146
    _globals['_REQUESTFIRMWAREVERSION']._serialized_start = 148
    _globals['_REQUESTFIRMWAREVERSION']._serialized_end = 172
    _globals['_RESPONSEFIRMWAREVERSION']._serialized_start = 175
    _globals['_RESPONSEFIRMWAREVERSION']._serialized_end = 309
    _globals['_REQUESTCAPABILITIESGET']._serialized_start = 311
    _globals['_REQUESTCAPABILITIESGET']._serialized_end = 335
    _globals['_RESPONSECAPABILITIESGET']._serialized_start = 338
    _globals['_RESPONSECAPABILITIESGET']._serialized_end = 501
    _globals['_REQUESTSIGNALSTART']._serialized_start = 503
    _globals['_REQUESTSIGNALSTART']._serialized_end = 562
    _globals['_RESPONSESIGNALSTART']._serialized_start = 564
    _globals['_RESPONSESIGNALSTART']._serialized_end = 585
    _globals['_REQUESTSIGNALSTOP']._serialized_start = 587
    _globals['_REQUESTSIGNALSTOP']._serialized_end = 606
    _globals['_RESPONSESIGNALSTOP']._serialized_start = 608
    _globals['_RESPONSESIGNALSTOP']._serialized_end = 628
    _globals['_REQUESTMODESET']._serialized_start = 630
    _globals['_REQUESTMODESET']._serialized_end = 646
    _globals['_RESPONSEMODESET']._serialized_start = 648
    _globals['_RESPONSEMODESET']._serialized_end = 665
    _globals['_REQUESTAXISMOVETO']._serialized_start = 667
    _globals['_REQUESTAXISMOVETO']._serialized_end = 756
    _globals['_RESPONSEAXISMOVETO']._serialized_start = 758
    _globals['_RESPONSEAXISMOVETO']._serialized_end = 778
    _globals['_REQUESTAXISSET']._serialized_start = 780
    _globals['_REQUESTAXISSET']._serialized_end = 885
    _globals['_RESPONSEAXISSET']._serialized_start = 887
    _globals['_RESPONSEAXISSET']._serialized_end = 904
    _globals['_REQUESTTIMESTAMPSET']._serialized_start = 906
    _globals['_REQUESTTIMESTAMPSET']._serialized_end = 949
    _globals['_RESPONSETIMESTAMPSET']._serialized_start = 951
    _globals['_RESPONSETIMESTAMPSET']._serialized_end = 1029
    _globals['_REQUESTTIMESTAMPGET']._serialized_start = 1031
    _globals['_REQUESTTIMESTAMPGET']._serialized_end = 1052
    _globals['_RESPONSETIMESTAMPGET']._serialized_start = 1054
    _globals['_RESPONSETIMESTAMPGET']._serialized_end = 1125
    _globals['_REQUESTWIFIPARAMETERSSET']._serialized_start = 1127
    _globals['_REQUESTWIFIPARAMETERSSET']._serialized_end = 1185
    _globals['_RESPONSEWIFIPARAMETERSSET']._serialized_start = 1187
    _globals['_RESPONSEWIFIPARAMETERSSET']._serialized_end = 1214
    _globals['_REQUESTWIFIIPGET']._serialized_start = 1216
    _globals['_REQUESTWIFIIPGET']._serialized_end = 1234
    _globals['_RESPONSEWIFIIPGET']._serialized_start = 1236
    _globals['_RESPONSEWIFIIPGET']._serialized_end = 1267
    _globals['_REQUESTLSM6DSOXSTART']._serialized_start = 1269
    _globals['_REQUESTLSM6DSOXSTART']._serialized_end = 1361
    _globals['_RESPONSELSM6DSOXSTART']._serialized_start = 1363
    _globals['_RESPONSELSM6DSOXSTART']._serialized_end = 1436
    _globals['_REQUESTLSM6DSOXSTOP']._serialized_start = 1438
    _globals['_REQUESTLSM6DSOXSTOP']._serialized_end = 1459
    _globals['_RESPONSELSM6DSOXSTOP']._serialized_start = 1461
    _globals['_RESPONSELSM6DSOXSTOP']._serialized_end = 1483
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_start = 1485
    _globals['_REQUESTDEBUGSTM32DEEPSLEEP']._serialized_end = 1513
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_start = 1515
    _globals['_RESPONSEDEBUGSTM32DEEPSLEEP']._serialized_end = 1544
    _globals['_REQUESTDEBUGENTERBOOTLOADER']._serialized_start = 1546
    _globals['_REQUESTDEBUGENTERBOOTLOADER']._serialized_end = 1575