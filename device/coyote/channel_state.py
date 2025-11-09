from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List

from device.coyote.types import CoyotePulse


class ChannelState:
    """Tracks playback progress for the last packet issued to a channel."""

    def __init__(self) -> None:
        self._current_packet: Deque[CoyotePulse] = deque()
        self._elapsed_ms = 0.0
        self._total_ms = 0.0
        self._start_time_s = 0.0
        self._finish_time_s = 0.0

    def load_packet(self, start_time_s: float, packet: Iterable[CoyotePulse]) -> None:
        pulses = list(packet)
        self._current_packet = deque(pulses)
        self._total_ms = float(sum(p.duration for p in pulses))
        self._elapsed_ms = 0.0
        self._start_time_s = start_time_s
        self._finish_time_s = start_time_s + (self._total_ms / 1000.0 if self._total_ms else 0.0)

    def advance(self, delta_ms: float) -> None:
        if delta_ms <= 0:
            return
        self._elapsed_ms += delta_ms

    def remaining_ms(self) -> float:
        if self._total_ms == 0:
            return 0.0
        return max(0.0, self._total_ms - self._elapsed_ms)

    def ready(self) -> bool:
        return self.remaining_ms() <= 0.0

    @property
    def finish_time_s(self) -> float:
        return self._finish_time_s

    @property
    def current_packet(self) -> List[CoyotePulse]:
        return list(self._current_packet)
