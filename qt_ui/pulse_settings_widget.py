from __future__ import unicode_literals
import matplotlib
import numpy as np
import time

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

from PySide6 import QtCore, QtWidgets

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import stim_math.limits
import stim_math.pulse
from stim_math.axis import create_constant_axis

from qt_ui import settings
from qt_ui.axis_controller import AxisController, PercentAxisController



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
        pass

    def updateParams(self, carrier_frequency, pulse_frequency, pulse_width, pulse_interval_random, rise_time):
        samplerate = 44100
        x_limit = .10

        rise_time = np.clip(rise_time,
                            stim_math.limits.PulseRiseTime.min,
                            stim_math.limits.PulseRiseTime.max)

        gen = np.random.default_rng(seed=6)

        y = []
        while len(y) / samplerate < x_limit:
            theta = np.linspace(0, 2 * np.pi * pulse_width, int(samplerate / carrier_frequency * pulse_width)) + gen.uniform(0, np.pi * 2)
            pulse = np.cos(theta) * stim_math.pulse.create_pulse_with_ramp_time(len(theta), pulse_width, rise_time)
            y += list(pulse)
            pause_length = samplerate / pulse_frequency - len(pulse)
            pause_length *= gen.uniform(1 - pulse_interval_random, 1 + pulse_interval_random)
            if pause_length > 0:
                pause = np.zeros(int(pause_length))
                y += list(pause)

        x = np.linspace(0, len(y) / samplerate, len(y))

        self.axes.cla()
        self.axes.set_title("Pulse shape")
        self.axes.set_xlim((0, x_limit))
        self.axes.set_ylim((-1.1, 1.1))
        self.axes.plot(x, y)
        self.draw()


class PulseSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.axis_carrier_frequency = create_constant_axis(settings.pulse_carrier_frequency.get())
        self.axis_pulse_frequency = create_constant_axis(settings.pulse_frequency.get())
        self.axis_pulse_width = create_constant_axis(settings.pulse_width.get())
        self.axis_pulse_interval_random = create_constant_axis(settings.pulse_interval_random.get() / 100)
        self.axis_pulse_rise_time = create_constant_axis(settings.pulse_rise_time.get())

        l = QtWidgets.QFormLayout(self)
        l.setObjectName("FormLayout")
        self.mpl_canvas = MyStaticMplCanvas(self, width=7, height=3, dpi=100)
        l.addWidget(self.mpl_canvas)

        gbc = QtWidgets.QGroupBox("Carrier", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        gbc_l.setObjectName("FormLayout carrier groupbox")
        carrier_slider = QtWidgets.QDoubleSpinBox(minimum=0,
                                                  maximum=9999999)
        carrier_slider.setSingleStep(10.0)
        carrier_slider.setValue(settings.pulse_carrier_frequency.get())
        carrier_slider_label = QtWidgets.QLabel("carrier frequency [Hz]")
        gbc_l.addRow(carrier_slider_label, carrier_slider)
        gbc.setLayout(gbc_l)
        l.addWidget(gbc)

        gb = QtWidgets.QGroupBox("Pulse settings", self, checkable=False)
        gb_l = QtWidgets.QFormLayout(gb)
        gb_l.setObjectName("FormLayout pulse settings")

        pulse_freq_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.PulseFrequency.min,
                                                     maximum=stim_math.limits.PulseFrequency.max)
        pulse_freq_slider.setSingleStep(1.0)
        pulse_freq_slider.setValue(settings.pulse_frequency.get())
        pulse_freq_slider_label = QtWidgets.QLabel("pulse frequency [Hz]")
        gb_l.addRow(pulse_freq_slider_label, pulse_freq_slider)

        pulse_width_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.PulseWidth.min,
                                                       maximum=stim_math.limits.PulseWidth.max)
        pulse_width_slider.setSingleStep(0.1)
        pulse_width_slider.setValue(settings.pulse_width.get())
        pulse_width_label = QtWidgets.QLabel("pulse width [carrier cycles]")
        gb_l.addRow(pulse_width_label, pulse_width_slider)

        pulse_interval_random_slider = QtWidgets.QDoubleSpinBox(minimum=0, maximum=100)
        pulse_interval_random_slider.setSingleStep(1)
        pulse_interval_random_slider.setValue(settings.pulse_interval_random.get())
        pulse_interval_random_label = QtWidgets.QLabel("pulse interval random [%]")
        gb_l.addRow(pulse_interval_random_label, pulse_interval_random_slider)

        pulse_rise_time_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.PulseRiseTime.min,
                                                          maximum=stim_math.limits.PulseRiseTime.max)
        pulse_rise_time_slider.setSingleStep(0.1)
        pulse_rise_time_slider.setValue(settings.pulse_rise_time.get())
        pulse_rise_time_label = QtWidgets.QLabel("rise time [carrier cycles]")
        gb_l.addRow(pulse_rise_time_label, pulse_rise_time_slider)

        details_label = QtWidgets.QLabel("duty cycle (?)")
        details_label.setToolTip('Low duty cycle is best for power efficiency (less skin irritation).')
        details_info = QtWidgets.QLabel("placeholder")
        gb_l.addRow(details_label, details_info)

        gb.setLayout(gb_l)
        l.addWidget(gb)

        self.carrier = carrier_slider
        self.pulse_freq_slider = pulse_freq_slider
        self.pulse_width_slider = pulse_width_slider
        self.details_info = details_info
        self.pulse_interval_random = pulse_interval_random_slider
        self.pulse_rise_time = pulse_rise_time_slider


        self.carrier_controller = AxisController(self.carrier)
        self.carrier_controller.link_axis(self.axis_carrier_frequency)

        self.pulse_frequency_controller = AxisController(self.pulse_freq_slider)
        self.pulse_frequency_controller.link_axis(self.axis_pulse_frequency)

        self.pulse_width_controller = AxisController(self.pulse_width_slider)
        self.pulse_width_controller.link_axis(self.axis_pulse_width)

        self.pulse_interval_random_controller = PercentAxisController(self.pulse_interval_random)
        self.pulse_interval_random_controller.link_axis(self.axis_pulse_interval_random)

        self.pulse_rise_time_controller = AxisController(self.pulse_rise_time)
        self.pulse_rise_time_controller.link_axis(self.axis_pulse_rise_time)

        self.carrier_controller.modified_by_user.connect(self.settings_changed)
        self.pulse_width_controller.modified_by_user.connect(self.settings_changed)
        self.pulse_frequency_controller.modified_by_user.connect(self.settings_changed)
        self.pulse_interval_random_controller.modified_by_user.connect(self.settings_changed)
        self.pulse_rise_time_controller.modified_by_user.connect(self.settings_changed)

        self.settings_changed()

    def set_safety_limits(self, min_carrier, max_carrier):
        self.carrier.setRange(min_carrier, max_carrier)

    def settings_changed(self):
        # update text
        carrier_freq = self.carrier.value()
        pulse_freq = self.pulse_freq_slider.value()
        pulse_width = self.pulse_width_slider.value()
        duty_cycle = pulse_freq*pulse_width / carrier_freq
        rise_time = self.pulse_rise_time.value()
        if duty_cycle <= 1:
            self.details_info.setStyleSheet('')
            self.details_info.setText(f'{duty_cycle:.0%}')
        else:
            self.details_info.setStyleSheet('color: red')
            self.details_info.setText(f'{1:.0%}')

        self.mpl_canvas.updateParams(carrier_freq, pulse_freq, pulse_width, self.pulse_interval_random.value() / 100, rise_time)

    def save_settings(self):
        settings.pulse_carrier_frequency.set(self.carrier_controller.last_user_entered_value)
        settings.pulse_frequency.set(self.pulse_frequency_controller.last_user_entered_value)
        settings.pulse_width.set(self.pulse_width_controller.last_user_entered_value)
        settings.pulse_interval_random.set(self.pulse_interval_random_controller.last_user_entered_value * 100)
        settings.pulse_rise_time.set(self.pulse_rise_time_controller.last_user_entered_value)
