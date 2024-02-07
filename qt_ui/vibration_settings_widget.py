from __future__ import unicode_literals
import matplotlib
import numpy as np

# Make sure that we are using QT5
from PyQt5.QtCore import QSettings

matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import stim_math.limits
from stim_math.amplitude_modulation import SineModulation
from stim_math.axis import create_temporal_axis
from stim_math.audio_gen.params import VibrationParams

from qt_ui import settings


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

    def updateParams(self, vib_1: VibrationParams, vib_2: VibrationParams):
        t = np.linspace(0, 1, 10000)

        def create_vibration_signal(timeline, vib: VibrationParams):
            if not vib.enabled.last_value():
                return 1

            theta = timeline * 2 * np.pi * vib.frequency.last_value()
            m = SineModulation(theta, vib.strength.last_value(), vib.left_right_bias.last_value(), vib.high_low_bias.last_value())
            return m.envelope()

            # return (np.cos(timeline * (2 * np.pi * frequency)) - 1) * 0.5 * modulation + 1.0

        # y = np.cos(t * 2 * np.pi * parameters.carrier_frequency)
        y = np.full_like(t, 1.0)
        y *= create_vibration_signal(t, vib_1)
        y *= create_vibration_signal(t, vib_2)

        self.axes.cla()
        self.axes.set_title("Volume")
        self.axes.set_xlim((0, 1))
        self.axes.set_ylim((0, 1.1))
        # self.axes.plot(t, y, 'r')
        self.axes.fill_between(t, y, 0)
        self.draw()


class VibrationSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.settings = QSettings()

        self.vibration_1 = VibrationParams(
            create_temporal_axis(False, interpolation='step'),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
        )
        self.vibration_2 = VibrationParams(
            create_temporal_axis(False, interpolation='step'),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
            create_temporal_axis(0.0),
        )

        l = QtWidgets.QFormLayout(self)
        l.setObjectName("FormLayout")
        self.mpl_canvas = MyStaticMplCanvas(self, width=7, height=3, dpi=100)
        l.addWidget(self.mpl_canvas)

        gb1 = QtWidgets.QGroupBox("Vibration 1", self, checkable=True)
        gb1.setChecked(settings.vibration_1_enabled.get())
        gb1_l = QtWidgets.QFormLayout(gb1)
        gb1_l.setObjectName("FormLayout modulation 1")
        freq1_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.ModulationFrequency.min,
                                                maximum=stim_math.limits.ModulationFrequency.max)
        freq1_slider.setValue(settings.vibration_1_frequency.get())
        freq1_slider.setSingleStep(0.1)
        freq1_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb1_l.addRow(freq1_slider_label, freq1_slider)
        mod1_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        mod1_slider.setValue(settings.vibration_1_strength.get())
        mod1_slider_label = QtWidgets.QLabel("Strength [%]")
        gb1_l.addRow(mod1_slider_label, mod1_slider)
        bias1_left_right_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias1_left_right_slider.setValue(settings.vibration_1_left_right_bias.get())
        bias1_left_right_slider_label = QtWidgets.QLabel("bias left-right [%]")
        gb1_l.addRow(bias1_left_right_slider_label, bias1_left_right_slider)
        bias1_high_low_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias1_high_low_slider.setValue(settings.vibration_1_high_low_bias.get())
        bias1_high_low_slider_label = QtWidgets.QLabel("bias high-low [%]")
        gb1_l.addRow(bias1_high_low_slider_label, bias1_high_low_slider)
        random1_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        random1_slider.setValue(settings.vibration_1_random.get())
        random1_slider_label = QtWidgets.QLabel("random [%]")
        gb1_l.addRow(random1_slider_label, random1_slider)
        gb1.setLayout(gb1_l)
        l.addWidget(gb1)

        gb2 = QtWidgets.QGroupBox("Vibration 2", self, checkable=True)
        gb2.setChecked(settings.vibration_2_enabled.get())
        gb2_l = QtWidgets.QFormLayout(gb2)
        gb2_l.setObjectName("FormLayout modulation 2")
        freq2_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.ModulationFrequency.min,
                                                maximum=stim_math.limits.ModulationFrequency.max)
        freq2_slider.setValue(settings.vibration_2_frequency.get())
        freq2_slider.setSingleStep(0.1)
        freq2_slider_label = QtWidgets.QLabel("frequency [Hz]")
        gb2_l.addRow(freq2_slider_label, freq2_slider)
        mod2_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        mod2_slider.setValue(settings.vibration_2_strength.get())
        mod2_slider_label = QtWidgets.QLabel("Strength [%]")
        gb2_l.addRow(mod2_slider_label, mod2_slider)
        bias2_left_right_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias2_left_right_slider.setValue(settings.vibration_2_left_right_bias.get())
        bias2_left_right_slider_label = QtWidgets.QLabel("bias left-right [%]")
        gb2_l.addRow(bias2_left_right_slider_label, bias2_left_right_slider)
        bias2_high_low_slider = QtWidgets.QDoubleSpinBox(minimum=-100, maximum=100)
        bias2_high_low_slider.setValue(settings.vibration_2_high_low_bias.get())
        bias2_high_low_slider_label = QtWidgets.QLabel("bias high-low [%]")
        gb2_l.addRow(bias2_high_low_slider_label, bias2_high_low_slider)
        random2_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        random2_slider.setValue(settings.vibration_2_random.get())
        random2_slider_label = QtWidgets.QLabel("random [%]")
        gb2_l.addRow(random2_slider_label, random2_slider)
        gb2.setLayout(gb2_l)
        l.addWidget(gb2)

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

        self.settings_changed()

    def settings_changed(self):
        self.vibration_1.enabled.add(self.gb1.isChecked())
        self.vibration_1.frequency.add(self.freq1_slider.value())
        self.vibration_1.strength.add(self.mod1_slider.value() / 100.0)
        self.vibration_1.left_right_bias.add(self.bias1_left_right_slider.value() / 100.0)
        self.vibration_1.high_low_bias.add(self.bias1_high_low_slider.value() / 100.0)
        self.vibration_1.random.add(self.random1_slider.value() / 100.0)

        self.vibration_2.enabled.add(self.gb2.isChecked())
        self.vibration_2.frequency.add(self.freq2_slider.value())
        self.vibration_2.strength.add(self.mod2_slider.value() / 100.0)
        self.vibration_2.left_right_bias.add(self.bias2_left_right_slider.value() / 100.0)
        self.vibration_2.high_low_bias.add(self.bias2_high_low_slider.value() / 100.0)
        self.vibration_2.random.add(self.random2_slider.value() / 100.0)

        self.mpl_canvas.updateParams(self.vibration_1, self.vibration_2)

    def save_settings(self):
        settings.vibration_1_enabled.set(self.gb1.isChecked())
        settings.vibration_1_frequency.set(self.freq1_slider.value())
        settings.vibration_1_strength.set(self.mod1_slider.value())
        settings.vibration_1_high_low_bias.set(self.bias1_high_low_slider.value())
        settings.vibration_1_left_right_bias.set(self.bias1_left_right_slider.value())
        settings.vibration_1_random.set(self.random1_slider.value())

        settings.vibration_2_enabled.set(self.gb2.isChecked())
        settings.vibration_2_frequency.set(self.freq2_slider.value())
        settings.vibration_2_strength.set(self.mod2_slider.value())
        settings.vibration_2_high_low_bias.set(self.bias2_high_low_slider.value())
        settings.vibration_2_left_right_bias.set(self.bias2_left_right_slider.value())
        settings.vibration_2_random.set(self.random2_slider.value())

