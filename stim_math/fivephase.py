import numpy as np

from stim_math.fourphase import split_point


class FivePhaseSignalGenerator:
    def __int__(self):
        pass

    def generate_from_electrode_amplitudes(self, theta, a, b, c, d, e, assume_valid=False):
        """
        :param theta:   t*2*pi*frequency
        :param a:   amplitide of electrode a
        :param b:   amplitude of electrode b
        :param c:   amplitude of electrode c
        :param d:   amplitude of electrode d
        :param e:   amplitude of electrode e
        :param assume_valid:
        :return:       5 electrode currents
        """
        a, b, c, d, e = self.project_on_complex_plane(a, b, c, d, e, assume_valid=assume_valid)

        # convert complex points to sine waves
        cos = np.cos(theta)
        sin = np.sin(theta)
        a = cos * np.real(a) + sin * np.imag(a)
        b = cos * np.real(b) + sin * np.imag(b)
        c = cos * np.real(c) + sin * np.imag(c)
        d = cos * np.real(d) + sin * np.imag(d)
        e = cos * np.real(e) + sin * np.imag(e)
        return a, b, c, d, e

    def check_constraints(self, a, b, c, d, e):
        # these constraints must hold:
        #  a+b+c+d-e >= 0
        #  a+b+c-d+e >= 0
        #  a+b-c+d+e >= 0
        #  a-b+c+d+e >= 0
        # -a+b+c+d+e >= 0
        # check and fix these constraints by projecting on the nearest point for which all(in[] > out[])
        # NOTE: due to rounding errors, it's possible that a+b+c-d = -0.0000000000001 after verification

        s_a = np.clip(-a+b+c+d+e, None, 0)
        s_b = np.clip(a-b+c+d+e, None, 0)
        s_c = np.clip(a+b-c+d+e, None, 0)
        s_d = np.clip(a+b+c-d+e, None, 0)
        s_e = np.clip(a+b+c+d-e, None, 0)
        adjustment = (np.ones((5, 5)) - np.eye(5)) / -4
        [a, b, c, d, e] = [a, b, c, d, e] + adjustment @ [s_a, s_b, s_c, s_d, s_e]

        if np.any(a+b+c+d-e < -0.001):
            print(a+b+c+d-e)
            assert(False)
        if np.any(a+b+c-d+e < -0.001):
            print(a+b+c-d+e)
            assert(False)
        if np.any(a+b-c+d+e < -0.001):
            print(a+b-c+d+e)
            assert(False)
        if np.any(a-b+c+d+e < -0.001):
            print(a-b+c+d+e)
            assert(False)
        if np.any(-a+b+c++d+e < -0.001):
            print(-a+b+c+d+e)
            assert(False)

        return a, b, c, d, e

    def project_on_complex_plane(self, a, b, c, d, e, assume_valid=False):
        """
        Find 4 points on the complex plane, such that norm(points) = [a, b, c, d, e] and sum(points) = 0
        """
        if not assume_valid:
            a, b, c, d, e = self.check_constraints(a, b, c, d, e)

        def range_from_two_reals(a, b):
            return np.abs(a-b), b+a

        def range_from_range_and_real(a, b):
            return np.clip(np.maximum(b - a[1], a[0] - b), 0, None), a[1] + b

        def union(left, right):
            return np.maximum(left[0], right[0]), np.minimum(left[1], right[1])


        a_b_range = range_from_two_reals(a, b)
        c_d_range = range_from_two_reals(c, d)
        c_d_e_range = range_from_range_and_real(c_d_range, e)

        p = union(a_b_range, c_d_e_range)
        p = np.average(p, axis=0)

        a, b = split_point(p, a, b)

        p_e_range = range_from_two_reals(p, e)
        c_d = union(c_d_range, p_e_range)
        c_d = np.average(c_d, axis=0)

        c_d, e = split_point(-p, c_d, e)

        c, d = split_point(c_d, c, d)
        return a, b, c, d, e


class FivePhaseHardwareCalibration:
    """
    Transform desired currents (5 vectors) to channel voltages (4 vectors),
    using user-provided hardware calibration parameters.
    """
    def __init__(self, t, s1, s2, s3, s4, s5):
        self.t = t

        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.s5 = s5

    def scaling_constant(self):
        """
        find a constant such that C * (st @ currents) never results in clipping.
        """
        return 1 / np.max([
            self.s1 + self.s2 + self.t,
            self.s2 + self.s3 + self.t + self.t,
            self.s3 + self.s4 + self.t + self.t,
            self.s4 + self.s5 + self.t,
        ])

    def s_t_matrix(self):
        t = self.t
        s1, s2, s3, s4, s5 = self.s1, self.s2, self.s3, self.s4, self.s5
        st = np.array([
            [-s1, s2+t, t, t, t],
            [0, -s2, s3+t, t, t],
            [0, 0, -s3, s4+t, t],
            [0, 0, 0, -s4, s5+t],
            # [1, 1, 1, 1]
        ])
        return st * self.scaling_constant()

    def transform(self, a, b, c, d, e):
        return self.s_t_matrix() @ [a, b, c, d, e]
