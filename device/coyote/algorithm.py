"""
DG-LAB Coyote 3.0 E-Stim Algorithm Implementation

EXPERIMENTAL: Best-effort adaptation of restim's funscript-based algorithms to the Coyote 3.0's
hardware square pulse generator. This implementation attempts to simulate smooth parameter changes
and modulation on hardware that fundamentally outputs discrete square pulses.

Protocol Specification (Chinese):
https://github.com/DG-LAB-OPENSOURCE/DG-LAB-OPENSOURCE/blob/main/coyote/v3/README_V3.md

Hardware Specifications & Limitations:
--------------------------------------
- Two independent channels (A and B)
- Square pulse generator only (no smooth waveforms like continuous audio devices)
- Pulse parameters: 
  * Intensity: 0-100%
  * Duration: 5-240ms (sent as "waveform frequency" parameter in protocol, despite the name)
    - Spec documents 10-240ms range, but hardware appears to support down to 5ms
    - Spec also provides an optional extended mapping from input values 10-1000 → output 10-240
  * Relationship: frequency_hz = 1000 / duration_ms (simple inverse)
  * Effective frequency range: ~4.17Hz (240ms) to 200Hz (5ms)
  * This algorithm works in Hz internally, then converts to duration_ms when sending to device
- Protocol: B0 command contains 4 pulses per packet (20 bytes total)
- Spec recommends ~100ms update rate, but this implementation uses adaptive scheduling
  (sends next packet at 80% of current packet duration for seamless transitions)
- Device repeats last packet until new one arrives
- Invalid waveform data causes device to discard entire 4-pulse packet for that channel
- Channel strength range: 0-200 (separate from pulse intensity 0-100%)
- Balance parameters (BF command): frequency balance and intensity balance affect perceived output

Key Limitations:
- Cannot produce smooth continuous waveforms - only discrete square pulses
- Limited frequency range compared to audio-based devices
- Packet-based protocol requires continuous streaming (no gaps or device repeats last packet)
- No native envelope/modulation support - must be simulated via parameter variations
- Hardware balance parameters (frequency/intensity) affect output independently
- Each pulse duration is quantized to integer milliseconds

Algorithm Overview (Best-Effort Approach):
------------------------------------------
- Maps funscript pulse_frequency to channel-specific frequency ranges
- Applies optional jitter (pulse_interval_random) to pulse timing
- Adds zero-mean micro-texture via pulse_width modulation to simulate smoothness
- Smooths intensity transitions based on pulse_rise_time
- Maintains pulse queues (750ms horizon) for continuous output
- Uses barycentric mapping for three-phase position diagram intensity control
- Adaptive packet scheduling (80% of packet duration) for seamless output

Each channel maintains an independent pulse queue. The algorithm attempts to create perceptually
smooth sensations by varying pulse duration and intensity, but results will differ significantly
from audio-based continuous algorithms due to fundamental hardware limitations.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from device.coyote.channel_controller import ChannelController
from device.coyote.channel_state import ChannelState
from device.coyote.common import normalize, split_seconds, volume_at
from device.coyote.config import PulseTuning, load_pulse_tuning
from device.coyote.constants import PULSES_PER_PACKET
from device.coyote.pulse_generator import PulseGenerator
from device.coyote.types import CoyotePulse, CoyotePulses
from stim_math.axis import AbstractMediaSync
from stim_math.audio_gen.params import CoyoteAlgorithmParams, SafetyParams
from stim_math.audio_gen.various import ThreePhasePosition
from stim_math.threephase import ThreePhaseCenterCalibration

logger = logging.getLogger("restim.coyote")


@dataclass
class ChannelPipeline:
    name: str
    generator: PulseGenerator
    controller: ChannelController
    state: ChannelState


class CoyoteAlgorithm:
    def __init__(
        self,
        media: AbstractMediaSync,
        params: CoyoteAlgorithmParams,
        safety_limits: SafetyParams,
        carrier_freq_limits: Tuple[float, float],
        pulse_freq_limits: Tuple[float, float],
        pulse_width_limits: Tuple[float, float],
        pulse_rise_time_limits: Tuple[float, float],
        tuning: Optional[PulseTuning] = None,
    ) -> None:
        self.media = media
        self.params = params
        self.safety_limits = safety_limits
        self._carrier_limits = carrier_freq_limits
        self._pulse_rise_time_limits = pulse_rise_time_limits  # retained for API compatibility
        self.tuning = tuning or load_pulse_tuning()

        self.position = ThreePhasePosition(params.position, params.transform)

        channels: List[ChannelPipeline] = []
        for name, channel_params in (("A", params.channel_a), ("B", params.channel_b)):
            generator = PulseGenerator(name, params, channel_params, carrier_freq_limits, pulse_freq_limits, pulse_width_limits, self.tuning)
            controller = ChannelController(name, media, params, generator, self._positional_intensity, self.tuning)
            state = ChannelState()
            channels.append(ChannelPipeline(name, generator, controller, state))
        self._channels: Tuple[ChannelPipeline, ...] = tuple(channels)

        self._last_update_time: Optional[float] = None
        self.next_update_time: float = 0.0
        self._start_time: Optional[float] = None

    def generate_packet(self, current_time: float) -> Optional[CoyotePulses]:
        if self._last_update_time is None:
            self._last_update_time = current_time

        delta_ms = max(0.0, (current_time - self._last_update_time) * 1000.0)
        self._last_update_time = current_time

        self._advance_state(current_time, delta_ms)

        if not self._needs_packet():
            self._schedule_from_remaining(current_time)
            return None

        for channel in self._channels:
            channel.controller.fill_queue(current_time)

        packet_map: Dict[str, List[CoyotePulse]] = {}
        duration_map: Dict[str, int] = {}
        for channel in self._channels:
            pulses = channel.controller.next_packet()
            channel.state.load_packet(current_time, pulses)
            packet_map[channel.name] = pulses
            duration_map[channel.name] = sum(p.duration for p in pulses)

        pulses_a = packet_map.get("A", [])
        pulses_b = packet_map.get("B", [])
        duration_a_ms = duration_map.get("A", 0)
        duration_b_ms = duration_map.get("B", 0)

        durations = [duration for duration in duration_map.values() if duration > 0]
        if not durations:
            durations = [1]
        min_duration_ms = max(1, min(durations))
        self.next_update_time = current_time + (min_duration_ms / 1000.0) * self.tuning.packet_margin

        self._log_packet(current_time, pulses_a, pulses_b, duration_a_ms, duration_b_ms)

        return CoyotePulses(pulses_a, pulses_b)

    def get_next_update_time(self) -> float:
        return self.next_update_time

    def _needs_packet(self) -> bool:
        queue_low = any(not channel.controller.has_pulses(PULSES_PER_PACKET) for channel in self._channels)
        ready = any(channel.state.ready() for channel in self._channels)
        return ready or queue_low

    def _advance_state(self, current_time: float, delta_ms: float) -> None:
        for channel in self._channels:
            channel.state.advance(delta_ms)

        delta_s = delta_ms / 1000.0
        if delta_s <= 0:
            return

        carrier_hz = float(self.params.carrier_frequency.interpolate(current_time))
        carrier_norm = normalize(carrier_hz, self._carrier_limits)
        texture_speed = self.tuning.texture_min_hz + (self.tuning.texture_max_hz - self.tuning.texture_min_hz) * carrier_norm

        for channel in self._channels:
            channel.generator.advance_phase(texture_speed, delta_s)

    def _schedule_from_remaining(self, current_time: float) -> None:
        remaining = min(channel.state.remaining_ms() for channel in self._channels)
        self.next_update_time = current_time + (remaining / 1000.0) * self.tuning.packet_margin

    def _positional_intensity(self, time_s: float, volume: float) -> Tuple[int, int]:
        alpha, beta = self.position.get_position(time_s)

        w_left = max(0.0, (beta + 1.0) / 2.0)
        w_right = max(0.0, (1.0 - beta) / 2.0)
        w_neutral = max(0.0, alpha)

        total = w_left + w_right + w_neutral
        if total > 0:
            w_left /= total
            w_right /= total
            w_neutral /= total
        else:
            w_left = w_right = w_neutral = 0.0

        center_db = float(self.params.calibrate.center.last_value())
        scale = ThreePhaseCenterCalibration(center_db).get_scale(alpha, beta)

        intensity_a = int((w_left + w_neutral) * volume * scale * 100.0)
        intensity_b = int((w_right + w_neutral) * volume * scale * 100.0)
        return intensity_a, intensity_b

    def _log_packet(
        self,
        current_time: float,
        pulses_a: List[CoyotePulse],
        pulses_b: List[CoyotePulse],
        duration_a_ms: int,
        duration_b_ms: int,
    ) -> None:
        if not logger.isEnabledFor(logging.DEBUG):
            return

        alpha, beta = self.position.get_position(current_time)
        comps = self._display_time_components(current_time)
        media_type = self._media_type()
        volume = volume_at(self.media, self.params.volume, current_time)

        lines = [
            "=" * 72,
            f"Packet Generated @ {comps[0]:02}:{comps[1]:02}:{comps[2]:02}.{comps[3]:03} [{media_type}]",
            "=" * 72,
            f"Position: alpha={alpha:+.2f}, beta={beta:+.2f}, volume={volume:.0%}",
            "",
            f"Channel A: duration={duration_a_ms:.0f} ms",
        ]

        for idx, pulse in enumerate(pulses_a, 1):
            lines.append(f"  Pulse {idx}: {pulse.duration} ms @ {pulse.frequency} Hz ({pulse.intensity}%)")

        lines.extend(["", f"Channel B: duration={duration_b_ms:.0f} ms"])
        for idx, pulse in enumerate(pulses_b, 1):
            lines.append(f"  Pulse {idx}: {pulse.duration} ms @ {pulse.frequency} Hz ({pulse.intensity}%)")

        next_ms = max(0.0, (self.next_update_time - current_time) * 1000.0)
        lines.extend(
            [
                "",
                f"Next update: {next_ms:.0f} ms "
                f"(packet_dur_a={duration_a_ms:.0f} ms, packet_dur_b={duration_b_ms:.0f} ms, margin={self.tuning.packet_margin:.0%})",
                "=" * 72,
                "",
            ]
        )

        logger.debug("\n".join(lines))

    def _media_type(self) -> str:
        media_type = getattr(self.media, "media_type", None)
        if media_type:
            return str(media_type)
        class_name = self.media.__class__.__name__.lower()
        if class_name.startswith("internal"):
            return "internal"
        if "vlc" in class_name:
            return "vlc"
        if "mpv" in class_name:
            return "mpv"
        return class_name

    def _display_time_components(self, current_time: float):
        media_type = getattr(self.media, "media_type", None)
        if media_type and str(media_type).lower() != "internal":
            mapper = getattr(self.media, "map_timestamp", None)
            if callable(mapper) and self.media.is_playing():
                try:
                    rel_time = mapper(time.time())
                    if rel_time is not None and rel_time >= 0:
                        return split_seconds(rel_time)
                except Exception:  # pragma: no cover - defensive
                    pass

        if media_type and str(media_type).lower() == "internal":
            now = time.localtime()
            millis = int((time.time() - int(time.time())) * 1000)
            return now.tm_hour, now.tm_min, now.tm_sec, millis

        if self._start_time is None:
            self._start_time = current_time
        return split_seconds(current_time - self._start_time)
