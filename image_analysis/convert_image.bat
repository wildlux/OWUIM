@echo off
setlocal enabledelayedexpansion
title Image Converter per Open WebUI

REM ======================================================================
REM  Image Converter - Converte PNG/SVG per compatibilita' Open WebUI
REM ======================================================================

set "SCRIPT_DIR=%~dp0"
set "PARENT_DIR=%SCRIPT_DIR%\.."

cd /d "%PARENT_DIR%"

REM Attiva venv se esiste
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Se passato un file come argomento, convertilo
if not "%~1"=="" (
    echo.
    echo Conversione: %~1
    python image_analysis\image_converter.py "%~1" -f base64
    echo.
    pause
    exit /b
)

REM Menu interattivo
:menu
cls
echo.
echo  ======================================================================
echo              IMAGE CONVERTER per Open WebUI
echo  ======================================================================
echo.
echo   Converte PNG/SVG in formato compatibile (evita bug base64 loop)
echo.
echo   [1] Converti immagine in Base64 (per incollare in chat)
echo   [2] Converti SVG in PNG
echo   [3] Comprimi immagine in JPEG
echo   [4] Converti tutti i PNG in una cartella
echo   [5] Installa dipendenze (Pillow, cairosvg)
echo   [0] Esci
echo.
echo  ======================================================================
echo.
set /p choice="Seleziona opzione: "

if "%choice%"=="1" goto convert_base64
if "%choice%"=="2" goto convert_svg
if "%choice%"=="3" goto compress_jpeg
if "%choice%"=="4" goto batch_convert
if "%choice%"=="5" goto install_deps
if "%choice%"=="0" exit /b

echo Opzione non valida
timeout /t 2 >nul
goto menu

:convert_base64
echo.
set /p filepath="Percorso immagine (trascina qui): "
if "%filepath%"=="" goto menu
set filepath=%filepath:"=%
python image_analysis\image_converter.py "%filepath%" -f base64
echo.
pause
goto menu

:convert_svg
echo.
set /p filepath="Percorso SVG (trascina qui): "
if "%filepath%"=="" goto menu
set filepath=%filepath:"=%
python image_analysis\image_converter.py "%filepath%" -f png
echo.
pause
goto menu

:compress_jpeg
echo.
set /p filepath="Percorso immagine (trascina qui): "
if "%filepath%"=="" goto menu
set filepath=%filepath:"=%
set /p quality="Qualita' JPEG (1-100, default 70): "
if "%quality%"=="" set quality=70
python image_analysis\image_converter.py "%filepath%" -f jpeg -q %quality%
echo.
pause
goto menu

:batch_convert
echo.
set /p folder="Percorso cartella: "
if "%folder%"=="" goto menu
set folder=%folder:"=%
echo.
echo Conversione di tutti i PNG in: %folder%
for %%f in ("%folder%\*.png") do (
    echo Elaborazione: %%~nxf
    python image_analysis\image_converter.py "%%f" -f jpeg
)
echo.
echo Completato!
pause
goto menu

:install_deps
echo.
echo Installazione dipendenze...
pip install Pillow cairosvg
echo.
echo Completato!
pause
goto menu
