"""Test per config.py - Configurazione centralizzata."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PORT_WEBUI, PORT_OLLAMA, PORT_TTS, PORT_IMAGE, PORT_DOCUMENT, PORT_MCP,
    URL_WEBUI, URL_OLLAMA, URL_TTS, URL_IMAGE, URL_DOCUMENT, URL_MCP,
    SERVICES, ServiceInfo, APP_VERSION, APP_NAME,
)


class TestPorts:
    """Verifica che le porte siano numeri interi validi."""

    def test_ports_are_integers(self):
        for port in [PORT_WEBUI, PORT_OLLAMA, PORT_TTS, PORT_IMAGE, PORT_DOCUMENT, PORT_MCP]:
            assert isinstance(port, int)

    def test_ports_in_valid_range(self):
        for port in [PORT_WEBUI, PORT_OLLAMA, PORT_TTS, PORT_IMAGE, PORT_DOCUMENT, PORT_MCP]:
            assert 1 <= port <= 65535

    def test_default_port_values(self):
        # Se non ci sono env override, verifica i default
        if "OWUI_PORT_TTS" not in os.environ:
            assert PORT_TTS == 5556
        if "OWUI_PORT_IMAGE" not in os.environ:
            assert PORT_IMAGE == 5555
        if "OWUI_PORT_DOCUMENT" not in os.environ:
            assert PORT_DOCUMENT == 5557
        if "OWUI_PORT_MCP" not in os.environ:
            assert PORT_MCP == 5558


class TestURLs:
    """Verifica formato URL."""

    def test_urls_start_with_http(self):
        for url in [URL_WEBUI, URL_OLLAMA, URL_TTS, URL_IMAGE, URL_DOCUMENT, URL_MCP]:
            assert url.startswith("http://")

    def test_urls_contain_port(self):
        assert str(PORT_TTS) in URL_TTS
        assert str(PORT_IMAGE) in URL_IMAGE
        assert str(PORT_DOCUMENT) in URL_DOCUMENT


class TestServiceInfo:
    """Verifica dataclass ServiceInfo."""

    def test_service_info_fields(self):
        svc = ServiceInfo("test", "Test Service", "T", 8080, "http://localhost:8080", "test.py")
        assert svc.name == "test"
        assert svc.label == "Test Service"
        assert svc.port == 8080

    def test_service_info_health_url(self):
        svc = ServiceInfo("test", "Test", "T", 8080, "http://localhost:8080", "test.py")
        assert svc.health_url == "http://localhost:8080/"

    def test_services_registry_has_all_services(self):
        expected_keys = {"tts", "image", "document", "mcp"}
        assert set(SERVICES.keys()) == expected_keys

    def test_services_registry_types(self):
        for key, svc in SERVICES.items():
            assert isinstance(svc, ServiceInfo)
            assert isinstance(svc.port, int)


class TestAppMetadata:
    """Verifica metadati applicazione."""

    def test_app_version_format(self):
        parts = APP_VERSION.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_app_name_not_empty(self):
        assert len(APP_NAME) > 0
