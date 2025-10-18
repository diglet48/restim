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
from typing import List, Tuple, Deque, Optional

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
                 pulse_width_limits: Tuple[float, float], pulse_rise_time_limits: Tuple[float, float],
                 channel_name: str = ""):
        self.params = params
        self.channel_params = channel_params
        self.carrier_freq_limits = carrier_freq_limits
        self.pulse_freq_limits = pulse_freq_limits
        self.pulse_width_limits = pulse_width_limits
        self.pulse_rise_time_limits = pulse_rise_time_limits
        self.channel_name = channel_name
        
        # Timing state
        self._last_pulse_time = 0.0
        self._start_time = None
        self.modulation_phase = 0.0
        self._duration_residual_ms = 0.0  # fractional ms accumulator to reduce rounding jitter
        
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
        - pulse_width: controls zero-mean micro-texture depth (duration modulation)
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

        # Map global funscript pulse_frequency into the channel's preferred range
        # 1) Normalize funscript value using global pulse_freq_limits (kit limits)
        raw_pf = float(self.params.pulse_frequency.interpolate(current_time))
        pf_min, pf_max = self.pulse_freq_limits
        if pf_max <= pf_min:
            pf_norm = 0.0
        else:
            pf_norm = float(np.clip((raw_pf - pf_min) / (pf_max - pf_min), 0.0, 1.0))
        # 2) Map normalized value into channel-specific [min_freq, max_freq]
        mapped_freq = min_freq + pf_norm * (max_freq - min_freq)
        mapped_freq = float(np.clip(mapped_freq, min_freq, max_freq))
        base_duration = 1000.0 / mapped_freq if mapped_freq > 0 else max_dur

        # Optional jitter around base duration (from funscript)
        jitter = float(self.params.pulse_interval_random.interpolate(current_time))
        # Treat jitter as a 0..1 fraction; clamp to ±50% to avoid pathological spans
        jitter = float(np.clip(jitter, 0.0, 0.5))
        jitter_factor = 1.0 + (np.random.rand() * 2.0 - 1.0) * jitter

        # Micro-texture from pulse_width (depth) with phase advanced in _advance_channel_states
        # Normalize pulse_width cycles to 0..1 using limits
        width_cycles = float(self.params.pulse_width.interpolate(current_time))
        min_w, max_w = self.pulse_width_limits
        width_norm = 0.0 if max_w <= min_w else np.clip((width_cycles - min_w) / (max_w - min_w), 0.0, 1.0)

        # Floating headroom on each side of base (use float limits, clamp to >=0)
        min_dur_f = 1000.0 / max_freq
        max_dur_f = 1000.0 / min_freq
        amp_up_ms = max(0.0, max_dur_f - base_duration)  # can increase duration up to this much
        amp_dn_ms = max(0.0, base_duration - min_dur_f)  # can decrease duration up to this much

        TEXTURE_MAX_DEPTH_FRACTION = 0.5
        amp_up_ms *= TEXTURE_MAX_DEPTH_FRACTION * width_norm
        amp_dn_ms *= TEXTURE_MAX_DEPTH_FRACTION * width_norm

        # Zero-mean texture respecting asymmetric headroom
        s = np.sin(self.modulation_phase)
        if amp_up_ms > 1e-6 and amp_dn_ms > 1e-6:
            # Symmetric case: use sine with symmetric amplitude
            texture_amplitude_ms = min(amp_up_ms, amp_dn_ms)
            texture_ms = texture_amplitude_ms * s
            tex_mode = 'sym'
        elif amp_up_ms > 1e-6:
            # One-sided (can only go up). Use rectified sine and subtract DC (E|sin|=2/π)
            texture_amplitude_ms = amp_up_ms
            texture_ms = amp_up_ms * (abs(s) - 2.0/np.pi)
            tex_mode = 'up'
        elif amp_dn_ms > 1e-6:
            # One-sided (can only go down). Negative rectified sine with DC removed
            texture_amplitude_ms = amp_dn_ms
            texture_ms = -amp_dn_ms * (abs(s) - 2.0/np.pi)
            tex_mode = 'down'
        else:
            texture_amplitude_ms = 0.0
            texture_ms = 0.0
            tex_mode = 'none'

        desired_ms = base_duration * jitter_factor + texture_ms

        # Fractional-duration accumulation to reduce jagged 10↔11ms toggling
        accum = self._duration_residual_ms + desired_ms
        pulse_duration = int(np.floor(accum + 0.5))  # nearest int
        self._duration_residual_ms = accum - pulse_duration
        # Keep residual bounded for numerical stability
        if self._duration_residual_ms > 0.49:
            self._duration_residual_ms = 0.49
        elif self._duration_residual_ms < -0.49:
            self._duration_residual_ms = -0.49

        # Clamp to channel-specific duration window and hardware bounds
        clamped = False
        if pulse_duration < min_dur:
            pulse_duration = min_dur
            clamped = True
        elif pulse_duration > max_dur:
            pulse_duration = max_dur
            clamped = True
        # If clamped to bounds, do not let residual drift; rounding is only for integer fairness
        if clamped:
            self._duration_residual_ms = 0.0

        final_frequency = int(max(1, round(1000.0 / pulse_duration)))

        # Intensity is supplied by the caller (already smoothed). Do not modulate here.
        final_intensity = int(np.clip(base_intensity, 0, 100))

        # Debug: log pulse generation details
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"  [{self.channel_name}] pulse #{pulse_index}: "
                f"freq_raw={raw_pf:.1f} Hz, freq_norm={pf_norm:.2f}, freq_mapped={mapped_freq:.1f} Hz, "
                f"freq_limits=({min_freq:.1f}-{max_freq:.1f}) Hz | "
                f"base_dur={base_duration:.1f} ms, dur_limits=({min_dur}-{max_dur}) ms, width_norm={width_norm:.2f}, "
                f"jitter={jitter:.0%} | "
                f"texture_mode={tex_mode}, texture_up={amp_up_ms:.2f} ms, texture_dn={amp_dn_ms:.2f} ms, texture_used={texture_amplitude_ms:.2f} ms | "
                f"desired={desired_ms:.2f} ms, residual={self._duration_residual_ms:+.2f} ms | "
                f"result: dur={pulse_duration} ms, freq={final_frequency} Hz, intensity={final_intensity}%"
            )

        return CoyotePulse(
            duration=pulse_duration,
            intensity=final_intensity,
            frequency=final_frequency,
        )




class ChannelController:
    """Encapsulates per-channel queuing, smoothing, and packet assembly."""

    def __init__(self,
                 name: str,
                 media: AbstractMediaSync,
                 params: CoyoteAlgorithmParams,
                 signal: ContinuousSignal,
                 get_positional_intensities,
                 max_change_per_pulse: float,
                 queue_horizon_s: float = 0.75):
        self.name = name  # 'A' or 'B'
        self.media = media
        self.params = params
        self.signal = signal
        self.get_positional_intensities = get_positional_intensities
        self.max_change_per_pulse = max_change_per_pulse
        self.queue_horizon_s = queue_horizon_s

        self.queue: Deque[CoyotePulse] = deque()
        self.queue_end_time: float | None = None

        # Smoothing state
        self._last_intensity: float | None = None
        self._last_intensity_time: float | None = None
        
        # Fill summary for logging
        self._last_fill_summary = None

    def _generate_single_pulse(self, t_pulse: float, seq_index: int) -> CoyotePulse:
        volume = compute_volume(self.media, self.params.volume, t_pulse)
        ia, ib = self.get_positional_intensities(t_pulse, volume)
        target_intensity = float(ia if self.name == 'A' else ib)

        carrier_hz = float(self.params.carrier_frequency.interpolate(t_pulse))
        rise_cycles = float(self.params.pulse_rise_time.interpolate(t_pulse))
        tau_s = 0.0 if carrier_hz <= 0 else (rise_cycles / carrier_hz)

        last_y = self._last_intensity
        last_t = self._last_intensity_time
        if last_y is None or tau_s <= 0 or last_t is None:
            y = target_intensity
        else:
            dt = max(0.0, t_pulse - last_t)
            allowed = (dt / tau_s) * 100.0
            if self.max_change_per_pulse > 0:
                allowed = min(allowed, self.max_change_per_pulse)
            delta = np.clip(target_intensity - last_y, -allowed, allowed)
            y = last_y + delta

        self._last_intensity = y
        self._last_intensity_time = t_pulse

        intensity = int(np.clip(round(y), 0, 100))
        pulse = self.signal.get_pulse_at(t_pulse, intensity, seq_index)
        return pulse

    def fill_queue(self, now_s: float) -> None:
        # Compute end_time from current queue coverage relative to now
        coverage_s = sum(p.duration for p in self.queue) / 1000.0
        end_time = now_s + coverage_s
        horizon_end = now_s + self.queue_horizon_s
        
        seq_index = 0
        new_pulses = []
        while end_time < horizon_end or len(self.queue) < COYOTE_PULSES_PER_PACKET:
            pulse = self._generate_single_pulse(end_time, seq_index)
            self.queue.append(pulse)
            new_pulses.append(pulse)
            end_time += pulse.duration / 1000.0
            seq_index += 1

        self.queue_end_time = end_time
        
        # Log queue fill summary
        if logger.isEnabledFor(logging.DEBUG):
            if new_pulses:
                durations = [p.duration for p in new_pulses]
                frequencies = [p.frequency for p in new_pulses]
                total_ms = sum(durations)
                logger.debug(
                    f"  [{self.name}] Queue filled: "
                    f"added={len(new_pulses)}, "
                    f"dur_range={min(durations)}-{max(durations)} ms, "
                    f"freq_range={min(frequencies)}-{max(frequencies)} Hz, "
                    f"total_added={total_ms} ms | "
                    f"queue_size={len(self.queue)}, "
                    f"coverage={coverage_s * 1000:.0f} ms, "
                    f"horizon={self.queue_horizon_s * 1000:.0f} ms\n"
                )
                self._last_fill_summary = (
                    len(new_pulses),
                    min(durations),
                    max(durations),
                    min(frequencies),
                    max(frequencies)
                )
            else:
                logger.debug(
                    f"  [{self.name}] Queue status: "
                    f"queue_size={len(self.queue)}, "
                    f"coverage={coverage_s * 1000:.0f} ms, "
                    f"horizon={self.queue_horizon_s * 1000:.0f} ms (no refill needed)\n"
                )
                self._last_fill_summary = None
        else:
            self._last_fill_summary = None

    def pop_packet(self) -> List[CoyotePulse]:
        packet: List[CoyotePulse] = []
        while len(packet) < COYOTE_PULSES_PER_PACKET:
            if self.queue:
                packet.append(self.queue.popleft())
            else:
                packet.append(CoyotePulse(frequency=0, intensity=0, duration=COYOTE_MIN_PULSE_DURATION))
        return packet

    def has_minimum_pulses(self, n: int) -> bool:
        return len(self.queue) >= n

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
                                         pulse_width_limits, pulse_rise_time_limits, channel_name="A")
        self.signal_b = ContinuousSignal(params, params.channel_b, carrier_freq_limits, pulse_freq_limits,
                                         pulse_width_limits, pulse_rise_time_limits, channel_name="B")

        self.channel_a = ChannelState()
        self.channel_b = ChannelState()

        self.start_time = None
        self.last_update_time_s = 0.0
        self.next_update_time = 0.0

        # Global per-pulse cap (percentage points). Read from settings if available.
        self._max_change_per_pulse = 3.0
        try:
            if ui_settings is not None:
                self._max_change_per_pulse = float(ui_settings.coyote_max_intensity_change_per_pulse.get())
        except Exception:
            pass

        # Per-channel controllers (queues, smoothing, assembly)
        self.ctrl_a = ChannelController(
            'A', self.media, self.params, self.signal_a,
            get_positional_intensities=self._get_positional_intensities,
            max_change_per_pulse=self._max_change_per_pulse,
            queue_horizon_s=0.75,
        )
        self.ctrl_b = ChannelController(
            'B', self.media, self.params, self.signal_b,
            get_positional_intensities=self._get_positional_intensities,
            max_change_per_pulse=self._max_change_per_pulse,
            queue_horizon_s=0.75,
        )

        # UI Preview Cache
        self._cached_envelope = np.full(200, 0.5)  # Default to a flat line
        self._cached_envelope_period = 0.0
        # Smoothing state handled by ChannelController

    # Channel-specific pulse generation and queues moved to ChannelController

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

    # Per-channel pulse generation was refactored into ChannelController

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

        # Advance shared micro-texture phase using carrier axis as speed control (mapped to ~0.5..5 Hz)
        carrier_norm, _, _, _ = _get_normalized_parameters(
            self.params, current_time, self.signal_a.carrier_freq_limits, self.signal_a.pulse_freq_limits)
        TEXTURE_MIN_HZ = 0.5
        TEXTURE_MAX_HZ = 5.0
        texture_speed_hz = TEXTURE_MIN_HZ + (TEXTURE_MAX_HZ - TEXTURE_MIN_HZ) * (carrier_norm / 100.0)
        delta_time_s = delta_time_ms / 1000.0
        phase_change = (delta_time_s * texture_speed_hz) * 2 * np.pi
        # Keep both channels in sync for texture phase
        self.signal_a.modulation_phase = (self.signal_a.modulation_phase + phase_change) % (2 * np.pi)
        self.signal_b.modulation_phase = (self.signal_b.modulation_phase + phase_change) % (2 * np.pi)

    def _is_packet_generation_needed(self) -> bool:
        """Check if either channel needs a new packet.

        We also allow proactive generation if queues are running low, to avoid
        starving the device with repeats for too long.
        """
        low_queue = (not self.ctrl_a.has_minimum_pulses(COYOTE_PULSES_PER_PACKET) or
                     not self.ctrl_b.has_minimum_pulses(COYOTE_PULSES_PER_PACKET))
        ready = (self.channel_a.is_ready_for_next_packet() or
                 self.channel_b.is_ready_for_next_packet())
        return ready or low_queue

    def _schedule_next_update(self, current_time: float, packet_duration_a: float, 
                             packet_duration_b: float, margin: float = 0.8) -> float:
        """Schedule the next update time based on packet durations. Returns next update delta in ms."""
        min_duration = min(packet_duration_a, packet_duration_b)
        self.next_update_time = current_time + min_duration * margin
        return min_duration * margin * 1000

    def _log_packet_debug(self, current_time: float, alpha: float, beta: float, 
                         pulses_a: List[CoyotePulse], pulses_b: List[CoyotePulse],
                         total_duration_a: float, total_duration_b: float, next_update_ms: float, margin: float) -> None:
        """Log debug information for generated packet."""
        if not logger.isEnabledFor(logging.DEBUG):
            return
            
        hours, minutes, seconds, millis = self._get_display_time(current_time)
        media_type = self._get_media_type()
        volume = compute_volume(self.media, self.params.volume, current_time)
        
        # Get common intensity (they should all be the same within a channel)
        intensity_a = pulses_a[0].intensity if pulses_a else 0
        intensity_b = pulses_b[0].intensity if pulses_b else 0
        
        log_lines = [
            "=" * 72,
            f"Packet Generated @ {hours:02}:{minutes:02}:{seconds:02}.{millis:03} [{media_type}]",
            "=" * 72,
            f"Position: alpha={alpha:+.2f}, beta={beta:+.2f}, volume={volume:.0%}",
            "",
            f"Channel A: duration={total_duration_a:.0f} ms, intensity={intensity_a}%",
        ]
        
        for i, p in enumerate(pulses_a, 1):
            log_lines.append(f"  Pulse {i}: {p.duration} ms @ {p.frequency} Hz")
        
        log_lines.extend([
            "",
            f"Channel B: duration={total_duration_b:.0f} ms, intensity={intensity_b}%"
        ])
        
        for i, p in enumerate(pulses_b, 1):
            log_lines.append(f"  Pulse {i}: {p.duration} ms @ {p.frequency} Hz")
        
        log_lines.extend([
            "",
            f"Next update: {next_update_ms:.0f} ms (packet_dur_a={total_duration_a:.0f} ms, packet_dur_b={total_duration_b:.0f} ms, margin={margin:.0%})",
            "=" * 72,
            ""
        ])
        
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

    def generate_packet(self, current_time: float) -> Optional[CoyotePulses]:
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
            return None

        # Update the UI preview cache from the current state
        self._update_envelope_preview(current_time)

        # Ensure queues are filled ahead of time
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("=== Channel A: Filling Queue ===")
        self.ctrl_a.fill_queue(current_time)
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("=== Channel B: Filling Queue ===")
        self.ctrl_b.fill_queue(current_time)

        # Assemble packets by popping from queues (atomic update for A and B)
        alpha, beta = self.position.get_position(current_time)
        pulses_a = self.ctrl_a.pop_packet()
        pulses_b = self.ctrl_b.pop_packet()
        duration_a = sum(p.duration for p in pulses_a)
        duration_b = sum(p.duration for p in pulses_b)

        # Update channel states so readiness reflects packet progress
        try:
            self.channel_a.set_new_packet(current_time, pulses_a, duration_a / 1000.0)
            self.channel_b.set_new_packet(current_time, pulses_b, duration_b / 1000.0)
        except Exception:
            pass

        # Schedule next update and get the delta for logging
        next_update_ms = self._schedule_next_update(current_time, duration_a / 1000.0, duration_b / 1000.0, PACKET_MARGIN)
        
        # Log debug information
        self._log_packet_debug(current_time, alpha, beta, pulses_a, pulses_b, duration_a, duration_b, next_update_ms, PACKET_MARGIN)

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
