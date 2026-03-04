"""
Pulse Auto-Derive Settings Dialog.

A popup window that lets the user configure how pulse parameters (frequency,
carrier, width, rise time) are automatically derived from funscript motion data.

Inspired by edger477's funscript-tools:
https://github.com/edger477/funscript-tools

This dialog serves as both a configuration UI and a teaching tool, showing
in real-time how the combine ratios and min/max ranges affect the generated
pulse signals.
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QDoubleSpinBox, QLabel, QCheckBox, QPushButton, QTabWidget,
    QWidget, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from qt_ui import settings
from qt_ui.pulse_auto_derive import compute_speed, combine, map_range, invert, clamp


class PreviewCanvas(FigureCanvas):
    """Matplotlib canvas showing the derived signals in real-time."""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

        # Create 5 subplots: input, speed, pulse_freq, carrier_freq, pulse_width, rise_time
        self.axes = self.fig.subplots(6, 1, sharex=True)
        self.fig.tight_layout(pad=1.5)

    def update_preview(self, main_t, main_p, params):
        """Update all preview plots with the given parameters."""
        for ax in self.axes:
            ax.cla()

        if main_t is None or len(main_t) < 2:
            # Show placeholder
            for ax in self.axes:
                ax.set_ylabel('')
                ax.text(0.5, 0.5, 'Load a funscript to see preview',
                        ha='center', va='center', transform=ax.transAxes,
                        color='gray', fontsize=10)
            self.draw()
            return

        speed_t, speed_y = compute_speed(main_t, main_p,
                                         window_seconds=params['speed_window'])
        speed_inv = invert(speed_y)
        main_inv = invert(main_p)

        # Plot 0: Input funscript
        ax = self.axes[0]
        ax.plot(main_t, main_p, color='#4080ff', linewidth=0.8)
        ax.set_ylabel('Position', fontsize=8)
        ax.set_title('Input Funscript', fontsize=9, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)

        # Plot 1: Speed signal
        ax = self.axes[1]
        ax.plot(speed_t, speed_y, color='#ff8040', linewidth=0.8)
        ax.set_ylabel('Speed', fontsize=8)
        ax.set_title(f'Speed (window={params["speed_window"]:.1f}s)', fontsize=9, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)

        # Plot 2: Pulse frequency
        ratio = params['pulse_freq_combine_ratio']
        pf_t, pf_y = combine(speed_t, speed_y, main_t, main_p, ratio)
        pf_t, pf_y = map_range(pf_t, pf_y, params['pulse_freq_min'], params['pulse_freq_max'])
        ax = self.axes[2]
        ax.plot(pf_t, pf_y, color='#40cc40', linewidth=0.8)
        left_pct = (ratio - 1) / ratio * 100
        right_pct = 1 / ratio * 100
        ax.set_ylabel('Hz', fontsize=8)
        ax.set_title(f'Pulse Freq: combine(speed {left_pct:.0f}%, alpha {right_pct:.0f}%) → [{params["pulse_freq_min"]:.0f}-{params["pulse_freq_max"]:.0f} Hz]',
                      fontsize=9, fontweight='bold')

        # Plot 3: Carrier frequency
        cf_t, cf_y = map_range(speed_t.copy(), speed_y.copy(),
                               params['carrier_freq_min'], params['carrier_freq_max'])
        ax = self.axes[3]
        ax.plot(cf_t, cf_y, color='#cc40cc', linewidth=0.8)
        ax.set_ylabel('Hz', fontsize=8)
        ax.set_title(f'Carrier Freq: map(speed) → [{params["carrier_freq_min"]:.0f}-{params["carrier_freq_max"]:.0f} Hz]',
                      fontsize=9, fontweight='bold')

        # Plot 4: Pulse width
        ratio_pw = params['pulse_width_combine_ratio']
        pw_base = clamp(main_inv, 0.0, 1.0)
        pw_t, pw_y = combine(speed_t, speed_y, main_t, pw_base, ratio_pw)
        pw_t, pw_y = map_range(pw_t, pw_y, params['pulse_width_min'], params['pulse_width_max'])
        ax = self.axes[4]
        ax.plot(pw_t, pw_y, color='#cc4040', linewidth=0.8)
        left_pct = (ratio_pw - 1) / ratio_pw * 100
        right_pct = 1 / ratio_pw * 100
        ax.set_ylabel('Cycles', fontsize=8)
        ax.set_title(f'Pulse Width: combine(speed {left_pct:.0f}%, inv_pos {right_pct:.0f}%) → [{params["pulse_width_min"]:.1f}-{params["pulse_width_max"]:.1f} cycles]',
                      fontsize=9, fontweight='bold')

        # Plot 5: Pulse rise time
        pr_t, pr_y = map_range(speed_t.copy(), speed_inv.copy(),
                               params['pulse_rise_min'], params['pulse_rise_max'])
        ax = self.axes[5]
        ax.plot(pr_t, pr_y, color='#4040cc', linewidth=0.8)
        ax.set_ylabel('Cycles', fontsize=8)
        ax.set_title(f'Rise Time: map(inv_speed) → [{params["pulse_rise_min"]:.1f}-{params["pulse_rise_max"]:.1f} cycles]',
                      fontsize=9, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=8)

        for ax in self.axes:
            ax.tick_params(labelsize=7)

        self.fig.tight_layout(pad=1.5)
        self.draw()


class PulseAutoSettingsDialog(QWidget):
    """
    Non-modal child window for configuring auto-derivation of pulse parameters
    from motion data. Stays alongside the main window and can be clicked past.
    Settings are only committed when the user clicks Apply.
    """

    settings_applied = Signal()  # emitted when user clicks Apply

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Auto-Derive Pulse Parameters")
        self.setMinimumSize(1000, 750)
        self.resize(1100, 800)

        self._demo_funscript = None  # (timestamps, positions) for preview
        self._alpha_funscript = None  # (timestamps, positions) for alpha

        self._build_ui()
        self._load_settings()
        self._connect_signals()
        self._update_preview()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)

        # Left panel: controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(420)
        left_panel.setMinimumWidth(350)

        # Enable checkbox
        self.chk_enabled = QCheckBox("Enable auto-derivation of pulse parameters")
        self.chk_enabled.setToolTip(
            "When enabled and no explicit funscripts are loaded for pulse parameters,\n"
            "they will be automatically derived from the motion data (speed + position)."
        )
        left_layout.addWidget(self.chk_enabled)

        # Info label
        info = QLabel(
            "<b>How it works:</b> When you load a funscript for position (1D, alpha/beta) "
            "but don't have separate funscripts for pulse parameters, restim can automatically "
            "derive them from the motion data using speed and position.<br><br>"
            "<i>Inspired by <a href='https://github.com/edger477/funscript-tools'>edger477's funscript-tools</a></i>"
        )
        info.setWordWrap(True)
        info.setOpenExternalLinks(True)
        info.setStyleSheet("padding: 5px; margin-bottom: 5px;")
        left_layout.addWidget(info)

        # Tabbed settings
        tabs = QTabWidget()

        # -- Speed tab --
        speed_tab = QWidget()
        speed_layout = QFormLayout(speed_tab)

        self.spin_speed_window = QDoubleSpinBox(minimum=0.5, maximum=30.0, singleStep=0.5)
        self.spin_speed_window.setToolTip(
            "Rolling window size for computing speed from position changes.\n"
            "Larger = smoother speed signal. Smaller = more responsive."
        )
        speed_layout.addRow("Speed window [s]:", self.spin_speed_window)

        speed_info = QLabel(
            "The <b>speed signal</b> measures how fast the position is changing.\n"
            "It's computed as a rolling average of |Δposition/Δtime|, normalized to 0-1.\n\n"
            "This signal drives most of the derived pulse parameters."
        )
        speed_info.setWordWrap(True)
        speed_layout.addRow(speed_info)

        tabs.addTab(speed_tab, "Speed")

        # -- Pulse Frequency tab --
        pf_tab = QWidget()
        pf_layout = QFormLayout(pf_tab)

        self.spin_pf_ratio = QDoubleSpinBox(minimum=1.0, maximum=10.0, singleStep=0.5)
        self.spin_pf_ratio.setToolTip(
            "Combine ratio for mixing speed and alpha signals.\n"
            "Ratio 2 = 50% speed + 50% alpha\n"
            "Ratio 3 = 67% speed + 33% alpha\n"
            "Higher = more speed-driven, less position influence."
        )
        self.lbl_pf_ratio = QLabel("")
        pf_layout.addRow("Combine ratio (speed:alpha):", self.spin_pf_ratio)
        pf_layout.addRow("Mix:", self.lbl_pf_ratio)
        pf_layout.addRow(QLabel(""))  # spacer

        self.spin_pf_min = QDoubleSpinBox(minimum=1, maximum=300, singleStep=5)
        self.spin_pf_min.setSuffix(" Hz")
        pf_layout.addRow("Min pulse frequency:", self.spin_pf_min)

        self.spin_pf_max = QDoubleSpinBox(minimum=1, maximum=300, singleStep=5)
        self.spin_pf_max.setSuffix(" Hz")
        pf_layout.addRow("Max pulse frequency:", self.spin_pf_max)

        pf_info = QLabel(
            "<b>Pulse Frequency</b> controls how often pulses fire.<br>"
            "Derived from: combine(speed, alpha) → map to [min, max]<br><br>"
            "Fast movement → higher pulse frequency.<br>"
            "Alpha position adds spatial variation."
        )
        pf_info.setWordWrap(True)
        pf_layout.addRow(pf_info)

        tabs.addTab(pf_tab, "Pulse Freq")

        # -- Carrier Frequency tab --
        cf_tab = QWidget()
        cf_layout = QFormLayout(cf_tab)

        self.spin_cf_min = QDoubleSpinBox(minimum=100, maximum=5000, singleStep=50)
        self.spin_cf_min.setSuffix(" Hz")
        cf_layout.addRow("Min carrier frequency:", self.spin_cf_min)

        self.spin_cf_max = QDoubleSpinBox(minimum=100, maximum=5000, singleStep=50)
        self.spin_cf_max.setSuffix(" Hz")
        cf_layout.addRow("Max carrier frequency:", self.spin_cf_max)

        cf_info = QLabel(
            "<b>Carrier Frequency</b> is the base waveform frequency.<br>"
            "Derived from: map(speed) → [min, max]<br><br>"
            "Fast movement → higher carrier frequency.<br>"
            "Slow/rest → lower carrier frequency."
        )
        cf_info.setWordWrap(True)
        cf_layout.addRow(cf_info)

        tabs.addTab(cf_tab, "Carrier Freq")

        # -- Pulse Width tab --
        pw_tab = QWidget()
        pw_layout = QFormLayout(pw_tab)

        self.spin_pw_ratio = QDoubleSpinBox(minimum=1.0, maximum=10.0, singleStep=0.5)
        self.spin_pw_ratio.setToolTip(
            "Combine ratio for mixing speed and inverted position.\n"
            "Ratio 2 = 50% speed + 50% inverted position\n"
            "Ratio 3 = 67% speed + 33% inverted position\n"
            "Higher = more speed-driven."
        )
        self.lbl_pw_ratio = QLabel("")
        pw_layout.addRow("Combine ratio (speed:inv_pos):", self.spin_pw_ratio)
        pw_layout.addRow("Mix:", self.lbl_pw_ratio)
        pw_layout.addRow(QLabel(""))  # spacer

        self.spin_pw_min = QDoubleSpinBox(minimum=3, maximum=100, singleStep=1)
        self.spin_pw_min.setSuffix(" cycles")
        pw_layout.addRow("Min pulse width:", self.spin_pw_min)

        self.spin_pw_max = QDoubleSpinBox(minimum=3, maximum=100, singleStep=1)
        self.spin_pw_max.setSuffix(" cycles")
        pw_layout.addRow("Max pulse width:", self.spin_pw_max)

        pw_info = QLabel(
            "<b>Pulse Width</b> controls how many carrier cycles per pulse.<br>"
            "Derived from: combine(speed, inv_position) → [min, max]<br><br>"
            "At rest (position low) → wider pulses (inverted).<br>"
            "During fast strokes → speed dominates."
        )
        pw_info.setWordWrap(True)
        pw_layout.addRow(pw_info)

        tabs.addTab(pw_tab, "Pulse Width")

        # -- Rise Time tab --
        pr_tab = QWidget()
        pr_layout = QFormLayout(pr_tab)

        self.spin_pr_min = QDoubleSpinBox(minimum=2, maximum=100, singleStep=1)
        self.spin_pr_min.setSuffix(" cycles")
        pr_layout.addRow("Min rise time:", self.spin_pr_min)

        self.spin_pr_max = QDoubleSpinBox(minimum=2, maximum=100, singleStep=1)
        self.spin_pr_max.setSuffix(" cycles")
        pr_layout.addRow("Max rise time:", self.spin_pr_max)

        pr_info = QLabel(
            "<b>Pulse Rise Time</b> controls how quickly pulses ramp up.<br>"
            "Derived from: map(inv_speed) → [min, max]<br><br>"
            "Slow movement → long rise time (softer sensation).<br>"
            "Fast movement → short rise time (sharper sensation)."
        )
        pr_info.setWordWrap(True)
        pr_layout.addRow(pr_info)

        tabs.addTab(pr_tab, "Rise Time")

        left_layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_defaults = QPushButton("Reset to Defaults")
        self.btn_defaults.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(self.btn_defaults)
        btn_layout.addStretch()
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self._apply_settings)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_close)
        left_layout.addLayout(btn_layout)

        # Right panel: preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("<b>Live Preview</b> (shows how parameters are derived from the loaded funscript)")
        right_layout.addWidget(preview_label)

        self.canvas = PreviewCanvas(right_panel, width=7, height=6, dpi=100)
        right_layout.addWidget(self.canvas)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

    def _connect_signals(self):
        """Connect all spinbox changes to the preview update."""
        for spin in [self.spin_speed_window,
                     self.spin_pf_ratio, self.spin_pf_min, self.spin_pf_max,
                     self.spin_cf_min, self.spin_cf_max,
                     self.spin_pw_ratio, self.spin_pw_min, self.spin_pw_max,
                     self.spin_pr_min, self.spin_pr_max]:
            spin.setKeyboardTracking(False)
            spin.valueChanged.connect(self._update_preview)

    def _load_settings(self):
        """Load current settings into the UI."""
        self.chk_enabled.setChecked(settings.pulse_auto_derive_enabled.get())
        self.spin_speed_window.setValue(settings.pulse_auto_derive_speed_window.get())

        self.spin_pf_ratio.setValue(settings.pulse_auto_derive_pulse_freq_combine_ratio.get())
        self.spin_pf_min.setValue(settings.pulse_auto_derive_pulse_freq_min.get())
        self.spin_pf_max.setValue(settings.pulse_auto_derive_pulse_freq_max.get())

        self.spin_cf_min.setValue(settings.pulse_auto_derive_carrier_freq_min.get())
        self.spin_cf_max.setValue(settings.pulse_auto_derive_carrier_freq_max.get())

        self.spin_pw_ratio.setValue(settings.pulse_auto_derive_pulse_width_combine_ratio.get())
        self.spin_pw_min.setValue(settings.pulse_auto_derive_pulse_width_min.get())
        self.spin_pw_max.setValue(settings.pulse_auto_derive_pulse_width_max.get())

        self.spin_pr_min.setValue(settings.pulse_auto_derive_pulse_rise_min.get())
        self.spin_pr_max.setValue(settings.pulse_auto_derive_pulse_rise_max.get())

    def _save_settings(self):
        """Save current UI values to persistent settings."""
        settings.pulse_auto_derive_enabled.set(self.chk_enabled.isChecked())
        settings.pulse_auto_derive_speed_window.set(self.spin_speed_window.value())

        settings.pulse_auto_derive_pulse_freq_combine_ratio.set(self.spin_pf_ratio.value())
        settings.pulse_auto_derive_pulse_freq_min.set(self.spin_pf_min.value())
        settings.pulse_auto_derive_pulse_freq_max.set(self.spin_pf_max.value())

        settings.pulse_auto_derive_carrier_freq_min.set(self.spin_cf_min.value())
        settings.pulse_auto_derive_carrier_freq_max.set(self.spin_cf_max.value())

        settings.pulse_auto_derive_pulse_width_combine_ratio.set(self.spin_pw_ratio.value())
        settings.pulse_auto_derive_pulse_width_min.set(self.spin_pw_min.value())
        settings.pulse_auto_derive_pulse_width_max.set(self.spin_pw_max.value())

        settings.pulse_auto_derive_pulse_rise_min.set(self.spin_pr_min.value())
        settings.pulse_auto_derive_pulse_rise_max.set(self.spin_pr_max.value())

    def _apply_settings(self):
        """Save settings and emit signal so the algorithm factory picks up the changes."""
        self._save_settings()
        self.settings_applied.emit()

    def _reset_defaults(self):
        """Reset all values to defaults."""
        self.chk_enabled.setChecked(False)
        self.spin_speed_window.setValue(5.0)

        self.spin_pf_ratio.setValue(3.0)
        self.spin_pf_min.setValue(20.0)
        self.spin_pf_max.setValue(95.0)

        self.spin_cf_min.setValue(600.0)
        self.spin_cf_max.setValue(900.0)

        self.spin_pw_ratio.setValue(3.0)
        self.spin_pw_min.setValue(4.0)
        self.spin_pw_max.setValue(20.0)

        self.spin_pr_min.setValue(2.0)
        self.spin_pr_max.setValue(20.0)

        self._update_preview()

    def set_demo_funscript(self, timestamps, positions, alpha_timestamps=None, alpha_positions=None):
        """
        Provide a funscript for live preview (e.g., the currently loaded funscript).
        """
        self._demo_funscript = (np.asarray(timestamps), np.asarray(positions))
        if alpha_timestamps is not None and alpha_positions is not None:
            self._alpha_funscript = (np.asarray(alpha_timestamps), np.asarray(alpha_positions))
        else:
            self._alpha_funscript = None
        self._update_preview()

    def _get_current_params(self):
        """Get the current parameter values from the UI."""
        return {
            'speed_window': self.spin_speed_window.value(),
            'pulse_freq_combine_ratio': self.spin_pf_ratio.value(),
            'pulse_freq_min': self.spin_pf_min.value(),
            'pulse_freq_max': self.spin_pf_max.value(),
            'carrier_freq_min': self.spin_cf_min.value(),
            'carrier_freq_max': self.spin_cf_max.value(),
            'pulse_width_combine_ratio': self.spin_pw_ratio.value(),
            'pulse_width_min': self.spin_pw_min.value(),
            'pulse_width_max': self.spin_pw_max.value(),
            'pulse_rise_min': self.spin_pr_min.value(),
            'pulse_rise_max': self.spin_pr_max.value(),
        }

    def _update_preview(self):
        """Refresh the preview plots with current parameters."""
        # Update ratio labels
        pf_ratio = self.spin_pf_ratio.value()
        pf_left = (pf_ratio - 1) / pf_ratio * 100
        pf_right = 1 / pf_ratio * 100
        self.lbl_pf_ratio.setText(f"Speed {pf_left:.0f}% + Alpha {pf_right:.0f}%")

        pw_ratio = self.spin_pw_ratio.value()
        pw_left = (pw_ratio - 1) / pw_ratio * 100
        pw_right = 1 / pw_ratio * 100
        self.lbl_pw_ratio.setText(f"Speed {pw_left:.0f}% + Inv Position {pw_right:.0f}%")

        params = self._get_current_params()

        if self._demo_funscript is not None:
            main_t, main_p = self._demo_funscript
            # Limit preview to first 120 seconds for performance
            if len(main_t) > 0 and main_t[-1] - main_t[0] > 120:
                mask = main_t <= main_t[0] + 120
                main_t = main_t[mask]
                main_p = main_p[mask]
            self.canvas.update_preview(main_t, main_p, params)
        else:
            self.canvas.update_preview(None, None, params)
