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
            (0, 0, 1.0), # center
            (0 / 3 * np.pi, r / 2, 1.0),
            (1 / 3 * np.pi, r / 2, 1.0),
            (2 / 3 * np.pi, r / 2, 1.0),
            (3 / 3 * np.pi, r / 2, 1.0),
            (4 / 3 * np.pi, r / 2, 1.0),
            (5 / 3 * np.pi, r / 2, 1.0),
            (0/3 * np.pi, r, 1.0),
            (1/3 * np.pi, r, 1.0),
            (2/3 * np.pi, r, 1.0),
            (3/3 * np.pi, r, 1.0),
            (4/3 * np.pi, r, 1.0),
            (5/3 * np.pi, r, 1.0),
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

