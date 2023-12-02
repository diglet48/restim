import numpy as np


class ThreePhaseCoordinateTransform:
    def __init__(self, rotation, mirror, top, bottom, left, right):
        mirror_matrix = np.eye(3)
        if mirror:
            mirror_matrix[1, 1] = -1

        rotation_in_rad = np.deg2rad(rotation)
        # rotate clockwise
        rotation_in_rad *= -1
        cos, sin = np.cos(rotation_in_rad), np.sin(rotation_in_rad)
        rotation_matrix = np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])

        alpha_center = (top + bottom) / 2
        beta_center = -(left + right) / 2
        alpha_scale = (top - bottom) / 2
        beta_scale = (right - left) / 2
        limits_matrix = np.array([
            [alpha_scale, 0, alpha_center],
            [0, beta_scale, beta_center],
            [0, 0, 1]]
        )
        self.matrix = limits_matrix @ rotation_matrix @ mirror_matrix

    def transform(self, alpha, beta):
        a, b, _ = self.matrix @ [alpha, beta, np.ones_like(alpha)]
        return a, b

    def inverse_transform(self, alpha, beta):
        matrix = np.linalg.inv(self.matrix)
        a, b, _ = matrix @ [alpha, beta, np.ones_like(alpha)]
        return a, b


class ThreePhaseCoordinateTransformMapToEdge:
    def __init__(self, start, length, invert):
        self.start = start
        self.end = start + length
        if invert:
            self.start, self.end = self.end, self.start

    def transform(self, alpha, beta):
        angle = self.start + (alpha * -0.5 + 0.5) * (self.end - self.start)
        return np.cos(np.deg2rad(-angle)), np.sin(np.deg2rad(-angle))

    def inverse_transform(self, alpha, beta):
        # this function is surprisingly hard to implement... so we don't! Who cares?
        return alpha, beta
