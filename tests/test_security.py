"""Test per il modulo security.py - validazione path, CORS, API key."""

import os
import tempfile
from pathlib import Path

import pytest

from security import (
    validate_path, add_allowed_dir, get_allowed_dirs, _ALLOWED_DIRS,
    ALLOWED_ORIGINS, API_KEY, verify_api_key,
)


@pytest.fixture
def safe_file(tmp_path):
    """Crea un file temporaneo in /tmp (directory permessa)."""
    f = tmp_path / "test_file.txt"
    f.write_text("contenuto di test")
    return f


@pytest.fixture
def restore_allowed_dirs():
    """Ripristina la whitelist dopo il test."""
    original = list(_ALLOWED_DIRS)
    yield
    _ALLOWED_DIRS.clear()
    _ALLOWED_DIRS.extend(original)


class TestValidatePath:
    """Test per validate_path()."""

    def test_path_sicuro_in_home(self):
        """Path dentro la home directory -> OK."""
        # Usa un file che esiste sicuramente
        home = Path.home()
        # Cerca un file qualsiasi nella home
        for item in home.iterdir():
            if item.is_file() and not any(
                p in str(item).lower() for p in [".ssh", ".gnupg", ".env", ".netrc",
                                                  ".aws", "shadow", "passwd",
                                                  "id_rsa", "id_ed25519",
                                                  "known_hosts", "credentials",
                                                  "token", "secret", ".pem",
                                                  ".key", ".gpg", ".git/config",
                                                  "sudoers"]
            ):
                result = validate_path(str(item))
                assert result == item.resolve()
                return
        pytest.skip("Nessun file sicuro trovato nella home")

    def test_path_in_tmp(self, safe_file):
        """Path in /tmp -> OK."""
        result = validate_path(str(safe_file))
        assert result == safe_file.resolve()

    def test_path_vuoto(self):
        """Path vuoto -> ValueError."""
        with pytest.raises(ValueError, match="Path vuoto"):
            validate_path("")

    def test_path_spazi(self):
        """Path solo spazi -> ValueError."""
        with pytest.raises(ValueError, match="Path vuoto"):
            validate_path("   ")

    def test_path_etc_shadow(self):
        """Path a /etc/shadow -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path("/etc/shadow")

    def test_path_ssh_id_rsa(self):
        """Path a .ssh/id_rsa -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path(str(Path.home() / ".ssh" / "id_rsa"))

    def test_path_gnupg(self):
        """Path a .gnupg -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path(str(Path.home() / ".gnupg" / "pubring.gpg"))

    def test_path_env(self):
        """Path a .env -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path(str(Path.home() / "progetto" / ".env"))

    def test_path_traversal(self):
        """Path con ../ che punta fuori dalla whitelist -> BLOCCATO."""
        with pytest.raises(ValueError):
            validate_path("/tmp/../../etc/hostname")

    def test_path_fuori_whitelist(self):
        """Path fuori dalla whitelist -> BLOCCATO."""
        with pytest.raises(ValueError, match="non e' in una directory consentita"):
            validate_path("/usr/bin/ls")

    def test_path_inesistente(self):
        """Path che non esiste -> ValueError."""
        with pytest.raises(ValueError, match="File non trovato"):
            validate_path(str(Path.home() / "file_che_non_esiste_xyz123.txt"))

    def test_symlink_fuori_whitelist(self, tmp_path):
        """Symlink che punta fuori dalla whitelist -> BLOCCATO."""
        link = tmp_path / "evil_link"
        try:
            link.symlink_to("/usr/bin/ls")
        except OSError:
            pytest.skip("Impossibile creare symlink")
        with pytest.raises(ValueError, match="non e' in una directory consentita"):
            validate_path(str(link))

    def test_pattern_passwd(self):
        """Path con 'passwd' -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path("/etc/passwd")

    def test_pattern_credentials(self):
        """Path con 'credentials' -> BLOCCATO."""
        with pytest.raises(ValueError, match="pattern sensibile"):
            validate_path(str(Path.home() / ".aws" / "credentials"))


class TestAddAllowedDir:
    """Test per add_allowed_dir() e get_allowed_dirs()."""

    def test_add_allowed_dir(self, restore_allowed_dirs):
        """Aggiungere una directory alla whitelist."""
        custom_dir = Path("/opt/custom")
        add_allowed_dir(custom_dir)
        assert custom_dir.resolve() in get_allowed_dirs()

    def test_add_allowed_dir_duplicato(self, restore_allowed_dirs):
        """Aggiungere la stessa directory due volte non crea duplicati."""
        custom_dir = Path("/tmp")
        count_before = get_allowed_dirs().count(custom_dir.resolve())
        add_allowed_dir(custom_dir)
        count_after = get_allowed_dirs().count(custom_dir.resolve())
        assert count_after == count_before

    def test_path_in_custom_dir(self, restore_allowed_dirs, tmp_path):
        """File in directory custom aggiunta -> OK."""
        # tmp_path e' gia' sotto /tmp, che e' permessa
        f = tmp_path / "custom_test.txt"
        f.write_text("test")
        result = validate_path(str(f))
        assert result == f.resolve()

    def test_get_allowed_dirs_ritorna_copia(self):
        """get_allowed_dirs() ritorna una copia, non il riferimento interno."""
        dirs = get_allowed_dirs()
        original_len = len(dirs)
        dirs.append(Path("/fake"))
        assert len(get_allowed_dirs()) == original_len


class TestAPIKey:
    """Test per autenticazione API key."""

    def test_api_key_generata(self):
        """API key e' stata generata e non e' vuota."""
        assert API_KEY
        assert len(API_KEY) > 20

    def test_verify_api_key_corretta(self):
        """Chiave corretta -> True."""
        assert verify_api_key(API_KEY) is True

    def test_verify_api_key_errata(self):
        """Chiave errata -> False."""
        assert verify_api_key("chiave-sbagliata") is False

    def test_verify_api_key_none(self):
        """Chiave None -> False."""
        assert verify_api_key(None) is False

    def test_verify_api_key_vuota(self):
        """Chiave vuota -> False."""
        assert verify_api_key("") is False


class TestCORSConfig:
    """Test per configurazione CORS."""

    def test_allowed_origins_non_contiene_wildcard(self):
        """CORS non deve contenere '*'."""
        assert "*" not in ALLOWED_ORIGINS

    def test_allowed_origins_solo_localhost(self):
        """Solo origini localhost permesse."""
        for origin in ALLOWED_ORIGINS:
            assert "localhost" in origin or "127.0.0.1" in origin


class TestAPIKeyEndpoints:
    """Test che gli endpoint POST rifiutino richieste senza API key."""

    def test_mcp_test_tts_senza_auth(self, mcp_client_noauth):
        """POST /test/tts senza API key -> 401."""
        resp = mcp_client_noauth.post("/test/tts?text=Ciao")
        assert resp.status_code == 401

    def test_mcp_test_tts_con_auth(self, mcp_client):
        """POST /test/tts con API key -> OK."""
        resp = mcp_client.post("/test/tts?text=Ciao")
        assert resp.status_code == 200

    def test_mcp_get_senza_auth(self, mcp_client_noauth):
        """GET / senza API key -> 200 (health check aperto)."""
        resp = mcp_client_noauth.get("/")
        assert resp.status_code == 200

    def test_tts_speak_senza_auth(self, tts_client_noauth):
        """POST /speak senza API key -> 401."""
        resp = tts_client_noauth.post("/speak", data={"text": "Test"})
        assert resp.status_code == 401

    def test_tts_get_senza_auth(self, tts_client_noauth):
        """GET / senza API key -> 200."""
        resp = tts_client_noauth.get("/")
        assert resp.status_code == 200

    def test_image_analyze_senza_auth(self, image_client_noauth):
        """POST /analyze senza API key -> 401."""
        resp = image_client_noauth.post("/analyze")
        assert resp.status_code == 401

    def test_document_read_senza_auth(self, document_client_noauth):
        """POST /read senza API key -> 401."""
        resp = document_client_noauth.post("/read")
        assert resp.status_code == 401

    def test_chiave_errata_rifiutata(self, mcp_client_noauth):
        """POST con API key sbagliata -> 401."""
        resp = mcp_client_noauth.post(
            "/test/tts?text=Ciao",
            headers={"X-API-Key": "chiave-falsa"}
        )
        assert resp.status_code == 401
