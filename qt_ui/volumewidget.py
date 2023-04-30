import time

from PyQt5.QtCore import QSettings
from PyQt5 import QtCore, QtWidgets

from qt_ui.preferencesdialog import KEY_DISPLAY_FPS, KEY_DISPLAY_LATENCY
from stim_math.threephase_parameter_manager import ThreephaseParameterManager


class VolumeWidget(QtWidgets.QProgressBar):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.latency = 0
        self.config: ThreephaseParameterManager = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(int(1000 / 60.0))
        self.refreshSettings()

    def refreshSettings(self):
        settings = QSettings()
        self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 60.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def refresh(self):
        if self.config is None:
            return

        ramp_volume = self.config.ramp_volume.last_value()
        inactivity_volume = self.config.inactivity_volume.last_value()
        api_volume = self.config.volume.interpolate(time.time() - self.latency)
        self.setValue(int(ramp_volume * api_volume * inactivity_volume * 100))

        self.setToolTip(
            f"ramp volume: {ramp_volume * 100:.0f}%\n" +
            f"inactivity volume: {inactivity_volume * 100:.0f}%\n" +
            f"api volume: {api_volume * 100:.0f}%"
        )
