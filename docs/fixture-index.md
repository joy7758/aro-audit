# Fixture Index

This index lists the current demo, fixture, and example files that are useful
for review loops, conformance checks, and evidence handoff.

## Compact receipt review

- `docs/demos/execution-receipt-demo.md` — short walkthrough for the compact execution receipt example.
- `examples/receipts/agent-run.input.example.json` — minimal input context for a reviewable run.
- `examples/receipts/agent-run.receipt.example.json` — compact receipt artifact for reviewer handoff.

## Conformance fixtures

- `spec/test_vectors/boundary_base_v1.jsonl` — baseline pass vector for the current boundary surface.
- `spec/test_vectors/boundary_attack_attestations_only.jsonl` — mutation outside the protected fact boundary; expected pass.
- `spec/test_vectors/boundary_attack_predicate.jsonl` — fact-boundary mutation; expected fail.
- `tools/run_conformance.sh` — driver script for the current boundary vectors.

## Quickstart outputs

- `quickstart/out/journal.jsonl` — generated baseline journal for the shortest structural verification loop.
- `quickstart/out/journal.tampered.jsonl` — generated tampered journal used for failure detection.
- `quickstart/out/public.pem` — public key used by the quickstart verifier.
- `quickstart/out/run.log` — captured pass/fail output from the quickstart loop.

## Lifecycle integrity demo

- `examples/dpp-battery/README.md` — entry point for the DPP-style lifecycle integrity example.
- `examples/dpp-battery/dpp.json` — business object used by the demo.
- `examples/dpp-battery/manifest.json` — integrity anchor and profile declaration for the demo.
- `examples/dpp-battery/journal.jsonl` — append-only lifecycle journal.
- `examples/dpp-battery/verification_report.json` — generated verification artifact for the demo.
