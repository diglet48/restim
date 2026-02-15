from enum import Enum


class AxisEnum(Enum):
    NONE = 0
    POSITION_ALPHA = 1
    POSITION_BETA = 2
    POSITION_GAMMA = 3

    VOLUME_API = 10
    VOLUME_MASTER = 11
    VOLUME_INACTIVITY = 12
    VOLUME_EXTERNAL = 13

    CARRIER_FREQUENCY = 20

    PULSE_FREQUENCY = 31
    PULSE_WIDTH = 32
    PULSE_INTERVAL_RANDOM = 33
    PULSE_RISE_TIME = 34

    VIBRATION_1_FREQUENCY = 40
    VIBRATION_1_STRENGTH = 41
    VIBRATION_1_LEFT_RIGHT_BIAS = 42
    VIBRATION_1_HIGH_LOW_BIAS = 43
    VIBRATION_1_RANDOM = 44

    VIBRATION_2_FREQUENCY = 50
    VIBRATION_2_STRENGTH = 51
    VIBRATION_2_LEFT_RIGHT_BIAS = 52
    VIBRATION_2_HIGH_LOW_BIAS = 53
    VIBRATION_2_RANDOM = 54

    INTENSITY_A = 60
    INTENSITY_B = 61
    INTENSITY_C = 62
    INTENSITY_D = 63


    def display_name(self) -> str:
        try:
            return {
                AxisEnum.NONE: '(none)',
                AxisEnum.POSITION_ALPHA: 'alpha',
                AxisEnum.POSITION_BETA: 'beta',
                AxisEnum.POSITION_GAMMA: 'gamma',
                AxisEnum.CARRIER_FREQUENCY: 'carrier frequency',
                AxisEnum.VOLUME_API: 'volume',
                AxisEnum.VOLUME_EXTERNAL: 'volume (external)',

                AxisEnum.PULSE_FREQUENCY: "pulse frequency",
                AxisEnum.PULSE_WIDTH: "pulse width",
                AxisEnum.PULSE_INTERVAL_RANDOM: "pulse interval random",
                AxisEnum.PULSE_RISE_TIME: "pulse rise time",

                AxisEnum.VIBRATION_1_FREQUENCY: "vibration 1 frequency",
                AxisEnum.VIBRATION_1_STRENGTH: "vibration 1 strength",
                AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS: "vibration 1 left right bias",
                AxisEnum.VIBRATION_1_HIGH_LOW_BIAS: "vibration 1 high low bias",
                AxisEnum.VIBRATION_1_RANDOM: "vibration 1 random",

                AxisEnum.VIBRATION_2_FREQUENCY: "vibration 2 frequency",
                AxisEnum.VIBRATION_2_STRENGTH: "vibration 2 strength",
                AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS: "vibration 2 left right bias",
                AxisEnum.VIBRATION_2_HIGH_LOW_BIAS: "vibration 2 high low bias",
                AxisEnum.VIBRATION_2_RANDOM: "vibration 2 random",

                AxisEnum.INTENSITY_A: 'intensity A',
                AxisEnum.INTENSITY_B: 'intensity B',
                AxisEnum.INTENSITY_C: 'intensity C',
                AxisEnum.INTENSITY_D: 'intensity D',
            }[self]
        except KeyError:
            return f'unknown {self.value}'

    def settings_key(self) -> str:
        return {
            AxisEnum.POSITION_ALPHA: 'POSITION_ALPHA',
            AxisEnum.POSITION_BETA: 'POSITION_BETA',
            AxisEnum.POSITION_GAMMA: 'POSITION_GAMMA',
            AxisEnum.CARRIER_FREQUENCY: 'CARRIER_FREQUENCY',
            AxisEnum.VOLUME_API: 'VOLUME_API',
            AxisEnum.VOLUME_EXTERNAL: 'VOLUME_EXTERNAL',

            AxisEnum.PULSE_FREQUENCY: "PULSE_FREQUENCY",
            AxisEnum.PULSE_WIDTH: "PULSE_WIDTH",
            AxisEnum.PULSE_INTERVAL_RANDOM: "PULSE_INTERVAL_RANDOM",
            AxisEnum.PULSE_RISE_TIME: "PULSE_RISE_TIME",

            AxisEnum.VIBRATION_1_FREQUENCY: "VIBRATION_1_FREQUENCY",
            AxisEnum.VIBRATION_1_STRENGTH: "VIBRATION_1_STRENGTH",
            AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS: "VIBRATION_1_LEFT_RIGHT_BIAS",
            AxisEnum.VIBRATION_1_HIGH_LOW_BIAS: "VIBRATION_1_HIGH_LOW_BIAS",
            AxisEnum.VIBRATION_1_RANDOM: "VIBRATION_1_RANDOM",

            AxisEnum.VIBRATION_2_FREQUENCY: "VIBRATION_2_FREQUENCY",
            AxisEnum.VIBRATION_2_STRENGTH: "VIBRATION_2_STRENGTH",
            AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS: "VIBRATION_2_LEFT_RIGHT_BIAS",
            AxisEnum.VIBRATION_2_HIGH_LOW_BIAS: "VIBRATION_2_HIGH_LOW_BIAS",
            AxisEnum.VIBRATION_2_RANDOM: "VIBRATION_2_RANDOM",

            AxisEnum.INTENSITY_A: 'INTENSITY_A',
            AxisEnum.INTENSITY_B: 'INTENSITY_B',
            AxisEnum.INTENSITY_C: 'INTENSITY_C',
            AxisEnum.INTENSITY_D: 'INTENSITY_D',
        }[self]


all_axis = [
    AxisEnum.POSITION_ALPHA,
    AxisEnum.POSITION_BETA,
    AxisEnum.POSITION_GAMMA,

    AxisEnum.VOLUME_API,
    AxisEnum.VOLUME_EXTERNAL,
    AxisEnum.CARRIER_FREQUENCY,

    AxisEnum.PULSE_FREQUENCY,
    AxisEnum.PULSE_WIDTH,
    AxisEnum.PULSE_INTERVAL_RANDOM,
    AxisEnum.PULSE_RISE_TIME,

    AxisEnum.VIBRATION_1_FREQUENCY,
    AxisEnum.VIBRATION_1_STRENGTH,
    AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS,
    AxisEnum.VIBRATION_1_HIGH_LOW_BIAS,
    AxisEnum.VIBRATION_1_RANDOM,

    AxisEnum.VIBRATION_2_FREQUENCY,
    AxisEnum.VIBRATION_2_STRENGTH,
    AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS,
    AxisEnum.VIBRATION_2_HIGH_LOW_BIAS,
    AxisEnum.VIBRATION_2_RANDOM,

    AxisEnum.INTENSITY_A,
    AxisEnum.INTENSITY_B,
    AxisEnum.INTENSITY_C,
    AxisEnum.INTENSITY_D,
]

