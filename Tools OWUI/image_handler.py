"""
title: Image Handler
author: Carlo
version: 1.0.0
description: Gestisce immagini evitando il bug base64 di Open WebUI. Salva su file invece di usare base64 inline.
"""

from pydantic import BaseModel, Field
from typing import Optional
import base64
import os
import hashlib
import time
from pathlib import Path


class Tools:
    """Tool per gestire immagini senza causare loop ciclici."""

    class Valves(BaseModel):
        """Configurazioni."""
        IMAGE_DIR: str = Field(
            default="/app/backend/data/images",
            description="Directory per salvare le immagini"
        )
        IMAGE_URL_PREFIX: str = Field(
            default="/api/v1/files/images",
            description="URL prefix per accedere alle immagini"
        )
        MAX_BASE64_LENGTH: int = Field(
            default=50000,
            description="Lunghezza massima base64 prima di salvare su file"
        )
        CLEANUP_HOURS: int = Field(
            default=24,
            description="Ore dopo cui eliminare immagini vecchie"
        )

    def __init__(self):
        self.valves = self.Valves()
        self._ensure_image_dir()

    def _ensure_image_dir(self):
        """Crea la directory immagini se non esiste."""
        try:
            Path(self.valves.IMAGE_DIR).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Impossibile creare directory immagini: {e}")

    def _generate_filename(self, content: bytes, extension: str = "png") -> str:
        """Genera nome file univoco basato su hash del contenuto."""
        content_hash = hashlib.md5(content).hexdigest()[:12]
        timestamp = int(time.time())
        return f"img_{timestamp}_{content_hash}.{extension}"

    def save_base64_image(
        self,
        base64_data: str = Field(..., description="Dati immagine in base64 (con o senza prefisso data:image/...)"),
        filename: str = Field(default="", description="Nome file opzionale (auto-generato se vuoto)")
    ) -> str:
        """
        Salva un'immagine base64 su file per evitare il bug del loop ciclico.

        Restituisce il percorso del file salvato o un messaggio di errore.
        """
        try:
            # Rimuovi prefisso data:image/xxx;base64, se presente
            if "base64," in base64_data:
                base64_data = base64_data.split("base64,")[1]

            # Pulisci whitespace
            base64_data = base64_data.strip().replace("\n", "").replace(" ", "")

            # Decodifica
            image_bytes = base64.b64decode(base64_data)

            # Genera nome file
            if not filename:
                filename = self._generate_filename(image_bytes)

            # Percorso completo
            filepath = os.path.join(self.valves.IMAGE_DIR, filename)

            # Salva
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            return f"""✅ **Immagine salvata**

**File:** `{filename}`
**Dimensione:** {len(image_bytes):,} bytes
**Percorso:** `{filepath}`

Per visualizzare: apri il file direttamente o usa un browser."""

        except Exception as e:
            return f"❌ Errore salvataggio: {e}"

    def convert_base64_to_small(
        self,
        base64_data: str = Field(..., description="Dati immagine base64"),
        quality: int = Field(default=50, description="Qualità JPEG (1-100)"),
        max_size: int = Field(default=400, description="Dimensione massima lato lungo in pixel")
    ) -> str:
        """
        Converte e comprime un'immagine base64 per renderla compatibile con Open WebUI.

        Riduce dimensioni e qualità per evitare il bug del loop ciclico.
        """
        try:
            from PIL import Image
            import io

            # Rimuovi prefisso
            if "base64," in base64_data:
                base64_data = base64_data.split("base64,")[1]

            base64_data = base64_data.strip().replace("\n", "").replace(" ", "")

            # Decodifica
            image_bytes = base64.b64decode(base64_data)

            # Apri immagine
            img = Image.open(io.BytesIO(image_bytes))

            # Ridimensiona
            ratio = min(max_size / max(img.size), 1.0)
            if ratio < 1.0:
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Converti in RGB se necessario (per JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Comprimi in JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            compressed = buffer.getvalue()

            # Codifica in base64
            new_base64 = base64.b64encode(compressed).decode('utf-8')

            # Verifica lunghezza
            if len(new_base64) > self.valves.MAX_BASE64_LENGTH:
                return f"""⚠️ **Immagine ancora troppo grande**

Dimensione base64: {len(new_base64):,} caratteri
Limite: {self.valves.MAX_BASE64_LENGTH:,} caratteri

Prova con:
- `quality` più basso (es. 30)
- `max_size` più piccolo (es. 200)

Oppure usa `save_base64_image` per salvare su file."""

            # Restituisci immagine compressa
            return f"""✅ **Immagine compressa**

**Originale:** {len(image_bytes):,} bytes
**Compresso:** {len(compressed):,} bytes
**Riduzione:** {(1 - len(compressed)/len(image_bytes))*100:.1f}%
**Dimensioni:** {img.size[0]}x{img.size[1]} px

---

![Immagine](data:image/jpeg;base64,{new_base64})"""

        except ImportError:
            return "❌ Richiede Pillow: `pip install Pillow`"
        except Exception as e:
            return f"❌ Errore conversione: {e}"

    def check_base64_compatibility(
        self,
        base64_data: str = Field(..., description="Dati base64 da verificare")
    ) -> str:
        """
        Verifica se un'immagine base64 è compatibile con Open WebUI.

        Controlla dimensioni e formato per evitare il bug del loop.
        """
        try:
            # Rimuovi prefisso
            clean_data = base64_data
            format_detected = "sconosciuto"

            if "base64," in base64_data:
                prefix = base64_data.split("base64,")[0]
                clean_data = base64_data.split("base64,")[1]
                if "png" in prefix:
                    format_detected = "PNG"
                elif "jpeg" in prefix or "jpg" in prefix:
                    format_detected = "JPEG"
                elif "gif" in prefix:
                    format_detected = "GIF"
                elif "webp" in prefix:
                    format_detected = "WebP"
                elif "svg" in prefix:
                    format_detected = "SVG ⚠️"

            clean_data = clean_data.strip().replace("\n", "").replace(" ", "")

            # Statistiche
            length = len(clean_data)
            decoded_size = len(base64.b64decode(clean_data))

            # Valutazione
            is_compatible = True
            warnings = []

            if length > self.valves.MAX_BASE64_LENGTH:
                is_compatible = False
                warnings.append(f"❌ Base64 troppo lungo: {length:,} > {self.valves.MAX_BASE64_LENGTH:,}")

            if format_detected == "SVG ⚠️":
                is_compatible = False
                warnings.append("❌ SVG non supportato da Open WebUI")

            if decoded_size > 500000:  # 500KB
                warnings.append(f"⚠️ File grande ({decoded_size/1024:.0f} KB) - potrebbe causare lentezza")

            status = "✅ Compatibile" if is_compatible else "❌ Non compatibile"

            return f"""📊 **Analisi Immagine Base64**

**Stato:** {status}
**Formato:** {format_detected}
**Lunghezza base64:** {length:,} caratteri
**Dimensione file:** {decoded_size:,} bytes ({decoded_size/1024:.1f} KB)

**Soglia sicura:** {self.valves.MAX_BASE64_LENGTH:,} caratteri

{chr(10).join(warnings) if warnings else '✅ Nessun problema rilevato'}

---

**Soluzioni se non compatibile:**
1. `convert_base64_to_small` - Comprimi l'immagine
2. `save_base64_image` - Salva su file"""

        except Exception as e:
            return f"❌ Errore analisi: {e}"

    def cleanup_old_images(
        self,
        hours: int = Field(default=24, description="Elimina immagini più vecchie di N ore")
    ) -> str:
        """
        Elimina immagini temporanee più vecchie del tempo specificato.
        """
        try:
            import time

            now = time.time()
            cutoff = now - (hours * 3600)
            deleted = 0
            kept = 0

            image_dir = Path(self.valves.IMAGE_DIR)
            if not image_dir.exists():
                return "📁 Directory immagini non esiste"

            for f in image_dir.iterdir():
                if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    if f.stat().st_mtime < cutoff:
                        f.unlink()
                        deleted += 1
                    else:
                        kept += 1

            return f"""🧹 **Pulizia completata**

**Eliminate:** {deleted} immagini (>{hours}h)
**Mantenute:** {kept} immagini recenti"""

        except Exception as e:
            return f"❌ Errore pulizia: {e}"
