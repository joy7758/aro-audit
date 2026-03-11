# Conformance Vectors RC1+

## Purpose

This document restates the current conformance surface in a standard-vector
format. It keeps the current RC1 boundary vectors visible, then adds a small
set of hardening vectors that are useful for future work without claiming that
they are already implemented.

## Baseline vectors

| Vector | Scenario | Expected gate behavior | Expected evidence artifact | Current support level |
| --- | --- | --- | --- | --- |
| baseline pass | Verify the untouched boundary sample in `spec/test_vectors/boundary_base_v1.jsonl` using `tools/run_conformance.sh`. | MUST pass with exit code `0` and verifier output indicating the chain is valid. | Baseline vector file, verifier stdout, and any generated report from the conformance driver. | present |
| credential-only pass | Verify `spec/test_vectors/boundary_attack_attestations_only.jsonl`, where changes stay outside the protected fact boundary. | MUST still pass because the mutation does not alter the signed or digested fact surface. | Credential-only vector file plus verifier stdout showing acceptance. | present |
| predicate tamper fail | Verify `spec/test_vectors/boundary_attack_predicate.jsonl`, where fact-bearing predicate content is changed. | MUST fail with a non-zero exit and a mismatch error such as digest or Merkle failure. | Predicate-tamper vector file plus verifier failure output. | present |

## Additional hardening vectors

| Vector | Scenario | Expected gate behavior | Expected evidence artifact | Current support level |
| --- | --- | --- | --- | --- |
| identity drift | An action record or compact receipt shows actor or identity context drifting across a run without an explicit handoff. | SHOULD fail review or emit an explicit drift signal once a fixed vector exists. | Candidate receipt or vector fixture showing actor mismatch and reviewer-visible drift evidence. | partial |
| resource exhaustion | A run stays structurally valid but crosses a resource or cost boundary that should still be visible for review. | SHOULD preserve the evidence artifact and surface the exhaustion condition as a review signal rather than silently hiding it. | Cost-aware receipt fields, runtime summaries, or candidate vector fixtures showing boundary strain. | partial |
| timestamp replay | A receipt or journal is replayed outside an intended freshness window or reused as if newly produced. | SHOULD fail freshness review once replay vectors are fixed, even if the artifact remains structurally parseable. | Candidate replay fixture with stale timestamps, verifier notes, and reviewer-visible freshness fields. | partial |

## Expected pass/fail behavior

- Baseline vectors are the current fixed conformance floor: baseline pass and
  credential-only pass must succeed, while predicate tamper must fail.
- Additional hardening vectors are not fixed conformance requirements yet.
  They should be treated as candidate tests for the next hardening phase.
- A failing vector should produce a bounded verification surface: the reviewer
  should be able to see which artifact failed and why, without needing the
  whole runtime.

## Evidence produced

Current evidence surfaces related to these vectors include:

- `spec/test_vectors/boundary_base_v1.jsonl`
- `spec/test_vectors/boundary_attack_attestations_only.jsonl`
- `spec/test_vectors/boundary_attack_predicate.jsonl`
- `tools/run_conformance.sh`
- `quickstart/out/journal.jsonl`
- `quickstart/out/journal.tampered.jsonl`
- `quickstart/out/run.log`
- `docs/assets/demo_output.txt`

These files are useful because they keep conformance discussion tied to
exportable evidence rather than to repository narration alone.
