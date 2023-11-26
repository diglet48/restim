import numpy as np


def create_pulse_envelope(n_samples):
    return 0.5 - np.cos(np.linspace(0, np.pi * 2, n_samples)) * 0.5


def create_pulse_envelope_half_circle(n_samples):
    return np.sin(np.linspace(0, np.pi, n_samples))


def create_pause(n_samples):
    return np.zeros(n_samples)