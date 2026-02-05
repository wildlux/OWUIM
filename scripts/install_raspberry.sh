#!/bin/bash
###############################################################################
# Installer per Raspberry Pi (Zero, Zero W, Zero 2 W, Pi 2/3/4/5)
# Installa Open WebUI Manager con interfaccia grafica leggera
###############################################################################

set -e

echo "═══════════════════════════════════════════════════════"
echo "    Open WebUI Manager - Installer Raspberry Pi"
echo "═══════════════════════════════════════════════════════"
echo

# Rileva architettura
ARCH=$(uname -m)
echo "Architettura rilevata: $ARCH"

# Verifica Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    MODEL=$(cat /proc/device-tree/model)
    echo "Modello: $MODEL"
fi
echo

# Verifica se è Pi Zero (ARMv6)
if [[ "$ARCH" == "armv6l" ]]; then
    echo "⚠️  Raspberry Pi Zero rilevato (ARMv6)"
    echo "   Verrà installata la versione Lite (Tkinter)"
    echo "   PyQt5 non è supportato su questo hardware."
    echo
    USE_LITE=true
elif [[ "$ARCH" == "armv7l" ]]; then
    echo "Raspberry Pi con ARMv7 rilevato"
    USE_LITE=true
elif [[ "$ARCH" == "aarch64" ]]; then
    echo "Raspberry Pi con ARM64 rilevato (Pi Zero 2 W, Pi 3/4/5)"
    USE_LITE=false
else
    echo "Architettura non riconosciuta: $ARCH"
    USE_LITE=true
fi

echo
echo "Installazione dipendenze..."
echo

# Aggiorna sistema
sudo apt update

# Installa Docker se non presente
if ! command -v docker &> /dev/null; then
    echo "Installazione Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    echo "✓ Docker installato"
    echo "  NOTA: Esegui 'newgrp docker' o riavvia per usare Docker senza sudo"
fi

# Installa dipendenze Python
if [ "$USE_LITE" = true ]; then
    echo "Installazione Python + Tkinter..."
    sudo apt install -y python3 python3-tk curl
else
    echo "Installazione Python + PyQt5..."
    sudo apt install -y python3 python3-pyqt5 curl
fi

echo
echo "✓ Dipendenze installate"
echo

# Crea launcher
echo "Creazione launcher..."

INSTALL_DIR="$HOME/openwebui-manager"
mkdir -p "$INSTALL_DIR"

# Copia file
cp docker-compose.yml "$INSTALL_DIR/" 2>/dev/null || true
cp manage.sh "$INSTALL_DIR/" 2>/dev/null || true
cp -r scripts "$INSTALL_DIR/" 2>/dev/null || true
cp -r tools "$INSTALL_DIR/" 2>/dev/null || true
cp -r docs "$INSTALL_DIR/" 2>/dev/null || true

if [ "$USE_LITE" = true ]; then
    cp openwebui_gui_lite.py "$INSTALL_DIR/openwebui_gui.py"
else
    cp openwebui_gui.py "$INSTALL_DIR/"
fi

chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true
chmod +x "$INSTALL_DIR"/*.py 2>/dev/null || true

# Crea script di avvio
cat > "$INSTALL_DIR/start_gui.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 openwebui_gui.py
EOF
chmod +x "$INSTALL_DIR/start_gui.sh"

# Crea desktop entry
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/openwebui-manager.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Open WebUI Manager
Comment=Gestione Open WebUI
Exec=$INSTALL_DIR/start_gui.sh
Icon=preferences-system
Terminal=false
Categories=Utility;
EOF

echo
echo "═══════════════════════════════════════════════════════"
echo "           ✓ Installazione Completata!"
echo "═══════════════════════════════════════════════════════"
echo
echo "Directory: $INSTALL_DIR"
echo
echo "Per avviare:"
echo "  cd $INSTALL_DIR"
echo "  ./start_gui.sh"
echo
echo "Oppure cerca 'Open WebUI Manager' nel menu applicazioni."
echo
echo "Primo avvio Open WebUI:"
echo "  cd $INSTALL_DIR"
echo "  docker compose up -d"
echo
echo "Poi apri: http://localhost:3000"
echo
