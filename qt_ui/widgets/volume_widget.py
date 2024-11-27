import time

from PyQt5 import QtCore, QtWidgets

from qt_ui import settings

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
        self.latency = settings.display_latency.get() / 1000.0

    def set_axis(self, volume: VolumeParams):
        self.volume = VolumeParams(
            api=volume.api,
            master=volume.master,
            inactivity=volume.inactivity,
            external=volume.external
        )

    def refresh(self):
        if self.volume is None:
            return

        master_volume = self.volume.master.last_value()
        inactivity_volume = self.volume.inactivity.last_value()
        api_volume = self.volume.api.interpolate(time.time() - self.latency)
        external_volume = self.volume.external.interpolate(time.time() - self.latency)
        self.setValue(int(master_volume * api_volume * inactivity_volume * external_volume * 100))

        self.setToolTip(
            f"master volume: {master_volume * 100:.0f}%\n" +
            f"tcode/funscript volume: {api_volume * 100:.0f}%\n" +
            f"inactivity volume: {inactivity_volume * 100:.0f}%\n" +
            f"external volume: {external_volume * 100:.0f}%"
        )
