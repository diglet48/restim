from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
from stim_math.threephase_coordinate_transform import ThreePhaseCoordinateTransform, \
    ThreePhaseCoordinateTransformMapToEdge
from stim_math.threephase_parameter_manager import ThreephaseParameterManager

matplotlib.use('Qt5Agg')
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen, QMouseEvent
from PyQt5 import QtCore, QtWidgets, QtSvg

from qt_ui.stim_config import PositionParameters, CalibrationParameters
from qt_ui.waveform_details_widget_ui import Ui_WaveformDetails

from stim_math import threephase, trig


class WaveformDetailsWidget(QtWidgets.QWidget, Ui_WaveformDetails):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        self.calibration = None
        self.config = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(int(1000 / 10.0))

        self.last_params = (None, None)

    def set_config_manager(self, config: ThreephaseParameterManager):
        self.config = config

    def refresh(self):
        if self.config is None:
            return

        if self.isVisible():
            self.timer.setInterval(1000 // 20)
        else:
            self.timer.setInterval(1000 // 5)
            return

        alpha = self.config.alpha.last_value()
        beta = self.config.beta.last_value()

        if self.config.transform_enabled.last_value():
            transform = ThreePhaseCoordinateTransform(
                self.config.transform_rotation_degrees.last_value(),
                self.config.transform_mirror.last_value(),
                self.config.transform_top_limit.last_value(),
                self.config.transform_bottom_limit.last_value(),
                self.config.transform_left_limit.last_value(),
                self.config.transform_right_limit.last_value(),
            )
            [alpha], [beta] = transform.transform([alpha], [beta])
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm
        if self.config.map_to_edge_enabled.last_value():
            transform = ThreePhaseCoordinateTransformMapToEdge(
                self.config.map_to_edge_start.last_value(),
                self.config.map_to_edge_length.last_value(),
                self.config.map_to_edge_invert.last_value(),
            )
            alpha, beta = transform.transform(alpha, beta)
            norm = np.clip(trig.norm(alpha, beta), 1.0, None)
            alpha /= norm
            beta /= norm

        if self.last_params == (alpha, beta):
            return
        self.last_params = (alpha, beta)

        L, R, center, phase_shift = threephase.ThreePhaseSignalGenerator.channel_amplitude(
            np.array([alpha]),
            np.array([beta]))

        def format_amplitude(f): return "{:.2f}".format(f)
        def format_angle(f): return "{:.0f}°".format(f / np.pi * 180)

        self.left_amplitude_label.setText(format_amplitude(L[0]))
        self.right_amplitude_label.setText(format_amplitude(R[0]))
        self.center_amplitude_label.setText(format_amplitude(center[0]))
        self.phase_label.setText(format_angle(phase_shift[0]))

        self.alpha_label.setText(format_amplitude(alpha))
        self.beta_label.setText(format_amplitude(beta))

        self.r_label.setText(format_amplitude((alpha**2 + beta**2)**.5))
        self.theta_label.setText(format_angle(np.arctan2(beta, alpha)))

        N, L, R = threephase.ThreePhaseSignalGenerator.electrode_amplitude(
            np.array([alpha]),
            np.array([beta]))

        self.neutral_label.setText(format_amplitude(N[0] / (3**.5 / 3)))
        self.left_label.setText(format_amplitude(L[0] / (3**.5 / 3)))
        self.right_label.setText(format_amplitude(R[0] / (3**.5 / 3)))




