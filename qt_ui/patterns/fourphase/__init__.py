# Import patterns for manual instantiation (no automatic registration)
from .mouse import MousePattern
from .orbit import OrbitPattern
from .sequence import SequencePattern
from .spiral import SpiralPattern

# Make patterns available at package level
__all__ = ['MousePattern', 'OrbitPattern', 'SequencePattern', 'SpiralPattern']
