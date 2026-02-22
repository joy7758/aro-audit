# DPP Battery Example (Demo) - ARO-Audit Lifecycle Integrity

This example demonstrates how to attach an audit-ready, append-only lifecycle integrity layer
to a DPP-like JSON object using the ARO Audit Profile concept.

Design goals:
- Running code (Python standard library only)
- Deterministic verification (canonical JSON + sha256 chain)
- Composable boundary (audit layer does not impose business semantics on `dpp.json`)
- FDO-aligned metadata declaration (`profile_handle` + manifest + verifiable journal)

## Contents

- `dpp.json`
A minimal DPP-like object (battery demo).

- `manifest.json`
Declares policy and integrity anchors:
- `integrity.target_sha256`
- `integrity.journal_sha256`
- `integrity.last_entry_hash`
- `profile_handle`
- `identity_anchor.public_key_fingerprint`

- `journal.jsonl`
Append-only event stream.
Each record contributes to:
`entry_hash = sha256(prev_entry_hash + canonical_entry_json)`

- `record_event.py`
Appends lifecycle events and updates manifest integrity fields.

- `verify_dpp.py`
Independent verifier for:
- required fields
- hash-chain continuity
- recomputed entry hashes
- manifest integrity consistency
- final state consistency between `dpp.json` and latest event

## Quick Start

From this directory:

1. Create first event
```bash
python3 record_event.py --event created --actor manufacturer
```

2. Verify integrity
```bash
python3 verify_dpp.py
```

Expected output includes:
- `VERIFY_OK: Lifecycle integrity intact ...`
- printed hashes for target/journal/last entry

3. Modify `dpp.json`, append another event, verify again
```bash
python3 record_event.py --event updated_recycled_content --actor manufacturer
python3 verify_dpp.py
```

## Why This Boundary Matters

Typical FDO workflows solve identity and resolution.
This attachment solves interaction integrity over lifecycle mutations.

Boundary separation:
- `dpp.json` = business object
- `journal.jsonl` + `manifest.json` = audit layer
- verification = independent and reproducible

## Extension Points

- Per-entry or snapshot signatures (optional)
- Multi-target manifests (SBOM, reports, certificates)
- Alternate governance policies via `audit_policy`

## References

- ARO Audit Profile (Testbed): `21.T11966/aro-audit-profile-v1`
- Repository: `https://github.com/joy7758/aro-audit`
- DOI archive: `https://doi.org/10.5281/zenodo.18728568`
