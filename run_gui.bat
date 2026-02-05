@echo off
setlocal enabledelayedexpansion
title Open WebUI Manager

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ======================================================================
REM  Open WebUI Manager - GUI + Image Analysis
REM ======================================================================

REM Verifica se esiste l'ambiente virtuale
if not exist "venv\Scripts\activate.bat" (
    echo [X] Ambiente virtuale non trovato!
    echo     Esegui prima: scripts\setup_env.bat
    pause
    exit /b 1
)

REM Attiva venv
call venv\Scripts\activate.bat

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
                python image_analysis\image_converter.py "%%f" -f base64
                echo.
            )
        )
        echo.
        echo [OK] Analisi completata!
    ) else (
        echo [*] File: %~1
        echo.
        python image_analysis\image_converter.py "%~1" -f base64
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
python openwebui_gui.py
goto menu

:start_image_service
echo.
echo [*] Avvio Image Analysis Service...
echo [*] Porta: 5555
echo [*] Premi Ctrl+C per fermare
echo.
python image_analysis\image_service.py
pause
goto menu

:start_tts_service
echo.
echo [*] Avvio TTS Locale (Piper - voci italiane offline)...
echo [*] Porta: 5556
echo [*] Premi Ctrl+C per fermare
echo.
python tts_service\tts_local.py
pause
goto menu

:convert_single
echo.
set /p filepath="Percorso immagine (trascina qui): "
if "%filepath%"=="" goto menu
set filepath=%filepath:"=%
echo.
python image_analysis\image_converter.py "%filepath%" -f base64
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
        python image_analysis\image_converter.py "%%f" -f base64
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
start "Image Service" cmd /c "python image_analysis\image_service.py"
timeout /t 2 >nul
echo [OK] Image Service avviato su http://localhost:5555
echo.
echo [*] Avvio TTS Service in background...
start "TTS Service" cmd /c "python tts_service\tts_local.py"
timeout /t 2 >nul
echo [OK] TTS Service avviato su http://localhost:5556
echo.
echo [*] Avvio GUI Manager...
python openwebui_gui.py
goto menu
