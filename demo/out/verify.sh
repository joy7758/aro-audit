#!/bin/bash
set -euo pipefail
/Users/zhangbin/aro-audit/tools/python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_subkey_ed25519.pem
