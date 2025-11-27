#!/usr/bin/env bash
set -e

echo "[postCreate] Installing extra tools..."

echo "[postCreate] Updating package lists..."
sudo apt-get update

echo "[postCreate] Installing Python dependencies..."
echo "[postCreate] Creating Python virtual environment..."
cd /workspace
rm -rf .venv
python3 -m venv .venv
echo "[postCreate] Activating virtual environment..."
source .venv/bin/activate

echo "[postCreate] Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

echo "[postCreate] Installing dependencies from requirements.txt..."
# if requirements.txt exists, install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "[postCreate] No requirements.txt found, skipping dependency installation."
fi

echo "[postCreate] Installing strace-parser..."
# test if ./strace-parser/ directory exists
if [ -d "./strace-parser/" ]; then
    pip install -e ./strace-parser/
else
    echo "[postCreate] No strace-parser directory found, skipping strace-parser installation."
fi

echo "[postCreate] Python Done."
deactivate

echo "[postCreate] Done."
