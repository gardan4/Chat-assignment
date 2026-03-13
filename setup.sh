#!/usr/bin/env bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

echo -e "${BOLD}Squad Nous — First-Time Setup${NC}"
echo ""

# ── 1. Check prerequisites ──────────────────────────────────────────

MISSING=()

if ! command -v docker &>/dev/null; then
  MISSING+=("docker")
fi

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  MISSING+=("python 3.13+")
fi

if ! command -v node &>/dev/null; then
  MISSING+=("node 18+")
fi

if ! command -v npm &>/dev/null; then
  MISSING+=("npm")
fi

if [ ${#MISSING[@]} -ne 0 ]; then
  error "Missing required tools: ${MISSING[*]}"
  echo ""
  echo "  Install them before running this script:"
  echo "    Docker:  https://docs.docker.com/get-docker/"
  echo "    Python:  https://www.python.org/downloads/"
  echo "    Node.js: https://nodejs.org/"
  echo ""
  exit 1
fi

info "Prerequisites found"

# Show versions
PYTHON_CMD=$(command -v python3 || command -v python)
echo "    Docker:  $(docker --version | head -1)"
echo "    Python:  $($PYTHON_CMD --version)"
echo "    Node:    $(node --version)"
echo "    npm:     $(npm --version)"
echo ""

# ── 2. Environment file ─────────────────────────────────────────────

if [ ! -f .env ]; then
  cp .env.example .env
  info "Created .env from .env.example"
  warn "Edit .env with your API keys before running the app"
else
  info ".env already exists — skipping"
fi

# ── 3. Python dependencies ──────────────────────────────────────────

echo ""
echo -e "${BOLD}Installing Python dependencies...${NC}"
pip install uv 2>/dev/null || true
if uv pip install --system ".[dev]" 2>/dev/null; then
  info "Python dependencies installed (uv)"
elif pip install ".[dev]" 2>/dev/null; then
  info "Python dependencies installed (pip)"
else
  error "Failed to install Python dependencies"
  echo "  Try manually: pip install '.[dev]'"
  exit 1
fi

# ── 4. Frontend dependencies ────────────────────────────────────────

echo ""
echo -e "${BOLD}Installing frontend dependencies...${NC}"
if (cd frontend && npm install); then
  info "Frontend dependencies installed"
else
  error "Failed to install frontend dependencies"
  echo "  Try manually: cd frontend && npm install"
  exit 1
fi

# ── 5. Done ─────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}Setup complete!${NC}"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Edit .env with your LLM API keys"
echo "  2. Start the full stack:"
echo "       docker compose up --build"
echo "     Or use the build script:"
echo "       ./build.sh run"
echo ""
echo "  Once running:"
echo "    Frontend:  http://localhost:3000"
echo "    API:       http://localhost:8000"
echo "    API Docs:  http://localhost:8000/docs"
echo ""
echo "  Useful commands:"
echo "    ./build.sh test        Run all tests"
echo "    ./build.sh lint        Lint check"
echo "    ./build.sh run-debug   Start with Mongo Express (:8081)"
echo ""
