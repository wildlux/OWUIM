@echo off
chcp 65001 >nul
title Build OpenWebUI Manager - Windows EXE

echo ═══════════════════════════════════════════════════════
echo        Build OpenWebUI Manager per Windows
echo ═══════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

:: Verifica Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python non trovato!
    echo Installa Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Installa dipendenze
echo [1/3] Installazione dipendenze...
pip install PyQt5 pyinstaller --quiet

:: Pulisci build precedenti
echo [2/3] Pulizia build precedenti...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: Build
echo [3/3] Creazione eseguibile Windows...
echo.

pyinstaller --onefile --windowed --name "OpenWebUI-Manager" ^
    --add-data "scripts;scripts" ^
    --add-data "docs;docs" ^
    --add-data "tools;tools" ^
    --add-data "docker-compose.yml;." ^
    --add-data "manage.sh;." ^
    --hidden-import PyQt5 ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    --exclude-module tkinter ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    openwebui_gui.py

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════
    echo              Build completata con successo!
    echo ═══════════════════════════════════════════════════════
    echo.
    echo File creato: dist\OpenWebUI-Manager.exe
    echo.

    :: Mostra dimensione
    for %%A in (dist\OpenWebUI-Manager.exe) do echo Dimensione: %%~zA bytes
    echo.

    :: Apri cartella dist
    explorer dist
) else (
    echo.
    echo [ERRORE] Build fallita!
)

echo.
pause
