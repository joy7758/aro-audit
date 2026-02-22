# FDO-Audit-Profile v1.0
## Draft Specification for Verifiable Lifecycle Integrity

Author: Bin Zhang  
ORCID: 0009-0002-8861-1481  
Reference Implementation DOI: https://doi.org/10.5281/zenodo.18728568  
Registered Profile Identifier: 21.T11966/aro-audit-profile-v1  

---

## 1. Purpose

This specification defines a minimal, composable audit profile for FAIR Digital Objects (FDO), enabling:

- Deterministic lifecycle logging
- Multi-target integrity validation
- Cryptographic verification
- Machine-consumable verification reporting

The profile introduces no external runtime dependencies and remains implementation-agnostic.

---

## 2. Architectural Scope

The FDO-Audit-Profile operates as a verification boundary layer and does not alter:

- FDO identity model
- Core metadata schema
- Handle resolution behavior

It adds an optional integrity subsystem.

---

## 3. Core Components

### 3.1 Manifest Structure

Defines integrity targets.

Required fields:

- manifest_version
- targets[]
- audit_policy
- manifest_sha256

Targets may include:

- DPP JSON
- Certificate PDF
- SBOM
- Any digital artifact

---

### 3.2 Journal (JSONL)

Append-only hash-chain log.

Each entry includes:

- sequence_no
- prev_digest
- event_payload_sha256
- object_state_sha256
- signature

This guarantees tamper-evident lifecycle traceability.

---

### 3.3 Verification Engine

Deterministic process:

1. Validate manifest integrity
2. Recompute target hashes
3. Validate journal hash-chain
4. Verify Ed25519 signatures
5. Emit verification_report.json

---

## 4. Verification Report Schema

Machine-readable output:

- manifest_valid
- targets_valid
- journal_chain_valid
- signatures_valid
- overall_status
- timestamp

Designed for automated compliance pipelines.

---

## 5. Composability

The profile:

- Does not mandate storage backend
- Does not mandate registry behavior
- Does not mandate policy logic

It provides a portable audit substrate.

---

## 6. Standardization Path

Proposed progression:

1. FDO Working Group discussion
2. Interoperability testing
3. Formal FDO Profile Recommendation
4. CEN/ISO liaison consideration

---

## 7. Industrial Use Cases

- Digital Product Passport (DPP)
- Battery Passport
- Cross-border compliance verification
- Supply chain lifecycle auditing

---

## 8. Conformance

An implementation conforms if it:

- Produces a valid manifest
- Maintains deterministic journal chain
- Provides public-key verifiable signatures
- Emits verification_report.json matching schema

---

## 9. Security Considerations

- Private keys MUST NOT be distributed.
- Public keys SHOULD be anchored via trusted identity mechanisms.
- Manifest MUST be immutable once published.

---

## 10. Reference Implementation

GitHub:
https://github.com/joy7758/aro-audit

Archived bundle:
Zenodo DOI above.

---

End of Draft Specification v1.0
