# Guida Rapida

## Installazione (Prima volta)

### Linux
1. Installa Docker:
```bash
sudo apt update && sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
```
2. Riavvia il computer
3. Vai alla cartella `ollama-webui`
4. Esegui: `./start.sh`

### Windows
1. Installa Docker Desktop da: https://www.docker.com/products/docker-desktop
2. Riavvia il computer
3. Vai alla cartella `ollama-webui`
4. Doppio click su `start.bat`

## Uso Quotidiano

### Avviare
- **Linux**: `./start.sh`
- **Windows**: doppio click su `start.bat`

Apri il browser su: http://localhost:3000

### Fermare
- **Linux**: `./stop.sh`
- **Windows**: doppio click su `stop.bat`

## Scaricare Modelli

Dopo aver avviato i servizi:

```bash
# Modello leggero e veloce (1.6GB)
docker exec -it ollama ollama pull phi

# Modello generale ottimo (4GB)
docker exec -it ollama ollama pull mistral

# Modello per codice (4GB)
docker exec -it ollama ollama pull codellama
```

## Primi Passi

1. Avvia con `start.sh` o `start.bat`
2. Il browser si apre automaticamente
3. Crea un account (il primo è admin)
4. Scarica un modello (vedi sopra)
5. Inizia a chattare!

## Problemi Comuni

**Errore "port already in use"**
- Qualche altro programma usa la porta 3000
- Chiudi altri server web o cambia porta in `docker-compose.yml`

**Container non si avvia**
- Verifica che Docker sia in esecuzione
- Linux: `sudo systemctl start docker`
- Windows: apri Docker Desktop

**Modello troppo lento**
- Usa modelli più piccoli (phi, gemma:2b)
- Chiudi altri programmi per liberare RAM

## Comandi Utili

```bash
# Vedere modelli scaricati
docker exec -it ollama ollama list

# Testare un modello da terminale
docker exec -it ollama ollama run mistral

# Vedere i log
docker compose logs -f

# Riavviare i servizi
docker compose restart
```

## Supporto

Leggi il README.md completo per maggiori informazioni.
