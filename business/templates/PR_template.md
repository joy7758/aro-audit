# Title
Integrate aro-audit AAR/ALC evidence export into <PROJECT>

## Summary
- What changed:
- Why it matters (audit/compliance):
- Scope and non-goals:

## Verification
```bash
aro gen-demo
aro export
python3 sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_pubkey_ed25519.pem
```

## Deliverables
- `audit_packet.zip` (journal + manifest + verify.sh + README + public key)

## Notes
- No private keys are shipped.
- Verification is public-key-only.
