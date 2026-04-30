#!/bin/bash
# =============================================================================
# setup_glowbot.sh
# CISC 886 — Cloud Computing Project · Queen's University
# Team: Hana Essam (25tvtm), Mariam Mousa (25qns4), Alaa Mahmoud (25lskh)
#
# PURPOSE:
#   Installs Streamlit on the EC2 instance, pulls the latest GlowBot app
#   from GitHub, and registers it as a systemd service on port 3000.
#   The GlowBot app connects to the local Ollama instance (cisc886-chatbot)
#   and provides a pink beauty-themed streaming chat interface.
#
# PREREQUISITES:
#   - setup_ollama.sh must be run first (Ollama must be running)
#   - Python 3.9 (pre-installed on Amazon Linux 2023)
#   - GitHub repo cloned at ~/cisc886-cloud-project
#
# USAGE:
#   chmod +x setup_glowbot.sh
#   ./setup_glowbot.sh
# =============================================================================

set -e
echo "========================================"
echo " GlowBot — Streamlit UI Setup"
echo " CISC 886 Cloud Computing Project"
echo "========================================"

# ── Step 1: Install pip for Python 3.9 ───────────────────────────────────────
# Amazon Linux 2023 ships with Python 3.9 but without pip.
# The standard get-pip.py URL does not support Python 3.9 — must use the
# version-specific URL at bootstrap.pypa.io/pip/3.9/get-pip.py.
echo "[1/4] Installing pip for Python 3.9..."
curl https://bootstrap.pypa.io/pip/3.9/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py --user
echo "✅ pip installed: $($HOME/.local/bin/pip --version)"

# ── Step 2: Install Streamlit ─────────────────────────────────────────────────
# Streamlit provides the web framework for the GlowBot chat interface.
# Installed with --user to avoid requiring sudo.
echo "[2/4] Installing Streamlit..."
~/.local/bin/pip install streamlit --user --quiet
echo "✅ Streamlit installed: $($HOME/.local/bin/streamlit --version)"

# ── Step 3: Pull latest GlowBot app ──────────────────────────────────────────
# Clone or update the project repo to get the latest app.py.
APP_DIR="$HOME/cisc886-cloud-project/glowbot-app"
REPO_URL="https://github.com/hanaessam/cisc886-cloud-project.git"

if [ -d "$HOME/cisc886-cloud-project" ]; then
    echo "[3/4] Pulling latest code..."
    cd "$HOME/cisc886-cloud-project" && git pull origin main
else
    echo "[3/4] Cloning repository..."
    git clone "$REPO_URL" "$HOME/cisc886-cloud-project"
fi

echo "✅ App ready at: $APP_DIR/app.py"

# ── Step 4: Register GlowBot as systemd service ───────────────────────────────
# Registers the Streamlit app to auto-start on EC2 reboot.
# Port 3000 must be open in the EC2 security group (sg-0a7f446a134a8048e).
# Depends on ollama.service — waits for Ollama to start before launching.
echo "[4/4] Registering GlowBot as systemd service..."
sudo tee /etc/systemd/system/glowbot.service > /dev/null << SVCEOF
[Unit]
Description=GlowBot Streamlit Beauty Assistant — cisc886 project
After=network-online.target ollama.service
Wants=network-online.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$APP_DIR
ExecStart=$STREAMLIT_BIN run app.py --server.port 3000 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
Restart=always
RestartSec=5
Environment="OLLAMA_HOST=http://127.0.0.1:11434"
Environment="HOME=$HOME"

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable glowbot
sudo systemctl start glowbot
sleep 3
sudo systemctl status glowbot --no-pager | head -8

echo ""
echo "========================================"
echo " GlowBot is live!"
echo " URL:     http://44.215.147.34:3000"
echo " Service: sudo systemctl status glowbot"
echo " Logs:    sudo journalctl -u glowbot -f"
echo "========================================"
