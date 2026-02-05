"""
title: Assistente Libri
author: Carlo
version: 1.0.0
description: Strumento per analisi, riassunti e studio di libri e testi letterari
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def analizza_libro(
        self,
        titolo: str = Field(..., description="Titolo del libro"),
        autore: str = Field(default="", description="Autore del libro"),
        genere: str = Field(default="", description="Genere letterario"),
    ) -> str:
        """
        Fornisce un'analisi completa di un libro conosciuto.
        """
        return f"""📖 **Analisi Libro**

**Titolo:** {titolo}
**Autore:** {autore if autore else "(da identificare)"}
**Genere:** {genere if genere else "(da identificare)"}

---
**Richiesta di analisi completa:**

1. **Informazioni generali**
   - Anno di pubblicazione
   - Contesto storico-culturale
   - Movimento letterario

2. **Trama**
   - Sinossi (senza spoiler importanti)
   - Struttura narrativa

3. **Personaggi principali**
   - Caratteristiche e ruoli
   - Evoluzione nel corso della storia

4. **Temi principali**
   - Tematiche affrontate
   - Messaggi dell'autore

5. **Stile e tecniche narrative**
   - Punto di vista
   - Linguaggio e registro
   - Tecniche particolari

6. **Significato e interpretazioni**
   - Chiavi di lettura
   - Rilevanza contemporanea"""

    def riassumi_capitolo(
        self,
        libro: str = Field(..., description="Titolo del libro"),
        capitolo: str = Field(..., description="Numero o titolo del capitolo"),
        dettaglio: str = Field(default="medio", description="Livello: breve, medio, dettagliato"),
    ) -> str:
        """
        Genera il riassunto di un capitolo specifico.
        """
        lunghezze = {
            "breve": "50-100 parole, solo eventi chiave",
            "medio": "150-250 parole, eventi e dettagli importanti",
            "dettagliato": "300-500 parole, analisi approfondita"
        }

        return f"""📑 **Riassunto Capitolo**

**Libro:** {libro}
**Capitolo:** {capitolo}
**Dettaglio:** {dettaglio} ({lunghezze.get(dettaglio, lunghezze['medio'])})

---
**Richiesta:**
1. Riassumi gli eventi principali del capitolo
2. Identifica i personaggi coinvolti
3. Evidenzia i momenti chiave
4. Nota eventuali simbolismi o elementi importanti
5. Collega agli eventi precedenti/successivi"""

    def analizza_personaggio(
        self,
        personaggio: str = Field(..., description="Nome del personaggio"),
        libro: str = Field(..., description="Titolo del libro"),
    ) -> str:
        """
        Analizza in profondità un personaggio letterario.
        """
        return f"""👤 **Analisi Personaggio**

**Personaggio:** {personaggio}
**Opera:** {libro}

---
**Richiesta di analisi:**

1. **Presentazione**
   - Chi è il personaggio
   - Ruolo nella storia (protagonista, antagonista, ecc.)

2. **Caratteristiche**
   - Aspetto fisico (se descritto)
   - Tratti psicologici
   - Background e storia personale

3. **Relazioni**
   - Rapporti con altri personaggi
   - Dinamiche familiari/sociali

4. **Evoluzione**
   - Arco narrativo del personaggio
   - Cambiamenti nel corso della storia
   - Momenti di svolta

5. **Simbolismo**
   - Cosa rappresenta il personaggio
   - Valori o idee incarnate

6. **Citazioni significative**
   - Frasi memorabili del/sul personaggio"""

    def confronta_libri(
        self,
        libro1: str = Field(..., description="Primo libro da confrontare"),
        libro2: str = Field(..., description="Secondo libro da confrontare"),
        aspetto: str = Field(default="generale", description="Aspetto: generale, temi, stile, personaggi, struttura"),
    ) -> str:
        """
        Confronta due libri evidenziando somiglianze e differenze.
        """
        return f"""⚖️ **Confronto Libri**

**Libro 1:** {libro1}
**Libro 2:** {libro2}
**Focus:** {aspetto}

---
**Richiesta di confronto:**

1. **Contesto**
   - Epoca e luogo di scrittura
   - Genere letterario

2. **Somiglianze**
   - Elementi comuni
   - Temi condivisi

3. **Differenze**
   - Approcci diversi
   - Stili narrativi

4. **Analisi comparativa su: {aspetto}**
   - Approfondimento specifico
   - Punti di forza di ciascuno

5. **Conclusioni**
   - Quale leggere per quale scopo
   - Complementarietà delle opere"""

    def genera_scheda_libro(
        self,
        titolo: str = Field(..., description="Titolo del libro"),
        scopo: str = Field(default="studio", description="Scopo: studio, recensione, presentazione, esame"),
    ) -> str:
        """
        Genera una scheda libro completa per lo scopo specificato.
        """
        return f"""📋 **Scheda Libro**

**Titolo:** {titolo}
**Scopo:** {scopo}

---
**Genera una scheda completa contenente:**

1. **Dati bibliografici**
   - Titolo completo
   - Autore
   - Casa editrice e anno
   - Genere

2. **L'autore**
   - Biografia essenziale
   - Altre opere importanti
   - Contesto storico

3. **Contenuto**
   - Trama (riassunto)
   - Ambientazione
   - Personaggi principali

4. **Analisi**
   - Temi trattati
   - Stile narrativo
   - Messaggio dell'opera

5. **Valutazione critica**
   - Punti di forza
   - Eventuali criticità
   - Pubblico consigliato

6. **Citazioni significative**
   - 2-3 passaggi memorabili"""

    def suggerisci_libri(
        self,
        genere: str = Field(default="", description="Genere preferito"),
        libro_piaciuto: str = Field(default="", description="Un libro che ti è piaciuto"),
        tema: str = Field(default="", description="Tema di interesse"),
        livello: str = Field(default="medio", description="Difficoltà: facile, medio, impegnativo"),
    ) -> str:
        """
        Suggerisce libri basandosi sui gusti dell'utente.
        """
        criteri = []
        if genere:
            criteri.append(f"Genere: {genere}")
        if libro_piaciuto:
            criteri.append(f"Simile a: {libro_piaciuto}")
        if tema:
            criteri.append(f"Tema: {tema}")
        criteri.append(f"Livello: {livello}")

        return f"""📚 **Suggerimenti di Lettura**

**Criteri:**
{chr(10).join('- ' + c for c in criteri)}

---
**Richiesta:**
Suggerisci 5-7 libri che potrebbero piacere, per ciascuno indica:

1. **Titolo e autore**
2. **Breve descrizione** (2-3 righe)
3. **Perché potrebbe piacere** (collegamento ai criteri)
4. **Livello di difficoltà**
5. **Lunghezza approssimativa**

Ordina dal più consigliato al meno."""

    def analizza_citazione(
        self,
        citazione: str = Field(..., description="La citazione da analizzare"),
        libro: str = Field(default="", description="Libro di provenienza (se noto)"),
        autore: str = Field(default="", description="Autore (se noto)"),
    ) -> str:
        """
        Analizza una citazione letteraria in profondità.
        """
        fonte = ""
        if libro and autore:
            fonte = f"**Fonte:** {libro} di {autore}"
        elif libro:
            fonte = f"**Libro:** {libro}"
        elif autore:
            fonte = f"**Autore:** {autore}"

        return f"""💬 **Analisi Citazione**

**Citazione:**
> "{citazione}"

{fonte}

---
**Richiesta di analisi:**

1. **Contesto**
   - Identificazione dell'opera e autore (se non forniti)
   - Momento della storia in cui appare

2. **Significato letterale**
   - Cosa dice esplicitamente

3. **Significato profondo**
   - Interpretazione simbolica
   - Messaggi impliciti

4. **Rilevanza**
   - Importanza nell'opera
   - Applicabilità universale

5. **Connessioni**
   - Riferimenti ad altre opere o filosofie
   - Attualità del messaggio"""

    def crea_mappa_concettuale(
        self,
        libro: str = Field(..., description="Titolo del libro"),
        focus: str = Field(default="generale", description="Focus: generale, personaggi, temi, eventi, luoghi"),
    ) -> str:
        """
        Crea una mappa concettuale del libro.
        """
        return f"""🗺️ **Mappa Concettuale**

**Libro:** {libro}
**Focus:** {focus}

---
**Crea una mappa concettuale che mostri:**

1. **Elemento centrale**
   - Il concetto principale attorno a cui ruota tutto

2. **Rami principali**
   - 4-6 elementi chiave collegati al centro

3. **Sotto-elementi**
   - Dettagli per ogni ramo principale

4. **Connessioni**
   - Relazioni tra i vari elementi
   - Causa-effetto
   - Influenze reciproche

Usa una struttura gerarchica chiara con:
- → per indicare relazioni dirette
- ↔ per relazioni bidirezionali
- ⊂ per inclusione"""

    def prepara_discussione(
        self,
        libro: str = Field(..., description="Titolo del libro"),
        tipo: str = Field(default="club", description="Tipo: club (book club), esame, presentazione"),
    ) -> str:
        """
        Prepara domande e spunti per discutere un libro.
        """
        return f"""🎤 **Preparazione Discussione**

**Libro:** {libro}
**Tipo:** {tipo}

---
**Genera materiale per la discussione:**

1. **Domande di comprensione**
   - 3-4 domande sulla trama e i fatti

2. **Domande di analisi**
   - 3-4 domande sui temi e significati

3. **Domande di opinione**
   - 3-4 domande per stimolare il dibattito

4. **Punti controversi**
   - Aspetti che potrebbero generare discussione

5. **Collegamenti**
   - Riferimenti ad attualità
   - Paragoni con altre opere

6. **Attività suggerite**
   - Esercizi o approfondimenti correlati"""
