# ARO Audit Profile

ARO Audit Profile defines an evidence-layer protocol for high-authority AI actions.
Operationally, it functions as an **immune system** for agent execution: it continuously records, seals, and verifies action traces, so unauthorized mutation is detected during audit and replay.

## Credentials

- FDO Testbed ID: `21.T11966/aro-audit-profile-v1`
- DOI: `https://doi.org/10.5281/zenodo.18728568`

## Core Components

1. Audit Manifest
- Detached metadata contract for verification context, checkpoint windowing, and key fingerprint references.

2. Journal (JSONL)
- Append-only event stream containing action records and checkpoint records.
- Each non-empty line is protocol material and is subject to verifier rules.

3. Verification Engine
- Recomputes chain integrity, Merkle consistency, checkpoint signatures, and range continuity.
- Fails closed on structural, cryptographic, or ordering violations.

4. Public Key Anchoring
- Ed25519 public key anchors trust for checkpoint signature validation.
- Enables independent third-party verification without private key access.

## Hash-Chain Logic

Execution continuity is modeled as:

\[
Root_{n} = \mathcal{H}(Root_{n-1} \parallel \text{Event}_{n})
\]

Where:
- `Root_n` is the cumulative integrity state after event `n`
- `\mathcal{H}` is the canonical hash function over normalized event bytes
- `\parallel` is byte concatenation

## Quickstart

```bash
bash quickstart/run.sh
```

Success criteria:
- baseline sample: `VERIFY_OK: full chain valid`
- tampered sample: verification rejection (`Merkle mismatch` / digest / signature failure)

## Open Discussion

Critical questions currently under community review (from mailing-list discussion):

1. Digest Boundary Contract
- Should the boundary remain fixed to core execution fields only, with all non-evidence metadata explicitly excluded?

2. Checkpoint Semantics and Interop
- Are `range`, `merkle_root`, and `prev_checkpoint_hash` definitions strict enough to prevent segmented replay/rebuild ambiguity across implementations?

3. Governance and Trust Anchoring
- What is the minimum acceptable anchoring policy (Git/WORM/notary/transparency log) for profile-level compliance claims?

Discussion channels:
- Review Guidelines: `https://github.com/joy7758/aro-audit/discussions/3`
- Issue Tracker: `https://github.com/joy7758/aro-audit/discussions/4`

