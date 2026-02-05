"""
title: Assistente Ricerca
author: Carlo
version: 1.0.0
description: Strumento per ricerche, analisi di informazioni e fact-checking
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def ricerca_argomento(
        self,
        argomento: str = Field(..., description="L'argomento da ricercare"),
        profondita: str = Field(default="media", description="Profondità: panoramica, media, approfondita"),
        focus: str = Field(default="generale", description="Focus specifico (opzionale)"),
    ) -> str:
        """
        Esegue una ricerca approfondita su un argomento.
        """
        profondita_desc = {
            "panoramica": "overview generale, concetti chiave",
            "media": "spiegazione dettagliata con esempi",
            "approfondita": "analisi completa con fonti e dettagli tecnici"
        }

        return f"""🔍 **Ricerca: {argomento}**

**Profondità:** {profondita} ({profondita_desc.get(profondita, '')})
**Focus:** {focus if focus != "generale" else "tutti gli aspetti"}

---
**Fornisci una ricerca che includa:**

1. **Definizione e introduzione**
   - Cos'è / Di cosa si tratta
   - Contesto generale

2. **Storia e background**
   - Origini e sviluppo
   - Evoluzione nel tempo

3. **Aspetti principali**
   - Caratteristiche chiave
   - Componenti/elementi fondamentali

4. **Stato attuale**
   - Situazione presente
   - Sviluppi recenti

5. **Prospettive future**
   - Tendenze
   - Previsioni

6. **Pro e contro / Controversie**
   - Dibattiti esistenti
   - Diverse prospettive

7. **Riferimenti**
   - Fonti autorevoli da consultare
   - Esperti nel campo"""

    def confronta_opzioni(
        self,
        opzione1: str = Field(..., description="Prima opzione da confrontare"),
        opzione2: str = Field(..., description="Seconda opzione da confrontare"),
        opzione3: str = Field(default="", description="Terza opzione (opzionale)"),
        criteri: str = Field(default="", description="Criteri specifici di confronto"),
    ) -> str:
        """
        Confronta diverse opzioni in modo oggettivo.
        """
        opzioni = [opzione1, opzione2]
        if opzione3:
            opzioni.append(opzione3)

        criteri_str = f"\n**Criteri specifici:** {criteri}" if criteri else ""

        return f"""⚖️ **Confronto Opzioni**

**Opzioni:** {', '.join(opzioni)}{criteri_str}

---
**Analisi comparativa:**

1. **Panoramica**
   - Breve descrizione di ogni opzione

2. **Tabella comparativa**

| Criterio | {opzione1} | {opzione2} |{f' {opzione3} |' if opzione3 else ''}
|----------|------------|------------|{'-----------' if opzione3 else ''}
| ... | ... | ... |{' ... |' if opzione3 else ''}

3. **Pro e Contro per ciascuna opzione**

4. **Analisi costi/benefici**

5. **Casi d'uso ideali**
   - Quando scegliere ciascuna opzione

6. **Raccomandazione**
   - Consiglio basato sui criteri forniti"""

    def analizza_problema(
        self,
        problema: str = Field(..., description="Il problema da analizzare"),
        contesto: str = Field(default="", description="Contesto aggiuntivo"),
    ) -> str:
        """
        Analizza un problema in modo strutturato e propone soluzioni.
        """
        contesto_str = f"\n**Contesto:** {contesto}" if contesto else ""

        return f"""🎯 **Analisi Problema**

**Problema:** {problema}{contesto_str}

---
**Analisi strutturata:**

1. **Definizione del problema**
   - Cosa esattamente non funziona/manca
   - Impatto del problema

2. **Cause radice**
   - Analisi delle cause (5 Whys)
   - Fattori contribuenti

3. **Stakeholder coinvolti**
   - Chi è interessato
   - Interessi diversi

4. **Vincoli**
   - Limitazioni da considerare
   - Risorse disponibili

5. **Soluzioni possibili**
   - Opzione A: ...
   - Opzione B: ...
   - Opzione C: ...

6. **Valutazione soluzioni**
   - Pro/contro di ciascuna
   - Fattibilità

7. **Raccomandazione**
   - Soluzione consigliata
   - Piano d'azione"""

    def fact_check(
        self,
        affermazione: str = Field(..., description="L'affermazione da verificare"),
        fonte: str = Field(default="", description="Fonte dell'affermazione (se nota)"),
    ) -> str:
        """
        Verifica la veridicità di un'affermazione.
        """
        fonte_str = f"\n**Fonte dichiarata:** {fonte}" if fonte else ""

        return f"""✓ **Fact Check**

**Affermazione:** "{affermazione}"{fonte_str}

---
**Verifica:**

1. **Classificazione**
   - ✅ VERO / ⚠️ PARZIALMENTE VERO / ❌ FALSO / ❓ NON VERIFICABILE

2. **Analisi dell'affermazione**
   - Cosa viene sostenuto esattamente
   - Elementi verificabili

3. **Evidenze**
   - Dati e fatti a supporto o contro
   - Fonti autorevoli

4. **Contesto**
   - Informazioni mancanti
   - Sfumature importanti

5. **Conclusione**
   - Verdetto finale con motivazione

6. **Fonti consigliate**
   - Dove approfondire"""

    def crea_bibliografia(
        self,
        argomento: str = Field(..., description="Argomento della ricerca"),
        tipo: str = Field(default="accademico", description="Tipo: accademico, divulgativo, misto"),
        formato: str = Field(default="APA", description="Formato: APA, MLA, Chicago, Harvard"),
    ) -> str:
        """
        Suggerisce una bibliografia ragionata su un argomento.
        """
        return f"""📚 **Bibliografia Ragionata**

**Argomento:** {argomento}
**Tipo fonti:** {tipo}
**Formato citazione:** {formato}

---
**Genera una bibliografia che includa:**

1. **Testi fondamentali**
   - Opere classiche/di riferimento sull'argomento
   - Citazione completa in formato {formato}
   - Breve descrizione del contributo

2. **Pubblicazioni recenti**
   - Ricerche e studi aggiornati
   - Citazione + descrizione

3. **Risorse online**
   - Siti web autorevoli
   - Database e archivi

4. **Altre risorse**
   - Documentari
   - Podcast/video educativi
   - Conferenze

**Per ogni fonte indica:**
- Citazione formattata
- Tipo di risorsa
- Rilevanza per la ricerca
- Livello di difficoltà"""

    def analizza_dati(
        self,
        dati: str = Field(..., description="I dati da analizzare (testo, numeri, statistiche)"),
        obiettivo: str = Field(default="comprensione", description="Obiettivo: comprensione, trend, anomalie, previsioni"),
    ) -> str:
        """
        Analizza dati e informazioni fornite.
        """
        return f"""📊 **Analisi Dati**

**Obiettivo:** {obiettivo}

**Dati forniti:**
{dati}

---
**Analisi:**

1. **Panoramica**
   - Cosa rappresentano i dati
   - Formato e struttura

2. **Statistiche descrittive**
   - Valori chiave
   - Medie, mediane, range (se applicabile)

3. **Pattern e trend**
   - Tendenze identificate
   - Correlazioni

4. **Anomalie**
   - Valori fuori norma
   - Dati mancanti o incoerenti

5. **Interpretazione**
   - Cosa significano i dati
   - Implicazioni

6. **Visualizzazione consigliata**
   - Tipo di grafico suggerito
   - Elementi da evidenziare

7. **Conclusioni e raccomandazioni**"""

    def genera_domande(
        self,
        argomento: str = Field(..., description="Argomento su cui generare domande"),
        tipo: str = Field(default="esplorative", description="Tipo: esplorative, critiche, intervista, sondaggio"),
        numero: int = Field(default=10, description="Numero di domande"),
    ) -> str:
        """
        Genera domande per esplorare o approfondire un argomento.
        """
        tipi_desc = {
            "esplorative": "per capire e scoprire",
            "critiche": "per analizzare e valutare",
            "intervista": "per un'intervista strutturata",
            "sondaggio": "per raccogliere opinioni"
        }

        return f"""❓ **Generazione Domande**

**Argomento:** {argomento}
**Tipo:** {tipo} ({tipi_desc.get(tipo, '')})
**Numero:** {numero}

---
**Genera {numero} domande {tipo}:**

Per ogni domanda indica:
1. La domanda
2. Perché è importante/utile
3. Possibili follow-up

Organizza le domande in ordine logico:
- Dal generale allo specifico
- Dal semplice al complesso

Include domande che:
- Esplorino fatti
- Indaghino opinioni
- Stimolino riflessioni
- Colleghino ad altri temi"""

    def sintetizza_fonti(
        self,
        fonte1: str = Field(..., description="Prima fonte/testo"),
        fonte2: str = Field(..., description="Seconda fonte/testo"),
        fonte3: str = Field(default="", description="Terza fonte (opzionale)"),
        obiettivo: str = Field(default="", description="Obiettivo della sintesi"),
    ) -> str:
        """
        Sintetizza e confronta informazioni da più fonti.
        """
        fonti = [fonte1, fonte2]
        if fonte3:
            fonti.append(fonte3)

        return f"""📑 **Sintesi Multi-Fonte**

**Numero fonti:** {len(fonti)}
**Obiettivo:** {obiettivo if obiettivo else "sintesi generale"}

**Fonte 1:**
{fonte1}

**Fonte 2:**
{fonte2}
{"**Fonte 3:**" + chr(10) + fonte3 if fonte3 else ""}

---
**Sintesi:**

1. **Punti di accordo**
   - Elementi su cui le fonti concordano

2. **Punti di disaccordo**
   - Elementi contrastanti
   - Diverse interpretazioni

3. **Informazioni esclusive**
   - Cosa aggiunge ciascuna fonte

4. **Lacune**
   - Cosa non è coperto

5. **Sintesi integrata**
   - Visione d'insieme che integra tutte le fonti

6. **Valutazione**
   - Affidabilità delle fonti
   - Eventuali bias"""

    def spiega_come(
        self,
        cosa: str = Field(..., description="Cosa si vuole imparare a fare"),
        livello: str = Field(default="principiante", description="Livello: principiante, intermedio, esperto"),
        contesto: str = Field(default="", description="Contesto specifico"),
    ) -> str:
        """
        Spiega come fare qualcosa passo per passo.
        """
        contesto_str = f"\n**Contesto:** {contesto}" if contesto else ""

        return f"""📖 **Guida: Come {cosa}**

**Livello:** {livello}{contesto_str}

---
**Guida passo-passo:**

1. **Prerequisiti**
   - Cosa serve prima di iniziare
   - Conoscenze necessarie

2. **Materiali/Strumenti**
   - Lista di cosa occorre

3. **Procedura**
   - **Passo 1:** ...
   - **Passo 2:** ...
   - [continua...]

4. **Consigli pratici**
   - Tips per fare meglio
   - Errori comuni da evitare

5. **Troubleshooting**
   - Problemi frequenti e soluzioni

6. **Approfondimenti**
   - Risorse per imparare di più
   - Varianti avanzate"""
