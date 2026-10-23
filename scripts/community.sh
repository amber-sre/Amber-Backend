#!/usr/bin/env bash
# ==============================================================================
# Amber SRE Engine — Free Community Edition Installer
#
# Usage:
#   curl -fsSL https://ambersre.xyz/community.sh | bash
#
# Features:
#   • 100% Self-Hosted & Free Forever ($0 Cloud Cost)
#   • Zero License Key Required
#   • Pre-configured for 3 Nodes, 5 Services, 1,000 Alerts/mo
#   • Sovereign Auto-Healing & 24/7 In-VPC Sentinel Daemon
#   • Local Ollama AI Setup & On-Call Alert Pairing
# ==============================================================================
set -euo pipefail

AMBER_DIR="${HOME}/.amber"
REPO_URL="https://github.com/amber-sre/Amber-Backend.git"

# Colours
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${GREEN}[Amber Community]${NC} $*"; }
warn()  { echo -e "${YELLOW}[Amber WARN]${NC} $*"; }
error() { echo -e "${RED}[Amber ERROR]${NC} $*"; exit 1; }

echo ""
echo -e "${CYAN}${BOLD}======================================================================${NC}"
echo -e "${CYAN}${BOLD}  ⚡ AMBER SRE — FREE COMMUNITY EDITION INSTALLER${NC}"
echo -e "  100% Self-Hosted • Up to 3 Nodes • 5 Services • 1,000 Alerts/mo"
echo -e "${CYAN}${BOLD}======================================================================${NC}"
echo ""

# ──────────────────────────────────────────────────────────────────────
# Step 1: System Pre-requisites Check
# ──────────────────────────────────────────────────────────────────────
info "Checking system requirements..."
for tool in git curl; do
    if ! command -v "$tool" &>/dev/null; then
        error "'$tool' is required but not installed. Please install it and re-run."
    fi
done

PYTHON_CMD=""
for cmd in python3.11 python3.12 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
        if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    error "Python 3.10 or higher is required. Please install Python 3.10+ and re-run."
fi
info "Using Python runtime: $("$PYTHON_CMD" --version 2>&1)"

if ! command -v docker &>/dev/null; then
    info "Docker not found (optional). Amber runs locally on zero-config embedded SQLite."
fi

# ──────────────────────────────────────────────────────────────────────
# Step 2: Clone or Update Amber Engine in ~/.amber
# ──────────────────────────────────────────────────────────────────────
info "Installing Amber SRE in ${AMBER_DIR}..."
if [[ -d "$AMBER_DIR/.git" ]]; then
    info "Found existing installation at ${AMBER_DIR}. Fetching latest updates..."
    git -C "$AMBER_DIR" fetch --depth=1 origin main 2>/dev/null || git -C "$AMBER_DIR" fetch origin main || true
    git -C "$AMBER_DIR" reset --hard origin/main 2>/dev/null || git -C "$AMBER_DIR" pull --ff-only || true
else
    git clone "$REPO_URL" "$AMBER_DIR"
fi
cd "$AMBER_DIR"

# ──────────────────────────────────────────────────────────────────────
# Step 3: Set up Python Virtual Environment
# ──────────────────────────────────────────────────────────────────────
if [[ ! -d ".venv" ]] || [[ ! -f ".venv/bin/pip" ]]; then
    info "Creating Python virtual environment..."
    rm -rf .venv 2>/dev/null || true
    "$PYTHON_CMD" -m venv .venv || "$PYTHON_CMD" -m venv --without-pip .venv
fi

VENV_PY="${AMBER_DIR}/.venv/bin/python"
VENV_PIP="${AMBER_DIR}/.venv/bin/pip"

# Ensure pip is available inside venv
if ! "$VENV_PY" -m pip --version &>/dev/null; then
    info "Bootstrapping pip inside virtual environment..."
    "$VENV_PY" -m ensurepip --upgrade 2>/dev/null || true
fi

info "Installing dependencies..."
"$VENV_PIP" install --upgrade pip --quiet
"$VENV_PIP" install -r requirements.txt --quiet || true

# ──────────────────────────────────────────────────────────────────────
# Step 4: Ensure Ollama is present for local AI compute
# ──────────────────────────────────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
    info "Ollama not found. Installing Ollama for local self-hosted AI reasoning..."
    curl -fsSL https://ollama.com/install.sh | sh 2>/dev/null || warn "Could not install Ollama automatically. You can install it manually from https://ollama.ai"
fi

# ──────────────────────────────────────────────────────────────────────
# Step 5: Launch Community Setup Wizard (Zero License Prompt)
# ──────────────────────────────────────────────────────────────────────
echo ""
info "Launching Community Onboarding Wizard..."
if [ -e /dev/tty ]; then
    "$VENV_PY" -m scripts.setup_wizards community < /dev/tty
else
    "$VENV_PY" -m scripts.setup_wizards community
fi

# ──────────────────────────────────────────────────────────────────────
# Step 6: Make CLI wrapper available
# ──────────────────────────────────────────────────────────────────────
chmod +x scripts/amber 2>/dev/null || true
mkdir -p "${HOME}/.local/bin"
ln -sf "${AMBER_DIR}/scripts/amber" "${HOME}/.local/bin/amber" 2>/dev/null || true

# ──────────────────────────────────────────────────────────────────────
# Step 7: Launch Background Containers
# ──────────────────────────────────────────────────────────────────────
if command -v docker &>/dev/null; then
    info "Launching local services via Docker Compose..."
    docker compose up -d 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo -e "${GREEN}${BOLD}  ✔ AMBER COMMUNITY EDITION IS READY!${NC}"
echo -e ""
echo -e "  🛡️ Sovereign Sentinel Daemon: ACTIVE (24x7 In-VPC Heartbeat)"
echo -e "  ⚡ Up to 3 Nodes Managed & Auto-Healed Sovereignly"
echo -e ""
echo -e "  To manage your engine anytime, use the CLI:"
echo -e "    ${BOLD}amber status${NC}"
echo -e "    ${BOLD}amber community setup${NC}"
echo -e "    ${BOLD}amber log-pruner status${NC}"
echo -e "${GREEN}${BOLD}======================================================================${NC}"
echo ""
