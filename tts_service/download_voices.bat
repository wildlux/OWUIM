@echo off
REM Download Voci Italiane per TTS Locale
REM Scarica Piper TTS + voci Paola e Riccardo

title Download Voci Italiane TTS

cd /d "%~dp0"

echo.
echo ====================================================
echo    DOWNLOAD VOCI ITALIANE - Piper TTS
echo ====================================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trovato!
    echo     Installa Python da https://python.org
    pause
    exit /b 1
)

REM Verifica requests
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [*] Installazione dipendenze...
    pip install requests
)

REM Esegui script
python download_voices.py

pause
