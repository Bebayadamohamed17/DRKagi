FROM kalilinux/kali-rolling

LABEL maintainer="DRKagi Team"
LABEL description="DRKagi - AI Offensive Security Framework"
LABEL version="0.3.0"

# Avoid prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# ── Install core Kali tools ────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 python3-pip python3-venv \
    # Reconnaissance
    nmap masscan netdiscover arp-scan fping dnsutils whois \
    # Web scanning
    nikto gobuster dirb wfuzz whatweb wafw00f \
    # Exploitation
    exploitdb crackmapexec evil-winrm \
    # Password attacks
    hydra medusa john hashcat wordlists \
    # Network
    tcpdump tshark proxychains4 tor \
    # SMB & Windows
    smbclient smbmap enum4linux \
    # Wireless
    aircrack-ng \
    # Utilities
    curl wget git jq \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Install optional tools (may not exist in all repos) ────
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlmap nuclei subfinder amass 2>/dev/null; \
    apt-get clean; rm -rf /var/lib/apt/lists/*; true

# ── Setup DRKagi ───────────────────────────────────────────
WORKDIR /opt/drkagi

COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

# ── Create directories ────────────────────────────────────
RUN mkdir -p logs sessions profiles plugins vault

# ── Create .env template if not exists ─────────────────────
RUN test -f .env || echo "GROQ_API_KEY=your_key_here" > .env

# ── Expose API port ───────────────────────────────────────
EXPOSE 5000

# ── Default command ───────────────────────────────────────
ENTRYPOINT ["python3", "drkagi.py"]
