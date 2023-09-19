import numpy as np
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
        carrier_x = np.cos(theta, dtype=np.float32)
        carrier_y = np.sin(theta, dtype=np.float32)
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


class ThreePhaseHardwareCalibration:
    """
    Attempt to reverse the effects of hardware bias by first transforming the (L, R) audio channel
    into (alpha, beta), and then scaling before transforming back to (L, R)

    method:
    [alpha, beta, 0] = P^-1 @ ab_transform^-1 @ [L, R, 0]
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

    def contour_in_ab(self, theta):
        transform = self.generate_transform_in_ab()
        alpha, beta, _ = transform @ [np.cos(theta), np.sin(theta), np.zeros_like(theta)]
        return alpha, beta

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
