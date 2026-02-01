"""
title: Assistente Codice
author: Carlo
version: 1.0.0
description: Strumento per analizzare, debuggare e spiegare codice in vari linguaggi
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def analizza_codice(
        self,
        codice: str = Field(..., description="Il codice sorgente da analizzare"),
        linguaggio: str = Field(default="auto", description="Linguaggio: python, javascript, java, c, cpp, rust, go, auto"),
    ) -> str:
        """
        Analizza un blocco di codice e fornisce una revisione dettagliata.
        """
        linee = codice.strip().split('\n')
        num_linee = len(linee)
        linee_vuote = sum(1 for l in linee if not l.strip())
        linee_commento = sum(1 for l in linee if l.strip().startswith(('#', '//', '/*', '*', '--')))

        return f"""🔍 **Analisi Codice**

**Statistiche:**
- Linee totali: {num_linee}
- Linee vuote: {linee_vuote}
- Linee commento: {linee_commento}
- Linee di codice: {num_linee - linee_vuote - linee_commento}
- Linguaggio: {linguaggio}

**Codice da analizzare:**
```{linguaggio if linguaggio != 'auto' else ''}
{codice}
```

---
**Richiesta di analisi:**
1. Identifica il linguaggio e lo scopo del codice
2. Verifica la correttezza sintattica
3. Cerca potenziali bug o problemi
4. Suggerisci miglioramenti per leggibilità
5. Valuta l'efficienza e le best practices
6. Identifica possibili vulnerabilità di sicurezza"""

    def debug_errore(
        self,
        codice: str = Field(..., description="Il codice che genera l'errore"),
        errore: str = Field(..., description="Il messaggio di errore ricevuto"),
        linguaggio: str = Field(default="auto", description="Linguaggio di programmazione"),
    ) -> str:
        """
        Aiuta a debuggare un errore nel codice.
        """
        return f"""🐛 **Debug Errore**

**Linguaggio:** {linguaggio}

**Messaggio di errore:**
```
{errore}
```

**Codice problematico:**
```{linguaggio if linguaggio != 'auto' else ''}
{codice}
```

---
**Richiesta di debug:**
1. Spiega cosa significa l'errore
2. Identifica la linea/causa del problema
3. Spiega perché si verifica
4. Fornisci il codice corretto
5. Suggerisci come prevenire errori simili"""

    def spiega_codice(
        self,
        codice: str = Field(..., description="Il codice da spiegare"),
        livello: str = Field(default="intermedio", description="Livello: principiante, intermedio, avanzato"),
    ) -> str:
        """
        Spiega cosa fa un blocco di codice in modo dettagliato.
        """
        dettaglio = {
            "principiante": "Spiega ogni concetto base, non dare nulla per scontato",
            "intermedio": "Spiega la logica generale e i punti chiave",
            "avanzato": "Focus su pattern, ottimizzazioni e dettagli tecnici"
        }

        return f"""📚 **Spiegazione Codice**

**Livello:** {livello}

**Codice:**
```
{codice}
```

---
**Richiesta:** {dettaglio.get(livello, dettaglio['intermedio'])}

Per favore spiega:
1. Cosa fa questo codice (panoramica)
2. Spiegazione linea per linea
3. Concetti chiave utilizzati
4. Input/Output attesi
5. Casi d'uso tipici"""

    def converti_linguaggio(
        self,
        codice: str = Field(..., description="Il codice sorgente da convertire"),
        da: str = Field(..., description="Linguaggio di partenza"),
        a: str = Field(..., description="Linguaggio di destinazione"),
    ) -> str:
        """
        Converte codice da un linguaggio di programmazione ad un altro.
        """
        return f"""🔄 **Conversione Codice**

**Da:** {da}
**A:** {a}

**Codice originale ({da}):**
```{da}
{codice}
```

---
**Richiesta:**
1. Converti il codice in {a}
2. Mantieni la stessa logica e funzionalità
3. Usa le convenzioni idiomatiche di {a}
4. Aggiungi commenti dove la sintassi differisce significativamente
5. Segnala funzionalità non direttamente traducibili"""

    def genera_codice(
        self,
        descrizione: str = Field(..., description="Descrizione di cosa deve fare il codice"),
        linguaggio: str = Field(default="python", description="Linguaggio in cui generare il codice"),
        con_commenti: bool = Field(default=True, description="Se includere commenti esplicativi"),
    ) -> str:
        """
        Genera codice a partire da una descrizione in linguaggio naturale.
        """
        commenti_str = "con commenti esplicativi" if con_commenti else "senza commenti"

        return f"""💻 **Generazione Codice**

**Linguaggio:** {linguaggio}
**Opzioni:** {commenti_str}

**Descrizione:**
{descrizione}

---
**Richiesta:**
1. Genera codice {linguaggio} funzionante
2. Segui le best practices del linguaggio
3. Usa nomi di variabili significativi
4. {"Aggiungi commenti per spiegare le parti importanti" if con_commenti else "Codice pulito senza commenti"}
5. Gestisci i casi limite principali
6. Fornisci un esempio di utilizzo"""

    def ottimizza_codice(
        self,
        codice: str = Field(..., description="Il codice da ottimizzare"),
        obiettivo: str = Field(default="performance", description="Obiettivo: performance, leggibilità, memoria, tutti"),
    ) -> str:
        """
        Suggerisce ottimizzazioni per il codice fornito.
        """
        obiettivi_desc = {
            "performance": "velocità di esecuzione",
            "leggibilità": "chiarezza e manutenibilità",
            "memoria": "utilizzo della memoria",
            "tutti": "tutti gli aspetti"
        }

        return f"""⚡ **Ottimizzazione Codice**

**Obiettivo:** {obiettivi_desc.get(obiettivo, 'tutti gli aspetti')}

**Codice attuale:**
```
{codice}
```

---
**Richiesta:**
1. Analizza le inefficienze attuali
2. Proponi ottimizzazioni per {obiettivi_desc.get(obiettivo, 'tutti gli aspetti')}
3. Mostra il codice ottimizzato
4. Spiega ogni modifica e il suo impatto
5. Indica i trade-off se presenti"""

    def genera_test(
        self,
        codice: str = Field(..., description="Il codice per cui generare i test"),
        framework: str = Field(default="auto", description="Framework di test: pytest, unittest, jest, mocha, auto"),
    ) -> str:
        """
        Genera test unitari per il codice fornito.
        """
        return f"""🧪 **Generazione Test**

**Framework:** {framework}

**Codice da testare:**
```
{codice}
```

---
**Richiesta:**
1. Identifica le funzioni/metodi da testare
2. Genera test per i casi normali
3. Aggiungi test per i casi limite (edge cases)
4. Includi test per la gestione errori
5. Usa asserzioni appropriate
6. Organizza i test in modo chiaro"""

    def documenta_codice(
        self,
        codice: str = Field(..., description="Il codice da documentare"),
        stile: str = Field(default="docstring", description="Stile: docstring, jsdoc, javadoc, markdown"),
    ) -> str:
        """
        Genera documentazione per il codice fornito.
        """
        return f"""📝 **Documentazione Codice**

**Stile:** {stile}

**Codice:**
```
{codice}
```

---
**Richiesta:**
1. Aggiungi documentazione in stile {stile}
2. Documenta parametri e tipi
3. Descrivi valori di ritorno
4. Aggiungi esempi d'uso
5. Nota eventuali eccezioni/errori
6. Restituisci il codice completo documentato"""

    def regex_helper(
        self,
        descrizione: str = Field(..., description="Descrizione di cosa deve matchare la regex"),
        esempi_validi: str = Field(default="", description="Esempi di stringhe che devono matchare"),
        esempi_invalidi: str = Field(default="", description="Esempi di stringhe che NON devono matchare"),
    ) -> str:
        """
        Aiuta a creare espressioni regolari (regex).
        """
        return f"""🔤 **Generatore Regex**

**Descrizione:**
{descrizione}

**Esempi che DEVONO matchare:**
{esempi_validi if esempi_validi else "(nessuno fornito)"}

**Esempi che NON devono matchare:**
{esempi_invalidi if esempi_invalidi else "(nessuno fornito)"}

---
**Richiesta:**
1. Crea la regex appropriata
2. Spiega ogni parte della regex
3. Fornisci esempi di utilizzo in Python e JavaScript
4. Testa con gli esempi forniti
5. Suggerisci varianti per casi simili"""
