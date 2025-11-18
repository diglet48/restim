import logging
import os.path
import numpy as np
import time

import soundfile as sf

from PySide6 import QtGui, QtCore
from PySide6.QtCore import QThread, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QDialog, QAbstractButton, QDialogButtonBox, QFileDialog

from qt_ui.algorithm_factory import AlgorithmFactory
from qt_ui.audio_write_dialog_ui import Ui_AudioWriteDialog
from qt_ui.models.funscript_kit import FunscriptKitModel
from qt_ui.models.script_mapping import ScriptMappingModel
from stim_math.axis import AbstractMediaSync, AbstractTimestampMapper
from qt_ui.device_wizard.enums import DeviceConfiguration
from qt_ui.file_dialog import FileDialog

logger = logging.getLogger('restim.bake_audio')


class DummyTimestamMapper(AbstractTimestampMapper, AbstractMediaSync):
    def __init__(self, epoch):
        self.epoch = epoch

    def is_playing(self) -> bool:
        return True

    def map_timestamp(self, timestamp):
        return timestamp - self.epoch


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class AudioWriteDialog(QDialog, Ui_AudioWriteDialog):
    def __init__(self, mainwindow,
                 kit: FunscriptKitModel,
                 script_mapping_model: ScriptMappingModel,
                 device: DeviceConfiguration,
                 media_filename: str
                 ):
        super().__init__(mainwindow)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.kit = kit
        self.script_mapping_model = script_mapping_model
        self.device = device
        self.media_filename = media_filename
        self.samplerate_spinbox.setCurrentText("44100")
        self.worker = None

        # auto-detect the media duration
        if self.media_filename:
            self.duration_spinbox.setEnabled(False)
            def duration_changed(duration: int):
                logger.info('media duration detected as %f (seconds)', duration / 1000)
                self.duration_spinbox.setValue(duration / 1000)
                self.duration_spinbox.setEnabled(True)

            def on_error(error: QMediaPlayer.Error):
                logger.warning('could not detect media duration')
                self.duration_spinbox.setEnabled(True)
            self.media_player = QMediaPlayer()
            self.media_player.durationChanged.connect(duration_changed)
            self.media_player.errorOccurred.connect(on_error)
            self.media_player.setSource(QUrl.fromUserInput(self.media_filename))

        self.commandLinkButton.clicked.connect(self.gen_audio)
        self.buttonBox.clicked.connect(self.buttonClicked)
        self.file_picker_button.clicked.connect(self.open_file_picker)

    def join_worker(self):
        if self.worker:
            logger.debug('Requesting worker interruption.')
            self.worker.requestInterruption()
            self.worker.wait()

    def gen_audio(self):
        self.join_worker()

        samplerate = int(self.samplerate_spinbox.currentText())
        duration_in_s = float(self.duration_spinbox.value())
        duration_in_samples = int(samplerate * duration_in_s)

        self.progressBar.setMaximum(int(duration_in_s))
        self.progressBar.setValue(5)
        self.progressBar.setFormat("%v/%m")

        epoch = time.time() + 100
        dummy_mapper = DummyTimestamMapper(epoch)

        filename = self.file_edit.text()
        if not filename:
            logger.error('No valid filename chosen')
            return

        algorithm_factory = AlgorithmFactory(
            self.mainwindow,
            self.kit,
            self.script_mapping_model,
            dummy_mapper,
            dummy_mapper,
            load_funscripts=True,
            create_for_bake=True
        )
        algo = algorithm_factory.create_algorithm(self.device)

        class Worker(QThread):
            def __init__(self, parent):
                super(Worker, self).__init__(parent)

            def run(self) -> None:
                logger.info('bake audio started.')
                logger.info(f'target file: {filename}')
                self.progress.emit(0)
                start_time = time.time()
                try:
                    _, ext = os.path.splitext(filename)
                    if ext.lower() == 'mp3':
                        # use constant instead of variable bitrate for mp3
                        # to improve seeking accuracy in VLC and other players
                        compression_level = 0.9
                        bitrate_mode = 'CONSTANT'
                    else:
                        compression_level = None
                        bitrate_mode = None

                    file = sf.SoundFile(filename, mode='w', samplerate=samplerate, channels=algo.channel_count(),
                                        compression_level=compression_level, bitrate_mode=bitrate_mode)
                except TypeError as e:
                    logger.error("Could not open output file. Error message is:")
                    logger.error(e.__str__())
                    return

                # TODO: for a 3 hour file this allocates 4GB of data, which is completely unnecessary
                timeline = np.linspace(0, duration_in_s, duration_in_samples) + epoch
                samples_processed = 0
                for chunk in chunker(timeline, int(samplerate/10)):
                    if self.isInterruptionRequested():
                        logger.warning('bake audio interrupted by user')
                        break
                    samples_processed += len(chunk)
                    self.progress.emit(int(samples_processed / samplerate))
                    data = np.vstack(algo.generate_audio(samplerate, chunk, chunk)).T
                    file.write(data)
                file.close()
                end_time = time.time()
                elapsed_time = end_time - start_time
                if not self.isInterruptionRequested():
                    logger.info(f'bake {duration_in_s:.1f} seconds of audio in {elapsed_time:.1f} seconds ({duration_in_s / elapsed_time:.1f}x realtime)')

            progress = QtCore.Signal(int)

        self.worker = Worker(self)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.finished.connect(self.progressBar.reset)
        self.worker.start()

    def open_file_picker(self):
        dlg = FileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilters(['Audio files (*.wav, *.mp3, *.ogg, *)'])

        if dlg.exec():
            filenames = dlg.selectedFiles()
            if filenames:
                self.file_edit.setText(filenames[0])

    def buttonClicked(self, button: QAbstractButton):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.RejectRole:
            self.join_worker()
            self.reject()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.join_worker()
        event.accept()

