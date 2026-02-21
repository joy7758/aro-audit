### Proposal: Integrate AAR-MCP-2.0 RC1 (Verifiable Agent Interaction Layer)

I’m publishing **AAR-MCP-2.0 Core Spec (RC1)**: a verifiable interaction layer for MCP/agent tool calls.
It provides **tamper-evident journals + checkpoint signatures + conformance vectors**, and exports an **audit bundle** reviewers can independently verify.

**Why this matters**
- Observability logs are not evidence. We need **non-repudiable action receipts** for high-risk tools (write config, transfer funds, etc.).
- This RC1 focuses on **fail-closed enforcement** and **format-stable verification**, not vendor lock-in.

**RC1 entry (spec bundle + sha256 + conformance gate)**
- Repo: joy7758/aro-audit
- RC1 Review入口已在 README 顶部（含 spec bundle + sha256）
- Conformance Gate: boundary vectors (base OK / attestations-only OK / predicate-tamper FAIL)

**Review workflow**
- Please review via GitHub Discussions:
  - Review Thread #3: https://github.com/joy7758/aro-audit/discussions/3
  - Review Thread #4: https://github.com/joy7758/aro-audit/discussions/4
- Or open an issue using our RC1 review template.

**Ask**
- I’d like feedback on:
  1) Record types + digest boundary definition
  2) Checkpoint semantics (range, merkle root, signature)
  3) Tool-level dependency policy (soft/strict/hard-gate)
  4) Conformance vectors coverage (what’s missing)

If your project exposes MCP tools, I can provide a minimal wrapper and a 30s demo bundle to validate integration.
