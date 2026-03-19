import json
import logging

from PySide6 import QtNetwork
from PySide6.QtCore import Signal, QObject
from PySide6.QtWebSockets import QWebSocket

from stim_math.sensors.imu import IMUData

logger = logging.getLogger('restim.websocket')


class WebsocketIMUHandler(QObject):
    def __init__(self, websocket: QWebSocket):
        super().__init__()
        self.websocket = websocket

        self.websocket.textMessageReceived.connect(self.textMessageReceived)
        self.websocket.disconnected.connect(self.disconnected)

    def textMessageReceived(self, msg):
        # print('imu data received over websocket:', msg)
        try:
            js = json.loads(msg)
            data = IMUData(samplerate=js['samplerate'],
                           acc_x=js['acc_x'], acc_y=js['acc_y'], acc_z=js['acc_z'],
                           gyr_x=js['gyr_x'], gyr_y=js['gyr_y'], gyr_z=js['gyr_z'])
            # print('received', data)
            self.new_imu_data.emit(data)
        except json.decoder.JSONDecodeError:
            pass
        except KeyError:
            pass

    def transmit_imu_data(self, data: IMUData):
        self.websocket.sendTextMessage(f'{{"samplerate": {data.samplerate}, '
                                       f'"acc_x": {data.acc_x:.5f}, '
                                       f'"acc_y": {data.acc_y:.5f}, '
                                       f'"acc_z": {data.acc_z:.5f}, '
                                       f'"gyr_x": {data.gyr_x:.5f}, '
                                       f'"gyr_y": {data.gyr_y:.5f}, '
                                       f'"gyr_z": {data.gyr_z:.5f}}}')

    def is_connected(self):
        return self.websocket.state() != QtNetwork.QAbstractSocket.SocketState.UnconnectedState

    new_imu_data = Signal(IMUData)
    disconnected = Signal()