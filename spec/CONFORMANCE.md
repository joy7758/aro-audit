# ARO-AUDIT Conformance (RC1)

本文件定义“实现必须满足的最小一致性要求”，用于保证：
- 证据事实层不可被篡改
- 核心摘要边界不可被“重新解释”绕过
- CI 作为标准守门人长期有效

## 1. 测试向量（v1 boundary）

公钥：`spec/test_vectors/keys/test_pubkey.pem`

### MUST PASS
- `spec/test_vectors/boundary_base_v1.jsonl`
- `spec/test_vectors/boundary_attack_attestations_only.jsonl`
  - 说明：仅修改 `attestations/checkpoint` 等不参与签名/摘要边界的区域，必须仍通过

### MUST FAIL
- `spec/test_vectors/boundary_attack_predicate.jsonl`
  - 说明：修改 `predicate/subjects/trace_context` 等事实层边界内容，必须被拒绝（digest mismatch 或等价错误）

## 2. 退出码约定
- PASS：exit code = 0
- FAIL：exit code != 0

## 3. 兼容性承诺（RC1）
- 只要上述向量的 PASS/FAIL 结果不变，可视为非破坏性变更
- 若必须改变向量结果，必须提升 major 或发布新的 RC，并明确迁移策略
