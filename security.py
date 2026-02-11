"""
Modulo di sicurezza centralizzato.

- Validazione path (anti path-traversal)
- Origini CORS consentite
- Autenticazione API key per servizi locali
"""

import os
import secrets
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("security")

# Directory permesse (whitelist)
_ALLOWED_DIRS: List[Path] = [
    Path.home(),
    Path("/tmp"),
    Path.home() / "Documenti",
    Path.home() / "Documents",
    Path.home() / "Desktop",
    Path.home() / "Scaricati",
    Path.home() / "Downloads",
    Path.home() / "Immagini",
    Path.home() / "Pictures",
]

# Pattern bloccati (file/directory sensibili)
BLOCKED_PATTERNS = [
    ".ssh", ".gnupg", ".gpg", ".pem", ".key",
    ".env", ".git/config", ".netrc", ".aws",
    "shadow", "passwd", "sudoers",
    "id_rsa", "id_ed25519", "known_hosts",
    "credentials", "token", "secret",
]


def validate_path(path_str: str) -> Path:
    """
    Valida un path e ritorna il Path risolto.

    1. Risolve symlink con realpath()
    2. Blocca pattern sensibili (.ssh, .gnupg, etc.)
    3. Verifica che il path sia dentro una directory permessa
    4. Verifica che il file esista

    Args:
        path_str: Stringa del path da validare

    Returns:
        Path risolto e validato

    Raises:
        ValueError: Se il path e' pericoloso o non permesso
    """
    if not path_str or not path_str.strip():
        raise ValueError("Path vuoto")

    # Risolvi symlink e path relativi
    resolved = Path(os.path.realpath(path_str))

    # Controlla pattern bloccati
    path_lower = str(resolved).lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in path_lower:
            raise ValueError(
                f"Path bloccato: contiene pattern sensibile '{pattern}'"
            )

    # Verifica whitelist directory
    in_allowed = False
    for allowed_dir in _ALLOWED_DIRS:
        try:
            resolved.relative_to(allowed_dir)
            in_allowed = True
            break
        except ValueError:
            continue

    if not in_allowed:
        raise ValueError(
            f"Path non permesso: '{resolved}' non e' in una directory consentita"
        )

    # Verifica esistenza
    if not resolved.exists():
        raise ValueError(f"File non trovato: '{resolved}'")

    return resolved


def add_allowed_dir(path: Path) -> None:
    """Aggiunge una directory alla whitelist."""
    resolved = Path(os.path.realpath(str(path)))
    if resolved not in _ALLOWED_DIRS:
        _ALLOWED_DIRS.append(resolved)


def get_allowed_dirs() -> List[Path]:
    """Ritorna le directory permesse."""
    return list(_ALLOWED_DIRS)


# ==================== CORS ====================

# Origini consentite per CORS (solo localhost)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5555",
    "http://localhost:5556",
    "http://localhost:5557",
    "http://localhost:5558",
]


# ==================== API Key ====================

# File dove salvare la chiave generata
_API_KEY_FILE = Path(__file__).parent / ".api_key"

# Env var per override
_API_KEY_ENV = "OWUI_API_KEY"


def _load_or_generate_api_key() -> str:
    """Carica la API key da env/file, o ne genera una nuova."""
    # 1. Variabile d'ambiente (priorita' massima)
    from_env = os.getenv(_API_KEY_ENV)
    if from_env:
        return from_env

    # 2. File .api_key esistente
    if _API_KEY_FILE.exists():
        key = _API_KEY_FILE.read_text().strip()
        if key:
            return key

    # 3. Genera nuova chiave e salvala
    key = secrets.token_urlsafe(32)
    try:
        _API_KEY_FILE.write_text(key)
        _API_KEY_FILE.chmod(0o600)
        logger.info(f"API key generata e salvata in {_API_KEY_FILE}")
    except OSError as e:
        logger.warning(f"Impossibile salvare API key su file: {e}")
    return key


# Chiave caricata al primo import
API_KEY = _load_or_generate_api_key()


def verify_api_key(provided_key: Optional[str]) -> bool:
    """Verifica che la chiave fornita corrisponda."""
    if not provided_key:
        return False
    return secrets.compare_digest(provided_key, API_KEY)


def get_api_key_header():
    """
    Dipendenza FastAPI per proteggere singoli endpoint.

    Uso:
        from security import get_api_key_header
        @app.post("/endpoint", dependencies=[Depends(get_api_key_header())])
    """
    from fastapi import Header, HTTPException

    async def _verify(x_api_key: Optional[str] = Header(None)):
        if not verify_api_key(x_api_key):
            raise HTTPException(status_code=401, detail="API key mancante o non valida")
    return _verify


def create_api_key_middleware(app):
    """
    Middleware che protegge tutti gli endpoint POST/PUT/DELETE con API key.
    GET restano aperti (health check, info).

    Uso:
        create_api_key_middleware(app)
    """
    from starlette.requests import Request
    from starlette.responses import JSONResponse

    @app.middleware("http")
    async def _check_api_key(request: Request, call_next):
        if request.method in ("POST", "PUT", "DELETE"):
            key = request.headers.get("x-api-key")
            if not verify_api_key(key):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "API key mancante o non valida"}
                )
        return await call_next(request)


# Host sicuro: solo localhost
SAFE_HOST = "127.0.0.1"
