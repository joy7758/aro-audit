#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo " AAR-MCP-2.0 High Risk Demo"
echo "=============================="
echo

echo "1️⃣ Generating high-risk action..."
python3 run_demo.py

echo
echo "2️⃣ Verifying integrity..."
python3 -m sdk.verify.verify_chain journal.jsonl public.pem

echo
echo "3️⃣ Simulating tampering..."
cp journal.jsonl journal.attack.jsonl
python3 - <<'PY'
from pathlib import Path
import json

path = Path("journal.attack.jsonl")
rows = []
tampered = False
for raw in path.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    obj = json.loads(raw)
    if not tampered and obj.get("type") == "AAR":
        args = obj.get("args", {})
        if isinstance(args, dict) and "amount" in args:
            args["amount"] = 10
            tampered = True
    rows.append(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
path.write_text("\n".join(rows) + "\n", encoding="utf-8")
print("tampered:", tampered)
PY

echo
echo "4️⃣ Verifying tampered journal..."
python3 -m sdk.verify.verify_chain journal.attack.jsonl public.pem || true

echo
echo "=============================="
echo " Demo complete"
echo "=============================="
