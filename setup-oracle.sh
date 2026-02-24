#!/bin/bash
# ============================================================
# Oracle Cloud Free Tier — Full Setup Script
# Run this AFTER SSH-ing into your Oracle ARM instance
#
# Usage:
#   chmod +x setup-oracle.sh
#   ./setup-oracle.sh
# ============================================================

set -e

echo "============================================"
echo " LinkedIn Job Tracker — Oracle Cloud Setup"
echo "============================================"
echo ""

# ── 1. System Updates ──
echo "[1/6] Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# ── 2. Install Docker ──
echo "[2/6] Installing Docker..."
sudo apt-get install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
echo "  Docker installed. Version: $(docker --version)"

# ── 3. Install Ollama ──
echo "[3/6] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
echo "  Ollama installed. Version: $(ollama --version)"

# ── 4. Start Ollama & Pull Model ──
echo "[4/6] Starting Ollama and pulling llama3.2 model..."
ollama serve &
sleep 5
ollama pull llama3.2
echo "  Model llama3.2 downloaded."

# ── 5. Clone / Setup Project ──
echo "[5/6] Setting up project..."
cd ~
if [ ! -d "linkedin-job-tracker" ]; then
    echo "  Creating project directory..."
    mkdir -p linkedin-job-tracker
    echo "  NOTE: Copy your project files here or git clone your repo"
fi
cd linkedin-job-tracker

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  .env created from .env.example — edit it with your RAPIDAPI_KEY"
    else
        cat > .env << 'EOF'
RAPIDAPI_KEY=your_rapidapi_key_here
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://ollama:11434
SCRAPE_INTERVAL_HOURS=1
JOB_KEYWORDS=software engineer,data engineer,backend,full stack,python,java
JOB_LOCATION=United States
EOF
        echo "  .env created — edit it with your RAPIDAPI_KEY"
    fi
fi

# Create dirs
mkdir -p data output

# ── 6. Open Firewall (optional, for external access) ──
echo "[6/6] Configuring firewall..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 11434 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true

echo ""
echo "============================================"
echo " SETUP COMPLETE!"
echo "============================================"
echo ""
echo " Next steps:"
echo "   1. Edit .env with your RAPIDAPI_KEY:"
echo "      nano ~/linkedin-job-tracker/.env"
echo ""
echo "   2. Edit base_resume.json with YOUR details:"
echo "      nano ~/linkedin-job-tracker/base_resume.json"
echo ""
echo "   3. Start the tracker:"
echo "      cd ~/linkedin-job-tracker"
echo "      docker compose up --build -d"
echo ""
echo "   4. Check logs:"
echo "      docker compose logs -f job-tracker"
echo ""
echo "   5. Check generated resumes:"
echo "      ls ~/linkedin-job-tracker/output/"
echo ""
echo " Ollama is running at: http://localhost:11434"
echo " Model loaded: llama3.2"
echo "============================================"
