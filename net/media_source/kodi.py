import json
import logging
import time

from PySide6 import QtCore
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from net.media_source.mediasource import MediaSource, MediaStatusReport, MediaConnectionState
from qt_ui import settings

logger = logging.getLogger('restim.media.kodi')


GET_PLAYERS = "query_players"
GET_FILE = "query_file"
GET_TIME = "query_time"

class Kodi(MediaSource):
    def __init__(self, parent):
        super(Kodi, self).__init__(parent)

        self._enabled = False
        self.playlist_id = None
        self.filename = None
        self.media_duration = None  # The length of the video according to QMediaPlayer
        self.media_player = None

        self.websocket : QWebSocket = None
        self.player_id = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setSingleShot(False)
        self.timer.setInterval(int(2000))

        self.reconnect_timer = QtCore.QTimer(self)
        self.reconnect_timer.timeout.connect(self.reconnect_timeout)
        self.reconnect_timer.setSingleShot(False)
        self.reconnect_timer.setInterval(int(2000))

    def open_connection(self):
        logger.info('opening websocket')
        self.websocket = QWebSocket()
        self.websocket.open(QUrl.fromUserInput(settings.media_sync_kodi_address.get()))

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
        self.timeout()

    def timeout(self):
        if self._enabled and self.websocket is not None:
            if self.player_id is None:
                self.query_players()
            else:
                self.query_file(self.player_id)
                self.query_time(self.player_id)

    def reconnect_timeout(self):
        if self._enabled and self.websocket.state() == QAbstractSocket.UnconnectedState:
            self.open_connection()

    def query_players(self):
        cmd = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": GET_PLAYERS}
        self.websocket.sendTextMessage(json.dumps(cmd))

    def query_file(self, playerid: int):
        cmd = {"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["file", "title"], "playerid":  playerid}, "id": GET_FILE}
        self.websocket.sendTextMessage(json.dumps(cmd))

    def query_time(self, playerid):
        # Player.Property.Value
        cmd = {"jsonrpc": "2.0", "method": "Player.GetProperties", "params": { "properties": ["time", "speed"], "playerid": playerid }, "id": GET_TIME}
        self.websocket.sendTextMessage(json.dumps(cmd))

    def error(self):
        logger.warning('error: %s', self.websocket.errorString())
        self.set_state(
            MediaStatusReport(
                time.time(),
                "",
                MediaConnectionState.NOT_CONNECTED,
            )
        )

    def textMessageReceived(self, msg):
        msg = json.loads(msg)
        # print(msg)
        if 'id' in msg:
            id = msg["id"]
            if id == GET_PLAYERS:
                # use only the first player.
                players = msg['result']
                if len(players):
                    self.player_id = players[0]['playerid']
                else:
                    self.player_id = None
                self.timeout()
            elif id == GET_FILE:
                file = msg['result']['item']['file']
                self.filename = file
                if self.filename is None or self.filename == "":
                    self.set_state(
                        MediaStatusReport(
                            time.time(),
                            "",
                            MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED,
                        )
                    )
            elif id == GET_TIME:
                speed = msg['result']['speed']
                t = msg['result']['time']
                time_in_seconds = (t['hours'] * 60 * 60 +
                                   t['minutes'] * 60 +
                                   t['seconds'] +
                                   t['milliseconds'] / 1000.0)
                if self.filename:
                    self.set_state(
                        MediaStatusReport(
                            time.time(),
                            "",
                            MediaConnectionState.CONNECTED_AND_PLAYING if speed else MediaConnectionState.CONNECTED_AND_PAUSED,
                            self.filename,
                            speed,
                            time_in_seconds
                        )
                    )

        elif 'method' in msg:
            method = msg['method']
            if method in (
                'Player.OnResume',
                'Player.OnPause',
                'Player.OnSeek',

            ):
                # trigger timeout for faster response times
                self.timeout()

    def enable(self):
        self._enabled = True
        self.timer.start()
        self.reconnect_timer.start()
        self.open_connection()

    def disable(self):
        self._enabled = False
        if self.websocket is not None:
            self.websocket.close()
            self.websocket = None
        self.player_id = None
        self.filename = None
        self.timer.stop()
        self.reconnect_timer.stop()

    def is_enabled(self) -> bool:
        return self._enabled

