# AROAUDIT_PROFILE_V1 (Draft)

This profile defines the minimum fields for an "audit-ready" digital object.

## Required Fields (on the Digital Object)
- manifest: a link/handle/URL pointing to the audit manifest
- journal: a link/handle/URL pointing to the audit journal (event log)
- pubkey_fingerprint: the fingerprint of the public key used for signatures

## Manifest (Minimum)
The manifest MUST describe the audit package contents and include file hashes.

## Journal (Minimum)
The journal MUST record the ordered audit events for traceability.

## Verification
A verifier can:
1) fetch manifest + journal
2) check hashes/signatures
3) output PASS/FAIL
