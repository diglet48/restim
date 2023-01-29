import numpy as np


def solve_with_law_of_cosines(a, b, c):
    """
    triangle with side lengths a, b, c. Solve for angle
    alpha = angle opposed to a
    beta = angle opposed to b
    gamma = angle opposed to c
    """
    assert np.all(a >= 0)
    assert np.all(b >= 0)
    assert np.all(c >= 0)

    a_2 = a**2
    b_2 = b**2
    c_2 = c**2

    alpha = np.arccos((b_2 + c_2 - a_2) / (2*b*c))
    beta = np.arccos((a_2 + c_2 - b_2) / (2*a*c))
    # gamma = np.arccos((a_2 + b_2 - c_2) / (2*a*b))
    gamma = (np.pi) - alpha - beta

    return alpha, beta, gamma


def solve_with_law_of_cotangents(a, b, c):
    """
    triangle with side lengths a, b, c. Solve for angle
    alpha = angle opposed to a
    beta = angle opposed to b
    gamma = angle opposed to c
    """
    assert np.all(a >= 0)
    assert np.all(b >= 0)
    assert np.all(c >= 0)

    s = (a + b + c) * 0.5
    r = np.sqrt((s - a) * (s - b) * (s - c) / s)

    alpha = 2 * np.arctan(r / (s-a))
    beta = 2 * np.arctan(r / (s-b))
    gamma = 2 * np.arctan(r / (s-c))

    return alpha, beta, gamma


def norm(x, y):
    return np.linalg.norm((x, y), axis=0)


def solve_quadratic_equation(a, b, c):
    d = np.sqrt(b**2 - 4 * a * c)
    # left_root = (-b - d) / (2 * a)
    right_root = (-b + d) / (2 * a)
    return right_root
