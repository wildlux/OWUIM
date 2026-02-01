"""
title: Assistente Studio
author: Carlo
version: 1.0.0
description: Strumento per studiare, memorizzare e prepararsi agli esami
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def crea_riassunto(
        self,
        argomento: str = Field(..., description="L'argomento o il testo da riassumere"),
        materia: str = Field(default="", description="Materia scolastica (storia, scienze, ecc.)"),
        livello: str = Field(default="superiori", description="Livello: medie, superiori, università"),
    ) -> str:
        """
        Crea un riassunto strutturato per lo studio.
        """
        return f"""📝 **Riassunto per lo Studio**

**Argomento:** {argomento}
**Materia:** {materia if materia else "(generale)"}
**Livello:** {livello}

---
**Crea un riassunto strutturato:**

1. **Concetti chiave**
   - Definizioni essenziali
   - Punti fondamentali

2. **Sviluppo**
   - Spiegazione dei concetti
   - Collegamenti logici
   - Esempi pratici

3. **Schema riassuntivo**
   - Punti elenco dei concetti principali
   - Facilmente memorizzabili

4. **Date/Formule/Dati importanti**
   - Elementi da ricordare a memoria

5. **Domande di verifica**
   - 3-5 domande per verificare la comprensione"""

    def genera_flashcard(
        self,
        argomento: str = Field(..., description="Argomento per cui creare le flashcard"),
        numero: int = Field(default=10, description="Numero di flashcard da generare"),
        difficolta: str = Field(default="media", description="Difficoltà: facile, media, difficile"),
    ) -> str:
        """
        Genera flashcard per la memorizzazione.
        """
        return f"""🎴 **Flashcard - {argomento}**

**Numero:** {numero}
**Difficoltà:** {difficolta}

---
**Genera {numero} flashcard nel formato:**

**Flashcard 1**
- 🔵 **Domanda:** [domanda]
- 🟢 **Risposta:** [risposta concisa]

**Flashcard 2**
- 🔵 **Domanda:** [domanda]
- 🟢 **Risposta:** [risposta concisa]

[continua...]

Le domande devono:
- Essere chiare e specifiche
- Avere risposte brevi e memorizzabili
- Coprire i concetti chiave dell'argomento
- Essere ordinate dal più semplice al più complesso"""

    def spiega_concetto(
        self,
        concetto: str = Field(..., description="Il concetto da spiegare"),
        livello: str = Field(default="superiori", description="Livello: elementari, medie, superiori, università"),
        con_esempi: bool = Field(default=True, description="Se includere esempi pratici"),
    ) -> str:
        """
        Spiega un concetto in modo chiaro e adatto al livello specificato.
        """
        esempi_str = "Includi esempi pratici e della vita quotidiana." if con_esempi else ""

        return f"""💡 **Spiegazione Concetto**

**Concetto:** {concetto}
**Livello:** {livello}

---
**Spiega questo concetto in modo:**

1. **Definizione semplice**
   - Cos'è in una frase

2. **Spiegazione dettagliata**
   - Approfondimento adatto al livello {livello}
   - Usa un linguaggio appropriato

3. **Come funziona**
   - Meccanismo o processo
   - Cause ed effetti

4. {"**Esempi pratici**" if con_esempi else "**Applicazioni**"}
   - {esempi_str if con_esempi else "Dove si applica questo concetto"}

5. **Collegamento con altri concetti**
   - Relazioni con argomenti correlati

6. **Errori comuni**
   - Misconcezioni da evitare"""

    def prepara_esame(
        self,
        materia: str = Field(..., description="Materia dell'esame"),
        argomenti: str = Field(..., description="Lista degli argomenti da studiare"),
        giorni: int = Field(default=7, description="Giorni disponibili per studiare"),
    ) -> str:
        """
        Crea un piano di studio per preparare un esame.
        """
        return f"""📅 **Piano di Studio per Esame**

**Materia:** {materia}
**Argomenti:** {argomenti}
**Giorni disponibili:** {giorni}

---
**Crea un piano di studio che includa:**

1. **Analisi degli argomenti**
   - Suddivisione per importanza
   - Stima del tempo necessario per ciascuno

2. **Calendario giornaliero**
   - Distribuzione degli argomenti sui {giorni} giorni
   - Sessioni di studio consigliate
   - Pause e ripasso

3. **Priorità**
   - Argomenti fondamentali (da sapere assolutamente)
   - Argomenti importanti
   - Argomenti di approfondimento

4. **Tecniche consigliate**
   - Metodi di studio per questa materia
   - Strategie di memorizzazione

5. **Ripasso finale**
   - Come organizzare l'ultimo giorno
   - Checklist pre-esame

6. **Simulazione**
   - Domande probabili
   - Esercizi tipo"""

    def quiz_verifica(
        self,
        argomento: str = Field(..., description="Argomento del quiz"),
        tipo: str = Field(default="misto", description="Tipo: scelta_multipla, vero_falso, aperte, misto"),
        numero: int = Field(default=10, description="Numero di domande"),
    ) -> str:
        """
        Genera un quiz di verifica con domande e risposte.
        """
        return f"""❓ **Quiz di Verifica**

**Argomento:** {argomento}
**Tipo domande:** {tipo}
**Numero:** {numero}

---
**Genera un quiz con {numero} domande:**

**Formato per ogni domanda:**

**Domanda X** [{tipo}]
[Testo della domanda]

{"A) ... B) ... C) ... D) ..." if tipo in ["scelta_multipla", "misto"] else ""}

**✓ Risposta corretta:** [risposta]
**📖 Spiegazione:** [breve spiegazione del perché]

---

Le domande devono:
- Coprire diversi aspetti dell'argomento
- Avere difficoltà crescente
- Testare comprensione, non solo memoria
- Avere spiegazioni utili per l'apprendimento"""

    def mappa_mentale(
        self,
        argomento: str = Field(..., description="Argomento centrale della mappa"),
        materia: str = Field(default="", description="Materia di riferimento"),
    ) -> str:
        """
        Crea una mappa mentale testuale per un argomento.
        """
        return f"""🗺️ **Mappa Mentale**

**Argomento centrale:** {argomento}
**Materia:** {materia if materia else "(generale)"}

---
**Crea una mappa mentale strutturata:**

```
                    ┌─────────────────┐
                    │   {argomento[:15]}...   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   [Ramo 1]             [Ramo 2]             [Ramo 3]
        │                    │                    │
   ├─ sotto1            ├─ sotto1            ├─ sotto1
   ├─ sotto2            ├─ sotto2            ├─ sotto2
   └─ sotto3            └─ sotto3            └─ sotto3
```

**Legenda:**
- 🔴 Concetti fondamentali
- 🟡 Concetti importanti
- 🟢 Dettagli e approfondimenti
- ↔️ Collegamenti tra rami

Sviluppa la mappa con tutti i rami e sotto-rami rilevanti."""

    def confronta_argomenti(
        self,
        argomento1: str = Field(..., description="Primo argomento"),
        argomento2: str = Field(..., description="Secondo argomento"),
        aspetti: str = Field(default="tutti", description="Aspetti da confrontare"),
    ) -> str:
        """
        Confronta due argomenti evidenziando somiglianze e differenze.
        """
        return f"""⚖️ **Confronto**

**Argomento 1:** {argomento1}
**Argomento 2:** {argomento2}
**Aspetti:** {aspetti}

---
**Tabella comparativa:**

| Aspetto | {argomento1[:20]} | {argomento2[:20]} |
|---------|---------|---------|
| Definizione | ... | ... |
| Caratteristiche | ... | ... |
| Vantaggi | ... | ... |
| Svantaggi | ... | ... |
| Applicazioni | ... | ... |

**Somiglianze:**
- ...

**Differenze:**
- ...

**Conclusioni:**
- Quando preferire uno o l'altro
- Complementarietà"""

    def traduci_spiega(
        self,
        testo: str = Field(..., description="Testo in lingua straniera"),
        lingua: str = Field(default="inglese", description="Lingua del testo"),
        livello: str = Field(default="intermedio", description="Livello: principiante, intermedio, avanzato"),
    ) -> str:
        """
        Traduce un testo e spiega la grammatica e il vocabolario.
        """
        return f"""🌍 **Traduzione e Analisi**

**Lingua:** {lingua}
**Livello:** {livello}

**Testo originale:**
{testo}

---
**Richiesta:**

1. **Traduzione**
   - Traduzione accurata in italiano

2. **Vocabolario**
   - Parole chiave con significato
   - Espressioni idiomatiche

3. **Grammatica**
   - Strutture grammaticali presenti
   - Tempi verbali usati
   - Costruzioni particolari

4. **Note linguistiche**
   - Livello di formalità
   - Varianti regionali (se presenti)

5. **Esercizio**
   - Suggerimento per praticare le strutture viste"""

    def esercizio_pratico(
        self,
        argomento: str = Field(..., description="Argomento dell'esercizio"),
        tipo: str = Field(default="problema", description="Tipo: problema, esercizio, caso_studio"),
        difficolta: str = Field(default="media", description="Difficoltà: facile, media, difficile"),
    ) -> str:
        """
        Genera esercizi pratici con soluzione guidata.
        """
        return f"""✏️ **Esercizio Pratico**

**Argomento:** {argomento}
**Tipo:** {tipo}
**Difficoltà:** {difficolta}

---
**Genera un {tipo} che:**

1. **Testo dell'esercizio**
   - Problema chiaro e completo
   - Tutti i dati necessari

2. **Suggerimenti**
   - Hint per iniziare (senza rivelare la soluzione)
   - Formule o concetti da utilizzare

3. **Soluzione guidata**
   - Passaggio 1: ...
   - Passaggio 2: ...
   - Passaggio N: ...

4. **Risultato finale**
   - Risposta corretta
   - Unità di misura (se applicabile)

5. **Verifica**
   - Come controllare se la soluzione è corretta

6. **Variante**
   - Un esercizio simile per ulteriore pratica"""
