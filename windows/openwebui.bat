@echo off
setlocal enabledelayedexpansion
title Open WebUI + Ollama + TTS

REM ======================================================================
REM  Open WebUI + Ollama - Gestore Unificato Windows
REM  Dual-Mode: Docker (ottimale) / Python (fallback)
REM  Include: OpenedAI Speech (TTS locale)
REM ======================================================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
cd /d "%PROJECT_DIR%"

if "%1"=="" goto :menu
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="install" goto :install
if "%1"=="status" goto :status
if "%1"=="wsl" goto :wsl
if "%1"=="test-tts" goto :test_tts
if "%1"=="logs" goto :logs
goto :menu

:menu
cls
echo.
echo ======================================================================
echo          OPEN WEBUI + OLLAMA + TTS - Sistema AI Locale
echo ======================================================================
echo.
echo   +------------------------------------------------------------------+
echo   ^|  Si consiglia Docker per massimizzare efficienza energetica,    ^|
echo   ^|  memoria e potenza di calcolo per i modelli AI locali.          ^|
echo   +------------------------------------------------------------------+
echo.
echo    [1] Avvia servizi (Open WebUI + Ollama + TTS)
echo    [2] Ferma servizi
echo    [3] Stato servizi
echo    [4] Installa/Configura
echo    [5] Risolvi problemi WSL2/Docker
echo    [6] Test TTS (sintesi vocale)
echo    [7] Mostra log
echo    [0] Esci
echo.
echo ======================================================================
echo.
set /p choice="Scegli: "

if "%choice%"=="1" goto :start
if "%choice%"=="2" goto :stop
if "%choice%"=="3" goto :status
if "%choice%"=="4" goto :install
if "%choice%"=="5" goto :wsl
if "%choice%"=="6" goto :test_tts
if "%choice%"=="7" goto :logs
if "%choice%"=="0" exit /b 0
goto :menu

REM ======================================================================
REM  AVVIO (Try Docker -> Fallback Python)
REM ======================================================================
:start
cls
echo.
echo ======================================================================
echo                         AVVIO SERVIZI
echo ======================================================================
echo.

REM Prova Docker
docker info >nul 2>&1
if errorlevel 1 goto :start_python

echo Modalita': DOCKER (efficienza ottimale)
echo.
echo [1/4] Avvio Ollama...
start /b "" ollama serve >nul 2>&1
timeout /t 2 >nul
echo    [OK] Ollama

echo [2/4] Avvio container (Open WebUI + TTS)...
docker compose up -d
if errorlevel 1 goto :start_python
echo    [OK] Container

echo [3/4] Attesa Open WebUI...
set /a count=0
:wait_docker
timeout /t 1 >nul
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! lss 30 goto :wait_docker
)
echo    [OK] Open WebUI pronto

echo [4/4] Attesa TTS (OpenedAI Speech)...
set /a count=0
:wait_tts
timeout /t 1 >nul
curl -s http://localhost:8000/v1/models >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! lss 20 goto :wait_tts
)
curl -s http://localhost:8000/v1/models >nul 2>&1
if errorlevel 1 (
    echo    [!] TTS non ancora pronto (attendi qualche secondo)
) else (
    echo    [OK] TTS pronto
)

echo.
echo ======================================================================
echo  [OK] AVVIATO
echo    Open WebUI:  http://localhost:3000
echo    Ollama API:  http://localhost:11434
echo    TTS API:     http://localhost:8000
echo    Efficienza: *****
echo ======================================================================
timeout /t 2 >nul
start http://localhost:3000
goto :end

:start_python
echo.
echo Modalita': PYTHON (fallback - Docker non disponibile)
echo.
echo  [!] Per prestazioni AI ottimali, configura Docker/WSL2
echo  [!] TTS non disponibile in modalita' Python
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo [X] Ollama non trovato. Scarica da: https://ollama.com/download/windows
    goto :end
)

if not exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    echo [X] Ambiente Python non trovato. Esegui: openwebui.bat install
    goto :end
)

echo [1/3] Avvio Ollama...
start "Ollama" /min ollama serve
timeout /t 3 >nul
echo    [OK] Ollama

echo [2/3] Avvio Open WebUI...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
start "OpenWebUI" /min cmd /c "open-webui serve"

echo [3/3] Attesa servizio...
set /a count=0
:wait_python
timeout /t 1 >nul
curl -s http://localhost:8080 >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! lss 45 goto :wait_python
)
echo    [OK] Pronto

echo.
echo ======================================================================
echo  [OK] AVVIATO - http://localhost:8080
echo    Efficienza: *** (usa Docker per *****)
echo    TTS: Non disponibile (richiede Docker)
echo ======================================================================
timeout /t 2 >nul
start http://localhost:8080
goto :end

REM ======================================================================
REM  STOP
REM ======================================================================
:stop
echo.
echo ======================================================================
echo                        ARRESTO SERVIZI
echo ======================================================================
echo.
echo [1/3] Container Docker (Open WebUI + TTS)...
docker compose down >nul 2>&1
echo    [OK]

echo [2/3] Open WebUI Python...
taskkill /f /fi "WINDOWTITLE eq OpenWebUI*" >nul 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list 2^>nul ^| find "PID:"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | find "open-webui" >nul && taskkill /f /pid %%a >nul 2>&1
)
echo    [OK]

echo [3/3] Ollama...
taskkill /f /im ollama.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Ollama*" >nul 2>&1
echo    [OK]

echo.
echo ======================================================================
echo  [OK] Servizi arrestati
echo ======================================================================
goto :end

REM ======================================================================
REM  STATUS
REM ======================================================================
:status
echo.
echo ======================================================================
echo                         STATO SERVIZI
echo ======================================================================
echo.

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker:       [X] Non disponibile
) else (
    echo Docker:       [OK] Attivo
)

curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo Ollama:       [X] Non attivo
) else (
    echo Ollama:       [OK] Attivo (porta 11434)
)

curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    curl -s http://localhost:8080 >nul 2>&1
    if errorlevel 1 (
        echo Open WebUI:   [X] Non attivo
    ) else (
        echo Open WebUI:   [OK] Attivo (Python - porta 8080)
    )
) else (
    echo Open WebUI:   [OK] Attivo (Docker - porta 3000)
)

curl -s http://localhost:8000/v1/models >nul 2>&1
if errorlevel 1 (
    echo TTS (Speech): [X] Non attivo
) else (
    echo TTS (Speech): [OK] Attivo (porta 8000)
)

echo.
goto :end

REM ======================================================================
REM  LOGS
REM ======================================================================
:logs
echo.
echo ======================================================================
echo                         LOG SERVIZI
echo ======================================================================
echo.
docker compose logs -f --tail=50
goto :end

REM ======================================================================
REM  TEST TTS
REM ======================================================================
:test_tts
echo.
echo ======================================================================
echo                         TEST TTS
echo ======================================================================
echo.

curl -s http://localhost:8000/v1/models >nul 2>&1
if errorlevel 1 (
    echo [X] Servizio TTS non attivo. Avvia prima con: openwebui.bat start
    goto :end
)

echo Generazione audio di test...
curl -s http://localhost:8000/v1/audio/speech -H "Content-Type: application/json" -d "{\"input\":\"Ciao! Il sistema text to speech funziona correttamente.\",\"voice\":\"alloy\",\"model\":\"tts-1\"}" -o "%TEMP%\test_tts.mp3"

if exist "%TEMP%\test_tts.mp3" (
    echo [OK] Audio generato: %TEMP%\test_tts.mp3
    echo.
    echo Riproduzione...
    start "" "%TEMP%\test_tts.mp3"
) else (
    echo [X] Errore generazione audio
)
echo.
goto :end

REM ======================================================================
REM  INSTALL
REM ======================================================================
:install
echo.
echo ======================================================================
echo                       INSTALLAZIONE
echo ======================================================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trovato!
    echo   Scarica da: https://www.python.org/downloads/
    goto :end
)
echo [OK] Python trovato

REM Verifica Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] Ollama non trovato
    echo   Scarica da: https://ollama.com/download/windows
    echo.
)

REM Crea venv e installa open-webui
if not exist "%SCRIPT_DIR%venv" (
    echo.
    echo Creazione ambiente Python...
    python -m venv "%SCRIPT_DIR%venv"
)

echo Installazione open-webui...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"
pip install --upgrade pip >nul 2>&1
pip install open-webui

echo.
echo ======================================================================
echo  [OK] Installazione completata
echo    Esegui: openwebui.bat start
echo ======================================================================
goto :end

REM ======================================================================
REM  WSL FIX
REM ======================================================================
:wsl
call "%SCRIPT_DIR%wsl_fix.bat"
goto :menu

:end
echo.
if "%1"=="" pause
