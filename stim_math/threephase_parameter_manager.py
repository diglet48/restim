import time
import numpy as np
# from PyQt5.QtCore import QObject

from net.tcode import TCodeCommand
from qt_ui.threephase_configuration import ThreephaseConfiguration
from qt_ui import stim_config


class ContinuousParameter:
    def __init__(self, init_value):
        self.data = np.array([[0, init_value]])

    def add(self, value, interval=0.0):
        ts = time.time() + interval

        # make sure data stays sorted
        if len(self.data[-1]) > 0:
            if self.data[-1, 0] == ts:
                # overwrite last value
                self.data[-1, 1] = value
            elif self.data[-1, 0] > ts:
                # delete any values >= interval
                i = np.searchsorted(self.data[:, 0], ts)
                self.data = self.data[:i]
                self.data = np.vstack((self.data, [ts, value]))
            else:
                # just insert
                self.data = np.vstack((self.data, [ts, value]))
        else:
            # just insert
            self.data = np.vstack((self.data, [ts, value]))

        # regularly cleanup stale data
        if self.data.shape[0] > 100 and self.data[0][0] < (time.time() - 10):
            cutoff = time.time() - 2
            self.data = self.data[self.data[:, 0] > cutoff]

    def interpolate(self, timeline):
        return np.interp(timeline, self.data[:, 0], self.data[:, 1])

    def last_value(self):
        return self.data[-1, 1]


class InstantParameter:
    def __init__(self, init_value):
        self.value = init_value

    def add(self, value, interval=0.0):
        self.value = value

    def interpolate(self, timeline):
        return self.value

    def last_value(self):
        return self.value


class ThreephaseParameterManager():
    def __init__(self, config: ThreephaseConfiguration):
        self.config = config

        self.alpha = ContinuousParameter(0.0)
        self.beta = ContinuousParameter(0.0)
        self.volume = ContinuousParameter(1.0)
        self.ramp_volume = ContinuousParameter(1.0)
        self.inactivity_volume = ContinuousParameter(1.0)

        self.e1 = ContinuousParameter(0.0)
        self.e2 = ContinuousParameter(0.0)
        self.e3 = ContinuousParameter(0.0)
        self.e4 = ContinuousParameter(0.0)
        self.e5 = ContinuousParameter(0.0)

        self.resistance_t = InstantParameter(1.0)
        self.resistance_s1 = InstantParameter(1.0)
        self.resistance_s2 = InstantParameter(1.0)
        self.resistance_s3 = InstantParameter(1.0)
        self.resistance_s4 = InstantParameter(1.0)
        self.resistance_s5 = InstantParameter(1.0)

        self.carrier_frequency = InstantParameter(0.0)
        self.modulation_1_enabled = InstantParameter(True)
        self.modulation_1_frequency = InstantParameter(0.0)
        self.modulation_1_strength = InstantParameter(0.0)
        self.modulation_1_left_right_bias = InstantParameter(0.0)
        self.modulation_1_high_low_bias = InstantParameter(0.0)
        self.modulation_2_enabled = InstantParameter(True)
        self.modulation_2_frequency = InstantParameter(0.0)
        self.modulation_2_strength = InstantParameter(0.0)
        self.modulation_2_left_right_bias = InstantParameter(0.0)
        self.modulation_2_high_low_bias = InstantParameter(0.0)

        self.calibration_neutral = InstantParameter(0.0)
        self.calibration_right = InstantParameter(0.0)
        self.calibration_center = InstantParameter(0.0)

        self.transform_enabled = InstantParameter(0.0)
        self.transform_rotation_degrees = InstantParameter(50.0)
        self.transform_mirror = InstantParameter(0.0)
        self.transform_top_limit = InstantParameter(1.0)
        self.transform_bottom_limit = InstantParameter(-1.0)
        self.transform_left_limit = InstantParameter(-1.0)
        self.transform_right_limit = InstantParameter(1.0)

        self.focus_alpha = ContinuousParameter(0.0)
        self.focus_beta = ContinuousParameter(0.0)

    def set_configuration(self, config: ThreephaseConfiguration):
        self.config = config

    def parse_tcode_command(self, cmd: TCodeCommand):
        for target, param in [
            (self.config.alpha, self.alpha),
            (self.config.beta, self.beta),
            (self.config.volume, self.volume),
            (self.config.carrier, self.carrier_frequency),
            (self.config.modulation_1_frequency, self.modulation_1_frequency)
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

    def set_carrier_frequency(self, value):
        self.carrier_frequency.add(value)

    def set_modulation_1_enabled(self, value):
        self.modulation_1_enabled.add(value)

    def set_modulation_1_frequency(self, value):
        self.modulation_1_frequency.add(value)

    def set_modulation_1_strength(self, value):
        self.modulation_1_strength.add(value)

    def set_modulation_2_enabled(self, value):
        self.modulation_2_enabled.add(value)

    def set_modulation_2_frequency(self, value):
        self.modulation_2_frequency.add(value)

    def set_modulation_2_strength(self, value):
        self.modulation_1_strength.add(value)

    def set_position_parameters(self, position_params: stim_config.PositionParameters):
        self.alpha.add(position_params.alpha)
        self.beta.add(position_params.beta)

    def set_focus_parameters(self, alpha: float, beta: float):
        self.focus_alpha.add(alpha)
        self.focus_beta.add(beta)

    def set_calibration_parameters(self, calibration_params: stim_config.ThreePhaseCalibrationParameters):
        self.calibration_neutral.add(calibration_params.up_down)
        self.calibration_right.add(calibration_params.left_right)
        self.calibration_center.add(calibration_params.center)

    def set_three_phase_transform_parameters(self, transform_params: stim_config.ThreePhaseTransformParameters):
        self.transform_enabled.add(transform_params.enabled)
        self.transform_rotation_degrees.add(transform_params.rotation_degrees)
        self.transform_mirror.add(transform_params.mirror)
        self.transform_top_limit.add(transform_params.top)
        self.transform_bottom_limit.add(transform_params.bottom)
        self.transform_left_limit.add(transform_params.left)
        self.transform_right_limit.add(transform_params.right)

    def set_modulation_parameters(self, modulation_parameters: stim_config.ModulationParameters):
        self.carrier_frequency.add(modulation_parameters.carrier_frequency)
        self.modulation_1_enabled.add(modulation_parameters.modulation_1_enabled)
        self.modulation_1_frequency.add(modulation_parameters.modulation_1_freq)
        self.modulation_1_strength.add(modulation_parameters.modulation_1_modulation)
        self.modulation_1_left_right_bias.add(modulation_parameters.modulation_1_left_right_bias)
        self.modulation_1_high_low_bias.add(modulation_parameters.modulation_1_high_low_bias)
        self.modulation_2_enabled.add(modulation_parameters.modulation_2_enabled)
        self.modulation_2_frequency.add(modulation_parameters.modulation_2_freq)
        self.modulation_2_strength.add(modulation_parameters.modulation_2_modulation)
        self.modulation_2_left_right_bias.add(modulation_parameters.modulation_2_left_right_bias)
        self.modulation_2_high_low_bias.add(modulation_parameters.modulation_2_high_low_bias)

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