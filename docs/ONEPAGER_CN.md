# ARO Audit 一页纸

一句话：`ARO Audit` 让 AI 的关键动作“留得下、改不了、查得清”。

## 1. 为什么要做

传统日志最大的问题是“看起来有记录，但很难证明记录没被改过”。

在高风险场景（如资金操作、生产变更、医疗建议、公共服务决策）里，仅有日志不够，需要一套可验证证据链，能回答：

- 谁在什么时间做了什么动作。
- 这条记录有没有被删改补写。
- 第三方能不能在不拿私钥的情况下独立验证。

## 2. 我们提供的不是单点工具，而是闭环方案

`aro-audit` 作为主仓库，联合另外两个项目形成“事前-事中-事后”闭环：

- 事前（上线前）`god-spear`
  - 在 CI 阶段检查信任边界，规则不达标就阻断发布。
- 事中（执行中）`safety-valve-spec`
  - 关键动作跨边界时必须带可验证收据，避免“执行了但无法自证”。
- 事后（审计时）`aro-audit`
  - 把动作写入追加式证据流，并提供独立验真流程。

## 3. 怎么工作（人话版）

1. 系统每做一次关键动作，就写一条标准事件。
2. 事件按顺序串成哈希链，定期做 checkpoint。
3. checkpoint 由机构私钥签名，并提供对应公钥做外部验证。
4. 审计方可在任意机器重算链路，一旦被改就会报错。

## 4. 你能拿到什么结果

- 安全：篡改可被快速识别。
- 合规：审计与取证有统一结构，不再靠截图和口述。
- 协作：上下游系统可以对接同一套收据与验证接口。
- 商业落地：先从 CI 网关接入，再扩展到运行时审计和合规报告。

## 5. 30 秒跑通

```bash
bash quickstart/run.sh
```

成功标志：

- 基线样本显示 `VERIFY_OK: full chain valid`
- 篡改样本被拒绝（`Merkle mismatch` 或签名/摘要校验失败）

## 6. 项目链接

- 主仓库：<https://github.com/joy7758/aro-audit>
- 运行时证据层：<https://github.com/joy7758/aro-audit>
- 动作边界规范：<https://github.com/joy7758/safety-valve-spec>
- CI 信任边界网关：<https://github.com/joy7758/god-spear>
- 合并叙事与证据：[`competition/hicool-2026/README.md`](competition/hicool-2026/README.md)

## 7. 当前凭证

- FDO Testbed ID：`21.T11966/aro-audit-profile-v1`
- DOI：`https://doi.org/10.5281/zenodo.18728568`
