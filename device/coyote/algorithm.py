"""
DG-LAB Coyote 3.0 E-Stim Algorithm Implementation

This algorithm controls a Coyote 3.0 dual-channel e-stim device using a symmetric ramp envelope
model that matches the pulse-based audio algorithm behavior while working within hardware constraints.

Hardware Specifications:
-----------------------
- Two independent channels (A and B)
- Each pulse: intensity (0-100%), duration (5-240ms)
- Protocol: 4 pulses per packet
- Device repeats last packet until new one arrives

<TODO: describe fully>

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
try:
    # Optional import; keeps algorithm functional in headless contexts
    from qt_ui import settings as ui_settings
except Exception:  # pragma: no cover - setting import is best-effort
    ui_settings = None

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


# --- Envelope Generators ---

def generate_ramp_envelope(attack: float, plateau: float, release: float, num_points: int) -> np.ndarray:
    """Generate a symmetric ramp (triangle/trapezoid) envelope 0→1→0.

    attack: seconds from 0→1
    plateau: seconds at level 1 between attack and release (may be 0)
    release: seconds from 1→0
    """
    total = attack + plateau + release
    if total <= 0 or num_points < 2:
        return np.zeros(num_points)

    a_pts = max(1, int(round(num_points * attack / total)))
    p_pts = max(0, int(round(num_points * plateau / total)))
    r_pts = num_points - a_pts - p_pts
    ascent = np.linspace(0, 1, a_pts, endpoint=False)
    plateau_arr = np.ones(p_pts)
    descent = np.linspace(1, 0, r_pts, endpoint=True)
    return np.concatenate([ascent, plateau_arr, descent])

def _normalize_axis(value: float, limits: Tuple[float, float]) -> float:
    """Normalize a raw axis value to a 0-100 scale based on its limits."""
    min_val, max_val = limits
    if max_val <= min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val) * 100.0


def _get_normalized_parameters(params: CoyoteAlgorithmParams, t: float, 
                              carrier_freq_limits: Tuple[float, float],
                              pulse_freq_limits: Tuple[float, float]) -> Tuple[float, float, float, float]:
    """Get parameter values: normalize frequency axes (Hz), return raw cycle values."""
    carrier_freq_raw = params.carrier_frequency.interpolate(t)
    pulse_freq_raw = params.pulse_frequency.interpolate(t)
    
    # Normalize frequency axes from Hz ranges
    carrier_freq = _normalize_axis(carrier_freq_raw, carrier_freq_limits)
    pulse_freq = _normalize_axis(pulse_freq_raw, pulse_freq_limits)
    
    # Return raw cycle values for pulse_width and pulse_rise_time
    pulse_width_cycles = params.pulse_width.interpolate(t)
    pulse_rise_time_cycles = params.pulse_rise_time.interpolate(t)
    
    return carrier_freq, pulse_freq, pulse_width_cycles, pulse_rise_time_cycles


class ContinuousSignal:
    """Models a single channel's pulse generation.

    Revised to keep the pulse frequency anchored to the funscript/UI
    `pulse_frequency` axis (with optional jitter), and to stop sweeping
    across the full min/max range. This preserves the intention of
    funscripts more faithfully while staying within hardware limits.
    """

    ENVELOPE_RESOLUTION = 200  # Number of points in envelope lookup table


    def __init__(self, params: CoyoteAlgorithmParams, channel_params: 'CoyoteChannelParams',
                 carrier_freq_limits: Tuple[float, float], pulse_freq_limits: Tuple[float, float],
                 pulse_width_limits: Tuple[float, float], pulse_rise_time_limits: Tuple[float, float]):
        self.params = params
        self.channel_params = channel_params
        self.carrier_freq_limits = carrier_freq_limits
        self.pulse_freq_limits = pulse_freq_limits
        self.pulse_width_limits = pulse_width_limits
        self.pulse_rise_time_limits = pulse_rise_time_limits
        
        # Timing state
        self._last_pulse_time = 0.0
        self._start_time = None
        self.modulation_phase = 0.0
        
        # Envelope cache
        self._envelope_lookup_table = None
        self._cached_envelope_params = None
        self._envelope_period = 0.0

    def _calculate_effective_frequency_limits(self) -> Tuple[float, float]:
        """Calculate effective frequency limits considering hardware constraints."""
        channel_min = self.channel_params.minimum_frequency.get()
        channel_max = self.channel_params.maximum_frequency.get()
        hardware_max = 1000.0 / COYOTE_MIN_PULSE_DURATION  # ~200 Hz
        hardware_min = 1000.0 / COYOTE_MAX_PULSE_DURATION  # ~4.17 Hz
        
        effective_min = max(channel_min, hardware_min)
        effective_max = min(channel_max, hardware_max)
        
        # Fallback to hardware limits if channel limits are invalid
        if effective_min >= effective_max:
            effective_min = hardware_min
            effective_max = hardware_max
            
        return effective_min, effective_max

    def _apply_frequency_randomization(self, base_frequency: float, randomization_strength: float,
                                     min_freq: float, max_freq: float) -> float:
        """Apply limited randomization to frequency."""
        if randomization_strength <= 0:
            return base_frequency
            
        # Limit randomization to 10% of the setting
        random_percentage = randomization_strength / 100.0 * 0.1
        random_factor = 1.0 + (np.random.rand() - 0.5) * 2 * random_percentage
        randomized_freq = base_frequency * random_factor
        
        return np.clip(randomized_freq, min_freq, max_freq)

    def get_pulse_at(self, current_time: float, base_intensity: float, pulse_index: int = 0) -> CoyotePulse:
        """Generate a pulse anchored to the requested pulse_frequency with optional jitter.

        - pulse_frequency: controls the base repetition rate (Hz)
        - pulse_interval_random: ±fractional jitter of the base duration
        - intensity: provided by caller (volume × position, smoothed elsewhere)
        """
        # Initialize timing state
        if self._start_time is None:
            self._start_time = current_time
        self._last_pulse_time = current_time

        # Effective channel limits → convert to duration window
        min_freq, max_freq = self._calculate_effective_frequency_limits()
        min_dur = max(COYOTE_MIN_PULSE_DURATION, int(round(1000.0 / max_freq)))
        max_dur = min(COYOTE_MAX_PULSE_DURATION, int(round(1000.0 / min_freq)))

        # Base frequency from UI/funscript axis, clamped by channel limits
        requested_freq = float(self.params.pulse_frequency.interpolate(current_time))
        requested_freq = float(np.clip(requested_freq, min_freq, max_freq))
        base_duration = 1000.0 / requested_freq if requested_freq > 0 else max_dur

        # Optional jitter around base duration
        jitter = float(self.params.pulse_interval_random.interpolate(current_time))
        # Treat jitter as a 0..1 fraction; clamp to ±50% to avoid pathological spans
        jitter = float(np.clip(jitter, 0.0, 0.5))
        jitter_factor = 1.0 + (np.random.rand() * 2.0 - 1.0) * jitter
        pulse_duration = int(round(base_duration * jitter_factor))

        # Clamp to channel-specific duration window and hardware bounds
        pulse_duration = int(np.clip(pulse_duration, min_dur, max_dur))

        final_frequency = int(max(1, round(1000.0 / pulse_duration)))

        # Intensity is supplied by the caller (already smoothed). Do not modulate here.
        final_intensity = int(np.clip(base_intensity, 0, 100))

        # Debug: trace pulse generation values (do not remove)
        try:
            print(
                f"[DEBUG] COYOTE get_pulse_at: t={current_time:.3f} idx={pulse_index} "
                f"req_freq={requested_freq:.2f}Hz limits=({min_freq:.1f},{max_freq:.1f})Hz "
                f"dur_limits=({min_dur},{max_dur})ms base_dur={base_duration:.1f}ms jitter={jitter:.2f} "
                f"final_dur={pulse_duration}ms final_freq={final_frequency}Hz intensity={final_intensity}%"
            )
        except Exception:
            pass

        return CoyotePulse(
            duration=pulse_duration,
            intensity=final_intensity,
            frequency=final_frequency,
        )




class CoyoteAlgorithm:
    """Coyote 3.0 pulse generation algorithm with symmetric ramp envelope modulation.
    
    Coordinates dual-channel pulse generation using ContinuousSignal instances.
    Handles packet timing, positional intensity distribution, and envelope preview.
    """
    def __init__(self, media: AbstractMediaSync, params: CoyoteAlgorithmParams, safety_limits: SafetyParams,
                 carrier_freq_limits: Tuple[float, float], pulse_freq_limits: Tuple[float, float],
                 pulse_width_limits: Tuple[float, float], pulse_rise_time_limits: Tuple[float, float]):
        self.media = media
        self.params = params
        self.calibration = ThreePhaseCenterCalibration(params.calibrate)
        self.position = ThreePhasePosition(params.position, params.transform)

        self.signal_a = ContinuousSignal(params, params.channel_a, carrier_freq_limits, pulse_freq_limits,
                                         pulse_width_limits, pulse_rise_time_limits)
        self.signal_b = ContinuousSignal(params, params.channel_b, carrier_freq_limits, pulse_freq_limits,
                                         pulse_width_limits, pulse_rise_time_limits)

        self.channel_a = ChannelState()
        self.channel_b = ChannelState()

        self.start_time = None
        self.last_update_time_s = 0.0
        self.next_update_time = 0.0

        # UI Preview Cache
        self._cached_envelope = np.full(200, 0.5)  # Default to a flat line
        self._cached_envelope_period = 0.0

        # Minimal per-channel intensity smoothing state
        self._last_intensity_a = None  # type: float | None
        self._last_intensity_b = None  # type: float | None
        self._last_intensity_time_a = None  # type: float | None
        self._last_intensity_time_b = None  # type: float | None

        # Global per-pulse cap (percentage points). Read from settings if available.
        self._max_change_per_pulse = 3.0
        try:
            if ui_settings is not None:
                self._max_change_per_pulse = float(ui_settings.coyote_max_intensity_change_per_pulse.get())
        except Exception:
            pass

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
        intensity_a = int((w_L + w_N) * volume * scale * 100.0)
        intensity_b = int((w_R + w_N) * volume * scale * 100.0)

        return intensity_a, intensity_b

    def _generate_channel_pulses(self, t: float, signal: 'ContinuousSignal', 
                                channel_name: str) -> Tuple[List[CoyotePulse], float]:
        """Generate pulses for a single channel, eliminating code duplication."""
        pulses: List[CoyotePulse] = []
        time_advanced_in_packet_ms = 0.0
        
        for i in range(COYOTE_PULSES_PER_PACKET):
            t_pulse = t + (time_advanced_in_packet_ms / 1000.0)
            volume = compute_volume(self.media, self.params.volume, t_pulse)
            intensity_a, intensity_b = self._get_positional_intensities(t_pulse, volume)
            
            # Select appropriate intensity based on channel
            target_intensity = float(intensity_a if channel_name == 'A' else intensity_b)

            # Convert pulse_rise_time (carrier cycles) to a time constant (seconds)
            carrier_hz = float(self.params.carrier_frequency.interpolate(t_pulse))
            rise_cycles = float(self.params.pulse_rise_time.interpolate(t_pulse))
            tau_s = 0.0 if carrier_hz <= 0 else (rise_cycles / carrier_hz)

            # Minimal EMA smoothing of intensity (no extra magic numbers)
            if channel_name == 'A':
                last_y = self._last_intensity_a
                last_t = self._last_intensity_time_a
                if last_y is None or tau_s <= 0 or last_t is None:
                    y = target_intensity
                else:
                    dt = max(0.0, t_pulse - last_t)
                    # Slew limit: base on tau, also cap by global per-pulse limit
                    allowed = (dt / tau_s) * 100.0
                    if self._max_change_per_pulse > 0:
                        allowed = min(allowed, self._max_change_per_pulse)
                    delta = np.clip(target_intensity - last_y, -allowed, allowed)
                    y = last_y + delta
                self._last_intensity_a = y
                self._last_intensity_time_a = t_pulse
            else:
                last_y = self._last_intensity_b
                last_t = self._last_intensity_time_b
                if last_y is None or tau_s <= 0 or last_t is None:
                    y = target_intensity
                else:
                    dt = max(0.0, t_pulse - last_t)
                    allowed = (dt / tau_s) * 100.0
                    if self._max_change_per_pulse > 0:
                        allowed = min(allowed, self._max_change_per_pulse)
                    delta = np.clip(target_intensity - last_y, -allowed, allowed)
                    y = last_y + delta
                self._last_intensity_b = y
                self._last_intensity_time_b = t_pulse

            intensity = int(np.clip(round(y), 0, 100))
            
            pulse = signal.get_pulse_at(t_pulse, intensity, i + 1)
            pulses.append(pulse)
            time_advanced_in_packet_ms += pulse.duration
            
        total_duration = sum(p.duration for p in pulses)
        return pulses, total_duration

    def _get_media_type(self) -> str:
        """Determine the media type for logging purposes."""
        if hasattr(self.media, 'media_type'):
            return str(getattr(self.media, 'media_type'))
        
        class_name = self.media.__class__.__name__.lower()
        if class_name.startswith('internal'):
            return 'internal'
        elif 'vlc' in class_name:
            return 'vlc'
        elif 'mpv' in class_name:
            return 'mpv'
        else:
            return class_name

    def _get_display_time(self, current_time: float) -> Tuple[int, int, int, int]:
        """Get formatted time for debug logging."""
        media_type = self._get_media_type()
        
        # Try to use media timestamp if available
        if (media_type != 'internal' and 
            hasattr(self.media, 'is_playing') and self.media.is_playing() and 
            hasattr(self.media, 'map_timestamp')):
            try:
                rel_time_s = self.media.map_timestamp(time.time())
                if rel_time_s is not None and rel_time_s >= 0:
                    return self._seconds_to_time_components(rel_time_s)
            except Exception:
                pass
        
        # Use local time for internal media
        if media_type == 'internal':
            now = time.localtime()
            millis = int((time.time() - int(time.time())) * 1000)
            return now.tm_hour, now.tm_min, now.tm_sec, millis
        
        # Use relative time from start
        if self.start_time is None:
            self.start_time = current_time
        rel_time_s = current_time - self.start_time
        return self._seconds_to_time_components(rel_time_s)

    def _seconds_to_time_components(self, seconds: float) -> Tuple[int, int, int, int]:
        """Convert seconds to (hours, minutes, seconds, milliseconds)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return hours, minutes, secs, millis

    def _advance_channel_states(self, current_time: float, delta_time_ms: float) -> None:
        """Advance channel timing and modulation phase for the next packet."""
        self.channel_a.advance_time(delta_time_ms)
        self.channel_b.advance_time(delta_time_ms)

        # Get normalized modulation speed
        # We use signal_a's limits, assuming they are the same for both channels.
        _, mod_speed_norm, _, _ = _get_normalized_parameters(
            self.params, current_time, self.signal_a.carrier_freq_limits, self.signal_a.pulse_freq_limits)

        # Calculate phase change based on elapsed time and modulation speed
        # This logic is now centralized here from its previous location in get_pulse_at.
        delta_time_s = delta_time_ms / 1000.0
        phase_change = (delta_time_s * mod_speed_norm / 10.0) * 2 * np.pi  # Simplified from / 50.0 * 5.0

        # Apply the same phase change to both signals to keep them in sync
        self.signal_a.modulation_phase = (self.signal_a.modulation_phase + phase_change) % (2 * np.pi)
        self.signal_b.modulation_phase = (self.signal_b.modulation_phase + phase_change) % (2 * np.pi)

    def _is_packet_generation_needed(self) -> bool:
        """Check if either channel needs a new packet."""
        return (self.channel_a.is_ready_for_next_packet() or 
                self.channel_b.is_ready_for_next_packet())

    def _schedule_next_update(self, current_time: float, packet_duration_a: float, 
                             packet_duration_b: float, margin: float = 0.8) -> None:
        """Schedule the next update time based on packet durations."""
        min_duration = min(packet_duration_a, packet_duration_b)
        self.next_update_time = current_time + min_duration * margin

    def _log_packet_debug(self, current_time: float, alpha: float, beta: float, 
                         pulses_a: List[CoyotePulse], pulses_b: List[CoyotePulse],
                         total_duration_a: float, total_duration_b: float) -> None:
        """Log debug information for generated packet."""
        hours, minutes, seconds, millis = self._get_display_time(current_time)
        media_type = self._get_media_type()
        
        # Calculate volume for logging (using first pulse time)
        volume = compute_volume(self.media, self.params.volume, current_time)
        
        log_lines = [
            "",
            f"=== Generating packet at {hours:02}:{minutes:02}:{seconds:02}:{millis:03} === [{media_type}]",
            f"  Position: alpha={alpha:.2f}, beta={beta:.2f}, volume={volume:.2f}",
            f"Channel A ({total_duration_a:.0f} ms):"
        ]
        
        for i, pulse in enumerate(pulses_a):
            log_lines.append(f"  Pulse {i+1}: duration={pulse.duration} ms, freq={pulse.frequency} Hz, intensity={pulse.intensity}%")
        
        log_lines.extend([
            "",
            f"Channel B ({total_duration_b:.0f} ms):"
        ])
        
        for i, pulse in enumerate(pulses_b):
            log_lines.append(f"  Pulse {i+1}: duration={pulse.duration} ms, freq={pulse.frequency} Hz, intensity={pulse.intensity}%")
        
        logger.debug("\n".join(log_lines))

    def _update_envelope_preview(self, t: float):
        """Generate and cache a simple flat envelope synced to pulse_frequency.

        The revised runtime no longer modulates frequency by a sine wave, so the
        preview reflects a steady state: flat line with period = 1/pulse_frequency.
        """
        num_points = 200
        freq = float(self.params.pulse_frequency.interpolate(t))
        self._cached_envelope_period = 1.0 / freq if freq > 0 else 0.0
        self._cached_envelope = np.full(num_points, 0.5)

    def generate_packet(self, current_time: float) -> CoyotePulses:
        """Generate one packet of pulses for both channels."""
        PACKET_MARGIN = 0.8  # Request next packet after 80% of current one has played
        
        # Initialize timing on first call
        if self.last_update_time_s == 0.0:
            self.last_update_time_s = current_time

        # Advance channel states
        delta_time_ms = (current_time - self.last_update_time_s) * 1000.0
        self.last_update_time_s = current_time
        self._advance_channel_states(current_time, delta_time_ms)

        # Check if packet generation is needed
        if not self._is_packet_generation_needed():
            # Schedule next update based on remaining time
            remaining_time_ms = min(
                self.channel_a.get_remaining_time_ms(),
                self.channel_b.get_remaining_time_ms()
            )
            self.next_update_time = current_time + (remaining_time_ms / 1000.0) * PACKET_MARGIN
            return CoyotePulses([], [])

        # Update the UI preview cache from the current state
        self._update_envelope_preview(current_time)

        # Generate pulses for both channels
        alpha, beta = self.position.get_position(current_time)
        pulses_a, duration_a = self._generate_channel_pulses(current_time, self.signal_a, 'A')
        pulses_b, duration_b = self._generate_channel_pulses(current_time, self.signal_b, 'B')

        # Update channel states so readiness reflects packet progress
        try:
            self.channel_a.set_new_packet(current_time, pulses_a, duration_a / 1000.0)
            self.channel_b.set_new_packet(current_time, pulses_b, duration_b / 1000.0)
        except Exception:
            pass

        # Log debug information
        self._log_packet_debug(current_time, alpha, beta, pulses_a, pulses_b, duration_a, duration_b)

        # Schedule next update
        self._schedule_next_update(current_time, duration_a / 1000.0, duration_b / 1000.0, PACKET_MARGIN)

        return CoyotePulses(pulses_a, pulses_b)


    def get_next_update_time(self) -> float:
        return self.next_update_time

    def get_envelope_data(self) -> Tuple[np.ndarray, float]:
        """Return the current flat envelope and its period for UI visualization."""
        t = time.time()
        freq = float(self.params.pulse_frequency.interpolate(t))
        period = 1.0 / freq if freq > 0 else 0.0
        num_points = 200
        return np.full(num_points, 0.5), period
