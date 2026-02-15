from dataclasses import dataclass
import logging

from net.tcode import TCodeCommand
from stim_math.axis import AbstractAxis

from qt_ui.models.funscript_kit import FunscriptKitModel, FunscriptKitItem
from qt_ui.device_wizard.axes import AxisEnum

logger = logging.getLogger('restim.tcode')


@dataclass
class Route:
    axis: AbstractAxis
    low: float
    high: float

    def remap(self, value):
        return min(max(value, 0.0), 1.0) * (self.high - self.low) + self.low


class TCodeCommandRouter:
    def __init__(self,
                 alpha: AbstractAxis,
                 beta: AbstractAxis,

                 volume_api: AbstractAxis,
                 volume_external: AbstractAxis,

                 carrier_frequency: AbstractAxis,   # either pulse of continuous

                 pulse_frequency: AbstractAxis,
                 pulse_width: AbstractAxis,
                 pulse_interval_random: AbstractAxis,
                 pulse_rise_time: AbstractAxis,

                 vibration_1_frequency: AbstractAxis,
                 vibration_1_strength: AbstractAxis,
                 vibration_1_left_right_bias: AbstractAxis,
                 vibration_1_high_low_bias: AbstractAxis,
                 vibration_1_random: AbstractAxis,

                 vibration_2_frequency: AbstractAxis,
                 vibration_2_strength: AbstractAxis,
                 vibration_2_left_right_bias: AbstractAxis,
                 vibration_2_high_low_bias: AbstractAxis,
                 vibration_2_random: AbstractAxis,

                 intensity_a: AbstractAxis,
                 intensity_b: AbstractAxis,
                 intensity_c: AbstractAxis,
                 intensity_d: AbstractAxis,
                 ):
        self.alpha = alpha
        self.beta = beta
        self.volume_api = volume_api
        self.volume_external = volume_external
        self.carrier_frequency = carrier_frequency
        self.pulse_frequency = pulse_frequency
        self.pulse_width = pulse_width
        self.pulse_interval_random = pulse_interval_random
        self.pulse_rise_time = pulse_rise_time
        self.vibration_1_frequency = vibration_1_frequency
        self.vibration_1_strength = vibration_1_strength
        self.vibration_1_left_right_bias = vibration_1_left_right_bias
        self.vibration_1_high_low_bias = vibration_1_high_low_bias
        self.vibration_1_random = vibration_1_random
        self.vibration_2_frequency = vibration_2_frequency
        self.vibration_2_strength = vibration_2_strength
        self.vibration_2_left_right_bias = vibration_2_left_right_bias
        self.vibration_2_high_low_bias = vibration_2_high_low_bias
        self.vibration_2_random = vibration_2_random

        self.intensity_a = intensity_a
        self.intensity_b = intensity_b
        self.intensity_c = intensity_c
        self.intensity_d = intensity_d

        self.mapping = {}
        self.reload_kit()

    def reload_kit(self):
        axis_enum_to_axis = {
            AxisEnum.POSITION_ALPHA: self.alpha,
            AxisEnum.POSITION_BETA: self.beta,

            AxisEnum.VOLUME_API: self.volume_api,
            AxisEnum.VOLUME_EXTERNAL: self.volume_external,
            AxisEnum.CARRIER_FREQUENCY: self.carrier_frequency,

            AxisEnum.PULSE_FREQUENCY: self.pulse_frequency,
            AxisEnum.PULSE_WIDTH: self.pulse_width,
            AxisEnum.PULSE_INTERVAL_RANDOM: self.pulse_interval_random,
            AxisEnum.PULSE_RISE_TIME: self.pulse_rise_time,

            AxisEnum.VIBRATION_1_FREQUENCY: self.vibration_1_frequency,
            AxisEnum.VIBRATION_1_STRENGTH: self.vibration_1_strength,
            AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS: self.vibration_1_left_right_bias,
            AxisEnum.VIBRATION_1_HIGH_LOW_BIAS: self.vibration_1_high_low_bias,
            AxisEnum.VIBRATION_1_RANDOM: self.vibration_1_random,

            AxisEnum.VIBRATION_2_FREQUENCY: self.vibration_2_frequency,
            AxisEnum.VIBRATION_2_STRENGTH: self.vibration_2_strength,
            AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS: self.vibration_2_left_right_bias,
            AxisEnum.VIBRATION_2_HIGH_LOW_BIAS: self.vibration_2_high_low_bias,
            AxisEnum.VIBRATION_2_RANDOM: self.vibration_2_random,

            AxisEnum.INTENSITY_A: self.intensity_a,
            AxisEnum.INTENSITY_B: self.intensity_b,
            AxisEnum.INTENSITY_C: self.intensity_c,
            AxisEnum.INTENSITY_D: self.intensity_d,
        }

        kit = FunscriptKitModel.load_from_settings()
        mapping = {}
        for child in kit.children:
            child: FunscriptKitItem
            if len(child.tcode_axis_name) == 2:
                if child.axis in axis_enum_to_axis:
                    route = Route(axis_enum_to_axis[child.axis], child.limit_min, child.limit_max)
                    if child.tcode_axis_name not in mapping:
                        mapping[child.tcode_axis_name] = route
            elif len(child.tcode_axis_name) != 0:
                logger.error(f'Invalid T-Code axis name: {child.tcode_axis_name}. Axis name must be 2 chars.')

        self.mapping = mapping

    def set_carrier_axis(self, carrier: AbstractAxis):
        self.carrier_frequency = carrier
        self.reload_kit()

    def route_command(self, cmd: TCodeCommand):
        try:
            route = self.mapping[cmd.axis_identifier]
            route.axis.add(route.remap(cmd.value), cmd.interval / 1000.0)
        except KeyError:
            pass
