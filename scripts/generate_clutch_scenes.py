"""
Generate clutch scene events with values taken directly from the blended funscripts.

At each event's video timestamp we read the funscript pos values:
  - pulse_frequency, pulse_width → pos / 100 (TCode 0-1)
  - alpha, beta → (pos - 50) / 50  (maps 0-100 → -1..+1)
  - volume → small additive constant (pattern boost, not absolute level)

The TCode values are written into the YAML and remapped to real units at runtime
via the user's FunscriptKit limits (e.g. pulse_frequency 0-100 Hz, pulse_width 4-10 cycles).
"""

import json, re, os, sys, yaml
import numpy as np

BLENDED = r'D:\downloads\01.estim\DeadlyDog_Clutch\Clutch\blended'
SC_DIR = os.path.join(os.path.dirname(__file__), 'clutch_supercollider', 'supercollider')

# Act offsets: SC relative time → absolute video time (ms)
# Found via grid search in _find_offsets.py
OFFSETS = {
    'intro': 6950,
    'act1':  373050,
    'act2':  1187200,
    'act31': 1973650,
    'act32': 2732250,
}


# =========================================================================
#  Funscript loading
# =========================================================================

def load_fs(axis):
    path = os.path.join(BLENDED, f'Clutch.{axis}.funscript')
    with open(path) as f:
        data = json.load(f)
    actions = data['actions']
    return (np.array([a['at'] for a in actions], dtype=float),
            np.array([a['pos'] for a in actions], dtype=float))


FS = {ax: load_fs(ax) for ax in ('pulse_frequency', 'pulse_width', 'volume', 'alpha', 'beta')}


def fs_pos(axis, t_ms):
    """Funscript pos (0-100) at t_ms — standard linear interpolation."""
    times, vals = FS[axis]
    return float(np.interp(t_ms, times, vals))


# =========================================================================
#  SC script parsing
# =========================================================================

def parse_sc(filename):
    with open(os.path.join(SC_DIR, filename)) as f:
        text = f.read()
    events = []
    for m in re.finditer(r'\[(\d+),\s*(\d+)\s*\+\s*\((\d+)/30\),\s*\{\s*\n\s*e\.(\w+)', text):
        t = int(m[1]) * 60 + int(m[2]) + int(m[3]) / 30
        events.append((t, m[4]))
    return events


ALL_SC = {
    'intro': parse_sc('00_intro_script.scd'),
    'act1':  parse_sc('01_act_1_script.scd'),
    'act2':  parse_sc('02_act_2_script.scd'),
    'act31': parse_sc('03_act_31_script.scd'),
    'act32': parse_sc('03_act_32_script.scd'),
}


# =========================================================================
#  Collect events by type
# =========================================================================

METHOD_GROUPS = {
    'good_slave':   'good_slave',
    'reward':       'reward',
    'higher_rate':  'higher_rate',
    'edge_1': 'edge', 'edge_2': 'edge',
    'spike': 'spike', 'spike_1': 'spike', 'spike_2': 'spike', 'spike_3': 'spike',
    'tantalize_1': 'tantalize', 'tantalize_2': 'tantalize',
    'tranquil':     'tranquil',
    'push': 'push', 'push_2': 'push',
}

occurrences = {}
for act, events in ALL_SC.items():
    for t_sec, method in events:
        group = METHOD_GROUPS.get(method)
        if group is None:
            continue
        video_ms = OFFSETS[act] + t_sec * 1000
        occurrences.setdefault(group, []).append((act, t_sec, video_ms))

for g in occurrences:
    occurrences[g].sort(key=lambda x: x[2])


def pick_3(items):
    """Pick 3 items spread evenly through the list."""
    n = len(items)
    if n <= 3:
        return items
    indices = [0, n // 2, n - 1]
    return [items[i] for i in indices]


# =========================================================================
#  Build a YAML event from funscript values
# =========================================================================

def make_event(name, comment, video_ms, duration_ms):
    """Build one event dict, reading all values directly from the funscripts."""

    # ---- pulse: TCode 0-1 (pos / 100) ----
    pf = round(fs_pos('pulse_frequency', video_ms) / 100.0, 3)
    pw = round(fs_pos('pulse_width',     video_ms) / 100.0, 3)

    # ---- alpha / beta: derive centre + amplitude from funscript ----
    half = duration_ms / 2
    a1 = (fs_pos('alpha', video_ms) - 50) / 50           # -1..+1
    a2 = (fs_pos('alpha', video_ms + half) - 50) / 50
    b1 = (fs_pos('beta',  video_ms) - 50) / 50
    b2 = (fs_pos('beta',  video_ms + half) - 50) / 50

    a_offset = round((a1 + a2) / 2, 3)
    a_amp    = max(round(abs(a1 - a2) / 2, 3), 0.1)
    b_offset = round((b1 + b2) / 2, 3)
    b_amp    = max(round(abs(b1 - b2) / 2, 3), 0.1)

    freq = round(1.0 / (duration_ms / 1000), 4)
    ramp = min(duration_ms // 4, 1000)

    params = {
        'duration_ms':     duration_ms,
        'pulse_rate':      pf,
        'pulse_width':     pw,
        'alpha_freq':      freq,
        'alpha_amplitude': a_amp,
        'alpha_offset':    a_offset,
        'beta_freq':       freq,
        'beta_amplitude':  b_amp,
        'beta_offset':     b_offset,
        'ramp_ms':         ramp,
        'volume_boost':    0.01,
    }

    steps = []

    # Volume boost (additive on user's base level)
    steps.append({
        'operation': 'apply_linear_change',
        'axis': 'volume,volume-prostate',
        'params': {
            'start_value': '$volume_boost',
            'end_value':   '$volume_boost',
            'duration_ms': '$duration_ms',
            'ramp_in_ms':  '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'additive',
        }
    })

    # Pulse frequency (TCode 0-1)
    steps.append({
        'operation': 'apply_linear_change',
        'axis': 'pulse_frequency',
        'params': {
            'start_value': '$pulse_rate',
            'end_value':   '$pulse_rate',
            'duration_ms': '$duration_ms',
            'ramp_in_ms':  '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'overwrite',
        }
    })

    # Pulse width (TCode 0-1)
    steps.append({
        'operation': 'apply_linear_change',
        'axis': 'pulse_width',
        'params': {
            'start_value': '$pulse_width',
            'end_value':   '$pulse_width',
            'duration_ms': '$duration_ms',
            'ramp_in_ms':  '$ramp_ms',
            'ramp_out_ms': '$ramp_ms',
            'mode': 'overwrite',
        }
    })

    # Alpha modulation (centre from funscript, sinusoidal oscillation)
    steps.append({
        'operation': 'apply_modulation',
        'axis': 'alpha',
        'params': {
            'waveform':         'sin',
            'frequency':        '$alpha_freq',
            'amplitude':        '$alpha_amplitude',
            'max_level_offset': '$alpha_offset',
            'duration_ms':      '$duration_ms',
            'ramp_in_ms':       '$ramp_ms',
            'ramp_out_ms':      '$ramp_ms',
            'mode': 'additive',
        }
    })

    # Beta modulation (90° phase for oval motion)
    steps.append({
        'operation': 'apply_modulation',
        'axis': 'beta',
        'params': {
            'waveform':         'sin',
            'frequency':        '$beta_freq',
            'amplitude':        '$beta_amplitude',
            'max_level_offset': '$beta_offset',
            'phase':            90,
            'duration_ms':      '$duration_ms',
            'ramp_in_ms':       '$ramp_ms',
            'ramp_out_ms':      '$ramp_ms',
            'mode': 'additive',
        }
    })

    return {
        'name': name,
        'comment': comment,
        'definition': {
            'default_params': params,
            'steps': steps,
        }
    }


# =========================================================================
#  Generate all events
# =========================================================================

EVENT_TYPES = [
    # (group_name,   description,   duration_ms)
    ('good_slave',   'good_slave',  8000),
    ('reward',       'reward',      6000),
    ('higher_rate',  'higher_rate', 8000),
    ('edge',         'edge',        20000),
    ('spike',        'spike',       6000),
    ('tantalize',    'tantalize',   14000),
    ('tranquil',     'tranquil',    16000),
    ('push',         'push',        8000),
]

events = []
for group_name, desc, dur_ms in EVENT_TYPES:
    if group_name not in occurrences:
        print(f"WARNING: no SC events for '{group_name}'")
        continue
    selected = pick_3(occurrences[group_name])
    for i, (act, t_sec, video_ms) in enumerate(selected, 1):
        ev_name = f'clutch_{group_name}_{i}'
        comment = f'{desc} — {act} @ {t_sec:.0f}s (video {video_ms/1000:.0f}s)'
        events.append(make_event(ev_name, comment, video_ms, dur_ms))

print(f'Generated {len(events)} events')
for ev in events:
    pf = ev['definition']['default_params']['pulse_rate']
    pw = ev['definition']['default_params']['pulse_width']
    print(f'  {ev["name"]:<30} pf={pf:.3f}  pw={pw:.3f}')


# =========================================================================
#  YAML output
# =========================================================================

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

    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find where the old clutch events start
    lines = content.split('\n')
    clutch_start = None
    for i, line in enumerate(lines):
        if 'Clutch scene events' in line and line.strip().startswith('#'):
            clutch_start = i - 1
            break

    if clutch_start is None:
        print("ERROR: Could not find clutch section header")
        sys.exit(1)

    kept_lines = lines[:clutch_start]

    # Build new clutch section
    new_section = []
    new_section.append('')
    new_section.append('  # =========================================================================')
    new_section.append('  #  Clutch scene events (credit: AquariumParrot)')
    new_section.append('  #  Values read directly from the blended funscripts at each event timestamp.')
    new_section.append('  #  pulse_rate / pulse_width are TCode 0-1 (funscript pos / 100).')
    new_section.append('  # =========================================================================')
    new_section.append('')

    base_names = [
        ('good_slave',  'good_slave'),
        ('reward',      'reward'),
        ('higher_rate', 'higher_rate'),
        ('edge',        'edge'),
        ('spike',       'spike'),
        ('tantalize',   'tantalize'),
        ('tranquil',    'tranquil'),
        ('push',        'push'),
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

    print(f'\nWrote {len(events)} clutch scene events')
    print(f'Output: {yaml_file}')

    # Verify
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    defs = data.get('definitions', {})
    clutch_events = [k for k in defs if k.startswith('clutch_')]
    print(f'Clutch events in file: {len(clutch_events)}')
    for k in sorted(clutch_events):
        v = defs[k]
        has_alpha = any('alpha' in s.get('axis', '') for s in v.get('steps', []))
        has_beta = any('beta' in s.get('axis', '') for s in v.get('steps', []))
        motion = 'OK' if (has_alpha and has_beta) else 'MISSING MOTION!'
        print(f'  {k}: {motion}')


if __name__ == '__main__':
    main()
