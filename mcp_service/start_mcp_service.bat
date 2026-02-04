@echo off
title MCP Bridge Service
cd /d "%~dp0\.."

echo ============================================================
echo   MCP Bridge Service - Avvio
echo ============================================================
echo.

REM Attiva venv se esiste
if exist "venv\Scripts\activate.bat" (
    echo [*] Attivazione ambiente virtuale...
    call venv\Scripts\activate.bat
)

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python non trovato. Installa Python 3.8+
    pause
    exit /b 1
)

REM Verifica dipendenze base
echo [*] Verifica dipendenze...
python -c "import fastapi, uvicorn, requests" 2>nul
if errorlevel 1 (
    echo [*] Installazione dipendenze base...
    pip install fastapi uvicorn requests sse-starlette
)

REM Verifica MCP SDK
python -c "import mcp" 2>nul
if errorlevel 1 (
    echo.
    echo [!] MCP SDK non installato.
    echo [*] Vuoi installarlo? Il servizio funzionera' anche senza,
    echo     ma non sara' possibile usare il protocollo MCP nativo.
    echo.
    set /p install_mcp="Installare MCP SDK? (s/n): "
    if /i "%install_mcp%"=="s" (
        echo [*] Installazione MCP SDK...
        pip install mcp
    )
)

echo.
echo [*] Avvio MCP Bridge Service sulla porta 5558...
echo.

python mcp_service\mcp_service.py

pause
