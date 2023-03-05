import numpy as np

potential_to_channel_matrix = np.array([
    [1, -1, 0],
    [1, 0, -1],
    [1, 1, 1],
])

potential_to_channel_matrix_inv = np.linalg.inv(potential_to_channel_matrix)

ab_transform = np.array([[1, 0, 1],
                         [-0.5, np.sqrt(3)/2, 1],
                         [-0.5, -np.sqrt(3)/2, 1]])

ab_transform_inv = np.linalg.inv(ab_transform)


def scale_in_arbitrary_direction(a, b, scale):
    # formula from:
    # https://computergraphics.stackexchange.com/questions/5586/what-does-it-mean-to-scale-in-an-arbitrary-direction
    s = (scale - 1)
    return np.array([[1 + s * a**2, s * a * b, 0],
                     [s * a * b, 1 + s * b**2, 0],
                     [0, 0, 1]])


class HardwareCalibration:
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

    def apply_transform(self, L, R):
        transform = self.generate_transform_in_ab()
        corrective_matrix = potential_to_channel_matrix @ ab_transform @ transform @ ab_transform_inv @ potential_to_channel_matrix_inv
        L, R, _ = corrective_matrix @ np.vstack((L, R, np.zeros_like(L)))
        return L, R
