# 🎤 Fix Rapido: "Autorizzazione Negata" per Microfono

## ⚡ Soluzione Immediata (30 secondi)

### Se accedi dal PC:

1. **Usa questo indirizzo:**
   ```
   http://localhost:3000
   ```
   ❌ NON usare: `http://127.0.0.1:3000` o `http://192.168.1.X:3000`

2. **Quando richiesto, clicca "Consenti"** per il microfono

3. **Se non funziona:**
   - Clicca sull'icona 🔒 nella barra degli indirizzi
   - **Autorizzazioni** → **Microfono** → **Consenti**
   - Ricarica la pagina (F5)

✅ **FATTO!** Il microfono dovrebbe funzionare.

---

## 📱 Se accedi da Cellulare/Tablet

Il cellulare richiede **HTTPS** per il microfono.

### Soluzione Automatica:

```bash
cd /home/wildlux/Desktop/CARLO/ollama-webui
./enable_https.sh
```

Lo script configurerà automaticamente HTTPS.

### Dopo lo script:

1. Sul cellulare, vai a: `https://192.168.1.X` (usa l'IP mostrato)
2. Accetta l'avviso di sicurezza (certificato self-signed - normale!)
3. Clicca "Consenti" quando chiede il permesso microfono

✅ **FATTO!** Modalità vocale funzionante da cellulare.

---

## 🔍 Verifica Veloce

Apri la Console del browser (F12) e scrivi:

```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(() => console.log("✅ Microfono OK"))
  .catch(err => console.error("❌ Errore:", err))
```

Se vedi **✅ Microfono OK** → Funziona!
Se vedi errore → Segui la guida completa sotto.

---

## 📚 Guida Completa

Per tutti i dettagli: [`docs/VOICE_MODE_PERMISSIONS.md`](docs/VOICE_MODE_PERMISSIONS.md)

---

## 💡 Riassunto

| Da dove accedi | Soluzione | Tempo |
|----------------|-----------|-------|
| PC (stesso dispositivo) | Usa `localhost:3000` + Consenti | 30 sec |
| Cellulare/Tablet (WiFi) | `./enable_https.sh` + Accetta certificato | 5 min |

---

**Creato:** 2026-01-22
**Autore:** Carlo
