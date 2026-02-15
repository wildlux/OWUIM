@echo off
title MCP Bridge Service
cd /d "%~dp0\.."

echo ============================================================
echo   MCP Bridge Service - Avvio
echo ============================================================
echo.

REM Cerca venv del progetto padre
set "PROJECT_ROOT=%~dp0\.."
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON=%PROJECT_ROOT%\venv\Scripts\python.exe"
    echo [OK] Ambiente virtuale trovato
) else if exist "venv\Scripts\activate.bat" (
    echo [*] Attivazione ambiente virtuale...
    call venv\Scripts\activate.bat
    set "PYTHON=python"
) else (
    set "PYTHON=python"
)

REM Verifica Python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python non trovato. Installa Python 3.8+
    pause
    exit /b 1
)

REM Verifica dipendenze base
echo [*] Verifica dipendenze...
%PYTHON% -c "import fastapi, uvicorn, requests" 2>nul
if errorlevel 1 (
    echo [*] Installazione dipendenze base...
    %PYTHON% -m pip install fastapi uvicorn requests sse-starlette
)

REM Verifica MCP SDK
%PYTHON% -c "import mcp" 2>nul
if errorlevel 1 (
    echo.
    echo [!] MCP SDK non installato.
    echo [*] Vuoi installarlo? Il servizio funzionera' anche senza,
    echo     ma non sara' possibile usare il protocollo MCP nativo.
    echo.
    set /p install_mcp="Installare MCP SDK? (s/n): "
    if /i "%install_mcp%"=="s" (
        echo [*] Installazione MCP SDK...
        %PYTHON% -m pip install mcp
    )
)

echo.
echo [*] Avvio MCP Bridge Service sulla porta 5558...
echo.

%PYTHON% mcp_service\mcp_service.py

pause
