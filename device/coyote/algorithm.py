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

def generate_envelope(
    t: float, 
    pulse_freq: float, 
    pulse_width_cycles: float, 
    pulse_rise_time_cycles: float,
    num_cycles: int = 1
) -> Tuple[np.ndarray, float]:
    """
    Generate an envelope shape that determines how pulses' durations are modulated.
    
    This function is similar to the envelope generation in the pulse-based algorithm, 
    but it's used to modulate duration instead of amplitude. It creates a continuous
    envelope shape that provides a wave-like sensation when applied to pulse durations.
    
    Note: The pulse_freq parameter that's passed in should already incorporate 
    any scaling from the carrier frequency. This allows the relationship between 
    pulse and carrier frequencies to affect the envelope's timing characteristics.
    
    Args:
        t: Current time in seconds (used for phase calculation)
        pulse_freq: Base frequency for the envelope (Hz), already scaled by carrier frequency
        pulse_width_cycles: Width of each pulse in carrier cycles (shape factor)
        pulse_rise_time_cycles: Fade in/out time in carrier cycles (smoothness)
        num_cycles: Number of complete cycles to generate in the envelope
    Returns:
        Tuple of (envelope array, period in seconds)
    """
    # Validate and clip parameters using the same limits as pulse-based algorithm
    pulse_freq = np.clip(pulse_freq, limits.PulseFrequency.min, limits.PulseFrequency.max)
    pulse_width_cycles = np.clip(pulse_width_cycles, limits.PulseWidth.min, limits.PulseWidth.max)
    pulse_rise_time_cycles = np.clip(pulse_rise_time_cycles, limits.PulseRiseTime.min, limits.PulseRiseTime.max)
    
    # Calculate envelope period (seconds per cycle)
    envelope_period = 1.0 / pulse_freq if pulse_freq > 0 else 1.0
    total_period = envelope_period * num_cycles
    
    # Use higher resolution for more accurate envelope shapes
    points_per_cycle = max(100, int(envelope_period * 200))
    num_points = points_per_cycle * num_cycles
    
    t_points = np.linspace(0, total_period, num_points, endpoint=False)
    
    # Convert parameters to shaping factors
    width_factor = pulse_width_cycles / 10.0  # Wider pulses = more time at peaks
    rise_factor = pulse_rise_time_cycles / 10.0  # More rise time = smoother transitions
    
    # Create base sine wave across multiple cycles
    envelope = np.sin(2 * np.pi * t_points / envelope_period)
    
    # Shape the envelope based on pulse width
    envelope_sign = np.sign(envelope)
    envelope = envelope_sign * np.power(np.abs(envelope), 1.0 / width_factor)
    
    # Apply smoothing based on rise time
    if rise_factor > 0:
        # Choose window size based on rise factor
        window_size = int(points_per_cycle * rise_factor)
        if window_size > 2:  # Need at least 3 points for a valid window
            window = np.hanning(window_size)
            envelope = np.convolve(envelope, window / np.sum(window), mode='same')
            envelope /= max(np.max(np.abs(envelope)), 1e-6)  # Renormalize after smoothing
    
    return envelope, total_period

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
        # Two-channel bias mapping: beta partitions channels, total strength by volume & calibration
        # Partition between A and B via beta (-1..+1 → A_frac=0..1)
        A_frac = np.clip(0.5 + 0.5 * beta, 0, 1)
        B_frac = 1.0 - A_frac
        # Total stimulation strength (shared constant sum)
        center_calib = ThreePhaseCenterCalibration(self.params.calibrate.center.last_value())
        scale = center_calib.get_scale(alpha, beta)
        total_strength = volume * scale
        # Channel intensity based on partition fraction
        intensity = (A_frac if channel_id == 'A' else B_frac) * total_strength
        
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
        
        # Find corresponding position in envelope
        # Apply phase offset to shift the envelope (similar to pulse-based algorithm)
        # phase = ((pulse_time % envelope_period) / envelope_period + phase_offset / (2 * np.pi)) % 1.0
        # env_idx = int(phase * len(envelope))
        # env_value = envelope[env_idx]

        # # Apply polarity to the envelope value
        # # This emulates the effect of polarity in the pulse-based algorithm
        # if pulse_polarity < 0:
        #     env_value = -env_value

        # Get envelope value at the current time
        phase = ((pulse_time % envelope_period) / envelope_period / (2 * np.pi)) % 1.0
        env_idx = int(phase * len(envelope))
        env_value = envelope[env_idx]

        # Use pulse_norm to interpolate between min and max duration
        # pulse_norm=0 (lowest frequency) → max_duration (longest pulses)
        # pulse_norm=1 (highest frequency) → min_duration (shortest pulses)
        if min_duration < max_duration:  # Just to be safe
            # First, establish base duration range based on pulse_norm
            base_duration_range = (max_duration - min_duration)
            base_min = max_duration - pulse_norm * base_duration_range
            base_max = base_min + (base_duration_range * 0.5)  # Half the original range
            
            # Now map envelope value (-1 to +1) to normalized [0, 1]
            normalized_env = (env_value + 1.0) / 2.0
            
            # Apply envelope modulation within the pulse_norm established range
            effective_duration = int(base_min + normalized_env * (base_max - base_min))
        else:
            effective_duration = min_duration  # Fallback
        
        # Ensure we stay within device limits
        effective_duration = np.clip(effective_duration, COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION)
        
        # Calculate equivalent frequency for the device output
        effective_freq = 1000.0 / effective_duration if effective_duration > 0 else 100.0
        
        pulse = CoyotePulse(
            frequency=int(effective_freq),
            intensity=base_intensity,
            duration=effective_duration
        )
        
        # Log first few pulses and occasional ones after for debugging
        if pulse_index < 4 or pulse_index % 10 == 0:
            time_since_start = (pulse_time - self.start_time) * 1000
            logger.debug(f"Pulse {pulse_index}: in {time_since_start:.1f}ms, env={env_value:.2f}, "
                        f"duration={effective_duration}ms, freq={effective_freq:.1f}Hz, intensity={base_intensity}%")
        
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
        
        # Generate new pulses with per-pulse parameter interpolation
        current_pulse_time = base_time  # Track the time for each pulse
        for i in range(new_pulses_needed):
            pulse_idx = pulse_idx_offset + i
            
            # Interpolate parameters at the exact time of this pulse
            pulse_time = current_pulse_time
            
            # Interpolate parameters at the exact time of this pulse
            carrier_freq = self.params.carrier_frequency.interpolate(pulse_time)
            pulse_freq = self.params.pulse_frequency.interpolate(pulse_time)
            pulse_width = self.params.pulse_width.interpolate(pulse_time)
            pulse_rise_time = self.params.pulse_rise_time.interpolate(pulse_time)
            pulse_interval_random = self.params.pulse_interval_random.interpolate(pulse_time)
            
            # Clip parameters
            carrier_freq = np.clip(carrier_freq, 
                                self.min_carrier_freq,
                                self.max_carrier_freq)
            pulse_freq = np.clip(pulse_freq, 
                                self.min_pulse_freq,
                                self.max_pulse_freq)
            pulse_width = np.clip(pulse_width, limits.PulseWidth.min, limits.PulseWidth.max)
            pulse_rise_time = np.clip(pulse_rise_time, limits.PulseRiseTime.min, limits.PulseRiseTime.max)
            
            # Normalize carrier and pulse frequencies within their respective ranges
            if self.carrier_freq_range > 0:
                carrier_norm = (carrier_freq - self.min_carrier_freq) / self.carrier_freq_range
            else:
                carrier_norm = 0.5
                
            if self.pulse_freq_range > 0:
                pulse_norm = (pulse_freq - self.min_pulse_freq) / self.pulse_freq_range
            else:
                pulse_norm = 0.5

            # Calculate min and max durations from channel frequency limits
            min_duration = frequency_to_duration(max_freq)  # Shortest duration (highest frequency)
            max_duration = frequency_to_duration(min_freq)  # Longest duration (lowest frequency)
            
            # Ensure durations stay within device limits
            min_duration = np.clip(min_duration, COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION)
            max_duration = np.clip(max_duration, COYOTE_MIN_PULSE_DURATION, COYOTE_MAX_PULSE_DURATION)
            
            # Update state duration range
            if i == 0:  # Only need to update this once per buffer fill
                state.min_duration = min_duration
                state.max_duration = max_duration
                state.last_pulse_freq = pulse_freq
                state.last_pulse_width = pulse_width
                state.last_pulse_rise_time = pulse_rise_time
            
            # Get or generate envelope
            # Calculate modified pulse frequency based on carrier normalization
            modified_pulse_freq = pulse_freq * (0.5 + carrier_norm)
            
            # Check if we need a new envelope
            if (self.shared_envelope.size == 0 or 
                abs(modified_pulse_freq - self.last_shared_pulse_freq) > 0.1 or
                abs(pulse_width - self.last_shared_pulse_width) > 0.01 or
                abs(pulse_rise_time - self.last_shared_pulse_rise_time) > 0.01):
                
                logger.debug(f"Generating new envelope: carrier={carrier_freq:.1f}Hz, "
                            f"pulse_freq={pulse_freq:.1f}Hz, width={pulse_width:.2f}, "
                            f"rise={pulse_rise_time:.2f}")
                
                self.shared_envelope, self.shared_envelope_period = generate_envelope(
                    pulse_time, 
                    modified_pulse_freq, 
                    pulse_width, 
                    pulse_rise_time,
                    num_cycles=4
                )
                
                # Store parameter values for comparison
                self.last_shared_pulse_freq = modified_pulse_freq
                self.last_shared_pulse_width = pulse_width
                self.last_shared_pulse_rise_time = pulse_rise_time
                
            pulse = self._generate_single_pulse(
                base_time=base_time,
                pulse_index=pulse_idx,
                base_intensity=intensity,
                envelope=self.shared_envelope,
                envelope_period=self.shared_envelope_period,
                pulse_freq=pulse_freq,
                carrier_freq=carrier_freq,
                min_duration=min_duration,
                max_duration=max_duration,
                pulse_interval_random=pulse_interval_random,
                carrier_norm=carrier_norm,
                pulse_norm=pulse_norm
            )
            state.pulse_buffer.append(pulse)
            
            # Update pulse time for next pulse using the actual duration
            current_pulse_time += pulse.duration / 1000.0
        
        if initialize:
            logger.info(f"Generated initial buffer with {len(state.pulse_buffer)} pulses")
        else:
            logger.debug(f"Added {new_pulses_needed} pulses to buffer, now has {len(state.pulse_buffer)} pulses")
        
        return state

    def _get_channel_packet(self, 
                            channel_id: str,
                            current_time: float,
                            intensity: int,
                            channel_params) -> Tuple[List[CoyotePulse], float]:
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
        It serves a similar role to the generate_audio method in the pulse-based
        algorithm, but adapted for the Coyote's packet-based protocol.
        
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
        return self.shared_envelope, self.shared_envelope_period