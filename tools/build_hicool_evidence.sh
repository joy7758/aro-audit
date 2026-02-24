#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="${1:-/Users/zhangbin/GitHub}"
ARO_DIR="${2:-$BASE_DIR/aro-audit}"
OUT_DIR="${3:-$ARO_DIR/competition/hicool-2026}"
OUT_FILE="$OUT_DIR/EVIDENCE.md"

REPOS=(aro-audit safety-valve-spec god-spear)

mkdir -p "$OUT_DIR"

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
spear_adoption_count="$(
  find "$BASE_DIR" -maxdepth 5 -type f -path "*/.github/workflows/spear.yml" 2>/dev/null | wc -l | tr -d ' '
)"

repo_slug() {
  local repo_path="$1"
  local origin
  origin="$(git -C "$repo_path" remote get-url origin 2>/dev/null || true)"
  if [[ -z "$origin" ]]; then
    echo "local-only"
    return
  fi
  origin="${origin#git@github.com:}"
  origin="${origin#https://github.com/}"
  origin="${origin%.git}"
  echo "$origin"
}

latest_run() {
  local slug="$1"
  if ! command -v gh >/dev/null 2>&1 || [[ "$slug" == "local-only" ]]; then
    echo "unavailable"
    return
  fi
  gh run list -R "$slug" -L 1 --json workflowName,conclusion,createdAt \
    -q 'if length==0 then "none" else .[0] | "\(.workflowName):\(.conclusion)@\(.createdAt)" end' \
    2>/dev/null || echo "unavailable"
}

spear_run() {
  local slug="$1"
  if ! command -v gh >/dev/null 2>&1 || [[ "$slug" == "local-only" ]]; then
    echo "unavailable"
    return
  fi
  gh run list -R "$slug" -w spear-check -L 1 --json conclusion,createdAt \
    -q 'if length==0 then "none" else .[0] | "\(.conclusion)@\(.createdAt)" end' \
    2>/dev/null || echo "unavailable"
}

artifact_flag() {
  local repo="$1"
  local repo_path="$2"
  case "$repo" in
    aro-audit)
      if [[ -f "$repo_path/demo/out/AAR-Manifest.json" && -f "$repo_path/demo/out/verify.sh" ]]; then
        echo "demo_bundle_ready"
      else
        echo "demo_bundle_missing"
      fi
      ;;
    safety-valve-spec)
      if [[ -f "$repo_path/spec/receipt-v0.1.md" && -f "$repo_path/conformance/tests.md" ]]; then
        echo "spec_and_conformance_ready"
      else
        echo "spec_or_conformance_missing"
      fi
      ;;
    god-spear)
      if [[ -f "$repo_path/ADOPTION.md" && -f "$repo_path/.github/workflows/spear.yml" ]]; then
        echo "adoption_and_ci_ready"
      else
        echo "adoption_or_ci_missing"
      fi
      ;;
    *)
      echo "unknown"
      ;;
  esac
}

{
  echo "# HICOOL 2026 Evidence Snapshot"
  echo
  echo "- Generated (UTC): $timestamp"
  echo "- Base directory: $BASE_DIR"
  echo "- spear-check adoption count: $spear_adoption_count"
  echo
  echo "## Unified Stack Health"
  echo
  echo "| Component Repo | Branch | Last Commit | Last Commit Date | Latest Run | Latest spear-check | Artifact Readiness |"
  echo "|---|---|---|---|---|---|---|"
} > "$OUT_FILE"

for repo in "${REPOS[@]}"; do
  repo_path="$BASE_DIR/$repo"
  if [[ ! -d "$repo_path/.git" ]]; then
    echo "| $repo | missing | - | - | - | - | - |" >> "$OUT_FILE"
    continue
  fi

  branch="$(git -C "$repo_path" branch --show-current || echo "-")"
  last_commit="$(git -C "$repo_path" log -1 --pretty=format:'%h' || echo "-")"
  last_date="$(git -C "$repo_path" log -1 --pretty=format:'%ad' --date=short || echo "-")"
  slug="$(repo_slug "$repo_path")"
  run_status="$(latest_run "$slug")"
  spear_status="$(spear_run "$slug")"
  artifacts="$(artifact_flag "$repo" "$repo_path")"

  echo "| $slug | $branch | $last_commit | $last_date | $run_status | $spear_status | $artifacts |" >> "$OUT_FILE"
done

{
  echo
  echo "## Notes"
  echo
  echo "- This snapshot is generated locally and intended for pitch/supporting materials."
  echo "- Use this file together with \`competition/hicool-2026/README.md\` and \`competition/hicool-2026/MATURITY_PLAN.md\`."
} >> "$OUT_FILE"

echo "Generated: $OUT_FILE"
