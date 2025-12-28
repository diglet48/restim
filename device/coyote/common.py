from __future__ import annotations

from typing import Tuple

from stim_math.audio_gen.params import VolumeParams
from stim_math.axis import AbstractMediaSync


def clamp(value: float, lower: float, upper: float) -> float:
    if lower > upper:
        lower, upper = upper, lower
    return max(lower, min(value, upper))


def normalize(value: float, bounds: Tuple[float, float]) -> float:
    low, high = bounds
    if high <= low:
        return 0.0
    return clamp((value - low) / (high - low), 0.0, 1.0)


def volume_at(media: AbstractMediaSync, volume: VolumeParams, time_s: float) -> float:
    if not media.is_playing():
        return 0.0

    master = clamp(float(volume.master.last_value()), 0.0, 1.0)
    api = clamp(float(volume.api.interpolate(time_s)), 0.0, 1.0)
    inactivity = clamp(float(volume.inactivity.last_value()), 0.0, 1.0)
    external = clamp(float(volume.external.last_value()), 0.0, 1.0)

    if inactivity == 0:
        inactivity = 1.0

    return master * api * inactivity * external


def split_seconds(seconds: float) -> Tuple[int, int, int, int]:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return hours, minutes, secs, millis
