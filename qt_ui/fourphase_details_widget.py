"""
4-phase waveform details widget.

Shows live telemetry from the FOCStim device:
  - Commanded electrode intensities (from pattern/funscript axes)
  - Measured RMS / peak currents per electrode (from firmware notifications)
  - Total output power and skin power
  - Per-electrode impedance model (resistance + reluctance)
"""
from __future__ import unicode_literals

import numpy as np
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QSizePolicy,
    QSpacerItem, QProgressBar,
)
from PySide6.QtCore import Qt

from stim_math.axis import AbstractAxis


class _BarLabel(QWidget):
    """A compact horizontal bar + text value display."""

    def __init__(self, color: str = '#4488ff', parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(14)
        self.bar.setStyleSheet(
            f"QProgressBar {{ border: 1px solid grey; border-radius: 2px; background: transparent; }}"
            f"QProgressBar::chunk {{ background-color: {color}; }}"
        )
        self.value_label = QLabel("—")
        self.value_label.setFixedWidth(70)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.bar, stretch=1)
        layout.addWidget(self.value_label)

    def set_value(self, fraction: float, text: str):
        self.bar.setValue(int(np.clip(fraction, 0, 1) * 1000))
        self.value_label.setText(text)

    def set_text_only(self, text: str):
        self.bar.setValue(0)
        self.value_label.setText(text)


class FourPhaseDetailsWidget(QWidget):
    """Details tab for 4-phase FOCStim mode.

    Two sections:
    1. **Commanded** – electrode intensities read from the pattern axes (timer).
    2. **Measured** – RMS/peak currents + power from firmware notifications.
    3. **Impedance** – per-electrode resistance from model estimation notifications.
    """

    # Colours matching the bar-chart widget electrode colours
    COLOURS = ['#f44336', '#4caf50', '#2196f3', '#ff9800']  # A, B, C, D
    LABELS = ['A', 'B', 'C', 'D']

    def __init__(self, parent=None):
        super().__init__(parent)

        self._intensity_axes = None  # tuple of 4 AbstractAxis
        self._last_intensities = (None, None, None, None)

        root = QVBoxLayout(self)

        # ── Commanded intensities ────────────────────────────────
        grp_cmd = QGroupBox("Commanded electrode intensities")
        form_cmd = QFormLayout(grp_cmd)
        self._cmd_bars = []
        for i, (lbl, col) in enumerate(zip(self.LABELS, self.COLOURS)):
            bar = _BarLabel(color=col)
            form_cmd.addRow(f"Electrode {lbl}", bar)
            self._cmd_bars.append(bar)
        root.addWidget(grp_cmd)

        # ── Measured RMS currents ────────────────────────────────
        grp_rms = QGroupBox("Measured RMS current")
        form_rms = QFormLayout(grp_rms)
        self._rms_bars = []
        for i, (lbl, col) in enumerate(zip(self.LABELS, self.COLOURS)):
            bar = _BarLabel(color=col)
            form_rms.addRow(f"RMS {lbl}", bar)
            self._rms_bars.append(bar)
        root.addWidget(grp_rms)

        # ── Measured peak currents ───────────────────────────────
        grp_peak = QGroupBox("Measured peak current")
        form_peak = QFormLayout(grp_peak)
        self._peak_bars = []
        for i, (lbl, col) in enumerate(zip(self.LABELS, self.COLOURS)):
            bar = _BarLabel(color=col)
            form_peak.addRow(f"Peak {lbl}", bar)
            self._peak_bars.append(bar)
        root.addWidget(grp_peak)

        # ── Power summary ────────────────────────────────────────
        grp_power = QGroupBox("Output power")
        form_power = QFormLayout(grp_power)
        self._lbl_power_total = QLabel("—")
        self._lbl_power_skin = QLabel("—")
        self._lbl_peak_cmd = QLabel("—")
        form_power.addRow("Total", self._lbl_power_total)
        form_power.addRow("Skin", self._lbl_power_skin)
        form_power.addRow("Peak cmd", self._lbl_peak_cmd)
        root.addWidget(grp_power)

        # ── Impedance model ──────────────────────────────────────
        grp_imp = QGroupBox("Electrode impedance")
        form_imp = QFormLayout(grp_imp)
        self._lbl_impedance = []
        for lbl in self.LABELS:
            l = QLabel("—")
            form_imp.addRow(f"|Z| {lbl}", l)
            self._lbl_impedance.append(l)
        root.addWidget(grp_imp)

        root.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Timer for commanded-intensity refresh (same approach as 3-phase details)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._refresh_commanded)
        self._timer.start(100)

        # Scale factor for bar display (max current in A for full bar)
        self._current_scale = 0.15  # same as FOCStim safety limit

    # ── Public API ───────────────────────────────────────────────

    def set_intensity_axes(self, a: AbstractAxis, b: AbstractAxis,
                           c: AbstractAxis, d: AbstractAxis):
        """Connect to the 4-phase electrode intensity axes."""
        self._intensity_axes = (a, b, c, d)

    def update_currents(self, rms_a, rms_b, rms_c, rms_d,
                        peak_a, peak_b, peak_c, peak_d,
                        output_power, output_power_skin, peak_cmd):
        """Called from the FOCStim notification handler."""
        scale = self._current_scale
        for bar, val in zip(self._rms_bars, [rms_a, rms_b, rms_c, rms_d]):
            bar.set_value(val / scale, f"{val*1000:.1f} mA")
        for bar, val in zip(self._peak_bars, [peak_a, peak_b, peak_c, peak_d]):
            bar.set_value(val / scale, f"{val*1000:.1f} mA")

        self._lbl_power_total.setText(f"{output_power*1000:.1f} mW")
        self._lbl_power_skin.setText(f"{output_power_skin*1000:.1f} mW")
        self._lbl_peak_cmd.setText(f"{peak_cmd*1000:.1f} mA")

    def update_impedance(self, resistance_a, reluctance_a,
                         resistance_b, reluctance_b,
                         resistance_c, reluctance_c,
                         resistance_d, reluctance_d):
        """Called from the FOCStim model estimation notification handler."""
        for lbl, r, x in zip(
            self._lbl_impedance,
            [resistance_a, resistance_b, resistance_c, resistance_d],
            [reluctance_a, reluctance_b, reluctance_c, reluctance_d],
        ):
            z = abs(complex(r, x))
            lbl.setText(f"{z:.0f} Ω  (R={r:.0f}, X={x:.0f})")

    # ── Internal ────────────────────────────────────────────────

    def _refresh_commanded(self):
        if self._intensity_axes is None:
            return

        if self.isVisible():
            self._timer.setInterval(50)  # 20 Hz
        else:
            self._timer.setInterval(500)
            return

        vals = tuple(ax.last_value() for ax in self._intensity_axes)
        if vals == self._last_intensities:
            return
        self._last_intensities = vals

        for bar, v in zip(self._cmd_bars, vals):
            bar.set_value(v, f"{v:.2f}")
