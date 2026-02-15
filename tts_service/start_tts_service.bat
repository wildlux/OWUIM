@echo off
title TTS Service - Sintesi Vocale Italiana
cd /d "%~dp0\.."

echo.
echo ======================================================================
echo          TTS SERVICE - Sintesi Vocale Italiana
echo ======================================================================
echo.

REM Cerca venv del progetto padre
set "PROJECT_ROOT=%~dp0\.."
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON=%PROJECT_ROOT%\venv\Scripts\python.exe"
    echo [OK] Ambiente virtuale trovato
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    set "PYTHON=python"
    echo [OK] Ambiente virtuale attivato
) else (
    set "PYTHON=python"
    echo [!] Ambiente virtuale non trovato, uso Python di sistema
)

REM Verifica dipendenze
echo.
echo [*] Verifica dipendenze...
%PYTHON% -c "import fastapi, uvicorn, requests" 2>nul
if errorlevel 1 (
    echo [!] Dipendenze base mancanti. Installazione...
    %PYTHON% -m pip install fastapi uvicorn requests
)

REM Verifica edge-tts (backend principale)
%PYTHON% -c "import edge_tts" 2>nul
if errorlevel 1 (
    echo [!] edge-tts non installato (consigliato per migliore qualita')
    set /p install="Vuoi installarlo ora? [S/n]: "
    if /i not "!install!"=="n" (
        %PYTHON% -m pip install edge-tts
    )
)

echo.
echo ======================================================================
echo  Servizio TTS in avvio su: http://localhost:5556
echo.
echo  Endpoint principali:
echo    POST /speak    - Sintetizza testo
echo    POST /test     - Test voce
echo    GET /backends  - Lista backend
echo    GET /voices/{backend}  - Lista voci
echo.
echo  Premi Ctrl+C per fermare
echo ======================================================================
echo.

%PYTHON% tts_service\tts_local.py

pause
