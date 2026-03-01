#!/usr/bin/env bash
set -euo pipefail

echo "[NEGATIVE] outbound network should be blocked"

CC="${CC:-gcc}"
if ! command -v "${CC}" >/dev/null 2>&1; then
  echo "❌ compiler not found: ${CC}"
  exit 2
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

cat <<'EOF' > "${TMP_DIR}/net_test.c"
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

int main(void) {
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0) {
        return 1;
    }
    close(s);
    return 0;
}
EOF

"${CC}" "${TMP_DIR}/net_test.c" -o "${TMP_DIR}/net_test"

run_target() {
  local binary_path="$1"
  if [[ -n "${CONFORMANCE_EXEC_WRAPPER:-}" ]]; then
    "${CONFORMANCE_EXEC_WRAPPER}" "${binary_path}"
  else
    "${binary_path}"
  fi
}

if run_target "${TMP_DIR}/net_test" 2>/dev/null; then
  echo "❌ network socket created (unexpected)"
  exit 1
else
  echo "✅ network blocked as expected"
fi
