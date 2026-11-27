"""Mixer channel strips, Editor panels, hardware transport, header.

UI only, no audio logic. Layout: channel strip per track (Tracks 1-4) plus a
Master strip on the right of the Mixer tab. No placeholder text blocks, no
"coming later" copy inside the UI. Panels look finished and compact.
"""

import math
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor, QLinearGradient, QPainter, QPainterPath, QPen,
)
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QVBoxLayout, QWidget,
)

from . import theme


# ---------------------------------------------------------------- widgets

class PanKnob(QWidget):
    """Small rotary pan knob. Drag vertically to turn, double-click recentres.

    Pure Qt painting, no dependencies. Value is -1.0 (L) .. +1.0 (R).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.PointingHandCursor)
        self.value = 0.0
        self._drag_y = None
        self._drag_start_value = 0.0
        self.setToolTip("Pan: drag vertically, double-click to centre")

    def minimumSizeHint(self):
        return self.size()

    def setValue(self, v):
        self.value = max(-1.0, min(1.0, float(v)))
        self.update()

    def mousePressEvent(self, event):
        self._drag_y = event.y()
        self._drag_start_value = self.value
        self.setFocus()

    def mouseMoveEvent(self, event):
        if self._drag_y is None:
            return
        delta = (self._drag_y - event.y()) / 60.0
        self.setValue(self._drag_start_value + delta)

    def mouseReleaseEvent(self, event):
        self._drag_y = None

    def mouseDoubleClickEvent(self, event):
        self.setValue(0.0)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Down):
            self.setValue(self.value - 0.05)
        elif event.key() in (Qt.Key_Right, Qt.Key_Up):
            self.setValue(self.value + 0.05)
        elif event.key() == Qt.Key_Home:
            self.setValue(0.0)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        radius = min(self.width(), self.height()) / 2.0 - 3

        # tick marks at L / C / R
        p.setPen(QPen(QColor(theme.TEXT_FAINT), 1))
        for ang in (-135, -90, -45):
            rad = math.radians(ang)
            x1 = cx + (radius + 1) * math.cos(rad)
            y1 = cy + (radius + 1) * math.sin(rad)
            x2 = cx + (radius + 4) * math.cos(rad)
            y2 = cy + (radius + 4) * math.sin(rad)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # dial body, subtle vertical gradient for depth
        grad = QLinearGradient(0, cy - radius, 0, cy + radius)
        grad.setColorAt(0, QColor(theme.PANEL_HI))
        grad.setColorAt(0.5, QColor(theme.PANEL_LIGHT))
        grad.setColorAt(1, QColor(theme.BG_DEEP))
        p.setBrush(grad)
        p.setPen(QPen(QColor(theme.BORDER), 1))
        p.drawEllipse(int(cx - radius), int(cy - radius),
                      int(radius * 2), int(radius * 2))

        # gold pointer: top at centre, rotates with value
        angle = -90 + self.value * 45.0  # -1 -> L(-135), 0 -> top, +1 -> R(-45)
        rad = math.radians(angle)
        x = cx + (radius - 5) * math.cos(rad)
        y = cy + (radius - 5) * math.sin(rad)
        p.setPen(QPen(QColor(theme.GOLD), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(int(cx), int(cy), int(x), int(y))
        p.end()


class LedMeter(QWidget):
    """Thin vertical LED-style meter, 10 segments, lit to self.level (0..1)."""

    SEGMENTS = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(10)
        self.setMinimumHeight(120)
        self.level = 0.62  # static UI demo level, no audio

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        gap = 3
        seg_h = (h - gap * (self.SEGMENTS - 1)) / float(self.SEGMENTS)
        lit = int(round(self.level * self.SEGMENTS))
        for i in range(self.SEGMENTS):
            # i = 0 is the bottom segment
            y = h - (i + 1) * seg_h - i * gap
            if i >= 8:
                on = QColor("#ff5a3c")
            elif i >= 6:
                on = QColor(theme.GOLD)
            else:
                on = QColor(theme.LED_GREEN)
            off = QColor("#1e1e1e")
            p.setPen(QPen(QColor(theme.BORDER_SOFT), 1))
            p.setBrush(on if i < lit else off)
            path = QPainterPath()
            path.addRoundedRect(1, int(y), w - 2, int(seg_h), 2, 2)
            p.drawPath(path)
        p.end()


def _toggle_button(text, object_name, tooltip):
    btn = QPushButton(text)
    btn.setObjectName("StripToggle")
    btn.setProperty("object_name", object_name)
    btn.setCheckable(True)
    btn.setToolTip(tooltip)
    # per-button object name via style hook: subclass trick not needed, the
    # stylesheet keys off #MuteBtn/#SoloBtn/#ArmBtn, so set objectName to the
    # combined id in addition: Qt allows only one objectName, so we keep
    # StripToggle for sizing and overlay the id by a second name is not
    # possible. Instead we give the button its real id and add a common
    # class via a subclass-free approach: set objectName to the specific id
    # and rely on the shared StripToggle rules not being needed (they are
    # duplicated in the specific selectors below via "StripToggle" only).
    # To keep the stylesheet in theme.py authoritative we simply keep
    # objectName="StripToggle" and set the active colour inline when toggled.
    btn.toggled.connect(lambda on, b=btn: _apply_toggle_colour(b, on))
    return btn


def _apply_toggle_colour(btn, on):
    name = btn.property("object_name") or ""
    colours = {
        "mute": "#d98a2b",
        "solo": "#3fae5a",
        "arm": "#e0442e",
    }
    if not on:
        btn.setProperty("on", False)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        return
    colour = colours.get(name, theme.GOLD)
    btn.setProperty("on", True)
    # foreground: dark on amber/green, white on red
    fg = "#ffffff" if name == "arm" else "#101010"
    btn.setStyleSheet(
        "QPushButton#StripToggle { background: %s; border-color: %s; color: %s; }"
        % (colour, colour, fg))
    btn.style().unpolish(btn)
    btn.style().polish(btn)


class ChannelStrip(QFrame):
    """One vertical mixer channel: label, meter, pan knob, fader, M/S/A."""

    def __init__(self, name, is_master=False, parent=None):
        super().__init__(parent)
        self.is_master = is_master
        self.setObjectName("ConsolePanel")
        self.setMinimumWidth(96 if not is_master else 112)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # label
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        colour = theme.GOLD if is_master else theme.TEXT
        weight = "bold" if is_master else "normal"
        label.setStyleSheet(
            "font-size: 9pt; font-weight: %s; color: %s; letter-spacing: 1px;"
            % (weight, colour))
        layout.addWidget(label)

        # meter + fader row
        mid = QHBoxLayout()
        mid.setSpacing(6)
        meter = LedMeter()
        meter.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        mid.addWidget(meter)

        fader = QSlider(Qt.Vertical)
        fader.setRange(0, 100)
        fader.setValue(80 if not is_master else 85)
        fader.setFixedWidth(36)
        fader.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        fader.setToolTip("Level")
        mid.addWidget(fader)
        layout.addLayout(mid, 1)

        # pan knob + value
        pan_row = QVBoxLayout()
        pan_row.setSpacing(2)
        pan_label = QLabel("PAN")
        pan_label.setAlignment(Qt.AlignCenter)
        pan_label.setStyleSheet(
            "font-size: 7pt; color: %s; letter-spacing: 1px;" % theme.TEXT_FAINT)
        pan_row.addWidget(pan_label)
        knob = PanKnob()
        knob_layout = QHBoxLayout()
        knob_layout.setContentsMargins(0, 0, 0, 0)
        knob_layout.addStretch(1)
        knob_layout.addWidget(knob)
        knob_layout.addStretch(1)
        pan_row.addLayout(knob_layout)
        layout.addLayout(pan_row)

        # Mute / Solo / Arm
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        self.mute_btn = _toggle_button("M", "mute", "Mute")
        self.solo_btn = _toggle_button("S", "solo", "Solo")
        self.arm_btn = _toggle_button("A", "arm", "Arm for recording")
        for b in (self.mute_btn, self.solo_btn, self.arm_btn):
            b.setFixedWidth(24)
            btn_row.addWidget(b)
        layout.addLayout(btn_row)


# ---------------------------------------------------------------- panels

class MixerPanel(QWidget):
    """Mixer tab: four track channel strips + Master strip on the right."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self.strips = []
        for i in range(1, 5):
            strip = ChannelStrip("TRACK %d" % i, is_master=False)
            self.strips.append(strip)
            root.addWidget(strip)

        # thin divider before Master
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("background: %s; width: 1px;" % theme.BORDER_SOFT)
        root.addWidget(divider)

        master = ChannelStrip("MASTER", is_master=True)
        self.strips.append(master)
        root.addWidget(master)
        root.addStretch(1)


class _EditorInset(QFrame):
    """Compact inset panel with a small heading and a short control row."""

    def __init__(self, title, controls, parent=None):
        super().__init__(parent)
        self.setObjectName("InsetPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(72)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        head = QLabel(title.upper())
        head.setStyleSheet(
            "font-size: 8pt; font-weight: bold; letter-spacing: 1px;"
            " color: %s;" % theme.TEXT_DIM)
        layout.addWidget(head)

        row = QHBoxLayout()
        row.setSpacing(8)
        for w in controls:
            row.addWidget(w)
        row.addStretch(1)
        layout.addLayout(row)


def _mini_button(text):
    btn = QPushButton(text)
    btn.setMinimumHeight(26)
    return btn


def _fader_row(label_text, value=70):
    box = QWidget()
    layout = QHBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    label = QLabel(label_text)
    label.setStyleSheet("font-size: 9pt; color: %s;" % theme.TEXT_DIM)
    label.setFixedWidth(64)
    layout.addWidget(label)
    slider = QSlider(Qt.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(value)
    slider.setFixedWidth(160)
    layout.addWidget(slider)
    return box


class EditorPanel(QWidget):
    """Editor tab: compact inset panels, no placeholder copy."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        root.addWidget(_EditorInset("Waveform display", [_fader_row("Zoom"), _mini_button("Fit")]))
        root.addWidget(_EditorInset("Selection", [_fader_row("Start"), _fader_row("End")]))
        root.addWidget(_EditorInset("File", [_mini_button("Open"), _mini_button("Save"), _mini_button("Export")]))
        root.addWidget(_EditorInset("Tools", [_mini_button("Normalise"), _mini_button("Fade in"), _mini_button("Fade out"), _mini_button("Trim silence")]))
        root.addStretch(1)


class TransportBar(QWidget):
    """Hardware-style transport: round Play/Stop/Record buttons + LED time."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TransportDock")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        play = QPushButton("▶")
        play.setObjectName("TransportRound")
        play.setFixedSize(52, 52)
        play.setToolTip("Play")
        play.clicked.connect(lambda: self._set_mode("play"))
        layout.addWidget(play)

        stop = QPushButton("■")
        stop.setObjectName("TransportRound")
        stop.setFixedSize(52, 52)
        stop.setToolTip("Stop")
        stop.clicked.connect(lambda: self._set_mode("stop"))
        layout.addWidget(stop)

        record = QPushButton("●")
        record.setObjectName("RecordRound")
        record.setFixedSize(52, 52)
        record.setToolTip("Record")
        record.clicked.connect(lambda: self._set_mode("record"))
        layout.addWidget(record)

        layout.addStretch(1)

        self.time_label = QLabel("00:00.0")
        self.time_label.setStyleSheet(theme.LED_STYLE)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setMinimumWidth(180)
        layout.addWidget(self.time_label)

        layout.addStretch(1)

        volume_label = QLabel("MASTER")
        volume_label.setStyleSheet(
            "font-size: 8pt; color: %s; letter-spacing: 1px;" % theme.TEXT_FAINT)
        layout.addWidget(volume_label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(80)
        slider.setFixedWidth(160)
        layout.addWidget(slider)

    def _set_mode(self, mode):
        if mode == "play":
            self.time_label.setText("▶ 00:00.0")
            self.time_label.setStyleSheet(theme.LED_PLAYING_STYLE)
        elif mode == "record":
            self.time_label.setText("● REC 00:00.0")
            self.time_label.setStyleSheet(theme.LED_RECORD_STYLE)
        else:
            self.time_label.setText("00:00.0")
            self.time_label.setStyleSheet(theme.LED_STYLE)


class Header(QWidget):
    """Top header: logo, app name, version badge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(12)

        logo = QLabel()
        logo.setFixedSize(120, 56)
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo.setPixmap(self._logo_pixmap())
        layout.addWidget(logo)

        title = QLabel("RevelateMix")
        title.setStyleSheet(
            "font-size: 15pt; font-weight: bold; color: %s;" % theme.GOLD)
        layout.addWidget(title)

        layout.addStretch(1)

        version = QLabel("v0.1  ·  CONSOLE")
        version.setStyleSheet(
            "font-size: 8pt; letter-spacing: 2px; color: %s;"
            " border: 1px solid %s; border-radius: 10px; padding: 4px 12px;"
            % (theme.TEXT_DIM, theme.BORDER))
        layout.addWidget(version)

    @staticmethod
    def _logo_pixmap():
        here = os.path.dirname(os.path.abspath(__file__))
        for name in ("logo.png", "logo.jpg"):
            path = os.path.normpath(os.path.join(here, "..", "assets", name))
            if os.path.exists(path):
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        120, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        from PyQt5.QtGui import QPixmap
        placeholder = QPixmap(120, 56)
        placeholder.fill(0x1a1a1a)
        return placeholder
