"""Mixer track lanes, Editor panels, hardware transport, header.

UI only, no audio logic. Mixer tab layout (v0.1.2, MixPad-inspired):
tracks stacked as horizontal lanes top-to-bottom, each lane a compact
row with track name, M/S/A buttons, horizontal volume slider, pan
control and a waveform/lane area taking the rest of the width, so the
whole project is visible at a glance on a small laptop screen.
Plus a Master lane at the bottom. No placeholder text blocks.
"""

import math
import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import (
    QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap,
)
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSlider, QVBoxLayout, QWidget,
)

from . import theme

# ---------------------------------------------------------------- logo


def scaled_logo_pixmap(path, target_w, target_h, device_ratio=1.0):
    """Load assets/logo.png fresh and downscale it smoothly for a small target.

    A single SmoothTransformation shrink from a large logo (e.g. 496x219
    down to ~68x30 in the menu bar) still softens the wordmark: Qt's single
    pass has to average very many source pixels per destination pixel.
    Halving the pixmap step by step (each step with SmoothTransformation)
    keeps more detail at the final size, the same trick image editors use
    for small exports. The result is painted at a device pixel ratio so
    labels on scaled/displays with a logical-to-device ratio above 1 do not
    get stretched back up. Nothing is cached here: callers pass the file
    path, so a new higher-quality PNG dropped in as assets/logo.png is
    picked up on the next launch with no code change.
    """
    pix = QPixmap(path)
    if pix.isNull():
        return pix
    target_size = QSize(
        int(round(target_w)), int(round(target_h)))
    if pix.size() != target_size:
        current = pix
        while (current.width() > target_w * 2
               or current.height() > target_h * 2):
            current = current.scaled(
                max(1, current.width() // 2),
                max(1, current.height() // 2),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
        current = current.scaled(
            target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pix = current
    if device_ratio and device_ratio > 1.0:
        # Paint at device resolution but present at the logical size: the
        # label keeps showing target_w x target_h, the pixels stay sharp.
        sharp = QPixmap(pix.size() * device_ratio)
        sharp.setDevicePixelRatio(device_ratio)
        painter = QPainter(sharp)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        pix = sharp
    return pix


# ---------------------------------------------------------------- widgets

class PanKnob(QWidget):
    """Small rotary pan knob. Drag vertically to turn, double-click recentres.

    Pure Qt painting, no dependencies. Value is -1.0 (L) .. +1.0 (R).
    """

    def __init__(self, size=44, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
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


class HorizontalLedMeter(QWidget):
    """Thin horizontal LED meter for a track lane (0..1 level, UI only)."""

    SEGMENTS = 16

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(10)
        self.setMinimumWidth(80)
        self.level = 0.62

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        gap = 2
        seg_w = (w - gap * (self.SEGMENTS - 1)) / float(self.SEGMENTS)
        lit = int(round(self.level * self.SEGMENTS))
        for i in range(self.SEGMENTS):
            x = i * (seg_w + gap)
            if i >= 13:
                on = QColor("#ff5a3c")
            elif i >= 10:
                on = QColor(theme.GOLD)
            else:
                on = QColor(theme.LED_GREEN)
            off = QColor("#1e1e1e")
            p.setPen(QPen(QColor(theme.BORDER_SOFT), 1))
            p.setBrush(on if i < lit else off)
            path = QPainterPath()
            path.addRoundedRect(int(x), 1, int(seg_w), h - 2, 2, 2)
            p.drawPath(path)
        p.end()


def _toggle_button(text, object_name, tooltip):
    btn = QPushButton(text)
    btn.setObjectName("StripToggle")
    btn.setProperty("object_name", object_name)
    btn.setCheckable(True)
    btn.setToolTip(tooltip)
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


class LaneWaveform(QWidget):
    """Empty waveform/lane area: dark inset panel with centre line + grid."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InsetPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(120)

    def paintEvent(self, event):
        p = QPainter(self)
        # dark inset background
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(theme.INNER_SHADOW))
        grad.setColorAt(0.4, QColor(theme.BG_DEEP))
        grad.setColorAt(1, QColor(theme.PANEL))
        p.setBrush(grad)
        p.setPen(QPen(QColor(theme.BORDER_SOFT), 1))
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width() - 2, self.height() - 2, 5, 5)
        p.drawPath(path)
        # faint vertical grid (one tick per second, UI only)
        p.setPen(QPen(QColor(theme.BORDER_SOFT), 1))
        step = max(24, self.width() // 12)
        x = step
        while x < self.width():
            p.drawLine(x, 4, x, self.height() - 4)
            x += step
        # centre line, gold-dim
        mid = self.height() // 2
        p.setPen(QPen(QColor(theme.GOLD_DARK), 1))
        p.drawLine(4, mid, self.width() - 4, mid)
        p.end()


class TrackLane(QFrame):
    """One horizontal track lane (MixPad-style):

    [ name + M/S/A | volume slider | pan | meter ]  | waveform area
    """

    def __init__(self, name, is_master=False, parent=None):
        super().__init__(parent)
        self.is_master = is_master
        self.lane_name = name
        self.setObjectName("ConsolePanel")
        self.setMinimumHeight(62)
        self.setMaximumHeight(76 if not is_master else 68)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root = QHBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 6)
        root.setSpacing(8)

        # ---- left control block (fixed width, stacked compactly) ----
        controls = QVBoxLayout()
        controls.setSpacing(3)
        controls.setContentsMargins(0, 0, 0, 0)

        # row 1: name + M/S/A
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        label = QLabel(name)
        colour = theme.GOLD if is_master else theme.TEXT
        weight = "bold" if is_master else "bold"
        label.setStyleSheet(
            "font-size: 9pt; font-weight: %s; color: %s;"
            % (weight, colour))
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row1.addWidget(label, 1)

        self.mute_btn = _toggle_button("M", "mute", "Mute")
        self.solo_btn = _toggle_button("S", "solo", "Solo")
        self.arm_btn = _toggle_button("A", "arm", "Arm for recording")
        for b in (self.mute_btn, self.solo_btn, self.arm_btn):
            b.setFixedSize(26, 20)
            row1.addWidget(b)
        controls.addLayout(row1)

        # row 2: volume slider (gold thumb via theme) + value-ish spacing
        vol_row = QHBoxLayout()
        vol_row.setSpacing(4)
        vol_label = QLabel("VOL")
        vol_label.setStyleSheet(
            "font-size: 7pt; color: %s; letter-spacing: 1px;"
            % theme.TEXT_FAINT)
        vol_row.addWidget(vol_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(85 if is_master else 80)
        self.volume_slider.setToolTip("Volume")
        vol_row.addWidget(self.volume_slider, 1)
        controls.addLayout(vol_row)

        # row 3: pan (small knob + pan slider for compact lane use)
        pan_row = QHBoxLayout()
        pan_row.setSpacing(4)
        pan_label = QLabel("PAN")
        pan_label.setStyleSheet(
            "font-size: 7pt; color: %s; letter-spacing: 1px;"
            % theme.TEXT_FAINT)
        pan_row.addWidget(pan_label)
        self.pan_knob = PanKnob(size=26)
        pan_row.addWidget(self.pan_knob)
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(-50, 50)
        self.pan_slider.setValue(0)
        self.pan_slider.setToolTip("Pan (L-C-R)")
        pan_row.addWidget(self.pan_slider, 1)
        # keep knob + slider in sync, UI only
        self.pan_slider.valueChanged.connect(self._on_pan_slider)
        self.pan_knob.setValue(0.0)
        controls.addLayout(pan_row)

        control_box = QWidget()
        control_box.setLayout(controls)
        control_box.setFixedWidth(300)
        control_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        root.addWidget(control_box)

        # thin vertical divider between controls and lane area
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("background: %s; width: 1px;" % theme.BORDER_SOFT)
        root.addWidget(divider)

        # ---- waveform / lane area (rest of the width) ----
        right = QVBoxLayout()
        right.setSpacing(3)
        right.setContentsMargins(0, 0, 0, 0)
        self.waveform = LaneWaveform()
        right.addWidget(self.waveform, 1)
        self.meter = HorizontalLedMeter()
        right.addWidget(self.meter)
        root.addLayout(right, 1)

    def _on_pan_slider(self, value):
        self.pan_knob.setValue(value / 50.0)


# keep old name as alias so nothing importing ChannelStrip breaks
ChannelStrip = TrackLane


class MixerPanel(QWidget):
    """Mixer tab: 4 stacked horizontal track lanes + Master lane below."""

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(6)

        # time ruler aligned with the waveform area (controls block is 300px)
        ruler_row = QHBoxLayout()
        ruler_row.setContentsMargins(0, 0, 0, 0)
        spacer = QWidget()
        spacer.setFixedWidth(308)  # 300 controls + margins/spacing
        ruler_row.addWidget(spacer)
        ruler = QLabel("0:00        0:01        0:02        0:03        "
                       "0:04        0:05        0:06        0:07        0:08")
        ruler.setStyleSheet(
            "font-size: 7pt; color: %s; letter-spacing: 1px;"
            % theme.TEXT_FAINT)
        ruler_row.addWidget(ruler, 1)
        root.addLayout(ruler_row)

        self.lanes = []
        for i in range(1, 5):
            lane = TrackLane("Untitled Track %d" % i, is_master=False)
            self.lanes.append(lane)
            root.addWidget(lane)

        # divider above Master
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(
            "background: %s; height: 1px; margin: 2px 0;" % theme.BORDER_SOFT)
        root.addWidget(divider)

        master = TrackLane("Master", is_master=True)
        self.lanes.append(master)
        root.addWidget(master)

        root.addStretch(1)

    # backward-compat alias used by older code/tests
    @property
    def strips(self):
        return self.lanes


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
    """Legacy top header: logo, app name, version badge.

    Kept for import compatibility but no longer added to the main window
    (v0.1.2: Mixer/Editor tabs sit directly under the menu bar, the logo
    still lives on as the window/taskbar icon from assets/logo.png).
    """

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

        version = QLabel("v0.1.2  ·  LANES")
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
                pix = scaled_logo_pixmap(path, 120, 56)
                if not pix.isNull():
                    return pix
        placeholder = QPixmap(120, 56)
        placeholder.fill(0x1a1a1a)
        return placeholder
