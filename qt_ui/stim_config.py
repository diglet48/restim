from __future__ import unicode_literals


class ModulationParameters:
    def __init__(self, carrier_frequency,
                 modulation_1_enabled, modulation_1_freq, modulation_1_modulation,
                 modulation_2_enabled, modulation_2_freq, modulation_2_modulation):
        self.carrier_frequency = carrier_frequency
        self.modulation_1_enabled = modulation_1_enabled
        self.modulation_1_freq = modulation_1_freq
        self.modulation_1_modulation = modulation_1_modulation
        self.modulation_2_enabled = modulation_2_enabled
        self.modulation_2_freq = modulation_2_freq
        self.modulation_2_modulation = modulation_2_modulation


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


class TransformParameters:
    def __init__(self, up_down, left_right, center):
        self.up_down = up_down
        self.left_right = left_right
        self.center = center
