import json
import logging
import time

from PySide6 import QtCore
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from net.media_source.mediasource import MediaSource, MediaStatusReport, MediaConnectionState
from qt_ui import settings

logger = logging.getLogger('restim.media.OFS')


class OFS(MediaSource):
    def __init__(self, parent):
        super(OFS, self).__init__(parent)

        self._enabled = False
        self.playback_speed = 1
        self.filename = ''
        self.playing = False
        self.media_duration = None
        self.claimed_media_position = 0

        self.websocket : QWebSocket = None

        self.reconnect_timer = QtCore.QTimer(self)
        self.reconnect_timer.timeout.connect(self.reconnect_timeout)
        self.reconnect_timer.setSingleShot(False)
        self.reconnect_timer.setInterval(int(2000))

    def open_connection(self):
        logger.info('opening websocket')
        self.websocket = QWebSocket()
        self.websocket.open(QUrl.fromUserInput(settings.media_sync_ofs_address.get()))

        self.websocket.connected.connect(self.connected)
        self.websocket.errorOccurred.connect(self.error)
        self.websocket.textMessageReceived.connect(self.textMessageReceived)

    def connected(self):
        self.set_state(
            MediaStatusReport(
                time.time(),
                "",
                MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED,
            )
        )

    def reconnect_timeout(self):
        if self._enabled and self.websocket.state() == QAbstractSocket.UnconnectedState:
            self.open_connection()

    def error(self):
        logger.warning('error: %s', self.websocket.errorString())
        self.set_state(
            MediaStatusReport(
                time.time(),
                "",
                MediaConnectionState.NOT_CONNECTED,
            )
        )

    def textMessageReceived(self, text):
        msg = json.loads(text)
        if 'connected' in msg.keys():
            version = msg['connected']
            logger.info(f'connected to {version}')
        else:
            type = msg['type']
            name = msg['name']
            data = msg['data']

            if type == 'event':
                # print(name, data)
                if name == 'project_change':
                    self.handle_project_change(data)
                elif name == 'media_change':
                    self.handle_media_change(data)
                elif name == 'playbackspeed_change':
                    self.handle_playbackspeed_change(data)
                elif name == 'play_change':
                    self.handle_play_change(data)
                elif name == 'duration_change':
                    self.handle_duration_change(data)
                elif name == 'time_change':
                    self.handle_time_change(data)
                elif name == 'funscript_change':
                    self.handle_funscript_change(data)
                else:
                    logger.warning(f"unknown event: {name}")
            else:
                logger.warning(f"unknown type: {type}")


            self.set_state(MediaStatusReport(
                time.time(),
                "",
                MediaConnectionState.CONNECTED_AND_PLAYING if self.playing else MediaConnectionState.CONNECTED_AND_PAUSED,
                self.filename,
                self.playback_speed,
                self.claimed_media_position,
            ))

    def handle_project_change(self, data):
        """
        {} empty?
        """
        # print('project change', data)
        pass

    def handle_playbackspeed_change(self, data):
        """
        {'speed': 1.0}
        """
        self.playback_speed = data['speed']
        # print('speed change', data)

    def handle_media_change(self, data):
        """
        {'path': 'C:/path/to/file/MistressAndControlBox.mp4'}
        """
        path = data['path']
        self.filename = path
        # print('media change', path)

    def handle_play_change(self, data):
        """
        {'playing': False}
        """
        self.playing = data['playing']
        # print('play change', data)

    def handle_duration_change(self, data):
        """
        {'duration': 3213.58935546875}
        """
        self.media_duration = data['duration']
        # print('duration change', data)

    def handle_time_change(self, data):
        """
        {'time': 1.0}
        """
        self.claimed_media_position = data['time']
        # print('time change', data)

    def handle_funscript_change(self, data):
        """
        {'funscript': {'actions': [], ...}, 'name': 'MistressAndControlBox'}
        """
        fs = data['funscript']
        name = data['name']
        # print('funscript change', name, len(fs['actions']))

    def enable(self):
        self._enabled = True
        self.reconnect_timer.start()
        self.open_connection()

    def disable(self):
        self._enabled = False
        if self.websocket is not None:
            self.websocket.close()
            self.websocket = None

            self.playback_speed = 1
        self.filename = ''
        self.playing = False
        self.media_duration = None
        self.claimed_media_position = 0
        self.reconnect_timer.stop()

    def is_enabled(self) -> bool:
        return self._enabled

