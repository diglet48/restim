import numpy as np


def split_point(m, a, b):
    """
    Replace the point m in the complex plane with two complex points p, q. Such that:
    p+q = m
    norm(p) = a
    norm(q) = b
    Requires abs(a-b) <= abs(m) <= a+b
    :param m: complex point
    :param a: float, desired distance of point from origin
    :param b: float, desired distance of point from origin
    """
    m_normalized = np.exp(np.angle(m) * 1j)

    c = np.abs(m)
    # handle special case c == 0. Note that if c==0 then a==b, therefore solution is trivial.
    c = np.clip(c, 0.0001, None)
    rational = (a**2 - b**2 + c**2) / (2 * c)
    imaginary = np.sqrt(np.clip(a**2 - rational**2, 0, None))

    p = rational + 1j * imaginary
    p = p * m_normalized
    q = m - p
    return p, q


class FourPhaseSignalGenerator:
    def __int__(self):
        pass

    # TODO: this doesn't appear to be useful, remove?
    # def generate_from_position(self, theta, alpha, beta, gamma):
    #     """
    #     :param theta:   t*2*pi*frequency
    #     :param alpha:   position
    #     :param beta:    position
    #     :param gamma:   position
    #     :return:        4 electrode currents
    #     """
    #     vec = np.array(alpha, beta, gamma)
    #     r = np.sqrt(alpha**2 + beta**2 + gamma**2) / 2
    #
    #     a = np.linalg.norm(vec * r + transforms_4.a_vec * (1 - r))
    #     b = np.linalg.norm(vec * r + transforms_4.b_vec * (1 - r))
    #     c = np.linalg.norm(vec * r + transforms_4.c_vec * (1 - r))
    #     d = np.linalg.norm(vec * r + transforms_4.d_vec * (1 - r))
    #     return self.generate_from_electrode_amplitudes(theta, a, b, c, d, assume_valid=True)

    def generate_from_electrode_amplitudes(self, theta, a, b, c, d, assume_valid=False):
        """
        :param theta:   t*2*pi*frequency
        :param a:   amplitide of electrode a
        :param b:   amplitude of electrode b
        :param c:   amplitude of electrode c
        :param d:   amplitude of electrode d
        :param assume_valid:
        :return:       4 electrode currents
        """
        a, b, c, d = self.project_on_complex_plane(a, b, c, d, assume_valid=assume_valid)

        # convert complex points to sine waves
        cos = np.cos(theta)
        sin = np.sin(theta)
        a = cos * np.real(a) + sin * np.imag(a)
        b = cos * np.real(b) + sin * np.imag(b)
        c = cos * np.real(c) + sin * np.imag(c)
        d = cos * np.real(d) + sin * np.imag(d)
        return a, b, c, d

    def check_constraints(self, a, b, c, d):
        # these constraints must hold:
        #  a+b+c-d >= 0
        #  a+b-c+d >= 0
        #  a-b+c+d >= 0
        # -a+b+c+d >= 0
        # check and fix these constraints by projecting on the nearest point for which all(in[] > out[])
        # NOTE: due to rounding errors, it's possible that a+b+c-d = -0.0000000000001 after verification

        s_a = np.clip(-a+b+c+d, None, 0)
        s_b = np.clip(a-b+c+d, None, 0)
        s_c = np.clip(a+b-c+d, None, 0)
        s_d = np.clip(a+b+c-d, None, 0)
        adjustment = (np.ones((4, 4)) - np.eye(4)) / -3
        [a, b, c, d] = [a, b, c, d] + adjustment @ [s_a, s_b, s_c, s_d]

        if np.any(np.all(a+b+c-d < -0.001)):
            print(a+b+c-d)
            assert(False)
        if np.any(a+b-c+d < -0.001):
            print(a+b-c+d)
            assert(False)
        if np.any(a-b+c+d < -0.001):
            print(a-b+c+d)
            assert(False)
        if np.any(-a+b+c+d < -0.001):
            print(-a+b+c+d)
            assert(False)

        return a, b, c, d

    def project_on_complex_plane(self, a, b, c, d, assume_valid=False):
        """
        Find 4 points on the complex plane, such that norm(points) = [a, b, c, d] and sum(points) = 0
        Strategy:
        first place 2 points, p and -p
        replace p by 2 new points: a and b
        replace -p by 2 new points: c and d

        p in (abs(a-b), a+b) and in (abs(c-d), c+d)
        """
        if not assume_valid:
            a, b, c, d = self.check_constraints(a, b, c, d)

        # construct point p, such that abs(a-b) <= abs(p) <= a+b
        p_min = np.abs(c - d)
        p_max = c + d
        p_max = np.clip(p_max, a_min=None, a_max=a + b)
        p_min = np.clip(p_min, a_min=np.abs(a - b), a_max=None)
        p = np.average((p_min, p_max), axis=0)

        a, b = split_point(p, a, b)
        c, d = split_point(-p, c, d)
        return a, b, c, d


class FourPhaseHardwareCalibration:
    """
    Transform desired currents (4 vectors) to channel voltages (3 vectors),
    using user-provided hardware calibration parameters.
    """
    def __init__(self, t, s1, s2, s3, s4):
        self.t = t
        # self.t = 5

        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4

    def scaling_constant(self):
        """
        find a constant such that c * (st @ v) never results in clipping.
        """
        return 1 / np.max([
            self.s1 + self.s2 + self.t,
            self.s2 + self.s3 + self.t + self.t,
            self.s3 + self.s4 + self.t,
        ])

    def s_t_matrix(self):
        t = self.t
        s1, s2, s3, s4 = self.s1, self.s2, self.s3, self.s4
        st = np.array([
            [-s1, s2+t, t, t],
            [0, -s2, s3+t, t],
            [0, 0, -s3, s4+t],
            # [1, 1, 1, 1]
        ])
        return st * self.scaling_constant()

    def transform(self, a, b, c, d):
        return self.s_t_matrix() @ [a, b, c, d]
