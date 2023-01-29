import numpy as np


# https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_transformation
def transform(ia, ib, ic):
    mat = np.array([[1, -.5, -.5],
                    [0, np.sqrt(3) / 2, -np.sqrt(3) / 2],
                    [.5, .5, .5]])

    i = np.vstack((ia, ib, ic))
    return (2.0 / 3.0) * np.matmul(mat, i)


def inverse(a, b, y=None):
    if y is None:
        y = np.zeros_like(a)
    mat = np.array([[1, 0, 1],
                    [-0.5, np.sqrt(3) / 2, 1],
                    [-0.5, -np.sqrt(3) / 2, 1]]).astype(a.dtype)

    c = np.vstack((a, b, y))
    return np.matmul(mat, c)
