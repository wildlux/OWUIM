#!/usr/bin/env python3
"""
Build & Export - Open WebUI Manager
Crea eseguibili per Windows (.exe) e Linux (AppImage/binario)

Autore: Carlo
Versione: 1.1.0

Uso:
    python build.py              # Menu interattivo
    python build.py windows      # Solo Windows .exe
    python build.py linux        # Solo Linux
    python build.py all          # Tutti
    python build.py zip          # Crea archivio progetto
    python build.py bat          # Pacchetto .bat portatile
"""

import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path
from datetime import datetime

# Colori (compatibili Windows)
os.system('')
G = '\033[92m'
Y = '\033[93m'
R = '\033[91m'
B = '\033[94m'
N = '\033[0m'
BOLD = '\033[1m'

# Directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent  # Root del progetto (padre di dist/)
DIST_DIR = SCRIPT_DIR
ICON_PNG = PROJECT_ROOT / "ICONA" / "ICONA_Trasparente.png"
ICON_ICO = PROJECT_ROOT / "ICONA" / "ICONA.ico"
GUI_SCRIPT = PROJECT_ROOT / "openwebui_gui.py"
VENV_DIR = PROJECT_ROOT / "venv"
VERSION = "1.1.0"
APP_NAME = "OpenWebUI-Manager"

IS_WINDOWS = platform.system() == "Windows"


def print_header():
    print(f"""
{B}{BOLD}
+===================================================================+
|              BUILD & EXPORT - Open WebUI Manager                  |
+===================================================================+
{N}""")


def run(cmd, check=True, shell=True, cwd=None):
    """Esegue comando."""
    print(f"  {Y}>{N} {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        print(f"  {R}Errore: {result.stderr or result.stdout}{N}")
        return False
    return True


def check_docker():
    """Verifica se Docker e' disponibile e funzionante."""
    print(f"\n{BOLD}[0] Verifica Docker...{N}")

    result = subprocess.run("docker info", shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"  {R}[X] Docker Desktop non e' in esecuzione!{N}")
        print(f"")
        print(f"  Soluzioni:")
        print(f"    1. Avvia Docker Desktop")
        print(f"    2. Attendi che sia completamente avviato")
        print(f"    3. Riprova")
        print(f"")
        return False

    print(f"  {G}[OK]{N} Docker attivo")
    return True


def check_venv():
    """Verifica e attiva l'ambiente virtuale."""
    print(f"\n{BOLD}[0.5] Verifica ambiente virtuale...{N}")

    if IS_WINDOWS:
        venv_python = VENV_DIR / "Scripts" / "python.exe"
        venv_pip = VENV_DIR / "Scripts" / "pip.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
        venv_pip = VENV_DIR / "bin" / "pip"

    # Se siamo gia' nel venv, assicura che bin/Scripts sia nel PATH
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_bin = Path(sys.prefix) / ("Scripts" if IS_WINDOWS else "bin")
        if str(venv_bin) not in os.environ.get("PATH", ""):
            os.environ["PATH"] = str(venv_bin) + os.pathsep + os.environ.get("PATH", "")
        print(f"  {G}[OK]{N} Ambiente virtuale gia' attivo")
        return True

    # Verifica se esiste il venv
    if not venv_python.exists():
        print(f"  {Y}[!]{N} Ambiente virtuale non trovato")
        print(f"")
        print(f"  Creazione ambiente virtuale...")

        # Crea venv
        result = subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], capture_output=True)
        if result.returncode != 0:
            print(f"  {R}[X] Errore creazione venv{N}")
            return False

        print(f"  {G}[OK]{N} Ambiente virtuale creato")

        # Installa dipendenze
        print(f"  Installazione dipendenze...")
        req_file = PROJECT_ROOT / "requirements.txt"
        if req_file.exists():
            subprocess.run([str(venv_pip), "install", "-r", str(req_file)], capture_output=True)

        # Installa pyinstaller
        subprocess.run([str(venv_pip), "install", "pyinstaller"], capture_output=True)
        print(f"  {G}[OK]{N} Dipendenze installate")

    # Riavvia con il Python del venv
    print(f"")
    print(f"  {Y}Riavvio con ambiente virtuale...{N}")
    print(f"")

    # Passa gli stessi argomenti
    args = [str(venv_python), str(Path(__file__).resolve())] + sys.argv[1:]

    if IS_WINDOWS:
        # os.execv non funziona correttamente su Windows:
        # usa subprocess e poi esci dal processo corrente
        result = subprocess.run(args)
        sys.exit(result.returncode)
    else:
        os.execv(str(venv_python), args)


def check_dependencies():
    """Verifica dipendenze build."""
    print(f"\n{BOLD}[1] Verifica dipendenze...{N}")

    missing = []

    # PyInstaller
    try:
        import PyInstaller
        print(f"  {G}[OK]{N} PyInstaller")
    except ImportError:
        print(f"  {Y}[!]{N} PyInstaller non trovato")
        missing.append("pyinstaller")

    # Pillow (per conversione icone)
    try:
        from PIL import Image
        print(f"  {G}[OK]{N} Pillow")
    except ImportError:
        print(f"  {Y}[!]{N} Pillow non trovato")
        missing.append("Pillow")

    # PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
        print(f"  {G}[OK]{N} PyQt5")
    except ImportError:
        print(f"  {Y}[!]{N} PyQt5 non trovato")
        missing.append("PyQt5")

    if missing:
        print(f"\n  Installazione dipendenze mancanti...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing, capture_output=True)
        print(f"  {G}[OK]{N} Dipendenze installate")

    return True


def convert_icon():
    """Converte PNG -> ICO per Windows."""
    if ICON_ICO.exists():
        return True

    if not ICON_PNG.exists():
        print(f"  {Y}[!]{N} Icona PNG non trovata")
        return False

    try:
        from PIL import Image
        print(f"  Conversione icona PNG -> ICO...")
        img = Image.open(ICON_PNG)
        img.save(str(ICON_ICO), format='ICO',
                sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])
        print(f"  {G}[OK]{N} Icona convertita")
        return True
    except Exception as e:
        print(f"  {R}Errore conversione icona: {e}{N}")
        return False


def build_windows():
    """Build per Windows (.exe)."""
    print(f"\n{BOLD}[2] Build Windows (.exe)...{N}")

    if platform.system() != "Windows":
        print(f"  {Y}[!]{N} Build Windows richiede Windows")
        print(f"  Usa Wine o una VM Windows")
        return False

    convert_icon()

    DIST_DIR.mkdir(exist_ok=True)

    # Usa percorsi con virgolette per gestire spazi
    gui_script_str = str(GUI_SCRIPT).replace("\\", "\\\\")
    script_dir_str = str(PROJECT_ROOT).replace("\\", "\\\\")
    icon_dir_str = str(PROJECT_ROOT / "ICONA").replace("\\", "\\\\")
    tools_dir_str = str(PROJECT_ROOT / "Tools OWUI").replace("\\", "\\\\")
    scripts_dir_str = str(PROJECT_ROOT / "scripts").replace("\\", "\\\\")
    fonts_dir_str = str(PROJECT_ROOT / "fonts").replace("\\", "\\\\")
    compose_str = str(PROJECT_ROOT / "docker-compose.yml").replace("\\", "\\\\")
    config_str = str(PROJECT_ROOT / "config.py").replace("\\", "\\\\")
    security_str = str(PROJECT_ROOT / "security.py").replace("\\", "\\\\")
    ui_dir_str = str(PROJECT_ROOT / "ui").replace("\\", "\\\\")
    translations_str = str(PROJECT_ROOT / "translations.py").replace("\\", "\\\\")
    icon_ico_str = str(ICON_ICO).replace("\\", "\\\\")

    # Crea spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    [r'{gui_script_str}'],
    pathex=[r'{script_dir_str}'],
    binaries=[],
    datas=[
        (r'{icon_dir_str}', 'ICONA'),
        (r'{tools_dir_str}', 'Tools OWUI'),
        (r'{scripts_dir_str}', 'scripts'),
        (r'{fonts_dir_str}', 'fonts'),
        (r'{ui_dir_str}', 'ui'),
        (r'{compose_str}', '.'),
        (r'{config_str}', '.'),
        (r'{security_str}', '.'),
        (r'{translations_str}', '.'),
    ],
    hiddenimports=['PyQt5.sip', 'config', 'translations', 'system_profiler',
                   'ui', 'ui.components', 'ui.dialogs', 'ui.main_window', 'ui.threads',
                   'ui.widgets', 'ui.widgets.dashboard', 'ui.widgets.config_widget',
                   'ui.widgets.models', 'ui.widgets.tts', 'ui.widgets.mcp',
                   'ui.widgets.logs', 'ui.widgets.info', 'ui.widgets.archivio'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=r'{icon_ico_str}',
)
'''

    spec_file = SCRIPT_DIR / f"{APP_NAME}.spec"
    spec_file.write_text(spec_content)

    # Trova pyinstaller
    if IS_WINDOWS:
        pyinstaller_path = VENV_DIR / "Scripts" / "pyinstaller.exe"
        if not pyinstaller_path.exists():
            pyinstaller_path = "pyinstaller"
        else:
            pyinstaller_path = str(pyinstaller_path)
    else:
        pyinstaller_path = "pyinstaller"

    # Directory di output dentro dist/
    build_dir = SCRIPT_DIR / "build"
    output_dir = SCRIPT_DIR / "output"

    # Build
    cmd = f'"{pyinstaller_path}" --clean --noconfirm --distpath "{output_dir}" --workpath "{build_dir}" "{spec_file}"'
    if run(cmd, cwd=str(SCRIPT_DIR)):
        exe_path = output_dir / f"{APP_NAME}.exe"
        if exe_path.exists():
            final_path = DIST_DIR / f"{APP_NAME}.exe"
            if final_path.exists():
                final_path.unlink()
            shutil.move(str(exe_path), str(final_path))
            print(f"  {G}[OK]{N} Creato: {final_path}")
            return True

    return False


def build_linux():
    """Build per Linux (binario + AppImage)."""
    print(f"\n{BOLD}[2] Build Linux...{N}")

    if platform.system() != "Linux":
        print(f"  {Y}[!]{N} Build Linux richiede Linux")
        return False

    DIST_DIR.mkdir(exist_ok=True)

    # Trova pyinstaller (preferisci venv, poi PATH)
    pyinstaller_path = VENV_DIR / "bin" / "pyinstaller"
    if not pyinstaller_path.exists():
        pyinstaller_path = shutil.which("pyinstaller") or "pyinstaller"
    else:
        pyinstaller_path = str(pyinstaller_path)

    # Build con PyInstaller
    icon_opt = f'--icon="{ICON_PNG}"' if ICON_PNG.exists() else ""

    # Directory di output dentro dist/
    build_dir = SCRIPT_DIR / "build"
    output_dir = SCRIPT_DIR / "output"

    cmd = f'''"{pyinstaller_path}" --onefile --windowed --name={APP_NAME} \
        {icon_opt} \
        --distpath "{output_dir}" \
        --workpath "{build_dir}" \
        --specpath "{SCRIPT_DIR}" \
        --add-data="{PROJECT_ROOT / 'ICONA'}:ICONA" \
        --add-data="{PROJECT_ROOT / 'Tools OWUI'}:Tools OWUI" \
        --add-data="{PROJECT_ROOT / 'scripts'}:scripts" \
        --add-data="{PROJECT_ROOT / 'fonts'}:fonts" \
        --add-data="{PROJECT_ROOT / 'ui'}:ui" \
        --add-data="{PROJECT_ROOT / 'docker-compose.yml'}:." \
        --add-data="{PROJECT_ROOT / 'config.py'}:." \
        --add-data="{PROJECT_ROOT / 'security.py'}:." \
        --add-data="{PROJECT_ROOT / 'translations.py'}:." \
        --hidden-import=PyQt5.sip \
        --hidden-import=config \
        --hidden-import=translations \
        --hidden-import=system_profiler \
        --hidden-import=ui --hidden-import=ui.components \
        --hidden-import=ui.dialogs --hidden-import=ui.main_window \
        --hidden-import=ui.threads --hidden-import=ui.widgets \
        "{GUI_SCRIPT}" '''

    if run(cmd, cwd=str(SCRIPT_DIR)):
        bin_path = output_dir / APP_NAME
        if bin_path.exists():
            final_bin = DIST_DIR / f"{APP_NAME}-Linux-x86_64"
            if final_bin.exists():
                final_bin.unlink()
            shutil.move(str(bin_path), str(final_bin))
            os.chmod(final_bin, 0o755)
            print(f"  {G}[OK]{N} Creato: {final_bin}")

            # Crea tar.gz
            tar_path = DIST_DIR / f"{APP_NAME}-Linux-x86_64.tar.gz"
            run(f'tar -czvf "{tar_path}" -C "{DIST_DIR}" "{final_bin.name}"')
            print(f"  {G}[OK]{N} Creato: {tar_path}")
            return True

    return False


def build_appimage():
    """Crea AppImage per Linux."""
    print(f"\n{BOLD}[3] Build AppImage...{N}")

    if platform.system() != "Linux":
        return False

    # Verifica appimagetool
    if not shutil.which("appimagetool"):
        print(f"  {Y}[!]{N} appimagetool non trovato")
        print(f"  Scarica da: https://github.com/AppImage/AppImageKit/releases")
        return False

    # Crea struttura AppDir
    appdir = SCRIPT_DIR / "AppDir"
    appdir.mkdir(exist_ok=True)

    (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
    (appdir / "usr" / "share" / "icons").mkdir(parents=True, exist_ok=True)

    # Copia binario
    bin_src = DIST_DIR / f"{APP_NAME}-Linux-x86_64"
    if bin_src.exists():
        shutil.copy(bin_src, appdir / "usr" / "bin" / APP_NAME)

    # Copia icona
    if ICON_PNG.exists():
        shutil.copy(ICON_PNG, appdir / "usr" / "share" / "icons" / "openwebui.png")
        shutil.copy(ICON_PNG, appdir / "openwebui.png")

    # Crea .desktop
    desktop = f"""[Desktop Entry]
Name=Open WebUI Manager
Exec={APP_NAME}
Icon=openwebui
Type=Application
Categories=Development;Utility;
"""
    (appdir / f"{APP_NAME}.desktop").write_text(desktop)

    # Crea AppRun
    apprun = f"""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${{SELF%/*}}
exec "$HERE/usr/bin/{APP_NAME}" "$@"
"""
    apprun_path = appdir / "AppRun"
    apprun_path.write_text(apprun)
    os.chmod(apprun_path, 0o755)

    # Build AppImage
    appimage_path = DIST_DIR / f"{APP_NAME}-x86_64.AppImage"
    if run(f'ARCH=x86_64 appimagetool "{appdir}" "{appimage_path}"'):
        print(f"  {G}[OK]{N} Creato: {appimage_path}")
        shutil.rmtree(appdir)
        return True

    return False


def create_zip():
    """Crea archivio ZIP dell'intero progetto."""
    print(f"\n{BOLD}[4] Creazione archivio progetto...{N}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"ollama-webui_{VERSION}_{timestamp}"

    project_name = PROJECT_ROOT.name  # "ollama-webui"
    zip_path = DIST_DIR / f"{zip_name}.zip"

    # Escludi cartelle non necessarie (pattern relativi al nome progetto)
    exclude_dirs = ["dist", "build", "__pycache__", "venv", ".git", "AppDir"]
    exclude_files = ["*.pyc", "*.pyo", "*.spec"]

    exclude_args = " ".join(
        [f'-x "{project_name}/{d}/*"' for d in exclude_dirs]
        + [f'-x "{e}"' for e in exclude_files]
    )

    cmd = f'cd "{PROJECT_ROOT.parent}" && zip -r "{zip_path}" "{project_name}" {exclude_args}'

    if run(cmd):
        print(f"  {G}[OK]{N} Creato: {zip_path}")
        print(f"  Dimensione: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True

    return False


def build_bat_portable():
    """Crea pacchetto .bat portatile per Windows."""
    print(f"\n{BOLD}[7] Creazione pacchetto .bat portatile...{N}")

    PROJECT_ROOT = SCRIPT_DIR.parent
    PORTABLE_DIR = SCRIPT_DIR / "OpenWebUI-Manager-Portable"

    # Pulisci eventuale build precedente
    if PORTABLE_DIR.exists():
        shutil.rmtree(PORTABLE_DIR)

    PORTABLE_DIR.mkdir(exist_ok=True)

    # File e cartelle da copiare dal progetto padre
    items_to_copy = [
        ("openwebui_gui.py", None),
        ("openwebui_gui_lite.py", None),
        ("docker-compose.yml", None),
        ("requirements.txt", None),
        ("config.py", None),
        ("security.py", None),
        ("system_profiler.py", None),
        ("translations.py", None),
        ("run_gui.bat", None),
        ("run_gui.sh", None),
        ("run_gui_lite.bat", None),
        ("run_gui_lite.sh", None),
        ("ICONA", None),
        ("ui", None),
        ("fonts", None),
        ("Tools OWUI", None),
        ("scripts", None),
        ("image_analysis", None),
        ("tts_service", None),
        ("document_service", None),
        ("mcp_service", None),
    ]

    copied = 0
    for item_name, dest_name in items_to_copy:
        src = PROJECT_ROOT / item_name
        dst = PORTABLE_DIR / (dest_name or item_name)
        if not src.exists():
            print(f"  {Y}[!]{N} Non trovato: {item_name} (saltato)")
            continue
        try:
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', '*.pyo', 'venv', '.git',
                    '*_backup*', '*.bak', '.tts_cache'))
            else:
                shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            print(f"  {R}[X]{N} Errore copia {item_name}: {e}")

    print(f"  {G}[OK]{N} Copiati {copied} elementi")

    # Download pacchetti per installazione offline (cross-platform)
    packages_dir = PORTABLE_DIR / "packages"
    packages_dir.mkdir(exist_ok=True)
    req_file = PROJECT_ROOT / "requirements.txt"

    # Usa il pip del Python corrente (funziona con o senza venv)
    pip_base = [sys.executable, "-m", "pip"]

    # Verifica che pip sia disponibile
    pip_check = subprocess.run(
        pip_base + ["--version"], capture_output=True, text=True
    )

    if pip_check.returncode == 0 and req_file.exists():
        print(f"\n  Download pacchetti offline per entrambe le piattaforme...")

        # 1. Download per piattaforma corrente (include source distributions)
        print(f"  [1/3] Pacchetti piattaforma corrente + sorgenti...")
        subprocess.run(
            pip_base + ["download", "-r", str(req_file), "-d", str(packages_dir)],
            capture_output=True, text=True
        )

        # 2. Download wheel Windows amd64 (per le versioni Python piu' comuni)
        for pyver in ["310", "311", "312", "313"]:
            print(f"  [2/3] Wheel Windows (Python 3.{pyver[1:]})...", end=" ")
            result = subprocess.run(
                pip_base + ["download", "-r", str(req_file), "-d", str(packages_dir),
                            "--platform", "win_amd64", "--python-version", pyver,
                            "--only-binary", ":all:", "--no-deps"],
                capture_output=True, text=True
            )
            print(f"{G}OK{N}" if result.returncode == 0 else f"{Y}parziale{N}")

        # 3. Download wheel Linux manylinux (per sicurezza, se non gia' presenti)
        for pyver in ["310", "311", "312", "313"]:
            print(f"  [3/3] Wheel Linux (Python 3.{pyver[1:]})...", end=" ")
            result = subprocess.run(
                pip_base + ["download", "-r", str(req_file), "-d", str(packages_dir),
                            "--platform", "manylinux2014_x86_64", "--python-version", pyver,
                            "--only-binary", ":all:", "--no-deps"],
                capture_output=True, text=True
            )
            print(f"{G}OK{N}" if result.returncode == 0 else f"{Y}parziale{N}")

        pkg_count = len(list(packages_dir.glob("*")))
        pkg_size = sum(f.stat().st_size for f in packages_dir.glob("*")) / 1024 / 1024
        print(f"  {G}[OK]{N} {pkg_count} pacchetti scaricati ({pkg_size:.0f} MB)")
    else:
        print(f"  {Y}[!]{N} pip o requirements.txt non trovati")
        print(f"  {Y}[!]{N} Il launcher scarichera' le dipendenze al primo avvio")

    # Genera il launcher .bat (Windows)
    bat_content = r'''@echo off
chcp 65001 >nul 2>&1
title Open WebUI Manager - Avvio
color 1F

echo.
echo  ======================================================
echo           Open WebUI Manager - Versione Portatile
echo  ======================================================
echo.

:: Trova Python (prova python, python3, py)
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
echo  Per usare Open WebUI Manager devi installare Python 3.8+
echo  Scaricalo da: https://www.python.org/downloads/
echo.
echo  IMPORTANTE: durante l'installazione seleziona
echo  "Add Python to PATH"
echo.
pause
exit /b 1

:python_found
echo  [OK] Python trovato: %PYTHON_CMD%
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo       %%i
echo.

:: Directory di questo script
set "BASE_DIR=%~dp0"
:: Rimuovi trailing backslash
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: Verifica/crea ambiente virtuale
if not exist "%BASE_DIR%\venv\Scripts\python.exe" (
    echo  [*] Creazione ambiente virtuale...
    echo      Questa operazione viene eseguita solo la prima volta.
    echo.
    %PYTHON_CMD% -m venv "%BASE_DIR%\venv"
    if %ERRORLEVEL% neq 0 (
        echo  [ERRORE] Impossibile creare l'ambiente virtuale.
        echo  Prova: %PYTHON_CMD% -m pip install virtualenv
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Ambiente virtuale creato
    echo.

    "%BASE_DIR%\venv\Scripts\pip.exe" install --upgrade pip >nul 2>&1

    echo  [*] Installazione dipendenze...
    if exist "%BASE_DIR%\packages" (
        echo      Installazione da pacchetti locali...
        "%BASE_DIR%\venv\Scripts\pip.exe" install --no-index --find-links="%BASE_DIR%\packages" -r "%BASE_DIR%\requirements.txt" >nul 2>&1
        if %ERRORLEVEL% neq 0 (
            echo      Alcuni pacchetti mancanti, scaricamento da internet...
            "%BASE_DIR%\venv\Scripts\pip.exe" install --find-links="%BASE_DIR%\packages" -r "%BASE_DIR%\requirements.txt"
        ) else (
            echo  [OK] Dipendenze installate (offline)
        )
    ) else (
        echo      Scaricamento da internet...
        "%BASE_DIR%\venv\Scripts\pip.exe" install -r "%BASE_DIR%\requirements.txt"
    )
    if %ERRORLEVEL% neq 0 (
        echo  [ATTENZIONE] Alcune dipendenze potrebbero non essere installate.
        echo  Il programma potrebbe comunque funzionare.
        echo.
    )
    echo.
) else (
    echo  [OK] Ambiente virtuale presente
    echo.
)

:: Avvio GUI
echo  [*] Avvio Open WebUI Manager...
echo.
"%BASE_DIR%\venv\Scripts\python.exe" "%BASE_DIR%\openwebui_gui.py"

if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERRORE] Il programma si e' chiuso con un errore.
    echo  Prova a eliminare la cartella "venv" e riavvia.
    echo.
    pause
)
'''

    bat_path = PORTABLE_DIR / "Avvia_OpenWebUI_Manager.bat"
    bat_path.write_text(bat_content, encoding='utf-8')
    print(f"  {G}[OK]{N} Creato: Avvia_OpenWebUI_Manager.bat")

    # Genera il launcher .sh (Linux/macOS)
    sh_content = '''#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "  ======================================================"
echo "       Open WebUI Manager - Versione Portatile"
echo "  ======================================================"
echo ""

# Trova Python
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "  [ERRORE] Python non trovato!"
    echo ""
    echo "  Installa Python 3.8+ con:"
    echo "    Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "    Fedora:        sudo dnf install python3 python3-pip"
    echo "    macOS:         brew install python3"
    echo ""
    exit 1
fi

echo "  [OK] Python trovato: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"
echo ""

# Verifica/crea ambiente virtuale
if [ ! -f "$SCRIPT_DIR/venv/bin/python" ]; then
    echo "  [*] Creazione ambiente virtuale..."
    echo "      Questa operazione viene eseguita solo la prima volta."
    echo ""
    $PYTHON_CMD -m venv "$SCRIPT_DIR/venv"
    echo "  [OK] Ambiente virtuale creato"
    echo ""

    "$SCRIPT_DIR/venv/bin/pip" install --upgrade pip > /dev/null 2>&1

    echo "  [*] Installazione dipendenze..."
    if [ -d "$SCRIPT_DIR/packages" ]; then
        echo "      Installazione da pacchetti locali..."
        "$SCRIPT_DIR/venv/bin/pip" install --no-index --find-links="$SCRIPT_DIR/packages" -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "      Alcuni pacchetti mancanti, scaricamento da internet..."
            "$SCRIPT_DIR/venv/bin/pip" install --find-links="$SCRIPT_DIR/packages" -r "$SCRIPT_DIR/requirements.txt"
        else
            echo "  [OK] Dipendenze installate (offline)"
        fi
    else
        echo "      Scaricamento da internet..."
        "$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
    fi
    echo ""
else
    echo "  [OK] Ambiente virtuale presente"
    echo ""
fi

# Avvio GUI
echo "  [*] Avvio Open WebUI Manager..."
echo ""
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/openwebui_gui.py"
'''

    sh_path = PORTABLE_DIR / "Avvia_OpenWebUI_Manager.sh"
    sh_path.write_text(sh_content, encoding='utf-8')
    os.chmod(sh_path, 0o755)
    print(f"  {G}[OK]{N} Creato: Avvia_OpenWebUI_Manager.sh")

    # Crea archivio ZIP
    zip_name = f"OpenWebUI-Manager-Portable-{VERSION}"
    zip_path = SCRIPT_DIR / f"{zip_name}.zip"

    print(f"\n  Creazione archivio ZIP...")
    shutil.make_archive(str(SCRIPT_DIR / zip_name), 'zip',
                        root_dir=SCRIPT_DIR,
                        base_dir="OpenWebUI-Manager-Portable")
    print(f"  {G}[OK]{N} Creato: {zip_path}")
    print(f"  Dimensione: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    print(f"\n  {G}Contenuto cartella portatile:{N}")
    for item in sorted(PORTABLE_DIR.iterdir()):
        tag = "DIR " if item.is_dir() else "FILE"
        print(f"    [{tag}] {item.name}")

    print(f"\n{G}==================================================================={N}")
    print(f"  {G}[OK]{N} Build completato!")
    print(f"  Cartella: {PORTABLE_DIR}")
    print(f"  ZIP:      {zip_path.name}")
    print(f"{G}==================================================================={N}\n")

    return True


def clean():
    """Pulisce file temporanei build."""
    print(f"\n{BOLD}Pulizia file temporanei...{N}")

    to_remove = [
        SCRIPT_DIR / "build",
        SCRIPT_DIR / "output",
        SCRIPT_DIR / "AppDir",
        SCRIPT_DIR / f"{APP_NAME}.spec",
        # Pulizia residui che PyInstaller potrebbe lasciare nella root
        PROJECT_ROOT / "build",
        PROJECT_ROOT / f"{APP_NAME}.spec",
    ]

    for path in to_remove:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  {G}[OK]{N} Rimosso: {path.name}")


def menu():
    """Menu interattivo."""
    print_header()

    print(f"""
  {BOLD}Cosa vuoi buildare?{N}

  [1] Windows (.exe)
  [2] Linux (binario)
  [3] Linux AppImage
  [4] Tutti (Windows + Linux)
  [5] Crea ZIP progetto
  [6] Pulisci file temporanei
  [7] Windows .bat (portatile)
  [0] Esci
""")

    choice = input(f"  {BOLD}Scegli: {N}").strip()

    if choice == "1":
        check_venv()
        check_dependencies()
        build_windows()
    elif choice == "2":
        check_venv()
        check_dependencies()
        build_linux()
    elif choice == "3":
        check_venv()
        check_dependencies()
        build_linux()
        build_appimage()
    elif choice == "4":
        check_venv()
        check_dependencies()
        build_windows()
        build_linux()
        build_appimage()
    elif choice == "5":
        create_zip()
    elif choice == "6":
        clean()
    elif choice == "7":
        build_bat_portable()
        return
    elif choice == "0":
        return

    clean()

    print(f"\n{G}==================================================================={N}")
    print(f"  {G}[OK]{N} Build completato!")
    print(f"  Output in: {DIST_DIR}")
    print(f"{G}==================================================================={N}\n")


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        print_header()

        # Verifica ambiente virtuale (si riavvia se necessario)
        if cmd in ["windows", "linux", "all"]:
            check_venv()

        if cmd not in ["bat", "zip", "clean"]:
            check_dependencies()

        if cmd == "windows":
            build_windows()
        elif cmd == "linux":
            build_linux()
            build_appimage()
        elif cmd == "all":
            build_windows()
            build_linux()
            build_appimage()
        elif cmd == "zip":
            create_zip()
        elif cmd == "bat":
            build_bat_portable()
            return
        elif cmd == "clean":
            clean()
            return
        else:
            print(f"Uso: {sys.argv[0]} [windows|linux|all|zip|bat|clean]")
            return

        clean()
    else:
        menu()


if __name__ == "__main__":
    main()
