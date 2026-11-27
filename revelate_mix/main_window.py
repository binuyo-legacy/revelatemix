"""Main window: Mixer/Editor tabs directly under the menu bar, transport bar below."""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QStatusBar, QTabWidget, QVBoxLayout, QWidget

from . import theme
from .panels import EditorPanel, MixerPanel, TransportBar

ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RevelateMix v0.1.2")
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
        path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(path):
            self.setWindowIcon(QIcon(QPixmap(path)))

    def _build_menus(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

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
        status.showMessage("RevelateMix v0.1.2 skeleton. UI only, no audio yet.")

    def _not_yet(self):
        self.statusBar().showMessage("Audio comes after the layout is approved.")

    def _about(self):
        self.statusBar().showMessage(
            "RevelateMix v0.1.2. Charcoal + gold console. Mixer track lanes, Editor tab, hardware transport. No audio logic yet.")


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
