# AAR/ALC 审计与保险 5 分钟路演稿（8–10 页）

> 目标受众：审计机构 / 保险公司风控 / 企业内控负责人  
> 目的：让对方用“风险与责任”的语言理解 AAR/ALC，并认可其作为证据底座的价值。

---

## Slide 1：一句话定位
**AAR/ALC 是 AI 代理时代的“黑匣子 + 责任链”基础设施。**  
- 不是更聪明的 Agent  
- 是让 Agent **可追责、可审计、可独立复核** 的证据底座

---

## Slide 2：痛点（审计/保险视角）
当前 Agent 在生产环境的三大不可控：
1) **越权**（权限碎片化 + Prompt 注入）
2) **不可追溯**（出了事只能看零散日志）
3) **不可采信**（日志可改、难复核、难抽查）

结论：这会直接变成 **董事会级风险** 与 **保险赔付风险**。

---

## Slide 3：我们把“日志”升级成“可核验陈述”
AAR v1.0：每个 action 生成一条 **可核验陈述（Verifiable Statement）**
- No-Plaintext：不存敏感原文，只存 hash + 受控 locator
- JCS + sha256：跨语言可复现的 digest
- prev_digest：形成时间之箭（责任链）

一句话：**不是“我说我做了”，而是“你能独立验证我确实这样做了”。**

---

## Slide 4：WORM 语义（为什么它像“黑匣子磁带”）
事实源 = JSONL append-only journal（可重复运行但可验证）
- 每条 statement 都可独立重算 digest
- 每 N 条写入 checkpoint（range + merkle_root）
- checkpoint 绑定 store_fingerprint（文件指纹）

审计含义：**删一条/改一条，会导致链与封签失效。**

---

## Slide 5：责任归属（为什么能“追责”）
checkpoint_sig 使用 ORG sub-key（Level-1）签名：
- 证明：该组织对这段行为链负责
- 可把责任精确落到：组织/部门/工作负载域（后续可扩展）

审计含义：**责任归属不是口头声明，而是加密绑定。**

---

## Slide 6：第三方独立复核（审计最关心的“可复现”）
我们交付的是一个审计包（audit_packet.zip）：
- journal.jsonl（事实源）
- AAR-Manifest.json（摘要 + 复核入口）
- verify.sh（1 条命令独立复核）

复核命令示例：
`python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_subkey_ed25519.pem`

审计含义：**你不需要信我，你只需要跑验证。**

---

## Slide 7：保险视角的价值（可量化的“保费因子”）
AAR/ALC 提供三类可量化指标：
1) 证据强度（L0–L3，v1.0 已实现 L1）
2) 行为风险特征（高危工具调用、回滚不可用、频率异常）
3) 抽查成本下降（Merkle Root 支持抽样验证）

结果：可以把“代理风险”纳入保费定价与免赔条款。

---

## Slide 8：部署形态（低摩擦）
Phase 1（开发者入口）：`aro` CLI
- gen-demo / verify / export

Phase 2（企业落地）：MCP Wrapper 插桩
- tool 调用返回必须携带 AAR 指针
- 企业网关可强制校验“无 AAR 不接入”

---

## Slide 9：商业模式（收税点）
开源层（扩散）：schema + journal + verify（基础闭环免费）
收费层（溢价）：
1) Policy Packs（行业策略包订阅：金融/政务/建筑安全）
2) 认证服务（proof-as-a-service：审计认可等级）
3) 证据网络效应（与保险/审计合作形成默认格式）

---

## Slide 10：下一步请求（对方该做什么）
对审计机构：
- 选 1 个场景做试点：抽样验证 + 内控报告导出

对保险公司：
- 共同定义“代理风险条款”与“证据等级要求”
- 把 AAR/ALC 纳入承保前置条件

