"""
title: Mega Assistente Completo
author: Carlo
version: 1.0.0
description: Assistente completo con tutte le funzioni: testi, matematica, codice, libri, studio, scrittura creativa, ricerca, pubblicazione, produttività e finanza italiana
"""

from pydantic import BaseModel, Field
from typing import Optional
import math


class Tools:
    def __init__(self):
        pass

    # ==========================================
    # SEZIONE: TESTI
    # ==========================================

    def analizza_testo(
        self,
        testo: str = Field(..., description="Il testo da analizzare"),
    ) -> str:
        """Analizza un testo e fornisce statistiche dettagliate."""
        parole = testo.split()
        frasi = testo.replace("!", ".").replace("?", ".").split(".")
        frasi = [f.strip() for f in frasi if f.strip()]
        num_parole = len(parole)
        num_frasi = len(frasi)
        return f"""📊 **Analisi Testo**
- Caratteri: {len(testo)}
- Parole: {num_parole}
- Frasi: {num_frasi}
- Media parole/frase: {round(num_parole / max(num_frasi, 1), 1)}
- Tempo lettura: ~{max(1, num_parole // 200)} min"""

    def correggi_grammatica(
        self,
        testo: str = Field(..., description="Il testo da correggere"),
    ) -> str:
        """Richiede correzione grammaticale del testo."""
        return f"""📝 **Correzione Grammaticale**

**Testo:**
{testo}

---
Correggi: ortografia, punteggiatura, concordanze, articoli, struttura frasi."""

    def riassumi_testo(
        self,
        testo: str = Field(..., description="Il testo da riassumere"),
        percentuale: int = Field(default=30, description="Percentuale (10-50)"),
    ) -> str:
        """Riassume un testo."""
        parole = len(testo.split())
        target = max(20, int(parole * percentuale / 100))
        return f"""📄 **Riassunto** ({parole} → ~{target} parole)

{testo}

---
Riassumi mantenendo i concetti chiave."""

    def migliora_stile(
        self,
        testo: str = Field(..., description="Testo da migliorare"),
        stile: str = Field(default="formale", description="formale/informale/accademico/giornalistico"),
    ) -> str:
        """Migliora lo stile di un testo."""
        return f"""✨ **Migliora Stile → {stile}**

{testo}

---
Riscrivi in stile {stile}."""

    # ==========================================
    # SEZIONE: MATEMATICA
    # ==========================================

    def calcola(
        self,
        espressione: str = Field(..., description="Espressione matematica"),
    ) -> str:
        """Calcola un'espressione matematica."""
        try:
            safe = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "log": math.log, "pi": math.pi, "e": math.e, "abs": abs, "pow": pow}
            expr = espressione.replace("^", "**").replace("×", "*").replace("÷", "/")
            result = eval(expr, {"__builtins__": {}}, safe)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            return f"🔢 `{espressione}` = **{round(result, 10) if isinstance(result, float) else result}**"
        except Exception as e:
            return f"❌ Errore: {e}"

    def risolvi_equazione(
        self,
        equazione: str = Field(..., description="Equazione da risolvere"),
    ) -> str:
        """Risolve un'equazione passo-passo."""
        return f"""📐 **Risolvi:** `{equazione}`

Mostra tutti i passaggi e verifica il risultato."""

    def converti_unita(
        self,
        valore: float = Field(..., description="Valore"),
        da: str = Field(..., description="Unità origine"),
        a: str = Field(..., description="Unità destinazione"),
    ) -> str:
        """Converte unità di misura."""
        conv = {
            ("km","m"): 1000, ("m","km"): 0.001, ("kg","g"): 1000, ("g","kg"): 0.001,
            ("m","cm"): 100, ("cm","m"): 0.01, ("l","ml"): 1000, ("ml","l"): 0.001,
        }
        if (da, a) in conv:
            return f"🔄 **{valore} {da}** = **{valore * conv[(da,a)]} {a}**"
        if (da, a) == ("°C", "°F"):
            return f"🔄 **{valore}°C** = **{valore * 9/5 + 32}°F**"
        if (da, a) == ("°F", "°C"):
            return f"🔄 **{valore}°F** = **{(valore - 32) * 5/9}°C**"
        return f"Converti {valore} da {da} a {a}"

    def percentuale(
        self,
        operazione: str = Field(..., description="calcola/trova/variazione"),
        valore1: float = Field(..., description="Primo valore"),
        valore2: float = Field(..., description="Secondo valore"),
    ) -> str:
        """Calcoli con percentuali."""
        if operazione == "calcola":
            return f"📊 {valore1}% di {valore2} = **{round(valore1/100*valore2, 4)}**"
        elif operazione == "trova":
            return f"📊 {valore1} è il **{round(valore1/valore2*100, 2)}%** di {valore2}"
        elif operazione == "variazione":
            v = ((valore2 - valore1) / valore1) * 100
            return f"📊 Variazione: **{'+' if v > 0 else ''}{round(v, 2)}%**"
        return "Usa: calcola, trova, variazione"

    def geometria(
        self,
        figura: str = Field(..., description="cerchio/quadrato/rettangolo/triangolo"),
        misura1: float = Field(..., description="Prima misura"),
        misura2: float = Field(default=0, description="Seconda misura"),
    ) -> str:
        """Calcola area e perimetro."""
        if figura == "cerchio":
            return f"📐 **Cerchio** r={misura1}\nArea: {round(math.pi*misura1**2, 4)}\nCirconferenza: {round(2*math.pi*misura1, 4)}"
        elif figura == "quadrato":
            return f"📐 **Quadrato** l={misura1}\nArea: {misura1**2}\nPerimetro: {4*misura1}"
        elif figura == "rettangolo":
            return f"📐 **Rettangolo** {misura1}×{misura2}\nArea: {misura1*misura2}\nPerimetro: {2*(misura1+misura2)}"
        elif figura == "triangolo":
            return f"📐 **Triangolo** b={misura1} h={misura2}\nArea: {misura1*misura2/2}"
        return f"Calcola {figura} con misure {misura1}, {misura2}"

    def spiega_problema(
        self,
        problema: str = Field(..., description="Problema matematico"),
    ) -> str:
        """Risolve problema con spiegazione."""
        return f"""🎓 **Problema:**
{problema}

---
Risolvi con: comprensione, dati, strategia, svolgimento, soluzione, verifica."""

    # ==========================================
    # SEZIONE: CODICE
    # ==========================================

    def analizza_codice(
        self,
        codice: str = Field(..., description="Codice da analizzare"),
        linguaggio: str = Field(default="auto", description="Linguaggio"),
    ) -> str:
        """Analizza codice sorgente."""
        return f"""🔍 **Analisi Codice** ({linguaggio})

```{linguaggio}
{codice}
```

Verifica: correttezza, bug, miglioramenti, sicurezza, best practices."""

    def debug_errore(
        self,
        codice: str = Field(..., description="Codice con errore"),
        errore: str = Field(..., description="Messaggio errore"),
    ) -> str:
        """Debug di un errore."""
        return f"""🐛 **Debug**

**Errore:** `{errore}`

```
{codice}
```

Spiega: causa, soluzione, prevenzione."""

    def spiega_codice(
        self,
        codice: str = Field(..., description="Codice da spiegare"),
        livello: str = Field(default="intermedio", description="principiante/intermedio/avanzato"),
    ) -> str:
        """Spiega cosa fa il codice."""
        return f"""📚 **Spiegazione** (livello: {livello})

```
{codice}
```

Spiega: panoramica, linea per linea, concetti, I/O."""

    def genera_codice(
        self,
        descrizione: str = Field(..., description="Cosa deve fare"),
        linguaggio: str = Field(default="python", description="Linguaggio"),
    ) -> str:
        """Genera codice da descrizione."""
        return f"""💻 **Genera {linguaggio}**

{descrizione}

Genera codice funzionante con commenti e esempio d'uso."""

    def genera_test(
        self,
        codice: str = Field(..., description="Codice da testare"),
    ) -> str:
        """Genera test unitari."""
        return f"""🧪 **Test per:**

```
{codice}
```

Genera test: casi normali, edge cases, errori."""

    # ==========================================
    # SEZIONE: LIBRI
    # ==========================================

    def analizza_libro(
        self,
        titolo: str = Field(..., description="Titolo libro"),
        autore: str = Field(default="", description="Autore"),
    ) -> str:
        """Analisi completa di un libro."""
        return f"""📖 **{titolo}**{f' di {autore}' if autore else ''}

Analizza: contesto, trama, personaggi, temi, stile, significato."""

    def riassumi_capitolo(
        self,
        libro: str = Field(..., description="Titolo"),
        capitolo: str = Field(..., description="Capitolo"),
    ) -> str:
        """Riassunto capitolo."""
        return f"""📑 **{libro}** - Cap. {capitolo}

Riassumi: eventi, personaggi, momenti chiave."""

    def analizza_personaggio(
        self,
        personaggio: str = Field(..., description="Personaggio"),
        libro: str = Field(..., description="Libro"),
    ) -> str:
        """Analisi personaggio."""
        return f"""👤 **{personaggio}** in *{libro}*

Analizza: ruolo, carattere, evoluzione, relazioni, simbolismo."""

    def suggerisci_libri(
        self,
        genere: str = Field(default="", description="Genere"),
        simile_a: str = Field(default="", description="Libro simile"),
    ) -> str:
        """Suggerimenti lettura."""
        criteri = []
        if genere: criteri.append(f"Genere: {genere}")
        if simile_a: criteri.append(f"Simile a: {simile_a}")
        return f"""📚 **Suggerimenti**

{chr(10).join(criteri) if criteri else 'Suggerisci libri interessanti'}

Consiglia 5-7 libri con descrizione."""

    # ==========================================
    # SEZIONE: STUDIO
    # ==========================================

    def crea_riassunto_studio(
        self,
        argomento: str = Field(..., description="Argomento"),
        materia: str = Field(default="", description="Materia"),
    ) -> str:
        """Riassunto per studio."""
        return f"""📝 **Riassunto: {argomento}**{f' ({materia})' if materia else ''}

Crea: concetti chiave, spiegazioni, schema, domande verifica."""

    def genera_flashcard(
        self,
        argomento: str = Field(..., description="Argomento"),
        numero: int = Field(default=10, description="Quante"),
    ) -> str:
        """Genera flashcard."""
        return f"""🎴 **Flashcard: {argomento}**

Genera {numero} flashcard:
🔵 Domanda: ...
🟢 Risposta: ..."""

    def spiega_concetto(
        self,
        concetto: str = Field(..., description="Concetto"),
        livello: str = Field(default="superiori", description="elementari/medie/superiori/università"),
    ) -> str:
        """Spiega un concetto."""
        return f"""💡 **{concetto}** (livello: {livello})

Spiega: definizione, come funziona, esempi, collegamenti."""

    def quiz_verifica(
        self,
        argomento: str = Field(..., description="Argomento"),
        numero: int = Field(default=10, description="Domande"),
    ) -> str:
        """Quiz di verifica."""
        return f"""❓ **Quiz: {argomento}**

Genera {numero} domande con risposte e spiegazioni."""

    def prepara_esame(
        self,
        materia: str = Field(..., description="Materia"),
        argomenti: str = Field(..., description="Argomenti"),
        giorni: int = Field(default=7, description="Giorni"),
    ) -> str:
        """Piano studio esame."""
        return f"""📅 **Esame: {materia}**

Argomenti: {argomenti}
Giorni: {giorni}

Crea piano: calendario, priorità, tecniche, simulazione."""

    # ==========================================
    # SEZIONE: SCRITTURA CREATIVA
    # ==========================================

    def genera_storia(
        self,
        genere: str = Field(..., description="fantasy/horror/romance/thriller/sci-fi"),
        lunghezza: str = Field(default="breve", description="flash/breve/media/lunga"),
    ) -> str:
        """Genera una storia."""
        return f"""📖 **Storia {genere}** ({lunghezza})

Scrivi con: hook, personaggi, tensione, climax, conclusione."""

    def crea_personaggio(
        self,
        ruolo: str = Field(default="protagonista", description="Ruolo"),
        genere_storia: str = Field(default="", description="Genere"),
    ) -> str:
        """Crea personaggio."""
        return f"""👤 **Personaggio** ({ruolo}{f', {genere_storia}' if genere_storia else ''})

Crea: identità, personalità, background, motivazioni, voce."""

    def genera_poesia(
        self,
        tema: str = Field(..., description="Tema"),
        stile: str = Field(default="libero", description="libero/sonetto/haiku"),
    ) -> str:
        """Genera poesia."""
        return f"""🎭 **Poesia: {tema}** ({stile})

Scrivi con profondità emotiva e immagini evocative."""

    def genera_dialogo(
        self,
        situazione: str = Field(..., description="Situazione"),
        personaggi: str = Field(default="A e B", description="Personaggi"),
    ) -> str:
        """Genera dialogo."""
        return f"""💬 **Dialogo:** {situazione}

Tra: {personaggi}

Scrivi dialogo naturale con sottotesto."""

    # ==========================================
    # SEZIONE: RICERCA
    # ==========================================

    def ricerca_argomento(
        self,
        argomento: str = Field(..., description="Argomento"),
        profondita: str = Field(default="media", description="panoramica/media/approfondita"),
    ) -> str:
        """Ricerca su argomento."""
        return f"""🔍 **{argomento}** ({profondita})

Fornisci: definizione, storia, aspetti principali, stato attuale, prospettive."""

    def confronta_opzioni(
        self,
        opzione1: str = Field(..., description="Opzione 1"),
        opzione2: str = Field(..., description="Opzione 2"),
    ) -> str:
        """Confronta opzioni."""
        return f"""⚖️ **{opzione1}** vs **{opzione2}**

Analizza: pro/contro, casi d'uso, raccomandazione."""

    def fact_check(
        self,
        affermazione: str = Field(..., description="Affermazione"),
    ) -> str:
        """Verifica affermazione."""
        return f"""✓ **Fact Check**

"{affermazione}"

Verdetto: ✅ VERO / ⚠️ PARZIALE / ❌ FALSO
Con evidenze e fonti."""

    def spiega_come(
        self,
        cosa: str = Field(..., description="Cosa fare"),
    ) -> str:
        """Guida passo-passo."""
        return f"""📖 **Come: {cosa}**

Guida: prerequisiti, materiali, passi, consigli, troubleshooting."""

    # ==========================================
    # SEZIONE: PUBBLICAZIONE LIBRI SCIENTIFICI
    # ==========================================

    def revisiona_capitolo(
        self,
        testo: str = Field(..., description="Testo capitolo"),
        tipo: str = Field(default="completa", description="completa/grammaticale/scientifica"),
    ) -> str:
        """Revisiona capitolo scientifico."""
        return f"""📝 **Revisione {tipo}**

{testo[:1000]}{'...' if len(testo) > 1000 else ''}

Verifica: correttezza scientifica, chiarezza, linguaggio tecnico, grammatica."""

    def verifica_formula(
        self,
        formula: str = Field(..., description="Formula LaTeX"),
        contesto: str = Field(default="", description="Contesto"),
    ) -> str:
        """Verifica formula matematica."""
        return f"""🔢 **Verifica Formula**

`{formula}`
{f'Contesto: {contesto}' if contesto else ''}

Verifica: sintassi LaTeX, correttezza, notazione standard."""

    def struttura_libro(
        self,
        titolo: str = Field(..., description="Titolo"),
        argomento: str = Field(..., description="Argomento"),
        capitoli: int = Field(default=10, description="Numero capitoli"),
    ) -> str:
        """Struttura libro scientifico."""
        return f"""📚 **{titolo}**

Argomento: {argomento}
Capitoli: ~{capitoli}

Genera: frontmatter, struttura capitoli, backmatter."""

    def genera_esercizi(
        self,
        argomento: str = Field(..., description="Argomento"),
        numero: int = Field(default=10, description="Quanti"),
        con_soluzioni: bool = Field(default=True, description="Con soluzioni"),
    ) -> str:
        """Esercizi matematici."""
        return f"""✏️ **Esercizi: {argomento}**

Genera {numero} esercizi (facili/medi/difficili) {'con' if con_soluzioni else 'senza'} soluzioni."""

    def scrivi_teorema(
        self,
        enunciato: str = Field(..., description="Enunciato"),
        con_dimostrazione: bool = Field(default=True, description="Con dimostrazione"),
    ) -> str:
        """Formalizza teorema."""
        return f"""📜 **Teorema**

{enunciato}

Formalizza: enunciato preciso{', dimostrazione' if con_dimostrazione else ''}, corollari, esempi."""

    def crea_definizione(
        self,
        concetto: str = Field(..., description="Concetto"),
    ) -> str:
        """Definizione formale."""
        return f"""📐 **Definizione: {concetto}**

Crea: definizione formale, notazione, osservazioni, esempi, controesempi."""

    # ==========================================
    # SEZIONE: PRODUTTIVITÀ
    # ==========================================

    def piano_progetto(
        self,
        progetto: str = Field(..., description="Nome progetto"),
        obiettivo: str = Field(..., description="Obiettivo"),
    ) -> str:
        """Piano progetto."""
        return f"""📋 **{progetto}**

Obiettivo: {obiettivo}

Crea: fasi, task, risorse, timeline, rischi."""

    def todo_list(
        self,
        contesto: str = Field(..., description="Contesto"),
    ) -> str:
        """Lista todo."""
        return f"""✅ **Todo: {contesto}**

Genera lista con priorità (🔴🟡🟢) e tempo stimato."""

    def scrivi_email(
        self,
        scopo: str = Field(..., description="Scopo"),
        tono: str = Field(default="professionale", description="Tono"),
    ) -> str:
        """Bozza email."""
        return f"""📧 **Email** ({tono})

Scopo: {scopo}

Genera: oggetto, corpo, call to action."""

    def prepara_riunione(
        self,
        argomento: str = Field(..., description="Argomento"),
        durata: int = Field(default=60, description="Minuti"),
    ) -> str:
        """Prepara riunione."""
        return f"""📅 **Riunione: {argomento}** ({durata} min)

Genera: agenda, obiettivi, materiali."""

    def brainstorming(
        self,
        tema: str = Field(..., description="Tema"),
        idee: int = Field(default=10, description="Numero idee"),
    ) -> str:
        """Brainstorming."""
        return f"""💡 **Brainstorming: {tema}**

Genera {idee}+ idee, categorizza, identifica top 3."""

    # ==========================================
    # SEZIONE: FINANZA ITALIANA
    # ==========================================

    def calcola_irpef(
        self,
        reddito: float = Field(..., description="Reddito annuo lordo"),
        detrazioni: float = Field(default=0, description="Detrazioni"),
    ) -> str:
        """Calcola IRPEF italiana."""
        imponibile = max(0, reddito - detrazioni)
        if imponibile <= 28000:
            irpef = imponibile * 0.23
        elif imponibile <= 50000:
            irpef = 6440 + (imponibile - 28000) * 0.35
        else:
            irpef = 14140 + (imponibile - 50000) * 0.43
        netto = reddito - irpef
        return f"""💰 **IRPEF**

Reddito: €{reddito:,.2f}
Detrazioni: €{detrazioni:,.2f}
Imponibile: €{imponibile:,.2f}

**IRPEF:** €{irpef:,.2f}
**Netto annuo:** €{netto:,.2f}
**Netto mensile:** €{netto/12:,.2f}"""

    def calcola_mutuo(
        self,
        importo: float = Field(..., description="Importo"),
        tasso: float = Field(..., description="Tasso % annuo"),
        anni: int = Field(default=20, description="Anni"),
    ) -> str:
        """Calcola rata mutuo."""
        n = anni * 12
        r = tasso / 100 / 12
        rata = importo * (r * (1+r)**n) / ((1+r)**n - 1) if r > 0 else importo/n
        totale = rata * n
        return f"""🏠 **Mutuo**

Importo: €{importo:,.2f}
Tasso: {tasso}%
Durata: {anni} anni

**Rata mensile:** €{rata:,.2f}
**Totale:** €{totale:,.2f}
**Interessi:** €{totale - importo:,.2f}"""

    def analizza_investimento(
        self,
        capitale: float = Field(..., description="Capitale"),
        rendimento: float = Field(default=5, description="Rendimento % annuo"),
        anni: int = Field(default=10, description="Anni"),
    ) -> str:
        """Analisi investimento."""
        montante = capitale * (1 + rendimento/100) ** anni
        guadagno = montante - capitale
        tasse = guadagno * 0.26
        netto = montante - tasse
        return f"""📈 **Investimento**

Capitale: €{capitale:,.2f}
Rendimento: {rendimento}%
Anni: {anni}

Montante lordo: €{montante:,.2f}
Tasse (26%): €{tasse:,.2f}
**Netto finale:** €{netto:,.2f}"""

    def analizza_piva(
        self,
        fatturato: float = Field(..., description="Fatturato annuo"),
        regime: str = Field(default="forfettario", description="forfettario/ordinario"),
    ) -> str:
        """Analisi Partita IVA."""
        if regime == "forfettario":
            imponibile = fatturato * 0.78
            imposta = imponibile * 0.15
        else:
            imponibile = fatturato * 0.7
            imposta = imponibile * 0.30
        inps = imponibile * 0.26
        netto = fatturato - imposta - inps
        return f"""💼 **P.IVA {regime}**

Fatturato: €{fatturato:,.2f}
Imponibile: €{imponibile:,.2f}
Imposta: €{imposta:,.2f}
INPS: €{inps:,.2f}

**Netto annuo:** €{netto:,.2f}
**Netto mensile:** €{netto/12:,.2f}"""

    def calcola_pensione(
        self,
        eta: int = Field(..., description="Età attuale"),
        reddito: float = Field(..., description="Reddito annuo"),
        anni_contributi: int = Field(..., description="Anni contributi"),
    ) -> str:
        """Stima pensione."""
        anni_mancanti = max(0, 67 - eta)
        totale = anni_contributi + anni_mancanti
        montante = reddito * 0.33 * totale
        pensione = montante * 0.057
        return f"""👴 **Pensione stimata**

Età: {eta} → pensione a 67
Contributi: {anni_contributi} + {anni_mancanti} = {totale} anni

**Pensione lorda:** €{pensione/12:,.2f}/mese
Tasso sostituzione: {pensione/reddito*100:.1f}%"""

    def simulazione_pac(
        self,
        rata: float = Field(..., description="Rata mensile"),
        anni: int = Field(default=10, description="Anni"),
        rendimento: float = Field(default=6, description="Rendimento % annuo"),
    ) -> str:
        """Simula PAC."""
        n = anni * 12
        r = rendimento / 100 / 12
        versato = rata * n
        montante = rata * (((1+r)**n - 1) / r) * (1+r) if r > 0 else versato
        tasse = (montante - versato) * 0.26
        netto = montante - tasse
        return f"""📊 **PAC**

Rata: €{rata:,.2f}/mese × {anni} anni
Versato: €{versato:,.2f}
Montante: €{montante:,.2f}
Tasse: €{tasse:,.2f}

**Netto finale:** €{netto:,.2f}"""
