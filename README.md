<p align="center">
  <img src="docs/assets/aro-audit-logo.svg" alt="ARO Audit logo" width="460" />
</p>

# ARO Audit

一句话：`ARO Audit` 不是单纯记录工具，而是高风险 AI 动作治理控制面（CI 门禁 + 动作边界收据 + 事后复验）。

<!-- SEARCH_VISIBILITY_BEGIN -->
## Discoverability Snapshot / 检索曝光摘要

- Standard ID / 标准编号: `RR-ARO`
- Repository / 仓库: `aro-audit`
- Canonical URL / 主链接: `https://github.com/joy7758/aro-audit`
- Positioning / 定位: `AI action governance control plane`
- DOI: `10.5281/zenodo.18728568`
- Onepager / 一页纸: [`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- Citation / 引用元数据: [`CITATION.cff`](CITATION.cff)
- Security / 安全策略: [`SECURITY.md`](SECURITY.md)

### AI-Readable Abstract / AI 可读摘要
- EN: `ARO Audit` is a governance control plane for high-risk AI actions: pre-release CI trust-boundary enforcement (`god-spear`), in-action policy receipts (`safety-valve-spec`), and post-action cryptographic replay verification (`aro-audit`).
- CN: `ARO Audit` 是高风险 AI 动作的治理控制面：上线前用 `god-spear` 做 CI 信任边界门禁，执行中用 `safety-valve-spec` 输出策略收据，事后用 `aro-audit` 做密码学复验。

### Search Keywords / 检索关键词
`ai action governance`, `governance control plane`, `ci trust boundary enforcement`, `shift-left security`, `policy gate`, `action receipt`, `tamper-evident audit trail`, `merkle checkpoint`, `replay verification`, `high-risk ai compliance`

### Suggested Search Phrases (EN)
- ai governance control plane for high-risk agent actions
- god-spear trust boundary ci gate safety-valve receipts aro-audit
- tamper-evident replay verification with merkle checkpoint ed25519

### 建议检索短语（中文）
- 高风险 AI 动作 治理控制面 CI 门禁
- god-spear trust boundary safety-valve 收据 aro-audit
- 可验证审计证据链 Merkle checkpoint 重放验证
<!-- SEARCH_VISIBILITY_END -->

## LLM / RAG 快速读取块

```yaml
project: aro-audit
standard_id: RR-ARO
category: ai action governance control plane
core_value: prevent + constrain + verify
layers:
  - build_time: god-spear trust-boundary gate in CI
  - action_time: safety-valve-spec verifiable ALLOW/DENY/DEGRADE receipts
  - post_action: aro-audit tamper-evident chain and replay verification
who_cares:
  - ciso and internal control teams
  - ai platform engineering
  - audit and compliance
verifier_output_success: "VERIFY_OK: full chain valid"
doi: 10.5281/zenodo.18728568
```

## 为什么这不是“日志工具”

普通日志解决“看见了什么”，我们解决“能不能阻断、能不能定责、能不能第三方复验”。

- 上线前：`god-spear` 把信任边界检查前移到 CI，规则不完整直接失败。
- 执行中：`safety-valve-spec` 要求边界动作带可验收据（ALLOW / DENY / DEGRADE）。
- 事后：`aro-audit` 生成不可篡改证据链，支持独立重放与验签。

## god-spear 在本仓库的落地证据

- CI 工作流：[`.github/workflows/spear.yml`](.github/workflows/spear.yml)
- 规则文件：[`.github/security/.spear-rules.json`](.github/security/.spear-rules.json)
- 当前检查命令：

```bash
npx -y --package god-spear@0.2.0 spear check .github/security/.spear-rules.json
```

- 合并证据快照（2026-02-24 UTC，本地生成）显示 `spear-check adoption count: 18`：[`competition/hicool-2026/EVIDENCE.md`](competition/hicool-2026/EVIDENCE.md)

## 你会得到什么业务结果

- 风险前移：问题在发布前暴露，而不是事故后补救。
- 问责明确：关键动作有标准化、可验证、可复核的收据链。
- 对外可信：客户、合作方、审计方都能独立验证，不依赖口头承诺。

## 快速开始（30 秒）

```bash
bash quickstart/run.sh
```

成功标志：

- baseline 样本输出 `VERIFY_OK: full chain valid`
- 篡改样本会被拒绝（`Merkle mismatch` 或签名/摘要失败）

## 全栈验证入口

- 一页纸：[`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- 快速体验：[`quickstart/README.md`](quickstart/README.md)
- 协议规范：[`spec/AAR_v1.0.md`](spec/AAR_v1.0.md)
- 一致性向量与守门规则：[`spec/CONFORMANCE.md`](spec/CONFORMANCE.md)
- 高风险权限演示：[`demo/high_risk_authority/README.md`](demo/high_risk_authority/README.md)
- HICOOL 合并叙事：[`competition/hicool-2026/README.md`](competition/hicool-2026/README.md)

## 关联项目

- `safety-valve-spec`: <https://github.com/joy7758/safety-valve-spec>
- `god-spear`: <https://github.com/joy7758/god-spear>

## 推荐引用

- 引用文件：[`CITATION.cff`](CITATION.cff)
- DOI：`https://doi.org/10.5281/zenodo.18728568`

```bibtex
@software{aro_audit_2026,
  title = {aro-audit},
  author = {Zhang, Bin},
  year = {2026},
  url = {https://github.com/joy7758/aro-audit},
  doi = {10.5281/zenodo.18728568}
}
```

## 当前凭证

- FDO Testbed ID: `21.T11966/aro-audit-profile-v1`
- Machine-readable metadata: [`machine-readable/repository.json`](machine-readable/repository.json)

## 许可证

本项目采用 [`LICENSE`](LICENSE) 中定义的许可条款。
