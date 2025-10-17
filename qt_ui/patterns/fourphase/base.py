"""
Base class for Fourphase patterns (matching original implementation)
"""
from abc import ABC, abstractmethod

class FourphasePattern(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def update(self, dt: float):
        ...
