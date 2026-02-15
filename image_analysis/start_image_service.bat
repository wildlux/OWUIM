@echo off
title Image Analysis Service
cd /d "%~dp0"

echo.
echo ======================================================================
echo          IMAGE ANALYSIS SERVICE per Open WebUI
echo ======================================================================
echo.
echo  Cartella: %~dp0
echo.

REM Vai alla cartella parent per usare il venv
cd ..

REM Cerca venv del progetto
if exist "venv\Scripts\python.exe" (
    set "PYTHON=venv\Scripts\python.exe"
    echo [OK] Ambiente virtuale trovato
) else (
    set "PYTHON=python"
    echo [!] Ambiente virtuale non trovato, uso Python di sistema
)

REM Verifica dipendenze
echo.
echo [*] Verifica dipendenze...
%PYTHON% -c "import fastapi, uvicorn, PIL, requests" 2>nul
if errorlevel 1 (
    echo [!] Dipendenze mancanti. Installazione...
    %PYTHON% -m pip install fastapi uvicorn Pillow requests python-multipart
)

REM Verifica Ollama
echo.
echo [*] Verifica Ollama...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo [!] Ollama non in esecuzione. Avvialo prima!
    echo     Comando: ollama serve
    pause
    exit /b 1
)
echo [OK] Ollama attivo

REM Verifica modello vision
echo.
echo [*] Verifica modello Vision...
curl -s http://localhost:11434/api/tags | findstr /i "llava vision bakllava" >nul
if errorlevel 1 (
    echo [!] Nessun modello vision trovato.
    echo.
    set /p install="Vuoi installare llava ora? [S/n]: "
    if /i not "%install%"=="n" (
        echo.
        echo [*] Download llava in corso...
        ollama pull llava
    )
) else (
    echo [OK] Modello vision trovato
)

echo.
echo ======================================================================
echo  Servizio in avvio su: http://localhost:5555
echo  Premi Ctrl+C per fermare
echo ======================================================================
echo.

REM Avvia il servizio
%PYTHON% image_analysis\image_service.py

pause
