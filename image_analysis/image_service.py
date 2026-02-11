#!/usr/bin/env python3
"""
Image Analysis Service - Servizio locale per analisi immagini

Analizza immagini localmente e restituisce descrizioni testuali/JSON
che possono essere usate da LLM senza problemi di base64.

Autore: Carlo
Versione: 1.0.0
Porta: 5555

Uso:
    python image_service.py                    # Avvia servizio
    curl -X POST -F "file=@image.png" http://localhost:5555/analyze
"""

import os
import sys
import json
import base64
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import threading

# FastAPI
try:
    from fastapi import FastAPI, File, UploadFile, Form, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Protezione sicurezza
_security_path = str(Path(__file__).parent.parent)
if _security_path not in sys.path:
    sys.path.insert(0, _security_path)
from security import ALLOWED_ORIGINS, create_api_key_middleware, SAFE_HOST

# Pillow per elaborazione immagini
try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Requests per Ollama
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# OCR opzionale
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


# ============================================================================
# CONFIGURAZIONE
# ============================================================================

SERVICE_PORT = 5555
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VISION_MODEL = os.getenv("VISION_MODEL", "llava")  # o llama3.2-vision, bakllava
CACHE_DIR = Path(__file__).parent / ".image_cache"
MAX_IMAGE_SIZE = 1024  # px max dimension per analisi
CACHE_EXPIRY_HOURS = 24


# ============================================================================
# CACHE
# ============================================================================

class ImageCache:
    """Cache per evitare ri-analisi di immagini già processate."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.index_file = cache_dir / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except:
                return {}
        return {}

    def _save_index(self):
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def get_hash(self, image_bytes: bytes) -> str:
        return hashlib.md5(image_bytes).hexdigest()

    def get(self, image_hash: str) -> Optional[Dict]:
        if image_hash in self.index:
            entry = self.index[image_hash]
            # Verifica scadenza
            if time.time() - entry.get("timestamp", 0) < CACHE_EXPIRY_HOURS * 3600:
                return entry.get("result")
        return None

    def set(self, image_hash: str, result: Dict):
        self.index[image_hash] = {
            "timestamp": time.time(),
            "result": result
        }
        self._save_index()

    def cleanup(self):
        """Rimuove entry scadute."""
        now = time.time()
        expired = [
            h for h, e in self.index.items()
            if now - e.get("timestamp", 0) > CACHE_EXPIRY_HOURS * 3600
        ]
        for h in expired:
            del self.index[h]
        self._save_index()
        return len(expired)


# ============================================================================
# ANALIZZATORE IMMAGINI
# ============================================================================

class ImageAnalyzer:
    """Analizza immagini usando Ollama Vision o fallback locali."""

    def __init__(self, ollama_url: str = OLLAMA_URL, model: str = VISION_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.cache = ImageCache(CACHE_DIR)
        self.available_models = []
        self._check_ollama()

    def _check_ollama(self):
        """Verifica disponibilità Ollama e modelli vision."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                self.available_models = [m["name"] for m in models]

                # Cerca modelli vision disponibili
                vision_models = ["llava", "llama3.2-vision", "bakllava", "moondream"]
                for vm in vision_models:
                    for am in self.available_models:
                        if vm in am.lower():
                            self.model = am
                            print(f"[OK] Modello vision trovato: {self.model}")
                            return True

                print(f"[!] Nessun modello vision trovato. Modelli disponibili: {self.available_models}")
                return False
        except Exception as e:
            print(f"[X] Ollama non raggiungibile: {e}")
            return False

    def _prepare_image(self, image_bytes: bytes) -> str:
        """Prepara immagine per Ollama (ridimensiona e converte in base64)."""
        img = Image.open(io.BytesIO(image_bytes))

        # Ridimensiona se troppo grande
        if max(img.size) > MAX_IMAGE_SIZE:
            ratio = MAX_IMAGE_SIZE / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # Converti in RGB se necessario
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Converti in base64
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _get_image_metadata(self, image_bytes: bytes) -> Dict:
        """Estrae metadati base dell'immagine."""
        img = Image.open(io.BytesIO(image_bytes))
        return {
            "width": img.size[0],
            "height": img.size[1],
            "format": img.format or "unknown",
            "mode": img.mode,
            "size_bytes": len(image_bytes),
            "size_kb": round(len(image_bytes) / 1024, 2)
        }

    def _analyze_colors(self, image_bytes: bytes, num_colors: int = 5) -> List[str]:
        """Analizza i colori dominanti dell'immagine."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')
            img = img.resize((100, 100))  # Riduci per velocità

            # Conta colori
            colors = img.getcolors(10000)
            if colors:
                colors.sort(key=lambda x: x[0], reverse=True)
                dominant = []
                for count, rgb in colors[:num_colors]:
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
                    dominant.append(hex_color)
                return dominant
        except:
            pass
        return []

    def _ocr_image(self, image_bytes: bytes) -> str:
        """Estrae testo dall'immagine usando OCR."""
        if not HAS_TESSERACT:
            return ""

        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img, lang='ita+eng')
            return text.strip()
        except Exception as e:
            return f"[OCR error: {e}]"

    def _analyze_with_ollama(self, image_bytes: bytes, prompt: str) -> str:
        """Analizza immagine usando Ollama Vision."""
        try:
            img_base64 = self._prepare_image(image_bytes)

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False
            }

            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )

            if resp.status_code == 200:
                return resp.json().get("response", "")
            else:
                return f"[Ollama error: {resp.status_code}]"

        except Exception as e:
            return f"[Error: {e}]"

    def analyze(
        self,
        image_bytes: bytes,
        analysis_type: str = "complete",
        custom_prompt: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Analizza un'immagine e restituisce risultati strutturati.

        Args:
            image_bytes: Bytes dell'immagine
            analysis_type: Tipo di analisi (complete, describe, objects, text, math)
            custom_prompt: Prompt personalizzato per Ollama
            use_cache: Usa cache per risultati

        Returns:
            Dict con risultati analisi
        """
        # Check cache
        img_hash = self.cache.get_hash(image_bytes)
        cache_key = f"{img_hash}_{analysis_type}"

        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                cached["from_cache"] = True
                return cached

        # Metadati base
        result = {
            "timestamp": datetime.now().isoformat(),
            "hash": img_hash,
            "analysis_type": analysis_type,
            "metadata": self._get_image_metadata(image_bytes),
            "from_cache": False
        }

        # Prompt basati sul tipo di analisi
        prompts = {
            "complete": """Analizza questa immagine in modo completo. Fornisci:
1. DESCRIZIONE: Cosa mostra l'immagine
2. OGGETTI: Lista degli oggetti/elementi visibili
3. TESTO: Qualsiasi testo leggibile nell'immagine
4. COLORI: Colori predominanti
5. CONTESTO: Possibile contesto o scopo dell'immagine

Rispondi in italiano in modo strutturato.""",

            "describe": "Descrivi questa immagine in italiano in modo dettagliato ma conciso.",

            "objects": """Elenca tutti gli oggetti e elementi visibili in questa immagine.
Formato: una lista puntata in italiano. Includi posizione relativa se rilevante.""",

            "text": """Estrai tutto il testo visibile in questa immagine.
Se è un documento, mantieni la struttura.
Se contiene formule matematiche, scrivi in LaTeX.
Rispondi solo con il testo estratto.""",

            "math": """Questa immagine contiene contenuto matematico.
1. Descrivi cosa rappresenta (grafico, formula, diagramma, etc.)
2. Se ci sono formule, trascrivile in LaTeX
3. Se è un grafico, descrivi assi, funzione, punti notevoli
4. Fornisci una spiegazione matematica del contenuto

Rispondi in italiano.""",

            "diagram": """Analizza questo diagramma/schema:
1. Tipo di diagramma (flowchart, UML, circuito, etc.)
2. Elementi principali e loro relazioni
3. Flusso o logica rappresentata
4. Eventuali etichette o annotazioni

Rispondi in italiano in modo strutturato.""",

            "code": """Se questa immagine contiene codice:
1. Identifica il linguaggio di programmazione
2. Trascrivi il codice
3. Spiega brevemente cosa fa

Se non contiene codice, descrivi cosa mostra."""
        }

        # Usa prompt personalizzato o predefinito
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = prompts.get(analysis_type, prompts["describe"])

        # Analisi con Ollama Vision
        if self.available_models:
            vision_result = self._analyze_with_ollama(image_bytes, prompt)
            result["description"] = vision_result
        else:
            result["description"] = "[Nessun modello vision disponibile. Installa llava con: ollama pull llava]"

        # Analisi aggiuntive locali
        result["colors"] = self._analyze_colors(image_bytes)

        # OCR se disponibile e richiesto
        if analysis_type in ("complete", "text", "code") and HAS_TESSERACT:
            result["ocr_text"] = self._ocr_image(image_bytes)

        # Salva in cache
        if use_cache:
            self.cache.set(cache_key, result)

        return result

    def quick_describe(self, image_bytes: bytes) -> str:
        """Descrizione veloce per uso in chat."""
        result = self.analyze(image_bytes, "describe")
        return result.get("description", "Impossibile analizzare l'immagine")


# ============================================================================
# API SERVICE
# ============================================================================

try:
    from pydantic import BaseModel, ConfigDict

    class ImageHealthResponse(BaseModel):
        model_config = ConfigDict(extra="allow")
        service: str
        status: str
        ollama_url: str
        vision_model: str

    class ModelsResponse(BaseModel):
        model_config = ConfigDict(extra="allow")
        current_model: str
        available: list
        vision_capable: list
except ImportError:
    ImageHealthResponse = None
    ModelsResponse = None


def create_app() -> FastAPI:
    """Crea l'applicazione FastAPI."""

    app = FastAPI(
        title="Image Analysis Service",
        description="Servizio locale per analisi immagini con Ollama Vision",
        version="1.0.0"
    )

    # CORS ristretto a localhost
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*", "X-API-Key"],
    )

    # API key middleware (protegge POST/PUT/DELETE)
    create_api_key_middleware(app)

    # Inizializza analyzer
    analyzer = ImageAnalyzer()

    @app.get("/", response_model=ImageHealthResponse)
    async def root():
        """Health check e info."""
        return {
            "service": "Image Analysis Service",
            "status": "running",
            "ollama_url": OLLAMA_URL,
            "vision_model": analyzer.model,
            "available_models": analyzer.available_models,
            "endpoints": [
                "POST /analyze - Analizza immagine",
                "POST /describe - Descrizione veloce",
                "POST /extract-text - Estrai testo/OCR",
                "POST /analyze-math - Analisi contenuto matematico",
                "GET /models - Lista modelli disponibili",
                "DELETE /cache - Pulisci cache"
            ]
        }

    @app.get("/models", response_model=ModelsResponse)
    async def list_models():
        """Lista modelli Ollama disponibili."""
        return {
            "current_model": analyzer.model,
            "available": analyzer.available_models,
            "vision_capable": [m for m in analyzer.available_models
                              if any(v in m.lower() for v in ["llava", "vision", "bakllava", "moondream"])]
        }

    @app.post("/analyze")
    async def analyze_image(
        file: UploadFile = File(...),
        analysis_type: str = Form(default="complete"),
        custom_prompt: str = Form(default=""),
        use_cache: bool = Form(default=True)
    ):
        """
        Analizza un'immagine e restituisce risultati strutturati.

        - **file**: File immagine (PNG, JPEG, SVG, etc.)
        - **analysis_type**: complete, describe, objects, text, math, diagram, code
        - **custom_prompt**: Prompt personalizzato opzionale
        - **use_cache**: Usa cache per risultati (default: true)
        """
        try:
            contents = await file.read()

            # Se SVG, converti prima in PNG
            if file.filename and file.filename.lower().endswith('.svg'):
                try:
                    import cairosvg
                    contents = cairosvg.svg2png(bytestring=contents)
                except ImportError:
                    raise HTTPException(400, "SVG non supportato: installa cairosvg")

            result = analyzer.analyze(
                contents,
                analysis_type=analysis_type,
                custom_prompt=custom_prompt,
                use_cache=use_cache
            )

            return JSONResponse(result)

        except Exception as e:
            raise HTTPException(500, f"Errore analisi: {str(e)}")

    @app.post("/describe")
    async def quick_describe(file: UploadFile = File(...)):
        """Descrizione veloce dell'immagine (solo testo)."""
        try:
            contents = await file.read()
            description = analyzer.quick_describe(contents)
            return {"description": description}
        except Exception as e:
            raise HTTPException(500, f"Errore: {str(e)}")

    @app.post("/extract-text")
    async def extract_text(file: UploadFile = File(...)):
        """Estrae testo dall'immagine (OCR + Vision)."""
        try:
            contents = await file.read()
            result = analyzer.analyze(contents, "text")
            return {
                "vision_text": result.get("description", ""),
                "ocr_text": result.get("ocr_text", ""),
                "combined": f"{result.get('description', '')}\n\n---\nOCR: {result.get('ocr_text', '')}"
            }
        except Exception as e:
            raise HTTPException(500, f"Errore: {str(e)}")

    @app.post("/analyze-math")
    async def analyze_math(file: UploadFile = File(...)):
        """Analizza contenuto matematico (grafici, formule, diagrammi)."""
        try:
            contents = await file.read()
            result = analyzer.analyze(contents, "math")
            return result
        except Exception as e:
            raise HTTPException(500, f"Errore: {str(e)}")

    @app.delete("/cache")
    async def clear_cache():
        """Pulisce la cache delle analisi."""
        removed = analyzer.cache.cleanup()
        return {"message": f"Cache pulita, rimosse {removed} entry scadute"}

    @app.post("/batch")
    async def batch_analyze(
        files: List[UploadFile] = File(...),
        analysis_type: str = Form(default="describe")
    ):
        """Analizza multiple immagini in batch."""
        results = []
        for file in files:
            try:
                contents = await file.read()
                result = analyzer.analyze(contents, analysis_type)
                result["filename"] = file.filename
                results.append(result)
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        return {"results": results}

    return app


# ============================================================================
# MAIN
# ============================================================================

def check_dependencies():
    """Verifica dipendenze necessarie."""
    missing = []

    if not HAS_FASTAPI:
        missing.append("fastapi uvicorn (pip install fastapi uvicorn)")
    if not HAS_PIL:
        missing.append("Pillow (pip install Pillow)")
    if not HAS_REQUESTS:
        missing.append("requests (pip install requests)")

    if missing:
        print("\n[X] Dipendenze mancanti:")
        for m in missing:
            print(f"    - {m}")
        print("\nInstalla con:")
        print("    pip install fastapi uvicorn Pillow requests")
        print("\nOpzionale per OCR:")
        print("    pip install pytesseract")
        print("    + installa Tesseract OCR sul sistema")
        return False

    return True


def main():
    """Entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          IMAGE ANALYSIS SERVICE per Open WebUI               ║
╠══════════════════════════════════════════════════════════════╣
║  Analizza immagini localmente e restituisce testo/JSON       ║
║  Evita il bug base64 di Open WebUI                           ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if not check_dependencies():
        sys.exit(1)

    print(f"[*] Ollama URL: {OLLAMA_URL}")
    print(f"[*] Modello Vision: {VISION_MODEL}")
    print(f"[*] Porta: {SERVICE_PORT}")
    print(f"[*] Cache: {CACHE_DIR}")
    print()

    # Verifica Ollama
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            vision = [m for m in models if any(v in m.lower() for v in ["llava", "vision", "bakllava"])]
            print(f"[OK] Ollama connesso. Modelli vision: {vision or 'nessuno'}")
            if not vision:
                print("[!] Installa un modello vision: ollama pull llava")
        else:
            print(f"[!] Ollama risponde ma con errore: {resp.status_code}")
    except Exception as e:
        print(f"[!] Ollama non raggiungibile: {e}")
        print("    Assicurati che Ollama sia in esecuzione")

    print()
    print(f"[*] Avvio servizio su http://localhost:{SERVICE_PORT}")
    print("[*] Premi Ctrl+C per fermare")
    print()

    # Avvia server
    app = create_app()
    uvicorn.run(app, host=SAFE_HOST, port=SERVICE_PORT, log_level="info")


if __name__ == "__main__":
    main()
