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

