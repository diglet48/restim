from PySide6 import QtWidgets
import numpy as np

from qt_ui.widgets.focstim_device_stats_widget_ui import Ui_FocStimDeviceStatsWidget
from qt_ui.widgets.fourphase_widget_stereographic import COLOR_A, COLOR_B, COLOR_C, COLOR_D

class FocStimDeviceStatsWidget(QtWidgets.QWidget, Ui_FocStimDeviceStatsWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.transformer_max = 0
        self.voltage_max = 0

        self.label_a.setStyleSheet(self.stylesheet_with_color(COLOR_A))
        self.label_b.setStyleSheet(self.stylesheet_with_color(COLOR_B))
        self.label_c.setStyleSheet(self.stylesheet_with_color(COLOR_C))
        self.label_d.setStyleSheet(self.stylesheet_with_color(COLOR_D))
        self.reset_utilization()

    def stylesheet_with_color(self, background_color):
        return f"""
            QLabel {{
                background-color: {background_color.name()};
                color: white;
                border-radius: 12px;
                padding: 5px;
                font-weight: bold;
                font-size: 12px;
            }}
        """

    def update_utilization(self, transformer, voltage):
        self.transformer_max = max(transformer, self.transformer_max)
        self.voltage_max = max(voltage, self.voltage_max)
        self.label_transformer.setText(f"{transformer * 100:3.0f}%")
        self.label_transformer_max.setText(f"(max {self.transformer_max * 100:3.0f}%)")
        self.label_voltage.setText(f"{voltage * 100:3.0f}%")
        self.label_voltage_max.setText(f"(max {self.voltage_max * 100:3.0f}%)")

    def update_resistance(self, a, b, c, d):
        def format(x):
            a = np.clip(np.real(x), -9999, 9999)
            b = np.clip(np.imag(x), -9999, 9999)
            return f"{a:3.0f}\r\n{b:3.0f}i"

        self.resistance_a.setText(format(a))
        self.resistance_b.setText(format(b))
        self.resistance_c.setText(format(c))
        if d is None:
            self.resistance_d.setText(f"N/A")
        else:
            self.resistance_d.setText(format(d))

    def reset_utilization(self):
        self.transformer_max = 0
        self.voltage_max = 0
        self.update_utilization(0, 0)
        self.update_resistance(0, 0, 0, 0)
