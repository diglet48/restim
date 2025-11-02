from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class NotificationBoot(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class NotificationPotentiometer(_message.Message):
    __slots__ = ('value',)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float

    def __init__(self, value: _Optional[float]=...) -> None:
        ...

class NotificationCurrents(_message.Message):
    __slots__ = ('rms_a', 'rms_b', 'rms_c', 'rms_d', 'peak_a', 'peak_b', 'peak_c', 'peak_d', 'output_power', 'output_power_skin', 'peak_cmd')
    RMS_A_FIELD_NUMBER: _ClassVar[int]
    RMS_B_FIELD_NUMBER: _ClassVar[int]
    RMS_C_FIELD_NUMBER: _ClassVar[int]
    RMS_D_FIELD_NUMBER: _ClassVar[int]
    PEAK_A_FIELD_NUMBER: _ClassVar[int]
    PEAK_B_FIELD_NUMBER: _ClassVar[int]
    PEAK_C_FIELD_NUMBER: _ClassVar[int]
    PEAK_D_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_POWER_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_POWER_SKIN_FIELD_NUMBER: _ClassVar[int]
    PEAK_CMD_FIELD_NUMBER: _ClassVar[int]
    rms_a: float
    rms_b: float
    rms_c: float
    rms_d: float
    peak_a: float
    peak_b: float
    peak_c: float
    peak_d: float
    output_power: float
    output_power_skin: float
    peak_cmd: float

    def __init__(self, rms_a: _Optional[float]=..., rms_b: _Optional[float]=..., rms_c: _Optional[float]=..., rms_d: _Optional[float]=..., peak_a: _Optional[float]=..., peak_b: _Optional[float]=..., peak_c: _Optional[float]=..., peak_d: _Optional[float]=..., output_power: _Optional[float]=..., output_power_skin: _Optional[float]=..., peak_cmd: _Optional[float]=...) -> None:
        ...

class NotificationModelEstimation(_message.Message):
    __slots__ = ('resistance_a', 'reluctance_a', 'resistance_b', 'reluctance_b', 'resistance_c', 'reluctance_c', 'resistance_d', 'reluctance_d', 'constant')
    RESISTANCE_A_FIELD_NUMBER: _ClassVar[int]
    RELUCTANCE_A_FIELD_NUMBER: _ClassVar[int]
    RESISTANCE_B_FIELD_NUMBER: _ClassVar[int]
    RELUCTANCE_B_FIELD_NUMBER: _ClassVar[int]
    RESISTANCE_C_FIELD_NUMBER: _ClassVar[int]
    RELUCTANCE_C_FIELD_NUMBER: _ClassVar[int]
    RESISTANCE_D_FIELD_NUMBER: _ClassVar[int]
    RELUCTANCE_D_FIELD_NUMBER: _ClassVar[int]
    CONSTANT_FIELD_NUMBER: _ClassVar[int]
    resistance_a: float
    reluctance_a: float
    resistance_b: float
    reluctance_b: float
    resistance_c: float
    reluctance_c: float
    resistance_d: float
    reluctance_d: float
    constant: float

    def __init__(self, resistance_a: _Optional[float]=..., reluctance_a: _Optional[float]=..., resistance_b: _Optional[float]=..., reluctance_b: _Optional[float]=..., resistance_c: _Optional[float]=..., reluctance_c: _Optional[float]=..., resistance_d: _Optional[float]=..., reluctance_d: _Optional[float]=..., constant: _Optional[float]=...) -> None:
        ...

class SystemStatsESC1(_message.Message):
    __slots__ = ('temp_stm32', 'temp_board', 'v_bus', 'v_ref')
    TEMP_STM32_FIELD_NUMBER: _ClassVar[int]
    TEMP_BOARD_FIELD_NUMBER: _ClassVar[int]
    V_BUS_FIELD_NUMBER: _ClassVar[int]
    V_REF_FIELD_NUMBER: _ClassVar[int]
    temp_stm32: float
    temp_board: float
    v_bus: float
    v_ref: float

    def __init__(self, temp_stm32: _Optional[float]=..., temp_board: _Optional[float]=..., v_bus: _Optional[float]=..., v_ref: _Optional[float]=...) -> None:
        ...

class SystemStatsFocstimV3(_message.Message):
    __slots__ = ('temp_stm32', 'v_sys_min', 'v_sys_max', 'v_ref', 'v_boost_min', 'v_boost_max', 'boost_duty_cycle')
    TEMP_STM32_FIELD_NUMBER: _ClassVar[int]
    V_SYS_MIN_FIELD_NUMBER: _ClassVar[int]
    V_SYS_MAX_FIELD_NUMBER: _ClassVar[int]
    V_REF_FIELD_NUMBER: _ClassVar[int]
    V_BOOST_MIN_FIELD_NUMBER: _ClassVar[int]
    V_BOOST_MAX_FIELD_NUMBER: _ClassVar[int]
    BOOST_DUTY_CYCLE_FIELD_NUMBER: _ClassVar[int]
    temp_stm32: float
    v_sys_min: float
    v_sys_max: float
    v_ref: float
    v_boost_min: float
    v_boost_max: float
    boost_duty_cycle: float

    def __init__(self, temp_stm32: _Optional[float]=..., v_sys_min: _Optional[float]=..., v_sys_max: _Optional[float]=..., v_ref: _Optional[float]=..., v_boost_min: _Optional[float]=..., v_boost_max: _Optional[float]=..., boost_duty_cycle: _Optional[float]=...) -> None:
        ...

class NotificationSystemStats(_message.Message):
    __slots__ = ('esc1', 'focstimv3')
    ESC1_FIELD_NUMBER: _ClassVar[int]
    FOCSTIMV3_FIELD_NUMBER: _ClassVar[int]
    esc1: SystemStatsESC1
    focstimv3: SystemStatsFocstimV3

    def __init__(self, esc1: _Optional[_Union[SystemStatsESC1, _Mapping]]=..., focstimv3: _Optional[_Union[SystemStatsFocstimV3, _Mapping]]=...) -> None:
        ...

class NotificationSignalStats(_message.Message):
    __slots__ = ('actual_pulse_frequency', 'v_drive')
    ACTUAL_PULSE_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    V_DRIVE_FIELD_NUMBER: _ClassVar[int]
    actual_pulse_frequency: float
    v_drive: float

    def __init__(self, actual_pulse_frequency: _Optional[float]=..., v_drive: _Optional[float]=...) -> None:
        ...

class NotificationBattery(_message.Message):
    __slots__ = ('battery_voltage', 'battery_charge_rate_watt', 'battery_soc', 'wall_power_present', 'chip_temperature')
    BATTERY_VOLTAGE_FIELD_NUMBER: _ClassVar[int]
    BATTERY_CHARGE_RATE_WATT_FIELD_NUMBER: _ClassVar[int]
    BATTERY_SOC_FIELD_NUMBER: _ClassVar[int]
    WALL_POWER_PRESENT_FIELD_NUMBER: _ClassVar[int]
    CHIP_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    battery_voltage: float
    battery_charge_rate_watt: float
    battery_soc: float
    wall_power_present: bool
    chip_temperature: float

    def __init__(self, battery_voltage: _Optional[float]=..., battery_charge_rate_watt: _Optional[float]=..., battery_soc: _Optional[float]=..., wall_power_present: bool=..., chip_temperature: _Optional[float]=...) -> None:
        ...

class NotificationDebugString(_message.Message):
    __slots__ = ('message',)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str

    def __init__(self, message: _Optional[str]=...) -> None:
        ...

class NotificationDebugAS5311(_message.Message):
    __slots__ = ('raw', 'tracked', 'flags')
    RAW_FIELD_NUMBER: _ClassVar[int]
    TRACKED_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    raw: int
    tracked: int
    flags: int

    def __init__(self, raw: _Optional[int]=..., tracked: _Optional[int]=..., flags: _Optional[int]=...) -> None:
        ...

class NotificationDebugEdging(_message.Message):
    __slots__ = ('full_power_threshold', 'reduced_power_threshold', 'reduction')
    FULL_POWER_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDUCED_POWER_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    REDUCTION_FIELD_NUMBER: _ClassVar[int]
    full_power_threshold: float
    reduced_power_threshold: float
    reduction: float

    def __init__(self, full_power_threshold: _Optional[float]=..., reduced_power_threshold: _Optional[float]=..., reduction: _Optional[float]=...) -> None:
        ...