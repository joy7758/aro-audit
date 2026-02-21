# Audit Remediation Sync (2026-02-21)

This file maps the findings in `AAR_ALC 证据层协议与实现深度审计与攻防演练报告` to concrete repository fixes.

## Scope

- Repository: `aro-audit`
- Baseline target: `AAR-MCP-2.0` flow (`wrapper -> journal -> checkpoint -> verify`)

## Finding-to-Fix Map

1. `F-01` MCP method bypass (`call_tool` vs `tools/call`)
- Status: Fixed
- Changes:
  - `sdk/mcp_server_wrapper/wrapper.py`
  - Wrapper now recognizes `tools/call` (spec path) and keeps `call_tool` as compatibility alias.
  - Fail-closed response path returns JSON-RPC error and blocks forwarding on evidence failure.

2. `F-02` Protocol drift / incompatible writer-verifier behavior
- Status: Fixed for active `AAR-MCP-2.0` path
- Changes:
  - `sdk/mcp_server_wrapper/wrapper.py`
  - `sdk/verify/verify_chain.py`
  - `sdk/verify/verify_checkpoint.py`
  - Unified canonical JSON for signing and hashing (`sort_keys=True`, compact separators).
  - Unified checkpoint chain hash calculation and segmented range verification.

3. `F-03` Private key material committed in repository
- Status: Fixed
- Changes:
  - Removed committed key artifacts:
    - `demo/high_risk_authority/private.pem`
    - `demo/high_risk_authority/public.pem`
  - Added ignore rules:
    - `.gitignore`
      - `demo/high_risk_authority/*.pem`
      - `demo/high_risk_authority/*.jsonl`
      - `demo/out/*.jsonl`
      - `anchor.log`

4. `F-04` Plaintext sensitive args in evidence records
- Status: Fixed
- Changes:
  - `sdk/mcp_server_wrapper/wrapper.py`
  - Added `sanitize_args()` and `args_hash` recording.
  - Sensitive fields (`password/token/secret/...`) are redacted + hashed.

5. `F-05` Anchor robustness (overwrite/silent failure)
- Status: Fixed (Git anchor path)
- Changes:
  - `sdk/anchor/git_anchor.py`
  - Append-only `anchor.log` entries with timestamp.
  - Canonical checkpoint hash input.
  - Git operations now check status and avoid silent failures.

6. `F-06` Journal write race / no lock
- Status: Fixed
- Changes:
  - `sdk/journal/jsonl_journal.py`
  - Added internal lock and canonical append behavior.
  - Added explicit flush + fsync control.

7. `F-07` Performance degradation from full-file re-read/re-hash on each call
- Status: Fixed
- Changes:
  - `sdk/mcp_server_wrapper/wrapper.py`
  - Added in-memory `JournalState` with incremental pending segment tracking.
  - Checkpoint generation now works on pending segment only.

8. `F-08` Dependency declaration gap
- Status: Fixed (direct dependency declaration)
- Changes:
  - `pyproject.toml`
  - `requirements.txt`
  - Added missing dependency: `pyyaml`

## Additional Hygiene

- Removed stale drift artifacts:
  - `sdk/journal/jsonl_journal.py.bak`
  - `sdk/mcp_server_wrapper/wrapper.py.bak`
- Updated CLI compatibility:
  - `sdk/cli/aro.py`
  - Restored callable entrypoint (`app`) and command dispatch return codes.

## Verification Commands

```bash
cd demo/high_risk_authority
source ../../.venv/bin/activate
./run.sh
```

Expected:
- Original journal: `VERIFY_OK: full chain valid`
- Tampered journal: verification failure (e.g. `Merkle mismatch`)
