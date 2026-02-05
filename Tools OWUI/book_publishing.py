"""
title: Assistente Pubblicazione Libri
author: Carlo
version: 1.0.0
description: Strumento per scrivere, revisionare e pubblicare libri scientifici e accademici
"""

from pydantic import BaseModel, Field
from typing import Optional


class Tools:
    def __init__(self):
        pass

    def revisiona_capitolo(
        self,
        testo: str = Field(..., description="Il testo del capitolo da revisionare"),
        tipo_revisione: str = Field(default="completa", description="Tipo: completa, grammaticale, scientifica, stile, struttura"),
        disciplina: str = Field(default="matematica", description="Disciplina: matematica, fisica, informatica, generale"),
    ) -> str:
        """
        Revisiona un capitolo di un libro scientifico.
        """
        return f"""📝 **Revisione Capitolo Scientifico**

**Tipo revisione:** {tipo_revisione}
**Disciplina:** {disciplina}

**Testo da revisionare:**
{testo}

---
**Esegui una revisione {tipo_revisione} verificando:**

1. **Correttezza scientifica**
   - Accuratezza dei concetti
   - Correttezza delle formule/dimostrazioni
   - Coerenza con la letteratura

2. **Chiarezza espositiva**
   - Logica argomentativa
   - Transizioni tra paragrafi
   - Definizioni precise

3. **Linguaggio tecnico**
   - Uso corretto della terminologia
   - Consistenza dei termini
   - Notazione appropriata

4. **Grammatica e stile**
   - Errori ortografici/grammaticali
   - Stile accademico appropriato
   - Chiarezza delle frasi

5. **Struttura**
   - Organizzazione logica
   - Bilanciamento delle sezioni
   - Presenza di tutti gli elementi necessari

**Output richiesto:**
- Testo corretto con modifiche evidenziate
- Lista delle correzioni principali
- Suggerimenti di miglioramento"""

    def verifica_formula(
        self,
        formula: str = Field(..., description="La formula matematica da verificare (in LaTeX o testo)"),
        contesto: str = Field(default="", description="Contesto in cui appare la formula"),
        verifica_dimostrazione: bool = Field(default=False, description="Se verificare anche i passaggi dimostrativi"),
    ) -> str:
        """
        Verifica la correttezza di formule e dimostrazioni matematiche.
        """
        contesto_str = f"\n**Contesto:** {contesto}" if contesto else ""
        dim_str = "\nVerifica anche i passaggi dimostrativi." if verifica_dimostrazione else ""

        return f"""🔢 **Verifica Formula Matematica**

**Formula:**
```latex
{formula}
```
{contesto_str}{dim_str}

---
**Verifica:**

1. **Sintassi LaTeX**
   - Correttezza della notazione
   - Suggerimenti di formattazione

2. **Correttezza matematica**
   - La formula è corretta?
   - Casi particolari o eccezioni

3. **Notazione standard**
   - Uso delle convenzioni standard
   - Alternative di notazione

4. **Dimensionalità** (se applicabile)
   - Coerenza delle unità
   - Analisi dimensionale

5. **Suggerimenti**
   - Eventuali semplificazioni
   - Forma equivalente più elegante

{"6. **Verifica dimostrazione**" if verifica_dimostrazione else ""}
{"   - Analisi passaggio per passaggio" if verifica_dimostrazione else ""}
{"   - Identificazione di eventuali lacune" if verifica_dimostrazione else ""}"""

    def crea_struttura_libro(
        self,
        titolo: str = Field(..., description="Titolo provvisorio del libro"),
        argomento: str = Field(..., description="Argomento principale del libro"),
        target: str = Field(default="università", description="Target: liceo, università, ricercatori, divulgazione"),
        num_capitoli: int = Field(default=10, description="Numero approssimativo di capitoli"),
    ) -> str:
        """
        Crea la struttura completa di un libro scientifico.
        """
        return f"""📚 **Struttura Libro Scientifico**

**Titolo:** {titolo}
**Argomento:** {argomento}
**Target:** {target}
**Capitoli previsti:** ~{num_capitoli}

---
**Genera una struttura completa:**

1. **Frontmatter**
   - Titolo e sottotitolo
   - Dedica (opzionale)
   - Prefazione
   - Introduzione
   - Lista simboli e notazioni
   - Prerequisiti consigliati

2. **Corpo del libro**
   Per ogni capitolo suggerisci:
   - Titolo del capitolo
   - Obiettivi di apprendimento
   - Sezioni principali
   - Teoremi/Risultati chiave
   - Esempi da includere
   - Esercizi proposti

3. **Backmatter**
   - Appendici necessarie
   - Soluzioni esercizi
   - Bibliografia
   - Indice analitico
   - Indice dei simboli

4. **Note editoriali**
   - Lunghezza stimata
   - Elementi grafici necessari
   - Suggerimenti per il layout"""

    def scrivi_introduzione(
        self,
        titolo_libro: str = Field(..., description="Titolo del libro"),
        argomento: str = Field(..., description="Argomento principale"),
        target: str = Field(default="studenti universitari", description="Pubblico target"),
        approccio: str = Field(default="", description="Approccio distintivo del libro"),
    ) -> str:
        """
        Genera una bozza di introduzione per il libro.
        """
        approccio_str = f"\n**Approccio distintivo:** {approccio}" if approccio else ""

        return f"""📖 **Introduzione al Libro**

**Titolo:** {titolo_libro}
**Argomento:** {argomento}
**Target:** {target}{approccio_str}

---
**Scrivi un'introduzione che includa:**

1. **Apertura coinvolgente**
   - Perché questo argomento è importante
   - Motivazione e contesto storico

2. **Obiettivi del libro**
   - Cosa il lettore imparerà
   - Competenze che acquisirà

3. **Struttura del libro**
   - Come è organizzato
   - Filo conduttore

4. **Prerequisiti**
   - Conoscenze necessarie
   - Come prepararsi

5. **Come usare il libro**
   - Suggerimenti di lettura
   - Ruolo degli esercizi

6. **Convenzioni adottate**
   - Notazioni
   - Struttura dei capitoli

7. **Ringraziamenti** (schema)

**Tono:** Accademico ma accessibile, che inviti alla lettura."""

    def genera_esercizi(
        self,
        argomento: str = Field(..., description="Argomento degli esercizi"),
        livello: str = Field(default="misto", description="Livello: base, intermedio, avanzato, misto"),
        numero: int = Field(default=10, description="Numero di esercizi"),
        con_soluzioni: bool = Field(default=True, description="Se includere le soluzioni"),
    ) -> str:
        """
        Genera esercizi per un libro di matematica.
        """
        sol_str = "con soluzioni dettagliate" if con_soluzioni else "senza soluzioni"

        return f"""✏️ **Generazione Esercizi**

**Argomento:** {argomento}
**Livello:** {livello}
**Numero:** {numero}
**Formato:** {sol_str}

---
**Genera {numero} esercizi che:**

1. **Struttura per ogni esercizio:**
   - **Esercizio X.Y** [Livello: ⭐/⭐⭐/⭐⭐⭐]
   - Testo dell'esercizio
   - Hint (suggerimento discreto)
   {"- Soluzione completa con passaggi" if con_soluzioni else ""}

2. **Distribuzione:**
   - 30% esercizi base (applicazione diretta)
   - 40% esercizi intermedi (ragionamento)
   - 30% esercizi avanzati (sfida)

3. **Varietà:**
   - Calcoli
   - Dimostrazioni
   - Problemi applicativi
   - Controesempi
   - Esercizi teorici

4. **Formattazione matematica:**
   - Usa notazione LaTeX
   - Figure se necessarie"""

    def crea_definizione(
        self,
        concetto: str = Field(..., description="Il concetto da definire"),
        contesto: str = Field(default="", description="Contesto matematico"),
        livello_formalita: str = Field(default="alto", description="Formalità: informale, medio, alto"),
    ) -> str:
        """
        Crea una definizione formale per un libro di matematica.
        """
        return f"""📐 **Definizione Formale**

**Concetto:** {concetto}
**Contesto:** {contesto if contesto else "(generale)"}
**Livello formalità:** {livello_formalita}

---
**Genera una definizione che includa:**

1. **Definizione formale**
   ```
   Definizione X.Y ({concetto})
   Sia... Diciamo che... se e solo se...
   ```

2. **Notazione**
   - Simboli utilizzati
   - Convenzioni

3. **Osservazioni**
   - Chiarimenti sulla definizione
   - Casi particolari

4. **Esempi**
   - Esempio che soddisfa la definizione
   - Controesempio (cosa NON è)

5. **Proprietà immediate**
   - Conseguenze dirette della definizione

6. **Collegamento con altri concetti**
   - Relazioni con definizioni correlate"""

    def scrivi_teorema(
        self,
        enunciato: str = Field(..., description="Enunciato del teorema (anche informale)"),
        con_dimostrazione: bool = Field(default=True, description="Se includere la dimostrazione"),
        stile_dim: str = Field(default="dettagliato", description="Stile dimostrazione: sketch, standard, dettagliato"),
    ) -> str:
        """
        Formatta un teorema con eventuale dimostrazione.
        """
        dim_str = f" ({stile_dim})" if con_dimostrazione else ""

        return f"""📜 **Teorema**

**Enunciato (da formalizzare):**
{enunciato}

**Con dimostrazione:** {"Sì" + dim_str if con_dimostrazione else "No"}

---
**Genera:**

1. **Teorema X.Y** (Nome, se noto)
   - Enunciato formale preciso
   - Ipotesi chiaramente separate
   - Tesi

2. **Osservazioni pre-dimostrazione**
   - Intuizione del risultato
   - Strategia dimostrativa

{"3. **Dimostrazione**" if con_dimostrazione else ""}
{"   - Passaggi logici dettagliati" if con_dimostrazione else ""}
{"   - Giustificazione di ogni passo" if con_dimostrazione else ""}
{"   - □ (fine dimostrazione)" if con_dimostrazione else ""}

{"4" if con_dimostrazione else "3"}. **Corollari**
   - Conseguenze immediate

{"5" if con_dimostrazione else "4"}. **Esempi di applicazione**
   - Come usare il teorema

{"6" if con_dimostrazione else "5"}. **Osservazioni**
   - Generalizzazioni possibili
   - Casi particolari"""

    def revisiona_bibliografia(
        self,
        bibliografia: str = Field(..., description="Lista delle referenze bibliografiche"),
        formato: str = Field(default="AMS", description="Formato: AMS, APA, Chicago, IEEE"),
    ) -> str:
        """
        Revisiona e formatta la bibliografia.
        """
        return f"""📚 **Revisione Bibliografia**

**Formato richiesto:** {formato}

**Bibliografia da revisionare:**
{bibliografia}

---
**Esegui:**

1. **Verifica completezza**
   - Autori (cognome, iniziali)
   - Titolo completo
   - Anno
   - Editore/Rivista
   - DOI/ISBN se disponibili

2. **Formattazione {formato}**
   - Applica lo stile corretto
   - Ordine alfabetico/cronologico
   - Punteggiatura corretta

3. **Consistenza**
   - Stile uniforme per tutte le voci
   - Abbreviazioni standard

4. **Citazioni consigliate**
   - Testi fondamentali mancanti
   - Riferimenti recenti da aggiungere

5. **Output finale**
   - Bibliografia corretta e formattata
   - Note su eventuali voci incomplete"""

    def genera_abstract(
        self,
        contenuto: str = Field(..., description="Breve descrizione del contenuto del libro/capitolo"),
        tipo: str = Field(default="libro", description="Tipo: libro, capitolo, articolo"),
        parole: int = Field(default=200, description="Lunghezza in parole (150-300)"),
    ) -> str:
        """
        Genera un abstract accademico.
        """
        return f"""📄 **Abstract**

**Tipo:** {tipo}
**Lunghezza:** ~{parole} parole

**Contenuto da sintetizzare:**
{contenuto}

---
**Genera un abstract che includa:**

1. **Contesto** (1-2 frasi)
   - Background del problema

2. **Obiettivo** (1 frase)
   - Scopo del lavoro

3. **Metodo/Approccio** (1-2 frasi)
   - Come viene affrontato

4. **Risultati principali** (2-3 frasi)
   - Contributi chiave

5. **Conclusioni/Impatto** (1 frase)
   - Significato del lavoro

**Keywords:** Suggerisci 5-6 parole chiave

**Stile:** Chiaro, conciso, oggettivo, tempo presente."""

    def confronta_versioni(
        self,
        versione1: str = Field(..., description="Prima versione del testo"),
        versione2: str = Field(..., description="Seconda versione del testo"),
    ) -> str:
        """
        Confronta due versioni di un testo e suggerisce la migliore.
        """
        return f"""🔄 **Confronto Versioni**

**Versione 1:**
{versione1}

**Versione 2:**
{versione2}

---
**Analisi comparativa:**

1. **Differenze principali**
   - Cosa cambia tra le versioni
   - Modifiche strutturali
   - Modifiche di contenuto

2. **Punti di forza V1**
   - ...

3. **Punti di forza V2**
   - ...

4. **Aspetti migliorabili**
   - In V1
   - In V2

5. **Raccomandazione**
   - Quale versione preferire
   - Suggerimento per versione ottimale che combini il meglio

6. **Versione consigliata**
   - Testo finale proposto"""

    def checklist_pubblicazione(
        self,
        fase: str = Field(default="pre-invio", description="Fase: scrittura, pre-invio, revisione, finale"),
    ) -> str:
        """
        Genera una checklist per la pubblicazione del libro.
        """
        return f"""✅ **Checklist Pubblicazione - Fase: {fase}**

---
**Verifica i seguenti elementi:**

**📝 Contenuto**
- [ ] Tutti i capitoli completati
- [ ] Introduzione e conclusioni scritte
- [ ] Coerenza tra capitoli
- [ ] Numerazione teoremi/definizioni corretta
- [ ] Riferimenti incrociati verificati

**🔢 Matematica**
- [ ] Formule verificate
- [ ] Dimostrazioni complete
- [ ] Notazione consistente
- [ ] Indice dei simboli aggiornato

**✏️ Esercizi**
- [ ] Esercizi per ogni capitolo
- [ ] Difficoltà progressiva
- [ ] Soluzioni corrette
- [ ] Numerazione esercizi

**📚 Bibliografia**
- [ ] Tutte le citazioni nel testo
- [ ] Formato consistente
- [ ] DOI/ISBN dove possibile
- [ ] Referenze recenti incluse

**📖 Formattazione**
- [ ] Figure numerate e referenziate
- [ ] Tabelle formattate
- [ ] LaTeX compilato senza errori
- [ ] Indice analitico completo

**📋 Materiale supplementare**
- [ ] Prefazione
- [ ] Ringraziamenti
- [ ] Lista prerequisiti
- [ ] Guida alla lettura

**🎯 Per l'editore**
- [ ] Abstract/Sinossi
- [ ] Keywords
- [ ] Bio autore
- [ ] Proposta editoriale"""
