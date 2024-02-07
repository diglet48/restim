from net.tcode import TCodeCommand
from qt_ui.tcode_route_configuration import ThreephaseRouteConfiguration
from stim_math.audio_gen.params import FivephasePositionParams
from stim_math.axis import AbstractAxis


class TCodeCommandRouter:
    def __init__(self,
                 routing: ThreephaseRouteConfiguration,
                 alpha: AbstractAxis,
                 beta: AbstractAxis,
                 api_volume: AbstractAxis,
                 continuous_carrier_frequency: AbstractAxis,
                 pulse_carrier_frequency: AbstractAxis,
                 vibration_frequency: AbstractAxis,
                 fivephase_position: FivephasePositionParams,
                 ):
        self.routing = routing
        self.alpha = alpha
        self.beta = beta
        self.api_volume = api_volume
        self.continuous_carrier_frequency = continuous_carrier_frequency
        self.pulse_carrier_frequency = pulse_carrier_frequency
        self.vibration_frequency = vibration_frequency
        self.fivephase_position = fivephase_position

    def update_routing_configuration(self, routing: ThreephaseRouteConfiguration):
        self.routing = routing

    def route_command(self, cmd: TCodeCommand):
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
