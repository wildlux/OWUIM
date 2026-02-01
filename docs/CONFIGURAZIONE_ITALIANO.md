# 🇮🇹 Configurazione Completa in Italiano - Open WebUI

## 📋 Panoramica

Questa guida spiega come configurare Open WebUI completamente in italiano, inclusi:
- ✅ Interfaccia utente
- ✅ Suggerimenti e prompt di sistema
- ✅ Messaggi di errore
- ✅ Modelli predefiniti in italiano

---

## ⚡ Configurazione Rapida

### Metodo 1: Script Automatico (Consigliato)

```bash
./configure_italian.sh
```

Lo script:
1. ✅ Configura variabili d'ambiente per l'italiano
2. ✅ Riavvia Open WebUI
3. ✅ Verifica configurazione

### Metodo 2: Manuale

Segui le sezioni dettagliate sotto.

---

## 🔧 Configurazione Backend (docker-compose.yml)

### Step 1: Modifica docker-compose.yml

Il file è già stato configurato con:

```yaml
environment:
  - DEFAULT_LOCALE=it-IT          # Lingua italiana
  - WEBUI_NAME=Open WebUI         # Nome applicazione
  - DEFAULT_MODELS=               # Modelli predefiniti
  - ENABLE_SIGNUP=true            # Abilita registrazione
```

**Variabili d'ambiente disponibili:**

| Variabile | Valore | Descrizione |
|-----------|--------|-------------|
| `DEFAULT_LOCALE` | `it-IT` | Imposta italiano come lingua predefinita |
| `WEBUI_NAME` | `Open WebUI` | Nome mostrato nell'interfaccia |
| `DEFAULT_MODELS` | (vuoto) | Modelli preselezionati alla prima chat |
| `ENABLE_SIGNUP` | `true/false` | Abilita/disabilita registrazione nuovi utenti |

### Step 2: Riavvia Open WebUI

```bash
docker-compose down
docker-compose up -d
```

Attendi 10-15 secondi per il riavvio completo.

---

## 🎨 Configurazione Interfaccia Utente

Dopo il riavvio, configura l'interfaccia dall'interno di Open WebUI:

### 1. Accedi a Open WebUI

`http://localhost:3000`

### 2. Vai alle Impostazioni

Clicca sull'icona del tuo profilo (in alto a destra) → **Impostazioni**

### 3. Configura Lingua

**Settings** → **Interface** → **Language**

Seleziona: **Italiano (Italian)**

### 4. Configura Sistema Prompt (Suggerimenti)

**Settings** → **Personalization** → **System Prompt**

Inserisci questo prompt per risposte sempre in italiano:

```
Sei un assistente AI utile e cordiale. Rispondi SEMPRE in italiano,
indipendentemente dalla lingua della domanda. Fornisci risposte
chiare, dettagliate e ben strutturate. Usa un tono professionale
ma amichevole. Se non conosci la risposta a una domanda, ammettilo
onestamente invece di inventare informazioni.
```

**Opzionale - Prompt Avanzato:**

```
Sei un assistente AI esperto che comunica esclusivamente in italiano.

REGOLE FONDAMENTALI:
1. Rispondi SEMPRE in italiano, anche se la domanda è in un'altra lingua
2. Usa un linguaggio chiaro e professionale
3. Struttura le risposte in modo ordinato (elenchi puntati, sezioni)
4. Fornisci esempi pratici quando appropriato
5. Ammetti quando non conosci qualcosa invece di inventare
6. Chiedi chiarimenti se la domanda è ambigua

STILE COMUNICAZIONE:
- Professionale ma amichevole
- Conciso ma completo
- Usa emoji quando aiutano la comprensione (es. ✅ ❌ 💡 ⚠️)
- Evita gergalismi eccessivi

FORMATO PREFERITO:
- Inizia con un riepilogo breve
- Usa intestazioni (##) per organizzare
- Codice in blocchi formattati
- Link e riferimenti quando utili
```

### 5. Applica Modifiche

Clicca **Save** (Salva)

---

## 🤖 Configurazione Modelli

### Impostare Modelli Predefiniti in Italiano

**Settings** → **Models** → **Default Model**

Seleziona un modello ottimizzato per l'italiano:

**Consigliati:**
- `mistral:7b-instruct` - Ottimo per italiano
- `qwen2.5:7b-instruct` - Buon supporto multilingue
- `gemma2:9b` - Eccellente per conversazioni in italiano

### Personalizzare Comportamento Modelli

Per ogni modello puoi impostare parametri personalizzati:

**Settings** → **Models** → Clicca sul modello → **Model Parameters**

**Parametri consigliati per risposte in italiano:**

```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40,
  "repeat_penalty": 1.1,
  "system": "Rispondi sempre in italiano. Usa un linguaggio chiaro e professionale."
}
```

---

## 📝 Personalizzazione Prompt per Funzioni

### Chat Titles (Titoli Chat)

**Settings** → **Personalization** → **Title Generation Prompt**

```
Genera un titolo breve (3-5 parole) in ITALIANO per questa conversazione
basandoti sul contenuto. Il titolo deve essere descrittivo e conciso.
```

### Search Query Generation

**Settings** → **Personalization** → **Search Query Generation Prompt**

```
Genera una query di ricerca efficace in ITALIANO basata sulla domanda dell'utente.
Estrai le parole chiave principali e formula una ricerca ottimizzata.
```

---

## 🎯 Configurazione Tools in Italiano

I tools personalizzati (come Scientific Council) rispettano già la lingua italiana.

Per verificare:

**Admin Panel** → **Functions** → **Tools** → Seleziona un tool → **Edit**

Verifica che i prompt interni usino l'italiano.

---

## 🌐 Impostazioni Avanzate

### Modifica Messaggi Sistema

**Admin Panel** → **Settings** → **System**

Personalizza messaggi mostrati agli utenti:

**Welcome Message:**
```
Benvenuto in Open WebUI!

Sono il tuo assistente AI personale. Posso aiutarti con:

✅ Rispondere a domande su qualsiasi argomento
✅ Scrivere e analizzare codice
✅ Creare contenuti creativi
✅ Risolvere problemi matematici
✅ Tradurre testi
✅ E molto altro!

Come posso aiutarti oggi?
```

**Empty Chat Message:**
```
👋 Ciao! Come posso aiutarti oggi?

Suggerimenti:
💡 Fai una domanda
📝 Chiedi di scrivere qualcosa
🔍 Cerca informazioni
💻 Analizza del codice
```

---

## 🔄 Configurazione Predefinita per Nuovi Utenti

Se vuoi che tutti i nuovi utenti abbiano l'italiano preimpostato:

**Admin Panel** → **Settings** → **Users** → **Default Settings**

```json
{
  "ui": {
    "language": "it-IT"
  },
  "models": {
    "default": "mistral:7b-instruct"
  }
}
```

---

## ✅ Verifica Configurazione

### Checklist

- [ ] `DEFAULT_LOCALE=it-IT` in docker-compose.yml
- [ ] Container riavviato
- [ ] Lingua interfaccia: Italiano
- [ ] System Prompt configurato in italiano
- [ ] Modello predefinito selezionato
- [ ] Messaggi di benvenuto personalizzati
- [ ] Test: chat risponde in italiano

### Test Rapido

1. Apri nuova chat
2. Scrivi: "Hello, how are you?"
3. La risposta dovrebbe essere in italiano: "Ciao! Sto bene, grazie..."

Se risponde in inglese, verifica lo System Prompt.

---

## 🛠️ Troubleshooting

### Problema: Interfaccia ancora in inglese

**Soluzione:**
1. Settings → Interface → Language → Italiano
2. Ricarica pagina (F5)
3. Se persiste: Pulisci cache browser (Ctrl+Shift+Del)

### Problema: Modelli rispondono in inglese

**Soluzione 1 - System Prompt:**
```
Settings → Personalization → System Prompt
Aggiungi: "Rispondi SEMPRE in italiano"
```

**Soluzione 2 - Modelfile personalizzato:**

Crea un modello custom con parametri italiani:

```bash
# Crea file: mistral-italiano.modelfile
FROM mistral:7b-instruct

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM """
Sei un assistente AI che risponde ESCLUSIVAMENTE in italiano.
Non importa la lingua della domanda, rispondi sempre in italiano.
Usa un linguaggio chiaro, professionale e amichevole.
"""
```

```bash
# Importa in Ollama
docker exec -it ollama ollama create mistral-italiano -f mistral-italiano.modelfile
```

Poi selezionalo in Open WebUI.

### Problema: Tools danno output in inglese

**Soluzione:**

Modifica i tools dall'Admin Panel:

1. Admin Panel → Functions → Tools
2. Seleziona il tool
3. Edit → Modifica i prompt interni in italiano
4. Save

---

## 📊 Configurazione Ottimale Consigliata

### docker-compose.yml

```yaml
environment:
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - WEBUI_SECRET_KEY=your-secret-key-change-this
  - DEFAULT_LOCALE=it-IT
  - WEBUI_NAME=Assistente AI
  - ENABLE_SIGNUP=false  # Se vuoi limitare accesso
```

### Settings → Personalization

**System Prompt:**
```
Sei un assistente AI italiano. Rispondi sempre in italiano con
un tono professionale e amichevole. Struttura le risposte in modo
chiaro usando elenchi, sezioni e esempi quando appropriato.
```

**Default Model:**
`mistral:7b-instruct` o `qwen2.5:7b-instruct`

**Temperature:** 0.7
**Top-p:** 0.9

---

## 🎁 Bonus: Frasi Predefinite (Shortcuts)

Crea scorciatoie per domande comuni in italiano:

**Settings** → **Personalization** → **Commands**

Aggiungi:

| Comando | Azione |
|---------|--------|
| `/riassumi` | Riassumi il testo seguente in italiano |
| `/traduci` | Traduci in italiano il seguente testo |
| `/spiega` | Spiegami in italiano e con esempi |
| `/codice` | Scrivi codice commentato in italiano |

---

## 📚 Risorse

- [Open WebUI Docs](https://docs.openwebui.com/)
- [Ollama Models](https://ollama.ai/library)
- [Guida Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

---

**Ultima modifica:** 2026-01-22
**Autore:** Carlo
**Versione:** 1.0.0
