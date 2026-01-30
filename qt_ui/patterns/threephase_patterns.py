import time
import logging
import numpy as np
from PySide6 import QtCore
import qt_ui.settings
from stim_math.axis import AbstractAxis, WriteProtectedAxis
from qt_ui.patterns.threephase.base import get_registered_patterns
from qt_ui.patterns.threephase.mouse import MousePattern
from qt_ui.services.pattern_service import PatternControlService
# Import other patterns to trigger registration
import qt_ui.patterns.threephase  # This will import and register all patterns

logger = logging.getLogger('restim.motion_generation')

class ThreephaseMotionGenerator(QtCore.QObject):
    def __init__(self, parent, alpha: AbstractAxis, beta: AbstractAxis):
        super().__init__(parent)
        self.alpha = alpha
        self.beta = beta

        self.script_alpha = None
        self.script_beta = None

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
        if isinstance(pattern, MousePattern):
            self.pattern = self.mouse_pattern
        elif pattern in self.patterns:
            self.pattern = pattern

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

        if not self.any_scripts_loaded():
            if isinstance(self.pattern, MousePattern):
                if self.pattern.last_position_is_mouse_position():
                    a = self.alpha.last_value()
                    b = self.beta.last_value()
                else:
                    a = self.alpha.interpolate(time.time() - self.latency)
                    b = self.beta.interpolate(time.time() - self.latency)
                self.position_updated.emit(a, b)
            else:
                a, b = self.pattern.update(dt * self.velocity)
                self.alpha.add(a)
                self.beta.add(b)
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

    position_updated = QtCore.Signal(float, float)  # a, b