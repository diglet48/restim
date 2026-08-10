"""
Generate positional axes from a 1D funscript.

A plain (1D) funscript only carries stroke position. To drive a 3-phase device
we synthesize alpha/beta. Results are cached on disk
(cache/<name>.<suffix>.funscript) so the expensive conversion runs only once
per script.

Pure of any Qt/UI-model dependency so it can be unit-tested in isolation. The
Qt model (script_mapping) only turns the returned dict into tree items.
"""
import logging
import re

from qt_ui.device_wizard.axes import AxisEnum
from funscript.funscript import Funscript, cache_dir
from funscript.funscript_conversion import convert_1d_to_2d

logger = logging.getLogger('restim.funscript.derived')

# suffix -> target axis
THREE_PHASE_AXES = {'alpha': AxisEnum.POSITION_ALPHA, 'beta': AxisEnum.POSITION_BETA}


def generate_derived_axes(script: Funscript, base_name: str) -> dict:
    """
    Map a 1D funscript to device axes: {AxisEnum: Funscript}.
    Uses the on-disk cache when available, otherwise converts and caches.
    Returns {} if the input is missing or conversion fails.
    """
    if script is None:
        return {}

    axis_map = THREE_PHASE_AXES

    cached = _load_cached(base_name, axis_map)
    if cached is not None:
        return cached

    try:
        scripts_by_suffix = _convert(script)
    except Exception:
        logger.exception('funscript conversion failed for %s', base_name)
        return {}

    _cache(base_name, scripts_by_suffix)
    return {axis_map[suffix]: fs for suffix, fs in scripts_by_suffix.items()}


def _convert(script: Funscript) -> dict:
    """Return {suffix: Funscript}. Raises on malformed input."""
    t, alpha, beta = convert_1d_to_2d(script)
    return {'alpha': Funscript(t, alpha), 'beta': Funscript(t, beta)}


def _cache_name(base_name: str, suffix: str) -> str:
    return re.sub(r'\.funscript$', f'.{suffix}.funscript', base_name)


def _load_cached(base_name: str, axis_map: dict):
    """Return {AxisEnum: Funscript} if ALL suffixes are cached, else None."""
    result = {}
    for suffix, axis in axis_map.items():
        path = cache_dir() / _cache_name(base_name, suffix)
        if not path.exists():
            return None
        result[axis] = Funscript.from_file(path)
    return result


def _cache(base_name: str, scripts_by_suffix: dict) -> None:
    for suffix, fs in scripts_by_suffix.items():
        try:
            fs.save_to_cache(_cache_name(base_name, suffix))
        except Exception:
            logger.exception('failed to cache %s.%s', base_name, suffix)
