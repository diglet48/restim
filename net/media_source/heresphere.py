import json
import time
import logging

from PySide6 import QtCore
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QTcpSocket

from net.media_source.mediasource import MediaSource, MediaStatusReport, MediaConnectionState
from qt_ui import settings

logger = logging.getLogger('restim.media.Heresphere')


def parse_reply(reply: dict):
    return MediaStatusReport(
        timestamp=time.time(),
        connectionState=MediaConnectionState.CONNECTED_AND_PLAYING if reply['playerState'] == 0 else MediaConnectionState.CONNECTED_AND_PAUSED,
        playbackRate=reply['playbackSpeed'],
        claimed_media_position=reply['currentTime'],
        filePath=reply['path']
    )


class HereSphere(MediaSource):
    def __init__(self, parent):
        super(HereSphere, self).__init__(parent)

        self.enabled = True

        self.keep_alive_timer = QtCore.QTimer(self)
        self.keep_alive_timer.setInterval(int(1000))
        self.keep_alive_timer.timeout.connect(self.keep_alive)

        self.reconnect_timer = QtCore.QTimer(self)
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self.reconnect)

        self.socket = QTcpSocket()

        self.socket.errorOccurred.connect(self.onError)
        self.socket.readyRead.connect(self.readyRead)

    def keep_alive(self):
        if self.socket.isWritable():
            self.socket.write(b'\0\0\0\0')

    def reconnect(self):
        if self.enabled:
            if self.socket.state() == QTcpSocket.UnconnectedState:
                url = QUrl.fromUserInput(settings.media_sync_heresphere_address.get())
                if url.host() and 0 < url.port() <= 65535:
                    self.socket.connectToHost(url.host(), url.port())
                else:
                    logger.error('invalid HereSphere address: %s', url.errorString())

    def enable(self):
        self.reconnect()
        self.reconnect_timer.start()
        self.keep_alive_timer.start()
        self.enabled = True

    def disable(self):
        self.reconnect_timer.stop()
        self.keep_alive_timer.stop()
        self.socket.abort()
        self.socket.close()
        self.set_state(MediaStatusReport(time.time()))
        self.enabled = False

    def pre_update(self, last_state: MediaStatusReport, state: MediaStatusReport):
        if state.connectionState == MediaConnectionState.CONNECTED_AND_PAUSED:
            if abs(last_state.claimed_media_position - state.cursor) < .05:
                state.cursor = self.last_state.cursor
        return state

    def readyRead(self):
        while self.socket.bytesAvailable() >= 4:
            header = self.socket.peek(4)
            length = int.from_bytes(header, byteorder='little', signed=False)
            if length == 0:
                self.socket.read(4)
                state = MediaStatusReport(
                    timestamp=time.time(),
                    connectionState=MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED,
                )
                self.set_state(state)

            elif self.socket.bytesAvailable() == (4 + length):
                data = self.socket.read(4 + length)[4:]
                js = json.loads(bytes(data).decode('utf-8'))
                state = parse_reply(js)
                self.set_state(state)

            elif self.socket.bytesAvailable() > (4 + length):
                self.socket.skip(4 + length)
            elif self.socket.bytesAvailable() < (4 + length):
                logger.error('invalid HereSphere data packet. Closing connection.')
                # something went wrong. Purge data.
                self.socket.close()
                state = MediaStatusReport(
                    timestamp=time.time(),
                    connectionState=MediaConnectionState.NOT_CONNECTED,
                )
                self.set_state(state)
                self.reconnect_timer.start(1000)

    def onError(self):
        if self.enabled:
            logger.debug('network error: %s', self.socket.errorString())

            state = MediaStatusReport(
                timestamp=time.time(),
                connectionState=MediaConnectionState.NOT_CONNECTED,
            )
            self.set_state(state)
            self.reconnect_timer.start(1000)

    def is_enabled(self) -> bool:
        return self.enabled

