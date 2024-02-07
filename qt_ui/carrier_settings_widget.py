from __future__ import unicode_literals
from PyQt5 import QtCore, QtWidgets

import stim_math.limits
from stim_math.axis import AbstractAxis, create_temporal_axis
from qt_ui import settings


class CarrierSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        l = QtWidgets.QFormLayout(self)
        l.setObjectName("FormLayout")

        self.axis_carrier = create_temporal_axis(0.0)

        gbc = QtWidgets.QGroupBox("Carrier", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        gbc_l.setObjectName("FormLayout carrier groupbox")
        carrier_slider = QtWidgets.QDoubleSpinBox(minimum=0,
                                                  maximum=9999999)
        carrier_slider.setSingleStep(10.0)
        carrier_slider.setValue(settings.mk312_carrier.get())
        carrier_slider_label = QtWidgets.QLabel("carrier frequency [Hz]")
        gbc_l.addRow(carrier_slider_label, carrier_slider)

        empty_label = QtWidgets.QLabel("")
        warning_label = QtWidgets.QLabel("Use frequencies below 300Hz only with pulse-based boxes")
        gbc_l.addRow(empty_label, warning_label)

        gbc.setLayout(gbc_l)
        l.addWidget(gbc)

        carrier_slider.valueChanged.connect(self.settings_changed)

        self.carrier = carrier_slider

        self.settings_changed()

    def set_safety_limits(self, min_carrier, max_carrier):
        self.carrier.setRange(min_carrier, max_carrier)

    def settings_changed(self):
        self.axis_carrier.add(self.carrier.value())

    def save_settings(self):
        settings.mk312_carrier.set(self.carrier.value())