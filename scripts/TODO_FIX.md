# TODO FIX - Percorsi e venv cross-platform

## Stato: COMPLETATO

### Problemi risolti

#### 1. `config.py` - Centralizzazione Python/venv
- [x] Aggiunto `PYTHON_EXE` - risolve automaticamente il Python del venv
- [x] Aggiunto `VENV_DIR` - percorso centralizzato al venv
- [x] Aggiunti percorsi assoluti: `TTS_SCRIPT`, `IMAGE_SCRIPT`, `DOCUMENT_SCRIPT`, `MCP_SCRIPT`

#### 2. `ui/widgets/tts.py` - Subprocess fix
- [x] `start_tts_service()` - usa `PYTHON_EXE` + `TTS_SCRIPT` (percorso assoluto)
- [x] `run_download_script()` - usa `PYTHON_EXE` invece di `python`/`python3`
- [x] `stop_tts_service()` - Windows: termina per porta (non `taskkill /im python.exe`)

#### 3. `ui/widgets/mcp.py` - Subprocess fix
- [x] `_do_start_mcp_service()` - usa `PYTHON_EXE` + `MCP_SCRIPT`
- [x] `_start_sub_service()` - usa `PYTHON_EXE` + percorsi assoluti da config

#### 4. `run_gui.sh` - venv Python
- [x] Opzione 2 (avvio con servizi) - usa `$VENV_PYTHON` con percorsi assoluti

#### 5. `run_gui.bat` - venv Python
- [x] Tutte le chiamate `python` sostituite con `%VENV_PYTHON%`
- [x] Servizi in background avviati con il Python del venv

#### 6. `scripts/start_all.sh` - venv Python
- [x] Aggiunto `VENV_PYTHON` che cerca il venv del progetto padre
- [x] `start_service()` usa `$VENV_PYTHON` invece di `python3`

#### 7. Script di avvio servizi - venv Python
- [x] `tts_service/start_tts_service.sh` - cerca venv progetto padre
- [x] `tts_service/start_tts_service.bat` - cerca venv progetto padre
- [x] `image_analysis/start_image_service.sh` - cerca venv progetto padre
- [x] `image_analysis/start_image_service.bat` - cerca venv progetto padre
- [x] `document_service/start_document_service.sh` - cerca venv progetto padre
- [x] `document_service/start_document_service.bat` - cerca venv progetto padre
- [x] `mcp_service/start_mcp_service.sh` - cerca venv progetto padre
- [x] `mcp_service/start_mcp_service.bat` - cerca venv progetto padre

#### 8. `dist/build.py` - Dati mancanti nel bundle
- [x] Aggiunto `system_profiler.py` ai dati (Windows + Linux)
- [x] Aggiunto `translations.py` ai dati (Windows + Linux)
- [x] Aggiunto `--hidden-import` per config, translations, system_profiler
- [x] Aggiunto `system_profiler.py` alla lista pacchetto portatile

#### 9. Organizzazione script
- [x] Spostato `GITHUB_avvia_commit.sh` -> `scripts/git_commit.sh`

### Pattern di risoluzione venv (tutti gli script)

```bash
# Bash: cerca venv del progetto padre
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
else
    PYTHON="python3"
fi
```

```bat
REM Batch: cerca venv del progetto padre
set "PROJECT_ROOT=%~dp0\.."
if exist "%PROJECT_ROOT%\venv\Scripts\python.exe" (
    set "PYTHON=%PROJECT_ROOT%\venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)
```

```python
# Python: config.py centralizzato
from config import PYTHON_EXE, TTS_SCRIPT, IMAGE_SCRIPT, ...
subprocess.Popen([PYTHON_EXE, str(TTS_SCRIPT)], ...)
```
