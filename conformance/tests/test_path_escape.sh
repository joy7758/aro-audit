#!/usr/bin/env bash
set -euo pipefail

echo "[NEGATIVE] write outside confined directory should fail"

TARGET="${CONFORMANCE_ESCAPE_TARGET:-${HOME}/.aro_conformance_escape_test}"
TARGET_PARENT="$(dirname "${TARGET}")"

if [[ ! -w "${TARGET_PARENT}" ]]; then
  echo "❌ target parent is not writable for this user: ${TARGET_PARENT}"
  echo "This is inconclusive. Set CONFORMANCE_ESCAPE_TARGET to a writable path outside confinement."
  exit 2
fi

if printf "test\n" > "${TARGET}" 2>/dev/null; then
  rm -f "${TARGET}"
  echo "❌ path escape succeeded (unexpected): ${TARGET}"
  exit 1
else
  echo "✅ path escape blocked as expected"
fi
