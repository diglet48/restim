from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg

from qt_ui.stim_config import PositionParameters, CalibrationParameters
from qt_ui.waveform_details_widget_ui import Ui_WaveformDetails

from stim_math import threephase, calibration

class WaveformDetailsWidget(QtWidgets.QWidget, Ui_WaveformDetails):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.calibration = None

        self.updatePositionParameters(PositionParameters(0, 0))

    def updateCalibrationParameters(self, calibration_params: CalibrationParameters):
        self.calibration = calibration.ThirteenPointCalibration([
            calibration_params.edge_0_3pi,
            calibration_params.edge_1_3pi,
            calibration_params.edge_2_3pi,
            calibration_params.edge_3_3pi,
            calibration_params.edge_4_3pi,
            calibration_params.edge_5_3pi,
            calibration_params.mid_0_3pi,
            calibration_params.mid_1_3pi,
            calibration_params.mid_2_3pi,
            calibration_params.mid_3_3pi,
            calibration_params.mid_4_3pi,
            calibration_params.mid_5_3pi,
            calibration_params.center])

    def updatePositionParameters(self, position_params: PositionParameters):
        L, R, center, phase_shift = threephase.ContinuousSineWaveform.channel_amplitude(
            np.array([position_params.alpha]),
            np.array([position_params.beta]))

        intensity = threephase.ContinuousSineWaveform.intensity(
            np.array([position_params.alpha]),
            np.array([position_params.beta]))[0]

        def format_amplitude(f): return "{:.2f}".format(f)
        def format_angle(f): return "{:.0f}°".format(f / np.pi * 180)

        scale = 1
        if self.calibration is not None:
            scale = self.calibration.get_scale(position_params.alpha, position_params.beta)
        self.scale_label.setText(format_amplitude(scale))

        self.left_amplitude_label.setText(format_amplitude(L[0] / intensity))
        self.right_amplitude_label.setText(format_amplitude(R[0] / intensity))
        self.center_amplitude_label.setText(format_amplitude(center[0] / intensity))
        self.phase_label.setText(format_angle(phase_shift[0]))

        self.alpha_label.setText(format_amplitude(position_params.alpha))
        self.beta_label.setText(format_amplitude(position_params.beta))

        self.r_label.setText(format_amplitude((position_params.alpha**2 + position_params.beta**2)**.5))
        self.theta_label.setText(format_angle(np.arctan2(position_params.beta, position_params.alpha)))

        N, L, R = threephase.ContinuousSineWaveform.electrode_amplitude(
            np.array([position_params.alpha]),
            np.array([position_params.beta]))

        self.neutral_label.setText(format_amplitude(N[0] / intensity / (3**.5 / 3)))
        self.left_label.setText(format_amplitude(L[0] / intensity / (3**.5 / 3)))
        self.right_label.setText(format_amplitude(R[0] / intensity / (3**.5 / 3)))




