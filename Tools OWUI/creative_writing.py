"""
title: Assistente Scrittura Creativa
author: Carlo
version: 1.0.0
description: Strumento per scrivere storie, poesie, sceneggiature e contenuti creativi
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def genera_storia(
        self,
        genere: str = Field(..., description="Genere: fantasy, horror, romance, thriller, sci-fi, avventura, drammatico"),
        tema: str = Field(default="", description="Tema principale (es: redenzione, amore, vendetta)"),
        lunghezza: str = Field(default="breve", description="Lunghezza: flash (100 parole), breve (500), media (1000), lunga (2000+)"),
        protagonista: str = Field(default="", description="Descrizione del protagonista (opzionale)"),
    ) -> str:
        """
        Genera una storia originale basata sui parametri forniti.
        """
        lunghezze = {
            "flash": "circa 100 parole (flash fiction)",
            "breve": "circa 500 parole",
            "media": "circa 1000 parole",
            "lunga": "2000+ parole"
        }

        prot_str = f"\n**Protagonista:** {protagonista}" if protagonista else ""
        tema_str = f"\n**Tema:** {tema}" if tema else ""

        return f"""📖 **Generazione Storia**

**Genere:** {genere}
**Lunghezza:** {lunghezze.get(lunghezza, lunghezze['breve'])}{tema_str}{prot_str}

---
**Scrivi una storia originale che:**

1. Abbia un inizio accattivante (hook)
2. Presenti personaggi memorabili
3. Sviluppi tensione narrativa
4. Abbia un climax soddisfacente
5. Si concluda in modo significativo

**Elementi da includere:**
- Descrizioni vivide (show, don't tell)
- Dialoghi naturali
- Atmosfera coerente con il genere {genere}
- Colpi di scena (se appropriato)"""

    def continua_storia(
        self,
        testo_precedente: str = Field(..., description="Il testo della storia da continuare"),
        direzione: str = Field(default="", description="Indicazioni su come proseguire (opzionale)"),
        parole: int = Field(default=300, description="Numero di parole da aggiungere"),
    ) -> str:
        """
        Continua una storia esistente mantenendo stile e coerenza.
        """
        dir_str = f"\n**Direzione suggerita:** {direzione}" if direzione else ""

        return f"""📝 **Continuazione Storia**

**Testo precedente:**
{testo_precedente}

**Parole da aggiungere:** ~{parole}{dir_str}

---
**Continua la storia:**

1. Mantieni lo stesso stile e tono
2. Rispetta la caratterizzazione dei personaggi
3. Sviluppa la trama in modo coerente
4. Aggiungi nuovi elementi interessanti
5. Crea tensione o risolvi conflitti secondo la direzione"""

    def crea_personaggio(
        self,
        ruolo: str = Field(default="protagonista", description="Ruolo: protagonista, antagonista, mentore, spalla, comparsa"),
        genere_storia: str = Field(default="", description="Genere della storia"),
        caratteristiche: str = Field(default="", description="Caratteristiche specifiche richieste"),
    ) -> str:
        """
        Crea un personaggio dettagliato per una storia.
        """
        return f"""👤 **Creazione Personaggio**

**Ruolo:** {ruolo}
**Genere storia:** {genere_storia if genere_storia else "(qualsiasi)"}
**Richieste specifiche:** {caratteristiche if caratteristiche else "(nessuna)"}

---
**Crea un personaggio completo:**

1. **Identità**
   - Nome e soprannome
   - Età e aspetto fisico
   - Professione/ruolo sociale

2. **Personalità**
   - Tratti caratteriali principali
   - Pregi e difetti
   - Abitudini e manie

3. **Background**
   - Storia passata
   - Famiglia e relazioni
   - Evento che l'ha segnato

4. **Motivazioni**
   - Cosa vuole (obiettivo esterno)
   - Di cosa ha bisogno (obiettivo interno)
   - Paure più profonde

5. **Voce**
   - Come parla (registro, intercalari)
   - Esempio di dialogo tipico

6. **Arco narrativo potenziale**
   - Come potrebbe evolversi nella storia"""

    def genera_poesia(
        self,
        tema: str = Field(..., description="Tema o soggetto della poesia"),
        stile: str = Field(default="libero", description="Stile: libero, sonetto, haiku, rima_alternata, rima_baciata"),
        tono: str = Field(default="lirico", description="Tono: lirico, malinconico, gioioso, drammatico, ironico"),
    ) -> str:
        """
        Genera una poesia originale.
        """
        stili_desc = {
            "libero": "verso libero, senza schema metrico fisso",
            "sonetto": "14 versi endecasillabi con schema ABAB ABAB CDC DCD",
            "haiku": "tre versi di 5-7-5 sillabe, tema naturale",
            "rima_alternata": "versi con schema ABAB",
            "rima_baciata": "versi con schema AABB"
        }

        return f"""🎭 **Generazione Poesia**

**Tema:** {tema}
**Stile:** {stile} ({stili_desc.get(stile, 'verso libero')})
**Tono:** {tono}

---
**Scrivi una poesia che:**

1. Esplori il tema con profondità emotiva
2. Usi immagini evocative
3. Rispetti lo stile richiesto
4. Abbia musicalità (anche nel verso libero)
5. Trasmetta il tono {tono}

**Dopo la poesia, aggiungi:**
- Breve commento sull'ispirazione
- Figure retoriche utilizzate"""

    def genera_dialogo(
        self,
        situazione: str = Field(..., description="La situazione/scena del dialogo"),
        personaggio1: str = Field(default="Persona A", description="Primo personaggio"),
        personaggio2: str = Field(default="Persona B", description="Secondo personaggio"),
        tono: str = Field(default="neutro", description="Tono: neutro, conflittuale, romantico, comico, teso"),
    ) -> str:
        """
        Genera un dialogo realistico tra personaggi.
        """
        return f"""💬 **Generazione Dialogo**

**Situazione:** {situazione}
**Personaggi:** {personaggio1} e {personaggio2}
**Tono:** {tono}

---
**Scrivi un dialogo che:**

1. Sia naturale e realistico
2. Riveli la personalità dei personaggi
3. Faccia avanzare la situazione
4. Includa sottotesto (non detto)
5. Abbia il tono {tono}

**Formato:**
{personaggio1}: [battuta]
{personaggio2}: [battuta]

**Includi anche:**
- Didascalie per azioni/espressioni (tra parentesi)
- Pause significative
- Interruzioni naturali"""

    def sviluppa_trama(
        self,
        idea: str = Field(..., description="L'idea base della storia"),
        struttura: str = Field(default="tre_atti", description="Struttura: tre_atti, viaggio_eroe, in_media_res, circolare"),
    ) -> str:
        """
        Sviluppa una trama completa da un'idea iniziale.
        """
        strutture_desc = {
            "tre_atti": "Setup, Confronto, Risoluzione",
            "viaggio_eroe": "12 stadi del viaggio dell'eroe di Campbell",
            "in_media_res": "Inizio nel mezzo dell'azione",
            "circolare": "Fine che richiama l'inizio"
        }

        return f"""📊 **Sviluppo Trama**

**Idea:** {idea}
**Struttura:** {struttura} ({strutture_desc.get(struttura, '')})

---
**Sviluppa la trama completa:**

1. **Premessa**
   - Logline (una frase)
   - Tema centrale

2. **Personaggi principali**
   - Protagonista e obiettivo
   - Antagonista/ostacolo
   - Personaggi secondari chiave

3. **Struttura dettagliata**
   {"- Atto 1: Setup e incidente scatenante" if struttura == "tre_atti" else ""}
   {"- Atto 2: Confronto e complicazioni" if struttura == "tre_atti" else ""}
   {"- Atto 3: Climax e risoluzione" if struttura == "tre_atti" else ""}
   [Sviluppa secondo la struttura {struttura}]

4. **Punti di svolta**
   - Incidente scatenante
   - Punto di non ritorno
   - Crisi/climax
   - Risoluzione

5. **Sottotrame**
   - Trame secondarie che arricchiscono la storia

6. **Outline capitoli/scene**
   - Sequenza delle scene principali"""

    def descrivi_ambientazione(
        self,
        luogo: str = Field(..., description="Il luogo da descrivere"),
        epoca: str = Field(default="contemporanea", description="Epoca: medievale, vittoriana, contemporanea, futuristica, fantasy"),
        atmosfera: str = Field(default="neutra", description="Atmosfera: cupa, luminosa, misteriosa, accogliente, inquietante"),
    ) -> str:
        """
        Crea una descrizione dettagliata di un'ambientazione.
        """
        return f"""🏰 **Descrizione Ambientazione**

**Luogo:** {luogo}
**Epoca:** {epoca}
**Atmosfera:** {atmosfera}

---
**Descrivi l'ambientazione includendo:**

1. **Vista d'insieme**
   - Prima impressione
   - Elementi dominanti

2. **Dettagli visivi**
   - Colori e luci
   - Architettura/paesaggio
   - Oggetti significativi

3. **Altri sensi**
   - Suoni caratteristici
   - Odori
   - Sensazioni tattili

4. **Atmosfera**
   - Mood generale
   - Come influenza chi vi entra

5. **Elementi narrativi**
   - Storia del luogo
   - Segreti o misteri
   - Come può influenzare la trama

Usa uno stile evocativo, "show don't tell"."""

    def critica_costruttiva(
        self,
        testo: str = Field(..., description="Il testo creativo da analizzare"),
        focus: str = Field(default="generale", description="Focus: generale, stile, trama, personaggi, dialoghi"),
    ) -> str:
        """
        Fornisce una critica costruttiva di un testo creativo.
        """
        return f"""📋 **Critica Costruttiva**

**Focus:** {focus}

**Testo da analizzare:**
{testo}

---
**Analizza il testo considerando:**

1. **Punti di forza**
   - Cosa funziona bene
   - Elementi da mantenere

2. **Aree di miglioramento**
   - Aspetti da sviluppare
   - Suggerimenti specifici

3. **Analisi {focus}**
   - Approfondimento sull'aspetto richiesto

4. **Esempi concreti**
   - Passaggi specifici con suggerimenti di riscrittura

5. **Valutazione complessiva**
   - Potenziale del testo
   - Prossimi passi consigliati

**Nota:** La critica è costruttiva, non distruttiva. L'obiettivo è aiutare a migliorare."""

    def genera_titolo(
        self,
        descrizione: str = Field(..., description="Breve descrizione dell'opera"),
        tipo: str = Field(default="romanzo", description="Tipo: romanzo, racconto, poesia, articolo, film"),
        stile: str = Field(default="evocativo", description="Stile: evocativo, diretto, misterioso, provocatorio"),
    ) -> str:
        """
        Genera proposte di titoli per un'opera.
        """
        return f"""✨ **Generazione Titoli**

**Descrizione:** {descrizione}
**Tipo:** {tipo}
**Stile:** {stile}

---
**Genera 10 proposte di titoli:**

Per ogni proposta indica:

1. **Titolo**
2. **Perché funziona** (breve spiegazione)

Considera:
- Memorabilità
- Rilevanza con il contenuto
- Impatto emotivo
- Originalità
- Adeguatezza al genere

Ordina dal più consigliato al meno."""

    def esercizio_scrittura(
        self,
        tipo: str = Field(default="prompt", description="Tipo: prompt, vincolo, stile, personaggio"),
        difficolta: str = Field(default="media", description="Difficoltà: facile, media, difficile"),
    ) -> str:
        """
        Genera un esercizio di scrittura creativa.
        """
        tipi_desc = {
            "prompt": "uno spunto narrativo da sviluppare",
            "vincolo": "una sfida con regole specifiche",
            "stile": "imitazione di uno stile particolare",
            "personaggio": "esplorazione di un personaggio"
        }

        return f"""✏️ **Esercizio di Scrittura**

**Tipo:** {tipo} - {tipi_desc.get(tipo, '')}
**Difficoltà:** {difficolta}

---
**Genera un esercizio che includa:**

1. **L'esercizio**
   - Istruzioni chiare
   - Eventuali vincoli o regole
   - Lunghezza suggerita

2. **Obiettivo didattico**
   - Cosa si impara con questo esercizio
   - Abilità sviluppate

3. **Suggerimenti**
   - Come approcciarsi all'esercizio
   - Errori comuni da evitare

4. **Varianti**
   - Versione più facile
   - Versione più difficile

5. **Esempio** (opzionale)
   - Breve esempio di come iniziare"""
