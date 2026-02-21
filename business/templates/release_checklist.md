# Release Checklist (Evidence + Legal)

## Functional
- [ ] `aro gen-demo` runs successfully
- [ ] `aro export` runs successfully
- [ ] public-key verification returns `VERIFY_OK`

## Artifact Hygiene
- [ ] `audit_packet.zip` includes only: journal, manifest, verify.sh, README, public key
- [ ] release bundle contains no private key material

## Legal Baseline
- [ ] `tools/check_legal.sh` returns `LEGAL_CHECK_OK`
- [ ] `LICENSE`, `COPYRIGHT`, `NOTICE`, `TRADEMARK_POLICY.md`, `CONTRIBUTING.md` exist
- [ ] README legal links are valid
