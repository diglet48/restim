import numpy as np

from stim_math import threephase
from stim_math.audio_gen.params import NeoStimDebugParams
from stim_math.transforms import n_vec, l_vec, r_vec
from stim_math.threephase import ThreePhaseCenterCalibration
from dataclasses import dataclass



def get_bounds(position_alpha, position_beta, calibration_neutral, calibration_left):
    """
    Calculate the pulse bounds, i.e. the maximum/minimum charge balance of the pulse.
    :param position_alpha:
    :param position_beta:
    :param calibration_neutral:
    :param calibration_left:
    :return: (a, b, c) in 0...1
    """
    r = np.linalg.norm((position_alpha, position_beta))
    a = position_alpha / max(1, r)
    b = position_beta / max(1, r)
    r = min(1, r)
    mat = np.array([[2 - r + a, b],
                    [b, 2 - r - a]]) * 0.5
    hw = threephase.ThreePhaseHardwareCalibration(calibration_neutral, calibration_left)
    # TODO: something with scaling constant?
    calib = hw.generate_transform_in_ab()
    # TODO: quite inefficient. Exact solution must exist?
    theta = np.linspace(0, np.pi * 2, 100)
    carrier = np.array([np.cos(theta), np.sin(theta)])

    vals = calib[:2, :2] @ mat @ carrier
    bound_neutral = float(max(np.dot(n_vec, vals)))
    bound_left = float(max(np.dot(r_vec, vals)))        # ???
    bound_right = float(max(np.dot(l_vec, vals)))       # ???

    assert bound_neutral <= 1
    assert bound_left <= 1
    assert bound_right <= 1
    return bound_neutral, bound_left, bound_right




# @dataclass
# class Pulse:
#     polarity_a: int     # -1, 0 or 1
#     polarity_b: int     # -1, 0 or 1
#     polarity_c: int     # -1, 0 or 1
#     pulse_width_us: int # 0...255
#     start_time_us:  int # 0...2^32
#
#     def flip_polarity(self):
#         self.polarity_a *= -1
#         self.polarity_b *= -1
#         self.polarity_c *= -1
#
#     def to_burst(self):
#         electrode_set_ac, electrode_set_bd, polarity = {
#             (1, -1, 0): (1 << 0, 1 << 1, 0),
#             (-1, 1, 0): (1 << 0, 1 << 1, 1),
#             (1, 0, -1): (1 << 0, 1 << 3, 0),
#             (-1, 0, 1): (1 << 0, 1 << 3, 1),
#             (0, 1, -1): (1 << 2, 1 << 1, 1),
#             (0, -1, 1): (1 << 2, 1 << 1, 0),
#             (1, -.5, -.5): (1 << 0, 1 << 1 | 1 << 3, 0),
#             (-1, .5, .5): (1 << 0, 1 << 1 | 1 << 3, 1),
#             (.5, -1, .5): (1 << 0, 1 << 2 | 1 << 1, 0),
#             (-.5, 1, -.5): (1 << 0, 1 << 2 | 1 << 1, 1),
#         }[(self.polarity_a, self.polarity_b, self.polarity_c)]
#
#         return Burst(
#             meta = 0,
#             sequence_number=0, # TODO: fix
#             phase = np.uint8(polarity & 0x01),
#             pulse_width_µs=np.uint8(self.pulse_width_us),
#             start_time_us=self.start_time_us,
#             electrode_set=(electrode_set_ac, electrode_set_bd),
#             nr_of_pulses=1,
#             pace_1_4_ms=0,
#             amplitude=0,
#             delta_pulse_width_1_4_µs=0,
#             delta_pace_µs=0,
#         )


class ThreePhasePlanner:
    def __init__(self):
        self.seq = 0
        self.debug: NeoStimDebugParams = None

    def set_debug_options(self, debug: NeoStimDebugParams):
        self.debug = debug

    def compute_bounds(self, position_alpha, position_beta, volume,
                       calibration_neutral, calibration_left, calibration_center):
        # compute bounds (calibration)
        bound_neutral, bound_left, bound_right = get_bounds(0, 0, calibration_neutral, calibration_left)
        s = ThreePhaseCenterCalibration(calibration_center).get_scale(position_alpha, position_alpha)
        bound_neutral *= s * volume
        bound_left *= s * volume
        bound_right *= s * volume

        # transform half-scale position into full-scale position
        angle = np.arctan2(position_beta, position_alpha) / 2
        r = np.linalg.norm((position_alpha, position_beta))
        r = np.clip(r, 0, 1)
        position_alpha = np.cos(angle) * r
        position_beta = np.sin(angle) * r
        p = np.array((position_alpha, position_beta))

        def vec(angle):
            return np.array((np.cos(angle), np.sin(angle)))

        def absdot(vector):
            return np.abs(np.dot(p, vector))

        vec_n = vec(np.pi / 6 * 0)
        vec_nl = vec(np.pi / 6 * 1)
        vec_l = vec(np.pi / 6 * 2)
        vec_lr = vec(np.pi / 6 * 3)
        vec_r = vec(np.pi / 6 * 4)
        vec_nr = vec(np.pi / 6 * 5)


        n_strength = absdot(vec_n) + (1 - r)
        l_strength = absdot(vec_l) + (1 - r)
        r_strength = absdot(vec_r) + (1 - r)
        nl_strength = (max(0, (absdot(vec_nl) - 0.3)) / .7) ** 2
        lr_strength = (max(0, (absdot(vec_lr) - 0.3)) / .7) ** 2
        nr_strength = (max(0, (absdot(vec_nr) - 0.3)) / .7) ** 2

        # 100% power means A-B, B-C and A-C are at 100% duty.
        # to achieve equal intensity with A-BC and B-AC, duty cycle there needs to be reduced.
        # most likely by a factor of sqrt(3)/2
        n_strength *= self.debug.triplet_power
        l_strength *= self.debug.triplet_power

        n_strength = n_strength if self.debug.use_a else 0
        l_strength = l_strength if self.debug.use_b else 0
        nl_strength = nl_strength if self.debug.use_ab else 0
        nr_strength = nr_strength if self.debug.use_ac else 0
        lr_strength = lr_strength if self.debug.use_bc else 0

        if self.debug.emulate_ab_c:
            lr_strength = max(lr_strength, r_strength * self.debug.emulation_power)
            nr_strength = max(nr_strength, r_strength * self.debug.emulation_power)

        # print(n_strength, l_strength, '---', nl_strength, lr_strength, nr_strength)

        # apply calibration
        n_strength = n_strength * bound_neutral
        l_strength = l_strength * bound_left
        nr_strength = nr_strength * min(bound_neutral, bound_right)
        nl_strength = nl_strength * min(bound_neutral, bound_left)
        lr_strength = lr_strength * min(bound_left, bound_right)

        assert n_strength <= 1
        assert l_strength <= 1
        assert nr_strength <= 1
        assert nl_strength <= 1
        assert lr_strength <= 1

        return n_strength, l_strength, nr_strength, nl_strength, lr_strength

