from __future__ import unicode_literals
from PyQt5 import QtCore, QtWidgets

from qt_ui.stim_config import Mk312Parameters
import stim_math.limits
from qt_ui import settings


class CarrierSettingsWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        l = QtWidgets.QFormLayout(self)
        l.setObjectName("FormLayout")

        gbc = QtWidgets.QGroupBox("Carrier", self)
        gbc_l = QtWidgets.QFormLayout(gbc)
        gbc_l.setObjectName("FormLayout carrier groupbox")
        carrier_slider = QtWidgets.QDoubleSpinBox(minimum=stim_math.limits.Mk312CarrierFrequency.min,
                                                  maximum=stim_math.limits.Mk312CarrierFrequency.max)
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

    carrierSettingsChanged = QtCore.pyqtSignal(Mk312Parameters)

    def settings_changed(self):
        params = Mk312Parameters(
            self.carrier.value()
        )
        self.carrierSettingsChanged.emit(params)

        settings.mk312_carrier.set(self.carrier.value())
