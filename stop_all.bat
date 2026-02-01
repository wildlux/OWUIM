@echo off
setlocal
title Open WebUI + Ollama - Arresto

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ======================================================================
echo        OPEN WEBUI + OLLAMA - Arresto Servizi
echo ======================================================================
echo.

REM Usa docker compose (nuovo) o docker-compose (vecchio)
docker compose version >nul 2>&1
if errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
) else (
    set "COMPOSE_CMD=docker compose"
)

echo [1/3] Arresto container Docker...
%COMPOSE_CMD% down >nul 2>&1
echo       [OK]

echo.
echo [2/3] Arresto Ollama...
taskkill /f /im ollama.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Ollama*" >nul 2>&1
echo       [OK]

echo.
echo [3/3] Verifica...
docker ps -q >nul 2>&1
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo       [OK] Open WebUI fermato
) else (
    echo       [!] Open WebUI ancora attivo
)

curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo       [OK] Ollama fermato
) else (
    echo       [!] Ollama ancora attivo
)

echo.
echo ======================================================================
echo  [OK] Servizi arrestati
echo ======================================================================
echo.
pause
