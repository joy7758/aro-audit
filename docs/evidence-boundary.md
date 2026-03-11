# Evidence Boundary

## Logs vs receipts vs evidence bundle

| Artifact type | What it captures | What it is not | Current repo examples |
| --- | --- | --- | --- |
| logs | Raw runtime output, operator messages, or verifier console text. | Logs alone are not the whole evidence surface because they are hard to hand off and easy to misread without context. | `quickstart/out/run.log`, `docs/assets/demo_output.txt` |
| receipts | Compact, review-ready summaries of a run or action boundary. | A receipt is not automatically a full chain proof or a complete runtime narrative. | `examples/receipts/agent-run.receipt.example.json` |
| evidence bundle | A reviewable set of artifacts that lets another party inspect what happened on a bounded verification surface. | It is not just observability exhaust. It must be exportable evidence that can leave the original runtime. | `quickstart/out/journal.jsonl`, `quickstart/out/public.pem`, bundle outputs described in the README |

## Minimal reviewable artifact

For a compact human review loop, the minimal reviewable artifact in this
repository is `examples/receipts/agent-run.receipt.example.json`. It keeps the
review surface small enough to inspect actor, tools, summaries, cost signals,
and outcome without parsing the full repository.

For structural verification, a stronger minimal set is `quickstart/out/journal.jsonl`
plus `quickstart/out/public.pem` and the verifier result. That set gives a
bounded verification surface for chain integrity without claiming to explain
the whole runtime.

## Exportability requirement

Evidence in this repository is meant to be portable. A reviewer should be able
to receive the journal, receipt, public key, manifest, or verifier output
outside the original execution environment and still inspect the result.
Without exportable evidence, review becomes a trust-me workflow instead of a
verifiable handoff.

## Why observability alone is insufficient

Observability can tell you what a system printed. It does not automatically
tell you what should count as the review surface, which fields are meant to be
stable, or what another party can verify independently.

ARO Audit therefore treats receipts, journals, and related artifacts as a
bounded verification surface rather than as generic log exhaust. The goal is
not the whole stack. The goal is exportable evidence that can survive handoff
to another reviewer, team, or verifier.
