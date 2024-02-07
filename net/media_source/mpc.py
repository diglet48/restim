import re
import time
import logging

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply

from net.media_source.mediasource import MediaSource, MediaStatusReport, MediaConnectionState
from qt_ui import settings

logger = logging.getLogger('restim.media.MPC_HC')


def parse_reply(reply: QNetworkReply):
    if reply.error():
        logger.debug('network error: %s', reply.errorString())
        return MediaStatusReport(
            timestamp=time.time(),
            connectionState=MediaConnectionState.NOT_CONNECTED,
            errorString=reply.errorString())

    try:
        pattern = b'\s+<p id="(\w+)">(.+)</p>\r\n'
        props = dict()
        while reply.bytesAvailable():
            line = reply.readLine()
            m = re.search(pattern, line)
            if m and len(m.groups()) == 2:
                key, value = m.groups()
                props[key.decode('utf-8')] = value.decode('utf-8')

        return MediaStatusReport(
            timestamp=time.time(),
            connectionState=MediaConnectionState.CONNECTED_AND_PLAYING if props['statestring'] == 'Playing' else MediaConnectionState.CONNECTED_AND_PAUSED,
            filePath=props['filepath'] if 'filepath' in props else '',
            playbackRate=float(props['playbackrate']),
            claimed_media_position=float(props['position']) / 1000
        )
    except KeyError:
        logger.error('unable to parse reply')
        return MediaStatusReport(
            timestamp=time.time(),
            connectionState=MediaConnectionState.NOT_CONNECTED,
            errorString="unable to parse reply")


class MPC(MediaSource):
    def __init__(self, parent):
        super(MPC, self).__init__(parent)

        self._enabled = False

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(200))

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.onFinished)

    def timeout(self):
        if self._enabled:
            url = QUrl.fromUserInput(settings.media_sync_mpc_address.get() + '/variables.html')
            if not url.isValid():
                logger.error('invalid MPC-HC address:', url.errorString())
                self.timer.setInterval(5000)
                self.timer.start()
            else:
                req = QNetworkRequest(url)
                req.setTransferTimeout(2000)
                self.nam.get(req)

    def onFinished(self, reply):
        if self._enabled:
            media_state = parse_reply(reply)
            self.set_state(media_state)
            reply.deleteLater()
            self.timer.start(100)

    def enable(self):
        self._enabled = True
        self.timer.start()

    def disable(self):
        self._enabled = False
        self.set_state(MediaStatusReport(time.time()))
        self.timer.stop()

    def is_enabled(self) -> bool:
        return self._enabled

