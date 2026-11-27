# RevelateMix v0.1 - UI skeleton

Lightweight 32-bit Windows audio app. This build is the frame only:
charcoal + warm gold theme, header with logo, Mixer / Editor tabs and a
transport bar. No audio logic yet.

## Run (Windows, Python 3.8 32-bit + PyQt5)
```
pip install -r requirements.txt
python main.py
```
or `python -m revelate_mix`.

## Build the exe (PyInstaller)
```
pip install pyinstaller
pyinstaller --noconfirm --windowed --name RevelateMix --add-data "assets;assets" main.py
```
The logo in `assets/logo.png` is picked up at runtime (header + window icon),
and PyInstaller bundles it with `--add-data "assets;assets"`.

## Layout
- `main.py` - entry point (PyInstaller target)
- `revelate_mix/main_window.py` - main window, menus, status bar
- `revelate_mix/panels.py` - header, Mixer/Editor placeholder panels, transport bar
- `revelate_mix/theme.py` - colours and Qt stylesheet
- `assets/logo.png` - official logo

## Smoke test (Linux, headless)
```
python -m py_compile main.py revelate_mix/*.py
QT_QPA_PLATFORM=offscreen python -c "from revelate_mix.main_window import MainWindow; from PyQt5.QtWidgets import QApplication; app=QApplication([]); w=MainWindow(); print(w.windowTitle(), w.tabs.count())"
```
