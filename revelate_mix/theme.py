"""Charcoal / warm-gold theme. Single source of truth for colours and the Qt stylesheet."""

BG_DEEP = "#101010"
BG = "#1a1a1a"
PANEL = "#232323"
PANEL_LIGHT = "#2c2c2c"
BORDER = "#3a3a3a"
GOLD = "#d4af37"
GOLD_LIGHT = "#f0d675"
GOLD_DARK = "#9c7c2e"
TEXT = "#e8e4d8"
TEXT_DIM = "#a8a29a"
RECORD_RED = "#e0442e"

STYLESHEET = f"""
* {{ color: {TEXT}; }}
QMainWindow, QTabWidget::pane, QWidget {{ background: {BG}; }}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background: {PANEL};
    margin-top: -1px;
}}
QTabBar::tab {{
    background: {PANEL_LIGHT};
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 22px;
    margin-right: 4px;
    font-size: 10pt;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background: {BG_DEEP};
    color: {GOLD};
    border-bottom: 2px solid {GOLD};
}}
QTabBar::tab:!selected:hover {{ color: {TEXT}; }}
QPushButton {{
    background: {PANEL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 10pt;
}}
QPushButton:hover {{ border-color: {GOLD}; color: {GOLD_LIGHT}; }}
QPushButton:pressed {{ background: {GOLD_DARK}; }}
QPushButton:disabled {{ color: {TEXT_DIM}; border-color: {BORDER}; }}
QLabel {{ background: transparent; }}
QFrame {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 6px; }}
QSlider::groove:horizontal {{
    height: 6px; background: {BG_DEEP}; border-radius: 3px;
}}
QSlider::handle:horizontal {{
    width: 14px; height: 14px; background: {GOLD};
    border: 1px solid {GOLD_DARK}; border-radius: 7px; margin: -4px 0;
}}
QSlider::sub-page:horizontal {{ background: {GOLD_DARK}; border-radius: 3px; }}
QScrollArea {{ border: none; background: {PANEL}; }}
QScrollBar:vertical {{ background: {PANEL}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background: {GOLD_DARK}; }}
QComboBox, QLineEdit {{
    background: {BG_DEEP}; border: 1px solid {BORDER}; border-radius: 4px;
    padding: 4px 8px; min-height: 24px;
}}
QComboBox:focus, QLineEdit:focus {{ border-color: {GOLD}; }}
QMenuBar {{ background: {BG_DEEP}; border-bottom: 1px solid {BORDER}; }}
QMenuBar::item {{ padding: 4px 8px; }}
QMenuBar::item:selected {{ background: {GOLD_DARK}; }}
QStatusBar {{ background: {BG_DEEP}; border-top: 1px solid {BORDER}; }}
QToolTip {{ background: {PANEL_LIGHT}; border: 1px solid {GOLD_DARK}; padding: 4px; }}
"""

# Transport button colours (inline, since they beat the stylesheet).
PLAY_STYLE = (
    f"background: {GOLD_DARK}; color: #101010; font-size: 11pt; font-weight: bold;"
    f" padding: 8px 18px; border-radius: 6px;"
)
RECORD_STYLE = (
    f"background: {PANEL_LIGHT}; color: {RECORD_RED}; font-size: 11pt;"
    f" font-weight: bold; padding: 8px 18px; border-radius: 6px;"
)
TIME_STYLE = (
    f"background: {BG_DEEP}; color: {GOLD}; font-family: Consolas, monospace;"
    f" font-size: 16pt; font-weight: bold; padding: 4px 12px;"
    f" border: 1px solid {BORDER}; border-radius: 6px;"
)
