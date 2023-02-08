from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg

from qt_ui.stim_config import PositionParameters
from qt_ui.waveform_details_widget_ui import Ui_WaveformDetails

from stim_math import threephase

class WaveformDetailsWidget(QtWidgets.QWidget, Ui_WaveformDetails):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.updatePositionParameters(PositionParameters(0, 0))

    def updatePositionParameters(self, position_params: PositionParameters):
        a, b, c, phase_shift = threephase.generate_3_dof_details(
            np.array([position_params.alpha]),
            np.array([position_params.beta]))

        def format_amplitude(f): return "{:.2f}".format(f)
        def format_angle(f): return "{:.0f}°".format(f / np.pi * 180)


        self.left_amplitude_label.setText(format_amplitude(a[0]))
        self.right_amplitude_label.setText(format_amplitude(b[0]))
        self.phase_label.setText(format_angle(phase_shift[0]))
        self.center_amplitude_label.setText(format_amplitude(c[0]))

        self.alpha_label.setText(format_amplitude(position_params.alpha))
        self.beta_label.setText(format_amplitude(position_params.beta))



