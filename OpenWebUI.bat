@echo off
setlocal enabledelayedexpansion
title Open WebUI - Avvio

REM ======================================================================
REM  OPEN WEBUI + OLLAMA - Doppio Click per Avviare Tutto
REM ======================================================================

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo  Avvio Open WebUI + Ollama...
echo.

REM ======================================================================
REM  [1] DOCKER DESKTOP
REM ======================================================================
echo  [1/5] Verifica Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo        Avvio Docker Desktop...

    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else if exist "%LOCALAPPDATA%\Docker\Docker Desktop.exe" (
        start "" "%LOCALAPPDATA%\Docker\Docker Desktop.exe"
    ) else (
        start "" "Docker Desktop" 2>nul
    )

    set /a count=0
    :wait_docker
    timeout /t 3 >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        set /a count+=1
        echo        Attesa Docker... [!count!/40]
        if !count! lss 40 goto :wait_docker
        echo        [X] Docker non disponibile
        goto :error
    )
)
echo        [OK] Docker attivo

REM ======================================================================
REM  [2] OLLAMA
REM ======================================================================
echo.
echo  [2/5] Verifica Ollama...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo        Avvio Ollama...

    where ollama >nul 2>&1
    if errorlevel 1 (
        echo        [X] Ollama non trovato
        echo        Scarica da: https://ollama.com/download/windows
        goto :error
    )

    start "Ollama" /min ollama serve

    set /a count=0
    :wait_ollama
    timeout /t 2 >nul
    curl -s http://localhost:11434/api/version >nul 2>&1
    if errorlevel 1 (
        set /a count+=1
        echo        Attesa Ollama... [!count!/15]
        if !count! lss 15 goto :wait_ollama
    )
)
echo        [OK] Ollama attivo

REM ======================================================================
REM  [3] CONTAINER DOCKER
REM ======================================================================
echo.
echo  [3/5] Avvio Open WebUI...

docker compose version >nul 2>&1
if errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)

%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo        Download immagine...
    %COMPOSE_CMD% pull
    %COMPOSE_CMD% up -d
    if errorlevel 1 (
        echo        [X] Errore avvio container
        goto :error
    )
)
echo        [OK] Container avviato

REM ======================================================================
REM  [4] ATTENDI SERVIZIO
REM ======================================================================
echo.
echo  [4/5] Attesa servizio...

set /a count=0
:wait_webui
timeout /t 2 >nul
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    echo        Attesa... [!count!/30]
    if !count! lss 30 goto :wait_webui
)
echo        [OK] Servizio pronto

REM ======================================================================
REM  [5] APRI BROWSER
REM ======================================================================
echo.
echo  [5/5] Apertura browser...
timeout /t 1 >nul
start http://localhost:3000

echo.
echo  ======================================================================
echo   [OK] TUTTO AVVIATO!
echo  ======================================================================
echo.
echo   Open WebUI:  http://localhost:3000
echo   Ollama API:  http://localhost:11434
echo.
echo   Questa finestra si chiudera' tra 5 secondi...
echo  ======================================================================
timeout /t 5 >nul
exit /b 0

:error
echo.
echo  ======================================================================
echo   [X] ERRORE - Verifica i requisiti:
echo       - Docker Desktop installato e funzionante
echo       - Ollama installato
echo  ======================================================================
echo.
pause
exit /b 1
