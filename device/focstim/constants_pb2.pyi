from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class AxisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AXIS_UNKNOWN: _ClassVar[AxisType]
    AXIS_POSITION_ALPHA: _ClassVar[AxisType]
    AXIS_POSITION_BETA: _ClassVar[AxisType]
    AXIS_POSITION_GAMMA: _ClassVar[AxisType]
    AXIS_WAVEFORM_AMPLITUDE_AMPS: _ClassVar[AxisType]
    AXIS_CARRIER_FREQUENCY_HZ: _ClassVar[AxisType]
    AXIS_PULSE_WIDTH_IN_CYCLES: _ClassVar[AxisType]
    AXIS_PULSE_RISE_TIME_CYCLES: _ClassVar[AxisType]
    AXIS_PULSE_FREQUENCY_HZ: _ClassVar[AxisType]
    AXIS_PULSE_INTERVAL_RANDOM_PERCENT: _ClassVar[AxisType]
    AXIS_CALIBRATION_3_CENTER: _ClassVar[AxisType]
    AXIS_CALIBRATION_3_UP: _ClassVar[AxisType]
    AXIS_CALIBRATION_3_LEFT: _ClassVar[AxisType]
    AXIS_CALIBRATION_4_CENTER: _ClassVar[AxisType]
    AXIS_CALIBRATION_4_A: _ClassVar[AxisType]
    AXIS_CALIBRATION_4_B: _ClassVar[AxisType]
    AXIS_CALIBRATION_4_C: _ClassVar[AxisType]
    AXIS_CALIBRATION_4_D: _ClassVar[AxisType]
    AXIS_ELECTRODE_1_POWER: _ClassVar[AxisType]
    AXIS_ELECTRODE_2_POWER: _ClassVar[AxisType]
    AXIS_ELECTRODE_3_POWER: _ClassVar[AxisType]
    AXIS_ELECTRODE_4_POWER: _ClassVar[AxisType]

class BoardIdentifier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BOARD_UNKNOWN: _ClassVar[BoardIdentifier]
    BOARD_B_G431B_ESC1: _ClassVar[BoardIdentifier]
    BOARD_FOCSTIM_V4: _ClassVar[BoardIdentifier]

class OutputMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTPUT_UNKNOWN: _ClassVar[OutputMode]
    OUTPUT_THREEPHASE: _ClassVar[OutputMode]
    OUTPUT_FOURPHASE: _ClassVar[OutputMode]
    OUTPUT_FOURPHASE_INDIVIDUAL_ELECTRODES: _ClassVar[OutputMode]

class StreamingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAMING_UNKNOWN: _ClassVar[StreamingMode]
    STREAMING_MOVETO: _ClassVar[StreamingMode]
    STREAMING_BUFFERED: _ClassVar[StreamingMode]

class Errors(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_UNKNOWN: _ClassVar[Errors]
    ERROR_OUTPUT_NOT_SUPPORTED: _ClassVar[Errors]
    ERROR_UNKNOWN_REQUEST: _ClassVar[Errors]
    ERROR_POWER_NOT_PRESENT: _ClassVar[Errors]
    ERROR_ALREADY_PLAYING: _ClassVar[Errors]
AXIS_UNKNOWN: AxisType
AXIS_POSITION_ALPHA: AxisType
AXIS_POSITION_BETA: AxisType
AXIS_POSITION_GAMMA: AxisType
AXIS_WAVEFORM_AMPLITUDE_AMPS: AxisType
AXIS_CARRIER_FREQUENCY_HZ: AxisType
AXIS_PULSE_WIDTH_IN_CYCLES: AxisType
AXIS_PULSE_RISE_TIME_CYCLES: AxisType
AXIS_PULSE_FREQUENCY_HZ: AxisType
AXIS_PULSE_INTERVAL_RANDOM_PERCENT: AxisType
AXIS_CALIBRATION_3_CENTER: AxisType
AXIS_CALIBRATION_3_UP: AxisType
AXIS_CALIBRATION_3_LEFT: AxisType
AXIS_CALIBRATION_4_CENTER: AxisType
AXIS_CALIBRATION_4_A: AxisType
AXIS_CALIBRATION_4_B: AxisType
AXIS_CALIBRATION_4_C: AxisType
AXIS_CALIBRATION_4_D: AxisType
AXIS_ELECTRODE_1_POWER: AxisType
AXIS_ELECTRODE_2_POWER: AxisType
AXIS_ELECTRODE_3_POWER: AxisType
AXIS_ELECTRODE_4_POWER: AxisType
BOARD_UNKNOWN: BoardIdentifier
BOARD_B_G431B_ESC1: BoardIdentifier
BOARD_FOCSTIM_V4: BoardIdentifier
OUTPUT_UNKNOWN: OutputMode
OUTPUT_THREEPHASE: OutputMode
OUTPUT_FOURPHASE: OutputMode
OUTPUT_FOURPHASE_INDIVIDUAL_ELECTRODES: OutputMode
STREAMING_UNKNOWN: StreamingMode
STREAMING_MOVETO: StreamingMode
STREAMING_BUFFERED: StreamingMode
ERROR_UNKNOWN: Errors
ERROR_OUTPUT_NOT_SUPPORTED: Errors
ERROR_UNKNOWN_REQUEST: Errors
ERROR_POWER_NOT_PRESENT: Errors
ERROR_ALREADY_PLAYING: Errors