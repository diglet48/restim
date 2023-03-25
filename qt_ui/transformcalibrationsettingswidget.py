from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_ui.stim_config import TransformParameters

from stim_math.hardware_calibration import HardwareCalibration


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.compute_initial_figure()

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        self.scatter = None
        self.line = None
        super(MyStaticMplCanvas, self).__init__(*args, **kwargs)

    def compute_initial_figure(self):
        self.axes.cla()

        self.axes.set_title("Calibration")
        self.axes.set_xlim((-15, 15))
        self.axes.set_ylim((-15, 15))
        self.scatter = self.axes.scatter([0], [0])

        alpha, beta = self.compute_line(TransformParameters(0, 0, 0))

        t = np.linspace(0, 2 * np.pi, 101)
        self.axes.plot(np.cos(t) * 10, np.sin(t)*10, color='gray')
        self.line = self.axes.plot(beta, alpha)[0]

        self.axes.grid(True)
        self.axes.set_box_aspect(1)
        self.draw()

    def compute_line(self, parameters: TransformParameters):
        t = np.linspace(0, 2 * np.pi, 101)
        hw = HardwareCalibration(parameters.up_down, parameters.left_right)
        alpha, beta = hw.contour_in_ab(t)

        r = np.sqrt(alpha ** 2 + beta ** 2)[:51]
        t = t[:51] * 2
        alpha = np.cos(t) * r
        beta = np.sin(t) * r
        alpha *= 10
        beta *= 10

        return alpha, beta

    def updateParams(self, parameters: TransformParameters):
        alpha, beta = self.compute_line(parameters)
        self.line.set_data(beta, alpha)
        self.scatter.set_offsets(np.c_ [parameters.left_right, parameters.up_down])
        self.draw()


class TransformCalibrationSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QFormLayout(self)
        sc = MyStaticMplCanvas(self, width=7, height=3, dpi=100)
        self.sc = sc
        l.addWidget(sc)

        gbc = QtWidgets.QGroupBox("Calibration", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        neutral_power_slider = QtWidgets.QDoubleSpinBox(minimum=-15, maximum=15)
        neutral_power_slider.setSingleStep(0.1)
        neutral_power_slider.setValue(0)
        neutral_power_label = QtWidgets.QLabel("Neutral power [dB]")
        gbc_l.addRow(neutral_power_label, neutral_power_slider)

        right_power_slider = QtWidgets.QDoubleSpinBox(minimum=-15, maximum=15)
        right_power_slider.setSingleStep(0.1)
        right_power_slider.setValue(0)
        right_power_label = QtWidgets.QLabel("Right power [dB]")
        gbc_l.addRow(right_power_label, right_power_slider)

        center_power_slider = QtWidgets.QDoubleSpinBox(minimum=-15, maximum=15)
        center_power_slider.setSingleStep(0.1)
        center_power_slider.setValue(-0.7)
        center_power_label = QtWidgets.QLabel("Center power [dB]")
        gbc_l.addRow(center_power_label, center_power_slider)
        gbc.setLayout(gbc_l)
        l.addWidget(gbc)

        neutral_power_slider.valueChanged.connect(self.settings_changed)
        right_power_slider.valueChanged.connect(self.settings_changed)
        center_power_slider.valueChanged.connect(self.settings_changed)

        self.neutral = neutral_power_slider
        self.right = right_power_slider
        self.center = center_power_slider

        self.transformCalibrationSettingsChanged.connect(self.sc.updateParams)
        self.settings_changed()

    transformCalibrationSettingsChanged = QtCore.pyqtSignal(TransformParameters)

    def settings_changed(self):
        params = TransformParameters(
            self.neutral.value(),
            self.right.value(),
            self.center.value()
        )
        self.transformCalibrationSettingsChanged.emit(params)