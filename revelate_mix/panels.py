"""Placeholder panels for the Mixer and Editor tabs. No audio logic yet."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLayout, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QVBoxLayout, QWidget,
)

from . import theme


class PlaceholderPanel(QFrame):
    """A labelled empty box used wherever real controls will land later."""

    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"font-size: 11pt; font-weight: bold; color: {theme.GOLD};")
        layout.addWidget(label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setAlignment(Qt.AlignCenter)
            sub.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 9pt;")
            layout.addWidget(sub)


def _row(*widgets, spacing=8):
    box = QWidget()
    layout = QHBoxLayout(box)
    layout.setSpacing(spacing)
    layout.setContentsMargins(0, 0, 0, 0)
    for w in widgets:
        if isinstance(w, QLayout):
            layout.addLayout(w)
        else:
            layout.addWidget(w)
    return box


class MixerPanel(QWidget):
    """Left track/clip area + right side panels, Mixer tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(8, 8, 8, 8)

        # Left: track list (placeholder strips, one per future track).
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel("Tracks (coming soon)")
        heading.setStyleSheet(f"color: {theme.TEXT_DIM}; font-weight: bold;")
        left_layout.addWidget(heading)
        for i in range(1, 5):
            left_layout.addWidget(PlaceholderPanel(
                f"Track {i}", "clip area, volume / pan and mute come later"))
        left_layout.addStretch(1)
        root.addWidget(left, 3)

        # Right: side panels.
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(PlaceholderPanel("Master output", "master fader comes later"))
        right_layout.addWidget(PlaceholderPanel("Effects (v2)", "stock sounds and 32-bit VST come later"))
        right_layout.addWidget(PlaceholderPanel("Guided mode (v1)", "plain-language commands come later"))
        right_layout.addStretch(1)
        root.addWidget(right, 2)


class EditorPanel(QWidget):
    """Right side panels for the Editor tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(8, 8, 8, 8)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        heading = QLabel("Single-file editor (coming soon)")
        heading.setStyleSheet(f"color: {theme.TEXT_DIM}; font-weight: bold;")
        left_layout.addWidget(heading)
        left_layout.addWidget(PlaceholderPanel("Waveform", "cut / trim / split comes later"))
        left_layout.addWidget(PlaceholderPanel("Convert", "WAV / MP3 export comes later"))
        left_layout.addStretch(1)
        root.addWidget(left, 3)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(PlaceholderPanel("File info", "format, length and sample rate come later"))
        right_layout.addWidget(PlaceholderPanel("Tools", "normalise, fade and clean up come later"))
        right_layout.addStretch(1)
        root.addWidget(right, 2)


class TransportBar(QWidget):
    """Bottom bar: play / stop / record buttons + time display. UI only."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 6, 10, 6)

        play = QPushButton("▶ Play")
        play.setStyleSheet(theme.PLAY_STYLE)
        play.clicked.connect(self._on_play)
        layout.addWidget(play)

        stop = QPushButton("■ Stop")
        stop.clicked.connect(self._on_stop)
        layout.addWidget(stop)

        record = QPushButton("● Record")
        record.setStyleSheet(theme.RECORD_STYLE)
        record.clicked.connect(self._on_record)
        layout.addWidget(record)

        layout.addStretch(1)

        self.time_label = QLabel("00:00.0")
        self.time_label.setStyleSheet(theme.TIME_STYLE)
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        layout.addStretch(1)

        slider = QSlider(Qt.Horizontal)
        slider.setFixedWidth(180)
        layout.addWidget(slider)

        volume = QLabel("Volume")
        volume.setStyleSheet(f"color: {theme.TEXT_DIM};")
        layout.addWidget(volume)

    def _on_play(self):
        self.time_label.setText("▶ 00:00.0")

    def _on_stop(self):
        self.time_label.setText("00:00.0")

    def _on_record(self):
        self.time_label.setText("● 00:00.0")


class Header(QWidget):
    """Top header: logo, app name, version."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)

        logo = QLabel()
        logo.setFixedSize(120, 64)
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo.setPixmap(self._logo_pixmap())
        layout.addWidget(logo)

        title = QLabel("RevelateMix")
        title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {theme.GOLD};")
        layout.addWidget(title)

        layout.addStretch(1)

        version = QLabel("v0.1 skeleton, UI only")
        version.setStyleSheet(f"color: {theme.TEXT_DIM}; font-size: 9pt;")
        layout.addWidget(version)

    @staticmethod
    def _logo_pixmap():
        import os
        from PyQt5.QtCore import Qt as _Qt
        from PyQt5.QtGui import QPixmap

        here = os.path.dirname(os.path.abspath(__file__))
        for name in ("logo.png", "logo.jpg"):
            path = os.path.normpath(os.path.join(here, "..", "assets", name))
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        120, 64, _Qt.KeepAspectRatio, _Qt.SmoothTransformation)
        placeholder = QPixmap(120, 64)
        placeholder.fill(0x1a1a1a)
        return placeholder
