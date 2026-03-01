#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${ROOT_DIR}/tests"
REPORT_GENERATOR="${ROOT_DIR}/report_generator.sh"

echo "Running RC1 Confinement Negative Tests"

SECCOMP_RESULT="UNKNOWN"
NETWORK_RESULT="UNKNOWN"
PATH_RESULT="UNKNOWN"

HAS_FAIL=0
HAS_INCONCLUSIVE=0

run_negative_test() {
  local test_name="$1"
  local test_script="$2"
  local result_var="$3"
  local rc=0

  if bash "${test_script}"; then
    printf -v "${result_var}" "%s" "PASS"
  else
    rc=$?
    if [[ "${rc}" -eq 2 ]]; then
      printf -v "${result_var}" "%s" "INCONCLUSIVE"
      HAS_INCONCLUSIVE=1
    else
      printf -v "${result_var}" "%s" "FAIL"
      HAS_FAIL=1
    fi
  fi

  echo "[SUMMARY] ${test_name}: ${!result_var}"
  return 0
}

run_negative_test "syscall_mediation" "${TEST_DIR}/test_seccomp_block.sh" SECCOMP_RESULT
run_negative_test "network_io_block" "${TEST_DIR}/test_network_block.sh" NETWORK_RESULT
run_negative_test "path_escape_prevention" "${TEST_DIR}/test_path_escape.sh" PATH_RESULT

if [[ -x "${REPORT_GENERATOR}" ]]; then
  "${REPORT_GENERATOR}" "${SECCOMP_RESULT}" "${NETWORK_RESULT}" "${PATH_RESULT}"
else
  echo "ERROR: report generator missing or not executable: ${REPORT_GENERATOR}"
  HAS_INCONCLUSIVE=1
fi

if [[ "${HAS_FAIL}" -eq 1 ]]; then
  echo "Negative tests failed."
  exit 1
fi

if [[ "${HAS_INCONCLUSIVE}" -eq 1 ]]; then
  echo "Negative tests inconclusive."
  exit 2
fi

echo "All negative tests passed."
