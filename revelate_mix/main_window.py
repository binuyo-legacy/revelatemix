"""Main window: Mixer/Editor tabs directly under the menu bar, transport bar below."""

import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction, QLabel, QMainWindow, QMenuBar, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget,
)

from . import theme
from .panels import EditorPanel, MixerPanel, TransportBar

ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RevelateMix v0.1.3")
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
        # Transparent-background logo for the window/taskbar icon, same size
        # as the inline menu-bar logo so both read as one brand mark.
        path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                pix = pix.scaled(QSize(64, 64), Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
            self.setWindowIcon(QIcon(pix))

    def _build_menus(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Inline app logo: transparent-background logo as first item in the
        # menu bar, sized to sit on the same line as File/Edit/Help.
        # The label is a child widget of the menu bar itself (not an action
        # icon): QMenuBar paints action icons at the small-icon size, which
        # shrank the wide logo into a 16px smudge. A child label paints at
        # its own size, so we anchor its height to the menu bar's height.
        # Left padding on the bar reserves the space so File/Edit/Help start
        # after the logo. The bar height grows with the logo so the row
        # never overflows. No text label beside the logo.
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo_pix = QPixmap(logo_path)
        if not logo_pix.isNull():
        # Target roughly the height of the menu text at default DPI so it
        # reads as inline with File/Edit/Help. The bar is too short before
        # layout to trust its height(), so anchor directly: 30px is the
        # default text line height in the bar (padding + cap height).
            target_h = 30
            scale = logo_pix.width() / float(max(1, logo_pix.height()))
            logo_pix = logo_pix.scaled(
                QSize(int(target_h * scale), target_h),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        status.showMessage("RevelateMix v0.1.3 skeleton. UI only, no audio yet.")

    def _not_yet(self):
        self.statusBar().showMessage("Audio comes after the layout is approved.")

    def _about(self):
        self.statusBar().showMessage(
            "RevelateMix v0.1.3. Charcoal + gold console. Mixer track lanes, Editor tab, hardware transport. No audio logic yet.")


def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("RevelateMix")
    app.setOrganizationName("Binuyo Legacy")
    app.setStyle("Fusion")
    app.setStyleSheet(theme.STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec_()
