# AAR-MCP-2.0 Core Specification
Status: Draft 1
Author: AAR Working Group
Date: 2026-02-21

---

## 1. Introduction

This document defines the core evidence protocol for AAR-MCP-2.0.

The protocol specifies:

- Action Attestation Record (AAR)
- Checkpoint structure
- Merkle tree calculation
- Signature rules
- Chain validation rules

This specification defines the Evidence Layer only.
It does not define UI behavior, risk scoring, deployment model, or implementation details.

---

## 2. Terminology

The key words "MUST", "MUST NOT", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "MAY", and "OPTIONAL"
in this document are to be interpreted as described in RFC 2119.

---

## 3. Versioning

Version format:

    AAR-MCP-MAJOR.MINOR

Rules:

- A MAJOR version change indicates breaking structural changes.
- A MINOR version change allows additive, backward-compatible fields.
- Validators MUST reject unknown MAJOR versions.
- Validators SHOULD accept higher MINOR versions.
- Implementations MAY warn on higher MINOR versions.

Current frozen version:

    AAR-MCP-2.0

---

## 4. Action Attestation Record (AAR)

### 4.1 Required Fields

An AAR object MUST contain:

- version
- type
- seq
- tool
- args
- timestamp

Example:

{
  "version": "AAR-MCP-2.0",
  "type": "AAR",
  "seq": 0,
  "tool": "write_file",
  "args": {},
  "timestamp": "2026-02-21T12:00:00Z"
}

### 4.2 Sequence Rules

- seq MUST be an integer.
- seq MUST start at 0.
- seq MUST strictly increase by exactly 1.
- Sequence gaps MUST NOT occur.
- Duplicate seq values MUST NOT occur.
- Validators MUST verify sequence continuity.

### 4.3 Extension Fields

- Additional fields MAY be included.
- Validators MUST ignore unknown fields.
- Extension fields MUST NOT affect signature validation.
- Extension fields MUST NOT alter canonical serialization of required fields.

---

## 5. Checkpoint Structure

### 5.1 Required Fields

A CHECKPOINT object MUST contain:

- version
- type
- range
- merkle_root
- prev_checkpoint_hash
- timestamp
- signature

Example:

{
  "version": "AAR-MCP-2.0",
  "type": "CHECKPOINT",
  "range": [0, 9],
  "merkle_root": "<hex>",
  "prev_checkpoint_hash": null,
  "timestamp": "2026-02-21T12:05:00Z",
  "signature": "<hex>"
}

### 5.2 Range Rules

- range MUST represent continuous seq values.
- range MUST match actual AAR records.
- The first checkpoint MUST use null prev_checkpoint_hash.
- Subsequent checkpoints MUST reference the hash of the immediately preceding checkpoint.
- Validators MUST reject mismatched ranges.

---

## 6. Merkle Tree Rules

- Hash algorithm MUST be SHA256.
- Leaf nodes MUST be the original JSON line string of each AAR record.
- Parent hash MUST be computed as:

      sha256(left + right)

- If an odd number of nodes exists, the last node MUST be duplicated.
- Output MUST be lowercase hexadecimal.
- Validators MUST recompute and compare Merkle roots.

---

## 7. Signature Rules

Signature algorithm:

    Ed25519

Signature input preparation:

- The signature field MUST be removed.
- JSON MUST be serialized with deterministic key ordering (sort_keys=True).
- UTF-8 encoding MUST be used.
- No additional whitespace MUST be introduced.

The resulting byte sequence MUST be signed.

Signature output MUST be lowercase hexadecimal.

Validators MUST verify signatures using the corresponding public key.

---

## 8. Chain Validation

Validators MUST:

1. Verify seq continuity.
2. Verify Merkle root correctness.
3. Verify checkpoint signature using public key.
4. Verify prev_checkpoint_hash chain linkage.
5. Reject any structural inconsistency.
6. Reject missing CHECKPOINT records.

Validation MUST fail on any single violation.

---

## 9. Anchor Definition

Anchor hash:

    sha256(json.dumps(checkpoint, sort_keys=True))

The protocol does not mandate a specific anchoring platform.

Implementations MAY use:

- Git
- Blockchain
- WORM storage
- Public notary systems

Anchoring is OPTIONAL but RECOMMENDED for high-integrity deployments.

---

End of Draft 1.

---

## 10. Security Considerations

This section describes security assumptions and threat boundaries of the AAR-MCP-2.0 protocol.

### 10.1 Integrity Guarantees

The protocol guarantees:

- Tamper-evidence of AAR records within a checkpoint range.
- Cryptographic integrity of checkpoint signatures.
- Chain integrity across multiple checkpoints.
- Public verifiability without private key access.

Any modification, deletion, reordering, or insertion of AAR records
within a sealed range MUST invalidate verification.

Any modification of checkpoint fields covered by signature MUST invalidate verification.

### 10.2 What the Protocol Does NOT Guarantee

The protocol does NOT guarantee:

- Private key security.
- Host system integrity.
- Runtime isolation.
- Prevention of malicious AAR generation prior to sealing.
- Availability of anchor platforms.

If a signing key is compromised, attackers MAY generate valid-looking checkpoints.
Key management is therefore outside the scope of this specification.

### 10.3 Replay and Reordering Attacks

Because seq MUST be strictly increasing and continuous,
validators MUST reject reordered or duplicated AAR records.

Checkpoints MUST bind explicit seq ranges.
Range mismatch MUST invalidate verification.

### 10.4 Truncation Attacks

If a journal is truncated after a valid checkpoint,
verification MUST fail if expected checkpoint continuity is broken.

Implementations SHOULD enforce end-of-file structural checks.

### 10.5 Signature Validation Failure Handling

Validators MUST treat signature verification failure as a fatal error.

Silent acceptance of invalid signatures MUST NOT occur.

### 10.6 Anchor Integrity

Anchoring enhances external tamper resistance.

However, the protocol does NOT mandate a specific anchoring system.

Anchoring platform compromise is outside the protocol boundary.

Implementations SHOULD document anchoring trust assumptions.

---


---

## 11. Implementation Conformance

This section defines requirements for claiming conformance
with the AAR-MCP-2.0 specification.

### 11.1 Conformant Validator

An implementation MAY claim to be a "Conformant Validator"
if and only if it:

- Verifies seq continuity strictly.
- Recomputes and validates Merkle roots.
- Verifies Ed25519 signatures correctly.
- Validates prev_checkpoint_hash linkage.
- Rejects malformed or structurally inconsistent records.
- Fails closed on any verification error.

Partial validation MUST NOT be labeled as conformant.

### 11.2 Conformant Producer

An implementation MAY claim to be a "Conformant Producer"
if it:

- Emits valid AAR records with strictly increasing seq.
- Produces valid CHECKPOINT objects.
- Signs checkpoints using Ed25519.
- Produces canonical JSON for signing.

Producers MAY include extension fields,
but MUST NOT violate core field semantics.

### 11.3 Interoperability

Implementations claiming conformance:

- MUST interoperate with other conformant validators.
- MUST accept unknown extension fields.
- MUST reject unknown MAJOR versions.

### 11.4 Compliance Profiles

Future revisions MAY define compliance profiles,
such as:

- AAR-MCP-2.0-Minimal
- AAR-MCP-2.0-Enterprise
- AAR-MCP-2.0-Anchored

Profiles MUST NOT alter core structural rules.

---

End of Specification.


---

# 2. Normative Requirements (Core Freeze)

## 2.1 Record Types

An AAR-MCP-2.0 journal MUST contain only the following record types:

- `statement`
- `checkpoint`

The following aliases MAY be accepted for backward compatibility:

- `AAR` (equivalent to `statement`)
- `CHECKPOINT` (equivalent to `checkpoint`)

Any other `_record_type` value MUST cause verification failure.




## 2.2 Canonicalization (JCS)

All digests and signatures MUST be computed over the canonical JSON form of the input object using
RFC 8785 JSON Canonicalization Scheme (JCS).

Rules:
- The canonicalization input MUST be UTF-8 JSON text.
- Object member order MUST be canonicalized by JCS (implementations MUST NOT rely on input ordering).
- Whitespace MUST NOT affect the digest (canonical JSON contains no insignificant whitespace).
- Numbers MUST follow RFC8785 canonical form (implementations MUST NOT use language-default float formatting).

If an implementation cannot guarantee RFC8785 canonicalization, it MUST fail closed.


