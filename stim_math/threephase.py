import numpy as np
from stim_math.transforms import ab_transform, potential_to_channel_matrix


class ContinuousSineWaveform:
    """
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

    squeeze is a scale in arbitrary direction matrix:
    [[1 + (k-1) * x^2, (k-1) * x * y],
     [(k-1) * x * y,   1 + (k-1) * y^2]]
    (k-1) and (x, y) are chosen dependent on input (alpha, beta)

    carrier is:
    [[cos(timeline * frequency * 2 * pi)],
     [sin(timeline * frequency * 2 * pi)]]
    """
    @staticmethod
    def intensity(alpha, beta):
        """
        defined as norm(electrode_amplitude) * c
        with c such that intensity(r=1) = 1
        """
        r = np.clip(np.sqrt(alpha.astype(np.float32) ** 2 + beta.astype(np.float32) ** 2), None, 1.0)

        # for k_minus_1 = (1 - r) - 1
        return np.sqrt(1 - r + 0.5 * r**2) * np.sqrt(2)

        # for k_minus_1 = (1 - r**2) - 1
        # return np.sqrt(1 - r**2 + 0.5 * r**4) * np.sqrt(2)

    @staticmethod
    def scale_in_arbitrary_direction_coefs(alpha, beta):
        # faster and uses less mem
        alpha = alpha.astype(np.float32)
        beta = beta.astype(np.float32)

        r = np.clip(np.sqrt(alpha ** 2 + beta ** 2), None, 1.0)
        theta = np.arctan2(beta, alpha) / 2

        # scale by k = (1 - r) in direction of theta
        # TODO: maybe 1 - r**2? Or other?
        k_minus_1 = (1 - r) - 1
        y = np.cos(theta)
        x = np.sin(theta)

        # setup scale in arbitrary direction matrix
        # [[1 + (k-1) * x^2, (k-1) * x * y  ],
        #  [(k-1) * x * y,   1 + (k-1) * y^2]]
        t11 = 1 + k_minus_1 * x ** 2
        t12 = k_minus_1 * x * y
        t21 = t12
        t22 = 1 + k_minus_1 * y ** 2
        return t11, t12, t21, t22

    @staticmethod
    def carrier(timeline, frequency):
        t = timeline * (frequency * 2 * np.pi)
        carrier_x = np.cos(t).astype(np.float32)
        carrier_y = np.sin(t).astype(np.float32)
        return carrier_x, carrier_y

    @staticmethod
    def generate(timeline, frequency: float, alpha, beta, chunksize=10000):
        # split into chunks for better cache performance and lower peak memory usage
        if len(timeline) > (2 * chunksize):
            L = np.empty_like(timeline)
            R = np.empty_like(timeline)
            for start in np.arange(0, len(timeline), chunksize):
                end = start + chunksize
                l, r = ContinuousSineWaveform.generate(timeline[start:end],
                                                       frequency,
                                                       alpha[start:end],
                                                       beta[start:end])
                L[start:end] = l
                R[start:end] = r
            return L, R

        carrier_x, carrier_y = ContinuousSineWaveform.carrier(timeline, frequency)

        # apply scale in arbitrary direction
        t11, t12, t21, t22 = ContinuousSineWaveform.scale_in_arbitrary_direction_coefs(alpha, beta)
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
        Therefore N = a * cos + b * sin
        with (a, b) being the coefs in (squeeze)
        """

        def add_sine(a, b, phase):
            # amplitude of a * sin(x) + b * sin(x + phase)
            return np.sqrt(a ** 2 + b ** 2 + 2 * a * b * np.cos(phase))

        def find_phase(a, b, phase):
            # phase of a * sin(x) + b * sin(x + phase)
            return np.arctan2(a * np.sin(0) + b * np.sin(phase), a * np.cos(0) + b * np.cos(phase))

        t11, t12, t21, t22 = ContinuousSineWaveform.scale_in_arbitrary_direction_coefs(alpha, beta)
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
        t11, t12, t21, t22 = ContinuousSineWaveform.scale_in_arbitrary_direction_coefs(alpha, beta)
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
        t11, t12, t21, t22 = ContinuousSineWaveform.scale_in_arbitrary_direction_coefs(alpha, beta)
        squeeze = np.array([[t11, t12],
                            [t21, t22]])
        T = P @ ab_transform @ squeeze
        L = add_sine(T[0][0], T[1][0], np.pi/2)
        R = add_sine(T[0][1], T[1][1], np.pi/2)
        center = add_sine(T[0][2], T[1][2], np.pi/2)
        phase_L = find_phase(T[0][0], T[1][0], np.pi/2)
        phase_R = find_phase(T[0][1], T[1][1], np.pi/2)
        return L, R, center, np.abs(phase_L - phase_R)
