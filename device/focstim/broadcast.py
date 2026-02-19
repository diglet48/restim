import logging
import time

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QAbstractSocket

from device.focstim.focstim_rpc_pb2 import RpcMessage, Notification
from device.focstim.notifications_pb2 import NotificationDebugAS5311
from device.focstim.hdlc import HDLC
from device.focstim.proto_api import FOCStimProtoAPI
from stim_math.sensors.as5311 import AS5311Data

logger = logging.getLogger('restim.focstim.broadcast')


class SensorBroadcaster(QObject):
    """TCP server for broadcasting sensor data to remote clients."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = None
        self.clients = []
        self.hdlc = HDLC()

    def start(self, port: int) -> bool:
        self.server = QTcpServer(self)
        if self.server.listen(port=port):
            logger.info(f"Broadcasting sensor data on port {port}")
            self.server.newConnection.connect(self._on_new_connection)
            return True
        else:
            logger.error(f"Failed to start broadcast server on port {port}: {self.server.errorString()}")
            self.server = None
            return False

    def stop(self):
        if self.server:
            self.server.close()
            self.server = None

        for client in self.clients:
            client.close()
        self.clients.clear()

    def attach_source(self, api: FOCStimProtoAPI):
        """Connect to the AS5311 notification signal of the given FOCStimProtoAPI."""
        api.on_notification_debug_as5311.connect(self._broadcast_as5311)

    def _on_new_connection(self):
        while self.server and self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            logger.info(f"New broadcast client connected: {client.peerAddress().toString()}")
            self.clients.append(client)
            client.disconnected.connect(
                lambda c=client: self._on_client_disconnected(c)
            )

    def _on_client_disconnected(self, client):
        logger.info(f"Broadcast client disconnected")
        if client in self.clients:
            self.clients.remove(client)

    def _broadcast_as5311(self, notif: NotificationDebugAS5311):
        """Broadcast AS5311 notification to all connected clients."""
        if not self.clients:
            return

        # Create notification wrapper
        notification = Notification()
        notification.notification_debug_as5311.CopyFrom(notif)
        notification.timestamp = time.time_ns()

        # Create RpcMessage and serialize with HDLC framing
        message = RpcMessage()
        message.notification.CopyFrom(notification)
        data = message.SerializeToString()
        framed_data = self.hdlc.encode(data)

        # Send to all connected clients
        disconnected = []
        for client in self.clients:
            if client.state() == QAbstractSocket.SocketState.ConnectedState:
                if client.write(framed_data) != len(framed_data):
                    logger.warning(f"Failed to send data to client")
                    disconnected.append(client)
            else:
                disconnected.append(client)

        for client in disconnected:
            if client in self.clients:
                self.clients.remove(client)


class RemoteSensorClient(QObject):
    """Client for receiving AS5311 sensor data from a remote broadcaster.

    Automatically reconnects when connection is lost, polling every second.
    """

    # Signal emitted when AS5311 data is received
    new_as5311_sensor_data = Signal(AS5311Data)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.transport = None
        self.api = None
        self.host_address = None
        self.port = None
        self.is_stopping = False

        # Reconnection timer - polls every second when disconnected
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setInterval(1000)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)

    def start(self, host_address: str, port: int):
        """Connect to remote AS5311 sensor data server."""
        self.host_address = host_address
        self.port = port
        self.is_stopping = False
        self._create_connection()

    def stop(self):
        """Disconnect from server and stop reconnection attempts."""
        self.is_stopping = True
        self.reconnect_timer.stop()
        if self.transport and self.transport.isOpen():
            self.transport.close()

    def _create_connection(self):
        """Create a new connection attempt."""
        if self.is_stopping:
            return

        logger.info(f"Connecting to remote AS5311 sensor at {self.host_address}:{self.port}")

        # Clean up old transport if exists
        if self.transport:
            self.transport.deleteLater()
            self.transport = None
            self.api = None

        self.transport = QTcpSocket(self)
        self.transport.setSocketOption(QAbstractSocket.SocketOption.LowDelayOption, 1)
        self.transport.connected.connect(self._on_connected)
        self.transport.errorOccurred.connect(self._on_error)
        self.transport.disconnected.connect(self._on_disconnected)
        self.transport.connectToHost(self.host_address, self.port)

    def _on_connected(self):
        """Handle connection established."""
        logger.info("Connected to remote AS5311 sensor data server")
        self.reconnect_timer.stop()
        # Initialize API for parsing incoming notifications only
        self.api = FOCStimProtoAPI(self, self.transport, None)
        self.api.on_notification_debug_as5311.connect(self._handle_as5311_notification)

    def _on_error(self, error):
        """Handle connection error."""
        if self.is_stopping:
            return
        logger.warning(f"Remote sensor connection error: {self.transport.errorString()}")
        self._start_reconnect_timer()

    def _on_disconnected(self):
        """Handle disconnection - start reconnect polling."""
        if self.is_stopping:
            return
        logger.info("Remote sensor server disconnected, will retry...")
        self._start_reconnect_timer()

    def _start_reconnect_timer(self):
        """Start the reconnection polling timer."""
        if not self.reconnect_timer.isActive() and not self.is_stopping:
            self.reconnect_timer.start()

    def _attempt_reconnect(self):
        """Attempt to reconnect to the server."""
        if self.is_stopping:
            self.reconnect_timer.stop()
            return
        self._create_connection()

    def _handle_as5311_notification(self, notif: NotificationDebugAS5311):
        """Convert notification to AS5311Data and emit signal."""
        m = notif.tracked * (2000.0 / 4096) * 1e-6
        self.new_as5311_sensor_data.emit(AS5311Data(m))
