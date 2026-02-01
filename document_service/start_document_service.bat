@echo off
REM ============================================================================
REM Document Reader Service - Script di avvio per Windows
REM ============================================================================
REM Questo script avvia il servizio di lettura documenti.
REM Installa automaticamente le dipendenze mancanti.
REM
REM Uso: Doppio click su start_document_service.bat
REM ============================================================================

chcp 65001 >nul
title Document Reader Service

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         DOCUMENT READER SERVICE - Avvio                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vai nella cartella dello script
cd /d "%~dp0"

REM ----------------------------------------------------------------------------
REM Verifica Python
REM ----------------------------------------------------------------------------
echo [*] Verifica Python...

where python >nul 2>&1
if errorlevel 1 (
    echo [X] Python non trovato!
    echo     Scarica da: https://www.python.org/downloads/
    echo     Assicurati di selezionare "Add Python to PATH" durante l'installazione
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION%

REM ----------------------------------------------------------------------------
REM Installa dipendenze mancanti
REM ----------------------------------------------------------------------------
echo.
echo [*] Verifica dipendenze...

REM Funzione per installare se mancante
call :install_if_missing fastapi fastapi
call :install_if_missing uvicorn uvicorn
call :install_if_missing multipart python-multipart
call :install_if_missing pypdf pypdf
call :install_if_missing docx python-docx
call :install_if_missing openpyxl openpyxl
call :install_if_missing pptx python-pptx
call :install_if_missing PIL Pillow
call :install_if_missing markdown markdown
call :install_if_missing bs4 beautifulsoup4
call :install_if_missing yaml PyYAML
call :install_if_missing ebooklib ebooklib
call :install_if_missing lxml lxml

echo [OK] Dipendenze verificate

REM ----------------------------------------------------------------------------
REM Verifica programmi esterni (opzionali)
REM ----------------------------------------------------------------------------
echo.
echo [*] Programmi esterni (opzionali):

where soffice >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] LibreOffice
) else (
    echo   [  ] LibreOffice ^(installa con: winget install TheDocumentFoundation.LibreOffice^)
)

where magick >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] ImageMagick
) else (
    echo   [  ] ImageMagick ^(installa con: winget install ImageMagick.ImageMagick^)
)

where gimp >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] GIMP
) else (
    echo   [  ] GIMP ^(installa con: winget install GIMP.GIMP^)
)

where ebook-convert >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Calibre
) else (
    echo   [  ] Calibre ^(scarica da: https://calibre-ebook.com/^)
)

REM ----------------------------------------------------------------------------
REM Avvia il servizio
REM ----------------------------------------------------------------------------
echo.
echo [*] Avvio servizio su http://localhost:5557
echo [*] Documentazione: http://localhost:5557/docs
echo [*] Premi Ctrl+C per fermare
echo.

python document_service.py

pause
exit /b 0

REM ----------------------------------------------------------------------------
REM Funzione: Installa pacchetto se non presente
REM ----------------------------------------------------------------------------
:install_if_missing
python -c "import %~1" 2>nul
if errorlevel 1 (
    echo [!] Installazione %~2...
    pip install --quiet %~2
)
exit /b 0
