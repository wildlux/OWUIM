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
DIST_DIR = SCRIPT_DIR / "dist"
ICON_PNG = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
ICON_ICO = SCRIPT_DIR / "ICONA" / "ICONA.ico"
GUI_SCRIPT = SCRIPT_DIR / "openwebui_gui.py"
VENV_DIR = SCRIPT_DIR / "venv"
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


def run(cmd, check=True, shell=True):
    """Esegue comando."""
    print(f"  {Y}>{N} {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
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

    # Se siamo gia' nel venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
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
        req_file = SCRIPT_DIR / "requirements.txt"
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
    script_dir_str = str(SCRIPT_DIR).replace("\\", "\\\\")
    icon_dir_str = str(SCRIPT_DIR / "ICONA").replace("\\", "\\\\")
    tools_dir_str = str(SCRIPT_DIR / "Tools OWUI").replace("\\", "\\\\")
    scripts_dir_str = str(SCRIPT_DIR / "scripts").replace("\\", "\\\\")
    compose_str = str(SCRIPT_DIR / "docker-compose.yml").replace("\\", "\\\\")
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
        (r'{compose_str}', '.'),
    ],
    hiddenimports=['PyQt5.sip'],
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

    # Build
    cmd = f'"{pyinstaller_path}" --clean --noconfirm "{spec_file}"'
    if run(cmd):
        # Sposta in dist/
        exe_path = SCRIPT_DIR / "dist" / f"{APP_NAME}.exe"
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

    # Build con PyInstaller
    icon_opt = f'--icon="{ICON_PNG}"' if ICON_PNG.exists() else ""

    cmd = f'''pyinstaller --onefile --windowed --name={APP_NAME} \
        {icon_opt} \
        --add-data="{SCRIPT_DIR / 'ICONA'}:ICONA" \
        --add-data="{SCRIPT_DIR / 'tools'}:tools" \
        --add-data="{SCRIPT_DIR / 'scripts'}:scripts" \
        --add-data="{SCRIPT_DIR / 'docker-compose.yml'}:." \
        --hidden-import=PyQt5.sip \
        "{GUI_SCRIPT}" '''

    if run(cmd):
        # Sposta binario
        bin_path = SCRIPT_DIR / "dist" / APP_NAME
        if bin_path.exists():
            final_bin = DIST_DIR / f"{APP_NAME}-Linux-x86_64"
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
    if run(f'appimagetool "{appdir}" "{appimage_path}"'):
        print(f"  {G}[OK]{N} Creato: {appimage_path}")
        shutil.rmtree(appdir)
        return True

    return False


def create_zip():
    """Crea archivio ZIP del progetto."""
    print(f"\n{BOLD}[4] Creazione archivio progetto...{N}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"ollama-webui_{VERSION}_{timestamp}"

    # Escludi cartelle non necessarie
    exclude = [
        "dist", "build", "__pycache__", "venv", ".git",
        "*.pyc", "*.pyo", "*.spec", "AppDir"
    ]

    exclude_args = " ".join([f'--exclude="{e}"' for e in exclude])

    parent_dir = SCRIPT_DIR.parent
    zip_path = parent_dir / f"{zip_name}.zip"

    cmd = f'cd "{parent_dir}" && zip -r "{zip_path}" "{SCRIPT_DIR.name}" {exclude_args}'

    if run(cmd):
        print(f"  {G}[OK]{N} Creato: {zip_path}")
        print(f"  Dimensione: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True

    return False


def clean():
    """Pulisce file temporanei build."""
    print(f"\n{BOLD}Pulizia file temporanei...{N}")

    to_remove = [
        SCRIPT_DIR / "build",
        SCRIPT_DIR / "AppDir",
        SCRIPT_DIR / f"{APP_NAME}.spec",
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
        elif cmd == "clean":
            clean()
        else:
            print(f"Uso: {sys.argv[0]} [windows|linux|all|zip|clean]")

        clean()
    else:
        menu()


if __name__ == "__main__":
    main()
