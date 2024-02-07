from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QStyle

from qt_ui.audio_test_dialog_ui import Ui_AudioTestDialog
from qt_ui.audio_generation_widget import AudioGenerationWidget, ChannelMappingParameters
from stim_math.sine_generator import AngleGenerator

import sounddevice as sd
import numpy as np


class AudioTestDialog(QDialog, Ui_AudioTestDialog):
    def __init__(self, parent, device_index):
        super().__init__(parent)
        self.setupUi(self)

        self.device_index = device_index
        self.angle = AngleGenerator()
        self.checkboxes = []
        self.audio_gen = AudioGenerationWidget(None)

        self.layout = QtWidgets.QFormLayout(self)
        self.groupBox_2.setLayout(self.layout)

        self.spinBox_channel_count.valueChanged.connect(self.channel_count_changed)
        self.spinBox_channel_count.setValue(sd.query_devices(device_index)['max_output_channels'])
        self.commandLinkButton.clicked.connect(self.audio_start_stop)

    def generate_audio(self, samplerate, timeline: np.ndarray, command_timeline: np.ndarray):
        volume = self.doubleSpinBox_volume.value() / 100
        frequency = self.doubleSpinBox_frequency.value()
        angle = self.angle.generate(len(timeline), frequency, samplerate)
        sine = np.sin(angle) * volume
        return [sine * self.checkboxes[i].isChecked() for i in range(self.spinBox_channel_count.value())]

    def audio_start_stop(self):
        if self.audio_gen.stream is None:
            self.audio_start()
        else:
            self.audio_stop()

    def audio_start(self):
        device = sd.query_devices(self.device_index)
        device_name = device['name']
        api_name = sd.query_hostapis(device['hostapi'])['name']
        mapping_parameters = [ChannelMappingParameters(
            self.spinBox_channel_count.value(),
            list(range(self.spinBox_channel_count.value()))
        )]
        self.audio_gen.start(api_name, device_name, 'high', self, mapping_parameters)
        if self.audio_gen.stream is not None:
            pixmapi = getattr(QStyle, 'SP_MediaStop')
            icon = self.style().standardIcon(pixmapi)
            self.commandLinkButton.setIcon(icon)
            self.commandLinkButton.setText("Stop audio")

    def audio_stop(self):
        self.audio_gen.stop()
        pixmapi = getattr(QStyle, 'SP_MediaPlay')
        icon = self.style().standardIcon(pixmapi)
        self.commandLinkButton.setIcon(icon)
        self.commandLinkButton.setText("Start audio")

    def refresh_channel_map(self):
        self.label_channel_map.setText(
            ','.join([str(i) for i, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()])
        )

    def channel_count_changed(self):
        self.audio_stop()

        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.checkboxes = []

        for i in range(self.spinBox_channel_count.value()):
            label = QtWidgets.QLabel(f"Channel {i}:")
            checkbox = QtWidgets.QCheckBox("")
            checkbox.setChecked(True)
            checkbox.clicked.connect(self.refresh_channel_map)
            self.layout.addRow(label, checkbox)
            self.checkboxes.append(checkbox)

        self.refresh_channel_map()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.audio_stop()
        event.accept()
