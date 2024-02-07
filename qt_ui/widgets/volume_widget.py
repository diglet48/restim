import time

from PyQt5.QtCore import QSettings
from PyQt5 import QtCore, QtWidgets

from qt_ui.preferences_dialog import KEY_DISPLAY_FPS, KEY_DISPLAY_LATENCY

from stim_math.audio_gen.params import VolumeParams


class VolumeWidget(QtWidgets.QProgressBar):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.volume: VolumeParams = None

        self.latency = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(int(1000 / 10.0))
        self.refreshSettings()

    def refreshSettings(self):
        settings = QSettings()
        # self.timer.setInterval(int(1000 // settings.value(KEY_DISPLAY_FPS, 10.0, float)))
        self.latency = settings.value(KEY_DISPLAY_LATENCY, 200.0, float) / 1000.0

    def set_axis(self, volume: VolumeParams):
        self.volume = VolumeParams(
            api=volume.api,
            ramp=volume.ramp,
            inactivity=volume.inactivity,
        )

    def refresh(self):
        if self.volume is None:
            return

        ramp_volume = self.volume.ramp.last_value()
        inactivity_volume = self.volume.inactivity.last_value()
        api_volume = self.volume.api.interpolate(time.time() - self.latency)
        self.setValue(int(ramp_volume * api_volume * inactivity_volume * 100))

        self.setToolTip(
            f"ramp volume: {ramp_volume * 100:.0f}%\n" +
            f"inactivity volume: {inactivity_volume * 100:.0f}%\n" +
            f"api volume: {api_volume * 100:.0f}%"
        )
