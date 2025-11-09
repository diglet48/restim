from __future__ import annotations

from dataclasses import dataclass

from qt_ui import settings


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


@dataclass(frozen=True)
class PulseTuning:
    queue_horizon_s: float
    packet_margin: float
    texture_min_hz: float
    texture_max_hz: float
    texture_depth_fraction: float
    jitter_limit_fraction: float
    residual_bound: float

    @classmethod
    def from_settings(cls) -> "PulseTuning":
        queue_horizon = max(0.1, float(settings.coyote_queue_horizon_seconds.get()))
        margin = _clamp(float(settings.coyote_packet_margin.get()), 0.1, 1.0)

        texture_min = max(0.0, float(settings.coyote_texture_min_hz.get()))
        texture_max = max(texture_min + 1e-6, float(settings.coyote_texture_max_hz.get()))

        depth = _clamp(float(settings.coyote_texture_depth_fraction.get()), 0.0, 1.0)
        jitter_limit = _clamp(float(settings.coyote_jitter_limit_fraction.get()), 0.0, 1.0)
        residual = max(0.0, float(settings.coyote_residual_bound.get()))

        return cls(
            queue_horizon_s=queue_horizon,
            packet_margin=margin,
            texture_min_hz=texture_min,
            texture_max_hz=texture_max,
            texture_depth_fraction=depth,
            jitter_limit_fraction=jitter_limit,
            residual_bound=residual,
        )


def load_pulse_tuning() -> PulseTuning:
    """Helper for consumers that do not need to customise tuning."""
    return PulseTuning.from_settings()
