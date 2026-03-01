#!/usr/bin/env bash
set -euo pipefail

echo "[NEGATIVE] fork syscall should be blocked"

CC="${CC:-gcc}"
if ! command -v "${CC}" >/dev/null 2>&1; then
  echo "❌ compiler not found: ${CC}"
  exit 2
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

cat <<'EOF' > "${TMP_DIR}/fork_test.c"
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    pid_t pid = fork();
    if (pid < 0) {
        return 2;
    }
    if (pid == 0) {
        _exit(0);
    }
    int status = 0;
    if (waitpid(pid, &status, 0) < 0) {
        return 3;
    }
    return 0;
}
EOF

"${CC}" "${TMP_DIR}/fork_test.c" -o "${TMP_DIR}/fork_test"

run_target() {
  local binary_path="$1"
  if [[ -n "${CONFORMANCE_EXEC_WRAPPER:-}" ]]; then
    "${CONFORMANCE_EXEC_WRAPPER}" "${binary_path}"
  else
    "${binary_path}"
  fi
}

if run_target "${TMP_DIR}/fork_test" 2>/dev/null; then
  echo "❌ fork succeeded (unexpected)"
  exit 1
else
  echo "✅ fork blocked as expected"
fi
