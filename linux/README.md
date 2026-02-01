# Linux - Setup Docker Nativo

**Prestazioni ottimali per AI locale**

## Uso

```bash
./openwebui.sh              # Menu comandi
./openwebui.sh start        # Avvia servizi
./openwebui.sh stop         # Ferma servizi
./openwebui.sh status       # Verifica stato
./openwebui.sh install      # Installa dipendenze
```

## Porta

http://localhost:3000

## Requisiti

```bash
# Docker (Ubuntu/Debian)
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
```
