import traceback
import os.path

from PySide6.QtWidgets import QDialog, QFileDialog

from qt_ui.simfile_conversion_dialog_ui import Ui_SimfileConversionDialog
from qt_ui.file_dialog import FileDialog
from funscript.funscript import Funscript

from simfile.simfile import Simfile
from simfile.conversion import notes_to_intensity, electrode_intensity_to_position_3p
from simfile.interpolation import interpolators

import numpy as np
from qt_ui import settings


class SimfileConversionDialog(QDialog, Ui_SimfileConversionDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.simfile_path = ''
        self.simfile = None

        for name, interp in interpolators:
            self.comboBox_interpolation.addItem(name, interp)

        self.comboBox_interpolation.setCurrentIndex(settings.simfile_conversion_atk_sus_rel_index.get())
        self.checkBox_debug_scripts.setChecked(settings.simfile_conversion_output_debug_scripts.get())

        self.toolButton.clicked.connect(self.open_file_dialog)
        self.pushButton.clicked.connect(self.convert)

    def open_file_dialog(self):
        dialog = FileDialog(self)
        dialog.setWindowTitle('Select simfile')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(['*.sm'])
        ret = dialog.exec()

        files = dialog.selectedFiles()
        if ret and len(files):
            dir = files[0]
            self.file_selected(dir)

    def file_selected(self, filename):
        self.simfile_path = filename
        self.lineEdit_funscript.setText(filename)
        self.comboBox_notes.clear()

        try:
            self.simfile = Simfile.from_file(filename)
            for notes in self.simfile.notes:
                self.comboBox_notes.addItem(
                    f"{notes.steps_type} / {notes.difficulty}",
                    notes
                )
        except Exception as e:
            traceback.print_exception(e)
            self.plainTextEdit.setText(''.join(traceback.format_exception(e)))

    def convert(self):
        self.save_settings()

        self.plainTextEdit.clear()
        if self.comboBox_notes.count() == 0:
            self.plainTextEdit.setPlainText('No charts found in file')
            return

        self.plainTextEdit.appendPlainText('converting ' + self.lineEdit_funscript.text() + '...')

        notes = self.comboBox_notes.currentData()
        interpolator = self.comboBox_interpolation.currentData()

        try:
            x, (a, b, c, d) = notes_to_intensity(notes, interpolator)
            alpha, beta = electrode_intensity_to_position_3p(a, b, c)
        except Exception as e:
            traceback.print_exception(e)
            self.plainTextEdit.setText(''.join(traceback.format_exception(e)))
            return

        alpha = np.array(alpha) / 2 + 0.5
        beta = np.array(beta) / 2 + 0.5

        if len(self.simfile.bpms.bpms) > 1:
            self.plainTextEdit.appendPlainText(f'simfile contains multiple BPM, which is not currently supported.')

        bpm = self.simfile.bpms.bpms[0][1]
        offset = self.simfile.offset
        t = x * (4 * 60 / bpm) - offset

        if self.checkBox_debug_scripts.isChecked():
            self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('e1'))[1]}')
            Funscript(t, a).save_to_path(self.funscript_path('e1'))
            self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('e2'))[1]}')
            Funscript(t, b).save_to_path(self.funscript_path('e2'))
            self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('e3'))[1]}')
            Funscript(t, c).save_to_path(self.funscript_path('e3'))
            self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('e4'))[1]}')
            Funscript(t, d).save_to_path(self.funscript_path('e4'))

        self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('alpha'))[1]}')
        Funscript(t, alpha).save_to_path(self.funscript_path('alpha'))
        self.plainTextEdit.appendPlainText(f'writing {os.path.split(self.funscript_path('beta'))[1]}')
        Funscript(t, beta).save_to_path(self.funscript_path('beta'))

    def funscript_path(self, affix):
        base, ext = os.path.splitext(self.simfile_path)
        return f"{base}.{affix}.funscript"

    def save_settings(self):
        settings.simfile_conversion_output_debug_scripts.set(self.checkBox_debug_scripts.isChecked())
        settings.simfile_conversion_atk_sus_rel_index.set(self.comboBox_interpolation.currentIndex())
