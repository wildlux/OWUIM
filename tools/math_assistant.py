"""
title: Assistente Matematica
author: Carlo
version: 1.0.0
description: Strumento per aiutare con calcoli e problemi matematici
"""

from pydantic import BaseModel, Field
from typing import Optional
import math
import re


class Tools:
    def __init__(self):
        pass

    def calcola(
        self,
        espressione: str = Field(..., description="L'espressione matematica da calcolare (es: 2+2, sqrt(16), 5**2)"),
    ) -> str:
        """
        Calcola un'espressione matematica.
        Supporta: +, -, *, /, ** (potenza), sqrt, sin, cos, tan, log, pi, e
        """
        try:
            # Funzioni matematiche permesse
            safe_dict = {
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "abs": abs,
                "round": round,
                "pi": math.pi,
                "e": math.e,
                "pow": pow,
            }

            # Pulisci l'espressione
            expr = espressione.replace("^", "**").replace("×", "*").replace("÷", "/")

            # Valuta in modo sicuro
            risultato = eval(expr, {"__builtins__": {}}, safe_dict)

            if isinstance(risultato, float):
                if risultato == int(risultato):
                    risultato = int(risultato)
                else:
                    risultato = round(risultato, 10)

            return f"""🔢 **Calcolo**

**Espressione:** `{espressione}`
**Risultato:** **{risultato}**"""

        except Exception as e:
            return f"""❌ **Errore nel calcolo**

**Espressione:** `{espressione}`
**Errore:** {str(e)}

**Suggerimenti:**
- Usa * per moltiplicazione
- Usa ** o ^ per potenza
- Usa sqrt(x) per radice quadrata
- Usa parentesi per raggruppare"""

    def risolvi_equazione(
        self,
        equazione: str = Field(..., description="L'equazione da risolvere (es: 2x + 5 = 15)"),
    ) -> str:
        """
        Prepara un'equazione per la risoluzione passo-passo.
        """
        return f"""📐 **Risoluzione Equazione**

**Equazione:** `{equazione}`

---
**Richiesta:** Risolvi questa equazione mostrando tutti i passaggi:

1. Identifica il tipo di equazione
2. Isola i termini con l'incognita
3. Semplifica passo per passo
4. Trova la soluzione
5. Verifica il risultato

Per favore risolvi: **{equazione}**"""

    def converti_unita(
        self,
        valore: float = Field(..., description="Il valore numerico da convertire"),
        da: str = Field(..., description="Unità di partenza (es: km, m, cm, kg, g, °C, °F)"),
        a: str = Field(..., description="Unità di arrivo"),
    ) -> str:
        """
        Converte tra diverse unità di misura.
        """
        conversioni = {
            # Lunghezza
            ("km", "m"): lambda x: x * 1000,
            ("m", "km"): lambda x: x / 1000,
            ("m", "cm"): lambda x: x * 100,
            ("cm", "m"): lambda x: x / 100,
            ("m", "mm"): lambda x: x * 1000,
            ("mm", "m"): lambda x: x / 1000,
            ("mi", "km"): lambda x: x * 1.60934,
            ("km", "mi"): lambda x: x / 1.60934,
            ("ft", "m"): lambda x: x * 0.3048,
            ("m", "ft"): lambda x: x / 0.3048,
            ("in", "cm"): lambda x: x * 2.54,
            ("cm", "in"): lambda x: x / 2.54,

            # Peso
            ("kg", "g"): lambda x: x * 1000,
            ("g", "kg"): lambda x: x / 1000,
            ("kg", "lb"): lambda x: x * 2.20462,
            ("lb", "kg"): lambda x: x / 2.20462,
            ("g", "mg"): lambda x: x * 1000,
            ("mg", "g"): lambda x: x / 1000,

            # Temperatura
            ("°C", "°F"): lambda x: x * 9/5 + 32,
            ("°F", "°C"): lambda x: (x - 32) * 5/9,
            ("°C", "K"): lambda x: x + 273.15,
            ("K", "°C"): lambda x: x - 273.15,

            # Tempo
            ("h", "min"): lambda x: x * 60,
            ("min", "h"): lambda x: x / 60,
            ("min", "s"): lambda x: x * 60,
            ("s", "min"): lambda x: x / 60,
            ("h", "s"): lambda x: x * 3600,
            ("s", "h"): lambda x: x / 3600,

            # Dati
            ("GB", "MB"): lambda x: x * 1024,
            ("MB", "GB"): lambda x: x / 1024,
            ("MB", "KB"): lambda x: x * 1024,
            ("KB", "MB"): lambda x: x / 1024,
            ("TB", "GB"): lambda x: x * 1024,
            ("GB", "TB"): lambda x: x / 1024,
        }

        chiave = (da, a)

        if chiave in conversioni:
            risultato = conversioni[chiave](valore)
            risultato = round(risultato, 6)
            return f"""🔄 **Conversione Unità**

**{valore} {da}** = **{risultato} {a}**"""
        else:
            return f"""⚠️ **Conversione non disponibile**

Da: {da} → A: {a}

**Conversioni supportate:**
- Lunghezza: km, m, cm, mm, mi, ft, in
- Peso: kg, g, mg, lb
- Temperatura: °C, °F, K
- Tempo: h, min, s
- Dati: TB, GB, MB, KB"""

    def percentuale(
        self,
        operazione: str = Field(..., description="Tipo: 'calcola' (X% di Y), 'trova' (X è che % di Y), 'variazione' (da X a Y)"),
        valore1: float = Field(..., description="Primo valore"),
        valore2: float = Field(..., description="Secondo valore"),
    ) -> str:
        """
        Esegue calcoli con le percentuali.
        """
        try:
            if operazione == "calcola":
                risultato = (valore1 / 100) * valore2
                return f"""📊 **Calcolo Percentuale**

**{valore1}% di {valore2}** = **{round(risultato, 4)}**"""

            elif operazione == "trova":
                risultato = (valore1 / valore2) * 100
                return f"""📊 **Trova Percentuale**

**{valore1}** è il **{round(risultato, 2)}%** di **{valore2}**"""

            elif operazione == "variazione":
                variazione = ((valore2 - valore1) / valore1) * 100
                segno = "+" if variazione > 0 else ""
                return f"""📊 **Variazione Percentuale**

Da **{valore1}** a **{valore2}**
Variazione: **{segno}{round(variazione, 2)}%**"""

            else:
                return """⚠️ **Operazione non riconosciuta**

Usa:
- `calcola`: per trovare X% di Y
- `trova`: per trovare che percentuale è X di Y
- `variazione`: per calcolare la variazione % da X a Y"""

        except Exception as e:
            return f"❌ Errore: {str(e)}"

    def geometria(
        self,
        figura: str = Field(..., description="Tipo: cerchio, rettangolo, triangolo, quadrato, sfera, cilindro"),
        misura1: float = Field(..., description="Prima misura (raggio, base, lato)"),
        misura2: float = Field(default=0, description="Seconda misura (altezza, se necessaria)"),
    ) -> str:
        """
        Calcola area, perimetro e volume di figure geometriche.
        """
        risultati = {}

        if figura == "cerchio":
            area = math.pi * misura1**2
            perimetro = 2 * math.pi * misura1
            risultati = {
                "Raggio": misura1,
                "Area": round(area, 4),
                "Circonferenza": round(perimetro, 4)
            }

        elif figura == "quadrato":
            area = misura1**2
            perimetro = 4 * misura1
            diagonale = misura1 * math.sqrt(2)
            risultati = {
                "Lato": misura1,
                "Area": round(area, 4),
                "Perimetro": round(perimetro, 4),
                "Diagonale": round(diagonale, 4)
            }

        elif figura == "rettangolo":
            if misura2 == 0:
                return "⚠️ Per il rettangolo serve anche l'altezza (misura2)"
            area = misura1 * misura2
            perimetro = 2 * (misura1 + misura2)
            diagonale = math.sqrt(misura1**2 + misura2**2)
            risultati = {
                "Base": misura1,
                "Altezza": misura2,
                "Area": round(area, 4),
                "Perimetro": round(perimetro, 4),
                "Diagonale": round(diagonale, 4)
            }

        elif figura == "triangolo":
            if misura2 == 0:
                return "⚠️ Per il triangolo serve anche l'altezza (misura2)"
            area = (misura1 * misura2) / 2
            risultati = {
                "Base": misura1,
                "Altezza": misura2,
                "Area": round(area, 4)
            }

        elif figura == "sfera":
            volume = (4/3) * math.pi * misura1**3
            superficie = 4 * math.pi * misura1**2
            risultati = {
                "Raggio": misura1,
                "Volume": round(volume, 4),
                "Superficie": round(superficie, 4)
            }

        elif figura == "cilindro":
            if misura2 == 0:
                return "⚠️ Per il cilindro serve anche l'altezza (misura2)"
            volume = math.pi * misura1**2 * misura2
            sup_laterale = 2 * math.pi * misura1 * misura2
            sup_totale = sup_laterale + 2 * math.pi * misura1**2
            risultati = {
                "Raggio": misura1,
                "Altezza": misura2,
                "Volume": round(volume, 4),
                "Sup. Laterale": round(sup_laterale, 4),
                "Sup. Totale": round(sup_totale, 4)
            }
        else:
            return f"""⚠️ **Figura non riconosciuta:** {figura}

**Figure supportate:**
- cerchio (misura1 = raggio)
- quadrato (misura1 = lato)
- rettangolo (misura1 = base, misura2 = altezza)
- triangolo (misura1 = base, misura2 = altezza)
- sfera (misura1 = raggio)
- cilindro (misura1 = raggio, misura2 = altezza)"""

        output = f"📐 **{figura.capitalize()}**\n\n"
        for k, v in risultati.items():
            output += f"- **{k}:** {v}\n"

        return output

    def spiega_problema(
        self,
        problema: str = Field(..., description="Il problema matematico da spiegare e risolvere"),
    ) -> str:
        """
        Richiede la spiegazione dettagliata e la risoluzione di un problema matematico.
        """
        return f"""🎓 **Risoluzione Problema Matematico**

**Problema:**
{problema}

---
**Richiesta:** Risolvi questo problema mostrando:

1. **Comprensione:** Cosa ci chiede il problema?
2. **Dati:** Quali informazioni abbiamo?
3. **Strategia:** Come possiamo risolverlo?
4. **Svolgimento:** Passaggi dettagliati con calcoli
5. **Soluzione:** Risposta finale con unità di misura
6. **Verifica:** Controllo del risultato

Per favore risolvi passo per passo: **{problema}**"""
