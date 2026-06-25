import numpy as np

from stim_math import trig
from stim_math.transforms import (
    potential_to_channel_matrix, potential_to_channel_matrix_inv,
    ab_transform, ab_transform_inv)


class ThreePhaseSignalGenerator:
    """
    See also https://github.com/diglet48/restim/wiki/technical-documentation

    The idea is that:
    [L, R, 0]^T = P @ ab_transform @ squeeze @ carrier

    Where P is the electrode-to-channel projection:
    [[1, -1,  0],
     [1,  0, -1],
     [-,  -,  -]

    ab_transform is the alpha-beta transform, which converts a vector of 2 (alpha, beta, -) to
    a vector of 3 (potentials at electrode N, L, R) with (N + L + R) = 0
    [[1,     0,           -],   (represents electrode N)
     [-0.5,  sin(2/3*pi), -],   (represents electrode L)
     [-0.5, -sin(2/3*pi), -]]   (represents electrode R)

    squeeze is this funky projection matrix, the derivation of this matrix is listed on the wiki
    [[2 - r + alpha, -beta],
     [-beta,         2 - r - alpha]] * 0.5

    carrier is:
    [[cos(timeline * frequency * 2 * pi)],
     [sin(timeline * frequency * 2 * pi)]]
    """
    @staticmethod
    def project_on_ab_coefs(alpha, beta):
        # faster and uses less mem
        alpha = alpha.astype(np.float32)
        beta = beta.astype(np.float32)

        r = np.sqrt(alpha ** 2 + beta ** 2)
        # sanitize input
        mask = r > 1
        alpha[mask] /= r[mask]
        beta[mask] /= r[mask]
        r[mask] = 1

        t11 = (2 - r + alpha) / 2
        t12 = -beta / 2  # TODO: calculations performed for the wiki arrive at +beta/2, where did we mess up?
        t21 = t12
        t22 = (2 - r - alpha) / 2
        return t11, t12, t21, t22

    @staticmethod
    def carrier(theta):
        carrier_x = np.cos(theta).astype(np.float32)
        carrier_y = np.sin(theta).astype(np.float32)
        return carrier_x, carrier_y

    @staticmethod
    def generate(theta, alpha, beta, chunksize=10000):
        # split into chunks for better cache performance and lower peak memory usage
        if len(theta) > (2 * chunksize):
            L = np.empty_like(theta, dtype=np.float32)
            R = np.empty_like(theta, dtype=np.float32)
            for start in np.arange(0, len(theta), chunksize):
                end = start + chunksize
                l, r = ThreePhaseSignalGenerator.generate(theta[start:end],
                                                          alpha[start:end],
                                                          beta[start:end])
                L[start:end] = l
                R[start:end] = r
            return L, R

        carrier_x, carrier_y = ThreePhaseSignalGenerator.carrier(theta)

        # apply projection
        t11, t12, t21, t22 = ThreePhaseSignalGenerator.project_on_ab_coefs(alpha, beta)
        a = t11 * carrier_x + t12 * carrier_y
        b = t21 * carrier_x + t22 * carrier_y

        T = (potential_to_channel_matrix @ ab_transform)[:2, :2] / np.sqrt(3)
        L, R = T @ np.array([a, b])
        return L, R

    @staticmethod
    def alpha_beta_amplitude(alpha, beta):
        """
        Returns the amplitude of alpha and beta axis

        [alpha, beta] = squeeze @ [cos, sin]
        Therefore alpha = a * cos + b * sin
        with (a, b) being the coefs in (squeeze)
        """

        def add_sine(a, b, phase):
            # amplitude of a * sin(x) + b * sin(x + phase)
            return np.sqrt(a ** 2 + b ** 2 + 2 * a * b * np.cos(phase))

        def find_phase(a, b, phase):
            # phase of a * sin(x) + b * sin(x + phase)
            return np.arctan2(a * np.sin(0) + b * np.sin(phase), a * np.cos(0) + b * np.cos(phase))

        t11, t12, t21, t22 = ThreePhaseSignalGenerator.project_on_ab_coefs(alpha, beta)
        squeeze = np.array([[t11, t12],
                            [t21, t22]])
        T = squeeze
        A = add_sine(T[0][0], T[1][0], np.pi / 2)
        B = add_sine(T[0][1], T[1][1], np.pi / 2)
        phase_A = find_phase(T[0][0], T[1][0], np.pi / 2)
        phase_B = find_phase(T[0][1], T[1][1], np.pi / 2)
        return A, B, np.abs(phase_A - phase_B)

    @staticmethod
    def electrode_amplitude(alpha, beta):
        """
        Returns the amplitude of the electrodes.

        [N, L, R] = ab_transform @ squeeze @ [cos, sin]
        Therefore N = a * cos + b * sin
        with (a, b) being the coefs in (ab_transform @ squeeze)
        """
        def add_sine(a, b, phase):
            # amplitude of a * sin(x) + b * sin(x + phase)
            return np.sqrt(a**2 + b**2 + 2 * a * b * np.cos(phase))

        ab_transform = np.array([[1, 0],
                                 [-0.5, np.sqrt(3)/2],
                                 [-0.5, -np.sqrt(3)/2]]) / np.sqrt(3)
        t11, t12, t21, t22 = ThreePhaseSignalGenerator.project_on_ab_coefs(alpha, beta)
        squeeze = np.array([[t11, t12],
                            [t21, t22]])
        T = ab_transform @ squeeze
        N = add_sine(T[0][0], T[1][0], np.pi/2)
        L = add_sine(T[0][1], T[1][1], np.pi/2)
        R = add_sine(T[0][2], T[1][2], np.pi/2)
        return N, L, R

    @staticmethod
    def channel_amplitude(alpha, beta):
        """
        Returns the amplitude of the channels.

        [L, R, -] = P @ ab_transform @ squeeze @ [cos, sin]
        Therefore L = a * cos + b * sin
        with (a, b) being the coefs in (P @ ab_transform @ squeeze)
        """
        def add_sine(a, b, phase):
            # amplitude of a * sin(x) + b * sin(x + phase)
            return np.sqrt(a**2 + b**2 + 2 * a * b * np.cos(phase))

        def find_phase(a, b, phase):
            # phase of a * sin(x) + b * sin(x + phase)
            return np.arctan2(a * np.sin(0) + b * np.sin(phase), a * np.cos(0) + b * np.cos(phase))

        P = np.array([[1, -1, 0],
                      [1, 0, -1],
                      [0, 1, -1]])
        ab_transform = np.array([[1, 0],
                                 [-0.5, np.sqrt(3)/2],
                                 [-0.5, -np.sqrt(3)/2]]) / np.sqrt(3)
        t11, t12, t21, t22 = ThreePhaseSignalGenerator.project_on_ab_coefs(alpha, beta)
        squeeze = np.array([[t11, t12],
                            [t21, t22]])
        T = P @ ab_transform @ squeeze
        L = add_sine(T[0][0], T[1][0], np.pi/2)
        R = add_sine(T[0][1], T[1][1], np.pi/2)
        center = add_sine(T[0][2], T[1][2], np.pi/2)
        phase_L = find_phase(T[0][0], T[1][0], np.pi/2)
        phase_R = find_phase(T[0][1], T[1][1], np.pi/2)
        return L, R, center, np.abs(phase_L - phase_R)


def scale_in_arbitrary_direction(a, b, scale):
    # formula from:
    # https://computergraphics.stackexchange.com/questions/5586/what-does-it-mean-to-scale-in-an-arbitrary-direction
    s = (scale - 1)
    return np.array([[1 + s * a**2, s * a * b, 0],
                     [s * a * b, 1 + s * b**2, 0],
                     [0, 0, 1]])

def inverse_scale_in_arbitrary_direction(matrix):
    s = matrix[0, 0] + matrix[1, 1] - 2
    scale = s + 1
    if s == 0:
        return 0, 0, 1
    a = np.abs((matrix[0, 0] - 1) / s) ** .5
    b = np.abs((matrix[1, 1] - 1) / s) ** .5
    if matrix[0, 1] <= 0:
        b = -b
    return a, b, scale


def calibration_matrix_from_ud_lr(up_down, left_right):
    """
    Calculate calibration matrix from up-down, left-right (in dB) format.
    The largest eigenvector of the result is 1
    """
    if (up_down, left_right) == (0, 0):
        return np.eye(3)

    theta = np.arctan2(left_right, up_down) / 2
    norm = np.sqrt(up_down ** 2 + left_right ** 2)
    ratio = 10 ** (norm / 10)
    return scale_in_arbitrary_direction(np.sin(-theta), np.cos(theta), 1/ratio)


def calibration_matrix_from_electrode_intensities(a, b, c):
    """
    Calculate calibration matrix from electrode intensities (in ratio) format.
    The largest eigenvector of the result is 1
    """
    def split_point(m, a, b):
        m_normalized = 1
        if np.abs(m) > .001:
            m_normalized = m / np.abs(m)

        # handle special case c == 0. Note that if c==0 then a==b, therefore solution is trivial.
        c = max(0.0001, np.abs(m))
        rational = (a * a - b * b + c * c) / (2 * c)
        imaginary = np.sqrt(max(a * a - rational * rational, 0))

        p = (rational + 1j * imaginary) * m_normalized
        q = m - p
        return p, q

    assert a > 0
    assert b > 0
    assert c > 0

    # clamp max = 1
    maximum = np.max([a, b, c])
    a /= maximum
    b /= maximum
    c /= maximum
    max_index = np.argmax([a, b, c])

    # check for valid input. Must have min(a, b, c) + mid(a, b, c) >= max(a, b, c)
    if max_index == 0:
        if b + c < a:
            offset = (a - (b + c)) / 2
            b += offset
            c += offset
    if max_index == 1:
        if a + c < b:
            offset = (b - (a + c)) / 2
            a += offset
            c += offset
    if max_index == 2:
        if a + b < c:
            offset = (c - (a + b)) / 2
            a += offset
            b += offset

    ab = np.array([
        [1, 0],
        [-0.5, -np.sqrt(3) / 2],
        [-0.5, np.sqrt(3) / 2],
    ])
    complex_b, complex_c = split_point(-a, b, c)
    ab2 = np.array([
        [a, 0],
        [np.real(complex_b), np.imag(complex_b)],
        [np.real(complex_c), np.imag(complex_c)],
    ])

    calib, resid, rank, singular = np.linalg.lstsq(ab[:, :2], ab2[:, :2])

    # rotate so matrix[0, 1] equals matrix[1, 0]
    q = np.arctan2(calib[0, 1] - calib[1, 0], calib[0, 0] + calib[1, 1])
    rot = np.array([[np.cos(q), -np.sin(q)], [np.sin(q), np.cos(q)]])
    calib = calib @ rot

    # scale so largest eigenvector is equal to 1
    largest_eigenvalue = np.max(np.linalg.eigvals(calib[:2, :2]))
    calib /= largest_eigenvalue
    return calib

def calibration_matrix_to_ud_lr(calib):
    """
    Must have calib[0, 1] == calib[1, 0] and
    max(eigval(calib)) == 1
    """
    a, b, scale = inverse_scale_in_arbitrary_direction(calib)
    ratio = 1 / np.clip(scale, .001, None)
    theta = -np.arctan2(a, -b)
    norm = np.log10(ratio) * 10
    theta = theta * 2
    ud = np.cos(theta) * norm
    lr = -np.sin(theta) * norm
    return ud, lr


def intensity_ratio_to_ud_lr(a, b, c):
    calib = calibration_matrix_from_electrode_intensities(a, b, c)
    return calibration_matrix_to_ud_lr(calib)

def ud_lr_to_intensity_ratio(ud, lr):
    """
    Compute the electrode intensities from up-down and left-right
    calibration format. Normalized to 1
    :param ud:
    :param lr:
    :return:
    """
    hw = ThreePhaseHardwareCalibration(ud, lr)
    calib = hw.generate_transform_in_ab()
    ab = np.array([
        [1, 0, 0],
        [-0.5, np.sqrt(3) / 2, 0],
        [-0.5, -np.sqrt(3) / 2, 1],
    ])
    z = ab[:, :2] @ calib[:2, :2]
    intensities = np.linalg.norm(z[:, :2], axis=1)
    intensities /= np.max(intensities)
    return intensities

class ThreePhaseHardwareCalibration:
    """
    Attempt to reverse the effects of hardware bias by first transforming the (L, R) audio channel
    into (alpha, beta), and then scaling before transforming back to (L, R)

    method:
    [alpha, beta, 0] = ab_transform^-1 @ P^-1 @ [L, R, 0]
    [alpha, beta, 0] = inverse_hardware_transform @ [alpha, beta, 0]
    [L, R, 0] = P @ ab_transform @ [alpha, beta, 0]
    """
    def __init__(self, up_down, left_right):
        self.up_down = up_down  # in dB
        self.left_right = left_right  # in dB

    def generate_transform_in_ab(self):
        if (self.up_down, self.left_right) == (0, 0):
            return np.eye(3)

        theta = np.arctan2(self.left_right, self.up_down) / 2
        norm = np.sqrt(self.up_down ** 2 + self.left_right ** 2)
        ratio = 10 ** (norm / 10)
        return scale_in_arbitrary_direction(np.sin(-theta), np.cos(theta), 1/ratio)

    def scaling_contant(self, transform_in_ab):
        """
        [L,     [[a, b],     [alpha,
         R]  =   [c, d]]  *   beta]
        We want |L| <= 1 and |R| <= 1
        We know that norm(alpha, beta) <= 1
        so we must scale matrix such that:
        - norm(a, b) <= 1 and
        - norm(c, d) <= 1
        """
        qq = potential_to_channel_matrix @ ab_transform @ transform_in_ab
        k1 = np.linalg.norm([qq[0, 0], qq[0, 1]])
        k2 = np.linalg.norm([qq[1, 0], qq[1, 1]])
        k = 1 / np.max((k1, k2))
        return k * 3**.5

    def apply_transform(self, L, R):
        transform = self.generate_transform_in_ab()
        corrective_matrix = potential_to_channel_matrix @ ab_transform @ transform @ ab_transform_inv @ potential_to_channel_matrix_inv
        corrective_matrix = corrective_matrix * self.scaling_contant(transform)
        L, R = corrective_matrix[:2, :2] @ (L, R)
        return L, R


class ThreePhaseCenterCalibration:
    """
    Reduce volume in the center of the phase diagram (linear scale).
    """
    def __init__(self, db_in_center):
        self.db_in_center = db_in_center

    def get_scale(self, x, y):
        ratio = 10 ** (self.db_in_center / 10)
        norm = trig.norm(x, y).clip(min=None, max=1)

        if ratio <= 1:
            edge = 1
            center = ratio
        else:
            edge = 1/ratio
            center = 1

        return center + norm * (edge - center)
