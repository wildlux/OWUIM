#!/bin/bash
# Avvia Open WebUI Manager Lite (GUI Tkinter)
# Non richiede ambiente virtuale - usa solo libreria standard

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 openwebui_gui_lite.py
