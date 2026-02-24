<p align="center">
  <img src="docs/assets/aro-audit-logo.svg" alt="ARO Audit logo" width="460" />
</p>

# ARO Audit

一句话：`ARO Audit` 是一套让 AI 高风险动作“可留证、可追责、可复验”的开源方案。

## 这次整合后的项目范围

`aro-audit` 现在作为主仓库，和另外两个项目组成同一套治理闭环：

- `god-spear`（事前）：在 CI 阶段检查信任边界，边界没说清就不让发布。
- `safety-valve-spec`（事中）：关键动作必须带可验证收据，避免“做了但说不清”。
- `aro-audit`（事后）：把动作写成不可篡改证据链，支持独立重放验真。

这是产品层整合，不是把三个代码仓库强行混成一个仓库。这样做的好处是工程风险更低、迭代更快、对外叙事更清楚。

## 一页纸

- [ARO Audit 一页纸（CN）](docs/ONEPAGER_CN.md)

## 你能直接用它做什么

- 给关键动作生成标准化证据，而不只是普通日志。
- 在审计时快速发现“删改补写”。
- 对内给安全/合规复盘，对外给客户或监管做第三方可验证证明。

## 快速开始（30 秒）

```bash
bash quickstart/run.sh
```

看到以下结果就算成功：

- baseline 样本输出 `VERIFY_OK: full chain valid`
- 篡改样本会被拒绝（`Merkle mismatch` 或签名/摘要失败）

## 仓库入口

- 快速体验：[`quickstart/README.md`](quickstart/README.md)
- 协议规范：[`spec/AAR_v1.0.md`](spec/AAR_v1.0.md)
- 一致性向量：[`spec/test_vectors/README.md`](spec/test_vectors/README.md)
- SDK 与 CLI：[`sdk/`](sdk/)
- 高风险权限演示：[`demo/high_risk_authority/README.md`](demo/high_risk_authority/README.md)
- HICOOL 合并叙事：[`competition/hicool-2026/README.md`](competition/hicool-2026/README.md)

## 关联项目（已合并进方案）

- `safety-valve-spec`：https://github.com/joy7758/safety-valve-spec
- `god-spear`：https://github.com/joy7758/god-spear
- 三项目证据快照：[`competition/hicool-2026/EVIDENCE.md`](competition/hicool-2026/EVIDENCE.md)

## 当前凭证

- FDO Testbed ID：`21.T11966/aro-audit-profile-v1`
- DOI：`https://doi.org/10.5281/zenodo.18728568`
- 引用信息：[`CITATION.cff`](CITATION.cff)
- 安全策略：[`SECURITY.md`](SECURITY.md)
- 机器可读元数据：[`machine-readable/repository.json`](machine-readable/repository.json)

## 许可证

本项目采用 [`LICENSE`](LICENSE) 中定义的许可条款。
