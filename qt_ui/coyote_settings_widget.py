import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional
from PySide6 import QtWidgets
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout,
                            QGraphicsView, QGraphicsScene, QGraphicsLineItem, QSpinBox,
                            QGraphicsRectItem, QToolTip, QGraphicsEllipseItem)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPen, QColor, QBrush, QPainterPath
from device.coyote.device import CoyoteDevice, CoyotePulse, CoyotePulses, CoyoteStrengths
from qt_ui import settings

class CoyoteSettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.device: Optional[CoyoteDevice] = None
        self.channel_controls: Dict[str, ChannelControl] = {}
        self.coyote_logger = logging.getLogger('restim.coyote')
        self._base_log_level = self.coyote_logger.getEffectiveLevel()
        self.setupUi()
        self.apply_debug_logging(settings.coyote_debug_logging.get())

    def setupUi(self):
        self.setLayout(QVBoxLayout())

        self.label_connection_status = QLabel("Device: Disconnected")
        self.label_connection_stage = QLabel("Stage: Waiting")
        self.label_battery_level = QLabel("Battery: —")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.label_connection_status)
        status_layout.addWidget(self.label_connection_stage)
        status_layout.addWidget(self.label_battery_level)
        self.layout().addLayout(status_layout)

        configs = (
            ChannelConfig(
                channel_id='A',
                freq_min_setting=settings.coyote_channel_a_freq_min,
                freq_max_setting=settings.coyote_channel_a_freq_max,
                strength_max_setting=settings.coyote_channel_a_strength_max,
            ),
            ChannelConfig(
                channel_id='B',
                freq_min_setting=settings.coyote_channel_b_freq_min,
                freq_max_setting=settings.coyote_channel_b_freq_max,
                strength_max_setting=settings.coyote_channel_b_strength_max,
            ),
        )

        for config in configs:
            control = ChannelControl(self, config)
            self.channel_controls[config.channel_id] = control
            self.layout().addLayout(control.build_ui())
            control.reset_volume()

    def setup_device(self, device: CoyoteDevice):
        self.device = device

        self.device.connection_status_changed.connect(self.on_connection_status_changed)
        self.device.battery_level_changed.connect(self.on_battery_level_changed)
        self.device.parameters_changed.connect(self.on_parameters_changed)
        self.device.power_levels_changed.connect(self.on_power_levels_changed)
        self.device.pulse_sent.connect(self.on_pulse_sent)

        for control in self.channel_controls.values():
            control.reset_volume()

        if device.strengths:
            for control in self.channel_controls.values():
                control.update_from_device(device.strengths)

    def update_channel_strength(self, control: 'ChannelControl', value: int):
        if not self.device or not self.device._event_loop:
            return

        strengths = control.with_strength(self.device.strengths, value)

        asyncio.run_coroutine_threadsafe(
            self.device.send_command(strengths),
            self.device._event_loop
        )

        self.device.strengths = strengths

    def on_connection_status_changed(self, connected: bool, stage: str = None):
        self.label_connection_status.setText("Device: Connected" if connected else "Device: Disconnected")
        if stage:
            normalized_stage = stage.strip()
            if connected and normalized_stage.lower() == "connected":
                stage_text = "Ready"
            else:
                stage_text = normalized_stage
            self.label_connection_stage.setText(f"Stage: {stage_text}")
        else:
            self.label_connection_stage.setText("Stage: —")

    def on_battery_level_changed(self, level: int):
        self.label_battery_level.setText(f"Battery: {level}%")

    def on_parameters_changed(self):
        pass

    def on_power_levels_changed(self, strengths: CoyoteStrengths):
        for control in self.channel_controls.values():
            control.update_from_device(strengths)

    def on_pulse_sent(self, pulses: CoyotePulses):
        if not self.device:
            return

        for control in self.channel_controls.values():
            control.apply_pulses(pulses, self.device.strengths)

    def apply_debug_logging(self, enabled: bool):
        new_level = logging.DEBUG if enabled else logging.INFO
        self.coyote_logger.setLevel(new_level)

@dataclass(frozen=True)
class ChannelConfig:
    channel_id: str
    freq_min_setting: settings.Setting
    freq_max_setting: settings.Setting
    strength_max_setting: settings.Setting

class ChannelControl:
    def __init__(self, parent: 'CoyoteSettingsWidget', config: ChannelConfig):
        self.parent = parent
        self.config = config

        self.freq_min: Optional[QSpinBox] = None
        self.freq_max: Optional[QSpinBox] = None
        self.strength_max: Optional[QSpinBox] = None
        self.volume_slider: Optional[QSlider] = None
        self.volume_label: Optional[QLabel] = None
        self.pulse_graph: Optional[PulseGraphContainer] = None
        self.stats_label: Optional[QLabel] = None

    @property
    def channel_id(self) -> str:
        return self.config.channel_id

    @property
    def _is_channel_a(self) -> bool:
        return self.channel_id.upper() == 'A'

    def build_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(QLabel(f"Channel {self.channel_id}"))

        freq_min_layout = QHBoxLayout()
        self.freq_min = QSpinBox()
        self.freq_min.setRange(10, 500)
        self.freq_min.setSingleStep(10)
        self.freq_min.setValue(self.config.freq_min_setting.get())
        self.freq_min.valueChanged.connect(self.on_freq_min_changed)
        freq_min_layout.addWidget(QLabel("Min Freq (Hz)"))
        freq_min_layout.addWidget(self.freq_min)
        left.addLayout(freq_min_layout)

        freq_max_layout = QHBoxLayout()
        self.freq_max = QSpinBox()
        self.freq_max.setRange(10, 500)
        self.freq_max.setSingleStep(10)
        self.freq_max.setValue(self.config.freq_max_setting.get())
        self.freq_max.valueChanged.connect(self.on_freq_max_changed)
        freq_max_layout.addWidget(QLabel("Max Freq (Hz)"))
        freq_max_layout.addWidget(self.freq_max)
        left.addLayout(freq_max_layout)

        strength_layout = QHBoxLayout()
        strength_layout.addWidget(QLabel("Max Strength"))
        self.strength_max = QSpinBox()
        self.strength_max.setRange(1, 200)
        self.strength_max.setSingleStep(1)
        self.strength_max.setValue(self.config.strength_max_setting.get())
        self.strength_max.valueChanged.connect(self.on_strength_max_changed)
        strength_layout.addWidget(self.strength_max)
        left.addLayout(strength_layout)

        layout.addLayout(left)

        self.pulse_graph = PulseGraphContainer(self.freq_min, self.freq_max)
        self.pulse_graph.plot.setMinimumHeight(100)

        graph_column = QVBoxLayout()
        graph_column.addWidget(self.pulse_graph)

        self.stats_label = QLabel("Intensity: 0%\nFrequency: 0 Hz")
        self.stats_label.setAlignment(Qt.AlignHCenter)
        self.pulse_graph.attach_stats_label(self.stats_label)
        graph_column.addWidget(self.stats_label)

        layout.addLayout(graph_column)

        volume_layout = QVBoxLayout()
        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, self.config.strength_max_setting.get())
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        self.volume_label = QLabel()
        self.volume_label.setAlignment(Qt.AlignHCenter)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)

        self.update_volume_label(self.volume_slider.value())
        return layout

    def reset_volume(self):
        self.set_strength_from_device(0)

    def select_strength(self, strengths: CoyoteStrengths) -> int:
        return strengths.channel_a if self._is_channel_a else strengths.channel_b

    def with_strength(self, strengths: CoyoteStrengths, value: int) -> CoyoteStrengths:
        if self._is_channel_a:
            return CoyoteStrengths(channel_a=value, channel_b=strengths.channel_b)
        return CoyoteStrengths(channel_a=strengths.channel_a, channel_b=value)

    def extract_pulses(self, pulses: CoyotePulses) -> list[CoyotePulse]:
        return pulses.channel_a if self._is_channel_a else pulses.channel_b

    def update_from_device(self, strengths: CoyoteStrengths):
        self.set_strength_from_device(self.select_strength(strengths))

    def apply_pulses(self, pulses: CoyotePulses, strengths: CoyoteStrengths):
        channel_pulses = self.extract_pulses(pulses)
        if not channel_pulses:
            return
        self.handle_pulses(channel_pulses, self.select_strength(strengths))

    def on_volume_changed(self, value: int):
        self.update_volume_label(value)
        self.parent.update_channel_strength(self, value)

    def update_volume_label(self, value: int):
        max_strength = max(1, self.config.strength_max_setting.get())
        percentage = int((value / max_strength) * 100)
        self.volume_label.setText(f"{value} ({percentage}%)")

    def set_strength_from_device(self, value: int):
        if self.volume_slider is None:
            return
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(value)
        self.volume_slider.blockSignals(False)
        self.update_volume_label(value)

    def on_strength_max_changed(self, value: int):
        self.config.strength_max_setting.set(value)

        current_value = self.volume_slider.value() if self.volume_slider else 0
        if self.volume_slider:
            self.volume_slider.blockSignals(True)
            self.volume_slider.setRange(0, value)
            clamped_value = min(current_value, value)
            self.volume_slider.setValue(clamped_value)
            self.volume_slider.blockSignals(False)
            self.update_volume_label(clamped_value)
            current_value = clamped_value

        self.parent.update_channel_strength(self, current_value)

    def on_freq_min_changed(self, value: int):
        if self.freq_min is None or self.freq_max is None:
            return

        corrected = value
        if value >= self.freq_max.value():
            corrected = max(self.freq_max.value() - self.freq_min.singleStep(), self.freq_min.minimum())
        if corrected != value:
            self.freq_min.blockSignals(True)
            self.freq_min.setValue(corrected)
            self.freq_min.blockSignals(False)
        self.config.freq_min_setting.set(corrected)

    def on_freq_max_changed(self, value: int):
        if self.freq_min is None or self.freq_max is None:
            return

        corrected = value
        if value <= self.freq_min.value():
            corrected = min(self.freq_min.value() + self.freq_max.singleStep(), self.freq_max.maximum())
        if corrected != value:
            self.freq_max.blockSignals(True)
            self.freq_max.setValue(corrected)
            self.freq_max.blockSignals(False)
        self.config.freq_max_setting.set(corrected)

    def handle_pulses(self, pulses: list[CoyotePulse], strength: int):
        if not self.pulse_graph or not pulses:
            return

        channel_limit = self.config.strength_max_setting.get()
        for pulse in pulses:
            self.pulse_graph.add_pulse(
                frequency=pulse.frequency,
                intensity=pulse.intensity,
                duration=pulse.duration,
                current_strength=strength,
                channel_limit=channel_limit,
            )

class PulseGraphContainer(QWidget):
    def __init__(self, freq_min: QSpinBox, freq_max: QSpinBox, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store frequency range controls
        self.freq_min = freq_min
        self.freq_max = freq_max

        # Initialize entries list to store CoyotePulse objects
        self.entries = []

        # Time window for stats display (in seconds)
        self.stats_window = 3.0  # Match the graph's time window

        # Create layout
        self.layout = QVBoxLayout(self)

        # Create plot widget
        self.plot = PulseGraph(*args, **kwargs)
        self.layout.addWidget(self.plot)

        # Optional stats label managed by parent component
        self.stats_label: Optional[QLabel] = None

    def attach_stats_label(self, label: QLabel):
        self.stats_label = label
        self.stats_label.setText("Intensity: 0%\nFrequency: 0 Hz")
        
    def get_frequency_range_text(self, entries) -> str:
        """Get the frequency range text from the given entries."""
        if not entries:
            return "N/A"
        frequencies = [entry.frequency for entry in entries]
        avg_frequency = sum(frequencies) / len(frequencies)
        min_freq = min(frequencies)
        max_freq = max(frequencies)
        
        # If min, max, and average are all the same, just show the single value
        if min_freq == max_freq == round(avg_frequency):
            return f"{int(avg_frequency)} Hz"
        # If min and max differ, show average with range
        return f"{avg_frequency:.0f} Hz ({min_freq} – {max_freq})"

    def format_intensity_text(self, intensities) -> str:
        """Format intensity text with smart range display."""
        if not intensities:
            return "N/A"
        avg_intensity = sum(intensities) / len(intensities)
        min_intensity = min(intensities)
        max_intensity = max(intensities)
        
        # If min, max, and average are all the same, just show the single value
        if min_intensity == max_intensity == round(avg_intensity):
            return f"{int(avg_intensity)}%"
        # If min and max differ, show average with range
        return f"{avg_intensity:.0f}% ({min_intensity} – {max_intensity})"
    
    def clean_old_entries(self):
        """Remove entries outside the time window"""
        current_time = time.time()
        self.entries = [e for e in self.entries if current_time - e.timestamp <= self.stats_window]

    def update_label_text(self):
        # Clean up old entries
        self.clean_old_entries()
        
        # Calculate stats using pulses from the time window
        recent_entries = self.entries
        
        # Get frequency range text
        freq_text = self.get_frequency_range_text(recent_entries)
        
        # Get intensity range
        intensities = [entry.intensity for entry in recent_entries]
        intensity_text = self.format_intensity_text(intensities)

        if self.stats_label:
            self.stats_label.setText(f"Intensity: {intensity_text}\nFrequency: {freq_text}")

    def add_pulse(self, frequency, intensity, duration, current_strength, channel_limit):
        # Calculate effective intensity after applying current strength
        effective_intensity = intensity * (current_strength / 100)
        
        # For zero intensity pulses, still create them but with zero intensity
        # This shows empty space in the graph
        
        # Create a CoyotePulse object
        pulse = CoyotePulse(
            frequency=frequency, 
            intensity=intensity,
            duration=duration
        )
        
        # Add timestamp for time-window filtering
        pulse.timestamp = time.time()
        
        # Store pulse data
        self.entries.append(pulse)
        
        self.update_label_text()
        
        # Update the plot - even zero intensity pulses are sent through for visualization
        self.plot.add_pulse(pulse, effective_intensity, channel_limit)

class PulseGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        
        # Completely disable scrolling and user interaction
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setInteractive(True)  # Enable interaction for tooltips
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Prevent wheel events
        self.view.wheelEvent = lambda event: None
        
        self.layout().addWidget(self.view)
        
        # Configuration for time window (in seconds)
        self.time_window = 3  # Show pulses from the last 3 seconds
        
        # Store pulses for visualization
        self.pulses = []
        self.channel_limit = 100  # Default channel limit
        
        # Packet tracking for FIFO visualization
        self.current_packet_index = 0  # Which 4-pulse packet is currently active
        self.last_packet_time = 0     # When the last packet was received
        self.pulse_fingerprints = {}  # Track pulse fingerprints to avoid duplicates
        
        # Initialize the scene size
        self.updateSceneRect()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(50)
        
        # Colors for visualization
        self.pulse_color = QColor(0, 255, 0, 200)  # Semi-transparent lime
        self.pulse_border_color = QColor("darkgreen")
        
        # Time scaling factor - how many pixels per ms of duration
        self.time_scale_factor = 0.5  # pixels per ms
    
    def resizeEvent(self, event):
        """Handle resize events by updating the scene rectangle"""
        super().resizeEvent(event)
        self.updateSceneRect()
        # Force a refresh after resize
        self.refresh()
    
    def updateSceneRect(self):
        """Update the scene rectangle to match the view size"""
        if self.view:
            width = self.view.viewport().width()
            height = self.view.viewport().height()
            self.view.setSceneRect(0, 0, width, height)
    
    def get_pulse_fingerprint(self, pulse: CoyotePulse) -> str:
        """Generate a fingerprint for a pulse to detect duplicates"""
        return f"{pulse.frequency}_{pulse.intensity}_{pulse.duration}"
    
    def clean_old_pulses(self):
        """Remove pulses outside the time window"""
        current_time = time.time()
        self.pulses = [p for p in self.pulses if current_time - p.timestamp <= self.time_window]
        
        # Also clean up old fingerprints
        for fingerprint, timestamp in list(self.pulse_fingerprints.items()):
            if current_time - timestamp > self.time_window:
                self.pulse_fingerprints.pop(fingerprint)

    def add_pulse(self, pulse: CoyotePulse, applied_intensity: float, channel_limit: int):
        """Add a new pulse to the visualization"""
        # Don't skip zero intensity pulses, but display them differently
        self.channel_limit = channel_limit
        
        # Generate a fingerprint for this pulse
        fingerprint = self.get_pulse_fingerprint(pulse)
        
        # Check if this pulse is from a new packet
        current_time = time.time()
        is_new_packet = len(self.pulses) % 4 == 0 or current_time - self.last_packet_time > 0.2
        
        # If we've seen this exact pulse recently and it's not a new packet, skip it
        if fingerprint in self.pulse_fingerprints and not is_new_packet:
            # Only add if it's been more than 1 second since we last saw this pulse
            last_seen_time = self.pulse_fingerprints[fingerprint]
            if current_time - last_seen_time < 1.0:
                return  # Skip this pulse, it's a duplicate
        
        # Update fingerprint timestamp
        self.pulse_fingerprints[fingerprint] = current_time
        
        # If it's a new packet, increment the packet index
        if is_new_packet:
            self.current_packet_index += 1
            self.last_packet_time = current_time
        
        # Store the CoyotePulse with additional metadata
        pulse_copy = CoyotePulse(
            frequency=pulse.frequency,
            intensity=pulse.intensity,
            duration=pulse.duration
        )
        
        # Add additional attributes to the pulse
        pulse_copy.applied_intensity = applied_intensity
        pulse_copy.packet_index = self.current_packet_index
        pulse_copy.timestamp = current_time
        
        # Add the pulse
        self.pulses.append(pulse_copy)
        
        # Clean up old pulses that are outside our time window
        self.clean_old_pulses()

    def refresh(self):
        """Redraw the pulse visualization"""
        self.scene.clear()
        
        # Always ensure we're using the current viewport size
        self.updateSceneRect()
        
        width = self.view.viewport().width()
        height = self.view.viewport().height()
        
        # Clean up old pulses again (in case the timer fired without any new pulses added)
        self.clean_old_pulses()
        
        if not self.pulses:
            return
        
        # Sort pulses by timestamp so they display in chronological order
        sorted_pulses = sorted(self.pulses, key=lambda p: p.timestamp)
        
        # Find the maximum intensity in current visible pulses
        max_intensity = max(pulse.applied_intensity for pulse in sorted_pulses)
        # Use either the channel limit or the current max intensity, whichever is larger
        scale_max = max(max_intensity, self.channel_limit)
        
        # Get the time span of the visible pulses
        now = time.time()
        oldest_time = now - self.time_window
        newest_time = now
        time_span_sec = self.time_window
        
        # Calculate total width available for all pulses
        usable_width = width - 10  # Leave small margin on right side
        
        # Scale based on the time window, not the pulse count
        # This ensures consistent scaling regardless of pulse frequency
        time_scale = usable_width / (time_span_sec * 1000)  # Convert to ms
        
        # Group pulses by packet for continuous display
        pulses_by_packet = {}
        for pulse in sorted_pulses:
            packet_idx = pulse.packet_index
            if packet_idx not in pulses_by_packet:
                pulses_by_packet[packet_idx] = []
            pulses_by_packet[packet_idx].append(pulse)
        
        # Get sorted list of packet indices
        packet_indices = sorted(pulses_by_packet.keys())
        
        # Draw each packet's pulses as a continuous sequence
        for i, packet_idx in enumerate(packet_indices):
            packet_pulses = sorted(pulses_by_packet[packet_idx], key=lambda p: p.timestamp)
            
            # Determine the time range this packet covers
            if i < len(packet_indices) - 1:
                # This packet runs until the next packet starts
                next_packet_idx = packet_indices[i + 1]
                next_packet_start = min(p.timestamp for p in pulses_by_packet[next_packet_idx])
                packet_end_time = next_packet_start
            else:
                # This is the last packet, it runs until now
                packet_end_time = now
            
            # Calculate packet colors
            packet_color = QColor(0, 255, 0, 200) if packet_idx % 2 == 0 else QColor(100, 255, 100, 200)
            
            # Draw each pulse in this packet
            for j, pulse in enumerate(packet_pulses):
                # Calculate time positions
                pulse_start_time = pulse.timestamp
                
                # For continuity, calculate the end time:
                if j < len(packet_pulses) - 1:
                    # If there's another pulse in this packet, it extends to that pulse
                    pulse_end_time = packet_pulses[j + 1].timestamp
                else:
                    # If this is the last pulse in the packet, it extends to the packet end
                    pulse_end_time = packet_end_time
                
                # Ensure we're within the visible time window
                pulse_start_time = max(pulse_start_time, oldest_time)
                pulse_end_time = min(pulse_end_time, newest_time)
                
                # Calculate positions and dimensions
                time_position_start = (pulse_start_time - oldest_time) / time_span_sec
                time_position_end = (pulse_end_time - oldest_time) / time_span_sec
                
                x_start = 5 + (time_position_start * usable_width)
                x_end = 5 + (time_position_end * usable_width)
                rect_width = max(2, x_end - x_start)  # Ensure minimum width
                
                # Calculate height based on intensity (always define rect_height)
                height_ratio = pulse.applied_intensity / scale_max if scale_max > 0 else 0
                rect_height = height * height_ratio

                # For zero-intensity pulses, still show something to indicate timing
                if pulse.applied_intensity <= 0:
                    # Draw a thin line or empty rectangle to show timing without intensity
                    empty_rect = QGraphicsRectItem(
                        x_start, height - 2,  # Just a thin line at the bottom
                        rect_width, 2
                    )
                    empty_rect.setPen(QPen(QColor(100, 100, 100, 100), 1))  # Very light gray
                    empty_rect.setBrush(QBrush(QColor(100, 100, 100, 50)))  # Almost transparent
                    self.scene.addItem(empty_rect)
                else:
                    # Create rectangle for the pulse
                    rect = PulseRectItem(
                        x_start, height - rect_height,  # x, y (bottom-aligned)
                        rect_width, rect_height,        # width, height
                        pulse                           # pass pulse data for tooltip
                    )
                    
                    rect.setPen(QPen(self.pulse_border_color, 1))
                    rect.setBrush(QBrush(packet_color))
                    
                    # Add rectangle to scene
                    self.scene.addItem(rect)
                
                # Draw frequency tick marks for visualization
                if pulse.frequency > 0 and rect_width > 10:
                    # Number of ticks based on frequency (higher frequency = more ticks)
                    num_ticks = min(max(2, int(pulse.frequency / 20)), 8)  # 2-8 ticks
                    
                    tick_spacing = rect_width / (num_ticks + 1)
                    tick_height = rect_height * 0.4  # 40% of rectangle height
                    
                    for t in range(1, num_ticks + 1):
                        tick_x = x_start + (t * tick_spacing)
                        tick_y = height - rect_height
                        
                        # Draw tick mark
                        tick = QGraphicsLineItem(
                            tick_x, tick_y,              # Start at top of rectangle
                            tick_x, tick_y + tick_height  # Go down
                        )
                        tick.setPen(QPen(QColor("white"), 1))
                        self.scene.addItem(tick)

class PulseRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, pulse):
        super().__init__(x, y, width, height)
        self.pulse = pulse
        self.setAcceptHoverEvents(True)
        
    def hoverEnterEvent(self, event):
        # Show tooltip with pulse information
        freq = self.pulse.frequency
        intensity = self.pulse.intensity
        duration = self.pulse.duration
        
        tooltip_text = f"Frequency: {freq} Hz\nIntensity: {intensity}%\nDuration: {duration} ms"
        QToolTip.showText(event.screenPos(), tooltip_text)
        
        # Change appearance on hover
        current_pen = self.pen()
        current_pen.setWidth(2)  # Make border thicker
        self.setPen(current_pen)
        
    def hoverLeaveEvent(self, event):
        # Restore original appearance
        current_pen = self.pen()
        current_pen.setWidth(1)  # Restore original border width
        self.setPen(current_pen)
        
