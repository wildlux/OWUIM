# 🎤 Risoluzione Problemi Modalità Vocale - Open WebUI

## ⚠️ Problema: "Autorizzazione Negata" per Dispositivi Multimediali

Quando provi ad usare la modalità vocale in Open WebUI, il browser blocca l'accesso al microfono con errore "Autorizzazione negata".

---

## 🔍 Causa del Problema

I browser moderni (Chrome, Firefox, Edge, Safari) richiedono **HTTPS** o **localhost** per accedere al microfono per motivi di sicurezza.

### Scenario 1: Accesso da PC (localhost)
✅ **Funziona** - `http://localhost:3000`
❌ **Non funziona** - `http://127.0.0.1:3000` (su alcuni browser)

### Scenario 2: Accesso da Cellulare/Tablet (LAN)
❌ **Non funziona** - `http://192.168.1.X:3000` (HTTP non sicuro)
✅ **Funziona** - `https://192.168.1.X:3000` (HTTPS richiesto!)

---

## ✅ Soluzioni

### 🖥️ Soluzione 1: Accesso da PC (Rapida)

Se accedi dal PC stesso:

#### A. Usa `localhost` invece di IP

**Corretto:**
```
http://localhost:3000
```

**Evita:**
```
http://127.0.0.1:3000
http://192.168.1.45:3000  (IP locale)
```

#### B. Autorizza Manualmente nel Browser

**Chrome/Edge:**
1. Clicca sull'icona 🔒 o ℹ️ nella barra degli indirizzi
2. **Autorizzazioni del sito** → **Microfono**
3. Seleziona **Consenti**
4. Ricarica la pagina (F5)

**Firefox:**
1. Clicca sull'icona 🔒 nella barra degli indirizzi
2. **Autorizzazioni** → **Usa il microfono**
3. Seleziona **Consenti**
4. Ricarica la pagina

**Brave:**
1. Clicca sull'icona del leone 🦁
2. **Controlli del sito** → **Microfono**
3. Attiva il toggle

---

### 📱 Soluzione 2: Accesso da Cellulare (HTTPS Richiesto)

Per usare la modalità vocale da cellulare/tablet, devi abilitare **HTTPS**.

#### Opzione A: Certificato Self-Signed (Consigliato per Uso Domestico)

Usa lo script automatico:

```bash
./enable_https.sh
```

Lo script:
1. ✅ Genera certificato SSL self-signed
2. ✅ Configura nginx come reverse proxy
3. ✅ Abilita HTTPS su porta 443
4. ✅ Mantiene HTTP su porta 3000

Accesso dopo configurazione:
- **Da PC:** `https://localhost` o `http://localhost:3000`
- **Da cellulare:** `https://192.168.1.X` (accetta l'avviso di sicurezza)

#### Opzione B: Configurazione Manuale Nginx

Se preferisci configurare manualmente, segui la [guida dettagliata](#configurazione-manuale-https).

---

### 🛠️ Soluzione 3: Trusted Certificate (Avanzato)

Per evitare avvisi di sicurezza, puoi usare un certificato fidato:

#### A. mDNS + Let's Encrypt Locale

```bash
# 1. Installa avahi (mDNS)
sudo apt install avahi-daemon

# 2. Il tuo PC sarà accessibile come: carlo-pc.local

# 3. Usa Certbot con DNS challenge
sudo apt install certbot
sudo certbot certonly --manual --preferred-challenges dns
```

#### B. Cloudflare Tunnel (Per Accesso Remoto Sicuro)

```bash
# Installa cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

# Crea tunnel
cloudflared tunnel login
cloudflared tunnel create openwebui
cloudflared tunnel route dns openwebui openwebui.tuodominio.com
```

---

## 🔧 Troubleshooting

### Problema: "Microfono bloccato permanentemente"

**Chrome/Edge:**
```
1. Vai a: chrome://settings/content/microphone
2. Rimuovi localhost:3000 dalla lista "Bloccati"
3. Ricarica la pagina
```

**Firefox:**
```
1. Vai a: about:preferences#privacy
2. Scorri a "Autorizzazioni" → "Microfono" → "Impostazioni"
3. Rimuovi localhost:3000
4. Ricarica la pagina
```

### Problema: "Nessun dispositivo audio trovato"

**Linux:**
```bash
# Verifica microfono riconosciuto
arecord -l

# Test registrazione
arecord -d 3 test.wav
aplay test.wav

# Se non funziona, verifica PulseAudio
pulseaudio --check
pulseaudio --start
```

**Windows:**
```
1. Impostazioni → Privacy → Microfono
2. Abilita "Consenti alle app di accedere al microfono"
3. Verifica che il browser abbia il permesso
```

### Problema: "HTTPS non funziona dopo configurazione"

```bash
# Verifica stato nginx
sudo systemctl status nginx

# Verifica log errori
sudo tail -f /var/log/nginx/error.log

# Testa configurazione
sudo nginx -t

# Riavvia nginx
sudo systemctl restart nginx
```

---

## 📋 Checklist Rapida

### Per Accesso da PC
- [ ] Usi `http://localhost:3000` (non IP)
- [ ] Hai cliccato "Consenti" quando richiesto
- [ ] Hai verificato permessi in Impostazioni Browser
- [ ] Hai ricaricato la pagina dopo aver dato il permesso

### Per Accesso da Cellulare
- [ ] Hai abilitato HTTPS (certificato self-signed ok)
- [ ] Accedi tramite `https://192.168.1.X`
- [ ] Hai accettato l'avviso di sicurezza del certificato
- [ ] Hai dato il permesso microfono nel browser mobile

---

## 🎯 Test Funzionamento

### Test 1: Verifica Permessi Browser

1. Apri Open WebUI
2. Premi F12 (Console Sviluppatore)
3. Nella Console, scrivi:
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(() => console.log("✅ Microfono OK"))
  .catch(err => console.error("❌ Errore:", err))
```

**Risultato atteso:** `✅ Microfono OK`

### Test 2: Verifica Dispositivi Disponibili

Nella Console:
```javascript
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    devices.forEach(d => console.log(d.kind, d.label))
  })
```

Dovresti vedere almeno un dispositivo `audioinput`.

---

## 🔐 Note Sicurezza

### ⚠️ Certificati Self-Signed

**Vantaggi:**
- ✅ Gratuiti
- ✅ Immediati
- ✅ Sufficienti per rete domestica

**Svantaggi:**
- ⚠️ Avviso sicurezza nel browser (accettabile per uso privato)
- ⚠️ Non fidati pubblicamente

**Quando usarli:**
- Rete domestica privata
- Dispositivi personali
- Non esporre su Internet

### ✅ Certificati Fidati (Let's Encrypt)

**Vantaggi:**
- ✅ Nessun avviso nel browser
- ✅ Fidati universalmente
- ✅ Gratuiti

**Quando usarli:**
- Accesso da Internet
- Condivisione con altre persone
- Uso professionale

---

## 📚 Link Utili

- [MDN: MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Chrome: Permessi Siti](https://support.google.com/chrome/answer/2693767)
- [Firefox: Permessi Siti](https://support.mozilla.org/en-US/kb/permissions-manager-give-ability-store-passwords-set-cookies-more)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)

---

## 💡 Raccomandazioni

### Per Uso Quotidiano sul PC
➡️ Usa semplicemente `http://localhost:3000` e dai il permesso nel browser. **Più semplice.**

### Per Uso da Cellulare Occasionale
➡️ Configura HTTPS con certificato self-signed. **Accetta l'avviso una volta, poi funziona sempre.**

### Per Accesso da Fuori Casa
➡️ Usa Cloudflare Tunnel o VPN. **Non esporre direttamente Open WebUI su Internet.**

---

**Ultima modifica:** 2026-01-22
**Autore:** Carlo
**Versione:** 1.0.0
