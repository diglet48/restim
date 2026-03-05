"""
Non-invasive dark mode overlay for restim.
Applies a Fusion-based dark palette + QSS tweaks + matplotlib/pyqtgraph theming.
"""

import matplotlib
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QStyleFactory


# ---------------------------------------------------------------------------
# Qt dark palette  (Fusion style)
# ---------------------------------------------------------------------------

def _make_dark_palette() -> QPalette:
    p = QPalette()
    # base colours
    WINDOW     = QColor(43, 43, 43)
    BASE       = QColor(30, 30, 30)
    ALT_BASE   = QColor(50, 50, 50)
    TEXT       = QColor(210, 210, 210)
    DIS_TEXT   = QColor(127, 127, 127)
    BRIGHT     = QColor(255, 255, 255)
    HIGHLIGHT  = QColor(42, 130, 218)
    HL_TEXT    = QColor(255, 255, 255)
    BUTTON     = QColor(53, 53, 53)
    LINK       = QColor(56, 170, 215)
    TOOLTIP_BG = QColor(60, 60, 60)
    TOOLTIP_FG = QColor(210, 210, 210)

    for group in (QPalette.ColorGroup.Active,
                  QPalette.ColorGroup.Inactive,
                  QPalette.ColorGroup.Disabled):
        p.setColor(group, QPalette.ColorRole.Window, WINDOW)
        p.setColor(group, QPalette.ColorRole.WindowText, TEXT)
        p.setColor(group, QPalette.ColorRole.Base, BASE)
        p.setColor(group, QPalette.ColorRole.AlternateBase, ALT_BASE)
        p.setColor(group, QPalette.ColorRole.ToolTipBase, TOOLTIP_BG)
        p.setColor(group, QPalette.ColorRole.ToolTipText, TOOLTIP_FG)
        p.setColor(group, QPalette.ColorRole.Text, TEXT)
        p.setColor(group, QPalette.ColorRole.Button, BUTTON)
        p.setColor(group, QPalette.ColorRole.ButtonText, TEXT)
        p.setColor(group, QPalette.ColorRole.BrightText, BRIGHT)
        p.setColor(group, QPalette.ColorRole.Link, LINK)
        p.setColor(group, QPalette.ColorRole.Highlight, HIGHLIGHT)
        p.setColor(group, QPalette.ColorRole.HighlightedText, HL_TEXT)

    # disabled-specific overrides
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, DIS_TEXT)
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, DIS_TEXT)
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, DIS_TEXT)

    return p


# ---------------------------------------------------------------------------
# Extra QSS for widgets that the palette alone doesn't fully theme
# ---------------------------------------------------------------------------

_DARK_QSS = """
/* tabs */
QTabWidget::pane { border: 1px solid #3a3a3a; }
QTabBar::tab {
    background: #353535; color: #d2d2d2;
    padding: 6px 14px; border: 1px solid #3a3a3a;
    border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
}
QTabBar::tab:selected { background: #2b2b2b; }
QTabBar::tab:hover    { background: #404040; }

/* group boxes */
QGroupBox {
    border: 1px solid #555; border-radius: 4px;
    margin-top: 0.5em; padding-top: 0.6em;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #d2d2d2; }

/* scroll bars */
QScrollBar:vertical   { background: #2b2b2b; width: 12px; }
QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 4px; }
QScrollBar:horizontal { background: #2b2b2b; height: 12px; }
QScrollBar::handle:horizontal { background: #555; min-width: 20px; border-radius: 4px; }

/* menu bar */
QMenuBar          { background: #2b2b2b; color: #d2d2d2; }
QMenuBar::item:selected { background: #404040; }
QMenu             { background: #2b2b2b; color: #d2d2d2; border: 1px solid #555; }
QMenu::item:selected { background: #2a82da; }

/* tool bar */
QToolBar { background: #2b2b2b; border: none; spacing: 4px; }
QToolButton       { color: #d2d2d2; }
QToolButton:hover { background: #404040; border-radius: 4px; }
QToolButton:checked { background: #2a82da; border-radius: 4px; }

/* line edits, text edits */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #1e1e1e; color: #d2d2d2;
    border: 1px solid #555; border-radius: 3px; padding: 2px;
}
QComboBox QAbstractItemView { background: #2b2b2b; color: #d2d2d2; selection-background-color: #2a82da; }

/* progress bar */
QProgressBar {
    background: #1e1e1e; border: 1px solid #555; border-radius: 3px;
    text-align: center; color: #d2d2d2;
}
QProgressBar::chunk { background: #2a82da; border-radius: 3px; }

/* sliders */
QSlider::groove:horizontal { background: #555; height: 6px; border-radius: 3px; }
QSlider::handle:horizontal { background: #2a82da; width: 14px; margin: -4px 0; border-radius: 7px; }
QSlider::groove:vertical   { background: #555; width: 6px; border-radius: 3px; }
QSlider::handle:vertical   { background: #2a82da; height: 14px; margin: 0 -4px; border-radius: 7px; }

/* checkboxes — just ensure text color */
QCheckBox { color: #d2d2d2; }

/* table / tree / list views */
QTableView, QTreeView, QListView, QHeaderView::section {
    background: #1e1e1e; color: #d2d2d2;
    border: 1px solid #3a3a3a; gridline-color: #3a3a3a;
}
QHeaderView::section {
    background: #353535; padding: 4px; border: 1px solid #3a3a3a;
}

/* status bar */
QStatusBar { background: #2b2b2b; color: #d2d2d2; }

/* splitter handle */
QSplitter::handle { background: #3a3a3a; }

/* tooltips */
QToolTip { background: #3c3c3c; color: #d2d2d2; border: 1px solid #555; }
"""


# ---------------------------------------------------------------------------
# Matplotlib dark theme
# ---------------------------------------------------------------------------

def _apply_matplotlib_dark():
    matplotlib.rcParams.update({
        'figure.facecolor': '#2b2b2b',
        'axes.facecolor':   '#1e1e1e',
        'axes.edgecolor':   '#888',
        'axes.labelcolor':  '#d2d2d2',
        'text.color':       '#d2d2d2',
        'xtick.color':      '#aaa',
        'ytick.color':      '#aaa',
        'grid.color':       '#444',
        'figure.edgecolor': '#2b2b2b',
        'savefig.facecolor':'#2b2b2b',
    })


# ---------------------------------------------------------------------------
# pyqtgraph dark theme
# ---------------------------------------------------------------------------

def _apply_pyqtgraph_dark():
    try:
        import pyqtgraph as pg
        pg.setConfigOptions(
            background='#1e1e1e',
            foreground='#d2d2d2',
        )
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_is_dark = False


def is_dark_mode() -> bool:
    """Return True if dark mode is currently active."""
    return _is_dark


def apply_dark_mode(app: QApplication):
    """Apply dark mode to the whole application. Call before showing any window."""
    global _is_dark

    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(_make_dark_palette())
    app.setStyleSheet(_DARK_QSS)

    _apply_matplotlib_dark()
    _apply_pyqtgraph_dark()

    _is_dark = True
