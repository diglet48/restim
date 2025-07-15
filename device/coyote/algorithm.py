"""
New Coyote 3.0 E-Stim Algorithm - Direct Control Model

This algorithm is a from-scratch redesign inspired by the Neostim architecture,
but tailored specifically for the DG-LAB Coyote 3.0's hardware constraints.

It abandons the previous audio-emulation approach in favor of direct parameter
control, aiming for a more faithful and responsive funscript experience.
"""

import logging
import time
import numpy as np
from collections import deque
from typing import List, Tuple, Deque

from stim_math.axis import AbstractMediaSync, AbstractAxis
from stim_math.threephase import ThreePhaseCenterCalibration
from stim_math.audio_gen.params import CoyoteAlgorithmParams, VolumeParams, SafetyParams
from stim_math.audio_gen.various import ThreePhasePosition
from device.coyote.device import CoyotePulse, CoyotePulses

logger = logging.getLogger('restim.coyote')

COYOTE_PULSES_PER_PACKET = 4
COYOTE_MIN_PULSE_DURATION = 5
COYOTE_MAX_PULSE_DURATION = 240


def compute_volume(media: AbstractMediaSync, volume_params: VolumeParams, t: float) -> float:
    """Calculate the overall volume multiplier from all volume sources."""
    if not media.is_playing():
        return 0.0

    master = np.clip(volume_params.master.last_value(), 0, 1)
    api = np.clip(volume_params.api.interpolate(t), 0, 1)
    inactivity = np.clip(volume_params.inactivity.last_value(), 0, 1)
    external = np.clip(volume_params.external.last_value(), 0, 1)

    if inactivity == 0:
        inactivity = 1.0

    volume = master * api * inactivity * external

    return volume



class ChannelState:
    """Holds the state for a single channel's pulse packet and timing."""
    def __init__(self):
        self.current_packet: Deque[CoyotePulse] = deque()
        self.time_in_packet_ms = 0.0
        self.total_packet_duration_ms = 0.0
        self.packet_start_time_s = 0.0
        self.packet_finish_time_s = 0.0

    def set_new_packet(self, t: float, packet: List[CoyotePulse], time_to_finish_s: float):
        """Updates the channel with a new packet and its timing information."""
        self.current_packet = deque(packet)
        self.packet_start_time_s = t
        self.packet_finish_time_s = self.packet_start_time_s + time_to_finish_s
        self.total_packet_duration_ms = sum(p.duration for p in packet)
        self.time_in_packet_ms = 0.0

    def advance_time(self, delta_time_ms: float):
        self.time_in_packet_ms += delta_time_ms

    def is_ready_for_next_packet(self) -> bool:
        """Returns True if the current packet has finished playing."""
        return self.get_remaining_time_ms() <= 0

    def get_remaining_time_ms(self) -> float:
        if self.total_packet_duration_ms == 0:
            return 0.0  # Ready for first packet
        return max(0.0, self.total_packet_duration_ms - self.time_in_packet_ms)


class WaveGenerator:
    """Generates a continuous, asymmetric triangle wave based on pulse frequency and rise time."""
    def __init__(self, pulse_frequency_axis: AbstractAxis, pulse_rise_time_axis: AbstractAxis,
                 pulse_rise_time_limits: Tuple[float, float]):
        self.pulse_frequency_axis = pulse_frequency_axis
        self.pulse_rise_time_axis = pulse_rise_time_axis
        self.pulse_rise_time_limits = pulse_rise_time_limits
        self.phase = 0.0
        self.rise_pct = 0.5  # Default to a symmetric wave

    def advance(self, t: float, delta_time_ms: float):
        pulse_freq_hz = self.pulse_frequency_axis.interpolate(t)
        if pulse_freq_hz <= 0:
            self.phase = 0.0
            return

        # Advance the phase based on the pulse frequency
        self.phase += (delta_time_ms / 1000.0) * pulse_freq_hz
        self.phase %= 1.0

        # Update the rise percentage based on the pulse_rise_time axis
        rise_time_val = self.pulse_rise_time_axis.interpolate(t)
        min_rise, max_rise = self.pulse_rise_time_limits
        rise_range = max_rise - min_rise

        # Normalize rise time to a 0-1 percentage for the wave shape
        normalized_rise = (rise_time_val - min_rise) / rise_range if rise_range > 0 else 0.5
        normalized_rise = np.clip(normalized_rise, 0.0, 1.0)

        # We don't want the rise/fall to be instantaneous, so map 0-1 to a safer range, e.g., 0.01 to 0.99
        self.rise_pct = 0.01 + normalized_rise * 0.98

    def get_value(self) -> float:
        """Returns the current wave value, from -1.0 to 1.0."""
        if self.rise_pct <= 0.0: return -1.0
        if self.rise_pct >= 1.0: return 1.0

        if self.phase < self.rise_pct:
            # Rising part of the wave
            return -1.0 + (self.phase / self.rise_pct) * 2.0
        else:
            # Falling part of the wave
            fall_phase = self.phase - self.rise_pct
            fall_duration_pct = 1.0 - self.rise_pct
            if fall_duration_pct <= 0: return -1.0
            return 1.0 - (fall_phase / fall_duration_pct) * 2.0


class ContinuousSignal:
    """Models the complete, time-aware signal for a single channel based on the 'wave' model."""
    def __init__(self, params: CoyoteAlgorithmParams, channel_params: 'CoyoteChannelParams',
                 carrier_freq_limits: Tuple[float, float], pulse_width_limits: Tuple[float, float],
                 pulse_rise_time_limits: Tuple[float, float]):
        self.params = params
        self.channel_params = channel_params
        self.pulse_rise_time_limits = pulse_rise_time_limits
        self.pulse_width_limits = pulse_width_limits
        self.wave = WaveGenerator(params.pulse_frequency, params.pulse_rise_time, pulse_rise_time_limits)
        self.last_pulse_time_s = 0.0
        self.start_time = None

    def get_pulse_at(self, t: float, base_intensity: float, pulse_index: int = 0) -> CoyotePulse:
        """
        Generate a pulse for this channel at time t.
        base_intensity should be in the range 0-100 (int or float), as per position/intensity logic.
        This method normalizes to [0,1] internally for all calculations.
        """
        delta_time_ms = (t - self.last_pulse_time_s) * 1000.0 if self.last_pulse_time_s > 0 else 0
        self.last_pulse_time_s = t
        self.wave.advance(t, delta_time_ms)

        if self.start_time is None:
            self.start_time = t

        # --- Get base parameters from axes ---
        carrier_freq = self.params.carrier_frequency.interpolate(t)
        pulse_width = self.params.pulse_width.interpolate(t)
        random_strength = self.params.pulse_interval_random.interpolate(t)

        # --- Calculate channel-specific frequency parameters ---
        min_freq = self.channel_params.minimum_frequency.get()
        max_freq = self.channel_params.maximum_frequency.get()
        midpoint_freq = (min_freq + max_freq) / 2.0
        max_deviation = (max_freq - min_freq) / 2.0

        # --- Build the wave that modulates the sensation frequency ---
        # 1. Normalize the raw carrier frequency (e.g., 500-1000Hz) to a 0-1 percentage
        min_carrier, max_carrier = self.pulse_width_limits
        carrier_range = max_carrier - min_carrier
        carrier_pct = (carrier_freq - min_carrier) / carrier_range if carrier_range > 0 else 0
        carrier_pct = np.clip(carrier_pct, 0.0, 1.0)

        # 2. Amplitude of the wave is controlled by this correct percentage
        amplitude = max_deviation * carrier_pct

        # 3. Get current position on the wave (-1 to 1)
        wave_value = self.wave.get_value()

        # 4. The final modulated frequency is the midpoint offset by the wave
        sensation_freq = midpoint_freq + (wave_value * amplitude)

        # --- Calculate Final Pulse Parameters ---
        # The final frequency is determined by the raw sensation frequency, scaled by the duty cycle (pulse_width)
        # and random jitter. This effective frequency is then clipped to the channel's limits.

        # 1. Calculate scaling factors
        min_pw, max_pw = self.pulse_width_limits
        pw_range = max_pw - min_pw
        norm_pulse_width = (pulse_width - min_pw) / pw_range if pw_range > 0 else 0.5
        norm_pulse_width = np.clip(norm_pulse_width, 0.0, 1.0)

        # Remap the normalized pulse width to a scaler that modulates frequency. A wider pulse (higher norm_pulse_width)
        # should result in a lower frequency (longer duration), so it needs a larger scaler.
        # We map [0,1] to [0.75, 1.25] for a +/- 25% modulation. This could be a user-configurable parameter.
        pulse_width_scaler = 0.75 + (norm_pulse_width * 0.5)

        random_multiplier = 1.0
        if random_strength > 0:
            random_pct = random_strength / 100.0
            random_jitter = (np.random.rand() - 0.5) * 2 * random_pct
            random_multiplier = 1.0 + random_jitter

        # 2. Calculate the effective frequency after scaling. A shorter pulse width (duty cycle) leads to a higher frequency.
        effective_freq = sensation_freq / (pulse_width_scaler * random_multiplier)

        # 3. Clip the effective frequency to the channel's configured min/max range.
        target_freq = np.clip(effective_freq, min_freq, max_freq)
        target_freq = max(0.1, target_freq)

        # 4. Calculate the duration from the target frequency, then clip it to the hardware's absolute limits.
        target_duration_ms = 1000.0 / target_freq
        final_duration = int(np.clip(target_duration_ms, COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION))

        # 5. Recalculate the final frequency from the actual final duration. This ensures perfect consistency
        # between the frequency and duration values, respecting hardware limits above all.
        final_freq = 1000.0 / final_duration if final_duration > 0 else 0

        effective_intensity = int(np.clip(base_intensity, 0, 100))
        pulse = CoyotePulse(
            frequency=int(final_freq),
            intensity=effective_intensity,
            duration=final_duration
        )
        return pulse


class CoyoteAlgorithm:
    """New Coyote pulse generation algorithm using a continuous signal model."""
    def __init__(self, media: AbstractMediaSync, params: CoyoteAlgorithmParams, safety_limits: SafetyParams,
                 carrier_freq_limits: Tuple[float, float], pulse_width_limits: Tuple[float, float],
                 pulse_rise_time_limits: Tuple[float, float]):
        self.media = media
        self.params = params
        self.calibration = ThreePhaseCenterCalibration(params.calibrate)
        self.position = ThreePhasePosition(params.position, params.transform)

        self.signal_a = ContinuousSignal(params, params.channel_a, carrier_freq_limits, pulse_width_limits,
                                         pulse_rise_time_limits)
        self.signal_b = ContinuousSignal(params, params.channel_b, carrier_freq_limits, pulse_width_limits,
                                         pulse_rise_time_limits)

        self.channel_a = ChannelState()
        self.channel_b = ChannelState()

        self.start_time = None
        self.last_update_time_s = 0.0
        self.next_update_time = 0.0

    def _get_positional_intensities(self, t: float, volume: float) -> Tuple[int, int]:
        """Barycentric phase diagram mapping: (beta, alpha) with left=+1, right=-1, neutral=+1 (top)."""
        alpha, beta = self.position.get_position(t)

        # Barycentric weights for triangle corners
        w_L = max(0.0, (beta + 1) / 2)
        w_R = max(0.0, (1 - beta) / 2)
        w_N = max(0.0, alpha)
        sum_w = w_L + w_R + w_N
        if sum_w > 0:
            w_L /= sum_w
            w_R /= sum_w
            w_N /= sum_w
        else:
            w_L = w_R = w_N = 0.0

        # Calibration scaling
        center_val = self.params.calibrate.center.last_value()
        center_calib = ThreePhaseCenterCalibration(center_val)
        scale = center_calib.get_scale(alpha, beta)

        # Channel mapping: A = left+neutral, B = right+neutral
        intensity_a = (w_L + w_N) * volume * scale
        intensity_b = (w_R + w_N) * volume * scale

        result_a = int(np.clip(intensity_a * 100, 0, 100))
        result_b = int(np.clip(intensity_b * 100, 0, 100))

        return result_a, result_b


    def generate_packet(self, current_time: float) -> CoyotePulses:
        """
        Generate one packet of pulses for both channels.

        This function is called periodically to generate a new set of pulses for both channels (A and B).
        It advances the channel state, checks if a new packet is needed, and then generates and logs pulse details.
        """
        # --- Timing Management ---
        margin = 0.8 # Request next packet after 80% of this one has played

        # Initialize last update time if first call
        if self.last_update_time_s == 0.0:
            self.last_update_time_s = current_time

        # Calculate elapsed time since last packet
        delta_time_s = current_time - self.last_update_time_s
        self.last_update_time_s = current_time

        # --- Channel State Advancement ---
        # Advance the state of each channel by the elapsed time (in ms)
        self.channel_a.advance_time(delta_time_s * 1000.0)
        self.channel_b.advance_time(delta_time_s * 1000.0)

        # --- Packet Generation Condition ---
        # Generate a new packet only if either channel is ready
        if self.channel_a.is_ready_for_next_packet() or self.channel_b.is_ready_for_next_packet():
            t = current_time
            use_media_time = False
            media_type = 'media'

            if hasattr(self.media, 'media_type'):
                media_type = str(getattr(self.media, 'media_type'))
            elif self.media.__class__.__name__.lower().startswith('internal'):
                media_type = 'internal'
            elif 'vlc' in self.media.__class__.__name__.lower():
                media_type = 'vlc'
            elif 'mpv' in self.media.__class__.__name__.lower():
                media_type = 'mpv'
            else:
                media_type = self.media.__class__.__name__.lower()
            comment = media_type

            try:
                if hasattr(self.media, 'is_playing') and self.media.is_playing() and hasattr(self.media, 'map_timestamp') and media_type != 'internal':
                    rel_time_s = self.media.map_timestamp(time.time())
                    if rel_time_s is not None and rel_time_s >= 0:
                        use_media_time = True
            except Exception:
                pass

            if use_media_time:
                # rel_time_s is set from map_timestamp
                hours = int(rel_time_s // 3600)
                minutes = int((rel_time_s % 3600) // 60)
                seconds = int(rel_time_s % 60)
                millis = int((rel_time_s - int(rel_time_s)) * 1000)
            elif media_type == 'internal':
                now = time.localtime()
                hours = now.tm_hour
                minutes = now.tm_min
                seconds = now.tm_sec
                millis = int((time.time() - int(time.time())) * 1000)
            else:
                if self.start_time is None:
                    self.start_time = t
                rel_time_s = t - self.start_time
                hours = int(rel_time_s // 3600)
                minutes = int((rel_time_s % 3600) // 60)
                seconds = int(rel_time_s % 60)
                millis = int((rel_time_s - int(rel_time_s)) * 1000)

            alpha, beta = self.position.get_position(t)
            volume = compute_volume(self.media, self.params.volume, t)
            intensity_a, intensity_b = self._get_positional_intensities(t, volume)

            # --- Channel A Pulse Generation ---
            pulses_a: List[CoyotePulse] = []
            time_advanced_in_packet_ms = 0.0
            for i in range(COYOTE_PULSES_PER_PACKET):
                t_pulse = t + (time_advanced_in_packet_ms / 1000.0)
                pulse = self.signal_a.get_pulse_at(t_pulse, intensity_a, i+1)
                pulses_a.append(pulse)
                time_advanced_in_packet_ms += pulse.duration
            total_a = sum(p.duration for p in pulses_a)

            # --- Channel B Pulse Generation ---
            pulses_b: List[CoyotePulse] = []
            time_advanced_in_packet_ms = 0.0
            for i in range(COYOTE_PULSES_PER_PACKET):
                t_pulse = t + (time_advanced_in_packet_ms / 1000.0)
                pulse = self.signal_b.get_pulse_at(t_pulse, intensity_b, i+1)
                pulses_b.append(pulse)
                time_advanced_in_packet_ms += pulse.duration
            total_b = sum(p.duration for p in pulses_b)

            # Build the entire debug log as a single string 
            log_lines = []
            log_lines.append("")
            log_lines.append(f"=== Generating packet at {hours:02}:{minutes:02}:{seconds:02}:{millis:03} === [{comment}]")
            log_lines.append(f"  Position: alpha={alpha:.2f}, beta={beta:.2f}, volume={volume:.2f}")
            log_lines.append(f"Channel A ({total_a} ms):")
            for i, pulse in enumerate(pulses_a):
                log_lines.append(f"  Pulse {i+1}: duration={pulse.duration} ms, freq={pulse.frequency} Hz, intensity={pulse.intensity}%")
            log_lines.append("")
            log_lines.append(f"Channel B ({total_b} ms):")
            for i, pulse in enumerate(pulses_b):
                log_lines.append(f"  Pulse {i+1}: duration={pulse.duration} ms, freq={pulse.frequency} Hz, intensity={pulse.intensity}%")
            logger.debug("\n".join(log_lines))

            # --- Schedule next update based on shortest channel duration ---
            # Use a margin to ensure timely updates before packet end
            time_a = sum(p.duration / 1000.0 for p in pulses_a)
            time_b = sum(p.duration / 1000.0 for p in pulses_b)
   
            self.next_update_time = t + min(time_a, time_b) * margin

            return CoyotePulses(pulses_a, pulses_b)
        else:
            # Not ready: schedule next update based on remaining time
            next_update_in_ms = min(self.channel_a.get_remaining_time_ms(), self.channel_b.get_remaining_time_ms())
            self.next_update_time = current_time + (next_update_in_ms / 1000.0) * margin

            return CoyotePulses([], [])


    def get_next_update_time(self) -> float:
        return self.next_update_time

    def get_envelope_data(self) -> Tuple[np.ndarray, float]:
        return np.array([]), 0.0
