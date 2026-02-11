"""Test per MCP Bridge Service (mcp_service/mcp_service.py)."""

import pytest


class TestMCPHealth:
    """Test endpoint health e info."""

    def test_root_returns_200(self, mcp_client):
        resp = mcp_client.get("/")
        assert resp.status_code == 200

    def test_root_has_service_name(self, mcp_client):
        data = mcp_client.get("/").json()
        assert "service" in data
        assert "MCP" in data["service"]

    def test_root_has_version(self, mcp_client):
        data = mcp_client.get("/").json()
        assert "version" in data


class TestMCPServices:
    """Test endpoint stato servizi."""

    def test_services_returns_200(self, mcp_client):
        resp = mcp_client.get("/services")
        assert resp.status_code == 200

    def test_services_has_all_three(self, mcp_client):
        data = mcp_client.get("/services").json()
        assert "tts" in data
        assert "image" in data
        assert "document" in data


class TestMCPTest:
    """Test endpoint di test."""

    def test_tts_test_returns_200(self, mcp_client):
        resp = mcp_client.post("/test/tts?text=Ciao")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
