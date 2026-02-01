╔══════════════════════════════════════════════════════════════╗
║         🤖 OLLAMA + OPEN WEBUI - PACCHETTO PORTATILE         ║
║              Con 50+ Tools AI Preinstallati!                 ║
╚══════════════════════════════════════════════════════════════╝

Questo pacchetto contiene Open WebUI configurato con Ollama e
tutti i tools AI già pronti all'uso.


📦 CONTENUTO
============
├── INSTALLA.sh      → Script di installazione automatica
├── start.sh         → Avvia i servizi
├── stop.sh          → Ferma i servizi
├── docker-compose.yml
├── webui.db         → Database con tools preconfigurati
├── tools/           → File sorgente dei tools (backup)
└── README.txt       → Questo file


🚀 INSTALLAZIONE RAPIDA (Linux/Mac)
===================================
1. Installa Docker: https://docs.docker.com/get-docker/
2. Installa Ollama: https://ollama.ai
3. Apri terminale in questa cartella
4. Esegui:

   chmod +x *.sh
   ./INSTALLA.sh

5. Apri http://localhost:3000 nel browser
6. Registra un account
7. Inizia a chattare!


🪟 INSTALLAZIONE WINDOWS
========================
1. Installa Docker Desktop: https://docs.docker.com/desktop/windows/
2. Installa Ollama: https://ollama.ai
3. Apri PowerShell in questa cartella
4. Esegui:

   docker compose up -d

5. Apri http://localhost:3000 nel browser


🔧 TOOLS INCLUSI
================
Il pacchetto include 50+ funzioni AI:

📝 TESTI
   - Analisi testo, correzione grammatica, riassunti, stile

🔢 MATEMATICA
   - Calcoli, equazioni, conversioni, geometria, percentuali

💻 CODICE
   - Analisi, debug, spiegazioni, generazione, test

📚 LIBRI
   - Analisi letteraria, riassunti, personaggi

🎓 STUDIO
   - Flashcard, quiz, mappe mentali, preparazione esami

✍️ SCRITTURA CREATIVA
   - Storie, poesie, dialoghi, personaggi

🔍 RICERCA
   - Ricerche, fact-check, confronti

📖 PUBBLICAZIONE LIBRI
   - Revisione capitoli, formule LaTeX, teoremi, esercizi

📋 PRODUTTIVITÀ
   - Progetti, todo, email, riunioni, brainstorming

💰 FINANZA ITALIANA
   - IRPEF, mutui, P.IVA, pensioni, investimenti, PAC


💡 COME USARE I TOOLS
=====================
1. Apri una chat in Open WebUI
2. Clicca sul "+" accanto al campo messaggio
3. Seleziona "Mega Assistente Completo"
4. Scrivi la tua richiesta!

Esempi:
- "Calcola 25% di 1500"
- "Calcola IRPEF per reddito 40000€"
- "Genera 10 flashcard sulla Seconda Guerra Mondiale"
- "Debug questo errore Python: ..."
- "Scrivi il teorema di Pitagora con dimostrazione"


⚙️ REQUISITI
=============
- Docker (obbligatorio)
- Ollama (consigliato, per eseguire modelli locali)
- 4GB RAM minimo
- 10GB spazio disco


📥 SCARICARE MODELLI OLLAMA
===========================
Dopo l'installazione, scarica un modello:

   ollama pull llama3.2
   ollama pull mistral
   ollama pull codellama

Poi selezionalo in Open WebUI.


🆘 PROBLEMI?
============
1. Errore porta 3000 occupata:
   → Modifica la porta in docker-compose.yml

2. Ollama non risponde:
   → Avvia manualmente: ollama serve

3. Tools non visibili:
   → Admin Panel → Functions → Tools → Attiva i tools


Creato con ❤️ da Carlo
