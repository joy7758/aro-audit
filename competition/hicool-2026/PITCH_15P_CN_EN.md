# HICOOL 2026 Pitch Deck (15 Pages, CN/EN)

## Page 1. 项目封面 / Cover

CN:
- 项目名：AegisTrust（可验证AI动作治理栈）
- 主项目仓库：`aro-audit`
- 融合能力：`aro-audit` + `safety-valve-spec` + `god-spear`
- 参赛赛道：人工智能/软件和信息服务

EN:
- Project: AegisTrust (Verifiable AI Action Governance Stack)
- Primary repo: `aro-audit`
- Unified stack: `aro-audit` + `safety-valve-spec` + `god-spear`
- Track: AI / Software & Information Services

---

## Page 2. 行业痛点 / Problem

CN:
- AI Agent进入生产后，企业常见三类风险：越权执行、证据不可采信、事故追责困难。
- 传统日志无法提供独立第三方可重复验证的证据链。
- 企业与监管都需要“事前门禁 + 事中控制 + 事后审计”的闭环。

EN:
- Production AI agents face three core risks: over-privileged actions, non-verifiable logs, and weak accountability.
- Traditional logs are not independently reproducible evidence.
- Enterprises and regulators require a full loop: pre-check, in-action control, and post-action audit.

---

## Page 3. 解决方案 / Solution

CN:
- 我们提供统一治理栈：
1. `god-spear`：CI阶段强制信任边界声明。
2. `safety-valve-spec`：动作边界必须具备可验收据。
3. `aro-audit`：事后回放与独立验签审计。
- 结果是“可阻断、可证明、可复核”的AI动作治理闭环。

EN:
- We provide a unified governance stack:
1. `god-spear`: trust-boundary enforcement in CI.
2. `safety-valve-spec`: verifiable receipts at action boundaries.
3. `aro-audit`: replay verification and independent auditing.
- Outcome: blockable, provable, and reproducible AI action governance.

---

## Page 4. 技术架构 / Architecture

CN:
- Layer A（Build-time）：检查配置是否定义 crossing、failure signal、revocation pathway。
- Layer B（Action-time）：ALLOW/DENY/DEGRADE 收据签名与一致性测试。
- Layer C（Post-action）：JSONL链路、checkpoint、Merkle一致性和签名验证。
- 三层均可独立部署，也可组合部署。

EN:
- Layer A (Build-time): validates crossing, failure signal, and revocation pathway.
- Layer B (Action-time): signed ALLOW/DENY/DEGRADE receipts with conformance checks.
- Layer C (Post-action): JSONL chain, checkpoints, Merkle consistency, and signature verification.
- Layers can run independently or as one integrated pipeline.

---

## Page 5. 核心创新 / Core Innovation

CN:
- 创新1：把“日志”升级为“可验证证据对象”。
- 创新2：把“安全规则”前移到CI，降低上线后风险暴露。
- 创新3：通过标准化收据和一致性测试，让不同系统具备互验证能力。
- 创新4：一条命令可独立复核，降低审计和风控使用门槛。

EN:
- Innovation 1: upgrade logs into verifiable evidence objects.
- Innovation 2: shift security controls left into CI.
- Innovation 3: standardize receipts and conformance for cross-system verification.
- Innovation 4: one-command independent verification for lower audit friction.

---

## Page 6. 可验证证据 / Verifiable Evidence

CN:
- 当前已形成可展示证据：
1. 三个核心仓库均有公开代码与文档。
2. `spear-check` 已在 18 个仓库接入并运行成功。
3. 提供一键生成的证据快照文件：`competition/hicool-2026/EVIDENCE.md`。
- 评委可直接复核，不依赖口头陈述。

EN:
- Public, verifiable proof already exists:
1. All three core repos are public with docs.
2. `spear-check` is adopted across 18 repos with successful runs.
3. A reproducible evidence snapshot is generated at `competition/hicool-2026/EVIDENCE.md`.
- Judges can verify directly, not rely on claims.

---

## Page 7. 演示流程 / Demo Flow

CN:
1. 运行 `god-spear` 校验规则完整性。
2. 运行 `safety-valve-spec` 一致性流程，生成合规结果。
3. 运行 `aro-audit` 生成审计包并执行独立验签。
4. 展示篡改后验证失败，证明“可检测、可阻断”。

EN:
1. Run `god-spear` to validate trust boundaries.
2. Run `safety-valve-spec` conformance flow.
3. Run `aro-audit` to generate an audit pack and verify independently.
4. Show tamper case failure to prove enforceability.

---

## Page 8. 商业场景 / Commercial Scenarios

CN:
- 场景1：企业内部AI助手（IT、法务、财务）高权限动作审计。
- 场景2：平台型AI产品向B端交付“可验收据”作为信任凭据。
- 场景3：审计机构、保险风控对AI动作进行抽样复核与评级。

EN:
- Scenario 1: internal enterprise AI assistants with privileged action auditing.
- Scenario 2: B2B AI platforms delivering verifiable receipts as trust artifacts.
- Scenario 3: audit and insurance workflows for sampling and risk grading.

---

## Page 9. 商业模式 / Business Model

CN:
- 开源底座：协议、校验器、基础工具。
- 商业化层：
1. 企业版策略包（行业模板、风险规则）。
2. 托管验证服务（报告、审计接口、证据归档）。
3. 认证与实施服务（部署、培训、合规咨询）。

EN:
- Open layer: protocol, verifier, and base tools.
- Monetization layer:
1. enterprise policy packs,
2. managed verification/reporting services,
3. certification and implementation services.

---

## Page 10. 竞争格局 / Competition

CN:
- 传统日志平台：可观测但不可强证明。
- 单点安全工具：覆盖局部，不形成闭环。
- 我们的优势：从CI到动作边界再到审计复核，全流程可验证。

EN:
- Traditional logging tools are observable but weak on cryptographic proof.
- Point security tools cover fragments only.
- Our advantage is end-to-end verifiability from CI to boundary to audit replay.

---

## Page 11. 里程碑与进展 / Milestones

CN:
- 已完成：
1. 统一技术叙事与证据页。
2. 多仓库接入与CI运行验证。
3. 一键生成比赛证据快照脚本。
- 下一阶段（8周）：
1. 行业样板场景打磨。
2. 外部试点与意向书收集。
3. 提交版材料冻结。

EN:
- Done:
1. unified stack narrative and evidence page,
2. multi-repo CI adoption verification,
3. one-command evidence generator.
- Next 8 weeks:
1. vertical demo hardening,
2. pilot/LOI collection,
3. submission freeze.

---

## Page 12. 北京落地计划 / Beijing Plan

CN:
- 在北京构建“AI动作治理标准样板间”：
1. 联合高校/研究机构做标准验证。
2. 对接产业园区和企业试点。
3. 输出培训与认证体系。
- 目标：形成可复制的本地化服务能力。

EN:
- Build a Beijing-based reference center for AI action governance:
1. joint validation with academic/research partners,
2. enterprise pilots in local ecosystem,
3. training and certification outputs.
- Goal: scalable local delivery capability.

---

## Page 13. 团队与分工 / Team

CN:
- 核心能力：协议设计、工程实现、验证工具链、开源运营。
- 顾问方向（可补强）：企业内控、审计合规、保险风控、ToB销售。
- 组织原则：技术迭代与商业验证并行。

EN:
- Core capability: protocol design, implementation, verification tooling, open-source operations.
- Advisor reinforcement: internal control, audit compliance, insurance risk, B2B sales.
- Operating principle: parallel technical and commercial execution.

---

## Page 14. 融资与资源诉求 / Ask

CN:
- 资金用途：
1. 核心研发与测试基础设施。
2. 行业试点实施和客户成功。
3. 合规认证和生态合作。
- 资源诉求：北京试点场景、产业导师、机构共建机会。

EN:
- Use of funds:
1. core R&D and testing infrastructure,
2. pilot delivery and customer success,
3. compliance and ecosystem partnerships.
- Resource ask: pilot opportunities in Beijing, mentors, and institutional co-build channels.

---

## Page 15. 结语 / Closing

CN:
- AegisTrust不是“再做一个Agent工具”，而是为AI时代建立可验证、可追责、可落地的治理基础设施。
- 我们已具备可公开复核的工程证据，下一步是规模化落地。

EN:
- AegisTrust is not another agent utility; it is verifiable governance infrastructure for the AI era.
- We already have reproducible engineering proof and are ready for scaled deployment.

---

## Appendix: Demo Commands

```bash
# 1) Refresh unified evidence snapshot
bash tools/build_hicool_evidence.sh /Users/zhangbin/GitHub

# 2) ARO quick verification demo
cd /Users/zhangbin/GitHub/aro-audit
bash quickstart/run.sh

# 3) SVS conformance demo
cd /Users/zhangbin/GitHub/safety-valve-spec
bash conformance/run.sh

# 4) Spear local rule check
cd /Users/zhangbin/GitHub/god-spear
npx -y --package god-spear@0.2.0 spear check .github/security/.spear-rules.json
```

