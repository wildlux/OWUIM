"""
title: Assistente Produttività
author: Carlo
version: 1.0.0
description: Strumento per gestire progetti, organizzare il lavoro e aumentare la produttività
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Tools:
    def __init__(self):
        pass

    def crea_piano_progetto(
        self,
        progetto: str = Field(..., description="Nome/descrizione del progetto"),
        obiettivo: str = Field(..., description="Obiettivo finale del progetto"),
        scadenza: str = Field(default="", description="Scadenza (se nota)"),
    ) -> str:
        """
        Crea un piano dettagliato per un progetto.
        """
        scadenza_str = f"\n**Scadenza:** {scadenza}" if scadenza else ""

        return f"""📋 **Piano Progetto**

**Progetto:** {progetto}
**Obiettivo:** {obiettivo}{scadenza_str}

---
**Crea un piano che includa:**

1. **Definizione del progetto**
   - Obiettivo SMART
   - Risultati attesi
   - Criteri di successo

2. **Scomposizione in fasi**
   - Fase 1: ...
   - Fase 2: ...
   - Fase N: ...

3. **Task per ogni fase**
   - Attività specifiche
   - Dipendenze tra task
   - Priorità

4. **Risorse necessarie**
   - Strumenti
   - Competenze
   - Materiali

5. **Timeline**
   - Milestone principali
   - Date chiave

6. **Rischi e mitigazioni**
   - Potenziali ostacoli
   - Piani B

7. **Metriche di avanzamento**
   - Come misurare il progresso"""

    def genera_todo_list(
        self,
        contesto: str = Field(..., description="Contesto o progetto per cui creare la lista"),
        priorita: str = Field(default="miste", description="Priorità: alta, media, bassa, miste"),
        formato: str = Field(default="dettagliato", description="Formato: semplice, dettagliato, eisenhower"),
    ) -> str:
        """
        Genera una lista di cose da fare organizzata.
        """
        return f"""✅ **To-Do List**

**Contesto:** {contesto}
**Formato:** {formato}

---
**Genera una lista di task:**

{"**Matrice di Eisenhower:**" if formato == "eisenhower" else ""}
{"" if formato != "eisenhower" else '''
| Urgente + Importante | Non Urgente + Importante |
|---------------------|-------------------------|
| FARE SUBITO         | PIANIFICARE             |
|---------------------|-------------------------|
| Urgente + Non Imp.  | Non Urgente + Non Imp.  |
|---------------------|-------------------------|
| DELEGARE            | ELIMINARE               |
'''}

**Lista Task:**

Per ogni task indica:
- [ ] **Task**: Descrizione chiara
- **Priorità**: 🔴 Alta / 🟡 Media / 🟢 Bassa
- **Tempo stimato**: X minuti/ore
- **Dipendenze**: (se presenti)
{"- **Quadrante**: (per Eisenhower)" if formato == "eisenhower" else ""}

**Suggerimenti:**
- Ordina per priorità/urgenza
- Raggruppa task simili
- Identifica "quick wins" (task veloci ad alto impatto)"""

    def analizza_tempo(
        self,
        attivita: str = Field(..., description="Lista delle attività svolte o da svolgere"),
        periodo: str = Field(default="giornata", description="Periodo: giornata, settimana, mese"),
    ) -> str:
        """
        Analizza come viene speso il tempo e suggerisce ottimizzazioni.
        """
        return f"""⏱️ **Analisi del Tempo**

**Periodo:** {periodo}

**Attività da analizzare:**
{attivita}

---
**Analisi:**

1. **Categorizzazione attività**
   - Lavoro profondo (deep work)
   - Lavoro superficiale
   - Riunioni/comunicazioni
   - Pause/distrazioni

2. **Distribuzione del tempo**
   - Percentuali per categoria
   - Ore effettive vs. previste

3. **Time sinks identificati**
   - Attività che consumano troppo tempo
   - Interruzioni frequenti

4. **Ottimizzazioni suggerite**
   - Task da eliminare
   - Task da delegare
   - Task da automatizzare
   - Batching di attività simili

5. **Piano migliorato**
   - Nuova distribuzione consigliata
   - Time blocking suggerito

6. **Tecniche consigliate**
   - Pomodoro, time boxing, ecc."""

    def scrivi_email(
        self,
        scopo: str = Field(..., description="Scopo dell'email"),
        destinatario: str = Field(default="", description="Chi è il destinatario"),
        tono: str = Field(default="professionale", description="Tono: formale, professionale, cordiale, informale"),
        punti_chiave: str = Field(default="", description="Punti da includere"),
    ) -> str:
        """
        Genera una bozza di email professionale.
        """
        dest_str = f"\n**Destinatario:** {destinatario}" if destinatario else ""
        punti_str = f"\n**Punti chiave:** {punti_chiave}" if punti_chiave else ""

        return f"""📧 **Email**

**Scopo:** {scopo}
**Tono:** {tono}{dest_str}{punti_str}

---
**Genera un'email che includa:**

1. **Oggetto**
   - Chiaro e specifico
   - Max 50 caratteri

2. **Corpo email**
   - Saluto appropriato
   - Introduzione (scopo in 1 frase)
   - Corpo principale
   - Call to action chiara
   - Chiusura cortese
   - Firma

3. **Varianti** (se utile)
   - Versione più breve
   - Versione più formale

**Caratteristiche:**
- Tono {tono}
- Paragrafi brevi
- Punti elenco se necessario
- Nessun errore grammaticale"""

    def prepara_riunione(
        self,
        argomento: str = Field(..., description="Argomento della riunione"),
        partecipanti: str = Field(default="", description="Chi parteciperà"),
        durata: int = Field(default=60, description="Durata in minuti"),
    ) -> str:
        """
        Prepara l'agenda e i materiali per una riunione.
        """
        part_str = f"\n**Partecipanti:** {partecipanti}" if partecipanti else ""

        return f"""📅 **Preparazione Riunione**

**Argomento:** {argomento}
**Durata:** {durata} minuti{part_str}

---
**Genera:**

1. **Agenda**
   - 00:00 - Benvenuto e obiettivi (5 min)
   - 00:05 - Punto 1 (X min)
   - ...
   - XX:XX - Prossimi passi e chiusura (5 min)

2. **Obiettivi della riunione**
   - Cosa vogliamo ottenere
   - Decisioni da prendere

3. **Materiali da preparare**
   - Documenti necessari
   - Presentazioni
   - Dati/report

4. **Domande da affrontare**
   - Lista di punti da discutere

5. **Template verbale**
   - Data e partecipanti
   - Punti discussi
   - Decisioni prese
   - Action items
   - Prossimi passi"""

    def riassumi_documento(
        self,
        documento: str = Field(..., description="Il documento da riassumere"),
        formato: str = Field(default="executive", description="Formato: executive, punti, narrativo"),
        lunghezza: str = Field(default="medio", description="Lunghezza: breve, medio, dettagliato"),
    ) -> str:
        """
        Riassume un documento in modo strutturato.
        """
        lunghezze = {
            "breve": "max 100 parole",
            "medio": "200-300 parole",
            "dettagliato": "500+ parole"
        }

        return f"""📄 **Riassunto Documento**

**Formato:** {formato}
**Lunghezza:** {lunghezza} ({lunghezze.get(lunghezza, '')})

**Documento:**
{documento}

---
**Genera un riassunto {formato}:**

{"**Executive Summary:**" if formato == "executive" else ""}
{"- Situazione/Contesto" if formato == "executive" else ""}
{"- Problema/Opportunità" if formato == "executive" else ""}
{"- Soluzione/Raccomandazione" if formato == "executive" else ""}
{"- Prossimi passi" if formato == "executive" else ""}

{"**Punti chiave:**" if formato == "punti" else ""}
{"• Punto 1" if formato == "punti" else ""}
{"• Punto 2" if formato == "punti" else ""}
{"• ..." if formato == "punti" else ""}

{"**Riassunto narrativo:**" if formato == "narrativo" else ""}
{"Testo fluido che riassume il documento..." if formato == "narrativo" else ""}

**Includi:**
- Idee principali
- Conclusioni chiave
- Action items (se presenti)"""

    def brainstorming(
        self,
        tema: str = Field(..., description="Tema su cui fare brainstorming"),
        metodo: str = Field(default="libero", description="Metodo: libero, 6_cappelli, scamper, 5_perche"),
        num_idee: int = Field(default=10, description="Numero minimo di idee"),
    ) -> str:
        """
        Facilita una sessione di brainstorming strutturata.
        """
        metodi_desc = {
            "libero": "generazione libera di idee",
            "6_cappelli": "metodo dei 6 cappelli di De Bono",
            "scamper": "Sostituire, Combinare, Adattare, Modificare, altri usi, Eliminare, Riorganizzare",
            "5_perche": "analisi delle cause profonde"
        }

        return f"""💡 **Brainstorming**

**Tema:** {tema}
**Metodo:** {metodo} ({metodi_desc.get(metodo, '')})
**Obiettivo:** almeno {num_idee} idee

---
**Sessione di brainstorming:**

{"**6 Cappelli:**" if metodo == "6_cappelli" else ""}
{"🔵 Blu (Processo): ..." if metodo == "6_cappelli" else ""}
{"⚪ Bianco (Fatti): ..." if metodo == "6_cappelli" else ""}
{"🔴 Rosso (Emozioni): ..." if metodo == "6_cappelli" else ""}
{"⚫ Nero (Cautela): ..." if metodo == "6_cappelli" else ""}
{"🟡 Giallo (Ottimismo): ..." if metodo == "6_cappelli" else ""}
{"🟢 Verde (Creatività): ..." if metodo == "6_cappelli" else ""}

**Idee generate:**
1. ...
2. ...
[continua fino a {num_idee}+]

**Categorizzazione:**
- Idee realizzabili subito
- Idee che richiedono risorse
- Idee a lungo termine
- Idee wild/creative

**Top 3 idee da sviluppare:**
1. (Migliore) - Perché
2. - Perché
3. - Perché"""

    def decision_matrix(
        self,
        decisione: str = Field(..., description="La decisione da prendere"),
        opzioni: str = Field(..., description="Le opzioni disponibili (separate da virgola)"),
        criteri: str = Field(default="", description="Criteri di valutazione (opzionale)"),
    ) -> str:
        """
        Crea una matrice decisionale per valutare opzioni.
        """
        opzioni_list = [o.strip() for o in opzioni.split(',')]
        criteri_str = f"\n**Criteri:** {criteri}" if criteri else ""

        return f"""⚖️ **Matrice Decisionale**

**Decisione:** {decisione}
**Opzioni:** {', '.join(opzioni_list)}{criteri_str}

---
**Analisi:**

1. **Criteri di valutazione**
   {"(suggeriti)" if not criteri else ""}
   - Criterio 1 (Peso: X/10)
   - Criterio 2 (Peso: X/10)
   - ...

2. **Matrice**

| Criterio (Peso) | {' | '.join(opzioni_list)} |
|-----------------|{'|'.join(['---------' for _ in opzioni_list])}|
| C1 (X) | ... | ... |
| C2 (X) | ... | ... |
| **TOTALE** | **X** | **X** |

3. **Analisi pro/contro**
   Per ogni opzione:
   - Pro: ...
   - Contro: ...

4. **Rischi**
   - Per ogni opzione

5. **Raccomandazione**
   - Opzione consigliata
   - Motivazione
   - Piano di implementazione"""

    def daily_review(
        self,
        tipo: str = Field(default="sera", description="Tipo: mattina (planning), sera (review)"),
        focus: str = Field(default="", description="Area di focus particolare"),
    ) -> str:
        """
        Genera template per review giornaliera.
        """
        focus_str = f"\n**Focus:** {focus}" if focus else ""

        if tipo == "mattina":
            return f"""🌅 **Morning Planning**{focus_str}

---
**Completa questo template:**

**🎯 Top 3 Priorità di oggi:**
1. [ ] ...
2. [ ] ...
3. [ ] ...

**📋 Altri task:**
- [ ] ...
- [ ] ...

**⏰ Time blocks:**
- 08:00-10:00: Deep work - ...
- 10:00-12:00: ...
- 14:00-16:00: ...
- 16:00-18:00: ...

**🚫 NON fare oggi:**
- ...

**💪 Affermazione del giorno:**
- ...

**🎯 Se oggi va bene, avrò:**
- ..."""

        else:
            return f"""🌙 **Evening Review**{focus_str}

---
**Completa questo template:**

**✅ Completato oggi:**
1. ...
2. ...
3. ...

**❌ Non completato (perché):**
- ... - Motivo: ...

**🎓 Cosa ho imparato:**
- ...

**🙏 Gratitudine:**
1. ...
2. ...
3. ...

**📈 Valutazione giornata (1-10):**
- Produttività: X
- Energia: X
- Umore: X

**🔄 Cosa farò diversamente domani:**
- ...

**📝 Note per domani:**
- ..."""

    def gestisci_obiettivi(
        self,
        obiettivo: str = Field(..., description="L'obiettivo da raggiungere"),
        timeframe: str = Field(default="trimestre", description="Timeframe: settimana, mese, trimestre, anno"),
    ) -> str:
        """
        Trasforma un obiettivo in un piano d'azione con milestone.
        """
        return f"""🎯 **Gestione Obiettivo**

**Obiettivo:** {obiettivo}
**Timeframe:** {timeframe}

---
**Trasforma in piano SMART:**

1. **Obiettivo SMART**
   - Specifico: ...
   - Misurabile: ...
   - Achievable: ...
   - Rilevante: ...
   - Time-bound: ...

2. **Milestone**
   - M1 (25%): ... - Entro: ...
   - M2 (50%): ... - Entro: ...
   - M3 (75%): ... - Entro: ...
   - M4 (100%): ... - Entro: ...

3. **Azioni settimanali**
   - Settimana 1: ...
   - Settimana 2: ...
   - ...

4. **Metriche di successo**
   - Come misurare il progresso
   - Check-in points

5. **Potenziali ostacoli**
   - Ostacolo 1 → Soluzione
   - Ostacolo 2 → Soluzione

6. **Risorse necessarie**
   - ...

7. **Accountability**
   - Come mantenersi responsabili
   - Chi coinvolgere"""
