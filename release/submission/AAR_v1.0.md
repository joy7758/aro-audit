# AAR v1.0 执行规范（冻结基线）

本规范用于生成“可核验陈述（Verifiable Statement）”与“责任链（ALC）”，作为自治代理行为审计的事实源（Source of Truth）。
本规范只定义事实层。解释层（风险评分等）必须放在 Index/Manifest，不得写入事实源。

## 冻结硬规则（v1.0 不可更改）

1) 签名输入（JCS + sha256）
- 脱敏：仅允许 hash 与受控 locator，不得出现明文敏感数据
- S_sig：Statement 副本，必须排除 attestations 与 checkpoint
- JCS：RFC8785 规范化得到 canonical_bytes
- digest：sha256(canonical_bytes) -> sha256:<hex>
- ORG 签名绑定 digest（v1.0 固定）

2) Checkpoint 覆盖区间（WORM 封签）
- range_start_seq..range_end_seq
- merkle_root + store_fingerprint + checkpoint_sig

3) 单写入者（Single-writer per Trace）
- v1.0 禁止同一 trace 多写入者并发写入
