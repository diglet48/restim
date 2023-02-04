from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_ui.stim_config import ModulationParameters


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        # t = arange(0.0, 3.0, 0.01)
        # s = sin(2*pi*t)
        # self.axes.plot(t, s)
        # self.axes.set_xlim((0, 1))
        pass

    def updateParams(self, parameters: ModulationParameters):
        t = np.linspace(0, 1, 10000)

        def create_modulation_signal(timeline, frequency, modulation):
            return (np.cos(timeline * (2 * np.pi * frequency)) - 1) * 0.5 * modulation + 1.0

        # y = np.cos(t * 2 * np.pi * parameters.carrier_frequency)
        y = np.full_like(t, 1.0)
        if parameters.modulation_1_enabled:
            y *= create_modulation_signal(t, parameters.modulation_1_freq, parameters.modulation_1_modulation)
        if parameters.modulation_2_enabled:
            y *= create_modulation_signal(t, parameters.modulation_2_freq, parameters.modulation_2_modulation)

        self.axes.cla()
        self.axes.set_title("Amplitude modulation")
        self.axes.set_xlim((0, 1))
        self.axes.set_ylim((0, 1.1))
        # self.axes.plot(t, y, 'r')
        self.axes.fill_between(t, y, 0)
        self.draw()


class ModulationSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QFormLayout(self)
        sc = MyStaticMplCanvas(self, width=7, height=3, dpi=100)
        self.sc = sc
        l.addWidget(sc)

        gbc = QtWidgets.QGroupBox("Carrier", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        carrier_slider = QtWidgets.QDoubleSpinBox(minimum=300, maximum=1000)
        carrier_slider.setValue(900)
        carrier_slider_label = QtWidgets.QLabel("carrier frequency [Hz]")
        gbc_l.addRow(carrier_slider_label, carrier_slider)
        gbc.setLayout(gbc_l)
        l.addWidget(gbc)


        gb1 = QtWidgets.QGroupBox("Modulation 1", self, checkable=True)
        gb1_l = QtWidgets.QFormLayout(gb1)
        freq1_slider = QtWidgets.QDoubleSpinBox()
        freq1_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb1_l.addRow(freq1_slider_label, freq1_slider)
        mod1_slider = QtWidgets.QDoubleSpinBox()
        mod1_slider_label = QtWidgets.QLabel("modulation [%]")
        gb1_l.addRow(mod1_slider_label, mod1_slider)
        gb1.setLayout(gb1_l)
        l.addWidget(gb1)

        gb2 = QtWidgets.QGroupBox("Modulation 2", self, checkable=True)
        gb2_l = QtWidgets.QFormLayout(self)
        freq2_slider = QtWidgets.QDoubleSpinBox()
        freq2_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb2_l.addRow(freq2_slider_label, freq2_slider)
        mod2_slider = QtWidgets.QDoubleSpinBox()
        mod2_slider_label = QtWidgets.QLabel("modulation [%]")
        gb2_l.addRow(mod2_slider_label, mod2_slider)
        gb2.setLayout(gb2_l)
        l.addWidget(gb2)


        carrier_slider.valueChanged.connect(self.settings_changed)
        gb1.toggled.connect(self.settings_changed)
        freq1_slider.valueChanged.connect(self.settings_changed)
        mod1_slider.valueChanged.connect(self.settings_changed)
        gb2.toggled.connect(self.settings_changed)
        freq2_slider.valueChanged.connect(self.settings_changed)
        mod2_slider.valueChanged.connect(self.settings_changed)

        self.carrier = carrier_slider
        self.gb1 = gb1
        self.freq1_slider = freq1_slider
        self.mod1_slider = mod1_slider
        self.gb2 = gb2
        self.freq2_slider = freq2_slider
        self.mod2_slider = mod2_slider


        self.modulationSettingsChanged.connect(self.sc.updateParams)
        self.settings_changed()

    modulationSettingsChanged = QtCore.pyqtSignal(ModulationParameters)

    def settings_changed(self):
        params = ModulationParameters(
            self.carrier.value(),
            self.gb1.isChecked(),
            self.freq1_slider.value(),
            self.mod1_slider.value() / 100.0,
            self.gb2.isChecked(),
            self.freq2_slider.value(),
            self.mod2_slider.value() / 100.0,
        )
        self.modulationSettingsChanged.emit(params)
