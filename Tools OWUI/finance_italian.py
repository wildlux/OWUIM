"""
title: Assistente Finanza Italiana
author: Carlo
version: 1.0.0
description: Strumento per consulenza finanziaria, fiscale e investimenti secondo normativa italiana
"""

from pydantic import BaseModel, Field
from typing import Optional
import math


class Tools:
    def __init__(self):
        pass

    def calcola_tasse_irpef(
        self,
        reddito_annuo: float = Field(..., description="Reddito annuo lordo in euro"),
        detrazioni: float = Field(default=0, description="Detrazioni fiscali totali"),
        anno: int = Field(default=2024, description="Anno fiscale di riferimento"),
    ) -> str:
        """
        Calcola l'IRPEF secondo gli scaglioni italiani vigenti.
        """
        # Scaglioni IRPEF 2024
        scaglioni = [
            (28000, 0.23),
            (50000, 0.35),
            (float('inf'), 0.43)
        ]

        reddito_imponibile = max(0, reddito_annuo - detrazioni)
        irpef = 0
        reddito_residuo = reddito_imponibile
        precedente = 0

        dettaglio_calcolo = []
        for limite, aliquota in scaglioni:
            if reddito_residuo <= 0:
                break
            scaglione = min(reddito_residuo, limite - precedente)
            imposta_scaglione = scaglione * aliquota
            irpef += imposta_scaglione
            if scaglione > 0:
                dettaglio_calcolo.append(f"  - €{scaglione:,.2f} × {aliquota*100:.0f}% = €{imposta_scaglione:,.2f}")
            reddito_residuo -= scaglione
            precedente = limite

        aliquota_media = (irpef / reddito_imponibile * 100) if reddito_imponibile > 0 else 0
        netto = reddito_annuo - irpef

        return f"""💰 **Calcolo IRPEF {anno}**

**Dati inseriti:**
- Reddito lordo: €{reddito_annuo:,.2f}
- Detrazioni: €{detrazioni:,.2f}
- Reddito imponibile: €{reddito_imponibile:,.2f}

**Calcolo per scaglioni:**
{chr(10).join(dettaglio_calcolo)}

**Risultato:**
- **IRPEF dovuta:** €{irpef:,.2f}
- **Aliquota media:** {aliquota_media:.2f}%
- **Reddito netto:** €{netto:,.2f}
- **Netto mensile (13 mensilità):** €{netto/13:,.2f}

⚠️ Calcolo indicativo. Consulta un commercialista per la situazione specifica."""

    def analizza_investimento(
        self,
        capitale: float = Field(..., description="Capitale da investire in euro"),
        rendimento_atteso: float = Field(default=5, description="Rendimento annuo atteso (%)"),
        anni: int = Field(default=10, description="Orizzonte temporale in anni"),
        tipo: str = Field(default="capitalizzazione", description="Tipo: capitalizzazione, rendita"),
    ) -> str:
        """
        Analizza un investimento con proiezioni di crescita.
        """
        # Calcolo interesse composto
        montante = capitale * (1 + rendimento_atteso/100) ** anni
        guadagno = montante - capitale

        # Tassazione capital gain Italia (26%)
        tasse_gain = guadagno * 0.26
        netto_finale = montante - tasse_gain

        # Tabella evoluzione
        evoluzione = []
        for anno in [1, 3, 5, 10, anni]:
            if anno <= anni:
                val = capitale * (1 + rendimento_atteso/100) ** anno
                evoluzione.append(f"  Anno {anno}: €{val:,.2f}")

        return f"""📈 **Analisi Investimento**

**Parametri:**
- Capitale iniziale: €{capitale:,.2f}
- Rendimento atteso: {rendimento_atteso}% annuo
- Orizzonte: {anni} anni

**Proiezione (interesse composto):**
{chr(10).join(evoluzione)}

**Risultato finale (anno {anni}):**
- Montante lordo: €{montante:,.2f}
- Guadagno lordo: €{guadagno:,.2f}
- Tasse capital gain (26%): €{tasse_gain:,.2f}
- **Montante netto:** €{netto_finale:,.2f}

**Rendimento effettivo:**
- Rendimento totale lordo: {(guadagno/capitale)*100:.2f}%
- Rendimento totale netto: {((netto_finale-capitale)/capitale)*100:.2f}%

⚠️ Proiezione basata su rendimento costante. I rendimenti passati non garantiscono quelli futuri."""

    def calcola_mutuo(
        self,
        importo: float = Field(..., description="Importo del mutuo in euro"),
        tasso: float = Field(..., description="Tasso di interesse annuo (%)"),
        anni: int = Field(default=20, description="Durata in anni"),
        tipo: str = Field(default="francese", description="Tipo ammortamento: francese, italiano"),
    ) -> str:
        """
        Calcola rata e piano di ammortamento di un mutuo.
        """
        n_rate = anni * 12
        tasso_mensile = tasso / 100 / 12

        if tipo == "francese":
            # Formula rata costante
            if tasso_mensile > 0:
                rata = importo * (tasso_mensile * (1 + tasso_mensile)**n_rate) / ((1 + tasso_mensile)**n_rate - 1)
            else:
                rata = importo / n_rate
            totale_interessi = (rata * n_rate) - importo
        else:
            # Ammortamento italiano (quota capitale costante)
            quota_capitale = importo / n_rate
            # Prima rata (la più alta)
            prima_rata = quota_capitale + (importo * tasso_mensile)
            # Ultima rata (la più bassa)
            ultima_rata = quota_capitale + (quota_capitale * tasso_mensile)
            rata = (prima_rata + ultima_rata) / 2  # Media
            totale_interessi = sum([(importo - i*quota_capitale) * tasso_mensile for i in range(n_rate)])

        totale_pagato = importo + totale_interessi

        # Prime 3 rate dettagliate
        debito_residuo = importo
        prime_rate = []
        for i in range(3):
            interesse_mese = debito_residuo * tasso_mensile
            if tipo == "francese":
                capitale_mese = rata - interesse_mese
            else:
                capitale_mese = importo / n_rate
            debito_residuo -= capitale_mese
            prime_rate.append(f"  Rata {i+1}: €{rata if tipo=='francese' else quota_capitale+interesse_mese:,.2f} (cap: €{capitale_mese:,.2f}, int: €{interesse_mese:,.2f})")

        return f"""🏠 **Calcolo Mutuo**

**Parametri:**
- Importo: €{importo:,.2f}
- Tasso: {tasso}% annuo (TAN)
- Durata: {anni} anni ({n_rate} rate)
- Ammortamento: {tipo}

**Risultato:**
- **Rata mensile:** €{rata:,.2f}
- Totale interessi: €{totale_interessi:,.2f}
- **Totale da rimborsare:** €{totale_pagato:,.2f}

**Prime rate:**
{chr(10).join(prime_rate)}

**Rapporto rata/reddito consigliato:** max 30-35%
- Reddito minimo consigliato: €{rata/0.30:,.2f}/mese

⚠️ Calcolo indicativo. Richiedi un preventivo alla banca per TAEG e spese."""

    def confronta_conti(
        self,
        saldo_medio: float = Field(..., description="Saldo medio previsto sul conto"),
        operazioni_mese: int = Field(default=20, description="Numero operazioni mensili"),
        carta_credito: bool = Field(default=True, description="Se serve carta di credito"),
    ) -> str:
        """
        Confronta tipologie di conti correnti italiani.
        """
        # Tipologie generiche di conto
        conti = [
            {
                "tipo": "Conto Online Base",
                "canone": 0,
                "ops_gratis": 999,
                "costo_op": 0,
                "carta": 0 if not carta_credito else 20,
                "bollo": 34.20 if saldo_medio > 5000 else 0
            },
            {
                "tipo": "Conto Tradizionale",
                "canone": 60,
                "ops_gratis": 50,
                "costo_op": 1.50,
                "carta": 0 if not carta_credito else 40,
                "bollo": 34.20 if saldo_medio > 5000 else 0
            },
            {
                "tipo": "Conto Premium",
                "canone": 120,
                "ops_gratis": 999,
                "costo_op": 0,
                "carta": 0,
                "bollo": 34.20 if saldo_medio > 5000 else 0
            }
        ]

        risultati = []
        for conto in conti:
            ops_extra = max(0, operazioni_mese * 12 - conto["ops_gratis"])
            costo_annuo = conto["canone"] + (ops_extra * conto["costo_op"]) + conto["carta"] + conto["bollo"]
            risultati.append(f"  - **{conto['tipo']}:** €{costo_annuo:,.2f}/anno")

        return f"""🏦 **Confronto Conti Correnti**

**Il tuo profilo:**
- Saldo medio: €{saldo_medio:,.2f}
- Operazioni/mese: {operazioni_mese}
- Carta di credito: {"Sì" if carta_credito else "No"}

**Costo annuo stimato:**
{chr(10).join(risultati)}

**Note:**
- Imposta di bollo: €34,20/anno se giacenza media > €5.000
- Confronta sempre: TAEG carte, interessi attivi/passivi, servizi inclusi

**Consiglio:** Per il tuo profilo, un conto {"online" if operazioni_mese < 30 else "premium"} potrebbe essere più conveniente."""

    def calcola_pensione(
        self,
        eta_attuale: int = Field(..., description="Età attuale"),
        reddito_annuo: float = Field(..., description="Reddito annuo lordo attuale"),
        anni_contributi: int = Field(..., description="Anni di contributi già versati"),
        sistema: str = Field(default="misto", description="Sistema: retributivo, contributivo, misto"),
    ) -> str:
        """
        Stima la pensione futura con il sistema italiano.
        """
        # Età pensionamento (stima)
        eta_pensione = 67
        anni_mancanti = max(0, eta_pensione - eta_attuale)
        anni_contributi_totali = anni_contributi + anni_mancanti

        # Calcolo semplificato sistema contributivo
        montante_contributivo = reddito_annuo * 0.33 * anni_contributi_totali
        # Coefficiente di trasformazione a 67 anni (circa 5.7%)
        coefficiente = 0.057
        pensione_annua_contributivo = montante_contributivo * coefficiente
        pensione_mensile = pensione_annua_contributivo / 12

        # Tasso di sostituzione
        tasso_sostituzione = (pensione_annua_contributivo / reddito_annuo) * 100

        return f"""👴 **Stima Pensione**

**Dati attuali:**
- Età: {eta_attuale} anni
- Reddito annuo: €{reddito_annuo:,.2f}
- Anni contributi versati: {anni_contributi}
- Sistema: {sistema}

**Proiezione:**
- Età pensionamento prevista: {eta_pensione} anni
- Anni mancanti: {anni_mancanti}
- Anni contributi totali: {anni_contributi_totali}

**Stima pensione (sistema contributivo):**
- Montante contributivo: €{montante_contributivo:,.2f}
- **Pensione lorda annua:** €{pensione_annua_contributivo:,.2f}
- **Pensione lorda mensile:** €{pensione_mensile:,.2f}
- Tasso di sostituzione: {tasso_sostituzione:.1f}%

**Gap previdenziale:**
- Reddito mensile attuale: €{reddito_annuo/12:,.2f}
- Differenza: €{reddito_annuo/12 - pensione_mensile:,.2f}/mese

💡 **Consiglio:** Considera un fondo pensione integrativo per colmare il gap.

⚠️ Stima indicativa. Consulta INPS per la tua situazione contributiva reale."""

    def analizza_p_iva(
        self,
        fatturato_annuo: float = Field(..., description="Fatturato annuo previsto"),
        costi_deducibili: float = Field(default=0, description="Costi deducibili annui"),
        regime: str = Field(default="forfettario", description="Regime: forfettario, ordinario"),
        codice_ateco: str = Field(default="generico", description="Settore attività"),
    ) -> str:
        """
        Analizza convenienza e tassazione Partita IVA.
        """
        if regime == "forfettario":
            # Coefficiente redditività medio (varia per ATECO)
            coeff_redditivita = 0.78  # Default servizi
            reddito_imponibile = fatturato_annuo * coeff_redditivita

            # Imposta sostitutiva
            aliquota = 0.15  # 5% per i primi 5 anni
            imposta = reddito_imponibile * aliquota

            # Contributi INPS gestione separata (circa 26%)
            inps = reddito_imponibile * 0.26

            netto = fatturato_annuo - imposta - inps
        else:
            # Regime ordinario semplificato
            reddito_imponibile = fatturato_annuo - costi_deducibili

            # IRPEF (scaglioni)
            if reddito_imponibile <= 28000:
                irpef = reddito_imponibile * 0.23
            elif reddito_imponibile <= 50000:
                irpef = 6440 + (reddito_imponibile - 28000) * 0.35
            else:
                irpef = 14140 + (reddito_imponibile - 50000) * 0.43

            # IRAP (3.9% circa) + Addizionali (~2%)
            altre_imposte = reddito_imponibile * 0.059
            imposta = irpef + altre_imposte

            # INPS
            inps = reddito_imponibile * 0.26

            netto = fatturato_annuo - costi_deducibili - imposta - inps

        return f"""💼 **Analisi Partita IVA**

**Parametri:**
- Fatturato annuo: €{fatturato_annuo:,.2f}
- Costi deducibili: €{costi_deducibili:,.2f}
- Regime: {regime}

**Calcolo ({regime}):**
- Reddito imponibile: €{reddito_imponibile:,.2f}
- Imposta {"sostitutiva (15%)" if regime == "forfettario" else "IRPEF + addizionali"}: €{imposta:,.2f}
- Contributi INPS (~26%): €{inps:,.2f}

**Risultato:**
- **Netto annuo:** €{netto:,.2f}
- **Netto mensile:** €{netto/12:,.2f}
- Pressione fiscale totale: {((imposta + inps) / fatturato_annuo * 100):.1f}%

**Soglia forfettario:** €85.000/anno (2024)
{"✅ Puoi accedere al regime forfettario" if fatturato_annuo <= 85000 else "⚠️ Superi la soglia del forfettario"}

💡 Confronta sempre con un commercialista la convenienza tra regimi."""

    def calcola_tfr(
        self,
        retribuzione_annua: float = Field(..., description="Retribuzione annua lorda"),
        anni_lavoro: int = Field(..., description="Anni di lavoro nell'azienda"),
        rivalutazione_media: float = Field(default=2.5, description="Rivalutazione media annua (%)"),
    ) -> str:
        """
        Calcola il TFR maturato e proiettato.
        """
        # TFR annuo = RAL / 13.5
        tfr_annuo = retribuzione_annua / 13.5

        # TFR lordo accumulato (semplificato, senza rivalutazione)
        tfr_base = tfr_annuo * anni_lavoro

        # Con rivalutazione stimata
        tfr_rivalutato = 0
        for anno in range(anni_lavoro):
            tfr_rivalutato += tfr_annuo * ((1 + rivalutazione_media/100) ** (anni_lavoro - anno))

        # Tassazione separata TFR (aliquota media ~23%)
        tasse_tfr = tfr_rivalutato * 0.23
        tfr_netto = tfr_rivalutato - tasse_tfr

        return f"""💵 **Calcolo TFR**

**Dati:**
- Retribuzione annua: €{retribuzione_annua:,.2f}
- Anni di lavoro: {anni_lavoro}
- Rivalutazione media: {rivalutazione_media}%

**Calcolo:**
- TFR annuo: €{tfr_annuo:,.2f}
- TFR base (senza rivalutazione): €{tfr_base:,.2f}
- TFR con rivalutazione: €{tfr_rivalutato:,.2f}

**Tassazione:**
- Imposta stimata (~23%): €{tasse_tfr:,.2f}
- **TFR netto stimato:** €{tfr_netto:,.2f}

**Opzioni:**
1. Lasciare in azienda (rivalutazione garantita)
2. Destinare a fondo pensione (vantaggi fiscali)
3. Anticipazione (max 70% per acquisto casa/spese mediche)

⚠️ La tassazione effettiva dipende dall'anzianità e dal reddito medio."""

    def simulazione_pac(
        self,
        rata_mensile: float = Field(..., description="Importo da investire ogni mese"),
        anni: int = Field(default=10, description="Durata del PAC in anni"),
        rendimento: float = Field(default=6, description="Rendimento medio annuo atteso (%)"),
    ) -> str:
        """
        Simula un Piano di Accumulo del Capitale (PAC).
        """
        n_versamenti = anni * 12
        totale_versato = rata_mensile * n_versamenti

        # Calcolo montante con interesse composto mensile
        r_mensile = rendimento / 100 / 12
        if r_mensile > 0:
            montante = rata_mensile * (((1 + r_mensile) ** n_versamenti - 1) / r_mensile) * (1 + r_mensile)
        else:
            montante = totale_versato

        guadagno = montante - totale_versato

        # Tasse capital gain
        tasse = guadagno * 0.26
        netto = montante - tasse

        # Milestone
        milestone = []
        for anno in [1, 3, 5, 10]:
            if anno <= anni:
                n = anno * 12
                if r_mensile > 0:
                    m = rata_mensile * (((1 + r_mensile) ** n - 1) / r_mensile) * (1 + r_mensile)
                else:
                    m = rata_mensile * n
                milestone.append(f"  Anno {anno}: €{m:,.2f} (versato: €{rata_mensile*n:,.2f})")

        return f"""📊 **Simulazione PAC**

**Parametri:**
- Rata mensile: €{rata_mensile:,.2f}
- Durata: {anni} anni ({n_versamenti} versamenti)
- Rendimento atteso: {rendimento}% annuo

**Evoluzione:**
{chr(10).join(milestone)}

**Risultato finale:**
- Totale versato: €{totale_versato:,.2f}
- Montante lordo: €{montante:,.2f}
- Guadagno lordo: €{guadagno:,.2f}
- Tasse (26%): €{tasse:,.2f}
- **Montante netto:** €{netto:,.2f}

**Rendimento:**
- Guadagno netto: €{netto - totale_versato:,.2f}
- Rendimento totale netto: {((netto - totale_versato) / totale_versato * 100):.2f}%

💡 Il PAC riduce il rischio del "market timing" mediando i prezzi di acquisto."""

    def info_bonus_fiscali(
        self,
        tipo_bonus: str = Field(default="tutti", description="Tipo: ristrutturazione, superbonus, mobili, verde, tutti"),
        anno: int = Field(default=2024, description="Anno di riferimento"),
    ) -> str:
        """
        Fornisce informazioni sui bonus fiscali italiani vigenti.
        """
        bonus_info = {
            "ristrutturazione": """**Bonus Ristrutturazione**
- Detrazione: 50% (36% dal 2025)
- Limite spesa: €96.000 per unità
- Recupero: 10 anni
- Lavori: manutenzione straordinaria, restauro, ristrutturazione""",

            "superbonus": """**Superbonus**
- Detrazione: 70% (2024), 65% (2025)
- Interventi: isolamento termico, impianti, sismabonus
- Requisiti: miglioramento 2 classi energetiche
- Opzioni: cessione credito limitata""",

            "mobili": """**Bonus Mobili**
- Detrazione: 50%
- Limite spesa: €5.000 (2024)
- Recupero: 10 anni
- Requisito: collegato a ristrutturazione""",

            "verde": """**Bonus Verde**
- Detrazione: 36%
- Limite spesa: €5.000 per unità
- Recupero: 10 anni
- Lavori: giardini, terrazzi, impianti irrigazione"""
        }

        if tipo_bonus == "tutti":
            output = "\n\n".join(bonus_info.values())
        else:
            output = bonus_info.get(tipo_bonus, "Bonus non trovato")

        return f"""🏗️ **Bonus Fiscali {anno}**

{output}

**Come usufruirne:**
1. Pagamenti tracciabili (bonifico parlante)
2. Conservare fatture e documentazione
3. Comunicazione ENEA (per energetici)
4. Dichiarazione dei redditi

⚠️ Normativa in evoluzione. Verifica sempre le disposizioni vigenti."""

    def glossario_finanziario(
        self,
        termine: str = Field(..., description="Termine finanziario da spiegare"),
    ) -> str:
        """
        Spiega termini finanziari e fiscali italiani.
        """
        return f"""📖 **Glossario Finanziario**

**Termine:** {termine}

---
**Richiesta:**
Fornisci una spiegazione completa del termine "{termine}" includendo:

1. **Definizione**
   - Significato preciso
   - Contesto di utilizzo

2. **Come funziona**
   - Meccanismo pratico
   - Esempi concreti

3. **Normativa italiana**
   - Riferimenti legislativi
   - Enti di riferimento

4. **Applicazione pratica**
   - Quando si incontra
   - Come gestirlo

5. **Termini correlati**
   - Concetti collegati
   - Differenze con termini simili

6. **Consigli pratici**
   - Come comportarsi
   - Errori da evitare"""
