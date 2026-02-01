# Windows - Setup Dual Mode

**Docker (ottimale) / Python (fallback)**

## Uso

```batch
openwebui.bat              :: Menu interattivo
openwebui.bat start        :: Avvia (auto-detect)
openwebui.bat stop         :: Ferma
openwebui.bat status       :: Verifica stato
openwebui.bat install      :: Installa dipendenze
```

## Porte

- Docker: http://localhost:3000 (★★★★★)
- Python: http://localhost:8080 (★★★☆☆)

## Problemi WSL2/Docker

```batch
wsl_fix.bat                :: Menu risoluzione problemi
```

## Nota

Si consiglia Docker per efficienza energetica e prestazioni AI ottimali.



## Build .exe aggiornato

```batch
:: Installa dipendenze build (una volta sola)
pip install pyinstaller PyQt5 Pillow qrcode

:: Crea .exe
python build.py windows
```

L'eseguibile sarà creato in `dist/OpenWebUI-Manager.exe` 
