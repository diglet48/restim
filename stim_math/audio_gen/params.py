from dataclasses import dataclass

from stim_math.axis import AbstractAxis


@dataclass
class ThreephasePositionParams:
    alpha: AbstractAxis    # float [-1, 1]
    beta: AbstractAxis     # float [-1, 1]


@dataclass
class FivephasePositionParams:
    e1: AbstractAxis    # float [0, 1]
    e2: AbstractAxis    # float [0, 1]
    e3: AbstractAxis    # float [0, 1]
    e4: AbstractAxis    # float [0, 1]
    e5: AbstractAxis    # float [0, 1]


@dataclass
class ThreephaseCalibrationParams:
    neutral: AbstractAxis   # float
    right: AbstractAxis     # float
    center: AbstractAxis    # float


@dataclass
class FivephaseCalibrationParams:
    t: AbstractAxis     # float [0 - inf)
    s1: AbstractAxis    # float [0 - inf)
    s2: AbstractAxis    # float [0 - inf)
    s3: AbstractAxis    # float [0 - inf)
    s4: AbstractAxis    # float [0 - inf)
    s5: AbstractAxis    # float [0 - inf)


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
    ramp: AbstractAxis        # [0, 1]
    inactivity: AbstractAxis  # [0, 1]


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
    pulse_polarity: AbstractAxis    # 1: clockwise. -1: counter-clockwise. else: random
    device_emulation_mode: AbstractAxis
    pulse_phase_offset_increment: AbstractAxis


@dataclass
class FivephaseContinuousAlgorithmParams:   # TODO: it says 5-phase, but used for both 4 and 5-phase.
    position: FivephasePositionParams  # TODO: technically not a position
    calibrate: FivephaseCalibrationParams
    vibration_1: VibrationParams
    vibration_2: VibrationParams
    volume: VolumeParams
    carrier_frequency: AbstractAxis


@dataclass
class SafetyParams:
    minimum_carrier_frequency: float
    maximum_carrier_frequency: float
