#!/bin/bash
###############################################################################
# Script: Abilita HTTPS per Open WebUI
# Autore: Carlo
# Versione: 1.0.0
# Descrizione: Configura HTTPS con certificato self-signed per accesso microfono
###############################################################################

set -e

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║        🔐 Configurazione HTTPS per Open WebUI            ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verifica permessi sudo
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Non eseguire questo script come root!${NC}"
    echo "Eseguilo come utente normale. Lo script chiederà sudo quando necessario."
    exit 1
fi

# Directory progetto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$PROJECT_DIR/ssl"

echo -e "${YELLOW}Questo script configurerà HTTPS per risolvere i problemi di accesso al microfono.${NC}"
echo
echo -e "${CYAN}Perché serve HTTPS?${NC}"
echo "I browser moderni richiedono HTTPS per accedere a microfono/webcam"
echo "da dispositivi sulla rete locale (cellulari, tablet)."
echo
echo -e "${CYAN}Cosa verrà fatto:${NC}"
echo "1. ✅ Installazione nginx (se non presente)"
echo "2. ✅ Generazione certificato SSL self-signed"
echo "3. ✅ Configurazione reverse proxy HTTPS"
echo "4. ✅ HTTP rimane disponibile su porta 3000"
echo
echo -e "${YELLOW}⚠️  NOTA: Il certificato sarà self-signed (avviso sicurezza nel browser)${NC}"
echo "   Per uso domestico è normale. Accetta l'avviso una volta."
echo

read -p "Procedere? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Configurazione annullata"
    exit 0
fi

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: Verifica/Installazione Nginx${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

if command -v nginx &> /dev/null; then
    echo -e "${GREEN}✅ Nginx già installato${NC}"
else
    echo -e "${YELLOW}📦 Installazione nginx...${NC}"
    sudo apt update
    sudo apt install -y nginx
    echo -e "${GREEN}✅ Nginx installato${NC}"
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Generazione Certificato SSL Self-Signed${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Crea directory SSL
mkdir -p "$SSL_DIR"

# Trova IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

echo -e "${CYAN}Informazioni per il certificato:${NC}"
echo "   IP locale: $LOCAL_IP"
echo "   Hostname: $HOSTNAME"
echo

if [ -f "$SSL_DIR/openwebui.crt" ] && [ -f "$SSL_DIR/openwebui.key" ]; then
    echo -e "${YELLOW}⚠️  Certificato esistente trovato${NC}"
    read -p "Vuoi rigenerarlo? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Uso certificato esistente"
    else
        rm -f "$SSL_DIR/openwebui.crt" "$SSL_DIR/openwebui.key"
        GENERATE_CERT=true
    fi
else
    GENERATE_CERT=true
fi

if [ "$GENERATE_CERT" = true ]; then
    echo "Generazione certificato (validità 365 giorni)..."

    # Crea file di configurazione OpenSSL
    cat > "$SSL_DIR/openssl.cnf" << SSLCONF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C=IT
ST=Italy
L=Local
O=Open WebUI
OU=Home
CN=$HOSTNAME

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = $HOSTNAME
DNS.3 = *.local
IP.1 = 127.0.0.1
IP.2 = $LOCAL_IP
SSLCONF

    # Genera certificato
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/openwebui.key" \
        -out "$SSL_DIR/openwebui.crt" \
        -config "$SSL_DIR/openssl.cnf" 2>/dev/null

    # Imposta permessi
    chmod 600 "$SSL_DIR/openwebui.key"
    chmod 644 "$SSL_DIR/openwebui.crt"

    echo -e "${GREEN}✅ Certificato generato${NC}"
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Configurazione Nginx${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

NGINX_CONF="/etc/nginx/sites-available/openwebui-https"
NGINX_ENABLED="/etc/nginx/sites-enabled/openwebui-https"

# Crea configurazione nginx
sudo tee "$NGINX_CONF" > /dev/null << NGINXCONF
# Open WebUI HTTPS Configuration
# Generato da enable_https.sh

server {
    listen 80;
    listen [::]:80;
    server_name localhost $HOSTNAME $LOCAL_IP;

    # Redirect HTTP a HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name localhost $HOSTNAME $LOCAL_IP;

    # SSL Certificate
    ssl_certificate $SSL_DIR/openwebui.crt;
    ssl_certificate_key $SSL_DIR/openwebui.key;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers sicurezza
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy a Open WebUI
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # Headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer
        proxy_buffering off;
        proxy_cache_bypass \$http_upgrade;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "OK";
    }
}
NGINXCONF

echo -e "${GREEN}✅ Configurazione nginx creata${NC}"

# Abilita sito
if [ -L "$NGINX_ENABLED" ]; then
    sudo rm "$NGINX_ENABLED"
fi
sudo ln -s "$NGINX_CONF" "$NGINX_ENABLED"

echo -e "${GREEN}✅ Sito abilitato${NC}"

# Testa configurazione
echo
echo "Test configurazione nginx..."
if sudo nginx -t 2>&1 | grep -q "syntax is ok"; then
    echo -e "${GREEN}✅ Configurazione valida${NC}"
else
    echo -e "${RED}❌ Errore nella configurazione${NC}"
    sudo nginx -t
    exit 1
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Configurazione Firewall${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo "Apertura porte 80 (HTTP) e 443 (HTTPS)..."

# firewalld
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --add-service=http --permanent 2>/dev/null
    sudo firewall-cmd --add-service=https --permanent 2>/dev/null
    sudo firewall-cmd --reload 2>/dev/null
    echo -e "${GREEN}✅ Firewalld configurato${NC}"
fi

# ufw
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp 2>/dev/null
    sudo ufw allow 443/tcp 2>/dev/null
    echo -e "${GREEN}✅ UFW configurato${NC}"
fi

# iptables
if command -v iptables &> /dev/null; then
    sudo iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || \
        sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    sudo iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || \
        sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

    if [ -d "/etc/iptables" ]; then
        sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
    fi
    echo -e "${GREEN}✅ IPTables configurato${NC}"
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 5: Riavvio Nginx${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

sudo systemctl enable nginx
sudo systemctl restart nginx

if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx avviato correttamente${NC}"
else
    echo -e "${RED}❌ Errore avvio nginx${NC}"
    sudo systemctl status nginx
    exit 1
fi

echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 6: Verifica Configurazione${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

echo "Test connessione HTTPS..."
sleep 2

HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ HTTPS funzionante (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS risponde con HTTP $HTTP_CODE${NC}"
    echo "   Verifica log: sudo tail -f /var/log/nginx/error.log"
fi

echo

# Risultato finale
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║           ✅ Configurazione HTTPS Completata!            ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🌐 Accedi a Open WebUI:${NC}"
echo
echo -e "${CYAN}Da questo PC:${NC}"
echo -e "${GREEN}   https://localhost${NC} (HTTPS - Consigliato per microfono)"
echo -e "   http://localhost:3000 (HTTP - Ancora disponibile)"
echo
echo -e "${CYAN}Da cellulare/tablet (stessa WiFi):${NC}"
echo -e "${GREEN}   https://$LOCAL_IP${NC}"
echo -e "   ⚠️  Accetta l'avviso di sicurezza del certificato (solo la prima volta)"
echo

echo -e "${YELLOW}📝 Note Importanti:${NC}"
echo
echo "1. ${CYAN}Avviso Certificato:${NC}"
echo "   Il browser mostrerà un avviso perché il certificato è self-signed."
echo "   È normale per uso domestico. Clicca 'Avanzate' → 'Procedi comunque'"
echo
echo "2. ${CYAN}Permesso Microfono:${NC}"
echo "   Con HTTPS, il browser ti chiederà il permesso per il microfono."
echo "   Clicca 'Consenti' quando richiesto."
echo
echo "3. ${CYAN}Accesso HTTP:${NC}"
echo "   L'accesso HTTP su porta 3000 rimane disponibile per compatibilità."
echo

echo -e "${BLUE}🔧 Comandi Utili:${NC}"
echo "   Stato nginx: sudo systemctl status nginx"
echo "   Riavvio nginx: sudo systemctl restart nginx"
echo "   Log nginx: sudo tail -f /var/log/nginx/error.log"
echo "   Disabilita HTTPS: sudo rm $NGINX_ENABLED && sudo systemctl restart nginx"
echo

echo -e "${BLUE}📚 Documentazione:${NC}"
echo "   Guida completa: $PROJECT_DIR/docs/VOICE_MODE_PERMISSIONS.md"
echo

echo -e "${GREEN}✨ HTTPS configurato con successo!${NC}"
echo -e "${YELLOW}Ora puoi usare la modalità vocale anche da cellulare! 🎤${NC}"
echo

exit 0
