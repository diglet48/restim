import asyncio
import time
import numpy as np
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, 
                            QGraphicsView, QGraphicsScene, QGraphicsLineItem, QDoubleSpinBox, QSpinBox,
                            QGraphicsRectItem, QToolTip, QGraphicsItem, QGraphicsEllipseItem, QGraphicsPathItem)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import QPen, QColor, QBrush, QPainterPath
from device.coyote.device import CoyoteDevice, CoyotePulse, CoyotePulses, CoyoteStrengths
from qt_ui import settings

# Channel color constants for use throughout the UI
CHANNEL_A_COLOR = QColor(160, 90, 255)  # Purple
CHANNEL_B_COLOR = QColor(255, 170, 50)  # Orange

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
        
        # Create and setup label
        self.label = QLabel("Intensity: 0%\nFrequency: 0 Hz")
        self.label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        self.layout.addWidget(self.plot)
        self.layout.addWidget(self.label)
        
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

        # Update label with frequency and intensity information
        self.label.setText(f"Intensity: {intensity_text}\nFrequency: {freq_text}")

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

# Create a custom graphics rect item with hover capability
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

class EnvelopeGraph(QWidget):
    """
    Displays a dynamic visualization of how the envelope pattern affects pulses.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        
        # Disable scrolling and user interaction
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setInteractive(True)  # Enable for tooltip hover events
        self.view.setDragMode(QGraphicsView.NoDrag)
        self.view.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        
        self.layout().addWidget(self.view)
        
        # Store envelope data
        self.envelope_data = np.zeros(100)  # Default empty envelope
        self.envelope_period = 1.0
        
        # Store recent pulses for overlay - increased to show more
        self.recent_pulses = []
        self.max_pulses = 50  # Show plenty of pulses
        self.max_pulse_age = 2.0  # Show a longer history (2 seconds)
        
        # Colors for visualization
        self.envelope_color = QColor(0, 180, 255, 150)
        self.pulse_colors = [
            CHANNEL_A_COLOR,
            CHANNEL_B_COLOR
        ]
        
        # Add margin to avoid clipping
        self.margin = 20
        
        # Simplified timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)  # 10fps
        
        # Initialize scene size
        self.updateSceneRect()
    
    def resizeEvent(self, event):
        """Handle resize events by updating the scene rectangle"""
        super().resizeEvent(event)
        self.updateSceneRect()
    
    def updateSceneRect(self):
        """Update the scene rectangle to match the view size"""
        if self.view:
            width = self.view.viewport().width()
            height = self.view.viewport().height()
            self.view.setSceneRect(0, 0, width, height)
    
    def setEnvelopeData(self, envelope_data, envelope_period):
        """
        Set new envelope data to display
        
        Args:
            envelope_data: numpy array of envelope values (-1 to 1)
            envelope_period: period of the envelope in seconds
        """
        if envelope_data is None or not isinstance(envelope_data, np.ndarray) or len(envelope_data) == 0:
            return
            
        # Make a copy to avoid reference issues
        self.envelope_data = np.array(envelope_data).copy()
        
        # Make sure we have valid data
        if np.isnan(self.envelope_data).any() or np.isinf(self.envelope_data).any():
            self.envelope_data = np.nan_to_num(self.envelope_data)
            
        # Validate period
        if envelope_period > 0:
            self.envelope_period = envelope_period
    
    def addPulse(self, channel_idx, intensity, duration, timestamp=None):
        """
        Add a pulse to visualize
        
        Args:
            channel_idx: 0 for channel A, 1 for channel B
            intensity: Pulse intensity (0-100)
            duration: Pulse duration in ms
            timestamp: When the pulse occurred (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Create a new pulse entry
        new_pulse = {
            'channel': channel_idx,
            'intensity': intensity,
            'duration': duration,
            'timestamp': timestamp
        }
        
        # Add to beginning for efficient removal of old ones
        self.recent_pulses.insert(0, new_pulse)
        
        # Limit the number of pulses
        while len(self.recent_pulses) > self.max_pulses:
            self.recent_pulses.pop()
    
    def refresh(self):
        """Simple redraw method without any complex error handling"""
        # Skip if not visible
        if not self.isVisible():
            return
            
        # Get current time for pulse age calculations
        current_time = time.time()
            
        # Clean old pulses first
        self.recent_pulses = [p for p in self.recent_pulses if current_time - p['timestamp'] <= self.max_pulse_age]
            
        # Clear scene
        self.scene.clear()
        
        # Get dimensions
        width = self.view.viewport().width()
        height = self.view.viewport().height()
        center_y = height / 2
        
        # Calculate scaling
        vertical_scale = (height - 2 * self.margin) / 2
        
        # Draw simple grid
        self._drawGrid(width, height, center_y)
        
        # Draw envelope
        self._drawEnvelope(width, height, center_y, vertical_scale)
        
        # Draw pulses
        self._drawPulses(width, height, center_y, vertical_scale, current_time)
        
        # Draw frequency label
        self._drawFrequencyLabel(width, height)
    
    def _drawGrid(self, width, height, center_y):
        """Draw minimal grid lines"""
        # Center line
        center_line = QGraphicsLineItem(self.margin, center_y, width - self.margin, center_y)
        center_line.setPen(QPen(QColor(200, 200, 200, 150), 1, Qt.DashLine))
        self.scene.addItem(center_line)
    
    def _drawEnvelope(self, width, height, center_y, vertical_scale):
        """Draw envelope curve"""
        # Ensure we have data
        if len(self.envelope_data) == 0:
            return
            
        # Calculate usable width
        usable_width = width - 2 * self.margin
        
        # Create envelope path
        path = QPainterPath()
        
        # Calculate number of points (1 point per 3 pixels for performance)
        num_points = min(len(self.envelope_data), int(usable_width / 3))
        if num_points < 2:
            return
            
        # Calculate step size for envelope data
        step = (len(self.envelope_data) - 1) / (num_points - 1)
        
        # Start path
        x = self.margin
        y = center_y - (self.envelope_data[0] * vertical_scale)
        path.moveTo(x, y)
        
        # Add points
        for i in range(1, num_points):
            x = self.margin + (i / (num_points - 1)) * usable_width
            idx = int(i * step)
            if idx >= len(self.envelope_data):
                idx = len(self.envelope_data) - 1
            y = center_y - (self.envelope_data[idx] * vertical_scale)
            path.lineTo(x, y)
        
        # Add path to scene
        pen = QPen(self.envelope_color, 2)
        self.scene.addPath(path, pen)
    
    def _drawPulses(self, width, height, center_y, vertical_scale, current_time):
        """Draw pulse dots on the envelope"""
        if not self.recent_pulses or len(self.envelope_data) == 0 or self.envelope_period <= 0:
            return
            
        usable_width = width - 2 * self.margin
        
        # Draw each pulse
        for pulse in self.recent_pulses:
            # Calculate age
            age = current_time - pulse['timestamp']
            
            # Calculate position
            phase = (age % self.envelope_period) / self.envelope_period
            phase_reversed = 1.0 - phase  # Newer pulses on right
            
            # Set x position
            x = self.margin + phase_reversed * usable_width
            
            # Find envelope height at this position
            if len(self.envelope_data) > 1:  # Prevent div by zero
                env_idx = min(int(phase_reversed * (len(self.envelope_data) - 1)), len(self.envelope_data) - 1)
                env_value = self.envelope_data[env_idx]
                y = center_y - (env_value * vertical_scale)
            else:
                y = center_y
            
            # Calculate dot size based on intensity
            intensity = pulse['intensity']
            size = 4 + (12 * intensity / 100.0)
            
            # Create dot
            channel = pulse['channel']
            dot = QGraphicsEllipseItem(x - size/2, y - size/2, size, size)
            dot.setBrush(QBrush(self.pulse_colors[channel]))
            dot.setPen(QPen(Qt.NoPen))
            
            # Add tooltip
            dot.setToolTip(f"Channel: {'A' if channel == 0 else 'B'}\n"
                           f"Intensity: {intensity}%\n"
                           f"Duration: {pulse['duration']} ms")
            
            # Add to scene
            dot.setAcceptHoverEvents(True)
            self.scene.addItem(dot)
    
    def _drawFrequencyLabel(self, width, height):
        """Draw frequency information"""
        if self.envelope_period > 0:
            freq_hz = 1.0 / self.envelope_period
            label_text = f"{freq_hz:.1f} Hz ({self.envelope_period*1000:.0f} ms)"
            label = self.scene.addText(label_text)
            label.setPos(width - 180, 5)
            label.setDefaultTextColor(QColor(60, 60, 60))

class EnvelopeGraphContainer(QWidget):
    """
    Container for the envelope graph with title and labels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better alignment
        
        # Add top controls row
        top_row = QHBoxLayout()
        
        # Add description
        self.description = QLabel("Envelope Pattern")
        self.description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_row.addWidget(self.description)
        
        # Add spacer
        top_row.addStretch(1)
        
        # Add waveform selector
        self.waveform_label = QLabel("Waveform:")
        top_row.addWidget(self.waveform_label)
        
        self.waveform_selector = QtWidgets.QComboBox()
        self.waveform_selector.addItem("Sine")
        # Add more waveforms here when supported
        top_row.addWidget(self.waveform_selector)
        
        self.layout.addLayout(top_row)
        
        # Create envelope graph
        self.graph = EnvelopeGraph()
        self.layout.addWidget(self.graph)
        
        # We don't need a complex buffer or cleanup timer since
        # the graph now handles its own pulse cleanup and display
        self.received_real_data = False
    
    def setEnvelopeData(self, envelope_data, envelope_period):
        """Pass envelope data to the graph"""
        self.received_real_data = True
        
        # Update envelope description based on real data
        if envelope_period > 0:
            freq_hz = 1.0 / envelope_period
            self.description.setText(f"Envelope Pattern - {freq_hz:.1f} Hz ({envelope_period*1000:.0f} ms)")
        
        # Pass data to the graph
        self.graph.setEnvelopeData(envelope_data, envelope_period)
    
    def addPulse(self, channel_id, intensity, duration, strength=100):
        """
        Add a pulse to the visualization
        
        Args:
            channel_id: 'A' or 'B'
            intensity: Pulse intensity
            duration: Pulse duration in ms
            strength: Current channel strength (0-100)
        """
        # Calculate effective intensity
        effective_intensity = intensity * (strength / 100)
        
        # Skip very low intensity pulses
        if effective_intensity < 1:
            return
            
        # Convert channel ID to index (0 for A, 1 for B)
        channel_idx = 0 if channel_id == 'A' else 1
        
        # Add directly to the graph without buffering
        self.graph.addPulse(channel_idx, intensity, duration)

class CoyoteSettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setupUi(self)
        
        # Always initialize volume sliders to 0 (non-persistent)
        self.volume_a_slider.setValue(0)
        self.volume_b_slider.setValue(0)
        
        # Connect signals
        self.volume_a_slider.valueChanged.connect(self.update_channel_a)
        self.volume_b_slider.valueChanged.connect(self.update_channel_b)
        self.freq_min_a.valueChanged.connect(self.update_freq_min_a)
        self.freq_max_a.valueChanged.connect(self.update_freq_max_a)
        self.freq_min_b.valueChanged.connect(self.update_freq_min_b)
        self.freq_max_b.valueChanged.connect(self.update_freq_max_b)
        self.strength_max_a.valueChanged.connect(self.update_strength_max_a)
        self.strength_max_b.valueChanged.connect(self.update_strength_max_b)

    def setupUi(self, CoyoteSettingsWidget):
        self.setLayout(QVBoxLayout())

        # Connection/Battery Status
        self.label_connection_status = QLabel("Disconnected")
        self.label_connection_stage = QLabel("")
        self.label_battery_level = QLabel("")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.label_connection_status)
        status_layout.addWidget(self.label_connection_stage)
        status_layout.addWidget(self.label_battery_level)
        self.layout().addLayout(status_layout)
        
        # Add envelope graph with matching layout to pulse graphs
        envelope_section = QHBoxLayout()
        
        # Left section - make it the same width as channel controls
        envelope_left = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setMinimumWidth(130)  # Increased width to match channel control sections
        left_widget.setMaximumWidth(130)  # Increased width to match channel control sections
        envelope_left.addWidget(left_widget)
        envelope_section.addLayout(envelope_left)
        
        # Add envelope graph in the center with stretch factor
        self.envelope_graph = EnvelopeGraphContainer()
        self.envelope_graph.setMinimumHeight(120)
        envelope_section.addWidget(self.envelope_graph, 1)  # Use stretch factor of 1
        
        # Right side controls with proper width
        envelope_right = QHBoxLayout()  # Changed to horizontal layout
        
        # Add a visual legend for dots with proper size
        legend_layout = QVBoxLayout()
        legend_layout.setSpacing(2)
        
        # Use shared channel colors
        channel_a_qcolor = CHANNEL_A_COLOR
        channel_b_qcolor = CHANNEL_B_COLOR

        legend_label = QLabel("Dots:")
        legend_label.setAlignment(Qt.AlignCenter)
        legend_layout.addWidget(legend_label)

        channel_a_legend = QHBoxLayout()
        channel_a_color = QLabel("●")
        channel_a_color.setFont(channel_a_color.font())
        channel_a_palette = channel_a_color.palette()
        channel_a_palette.setColor(channel_a_color.foregroundRole(), channel_a_qcolor)
        channel_a_color.setPalette(channel_a_palette)
        channel_a_color.setStyleSheet("font-size: 16px;")
        channel_a_text = QLabel("Channel A")
        channel_a_legend.addWidget(channel_a_color)
        channel_a_legend.addWidget(channel_a_text)
        legend_layout.addLayout(channel_a_legend)

        channel_b_legend = QHBoxLayout()
        channel_b_color = QLabel("●")
        channel_b_color.setFont(channel_b_color.font())
        channel_b_palette = channel_b_color.palette()
        channel_b_palette.setColor(channel_b_color.foregroundRole(), channel_b_qcolor)
        channel_b_color.setPalette(channel_b_palette)
        channel_b_color.setStyleSheet("font-size: 16px;")
        channel_b_text = QLabel("Channel B")
        channel_b_legend.addWidget(channel_b_color)
        channel_b_legend.addWidget(channel_b_text)
        legend_layout.addLayout(channel_b_legend)
        
        size_legend = QHBoxLayout()
        size_label = QLabel("Size = Intensity")
        size_legend.addWidget(size_label)
        legend_layout.addLayout(size_legend)
        
        # Create a widget to contain the legend with proper width
        legend_widget = QWidget()
        legend_widget.setLayout(legend_layout)
        legend_widget.setMinimumWidth(130)  # Match the width of volume sliders
        envelope_right.addWidget(legend_widget)
        
        envelope_section.addLayout(envelope_right)
        
        self.layout().addLayout(envelope_section)

        # Channel A Row
        channel_a_layout = QHBoxLayout()
        
        # Left side layout for Channel A (label and frequency controls)
        channel_a_left = QVBoxLayout()
        channel_a_label = QLabel("Channel A")
        
        # Frequency controls in horizontal layouts
        freq_min_a_controls = QHBoxLayout()
        self.freq_min_a = QSpinBox()
        self.freq_min_a.setRange(10, 500)
        self.freq_min_a.setValue(settings.coyote_channel_a_freq_min.get())
        self.freq_min_a.setSingleStep(10)
        freq_min_a_controls.addWidget(QLabel("Min (Hz)"))
        freq_min_a_controls.addWidget(self.freq_min_a)
        
        freq_max_a_controls = QHBoxLayout()
        self.freq_max_a = QSpinBox()
        self.freq_max_a.setRange(10, 500)
        self.freq_max_a.setValue(settings.coyote_channel_a_freq_max.get())
        self.freq_max_a.setSingleStep(10)
        freq_max_a_controls.addWidget(QLabel("Max (Hz)"))
        freq_max_a_controls.addWidget(self.freq_max_a)
        
        # Max strength controls for Channel A
        strength_max_a_controls = QHBoxLayout()
        strength_max_a_controls.addWidget(QLabel("Max Strength"))
        self.strength_max_a = QSpinBox()
        self.strength_max_a.setRange(1, 200)
        self.strength_max_a.setValue(settings.coyote_channel_a_strength_max.get())
        self.strength_max_a.setSingleStep(1)
        self.strength_max_a.valueChanged.connect(self.update_strength_max_a)
        strength_max_a_controls.addWidget(self.strength_max_a)
        
        channel_a_left.addWidget(channel_a_label)
        channel_a_left.addLayout(freq_min_a_controls)
        channel_a_left.addLayout(freq_max_a_controls)
        channel_a_left.addLayout(strength_max_a_controls)

        # Pulse graph for Channel A
        self.pulse_graph_a = PulseGraphContainer(self.freq_min_a, self.freq_max_a)
        self.pulse_graph_a.plot.setMinimumHeight(100)

        # Volume slider layout for Channel A
        volume_a_layout = QVBoxLayout()
        self.volume_a_label = QLabel("0 (0%)")
        self.volume_a_label.setAlignment(Qt.AlignHCenter)
        self.volume_a_slider = QSlider(Qt.Vertical)
        self.volume_a_slider.setRange(0, settings.coyote_channel_a_strength_max.get())
        self.volume_a_slider.valueChanged.connect(self.update_volume_a_label)
        volume_a_layout.addWidget(self.volume_a_slider)
        volume_a_layout.addWidget(self.volume_a_label)

        channel_a_layout.addLayout(channel_a_left)
        channel_a_layout.addWidget(self.pulse_graph_a)
        channel_a_layout.addLayout(volume_a_layout)

        self.layout().addLayout(channel_a_layout)

        # Channel B Row
        channel_b_layout = QHBoxLayout()
        
        # Left side layout for Channel B (label and frequency controls)
        channel_b_left = QVBoxLayout()
        channel_b_label = QLabel("Channel B")
        
        # Frequency controls in horizontal layouts
        freq_min_b_controls = QHBoxLayout()
        self.freq_min_b = QSpinBox()
        self.freq_min_b.setRange(10, 500)
        self.freq_min_b.setValue(settings.coyote_channel_b_freq_min.get())
        self.freq_min_b.setSingleStep(10)
        freq_min_b_controls.addWidget(QLabel("Min (Hz)"))
        freq_min_b_controls.addWidget(self.freq_min_b)
        
        freq_max_b_controls = QHBoxLayout()
        self.freq_max_b = QSpinBox()
        self.freq_max_b.setRange(10, 500)
        self.freq_max_b.setValue(settings.coyote_channel_b_freq_max.get())
        self.freq_max_b.setSingleStep(10)
        freq_max_b_controls.addWidget(QLabel("Max (Hz)"))
        freq_max_b_controls.addWidget(self.freq_max_b)
        
        # Max strength controls for Channel B
        strength_max_b_controls = QHBoxLayout()
        strength_max_b_controls.addWidget(QLabel("Max Strength"))
        self.strength_max_b = QSpinBox()
        self.strength_max_b.setRange(1, 200)
        self.strength_max_b.setValue(settings.coyote_channel_b_strength_max.get())
        self.strength_max_b.setSingleStep(1)
        self.strength_max_b.valueChanged.connect(self.update_strength_max_b)
        strength_max_b_controls.addWidget(self.strength_max_b)
        
        channel_b_left.addWidget(channel_b_label)
        channel_b_left.addLayout(freq_min_b_controls)
        channel_b_left.addLayout(freq_max_b_controls)
        channel_b_left.addLayout(strength_max_b_controls)

        # Pulse graph for Channel B
        self.pulse_graph_b = PulseGraphContainer(self.freq_min_b, self.freq_max_b)
        self.pulse_graph_b.plot.setMinimumHeight(100)

        # Volume slider layout for Channel B
        volume_b_layout = QVBoxLayout()
        self.volume_b_label = QLabel("0 (0%)")
        self.volume_b_label.setAlignment(Qt.AlignHCenter)
        self.volume_b_slider = QSlider(Qt.Vertical)
        self.volume_b_slider.setRange(0, settings.coyote_channel_b_strength_max.get())
        self.volume_b_slider.valueChanged.connect(self.update_volume_b_label)
        volume_b_layout.addWidget(self.volume_b_slider)
        volume_b_layout.addWidget(self.volume_b_label)

        channel_b_layout.addLayout(channel_b_left)
        channel_b_layout.addWidget(self.pulse_graph_b)
        channel_b_layout.addLayout(volume_b_layout)

        self.layout().addLayout(channel_b_layout)

    def setup_device(self, device: CoyoteDevice):
        self.device = device

        # Connect device signals
        self.device.connection_status_changed.connect(self.on_connection_status_changed)
        self.device.battery_level_changed.connect(self.on_battery_level_changed)
        self.device.parameters_changed.connect(self.on_parameters_changed)
        self.device.power_levels_changed.connect(self.on_power_levels_changed)
        self.device.pulse_sent.connect(self.on_pulse_sent)

        # Initialize labels
        self.update_volume_a_label(0)
        self.update_volume_b_label(0)
        
        # If we are already connected to a device, initialize with its values
        if device.strengths:
            self.update_channel_a(0)
            self.update_channel_b(0)
        
        # Set up timer to periodically fetch envelope data directly
        self.envelope_timer = QTimer()
        self.envelope_timer.timeout.connect(self.fetch_envelope_data)
        self.envelope_timer.start(500)  # Fetch every 500ms

    def update_channel_a(self, value):
        """Update channel A strength (volume) in the device."""
        if self.device._event_loop:
            # value is already the actual strength value (not a percentage)
            asyncio.run_coroutine_threadsafe(
                self.device.send_command(CoyoteStrengths(value, self.device.strengths.channel_b)),
                self.device._event_loop
            )

    def update_channel_b(self, value):
        """Update channel B strength (volume) in the device."""
        if self.device._event_loop:
            # value is already the actual strength value (not a percentage)
            asyncio.run_coroutine_threadsafe(
                self.device.send_command(CoyoteStrengths(self.device.strengths.channel_a, value)),
                self.device._event_loop
            )

    def on_connection_status_changed(self, connected: bool, stage: str = None):
        """Update connection status and stage in UI"""
        self.label_connection_status.setText("Connected" if connected else "Disconnected")
        if stage:
            self.label_connection_stage.setText(stage)
        # Enable/disable sliders based on connection status
        # self.volume_a_slider.setEnabled(connected)
        # self.volume_b_slider.setEnabled(connected)

    def on_battery_level_changed(self, level: int):
        """Update battery level display"""
        self.label_battery_level.setText(f"Battery: {level}%")

    def on_parameters_changed(self):
        """Update UI when device parameters change"""
        self.volume_a_slider.blockSignals(True)
        self.volume_b_slider.blockSignals(True)
        
        # self.volume_a_slider.setValue(self.device.parameters.channel_a_intensity_balance)
        # self.volume_b_slider.setValue(self.device.parameters.channel_b_intensity_balance)
        
        self.volume_a_slider.blockSignals(False)
        self.volume_b_slider.blockSignals(False)

    def on_power_levels_changed(self, strengths: CoyoteStrengths):
        """Update sliders when device power levels change"""
        self.volume_a_slider.blockSignals(True)
        self.volume_b_slider.blockSignals(True)
        
        self.volume_a_slider.setValue(strengths.channel_a)
        self.volume_b_slider.setValue(strengths.channel_b)
        
        self.volume_a_slider.blockSignals(False)
        self.volume_b_slider.blockSignals(False)
        
        # Update labels
        self.update_volume_a_label(strengths.channel_a)
        self.update_volume_b_label(strengths.channel_b)
    
    def on_pulse_sent(self, pulses: CoyotePulses):
        # Update Channel A
        if pulses.channel_a:
            # Get the actual strength value
            strength_a = self.device.strengths.channel_a
            # Get the max strength from settings
            max_strength_a = settings.coyote_channel_a_strength_max.get()
            
            for pulse in pulses.channel_a:
                # Calculate effective intensity
                effective_intensity = pulse.intensity * (strength_a / 100)
                
                self.pulse_graph_a.add_pulse(
                    frequency=pulse.frequency,
                    intensity=pulse.intensity,
                    duration=pulse.duration,
                    current_strength=strength_a,
                    channel_limit=max_strength_a
                )
                
                # Add to envelope graph only if effective intensity is > 0
                if effective_intensity > 0:
                    self.envelope_graph.addPulse('A', pulse.intensity, pulse.duration, strength_a)

        # Update Channel B
        if pulses.channel_b:
            # Get the actual strength value
            strength_b = self.device.strengths.channel_b
            # Get the max strength from settings
            max_strength_b = settings.coyote_channel_b_strength_max.get()
            
            for pulse in pulses.channel_b:
                # Calculate effective intensity
                effective_intensity = pulse.intensity * (strength_b / 100)
                
                self.pulse_graph_b.add_pulse(
                    frequency=pulse.frequency,
                    intensity=pulse.intensity,
                    duration=pulse.duration,
                    current_strength=strength_b,
                    channel_limit=max_strength_b
                )
                
                # Add to envelope graph only if effective intensity is > 0
                if effective_intensity > 0:
                    self.envelope_graph.addPulse('B', pulse.intensity, pulse.duration, strength_b)

    def update_freq_min_a(self, value):
        """Update minimum frequency for channel A"""
        if value >= self.freq_max_a.value():
            self.freq_min_a.setValue(self.freq_max_a.value() - 10)
        else:
            settings.coyote_channel_a_freq_min.set(value)

    def update_freq_max_a(self, value):
        """Update maximum frequency for channel A"""
        if value <= self.freq_min_a.value():
            self.freq_max_a.setValue(self.freq_min_a.value() + 10)
        else:
            settings.coyote_channel_a_freq_max.set(value)

    def update_freq_min_b(self, value):
        """Update minimum frequency for channel B"""
        if value >= self.freq_max_b.value():
            self.freq_min_b.setValue(self.freq_max_b.value() - 10)
        else:
            settings.coyote_channel_b_freq_min.set(value)

    def update_freq_max_b(self, value):
        """Update maximum frequency for channel B"""
        if value <= self.freq_min_b.value():
            self.freq_max_b.setValue(self.freq_min_b.value() + 10)
        else:
            settings.coyote_channel_b_freq_max.set(value)

    def update_volume_a_label(self, value):
        # Calculate percentage based on max strength
        percentage = int((value / max(1, settings.coyote_channel_a_strength_max.get())) * 100)
        self.volume_a_label.setText(f"{value} ({percentage}%)")

    def update_volume_b_label(self, value):
        # Calculate percentage based on max strength
        percentage = int((value / max(1, settings.coyote_channel_b_strength_max.get())) * 100)
        self.volume_b_label.setText(f"{value} ({percentage}%)")
        
    def update_strength_max_a(self, value):
        """Update max strength for channel A and save to settings."""
        settings.coyote_channel_a_strength_max.set(value)
        
        # Update volume slider range
        current_value = self.volume_a_slider.value()
        self.volume_a_slider.setRange(0, value)
        
        # Update the volume label to reflect the new max strength
        self.update_volume_a_label(current_value)
        
        # If the current value exceeds the new max, cap it
        if current_value > value:
            self.volume_a_slider.setValue(value)
        
        # Send updated strength to device
        self.update_channel_a(self.volume_a_slider.value())
        
    def update_strength_max_b(self, value):
        """Update max strength for channel B and save to settings."""
        settings.coyote_channel_b_strength_max.set(value)
        
        # Update volume slider range
        current_value = self.volume_b_slider.value()
        self.volume_b_slider.setRange(0, value)
        
        # Update the volume label to reflect the new max strength
        self.update_volume_b_label(current_value)
        
        # If the current value exceeds the new max, cap it
        if current_value > value:
            self.volume_b_slider.setValue(value)
            
        # Send updated strength to device
        self.update_channel_b(self.volume_b_slider.value())

    def fetch_envelope_data(self):
        """Fetch shared envelope data and update the graph"""
        if self.device is None or self.device.algorithm is None or not self.isVisible():
            return

        try:
            env_data, env_period = self.device.algorithm.get_envelope_data()
            if env_data is not None and env_data.size > 0 and env_period > 0:
                self.envelope_graph.setEnvelopeData(env_data, env_period)
        except Exception as e:
            print(f"Error fetching envelope data: {str(e)}")