import constants_pb2 as _constants_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class FirmwareVersion(_message.Message):
    __slots__ = ('major', 'minor', 'revision', 'branch', 'comment')
    MAJOR_FIELD_NUMBER: _ClassVar[int]
    MINOR_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    major: int
    minor: int
    revision: int
    branch: str
    comment: str

    def __init__(self, major: _Optional[int]=..., minor: _Optional[int]=..., revision: _Optional[int]=..., branch: _Optional[str]=..., comment: _Optional[str]=...) -> None:
        ...

class RequestFirmwareVersion(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseFirmwareVersion(_message.Message):
    __slots__ = ('board', 'stm32_firmware_version_2')
    BOARD_FIELD_NUMBER: _ClassVar[int]
    STM32_FIRMWARE_VERSION_2_FIELD_NUMBER: _ClassVar[int]
    board: _constants_pb2.BoardIdentifier
    stm32_firmware_version_2: FirmwareVersion

    def __init__(self, board: _Optional[_Union[_constants_pb2.BoardIdentifier, str]]=..., stm32_firmware_version_2: _Optional[_Union[FirmwareVersion, _Mapping]]=...) -> None:
        ...

class RequestCapabilitiesGet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseCapabilitiesGet(_message.Message):
    __slots__ = ('threephase', 'fourphase', 'battery', 'potentiometer', 'maximum_waveform_amplitude_amps', 'lsm6dsox')
    THREEPHASE_FIELD_NUMBER: _ClassVar[int]
    FOURPHASE_FIELD_NUMBER: _ClassVar[int]
    BATTERY_FIELD_NUMBER: _ClassVar[int]
    POTENTIOMETER_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_WAVEFORM_AMPLITUDE_AMPS_FIELD_NUMBER: _ClassVar[int]
    LSM6DSOX_FIELD_NUMBER: _ClassVar[int]
    threephase: bool
    fourphase: bool
    battery: bool
    potentiometer: bool
    maximum_waveform_amplitude_amps: float
    lsm6dsox: bool

    def __init__(self, threephase: bool=..., fourphase: bool=..., battery: bool=..., potentiometer: bool=..., maximum_waveform_amplitude_amps: _Optional[float]=..., lsm6dsox: bool=...) -> None:
        ...

class RequestSignalStart(_message.Message):
    __slots__ = ('mode',)
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: _constants_pb2.OutputMode

    def __init__(self, mode: _Optional[_Union[_constants_pb2.OutputMode, str]]=...) -> None:
        ...

class ResponseSignalStart(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestSignalStop(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseSignalStop(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestModeSet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseModeSet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestAxisMoveTo(_message.Message):
    __slots__ = ('axis', 'value', 'interval')
    AXIS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_FIELD_NUMBER: _ClassVar[int]
    axis: _constants_pb2.AxisType
    value: float
    interval: int

    def __init__(self, axis: _Optional[_Union[_constants_pb2.AxisType, str]]=..., value: _Optional[float]=..., interval: _Optional[int]=...) -> None:
        ...

class ResponseAxisMoveTo(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestAxisSet(_message.Message):
    __slots__ = ('axis', 'timestamp_ms', 'value', 'clear')
    AXIS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CLEAR_FIELD_NUMBER: _ClassVar[int]
    axis: _constants_pb2.AxisType
    timestamp_ms: int
    value: float
    clear: bool

    def __init__(self, axis: _Optional[_Union[_constants_pb2.AxisType, str]]=..., timestamp_ms: _Optional[int]=..., value: _Optional[float]=..., clear: bool=...) -> None:
        ...

class ResponseAxisSet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestTimestampSet(_message.Message):
    __slots__ = ('timestamp_ms',)
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    timestamp_ms: int

    def __init__(self, timestamp_ms: _Optional[int]=...) -> None:
        ...

class ResponseTimestampSet(_message.Message):
    __slots__ = ('offset_ms', 'change_ms', 'error_ms')
    OFFSET_MS_FIELD_NUMBER: _ClassVar[int]
    CHANGE_MS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MS_FIELD_NUMBER: _ClassVar[int]
    offset_ms: int
    change_ms: int
    error_ms: int

    def __init__(self, offset_ms: _Optional[int]=..., change_ms: _Optional[int]=..., error_ms: _Optional[int]=...) -> None:
        ...

class RequestTimestampGet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseTimestampGet(_message.Message):
    __slots__ = ('timestamp_ms', 'unix_timestamp_ms')
    TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    UNIX_TIMESTAMP_MS_FIELD_NUMBER: _ClassVar[int]
    timestamp_ms: int
    unix_timestamp_ms: int

    def __init__(self, timestamp_ms: _Optional[int]=..., unix_timestamp_ms: _Optional[int]=...) -> None:
        ...

class RequestWifiParametersSet(_message.Message):
    __slots__ = ('ssid', 'password')
    SSID_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ssid: bytes
    password: bytes

    def __init__(self, ssid: _Optional[bytes]=..., password: _Optional[bytes]=...) -> None:
        ...

class ResponseWifiParametersSet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestWifiIPGet(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseWifiIPGet(_message.Message):
    __slots__ = ('ip',)
    IP_FIELD_NUMBER: _ClassVar[int]
    ip: int

    def __init__(self, ip: _Optional[int]=...) -> None:
        ...

class RequestLSM6DSOXStart(_message.Message):
    __slots__ = ('imu_samplerate', 'acc_fullscale', 'gyr_fullscale')
    IMU_SAMPLERATE_FIELD_NUMBER: _ClassVar[int]
    ACC_FULLSCALE_FIELD_NUMBER: _ClassVar[int]
    GYR_FULLSCALE_FIELD_NUMBER: _ClassVar[int]
    imu_samplerate: float
    acc_fullscale: float
    gyr_fullscale: float

    def __init__(self, imu_samplerate: _Optional[float]=..., acc_fullscale: _Optional[float]=..., gyr_fullscale: _Optional[float]=...) -> None:
        ...

class ResponseLSM6DSOXStart(_message.Message):
    __slots__ = ('acc_sensitivity', 'gyr_sensitivity')
    ACC_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    GYR_SENSITIVITY_FIELD_NUMBER: _ClassVar[int]
    acc_sensitivity: float
    gyr_sensitivity: float

    def __init__(self, acc_sensitivity: _Optional[float]=..., gyr_sensitivity: _Optional[float]=...) -> None:
        ...

class RequestLSM6DSOXStop(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseLSM6DSOXStop(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestDebugStm32DeepSleep(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ResponseDebugStm32DeepSleep(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RequestDebugEnterBootloader(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...