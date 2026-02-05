@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Open WebUI.lnk"
set "TARGET=%SCRIPT_DIR%OpenWebUI.vbs"
set "ICON=%SCRIPT_DIR%ICONA\ICONA.ico"

echo.
echo ======================================================================
echo        CREAZIONE COLLEGAMENTO DESKTOP
echo ======================================================================
echo.

REM Converti icona PNG in ICO se necessario
if not exist "%ICON%" (
    if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
        "%SCRIPT_DIR%venv\Scripts\python.exe" -c "from PIL import Image; img = Image.open(r'%SCRIPT_DIR%ICONA\ICONA_Trasparente.png'); img.save(r'%ICON%', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])" 2>nul
    ) else (
        python -c "from PIL import Image; img = Image.open(r'%SCRIPT_DIR%ICONA\ICONA_Trasparente.png'); img.save(r'%ICON%', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])" 2>nul
    )
)

REM Crea collegamento usando PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = '%ICON%'; $Shortcut.Description = 'Open WebUI + Ollama - AI Locale'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo [OK] Collegamento creato sul Desktop!
    echo.
    echo     Icona: "Open WebUI" sul Desktop
    echo     Doppio click per avviare tutto automaticamente
) else (
    echo [X] Errore nella creazione del collegamento
)

echo.
echo ======================================================================
pause
