"""
HereSphere funscript resolution (sidecar to collect_funscripts).

Resolve the funscript for a media file by querying an external HereSphere
video-server API (GET {url}/api/scene/{id}). Disabled by default; enable and
configure the URL + path mappings via settings (restim.ini) or the GUI dialog
(qt_ui/heresphere_api_dialog.py).

When the media name starts with a numeric scene id and the API is enabled, we
ask the server for the funscript path, remap the server-side path to a
locally-mounted path, and return it. Any failure degrades gracefully to [] so
the normal local filesystem detection still runs.

Returns plain pathlib.Path objects (not Resource) to avoid a circular import
with collect_funscripts; the caller wraps them.
"""
import logging
import os
import pathlib

from qt_ui import settings

logger = logging.getLogger('restim.funscript.heresphere')


def _scene_id_from_media(media: str):
    """Extract a leading numeric scene id from a media filename, else None."""
    basename = os.path.basename(media)
    token = basename.split(' - ')[0].strip()
    return token if token.isdigit() else None


def _apply_path_mappings(path: str, mappings: list) -> str:
    """Apply "server_prefix=>local_prefix" mappings (each applied at most once)."""
    for mapping in mappings:
        if '=>' not in mapping:
            continue
        prefix, replacement = (part.strip() for part in mapping.split('=>', 1))
        if prefix and path.startswith(prefix):
            return replacement + path[len(prefix):]
    return path


# Selection state for the current scene: a scene may expose several funscripts;
# we keep the full list and which one is selected so the UI can switch between
# them without re-querying the API on every switch.
_state = {'scene_id': None, 'paths': [], 'index': 0}


def _fetch_funscripts(scene_id: str) -> list:
    """Query the API and return ALL locally-available funscripts for the scene."""
    base_url = settings.heresphere_api_url.get().strip().rstrip('/')
    if not base_url:
        return []
    try:
        import requests  # imported lazily so restim runs without it when disabled
    except ImportError:
        logger.warning('HereSphere API enabled but the "requests" package is not installed')
        return []

    url = f'{base_url}/api/scene/{scene_id}'
    timeout = settings.heresphere_api_timeout.get()
    mappings = settings.heresphere_api_path_mappings.get()

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        scene_data = resp.json()
    except Exception as e:  # network error, non-200, malformed JSON
        logger.warning('HereSphere API request failed (%s): %s', url, e)
        return []

    paths = []
    for file in scene_data.get('file', []):
        filename = file.get('filename', '')
        if not filename.endswith('.funscript'):
            continue
        local_dir = _apply_path_mappings(file.get('path', ''), mappings)
        full_path = os.path.join(local_dir, filename)
        if not os.path.exists(full_path):
            logger.warning('HereSphere API funscript not found locally: %s', full_path)
            continue
        paths.append(pathlib.Path(full_path))
    return paths


def _reset():
    _state['scene_id'] = None
    _state['paths'] = []
    _state['index'] = 0


def resolve(media: str) -> list:
    """
    Return [pathlib.Path] for the currently-selected HereSphere funscript, or []
    if disabled / no scene id / none available. On a new scene, (re)fetches the
    full list and selects the first; on the same scene, keeps the current
    selection (no network call). Never raises.
    """
    if not settings.heresphere_api_enabled.get():
        _reset()
        return []

    scene_id = _scene_id_from_media(media)
    if scene_id is None:
        _reset()
        return []

    if scene_id != _state['scene_id']:
        paths = _fetch_funscripts(scene_id)
        _state['scene_id'] = scene_id
        _state['paths'] = paths
        _state['index'] = 0
        if len(paths) > 1:
            logger.info('HereSphere API: %d funscripts for scene %s', len(paths), scene_id)

    if not _state['paths']:
        return []
    index = min(_state['index'], len(_state['paths']) - 1)
    selected = _state['paths'][index]
    logger.info('HereSphere API selected funscript (%d/%d): %s',
                index + 1, len(_state['paths']), selected)
    return [selected]


# ── selection API for the UI ──────────────────────────────────────────────
def available_count() -> int:
    return len(_state['paths'])


def current_index() -> int:
    return _state['index']


def funscript_names() -> list:
    """Basenames of the funscripts available for the current scene (for a combo)."""
    return [p.name for p in _state['paths']]


def select(index: int) -> bool:
    """Select funscript by index. Returns True if the selection actually changed."""
    if 0 <= index < len(_state['paths']) and index != _state['index']:
        _state['index'] = index
        return True
    return False


def select_next() -> bool:
    """Cycle to the next funscript. Returns True if there is more than one."""
    n = len(_state['paths'])
    if n <= 1:
        return False
    _state['index'] = (_state['index'] + 1) % n
    return True
