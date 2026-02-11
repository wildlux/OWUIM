"""Test per TTS Local Service (tts_service/tts_local.py)."""

import json
import pytest


class TestTTSHealth:
    """Test endpoint health e info."""

    def test_root_returns_200(self, tts_client):
        resp = tts_client.get("/")
        assert resp.status_code == 200

    def test_root_has_service_name(self, tts_client):
        data = tts_client.get("/").json()
        assert "service" in data
        assert "TTS" in data["service"]

    def test_root_has_status_running(self, tts_client):
        data = tts_client.get("/").json()
        assert data["status"] == "running"

    def test_root_shows_ready(self, tts_client):
        data = tts_client.get("/").json()
        assert data["ready"] is True


class TestTTSVoices:
    """Test endpoint voci."""

    def test_voices_returns_200(self, tts_client):
        resp = tts_client.get("/voices")
        assert resp.status_code == 200

    def test_voices_has_list(self, tts_client):
        data = tts_client.get("/voices").json()
        assert "voices" in data
        assert isinstance(data["voices"], list)

    def test_voices_has_default(self, tts_client):
        data = tts_client.get("/voices").json()
        assert "default" in data

    def test_voices_check_returns_200(self, tts_client):
        resp = tts_client.get("/voices/check")
        assert resp.status_code == 200

    def test_voices_check_ready(self, tts_client):
        data = tts_client.get("/voices/check").json()
        assert data["ready"] is True
        assert isinstance(data["voices_installed"], list)


class TestTTSSpeak:
    """Test endpoint di sintesi vocale."""

    def test_speak_returns_audio(self, tts_client):
        resp = tts_client.post("/speak", data={"text": "Ciao"})
        assert resp.status_code == 200
        assert "audio" in resp.headers.get("content-type", "")

    def test_speak_with_voice(self, tts_client):
        resp = tts_client.post("/speak", data={"text": "Test", "voice": "paola"})
        assert resp.status_code == 200

    def test_test_voice_returns_json(self, tts_client):
        resp = tts_client.post("/test", data={"voice": "paola"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


class TestTTSOpenAICompat:
    """Test endpoint compatibile OpenAI."""

    def test_speech_ready_returns_200(self, tts_client):
        resp = tts_client.get("/v1/audio/speech/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["ready"] is True

    def test_openai_speech_returns_audio(self, tts_client):
        resp = tts_client.post(
            "/v1/audio/speech",
            json={"input": "Ciao mondo", "voice": "paola", "model": "tts-1"}
        )
        assert resp.status_code == 200

    def test_openai_speech_empty_text_returns_400(self, tts_client):
        resp = tts_client.post(
            "/v1/audio/speech",
            json={"input": "", "voice": "paola"}
        )
        assert resp.status_code == 400

    def test_openai_speech_maps_alloy_voice(self, tts_client):
        """Verifica che le voci OpenAI vengano mappate correttamente."""
        resp = tts_client.post(
            "/v1/audio/speech",
            json={"input": "Test mapping", "voice": "alloy"}
        )
        assert resp.status_code == 200


class TestTTSErrors:
    """Test gestione errori."""

    def test_install_unknown_voice_returns_404(self, tts_client):
        resp = tts_client.post("/install/voce_inesistente")
        assert resp.status_code == 404

    def test_openwebui_config_returns_200(self, tts_client):
        resp = tts_client.get("/openwebui-config")
        assert resp.status_code == 200
        data = resp.json()
        assert "docker_compose_env" in data
