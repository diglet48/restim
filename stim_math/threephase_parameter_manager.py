import time
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

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

    def add(self, value):
        self.value = value

    def interpolate(self, timeline):
        return self.value

    def last_value(self):
        return self.value


class ThreephaseParameterManager(QObject):
    def __init__(self, parent, config: ThreephaseConfiguration):
        super(ThreephaseParameterManager, self).__init__(parent)
        self.config = config

        self.alpha = ContinuousParameter(0.0)
        self.beta = ContinuousParameter(0.0)
        self.volume = ContinuousParameter(1.0)
        self.ramp_volume = ContinuousParameter(1.0)

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
                    return

    def set_alpha(self, value):
        self.alpha.add(value)

    def set_beta(self, value):
        self.beta.add(value)

    def set_volume(self, value):
        self.volume.add(value)

    def set_ramp_volume(self, value):
        self.ramp_volume.add(value)

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

    def set_calibration_parameters(self, calibration_params: stim_config.TransformParameters):
        self.calibration_neutral.add(calibration_params.up_down)
        self.calibration_right.add(calibration_params.left_right)
        self.calibration_center.add(calibration_params.center)

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

