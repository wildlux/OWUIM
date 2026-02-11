#!/usr/bin/env python3
"""
MCP Bridge Service - Espone i servizi locali via Model Context Protocol
Porta: 5558

Questo servizio fa da bridge MCP per:
- TTS Service (porta 5556)
- Image Analysis Service (porta 5555)
- Document Service (porta 5557)

Permette a client MCP (Claude Desktop, etc.) di usare questi servizi.
"""

import asyncio
import json
import base64
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

# FastAPI per health check e gestione
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# MCP SDK
try:
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LATEST_PROTOCOL_VERSION
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[!] MCP SDK non installato. Installa con: pip install mcp")

import requests
from pathlib import Path

# Protezione path traversal
sys_path = str(Path(__file__).parent.parent)
if sys_path not in __import__('sys').path:
    __import__('sys').path.insert(0, sys_path)
from security import validate_path, ALLOWED_ORIGINS, get_api_key_header, SAFE_HOST

try:
    from pydantic import BaseModel, ConfigDict

    class MCPHealthResponse(BaseModel):
        model_config = ConfigDict(extra="allow")
        service: str
        version: str
        port: int
        mcp_available: bool
except ImportError:
    MCPHealthResponse = None

# Configurazione
SERVICE_PORT = 5558
TTS_SERVICE_URL = "http://localhost:5556"
IMAGE_SERVICE_URL = "http://localhost:5555"
DOCUMENT_SERVICE_URL = "http://localhost:5557"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_bridge")

# Cache directory
CACHE_DIR = Path(__file__).parent / ".mcp_cache"
CACHE_DIR.mkdir(exist_ok=True)


class ServiceBridge:
    """Bridge per comunicare con i servizi locali"""

    def __init__(self):
        self.services = {
            "tts": {"url": TTS_SERVICE_URL, "name": "TTS Service", "port": 5556},
            "image": {"url": IMAGE_SERVICE_URL, "name": "Image Analysis", "port": 5555},
            "document": {"url": DOCUMENT_SERVICE_URL, "name": "Document Service", "port": 5557}
        }

    def check_service(self, service_name: str) -> dict:
        """Verifica se un servizio è disponibile"""
        if service_name not in self.services:
            return {"available": False, "error": f"Servizio sconosciuto: {service_name}"}

        service = self.services[service_name]
        try:
            resp = requests.get(service["url"], timeout=3)
            return {
                "available": resp.status_code == 200,
                "name": service["name"],
                "port": service["port"],
                "url": service["url"]
            }
        except requests.exceptions.RequestException as e:
            return {
                "available": False,
                "name": service["name"],
                "port": service["port"],
                "error": str(e)
            }

    def check_all_services(self) -> dict:
        """Verifica tutti i servizi"""
        return {name: self.check_service(name) for name in self.services}

    # ==================== TTS Methods ====================

    def tts_speak(self, text: str, voice: str = "riccardo",
                  backend: str = "piper") -> dict:
        """Sintetizza testo in audio"""
        try:
            resp = requests.post(
                f"{TTS_SERVICE_URL}/speak",
                data={"text": text, "voice": voice, "backend": backend},
                timeout=30
            )
            if resp.status_code == 200:
                # Salva audio in cache
                audio_path = CACHE_DIR / "last_audio.mp3"
                audio_path.write_bytes(resp.content)
                return {
                    "success": True,
                    "audio_path": str(audio_path),
                    "audio_size": len(resp.content),
                    "text": text,
                    "voice": voice
                }
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tts_list_voices(self, backend: str = "edge-tts") -> dict:
        """Lista voci disponibili"""
        try:
            resp = requests.get(f"{TTS_SERVICE_URL}/voices/{backend}", timeout=10)
            if resp.status_code == 200:
                return {"success": True, "voices": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def tts_list_backends(self) -> dict:
        """Lista backend TTS disponibili"""
        try:
            resp = requests.get(f"{TTS_SERVICE_URL}/backends", timeout=5)
            if resp.status_code == 200:
                return {"success": True, "backends": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== Image Methods ====================

    def image_analyze(self, image_path: str, prompt: str = "Descrivi questa immagine in dettaglio",
                      model: str = "llava") -> dict:
        """Analizza un'immagine"""
        try:
            safe_path = validate_path(image_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(image_path).name, f, "image/png")}
                data = {"prompt": prompt, "model": model}
                resp = requests.post(
                    f"{IMAGE_SERVICE_URL}/analyze",
                    files=files,
                    data=data,
                    timeout=60
                )
            if resp.status_code == 200:
                return {"success": True, "analysis": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def image_describe(self, image_path: str) -> dict:
        """Descrizione veloce di un'immagine"""
        try:
            safe_path = validate_path(image_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(image_path).name, f, "image/png")}
                resp = requests.post(
                    f"{IMAGE_SERVICE_URL}/describe",
                    files=files,
                    timeout=30
                )
            if resp.status_code == 200:
                return {"success": True, "description": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def image_extract_text(self, image_path: str) -> dict:
        """Estrai testo da immagine (OCR)"""
        try:
            safe_path = validate_path(image_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(image_path).name, f, "image/png")}
                resp = requests.post(
                    f"{IMAGE_SERVICE_URL}/extract-text",
                    files=files,
                    timeout=30
                )
            if resp.status_code == 200:
                return {"success": True, "text": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def image_list_models(self) -> dict:
        """Lista modelli vision disponibili"""
        try:
            resp = requests.get(f"{IMAGE_SERVICE_URL}/models", timeout=5)
            if resp.status_code == 200:
                return {"success": True, "models": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== Document Methods ====================

    def document_read(self, file_path: str) -> dict:
        """Leggi un documento"""
        try:
            safe_path = validate_path(file_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                resp = requests.post(
                    f"{DOCUMENT_SERVICE_URL}/read",
                    files=files,
                    timeout=60
                )
            if resp.status_code == 200:
                return {"success": True, "content": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def document_extract_text(self, file_path: str) -> dict:
        """Estrai solo testo da documento"""
        try:
            safe_path = validate_path(file_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                resp = requests.post(
                    f"{DOCUMENT_SERVICE_URL}/extract-text",
                    files=files,
                    timeout=60
                )
            if resp.status_code == 200:
                return {"success": True, "text": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def document_summary(self, file_path: str) -> dict:
        """Riassunto di un documento"""
        try:
            safe_path = validate_path(file_path)
            with open(safe_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                resp = requests.post(
                    f"{DOCUMENT_SERVICE_URL}/summary",
                    files=files,
                    timeout=60
                )
            if resp.status_code == 200:
                return {"success": True, "summary": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def document_formats(self) -> dict:
        """Lista formati supportati"""
        try:
            resp = requests.get(f"{DOCUMENT_SERVICE_URL}/formats", timeout=5)
            if resp.status_code == 200:
                return {"success": True, "formats": resp.json()}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Inizializza bridge
bridge = ServiceBridge()

# ==================== MCP Server ====================

if MCP_AVAILABLE:
    mcp_server = Server("ollama-webui-bridge")

    @mcp_server.list_tools()
    async def list_tools() -> list[Tool]:
        """Lista tutti i tools disponibili"""
        tools = [
            # TTS Tools
            Tool(
                name="tts_speak",
                description="Sintetizza testo in audio usando il servizio TTS locale. Supporta voci italiane.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Testo da sintetizzare"
                        },
                        "voice": {
                            "type": "string",
                            "description": "Nome voce (default: it-IT-IsabellaNeural)",
                            "default": "riccardo"
                        },
                        "backend": {
                            "type": "string",
                            "description": "Backend TTS (edge-tts, gtts, piper)",
                            "default": "piper"
                        }
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="tts_list_voices",
                description="Elenca le voci disponibili per un backend TTS",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backend": {
                            "type": "string",
                            "description": "Backend TTS (default: edge-tts)",
                            "default": "piper"
                        }
                    }
                }
            ),
            Tool(
                name="tts_list_backends",
                description="Elenca i backend TTS disponibili",
                inputSchema={"type": "object", "properties": {}}
            ),

            # Image Tools
            Tool(
                name="image_analyze",
                description="Analizza un'immagine usando modelli vision (LLaVA). Richiede il percorso del file.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Percorso assoluto dell'immagine da analizzare"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Prompt per l'analisi",
                            "default": "Descrivi questa immagine in dettaglio"
                        },
                        "model": {
                            "type": "string",
                            "description": "Modello vision da usare",
                            "default": "llava"
                        }
                    },
                    "required": ["image_path"]
                }
            ),
            Tool(
                name="image_describe",
                description="Ottieni una descrizione veloce di un'immagine",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Percorso assoluto dell'immagine"
                        }
                    },
                    "required": ["image_path"]
                }
            ),
            Tool(
                name="image_extract_text",
                description="Estrai testo da un'immagine (OCR + Vision)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Percorso assoluto dell'immagine"
                        }
                    },
                    "required": ["image_path"]
                }
            ),
            Tool(
                name="image_list_models",
                description="Elenca i modelli vision disponibili",
                inputSchema={"type": "object", "properties": {}}
            ),

            # Document Tools
            Tool(
                name="document_read",
                description="Legge un documento (PDF, Word, Excel, PowerPoint, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Percorso assoluto del documento"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="document_extract_text",
                description="Estrae solo il testo da un documento",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Percorso assoluto del documento"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="document_summary",
                description="Genera un riassunto di un documento",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Percorso assoluto del documento"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="document_formats",
                description="Elenca i formati di documento supportati",
                inputSchema={"type": "object", "properties": {}}
            ),

            # Utility Tools
            Tool(
                name="check_services",
                description="Verifica lo stato di tutti i servizi locali (TTS, Image, Document)",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
        return tools

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Esegui un tool"""
        result = None

        # TTS Tools
        if name == "tts_speak":
            result = bridge.tts_speak(
                text=arguments.get("text", ""),
                voice=arguments.get("voice", "riccardo"),
                backend=arguments.get("backend", "piper")
            )
        elif name == "tts_list_voices":
            result = bridge.tts_list_voices(arguments.get("backend", "piper"))
        elif name == "tts_list_backends":
            result = bridge.tts_list_backends()

        # Image Tools
        elif name == "image_analyze":
            result = bridge.image_analyze(
                image_path=arguments.get("image_path", ""),
                prompt=arguments.get("prompt", "Descrivi questa immagine in dettaglio"),
                model=arguments.get("model", "llava")
            )
        elif name == "image_describe":
            result = bridge.image_describe(arguments.get("image_path", ""))
        elif name == "image_extract_text":
            result = bridge.image_extract_text(arguments.get("image_path", ""))
        elif name == "image_list_models":
            result = bridge.image_list_models()

        # Document Tools
        elif name == "document_read":
            result = bridge.document_read(arguments.get("file_path", ""))
        elif name == "document_extract_text":
            result = bridge.document_extract_text(arguments.get("file_path", ""))
        elif name == "document_summary":
            result = bridge.document_summary(arguments.get("file_path", ""))
        elif name == "document_formats":
            result = bridge.document_formats()

        # Utility Tools
        elif name == "check_services":
            result = bridge.check_all_services()

        else:
            result = {"error": f"Tool sconosciuto: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ==================== FastAPI App ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    logger.info(f"MCP Bridge Service avviato su porta {SERVICE_PORT}")
    logger.info(f"MCP SDK disponibile: {MCP_AVAILABLE}")
    yield
    logger.info("MCP Bridge Service terminato")

app = FastAPI(
    title="MCP Bridge Service",
    description="Bridge MCP per servizi locali (TTS, Image, Document)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Key"],
)


@app.get("/", response_model=MCPHealthResponse)
async def root():
    """Health check e info servizio"""
    services_status = bridge.check_all_services()
    return {
        "service": "MCP Bridge",
        "version": "1.0.0",
        "port": SERVICE_PORT,
        "mcp_available": MCP_AVAILABLE,
        "services": services_status,
        "tools_count": 12 if MCP_AVAILABLE else 0
    }


@app.get("/services")
async def get_services():
    """Stato dettagliato dei servizi"""
    return bridge.check_all_services()


@app.get("/tools")
async def get_tools():
    """Lista tools disponibili"""
    if not MCP_AVAILABLE:
        return {"error": "MCP SDK non installato"}

    tools = await list_tools()
    return {
        "count": len(tools),
        "tools": [{"name": t.name, "description": t.description} for t in tools]
    }


# ==================== CLI Test Endpoints ====================

_auth = get_api_key_header()


@app.post("/test/tts", dependencies=[Depends(_auth)])
async def test_tts(text: str = "Ciao, questo è un test del servizio TTS"):
    """Test TTS"""
    return bridge.tts_speak(text)


@app.post("/test/image", dependencies=[Depends(_auth)])
async def test_image(image_path: str):
    """Test analisi immagine"""
    try:
        validate_path(image_path)
    except ValueError as e:
        return {"success": False, "error": f"Accesso negato: {e}"}
    return bridge.image_analyze(image_path)


@app.post("/test/document", dependencies=[Depends(_auth)])
async def test_document(file_path: str):
    """Test lettura documento"""
    try:
        validate_path(file_path)
    except ValueError as e:
        return {"success": False, "error": f"Accesso negato: {e}"}
    return bridge.document_read(file_path)


# ==================== Main ====================

if __name__ == "__main__":
    print("=" * 60)
    print("  MCP Bridge Service")
    print("=" * 60)
    print(f"  Porta: {SERVICE_PORT}")
    print(f"  MCP SDK: {'Disponibile' if MCP_AVAILABLE else 'Non installato'}")
    print()
    print("  Servizi collegati:")
    for name, status in bridge.check_all_services().items():
        icon = "✓" if status.get("available") else "✗"
        print(f"    [{icon}] {status.get('name', name)} (:{status.get('port', '?')})")
    print()
    print(f"  API Docs: http://localhost:{SERVICE_PORT}/docs")
    print(f"  Tools:    http://localhost:{SERVICE_PORT}/tools")
    print("=" * 60)

    uvicorn.run(app, host=SAFE_HOST, port=SERVICE_PORT)
