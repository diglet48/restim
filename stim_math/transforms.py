import numpy as np

potential_to_channel_matrix = np.array([
    [1, -1, 0],
    [1, 0, -1],
    [1, 1, 1],
]).astype(np.float32)

potential_to_channel_matrix_inv = np.linalg.inv(potential_to_channel_matrix).astype(np.float32)

ab_transform = np.array([[1, 0, 1],
                         [-0.5, np.sqrt(3)/2, 1],
                         [-0.5, -np.sqrt(3)/2, 1]]).astype(np.float32)

ab_transform_inv = np.linalg.inv(ab_transform).astype(np.float32)

n_vec = ab_transform[0, :2]
l_vec = ab_transform[1, :2]
r_vec = ab_transform[2, :2]


def half_angle_to_full(a, b):
    """
    Convert half angle (one dot) notation to full angle (two dots on opposite side of circle).
    """
    theta = np.arctan2(b, a)
    r = np.linalg.norm((a, b), axis=0)
    theta = theta / 2
    a = np.cos(theta) * r
    b = np.sin(theta) * r
    return a, b

def full_angle_to_half(a, b):
    theta = np.arctan2(b, a)
    r = np.linalg.norm((a, b), axis=0)
    theta = theta * 2
    a = np.cos(theta) * r
    b = np.sin(theta) * r
    return a, b

def ab_to_e123(a, b):
    a, b = half_angle_to_full(a, b)

    # ab transform
    e1, e2, e3 = ab_transform[:, :2] @ (a, b)
    e = np.vstack([e1, e2, e3])

    # ensure one component = 0
    min_index = np.argmin(np.abs(e), axis=0)
    z = e[min_index, np.arange(len(min_index))]
    e = e - z
    e = e / 1.5
    e = np.abs(e)
    return e

def e123_to_ab(e1, e2, e3):
    assert np.all(e1 >= 0)
    assert np.all(e2 >= 0)
    assert np.all(e3 >= 0)

    e = np.vstack([e1, e2, e3])
    # normalize: one component must be 0
    min_index = np.argmin(np.abs(e), axis=0)
    e = e - e[min_index, np.arange(len(min_index))]

    # select correct quadrant
    e[2, min_index == 0] *= -1
    e[0, min_index == 1] *= -1
    e[1, min_index == 2] *= -1
    a, b = (e.T @ ab_transform[:, :2]).T
    return full_angle_to_half(a, b)