@echo off
setlocal
title Open WebUI Manager Lite

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM La GUI Lite usa solo Tkinter (incluso in Python)
REM Non richiede ambiente virtuale

python openwebui_gui_lite.py
