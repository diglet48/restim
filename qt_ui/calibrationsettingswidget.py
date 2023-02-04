from __future__ import unicode_literals
import matplotlib
import numpy as np
# Make sure that we are using QT5
from qt_ui.stim_config import CalibrationParameters

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets


class CalibrationSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        frame = QtWidgets.QGroupBox(self)
        frame.setFixedWidth(350)
        frame.setFixedHeight(300)

        r = 110
        widget_positions = [
            (0, 0, 0.44), # center
            (0 / 3 * np.pi, r / 2, 0.38),
            (1 / 3 * np.pi, r / 2, 0.40),
            (2 / 3 * np.pi, r / 2, 0.48),
            (3 / 3 * np.pi, r / 2, 0.47),
            (4 / 3 * np.pi, r / 2, 0.46),
            (5 / 3 * np.pi, r / 2, 0.40),
            (0/3 * np.pi, r, 0.32),
            (1/3 * np.pi, r, 0.36),
            (2/3 * np.pi, r, 0.50),
            (3/3 * np.pi, r, 0.70),
            (4/3 * np.pi, r, 0.47),
            (5/3 * np.pi, r, 0.36),
        ]

        self.widgets = []

        for theta, r, init_value in widget_positions:
            spinbox = QtWidgets.QSpinBox(frame, value=100, minimum=0, maximum=100)
            x, y = int(155 - np.sin(theta) * r), int(140 - np.cos(theta) * r)
            spinbox.move(x, y)
            spinbox.setValue(int(init_value * 100))
            self.widgets.append(spinbox)

        for w in self.widgets:
            w.valueChanged.connect(self.settings_changed)

    calibrationSettingsChanged = QtCore.pyqtSignal(CalibrationParameters)

    def settings_changed(self):
        params = CalibrationParameters(
            *[w.value() / 100.0 for w in self.widgets]
        )
        self.calibrationSettingsChanged.emit(params)

