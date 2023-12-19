from net.tcode import TCodeCommand
from qt_ui.threephase_configuration import ThreephaseConfiguration
from qt_ui import stim_config
from stim_math import axis


class ThreephaseParameterManager:
    def __init__(self, config: ThreephaseConfiguration):
        self.config = config

        # self.alpha = ContinuousParameter(0.0)
        self.alpha = axis.LinearInterpolatedAxis(0.0)
        self.beta = axis.LinearInterpolatedAxis(0.0)
        self.volume = axis.LinearInterpolatedAxis(1.0)
        self.ramp_volume = axis.LinearInterpolatedAxis(1.0)
        self.inactivity_volume = axis.LinearInterpolatedAxis(1.0)

        self.e1 = axis.LinearInterpolatedAxis(0.0)
        self.e2 = axis.LinearInterpolatedAxis(0.0)
        self.e3 = axis.LinearInterpolatedAxis(0.0)
        self.e4 = axis.LinearInterpolatedAxis(0.0)
        self.e5 = axis.LinearInterpolatedAxis(0.0)

        self.resistance_t = axis.ConstantAxis(1.0)
        self.resistance_s1 = axis.ConstantAxis(1.0)
        self.resistance_s2 = axis.ConstantAxis(1.0)
        self.resistance_s3 = axis.ConstantAxis(1.0)
        self.resistance_s4 = axis.ConstantAxis(1.0)
        self.resistance_s5 = axis.ConstantAxis(1.0)

        self.mk312_carrier_frequency = axis.ConstantAxis(0.0)

        self.vibration_1_enabled = axis.ConstantAxis(True)
        self.vibration_1_frequency = axis.ConstantAxis(0.0)
        self.vibration_1_strength = axis.ConstantAxis(0.0)
        self.vibration_1_left_right_bias = axis.ConstantAxis(0.0)
        self.vibration_1_high_low_bias = axis.ConstantAxis(0.0)
        self.vibration_1_random = axis.ConstantAxis(0.0)
        self.vibration_2_enabled = axis.ConstantAxis(True)
        self.vibration_2_frequency = axis.ConstantAxis(0.0)
        self.vibration_2_strength = axis.ConstantAxis(0.0)
        self.vibration_2_left_right_bias = axis.ConstantAxis(0.0)
        self.vibration_2_high_low_bias = axis.ConstantAxis(0.0)
        self.vibration_2_random = axis.ConstantAxis(0.0)

        self.pulse_carrier_frequency = axis.ConstantAxis(0.0)
        self.pulse_frequency = axis.ConstantAxis(0.0)
        self.pulse_width = axis.ConstantAxis(0.0)
        self.pulse_interval_random = axis.ConstantAxis(0.0)
        self.polarity = axis.ConstantAxis(0.0)
        self.device_emulation_mode = axis.ConstantAxis(0.0)
        self.pulse_phase_offset_increment = axis.ConstantAxis(0.0)

        self.calibration_neutral = axis.ConstantAxis(0.0)
        self.calibration_right = axis.ConstantAxis(0.0)
        self.calibration_center = axis.ConstantAxis(0.0)

        self.transform_enabled = axis.ConstantAxis(0.0)
        self.transform_rotation_degrees = axis.ConstantAxis(50.0)
        self.transform_mirror = axis.ConstantAxis(0.0)
        self.transform_top_limit = axis.ConstantAxis(1.0)
        self.transform_bottom_limit = axis.ConstantAxis(-1.0)
        self.transform_left_limit = axis.ConstantAxis(-1.0)
        self.transform_right_limit = axis.ConstantAxis(1.0)
        self.threephase_exponent = axis.ConstantAxis(0.0)
        self.map_to_edge_enabled = axis.ConstantAxis(0.0)
        self.map_to_edge_start = axis.ConstantAxis(0.0)
        self.map_to_edge_length = axis.ConstantAxis(0.0)
        self.map_to_edge_invert = axis.ConstantAxis(0.0)

        self.focus_alpha = axis.LinearInterpolatedAxis(0.0)
        self.focus_beta = axis.LinearInterpolatedAxis(0.0)

    def set_configuration(self, config: ThreephaseConfiguration):
        self.config = config

    def parse_tcode_command(self, cmd: TCodeCommand):
        for target, param in [
            (self.config.alpha, self.alpha),
            (self.config.beta, self.beta),
            (self.config.volume, self.volume),
            (self.config.carrier, self.mk312_carrier_frequency),
            (self.config.vibration_1_frequency, self.vibration_1_frequency)
        ]:
            if target.axis == cmd.axis_identifier:
                if target.enabled:
                    param.add(target.left + cmd.value * (target.right - target.left),
                              cmd.interval / 1000.0)

        for target, param in [
            ('E0', self.e1),
            ('E1', self.e2),
            ('E2', self.e3),
            ('E3', self.e4),
            ('E4', self.e5),
        ]:
            if target == cmd.axis_identifier:
                param.add(cmd.value, cmd.interval / 1000.0)

    def set_alpha(self, value):
        self.alpha.add(value)

    def set_beta(self, value):
        self.beta.add(value)

    def set_volume(self, value):
        self.volume.add(value)

    def set_ramp_volume(self, value):
        self.ramp_volume.add(value)

    def set_inactivity_volume(self, value):
        self.inactivity_volume.add(value)

    def set_position_parameters(self, position_params: stim_config.PositionParameters):
        self.alpha.add(position_params.alpha)
        self.beta.add(position_params.beta)

    def set_mk312_parameters(self, params: stim_config.Mk312Parameters):
        self.mk312_carrier_frequency.add(params.carrier_frequency)

    def set_focus_parameters(self, alpha: float, beta: float):
        self.focus_alpha.add(alpha)
        self.focus_beta.add(beta)

    def set_calibration_parameters(self, calibration_params: stim_config.ThreePhaseCalibrationParameters):
        self.calibration_neutral.add(calibration_params.up_down)
        self.calibration_right.add(calibration_params.left_right)
        self.calibration_center.add(calibration_params.center)

    def set_three_phase_transform_parameters(self, transform_params: stim_config.ThreePhaseTransformParameters):
        self.transform_enabled.add(transform_params.transform_enabled)
        self.transform_rotation_degrees.add(transform_params.rotation_degrees)
        self.transform_mirror.add(transform_params.mirror)
        self.transform_top_limit.add(transform_params.top)
        self.transform_bottom_limit.add(transform_params.bottom)
        self.transform_left_limit.add(transform_params.left)
        self.transform_right_limit.add(transform_params.right)
        self.threephase_exponent.add(transform_params.exponent)
        self.map_to_edge_enabled.add(transform_params.map_to_edge_enabled)
        self.map_to_edge_start.add(transform_params.map_to_edge_start)
        self.map_to_edge_length.add(transform_params.map_to_edge_length)
        self.map_to_edge_invert.add(transform_params.map_to_edge_invert)

    def set_vibration_parameters(self, vibration_parameters: stim_config.VibrationParameters):
        self.vibration_1_enabled.add(vibration_parameters.vibration_1_enabled)
        self.vibration_1_frequency.add(vibration_parameters.vibration_1_freq)
        self.vibration_1_strength.add(vibration_parameters.vibration_1_strength)
        self.vibration_1_left_right_bias.add(vibration_parameters.vibration_1_left_right_bias)
        self.vibration_1_high_low_bias.add(vibration_parameters.vibration_1_high_low_bias)
        self.vibration_1_random.add(vibration_parameters.vibration_1_random)
        self.vibration_2_enabled.add(vibration_parameters.vibration_2_enabled)
        self.vibration_2_frequency.add(vibration_parameters.vibration_2_freq)
        self.vibration_2_strength.add(vibration_parameters.vibration_2_strength)
        self.vibration_2_left_right_bias.add(vibration_parameters.vibration_2_left_right_bias)
        self.vibration_2_high_low_bias.add(vibration_parameters.vibration_2_high_low_bias)
        self.vibration_2_random.add(vibration_parameters.vibration_2_random)

    def set_pulse_parameters(self, pulse_parameters: stim_config.PulseParameters):
        self.pulse_carrier_frequency.add(pulse_parameters.carrier_frequency)
        self.pulse_frequency.add(pulse_parameters.pulse_frequency)
        self.pulse_width.add(pulse_parameters.pulse_width)
        self.pulse_interval_random.add(pulse_parameters.pulse_interval_random)
        self.polarity.add(pulse_parameters.polarity)
        self.device_emulation_mode.add(pulse_parameters.device_emulation_mode)
        self.pulse_phase_offset_increment.add(pulse_parameters.pulse_phase_offset_increment)

    def set_five_phase_resistance_parameters(self, resistance_parameters: stim_config.FivePhaseResistanceParameters):
        self.resistance_t.add(resistance_parameters.t)
        self.resistance_s1.add(resistance_parameters.s1)
        self.resistance_s2.add(resistance_parameters.s2)
        self.resistance_s3.add(resistance_parameters.s3)
        self.resistance_s4.add(resistance_parameters.s4)
        self.resistance_s5.add(resistance_parameters.s5)

    def set_five_phase_current_parameters(self, current_parameters: stim_config.FivePhaseCurrentParameters):
        self.e1.add(current_parameters.i1)
        self.e2.add(current_parameters.i2)
        self.e3.add(current_parameters.i3)
        self.e4.add(current_parameters.i4)
        self.e5.add(current_parameters.i5)