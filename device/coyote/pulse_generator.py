from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass
from typing import Tuple

from device.coyote.common import clamp, normalize
from device.coyote.config import PulseTuning
from device.coyote.constants import (
    HARDWARE_MAX_FREQ_HZ,
    HARDWARE_MIN_FREQ_HZ,
    MAX_PULSE_DURATION_MS,
    MIN_PULSE_DURATION_MS,
)
from device.coyote.types import CoyotePulse
from stim_math.audio_gen.params import CoyoteAlgorithmParams, CoyoteChannelParams

logger = logging.getLogger("restim.coyote")


@dataclass
class TextureInfo:
    offset_ms: float
    mode: str
    headroom_up_ms: float
    headroom_down_ms: float


@dataclass
class PulseDebug:
    sequence_index: int
    raw_frequency_hz: float
    normalised_frequency: float
    mapped_frequency_hz: float
    frequency_limits: Tuple[float, float]
    base_duration_ms: float
    duration_limits: Tuple[int, int]
    jitter_fraction: float
    jitter_factor: float
    width_normalised: float
    texture_mode: str
    texture_headroom_up_ms: float
    texture_headroom_down_ms: float
    texture_applied_ms: float
    desired_duration_ms: float
    residual_ms: float


class PulseGenerator:
    """Builds hardware-friendly pulses for a single Coyote channel."""

    def __init__(
        self,
        name: str,
        params: CoyoteAlgorithmParams,
        channel_params: CoyoteChannelParams,
        carrier_freq_limits: Tuple[float, float],
        pulse_freq_limits: Tuple[float, float],
        pulse_width_limits: Tuple[float, float],
        tuning: PulseTuning,
    ) -> None:
        self.name = name
        self.params = params
        self.channel_params = channel_params
        self._carrier_limits = carrier_freq_limits
        self._pulse_freq_limits = pulse_freq_limits
        self._pulse_width_limits = pulse_width_limits
        self._tuning = tuning

        self._phase = 0.0
        self._residual_ms = 0.0

    @property
    def carrier_limits(self) -> Tuple[float, float]:
        return self._carrier_limits

    def advance_phase(self, texture_speed_hz: float, delta_time_s: float) -> None:
        if delta_time_s <= 0 or texture_speed_hz <= 0:
            return
        phase_delta = delta_time_s * texture_speed_hz * 2 * math.pi
        self._phase = (self._phase + phase_delta) % (2 * math.pi)

    def create_pulse(self, time_s: float, intensity: int, sequence_index: int) -> Tuple[CoyotePulse, PulseDebug]:
        min_freq, max_freq = self._channel_frequency_window()
        duration_limits = self._duration_limits(min_freq, max_freq)

        raw_frequency = float(self.params.pulse_frequency.interpolate(time_s))
        normalised = normalize(raw_frequency, self._pulse_freq_limits)
        mapped_frequency = min_freq + (max_freq - min_freq) * normalised
        if mapped_frequency <= 0:
            mapped_frequency = 1000.0 / duration_limits[1]
        base_duration = 1000.0 / mapped_frequency

        jitter_fraction = clamp(
            float(self.params.pulse_interval_random.interpolate(time_s)),
            0.0,
            self._tuning.jitter_limit_fraction,
        )
        jitter_factor = 1.0 + random.uniform(-jitter_fraction, jitter_fraction)

        width_normalised = self._pulse_width_normalised(time_s)
        texture_info = self._texture_offset(base_duration, width_normalised, min_freq, max_freq)

        desired_ms = base_duration * jitter_factor + texture_info.offset_ms
        duration, residual = self._apply_residual(desired_ms)
        duration, clamped = self._clamp_duration(duration, duration_limits)
        if clamped:
            residual = 0.0

        final_duration = max(MIN_PULSE_DURATION_MS, duration)
        final_frequency = int(max(1, round(1000.0 / final_duration)))
        final_intensity = int(clamp(intensity, 0, 100))

        debug = PulseDebug(
            sequence_index=sequence_index,
            raw_frequency_hz=raw_frequency,
            normalised_frequency=normalised,
            mapped_frequency_hz=mapped_frequency,
            frequency_limits=(min_freq, max_freq),
            base_duration_ms=base_duration,
            duration_limits=duration_limits,
            jitter_fraction=jitter_fraction,
            jitter_factor=jitter_factor,
            width_normalised=width_normalised,
            texture_mode=texture_info.mode,
            texture_headroom_up_ms=texture_info.headroom_up_ms,
            texture_headroom_down_ms=texture_info.headroom_down_ms,
            texture_applied_ms=texture_info.offset_ms,
            desired_duration_ms=desired_ms,
            residual_ms=residual,
        )

        return CoyotePulse(duration=final_duration, intensity=final_intensity, frequency=final_frequency), debug

    def _channel_frequency_window(self) -> Tuple[float, float]:
        minimum = max(float(self.channel_params.minimum_frequency.get()), HARDWARE_MIN_FREQ_HZ)
        maximum = min(float(self.channel_params.maximum_frequency.get()), HARDWARE_MAX_FREQ_HZ)
        if minimum >= maximum:
            return HARDWARE_MIN_FREQ_HZ, HARDWARE_MAX_FREQ_HZ
        return minimum, maximum

    def _pulse_width_normalised(self, time_s: float) -> float:
        raw = float(self.params.pulse_width.interpolate(time_s))
        low, high = self._pulse_width_limits
        if high <= low:
            return 0.0
        return clamp((raw - low) / (high - low), 0.0, 1.0)

    def _texture_offset(
        self,
        base_duration: float,
        width_norm: float,
        min_freq: float,
        max_freq: float,
    ) -> TextureInfo:
        if width_norm <= 0 or self._tuning.texture_depth_fraction <= 0:
            return TextureInfo(offset_ms=0.0, mode="none", headroom_up_ms=0.0, headroom_down_ms=0.0)

        min_duration = 1000.0 / max_freq
        max_duration = 1000.0 / min_freq

        up_headroom = max(0.0, max_duration - base_duration) * self._tuning.texture_depth_fraction * width_norm
        down_headroom = max(0.0, base_duration - min_duration) * self._tuning.texture_depth_fraction * width_norm

        if up_headroom > 1e-6 and down_headroom > 1e-6:
            amplitude = min(up_headroom, down_headroom)
            offset = amplitude * math.sin(self._phase)
            return TextureInfo(offset_ms=offset, mode="sym", headroom_up_ms=up_headroom, headroom_down_ms=down_headroom)

        sine = math.sin(self._phase)
        rectified = abs(sine) - 2.0 / math.pi

        if up_headroom > 1e-6:
            offset = up_headroom * rectified
            return TextureInfo(offset_ms=offset, mode="up", headroom_up_ms=up_headroom, headroom_down_ms=down_headroom)
        if down_headroom > 1e-6:
            offset = -down_headroom * rectified
            return TextureInfo(offset_ms=offset, mode="down", headroom_up_ms=up_headroom, headroom_down_ms=down_headroom)
        return TextureInfo(offset_ms=0.0, mode="none", headroom_up_ms=up_headroom, headroom_down_ms=down_headroom)

    def _apply_residual(self, desired_ms: float) -> Tuple[int, float]:
        accum = desired_ms + self._residual_ms
        rounded = int(round(accum))
        residual = accum - rounded
        bound = self._tuning.residual_bound
        residual = clamp(residual, -bound, bound)
        self._residual_ms = residual
        return max(1, rounded), residual

    def _duration_limits(self, min_freq: float, max_freq: float) -> Tuple[int, int]:
        minimum = max(MIN_PULSE_DURATION_MS, int(round(1000.0 / max_freq)))
        maximum = min(MAX_PULSE_DURATION_MS, int(round(1000.0 / min_freq)))
        if minimum > maximum:
            return MIN_PULSE_DURATION_MS, MAX_PULSE_DURATION_MS
        return minimum, maximum

    def _clamp_duration(self, duration_ms: int, limits: Tuple[int, int]) -> Tuple[int, bool]:
        low, high = limits
        clamped_duration = int(clamp(duration_ms, low, high))
        clamped = clamped_duration != duration_ms
        if clamped:
            self._residual_ms = 0.0
        return clamped_duration, clamped
