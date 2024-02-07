import matplotlib.pyplot as plt
import numpy as np


def show_continuous():
    duration = 0.01
    t = np.linspace(0, duration, 1000)

    theta = t * 2 * np.pi
    frequency = 900
    carrier_theta = theta * frequency

    # this waveform looks decent
    a = np.cos(carrier_theta)
    b = np.cos(carrier_theta + np.pi * 0.6)

    fig, ax = plt.subplots(figsize=(4, 1.5))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xlim((0, duration))
    fig.tight_layout()
    ax.plot(t, a)
    ax.plot(t, b)
    fig.show()
    fig.savefig('../resources/wizard/continuous.png', bbox_inches='tight')
    plt.show()


def show_pulse_based():
    duration = 0.01
    t = np.linspace(0, duration, 1000)

    theta = t * 2 * np.pi
    frequency = 900
    carrier_theta = theta * frequency

    # this waveform looks decent
    a = np.cos(carrier_theta)
    b = np.cos(carrier_theta + np.pi * 0.6)

    envelope_theta = 0.5 - np.cos(np.interp(t,
                                            [0, duration * .3, duration * 0.5, duration * 0.8, duration],
                                            [0, 2 * np.pi, 2 * np.pi, 4 * np.pi, 4 * np.pi])) * 0.5
    a *= envelope_theta
    b *= envelope_theta

    fig, ax = plt.subplots(figsize=(4, 1.5))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_xlim((0, duration))
    fig.tight_layout()
    ax.plot(t, a)
    ax.plot(t, b)
    fig.show()
    fig.savefig('../resources/wizard/pulse_based.png', bbox_inches='tight')
    plt.show()

show_continuous()
show_pulse_based()