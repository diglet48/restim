"""
Generate MCB (Mistress & the Control Box) scene events from funscript data.

Parses the SuperCollider script to get event timestamps, then extracts
the actual funscript keyframes over each event's duration.  No sampling,
no averaging — the funscript IS the data.

MCB SC sections:
  ~scriptIntro  (line 969)  — calibration + warmup
  ~scriptCh1    (line 1369) — T&D training + cock enslavement + obey
  ~scriptCh2    (line 1940) — milking + mind control
  ~scriptCh3    (line 2711) — final stroking + edge + orgasm

SC event types we care about:
  ~goodBoy:  pulse freq=27, width=0.5, duration=5s
  ~submit:   pulse freq=20, width=0.5, duration=5s
  ~edge:     pulse freq=100, duration=~30s (runs until ~rest)
  ~edgeCE:   pulse freq=160, duration=~varies (runs until ~restCE)
  ~obey:     pulse freq=27, duration=~varies (runs until ~obeyStop)
"""

import json, re, os, sys, math
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────
SC_FILE = os.path.join(os.path.dirname(__file__), 'mistress_and_box.scd')
FUNSCRIPT_DIR = r'D:\downloads\01.estim\mistress and control box'
FUNSCRIPT_BASE = 'MistressAndControlBox'

# ── Load funscripts ───────────────────────────────────────────────────

def load_funscript(axis):
    fp = os.path.join(FUNSCRIPT_DIR, f'{FUNSCRIPT_BASE}.{axis}.funscript')
    data = json.load(open(fp))
    acts = data['actions']
    ts = np.array([a['at'] for a in acts], dtype=float)
    ps = np.array([a['pos'] for a in acts], dtype=float)
    return ts, ps, acts

pf_ts, pf_ps, pf_acts = load_funscript('pulse_frequency')
pw_ts, pw_ps, pw_acts = load_funscript('pulse_width')
vol_ts, vol_ps, vol_acts = load_funscript('volume')
alpha_ts, alpha_ps, alpha_acts = load_funscript('alpha')
beta_ts, beta_ps, beta_acts = load_funscript('beta')

ALL_AXES = {
    'pulse_frequency': (pf_ts, pf_ps, pf_acts),
    'pulse_width': (pw_ts, pw_ps, pw_acts),
    'volume': (vol_ts, vol_ps, vol_acts),
    'alpha': (alpha_ts, alpha_ps, alpha_acts),
    'beta': (beta_ts, beta_ps, beta_acts),
}


def interp(ts, ps, t):
    return float(np.interp(t, ts, ps))


def convert_pos(pos, axis):
    """Convert funscript pos (0-100) to the value the runtime expects.
    alpha/beta: -1..+1   (50 = centre)
    everything else: 0..1 TCode  (pos/100)
    """
    if axis in ('alpha', 'beta'):
        return (pos - 50.0) / 50.0
    return pos / 100.0


def extract_keyframes(acts, start_ms, end_ms, axis):
    """Extract funscript actions within [start_ms, end_ms], adding
    interpolated boundary points.  Returns list of [relative_ms, value]
    with values already converted to TCode."""
    ts = np.array([a['at'] for a in acts], dtype=float)
    ps = np.array([a['pos'] for a in acts], dtype=float)

    # Interpolated values at boundaries
    start_pos = float(np.interp(start_ms, ts, ps))
    end_pos = float(np.interp(end_ms, ts, ps))

    keyframes = [(0, round(convert_pos(start_pos, axis), 4))]

    for a in acts:
        t = a['at']
        if t <= start_ms or t >= end_ms:
            continue
        rel_t = round(t - start_ms, 1)
        val = round(convert_pos(a['pos'], axis), 4)
        keyframes.append((rel_t, val))

    dur = round(end_ms - start_ms, 1)
    keyframes.append((dur, round(convert_pos(end_pos, axis), 4)))

    return keyframes


# ── Parse SC events ──────────────────────────────────────────────────

def parse_sc_section(text, section_var):
    """Parse a ~scriptXxx = [...] section from the SC file.
    Returns list of (time_sec, label, code_block)."""
    # Find the section start
    pattern = re.escape(section_var) + r'\s*=\s*\['
    m = re.search(pattern, text)
    if not m:
        print(f"WARNING: Could not find {section_var}")
        return []

    start_pos = m.end()
    # Find the matching close bracket
    depth = 1
    pos = start_pos
    while pos < len(text) and depth > 0:
        if text[pos] == '[':
            depth += 1
        elif text[pos] == ']':
            depth -= 1
        pos += 1
    section_text = text[start_pos:pos-1]

    # Parse events: [MM, SS + (FF/30), { ... }]
    event_pattern = r'\[(\d+),\s*(\d+)\s*(?:\+\s*\((\d+)/30\))?\s*,\s*\{(.*?)\}\]'
    events = []
    for m in re.finditer(event_pattern, section_text, re.DOTALL):
        mins = int(m.group(1))
        secs = int(m.group(2))
        frames = int(m.group(3)) if m.group(3) else 0
        code = m.group(4)

        t_sec = mins * 60 + secs + frames / 30.0

        # Extract label from postln
        label_m = re.search(r'"([^"]+)"\.postln', code)
        label = label_m.group(1) if label_m else ''

        # Detect event type from code
        event_type = 'other'
        if '~goodBoy' in code and 'goodBoy =' not in code:
            event_type = 'goodboy'
        elif '~submit' in code and 'submit =' not in code and 'submit =' not in code:
            event_type = 'submit'
        elif '~edge.value' in code or '~edge.(release' in code:
            event_type = 'edge'
        elif '~edgeCE' in code and 'edgeCE =' not in code:
            event_type = 'edge_ce'
        elif '~rest.value' in code or '~restCE' in code and 'restCE =' not in code:
            event_type = 'rest'
        elif '~obey.value' in code or '~obey.(release' in code:
            event_type = 'obey'
        elif '~obeyStop' in code and 'obeyStop =' not in code:
            event_type = 'obey_stop'

        events.append({
            'time_sec': t_sec,
            'label': label,
            'type': event_type,
            'code': code.strip(),
        })

    return events


# ── Grid-search section offsets ──────────────────────────────────────

# Known pulse freq values for correlation
TYPE_FREQ = {
    'goodboy': 27,  # pulse freq drops to 27
    'edge': 100,    # pulse freq jumps to 100
    'edge_ce': 100, # after CE freq is 160, but funscript clips at 100
    'obey': 27,     # pulse freq drops to 27
}


def score_offset(events, offset_ms, delay_ms=2000):
    """Score by checking pulse_freq funscript at event+delay vs expected."""
    total_err = 0
    n = 0
    for ev in events:
        if ev['type'] not in TYPE_FREQ:
            continue
        expected = TYPE_FREQ[ev['type']]
        video_ms = offset_ms + ev['time_sec'] * 1000 + delay_ms
        if video_ms < pf_ts[0] or video_ms > pf_ts[-1]:
            total_err += 50
            n += 1
            continue
        observed = interp(pf_ts, pf_ps, video_ms)
        total_err += abs(observed - expected)
        n += 1
    return total_err / max(n, 1) if n > 0 else 999


def grid_search(events, lo_ms, hi_ms, step_ms=500):
    best_offset = lo_ms
    best_score = 999
    for off in np.arange(lo_ms, hi_ms, step_ms):
        s = score_offset(events, off)
        if s < best_score:
            best_score = s
            best_offset = off
    # Refine
    for off in np.arange(best_offset - step_ms, best_offset + step_ms, 50):
        s = score_offset(events, off)
        if s < best_score:
            best_score = s
            best_offset = off
    return int(best_offset), best_score


# ── Identify meaningful scenes from SC events ────────────────────────

def identify_scenes(events, section_name, offset_ms):
    """Walk through events and identify scenes with start/end times.
    A scene starts at an interesting event and ends at the next event."""
    scenes = []
    for i, ev in enumerate(events):
        if ev['type'] in ('other', 'rest', 'obey_stop'):
            continue

        start_sec = ev['time_sec']
        start_ms = offset_ms + start_sec * 1000

        # Find end: next event's start, or +5s for goodboy/submit (fixed 5s)
        if ev['type'] in ('goodboy', 'submit'):
            duration_s = 5.0
        elif i + 1 < len(events):
            duration_s = events[i + 1]['time_sec'] - start_sec
            duration_s = min(duration_s, 30.0)  # cap at 30s
        else:
            duration_s = 10.0

        end_ms = start_ms + duration_s * 1000

        # Make sure we're in funscript range
        if start_ms < pf_ts[0] or end_ms > pf_ts[-1] + 5000:
            continue

        scenes.append({
            'section': section_name,
            'type': ev['type'],
            'label': ev['label'],
            'start_ms': start_ms,
            'end_ms': end_ms,
            'duration_ms': round(end_ms - start_ms),
        })

    return scenes


# ── Build YAML event from scene ──────────────────────────────────────

def build_event(name, comment, scene, ramp_ms=500):
    """Build a YAML event dict with keyframe steps from funscript data."""
    start_ms = scene['start_ms']
    end_ms = scene['end_ms']
    duration_ms = scene['duration_ms']

    steps = []

    # For each axis, extract keyframes
    for axis_name, (ts, ps, acts) in ALL_AXES.items():
        kf = extract_keyframes(acts, start_ms, end_ms, axis_name)

        # Determine mode
        if axis_name == 'volume':
            mode = 'additive'
        elif axis_name in ('alpha', 'beta'):
            mode = 'additive'
        else:
            mode = 'overwrite'

        # Map YAML axis names
        if axis_name == 'alpha':
            yaml_axis = 'alpha'
        elif axis_name == 'beta':
            yaml_axis = 'beta'
        else:
            yaml_axis = axis_name

        steps.append({
            'operation': 'apply_keyframes',
            'axis': yaml_axis,
            'params': {
                'keyframes': kf,
                'duration_ms': duration_ms,
                'ramp_in_ms': ramp_ms,
                'ramp_out_ms': ramp_ms,
                'mode': mode,
            }
        })

    return {
        'name': name,
        'comment': comment,
        'definition': {
            'default_params': {
                'duration_ms': duration_ms,
                'ramp_ms': ramp_ms,
            },
            'steps': steps,
        }
    }


# ── Format YAML ──────────────────────────────────────────────────────

def format_keyframes(kf):
    """Format keyframes list for YAML output."""
    parts = []
    for t, v in kf:
        # Format numbers cleanly
        t_str = f'{t:.0f}' if t == int(t) else f'{t:.1f}'
        # Format value: trim trailing zeros but keep at least one decimal
        v_str = f'{v:.4f}'.rstrip('0').rstrip('.')
        if '.' not in v_str:
            v_str += '.0'
        parts.append(f'[{t_str}, {v_str}]')
    return '[' + ', '.join(parts) + ']'


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
            if pk == 'keyframes':
                lines.append(f'          keyframes: {format_keyframes(pv)}')
            else:
                lines.append(f'          {pk}: {pv}')
        lines.append(f'')  # blank line between steps

    return '\n'.join(lines)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    # Read SC file
    with open(SC_FILE, 'r') as f:
        sc_text = f.read()

    # Parse each section
    intro_events = parse_sc_section(sc_text, '~scriptIntro')
    ch1_events = parse_sc_section(sc_text, '~scriptCh1')
    ch2_events = parse_sc_section(sc_text, '~scriptCh2')
    ch3_events = parse_sc_section(sc_text, '~scriptCh3')

    print(f"Parsed: intro={len(intro_events)}, ch1={len(ch1_events)}, ch2={len(ch2_events)}, ch3={len(ch3_events)} events")

    # Show event types found
    for name, evts in [('intro', intro_events), ('ch1', ch1_events), ('ch2', ch2_events), ('ch3', ch3_events)]:
        types = {}
        for e in evts:
            types[e['type']] = types.get(e['type'], 0) + 1
        print(f"  {name}: {types}")

    # Grid search for offsets
    print("\n=== Grid searching section offsets ===")

    off_intro, sc_intro = grid_search(intro_events, 0, 120000)
    print(f"Intro: offset={off_intro}ms ({off_intro/1000:.1f}s), score={sc_intro:.1f}")

    # Ch1 starts after intro (~7min mark in video)
    # Intro last event at ~6:44 relative, so video time ~6:44 + intro_offset
    intro_end_est = off_intro + 420000
    off_ch1, sc_ch1 = grid_search(ch1_events, intro_end_est - 60000, intro_end_est + 120000)
    print(f"Ch1:   offset={off_ch1}ms ({off_ch1/1000:.1f}s = {off_ch1/60000:.1f}min), score={sc_ch1:.1f}")

    # Ch2 starts after ch1 (~17:50 relative + ch1_offset)
    ch1_end_est = off_ch1 + 1070000
    off_ch2, sc_ch2 = grid_search(ch2_events, ch1_end_est - 60000, ch1_end_est + 120000)
    print(f"Ch2:   offset={off_ch2}ms ({off_ch2/1000:.1f}s = {off_ch2/60000:.1f}min), score={sc_ch2:.1f}")

    # Ch3 starts after ch2
    ch2_end_est = off_ch2 + 500000
    off_ch3, sc_ch3 = grid_search(ch3_events, ch2_end_est - 60000, ch2_end_est + 120000)
    print(f"Ch3:   offset={off_ch3}ms ({off_ch3/1000:.1f}s = {off_ch3/60000:.1f}min), score={sc_ch3:.1f}")

    # Identify scenes from all sections
    all_scenes = []
    all_scenes.extend(identify_scenes(intro_events, 'intro', off_intro))
    all_scenes.extend(identify_scenes(ch1_events, 'ch1', off_ch1))
    all_scenes.extend(identify_scenes(ch2_events, 'ch2', off_ch2))
    all_scenes.extend(identify_scenes(ch3_events, 'ch3', off_ch3))

    print(f"\n=== Found {len(all_scenes)} scenes ===")
    for s in all_scenes:
        dur_s = s['duration_ms'] / 1000
        vid_s = s['start_ms'] / 1000
        print(f"  {s['section']:<6} {s['type']:<10} {s['label']:<40} @{vid_s:7.1f}s  dur={dur_s:5.1f}s")

    # Group by type and pick representative scenes
    from collections import defaultdict
    by_type = defaultdict(list)
    for s in all_scenes:
        by_type[s['type']].append(s)

    print(f"\n=== Scenes by type ===")
    for t in sorted(by_type.keys()):
        print(f"  {t}: {len(by_type[t])} scenes")

    # Generate events
    events = []
    event_counter = {}

    for scene_type, type_scenes in sorted(by_type.items()):
        # For each type, generate events from the actual scene data
        for i, scene in enumerate(type_scenes, 1):
            event_name = f'mcb_{scene_type}_{i}'
            comment = f'{scene["section"]}: {scene["label"]} ({scene["duration_ms"]/1000:.1f}s)'
            ev = build_event(event_name, comment, scene, ramp_ms=500)
            events.append(ev)

    print(f"\n=== Generated {len(events)} events ===")
    for ev in events:
        print(f"  {ev['name']}: {ev['comment']}")

    # Write to YAML section
    yaml_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'event_definitions', 'edger477_events.yml')

    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the MCB section boundaries
    lines = content.split('\n')
    mcb_start = None
    mcb_end = None  # where clutch section starts (or end of file)

    # Find first MCB or definitions section
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ==') and i > 5:
            # Check if this is inside definitions:
            mcb_start = i
            break
        if 'mcb_edge' in stripped and ':' in stripped:
            # First MCB event — go back to find header
            for j in range(i, max(0, i-10), -1):
                if lines[j].strip().startswith('# ==') or lines[j].strip() == '':
                    mcb_start = j
                    break
            if mcb_start is None:
                mcb_start = i
            break

    if mcb_start is None:
        print("ERROR: Could not find MCB section start")
        sys.exit(1)

    # Find the end of MCB section (start of Clutch section)
    for i in range(mcb_start + 1, len(lines)):
        stripped = lines[i].strip()
        if 'Clutch' in stripped and stripped.startswith('#'):
            # Go back to the separator line
            mcb_end = i
            for j in range(i, max(0, i-3), -1):
                if lines[j].strip().startswith('# =='):
                    mcb_end = j
                    break
            break

    if mcb_end is None:
        mcb_end = len(lines)

    print(f"\nMCB section: lines {mcb_start}-{mcb_end}")

    # Build new MCB section
    new_section = []
    new_section.append('  # =========================================================================')
    new_section.append('  #  Mistress & Control Box events (credit: AquariumParrot)')
    new_section.append('  #  Funscript keyframes extracted from SuperCollider script timestamps.')
    new_section.append('  #  Each event replays the actual funscript data for its duration.')
    new_section.append('  # =========================================================================')
    new_section.append('')

    # Group events by type for nice formatting
    current_type = None
    for ev in events:
        ev_type = ev['name'].rsplit('_', 1)[0]  # mcb_edge, mcb_goodboy, etc.
        if ev_type != current_type:
            current_type = ev_type
            new_section.append(f'  # --- {current_type} ---')
            new_section.append('')
        new_section.append(emit_yaml_event(ev))

    # Replace MCB section
    kept_before = lines[:mcb_start]
    kept_after = lines[mcb_end:]

    output = '\n'.join(kept_before) + '\n' + '\n'.join(new_section) + '\n' + '\n'.join(kept_after)

    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nWrote {len(events)} MCB events to {yaml_file}")


if __name__ == '__main__':
    main()
