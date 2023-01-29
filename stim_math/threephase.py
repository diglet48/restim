import numpy as np

from stim_math import ab_transform, trig

# for numerical stability, no intended change on output
regularization_parameter = 0.01


def generate_3_dof(timeline, frequency: float, amplitude, alpha, beta):
    """
    :param timeline: in seconds
    :param frequency: in hz
    :param amplitude: volume [0, 1] to avoid clipping output
    :param alpha:
    :param beta:
    :return: The (left, right) audio channel
    """
    assert np.all(trig.norm(alpha, beta) <= 1.001)

    def remap_xy(x, y):
        # project (x, y) onto the imaginary plane with i >= 0
        z = x + y * 1j
        len = np.absolute(z)
        z = np.sqrt(z) * len
        return np.real(z), np.imag(z)

    def rotate(x, y, angle):
        x2 = x * np.cos(angle) - y * np.sin(angle)
        y2 = x * np.sin(angle) + y * np.cos(angle)
        return x2, y2

    # use less mem
    alpha = alpha.astype(np.float32)
    beta = beta.astype(np.float32)

    # transform into appropriate coordinate system.
    alpha, beta = rotate(alpha, beta, -1.0 / 3 * np.pi)
    alpha, beta = remap_xy(alpha, beta)

    # three channel amplitudes
    a, b, c = ab_transform.inverse(alpha, beta)
    alpha, beta = None, None  # clean mem

    # might be able to optimize this away with smarter math?
    a = np.abs(a)
    b = np.abs(b)
    c = np.abs(c)

    # prevents rounding errors, division-by-zero in later steps. No functional change intended
    a = a * (1 - regularization_parameter) + regularization_parameter
    b = b * (1 - regularization_parameter) + regularization_parameter
    c = c * (1 - regularization_parameter) + regularization_parameter

    # Math so far only works at the edge of the unit circle, interpolate if (a, b) is near the center.
    # At the edge we have a**2 + b**2 + c**2 = 1.5. This sounds like a really nice property to preserve.
    # To interpolate we solve: (a + gamma)**2 + (b + gamma)**2 + (c + gamma)**2 = 1.5
    gamma = trig.solve_quadratic_equation(3.0, 2 * (a + b + c), (a**2 + b**2 + c**2) - 1.5)
    gamma = np.clip(gamma, 0, None)  # rounding error crap
    a = a + gamma
    b = b + gamma
    c = c + gamma

    # now we have our three channel amplitudes, solve this set of equations...
    # A = a * sin(x)            (left channel)
    # B = b * sin(x + delta)    (right channel)
    # C = c * sin(x + phi)      (center channel)
    # A + B + C = 0
    angle_bc, angle_ac, angle_ab = trig.solve_with_law_of_cotangents(a, b, c)
    delta = np.pi - angle_ab
    # phi = np.pi - angle_ac
    angle_bc, angle_ac, angle_ab, c, phi, gamma = None, None, None, None, None, None  # clean mem

    # all variables calculated! Now generate the final waveforms.
    x = timeline * (frequency * 2 * np.pi)
    A = a * np.sin(x).astype(np.float32)           # L, power between head and mid electrode
    B = b * np.sin(x + delta).astype(np.float32)   # -R, power between head and bottom electrode
    # C = c * np.sin(x + phi)                      # center, power between bottom and mid electrode
    return amplitude * A, amplitude * -B  # (L, R)
