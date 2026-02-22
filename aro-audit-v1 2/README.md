# ARO-Audit v1.0

ARO-Audit introduces a declarative audit overlay for digital objects enabling cryptographically verifiable execution provenance.

## Components

- Hash-chained journal
- Merkle checkpoint manifest
- Ed25519 signature verification
- Registry-compatible metadata declaration

## Files Included

- ARO-Audit.pdf (paper)
- journal.jsonl (sample journal)
- AAR-Manifest.json (detached manifest)
- org_pubkey_ed25519.pem (public key)
- verify.py (verification script)

## Verification

Run:

python verify.py journal.jsonl org_pubkey_ed25519.pem

Expected output:

VERIFY_OK: journal.jsonl statements=10
