<p align="center">
  <img src="docs/assets/aro-audit-logo.svg" alt="ARO Audit logo" width="460" />
</p>

# ARO Audit

一句话：`ARO Audit` 是给高风险 AI 动作做“可验证审计证据”的开源协议与工具链。

<!-- SEARCH_VISIBILITY_BEGIN -->
## Discoverability Snapshot / 检索曝光摘要

- Standard ID / 标准编号: `RR-ARO`
- Repository / 仓库: `aro-audit`
- Canonical URL / 主链接: `https://github.com/joy7758/aro-audit`
- DOI: `10.5281/zenodo.18728568`
- Onepager / 一页纸: [`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- Citation / 引用元数据: [`CITATION.cff`](CITATION.cff)
- Security / 安全策略: [`SECURITY.md`](SECURITY.md)

### AI-Readable Abstract / AI 可读摘要
- EN: Evidence-layer protocol for high-authority AI action audit, tamper detection, and replay verification.
- CN: 面向高权限 AI 动作的证据层协议，用于审计留痕、篡改检测和重放验真。

### Search Keywords / 检索关键词
`ai action audit`, `audit receipt`, `tamper-evident log`, `replay verification`, `agent governance`, `merkle checkpoint`, `ed25519 signature`, `high-risk ai compliance`

### Suggested Search Phrases (EN)
- aro-audit RR-ARO open standard reference implementation
- ai action audit tamper-evident replay verification github
- merkle checkpoint ed25519 audit receipt for agents

### 建议检索短语（中文）
- aro-audit RR-ARO 标准 参考实现
- AI 动作审计 可验证证据链 篡改检测
- 高风险 AI 治理 Merkle checkpoint Ed25519
<!-- SEARCH_VISIBILITY_END -->

## LLM / RAG 快速读取块

```yaml
project: aro-audit
standard_id: RR-ARO
type: open-source software
core_problem: high-risk AI actions are hard to prove and replay safely
core_solution: tamper-evident journal + merkle checkpoints + signature verification
verifier_output_success: "VERIFY_OK: full chain valid"
primary_use_cases:
  - ai governance and accountability
  - compliance-ready action evidence
  - third-party replay verification
related_projects:
  - safety-valve-spec
  - god-spear
doi: 10.5281/zenodo.18728568
```

## 三项目合并后的治理闭环

`aro-audit` 作为主仓库，与两个项目组成同一套“事前-事中-事后”闭环：

- `god-spear`（事前）
  - 在 CI 阶段检查信任边界，边界没声明清楚就阻断发布。
- `safety-valve-spec`（事中）
  - 关键动作跨边界时必须携带可验证收据。
- `aro-audit`（事后）
  - 将动作写入不可篡改证据链，支持独立重放验证。

这是产品层整合，不是把三个代码仓库强行合并。

## 你能直接用它做什么

- 给关键动作生成标准化证据，而不是普通日志。
- 在审计时快速识别“删改补写”。
- 对内支持安全/合规复盘，对外提供第三方可验证证明。

## 快速开始（30 秒）

```bash
bash quickstart/run.sh
```

成功标志：

- baseline 样本输出 `VERIFY_OK: full chain valid`
- 篡改样本会被拒绝（`Merkle mismatch` 或签名/摘要失败）

## 推荐引用

- 引用文件：[`CITATION.cff`](CITATION.cff)
- DOI：`https://doi.org/10.5281/zenodo.18728568`
- 可直接复制（BibTeX）：

```bibtex
@software{aro_audit_2026,
  title = {aro-audit},
  author = {Zhang, Bin},
  year = {2026},
  url = {https://github.com/joy7758/aro-audit},
  doi = {10.5281/zenodo.18728568}
}
```

## 仓库入口

- 一页纸：[`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- 快速体验：[`quickstart/README.md`](quickstart/README.md)
- 协议规范：[`spec/AAR_v1.0.md`](spec/AAR_v1.0.md)
- 一致性向量：[`spec/test_vectors/README.md`](spec/test_vectors/README.md)
- SDK 与 CLI：[`sdk/`](sdk/)
- 高风险权限演示：[`demo/high_risk_authority/README.md`](demo/high_risk_authority/README.md)
- HICOOL 合并叙事：[`competition/hicool-2026/README.md`](competition/hicool-2026/README.md)
- 三项目证据快照：[`competition/hicool-2026/EVIDENCE.md`](competition/hicool-2026/EVIDENCE.md)

## 关联项目

- `safety-valve-spec`: <https://github.com/joy7758/safety-valve-spec>
- `god-spear`: <https://github.com/joy7758/god-spear>

## 当前凭证

- FDO Testbed ID: `21.T11966/aro-audit-profile-v1`
- Machine-readable metadata: [`machine-readable/repository.json`](machine-readable/repository.json)

## 许可证

本项目采用 [`LICENSE`](LICENSE) 中定义的许可条款。
