#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "=== [1/5] Aktualizacja systemu Ubuntu ==="
apt-get update -y
apt-get install -y curl wget git jq ufw

echo "=== [2/5] Instalacja silnika Ollama ==="
curl -fsSL https://ollama.com/install.sh | sh

# Konfiguracja Ollamy, aby nasłuchiwała na 0.0.0.0 (wszystkie interfejsy)
mkdir -p /etc/systemd/system/ollama.service.d
cat << 'EOF' > /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_ORIGINS=*"
EOF

systemctl daemon-reload
systemctl restart ollama

echo "=== [3/5] Oczekiwanie na start serwisu Ollama ==="
until curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "Oczekiwanie na start Ollamy..."
    sleep 2
done

echo "=== [4/5] Pobieranie modelu Bielik ==="
ollama pull bielik || ollama pull speakleash/bielik-11b-v2.3-instruct:Q4_K_M || ollama pull qwen2.5:7b

echo "=== [5/5] Instalacja Cloudflare Tunnel (Zdalny bezpieczny dostep) ==="
curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i /tmp/cloudflared.deb || apt-get install -f -y

# Uruchomienie tunelu w tle i logowanie publicznego URL
cat << 'EOF' > /etc/systemd/system/bielik-tunnel.service
[Unit]
Description=Cloudflare Tunnel for Bielik Ollama
After=network.target ollama.service

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:11434 --logfile /var/log/bielik_tunnel.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bielik-tunnel.service

echo "=== Instalacja zakonczona sukcesem! ===" > /var/log/bielik_install_complete.txt
