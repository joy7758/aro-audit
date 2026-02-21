# AAR/ALC (ARO-Audit)

> **AAR-MCP-2.0 RC1（对外冻结）**：规范 + Conformance + 可下载 Bundle 已发布。
> - 规范：`docs/spec/AAR-MCP-2.0-Core-Spec.md`
> - Conformance：`spec/CONFORMANCE.md`
> - Bundle：`release/spec_bundle_rc1.zip`
> - 验证：运行 `./tools/run_conformance.sh`

# AAR-MCP-2.0
## Evidence Layer for AI With Real Authority

AAR-MCP-2.0 is a tamper-evident evidence protocol for AI actions in privileged environments.
AAR-MCP-2.0 是一个面向高权限 AI 行为的防篡改证据层协议。

When an AI can write files, change configs, or trigger financial actions, observability is not enough.
当 AI 能写文件、改配置、甚至触发转账时，仅有日志远远不够。

You need verifiable evidence.
你需要可验证的证据。

---

## Why This Exists | 为什么要做这个协议

Traditional logs answer: "What did the system say happened?"
传统日志回答的是：“系统声称发生了什么？”

AAR-MCP answers: "Can anyone independently verify what happened and detect tampering?"
AAR-MCP 回答的是：“任何第三方能否独立验证发生了什么，并检测篡改？”

---

## Core Guarantees | 核心保证

- `AAR` records each high-risk action with explicit fields (`seq`, `tool`, `args`, `timestamp`).
- `CHECKPOINT` seals record ranges using Merkle root + Ed25519 signature.
- `prev_checkpoint_hash` links checkpoints into a verifiable chain.
- Any deletion, insertion, reordering, or field tampering breaks verification.

- `AAR` 对高风险操作逐条留痕（`seq`、`tool`、`args`、`timestamp`）。
- `CHECKPOINT` 通过 Merkle Root 与 Ed25519 对区间封签。
- `prev_checkpoint_hash` 将多个 checkpoint 串成可验证链。
- 删除、插入、重排、字段篡改都会导致验证失败。

---

## Scope Boundary | 协议边界

AAR-MCP provides tamper-evidence, not endpoint hardening.
AAR-MCP 提供“可验伪”，不直接提供主机加固。

Out of scope:

- private key theft
- host compromise before sealing
- infrastructure availability

不在协议内的问题：私钥泄露、封签前主机沦陷、基础设施可用性。

---

## 30-Second Demo | 30 秒演示

```text
===============================
 AAR-MCP-2.0 High Risk Demo
===============================

1️⃣ Generating high-risk action...
High-risk action recorded.
Amount transferred: 100000

2️⃣ Verifying integrity...
VERIFY_OK: full chain valid

3️⃣ Simulating tampering...

4️⃣ Verifying tampered journal...
Merkle mismatch

===============================
 Demo complete
===============================
```

From repo root:

```bash
cd demo/high_risk_authority
source ../../.venv/bin/activate
./run.sh
```

Expected behavior:

- Original journal: `VERIFY_OK: full chain valid`
- Tampered journal: verification fails (for example `Merkle mismatch`)
- Demo key mode: private key stays in memory by default (no `private.pem` is written)

预期结果：原始日志验证通过；篡改后日志验证失败。

---

## Spec Status | 协议状态

Core specification is frozen as Release Candidate:

- Spec: `docs/spec/AAR-MCP-2.0-Core-Spec.md`
- Tag: `spec/v2.0.0-rc1`
- Audit remediation sync: `docs/AUDIT_REMEDIATION_2026-02-21.md`

---

## Repository Map | 仓库结构

- `sdk/mcp_server_wrapper/`: enforcement + checkpoint generation
- `sdk/verify/`: checkpoint / chain verification
- `sdk/anchor/`: external anchoring helpers (Git anchor)
- `demo/high_risk_authority/`: self-contained high-risk demo
- `docs/spec/`: protocol specification

Note: `mcp-aar` requires an existing Ed25519 private key path via `--key`; it will not auto-generate private keys on disk.

---

## One-Line Positioning | 一句话定位

AAR-MCP-2.0 turns AI operation logs into cryptographically verifiable evidence.
AAR-MCP-2.0 把“可观测日志”升级为“可密码学验证证据”。

---

# 🔗 结构示意

AAR Record → Merkle Tree → CHECKPOINT → Signature → Verification

篡改任何一条 AAR  
        ↓  
Merkle Root 改变  
        ↓  
签名验证失败  

---

# 🗣 Open Discussions

We are actively discussing the protocol design:

- 🧠 Core Question  
  https://github.com/joy7758/aro-audit/discussions/1

- 🔬 Technical Review Guidelines  
  https://github.com/joy7758/aro-audit/discussions/2

Structured critique is welcome.
