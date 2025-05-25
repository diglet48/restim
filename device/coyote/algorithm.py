"""
DG-LAB Coyote 3.0 E-Stim Algorithm Implementation

This algorithm controls a Coyote 3.0 dual-channel e-stim device by emulating the behavior
of the pulse-based audio algorithm (used for traditional audio e-stim) while working
within the constraints of the Coyote hardware protocol.

NOTE: This algorithm is designed specifically for the Coyote 3.0 device. 
Other versions are not supported.

The Coyote 3.0 is a dual-channel e-stim device with the following characteristics:
- Two independent channels (A and B)
- Each channel accepts pulses with:
  - Intensity (0-100%)
  - Duration (5-240ms)
  - The device plays these pulses sequentially
- Protocol accepts 4 pulses per packet
- Device repeats the last received packet until a new one is sent

Frequency Handling:
-----------------
Both carrier and pulse frequencies are user-configurable with ranges defined in 
funscript configuration and constrained by safety limits:

- Each frequency has its own user-defined range from funscript configurations
- Carrier frequency (typically 500-1000 Hz) affects pulse durations
- Pulse frequency (typically 0-100 Hz) controls pulse repetition rate

Their relationship:
- Higher carrier frequencies result in shorter pulse durations (inversely related)
- Carrier frequency also modulates the effective pulse frequency
- Channel-specific frequency limits determine valid pulse duration ranges
- All frequencies are normalized within ranges before being applied

This approach ensures all values stay within valid ranges and changes to either
frequency produce intuitive results that adapt to user settings.

Key Differences Between Audio E-Stim and Coyote:
------------------------------------------------
1. Protocol Constraints:
   - Audio: Continuous stream of audio samples (44.1kHz) with full waveform control
   - Coyote: Packets of exactly 4 pulses per channel with limited parameter control (intensity, duration)

2. Parameter Control:
   - Audio: Direct control over carrier frequency, pulse width, pulse shape, polarity, etc.
   - Coyote: Only control over intensity (0-100%) and duration (5-240ms per pulse)

3. Timing:
   - Audio: Microsecond-level precision with continuous buffer
   - Coyote: Packet-based with potential gaps between updates

Emulation Approach:
------------------
This algorithm bridges these differences by:

1. Buffer Abstraction:
   - Maintains a FIFO buffer of pulses that abstract away the packet-based nature
   - Similar to audio algorithm's sample buffer, but at a higher level

2. Parameter Mapping:
   - Maps pulse-based algorithm parameters to Coyote parameters:
     - Carrier and pulse frequencies → Duration (inversely related)
     - Alpha/Beta position → Channel intensity split
     - Pulse polarity → Inverted envelope value 
     - Envelope shape → Duration modulation

3. Timing Management:
   - Uses a predictive timing model to request new packets before the 
     current one completes, ensuring smooth playback

The result is an algorithm that behaves as similarly as possible to the 
pulse-based audio algorithm while working within the hardware constraints.
"""

import logging
import numpy as np
from collections import deque
from typing import List, Tuple, Dict, Deque
from stim_math.audio_gen.various import ThreePhasePosition
from stim_math.axis import AbstractMediaSync
from device.coyote.device import CoyotePulse, CoyotePulses
from stim_math.audio_gen.params import SafetyParams, CoyoteAlgorithmParams, VolumeParams
from stim_math.threephase import ThreePhaseCenterCalibration
from stim_math import limits
import time

logger = logging.getLogger('restim.coyote')

# Protocol constraints
COYOTE_PULSES_PER_PACKET = 4  # Coyote protocol requires exactly 4 pulses per packet
COYOTE_MIN_PULSE_DURATION = 5  # Minimum pulse duration in ms
COYOTE_MAX_PULSE_DURATION = 240  # Maximum pulse duration in ms

# ===== Channel State Tracking =====

class ChannelState:
    """
    Tracks the state of a single channel's pulse buffer.
    
    This class serves a similar purpose to the audio buffer in the pulse-based algorithm,
    but at a higher level of abstraction (pulses instead of audio samples). It maintains
    a FIFO queue of pulses that are consumed over time, abstracting away the 
    packet-based nature of the Coyote protocol.
    
    The buffer is continuously refilled as pulses are consumed, ensuring smooth playback
    and allowing for dynamic parameter changes during operation.
    """
    def __init__(self, 
                 pulse_buffer: deque, 
                 start_time: float, 
                 elapsed_duration_ms: float,

                 min_freq: float,  # Minimum frequency in Hz
                 max_freq: float,  # Maximum frequency in Hz
                 min_duration: int,  # Corresponds to max_freq
                 max_duration: int): # Corresponds to min_freq
        self.pulse_buffer = pulse_buffer
        self.start_time = start_time
        self.elapsed_duration_ms = elapsed_duration_ms

        self.min_freq = min_freq
        self.max_freq = max_freq
        self.min_duration = min_duration
        self.max_duration = max_duration
        
        # Track last parameters for detecting changes
        self.last_pulse_freq = 0.0
        self.last_pulse_width = 0.0
        self.last_pulse_rise_time = 0.0

        # Track current phase (0.0-1.0) within the envelope period for phase-locked pulse generation
        self.envelope_phase = 0.0  # Always in [0.0, 1.0)


    @property
    def is_empty(self) -> bool:
        """
        Check if this channel's pulse buffer is empty.
        
        Returns:
            bool: True if the buffer has no pulses, False otherwise
        """
        return len(self.pulse_buffer) == 0
    
    def advance_time(self, elapsed_time_ms: float) -> bool:
        """
        Advance this channel's state by consuming pulses based on elapsed time.
        
        This method is similar to how the pulse-based algorithm consumes samples
        from its audio buffer. Pulses whose duration has passed are removed from
        the buffer, and the elapsed time is adjusted accordingly.
        
        Args:
            elapsed_time_ms: Time elapsed since last update in milliseconds
            
        Returns:
            bool: True if the buffer needs more pulses, False otherwise
        """
        if self.is_empty:
            logger.debug("Channel buffer is empty when advancing time")
            return True
            
        self.elapsed_duration_ms += elapsed_time_ms
        
        # Consume pulses that have completed
        accumulated_duration = 0
        consumed_count = 0
        while self.pulse_buffer and accumulated_duration + self.pulse_buffer[0].duration <= self.elapsed_duration_ms:
            pulse = self.pulse_buffer.popleft()
            accumulated_duration += pulse.duration
            consumed_count += 1
            
        if consumed_count > 0:
            logger.debug(f"Consumed {consumed_count} pulses, total duration {accumulated_duration:.1f}ms")
            
        # Adjust elapsed time to account for consumed pulses
        self.elapsed_duration_ms -= accumulated_duration
        
        # Buffer needs refilling if it's getting low (less than 2 packets worth)
        buffer_low = len(self.pulse_buffer) < COYOTE_PULSES_PER_PACKET * 2
        if buffer_low:
            logger.debug(f"Buffer running low: {len(self.pulse_buffer)} pulses remaining")
        return buffer_low

# ===== Utility Functions =====

def frequency_to_duration(frequency: float) -> int:
    """
    Convert frequency to Coyote pulse duration using the device's specific mapping.
    
    This is a key function for emulating the pulse-based algorithm's frequency control.
    In the pulse-based algorithm, frequency directly controls the waveform.
    For Coyote, we must convert frequency to duration (they're inversely related).
    
    The Coyote uses a non-linear mapping for durations:
    - 5-100ms: Direct 1:1 mapping from period
    - 100-600ms: Compressed 5:1 mapping
    - 600-1000ms: Compressed 10:1 mapping
    
    Args:
        frequency: Input frequency in Hz
    Returns:
        Duration in milliseconds (5-240ms range)
    """
    # Frequency must be positive
    if frequency <= 0:
        logger.warning(f"Invalid frequency {frequency}Hz, using default")
        frequency = 10.0  # Default fallback
        
    period = 1000.0 / frequency  # Convert Hz to period in ms
    
    if 5.0 <= period <= 100.0:
        calculated = period
    elif 100.0 < period <= 600.0:
        calculated = (period - 100) / 5.0 + 100
    elif 600.0 < period <= 1000.0:
        calculated = (period - 600) / 10.0 + 200
    else:
        calculated = 10.0  # Default fallback
        
    result = int(np.clip(round(calculated), COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION))

    return result

def generate_discrete_envelope(num_pulses: int, attack: int, sustain: int, release: int) -> np.ndarray:
    """
    Generate a discrete ADSR/trapezoidal envelope array (values in [0, 1]) sampled at the pulse frequency.
    Args:
        num_pulses: Number of pulses in one envelope cycle
        attack: Number of pulses for attack (ramp up)
        sustain: Number of pulses for sustain (max value)
        release: Number of pulses for release (ramp down)
    Returns:
        Numpy array of length num_pulses, values in [0, 1]
    """
    envelope = np.zeros(num_pulses)
    # Attack
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack, endpoint=False)
    # Sustain
    if sustain > 0:
        envelope[attack:attack+sustain] = 1.0
    # Release
    if release > 0:
        envelope[attack+sustain:] = np.linspace(1, 0, num_pulses - (attack + sustain))
    return envelope

# Replace old generate_envelope with a new function that creates a discrete envelope for Coyote

def generate_envelope(
    t: float,
    pulse_freq: float,
    carrier_freq: float,
    num_points: int = 100,
    preview_pulses: int = 6
) -> Tuple[np.ndarray, float]:
    """
    Generate a high-resolution envelope for EnvelopeGraph, matching the audio-based UI.
    Args:
        t: Current time in seconds (for phase alignment)
        pulse_freq: Pulse frequency (Hz)
        carrier_freq: Carrier frequency (Hz)
        num_points: Number of points for the preview graph
        preview_pulses: Number of pulses to visualize in the preview window
    Returns:
        Tuple of (envelope array, period in seconds)
    """
    if num_points < 3:
        num_points = 3
    preview_duration = preview_pulses / pulse_freq if pulse_freq > 0 else 1.0
    envelope = np.zeros(num_points)
    for i in range(num_points):
        t_i = t + (i / (num_points - 1)) * preview_duration
        phase = 2 * np.pi * carrier_freq * t_i
        envelope[i] = np.abs(np.sin(phase))
    period = preview_duration
    return envelope, period


def compute_volume(media: AbstractMediaSync, volume_params: VolumeParams, t: float) -> float:
    """
    Calculate the overall volume multiplier from all volume sources.
    
    This function matches the volume calculation in the pulse-based algorithm,
    combining multiple volume sources into a single multiplier.
    
    Args:
        media: Media sync object to check playback status
        volume_params: Volume parameters
        t: Current time in seconds
    Returns:
        Volume multiplier (0-1)
    """
    if not media.is_playing():
        return 0
    
    master_vol = np.clip(volume_params.master.last_value(), 0, 1)
    api_vol = np.clip(volume_params.api.interpolate(t), 0, 1)
    inactivity_vol = np.clip(volume_params.inactivity.last_value(), 0, 1)
    external_vol = np.clip(volume_params.external.last_value(), 0, 1)

    if inactivity_vol == 0:
        logger.warning("Inactivity volume is 0, using 1")
        inactivity_vol = 1
    
    volume = master_vol * api_vol * inactivity_vol * external_vol
    
    return volume

class CoyoteAlgorithm:
    """
    Coyote pulse generation algorithm that emulates the pulse-based audio algorithm.
    
    This class maintains a buffer of pulses for each channel, dynamically generating
    new pulses as needed and packaging them into packets for the Coyote device.
    It closely follows the design pattern of the pulse-based algorithm while
    adapting to the constraints of the Coyote protocol.
    
    Frequency Handling:
    ------------------
    Both carrier and pulse frequencies are user-configurable parameters with their own
    ranges defined in the funscript configuration and constrained by safety limits:
    
    - Carrier frequency: Typically ranges from 500-1000 Hz, primarily affects pulse timing
      and spacing, but not directly their durations
    - Pulse frequency: Typically ranges from 0-100 Hz, controls pulse repetition rate
      and is the primary factor determining pulse durations
    
    Their relationship:
    - Pulse frequency directly controls the duration of pulses (higher freq = shorter durations)
    - Carrier frequency primarily modifies the effective pulse frequency for timing purposes
    - The specific channel frequency limits determine the valid range of pulse durations
    - All frequencies are normalized within their respective ranges before being applied
    
    This approach ensures:
    - All values stay within their valid ranges
    - Changes to either frequency produce intuitive and predictable results
    - The algorithm adapts to different user settings and funscript configurations
    
    Key similarities with pulse-based algorithm:
    - Uses a buffer abstraction (pulses instead of audio samples)
    - Dynamically generates pulses based on current parameters
    - Handles parameter interpolation over time
    - Supports per-pulse polarity and phase control
    - Maps position coordinates to output intensities
    
    Key adaptations for Coyote:
    - Works with packets of 4 pulses instead of continuous audio
    - Maps frequency to duration (inversely related)
    - Updates based on packet timing rather than sample count
    """
    def __init__(self, media: AbstractMediaSync, params: CoyoteAlgorithmParams, safety_limits: SafetyParams,
                 carrier_freq_limits=(0, 100), pulse_freq_limits=(0, 100)):
        """
        Initialize the Coyote algorithm.
        
        Args:
            media: Media synchronization object
            params: Algorithm parameters
            safety_limits: Safety constraints for parameters
            carrier_freq_limits: Tuple of (min, max) for carrier frequency range
            pulse_freq_limits: Tuple of (min, max) for pulse frequency range
        """
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self.position_params = ThreePhasePosition(params.position, params.transform)
        self.seq = 0  # Sequence counter (for phase increment)
        self.next_update_time = 0  # When to request next packet
        self.last_pulses = None  # Last generated packet
        self.start_time = 0  # Reference time for relative logging
        
        # Get carrier frequency range from parameters and kit limits
        carrier_min, carrier_max = carrier_freq_limits
        self.min_carrier_freq = carrier_min
        self.max_carrier_freq = carrier_max
        
        # Apply safety limits as a final constraint
        # self.min_carrier_freq = max(carrier_min, safety_limits.minimum_carrier_frequency)
        # self.max_carrier_freq = min(carrier_max, safety_limits.maximum_carrier_frequency)
        self.carrier_freq_range = self.max_carrier_freq - self.min_carrier_freq
        
        # Get pulse frequency range from kit limits
        self.min_pulse_freq, self.max_pulse_freq = pulse_freq_limits
        self.pulse_freq_range = self.max_pulse_freq - self.min_pulse_freq
        
        # Initialize per-channel state
        self.channel_states = {
            'A': None,  # Will be initialized on first packet generation
            'B': None   # Will be initialized on first packet generation
        }
        
        # Buffer size (number of pulses to generate ahead)
        self.buffer_size = COYOTE_PULSES_PER_PACKET * 4  # Buffer 4 packets worth of pulses
        
        logger.info("Initialized CoyoteAlgorithm")
        logger.info(f"Safety limits: {safety_limits.minimum_carrier_frequency}-{safety_limits.maximum_carrier_frequency}Hz")
        logger.info(f"Carrier frequency range: {self.min_carrier_freq}-{self.max_carrier_freq}Hz")
        logger.info(f"Pulse frequency range: {self.min_pulse_freq}-{self.max_pulse_freq}Hz")

        # Initialize shared envelope data (used by all channels)
        self.shared_envelope = np.array([])
        self.shared_envelope_period = 0.0
        self.last_shared_pulse_freq = 0.0
        self.last_shared_pulse_width = 0.0
        self.last_shared_pulse_rise_time = 0.0
        
        # Set start time for relative time logging
        self.start_time = np.float64(time.time())
    
    def compute_volume(self, t: float) -> float:
        """
        Calculate the current volume setting from all sources.
        
        Args:
            t: Current time in seconds
        Returns:
            Volume multiplier (0-1)
        """
        return compute_volume(self.media, self.params.volume, t)
    
    def _rel_time(self, t: float) -> float:
        """
        Convert absolute timestamp to relative time in milliseconds.
        
        Args:
            t: Absolute timestamp in seconds
        Returns:
            Relative time in milliseconds
        """
        return (t - self.start_time) * 1000.0
    
    def _compute_channel_intensity(self, 
                              channel_id: str, 
                              alpha: float, 
                              beta: float, 
                              volume: float) -> int:
        """
        Convert position coordinates to channel intensity.
        
        This method is similar to how the pulse-based algorithm maps position
        coordinates to channel intensities, but adapted for the Coyote's
        dual-channel architecture.
        
        Args:
            channel_id: 'A' or 'B' channel identifier
            alpha: +1 to -1 coordinate (top-bottom) where +1 is top, -1 is bottom
            beta: +1 to -1 coordinate (left-right) where +1 is left, -1 is right
            volume: 0 to 1 volume multiplier
        Returns:
            Integer intensity 0-100
        """
        # Vertices
        sqrt3 = np.sqrt(3)
        x, y = alpha, beta
        xN, yN = 1.0, 0.0
        xL, yL = -0.5, sqrt3 / 2
        xR, yR = -0.5, -sqrt3 / 2

        # Barycentric coordinates
        denom = (yL - yR) * (xN - xR) + (xR - xL) * (yN - yR)
        w_N = ((yL - yR) * (x - xR) + (xR - xL) * (y - yR)) / denom
        w_L = ((yR - yN) * (x - xR) + (xN - xR) * (y - yR)) / denom
        w_R = 1.0 - w_N - w_L

        # Clamp
        w_N = np.clip(w_N, 0, 1)
        w_L = np.clip(w_L, 0, 1)
        w_R = np.clip(w_R, 0, 1)

        if channel_id == 'A':
            intensity = w_L + w_N
        elif channel_id == 'B':
            intensity = w_R + w_N
        else:
            intensity = w_N

        # Clamp to [0, 1] after sum
        intensity = np.clip(intensity, 0, 1)

        # Apply volume and calibration scaling
        intensity *= volume
        center_calib = ThreePhaseCenterCalibration(self.params.calibrate.center.last_value())
        scale = center_calib.get_scale(alpha, beta)
        intensity *= scale

        # Convert to 0-100 range
        result = int(np.clip(intensity * 100, 0, 100))
        return result
    
    def _generate_single_pulse(self,
                           base_time: float,
                           pulse_index: int,
                           base_intensity: int,
                           envelope: np.ndarray,
                           envelope_period: float,
                           pulse_freq: float,
                           carrier_freq: float,
                           pulse_width: float,
                           pulse_rise_time: float,
                           min_duration: int,
                           max_duration: int,
                           pulse_interval_random: float,
                           carrier_norm: float = 0.5,
                           pulse_norm: float = 0.5) -> CoyotePulse:
        """
        Generate a single pulse with envelope-modulated duration.
        
        This method is the Coyote equivalent of the pulse generation in the
        pulse-based algorithm. It creates a single pulse with parameters determined
        by the current envelope value, applying randomization and polarity as needed.
        
        Note: Parameters are already interpolated and clipped to appropriate ranges.
        
        Args:
            base_time: Starting time for this pulse sequence (seconds)
            pulse_index: Index of this pulse within the sequence
            base_intensity: Base intensity value (0-100)
            envelope: The envelope array for duration modulation
            envelope_period: Period of the envelope in seconds
            pulse_freq: Pulse frequency parameter (Hz) - already interpolated
            carrier_freq: Carrier frequency parameter (Hz) - already interpolated
            min_duration: Minimum pulse duration (ms)
            max_duration: Maximum pulse duration (ms)
            pulse_interval_random: Random factor for pulse interval (0-1) - already interpolated
            carrier_norm: Normalized carrier frequency (0-1) - pre-calculated
            pulse_norm: Normalized pulse frequency (0-1) - pre-calculated
        Returns:
            A CoyotePulse object
        """
        # The carrier frequency only affects pulse timing, not durations
        # Higher carrier frequencies = faster pulse intervals
        modified_pulse_freq = pulse_freq * (0.5 + carrier_norm)
        
        # Calculate pulse interval based on the modified frequency
        pulse_interval_sec = 1.0 / modified_pulse_freq if modified_pulse_freq > 0 else 1.0
        
        # Apply random interval variation if specified (same as pulse-based algorithm)
        if pulse_interval_random != 0:
            pulse_interval_sec = pulse_interval_sec * np.random.uniform(1 - pulse_interval_random, 1 + pulse_interval_random)
            
        pulse_time = base_time + pulse_index * pulse_interval_sec
        
        # Sequence-based envelope: compute phase in envelope period and use attack envelope function
        # Interpolate axes at pulse_time
        rise_time = float(self.params.pulse_rise_time.interpolate(pulse_time))
        width_time = float(self.params.pulse_width.interpolate(pulse_time))
        # For now, set fall_time = rise_time (symmetrical attack/decay); can add separate fall axis if needed
        fall_time = rise_time
        envelope_period = rise_time + width_time + fall_time
        if envelope_period <= 0:
            envelope_period = 1e-6  # Prevent div by zero
        # Compute phase in envelope period
        phase = (pulse_time % envelope_period) / envelope_period
        rise_frac = rise_time / envelope_period
        width_frac = width_time / envelope_period
        fall_frac = fall_time / envelope_period
        def envelope_func(phase, rise, width, fall):
            if phase < rise:
                return phase / max(rise, 1e-6)
            elif phase < rise + width:
                return 1.0
            elif phase < rise + width + fall:
                return 1.0 - (phase - rise - width) / max(fall, 1e-6)
            else:
                return 0.0
        env_value = envelope_func(phase, rise_frac, width_frac, fall_frac)

        # --- Duration calculation ---
        # 1. Base duration from pulse_width and carrier_freq (classic TENS logic)
        base_duration = pulse_width / carrier_freq * 1000 if carrier_freq > 0 else COYOTE_MIN_PULSE_DURATION
        # 2. Add rise time shaping: treat rise time as a ramp proportion of the pulse
        #    For Coyote, we can't shape the pulse itself, but we can modulate intensity to simulate a ramp
        #    We'll scale intensity by a ramp factor if rise_time > 0
        ramp_factor = 1.0
        if pulse_rise_time > 0 and pulse_width > 0:
            ramp_fraction = min(pulse_rise_time / pulse_width, 1.0)
            # Simulate a linear ramp: average intensity over the pulse is reduced
            ramp_factor = 1.0 - 0.5 * ramp_fraction  # crude approximation

        # 3. Use envelope to modulate both duration and intensity (hybrid stereostim effect)
        min_dur = max(min_duration, COYOTE_MIN_PULSE_DURATION)
        max_dur = min(max_duration, COYOTE_MAX_PULSE_DURATION)
        env_norm = np.clip(env_value, 0, 1)
        
        # Duration: envelope controls frequency/texture
        effective_duration = int(np.clip(
            min_dur + (1 - env_norm) * (max_dur - min_dur),
            min_dur, max_dur
        ))
        effective_duration = int(np.clip(effective_duration, COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION))

        # Intensity: modulate by envelope and ramp, always relative to base_intensity (from alpha/beta)
        max_intensity = min(base_intensity, 100)
        # Weighted blend: channel mapping dominates, envelope/ramp add texture
        blend_weight = 0.3  # 0 = pure base_intensity, 1 = pure envelope/ramp
        shaped = env_norm * ramp_factor
        effective_intensity = int(np.clip(
            max_intensity * (blend_weight * shaped + (1 - blend_weight)),
            0, max_intensity
        ))
        # This ensures base intensity is always recognizable and envelope/ramp provide subtle shaping

        # --- Frequency reporting (for UI/debug) ---
        effective_freq = 1000.0 / effective_duration if effective_duration > 0 else 100.0

        # --- Optionally: Add randomization to pulse interval (not duration) ---
        # This is handled elsewhere, but can be used for advanced effects

        # --- Comments on packet timing ---
        # Max pulse duration: COYOTE_MAX_PULSE_DURATION (240 ms)
        # One packet (4 pulses) at max duration: 960 ms
        # This is the slowest possible output: ~1 packet/sec
        # At min duration (5 ms), one packet is 20 ms: fastest possible
        # The FIFO buffer and update logic ensure smooth, continuous output

        pulse = CoyotePulse(
            frequency=int(effective_freq),
            intensity=effective_intensity,
            duration=effective_duration
        )
        if pulse_index < 4 or pulse_index % 10 == 0:
            time_since_start = (pulse_time - self.start_time) * 1000
            logger.debug(f"Pulse {pulse_index}: in {time_since_start:.1f}ms, env={env_value:.2f}, "
                        f"duration={effective_duration}ms, freq={effective_freq:.1f}Hz, intensity={effective_intensity}% (env-modulated)")
        return pulse

    
    def _fill_channel_buffer(self, 
                          channel_id: str, 
                          current_time: float, 
                          intensity: int,
                          channel_params,
                          initialize: bool = False) -> ChannelState:
        """
        Fill or initialize a channel's pulse buffer with pulses.
        
        This unified method replaces both _initialize_buffer and _update_buffer,
        eliminating redundancy and ensuring consistent parameter handling.
        
        Args:
            channel_id: 'A' or 'B' channel identifier
            current_time: Current system time in seconds
            intensity: Intensity for this channel (0-100)
            channel_params: Channel-specific parameters
            initialize: If True, create a new buffer; if False, update existing one
        Returns:
            ChannelState object (new or updated)
        """
        if initialize:
            logger.info(f"Initializing pulse buffer for channel {channel_id} (in {(current_time - self.start_time) * 1000:.1f}ms)")
            state = None
        else:
            state = self.channel_states[channel_id]
            logger.debug(f"Filling buffer for channel {channel_id} (currently has {len(state.pulse_buffer)} pulses)")
        
        # Get channel frequency limits - these are used to calculate duration range
        min_freq = channel_params.minimum_frequency.get()
        max_freq = channel_params.maximum_frequency.get()
        
        # Apply global safety limits to channel limits
        # min_freq = np.clip(min_freq, self.safety_limits.minimum_carrier_frequency, 
        #                    self.safety_limits.maximum_carrier_frequency)
        # max_freq = np.clip(max_freq, self.safety_limits.minimum_carrier_frequency, 
        #                    self.safety_limits.maximum_carrier_frequency)
        
        # Calculate or reuse duration range based on frequency limits
        if initialize:
            # Initialize empty buffer
            pulse_buffer = deque()
            # Set up initial state
            state = ChannelState(
                pulse_buffer=pulse_buffer,
                start_time=current_time,
                elapsed_duration_ms=0.0,
                min_freq=min_freq,
                max_freq=max_freq,
                min_duration=0,  # Will be calculated below
                max_duration=0   # Will be calculated below
            )
            state.envelope_phase = 0.0  # Start at phase 0 for new buffer
        
        # Calculate how many new pulses to generate
        if initialize:
            new_pulses_needed = self.buffer_size
            pulse_idx_offset = 0
        else:
            new_pulses_needed = max(0, self.buffer_size - len(state.pulse_buffer))
            pulse_idx_offset = len(state.pulse_buffer)
        
        if new_pulses_needed <= 0:
            return state
            
        # Calculate base time for next pulse
        base_time = current_time
        if not initialize and state.pulse_buffer:
            # If buffer is not empty, start after the last pulse
            # Calculate how long since first pulse for accurate alignment
            elapsed_time = sum(p.duration for p in state.pulse_buffer) / 1000.0
            base_time = state.start_time + elapsed_time
        
        # --- Refactored: Phase-locked, envelope-synchronized pulse train generation ---
        # 1. Determine envelope period and average pulse frequency
        envelope = self.shared_envelope
        envelope_period = self.shared_envelope_period
        min_duration = frequency_to_duration(max_freq)
        max_duration = frequency_to_duration(min_freq)

        # 2. Determine how many pulses fit in one envelope period
        # Use the average pulse frequency (Hz) to determine N
        avg_pulse_freq = self.params.pulse_frequency.interpolate(current_time)
        if avg_pulse_freq <= 0:
            avg_pulse_freq = 1.0  # Prevent div by zero
        N = max(1, int(round(envelope_period * avg_pulse_freq)))

        # 3. Generate pulses for enough envelope periods to fill the buffer
        pulses_to_generate = new_pulses_needed
        period_idx = 0
        pulses_generated = 0
        while pulses_to_generate > 0:
            envelope_start_time = base_time + period_idx * envelope_period
            for i in range(N):
                if pulses_to_generate <= 0:
                    break
                # Phase-locked: continue from previous phase
                phase = (state.envelope_phase + pulses_generated / N) % 1.0
                pulse_time = envelope_start_time + phase * envelope_period
                subtle_jitter = 0.0
                pulse_time_jittered = pulse_time + subtle_jitter
                carrier_freq = self.params.carrier_frequency.interpolate(pulse_time_jittered)
                pulse_freq = self.params.pulse_frequency.interpolate(pulse_time_jittered)
                pulse_width = self.params.pulse_width.interpolate(pulse_time_jittered)
                pulse_rise_time = self.params.pulse_rise_time.interpolate(pulse_time_jittered)
                pulse_interval_random = self.params.pulse_interval_random.interpolate(pulse_time_jittered)
                carrier_freq = np.clip(carrier_freq, self.min_carrier_freq, self.max_carrier_freq)
                pulse_freq = np.clip(pulse_freq, self.min_pulse_freq, self.max_pulse_freq)
                pulse_width = np.clip(pulse_width, limits.PulseWidth.min, limits.PulseWidth.max)
                pulse_rise_time = np.clip(pulse_rise_time, limits.PulseRiseTime.min, limits.PulseRiseTime.max)
                carrier_norm = (carrier_freq - self.min_carrier_freq) / self.carrier_freq_range if self.carrier_freq_range > 0 else 0.5
                pulse_norm = (pulse_freq - self.min_pulse_freq) / self.pulse_freq_range if self.pulse_freq_range > 0 else 0.5
                env_idx = int(phase * (len(envelope) - 1))
                env_value = envelope[env_idx] if len(envelope) > 0 else 1.0
                pulse = self._generate_single_pulse(
                    base_time=pulse_time_jittered,
                    pulse_index=i,
                    base_intensity=intensity,
                    envelope=envelope,
                    envelope_period=envelope_period,
                    pulse_freq=pulse_freq,
                    carrier_freq=carrier_freq,
                    pulse_width=pulse_width,
                    pulse_rise_time=pulse_rise_time,
                    min_duration=min_duration,
                    max_duration=max_duration,
                    pulse_interval_random=pulse_interval_random,
                    carrier_norm=carrier_norm,
                    pulse_norm=pulse_norm
                )
                state.pulse_buffer.append(pulse)
                pulses_to_generate -= 1
                pulses_generated += 1
            period_idx += 1
        # Update envelope phase for continuity
        state.envelope_phase = (state.envelope_phase + pulses_generated / N) % 1.0
        # --- End refactor ---

        
        if initialize:
            logger.info(f"Generated initial buffer with {len(state.pulse_buffer)} pulses")
        else:
            logger.debug(f"Added {new_pulses_needed} pulses to buffer, now has {len(state.pulse_buffer)} pulses")
        
        return state
    
    def _get_channel_packet(self, channel_id: str, current_time: float, intensity: int, channel_params):
        """
        Get a packet of pulses for a channel, handling buffer management.
        
        This method is conceptually similar to how the pulse-based algorithm
        gets audio samples from its buffer, but adapted for the packet-based
        nature of the Coyote protocol.
        
        Args:
            channel_id: 'A' or 'B' channel identifier
            current_time: Current system time in seconds
            intensity: Intensity for this channel (0-100)
            channel_params: Channel-specific parameters
        Returns:
            Tuple of (list of pulses for this packet, next update time in seconds)
        """
        channel_state = self.channel_states[channel_id]
        
        # Initialize channel state if needed
        if channel_state is None:
            logger.info(f"First initialization for channel {channel_id}")
            channel_state = self._fill_channel_buffer(
                channel_id, current_time, intensity, channel_params, initialize=True
            )
            self.channel_states[channel_id] = channel_state
        else:
            # Calculate elapsed time since last update
            elapsed_time_ms = (current_time - channel_state.start_time) * 1000.0
            logger.debug(f"Channel {channel_id}: advancing time by {elapsed_time_ms:.1f}ms")
            
            # Update buffer based on elapsed time
            needs_more_pulses = channel_state.advance_time(elapsed_time_ms)
            
            # Reset start time for future calculations
            channel_state.start_time = current_time
            
            # If buffer is low, fill it
            if needs_more_pulses:
                if channel_state.is_empty:
                    logger.warning(f"Channel {channel_id}: Buffer is empty! Reinitializing.")
                    channel_state = self._fill_channel_buffer(
                        channel_id, current_time, intensity, channel_params, initialize=True
                    )
                    self.channel_states[channel_id] = channel_state
                else:
                    logger.debug(f"Channel {channel_id}: Filling buffer (currently has {len(channel_state.pulse_buffer)} pulses)")
                    channel_state = self._fill_channel_buffer(
                        channel_id, current_time, intensity, channel_params, initialize=False
                    )
        
        # Ensure we have enough pulses for a packet
        available_pulses = len(channel_state.pulse_buffer)
        
        assert available_pulses >= COYOTE_PULSES_PER_PACKET, \
            f"Not enough pulses available for channel {channel_id}: have {available_pulses}, need {COYOTE_PULSES_PER_PACKET}"
        
        # Take pulses for this packet
        packet_pulses = [channel_state.pulse_buffer.popleft() for _ in range(COYOTE_PULSES_PER_PACKET)]
        
        # Calculate when we should check back based on the pulse durations
        packet_duration_ms = sum(p.duration for p in packet_pulses)
        
        # We want to update before the packet is completely played
        # This ensures smooth transitions between packets
        margin_factor = 0.8  # Update after 80% of the packet duration
        next_update = current_time + (packet_duration_ms * margin_factor / 1000.0)
        next_update_in_ms = packet_duration_ms * margin_factor
        
        logger.debug(f"Channel {channel_id}: Packet with {len(packet_pulses)} pulses, "
                    f"duration={packet_duration_ms:.1f}ms, next update in {next_update_in_ms:.1f}ms")
        
        return packet_pulses, next_update
    
    def generate_packet(self, current_time: float) -> CoyotePulses:
        """
        Generate one packet of pulses for both channels.
        
        This method is the main entry point for generating Coyote pulse packets.
        It serves a similar role to the generate_audio method in the pulse-based algorithm, 
        but adapted for the Coyote's packet-based protocol.
        
        Args:
            current_time: Current system time in seconds
        Returns:
            CoyotePulses object containing pulses for both channels
        """
        self.seq += 1
        
        # Set start time if this is the first call
        if self.start_time == 0:
            self.start_time = current_time
        
        time_since_start_ms = (current_time - self.start_time) * 1000
        logger.debug(f"\n=== Generating packet #{self.seq} in {time_since_start_ms:.1f}ms ===")
        
        # Get position and volume (same as pulse-based algorithm)
        alpha, beta = self.position_params.get_position(current_time)
        volume = compute_volume(self.media, self.params.volume, current_time)
        
        # Process each channel independently
        channel_pulses = {}
        channel_next_updates = {}
        
        for channel_id, channel_params in [('A', self.params.channel_a), ('B', self.params.channel_b)]:
            # Calculate intensity for this channel based on position
            intensity = self._compute_channel_intensity(
                channel_id, 
                alpha, 
                beta, 
                volume
            )
            
            # Get pulses for this channel
            pulses, next_update = self._get_channel_packet(
                channel_id,
                current_time,
                intensity,
                channel_params
            )
            
            # Store results
            channel_pulses[channel_id] = pulses
            channel_next_updates[channel_id] = next_update
        
        # Calculate next update time based on shortest channel duration (earliest next update)
        next_update_time = min(channel_next_updates.values())
        update_in_ms = (next_update_time - current_time) * 1000
        
        # Create final pulse packet
        result = CoyotePulses(channel_pulses['A'], channel_pulses['B'])
        
        # Log details using relative time
        logger.debug(f"  Position: alpha={alpha:.2f}, beta={beta:.2f}, volume={volume:.2f}")
        logger.debug(f"  Next update in {update_in_ms:.1f}ms")
        
        # Store for later reference
        self.last_pulses = result
        self.next_update_time = next_update_time
        
        return result

    def get_envelope_data(self) -> Tuple[np.ndarray, float]:
        """
        Get the current (shared) envelope data for both channels.
        Returns:
            Tuple of (envelope array, envelope period in seconds)
            If no data is available, returns (empty array, 0)
        """
        # Always return a high-resolution preview envelope for UI widgets
        # Use current time and interpolated parameters for preview
        t = time.time()
        pulse_freq = self.params.pulse_frequency.interpolate(t)
        carrier_freq = self.params.carrier_frequency.interpolate(t)
        preview_points = 100
        preview_pulses = 6
        envelope, period = generate_envelope(
            t=t,
            pulse_freq=pulse_freq,
            carrier_freq=carrier_freq,
            num_points=preview_points,
            preview_pulses=preview_pulses
        )
        return envelope, period