"""
Global hotkey listener using pynput.

Provides system-wide spacebar and middle-click long-press detection for
Finish mode activation, even when restim is not the focused window.

Emits Qt signals on the main thread via QMetaObject.invokeMethod.
"""
from __future__ import annotations

import logging
import time
import threading
from typing import Optional

from PySide6 import QtCore

logger = logging.getLogger('restim.global_hotkeys')

# Try to import pynput — optional dependency
try:
    from pynput import keyboard as pynput_kb
    from pynput import mouse as pynput_mouse
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    logger.info("pynput not installed — global hotkeys unavailable. "
                "Install with: pip install pynput")


class GlobalHotkeyListener(QtCore.QObject):
    """Runs pynput keyboard + mouse listeners on background threads and
    emits Qt signals when the spacebar or middle mouse button is
    long-pressed or short-pressed.

    Signals
    -------
    long_press_triggered : emitted after hold threshold reached
    short_press_triggered : emitted on short press (release before threshold)
    """

    long_press_triggered = QtCore.Signal()   # held long enough → activate
    short_press_triggered = QtCore.Signal()  # quick tap → deactivate

    def __init__(self, hold_ms: int = 800, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self._hold_ms = hold_ms / 1000.0  # seconds
        self._enabled = False

        # State shared between listener threads (protected by lock)
        self._lock = threading.Lock()
        self._press_time: Optional[float] = None
        self._held = False
        self._timer: Optional[threading.Timer] = None

        self._kb_listener: Optional[pynput_kb.Listener] = None if HAS_PYNPUT else None
        self._mouse_listener: Optional[pynput_mouse.Listener] = None if HAS_PYNPUT else None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Start listening for global hotkeys."""
        if not HAS_PYNPUT:
            logger.warning("Cannot start global hotkeys — pynput not installed")
            return
        if self._enabled:
            return
        self._enabled = True

        self._kb_listener = pynput_kb.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._kb_listener.daemon = True
        self._kb_listener.start()

        self._mouse_listener = pynput_mouse.Listener(
            on_click=self._on_mouse_click,
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        logger.info("Global hotkey listeners started")

    def stop(self):
        """Stop listening for global hotkeys."""
        if not self._enabled:
            return
        self._enabled = False
        self._cancel_timer()

        if self._kb_listener is not None:
            self._kb_listener.stop()
            self._kb_listener = None
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None

        logger.info("Global hotkey listeners stopped")

    def is_running(self) -> bool:
        return self._enabled

    @staticmethod
    def is_available() -> bool:
        return HAS_PYNPUT

    # ------------------------------------------------------------------
    # pynput callbacks (run on listener threads)
    # ------------------------------------------------------------------

    def _on_key_press(self, key):
        if not self._enabled:
            return
        try:
            if key == pynput_kb.Key.space:
                self._handle_press()
        except Exception:
            pass

    def _on_key_release(self, key):
        if not self._enabled:
            return
        try:
            if key == pynput_kb.Key.space:
                self._handle_release()
        except Exception:
            pass

    def _on_mouse_click(self, x, y, button, pressed):
        if not self._enabled:
            return
        try:
            if button == pynput_mouse.Button.middle:
                if pressed:
                    self._handle_press()
                else:
                    self._handle_release()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Shared press/release logic
    # ------------------------------------------------------------------

    def _handle_press(self):
        with self._lock:
            if self._press_time is not None:
                return  # already tracking a press
            self._press_time = time.time()
            self._held = False
            self._cancel_timer_unlocked()
            self._timer = threading.Timer(self._hold_ms, self._hold_timeout)
            self._timer.daemon = True
            self._timer.start()

    def _handle_release(self):
        with self._lock:
            if self._press_time is None:
                return
            if not self._held:
                # Released before threshold → short press
                self._cancel_timer_unlocked()
                self._press_time = None
                # Emit on Qt main thread
                QtCore.QMetaObject.invokeMethod(
                    self, '_emit_short_press', QtCore.Qt.QueuedConnection)
            else:
                # Was already held — nothing to do on release
                self._press_time = None

    def _hold_timeout(self):
        """Called by threading.Timer after hold threshold."""
        with self._lock:
            if self._press_time is None:
                return
            self._held = True
        # Emit on Qt main thread
        QtCore.QMetaObject.invokeMethod(
            self, '_emit_long_press', QtCore.Qt.QueuedConnection)

    # ------------------------------------------------------------------
    # Qt-thread signal emitters (invoked via QMetaObject)
    # ------------------------------------------------------------------

    @QtCore.Slot()
    def _emit_long_press(self):
        self.long_press_triggered.emit()

    @QtCore.Slot()
    def _emit_short_press(self):
        self.short_press_triggered.emit()

    # ------------------------------------------------------------------
    # Timer helpers
    # ------------------------------------------------------------------

    def _cancel_timer(self):
        with self._lock:
            self._cancel_timer_unlocked()

    def _cancel_timer_unlocked(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
