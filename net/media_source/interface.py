from abc import ABC, abstractmethod
from enum import Enum

from PyQt5 import QtCore


class MediaConnectionState(Enum):
    NOT_CONNECTED = 0
    CONNECTED_BUT_NO_FILE_LOADED = 1
    CONNECTED_AND_PAUSED = 2
    CONNECTED_AND_PLAYING = 3

    def is_connected(self):
        return self in (
            MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED,
            MediaConnectionState.CONNECTED_AND_PAUSED,
            MediaConnectionState.CONNECTED_AND_PLAYING,
        )

    def is_file_loaded(self):
        return self in (
            MediaConnectionState.CONNECTED_AND_PAUSED,
            MediaConnectionState.CONNECTED_AND_PLAYING,
        )

    def is_playing(self):
        return self == MediaConnectionState.CONNECTED_AND_PLAYING


class MediaSourceInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def enable(self):
        """
        Start the connection loop
        """
        pass

    @abstractmethod
    def disable(self):
        """
        Stop the connection loop
        """
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        pass

    @abstractmethod
    def state(self) -> MediaConnectionState:
        pass

    def is_internal(self) -> bool:
        return False

    def is_connected(self) -> bool:
        return self.state() in (
            MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED,
            MediaConnectionState.CONNECTED_AND_PAUSED,
            MediaConnectionState.CONNECTED_AND_PLAYING,
        )

    def is_media_loaded(self) -> bool:
        return self.state() in (
            MediaConnectionState.CONNECTED_AND_PAUSED,
            MediaConnectionState.CONNECTED_AND_PLAYING,
        )

    def is_playing(self) -> bool:
        return self.state() == MediaConnectionState.CONNECTED_AND_PLAYING

    @abstractmethod
    def media_path(self) -> str:
        pass

    """
    Signal to emit whenever:
    - the connection status changes
    - the loaded file changes
    """
    connectionStatusChanged = QtCore.pyqtSignal()