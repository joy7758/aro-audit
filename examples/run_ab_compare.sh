#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART="$ROOT/artifacts"
mkdir -p "$ART"

DOMAIN="CP_IAM,CP_CICD,pFDO_KERNEL_PERMS,pFDO_OBJECT_REGISTRY"
SOURCES="DEV_PUF_WEAK,DEV_PUF_STRONG,WORKLOAD_ID"

MAX_DEPTH="5"
MAX_PATHS="1000"
TOP_K="5"

A_GRAPH="$ROOT/examples/pFDO_controlplane_case.yaml"
B_GRAPH="$ROOT/examples/pFDO_strong_anchor.yaml"

A_JSON="$ART/vpml_A.json"
B_JSON="$ART/vpml_B.json"
SUMMARY_TXT="$ART/SUMMARY.txt"

# --- Derive version + git hash (best-effort) ---
VERSION="unknown"
if [[ -f "$ROOT/pyproject.toml" ]]; then
  # Extract first occurrence of: version = "x.y.z"
  VERSION="$(python - <<PY 2>/dev/null || echo "unknown"
import re, pathlib
t = pathlib.Path("$ROOT/pyproject.toml").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', t, re.M)
print(m.group(1) if m else "unknown")
PY
)"
fi

GIT_HASH="nogit"
if command -v git >/dev/null 2>&1 && git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_HASH="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "nogit")"
fi

UTC_NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "=== Case A (baseline) ==="
aro-vpml --graph "$A_GRAPH" \
  --domain "$DOMAIN" --sources "$SOURCES" \
  --max-depth "$MAX_DEPTH" --max-paths "$MAX_PATHS" --top-k "$TOP_K" \
  --pretty --json-out "$A_JSON" >/dev/null

echo "=== Case B (strong anchor) ==="
aro-vpml --graph "$B_GRAPH" \
  --domain "$DOMAIN" --sources "$SOURCES" \
  --max-depth "$MAX_DEPTH" --max-paths "$MAX_PATHS" --top-k "$TOP_K" \
  --pretty --json-out "$B_JSON" >/dev/null

python - <<PY
import json
a=json.load(open("$A_JSON","r",encoding="utf-8"))["SCI"]
b=json.load(open("$B_JSON","r",encoding="utf-8"))["SCI"]
delta=b-a
reduction = (-delta/a*100.0) if a else 0.0
print(f"SCI_A = {a}")
print(f"SCI_B = {b}")
print(f"DELTA = {delta}")
print(f"PASS (SCI_B < SCI_A) = {b < a}")
print(f"SUMMARY: SCI_A={a:.6f}, SCI_B={b:.6f}, DELTA={delta:.6f}, REDUCTION={reduction:.2f}%")

# Write summary file (single source of truth)
summary_lines = [
  "UTC=$UTC_NOW",
  "VERSION=$VERSION",
  "GIT=$GIT_HASH",
  "A_GRAPH=$A_GRAPH",
  "B_GRAPH=$B_GRAPH",
  "DOMAIN=$DOMAIN",
  "SOURCES=$SOURCES",
  "MAX_DEPTH=$MAX_DEPTH",
  "MAX_PATHS=$MAX_PATHS",
  "TOP_K=$TOP_K",
  f"SCI_A={a:.12f}",
  f"SCI_B={b:.12f}",
  f"DELTA={delta:.12f}",
  f"REDUCTION={reduction:.4f}%",
  f"PASS={b < a}",
]
open("$SUMMARY_TXT","w",encoding="utf-8").write("\\n".join(summary_lines) + "\\n")
PY

echo "[+] Artifacts saved:"
echo "    - $A_JSON"
echo "    - $B_JSON"
echo "    - $SUMMARY_TXT"
