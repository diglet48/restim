from __future__ import annotations

import logging
from collections import deque
from typing import Callable, Deque, List, Tuple

from device.coyote.common import clamp, volume_at
from device.coyote.config import PulseTuning
from device.coyote.constants import MIN_PULSE_DURATION_MS, PULSES_PER_PACKET
from device.coyote.pulse_generator import PulseDebug, PulseGenerator
from device.coyote.types import CoyotePulse
from stim_math.axis import AbstractMediaSync
from stim_math.audio_gen.params import CoyoteAlgorithmParams

logger = logging.getLogger("restim.coyote")


class ChannelController:
    """Maintains a rolling queue of pulses for a single hardware channel."""

    def __init__(
        self,
        name: str,
        media: AbstractMediaSync,
        params: CoyoteAlgorithmParams,
        generator: PulseGenerator,
        positional_intensity_fn: Callable[[float, float], Tuple[int, int]],
        tuning: PulseTuning,
    ) -> None:
        self._name = name
        self._media = media
        self._params = params
        self._generator = generator
        self._positional_intensity_fn = positional_intensity_fn
        self._tuning = tuning

        self._queue: Deque[CoyotePulse] = deque()
        self._queued_ms = 0.0

        self._last_intensity: float | None = None
        self._last_time: float | None = None
        self._max_change_per_pulse = float(self._params.max_intensity_change_per_pulse.get())

    def has_pulses(self, count: int) -> bool:
        return len(self._queue) >= count

    def queue_duration_ms(self) -> float:
        return self._queued_ms

    def fill_queue(self, now_s: float) -> None:
        horizon_end = now_s + self._tuning.queue_horizon_s
        coverage_s = self._queued_ms / 1000.0
        end_time = now_s + coverage_s

        added: List[CoyotePulse] = []
        seq_index = 0
        while end_time < horizon_end or len(self._queue) < PULSES_PER_PACKET:
            pulse_time = end_time
            pulse, debug = self._generate_pulse(pulse_time, seq_index)
            self._queue.append(pulse)
            added.append(pulse)
            self._queued_ms += pulse.duration
            end_time += pulse.duration / 1000.0
            seq_index += 1

        if added and logger.isEnabledFor(logging.DEBUG):
            durations = [p.duration for p in added]
            freqs = [p.frequency for p in added]
            logger.debug(
                "[%s] queued %d pulses (dur %d-%d ms, freq %d-%d Hz)",
                self._name,
                len(added),
                min(durations),
                max(durations),
                min(freqs),
                max(freqs),
            )

    def next_packet(self) -> List[CoyotePulse]:
        packet: List[CoyotePulse] = []
        while len(packet) < PULSES_PER_PACKET:
            if self._queue:
                pulse = self._queue.popleft()
                self._queued_ms = max(0.0, self._queued_ms - pulse.duration)
                packet.append(pulse)
            else:
                pulse = CoyotePulse(frequency=0, intensity=0, duration=MIN_PULSE_DURATION_MS)
                packet.append(pulse)
        return packet

    def _generate_pulse(self, time_s: float, seq_index: int) -> Tuple[CoyotePulse, PulseDebug]:
        volume = volume_at(self._media, self._params.volume, time_s)
        intensity_a, intensity_b = self._positional_intensity_fn(time_s, volume)
        target = float(intensity_a if self._name == "A" else intensity_b)
        smoothed = self._smooth_intensity(target, time_s)
        pulse, debug = self._generator.create_pulse(time_s, int(round(smoothed)), seq_index)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                (
                    "  [%s] pulse #%d: freq_raw=%.2f Hz, freq_norm=%.2f, "
                    "freq_mapped=%.2f Hz, freq_limits=(%.1f-%.1f) Hz | "
                    "base_dur=%.2f ms, dur_limits=(%d-%d) ms, width_norm=%.2f, jitter=%.0f%% | "
                    "texture_mode=%s, texture_up=%.2f ms, texture_dn=%.2f ms, "
                    "texture_used=%.2f ms | desired=%.2f ms, residual=%.2f ms | "
                    "result: dur=%d ms, freq=%d Hz, intensity=%d%%"
                ),
                self._name,
                debug.sequence_index,
                debug.raw_frequency_hz,
                debug.normalised_frequency,
                debug.mapped_frequency_hz,
                debug.frequency_limits[0],
                debug.frequency_limits[1],
                debug.base_duration_ms,
                debug.duration_limits[0],
                debug.duration_limits[1],
                debug.width_normalised,
                debug.jitter_fraction * 100.0,
                debug.texture_mode,
                debug.texture_headroom_up_ms,
                debug.texture_headroom_down_ms,
                debug.texture_applied_ms,
                debug.desired_duration_ms,
                debug.residual_ms,
                pulse.duration,
                pulse.frequency,
                pulse.intensity,
            )

        return pulse, debug

    def _smooth_intensity(self, target: float, time_s: float) -> float:
        carrier_hz = float(self._params.carrier_frequency.interpolate(time_s))
        rise_cycles = float(self._params.pulse_rise_time.interpolate(time_s))
        tau_s = rise_cycles / carrier_hz if carrier_hz > 0 else 0.0

        last_value = self._last_intensity
        last_time = self._last_time

        if last_value is None or tau_s <= 0 or last_time is None:
            result = target
        else:
            dt = max(0.0, time_s - last_time)
            allowed = (dt / tau_s) * 100.0 if tau_s > 0 else float("inf")
            if self._max_change_per_pulse > 0:
                allowed = min(allowed, self._max_change_per_pulse)
            delta = clamp(target - last_value, -allowed, allowed)
            result = last_value + delta

        self._last_intensity = result
        self._last_time = time_s
        return result
