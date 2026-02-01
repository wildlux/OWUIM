@echo off
title Risoluzione Problemi WSL2/Docker

echo.
echo ======================================================================
echo           RISOLUZIONE PROBLEMI WSL2 / DOCKER - Windows
echo ======================================================================
echo.
echo   [1] Verifica virtualizzazione (BIOS)
echo   [2] Installa/Ripara WSL2
echo   [3] Reset WSL2 + Docker
echo   [4] Pulisci registro WSL
echo   [5] Ripara VHDX corrotto
echo   [6] Test Docker
echo   [0] Esci
echo.
echo ======================================================================
echo.

set /p choice="Scegli opzione: "

if "%choice%"=="1" goto :verifica_virt
if "%choice%"=="2" goto :installa_wsl
if "%choice%"=="3" goto :reset_wsl
if "%choice%"=="4" goto :pulisci_registro
if "%choice%"=="5" goto :ripara_vhdx
if "%choice%"=="6" goto :test_docker
if "%choice%"=="0" exit /b 0
goto :eof

:verifica_virt
echo.
echo ======================================================================
echo   VERIFICA VIRTUALIZZAZIONE
echo ======================================================================
echo.
systeminfo | findstr /i "Hyper-V"
echo.
echo Se "Hyper-V Requirements" mostra "No", abilita virtualizzazione nel BIOS:
echo   - Intel: VT-x / Intel Virtualization Technology
echo   - AMD: AMD-V / SVM Mode
echo.
pause
goto :eof

:installa_wsl
echo.
echo ======================================================================
echo   INSTALLAZIONE WSL2
echo ======================================================================
echo.
echo Esecuzione: wsl --install
wsl --install
echo.
echo Esecuzione: wsl --set-default-version 2
wsl --set-default-version 2
echo.
echo [OK] Riavvia il PC per completare l'installazione
pause
goto :eof

:reset_wsl
echo.
echo ======================================================================
echo   RESET WSL2 + DOCKER
echo ======================================================================
echo.
echo [!] Questo rimuovera' tutte le distribuzioni WSL!
set /p confirm="Continuare? [s/N]: "
if /i not "%confirm%"=="s" goto :eof

echo.
echo [1/4] Arresto WSL...
wsl --shutdown

echo [2/4] Rimozione distribuzioni Docker...
wsl --unregister docker-desktop 2>nul
wsl --unregister docker-desktop-data 2>nul

echo [3/4] Pulizia cartelle Docker...
rmdir /s /q "%LOCALAPPDATA%\Docker" 2>nul
rmdir /s /q "%APPDATA%\Docker" 2>nul

echo [4/4] Reset completato
echo.
echo Prossimi passi:
echo   1. Disinstalla Docker Desktop dal Pannello di Controllo
echo   2. Riavvia il PC
echo   3. Reinstalla Docker Desktop
pause
goto :eof

:pulisci_registro
echo.
echo ======================================================================
echo   PULIZIA REGISTRO WSL
echo ======================================================================
echo.
echo [!] Richiede privilegi amministratore
echo.
echo Rimozione chiavi registro WSL...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss" /f 2>nul
echo.
echo [OK] Registro pulito. Riavvia e reinstalla WSL con: wsl --install
pause
goto :eof

:ripara_vhdx
echo.
echo ======================================================================
echo   RIPARA VHDX CORROTTO
echo ======================================================================
echo.
echo Arresto WSL...
wsl --shutdown
timeout /t 3 >nul

echo.
echo Ricerca file VHDX...
echo.
dir /s /b "%LOCALAPPDATA%\Docker\wsl\*.vhdx" 2>nul
dir /s /b "%LOCALAPPDATA%\Packages\*docker*\LocalState\*.vhdx" 2>nul

echo.
echo Se i file sono corrotti, eliminarli e reinstallare Docker Desktop.
echo Percorso tipico: %LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx
echo.
pause
goto :eof

:test_docker
echo.
echo ======================================================================
echo   TEST DOCKER
echo ======================================================================
echo.
echo [1/3] Verifica Docker CLI...
docker --version
if errorlevel 1 (
    echo [X] Docker CLI non trovato
    goto :test_end
)
echo [OK] Docker CLI OK

echo.
echo [2/3] Verifica Docker Daemon...
docker info >nul 2>&1
if errorlevel 1 (
    echo [X] Docker Daemon non risponde
    echo   Avvia Docker Desktop e riprova
    goto :test_end
)
echo [OK] Docker Daemon OK

echo.
echo [3/3] Test container...
docker run --rm hello-world
if errorlevel 1 (
    echo [X] Test container fallito
    goto :test_end
)
echo [OK] Container OK

:test_end
echo.
pause
goto :eof
