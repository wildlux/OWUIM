"""
title: Image Analyzer
author: Carlo
version: 1.0.0
description: Analizza immagini tramite servizio locale. Evita il bug base64 di Open WebUI convertendo immagini in descrizioni testuali.
"""

from pydantic import BaseModel, Field
from typing import Optional
import requests
import base64
import json


class Tools:
    """Tool per analizzare immagini tramite Image Analysis Service."""

    class Valves(BaseModel):
        """Configurazione del tool."""
        SERVICE_URL: str = Field(
            default="http://localhost:5555",
            description="URL del servizio Image Analysis"
        )
        DEFAULT_ANALYSIS: str = Field(
            default="complete",
            description="Tipo analisi default (complete, describe, objects, text, math, diagram, code)"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _check_service(self) -> bool:
        """Verifica se il servizio è attivo."""
        try:
            resp = requests.get(f"{self.valves.SERVICE_URL}/", timeout=5)
            return resp.status_code == 200
        except:
            return False

    def _analyze_image(self, image_data: str, analysis_type: str, custom_prompt: str = "") -> dict:
        """Invia immagine al servizio per analisi."""
        try:
            # Prepara i dati
            if image_data.startswith("data:"):
                # Estrai base64 da data URL
                _, encoded = image_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)
            else:
                # Assume sia già base64
                image_bytes = base64.b64decode(image_data)

            # Invia al servizio
            files = {"file": ("image.png", image_bytes, "image/png")}
            data = {
                "analysis_type": analysis_type,
                "custom_prompt": custom_prompt,
                "use_cache": "true"
            }

            resp = requests.post(
                f"{self.valves.SERVICE_URL}/analyze",
                files=files,
                data=data,
                timeout=60
            )

            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": f"Errore servizio: {resp.status_code} - {resp.text}"}

        except Exception as e:
            return {"error": str(e)}

    def analyze_image_url(
        self,
        image_url: str = Field(..., description="URL dell'immagine da analizzare"),
        analysis_type: str = Field(default="complete", description="Tipo: complete, describe, objects, text, math, diagram, code")
    ) -> str:
        """
        Analizza un'immagine da URL.

        Scarica l'immagine e la analizza tramite il servizio locale.
        Restituisce una descrizione testuale dettagliata.
        """
        if not self._check_service():
            return """❌ **Servizio Image Analysis non attivo**

Avvia il servizio con:
```bash
python image_service.py
```

Oppure installa le dipendenze:
```bash
pip install fastapi uvicorn Pillow requests
```"""

        try:
            # Scarica immagine
            resp = requests.get(image_url, timeout=30)
            if resp.status_code != 200:
                return f"❌ Impossibile scaricare immagine: {resp.status_code}"

            image_bytes = resp.content
            image_base64 = base64.b64encode(image_bytes).decode()

            # Analizza
            result = self._analyze_image(image_base64, analysis_type)

            if "error" in result:
                return f"❌ Errore: {result['error']}"

            return self._format_result(result)

        except Exception as e:
            return f"❌ Errore: {e}"

    def analyze_image_base64(
        self,
        image_base64: str = Field(..., description="Immagine in formato base64"),
        analysis_type: str = Field(default="complete", description="Tipo: complete, describe, objects, text, math, diagram, code")
    ) -> str:
        """
        Analizza un'immagine in formato base64.

        Utile quando l'immagine è già stata caricata o generata.
        """
        if not self._check_service():
            return """❌ **Servizio Image Analysis non attivo**

Avvia il servizio con: `python image_service.py`"""

        result = self._analyze_image(image_base64, analysis_type)

        if "error" in result:
            return f"❌ Errore: {result['error']}"

        return self._format_result(result)

    def analyze_image_file(
        self,
        file_path: str = Field(..., description="Percorso locale del file immagine"),
        analysis_type: str = Field(default="complete", description="Tipo: complete, describe, objects, text, math, diagram, code")
    ) -> str:
        """
        Analizza un file immagine locale.

        Legge il file dal disco e lo analizza.
        """
        if not self._check_service():
            return """❌ **Servizio Image Analysis non attivo**

Avvia il servizio con: `python image_service.py`"""

        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()

            image_base64 = base64.b64encode(image_bytes).decode()
            result = self._analyze_image(image_base64, analysis_type)

            if "error" in result:
                return f"❌ Errore: {result['error']}"

            return self._format_result(result)

        except FileNotFoundError:
            return f"❌ File non trovato: {file_path}"
        except Exception as e:
            return f"❌ Errore: {e}"

    def analyze_math_image(
        self,
        image_base64: str = Field(..., description="Immagine matematica in base64")
    ) -> str:
        """
        Analizza un'immagine con contenuto matematico.

        Specializzato per: grafici, formule, diagrammi, equazioni.
        Restituisce formule in LaTeX quando possibile.
        """
        if not self._check_service():
            return "❌ Servizio non attivo. Avvia: `python image_service.py`"

        result = self._analyze_image(image_base64, "math")

        if "error" in result:
            return f"❌ Errore: {result['error']}"

        return self._format_result(result, math_mode=True)

    def extract_text_from_image(
        self,
        image_base64: str = Field(..., description="Immagine con testo in base64")
    ) -> str:
        """
        Estrae tutto il testo da un'immagine.

        Usa sia Vision AI che OCR per massima accuratezza.
        Utile per screenshot, documenti, foto di testi.
        """
        if not self._check_service():
            return "❌ Servizio non attivo. Avvia: `python image_service.py`"

        result = self._analyze_image(image_base64, "text")

        if "error" in result:
            return f"❌ Errore: {result['error']}"

        # Formatta risultato specifico per estrazione testo
        output = ["📝 **Testo Estratto**\n"]

        if result.get("description"):
            output.append("**Vision AI:**")
            output.append(result["description"])
            output.append("")

        if result.get("ocr_text"):
            output.append("**OCR:**")
            output.append("```")
            output.append(result["ocr_text"])
            output.append("```")

        return "\n".join(output)

    def custom_analyze(
        self,
        image_base64: str = Field(..., description="Immagine in base64"),
        prompt: str = Field(..., description="Prompt personalizzato per l'analisi")
    ) -> str:
        """
        Analizza un'immagine con un prompt personalizzato.

        Permette di fare domande specifiche sull'immagine.
        Esempio: "Quanti oggetti rossi ci sono?" o "Che font viene usato?"
        """
        if not self._check_service():
            return "❌ Servizio non attivo. Avvia: `python image_service.py`"

        result = self._analyze_image(image_base64, "complete", custom_prompt=prompt)

        if "error" in result:
            return f"❌ Errore: {result['error']}"

        return f"""🔍 **Analisi Personalizzata**

**Prompt:** {prompt}

**Risposta:**
{result.get('description', 'Nessuna risposta')}"""

    def get_service_status(self) -> str:
        """
        Verifica lo stato del servizio Image Analysis.

        Mostra modelli disponibili e stato connessione.
        """
        try:
            resp = requests.get(f"{self.valves.SERVICE_URL}/", timeout=5)
            if resp.status_code == 200:
                info = resp.json()
                models_resp = requests.get(f"{self.valves.SERVICE_URL}/models", timeout=5)
                models = models_resp.json() if models_resp.status_code == 200 else {}

                return f"""✅ **Image Analysis Service**

**Stato:** Attivo
**URL:** {self.valves.SERVICE_URL}
**Modello Vision:** {info.get('vision_model', 'N/A')}

**Modelli Vision Disponibili:**
{chr(10).join('- ' + m for m in models.get('vision_capable', [])) or '- Nessuno (installa con: ollama pull llava)'}

**Endpoint:**
{chr(10).join('- ' + e for e in info.get('endpoints', []))}
"""
            else:
                return f"⚠️ Servizio risponde con errore: {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return """❌ **Servizio non raggiungibile**

Avvia il servizio con:
```bash
python image_service.py
```

Requisiti:
```bash
pip install fastapi uvicorn Pillow requests
ollama pull llava  # Modello vision
```"""
        except Exception as e:
            return f"❌ Errore: {e}"

    def _format_result(self, result: dict, math_mode: bool = False) -> str:
        """Formatta il risultato dell'analisi."""
        output = []

        # Header
        if result.get("from_cache"):
            output.append("📸 **Analisi Immagine** (dalla cache)\n")
        else:
            output.append("📸 **Analisi Immagine**\n")

        # Metadati
        meta = result.get("metadata", {})
        if meta:
            output.append(f"📐 **Dimensioni:** {meta.get('width', '?')}x{meta.get('height', '?')} px")
            output.append(f"📦 **Size:** {meta.get('size_kb', '?')} KB")
            output.append("")

        # Descrizione principale
        if result.get("description"):
            if math_mode:
                output.append("📐 **Analisi Matematica:**")
            else:
                output.append("📝 **Descrizione:**")
            output.append(result["description"])
            output.append("")

        # Colori dominanti
        if result.get("colors"):
            colors = result["colors"][:5]
            color_display = " ".join([f"`{c}`" for c in colors])
            output.append(f"🎨 **Colori dominanti:** {color_display}")
            output.append("")

        # OCR
        if result.get("ocr_text"):
            output.append("📖 **Testo OCR:**")
            output.append("```")
            output.append(result["ocr_text"][:500])
            if len(result["ocr_text"]) > 500:
                output.append("... (troncato)")
            output.append("```")

        return "\n".join(output)
