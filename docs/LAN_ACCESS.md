# 📱 Accesso Open WebUI da Rete Locale (LAN)

## Panoramica

Questa guida spiega come abilitare l'accesso a Open WebUI da dispositivi mobili (smartphone, tablet) e altri computer sulla tua rete locale (LAN).

**⚠️ IMPORTANTE:** Questa configurazione è sicura solo per reti domestiche private. Non esporre mai direttamente su Internet senza protezioni aggiuntive.

---

## 🔍 Come Funziona

### Modalità Localhost (Default)
```
Open WebUI ascolta solo su: 127.0.0.1:3000
├─ ✅ Accessibile dal PC stesso
└─ ❌ NON accessibile da altri dispositivi
```

### Modalità LAN
```
Open WebUI ascolta su: 0.0.0.0:3000
├─ ✅ Accessibile dal PC stesso
├─ ✅ Accessibile da cellulari sulla stessa WiFi
├─ ✅ Accessibile da tablet sulla stessa LAN
└─ ✅ Accessibile da altri PC sulla stessa rete
```

---

## 🚀 Attivazione Rapida

### Metodo Automatico (Consigliato)

```bash
# Abilita accesso LAN
./enable_lan_access.sh

# Disabilita accesso LAN (torna a localhost)
./disable_lan_access.sh
```

### Metodo Manuale

**1. Trova il tuo indirizzo IP locale:**
```bash
hostname -I
# Output esempio: 192.168.1.45
```

**2. Modifica docker-compose.yml:**
```yaml
services:
  ollama:
    ports:
      - "0.0.0.0:11434:11434"  # Cambia da 127.0.0.1

  open-webui:
    ports:
      - "0.0.0.0:3000:8080"    # Cambia da 127.0.0.1
```

**3. Riavvia i servizi:**
```bash
docker-compose down
docker-compose up -d
```

**4. Configura il firewall:**
```bash
# Firewalld
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --add-port=11434/tcp --permanent
sudo firewall-cmd --reload

# UFW
sudo ufw allow 3000/tcp
sudo ufw allow 11434/tcp

# IPTables
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

---

## 📱 Connessione da Dispositivi Mobili

### 1. Trova l'IP del PC Server
Sul PC che esegue Open WebUI:
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Esempio output: `192.168.1.45`

### 2. Connetti il Cellulare alla Stessa WiFi
- Verifica che il cellulare sia sulla **stessa rete WiFi** del PC
- NON usare WiFi ospite (guest network)

### 3. Apri il Browser sul Cellulare
Vai a: `http://192.168.1.45:3000` (sostituisci con il tuo IP)

### 4. Effettua il Login
Usa le stesse credenziali dell'account Open WebUI

---

## 🔧 Troubleshooting

### Problema: "Impossibile connettersi"

**Verifica 1: Servizi in esecuzione**
```bash
docker ps | grep -E "ollama|open-webui"
# Devono essere entrambi UP
```

**Verifica 2: Porte aperte**
```bash
sudo ss -tulpn | grep -E ":3000|:11434"
# Devono mostrare 0.0.0.0:3000 e 0.0.0.0:11434
```

**Verifica 3: Firewall**
```bash
# Test da PC
curl http://192.168.1.45:3000

# Se funziona dal PC ma non dal cellulare → problema firewall
sudo firewall-cmd --list-all
```

**Verifica 4: Stesso network**
```bash
# Sul PC, trova il gateway
ip route | grep default

# Sul cellulare, controlla l'IP nelle impostazioni WiFi
# Devono avere lo stesso gateway (es. 192.168.1.1)
```

### Problema: "Connessione lenta"

**Ottimizzazioni:**
```bash
# Verifica latenza
ping -c 5 192.168.1.45

# Se >10ms, possibili cause:
# - WiFi debole → avvicinati al router
# - Congestione rete → disconnetti dispositivi non necessari
# - Router sovraccarico → riavvia il router
```

### Problema: "Disconnessioni frequenti"

**Soluzioni:**
```bash
# 1. Assegna IP statico al PC server
# In /etc/network/interfaces o NetworkManager

# 2. Aumenta timeout nel docker-compose.yml
environment:
  - TIMEOUT=300

# 3. Disabilita risparmio energetico WiFi sul cellulare
```

---

## 🔒 Sicurezza

### ✅ Configurazione Sicura (Rete Domestica)

```yaml
# docker-compose.yml
services:
  open-webui:
    ports:
      - "0.0.0.0:3000:8080"  # OK per LAN
    environment:
      - ENABLE_SIGNUP=false      # Disabilita registrazioni pubbliche
      - WEBUI_AUTH=true          # Abilita autenticazione
```

### ⚠️ Best Practices

1. **Usa password forti** per gli account Open WebUI
2. **Non fare port forwarding** sul router (porta 3000/11434)
3. **Non esporre direttamente su Internet** senza HTTPS
4. **Usa VPN** se devi accedere da fuori casa
5. **Backup regolari** dei dati (vedi `backup_to_usb.sh`)

### 🛡️ Configurazione Avanzata (Opzionale)

**Reverse Proxy con Nginx + SSL:**
```nginx
# /etc/nginx/sites-available/openwebui
server {
    listen 443 ssl http2;
    server_name openwebui.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Autenticazione Basic HTTP:**
```bash
# Crea file password
htpasswd -c /etc/nginx/.htpasswd utente

# Aggiungi a nginx config
auth_basic "Area Riservata";
auth_basic_user_file /etc/nginx/.htpasswd;
```

---

## 📊 Monitoraggio Accessi

### Log Connessioni

```bash
# Log Open WebUI
docker logs open-webui -f | grep "GET\|POST"

# Log Ollama
docker logs ollama -f

# Connessioni attive
sudo netstat -tn | grep :3000
```

### Dashboard Accessi (Opzionale)

```bash
# Installa fail2ban per protezione brute force
sudo apt install fail2ban

# Configura per Open WebUI
sudo nano /etc/fail2ban/jail.local
```

```ini
[openwebui]
enabled = true
port = 3000
filter = openwebui
logpath = /var/log/openwebui.log
maxretry = 5
bantime = 3600
```

---

## 🌐 Configurazioni Avanzate

### Accesso Multi-Subnet

Se hai più sottoreti (es. WiFi 2.4GHz + 5GHz su subnet diverse):

```yaml
# docker-compose.yml
services:
  open-webui:
    networks:
      - frontend
    extra_hosts:
      - "host.docker.internal:host-gateway"

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### DNS Locale (mDNS)

```bash
# Installa avahi
sudo apt install avahi-daemon

# Accedi tramite nome invece che IP
# Da cellulare: http://carlo-pc.local:3000
```

### Accesso VPN da Remoto

**Con WireGuard:**
```bash
# Server VPN su PC casa
sudo apt install wireguard

# Configura tunnel
sudo nano /etc/wireguard/wg0.conf

# Da fuori casa, connetti VPN e accedi normalmente
```

---

## 📋 Checklist Attivazione

- [ ] IP locale identificato
- [ ] docker-compose.yml modificato (0.0.0.0)
- [ ] Firewall configurato (porte 3000, 11434)
- [ ] Servizi riavviati
- [ ] Test da PC locale (http://IP:3000)
- [ ] Test da cellulare sulla stessa WiFi
- [ ] Login funzionante
- [ ] Tool Scientific Council testato
- [ ] ENABLE_SIGNUP=false impostato
- [ ] Password account sicure

---

## 🔄 Ripristino a Localhost

Se vuoi tornare alla modalità localhost-only:

```bash
./disable_lan_access.sh
```

Oppure manualmente:
```yaml
# docker-compose.yml
services:
  ollama:
    ports:
      - "127.0.0.1:11434:11434"

  open-webui:
    ports:
      - "127.0.0.1:3000:8080"
```

```bash
docker-compose down && docker-compose up -d
```

---

## 📚 Risorse Aggiuntive

- [Docker Networking](https://docs.docker.com/network/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Ollama Network Configuration](https://github.com/ollama/ollama/blob/main/docs/faq.md)
- [Firewalld Guide](https://firewalld.org/documentation/)

---

**Ultima modifica:** 2026-01-22
**Autore:** Carlo
**Versione:** 1.0.0
