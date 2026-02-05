@echo off
title Build OpenWebUI-Manager.exe

cd /d "%~dp0"

echo.
echo ======================================================================
echo        BUILD OPEN WEBUI MANAGER (.exe)
echo ======================================================================
echo.

python build.py windows

echo.
echo ======================================================================
if exist "dist\OpenWebUI-Manager.exe" (
    echo  [OK] Build completato!
    echo.
    echo  File creato: dist\OpenWebUI-Manager.exe
    echo.
    echo  Puoi copiare l'exe su qualsiasi PC Windows.
    echo  Requisiti: Docker Desktop e Ollama installati.
) else (
    echo  [X] Build fallito
    echo.
    echo  Verifica che Python sia installato correttamente.
)
echo ======================================================================
echo.
pause
