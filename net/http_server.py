import logging
import json

from PySide6.QtCore import QObject
from PySide6.QtNetwork import QTcpServer, QHostAddress
from PySide6.QtHttpServer import QHttpServer, QHttpServerRequest

from qt_ui import settings

logger = logging.getLogger('restim.http')


class HttpServer(QObject):
    def __init__(self, parent):
        super().__init__(parent)

        self.http_server = QHttpServer(self)
        self.tcp_server = QTcpServer(self)
        self.bottomless_pit = []
        self.actions = []

        enabled = settings.rest_enabled.get()
        port = settings.rest_port.get()
        localhost_only = settings.rest_localhost_only.get()

        if not enabled:
            logger.info("REST API not enabled.")
            return

        address = QHostAddress.SpecialAddress.LocalHost if localhost_only else QHostAddress.SpecialAddress.Any

        if not self.tcp_server.listen(address, port):
            logger.error("HTTP server failed to listen on port")
            logger.error(f"{self.tcp_server.errorString()}")
            return


        if not self.http_server.bind(self.tcp_server):
            logger.error("HTTP server failed to bind to socket")
            return

        logger.info(f"HTTP server active at localhost:{port}")

        self.route("/v1/actions", self.api_actions)

    def add_action(self, action_string, fn):
        self.actions.append(action_string)
        self.route(f"/v1/actions/{action_string}", fn)

    def route(self, rule, fn):
        # store fn somewhere, because QHttpServer::route
        # forgets to increase the object refcount
        self.bottomless_pit.append(fn)
        self.http_server.route(rule, fn)

    def api_actions(self, request: QHttpServerRequest):
        return json.dumps({'actions': self.actions})


