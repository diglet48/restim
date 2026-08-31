"""
Prevents the OS from sleeping (or turning off the display) while restim is actively running.
"""
import logging

from wakepy import keep
from wakepy.core import Mode

logger = logging.getLogger('restim.sleep_inhibitor')


class SleepInhibitor:
    def __init__(self):
        self._mode: Mode | None = None

    def start(self):
        if self._mode is not None:
            return
        mode = keep.presenting(on_fail='warn')
        mode.__enter__()
        self._mode = mode
        logger.info("SleepInhibitor activated")

    def stop(self):
        if self._mode is None:
            return
        self._mode.__exit__(None, None, None)
        self._mode = None
        logger.info("SleepInhibitor deactivated")
