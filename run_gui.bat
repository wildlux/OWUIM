@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Open WebUI Manager

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"

REM ======================================================================
REM  Open WebUI Manager - GUI + Image Analysis
REM ======================================================================

REM --- Trova Python ---
set "PYTHON_CMD="

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :python_found
)

where python3 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python3"
    goto :python_found
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :python_found
)

echo  [ERRORE] Python non trovato!
echo.
echo  Installa Python 3.8+ da: https://www.python.org/downloads/
echo  IMPORTANTE: seleziona "Add Python to PATH"
echo.
pause
exit /b 1

:python_found

REM --- Verifica/crea ambiente virtuale ---
if not exist "%SCRIPT_DIR%\venv\Scripts\python.exe" (
    echo.
    echo  [*] Creazione ambiente virtuale...
    echo      Questa operazione viene eseguita solo la prima volta.
    echo.
    %PYTHON_CMD% -m venv "%SCRIPT_DIR%\venv"
    if %ERRORLEVEL% neq 0 (
        echo  [ERRORE] Impossibile creare l'ambiente virtuale.
        echo  Prova: %PYTHON_CMD% -m pip install virtualenv
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Ambiente virtuale creato
    echo.

    "%SCRIPT_DIR%\venv\Scripts\pip.exe" install --upgrade pip >nul 2>&1

    echo  [*] Installazione dipendenze...
    if exist "%SCRIPT_DIR%\packages" (
        echo      Installazione da pacchetti locali...
        "%SCRIPT_DIR%\venv\Scripts\pip.exe" install --no-index --find-links="%SCRIPT_DIR%\packages" -r "%SCRIPT_DIR%\requirements.txt" >nul 2>&1
        if %ERRORLEVEL% neq 0 (
            echo      Alcuni pacchetti mancanti, scaricamento da internet...
            "%SCRIPT_DIR%\venv\Scripts\pip.exe" install --find-links="%SCRIPT_DIR%\packages" -r "%SCRIPT_DIR%\requirements.txt"
        ) else (
            echo  [OK] Dipendenze installate (offline)
        )
    ) else (
        echo      Scaricamento da internet...
        "%SCRIPT_DIR%\venv\Scripts\pip.exe" install -r "%SCRIPT_DIR%\requirements.txt"
    )
    echo.
) else (
    echo  [OK] Ambiente virtuale presente
)

REM Attiva venv
call "%SCRIPT_DIR%\venv\Scripts\activate.bat"

REM Usa il Python del venv per tutti i comandi
set "VENV_PYTHON=%SCRIPT_DIR%\venv\Scripts\python.exe"

REM Se passato un file/cartella come argomento, analizzalo
if not "%~1"=="" (
    echo.
    echo ======================================================================
    echo  Analisi Immagini
    echo ======================================================================
    echo.

    REM Verifica se e' un file o una cartella
    if exist "%~1\*" (
        echo [*] Cartella rilevata: %~1
        echo [*] Analisi di tutti i file immagine...
        echo.

        for %%f in ("%~1\*.png" "%~1\*.jpg" "%~1\*.jpeg" "%~1\*.svg" "%~1\*.webp") do (
            if exist "%%f" (
                echo Elaborazione: %%~nxf
                "%VENV_PYTHON%" image_analysis\image_converter.py "%%f" -f base64
                echo.
            )
        )
        echo.
        echo [OK] Analisi completata!
    ) else (
        echo [*] File: %~1
        echo.
        "%VENV_PYTHON%" image_analysis\image_converter.py "%~1" -f base64
    )
    echo.
    pause
    exit /b
)

REM Menu principale
:menu
cls
echo.
echo  ======================================================================
echo              OPEN WEBUI MANAGER
echo  ======================================================================
echo.
echo   [1] Avvia GUI Manager (gestione completa)
echo   [2] Avvia Image Analysis Service (porta 5555)
echo   [3] Avvia TTS Service (porta 5556)
echo   [4] Converti immagine singola
echo   [5] Converti cartella immagini
echo   [6] Avvia tutto (GUI + Image + TTS)
echo   [0] Esci
echo.
echo  ======================================================================
echo.
echo  TIP: Trascina un file/cartella su questo script per analizzarlo!
echo.
set /p choice="Seleziona opzione: "

if "%choice%"=="1" goto start_gui
if "%choice%"=="2" goto start_image_service
if "%choice%"=="3" goto start_tts_service
if "%choice%"=="4" goto convert_single
if "%choice%"=="5" goto convert_folder
if "%choice%"=="6" goto start_all
if "%choice%"=="0" exit /b

echo Opzione non valida
timeout /t 2 >nul
goto menu

:start_gui
echo.
echo [*] Avvio GUI Manager...
"%VENV_PYTHON%" openwebui_gui.py
goto menu

:start_image_service
echo.
echo [*] Avvio Image Analysis Service...
echo [*] Porta: 5555
echo [*] Premi Ctrl+C per fermare
echo.
"%VENV_PYTHON%" image_analysis\image_service.py
pause
goto menu

:start_tts_service
echo.
echo [*] Avvio TTS Locale (Piper - voci italiane offline)...
echo [*] Porta: 5556
echo [*] Premi Ctrl+C per fermare
echo.
"%VENV_PYTHON%" tts_service\tts_local.py
pause
goto menu

:convert_single
echo.
set /p filepath="Percorso immagine (trascina qui): "
if "%filepath%"=="" goto menu
set filepath=%filepath:"=%
echo.
"%VENV_PYTHON%" image_analysis\image_converter.py "%filepath%" -f base64
echo.
pause
goto menu

:convert_folder
echo.
set /p folder="Percorso cartella (trascina qui): "
if "%folder%"=="" goto menu
set folder=%folder:"=%
echo.
echo [*] Analisi immagini in: %folder%
echo.
for %%f in ("%folder%\*.png" "%folder%\*.jpg" "%folder%\*.jpeg" "%folder%\*.svg") do (
    if exist "%%f" (
        echo Elaborazione: %%~nxf
        "%VENV_PYTHON%" image_analysis\image_converter.py "%%f" -f base64
        echo.
    )
)
echo.
echo [OK] Completato!
pause
goto menu

:start_all
echo.
echo [*] Avvio Image Analysis Service in background...
start "Image Service" cmd /c ""%VENV_PYTHON%" image_analysis\image_service.py"
timeout /t 2 >nul
echo [OK] Image Service avviato su http://localhost:5555
echo.
echo [*] Avvio TTS Service in background...
start "TTS Service" cmd /c ""%VENV_PYTHON%" tts_service\tts_local.py"
timeout /t 2 >nul
echo [OK] TTS Service avviato su http://localhost:5556
echo.
echo [*] Avvio GUI Manager...
"%VENV_PYTHON%" openwebui_gui.py
goto menu
