"""Charcoal / warm-gold console theme.

Base #1a1a1a with depth (bordered panels, subtle gradients via qlineargradient,
inner shadows via dark groove + light top border tricks). Gold #d4af37 is used
only as an accent: active states, fader thumbs, logo/title, LED readouts.
No default Windows grey anywhere: menu bar, tabs, buttons and menus are all
dark-styled. Qt stylesheets only, no new dependencies.
"""

BG_DEEP = "#101010"
BG = "#1a1a1a"
BG_RAISED = "#222222"
PANEL = "#232323"
PANEL_LIGHT = "#2c2c2c"
PANEL_HI = "#363636"
BORDER = "#3a3a3a"
BORDER_SOFT = "#2e2e2e"
INNER_SHADOW = "#0c0c0c"
GOLD = "#d4af37"
GOLD_LIGHT = "#f0d675"
GOLD_DARK = "#9c7c2e"
TEXT = "#e8e4d8"
TEXT_DIM = "#a8a29a"
TEXT_FAINT = "#7a756c"
LED_GREEN = "#3dff7a"
RECORD_RED = "#e0442e"
SOLO_GREEN = "#3fae5a"
MUTE_AMBER = "#d98a2b"
ARM_RED = "#e0442e"


def apply_app_theme(app):
    """Apply the charcoal + gold theme so NO widget can fall back to a
    default light/white palette. Two layers, both dark:

    1. A dark QPalette: the Windows style engine paints every widget
       that has no stylesheet background (empty container widgets with
       no autoFillBackground, and any control a stylesheet rule misses)
       from the palette. With the default light palette those canvases
       render as default white/light on Windows; dark on Linux because
       the offscreen plugin does not repaint them.
    2. The full STYLESHEET on the application object.

    Track lanes, labels, VOL/PAN sliders, M/S/A buttons, the Master
    section, Editor panels and transport all pick this up because the
    stylesheet is applied app-wide and the palette sits underneath.
    """
    from PyQt5.QtGui import QBrush, QColor, QPalette

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT))
    palette.setColor(QPalette.Base, QColor(BG_DEEP))
    palette.setColor(QPalette.AlternateBase, QColor(PANEL))
    palette.setColor(QPalette.Text, QColor(TEXT))
    palette.setColor(QPalette.Button, QColor(PANEL_LIGHT))
    palette.setColor(QPalette.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.Highlight, QColor(GOLD_DARK))
    palette.setColor(QPalette.HighlightedText, QColor("#101010"))
    palette.setColor(QPalette.ToolTipBase, QColor(PANEL_LIGHT))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(TEXT_FAINT))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(TEXT_FAINT))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(TEXT_FAINT))
    palette.setBrush(QPalette.Midlight, QBrush(QColor(PANEL_HI)))
    palette.setBrush(QPalette.Mid, QBrush(QColor(BORDER)))
    palette.setBrush(QPalette.Dark, QBrush(QColor(BORDER_SOFT)))
    palette.setBrush(QPalette.Shadow, QBrush(QColor(INNER_SHADOW)))
    palette.setBrush(QPalette.Active, QPalette.Window, QBrush(QColor(BG)))
    palette.setBrush(QPalette.Inactive, QPalette.Window, QBrush(QColor(BG)))
    palette.setBrush(QPalette.Disabled, QPalette.Window, QBrush(QColor(BG)))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)
    return app

STYLESHEET = f"""
* {{ color: {TEXT}; font-family: "Segoe UI", "Segoe UI Symbol", sans-serif; }}
QMainWindow, QWidget, QFrame, QLabel, QTabWidget::pane, QScrollArea,
QDialog, QMenuBar, QStatusBar, QToolBar, QComboBox, QLineEdit {{ background: {BG}; }}
QMainWindow::separator {{ background: {BORDER_SOFT}; height: 1px; }}

/* ---- menu bar + menus: fully dark, no Windows grey ---- */
QMenuBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_HI}, stop:0.5 {PANEL}, stop:1 {BG_DEEP});
    border-bottom: 1px solid {BORDER};
    padding: 3px 4px;
    spacing: 2px;
}}
QMenuBar::item {{
    padding: 5px 10px;
    border-radius: 4px;
    color: {TEXT_DIM};
}}
QMenuBar::item:selected {{ background: {GOLD_DARK}; color: #101010; }}
QMenuBar::item:pressed {{ background: {GOLD}; color: #101010; }}
QMenu {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    padding: 4px;
}}
QMenu::item {{ padding: 5px 26px 5px 22px; color: {TEXT}; border-radius: 4px; }}
QMenu::item:selected {{ background: {GOLD_DARK}; color: #101010; }}
QMenu::item:disabled {{ color: {TEXT_FAINT}; }}
QMenu::separator {{ height: 1px; background: {BORDER_SOFT}; margin: 5px 8px; }}
QMenu::indicator {{ width: 14px; height: 14px; }}

/* ---- tabs ---- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-top: 1px solid {PANEL_HI};
    border-radius: 0 0 8px 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL}, stop:1 {BG_DEEP});
    margin-top: -1px;
}}
QTabBar {{
    padding-top: 5px;
}}
QTabBar::tab {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_LIGHT}, stop:1 {PANEL});
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 12px 30px;
    min-width: 120px;
    min-height: 32px;
    margin-right: 6px;
    margin-left: 2px;
    font-size: 10pt;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_RAISED}, stop:1 {BG_DEEP});
    color: {GOLD};
    border-bottom: 2px solid {GOLD};
}}
QTabBar::tab:!selected:hover {{ color: {TEXT}; border-color: {GOLD_DARK}; }}

/* ---- buttons ---- */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_LIGHT}, stop:1 {PANEL});
    border: 1px solid {BORDER};
    border-top: 1px solid {PANEL_HI};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 10pt;
}}
QPushButton:hover {{ border-color: {GOLD}; color: {GOLD_LIGHT}; }}
QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG_DEEP}, stop:1 {PANEL});
    border-color: {GOLD_DARK};
}}
QPushButton:disabled {{ color: {TEXT_FAINT}; border-color: {BORDER_SOFT}; }}
QPushButton:focus {{ outline: none; border-color: {GOLD}; }}

/* ---- transport round buttons ---- */
QPushButton#TransportRound {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_HI}, stop:0.5 {PANEL_LIGHT}, stop:1 {BG_DEEP});
    border: 1px solid {BORDER};
    border-radius: 26px;
    font-size: 13pt;
    font-weight: bold;
    padding: 0;
}}
QPushButton#TransportRound:hover {{ border-color: {GOLD}; color: {GOLD_LIGHT}; }}
QPushButton#TransportRound:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {GOLD_DARK}, stop:1 {GOLD});
    color: #101010;
}}
QPushButton#TransportRoundCloser {{ border-radius: 20px; font-size: 11pt; }}
QPushButton#RecordRound {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_HI}, stop:0.5 {PANEL_LIGHT}, stop:1 {BG_DEEP});
    border: 1px solid {BORDER};
    border-radius: 26px;
    font-size: 13pt;
    font-weight: bold;
    padding: 0;
    color: {RECORD_RED};
}}
QPushButton#RecordRound:hover {{ border-color: {RECORD_RED}; }}
QPushButton#RecordRound:pressed, QPushButton#RecordRound[armed="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7a1f14, stop:1 {RECORD_RED});
    color: #ffffff;
}}

/* ---- strip Mute/Solo/Arm ---- */
QPushButton#StripToggle {{
    font-size: 8pt;
    font-weight: bold;
    padding: 3px 0;
    border-radius: 4px;
    min-height: 18px;
}}
QPushButton#StripToggle[on="true"] {{ color: #101010; }}
QPushButton#StripToggle#MuteBtn[on="true"] {{ background: {MUTE_AMBER}; border-color: {MUTE_AMBER}; }}
QPushButton#StripToggle#SoloBtn[on="true"] {{ background: {SOLO_GREEN}; border-color: {SOLO_GREEN}; }}
QPushButton#StripToggle#ArmBtn[on="true"] {{ background: {ARM_RED}; border-color: {ARM_RED}; color: #ffffff; }}

/* ---- frames / panels ---- */
QLabel {{ background: transparent; }}
QFrame#ConsolePanel {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_LIGHT}, stop:0.25 {PANEL}, stop:1 {BG_DEEP});
    border: 1px solid {BORDER};
    border-top: 1px solid {PANEL_HI};
    border-radius: 8px;
}}
QFrame#InsetPanel {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {INNER_SHADOW}, stop:0.3 {BG_DEEP}, stop:1 {PANEL});
    border: 1px solid {BORDER_SOFT};
    border-top: 1px solid {INNER_SHADOW};
    border-radius: 6px;
}}
QFrame#HeaderBar {{ background: {BG_DEEP}; border: none; border-bottom: 1px solid {BORDER}; border-radius: 0; }}
QFrame#TransportDock {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_LIGHT}, stop:0.5 {PANEL}, stop:1 {BG_DEEP});
    border: 1px solid {BORDER};
    border-top: 1px solid {PANEL_HI};
    border-radius: 8px;
}}

/* ---- faders ---- */
QSlider::groove:horizontal {{
    height: 6px; background: {INNER_SHADOW};
    border: 1px solid {BORDER_SOFT}; border-radius: 3px;
}}
QSlider::handle:horizontal {{
    width: 14px; height: 14px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {GOLD_LIGHT}, stop:0.5 {GOLD}, stop:1 {GOLD_DARK});
    border: 1px solid {GOLD_DARK}; border-radius: 7px; margin: -5px 0;
}}
QSlider::sub-page:horizontal {{ background: {GOLD_DARK}; border-radius: 3px; }}
QSlider::groove:vertical {{
    width: 6px; background: {INNER_SHADOW};
    border: 1px solid {BORDER_SOFT}; border-radius: 3px;
}}
QSlider::handle:vertical {{
    width: 26px; height: 14px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {GOLD_DARK}, stop:0.5 {GOLD_LIGHT}, stop:1 {GOLD_DARK});
    border: 1px solid {GOLD_DARK}; border-radius: 4px; margin: 0 -11px;
}}
QSlider::sub-page:vertical {{ background: {GOLD_DARK}; border-radius: 3px; }}
QSlider#PanKnob::groove:horizontal {{ height: 4px; }}
QSlider#PanKnob::handle:horizontal {{
    width: 12px; height: 12px; border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {PANEL_HI}, stop:1 {BG_DEEP});
    border: 1px solid {BORDER}; margin: -5px 0;
}}

/* ---- scroll + inputs + status ---- */
QScrollArea {{ border: none; background: {PANEL}; }}
QScrollBar:vertical {{ background: {PANEL}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background: {GOLD_DARK}; }}
QComboBox, QLineEdit {{
    background: {BG_DEEP}; border: 1px solid {BORDER}; border-radius: 4px;
    padding: 4px 8px; min-height: 24px;
}}
QComboBox:focus, QLineEdit:focus {{ border-color: {GOLD}; }}
QStatusBar {{ background: {BG_DEEP}; border-top: 1px solid {BORDER}; color: {TEXT_DIM}; }}
QStatusBar::item {{ border: none; }}
QToolTip {{ background: {PANEL_LIGHT}; border: 1px solid {GOLD_DARK}; padding: 4px; }}
"""

# Transport round buttons (objectName + fixed size handled in panels.py).
# These are kept here so the palette lives in one place.
STOP_STYLE = (
    f"color: {TEXT};"
)
PLAY_ARMED_STYLE = (
    f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
    f" stop:0 {GOLD_DARK}, stop:1 {GOLD}); color: #101010;"
)

# LED time display: dark inset, amber/gold mono readout, inner-shadow border.
LED_STYLE = (
    f"background: {INNER_SHADOW}; color: {GOLD};"
    " font-family: Consolas, 'Courier New', monospace;"
    " font-size: 20pt; font-weight: bold; letter-spacing: 2px;"
    " padding: 6px 18px;"
    f" border: 1px solid {BORDER_SOFT}; border-top: 1px solid #000000;"
    " border-radius: 6px;"
)
LED_PLAYING_STYLE = (
    f"background: {INNER_SHADOW}; color: {LED_GREEN};"
    " font-family: Consolas, 'Courier New', monospace;"
    " font-size: 20pt; font-weight: bold; letter-spacing: 2px;"
    " padding: 6px 18px;"
    f" border: 1px solid {BORDER_SOFT}; border-top: 1px solid #000000;"
    " border-radius: 6px;"
)
LED_RECORD_STYLE = (
    f"background: {INNER_SHADOW}; color: {RECORD_RED};"
    " font-family: Consolas, 'Courier New', monospace;"
    " font-size: 20pt; font-weight: bold; letter-spacing: 2px;"
    " padding: 6px 18px;"
    f" border: 1px solid {BORDER_SOFT}; border-top: 1px solid #000000;"
    " border-radius: 6px;"
)

# Kept for backward compat with anything importing the old names.
PLAY_STYLE = PLAY_ARMED_STYLE
RECORD_STYLE = f"color: {RECORD_RED};"
TIME_STYLE = LED_STYLE
