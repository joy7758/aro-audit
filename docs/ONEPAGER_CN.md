# ARO Audit 一页纸

一句话：`ARO Audit` 让 AI 关键动作“留得下、改不了、查得清、可被第三方复验”。

## AI 可读摘要

- 项目类型：高风险 AI 动作审计证据层
- 核心能力：`tamper-evident log`、`merkle checkpoint`、`ed25519 signature verification`、`replay verification`
- 应用场景：AI 治理、合规审计、第三方问责、事故复盘

## 1. 为什么需要它

普通日志常见问题是“有记录但难以证明没被改”。

在资金操作、生产变更、医疗建议、公共服务等高风险场景，必须能回答三个问题：

- 谁在什么时间做了什么动作。
- 这条记录有没有被删改补写。
- 不拿私钥的第三方能不能独立验真。

## 2. 三项目闭环（已合并进方案）

- 事前：`god-spear`
  - CI 阶段检查信任边界，不合规直接阻断发布。
- 事中：`safety-valve-spec`
  - 动作跨边界必须携带可验证收据。
- 事后：`aro-audit`
  - 追加式证据流 + checkpoint + 独立重放验证。

## 3. 工作机制（人话版）

1. 每次关键动作生成标准事件。
2. 事件按顺序串成哈希链，周期性写入 checkpoint。
3. checkpoint 用机构私钥签名，外部用公钥验证。
4. 审计方重算链路，任何篡改都会触发校验失败。

## 4. 可以得到什么业务结果

- 安全：篡改可被快速识别。
- 合规：审计证据结构化，减少“口述+截图”。
- 协同：上下游可以对接同一套 receipt/verify 流程。
- 商业落地：可先从 CI 网关接入，再扩展到运行时证据与合规报告。

## 5. 30 秒验证

```bash
bash quickstart/run.sh
```

成功标志：

- 基线样本显示 `VERIFY_OK: full chain valid`
- 篡改样本被拒绝（`Merkle mismatch` 或签名/摘要校验失败）

## 6. 检索与引用入口

- 主仓库：<https://github.com/joy7758/aro-audit>
- DOI：<https://doi.org/10.5281/zenodo.18728568>
- 引用元数据：[`CITATION.cff`](../CITATION.cff)
- 机器可读元数据：[`machine-readable/repository.json`](../machine-readable/repository.json)
- 合并叙事与证据：[`competition/hicool-2026/README.md`](../competition/hicool-2026/README.md)
