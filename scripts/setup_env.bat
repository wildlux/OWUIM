@echo off
setlocal
title Setup Ambiente Python - Open WebUI Manager

echo.
echo ======================================================================
echo        SETUP AMBIENTE PYTHON - Open WebUI Manager
echo ======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Verifica Python
echo [1/4] Verifica Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trovato!
    echo     Scarica da: https://www.python.org/downloads/
    echo     Assicurati di selezionare "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python trovato

REM Crea ambiente virtuale
echo.
echo [2/4] Creazione ambiente virtuale...
if exist "venv" (
    echo [!] Ambiente virtuale esistente trovato
    set /p choice="Vuoi ricrearlo? [s/N]: "
    if /i "%choice%"=="s" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Ambiente virtuale ricreato
    ) else (
        echo [OK] Ambiente virtuale esistente mantenuto
    )
) else (
    python -m venv venv
    echo [OK] Ambiente virtuale creato
)

REM Attiva venv e aggiorna pip
echo.
echo [3/4] Aggiornamento pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
echo [OK] pip aggiornato

REM Installa dipendenze
echo.
echo [4/4] Installazione dipendenze...
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Errore durante l'installazione
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  [OK] SETUP COMPLETATO!
echo ======================================================================
echo.
echo  Per avviare la GUI:
echo    - Doppio click su: run_gui.bat (GUI completa PyQt5)
echo    - Oppure:          run_gui_lite.bat (GUI leggera Tkinter)
echo.
echo  Per attivare manualmente l'ambiente:
echo    venv\Scripts\activate.bat
echo.
echo ======================================================================
pause
