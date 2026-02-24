# Maturity Sprint Plan (8 Weeks)

## Goal

Raise the unified entry from "strong open-source protocol set" to "competition-grade venture project" with measurable delivery.

## Milestones

1. Week 1-2: Product unification and demo hardening
- Deliver one public architecture diagram and one end-to-end demo script.
- Acceptance: external reviewer can run demo and reproduce verification output in under 15 minutes.

2. Week 3-4: Conformance and evidence quality upgrade
- Add fixed test vectors for ALLOW, DENY, DEGRADE, and tamper cases.
- Acceptance: repeatable reports generated in CI and attached as artifacts.

3. Week 5-6: Commercial readiness packaging
- Produce one vertical scenario pack (e.g. enterprise AI ops or regulated workflow).
- Acceptance: one 5-minute pitch deck + one pricing and deployment model draft.

4. Week 7-8: External validation and submission freeze
- Collect 2-3 letters of intent or pilot confirmations.
- Acceptance: submission bundle frozen with versioned evidence and reproducible commands.

## KPI Targets For Scoring

- Technical proof reproducibility: >= 95% successful reruns in clean environment.
- Verification latency budget: core verification flow <= 30 seconds for demo dataset.
- Security baseline: zero high-severity unresolved issues in submission branch.
- Adoption proof: keep public dogfooding list updated and timestamped.
- Judge clarity: one-page architecture + one-page business model + one-page traction proof.

## Risk Controls

- Scope risk: do not add new protocol surface without conformance tests.
- Demo risk: keep offline fallback artifacts in `release/submission`.
- CI risk: keep only stable required checks active on submission branch.

