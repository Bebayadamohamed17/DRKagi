#!/bin/bash
# ─────────────────────────────────────────────────────────────
# DRKagi — One-Line Installer for Kali Linux
# Usage: curl -sL https://raw.githubusercontent.com/Bebayadamohamed17/DRKagi/main/install.sh | bash
# ─────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${RED}"
echo "██████╗ ██████╗ ██╗  ██╗ █████╗  ██████╗ ██╗"
echo "██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔════╝ ██║"
echo "██║  ██║██████╔╝█████╔╝ ███████║██║  ███╗██║"
echo "██║  ██║██╔══██╗██╔═██╗ ██╔══██║██║   ██║██║"
echo "██████╔╝██║  ██║██║  ██╗██║  ██║╚██████╔╝██║"
echo "╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝"
echo -e "${NC}"
echo -e "${CYAN}DRKagi Installer v0.3${NC}"
echo ""

# ── Check if running on Kali ───────────────────────────────
if ! grep -qi 'kali' /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}[!] Warning: This doesn't appear to be Kali Linux.${NC}"
    echo -e "${YELLOW}    DRKagi works best on Kali. Continue? (y/n)${NC}"
    read -r answer
    if [ "$answer" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

INSTALL_DIR="$HOME/DRKagi"

# ── Clone or update repo ──────────────────────────────────
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[*] DRKagi directory exists. Updating...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || echo -e "${YELLOW}  Could not git pull. Using existing files.${NC}"
else
    echo -e "${GREEN}[+] Cloning DRKagi...${NC}"
    git clone https://github.com/Bebayadamohamed17/DRKagi.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ── Install system dependencies ────────────────────────────
echo -e "${GREEN}[+] Installing system tools...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv \
    nmap masscan gobuster nikto hydra sqlmap smbclient smbmap \
    enum4linux whatweb wafw00f exploitdb 2>/dev/null || true

# ── Create virtual environment ────────────────────────────
echo -e "${GREEN}[+] Setting up Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# ── Install Python dependencies ───────────────────────────
echo -e "${GREEN}[+] Installing Python dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── Create .env if not exists ─────────────────────────────
if [ ! -f .env ]; then
    echo -e "${YELLOW}[*] Creating .env template...${NC}"
    cat > .env << 'EOF'
# DRKagi Configuration
# Get your API key at https://console.groq.com

# Single key:
GROQ_API_KEY=gsk_your_key_here

# Multi-key (recommended for zero rate limits):
# GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3

EOF
    echo -e "${YELLOW}  Please edit ${INSTALL_DIR}/.env with your API key!${NC}"
fi

# ── Create launch script ─────────────────────────────────
echo -e "${GREEN}[+] Creating launch command...${NC}"
sudo tee /usr/local/bin/drkagi > /dev/null << EOF
#!/bin/bash
cd $INSTALL_DIR
source .venv/bin/activate
python3 drkagi.py "\$@"
EOF
sudo chmod +x /usr/local/bin/drkagi

# ── Create directories ───────────────────────────────────
mkdir -p logs sessions profiles plugins vault

# ── Done ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DRKagi installed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}1. Edit your API key:${NC}"
echo -e "     nano ${INSTALL_DIR}/.env"
echo ""
echo -e "  ${CYAN}2. Launch DRKagi:${NC}"
echo -e "     drkagi"
echo ""
echo -e "  ${CYAN}Or run directly:${NC}"
echo -e "     cd ${INSTALL_DIR} && source .venv/bin/activate && python3 drkagi.py"
echo ""
echo -e "${RED}  Remember: Authorized testing only!${NC}"
echo ""
