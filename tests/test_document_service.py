"""Test per Document Reader Service (document_service/document_service.py)."""

import io
import json
import pytest


class TestDocumentHealth:
    """Test endpoint health e info."""

    def test_root_returns_200(self, document_client):
        resp = document_client.get("/")
        assert resp.status_code == 200

    def test_root_has_service_name(self, document_client):
        data = document_client.get("/").json()
        assert "service" in data
        assert "Document" in data["service"]

    def test_root_has_status_running(self, document_client):
        data = document_client.get("/").json()
        assert data["status"] == "running"

    def test_root_has_version(self, document_client):
        data = document_client.get("/").json()
        assert "version" in data

    def test_root_has_endpoints_list(self, document_client):
        data = document_client.get("/").json()
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)


class TestDocumentFormats:
    """Test endpoint formati supportati."""

    def test_formats_returns_200(self, document_client):
        resp = document_client.get("/formats")
        assert resp.status_code == 200

    def test_formats_returns_dict(self, document_client):
        data = document_client.get("/formats").json()
        assert isinstance(data, dict)


class TestDocumentRead:
    """Test endpoint lettura documenti."""

    def test_read_pdf_returns_200(self, document_client):
        fake_pdf = b"%PDF-1.4 fake content"
        resp = document_client.post(
            "/read",
            files={"file": ("test.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        assert resp.status_code == 200

    def test_read_returns_full_text(self, document_client):
        fake_pdf = b"%PDF-1.4 fake content"
        resp = document_client.post(
            "/read",
            files={"file": ("test.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        data = resp.json()
        assert "full_text" in data

    def test_read_with_cache_disabled(self, document_client):
        fake_txt = b"Hello world"
        resp = document_client.post(
            "/read",
            files={"file": ("test.txt", io.BytesIO(fake_txt), "text/plain")},
            data={"use_cache": "false"},
        )
        assert resp.status_code == 200


class TestDocumentExtract:
    """Test endpoint estrazione testo."""

    def test_extract_text_returns_200(self, document_client):
        fake_txt = b"Testo di esempio"
        resp = document_client.post(
            "/extract-text",
            files={"file": ("doc.txt", io.BytesIO(fake_txt), "text/plain")},
        )
        assert resp.status_code == 200

    def test_extract_text_has_text_field(self, document_client):
        fake_txt = b"Testo di esempio"
        resp = document_client.post(
            "/extract-text",
            files={"file": ("doc.txt", io.BytesIO(fake_txt), "text/plain")},
        )
        data = resp.json()
        assert "text" in data


class TestDocumentMetadata:
    """Test endpoint metadati."""

    def test_get_metadata_returns_200(self, document_client):
        fake_pdf = b"%PDF-1.4 fake"
        resp = document_client.post(
            "/get-metadata",
            files={"file": ("doc.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        assert resp.status_code == 200

    def test_metadata_excludes_full_text(self, document_client):
        fake_pdf = b"%PDF-1.4 fake"
        resp = document_client.post(
            "/get-metadata",
            files={"file": ("doc.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        data = resp.json()
        assert "full_text" not in data


class TestDocumentSummary:
    """Test endpoint riassunto."""

    def test_summary_returns_200(self, document_client):
        fake_txt = b"Testo lungo di esempio per il riassunto"
        resp = document_client.post(
            "/summary",
            files={"file": ("doc.txt", io.BytesIO(fake_txt), "text/plain")},
        )
        assert resp.status_code == 200

    def test_summary_has_summary_field(self, document_client):
        fake_txt = b"Testo lungo"
        resp = document_client.post(
            "/summary",
            files={"file": ("doc.txt", io.BytesIO(fake_txt), "text/plain")},
        )
        data = resp.json()
        assert "summary" in data


class TestDocumentCache:
    """Test endpoint cache."""

    def test_delete_cache_returns_200(self, document_client):
        resp = document_client.delete("/cache")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
