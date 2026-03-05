import numpy as np
from numpy import sqrt, pi

COEF_1 = 1
COEF_2 = sqrt(8) / 3        # sqrt(1 - coef_1**2/3)
COEF_3 = sqrt(2) / sqrt(3)  # sqrt(1 - coef_1**2/3 - coef_2**2/2)

ab_transform = np.array([
    [COEF_1, 0, 0, 1],
    [-COEF_1 / 3, COEF_2, 0, 1],
    [-COEF_1 / 3, -COEF_2 / 2, COEF_3, 1],
    [-COEF_1 / 3, -COEF_2 / 2, -COEF_3, 1],
])

ab_transform_inv = np.linalg.inv(ab_transform)

potential_to_channel_matrix = np.array([
    [1, -1, 0, 0],
    [0, 1, -1, 0],
    [0, 0, 1, -1],
    [1, 1, 1, 1],
])

potential_to_channel_matrix_inv = np.linalg.inv(potential_to_channel_matrix)

angle_1 = 0     # any
angle_2 = pi/3*2     # any
angle_3 = pi/3*4     # any
angle_matrix = np.array([
    [angle_1, 0,       0,       np.pi/2*0],
    [angle_1, angle_2, 0,       np.pi/2*1],
    [angle_1, angle_2, angle_3, np.pi/2*2],
    [angle_1, angle_2, angle_3, np.pi/2*3],
])
complex_matrix = np.exp(1j * angle_matrix)


a_vec = ab_transform[0, :-1]
b_vec = ab_transform[1, :-1]
c_vec = ab_transform[2, :-1]
d_vec = ab_transform[3, :-1]

alpha_vec = np.array([1, 0, 0])
beta_vec = np.array([0, 1, 0])
gamma_vec = np.array([0, 0, 1])


def abc_to_e1234(a, b, c):
    # ab transform
    e1, e2, e3, e4 = ab_transform[:, :3] @ (a, b, c)
    e = np.vstack([e1, e2, e3, e4])

    # ensure one component = 0
    min_index = np.argmin(np.abs(e), axis=0)
    z = e[min_index, np.arange(len(min_index))]
    e = e - z
    e = e / (4.0 / 3)
    e = np.abs(e)
    return e

def e1234_to_abc(e1, e2, e3, e4):
    assert np.all(e1 >= 0)
    assert np.all(e2 >= 0)
    assert np.all(e3 >= 0)
    assert np.all(e4 >= 0)

    e = np.vstack([e1, e2, e3, e4])
    # normalize: one component must be 0
    min_index = np.argmin(np.abs(e), axis=0)
    e = e - e[min_index, np.arange(len(min_index))]

    max_index = np.argmax(np.abs(e), axis=0)

    # select correct quadrant
    e[0, max_index == 0] *= -1
    e[1, max_index == 1] *= -1
    e[2, max_index == 2] *= -1
    e[3, max_index == 3] *= -1
    a, b, c = (e.T @ ab_transform[:, :3]).T

    q = np.vstack((a, b, c))
    z = np.sum(np.multiply(q[:, :-1], q[:, 1:]), axis=0)
    mask = z >= 0
    z[mask] = 1
    z[~mask] = -1
    invert = np.cumprod(z)
    q[:, 1:] *= invert
    a, b, c = q
    return a, b, c

def constrain_4p_amplitudes(a, b, c, d):
    a = np.clip(a, 0, 1)
    b = np.clip(b, 0, 1)
    c = np.clip(c, 0, 1)
    d = np.clip(d, 0, 1)

    s_a = min(-a + b + c + d, 0) / -3
    s_b = min( a - b + c + d, 0) / -3
    s_c = min( a + b - c + d, 0) / -3
    s_d = min( a + b + c - d, 0) / -3

    a += s_b + s_c + s_d
    b += s_a + s_c + s_d
    c += s_a + s_b + s_d
    d += s_a + s_b + s_c

    vec = [a, b, c, d]

    maximum = max(vec)
    if maximum < 1:
        to_add = 1 - maximum
        if vec[0] == maximum:
            vec = vec + to_add
            vec[0] = 1     # ensure floating point value is EXACTLY 1.0f
        elif vec[1] == maximum:
            vec = vec + to_add
            vec[1] = 1
        elif vec[2] == maximum:
            vec = vec + to_add
            vec[2] = 1
        elif vec[3] == maximum:
            vec = vec + to_add
            vec[3] = 1
        else:
            pass # unreachable ????

    return vec

# ---------------------------------------------------------------------------
# Per-electrode response curves (inspired by edger477/funscript-tools)
# ---------------------------------------------------------------------------

# Preset curve libraries.  Each curve is a list of (input, output) control
# points in [0, 1].  Linear interpolation between points.
CURVE_PRESETS = {
    'linear':   [(0.0, 0.0), (1.0, 1.0)],
    'ease_in':  [(0.0, 0.0), (0.5, 0.2), (1.0, 1.0)],
    'ease_out': [(0.0, 0.0), (0.5, 0.8), (1.0, 1.0)],
    'bell':     [(0.0, 0.0), (0.25, 0.3), (0.5, 1.0), (0.75, 0.3), (1.0, 0.0)],
    's_curve':  [(0.0, 0.0), (0.2, 0.05), (0.5, 0.5), (0.8, 0.95), (1.0, 1.0)],
    'inverted': [(0.0, 1.0), (1.0, 0.0)],
}

# Named preset packs that assign a curve to each electrode.
ELECTRODE_CURVE_PACKS = {
    'off':           ('linear', 'linear', 'linear', 'linear'),
    'edger_default': ('linear', 'ease_in', 'ease_out', 'bell'),
    'crossover':     ('ease_out', 'ease_in', 'ease_in', 'ease_out'),
    'emphasis_cd':   ('linear', 'linear', 's_curve', 's_curve'),
}


def apply_response_curve(value, control_points):
    """Map *value* (0-1) through piecewise-linear *control_points*.

    Works on scalars and numpy arrays alike.
    """
    value = np.clip(value, 0.0, 1.0)
    pts = sorted(control_points, key=lambda p: p[0])
    xs = np.array([p[0] for p in pts])
    ys = np.array([p[1] for p in pts])
    return np.clip(np.interp(value, xs, ys), 0.0, 1.0)


def apply_electrode_curves(e1, e2, e3, e4, curve_pack_name='off'):
    """Apply per-electrode response curves from a named preset pack.

    Returns shaped (e1, e2, e3, e4).  If *curve_pack_name* is 'off' or
    unknown the values pass through unchanged.
    """
    pack = ELECTRODE_CURVE_PACKS.get(curve_pack_name)
    if pack is None or curve_pack_name == 'off':
        return e1, e2, e3, e4

    curves = [CURVE_PRESETS.get(name, CURVE_PRESETS['linear']) for name in pack]
    e1 = apply_response_curve(e1, curves[0])
    e2 = apply_response_curve(e2, curves[1])
    e3 = apply_response_curve(e3, curves[2])
    e4 = apply_response_curve(e4, curves[3])
    return e1, e2, e3, e4


def position_based_gamma(a, b):
    """Derive gamma from alpha/beta radius using a bell curve.

    Gamma peaks when the position is at ~50% of maximum radius
    (mid-stroke for circular motion), and drops to zero at the extremes
    (resting at centre or at full extension).

    Works on both scalars and arrays.
    """
    r = np.sqrt(np.asarray(a, dtype=float)**2 + np.asarray(b, dtype=float)**2)
    # Normalize radius so 1.0 = sqrt(2) (the farthest corner of the unit square)
    r_norm = np.clip(r / np.sqrt(2.0), 0.0, 1.0)
    # Bell curve peaking at ~0.5 radius
    gamma = apply_response_curve(r_norm, CURVE_PRESETS['bell'])
    # Scale so peak gamma ≈ mean alpha/beta radius to keep proportions similar
    r_mean = float(np.mean(r)) if np.size(r) > 0 else 0.1
    return gamma * max(r_mean, 0.1)