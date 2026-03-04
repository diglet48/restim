# Import patterns for manual instantiation (no automatic registration)
from .mouse import MousePattern
from .sequence import SequencePattern

# Make patterns available at package level
__all__ = ['MousePattern', 'SequencePattern']
