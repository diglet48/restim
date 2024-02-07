from PyQt5.QtCore import QObject

from net.media_source.interface import MediaSourceInterface, MediaConnectionState


class _InternalMeta(type(QObject), type(MediaSourceInterface)):
    pass


class Internal(QObject, MediaSourceInterface, metaclass=_InternalMeta):
    def __init__(self):
        super(Internal, self).__init__()
        self._enabled = False

    def is_internal(self) -> bool:
        return True

    def enable(self):
        self._enabled = True
        self.connectionStatusChanged.emit()

    def disable(self):
        self._enabled = False

    def state(self) -> MediaConnectionState:
        return MediaConnectionState.CONNECTED_AND_PLAYING

    def is_enabled(self) -> bool:
        return True

    def map_timestamp(self, timestamp):
        # this should never be called because internal doesn't support any funscripts
        return timestamp

    def media_path(self) -> str:
        return ''
