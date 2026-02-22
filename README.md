# ARO Audit Profile

<!-- SEARCH_VISIBILITY_BEGIN -->
## Discoverability Snapshot / 检索曝光摘要

- Standard ID / 标准编号: `RR-ARO`
- Repository / 仓库名: `aro-audit`
- A/B Recommended Variant / 推荐版本: `A`

### EN Summary / 英文摘要
Evidence-layer protocol for high-authority AI action audit and replay verification.

### CN Summary / 中文摘要
用于高权限AI动作审计与重放验证的证据层协议。

### SEO Keywords / 检索关键词
`audit-receipt`, `ai-governance`, `evidence-layer`, `merkle`, `verification`

### Suggested Search Phrases (EN)
- aro-audit RR-ARO open standard
- aro-audit audit-receipt ai-governance github
- RR-ARO audit-receipt reference implementation

### 建议检索短语（中文）
- aro-audit RR-ARO 标准 规范
- aro-audit audit-receipt ai-governance 仓库
- RR-ARO 参考实现 红岩 宪章

### A/B Hero Variants / 首屏 A/B 版本
- Variant A (Citation-First) / 引用优先: [`docs/readme-ab/README_HERO_A_CN_EN.md`](docs/readme-ab/README_HERO_A_CN_EN.md)
- Variant B (Adoption-First) / 落地优先: [`docs/readme-ab/README_HERO_B_CN_EN.md`](docs/readme-ab/README_HERO_B_CN_EN.md)
- Experiment Window / 观测窗口: 14 days

### Quick Links / 快速入口
- Governance Hub / 总入口: https://github.com/joy7758/RedRock-Constitution
- Standards Registry / 标准注册表: https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-aro
- Repos Index / 仓库索引: https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/REPOS_INDEX_CN_EN.md
- Ecosystem Graph / 生态关系图: https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/ECOSYSTEM_GRAPH_CN_EN.md
- Onepager / 一页纸: (pending)
- Citation / 引用元数据: `CITATION.cff`
- Security Policy / 安全策略: `SECURITY.md`
- Machine-readable / 机器可读: `machine-readable/repository.json`
<!-- SEARCH_VISIBILITY_END -->

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

<!-- ECOSYSTEM_LINKS_BEGIN -->
## Ecosystem Links / 生态关系链接

![quality-baseline](https://github.com/joy7758/aro-audit/actions/workflows/quality-baseline.yml/badge.svg)

### CN
- 总入口（宪章）：[RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)
- 标准注册表：[STANDARDS_REGISTRY](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-aro)
- 仓库总索引：[REPOS_INDEX_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/REPOS_INDEX_CN_EN.md)
- 全局生态图：[ECOSYSTEM_GRAPH_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/ECOSYSTEM_GRAPH_CN_EN.md)
- 机器可读元数据：[`machine-readable/repository.json`](machine-readable/repository.json)

### EN
- Governance hub: [RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)
- Standards registry: [STANDARDS_REGISTRY](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-aro)
- Repositories index: [REPOS_INDEX_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/REPOS_INDEX_CN_EN.md)
- Global ecosystem graph: [ECOSYSTEM_GRAPH_CN_EN](https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/ECOSYSTEM_GRAPH_CN_EN.md)
- Machine-readable metadata: [`machine-readable/repository.json`](machine-readable/repository.json)

### Related Repositories / 关联仓库
- [AASP-Core](https://github.com/joy7758/AASP-Core)
- [pFDO-Specification](https://github.com/joy7758/pFDO-Specification)
- [safety-valve-spec](https://github.com/joy7758/safety-valve-spec)
- [RedRock-Constitution](https://github.com/joy7758/RedRock-Constitution)

### Search Keywords / 检索关键词
`audit-receipt`, `ai-governance`, `evidence-layer`, `merkle`, `verification`

### Bilingual Project Abstract / 双语项目摘要
- EN: Evidence-layer protocol for high-authority AI action audit and replay verification.
- CN: 用于高权限AI动作审计与重放验证的证据层协议。
<!-- ECOSYSTEM_LINKS_END -->
