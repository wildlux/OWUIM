@echo off
setlocal enabledelayedexpansion
title Open WebUI + Ollama - Avvio Completo

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ======================================================================
echo        OPEN WEBUI + OLLAMA - Avvio Completo
echo ======================================================================
echo.

REM ======================================================================
REM  [1] VERIFICA DOCKER DESKTOP
REM ======================================================================
echo [1/5] Verifica Docker Desktop...

REM Controlla se Docker risponde
docker info >nul 2>&1
if errorlevel 1 (
    echo       [!] Docker Desktop non risponde
    echo       Tento di avviarlo...

    REM Prova ad avviare Docker Desktop
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
    if errorlevel 1 (
        start "" "%LOCALAPPDATA%\Docker\Docker Desktop.exe" 2>nul
    )

    echo       Attendo avvio Docker Desktop...
    set /a wait_count=0
    :wait_docker
    timeout /t 3 >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        set /a wait_count+=1
        if !wait_count! lss 20 (
            echo       Attesa... [!wait_count!/20]
            goto :wait_docker
        ) else (
            echo.
            echo       [X] Docker Desktop non si avvia!
            echo.
            echo       Soluzioni:
            echo         1. Avvia manualmente Docker Desktop
            echo         2. Verifica che sia installato correttamente
            echo         3. Esegui: windows\wsl_fix.bat
            echo.
            pause
            exit /b 1
        )
    )
)
echo       [OK] Docker Desktop attivo

REM ======================================================================
REM  [2] VERIFICA/AVVIA OLLAMA
REM ======================================================================
echo.
echo [2/5] Verifica Ollama...

REM Controlla se Ollama risponde sulla porta 11434
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo       [!] Ollama non risponde

    REM Verifica se ollama esiste
    where ollama >nul 2>&1
    if errorlevel 1 (
        echo       [X] Ollama non trovato!
        echo       Scarica da: https://ollama.com/download/windows
        pause
        exit /b 1
    )

    echo       Avvio Ollama...
    start "Ollama" /min ollama serve

    REM Attendi che Ollama sia pronto
    set /a wait_count=0
    :wait_ollama
    timeout /t 2 >nul
    curl -s http://localhost:11434/api/version >nul 2>&1
    if errorlevel 1 (
        set /a wait_count+=1
        if !wait_count! lss 15 (
            echo       Attesa Ollama... [!wait_count!/15]
            goto :wait_ollama
        ) else (
            echo       [X] Ollama non si avvia!
            pause
            exit /b 1
        )
    )
)
echo       [OK] Ollama attivo (porta 11434)

REM ======================================================================
REM  [3] AVVIA CONTAINER DOCKER
REM ======================================================================
echo.
echo [3/5] Avvio container Open WebUI...

REM Usa docker compose (nuovo) o docker-compose (vecchio)
docker compose version >nul 2>&1
if errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)

%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo       [!] Errore avvio container
    echo       Provo a scaricare l'immagine...
    %COMPOSE_CMD% pull
    %COMPOSE_CMD% up -d
    if errorlevel 1 (
        echo       [X] Impossibile avviare i container
        pause
        exit /b 1
    )
)
echo       [OK] Container avviato

REM ======================================================================
REM  [4] ATTESA SERVIZIO PRONTO
REM ======================================================================
echo.
echo [4/5] Attesa che Open WebUI sia pronto...

set /a wait_count=0
:wait_webui
timeout /t 2 >nul
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    set /a wait_count+=1
    if !wait_count! lss 30 (
        echo       Attesa... [!wait_count!/30]
        goto :wait_webui
    ) else (
        echo       [!] Timeout - il servizio potrebbe non essere pronto
    )
) else (
    echo       [OK] Open WebUI pronto
)

REM ======================================================================
REM  [5] APRI BROWSER
REM ======================================================================
echo.
echo [5/5] Apertura browser...
timeout /t 2 >nul
start http://localhost:3000

echo.
echo ======================================================================
echo  [OK] TUTTO AVVIATO!
echo ======================================================================
echo.
echo  Open WebUI:  http://localhost:3000
echo  Ollama API:  http://localhost:11434
echo.
echo  Per fermare: stop_all.bat
echo  Per la GUI:  run_gui.bat
echo.
echo ======================================================================
echo.
echo Premi un tasto per chiudere questa finestra...
echo (I servizi continueranno a funzionare in background)
pause >nul
