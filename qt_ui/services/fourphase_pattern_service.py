"""
Pattern Control Service for Fourphase
Handles pattern application and validation logic for fourphase patterns.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from qt_ui.patterns.fourphase.base import get_registered_patterns

logger = logging.getLogger('restim.pattern_service.fourphase')

@dataclass
class PatternParams:
    pattern_name: str
    amplitude: float = 10.0
    velocity: float = 1.0
    power: float = 100.0
    active: bool = True
    
    def validate(self) -> List[str]:
        errors = []
        if not self.pattern_name:
            errors.append("Pattern name is required")
        if not (0 <= self.amplitude <= 10):
            errors.append("Amplitude must be between 0 and 10")
        if not (0.1 <= self.velocity <= 10):
            errors.append("Velocity must be between 0.1 and 10")
        if not (0 <= self.power <= 100):
            errors.append("Power must be between 0 and 100")
        return errors

@dataclass
class ActivityRecord:
    pattern_name: str
    amplitude: float
    velocity: float
    power: float
    active: bool
    timestamp: datetime
    
    @classmethod
    def from_params(cls, params: PatternParams) -> 'ActivityRecord':
        return cls(
            pattern_name=params.pattern_name,
            amplitude=params.amplitude,
            velocity=params.velocity,
            power=params.power,
            active=params.active,
            timestamp=datetime.now()
        )

class FourphasePatternControlService:
    def __init__(self, max_history_size: int = 100):
        self.activity_history: List[ActivityRecord] = []
        self.max_history_size = max_history_size
        self._pattern_registry = get_registered_patterns()
    
    def get_available_patterns(self) -> List[Dict[str, Any]]:
        patterns = []
        for pattern_name, pattern_class in self._pattern_registry.items():
            if hasattr(pattern_class, 'display_name'):
                patterns.append({
                    "name": pattern_class.display_name,
                    "description": getattr(pattern_class, 'description', pattern_name),
                    "category": getattr(pattern_class, 'category', 'basic'),
                    "class_name": pattern_class.__name__
                })
            else:
                patterns.append({
                    "name": pattern_name,
                    "description": f"Pattern: {pattern_name}",
                    "category": "basic",
                    "class_name": pattern_class.__name__
                })
        return patterns
    
    def validate_pattern(self, pattern_name: str) -> bool:
        return pattern_name in self._pattern_registry
    
    def apply_pattern(self, params: PatternParams) -> Dict[str, Any]:
        errors = params.validate()
        if errors:
            logger.warning(f"Pattern validation failed: {errors}")
            return {
                "success": False,
                "errors": errors,
                "message": "Parameter validation failed"
            }
        if not self.validate_pattern(params.pattern_name):
            error_msg = f"Pattern '{params.pattern_name}' not found"
            logger.warning(error_msg)
            return {
                "success": False,
                "errors": [error_msg],
                "message": "Pattern not found"
            }
        activity = ActivityRecord.from_params(params)
        self.add_activity_record(activity)
        logger.info(f"Applied pattern: {params.pattern_name} (amp={params.amplitude}, vel={params.velocity}, power={params.power}, active={params.active})")
        return {
            "success": True,
            "errors": [],
            "message": f"Applied pattern '{params.pattern_name}' successfully",
            "params": params
        }
    
    def stop_stimulation(self) -> Dict[str, Any]:
        stop_params = PatternParams(
            pattern_name="Stop",
            amplitude=0,
            velocity=1.0,
            power=0,
            active=False
        )
        activity = ActivityRecord.from_params(stop_params)
        self.add_activity_record(activity)
        logger.info("Stimulation stopped")
        return {
            "success": True,
            "errors": [],
            "message": "Stimulation stopped successfully",
            "params": stop_params
        }
    
    def add_activity_record(self, record: ActivityRecord):
        self.activity_history.append(record)
        if len(self.activity_history) > self.max_history_size:
            self.activity_history = self.activity_history[-self.max_history_size:]
    
    def get_recent_activity(self, count: int = 10) -> List[ActivityRecord]:
        return self.activity_history[-count:]
    
    def get_last_pattern_params(self) -> Optional[PatternParams]:
        if not self.activity_history:
            return None
        last_record = self.activity_history[-1]
        return PatternParams(
            pattern_name=last_record.pattern_name,
            amplitude=last_record.amplitude,
            velocity=last_record.velocity,
            power=last_record.power,
            active=last_record.active
        )
    
    def build_activity_summary(self, recent_count: int = 5) -> str:
        if not self.activity_history:
            return "No recent activity."
        recent = self.get_recent_activity(recent_count)
        summary_lines = []
        for record in recent:
            status = "Active" if record.active else "Inactive"
            summary_lines.append(
                f"- {record.pattern_name}: {status}, Power={record.power}%, Amp={record.amplitude}, Vel={record.velocity} ({record.timestamp.strftime('%H:%M:%S')})"
            )
        return "Recent Activity:\n" + "\n".join(summary_lines)
