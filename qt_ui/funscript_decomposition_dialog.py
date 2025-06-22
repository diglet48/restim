import re
import traceback
from enum import Enum
import pathlib
import numpy as np

from PySide6.QtWidgets import QDialog, QFileDialog

import stim_math.transforms
import stim_math.transforms_4
from qt_ui.funscript_decomposition_ui import Ui_FunscriptDecompositionDialog
from qt_ui.file_dialog import FileDialog
from funscript.funscript import Funscript


class ConversionType(Enum):
    AB_TO_E123 = 1
    E123_TO_AB = 2
    ABC_TO_E1234 = 3
    E1234_TO_ABC = 4


class FunscriptDecompositionDialog(QDialog, Ui_FunscriptDecompositionDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.toolButton.clicked.connect(self.open_file_dialog)
        self.pushButton.clicked.connect(self.convert)

        self.comboBox_action.clear()
        self.comboBox_action.addItem("alpha, beta -> e1, e2, e3", ConversionType.AB_TO_E123)
        self.comboBox_action.addItem("e1, e2, e3  -> alpha, beta", ConversionType.E123_TO_AB)
        self.comboBox_action.addItem("alpha, beta, gamma -> e1, e2, e3, e4", ConversionType.ABC_TO_E1234)
        self.comboBox_action.addItem("e1, e2, e3, e4  -> alpha, beta, gamma", ConversionType.E1234_TO_ABC)

    def open_file_dialog(self):
        dialog = FileDialog(self)
        dialog.setWindowTitle('Select directory')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(['*.funscript'])
        ret = dialog.exec()

        files = dialog.selectedFiles()
        if ret and len(files):
            self.lineEdit_funscript.setText(files[0])

    def convert(self):
        self.textEdit.clear()

        try:
            if self.comboBox_action.currentData() == ConversionType.AB_TO_E123:
                self.convert_ab_to_e123()
            elif self.comboBox_action.currentData() == ConversionType.E123_TO_AB:
                self.convert_e123_to_ab()
            elif self.comboBox_action.currentData() == ConversionType.ABC_TO_E1234:
                self.convert_abc_to_e1234()
            elif self.comboBox_action.currentData() == ConversionType.E1234_TO_ABC:
                self.convert_e1234_to_abc()

            # original_funscript = Funscript.from_file(self.lineEdit_funscript.text())
            # random_direction_change_probability = self.random_direction_change_probability.value() / 100
            # t, alpha, beta = convert_1d_to_2d(original_funscript, random_direction_change_probability)
            # alpha_funscript = Funscript(t, alpha)
            # beta_funscript = Funscript(t, beta)
            # alpha_funscript.save_to_path(self.lineEdit_alpha.text())
            # beta_funscript.save_to_path(self.lineEdit_beta.text())
            self.textEdit.append("conversion completed")
        except Exception as e:
            traceback.print_exception(e)
            self.textEdit.setText(''.join(traceback.format_exception(e)))

    def funscript_path(self, suffix):
        path = pathlib.Path(self.lineEdit_funscript.text())
        if path.suffix == '.funscript':
            path = path.parent / path.stem
        return path.parent / (path.stem + f'.{suffix}.funscript')

    def convert_ab_to_e123(self):
        alpha_fs = Funscript.from_file(self.funscript_path('alpha'))
        beta_fs = Funscript.from_file(self.funscript_path('beta'))

        timestamps = np.union1d(alpha_fs.x, beta_fs.x)
        a = np.interp(timestamps, alpha_fs.x, alpha_fs.y) * 2 - 1
        b = np.interp(timestamps, beta_fs.x, beta_fs.y) * 2 - 1

        e1, e2, e3 = stim_math.transforms.ab_to_e123(a, b)
        Funscript(timestamps, e1).save_to_path(self.funscript_path('e1'))
        Funscript(timestamps, e2).save_to_path(self.funscript_path('e2'))
        Funscript(timestamps, e3).save_to_path(self.funscript_path('e3'))

    def convert_e123_to_ab(self):
        e1_fs = Funscript.from_file(self.funscript_path('e1'))
        e2_fs = Funscript.from_file(self.funscript_path('e2'))
        e3_fs = Funscript.from_file(self.funscript_path('e3'))

        timestamps = np.union1d(np.union1d(e1_fs.x, e2_fs.x), e3_fs.x)
        e1 = np.interp(timestamps, e1_fs.x, e1_fs.y)
        e2 = np.interp(timestamps, e2_fs.x, e2_fs.y)
        e3 = np.interp(timestamps, e3_fs.x, e3_fs.y)

        a, b = stim_math.transforms.e123_to_ab(e1, e2, e3)
        a = (a + 1) / 2
        b = (b + 1) / 2
        Funscript(timestamps, a).save_to_path(self.funscript_path('alpha'))
        Funscript(timestamps, b).save_to_path(self.funscript_path('beta'))

    def convert_abc_to_e1234(self):
        alpha_fs = Funscript.from_file(self.funscript_path('alpha'))
        beta_fs = Funscript.from_file(self.funscript_path('beta'))
        gamma_fs = Funscript.from_file(self.funscript_path('gamma'))

        timestamps = np.union1d(np.union1d(alpha_fs.x, beta_fs.x), gamma_fs.x)
        a = np.interp(timestamps, alpha_fs.x, alpha_fs.y) * 2 - 1
        b = np.interp(timestamps, beta_fs.x, beta_fs.y) * 2 - 1
        c = np.interp(timestamps, gamma_fs.x, gamma_fs.y) * 2 - 1

        e1, e2, e3, e4 = stim_math.transforms_4.abc_to_e1234(a, b, c)
        Funscript(timestamps, e1).save_to_path(self.funscript_path('e1'))
        Funscript(timestamps, e2).save_to_path(self.funscript_path('e2'))
        Funscript(timestamps, e3).save_to_path(self.funscript_path('e3'))
        Funscript(timestamps, e4).save_to_path(self.funscript_path('e4'))

    def convert_e1234_to_abc(self):
        e1_fs = Funscript.from_file(self.funscript_path('e1'))
        e2_fs = Funscript.from_file(self.funscript_path('e2'))
        e3_fs = Funscript.from_file(self.funscript_path('e3'))
        e4_fs = Funscript.from_file(self.funscript_path('e4'))

        timestamps = np.union1d(np.union1d(np.union1d(e1_fs.x, e2_fs.x), e3_fs.x), e4_fs.x)
        e1 = np.interp(timestamps, e1_fs.x, e1_fs.y)
        e2 = np.interp(timestamps, e2_fs.x, e2_fs.y)
        e3 = np.interp(timestamps, e3_fs.x, e3_fs.y)
        e4 = np.interp(timestamps, e4_fs.x, e4_fs.y)

        a, b, c = stim_math.transforms_4.e1234_to_abc(e1, e2, e3, e4)
        a = (a + 1) / 2
        b = (b + 1) / 2
        c = (c + 1) / 2
        Funscript(timestamps, a).save_to_path(self.funscript_path('alpha'))
        Funscript(timestamps, b).save_to_path(self.funscript_path('beta'))
        Funscript(timestamps, c).save_to_path(self.funscript_path('gamma'))

