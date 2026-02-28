import logging

from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QIODevice

from device.focstim.proto_api import FOCStimProtoAPI


logger = logging.getLogger('restim.focstim')


class WifiUploadHelper:
    def __init__(self):
        pass

    def upload(self, com_port, ssid, password):
        logger.info(f"Connecting to FOC-Stim at {com_port}")
        self.transport = QSerialPort()
        self.transport.setPortName(com_port)
        self.transport.setBaudRate(115200)
        success = self.transport.open(QIODevice.OpenModeFlag.ReadWrite)
        self.transport.setSettingsRestoredOnClose(False)

        if not success:
            logger.error(f"connection error: {self.transport.errorString()}")
            return None

        self.api = FOCStimProtoAPI(None, self.transport, None)
        self.fut = self.api.request_wifi_parameters_set(ssid, password)
        self.fut.set_timeout(1000)

        # self.fut.on_timeout.connect(self.timeout)
        # self.fut.on_result.connect(self.result)
        return self.fut

    def close(self):
        self.transport.close()
        self.api = None


class GrabIpHelper:
    def __init__(self):
        pass

    def get_ip(self, com_port):
        logger.info(f"Connecting to FOC-Stim at {com_port}")
        self.transport = QSerialPort()
        self.transport.setPortName(com_port)
        self.transport.setBaudRate(115200)
        success = self.transport.open(QIODevice.OpenModeFlag.ReadWrite)
        self.transport.setSettingsRestoredOnClose(False)

        if not success:
            logger.error(f"connection error: {self.transport.errorString()}")
            return None

        self.api = FOCStimProtoAPI(None, self.transport, None)
        self.fut = self.api.request_wifi_ip_get()
        self.fut.set_timeout(1000)

        # self.fut.on_timeout.connect(self.timeout)
        # self.fut.on_result.connect(self.result)
        return self.fut

    def close(self):
        self.transport.close()
        self.api = None


