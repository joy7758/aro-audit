# Execution Receipt Demo

Showing how a verifiable agent run can produce a compact execution receipt.

This is a demo example for repository entry and review. It does not change the current specification or conformance surface of ARO Audit.

## Scenario

An internal agent run prepares a short procurement summary and emits a compact receipt for later review.

## Input Context

The demo starts from a minimal run input with actor, model, tool set, and a short task summary:

- [agent-run.input.example.json](../../examples/receipts/agent-run.input.example.json)

## Example Receipt

The sample receipt keeps only the fields needed for a small review loop: run identity, timing, actor, model, tools, summaries, policy signals, cost summary, and outcome.

- [agent-run.receipt.example.json](../../examples/receipts/agent-run.receipt.example.json)

## Review Signals

The policy signals in the example are intentionally compact. They show whether the run stayed within declared boundaries and whether the receipt is ready for reviewer handoff.

## Why this matters

Compact execution receipts make agent runs easier to verify, discuss, and hand off across teams. The point of this demo is evidence visibility and reviewability, not a change to the repository's existing spec.
