# 🚀 Open WebUI + Ollama - Sistema Completo

**Autore:** Carlo | **Versione:** 1.0.0 | **Data:** 2026-01-22

Sistema completo LLM locali con 11 tools specializzati, concilio multi-modello, italiano nativo, accesso LAN e backup automatico.
I programmi windows/linux chiamati  BUILD servono a esportare il progetto se fai una modifica.
---

## 🎯 Quick Start

```bash
./start.sh                     # Avvia servizi
./configure_italian.sh         # Configura italiano
python3 install_tools.py       # Installa tools
```

Apri: `http://localhost:3000`

📖 **[GUIDA COMPLETA](GUIDA_COMPLETA.md)** - Tutto in un unico documento organizzato

---

## 📋 Indice

1. [Requisiti Sistema](#-requisiti-sistema)
2. [Installazione Rapida](#-installazione-rapida)
3. [Tools Disponibili](#-tools-disponibili)
4. [Scientific Council](#-scientific-council---nuovo)
5. [Accesso da Dispositivi Mobili](#-accesso-da-dispositivi-mobili-lan)
6. [Sistema di Backup](#-sistema-di-backup-su-usb)
7. [Gestione Modelli](#-gestione-modelli-llm)
8. [Troubleshooting](#-troubleshooting)
9. [Miglioramenti Futuri](#-miglioramenti-futuri)

---

## 💻 Requisiti Sistema

### Hardware Minimo
- **CPU:** 4+ core
- **RAM:** 8GB (16GB raccomandati per 4+ modelli paralleli)
- **Spazio Disco:** 50GB liberi
  - Sistema base: ~5GB
  - Modelli 7B (quantizzati): ~4-5GB ciascuno
  - Modelli 13B: ~8-10GB ciascuno

### Software
- **OS:** Linux (Ubuntu 20.04+, Debian, Fedora, ecc.) oppure Windows con WSL2
- **Docker:** 20.10+
- **Docker Compose:** 1.29+
- **Python:** 3.8+ (per script installazione tools)

### Opzionale
- Chiavetta USB: 32GB+ (per backup completi con modelli)
- Router WiFi (per accesso LAN da mobile)

---

## 🚀 Installazione Rapida

### 1. Installa Docker

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Riavvia la sessione dopo questo comando
```

**Windows:**
Scarica Docker Desktop da: https://www.docker.com/products/docker-desktop

### 2. Clona o Prepara il Progetto

```bash
cd ~/Desktop/CARLO/ollama-webui
```

### 3. Avvia i Servizi

**Linux:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

Oppure manualmente:
```bash
docker-compose up -d
```

Attendi 1-2 minuti per l'avvio completo.

### 4. Accedi a Open WebUI

Apri il browser: `http://localhost:3000`

- Crea un account (il primo sarà admin)
- Effettua il login

### 5. Scarica Modelli LLM

```bash
# Modelli consigliati per Scientific Council
docker exec -it ollama ollama pull qwen2.5:7b-instruct-q4_K_M
docker exec -it ollama ollama pull mistral:7b-instruct
docker exec -it ollama ollama pull qwen2-math:latest
docker exec -it ollama ollama pull qwen2.5-coder:7b
docker exec -it ollama ollama pull gemma2:9b
```

### 6. Installa i Tools

```bash
python3 install_tools.py
```

Inserisci le credenziali admin di Open WebUI quando richiesto.

### 7. Attiva i Tools in Open WebUI

1. Admin Panel → **Functions** → **Tools**
2. Toggle per attivare i tools desiderati
3. Nelle chat: clicca **+** per selezionare i tools

---

## 🔧 Tools Disponibili

| Tool | Descrizione | Domini |
|------|-------------|--------|
| **Text Assistant** | Assistente testi generale | Scrittura, editing, traduzioni |
| **Math Assistant** | Matematica e calcoli | Algebra, calcolo, statistica |
| **Code Assistant** | Programmazione | Python, JS, debug, review |
| **Book Assistant** | Creazione libri | Struttura, capitoli, editing |
| **Study Assistant** | Studio e apprendimento | Riassunti, quiz, spiegazioni |
| **Creative Writing** | Scrittura creativa | Storie, poesie, dialoghi |
| **Research Assistant** | Ricerca scientifica | Paper, analisi, sintesi |
| **Book Publishing** | Pubblicazione libri | Formattazione, export, marketing |
| **Productivity Assistant** | Produttività | Task, email, planning |
| **Finance Italian** | Finanza personale | Budget, investimenti (ITA) |
| **Scientific Council** 🆕 | Concilio multi-LLM | Matematica pura, LaTeX, grafici |

---

## 🧠 Scientific Council - NUOVO!

### Descrizione

Sistema innovativo che consulta **3-5 modelli LLM in parallelo** per ottenere risposte aggregate attraverso votazione intelligente e consenso.

### Funzionalità Specializzate

#### 1. **Consultazione Concilio**
Interroga più LLM e aggrega le risposte.

```python
consult_council(
    domanda="Dimostra il teorema di Pitagora",
    dominio="matematica",  # matematica, codice, italiano, sicurezza, generale
    strategia="comparative"  # weighted, comparative, synthesis
)
```

**Strategie:**
- `weighted`: Presenta risposta primaria + alternative ordinate per peso
- `comparative`: Analisi similarità, identifica consenso/divergenze
- `synthesis`: Un LLM unifica tutte le risposte

#### 2. **Generazione LaTeX**
Crea formule matematiche da linguaggio naturale.

```python
generate_latex_formula(
    descrizione="integrale di x al quadrato da 0 a 1",
    tipo="equation",  # inline, display, equation, align
    verifica=true
)
```

Output: codice LaTeX + rendering MathJax + validazione sintassi

#### 3. **Verifica Dimostrazioni**
Analisi rigorosità matematica multi-modello.

```python
verify_proof(
    teorema="Se n è pari allora n^2 è pari",
    dimostrazione="Sia n=2k. Allora n^2=(2k)^2=4k^2=2(2k^2) che è pari",
    livello_rigore="alto"  # basso, medio, alto
)
```

Analizza: correttezza logica, gap, assunzioni, completezza

#### 4. **Bibliografia Scientifica**
Genera riferimenti autorevoli.

```python
generate_bibliography(
    argomento="topologia algebrica",
    stile="bibtex",  # bibtex, apa, ieee, chicago
    numero=5
)
```

#### 5. **Esercizi con Soluzioni**
Crea esercizi graduali con soluzioni step-by-step.

```python
create_exercises(
    argomento="derivate di funzioni trigonometriche",
    numero=3,
    difficolta="medio",  # facile, medio, difficile, misto
    con_soluzioni=true,
    con_hint=true
)
```

#### 6. **Visualizzazioni Matematiche**
Grafici 2D/3D con matplotlib/plotly.

```python
# Grafico 2D
plot_mathematical(
    espressione="sin(x) + cos(2*x)",
    tipo="2d",
    range_x="-6.28,6.28"
)

# Superficie 3D
plot_mathematical(
    espressione="sin(sqrt(x**2 + y**2))",
    tipo="3d",
    range_x="-5,5",
    range_y="-5,5",
    interattivo=true  # Usa Plotly per interattività
)
```

### Configurazioni Modelli per Dominio

| Dominio | Modelli Specializzati | Peso |
|---------|----------------------|------|
| **matematica** | qwen2-math, qwen2.5, mistral, gemma2 | 1.5, 1.0, 0.8, 0.9 |
| **codice** | qwen2.5-coder, codellama, mistral | 1.5, 1.3, 0.8 |
| **italiano** | mistral, gemma2, llama3 | 1.2, 1.0, 0.9 |
| **sicurezza** | qwen2.5-coder, mistral, codellama | 1.2, 1.0, 0.9 |
| **generale** | qwen2.5, mistral, llama3, gemma2 | 1.0, 1.0, 0.9, 0.8 |

---

## 📱 Accesso da Dispositivi Mobili (LAN)

### Attivazione Rapida

```bash
./enable_lan_access.sh
```

Lo script:
1. ✅ Configura docker-compose.yml (0.0.0.0 binding)
2. ✅ Apre le porte nel firewall (3000, 11434)
3. ✅ Riavvia i servizi
4. ✅ Mostra l'IP per la connessione mobile

### Connessione da Cellulare

1. Connetti il cellulare alla **stessa WiFi** del PC
2. Apri il browser
3. Vai a: `http://192.168.1.X:3000` (usa l'IP mostrato dallo script)
4. Login con le tue credenziali Open WebUI

### Disattivazione

```bash
./disable_lan_access.sh
```

Ripristina modalità localhost-only (127.0.0.1).

### 📚 Documentazione Completa

Vedi: [`docs/LAN_ACCESS.md`](docs/LAN_ACCESS.md)

---

## 💾 Sistema di Backup su USB

### Backup Completo

```bash
./backup_to_usb.sh
```

Lo script:
1. 🔍 Rileva chiavette USB automaticamente
2. ❓ Chiede se includere modelli LLM (5-10GB ciascuno)
3. 📊 Verifica spazio disponibile
4. 💾 Crea backup di:
   - Configurazioni Docker
   - Tutti gli script
   - Tools Open WebUI
   - Dati utente e conversazioni
   - Modelli LLM (opzionale)
5. 📝 Genera script di ripristino automatico

### Cosa Viene Salvato

**Sempre incluso:**
- ✅ `docker-compose.yml`, `.env`
- ✅ Script bash (enable/disable LAN, backup)
- ✅ `install_tools.py`
- ✅ Directory `tools/` completa (11 tools)
- ✅ Dati utente Open WebUI (account, chat, documenti)
- ✅ Documentazione

**Opzionale (richiesto in CLI):**
- ❓ Modelli LLM Ollama (~5-50GB totali)

### Ripristino Backup

Sul PC di destinazione (con Docker installato):

```bash
cd /media/usb/openwebui_backup_20260122_153045
./RESTORE.sh
```

Lo script ripristina tutto automaticamente.

### Dimensioni Tipiche

| Componente | Dimensione Approssimativa |
|------------|---------------------------|
| Configurazioni + Tools | ~15-20MB |
| Dati utente | ~50-500MB (dipende da uso) |
| Modello 7B (singolo) | ~4-5GB |
| Backup completo (5 modelli) | ~25-30GB |
| Backup senza modelli | ~500MB |

**Consiglio:** Per backup frequenti escludi i modelli (puoi riscaricarli velocemente).

---

## 🤖 Gestione Modelli LLM

### Scaricare Modelli

```bash
# Lista modelli disponibili
docker exec -it ollama ollama list

# Scarica un modello
docker exec -it ollama ollama pull <nome_modello>

# Esempi
docker exec -it ollama ollama pull qwen2.5:7b-instruct-q4_K_M
docker exec -it ollama ollama pull mistral:7b-instruct
docker exec -it ollama ollama pull llama3:8b
```

### Modelli Consigliati per Scientific Council

| Modello | Specialità | Dimensione | Comando |
|---------|-----------|------------|---------|
| qwen2-math | Matematica pura | ~4.7GB | `ollama pull qwen2-math` |
| qwen2.5:7b | Generale + ragionamento | ~4.7GB | `ollama pull qwen2.5:7b-instruct-q4_K_M` |
| qwen2.5-coder:7b | Codice + sicurezza | ~4.7GB | `ollama pull qwen2.5-coder:7b` |
| mistral:7b | Generale + italiano | ~4.1GB | `ollama pull mistral:7b-instruct` |
| gemma2:9b | Analisi + sintesi | ~5.4GB | `ollama pull gemma2:9b` |

**Totale consigliato:** ~24GB per esperienza completa

### Rimuovere Modelli

```bash
docker exec -it ollama ollama rm <nome_modello>
```

### Verificare Modelli in Uso

```bash
docker exec -it ollama ollama ps
```

---

## 🔧 Troubleshooting

### Open WebUI Non Carica (Errori 404 JS)

Se vedi errori `404` per file `.js` nella console:

```bash
# 1. Pulisci container e ricostruisci
docker-compose down
docker system prune -f
docker-compose up -d --build

# 2. Verifica log
docker-compose logs -f open-webui

# 3. Se persiste, rimuovi volumi e ricrea
docker-compose down -v
docker-compose up -d
```

### Servizi Non si Avviano

```bash
# Verifica log
docker-compose logs -f

# Riavvia
docker-compose restart

# Ricostruisci
docker-compose down
docker-compose up -d --build
```

### Porta 3000 Già in Uso

```bash
# Trova processo
sudo lsof -i :3000

# Cambia porta in docker-compose.yml
ports:
  - "3001:8080"  # Usa porta 3001
```

### Tools Non Compaiono in Open WebUI

1. Verifica installazione: `python3 install_tools.py`
2. Admin Panel → Functions → Tools
3. Toggle per attivare
4. Ricarica pagina (F5)
5. Controlla log: `docker-compose logs open-webui`

### Accesso LAN Non Funziona

```bash
# Verifica porte aperte
sudo ss -tulpn | grep -E ":3000|:11434"
# Devono mostrare 0.0.0.0, non 127.0.0.1

# Verifica firewall
sudo firewall-cmd --list-ports
# Devono essere presenti 3000/tcp e 11434/tcp

# Test da PC
curl http://192.168.1.X:3000
```

### Modelli Lenti

- Usa modelli quantizzati (q4_K_M, q5_K_M)
- Chiudi applicazioni pesanti
- Aumenta RAM allocata a Docker
- Usa meno modelli in parallelo nel Scientific Council

### Modalità Vocale - "Autorizzazione Negata" per Microfono 🎤

**Problema:** Il browser blocca l'accesso al microfono.

**Soluzione Rapida (da PC):**
```
1. Usa http://localhost:3000 (non IP!)
2. Clicca "Consenti" quando richiesto
3. Se non appare: 🔒 → Autorizzazioni → Microfono → Consenti
4. Ricarica pagina (F5)
```

**Soluzione per Cellulare/Tablet:**

I browser mobili richiedono HTTPS per il microfono:

```bash
./enable_https.sh
```

Poi accedi da: `https://192.168.1.X` (accetta certificato self-signed)

**Guida completa:** [`QUICK_FIX_MICROFONO.md`](QUICK_FIX_MICROFONO.md) e [`docs/VOICE_MODE_PERMISSIONS.md`](docs/VOICE_MODE_PERMISSIONS.md)

---

## 🎯 Miglioramenti Futuri

### Funzionalità Pianificate

#### Scientific Council
- [ ] Grafici parametrici e coordinate polari
- [ ] Animazioni matplotlib per evoluzioni temporali
- [ ] Integrazione proof assistants (Lean, Coq)
- [ ] Embedding semantici per similarità (migliore del Jaccard)
- [ ] Caching risposte LLM (evita query ripetute)
- [ ] Async/await per performance migliorate

#### Sistema Generale
- [ ] Interfaccia web per gestione backup
- [ ] Backup automatici programmati (cron)
- [ ] Sincronizzazione cloud (opzionale)
- [ ] Dashboard monitoring risorse
- [ ] Auto-update modelli LLM
- [ ] Template conversazioni pre-configurate
- [ ] Export conversazioni in PDF/Markdown

#### Sicurezza
- [ ] Autenticazione a due fattori (2FA)
- [ ] HTTPS con certificati self-signed
- [ ] Rate limiting per API
- [ ] Audit log accessi

### Come Contribuire

Suggerimenti e miglioramenti sono benvenuti!

---

## 📚 Documentazione Aggiuntiva

- [`docs/LAN_ACCESS.md`](docs/LAN_ACCESS.md) - Guida completa accesso LAN
- `BACKUP_INFO.txt` - Generato automaticamente nei backup
- Inline docstrings nei file Python

---

## 📄 Licenza

**Uso Personale e Educativo**

Questo progetto è fornito "as-is" per uso personale ed educativo.

---

## 👤 Autore

**Carlo**
Data: 2026-01-22
Versione: 1.0.0

---

## 🙏 Ringraziamenti

- [Open WebUI](https://github.com/open-webui/open-webui) - Interfaccia web fantastica
- [Ollama](https://ollama.ai/) - Runtime LLM locale
- Community open source per i modelli LLM

---

## 📞 Supporto

Per problemi o domande:
1. Controlla questa documentazione
2. Consulta `docs/LAN_ACCESS.md`
3. Verifica i log: `docker-compose logs -f`
4. Ricostruisci i container: `docker-compose down && docker-compose up -d --build`

---

**Buon utilizzo! 🚀**
