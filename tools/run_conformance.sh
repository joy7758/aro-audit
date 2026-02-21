#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install -U pip
if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
fi
python -m pip install -e .

echo "== base must pass =="
python sdk/verify/verify.py spec/test_vectors/boundary_base_v1.jsonl demo/out/org_pubkey_ed25519.pem

echo "== attestations-only mutation must still pass =="
python sdk/verify/verify.py spec/test_vectors/boundary_attack_attestations_only.jsonl demo/out/org_pubkey_ed25519.pem

echo "== predicate mutation must fail =="
if python sdk/verify/verify.py spec/test_vectors/boundary_attack_predicate.jsonl demo/out/org_pubkey_ed25519.pem; then
  echo "ERROR: predicate mutation unexpectedly passed (boundary broken)"
  exit 2
else
  echo "OK: predicate mutation rejected"
fi

echo "✅ CONFORMANCE_OK: boundary gate holds"
