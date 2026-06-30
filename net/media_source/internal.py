import time

from PySide6.QtCore import QObject

from net.media_source.interface import MediaSourceInterface, MediaConnectionState


class _InternalMeta(type(QObject), type(MediaSourceInterface)):
    pass


class Internal(QObject, MediaSourceInterface, metaclass=_InternalMeta):
    # Internal has no real media file. Report PLAYING only while something has
    # been driving the output recently — external TCode traffic OR the built-in
    # pattern generator (see mainwindow wiring). Otherwise the mute guard in the
    # audio-gen algorithm keeps the carrier silent. Without this, selecting
    # Internal + pressing Start with nothing driving produced a steady carrier
    # tone on the output.
    ACTIVITY_TIMEOUT_S = 2.0

    def __init__(self):
        super(Internal, self).__init__()
        self._enabled = False
        self._last_activity_time = 0.0

    def notify_activity(self, *_):
        """Mark recent TCode / API / pattern activity. Accepts and ignores any
        args so it can be hooked directly to Qt signals that carry payloads."""
        self._last_activity_time = time.time()

    def is_internal(self) -> bool:
        return True

    def enable(self):
        self._enabled = True
        self.connectionStatusChanged.emit()

    def disable(self):
        self._enabled = False

    def state(self) -> MediaConnectionState:
        if time.time() - self._last_activity_time < self.ACTIVITY_TIMEOUT_S:
            return MediaConnectionState.CONNECTED_AND_PLAYING
        return MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED

    def is_enabled(self) -> bool:
        return True

    def map_timestamp(self, timestamp):
        # this should never be called because internal doesn't support any funscripts
        return timestamp

    def media_path(self) -> str:
        return ''
