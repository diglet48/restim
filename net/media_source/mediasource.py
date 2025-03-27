import copy
from dataclasses import dataclass
import logging

from PySide6.QtCore import QObject

from net.media_source.interface import MediaSourceInterface, MediaConnectionState

logger = logging.getLogger('restim.media')


@dataclass
class MediaState:
    connectionState: MediaConnectionState
    filePath: str = ''
    cursor: float = -1   # when paused, the media cursor. When playing, the time at which media was started.
    media_play_timestamp: float = -1


@dataclass
class MediaStatusReport:
    timestamp: float    # timestamp the report was generated
    errorString: str = ''
    connectionState: MediaConnectionState = MediaConnectionState.NOT_CONNECTED
    filePath: str = ''
    playbackRate: float = 1
    claimed_media_position: float = -1   # seconds since start of the file


class A(type(QObject), type(MediaSourceInterface)):
    pass


class MediaSource(QObject, MediaSourceInterface, metaclass=A):
    def __init__(self, parent):
        super(MediaSource, self).__init__(parent)

        self.last_state = MediaState(MediaConnectionState.NOT_CONNECTED)

    def state(self) -> MediaConnectionState:
        return self.last_state.connectionState

    def pre_update(self, last_state, state):
        return state

    def set_state(self, report: MediaStatusReport):
        # report = self.pre_update(self.last_state, report)
        new_state = copy.copy(self.last_state)

        # only support playback rate == 1
        if report.playbackRate != 1:
            if report.connectionState.is_playing():
                report.connectionState = MediaConnectionState.CONNECTED_AND_PAUSED

        # initial connect
        if self.last_state.connectionState == MediaConnectionState.NOT_CONNECTED:
            if report.connectionState.is_connected():
                logger.info('connected')
                new_state.connectionState = report.connectionState
                new_state.filePath = report.filePath
                new_state.cursor = report.claimed_media_position
                new_state.media_play_timestamp = report.timestamp

                if report.connectionState.is_playing():
                    logger.info('play-on-connect')
                    new_state.media_play_timestamp = report.timestamp
                    new_state.cursor = report.claimed_media_position

        # any disconnect
        elif not report.connectionState.is_connected():
            logger.info('disconnected')
            new_state.connectionState = MediaConnectionState.NOT_CONNECTED
            new_state.filePath = ''

        elif self.last_state.connectionState == MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED:
            if report.connectionState.is_file_loaded():
                logger.info('file loaded')
                new_state.filePath = report.filePath
                new_state.connectionState = report.connectionState
                new_state.cursor = report.claimed_media_position
                new_state.media_play_timestamp = report.timestamp

                if report.connectionState.is_playing():
                    logger.info('play-on-load')

        elif self.last_state.connectionState == MediaConnectionState.CONNECTED_AND_PAUSED:
            if self.last_state.connectionState.is_file_loaded():
                if report.connectionState.is_file_loaded():
                    if self.last_state.filePath != report.filePath:
                        logger.info('loaded file changed')
                        new_state.filePath = report.filePath

            if report.connectionState.is_playing():
                logger.info('play')
                new_state.connectionState = report.connectionState
                new_state.media_play_timestamp = report.timestamp
                new_state.cursor = report.claimed_media_position
            elif not report.connectionState.is_file_loaded():
                logger.info('file unload')
                new_state.connectionState = report.connectionState
                new_state.filePath = ''
            else:
                # seek
                new_state.cursor = report.claimed_media_position

        elif self.last_state.connectionState == MediaConnectionState.CONNECTED_AND_PLAYING:
            if self.last_state.connectionState.is_file_loaded():
                if report.connectionState.is_file_loaded():
                    if self.last_state.filePath != report.filePath:
                        logger.info('loaded file changed')
                        new_state.filePath = report.filePath

            # play to unloaded
            if report.connectionState == MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED:
                logger.info('file unload')
                new_state.connectionState = report.connectionState
                new_state.filePath = ''
            # play to pause
            elif report.connectionState == MediaConnectionState.CONNECTED_AND_PAUSED:
                new_state.connectionState = MediaConnectionState.CONNECTED_AND_PAUSED
                new_state.cursor = report.claimed_media_position
                logger.info('pause')
            # still playing
            else:
                # equation: report.timestamp - status.media_play_timestamp = report.claimed_media_position - self.state.cursor
                drift = (report.timestamp - self.last_state.media_play_timestamp) - (
                            report.claimed_media_position - self.last_state.cursor)
                # logger.debug('still playing, drift=%f', drift)

                if abs(drift) > 2.0:
                    new_state.media_play_timestamp = report.timestamp
                    new_state.connectionState = MediaConnectionState.CONNECTED_AND_PLAYING
                    new_state.cursor = report.claimed_media_position
                    logger.info(f'drift too much ({drift}), re-sync')

        prev_state = self.last_state
        self.last_state = new_state
        if (prev_state.connectionState != new_state.connectionState) or \
                (prev_state.filePath != new_state.filePath):
            self.connectionStatusChanged.emit()

    def map_timestamp(self, timestamp):
        if self.is_playing():
            adj_timestamp = timestamp - self.last_state.media_play_timestamp + self.last_state.cursor
            return adj_timestamp
        else:
            return timestamp - timestamp + self.last_state.cursor

    def media_path(self) -> str:
        return self.last_state.filePath

