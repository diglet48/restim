from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
from PyQt5.QtCore import QSettings

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_ui.stim_config import ModulationParameters
import stim_math.limits
from stim_math.amplitude_modulation import SineModulation


SETTING_CARRIER_FREQUENCY = 'carrier/carrier_frequency'
SETTING_MOD1_ENABLED = 'carrier/modulation_1_enabled'
SETTING_MOD1_FREQUENCY = 'carrier/modulation_1_frequency'
SETTING_MOD1_MODULATION = 'carrier/modulation_1_strength'
SETTING_MOD1_LR_BIAS = 'carrier/modulation_1_high_low_bias'
SETTING_MOD1_HL_BIAS = 'carrier/modulation_1_left_right_bias'
SETTING_MOD1_RANDOM = 'carrier/modulation_1_random'
SETTING_MOD2_ENABLED = 'carrier/modulation_2_enabled'
SETTING_MOD2_FREQUENCY = 'carrier/modulation_2_frequency'
SETTING_MOD2_MODULATION = 'carrier/modulation_2_strength'
SETTING_MOD2_LR_BIAS = 'carrier/modulation_2_high_low_bias'
SETTING_MOD2_HL_BIAS = 'carrier/modulation_2_left_right_bias'
SETTING_MOD2_RANDOM = 'carrier/modulation_2_random'


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

        def create_modulation_signal(timeline, frequency, modulation, l_r_bias, h_l_bias):
            theta = timeline * 2 * np.pi * frequency
            m = SineModulation(theta, modulation, l_r_bias, h_l_bias)
            return m.envelope()

            # return (np.cos(timeline * (2 * np.pi * frequency)) - 1) * 0.5 * modulation + 1.0

        # y = np.cos(t * 2 * np.pi * parameters.carrier_frequency)
        y = np.full_like(t, 1.0)
        if parameters.modulation_1_enabled:
            y *= create_modulation_signal(t, parameters.modulation_1_freq, parameters.modulation_1_modulation, parameters.modulation_1_left_right_bias, parameters.modulation_1_high_low_bias)
        if parameters.modulation_2_enabled:
            y *= create_modulation_signal(t, parameters.modulation_2_freq, parameters.modulation_2_modulation, parameters.modulation_2_left_right_bias, parameters.modulation_2_high_low_bias)

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
        self.settings = QSettings()

        l = QtWidgets.QFormLayout(self)
        l.setObjectName("FormLayout")
        self.mpl_canvas = MyStaticMplCanvas(self, width=7, height=3, dpi=100)
        l.addWidget(self.mpl_canvas)

        gbc = QtWidgets.QGroupBox("Carrier", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        gbc_l.setObjectName("FormLayout carrier groupbox")
        carrier_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.Carrier.min,
                                                  maximum=stim_math.limits.Carrier.max)
        carrier_slider.setValue(self.settings.value(SETTING_CARRIER_FREQUENCY, 700, float))
        carrier_slider_label = QtWidgets.QLabel("carrier frequency [Hz]")
        gbc_l.addRow(carrier_slider_label, carrier_slider)
        gbc.setLayout(gbc_l)
        l.addWidget(gbc)

        gb1 = QtWidgets.QGroupBox("Modulation 1", self, checkable=True)
        gb1.setChecked(self.settings.value(SETTING_MOD1_ENABLED, True, bool))
        gb1_l = QtWidgets.QFormLayout(gb1)
        gb1_l.setObjectName("FormLayout modulation 1")
        freq1_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.ModulationFrequency.min,
                                                maximum=stim_math.limits.ModulationFrequency.max)
        freq1_slider.setValue(self.settings.value(SETTING_MOD1_FREQUENCY, 0, float))
        freq1_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb1_l.addRow(freq1_slider_label, freq1_slider)
        mod1_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        mod1_slider.setValue(self.settings.value(SETTING_MOD1_MODULATION, 0, float))
        mod1_slider_label = QtWidgets.QLabel("modulation [%]")
        gb1_l.addRow(mod1_slider_label, mod1_slider)
        bias1_left_right_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias1_left_right_slider.setValue(self.settings.value(SETTING_MOD1_LR_BIAS, 0, float))
        bias1_left_right_slider_label = QtWidgets.QLabel("bias left-right [%]")
        gb1_l.addRow(bias1_left_right_slider_label, bias1_left_right_slider)
        bias1_high_low_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias1_high_low_slider.setValue(self.settings.value(SETTING_MOD1_HL_BIAS, 0, float))
        bias1_high_low_slider_label = QtWidgets.QLabel("bias high-low [%]")
        gb1_l.addRow(bias1_high_low_slider_label, bias1_high_low_slider)
        random1_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        random1_slider.setValue(self.settings.value(SETTING_MOD1_RANDOM, 0, float))
        random1_slider_label = QtWidgets.QLabel("random [%]")
        gb1_l.addRow(random1_slider_label, random1_slider)
        gb1.setLayout(gb1_l)
        l.addWidget(gb1)

        gb2 = QtWidgets.QGroupBox("Modulation 2", self, checkable=True)
        gb2.setChecked(self.settings.value(SETTING_MOD2_ENABLED, True, bool))
        gb2_l = QtWidgets.QFormLayout(gb2)
        gb2_l.setObjectName("FormLayout modulation 2")
        freq2_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.ModulationFrequency.min,
                                                maximum=stim_math.limits.ModulationFrequency.max)
        freq2_slider.setValue(self.settings.value(SETTING_MOD2_FREQUENCY, 0, float))
        freq2_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb2_l.addRow(freq2_slider_label, freq2_slider)
        mod2_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        mod2_slider.setValue(self.settings.value(SETTING_MOD2_MODULATION, 0, float))
        mod2_slider_label = QtWidgets.QLabel("modulation [%]")
        gb2_l.addRow(mod2_slider_label, mod2_slider)
        bias2_left_right_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias2_left_right_slider.setValue(self.settings.value(SETTING_MOD2_LR_BIAS, 0, float))
        bias2_left_right_slider_label = QtWidgets.QLabel("bias left-right [%]")
        gb2_l.addRow(bias2_left_right_slider_label, bias2_left_right_slider)
        bias2_high_low_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias2_high_low_slider.setValue(self.settings.value(SETTING_MOD2_HL_BIAS, 0, float))
        bias2_high_low_slider_label = QtWidgets.QLabel("bias high-low [%]")
        gb2_l.addRow(bias2_high_low_slider_label, bias2_high_low_slider)
        random2_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        random2_slider.setValue(self.settings.value(SETTING_MOD2_RANDOM, 0, float))
        random2_slider_label = QtWidgets.QLabel("random [%]")
        gb2_l.addRow(random2_slider_label, random2_slider)
        gb2.setLayout(gb2_l)
        l.addWidget(gb2)

        gb3 = QtWidgets.QGroupBox("Modulation 3 (pulses)", self, checkable=True)
        # gb3.setChecked(self.settings.value(SETTING_MOD3_ENABLED, True, bool))
        gb3_l = QtWidgets.QFormLayout(gb3)
        gb3_l.setObjectName("FormLayout modulation 3")
        freq3_slider = QtWidgets.QDoubleSpinBox(minimum=1, # TODO: limits
                                                maximum=stim_math.limits.ModulationFrequency.max)
        # freq3_slider.setValue(self.settings.value(SETTING_MOD3_FREQUENCY, 0, float))
        freq3_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb3_l.addRow(freq3_slider_label, freq3_slider)
        mod3_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        # mod3_slider.setValue(self.settings.value(SETTING_MOD3_MODULATION, 0, float))
        mod3_slider_label = QtWidgets.QLabel("modulation [%]")
        gb3_l.addRow(mod3_slider_label, mod3_slider)
        pulse_width3_slider = QtWidgets.QDoubleSpinBox(minimum=3,
                                                      maximum=50)
        pulse_width3_slider.setSingleStep(0.1)
        # pulse_width3_slider.setValue(self.settings.value(SETTING_MOD3_FREQUENCY, 0, float))
        pulse_width3_label = QtWidgets.QLabel("pulse width [carrier cycles]")
        gb3_l.addRow(pulse_width3_label, pulse_width3_slider)
        random3_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        # random3_slider.setValue(self.settings.value(SETTING_MOD3_RANDOM, 0, float))
        random3_slider_label = QtWidgets.QLabel("random [%]")
        gb3_l.addRow(random3_slider_label, random3_slider)
        gb3.setLayout(gb3_l)
        l.addWidget(gb3)


        carrier_slider.valueChanged.connect(self.settings_changed)
        gb1.toggled.connect(self.settings_changed)
        freq1_slider.valueChanged.connect(self.settings_changed)
        mod1_slider.valueChanged.connect(self.settings_changed)
        bias1_left_right_slider.valueChanged.connect(self.settings_changed)
        bias1_high_low_slider.valueChanged.connect(self.settings_changed)
        random1_slider.valueChanged.connect(self.settings_changed)
        gb2.toggled.connect(self.settings_changed)
        freq2_slider.valueChanged.connect(self.settings_changed)
        mod2_slider.valueChanged.connect(self.settings_changed)
        bias2_left_right_slider.valueChanged.connect(self.settings_changed)
        bias2_high_low_slider.valueChanged.connect(self.settings_changed)
        random2_slider.valueChanged.connect(self.settings_changed)
        gb3.toggled.connect(self.settings_changed)
        freq3_slider.valueChanged.connect(self.settings_changed)
        mod3_slider.valueChanged.connect(self.settings_changed)
        pulse_width3_slider.valueChanged.connect(self.settings_changed)
        random3_slider.valueChanged.connect(self.settings_changed)

        self.carrier = carrier_slider
        self.gb1 = gb1
        self.freq1_slider = freq1_slider
        self.mod1_slider = mod1_slider
        self.bias1_left_right_slider = bias1_left_right_slider
        self.bias1_high_low_slider = bias1_high_low_slider
        self.random1_slider = random1_slider
        self.gb2 = gb2
        self.freq2_slider = freq2_slider
        self.mod2_slider = mod2_slider
        self.bias2_left_right_slider = bias2_left_right_slider
        self.bias2_high_low_slider = bias2_high_low_slider
        self.random2_slider = random2_slider
        self.gb3 = gb3
        self.freq3_slider = freq3_slider
        self.mod3_slider = mod3_slider
        self.pulse_width3_slider = pulse_width3_slider
        self.random3_slider = random3_slider

        self.modulationSettingsChanged.connect(self.mpl_canvas.updateParams)
        self.settings_changed()

    modulationSettingsChanged = QtCore.pyqtSignal(ModulationParameters)

    def settings_changed(self):
        params = ModulationParameters(
            self.carrier.value(),
            self.gb1.isChecked(),
            self.freq1_slider.value(),
            self.mod1_slider.value() / 100.0,
            self.bias1_left_right_slider.value() / 100.0,
            self.bias1_high_low_slider.value() / 100.0,
            self.random1_slider.value() / 100.0,
            self.gb2.isChecked(),
            self.freq2_slider.value(),
            self.mod2_slider.value() / 100.0,
            self.bias2_left_right_slider.value() / 100.0,
            self.bias2_high_low_slider.value() / 100.0,
            self.random2_slider.value() / 100.0,
            self.gb3.isChecked(),
            self.freq3_slider.value(),
            self.mod3_slider.value() / 100.0,
            self.pulse_width3_slider.value(),
            self.random3_slider.value() / 100.0,
        )
        self.modulationSettingsChanged.emit(params)

        self.settings.setValue(SETTING_CARRIER_FREQUENCY, self.carrier.value())
        self.settings.setValue(SETTING_MOD1_ENABLED, self.gb1.isChecked())
        self.settings.setValue(SETTING_MOD1_FREQUENCY, self.freq1_slider.value())
        self.settings.setValue(SETTING_MOD1_MODULATION, self.mod1_slider.value())
        self.settings.setValue(SETTING_MOD1_LR_BIAS, self.bias1_left_right_slider.value())
        self.settings.setValue(SETTING_MOD1_HL_BIAS, self.bias1_high_low_slider.value())
        self.settings.setValue(SETTING_MOD1_RANDOM, self.random1_slider.value())
        self.settings.setValue(SETTING_MOD2_ENABLED, self.gb2.isChecked())
        self.settings.setValue(SETTING_MOD2_FREQUENCY, self.freq2_slider.value())
        self.settings.setValue(SETTING_MOD2_MODULATION, self.mod2_slider.value())
        self.settings.setValue(SETTING_MOD2_LR_BIAS, self.bias2_left_right_slider.value())
        self.settings.setValue(SETTING_MOD2_HL_BIAS, self.bias2_high_low_slider.value())
        self.settings.setValue(SETTING_MOD2_RANDOM, self.random2_slider.value())
        # TODO: save mod3 settings
