# 🔍 Ricerca Web Intelligente - Open WebUI

## 📋 Panoramica

Questa guida spiega come configurare Open WebUI per utilizzare la ricerca web **solo quando strettamente necessario**, come ultima risorsa invece che come default.

---

## 🎯 Obiettivo

**PROBLEMA:** Se la ricerca web è sempre attiva, il modello cerca online anche per domande semplici, rallentando le risposte e consumando risorse inutilmente.

**SOLUZIONE:** Configurare il modello per usare la ricerca web solo in casi specifici:
- ⏱️ Eventi molto recenti (dopo gennaio 2025)
- 📊 Dati in tempo reale (meteo, borsa, notizie)
- 🔍 Argomenti fuori dalla conoscenza del modello
- 📚 Richiesta esplicita dell'utente

---

## ⚡ Configurazione Rapida

### Metodo Automatico (Consigliato)

```bash
./configure_smart_websearch.sh
```

Lo script creerà automaticamente il file `system_prompt_smart_search.txt` con le istruzioni ottimizzate.

### Applicazione Manuale

1. **Apri Open WebUI:** `http://localhost:3000`

2. **Vai in Settings:**
   Profilo → **Settings** → **Personalization** → **System Prompt**

3. **Copia il contenuto di:**
   ```
   /home/wildlux/Desktop/CARLO/ollama-webui/system_prompt_smart_search.txt
   ```

4. **Incolla nel campo System Prompt**

5. **Clicca Save**

---

## 🧠 Come Funziona

### Logica di Decisione

Il system prompt istruisce il modello a seguire questo flusso decisionale:

```
Domanda dell'utente
       ↓
Analizza argomento
       ↓
┌──────────────────────┐
│ Conosciuto?          │
│ Prima del 2025?      │
└──────────────────────┘
       ↓
   Sì  │  No
       ↓      ↓
  ✅ Usa     🔍 Valuta
  conoscenza    ricerca
  interna       web
       ↓           ↓
   Rispondi   Chiedi conferma
   subito     o cerca online
```

### Esempi Pratici

#### ✅ Usa Conoscenza Interna (NO ricerca web)

**Domanda:** "Chi era Leonardo da Vinci?"
**Decisione:** Conoscenza storica consolidata → Risposta diretta

**Domanda:** "Come funziona React?"
**Decisione:** Tecnologia conosciuta (fino a gen 2025) → Risposta + nota temporale

**Domanda:** "Spiega la teoria della relatività"
**Decisione:** Concetto scientifico → Risposta diretta

**Domanda:** "Scrivi codice Python per..."
**Decisione:** Programmazione generale → Risposta diretta

#### 🔍 Usa Ricerca Web (SÌ ricerca necessaria)

**Domanda:** "Che tempo farà domani a Roma?"
**Decisione:** Dati meteo in tempo reale → Ricerca web

**Domanda:** "Chi ha vinto le elezioni del 2025?"
**Decisione:** Evento dopo data di training → Ricerca web

**Domanda:** "Quanto costa Bitcoin adesso?"
**Decisione:** Prezzo in tempo reale → Ricerca web

**Domanda:** "Cerca online informazioni su..."
**Decisione:** Richiesta esplicita → Ricerca web

#### 💬 Chiede Conferma (Situazione ambigua)

**Domanda:** "Parlami dell'intelligenza artificiale"
**Risposta:** "Posso spiegarti l'IA basandomi sulla mia conoscenza (aggiornata a gennaio 2025). Vuoi che cerchi anche gli sviluppi più recenti online?"

---

## 🎨 Personalizzazione Prompt

### Modifica Soglia Temporale

Nel file `system_prompt_smart_search.txt`, trova:

```markdown
- Notizie dopo gennaio 2025
```

Cambia con la tua data preferita (es. giugno 2025):

```markdown
- Notizie dopo giugno 2025
```

### Aggiungi Eccezioni Specifiche

Puoi aggiungere argomenti che richiedono sempre ricerca web:

```markdown
### SEMPRE USA RICERCA WEB PER:
- Prezzi di prodotti specifici
- Informazioni su aziende locali
- Eventi sportivi live
- [Aggiungi qui altre eccezioni]
```

### Cambia Comportamento Default

**Più conservativo (meno ricerca web):**
```markdown
### REGOLA: Usa SOLO conoscenza interna a meno che esplicitamente richiesto
```

**Più liberale (più ricerca web):**
```markdown
### REGOLA: Valuta sempre se informazioni più recenti potrebbero essere utili
```

---

## 🔧 Configurazioni Avanzate

### Disabilitare Completamente la Ricerca Web

Se vuoi che il modello NON usi MAI la ricerca web automaticamente:

**Settings → Admin → Functions**

Disattiva tutti i tools di web search.

Poi nel System Prompt:

```markdown
NON usare mai la ricerca web automaticamente.
Se servono informazioni aggiornate, suggerisci all'utente di cercarle manualmente.
```

### Abilitare Ricerca Web Solo per Argomenti Specifici

```markdown
USA RICERCA WEB SOLO PER:
1. Notizie italiane recenti
2. Meteo e condizioni ambientali
3. Eventi sportivi Serie A

Per tutto il resto, usa conoscenza interna.
```

### Creare Profili Multipli

Puoi salvare diversi system prompts per diverse situazioni:

**Profilo "Ricerca Aggressiva":**
- Usa ricerca web frequentemente
- Controlla sempre fonti recenti

**Profilo "Solo Locale":**
- Mai ricerca web
- Solo conoscenza interna

**Profilo "Bilanciato":** (quello creato dallo script)
- Ricerca web quando necessario

Cambia profilo copiando il prompt appropriato in Settings.

---

## 📊 Monitoraggio Utilizzo

### Verifica Quanto Usa la Ricerca Web

Osserva le risposte del modello:

**Usa ricerca web se vedi:**
- "Ho cercato online..."
- "Secondo fonti recenti..."
- Link a siti web nelle risposte

**Usa conoscenza interna se:**
- Risposta diretta senza citazioni
- "Basandomi sulla mia conoscenza..."
- No link esterni

### Log delle Ricerche (Admin)

**Admin Panel → Logs**

Controlla quante volte viene chiamato il tool di web search.

Se troppo frequente → Rendi il prompt più conservativo
Se mai usato quando serve → Rendi il prompt più liberale

---

## 🎯 Best Practices

### ✅ DO (Fai)

1. **Mantieni prompt chiaro e specifico**
   - Elenca casi d'uso precisi
   - Usa esempi concreti

2. **Aggiorna data di cutoff**
   - Se cambi modello, aggiorna la data nel prompt
   - Esempio: "conoscenza fino a giugno 2025"

3. **Testa con domande tipo**
   - "Chi era Einstein?" → NO web search
   - "Meteo domani?" → SÌ web search

4. **Rivedi periodicamente**
   - Ogni mese, aggiorna se necessario
   - Aggiungi eccezioni scoperte

### ❌ DON'T (Non fare)

1. **Non rendere il prompt troppo restrittivo**
   - Il modello potrebbe rifiutare ricerche legittime

2. **Non dimenticare casi limite**
   - Eventi storici recenti (es. pandemia)
   - Tecnologie nuove ma già consolidate

3. **Non sovraccaricare di regole**
   - Troppi dettagli confondono il modello
   - Mantieni semplice e chiaro

---

## 🔍 Troubleshooting

### Problema: Il modello cerca online troppo spesso

**Soluzione 1:** Rendi il prompt più conservativo

Cambia:
```markdown
### REGOLA PRINCIPALE: Usa la ricerca web SOLO quando strettamente necessario
```

In:
```markdown
### REGOLA PRINCIPALE: Usa SOLO conoscenza interna. Ricerca web RARISSIMA ECCEZIONE.
```

**Soluzione 2:** Aggiungi esempi negativi

```markdown
### NON USARE RICERCA WEB PER:
- Domande generali sulla storia
- Spiegazioni scientifiche di base
- Tutorial di programmazione
- Matematica e logica
- Analisi di testi forniti dall'utente
```

### Problema: Il modello non cerca mai online quando serve

**Soluzione 1:** Verifica che i tools di web search siano attivi

**Admin Panel → Functions → Tools**

Assicurati che almeno un tool di web search sia abilitato.

**Soluzione 2:** Rendi espliciti i trigger

```markdown
### USA RICERCA WEB IMMEDIATAMENTE SE:
- Domanda contiene "oggi", "ieri", "adesso", "attualmente"
- Richiesta di dati in tempo reale
- Menzione esplicita di date post-2025
```

### Problema: Risposte inconsistenti

Il modello a volte cerca online, a volte no per la stessa domanda.

**Soluzione:** Usa parametri modello più deterministici

**Settings → Models → [Modello] → Parameters**

```json
{
  "temperature": 0.3,
  "top_p": 0.85
}
```

Temperature più bassa = comportamento più consistente

---

## 📚 Risorse Aggiuntive

### File Correlati

- `system_prompt_smart_search.txt` - Prompt generato dallo script
- `configure_smart_websearch.sh` - Script di configurazione
- `CONFIGURAZIONE_ITALIANO.md` - Guida completa italiano

### Link Utili

- [Open WebUI System Prompts](https://docs.openwebui.com/)
- [RAG e Web Search](https://docs.openwebui.com/features/web-search)

---

## 💡 Esempi Avanzati

### Caso Studio: Assistente Ricerca Scientifica

**Scenario:** Vuoi un assistente che usi sempre fonti recenti per paper scientifici

```markdown
Per domande su ricerca scientifica pubblicata dopo gennaio 2025:
1. Cerca SEMPRE su arXiv, PubMed, Google Scholar
2. Cita DOI e autori
3. Indica data di pubblicazione

Per concetti scientifici consolidati:
- Usa conoscenza interna
- Menziona solo eventuali sviluppi recenti
```

### Caso Studio: Assistente Notizie Italiane

**Scenario:** Focus su notizie italiane aggiornate

```markdown
Per domande su:
- Politica italiana corrente → Ricerca web obbligatoria
- Cronaca recente → Ricerca web obbligatoria
- Economia italiana → Ricerca web se dati < 1 mese

Per:
- Storia italiana → Conoscenza interna
- Geografia → Conoscenza interna
- Cultura → Conoscenza interna + optional web search per eventi
```

---

## ✅ Checklist Configurazione

- [ ] Script eseguito: `./configure_smart_websearch.sh`
- [ ] File generato: `system_prompt_smart_search.txt`
- [ ] Prompt copiato in Open WebUI Settings
- [ ] System Prompt salvato
- [ ] Test con domanda semplice (no web search)
- [ ] Test con richiesta tempo reale (sì web search)
- [ ] Verifica comportamento soddisfacente
- [ ] Documentazione letta e compresa

---

**Ultima modifica:** 2026-01-22
**Autore:** Carlo
**Versione:** 1.0.0
