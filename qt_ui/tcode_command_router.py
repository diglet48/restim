from dataclasses import dataclass

from net.tcode import TCodeCommand
from stim_math.audio_gen.params import FivephasePositionParams
from stim_math.axis import AbstractAxis

from qt_ui.models.funscript_kit import FunscriptKitModel, FunscriptKitItem
from qt_ui.device_wizard.axes import AxisEnum


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
                 api_volume: AbstractAxis,

                 carrier_frequency: AbstractAxis,   # either pulse of continuous

                 pulse_frequency: AbstractAxis,
                 pulse_width: AbstractAxis,
                 pulse_interval_random: AbstractAxis,

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

                 fivephase_position: FivephasePositionParams,
                 ):
        self.alpha = alpha
        self.beta = beta
        self.api_volume = api_volume
        self.carrier_frequency = carrier_frequency
        self.pulse_frequency = pulse_frequency
        self.pulse_width = pulse_width
        self.pulse_interval_random = pulse_interval_random
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
        self.fivephase_position = fivephase_position

        self.mapping = {}
        self.reload_kit()

    def reload_kit(self):
        axis_enum_to_axis = {
            AxisEnum.POSITION_ALPHA: self.alpha,
            AxisEnum.POSITION_BETA: self.beta,
            AxisEnum.VOLUME_API: self.api_volume,
            AxisEnum.CARRIER_FREQUENCY: self.carrier_frequency,

            AxisEnum.PULSE_FREQUENCY: self.pulse_frequency,
            AxisEnum.PULSE_WIDTH: self.pulse_width,
            AxisEnum.PULSE_INTERVAL_RANDOM: self.pulse_interval_random,

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
        }

        kit = FunscriptKitModel.load_from_settings()
        mapping = {}
        for child in kit.children:
            child: FunscriptKitItem
            if child.auto_loading:
                if len(child.tcode_axis_name) == 2:
                    if child.axis in axis_enum_to_axis:
                        route = Route(axis_enum_to_axis[child.axis], child.limit_min, child.limit_max)
                        if child.tcode_axis_name not in mapping:
                            mapping[child.tcode_axis_name] = route

        # UGLY: patch in five-phase axis
        mapping['E0'] = Route(self.fivephase_position.e1, 0, 1)
        mapping['E1'] = Route(self.fivephase_position.e2, 0, 1)
        mapping['E2'] = Route(self.fivephase_position.e3, 0, 1)
        mapping['E3'] = Route(self.fivephase_position.e4, 0, 1)
        mapping['E4'] = Route(self.fivephase_position.e5, 0, 1)

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
        return

        for target, param in [
            (self.routing.alpha, self.alpha),
            (self.routing.beta, self.beta),
            (self.routing.volume, self.api_volume),
            (self.routing.carrier, self.continuous_carrier_frequency),
            (self.routing.carrier, self.pulse_carrier_frequency),
            (self.routing.vibration_1_frequency, self.vibration_frequency)
        ]:
            if target.axis == cmd.axis_identifier:
                if target.enabled:
                    param.add(target.left + cmd.value * (target.right - target.left),
                              cmd.interval / 1000.0)

        for target, param in [
            ('E0', self.fivephase_position.e1),
            ('E1', self.fivephase_position.e2),
            ('E2', self.fivephase_position.e3),
            ('E3', self.fivephase_position.e4),
            ('E4', self.fivephase_position.e5),
        ]:
            if target == cmd.axis_identifier:
                param.add(cmd.value, cmd.interval / 1000.0)
