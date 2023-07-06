from __future__ import unicode_literals


class ModulationParameters:
    def __init__(self, carrier_frequency,
                 modulation_1_enabled, modulation_1_freq, modulation_1_modulation, modulation_1_left_right_bias, modulation_1_high_low_bias,
                 modulation_2_enabled, modulation_2_freq, modulation_2_modulation, modulation_2_left_right_bias, modulation_2_high_low_bias):
        self.carrier_frequency = carrier_frequency
        self.modulation_1_enabled = modulation_1_enabled
        self.modulation_1_freq = modulation_1_freq
        self.modulation_1_modulation = modulation_1_modulation
        self.modulation_1_left_right_bias = modulation_1_left_right_bias
        self.modulation_1_high_low_bias = modulation_1_high_low_bias
        self.modulation_2_enabled = modulation_2_enabled
        self.modulation_2_freq = modulation_2_freq
        self.modulation_2_modulation = modulation_2_modulation
        self.modulation_2_left_right_bias = modulation_2_left_right_bias
        self.modulation_2_high_low_bias = modulation_2_high_low_bias


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
    def __init__(self, enabled, rotation_degrees, mirror, top, bottom, left, right):
        self.enabled = enabled
        self.rotation_degrees = rotation_degrees
        self.mirror = mirror
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right


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
