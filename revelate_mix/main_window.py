"""Main window: Mixer/Editor tabs directly under the menu bar, transport bar below."""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction, QLabel, QMainWindow, QMenuBar, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget,
)

from . import theme
from .panels import EditorPanel, MixerPanel, TransportBar, scaled_logo_pixmap

ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RevelateMix v0.1.6")
        self.setMinimumSize(900, 600)
        self._set_icon()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.addTab(MixerPanel(), "Mixer")
        self.tabs.addTab(EditorPanel(), "Editor")
        layout.addWidget(self.tabs, 1)

        layout.addWidget(TransportBar())

        self._build_menus()
        self._build_statusbar()

    def _set_icon(self):
        # Window/taskbar icon stays the FULL original logo (icon + wordmark):
        # assets/logo.png, the user's design from v0.1.4, restored here.
        # Loads it fresh each launch (no cached derivative), so a
        # replacement PNG is picked up unchanged.
        path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(path):
            pix = scaled_logo_pixmap(path, 64, 64)
            if not pix.isNull():
                self.setWindowIcon(QIcon(pix))

    def _build_menus(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Inline app logo: the gold audio-bars icon mark ONLY (no wordmark
        # text), as first item in the menu bar before File/Edit/Help.
        # Source is assets/logo_icon.png, cropped from the user's original
        # full logo (v0.1.4) without touching the artwork: the left
        # audio-bars mark, alpha-trimmed. The full original logo stays as
        # the window/taskbar icon via _set_icon().
        # The label is a child widget of the menu bar itself (not an action
        # icon): QMenuBar paints action icons at the small-icon size, which
        # shrank the wide logo into a 16px smudge. A child label paints at
        # its own size, so we anchor its height to the menu bar's height.
        # Left padding on the bar reserves the space so File/Edit/Help start
        # after the logo. The bar height grows with the logo so the row
        # never overflows. No text label beside the logo.
        # scaled_logo_pixmap shrinks it smoothly (stepwise
        # SmoothTransformation + device pixel ratio).
        logo_path = os.path.join(ASSETS_DIR, "logo_icon.png")
        logo_pix = scaled_logo_pixmap(logo_path, 26, 26)
        if not logo_pix.isNull():
        # Target roughly the height of the menu text at default DPI so it
        # reads as inline with File/Edit/Help. The bar is too short before
        # layout to trust its height(), so anchor directly: 30px is the
        # default text line height in the bar (padding + cap height).
            logo_label = QLabel(menu_bar)
            logo_label.setPixmap(logo_pix)
            logo_label.setToolTip("RevelateMix")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setGeometry(2, 4, logo_pix.width(), logo_pix.height())
            logo_label.show()
            # Reserve the logo's width as left padding so menus start after
            # it, and grow the bar so the row fits the logo vertically.
            menu_bar.setStyleSheet(
                theme.STYLESHEET + "\nQMenuBar { padding-left: %dpx; }" %
                (logo_pix.width() + 8))
            menu_bar.setFixedHeight(logo_pix.height() + 8)

        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("New project", self._not_yet)
        file_menu.addAction("Open...", self._not_yet)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        edit_menu = menu_bar.addMenu("&Edit")
        edit_menu.addAction("Cut", self._not_yet)
        edit_menu.addAction("Copy", self._not_yet)
        edit_menu.addAction("Paste", self._not_yet)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction("About RevelateMix", self._about)

    def _build_statusbar(self):
        status = QStatusBar(self)
        self.setStatusBar(status)
        status.showMessage("RevelateMix v0.1.6 skeleton. UI only, no audio yet.")

    def _not_yet(self):
        self.statusBar().showMessage("Audio comes after the layout is approved.")

    def _about(self):
        self.statusBar().showMessage(
            "RevelateMix v0.1.6. Charcoal + gold console. Mixer track lanes, Editor tab, hardware transport. No audio logic yet.")


def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("RevelateMix")
    app.setOrganizationName("Binuyo Legacy")
    app.setStyle("Fusion")
    # Dark palette + stylesheet: no widget can render default light/white
    # on Windows, including the mixer lane control containers.
    theme.apply_app_theme(app)

    window = MainWindow()
    window.show()
    return app.exec_()
