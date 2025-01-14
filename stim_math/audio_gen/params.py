from dataclasses import dataclass

from stim_math.axis import AbstractAxis


@dataclass
class ThreephasePositionParams:
    alpha: AbstractAxis    # float [-1, 1]
    beta: AbstractAxis     # float [-1, 1]

@dataclass
class ThreephaseCalibrationParams:
    neutral: AbstractAxis   # float
    right: AbstractAxis     # float
    center: AbstractAxis    # float

@dataclass
class ThreephasePositionTransformParams:
    transform_enabled: AbstractAxis             # bool
    transform_rotation_degrees: AbstractAxis    # float
    transform_mirror: AbstractAxis              # bool
    transform_top_limit: AbstractAxis           # float
    transform_bottom_limit: AbstractAxis        # float
    transform_left_limit: AbstractAxis          # float
    transform_right_limit: AbstractAxis         # float

    map_to_edge_enabled: AbstractAxis           # bool
    map_to_edge_start: AbstractAxis             # float
    map_to_edge_length: AbstractAxis            # float
    map_to_edge_invert: AbstractAxis            # bool

    exponent: AbstractAxis # TODO: remove?


@dataclass
class VibrationParams:
    enabled: AbstractAxis           # bool
    frequency: AbstractAxis         # float [0-inf)
    strength: AbstractAxis          # float [0-1]
    left_right_bias: AbstractAxis   # float [-1, 1]
    high_low_bias: AbstractAxis     # float [-1, 1]
    random: AbstractAxis            # float [0, 1]


@dataclass
class VolumeParams:
    api: AbstractAxis         # [0, 1]
    master: AbstractAxis      # [0, 1]
    inactivity: AbstractAxis  # [0, 1]
    external: AbstractAxis    # [0, 1]


@dataclass
class ThreephaseContinuousAlgorithmParams:
    position: ThreephasePositionParams
    transform: ThreephasePositionTransformParams
    calibrate: ThreephaseCalibrationParams
    vibration_1: VibrationParams
    vibration_2: VibrationParams
    volume: VolumeParams
    carrier_frequency: AbstractAxis


@dataclass
class ThreephasePulsebasedAlgorithmParams:
    position: ThreephasePositionParams
    transform: ThreephasePositionTransformParams
    calibrate: ThreephaseCalibrationParams
    vibration_1: VibrationParams
    vibration_2: VibrationParams
    volume: VolumeParams
    carrier_frequency: AbstractAxis # Hz
    pulse_frequency: AbstractAxis   # Hz
    pulse_width: AbstractAxis       # carrier cycles
    pulse_interval_random: AbstractAxis
    pulse_rise_time: AbstractAxis


@dataclass
class ThreephaseABTestAlgorithmParams:
    position: ThreephasePositionParams
    transform: ThreephasePositionTransformParams
    calibrate: ThreephaseCalibrationParams
    vibration_1: VibrationParams
    vibration_2: VibrationParams
    volume: VolumeParams
    a_volume: AbstractAxis
    a_train_duration: AbstractAxis # s
    a_carrier_frequency: AbstractAxis  # Hz
    a_pulse_frequency: AbstractAxis  # Hz
    a_pulse_width: AbstractAxis  # carrier cycles
    a_pulse_interval_random: AbstractAxis
    a_pulse_rise_time: AbstractAxis
    b_volume: AbstractAxis
    b_train_duration: AbstractAxis # s
    b_carrier_frequency: AbstractAxis  # Hz
    b_pulse_frequency: AbstractAxis  # Hz
    b_pulse_width: AbstractAxis  # carrier cycles
    b_pulse_interval_random: AbstractAxis
    b_pulse_rise_time: AbstractAxis


@dataclass
class FOCStimParams:
    position: ThreephasePositionParams
    transform: ThreephasePositionTransformParams
    calibrate: ThreephaseCalibrationParams
    volume: VolumeParams
    carrier_frequency: AbstractAxis # Hz
    pulse_frequency: AbstractAxis   # Hz
    pulse_width: AbstractAxis       # carrier cycles
    pulse_interval_random: AbstractAxis
    pulse_rise_time: AbstractAxis
    tau: AbstractAxis               # µs


@dataclass
class SafetyParams:
    minimum_carrier_frequency: float
    maximum_carrier_frequency: float
