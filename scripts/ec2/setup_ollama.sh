#!/bin/bash
# =============================================================================
# setup_ollama.sh
# CISC 886 — Cloud Computing Project · Queen's University
# Team: Hana Essam (25tvtm), Mariam Mousa (25qns4), Alaa Mahmoud (25lskh)
#
# PURPOSE:
#   Installs Ollama on the EC2 instance (Amazon Linux 2023), downloads the
#   fine-tuned GGUF model from S3, creates the cisc886-chatbot Ollama model,
#   and registers Ollama as a systemd service for auto-start on reboot.
#
# PREREQUISITES:
#   - Amazon Linux 2023 (requires GLIBC 2.27+ — AL2 is incompatible)
#   - EC2 IAM role with AmazonS3ReadOnlyAccess attached
#   - Fine-tuned model uploaded to S3:
#     s3://25tvtm-cisc886-bucket-cloud-project/model/cisc886-beauty-model.gguf
#
# USAGE:
#   chmod +x setup_ollama.sh
#   ./setup_ollama.sh
# =============================================================================

set -e   # Exit immediately on any error
echo "========================================"
echo " GlowBot — Ollama Setup"
echo " CISC 886 Cloud Computing Project"
echo "========================================"

# ── Step 1: Install zstd ──────────────────────────────────────────────────────
# Required by the Ollama installer for archive extraction on AL2023.
echo "[1/6] Installing zstd dependency..."
sudo dnf install -y zstd
echo "✅ zstd installed"

# ── Step 2: Install Ollama ────────────────────────────────────────────────────
# Official Ollama installer. Installs the Ollama binary to /usr/local/bin/ollama.
# Note: Ollama requires GLIBC 2.27+. Amazon Linux 2023 provides GLIBC 2.34.
echo "[2/6] Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh
echo "✅ Ollama installed: $(ollama --version)"

# ── Step 3: Download fine-tuned model from S3 ─────────────────────────────────
# The EC2 IAM role (AmazonS3ReadOnlyAccess) authenticates the download.
# No hardcoded credentials are needed or used.
BUCKET="25tvtm-cisc886-bucket-cloud-project"
MODEL_KEY="model/cisc886-beauty-model.gguf"
LOCAL_PATH="$HOME/cisc886-beauty-model.gguf"

echo "[3/6] Downloading fine-tuned model from S3..."
echo "  Source: s3://$BUCKET/$MODEL_KEY"
echo "  Destination: $LOCAL_PATH"
aws s3 cp "s3://$BUCKET/$MODEL_KEY" "$LOCAL_PATH"
echo "✅ Model downloaded: $(du -sh $LOCAL_PATH | cut -f1)"

# ── Step 4: Create Modelfile ──────────────────────────────────────────────────
# The Modelfile configures Ollama with:
#   - The GGUF model path
#   - Llama 3 chat template (must match the training prompt format exactly)
#   - System prompt defining GlowBot's identity
#   - Generation parameters: temperature, context length, token limit
echo "[4/6] Creating Modelfile..."
cat > "$HOME/Modelfile" << 'EOF'
# Ollama Modelfile — cisc886-chatbot
# Base: Llama-3.2-3B-Instruct fine-tuned on Amazon Beauty & Personal Care reviews
# Quantization: GGUF Q4_K_M (4-bit, 2.02 GB)

FROM /home/ec2-user/cisc886-beauty-model.gguf

# Llama 3 chat template — must match the format used during QLoRA fine-tuning
TEMPLATE """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{{ .System }}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{{ .Prompt }}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

# System prompt — defines GlowBot's domain and behavior
SYSTEM """You are GlowBot, a knowledgeable beauty and personal care assistant
trained on Amazon customer reviews. Help users find the right products,
understand ingredients, compare options, and make informed purchasing
decisions based on real customer experiences."""

# Generation parameters
PARAMETER temperature 0.7      # Controls creativity — 0.7 balances helpful/varied
PARAMETER num_ctx    2048      # Context window — enough for multi-turn conversation
PARAMETER num_predict 300      # Max tokens per response — prevents runaway generation
EOF

echo "✅ Modelfile created at $HOME/Modelfile"

# ── Step 5: Start Ollama and create the model ─────────────────────────────────
# Start Ollama server in background, wait for it to initialize,
# then register the fine-tuned model under the name cisc886-chatbot.
echo "[5/6] Starting Ollama and loading model..."
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "  Ollama PID: $OLLAMA_PID — waiting for startup..."
sleep 8

ollama create cisc886-chatbot -f "$HOME/Modelfile"
echo ""
echo "  Registered models:"
ollama list

# Quick smoke test
echo ""
echo "  Smoke test (expect a beauty-related response)..."
RESPONSE=$(curl -s http://localhost:11434/api/generate \
  -d '{"model":"cisc886-chatbot","prompt":"Name one moisturizer for dry skin.","stream":false}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('response','ERROR')[:100])")
echo "  Response preview: $RESPONSE"

# Stop the background Ollama (systemd will manage it going forward)
kill $OLLAMA_PID 2>/dev/null || true
sleep 2

# ── Step 6: Register Ollama as systemd service ────────────────────────────────
# Ensures Ollama starts automatically when EC2 reboots (Section 7 requirement).
echo "[6/6] Registering Ollama as systemd service..."
sudo tee /etc/systemd/system/ollama.service > /dev/null << 'SVCEOF'
[Unit]
Description=Ollama LLM Runner — cisc886 project
After=network.target

[Service]
Type=simple
User=ec2-user
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="HOME=/home/ec2-user"

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

echo ""
echo "========================================"
echo " Setup complete!"
echo " Model:   cisc886-chatbot:latest"
echo " API:     http://localhost:11434"
echo " Service: sudo systemctl status ollama"
echo "========================================"
