@echo off
setlocal enabledelayedexpansion
title Build Installer - Open WebUI Manager

cd /d "%~dp0"

echo.
echo ======================================================================
echo        BUILD INSTALLER - Open WebUI Manager
echo ======================================================================
echo.
echo  Questo script verifica tutti i requisiti e crea l'installer.
echo.
echo ======================================================================
echo.

set "ERRORI=0"
set "AVVISI=0"

REM ======================================================================
REM  [1] VERIFICA PYTHON
REM ======================================================================
echo [1/8] Verifica Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo       [X] Python non trovato!
    echo           Scarica da: https://www.python.org/downloads/
    set /a ERRORI+=1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
    echo       [OK] Python !PYVER!
)

REM ======================================================================
REM  [2] VERIFICA/CREA AMBIENTE VIRTUALE
REM ======================================================================
echo.
echo [2/8] Verifica ambiente virtuale...

if exist "venv\Scripts\python.exe" (
    echo       [OK] Ambiente virtuale presente
    set "PYTHON=venv\Scripts\python.exe"
    set "PIP=venv\Scripts\pip.exe"
) else (
    echo       [!] Ambiente virtuale non trovato
    echo           Creazione in corso...
    python -m venv venv
    if errorlevel 1 (
        echo       [X] Errore creazione venv
        set /a ERRORI+=1
    ) else (
        echo       [OK] Ambiente virtuale creato
        set "PYTHON=venv\Scripts\python.exe"
        set "PIP=venv\Scripts\pip.exe"
    )
)

REM ======================================================================
REM  [3] VERIFICA DIPENDENZE PYTHON
REM ======================================================================
echo.
echo [3/8] Verifica dipendenze Python...

REM PyInstaller
"%PYTHON%" -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo       [!] PyInstaller non trovato - installazione...
    "%PIP%" install pyinstaller >nul 2>&1
    "%PYTHON%" -c "import PyInstaller" 2>nul
    if errorlevel 1 (
        echo       [X] Errore installazione PyInstaller
        set /a ERRORI+=1
    ) else (
        echo       [OK] PyInstaller installato
    )
) else (
    echo       [OK] PyInstaller
)

REM Pillow
"%PYTHON%" -c "from PIL import Image" 2>nul
if errorlevel 1 (
    echo       [!] Pillow non trovato - installazione...
    "%PIP%" install Pillow >nul 2>&1
    "%PYTHON%" -c "from PIL import Image" 2>nul
    if errorlevel 1 (
        echo       [X] Errore installazione Pillow
        set /a ERRORI+=1
    ) else (
        echo       [OK] Pillow installato
    )
) else (
    echo       [OK] Pillow
)

REM PyQt5
"%PYTHON%" -c "from PyQt5.QtWidgets import QApplication" 2>nul
if errorlevel 1 (
    echo       [!] PyQt5 non trovato - installazione...
    "%PIP%" install PyQt5 >nul 2>&1
    "%PYTHON%" -c "from PyQt5.QtWidgets import QApplication" 2>nul
    if errorlevel 1 (
        echo       [X] Errore installazione PyQt5
        set /a ERRORI+=1
    ) else (
        echo       [OK] PyQt5 installato
    )
) else (
    echo       [OK] PyQt5
)

REM ======================================================================
REM  [4] VERIFICA INNO SETUP
REM ======================================================================
echo.
echo [4/8] Verifica Inno Setup...

set "ISCC="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo       [X] Inno Setup 6 non trovato!
    echo.
    echo           Scarica e installa da:
    echo           https://jrsoftware.org/isdl.php
    echo.
    set /a ERRORI+=1
) else (
    echo       [OK] Inno Setup trovato
    echo           !ISCC!
)

REM ======================================================================
REM  [5] VERIFICA/CREA ICONA .ICO
REM ======================================================================
echo.
echo [5/8] Verifica icona...

if exist "ICONA\ICONA_Trasparente.png" (
    if not exist "ICONA\ICONA.ico" (
        echo       [!] Icona .ico mancante - conversione...
        "%PYTHON%" -c "from PIL import Image; img = Image.open('ICONA/ICONA_Trasparente.png'); img.save('ICONA/ICONA.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])" 2>nul
        if exist "ICONA\ICONA.ico" (
            echo       [OK] Icona .ico creata
        ) else (
            echo       [X] Errore conversione icona
            set /a AVVISI+=1
        )
    ) else (
        echo       [OK] ICONA\ICONA.ico presente
    )
) else (
    echo       [X] ICONA\ICONA_Trasparente.png non trovato!
    set /a ERRORI+=1
)

REM ======================================================================
REM  [6] VERIFICA FILE NECESSARI
REM ======================================================================
echo.
echo [6/8] Verifica file necessari...

set "FILES_OK=1"

if not exist "openwebui_gui.py" (
    echo       [X] openwebui_gui.py mancante
    set "FILES_OK=0"
    set /a ERRORI+=1
) else (
    echo       [OK] openwebui_gui.py
)

if not exist "docker-compose.yml" (
    echo       [X] docker-compose.yml mancante
    set "FILES_OK=0"
    set /a ERRORI+=1
) else (
    echo       [OK] docker-compose.yml
)

if not exist "installer\OpenWebUI-Setup.iss" (
    echo       [X] installer\OpenWebUI-Setup.iss mancante
    set "FILES_OK=0"
    set /a ERRORI+=1
) else (
    echo       [OK] installer\OpenWebUI-Setup.iss
)

if not exist "OpenWebUI.bat" (
    echo       [!] OpenWebUI.bat mancante
    set /a AVVISI+=1
) else (
    echo       [OK] OpenWebUI.bat
)

if not exist "tools" (
    echo       [!] Cartella tools mancante
    set /a AVVISI+=1
) else (
    echo       [OK] Cartella tools
)

if not exist "scripts" (
    echo       [!] Cartella scripts mancante
    set /a AVVISI+=1
) else (
    echo       [OK] Cartella scripts
)

if not exist "docs\INFO_PRIMA_INSTALLAZIONE.txt" (
    echo       [!] docs\INFO_PRIMA_INSTALLAZIONE.txt mancante
    set /a AVVISI+=1
) else (
    echo       [OK] docs\INFO_PRIMA_INSTALLAZIONE.txt
)

REM ======================================================================
REM  [7] RIEPILOGO VERIFICA
REM ======================================================================
echo.
echo ======================================================================
echo  RIEPILOGO VERIFICA
echo ======================================================================
echo.

if %ERRORI% GTR 0 (
    echo  [X] ERRORI CRITICI: %ERRORI%
    echo      Risolvi gli errori prima di continuare.
    echo.
    echo ======================================================================
    pause
    exit /b 1
)

if %AVVISI% GTR 0 (
    echo  [!] Avvisi: %AVVISI% (non bloccanti)
)

echo  [OK] Tutti i requisiti sono soddisfatti!
echo.
echo ======================================================================
echo.

set /p CONTINUA="Vuoi procedere con il build? [S/n]: "
if /i "%CONTINUA%"=="n" (
    echo.
    echo Build annullato.
    pause
    exit /b 0
)

REM ======================================================================
REM  [8] BUILD
REM ======================================================================
echo.
echo ======================================================================
echo  AVVIO BUILD
echo ======================================================================
echo.

REM 8a. Build EXE con PyInstaller
echo [8a] Build eseguibile (.exe)...
echo.

if exist "dist\OpenWebUI-Manager.exe" (
    echo      Exe esistente trovato. Vuoi ricostruirlo?
    set /p REBUILD="      [S/n]: "
    if /i "!REBUILD!"=="n" (
        echo      [OK] Uso exe esistente
        goto :build_installer
    )
)

echo      Esecuzione PyInstaller...
echo.

"%PYTHON%" build.py windows
if errorlevel 1 (
    echo.
    echo      [X] Errore build exe
    pause
    exit /b 1
)

if not exist "dist\OpenWebUI-Manager.exe" (
    echo      [X] Exe non trovato dopo il build
    pause
    exit /b 1
)

echo.
echo      [OK] Exe creato: dist\OpenWebUI-Manager.exe

:build_installer
echo.
echo [8b] Build installer con Inno Setup...
echo.

"%ISCC%" "installer\OpenWebUI-Setup.iss"
if errorlevel 1 (
    echo.
    echo      [X] Errore build installer
    pause
    exit /b 1
)

REM ======================================================================
REM  COMPLETATO
REM ======================================================================
echo.
echo ======================================================================
echo  [OK] BUILD COMPLETATO CON SUCCESSO!
echo ======================================================================
echo.

REM Trova il file creato
for %%f in (dist\OpenWebUI-Manager-Setup-*.exe) do (
    echo  Installer: %%f
    for %%A in ("%%f") do (
        set /a SIZE=%%~zA / 1024 / 1024
        echo  Dimensione: ~!SIZE! MB
    )
)

echo.
echo  Puoi distribuire l'installer su qualsiasi PC Windows.
echo.
echo  Requisiti per l'utente finale:
echo    - Windows 10/11 (64-bit)
echo    - Docker Desktop
echo    - Ollama
echo.
echo ======================================================================
echo.
pause
