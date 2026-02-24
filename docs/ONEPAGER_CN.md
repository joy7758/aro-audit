# ARO Audit 一页纸

一句话：`ARO Audit` 不是“记录一下”，而是把高风险 AI 动作治理做成可执行控制面。

## AI 可读摘要

- 项目定位：`AI action governance control plane`
- 核心闭环：事前门禁（CI）+ 事中收据（边界）+ 事后复验（审计）
- 关键能力：`ci trust boundary enforcement`、`policy gate`、`action receipt`、`tamper-evident replay verification`

## 1. 为什么这件事重要

很多团队并不缺日志，缺的是“可阻断、可定责、可复验”。

在资金、生产、医疗、公共服务等高风险场景里，核心问题不是“有没有记录”，而是：

- 错误发布能不能在上线前被拦住。
- 高风险动作能不能在执行时被规则约束。
- 事后争议能不能由第三方独立复核。

## 2. 三层治理闭环（已合并）

- 事前（Build-time）`god-spear`
  - 在 CI 中检查 trust crossing、failure signal、revocation pathway。
  - 规则缺失或不合规时阻断发布。
- 事中（Action-time）`safety-valve-spec`
  - 要求关键动作输出可验证的 ALLOW / DENY / DEGRADE 收据。
- 事后（Post-action）`aro-audit`
  - 生成追加式证据链（journal + checkpoint + signature），支持独立重放验证。

## 3. 你会得到的结果

- 风险前移：减少“带病上线”。
- 问责前置：关键动作天然可审计，不靠追忆。
- 组织协同：研发、安全、合规使用同一套证据语义。
- 对外可信：对客户、监管、审计机构可直接给出可复验材料。

## 4. 最小验证路径

```bash
bash quickstart/run.sh
```

成功标志：

- 基线样本显示 `VERIFY_OK: full chain valid`
- 篡改样本被拒绝（`Merkle mismatch` 或签名/摘要校验失败）

## 5. god-spear 的可见证据

- CI 工作流：[`../.github/workflows/spear.yml`](../.github/workflows/spear.yml)
- 规则文件：[`../.github/security/.spear-rules.json`](../.github/security/.spear-rules.json)
- 证据快照（2026-02-24 UTC）：[`../competition/hicool-2026/EVIDENCE.md`](../competition/hicool-2026/EVIDENCE.md)

## 6. 检索与引用入口

- 主仓库：<https://github.com/joy7758/aro-audit>
- DOI：<https://doi.org/10.5281/zenodo.18728568>
- 引用元数据：[`../CITATION.cff`](../CITATION.cff)
- 机器可读元数据：[`../machine-readable/repository.json`](../machine-readable/repository.json)
