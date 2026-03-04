"""
Auto-derivation of pulse parameters from funscript motion data.

Inspired by edger477's funscript-tools processor:
https://github.com/edger477/funscript-tools

When a user loads a 1D or 2D funscript but has no explicit pulse_frequency,
pulse_width, carrier_frequency, or pulse_rise_time funscripts, these parameters
can be automatically derived from the motion data (speed + alpha + inverted position).

The derivation approach:
- Speed signal: rolling-window average of position changes, normalized 0-1
- Pulse frequency:  combine(speed, alpha, ratio) → map to [freq_min, freq_max]
- Carrier frequency: map(speed, carrier_min, carrier_max)
- Pulse width:       combine(speed, clamp(invert(main), pw_min, pw_max), ratio)
- Pulse rise time:   map(invert(speed), rise_min, rise_max)
"""

import numpy as np
import logging

logger = logging.getLogger('restim.pulse_auto_derive')


def compute_speed(timestamps, positions, window_seconds=5.0, interpolation_interval=0.1):
    """
    Compute a speed signal from a funscript (timestamps, positions).

    Uses a rolling window to compute average position-change-per-second,
    then normalizes to 0-1 range.

    Args:
        timestamps: array of timestamps in seconds
        positions: array of position values 0-1
        window_seconds: size of the rolling window in seconds
        interpolation_interval: interval for resampling in seconds

    Returns:
        (speed_timestamps, speed_values) both numpy arrays, speed_values in [0, 1]
    """
    if len(timestamps) < 2:
        return np.array([0.0]), np.array([0.0])

    timestamps = np.asarray(timestamps, dtype=float)
    positions = np.asarray(positions, dtype=float)

    # Resample to uniform intervals
    t_start = timestamps[0]
    t_end = timestamps[-1]
    uniform_t = np.arange(t_start, t_end, interpolation_interval)
    if len(uniform_t) < 2:
        return timestamps, np.zeros_like(positions)

    uniform_p = np.interp(uniform_t, timestamps, positions)

    # Compute instantaneous speed (position change per second)
    dt = np.diff(uniform_t)
    dp = np.abs(np.diff(uniform_p))
    inst_speed = dp / np.maximum(dt, 1e-9)

    # Rolling window average
    window_samples = max(1, int(window_seconds / interpolation_interval))
    kernel = np.ones(window_samples) / window_samples
    smoothed_speed = np.convolve(inst_speed, kernel, mode='same')

    # Prepend a zero so length matches uniform_t
    speed_values = np.zeros(len(uniform_t))
    speed_values[1:] = smoothed_speed
    # Shift by half window to center the speed on the right time
    shift = window_samples // 2
    if shift > 0 and shift < len(speed_values):
        speed_values = np.roll(speed_values, -shift)
        speed_values[-shift:] = 0

    # Normalize to 0-1
    max_speed = np.max(speed_values)
    if max_speed > 0:
        speed_values = speed_values / max_speed

    return uniform_t, speed_values


def combine(left_t, left_y, right_t, right_y, ratio):
    """
    Combine two signals using weighted average (edger477 formula).

    y = (y_left * (ratio - 1) + y_right) / ratio

    With ratio=2: 50% left + 50% right
    With ratio=3: 66.7% left + 33.3% right

    Returns:
        (timestamps, combined_values)
    """
    t = np.union1d(left_t, right_t)
    y_l = np.interp(t, left_t, left_y)
    y_r = np.interp(t, right_t, right_y)
    y = (y_l * (ratio - 1) + y_r) / ratio
    return t, y


def map_range(timestamps, values, new_min, new_max):
    """
    Linearly map values from their current range to [new_min, new_max].
    """
    current_min = np.min(values)
    current_max = np.max(values)
    if current_max == current_min:
        mapped = np.full_like(values, (new_min + new_max) / 2)
    else:
        mapped = (values - current_min) / (current_max - current_min) * (new_max - new_min) + new_min
    return timestamps, mapped


def invert(values):
    """Invert values: 1.0 - value"""
    return 1.0 - values


def clamp(values, min_val, max_val):
    """Clamp values to [min_val, max_val]"""
    return np.clip(values, min_val, max_val)


class PulseAutoDeriver:
    """
    Derives pulse parameters from motion data.

    Parameters (all configurable via the dialog):
        speed_window: rolling window for speed computation (seconds)
        pulse_freq_combine_ratio: combine ratio for speed+alpha → pulse frequency
        pulse_freq_min/max: output range for pulse frequency (Hz)
        carrier_freq_min/max: output range for carrier frequency (Hz)
        pulse_width_combine_ratio: combine ratio for speed+inverted_position → pulse width
        pulse_width_min/max: clamp range for the inverted position component (carrier cycles)
        pulse_rise_min/max: output range for pulse rise time (carrier cycles)
    """

    def __init__(self, params=None):
        from qt_ui import settings
        if params is None:
            params = {}

        self.enabled = params.get('enabled',
            settings.pulse_auto_derive_enabled.get())
        self.speed_window = params.get('speed_window',
            settings.pulse_auto_derive_speed_window.get())

        # Pulse frequency params
        self.pulse_freq_combine_ratio = params.get('pulse_freq_combine_ratio',
            settings.pulse_auto_derive_pulse_freq_combine_ratio.get())
        self.pulse_freq_min = params.get('pulse_freq_min',
            settings.pulse_auto_derive_pulse_freq_min.get())
        self.pulse_freq_max = params.get('pulse_freq_max',
            settings.pulse_auto_derive_pulse_freq_max.get())

        # Carrier frequency params
        self.carrier_freq_min = params.get('carrier_freq_min',
            settings.pulse_auto_derive_carrier_freq_min.get())
        self.carrier_freq_max = params.get('carrier_freq_max',
            settings.pulse_auto_derive_carrier_freq_max.get())

        # Pulse width params
        self.pulse_width_combine_ratio = params.get('pulse_width_combine_ratio',
            settings.pulse_auto_derive_pulse_width_combine_ratio.get())
        self.pulse_width_min = params.get('pulse_width_min',
            settings.pulse_auto_derive_pulse_width_min.get())
        self.pulse_width_max = params.get('pulse_width_max',
            settings.pulse_auto_derive_pulse_width_max.get())

        # Pulse rise time params
        self.pulse_rise_min = params.get('pulse_rise_min',
            settings.pulse_auto_derive_pulse_rise_min.get())
        self.pulse_rise_max = params.get('pulse_rise_max',
            settings.pulse_auto_derive_pulse_rise_max.get())

    def derive_all(self, main_timestamps, main_positions, alpha_timestamps=None, alpha_positions=None):
        """
        Derive all pulse parameters from the motion data.

        Args:
            main_timestamps: timestamps from the main 1D funscript
            main_positions: position values from the main 1D funscript (0-1)
            alpha_timestamps: timestamps from alpha channel (optional, uses main if None)
            alpha_positions: values from alpha channel (optional, uses main if None)

        Returns:
            dict with keys: 'pulse_frequency', 'carrier_frequency', 'pulse_width', 'pulse_rise_time'
            Each value is (timestamps, values) tuple in the output unit space.
        """
        main_t = np.asarray(main_timestamps, dtype=float)
        main_p = np.asarray(main_positions, dtype=float)

        # Compute speed signal
        speed_t, speed_y = compute_speed(main_t, main_p, window_seconds=self.speed_window)
        speed_inv = invert(speed_y)

        # Alpha (use alpha if provided, else use main positions)
        if alpha_timestamps is not None and alpha_positions is not None:
            alpha_t = np.asarray(alpha_timestamps, dtype=float)
            alpha_y = np.asarray(alpha_positions, dtype=float)
        else:
            alpha_t = main_t
            alpha_y = main_p

        # Inverted main position
        main_inv = invert(main_p)

        results = {}

        # 1. Pulse frequency: combine(speed, alpha, ratio) → map to [freq_min, freq_max]
        pf_t, pf_y = combine(speed_t, speed_y, alpha_t, alpha_y, self.pulse_freq_combine_ratio)
        pf_t, pf_y = map_range(pf_t, pf_y, self.pulse_freq_min, self.pulse_freq_max)
        results['pulse_frequency'] = (pf_t, pf_y)

        # 2. Carrier frequency: map(speed, carrier_min, carrier_max)
        cf_t, cf_y = map_range(speed_t.copy(), speed_y.copy(), self.carrier_freq_min, self.carrier_freq_max)
        results['carrier_frequency'] = (cf_t, cf_y)

        # 3. Pulse width: combine(speed, clamp(invert(main), pw_min_norm, pw_max_norm), ratio)
        #    The clamped inverted main is normalized 0-1, then the combined result is mapped to output range
        pw_base = clamp(main_inv, 0.0, 1.0)
        pw_t, pw_y = combine(speed_t, speed_y, main_t, pw_base, self.pulse_width_combine_ratio)
        pw_t, pw_y = map_range(pw_t, pw_y, self.pulse_width_min, self.pulse_width_max)
        results['pulse_width'] = (pw_t, pw_y)

        # 4. Pulse rise time: map(invert(speed), rise_min, rise_max)
        #    Slow → long rise time (soft), fast → short rise time (sharp)
        pr_t, pr_y = map_range(speed_t.copy(), speed_inv.copy(), self.pulse_rise_min, self.pulse_rise_max)
        results['pulse_rise_time'] = (pr_t, pr_y)

        logger.info(f'Auto-derived pulse parameters: '
                    f'pulse_freq=[{self.pulse_freq_min:.1f}-{self.pulse_freq_max:.1f}Hz], '
                    f'carrier=[{self.carrier_freq_min:.0f}-{self.carrier_freq_max:.0f}Hz], '
                    f'pulse_width=[{self.pulse_width_min:.1f}-{self.pulse_width_max:.1f}cycles], '
                    f'rise_time=[{self.pulse_rise_min:.1f}-{self.pulse_rise_max:.1f}cycles]')

        return results
