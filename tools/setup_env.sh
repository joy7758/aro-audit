#!/bin/bash
set -euo pipefail
python3 --version
python3 -m pip --version
git --version
if [ ! -x ".venv/bin/python" ]; then python3 -m venv .venv; fi
source .venv/bin/activate
python -m pip install -U pip
if [ ! -f "requirements.txt" ]; then
  cat > requirements.txt <<'EOR'
cryptography
jsonschema
duckdb
orjson
typer
rfc8785
EOR
fi
python -m pip install -r requirements.txt
touch .gitignore
ensure_line() { grep -qxF "$1" "$2" 2>/dev/null || echo "$1" >> "$2"; }
ensure_line ".venv/" ".gitignore"
ensure_line "__pycache__/" ".gitignore"
ensure_line "*.pyc" ".gitignore"
ensure_line ".DS_Store" ".gitignore"
python --version
pip --version
pip list | head -n 20
