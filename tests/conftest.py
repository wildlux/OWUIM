"""
Fixture condivise per la test suite.

Mocking strategy:
- PiperTTS: mock completo per evitare download modelli e dipendenza da piper
- ImageAnalyzer: mock per evitare dipendenza da Ollama e Pillow
- DocumentReader: mock per evitare dipendenze opzionali (pypdf, docx, etc.)
- ServiceBridge: mock requests per evitare servizi reali in esecuzione
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Aggiungi root del progetto al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from security import API_KEY

# Header di autenticazione per i test
AUTH_HEADERS = {"X-API-Key": API_KEY}


# ============================================================================
# TTS Service Fixtures
# ============================================================================

@pytest.fixture
def mock_piper_tts():
    """Mock di PiperTTS che simula voci installate e sintesi."""
    mock = MagicMock()
    mock.piper_path = "/usr/bin/piper"
    mock.use_python_lib = False
    mock.available_models = {
        "paola": {
            "name": "Paola",
            "gender": "F",
            "quality": "medium",
            "description": "Voce femminile, qualità media",
            "model_file": "it_IT-paola-medium.onnx",
            "config_file": "it_IT-paola-medium.onnx.json",
            "model_path": "/models/it_IT-paola-medium.onnx",
            "config_path": "/models/it_IT-paola-medium.onnx.json",
            "installed": True,
            "sample_rate": 22050,
        },
        "riccardo": {
            "name": "Riccardo",
            "gender": "M",
            "quality": "x_low",
            "description": "Voce maschile, veloce",
            "model_file": "it_IT-riccardo-x_low.onnx",
            "config_file": "it_IT-riccardo-x_low.onnx.json",
            "model_path": "/models/it_IT-riccardo-x_low.onnx",
            "config_path": "/models/it_IT-riccardo-x_low.onnx.json",
            "installed": True,
            "sample_rate": 22050,
        },
    }
    mock.is_ready.return_value = (True, "TTS pronto. Voci disponibili: paola, riccardo")
    # WAV header minimo valido
    mock.synthesize.return_value = b"RIFF" + b"\x00" * 40
    mock.synthesize_to_mp3.return_value = b"\xff\xfb\x90\x00" + b"\x00" * 40
    return mock


@pytest.fixture
def tts_app(mock_piper_tts):
    """App FastAPI TTS con PiperTTS mockato."""
    with patch.dict(sys.modules, {
        "piper": MagicMock(),
        "system_profiler": MagicMock(),
    }):
        # Mock delle importazioni opzionali nel modulo tts_local
        with patch("tts_service.tts_local.PiperTTS", return_value=mock_piper_tts):
            with patch("tts_service.tts_local.HAS_PROFILER", False):
                from tts_service.tts_local import create_app
                app = create_app()
                return app


@pytest.fixture
def tts_client(tts_app):
    """TestClient per TTS service (con API key)."""
    from fastapi.testclient import TestClient
    client = TestClient(tts_app)
    client.headers.update(AUTH_HEADERS)
    return client


# ============================================================================
# Image Service Fixtures
# ============================================================================

@pytest.fixture
def mock_image_analyzer():
    """Mock di ImageAnalyzer che simula analisi senza Ollama."""
    mock = MagicMock()
    mock.model = "llava:latest"
    mock.available_models = ["llava:latest"]
    mock.cache = MagicMock()
    mock.analyze.return_value = {
        "timestamp": "2026-02-11T12:00:00",
        "hash": "abc123",
        "analysis_type": "describe",
        "metadata": {"width": 800, "height": 600, "format": "JPEG", "mode": "RGB",
                      "size_bytes": 50000, "size_kb": 48.83},
        "description": "Una foto di test",
        "colors": ["#ffffff", "#000000"],
        "from_cache": False,
    }
    mock.quick_describe.return_value = "Una foto di test"
    return mock


@pytest.fixture
def image_app(mock_image_analyzer):
    """App FastAPI Image con analyzer mockato."""
    with patch("image_analysis.image_service.ImageAnalyzer", return_value=mock_image_analyzer):
        from image_analysis.image_service import create_app
        app = create_app()
        return app


@pytest.fixture
def image_client(image_app):
    """TestClient per Image service (con API key)."""
    from fastapi.testclient import TestClient
    client = TestClient(image_app)
    client.headers.update(AUTH_HEADERS)
    return client


# ============================================================================
# Document Service Fixtures
# ============================================================================

@pytest.fixture
def mock_document_reader():
    """Mock di DocumentReader che simula lettura senza dipendenze."""
    mock = MagicMock()
    mock.cache = MagicMock()
    mock.available_readers = {
        "pdf": True, "docx": True, "xlsx": True, "pptx": True,
        "text": True, "csv": True, "json": True, "xml": True,
        "code": True, "yaml": True, "markdown": True, "html": True,
        "image": True, "libreoffice": False, "gimp": False,
        "svg": False, "raw": False, "epub": False, "ebook": False,
    }
    mock.read.return_value = {
        "format": "PDF",
        "pages": 3,
        "metadata": {"title": "Test Doc"},
        "full_text": "Contenuto di test del documento.",
        "filename": "test.pdf",
        "extension": ".pdf",
        "size_bytes": 1024,
        "size_kb": 1.0,
        "hash": "abc123",
        "timestamp": "2026-02-11T12:00:00",
        "from_cache": False,
    }
    mock.get_summary.return_value = "[PDF] test.pdf\n\nContenuto di test."
    mock.get_supported_formats.return_value = {
        ".pdf": {"name": "PDF Document", "available": True},
        ".docx": {"name": "Word Document", "available": True},
        ".txt": {"name": "Plain Text", "available": True},
    }
    mock.cache.cleanup.return_value = 2
    return mock


@pytest.fixture
def document_app(mock_document_reader):
    """App FastAPI Document con reader mockato."""
    with patch("document_service.document_service.DocumentReader", return_value=mock_document_reader):
        from document_service.document_service import create_app
        app = create_app()
        return app


@pytest.fixture
def document_client(document_app):
    """TestClient per Document service (con API key)."""
    from fastapi.testclient import TestClient
    client = TestClient(document_app)
    client.headers.update(AUTH_HEADERS)
    return client


# ============================================================================
# MCP Service Fixtures
# ============================================================================

@pytest.fixture
def mock_service_bridge():
    """Mock di ServiceBridge che simula servizi senza connessioni reali."""
    mock = MagicMock()
    mock.services = {
        "tts": {"url": "http://localhost:5556", "name": "TTS Service", "port": 5556},
        "image": {"url": "http://localhost:5555", "name": "Image Analysis", "port": 5555},
        "document": {"url": "http://localhost:5557", "name": "Document Service", "port": 5557},
    }
    mock.check_all_services.return_value = {
        "tts": {"available": True, "name": "TTS Service", "port": 5556, "url": "http://localhost:5556"},
        "image": {"available": True, "name": "Image Analysis", "port": 5555, "url": "http://localhost:5555"},
        "document": {"available": True, "name": "Document Service", "port": 5557, "url": "http://localhost:5557"},
    }
    mock.check_service.return_value = {"available": True, "name": "TTS Service", "port": 5556}
    mock.tts_speak.return_value = {"success": True, "audio_path": "/tmp/audio.mp3", "audio_size": 1024}
    mock.tts_list_voices.return_value = {"success": True, "voices": []}
    mock.tts_list_backends.return_value = {"success": True, "backends": []}
    mock.image_list_models.return_value = {"success": True, "models": {"current_model": "llava"}}
    mock.document_formats.return_value = {"success": True, "formats": {}}
    return mock


@pytest.fixture
def mcp_client_noauth(mock_service_bridge):
    """TestClient per MCP service SENZA API key (per test sicurezza)."""
    with patch("mcp_service.mcp_service.bridge", mock_service_bridge):
        from mcp_service.mcp_service import app
        from fastapi.testclient import TestClient
        yield TestClient(app)


@pytest.fixture
def tts_client_noauth(tts_app):
    """TestClient TTS SENZA API key."""
    from fastapi.testclient import TestClient
    return TestClient(tts_app)


@pytest.fixture
def image_client_noauth(image_app):
    """TestClient Image SENZA API key."""
    from fastapi.testclient import TestClient
    return TestClient(image_app)


@pytest.fixture
def document_client_noauth(document_app):
    """TestClient Document SENZA API key."""
    from fastapi.testclient import TestClient
    return TestClient(document_app)


@pytest.fixture
def mcp_client(mock_service_bridge):
    """TestClient per MCP service (con API key)."""
    with patch("mcp_service.mcp_service.bridge", mock_service_bridge):
        from mcp_service.mcp_service import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        client.headers.update(AUTH_HEADERS)
        yield client
