import re
import traceback

from PyQt5.QtWidgets import QDialog, QFileDialog

from qt_ui.funscript_conversion_ui import Ui_FunscriptConversionDialog
from qt_ui.file_dialog import FileDialog
from funscript.funscript import Funscript
from funscript.funscript_conversion import convert_1d_to_2d

KEY_FILEPICKER_LAST_DIR = "funscript_conversion/last_dir"


class FunscriptConversionDialog(QDialog, Ui_FunscriptConversionDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.toolButton.clicked.connect(self.open_file_dialog)

        self.pushButton.clicked.connect(self.convert)

    def open_file_dialog(self):
        dialog = FileDialog(self)
        dialog.setWindowTitle('Select directory')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(['*.funscript'])
        ret = dialog.exec()

        files = dialog.selectedFiles()
        if ret and len(files):
            dir = files[0]
            self.file_selected(dir)

    def file_selected(self, filename):
        self.lineEdit_funscript.setText(filename)
        self.lineEdit_alpha.setText(re.sub("\.funscript$", ".alpha.funscript", filename))
        self.lineEdit_beta.setText(re.sub("\.funscript$", ".beta.funscript", filename))

    def convert(self):
        self.textEdit.clear()
        self.textEdit.append('converting ' + self.lineEdit_funscript.text() + '...')
        try:
            original_funscript = Funscript.from_file(self.lineEdit_funscript.text())
            t, alpha, beta = convert_1d_to_2d(original_funscript)
            alpha_funscript = Funscript(t, alpha)
            beta_funscript = Funscript(t, beta)
            alpha_funscript.save_to_path(self.lineEdit_alpha.text())
            beta_funscript.save_to_path(self.lineEdit_beta.text())
            self.textEdit.append("conversion completed")
        except Exception as e:
            traceback.print_exception(e)
            self.textEdit.setText(''.join(traceback.format_exception(e)))
