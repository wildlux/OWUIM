"""
title: Assistente Testi
author: Carlo
version: 1.0.0
description: Strumento per creare, revisionare e migliorare testi
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def analizza_testo(
        self,
        testo: str = Field(..., description="Il testo da analizzare"),
    ) -> str:
        """
        Analizza un testo e fornisce statistiche dettagliate.
        Utile per capire la struttura e complessità di un testo.
        """
        parole = testo.split()
        frasi = testo.replace("!", ".").replace("?", ".").split(".")
        frasi = [f.strip() for f in frasi if f.strip()]
        paragrafi = [p.strip() for p in testo.split("\n\n") if p.strip()]

        num_parole = len(parole)
        num_caratteri = len(testo)
        num_caratteri_no_spazi = len(testo.replace(" ", ""))
        num_frasi = len(frasi)
        num_paragrafi = len(paragrafi)
        media_parole_frase = round(num_parole / max(num_frasi, 1), 1)

        parole_lunghe = [p for p in parole if len(p) > 8]

        return f"""📊 **Analisi del Testo**

**Statistiche generali:**
- Caratteri (con spazi): {num_caratteri}
- Caratteri (senza spazi): {num_caratteri_no_spazi}
- Parole: {num_parole}
- Frasi: {num_frasi}
- Paragrafi: {num_paragrafi}

**Leggibilità:**
- Media parole per frase: {media_parole_frase}
- Parole lunghe (>8 caratteri): {len(parole_lunghe)}

**Tempo di lettura stimato:** ~{max(1, num_parole // 200)} minuti
"""

    def correggi_grammatica(
        self,
        testo: str = Field(..., description="Il testo da correggere"),
    ) -> str:
        """
        Prepara il testo per la correzione grammaticale.
        Restituisce il testo formattato con istruzioni per la revisione.
        """
        return f"""📝 **Richiesta di Correzione Grammaticale**

**Testo originale:**
{testo}

---
**Istruzioni per la revisione:**
1. Correggi errori ortografici
2. Sistema la punteggiatura
3. Verifica la concordanza soggetto-verbo
4. Controlla l'uso degli articoli
5. Migliora la struttura delle frasi se necessario

Per favore analizza il testo sopra e fornisci la versione corretta evidenziando le modifiche."""

    def genera_schema(
        self,
        argomento: str = Field(..., description="L'argomento del testo da creare"),
        tipo: str = Field(default="articolo", description="Tipo di testo: articolo, saggio, relazione, email, lettera"),
        lunghezza: str = Field(default="media", description="Lunghezza: breve, media, lunga"),
    ) -> str:
        """
        Genera uno schema/outline per scrivere un testo su un argomento specifico.
        """
        lunghezze = {
            "breve": "300-500 parole",
            "media": "500-1000 parole",
            "lunga": "1000-2000 parole"
        }

        return f"""📋 **Schema per {tipo.capitalize()}**

**Argomento:** {argomento}
**Lunghezza consigliata:** {lunghezze.get(lunghezza, lunghezze['media'])}

---
**Struttura suggerita:**

1. **Introduzione**
   - Hook/Apertura accattivante
   - Presentazione dell'argomento
   - Tesi o obiettivo principale

2. **Sviluppo**
   - Punto principale 1
   - Punto principale 2
   - Punto principale 3
   - Esempi e argomentazioni

3. **Conclusione**
   - Riepilogo dei punti chiave
   - Riflessione finale
   - Call to action (se appropriato)

---
Genera ora il testo completo seguendo questo schema sull'argomento: **{argomento}**"""

    def riassumi(
        self,
        testo: str = Field(..., description="Il testo da riassumere"),
        percentuale: int = Field(default=30, description="Percentuale del testo originale (10-50)"),
    ) -> str:
        """
        Prepara un testo per essere riassunto alla percentuale specificata.
        """
        parole_originali = len(testo.split())
        parole_target = max(20, int(parole_originali * percentuale / 100))

        return f"""📄 **Richiesta di Riassunto**

**Testo originale** ({parole_originali} parole):
{testo}

---
**Istruzioni:**
Riassumi il testo in circa **{parole_target} parole** ({percentuale}% dell'originale).
Mantieni i concetti chiave e le informazioni essenziali."""

    def migliora_stile(
        self,
        testo: str = Field(..., description="Il testo da migliorare"),
        stile: str = Field(default="formale", description="Stile target: formale, informale, accademico, giornalistico, creativo"),
    ) -> str:
        """
        Richiede il miglioramento dello stile di un testo.
        """
        stili_desc = {
            "formale": "professionale, preciso, rispettoso delle convenzioni",
            "informale": "colloquiale, amichevole, diretto",
            "accademico": "rigoroso, con terminologia specifica, citazioni",
            "giornalistico": "chiaro, conciso, oggettivo, piramide invertita",
            "creativo": "espressivo, originale, con figure retoriche"
        }

        return f"""✨ **Richiesta di Miglioramento Stile**

**Stile richiesto:** {stile.capitalize()}
*({stili_desc.get(stile, stili_desc['formale'])})*

**Testo originale:**
{testo}

---
**Istruzioni:**
Riscrivi il testo nello stile {stile}, mantenendo il significato originale ma adattando:
- Vocabolario
- Struttura delle frasi
- Tono
- Registro linguistico"""
