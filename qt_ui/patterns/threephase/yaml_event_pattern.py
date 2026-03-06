"""
YAML Event Pattern — turns edger477-style event definitions into loopable threephase patterns.

Each YAML event defines steps that modulate volume, pulse_frequency, pulse_width,
and carrier_frequency.  When used as a pattern the event's duration_ms becomes
the loop period; ramp_in / ramp_out at the seam create a natural rhythmic
swell-and-fade.

The pattern's update() returns (alpha, beta) — only non-zero if the event
explicitly modulates those axes.  update_extended() returns a dict of
axis-name → normalised value for the extra axes the motion generator should
write.
"""
from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Type

from qt_ui.patterns.threephase.base import ThreephasePattern, register_pattern

logger = logging.getLogger('restim.patterns.yaml_event')

# ---------------------------------------------------------------------------
# Data classes describing a parsed YAML event
# ---------------------------------------------------------------------------

@dataclass
class EventStep:
    """One operation inside an event definition."""
    operation: str                          # 'apply_modulation' or 'apply_linear_change'
    axes: List[str]                         # target axis names (comma-split)
    params: Dict[str, Any] = field(default_factory=dict)
    start_offset_ms: int = 0


@dataclass
class EventDefinition:
    """Fully-parsed event definition ready to be instantiated as a pattern."""
    name: str
    display_name: str
    category: str
    default_params: Dict[str, Any] = field(default_factory=dict)
    steps: List[EventStep] = field(default_factory=list)

    @property
    def duration_ms(self) -> int:
        return int(self.default_params.get('duration_ms', 10000))


# ---------------------------------------------------------------------------
# Waveform helpers
# ---------------------------------------------------------------------------

def _waveform_value(waveform: str, phase: float, duty_cycle: float = 0.5) -> float:
    """Evaluate a unit waveform at *phase* (0–2π), returning value in [-1, 1]."""
    t = (phase % (2 * math.pi)) / (2 * math.pi)  # 0–1 within one period
    if waveform == 'sin':
        return math.sin(phase)
    elif waveform == 'square':
        return 1.0 if t < duty_cycle else -1.0
    elif waveform == 'triangle':
        if t < 0.5:
            return -1.0 + 4.0 * t
        else:
            return 3.0 - 4.0 * t
    elif waveform == 'sawtooth':
        return 2.0 * t - 1.0
    return math.sin(phase)  # fallback


def _ramp_envelope(t_sec: float, duration_sec: float,
                   ramp_in_sec: float, ramp_out_sec: float) -> float:
    """Compute a trapezoidal ramp envelope value in [0, 1]."""
    if duration_sec <= 0:
        return 1.0
    env = 1.0
    if ramp_in_sec > 0 and t_sec < ramp_in_sec:
        env = min(env, t_sec / ramp_in_sec)
    if ramp_out_sec > 0 and t_sec > duration_sec - ramp_out_sec:
        env = min(env, (duration_sec - t_sec) / ramp_out_sec)
    return max(0.0, min(1.0, env))


# ---------------------------------------------------------------------------
# Step evaluators
# ---------------------------------------------------------------------------

def _resolve_param(value, defaults: Dict[str, Any]):
    """Substitute $-prefixed references with values from *defaults*."""
    if isinstance(value, str) and value.startswith('$'):
        key = value[1:]
        return defaults.get(key, 0.0)
    return value


def _eval_modulation(t_sec: float, duration_sec: float, params: Dict[str, Any],
                     axis: str) -> float:
    waveform = params.get('waveform', 'sin')
    frequency = float(params.get('frequency', 1.0))
    amplitude = float(params.get('amplitude', 0.0))
    max_level_offset = float(params.get('max_level_offset', 0.0))
    phase_deg = float(params.get('phase', 0.0))
    duty_cycle = float(params.get('duty_cycle', 0.5))
    ramp_in = float(params.get('ramp_in_ms', 0)) / 1000.0
    ramp_out = float(params.get('ramp_out_ms', params.get('ramp_in_ms', 0))) / 1000.0

    # Values are already in final units (TCode 0-1 or alpha/beta -1..+1).
    centre = max_level_offset
    phase_rad = math.radians(phase_deg)
    w = _waveform_value(waveform, 2 * math.pi * frequency * t_sec + phase_rad, duty_cycle)
    env = _ramp_envelope(t_sec, duration_sec, ramp_in, ramp_out)
    return (centre + amplitude * w) * env


def _eval_linear_change(t_sec: float, duration_sec: float, params: Dict[str, Any],
                        axis: str) -> float:
    start_value = float(params.get('start_value', 0.0))
    end_value = float(params.get('end_value', start_value))
    ramp_in = float(params.get('ramp_in_ms', 0)) / 1000.0
    ramp_out = float(params.get('ramp_out_ms', params.get('ramp_in_ms', 0))) / 1000.0

    # Values are already in final units (TCode 0-1 or alpha/beta -1..+1).
    # linear interpolation
    if duration_sec > 0:
        frac = t_sec / duration_sec
    else:
        frac = 1.0
    frac = max(0.0, min(1.0, frac))
    interp = start_value + (end_value - start_value) * frac

    env = _ramp_envelope(t_sec, duration_sec, ramp_in, ramp_out)
    return interp * env


def _eval_keyframes(t_sec: float, duration_sec: float, params: Dict[str, Any]) -> float:
    """Evaluate a keyframe sequence at the given time.

    Keyframes are a list of [time_ms, value] pairs.  Values are linearly
    interpolated between adjacent keyframes.  Outside the keyframe range
    the nearest endpoint value is held.
    """
    keyframes = params.get('keyframes', [])
    if not keyframes:
        return 0.0

    ramp_in = float(params.get('ramp_in_ms', 0)) / 1000.0
    ramp_out = float(params.get('ramp_out_ms', params.get('ramp_in_ms', 0))) / 1000.0

    t_ms = t_sec * 1000.0

    # Binary search or linear scan for the right segment
    if t_ms <= keyframes[0][0]:
        val = float(keyframes[0][1])
    elif t_ms >= keyframes[-1][0]:
        val = float(keyframes[-1][1])
    else:
        # Linear scan (keyframes are typically < 300 entries)
        val = float(keyframes[-1][1])
        for i in range(len(keyframes) - 1):
            t0, v0 = keyframes[i]
            t1, v1 = keyframes[i + 1]
            if t0 <= t_ms <= t1:
                if t1 == t0:
                    val = float(v0)
                else:
                    frac = (t_ms - t0) / (t1 - t0)
                    val = v0 + (v1 - v0) * frac
                break

    env = _ramp_envelope(t_sec, duration_sec, ramp_in, ramp_out)
    return val * env


# ---------------------------------------------------------------------------
# Mapping from YAML axis names → restim extended-axis dict keys
# ---------------------------------------------------------------------------

# The motion generator understands these keys:
AXIS_MAP: Dict[str, str] = {
    'volume':           'volume',
    'volume-prostate':  'volume',       # treated as same volume axis in restim
    'pulse_frequency':  'pulse_frequency',
    'pulse_width':      'pulse_width',
    'frequency':        'carrier_frequency',
    'alpha':            'alpha',
    'beta':             'beta',
    'alpha-prostate':   'alpha',
    'beta-prostate':    'beta',
}


# ---------------------------------------------------------------------------
# The pattern class
# ---------------------------------------------------------------------------

class YamlEventPattern(ThreephasePattern):
    """A threephase pattern generated from a YAML event definition.

    The event loops on a period of *duration_ms*.  Velocity scales the loop
    rate (higher velocity → shorter loop period) without changing internal
    waveform frequencies.
    """

    # display_name and category are set dynamically per-instance
    display_name = "YAML Event"
    description = ""
    category = "yaml"
    event_definition: Optional[EventDefinition] = None

    def __init__(self, amplitude: float = 1.0, velocity: float = 1.0,
                 event_def: Optional[EventDefinition] = None):
        super().__init__(amplitude=amplitude, velocity=velocity)
        resolved_event_def = event_def or self.event_definition
        if resolved_event_def is None:
            raise ValueError("YamlEventPattern requires an EventDefinition")

        self.event_def = resolved_event_def
        self.display_name = resolved_event_def.display_name
        self.description = resolved_event_def.name
        self.category = resolved_event_def.category
        self.elapsed = 0.0
        self.loop_duration = resolved_event_def.duration_ms / 1000.0  # seconds

        # Pre-resolve $-params in every step
        self._resolved_steps: List[tuple[EventStep, Dict[str, Any]]] = []  # (step, resolved_params)
        for step in resolved_event_def.steps:
            resolved = {}
            for k, v in step.params.items():
                resolved[k] = _resolve_param(v, resolved_event_def.default_params)
            # duration_ms inside params
            if 'duration_ms' not in resolved:
                resolved['duration_ms'] = resolved_event_def.duration_ms
            self._resolved_steps.append((step, resolved))

        # Extract ramp for pattern-level ping-pong envelope, then zero it
        # in step params so evaluators don't double-apply.
        if self._resolved_steps:
            first_p = self._resolved_steps[0][1]
            self._ramp_in_sec = float(first_p.get('ramp_in_ms', 500)) / 1000.0
            self._ramp_out_sec = float(first_p.get('ramp_out_ms',
                                       first_p.get('ramp_in_ms', 500))) / 1000.0
        else:
            self._ramp_in_sec = 0.5
            self._ramp_out_sec = 0.5
        for _, step_params in self._resolved_steps:
            step_params['ramp_in_ms'] = 0
            step_params['ramp_out_ms'] = 0

        # Detect whether this event has any alpha/beta steps
        self._has_motion = False
        for step in resolved_event_def.steps:
            for ax in step.axes:
                mapped = AXIS_MAP.get(ax, ax)
                if mapped in ('alpha', 'beta'):
                    self._has_motion = True
                    break
            if self._has_motion:
                break

    def name(self) -> str:
        return self.display_name

    def _ping_pong_time(self) -> tuple:
        """Compute ping-pong time and cycle envelope.

        Returns (t_sec, envelope) where t_sec bounces within
        [0, loop_duration] and envelope fades only at the cycle
        restart (t_sec near 0), not at the turnaround (t_sec near
        duration).
        """
        if self.loop_duration <= 0:
            return (0.0, 1.0)
        pp_period = 2.0 * self.loop_duration
        cycle_t = self.elapsed % pp_period
        # Mirror: forward on first half, reverse on second half
        if cycle_t <= self.loop_duration:
            t_sec = cycle_t
        else:
            t_sec = pp_period - cycle_t
        # Ramp envelope at the restart seam (cycle_t near 0 / pp_period)
        env = 1.0
        if self._ramp_in_sec > 0 and cycle_t < self._ramp_in_sec:
            env = min(env, cycle_t / self._ramp_in_sec)
        if self._ramp_out_sec > 0 and cycle_t > pp_period - self._ramp_out_sec:
            env = min(env, (pp_period - cycle_t) / self._ramp_out_sec)
        return (t_sec, max(0.0, min(1.0, env)))

    # -- core interface ----------------------------------------------------

    def update(self, dt: float) -> tuple:
        """Advance time and return (alpha, beta).
        If the event modulates alpha/beta, those values are returned;
        otherwise generate a default circular motion so the pattern
        produces visible movement while extended axes modulate the signal."""
        self.elapsed += dt
        # velocity is applied by the motion generator to dt already
        t_sec, envelope = self._ping_pong_time()

        if not self._has_motion:
            # Auto-generate circular motion driven by event envelope
            # Use the volume envelope (if any) to modulate radius
            radius = 0.6
            # One full circle per loop period
            phase = 2 * math.pi * t_sec / self.loop_duration if self.loop_duration > 0 else 0.0
            alpha_val = radius * math.cos(phase)
            beta_val = radius * math.sin(phase)
            return (alpha_val * envelope, beta_val * envelope)

        alpha_val = 0.0
        beta_val = 0.0

        for step, params in self._resolved_steps:
            step_duration = float(params.get('duration_ms', self.event_def.duration_ms)) / 1000.0
            offset = step.start_offset_ms / 1000.0
            local_t = t_sec - offset
            if local_t < 0 or local_t > step_duration:
                continue

            for ax in step.axes:
                mapped = AXIS_MAP.get(ax, ax)
                if mapped == 'alpha':
                    alpha_val += self._eval_step(step.operation, local_t, step_duration, params, ax)
                elif mapped == 'beta':
                    beta_val += self._eval_step(step.operation, local_t, step_duration, params, ax)

        return (alpha_val * envelope, beta_val * envelope)

    def update_extended(self, dt: float) -> Optional[Dict[str, float]]:
        """Return dict of extra axis values for the current tick.
        dt is unused here — elapsed was already advanced in update()."""
        if self.loop_duration <= 0:
            return None

        t_sec, envelope = self._ping_pong_time()

        # accumulate per-axis
        accum: Dict[str, float] = {}
        for step, params in self._resolved_steps:
            step_duration = float(params.get('duration_ms', self.event_def.duration_ms)) / 1000.0
            offset = step.start_offset_ms / 1000.0
            local_t = t_sec - offset
            if local_t < 0 or local_t > step_duration:
                continue

            for ax in step.axes:
                mapped = AXIS_MAP.get(ax, ax)
                if mapped in ('alpha', 'beta'):
                    continue  # handled in update()
                val = self._eval_step(step.operation, local_t, step_duration, params, ax)
                accum[mapped] = accum.get(mapped, 0.0) + val

        if not accum:
            return None

        # Apply ping-pong envelope
        if envelope != 1.0:
            for k in accum:
                accum[k] *= envelope

        # Values are already in final units (TCode 0-1) — pass through directly.
        return accum

    # -- helpers -----------------------------------------------------------

    def _eval_step(self, operation: str, t_sec: float, duration_sec: float,
                   params: Dict[str, Any], axis: str) -> float:
        if operation == 'apply_modulation':
            return _eval_modulation(t_sec, duration_sec, params, axis)
        elif operation == 'apply_linear_change':
            return _eval_linear_change(t_sec, duration_sec, params, axis)
        elif operation == 'apply_keyframes':
            return _eval_keyframes(t_sec, duration_sec, params)
        return 0.0


# ---------------------------------------------------------------------------
# Factory: bulk-register YAML patterns from parsed definitions
# ---------------------------------------------------------------------------

def register_yaml_events(definitions: List[EventDefinition]):
    """Dynamically register a list of EventDefinitions as patterns.

    Each gets its own subclass so @register_pattern can track them
    independently.
    """
    from qt_ui.patterns.threephase.base import _pattern_registry, _pattern_categories

    for event_def in definitions:
        cls_name = f"YamlEvent_{event_def.name}"
        pattern_cls: Type[ThreephasePattern] = type(cls_name, (YamlEventPattern,), {
            'display_name': event_def.display_name,
            'description': event_def.name,
            'category': event_def.category,
            'event_definition': event_def,
        })

        # Register in the global registry
        _pattern_registry[event_def.display_name] = pattern_cls
        cat = event_def.category
        if cat not in _pattern_categories:
            _pattern_categories[cat] = set()
        _pattern_categories[cat].add(event_def.display_name)

        logger.debug(f"Registered YAML event pattern '{event_def.display_name}' in category '{cat}'")
