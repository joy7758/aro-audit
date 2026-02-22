#!/usr/bin/env bash
set -euo pipefail

required_files=(
  "LICENSE"
  "COPYRIGHT"
  "NOTICE"
  "TRADEMARK_POLICY.md"
  "CONTRIBUTING.md"
)

for f in "${required_files[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    exit 1
  fi
 done

missing_headers=0
while IFS= read -r py; do
  if ! grep -q "SPDX-License-Identifier: MIT" "$py"; then
    echo "MISSING SPDX: $py"
    missing_headers=1
  fi
  if ! grep -q "Copyright (c) 2026 joy7758 contributors" "$py"; then
    echo "MISSING COPYRIGHT HEADER: $py"
    missing_headers=1
  fi
done < <(
  find . -type f -name '*.py' \
    -not -path './.venv/*' \
    -not -path './vendor/*' \
    -not -path './.git/*' \
    -not -path './quickstart/out/*'
)

if [[ $missing_headers -ne 0 ]]; then
  exit 1
fi

echo "LEGAL_CHECK_OK"
