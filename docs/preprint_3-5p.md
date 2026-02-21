# AAR/ALC: WORM-Backed Verifiable Statements for Non-Repudiable Agent Auditing (v1.0 Baseline)

**Author:** Zhang Bin  
**Date:** 2026-02-21  
**Code & Artifacts:** `aro` CLI, `audit_packet.zip` (journal + manifest + verify)

---

## Abstract
AI agents are rapidly entering production environments, but current audit trails are often non-deterministic, privacy-leaking, or non-verifiable, making post-incident attribution and compliance difficult. We introduce **Agent Action Receipts (AAR)** and **Agent Liability Chains (ALC)**: an attestation-grade auditing substrate that turns agent tool invocations into **verifiable statements** stored in an append-only **WORM** journal. AAR/ALC provides deterministic hashing (RFC 8785 JCS + SHA-256), chain integrity (prev-digest), periodic checkpoint sealing (range + Merkle root + store fingerprint), and organization-level accountability via sub-key checkpoint signatures. We provide a reproducible artifact bundle and a verification command enabling third-party independent validation.

---

## 1. Problem Statement
Production agents face three governance gaps:
1) **Privilege confusion and overreach** (permission fragmentation, prompt injection, “confusable deputy” risk)  
2) **Non-replayable evidence** (logs are incomplete, scattered, or mutable)  
3) **Non-admissible records** (difficult to independently verify and to sample-audit at scale)

These gaps translate to board-level risk and impede compliance adoption.

---

## 2. Design Goals
- **Verifiability:** third parties can recompute hashes and validate seals  
- **Non-repudiation (baseline):** organization-level checkpoint signing (Level-1 evidence)  
- **Privacy-first:** No-Plaintext rule; store hashes + controlled locators only  
- **Reproducibility:** test vectors + deterministic canonicalization (RFC 8785 JCS)  
- **Low-friction adoption:** CLI first, MCP insertion point later

---

## 3. AAR v1.0 Baseline
Each AAR is a **verifiable statement** (JSON object) written to an append-only JSONL journal.

### 3.1 Frozen Rule #1: Canonicalization + Digest + Signing Input
To avoid recursive-signing pitfalls and cross-language divergence, AAR v1.0 fixes:
- Redaction first (No-Plaintext)  
- Signature input object `S_sig` excludes `attestations` and `checkpoint`  
- Canonicalization: RFC 8785 JCS → `canonical_bytes`  
- Digest: `sha256(canonical_bytes)` → `sha256:<hex>`  
- Attestations bind `signed_digest` (baseline binds digest)

---

## 4. ALC and Checkpoint Sealing
### 4.1 Frozen Rule #2: WORM Checkpoint with Explicit Coverage Range
Journal is append-only. Every N statements a **checkpoint record** is appended:
- `range_start_seq..range_end_seq`
- `merkle_root` over statement digests in range
- `store_fingerprint` (sha256 over journal bytes at seal time)
- `checkpoint_sig` signed by organization sub-key
This makes deletion or mutation detectable via independent verification.

### 4.2 Frozen Rule #3: Single-writer per Trace (v1.0)
A single writer per trace ensures a linear time-arrow:
- `sequence_no` monotonic
- `prev_digest` equals prior statement digest

Multi-writer is explicitly out-of-scope for v1.0 and requires sub-trace anchoring.

---

## 5. Reproducibility and Independent Verification
We publish an artifact bundle (`audit_packet.zip`) containing:
- `journal.jsonl` (facts)
- `AAR-Manifest.json` (summary + verification command)
- `verify.sh` (one-command verification)
- key material (demo only)

Verification command example:
`python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_subkey_ed25519.pem`

---

## 6. MCP Insertion Point (Roadmap)
The shortest “must-pass gate” is tool invocation in MCP servers:
- wrap `call_tool` to emit AAR before/after tool execution
- enforce “no AAR pointer, no enterprise acceptance” at gateways

---

## 7. Discussion: Evidence Levels and Commercialization
- **Open layer:** schema + journal + verify (adoption)
- **Paid layer:** policy packs, certification, proof-as-a-service (interpretation/recognition network)
Risk scoring is kept in interpretation layers (Index/Manifest), not in the immutable fact journal.

---

## 8. Conclusion
AAR/ALC converts agent actions into deterministic, privacy-first, independently verifiable records with organization-level accountability. The v1.0 baseline establishes a minimal substrate for enterprise-grade governance and standards participation.

