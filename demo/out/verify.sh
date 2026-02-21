#!/bin/bash
set -euo pipefail
tools/python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_pubkey_ed25519.pem
