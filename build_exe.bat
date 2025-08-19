@echo off
pip install pyinstaller
pyinstaller --noconsole --onefile app.py
echo.
echo Build complete. Find your EXE in the dist\ folder (app.exe).
pause
