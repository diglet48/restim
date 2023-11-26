from __future__ import unicode_literals


class VibrationParameters:
    def __init__(self,
                 vibration_1_enabled, vibration_1_freq, vibration_1_strength, vibration_1_left_right_bias, vibration_1_high_low_bias, vibration_1_random,
                 vibration_2_enabled, vibration_2_freq, vibration_2_strength, vibration_2_left_right_bias, vibration_2_high_low_bias, vibration_2_random,
                 ):
        self.vibration_1_enabled = vibration_1_enabled
        self.vibration_1_freq = vibration_1_freq
        self.vibration_1_strength = vibration_1_strength
        self.vibration_1_left_right_bias = vibration_1_left_right_bias
        self.vibration_1_high_low_bias = vibration_1_high_low_bias
        self.vibration_1_random = vibration_1_random
        self.vibration_2_enabled = vibration_2_enabled
        self.vibration_2_freq = vibration_2_freq
        self.vibration_2_strength = vibration_2_strength
        self.vibration_2_left_right_bias = vibration_2_left_right_bias
        self.vibration_2_high_low_bias = vibration_2_high_low_bias
        self.vibration_2_random = vibration_2_random


class Mk312Parameters:
    def __init__(self, carrier_frequency):
        self.carrier_frequency = carrier_frequency


class PulseParameters:
    def __init__(self, carrier_frequency, pulse_frequency, pulse_width, pulse_interval_random, polarity, device_emulation_mode, pulse_phase_offset_increment):
        self.carrier_frequency = carrier_frequency
        self.pulse_frequency = pulse_frequency
        self.pulse_width = pulse_width
        self.pulse_interval_random = pulse_interval_random
        self.polarity = polarity
        self.device_emulation_mode = device_emulation_mode
        self.pulse_phase_offset_increment = pulse_phase_offset_increment


class CalibrationParameters:
    def __init__(self, center,
                 mid_0_3pi, mid_1_3pi, mid_2_3pi, mid_3_3pi, mid_4_3pi, mid_5_3pi,
                 edge_0_3pi, edge_1_3pi, edge_2_3pi, edge_3_3pi, edge_4_3pi, edge_5_3pi):
        self.center = center
        self.mid_0_3pi = mid_0_3pi
        self.mid_1_3pi = mid_1_3pi
        self.mid_2_3pi = mid_2_3pi
        self.mid_3_3pi = mid_3_3pi
        self.mid_4_3pi = mid_4_3pi
        self.mid_5_3pi = mid_5_3pi
        self.edge_0_3pi = edge_0_3pi
        self.edge_1_3pi = edge_1_3pi
        self.edge_2_3pi = edge_2_3pi
        self.edge_3_3pi = edge_3_3pi
        self.edge_4_3pi = edge_4_3pi
        self.edge_5_3pi = edge_5_3pi


class PositionParameters:
    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta


class ThreePhaseCalibrationParameters:
    def __init__(self, up_down, left_right, center):
        self.up_down = up_down
        self.left_right = left_right
        self.center = center


class ThreePhaseTransformParameters:
    def __init__(self, enabled, rotation_degrees, mirror, top, bottom, left, right, exponent):
        self.enabled = enabled
        self.rotation_degrees = rotation_degrees
        self.mirror = mirror
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.exponent = exponent


class FivePhaseCurrentParameters:
    def __init__(self, i1, i2, i3, i4, i5):
        self.i1 = i1
        self.i2 = i2
        self.i3 = i3
        self.i4 = i4
        self.i5 = i5


class FivePhaseResistanceParameters:
    def __init__(self, t, s1, s2, s3, s4, s5):
        self.t = t
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.s5 = s5
