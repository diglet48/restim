"""
YAML Event Loader — parses event_definitions.yml files and produces
EventDefinition objects that can be registered as patterns.

Looks for YAML files in:
  1. Built-in: ``<package>/event_definitions/`` directory
  2. User-defined: ``<cwd>/event_definitions/`` and any additional search paths

Provides ``load_all_yaml_events()`` as the single entry-point used at startup.
"""
from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger('restim.patterns.yaml_loader')

# Try to import yaml — optional dependency
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("PyYAML not installed — YAML event patterns will not be available. "
                   "Install with: pip install pyyaml")


from qt_ui.patterns.threephase.yaml_event_pattern import (
    EventDefinition, EventStep, NormalizationConfig, register_yaml_events
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pretty_name(raw_name: str) -> str:
    """Convert snake_case event name to Title Case display name.
    'mcb_edge_ce' → 'MCB Edge CE'
    """
    parts = raw_name.split('_')
    result = []
    for p in parts:
        if p.lower() in ('mcb', 'ce'):
            result.append(p.upper())
        else:
            result.append(p.capitalize())
    return ' '.join(result)


def _pick_category(event_name: str, groups: List[Dict]) -> str:
    """Determine category by matching event name prefix against group
    definitions."""
    for group in groups:
        prefix = group.get('prefix', '')
        if prefix and event_name.startswith(prefix):
            return group.get('name', prefix)
    # check for test_ prefix
    if event_name.startswith('test_'):
        for group in groups:
            if group.get('prefix', '') == 'test_':
                return group.get('name', 'Test')
    return groups[0].get('name', 'General') if groups else 'General'


def _resolve_param(value, defaults: Dict[str, Any]):
    """Resolve $-prefixed parameter references."""
    if isinstance(value, str) and value.startswith('$'):
        key = value[1:]
        return defaults.get(key, value)
    return value


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------

def parse_yaml_file(filepath: str) -> List[EventDefinition]:
    """Parse a single YAML event definitions file and return a list of
    ``EventDefinition`` objects."""
    if not HAS_YAML:
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to parse YAML file {filepath}: {e}")
        return []

    if not isinstance(data, dict):
        logger.warning(f"YAML file {filepath} does not contain a mapping at top level")
        return []

    # --- normalisation config ---
    norm_data = data.get('normalization', {})
    norm = NormalizationConfig(
        pulse_frequency_max=float(norm_data.get('pulse_frequency', {}).get('max', 120.0)),
        pulse_width_max=float(norm_data.get('pulse_width', {}).get('max', 100.0)),
        frequency_max=float(norm_data.get('frequency', {}).get('max', 1200.0)),
        volume_max=float(norm_data.get('volume', {}).get('max', 1.0)),
    )

    # --- groups ---
    groups = data.get('groups', [{'name': 'General', 'prefix': ''}])

    # --- definitions ---
    definitions_raw = data.get('definitions', {})
    result: List[EventDefinition] = []

    for event_name, event_data in definitions_raw.items():
        if not isinstance(event_data, dict):
            continue

        default_params = {}
        for k, v in event_data.get('default_params', {}).items():
            default_params[k] = v

        steps_raw = event_data.get('steps', [])
        steps: List[EventStep] = []

        for step_raw in steps_raw:
            if not isinstance(step_raw, dict):
                continue
            operation = step_raw.get('operation', '')
            axis_str = step_raw.get('axis', '')
            axes = [a.strip() for a in axis_str.split(',') if a.strip()]
            params_raw = step_raw.get('params', {})
            start_offset = int(step_raw.get('start_offset', 0))

            # Resolve $-references
            resolved_params = {}
            for pk, pv in params_raw.items():
                resolved_params[pk] = _resolve_param(pv, default_params)

            steps.append(EventStep(
                operation=operation,
                axes=axes,
                params=resolved_params,
                start_offset_ms=start_offset,
            ))

        category = _pick_category(event_name, groups)
        display = _pretty_name(event_name)

        result.append(EventDefinition(
            name=event_name,
            display_name=display,
            category=category,
            default_params=default_params,
            steps=steps,
            normalization=norm,
        ))

    logger.info(f"Parsed {len(result)} event definitions from {filepath}")
    return result


# ---------------------------------------------------------------------------
# Discovery and loading
# ---------------------------------------------------------------------------

def _search_paths() -> List[Path]:
    """Return list of directories to search for YAML event files."""
    paths = []
    # 1. Built-in: alongside this file
    builtin = Path(__file__).resolve().parent.parent.parent / 'event_definitions'
    paths.append(builtin)
    # 2. CWD
    paths.append(Path.cwd() / 'event_definitions')
    # 3. Same directory as the settings file (restim.ini)
    # This lets portable builds carry event YAML alongside the exe
    import sys
    if getattr(sys, 'frozen', False):
        paths.append(Path(sys.executable).parent / 'event_definitions')
    return paths


def load_all_yaml_events() -> List[EventDefinition]:
    """Discover and parse all YAML event definition files, returning a
    flat list of ``EventDefinition`` objects.  Also registers them in the
    pattern registry."""
    if not HAS_YAML:
        logger.info("PyYAML not available — skipping YAML event loading")
        return []

    all_defs: List[EventDefinition] = []
    seen_files: set = set()

    for search_dir in _search_paths():
        if not search_dir.is_dir():
            continue
        for yml_file in sorted(search_dir.glob('*.yml')):
            real = yml_file.resolve()
            if real in seen_files:
                continue
            seen_files.add(real)
            defs = parse_yaml_file(str(yml_file))
            all_defs.extend(defs)
        for yaml_file in sorted(search_dir.glob('*.yaml')):
            real = yaml_file.resolve()
            if real in seen_files:
                continue
            seen_files.add(real)
            defs = parse_yaml_file(str(yaml_file))
            all_defs.extend(defs)

    if all_defs:
        register_yaml_events(all_defs)
        logger.info(f"Loaded {len(all_defs)} YAML event patterns total")
    else:
        logger.info("No YAML event definition files found")

    return all_defs
