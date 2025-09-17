"""
Pattern base and registry system with decorator registration
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Set, Any

logger = logging.getLogger('restim.patterns.base')

_pattern_registry: Dict[str, Type['ThreephasePattern']] = {}
_pattern_categories: Dict[str, Set[str]] = {}

def register_pattern(category: str = "basic"):
    def decorator(pattern_class: Type['ThreephasePattern']):
        if not issubclass(pattern_class, ThreephasePattern):
            raise TypeError(f"Pattern {pattern_class.__name__} must inherit from ThreephasePattern")
        if not hasattr(pattern_class, 'display_name') or not pattern_class.display_name:
            raise ValueError(f"Pattern {pattern_class.__name__} must define display_name")
        display_name = pattern_class.display_name
        _pattern_registry[display_name] = pattern_class
        if category not in _pattern_categories:
            _pattern_categories[category] = set()
        _pattern_categories[category].add(display_name)
        pattern_class.category = category
        logger.debug(f"Registered pattern '{display_name}' in category '{category}'")
        return pattern_class
    return decorator

def get_registered_patterns() -> Dict[str, Type['ThreephasePattern']]:
    return _pattern_registry.copy()

def get_patterns_by_category(category: str) -> Dict[str, Type['ThreephasePattern']]:
    if category not in _pattern_categories:
        return {}
    return {name: _pattern_registry[name] for name in _pattern_categories[category] if name in _pattern_registry}

def get_all_categories() -> Set[str]:
    return set(_pattern_categories.keys())

def clear_registry():
    global _pattern_registry, _pattern_categories
    _pattern_registry.clear()
    _pattern_categories.clear()

class ThreephasePattern(ABC):
    display_name = "Abstract Pattern"
    description = "Base pattern class"
    category = "base"
    def __init__(self, amplitude: float = 1.0, velocity: float = 1.0):
        self.amplitude = amplitude
        self.velocity = velocity
    def name(self) -> str:
        return self.display_name
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        return {
            "name": cls.display_name,
            "description": cls.description,
            "category": cls.category,
            "class": cls
        }
    @abstractmethod
    def update(self, dt: float) -> tuple[float, float]:
        pass
