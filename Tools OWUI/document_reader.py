"""
title: Document Reader
author: Carlo
version: 1.0.0
description: Legge documenti (PDF, Word, Excel, PowerPoint, etc.) tramite Document Reader Service locale
required_open_webui_version: 0.4.0
"""

import os
import json
import base64
import tempfile
from typing import Optional
from pydantic import BaseModel, Field

# Requests per chiamate API
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class Tools:
    """Tool per leggere documenti di vari formati via Document Reader Service."""

    class Valves(BaseModel):
        """Configurazione del tool."""
        DOCUMENT_SERVICE_URL: str = Field(
            default="http://localhost:5557",
            description="URL del Document Reader Service"
        )
        MAX_TEXT_LENGTH: int = Field(
            default=50000,
            description="Lunghezza massima del testo da restituire"
        )
        USE_CACHE: bool = Field(
            default=True,
            description="Usa cache per evitare riletture"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _check_service(self) -> bool:
        """Verifica che il Document Reader Service sia attivo."""
        try:
            resp = requests.get(f"{self.valves.DOCUMENT_SERVICE_URL}/", timeout=5)
            return resp.status_code == 200
        except:
            return False

    def _call_service(self, endpoint: str, file_bytes: bytes, filename: str, **kwargs) -> dict:
        """Chiama il Document Reader Service."""
        if not HAS_REQUESTS:
            return {"error": "Libreria 'requests' non installata. Esegui: pip install requests"}

        if not self._check_service():
            return {
                "error": f"Document Reader Service non raggiungibile su {self.valves.DOCUMENT_SERVICE_URL}",
                "solution": "Avvia il servizio: cd document_service && ./start_document_service.sh"
            }

        try:
            files = {"file": (filename, file_bytes)}
            data = {"use_cache": str(self.valves.USE_CACHE).lower()}
            data.update(kwargs)

            resp = requests.post(
                f"{self.valves.DOCUMENT_SERVICE_URL}{endpoint}",
                files=files,
                data=data,
                timeout=60
            )

            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": f"Errore servizio: {resp.status_code} - {resp.text}"}

        except requests.Timeout:
            return {"error": "Timeout nella lettura del documento"}
        except Exception as e:
            return {"error": f"Errore: {str(e)}"}

    def read_document(
        self,
        file_path: str = Field(..., description="Percorso del file documento da leggere"),
        extract_only_text: bool = Field(default=False, description="Se True, restituisce solo il testo senza metadati")
    ) -> str:
        """
        Legge un documento e restituisce il contenuto.

        Formati supportati: PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx),
        testo (.txt, .md, .csv, .json), codice sorgente, e altri.

        Args:
            file_path: Percorso del file da leggere
            extract_only_text: Se True, restituisce solo il testo

        Returns:
            Contenuto del documento in formato testuale/JSON
        """
        # Verifica esistenza file
        if not os.path.exists(file_path):
            return f"Errore: File non trovato: {file_path}"

        # Leggi file
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        except Exception as e:
            return f"Errore lettura file: {str(e)}"

        filename = os.path.basename(file_path)

        # Chiama servizio
        endpoint = "/extract-text" if extract_only_text else "/read"
        result = self._call_service(endpoint, file_bytes, filename)

        if "error" in result:
            return f"Errore: {result['error']}"

        # Formatta output
        if extract_only_text:
            text = result.get("text", "")
            if len(text) > self.valves.MAX_TEXT_LENGTH:
                text = text[:self.valves.MAX_TEXT_LENGTH] + "\n...[testo troncato]"
            return f"**{filename}** ({result.get('format', 'Documento')})\n\n{text}"
        else:
            full_text = result.get("full_text", "")
            if len(full_text) > self.valves.MAX_TEXT_LENGTH:
                result["full_text"] = full_text[:self.valves.MAX_TEXT_LENGTH] + "\n...[testo troncato]"

            return json.dumps(result, indent=2, ensure_ascii=False)

    def read_document_from_base64(
        self,
        base64_content: str = Field(..., description="Contenuto del file in base64"),
        filename: str = Field(..., description="Nome del file con estensione (es. documento.pdf)")
    ) -> str:
        """
        Legge un documento da contenuto base64.

        Utile quando il documento è già in memoria come stringa base64.

        Args:
            base64_content: Contenuto del file codificato in base64
            filename: Nome del file con estensione

        Returns:
            Contenuto del documento
        """
        try:
            file_bytes = base64.b64decode(base64_content)
        except Exception as e:
            return f"Errore decodifica base64: {str(e)}"

        result = self._call_service("/read", file_bytes, filename)

        if "error" in result:
            return f"Errore: {result['error']}"

        full_text = result.get("full_text", "")
        if len(full_text) > self.valves.MAX_TEXT_LENGTH:
            result["full_text"] = full_text[:self.valves.MAX_TEXT_LENGTH] + "\n...[testo troncato]"

        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_document_metadata(
        self,
        file_path: str = Field(..., description="Percorso del file documento")
    ) -> str:
        """
        Restituisce solo i metadati del documento (senza contenuto).

        Utile per ottenere informazioni rapide su un documento.

        Args:
            file_path: Percorso del file

        Returns:
            Metadati del documento (formato, pagine, autore, etc.)
        """
        if not os.path.exists(file_path):
            return f"Errore: File non trovato: {file_path}"

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        except Exception as e:
            return f"Errore lettura file: {str(e)}"

        filename = os.path.basename(file_path)
        result = self._call_service("/get-metadata", file_bytes, filename)

        if "error" in result:
            return f"Errore: {result['error']}"

        return json.dumps(result, indent=2, ensure_ascii=False)

    def get_document_summary(
        self,
        file_path: str = Field(..., description="Percorso del file documento"),
        max_chars: int = Field(default=2000, description="Lunghezza massima del riassunto")
    ) -> str:
        """
        Restituisce un riassunto breve del documento.

        Utile per avere una panoramica veloce del contenuto.

        Args:
            file_path: Percorso del file
            max_chars: Lunghezza massima del riassunto

        Returns:
            Riassunto del documento
        """
        if not os.path.exists(file_path):
            return f"Errore: File non trovato: {file_path}"

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        except Exception as e:
            return f"Errore lettura file: {str(e)}"

        filename = os.path.basename(file_path)
        result = self._call_service("/summary", file_bytes, filename, max_chars=str(max_chars))

        if "error" in result:
            return f"Errore: {result['error']}"

        return result.get("summary", "Nessun riassunto disponibile")

    def list_supported_formats(self) -> str:
        """
        Elenca tutti i formati di documento supportati.

        Returns:
            Lista dei formati supportati con stato disponibilità
        """
        if not self._check_service():
            return (
                "Document Reader Service non attivo.\n\n"
                "Formati supportati (quando il servizio è attivo):\n"
                "- PDF (.pdf)\n"
                "- Word (.docx, .doc)\n"
                "- Excel (.xlsx, .xls)\n"
                "- PowerPoint (.pptx, .ppt)\n"
                "- Testo (.txt, .md, .csv, .json, .xml, .html)\n"
                "- LibreOffice (.odt, .ods, .odp)\n"
                "- Codice sorgente (.py, .js, .java, etc.)\n\n"
                "Avvia il servizio: cd document_service && ./start_document_service.sh"
            )

        try:
            resp = requests.get(f"{self.valves.DOCUMENT_SERVICE_URL}/formats", timeout=5)
            if resp.status_code == 200:
                formats = resp.json()

                output = "**Formati Supportati**\n\n"

                # Raggruppa per disponibilità
                available = []
                unavailable = []

                for ext, info in formats.items():
                    entry = f"{ext} - {info['name']}"
                    if info["available"]:
                        available.append(entry)
                    else:
                        unavailable.append(entry)

                output += "**Disponibili:**\n"
                for f in sorted(available):
                    output += f"- {f}\n"

                if unavailable:
                    output += "\n**Non disponibili (dipendenze mancanti):**\n"
                    for f in sorted(unavailable):
                        output += f"- {f}\n"

                return output

        except Exception as e:
            return f"Errore: {str(e)}"

    def check_service_status(self) -> str:
        """
        Verifica lo stato del Document Reader Service.

        Returns:
            Stato del servizio con dettagli
        """
        try:
            resp = requests.get(f"{self.valves.DOCUMENT_SERVICE_URL}/", timeout=5)
            if resp.status_code == 200:
                info = resp.json()
                return (
                    f"**Document Reader Service: ATTIVO**\n\n"
                    f"- URL: {self.valves.DOCUMENT_SERVICE_URL}\n"
                    f"- Porta: {info.get('port', 5557)}\n"
                    f"- Formati disponibili: {info.get('formats_available', 'N/A')}/{info.get('formats_total', 'N/A')}\n"
                    f"- Endpoint: {', '.join(info.get('endpoints', []))}"
                )
            else:
                return f"Servizio risponde ma con errore: {resp.status_code}"
        except requests.ConnectionError:
            return (
                f"**Document Reader Service: NON ATTIVO**\n\n"
                f"URL configurato: {self.valves.DOCUMENT_SERVICE_URL}\n\n"
                f"Per avviare il servizio:\n"
                f"```bash\n"
                f"cd document_service\n"
                f"./start_document_service.sh  # Linux\n"
                f"start_document_service.bat   # Windows\n"
                f"```"
            )
        except Exception as e:
            return f"Errore verifica servizio: {str(e)}"
