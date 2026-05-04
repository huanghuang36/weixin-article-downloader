#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/tool"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers (first time only)..."
playwright install --with-deps chromium

echo "Done. Run: python main.py --help"
