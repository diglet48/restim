"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'constants.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fconstants.proto\x12\x0bfocstim_rpc*\xfb\x04\n\x08AxisType\x12\x10\n\x0cAXIS_UNKNOWN\x10\x00\x12\x17\n\x13AXIS_POSITION_ALPHA\x10\x01\x12\x16\n\x12AXIS_POSITION_BETA\x10\x02\x12\x17\n\x13AXIS_POSITION_GAMMA\x10\x03\x12 \n\x1cAXIS_WAVEFORM_AMPLITUDE_AMPS\x10\x0b\x12\x1d\n\x19AXIS_CARRIER_FREQUENCY_HZ\x10\x14\x12\x1e\n\x1aAXIS_PULSE_WIDTH_IN_CYCLES\x10\x15\x12\x1f\n\x1bAXIS_PULSE_RISE_TIME_CYCLES\x10\x16\x12\x1b\n\x17AXIS_PULSE_FREQUENCY_HZ\x10\x17\x12&\n"AXIS_PULSE_INTERVAL_RANDOM_PERCENT\x10\x18\x12\x1d\n\x19AXIS_CALIBRATION_3_CENTER\x10\x1e\x12\x19\n\x15AXIS_CALIBRATION_3_UP\x10\x1f\x12\x1b\n\x17AXIS_CALIBRATION_3_LEFT\x10 \x12\x1d\n\x19AXIS_CALIBRATION_4_CENTER\x10(\x12\x18\n\x14AXIS_CALIBRATION_4_A\x10)\x12\x18\n\x14AXIS_CALIBRATION_4_B\x10*\x12\x18\n\x14AXIS_CALIBRATION_4_C\x10+\x12\x18\n\x14AXIS_CALIBRATION_4_D\x10,\x12\x1a\n\x16AXIS_ELECTRODE_1_POWER\x102\x12\x1a\n\x16AXIS_ELECTRODE_2_POWER\x103\x12\x1a\n\x16AXIS_ELECTRODE_3_POWER\x104\x12\x1a\n\x16AXIS_ELECTRODE_4_POWER\x105*R\n\x0fBoardIdentifier\x12\x11\n\rBOARD_UNKNOWN\x10\x00\x12\x16\n\x12BOARD_B_G431B_ESC1\x10\x01\x12\x14\n\x10BOARD_FOCSTIM_V4\x10\x02*y\n\nOutputMode\x12\x12\n\x0eOUTPUT_UNKNOWN\x10\x00\x12\x15\n\x11OUTPUT_THREEPHASE\x10\x02\x12\x14\n\x10OUTPUT_FOURPHASE\x10\x03\x12*\n&OUTPUT_FOURPHASE_INDIVIDUAL_ELECTRODES\x10\x04*T\n\rStreamingMode\x12\x15\n\x11STREAMING_UNKNOWN\x10\x00\x12\x14\n\x10STREAMING_MOVETO\x10\x01\x12\x16\n\x12STREAMING_BUFFERED\x10\x02*\x8e\x01\n\x06Errors\x12\x11\n\rERROR_UNKNOWN\x10\x00\x12\x1e\n\x1aERROR_OUTPUT_NOT_SUPPORTED\x10\x01\x12\x19\n\x15ERROR_UNKNOWN_REQUEST\x10\x02\x12\x1b\n\x17ERROR_POWER_NOT_PRESENT\x10\x03\x12\x19\n\x15ERROR_ALREADY_PLAYING\x10\x04b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'constants_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_AXISTYPE']._serialized_start = 33
    _globals['_AXISTYPE']._serialized_end = 668
    _globals['_BOARDIDENTIFIER']._serialized_start = 670
    _globals['_BOARDIDENTIFIER']._serialized_end = 752
    _globals['_OUTPUTMODE']._serialized_start = 754
    _globals['_OUTPUTMODE']._serialized_end = 875
    _globals['_STREAMINGMODE']._serialized_start = 877
    _globals['_STREAMINGMODE']._serialized_end = 961
    _globals['_ERRORS']._serialized_start = 964
    _globals['_ERRORS']._serialized_end = 1106