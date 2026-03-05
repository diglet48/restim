"""
Generate 30 clutch scene events (3 per original event) with alpha/beta motion
derived from the Clutch SuperCollider source code.

Clutch uses polar coordinates (rho, theta) which map to cartesian:
  alpha = cos(theta) * rho
  beta  = sin(theta) * rho

Direction angles from core.sc:
  pX  = -π/2  -> (alpha=0.000, beta=-1.000)   pure -beta
  pY  =  π/2  -> (alpha=0.000, beta=+1.000)   pure +beta
  pX3 = -π/3  -> (alpha=0.500, beta=-0.866)   alpha+, beta-
  pY3 =  π/3  -> (alpha=0.500, beta=+0.866)   alpha+, beta+
  pA  = -2π/3 -> (alpha=-0.500, beta=-0.866)  alpha-, beta-
  pB  =  2π/3 -> (alpha=-0.500, beta=+0.866)  alpha-, beta+
  0   =  0    -> (alpha=1.000, beta=0.000)     pure alpha

For stroke patterns alternating dirs θ1 <-> θ2 at depth d:
  alpha oscillates between cos(θ1)*d and cos(θ2)*d
  beta  oscillates between sin(θ1)*d and sin(θ2)*d
  Frequency = 1 / (2 * dur_per_note)

For sweep from start to end angle at depth d:
  The dot traces an arc; alpha and beta both change.

For pingpong visiting 4 angles p1->p2->p3->p4:
  Complex multi-axis motion.

We approximate each as sin waves on alpha and beta axes.
"""

import math, yaml, sys, os

# Direction angles
pX  = -math.pi / 2
pY  =  math.pi / 2
pX3 = -math.pi / 3
pY3 =  math.pi / 3
pA  = -2 * math.pi / 3
pB  =  2 * math.pi / 3

def dir_xy(angle, depth=1.0):
    """Convert polar direction+depth to (alpha, beta)."""
    return (math.cos(angle) * depth, math.sin(angle) * depth)


def make_event(name, comment, pulse_rate, pulse_width,
               alpha_freq, alpha_amp, alpha_offset,
               beta_freq, beta_amp, beta_offset,
               beta_phase=0, duration_ms=8000, ramp_ms=500,
               volume_boost=0.01):
    """Build a YAML event dict."""
    params = {
        'duration_ms': duration_ms,
        'pulse_rate': pulse_rate,
        'pulse_width': pulse_width,
        'alpha_freq': alpha_freq,
        'alpha_amplitude': alpha_amp,
        'alpha_offset': alpha_offset,
        'beta_freq': beta_freq,
        'beta_amplitude': beta_amp,
        'ramp_ms': ramp_ms,
    }
    if beta_offset != 0:
        params['beta_offset'] = beta_offset
    if beta_phase != 0:
        params['beta_phase'] = beta_phase
    if volume_boost != 0:
        params['volume_boost'] = volume_boost

    steps = []

    # Volume boost (if any)
    if volume_boost != 0:
        steps.append({
            'operation': 'apply_linear_change',
            'axis': 'volume,volume-prostate',
            'params': {
                'start_value': '$volume_boost',
                'end_value': '$volume_boost',
                'duration_ms': '$duration_ms',
                'ramp_in_ms': '$ramp_ms',
                'ramp_out_ms': '$ramp_ms',
                'mode': 'additive',
            }
        })

    # Pulse frequency
    steps.append({
        'operation': 'apply_linear_change',
        'axis': 'pulse_frequency',
        'params': {
            'start_value': '$pulse_rate',
            'end_value': '$pulse_rate',
            'duration_ms': '$duration_ms',
            'ramp_in_ms': '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'overwrite',
        }
    })

    # Pulse width
    steps.append({
        'operation': 'apply_linear_change',
        'axis': 'pulse_width',
        'params': {
            'start_value': '$pulse_width',
            'end_value': '$pulse_width',
            'duration_ms': '$duration_ms',
            'ramp_in_ms': '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'overwrite',
        }
    })

    # Alpha modulation
    alpha_step = {
        'operation': 'apply_modulation',
        'axis': 'alpha',
        'params': {
            'waveform': 'sin',
            'frequency': '$alpha_freq',
            'amplitude': '$alpha_amplitude',
            'max_level_offset': '$alpha_offset',
            'duration_ms': '$duration_ms',
            'ramp_in_ms': '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'additive',
        }
    }
    steps.append(alpha_step)

    # Beta modulation
    beta_params = {
        'waveform': 'sin',
        'frequency': '$beta_freq',
        'amplitude': '$beta_amplitude',
        'max_level_offset': '$beta_offset' if beta_offset != 0 else 0,
        'duration_ms': '$duration_ms',
        'ramp_in_ms': '$ramp_ms',
        'ramp_out_ms': '$ramp_ms',
        'mode': 'additive',
    }
    if beta_phase != 0:
        beta_params['phase'] = '$beta_phase'
    beta_step = {
        'operation': 'apply_modulation',
        'axis': 'beta',
        'params': beta_params,
    }
    steps.append(beta_step)

    return {
        'name': name,
        'comment': comment,
        'definition': {
            'default_params': params,
            'steps': steps,
        }
    }


# ============================================================================
# Define all 30 events
# ============================================================================
events = []

# --- good_slave (pulse_rate=27, width=45) ---
# SC: pulse_change(rate:27, width:0.45, powerShift:0.01)
# 3 distinct contexts from scripts:

# 1. Intro warmup: stroke pX3/pY3, dur=4s, depth~0.85, wiggle_freq=3
#    alpha: ~constant 0.5*0.85=0.425, wiggle at 3Hz ~0.08
#    beta: oscillates ±0.866*0.85=0.74, freq=1/(2*4)=0.125Hz
events.append(make_event(
    'clutch_good_slave_1',
    'Intro: gentle stroke pX3/pY3, dur=4s — constant alpha bias, slow beta swing',
    pulse_rate=27, pulse_width=45,
    alpha_freq=3, alpha_amp=0.08, alpha_offset=0.42,
    beta_freq=0.125, beta_amp=0.73, beta_offset=0,
    duration_ms=8000, ramp_ms=500,
))

# 2. Act1 stroke_3: pX3/pX3/pY3/0, dur=2s, depth~0.85, wiggle_freq=5
#    4-beat pattern over 8s: alpha varies 0.425<->0.85, beta ±0.74 with gaps
#    alpha: sin 0.125Hz amp=0.2 offset=0.5; beta: sin 0.25Hz amp=0.73
events.append(make_event(
    'clutch_good_slave_2',
    'Act1: fast stroke pX3/pX3/pY3/0, dur=2s — alpha wanders, fast beta',
    pulse_rate=27, pulse_width=45,
    alpha_freq=0.125, alpha_amp=0.2, alpha_offset=0.5,
    beta_freq=0.25, beta_amp=0.73, beta_offset=0,
    duration_ms=8000, ramp_ms=500,
))

# 3. Act31 milk_1 sweep: pY->pX3, dur=4s, depth~0.9
#    Sweeps from (0, 0.9) to (0.45, -0.78)
#    alpha: 0->0.45 -> sin 0.25Hz amp=0.22 offset=0.22
#    beta: 0.9->-0.78 -> sin 0.125Hz amp=0.84
events.append(make_event(
    'clutch_good_slave_3',
    'Act31: sweep pY->pX3, dur=4s — diagonal motion across field',
    pulse_rate=27, pulse_width=45,
    alpha_freq=0.25, alpha_amp=0.22, alpha_offset=0.22,
    beta_freq=0.125, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=8000, ramp_ms=500,
))

# --- reward (pulse_rate=35, width=45) ---
# SC: pulse_change(rate:35, width:0.45, powerShift:0.01)

# 1. Intro warmup_3: stroke pX3/pY3, dur=2s, depth~0.85, wiggle_freq=3
#    Fast beta oscillation at 0.25Hz, alpha constant ~0.42
events.append(make_event(
    'clutch_reward_1',
    'Intro: fast stroke pX3/pY3, dur=2s — quick beta swing',
    pulse_rate=35, pulse_width=45,
    alpha_freq=3, alpha_amp=0.06, alpha_offset=0.42,
    beta_freq=0.25, beta_amp=0.73, beta_offset=0,
    duration_ms=6000, ramp_ms=400,
))

# 2. Act2 slow_1 sweep: pX<->pY, dur=6s, depth~0.65
#    Pure beta sweep (alpha≈0), slow
#    beta: sin 0.083Hz amp=0.65
events.append(make_event(
    'clutch_reward_2',
    'Act2: slow sweep pX<->pY, dur=6s — pure beta, gentle',
    pulse_rate=35, pulse_width=45,
    alpha_freq=1, alpha_amp=0.08, alpha_offset=0,
    beta_freq=0.083, beta_amp=0.65, beta_offset=0,
    duration_ms=12000, ramp_ms=500,
))

# 3. Act31 slow pingpong: pB/pA/pX3/pA, dur=8s, depth~0.9
#    Visits (-0.45,0.78),(-0.45,-0.78),(0.45,-0.78),(-0.45,-0.78)
#    alpha: sin 0.0625Hz amp=0.45 offset=0
#    beta: sin 0.125Hz amp=0.78
events.append(make_event(
    'clutch_reward_3',
    'Act31: slow pingpong pB->pA->pX3->pA, dur=8s — wide 4-angle traverse',
    pulse_rate=35, pulse_width=45,
    alpha_freq=0.0625, alpha_amp=0.45, alpha_offset=0,
    beta_freq=0.125, beta_amp=0.78, beta_offset=0,
    beta_phase=90,
    duration_ms=16000, ramp_ms=800,
))

# --- higher_rate (pulse_rate=120, width=35) ---
# SC: pulse_change(rate:120, width:0.35, powerShift:0.02)

# 1. Act2 intro_2: stroke pX3/pY3, dur=4s, depth~0.8
events.append(make_event(
    'clutch_higher_rate_1',
    'Act2: stroke pX3/pY3, dur=4s — standard beta swing with high pulse rate',
    pulse_rate=120, pulse_width=35,
    alpha_freq=2, alpha_amp=0.06, alpha_offset=0.4,
    beta_freq=0.125, beta_amp=0.69, beta_offset=0,
    duration_ms=8000, ramp_ms=300, volume_boost=0.02,
))

# 2. Act2 intro_3: stroke 0/0/pX3/pY3, dur=2s, depth~0.85
#    First 2 beats at dir=0 (pure alpha), last 2 at pX3/pY3
#    alpha: sin 0.125Hz amp=0.25 offset=0.55
#    beta: sin 0.25Hz amp=0.55 (less beta because 2/4 beats are at dir=0)
events.append(make_event(
    'clutch_higher_rate_2',
    'Act2: stroke 0/0/pX3/pY3, dur=2s — mixed alpha reach + beta swing',
    pulse_rate=120, pulse_width=35,
    alpha_freq=0.125, alpha_amp=0.25, alpha_offset=0.55,
    beta_freq=0.25, beta_amp=0.55, beta_offset=0,
    duration_ms=8000, ramp_ms=300, volume_boost=0.02,
))

# 3. Act31 milk_1 sweep: pY->pX3, dur=4s, depth~0.9
events.append(make_event(
    'clutch_higher_rate_3',
    'Act31: sweep pY->pX3, dur=4s — diagonal sweep with high pulse rate',
    pulse_rate=120, pulse_width=35,
    alpha_freq=0.25, alpha_amp=0.22, alpha_offset=0.22,
    beta_freq=0.125, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=8000, ramp_ms=300, volume_boost=0.02,
))

# --- edge (incr_power for duration, then reset) ---
# SC: edge just does power change; motion is whatever was running.
# For restim pattern: pulse_rate from the scene, plus the background motion.

# 1. Act1 edge_1: stroke pX3/pX3/pX3/pY3, dur=2s, depth~0.85, legato=0.4
#    Mostly pX3 with occasional pY3 -> alpha bias 0.42, beta mostly -0.74, occasional +0.74
#    Effective: alpha offset=0.42, beta asymmetric -> sin 0.125Hz amp=0.73
events.append(make_event(
    'clutch_edge_1',
    'Act1: edge over stroke pX3*3/pY3, dur=2s — rapid uneven beta',
    pulse_rate=60, pulse_width=40,
    alpha_freq=2, alpha_amp=0.15, alpha_offset=0.42,
    beta_freq=0.125, beta_amp=0.73, beta_offset=-0.2,
    duration_ms=20000, ramp_ms=2000, volume_boost=0.03,
))

# 2. Act2 sweep stroke_3: pX3<->pY3 alternating sweep, dur=2s, depth~0.85
#    Sweeps along the pX3->pY3 arc repeatedly
events.append(make_event(
    'clutch_edge_2',
    'Act2: edge over sweep pX3<->pY3, dur=2s — fast arc sweep',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.5, alpha_amp=0.15, alpha_offset=0.35,
    beta_freq=0.25, beta_amp=0.8, beta_offset=0,
    duration_ms=20000, ramp_ms=2000, volume_boost=0.03,
))

# 3. Act32 pingpong stroke_fast: pB/pX/pY3/0, dur=4s, depth~0.9
#    Visits (-0.45,0.78),(0,-0.9),(0.45,0.78),(0.9,0) -> wide traverse
#    alpha: sin 0.125Hz amp=0.45 offset=0.22
#    beta: sin 0.25Hz amp=0.84 phase=90
events.append(make_event(
    'clutch_edge_3',
    'Act32: edge over pingpong pB/pX/pY3/0, dur=4s — wide 4-angle sweep',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.125, alpha_amp=0.45, alpha_offset=0.22,
    beta_freq=0.25, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=20000, ramp_ms=2000, volume_boost=0.03,
))

# --- spike (pulsar signal overlaid on motion) ---
# SC: spike plays a pulsar tone; background motion continues.

# 1. Act31 milk_1 sweep: pY->pX3, dur=4s, depth~0.9
events.append(make_event(
    'clutch_spike_1',
    'Act31: spike over sweep pY->pX3 — diagonal motion with pulsar hit',
    pulse_rate=50, pulse_width=40,
    alpha_freq=0.25, alpha_amp=0.22, alpha_offset=0.22,
    beta_freq=0.125, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=6000, ramp_ms=300, volume_boost=0.02,
))

# 2. Act31 milk_3 sweep: pB<->pA, dur=4s, depth~0.83
#    Sweeps between (-0.42, 0.72) and (-0.42, -0.72) -> pure beta, alpha constant negative
events.append(make_event(
    'clutch_spike_2',
    'Act31: spike over sweep pB<->pA, dur=4s — beta oscillation, alpha bias negative',
    pulse_rate=60, pulse_width=40,
    alpha_freq=1, alpha_amp=0.05, alpha_offset=-0.42,
    beta_freq=0.125, beta_amp=0.72, beta_offset=0,
    duration_ms=6000, ramp_ms=300, volume_boost=0.02,
))

# 3. Act32 pingpong stroke_fast: pB/pX/pY3/0, dur variable
events.append(make_event(
    'clutch_spike_3',
    'Act32: spike over pingpong pB/pX/pY3/0 — wide 4-angle with pulsar hit',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.125, alpha_amp=0.45, alpha_offset=0.22,
    beta_freq=0.25, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=6000, ramp_ms=300, volume_boost=0.02,
))

# --- tantalize (edge-like with lighter spike) ---
# SC: tantalize_1/2 in ClutchAct31, always with slow pingpong

# 1. Act31 slow_1 pingpong: pB/pA/pX3/pA, dur=8s, depth~0.9, pulse(60,0.4)
events.append(make_event(
    'clutch_tantalize_1',
    'Act31: tantalize over slow pingpong pB/pA/pX3/pA, 60Hz — wide slow traverse',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.0625, alpha_amp=0.45, alpha_offset=0,
    beta_freq=0.125, beta_amp=0.78, beta_offset=0,
    beta_phase=90,
    duration_ms=14000, ramp_ms=1000, volume_boost=0.03,
))

# 2. Act31 slow_2 pingpong: same angles but pulse(35,0.4)
events.append(make_event(
    'clutch_tantalize_2',
    'Act31: tantalize over slow pingpong, 35Hz — gentler pulse, same wide motion',
    pulse_rate=35, pulse_width=40,
    alpha_freq=0.0625, alpha_amp=0.45, alpha_offset=0,
    beta_freq=0.125, beta_amp=0.78, beta_offset=0,
    beta_phase=90,
    duration_ms=14000, ramp_ms=1000, volume_boost=0.03,
))

# 3. Act31 go_stroke_3: stroke_fast + pingpong pB/pX/pY3/0
#    (tantalize never actually appears in this context in the script, but it's
#    a distinct 3rd motion archetype paired with tantalize's pulse behavior)
events.append(make_event(
    'clutch_tantalize_3',
    'Act31: tantalize over fast pingpong pB/pX/pY3/0 — rapid 4-angle',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.125, alpha_amp=0.45, alpha_offset=0.22,
    beta_freq=0.25, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=14000, ramp_ms=1000, volume_boost=0.03,
))

# --- tranquil (signal=nil, pulsar plays, then stops) ---
# SC: tranquil explicitly nils the motion signal. It's a rest moment.
# For looping patterns we add gentle motion curves from the surrounding context.

# 1. Gentle sweep pX<->pY: pure beta, very slow, low depth (calming)
events.append(make_event(
    'clutch_tranquil_1',
    'Gentle sweep pX<->pY — slow pure beta oscillation, restful',
    pulse_rate=15, pulse_width=45,
    alpha_freq=0.5, alpha_amp=0.05, alpha_offset=0,
    beta_freq=0.083, beta_amp=0.55, beta_offset=0,
    duration_ms=16000, ramp_ms=1000, volume_boost=0,
))

# 2. Very slow stroke pX3/pY3, low depth — barely moving
events.append(make_event(
    'clutch_tranquil_2',
    'Gentle stroke pX3/pY3 — barely moving, subtle alpha bias',
    pulse_rate=15, pulse_width=45,
    alpha_freq=1, alpha_amp=0.04, alpha_offset=0.3,
    beta_freq=0.0625, beta_amp=0.5, beta_offset=0,
    duration_ms=16000, ramp_ms=1000, volume_boost=0,
))

# 3. Slow sweep pY->pX3: very gentle diagonal drift
events.append(make_event(
    'clutch_tranquil_3',
    'Gentle sweep pY->pX3 — slow diagonal drift, peaceful',
    pulse_rate=15, pulse_width=45,
    alpha_freq=0.1, alpha_amp=0.15, alpha_offset=0.15,
    beta_freq=0.083, beta_amp=0.6, beta_offset=0,
    beta_phase=90,
    duration_ms=16000, ramp_ms=1000, volume_boost=0,
))

# --- freq_shift_up (no SC script calls, invented by edger477) ---
# Paired with representative motions from across the Clutch scripts.

# 1. Stroke pX3/pY3 standard
events.append(make_event(
    'clutch_freq_shift_up_1',
    'Freq shift up + stroke pX3/pY3 — standard beta swing',
    pulse_rate=60, pulse_width=40,
    alpha_freq=2, alpha_amp=0.06, alpha_offset=0.42,
    beta_freq=0.25, beta_amp=0.73, beta_offset=0,
    duration_ms=8000, ramp_ms=400,
))

# 2. Sweep pB<->pA
events.append(make_event(
    'clutch_freq_shift_up_2',
    'Freq shift up + sweep pB<->pA — negative alpha bias, beta swing',
    pulse_rate=60, pulse_width=40,
    alpha_freq=1, alpha_amp=0.05, alpha_offset=-0.42,
    beta_freq=0.125, beta_amp=0.72, beta_offset=0,
    duration_ms=8000, ramp_ms=400,
))

# 3. Sweep pY->pX3
events.append(make_event(
    'clutch_freq_shift_up_3',
    'Freq shift up + sweep pY->pX3 — diagonal motion',
    pulse_rate=60, pulse_width=40,
    alpha_freq=0.25, alpha_amp=0.22, alpha_offset=0.22,
    beta_freq=0.125, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=8000, ramp_ms=400,
))

# --- freq_shift_down (no SC script calls, invented by edger477) ---

# 1. Slow stroke
events.append(make_event(
    'clutch_freq_shift_down_1',
    'Freq shift down + slow stroke pX3/pY3 — gentle beta swing',
    pulse_rate=45, pulse_width=40,
    alpha_freq=2, alpha_amp=0.06, alpha_offset=0.42,
    beta_freq=0.125, beta_amp=0.73, beta_offset=0,
    duration_ms=8000, ramp_ms=400,
))

# 2. Pingpong pA/pB/pX3/pA
events.append(make_event(
    'clutch_freq_shift_down_2',
    'Freq shift down + pingpong pA/pB/pX3/pA — slow multi-angle',
    pulse_rate=45, pulse_width=40,
    alpha_freq=0.0625, alpha_amp=0.45, alpha_offset=0,
    beta_freq=0.125, beta_amp=0.78, beta_offset=0,
    beta_phase=90,
    duration_ms=12000, ramp_ms=500,
))

# 3. Sweep pX<->pY pure beta
events.append(make_event(
    'clutch_freq_shift_down_3',
    'Freq shift down + sweep pX<->pY — pure beta oscillation',
    pulse_rate=45, pulse_width=40,
    alpha_freq=1, alpha_amp=0.08, alpha_offset=0,
    beta_freq=0.083, beta_amp=0.65, beta_offset=0,
    duration_ms=12000, ramp_ms=500,
))

# --- pulse_wobble (no SC source, invented by edger477) ---

# 1. Stroke pX3/pY3 medium
events.append(make_event(
    'clutch_pulse_wobble_1',
    'Pulse wobble + stroke pX3/pY3 — medium beta swing',
    pulse_rate=50, pulse_width=40,
    alpha_freq=2, alpha_amp=0.08, alpha_offset=0.42,
    beta_freq=0.2, beta_amp=0.73, beta_offset=0,
    duration_ms=8000, ramp_ms=400,
))

# 2. Sweep pY->pX3 diagonal
events.append(make_event(
    'clutch_pulse_wobble_2',
    'Pulse wobble + sweep pY->pX3 — diagonal drift',
    pulse_rate=50, pulse_width=40,
    alpha_freq=0.25, alpha_amp=0.22, alpha_offset=0.22,
    beta_freq=0.125, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=8000, ramp_ms=400,
))

# 3. Pingpong pB/pX/pY3/0 fast
events.append(make_event(
    'clutch_pulse_wobble_3',
    'Pulse wobble + pingpong pB/pX/pY3/0 — fast 4-angle',
    pulse_rate=50, pulse_width=40,
    alpha_freq=0.125, alpha_amp=0.45, alpha_offset=0.22,
    beta_freq=0.25, beta_amp=0.84, beta_offset=0,
    beta_phase=90,
    duration_ms=8000, ramp_ms=400,
))


# ============================================================================
# Generate YAML text
# ============================================================================

def emit_yaml_event(ev):
    """Produce hand-formatted YAML text for one event definition."""
    lines = []
    lines.append(f'  # {ev["comment"]}')
    lines.append(f'  {ev["name"]}:')
    lines.append(f'    default_params:')

    dp = ev['definition']['default_params']
    for key, val in dp.items():
        lines.append(f'      {key}: {val}')

    lines.append(f'')
    lines.append(f'    steps:')

    for step in ev['definition']['steps']:
        lines.append(f'      - operation: {step["operation"]}')
        lines.append(f'        axis: {step["axis"]}')
        lines.append(f'        params:')
        for pk, pv in step['params'].items():
            lines.append(f'          {pk}: {pv}')
        lines.append(f'')  # blank line between steps

    return '\n'.join(lines)


def main():
    yaml_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'event_definitions', 'edger477_events.yml')

    # Read existing file
    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where the old clutch events start
    lines = content.split('\n')
    clutch_start = None
    for i, line in enumerate(lines):
        if 'Clutch events (credit' in line and line.strip().startswith('#'):
            # Go back to the separator line
            clutch_start = i - 1
            break

    if clutch_start is None:
        print("ERROR: Could not find clutch section header")
        sys.exit(1)

    # Keep everything before the old clutch section
    kept_lines = lines[:clutch_start]

    # Build new clutch section
    new_section = []
    new_section.append('')
    new_section.append('  # =========================================================================')
    new_section.append('  #  Clutch scene events (credit: AquariumParrot)')
    new_section.append('  #  Each captures motion context from the original SuperCollider script.')
    new_section.append('  #  3 variants per event with distinct motion patterns.')
    new_section.append('  # =========================================================================')
    new_section.append('')

    # Group events by base name
    base_names = [
        ('good_slave', 'good_slave (pulse_rate->27Hz for 5s, pulse_width->45%)'),
        ('reward', 'reward (pulse_rate->35Hz, pulse_width->45%)'),
        ('higher_rate', 'higher_rate (pulse_rate->120Hz, pulse_width->35%)'),
        ('edge', 'edge (power boost for duration)'),
        ('spike', 'spike (pulsar signal overlay)'),
        ('tantalize', 'tantalize (gentle edge with light spike)'),
        ('tranquil', 'tranquil (restful moment, low pulse rate)'),
        ('freq_shift_up', 'freq_shift_up (carrier frequency shift)'),
        ('freq_shift_down', 'freq_shift_down (carrier frequency shift)'),
        ('pulse_wobble', 'pulse_wobble (pulse rate modulation)'),
    ]

    for base, desc in base_names:
        matching = [e for e in events if e['name'].startswith(f'clutch_{base}_')]
        if matching:
            new_section.append(f'  # --- {desc} ---')
            new_section.append('')
            for ev in matching:
                new_section.append(emit_yaml_event(ev))

    # Write output
    output = '\n'.join(kept_lines) + '\n' + '\n'.join(new_section) + '\n'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'Wrote {len(events)} clutch scene events')
    print(f'Output: {yaml_file}')

    # Verify by parsing
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    defs = data.get('definitions', {})
    clutch_events = [k for k in defs if k.startswith('clutch_')]
    print(f'Clutch events in file: {len(clutch_events)}')
    for k in clutch_events:
        v = defs[k]
        has_alpha = any('alpha' in s.get('axis', '') for s in v.get('steps', []))
        has_beta = any('beta' in s.get('axis', '') for s in v.get('steps', []))
        motion = 'OK' if (has_alpha and has_beta) else 'MISSING MOTION!'
        print(f'  {k}: {motion}')


if __name__ == '__main__':
    main()
