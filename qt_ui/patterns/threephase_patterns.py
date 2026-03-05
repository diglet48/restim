import time
import logging
import numpy as np
from PySide6 import QtCore
import qt_ui.settings
from stim_math.axis import AbstractAxis, WriteProtectedAxis
from qt_ui.patterns.threephase.base import get_registered_patterns, get_patterns_by_category
from qt_ui.patterns.threephase.mouse import MousePattern
from qt_ui.services.pattern_service import PatternControlService
# Import other patterns to trigger registration (including YAML events)
import qt_ui.patterns.threephase

logger = logging.getLogger('restim.motion_generation')

class ThreephaseMotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis):
        super().__init__(parent)
        self.alpha = alpha
        self.beta = beta

        self.script_alpha = None
        self.script_beta = None

        # Extended axes that YAML event patterns can control
        # Wired from mainwindow after construction
        self.extra_axes = {}          # name → AbstractAxis
        self._extra_axes_enabled = {  # user-toggled enabled state per axis
            'volume': True,
            'pulse_frequency': True,
            'pulse_width': True,
            'carrier_frequency': False,
        }
        self._extra_axes_user_values = {}   # snapshot for restore on pattern switch
        self._pattern_controls_extra = False  # true when current pattern is YAML

        # Finish mode: overlay a pattern over funscript
        self._finish_armed = False
        self._finish_active = False
        self._finish_pattern = None

        # Initialize pattern service for preferences
        self.pattern_service = PatternControlService()

        # Instantiate MousePattern with axes
        self.mouse_pattern = MousePattern(alpha, beta)

        # Default to mouse pattern
        self.pattern = self.mouse_pattern

        self.velocity = 1
        self.last_update_time = time.time()
        self.latency = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timeout)
        self.timer.setInterval(int(1000 / 60.0))

        self.refreshSettings()

    def set_enable(self, enable):
        if enable:
            self.timer.start()
        else:
            self.timer.stop()

    def refresh_patterns(self):
        """Refresh the patterns list based on current user preferences"""
        # Get available patterns from the service, respecting user preferences
        available_patterns = self.pattern_service.get_available_patterns(respect_user_preferences=True)
        
        # Get registry for pattern classes
        registry = get_registered_patterns()
        
        # Rebuild patterns list
        self.patterns = []
        
        for pattern_info in available_patterns:
            pattern_name = pattern_info['name']
            class_name = pattern_info['class_name']
            
            if class_name == 'MousePattern':
                # Always include mouse pattern (special case with axes)
                self.patterns.append(self.mouse_pattern)
            elif pattern_name in registry:
                # Instantiate other patterns
                pattern_cls = registry[pattern_name]
                self.patterns.append(pattern_cls())
            else:
                # Fallback - find by class name
                for reg_name, pattern_cls in registry.items():
                    if pattern_cls.__name__ == class_name:
                        self.patterns.append(pattern_cls())
                        break
        
        logger.info(f"Refreshed patterns: {len(self.patterns)} patterns loaded")
        for pattern in self.patterns:
            logger.debug(f"  - {pattern.name()}")

    def set_pattern(self, pattern):
        # Release extra axes when switching away from a YAML pattern
        if self._pattern_controls_extra:
            self._release_extra_axes()

        if isinstance(pattern, MousePattern):
            self.pattern = self.mouse_pattern
        elif pattern in self.patterns:
            self.pattern = pattern

        # Check if new pattern is YAML-based (has update_extended returning values)
        from qt_ui.patterns.threephase.yaml_event_pattern import YamlEventPattern
        self._pattern_controls_extra = isinstance(self.pattern, YamlEventPattern)
        if self._pattern_controls_extra:
            self._snapshot_extra_axes()

    def set_scripts(self, alpha, beta):
        self.script_alpha = alpha if isinstance(alpha, WriteProtectedAxis) else None
        self.script_beta = beta if isinstance(beta, WriteProtectedAxis) else None

    def any_scripts_loaded(self):
        return (self.script_alpha, self.script_beta) != (None, None)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def timeout(self):
        dt = time.time() - self.last_update_time
        self.last_update_time = time.time()

        if not self.any_scripts_loaded() or self._finish_active:
            active_pattern = self._finish_pattern if self._finish_active else self.pattern

            if isinstance(active_pattern, MousePattern):
                if active_pattern.last_position_is_mouse_position():
                    a = self.alpha.last_value()
                    b = self.beta.last_value()
                else:
                    a = self.alpha.interpolate(time.time() - self.latency)
                    b = self.beta.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b)
            else:
                a, b = active_pattern.update(dt * self.velocity)
                self.alpha.add(a)
                self.beta.add(b)

                # Handle extended axes (YAML event patterns)
                extended = active_pattern.update_extended(dt * self.velocity)
                if extended:
                    self._write_extended_axes(extended)

                a = self.alpha.interpolate(time.time() - self.latency)
                b = self.beta.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b)
        else:
            if self.script_alpha:
                a = self.script_alpha.interpolate(time.time() - self.latency)
            else:
                a = self.alpha.interpolate(time.time() - self.latency)
            if self.script_beta:
                b = self.script_beta.interpolate(time.time() - self.latency)
            else:
                b = self.beta.interpolate(time.time() - self.latency)
            self.position_updated.emit(a, b)

    def mouse_event(self, a, b):
        if self.pattern == self.mouse_pattern and not self.any_scripts_loaded():
            self.mouse_pattern.mouse_event(a, b)
            self.alpha.add(a)
            self.beta.add(b)
            self.position_updated.emit(a, b)

    def refreshSettings(self):
        self.timer.setInterval(int(1000 // np.clip(qt_ui.settings.display_fps.get(), 1.0, 500.0)))
        self.latency = qt_ui.settings.display_latency.get() / 1000.0
        self.refresh_patterns()

    # ------------------------------------------------------------------
    # Extended axis helpers (YAML event patterns)
    # ------------------------------------------------------------------

    def set_extra_axis(self, name: str, axis: AbstractAxis):
        """Register an axis that YAML patterns can write to."""
        self.extra_axes[name] = axis

    def set_extra_axis_enabled(self, name: str, enabled: bool):
        """Toggle whether a specific extra axis is controlled by patterns."""
        self._extra_axes_enabled[name] = enabled

    def is_extra_axis_enabled(self, name: str) -> bool:
        return self._extra_axes_enabled.get(name, False)

    def _write_extended_axes(self, extended: dict):
        """Write extended axis values from a YAML pattern tick."""
        for axis_name, value in extended.items():
            if axis_name not in self.extra_axes:
                continue
            if not self._extra_axes_enabled.get(axis_name, False):
                continue
            self.extra_axes[axis_name].add(value)

    def _snapshot_extra_axes(self):
        """Capture current extra axis values so we can restore them later."""
        self._extra_axes_user_values.clear()
        for name, axis in self.extra_axes.items():
            try:
                self._extra_axes_user_values[name] = axis.last_value()
            except Exception:
                self._extra_axes_user_values[name] = 0.0

    def _release_extra_axes(self):
        """Restore extra axes to their pre-pattern values."""
        for name, value in self._extra_axes_user_values.items():
            if name in self.extra_axes:
                self.extra_axes[name].add(value)
        self._extra_axes_user_values.clear()
        self._pattern_controls_extra = False

    # ------------------------------------------------------------------
    # Finish mode (overlay pattern over funscript)
    # ------------------------------------------------------------------

    def arm_finish(self, armed: bool):
        """Arm or disarm the finish pattern overlay."""
        self._finish_armed = armed
        if not armed:
            self.deactivate_finish()

    def is_finish_armed(self) -> bool:
        return self._finish_armed

    def activate_finish(self):
        """Activate finish mode — play current pattern over funscript."""
        if not self._finish_armed:
            return
        self._finish_pattern = self.pattern
        self._finish_active = True
        # Snapshot extra axes before overlay
        self._snapshot_extra_axes()
        self._pattern_controls_extra = True
        self.finish_state_changed.emit(True)
        logger.info(f"Finish activated: {self._finish_pattern.name()}")

    def deactivate_finish(self):
        """Deactivate finish mode — return to funscript."""
        if self._finish_active:
            self._release_extra_axes()
            self._finish_active = False
            self._finish_pattern = None
            self.finish_state_changed.emit(False)
            logger.info("Finish deactivated")

    def is_finish_active(self) -> bool:
        return self._finish_active

    position_updated = QtCore.Signal(float, float)  # a, b
    finish_state_changed = QtCore.Signal(bool)  # active/inactive