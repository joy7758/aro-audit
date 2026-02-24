# HICOOL 2026 Unified Entry

## Positioning

This entry uses `aro-audit` as the primary product shell and merges two sibling projects into one verifiable solution narrative:

- Runtime evidence layer: `aro-audit`
- Action-boundary conformance layer: `safety-valve-spec`
- CI trust-boundary gate: `god-spear`

This is a product-level merge, not a forced codebase merge. It keeps engineering risk low while increasing competition readiness.

## Why This Merge Improves Ranking Odds

- Clear system story: prevention + detection + verification + governance in one stack.
- Stronger defensibility: protocol spec, conformance tests, and CI enforcement are all visible.
- Better judge readability: one main project, one architecture, one evidence page.
- Better commercialization path: enterprise integration can start from CI gate, then move to runtime audit and policy receipts.

## Unified Architecture

1. Build-time trust gate (`god-spear`)
- Blocks CI if trust crossings are not explicitly defined.

2. Action-time policy gate (`safety-valve-spec`)
- Requires verifiable action receipts at boundary crossings.

3. Post-action evidence and replay verification (`aro-audit`)
- Generates append-only journal + manifest + independent verification flow.

## Competition Materials In This Folder

- `README.md`: unified entry narrative
- `MATURITY_PLAN.md`: execution milestones to improve scoring odds
- `EVIDENCE.md`: generated proof snapshot from local repos

## Regenerate Evidence

```bash
bash tools/build_hicool_evidence.sh /Users/zhangbin/GitHub
```

## Recommended Submission Name

`AegisTrust: Verifiable AI Action Governance Stack`

