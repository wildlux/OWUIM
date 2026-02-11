"""Test per Image Analysis Service (image_analysis/image_service.py)."""

import io
import pytest


def _make_png_bytes():
    """Crea un PNG 1x1 minimo valido per i test."""
    # PNG minimo: header + IHDR + IDAT + IEND
    import struct
    import zlib

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    header = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)  # 1x1, 8bit, RGB
    raw_data = zlib.compress(b"\x00\xff\x00\x00")  # filter + 1 pixel RGB
    return header + chunk(b"IHDR", ihdr_data) + chunk(b"IDAT", raw_data) + chunk(b"IEND", b"")


class TestImageHealth:
    """Test endpoint health e info."""

    def test_root_returns_200(self, image_client):
        resp = image_client.get("/")
        assert resp.status_code == 200

    def test_root_has_service_name(self, image_client):
        data = image_client.get("/").json()
        assert "service" in data
        assert "Image" in data["service"]

    def test_root_has_status_running(self, image_client):
        data = image_client.get("/").json()
        assert data["status"] == "running"

    def test_root_has_endpoints_list(self, image_client):
        data = image_client.get("/").json()
        assert "endpoints" in data
        assert isinstance(data["endpoints"], list)


class TestImageModels:
    """Test endpoint modelli."""

    def test_models_returns_200(self, image_client):
        resp = image_client.get("/models")
        assert resp.status_code == 200

    def test_models_has_current(self, image_client):
        data = image_client.get("/models").json()
        assert "current_model" in data


class TestImageAnalyze:
    """Test endpoint di analisi."""

    def test_analyze_returns_200(self, image_client):
        png = _make_png_bytes()
        resp = image_client.post(
            "/analyze",
            files={"file": ("test.png", io.BytesIO(png), "image/png")},
            data={"analysis_type": "describe"}
        )
        assert resp.status_code == 200

    def test_describe_returns_200(self, image_client):
        png = _make_png_bytes()
        resp = image_client.post(
            "/describe",
            files={"file": ("test.png", io.BytesIO(png), "image/png")}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "description" in data

    def test_extract_text_returns_200(self, image_client):
        png = _make_png_bytes()
        resp = image_client.post(
            "/extract-text",
            files={"file": ("test.png", io.BytesIO(png), "image/png")}
        )
        assert resp.status_code == 200

    def test_analyze_math_returns_200(self, image_client):
        png = _make_png_bytes()
        resp = image_client.post(
            "/analyze-math",
            files={"file": ("formula.png", io.BytesIO(png), "image/png")}
        )
        assert resp.status_code == 200


class TestImageBatch:
    """Test endpoint batch."""

    def test_batch_returns_200(self, image_client):
        png = _make_png_bytes()
        resp = image_client.post(
            "/batch",
            files=[
                ("files", ("a.png", io.BytesIO(png), "image/png")),
                ("files", ("b.png", io.BytesIO(png), "image/png")),
            ],
            data={"analysis_type": "describe"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert len(data["results"]) == 2


class TestImageCache:
    """Test endpoint cache."""

    def test_delete_cache_returns_200(self, image_client):
        resp = image_client.delete("/cache")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
