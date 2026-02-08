#!/usr/bin/env python3
"""
Open WebUI Manager - Launcher
Autore: Paolo Lo Bello
Versione: 1.1.0
Framework: PyQt5

Questo file e' il punto d'ingresso dell'applicazione.
I moduli UI sono in ui/, la configurazione in config.py.

Principi applicati:
- SRP: Solo logica di avvio, nessuna definizione di widget
- DIP: URL e porte da config.py, non hardcoded
- Programmazione difensiva: Eccezioni specifiche
"""

import sys
import os
import subprocess
import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

from config import (
    IS_WINDOWS, IS_MAC, SCRIPT_DIR,
    URL_WEBUI, URL_TTS, APP_NAME,
)
from ui.dialogs import StartupDialog
from ui.main_window import MainWindow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # Imposta icona applicazione
    icon_path = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Verifica argomenti (--no-startup per saltare avvio automatico)
    skip_startup = "--no-startup" in sys.argv or "-n" in sys.argv

    if not skip_startup:
        startup = StartupDialog()
        startup.start()
        startup.exec_()

    # Mostra finestra principale
    window = MainWindow()
    window.show()

    # Se i servizi sono attivi, apri il browser dopo 2 secondi
    if not skip_startup:
        def open_browser_delayed():
            try:
                result = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", URL_WEBUI],
                    capture_output=True, timeout=5, text=True
                )
                if result.stdout.strip() in ["200", "302"]:
                    if IS_WINDOWS:
                        os.startfile(URL_WEBUI)
                    elif IS_MAC:
                        subprocess.Popen(['open', URL_WEBUI],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.Popen(['xdg-open', URL_WEBUI],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                logger.debug("curl non trovato, impossibile verificare Open WebUI")
            except subprocess.TimeoutExpired:
                logger.debug("Timeout verifica Open WebUI")

        QTimer.singleShot(2000, open_browser_delayed)

        # Avvia automaticamente il servizio TTS
        def start_tts_delayed():
            try:
                result = subprocess.run(
                    ["curl", "-s", URL_TTS + "/"],
                    capture_output=True, timeout=2
                )
                if result.returncode != 0:
                    window.tts_widget.start_tts_service()
            except (FileNotFoundError, subprocess.TimeoutExpired):
                window.tts_widget.start_tts_service()

        QTimer.singleShot(4000, start_tts_delayed)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
