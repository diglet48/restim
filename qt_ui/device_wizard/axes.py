from enum import Enum


class AxisEnum(Enum):
    NONE = 0
    POSITION_ALPHA = 1
    POSITION_BETA = 2

    VOLUME_API = 10
    VOLUME_RAMP = 11
    VOLUME_INACTIVITY = 12

    CARRIER_FREQUENCY = 20

    PULSE_CARRIER_FREQUENCY = 30
    PULSE_FREQUENCY = 31
    PULSE_WIDTH = 32

    def display_name(self) -> str:
        try:
            return {
                AxisEnum.NONE: '(none)',
                AxisEnum.POSITION_ALPHA: 'alpha',
                AxisEnum.POSITION_BETA: 'beta',
                AxisEnum.CARRIER_FREQUENCY: 'carrier frequency',
                AxisEnum.VOLUME_API: 'volume'
            }[self]
        except KeyError:
            return f'unknown {self.value}'

    def settings_key(self) -> str:
        return {
            AxisEnum.POSITION_ALPHA: 'POSITION_ALPHA',
            AxisEnum.POSITION_BETA: 'POSITION_BETA',
            AxisEnum.CARRIER_FREQUENCY: 'CARRIER_FREQUENCY',
            AxisEnum.VOLUME_API: 'VOLUME_API'
        }[self]


all_axis = [
    AxisEnum.POSITION_ALPHA,
    AxisEnum.POSITION_BETA,

    AxisEnum.VOLUME_API,
    AxisEnum.CARRIER_FREQUENCY,
]

text_and_data = []
for k in all_axis:
    text_and_data.append((k.display_name(), k))