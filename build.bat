@echo off
REM Build RevelateMix.exe with PyInstaller (Python 3.8 32-bit).
REM Run from Command Prompt (not Git CMD, keeps Python PATH).
cd /d "%~dp0"
pip install --timeout 120 PyQt5 pyinstaller
pyinstaller --noconfirm --windowed --name RevelateMix --add-data "assets;assets" main.py
echo.
echo Done. The exe is in dist\RevelateMix\RevelateMix.exe
pause
