from PyQt5 import QtCore, QtWebSockets, QtNetwork

from net.tcode import TCodeCommand
from qt_ui.stim_config import CalibrationParameters, ModulationParameters, PositionParameters, TransformParameters


class WebsocketClient(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)

        # self.client = QtWebSockets.QWebSocket("", QtWebSockets.QWebSocketProtocol.Version13, None)
        self.client = QtWebSockets.QWebSocket("")
        self.client.error.connect(self.error)

        self.client.connected.connect(self.onConnected)

        self.position_parameters = None
        self.calibration_parameters = None
        self.modulation_parameters = None
        self.transform_parameters = None

        # send the calibration and modulation parameters once every second just in case the server restarts
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.sendCalibrationParameters)
        timer.timeout.connect(self.sendModulationParameters)
        timer.timeout.connect(self.sendTransformParameters)
        timer.start(1000)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.reconnect_if_unconnected)
        timer.start(1000)


    def reconnect_if_unconnected(self):
        if self.client.state() == QtNetwork.QAbstractSocket.SocketState.UnconnectedState:
            self.client.open(QtCore.QUrl("ws://127.0.0.1:12346"))

    def send_message(self):
        self.client.sendTextMessage("asd")

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def onConnected(self):
        print("connected")

    def sendPositionParameters(self):
        if self.position_parameters:
            cmd = "\n".join([
                TCodeCommand("L0", (self.position_parameters.alpha + 1.0) * 0.5).format_cmd(),
                TCodeCommand("L1", (self.position_parameters.beta + 1.0) * 0.5).format_cmd()])
            self.client.sendTextMessage(cmd)

    def sendCalibrationParameters(self):
        if self.calibration_parameters:
            cmd = "\n".join([
                TCodeCommand("C0", self.calibration_parameters.edge_0_3pi).format_cmd(),
                TCodeCommand("C1", self.calibration_parameters.edge_1_3pi).format_cmd(),
                TCodeCommand("C2", self.calibration_parameters.edge_2_3pi).format_cmd(),
                TCodeCommand("C3", self.calibration_parameters.edge_3_3pi).format_cmd(),
                TCodeCommand("C4", self.calibration_parameters.edge_4_3pi).format_cmd(),
                TCodeCommand("C5", self.calibration_parameters.edge_5_3pi).format_cmd(),
                TCodeCommand("C6", self.calibration_parameters.center).format_cmd(),
                TCodeCommand("D0", self.calibration_parameters.mid_0_3pi).format_cmd(),
                TCodeCommand("D1", self.calibration_parameters.mid_1_3pi).format_cmd(),
                TCodeCommand("D2", self.calibration_parameters.mid_2_3pi).format_cmd(),
                TCodeCommand("D3", self.calibration_parameters.mid_3_3pi).format_cmd(),
                TCodeCommand("D4", self.calibration_parameters.mid_4_3pi).format_cmd(),
                TCodeCommand("D5", self.calibration_parameters.mid_5_3pi).format_cmd(),
            ])
            self.client.sendTextMessage(cmd)

    def sendModulationParameters(self):
        if self.modulation_parameters:
            cmd = [
                TCodeCommand("M0", self.modulation_parameters.carrier_frequency / 1000.0).format_cmd(),
            ]
            if self.modulation_parameters.modulation_1_enabled:
                cmd += [
                    TCodeCommand("M1", self.modulation_parameters.modulation_1_freq / 150.0).format_cmd(),
                    TCodeCommand("M2", self.modulation_parameters.modulation_1_modulation).format_cmd(),
                ]
            else:
                cmd += [
                    TCodeCommand("M1", 0.0).format_cmd(),
                    TCodeCommand("M2", 0.0).format_cmd(),
                ]
            if self.modulation_parameters.modulation_2_enabled:
                cmd += [
                    TCodeCommand("M3", self.modulation_parameters.modulation_2_freq / 150.0).format_cmd(),
                    TCodeCommand("M4", self.modulation_parameters.modulation_2_modulation).format_cmd(),
                ]
            else:
                cmd += [
                    TCodeCommand("M3", 0).format_cmd(),
                    TCodeCommand("M4", 0).format_cmd(),
                ]
            cmd = "\n".join(cmd)
            self.client.sendTextMessage(cmd)
        pass

    def sendTransformParameters(self):
        if self.transform_parameters:
            cmd = "\n".join([
                TCodeCommand("H0", (self.transform_parameters.up_down / 30) + 0.5).format_cmd(),
                TCodeCommand("H1", (self.transform_parameters.left_right / 30) + 0.5).format_cmd()])
            self.client.sendTextMessage(cmd)


    def updatePositionParameters(self, position_params: PositionParameters):
        self.position_parameters = position_params
        self.sendPositionParameters()

    def updateCalibrationParameters(self, calibration_params: CalibrationParameters):
        self.calibration_parameters = calibration_params
        self.sendCalibrationParameters()

    def updateModulationParameters(self, modulation_params: ModulationParameters):
        self.modulation_parameters = modulation_params
        self.sendModulationParameters()

    def updateTransformParameters(self, transform_parameters: TransformParameters):
        self.transform_parameters = transform_parameters
        self.sendTransformParameters()
