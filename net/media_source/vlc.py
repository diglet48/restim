import time
import functools
import logging

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, QXmlStreamReader
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply, QAuthenticator
from PyQt5.QtXmlPatterns import QXmlQuery

from net.media_source.mediasource import MediaSource, MediaStatusReport, MediaConnectionState
from qt_ui import settings

logger = logging.getLogger('restim.media.VLC')


class VLC(MediaSource):
    def __init__(self, parent):
        super(VLC, self).__init__(parent)

        self._enabled = False
        self.playlist_id = None
        self.filename = None
        self.media_duration = None  # The length of the video according to QMediaPlayer
        self.media_player = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(2000))

        self.nam = QNetworkAccessManager()
        self.nam.authenticationRequired.connect(self.authenticationRequired)
        self.nam.finished.connect(self.on_request_finished)

    def authenticationRequired(self, request: QNetworkRequest, authenticator: QAuthenticator):
        logger.info('authenticating')
        authenticator.setUser(settings.media_sync_vlc_username.get())
        authenticator.setPassword(settings.media_sync_vlc_password.get())

    def timeout(self):
        status_url = QUrl.fromUserInput(settings.media_sync_vlc_address.get() + '/requests/status.xml')
        playlist_url = QUrl.fromUserInput(settings.media_sync_vlc_address.get() + '/requests/playlist.xml')

        if self._enabled:
            if not status_url.isValid():
                logger.error('Invalid VLC address: %s', status_url.errorString)
                self.timer.setInterval(5000)
                return
            if not playlist_url.isValid():
                logger.error('Invalid VLC address %s', playlist_url.errorString)
                self.timer.setInterval(5000)
                return

            req = QNetworkRequest(status_url)
            req.setTransferTimeout(2000)
            self.nam.get(req)

    def on_request_finished(self, reply: QNetworkReply):
        if reply.url().toString().endswith('status.xml'):
            self.on_status_request_finished(reply)
        if reply.url().toString().endswith('playlist.xml'):
            self.on_playlist_request_finished(reply)

    def on_status_request_finished(self, reply: QNetworkReply):
        if self._enabled:
            media_state = self.parse_status_reply(reply)
            self.set_state(media_state)
            self.timer.setInterval(100)
            self.timer.start()

            reply.deleteLater()
            self.timer.start(100)

    def send_playlist_request(self):
        logger.debug('send playlist request')
        playlist_url = QUrl.fromUserInput(settings.media_sync_vlc_address.get() + '/requests/playlist.xml')

        if self._enabled and playlist_url.isValid():
            req = QNetworkRequest(playlist_url)
            req.setTransferTimeout(2000)
            self.nam.get(req)

    def on_playlist_request_finished(self, reply: QNetworkReply):
        if self._enabled:
            # TODO: retry if fails?
            self.parse_playlist_reply(reply)

            reply.deleteLater()
            self.timer.start(100)

    def query_media_duration(self):
        """
        Open the video file and query the video length with QMediaPlayer.
        """
        the_file = self.filename
        logger.info('query media duration from: %s', the_file)

        self.media_player = QMediaPlayer()

        def duration_changed(duration: int):
            if the_file == self.filename:
                self.media_duration = float(duration) / 1000
                logger.info('media duration detected as %f (seconds)', self.media_duration)

        def on_error(error: QMediaPlayer.Error):
            logger.warning('error detecting media duration: %s', self.media_player.errorString())

        self.media_player.durationChanged.connect(duration_changed)
        self.media_player.error.connect(on_error)
        self.media_player.setMedia(QMediaContent(QUrl(the_file)))

    def enable(self):
        self._enabled = True
        self.timeout()

    def disable(self):
        self._enabled = False
        self.set_state(MediaStatusReport(time.time()))
        self.timer.stop()

    def is_enabled(self) -> bool:
        return self._enabled

    def parse_status_reply(self, reply: QNetworkReply) -> MediaStatusReport:
        """
        example response (some properties removed):
        <?xml version="1.0" encoding="utf-8" standalone="yes" ?>
        <root>
            <fullscreen>false</fullscreen>
            <apiversion>3</apiversion>
            <currentplid>4</currentplid>
            <time>28</time>
            <volume>256</volume>
            <length>3726</length>
            <state>paused</state>
            <position>0.0076895346865058</position>
            ...
            <stats>
                <readpackets>1833</readpackets>
                <lostpictures>3</lostpictures>
                ...
            </stats>
        </root>
        """

        if reply.error():
            logger.debug('network error: %s', reply.errorString())
            self.media_info = None
            self.playlist_id = None
            return MediaStatusReport(
                timestamp=time.time(),
                connectionState=MediaConnectionState.NOT_CONNECTED,
                errorString=reply.errorString())

        # TODO: QXmlQuery is deprecated in Qt6
        query = QXmlQuery()
        query.setFocus(reply)
        query.setQuery("string(//rate)")
        rate = query.evaluateToString().strip()
        query.setQuery("string(//state)")
        state = query.evaluateToString().strip()
        query.setQuery("string(//position)")
        position = query.evaluateToString().strip()
        query.setQuery("string(//currentplid)")
        currentplid = query.evaluateToString().strip()
        query.setQuery("string(//length)")
        length = query.evaluateToString().strip()

        if currentplid == '-1':
            currentplid = None

        if currentplid is None:  # file unloaded
            self.playlist_id = None
            self.filename = None
            self.media_duration = None
            self.media_player = None
        elif self.playlist_id != currentplid:  # file changed
            self.playlist_id = currentplid
            self.filename = None
            self.media_duration = None
            self.media_player = None
            self.send_playlist_request()

        if self.filename:
            file_path = self.filename
        else:
            file_path = ''

        media_position = float(length) * float(position)
        if self.media_duration:  # if detected precise media position
            media_position = self.media_duration * float(position)

        if file_path and state == 'playing':
            connection_status = MediaConnectionState.CONNECTED_AND_PLAYING
        elif file_path:
            connection_status = MediaConnectionState.CONNECTED_AND_PAUSED
        else:
            connection_status = MediaConnectionState.CONNECTED_BUT_NO_FILE_LOADED

        return MediaStatusReport(
            timestamp=time.time(),
            connectionState=connection_status,
            filePath=file_path,
            playbackRate=float(rate),
            claimed_media_position=media_position,
        )

    def parse_playlist_reply(self, reply: QNetworkReply) -> None:
        """
        example response:
        <node ro="rw" name="" id="0">
            <node ro="ro" name="Playlist" id="1">
                <leaf ro="rw" name="RedLightGreenLight-Lily Ivy.mp4" id="3" duration="4130" uri="file:///C:/RedLightGreenLight-Lily%20Ivy.mp4"/>
                <leaf ro="rw" name="Rhythms of Desire.mp4" id="4" duration="3726" uri="file:///C:/Rhythms%20of%20Desire.mp4" current="current"/>
                <leaf ro="rw" name="Twisted Tales E-Stim CH Str8.mp4" id="5" duration="4517" uri="file:///C:/Twisted%20Tales%20E-Stim%20CH%20Str8.mp4"/>
            </node>
            <node ro="ro" name="Media Library" id="2">
            </node>
        </node>
        """

        if reply.error() != QNetworkReply.NoError:
            logger.debug('network error: %s', reply.errorString())
            return

        xml = QXmlStreamReader(reply)
        if xml.readNextStartElement():  # root node
            while xml.readNextStartElement():  # read playlist or media library element
                attributes = xml.attributes()
                # if attributes.value('name') == 'Playlist':    # only works if language is english
                if attributes.value('id') == '1':               # playlist has ID 1
                    while xml.readNextStartElement():
                        attributes = xml.attributes()
                        id = attributes.value('id') # playlist id
                        uri = attributes.value('uri')
                        url = QUrl(uri)
                        if id == self.playlist_id:
                            self.filename = url.toLocalFile()
                            self.query_media_duration()
                        xml.skipCurrentElement()
                xml.skipCurrentElement()
