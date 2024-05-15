import numpy as np


def create_pulse_envelope(n_samples):
    return 0.5 - np.cos(np.linspace(0, np.pi * 2, n_samples)) * 0.5


def create_pulse_envelope_half_circle(n_samples):
    return np.sin(np.linspace(0, np.pi, n_samples))


def create_pulse_with_ramp_time(n_samples, carrier_cycles, rise_time):
    a = 1 / carrier_cycles * rise_time
    b = 1 - a
    if a >= b:
        return create_pulse_envelope_half_circle(n_samples)
    theta = np.interp(np.linspace(0, 1, n_samples), [0, a, b, 1], [0, np.pi/2, np.pi/2, np.pi])
    return np.sin(theta)


def create_pause(n_samples):
    return np.zeros(n_samples)