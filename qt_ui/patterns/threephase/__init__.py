# Automatically import all patterns to register them
# Priority patterns first (Mouse and Circle), then rest alphabetically
from .mouse import MousePattern
from .circle import CirclePattern

# Additional patterns in alphabetical order
from .butterfly import ButterflyPattern
from .deep_throb import DeepThrobPattern
from .figure_eight import FigureEightPattern
from .jerky_stroke import JerkyStrokePattern
from .lightning_strike import LightningStrikePattern
from .micro_circles import MicroCirclesPattern
from .orbiting_circles import OrbitingCirclesPattern
from .random_walk import RandomWalkPattern
from .rose_curve import RoseCurvePattern
from .spirograph import SpirographPattern
from .tremor_circle import TremorCirclePattern
from .vertical_oscillation import VerticalOscillationPattern
from .w_shape import WShapePattern
from .panning1 import PanningPattern1
from .panning2 import PanningPattern2

# Make patterns available at package level
__all__ = [
    'MousePattern', 'CirclePattern',  # Priority patterns first
    'ButterflyPattern', 'DeepThrobPattern', 'FigureEightPattern',
    'JerkyStrokePattern', 'LightningStrikePattern', 'MicroCirclesPattern',
    'OrbitingCirclesPattern', 'RandomWalkPattern', 'RoseCurvePattern',
    'SpirographPattern', 'TremorCirclePattern', 'VerticalOscillationPattern',
    'WShapePattern', 'PanningPattern1', 'PanningPattern2'
]
