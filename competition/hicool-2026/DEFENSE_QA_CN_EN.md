# HICOOL 2026 Defense Q&A (CN/EN)

## Q1. 你们和普通日志系统有什么本质区别？

CN:
- 普通日志重“记录”，我们重“可验证证据”。
- 我们支持独立第三方重放验证，不依赖系统原作者口径。

EN:
- Traditional logging focuses on recording; we focus on verifiable evidence.
- Our outputs can be independently replay-verified by third parties.

## Q2. 为什么要做三层，而不是一个工具？

CN:
- 单工具无法覆盖“上线前、执行中、事故后”全链路风险。
- 三层分别解决预防、约束、追责问题，组合后形成治理闭环。

EN:
- One tool cannot fully cover pre-release, in-action, and post-incident risks.
- Three layers handle prevention, boundary enforcement, and accountability.

## Q3. 你们的技术壁垒是什么？

CN:
- 协议+一致性测试+验证工具链共同构成壁垒，不是单点脚本。
- 难点在跨系统可验证性与工程化落地，不是“做个规则文件”。

EN:
- The moat is protocol + conformance + verifier tooling, not a single script.
- The hard part is cross-system verifiability with operational reliability.

## Q4. 为什么评委可以相信你们不是“自说自话”？

CN:
- 我们提供公开仓库、可执行命令和可重复证据页。
- 评委可以按文档独立复核，不需要依赖团队解释。

EN:
- We provide public repos, executable commands, and reproducible evidence snapshots.
- Judges can independently verify claims without relying on our narrative.

## Q5. 商业化路径是什么？

CN:
- 第一阶段：开源扩散，建立事实标准入口。
- 第二阶段：企业策略包与托管验证服务收费。
- 第三阶段：认证、培训、实施服务形成复购与网络效应。

EN:
- Phase 1: open adoption and standard entry.
- Phase 2: monetization via policy packs and managed verification services.
- Phase 3: certification/training/implementation recurring revenue.

## Q6. 你们最先切入的客户是谁？

CN:
- 首批客户优先是“高权限AI动作密集”的中大型企业。
- 典型部门：法务、财务、IT运维、合规风控。

EN:
- Initial customers are mid-to-large enterprises with high-risk AI actions.
- Typical departments: legal, finance, IT ops, and compliance.

## Q7. 与现有安全产品关系是替代还是补充？

CN:
- 定位是补充并增强，不替代现有SIEM、监控或权限系统。
- 我们给现有系统增加“可验证性”和“可追责证据层”。

EN:
- We complement existing SIEM/monitoring/identity stacks, not replace them.
- We add verifiability and accountability evidence to existing controls.

## Q8. 如何应对误报或业务阻断担忧？

CN:
- 采用分阶段策略：先告警模式，再强制阻断模式。
- 提供回滚路径与白名单机制，避免一刀切影响业务连续性。

EN:
- We use phased rollout: alert mode first, enforcement mode next.
- Rollback and allowlist controls reduce business disruption risk.

## Q9. 如何证明可规模化？

CN:
- 通过标准化收据和自动化验证降低边际接入成本。
- CI与运行时都可自动化集成，适配多团队并行开发。

EN:
- Standardized receipts and automated verification reduce marginal onboarding cost.
- CI and runtime integration both support multi-team scale.

## Q10. 你们现在最大的短板是什么？

CN:
- 商业化案例数量仍在早期，需要更多外部试点与付费验证。
- 我们已制定8周成熟度计划，重点补齐试点与收入证据。

EN:
- Commercial case volume is still early; more pilots and paid validation are needed.
- We have an 8-week maturity plan focused on pilot and revenue evidence.

## Q11. 如果竞品快速复制你们开源能力怎么办？

CN:
- 协议文档可复制，但跨仓库一致性、证据质量和生态整合难复制。
- 我们会通过标准治理、认证体系和实施经验建立护城河。

EN:
- Docs can be copied; reliable cross-repo conformance and evidence quality are harder.
- We build defensibility via governance, certification, and implementation know-how.

## Q12. 北京落地价值是什么？

CN:
- 可作为北京AI治理与可信执行的标杆样板，服务产业链和监管协同。
- 适配北京对AI安全、数字治理、国际化创新项目的政策方向。

EN:
- It can serve as a Beijing reference project for AI governance and trusted execution.
- It aligns with local priorities on AI safety, digital governance, and global innovation.

## Q13. 你们需要大赛提供什么帮助？

CN:
- 产业试点对接：2-3个真实业务场景。
- 资源支持：政策导师、行业顾问、机构合作窗口。
- 融资支持：帮助团队加速从“技术验证”走向“商业验证”。

EN:
- Pilot matching: 2-3 real business scenarios.
- Resource support: policy mentors, domain advisors, and institutional channels.
- Financing support to accelerate from technical validation to commercial validation.

## Q14. 为什么这个项目值得拿名次？

CN:
- 技术上可验证，不是概念演示。
- 工程上可复现，不是一次性脚本。
- 产业上可落地，覆盖企业AI治理刚需。

EN:
- It is verifiable technically, not conceptual.
- It is reproducible operationally, not one-off.
- It is deployable commercially for urgent enterprise governance needs.

## Q15. 评委当场要看“真东西”，你们展示什么？

CN:
1. 现场运行一条校验命令，展示可复核证据输出。
2. 展示篡改样本被拒绝，证明系统不是“只会报喜”。
3. 打开 `EVIDENCE.md` 显示多仓库接入与最新状态。

EN:
1. Run a live verification command and show reproducible outputs.
2. Show tamper-case rejection to prove fail-closed behavior.
3. Open `EVIDENCE.md` for multi-repo adoption and latest status.

