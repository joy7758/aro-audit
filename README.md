## AAR-MCP-2.0 Core Specification

The AAR-MCP-2.0 Core Specification is frozen as Release Candidate (rc1).

See:
docs/spec/AAR-MCP-2.0-Core-Spec.md

Tag:
spec/v2.0.0-rc1

---
# aro-audit

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![License](https://img.shields.io/badge/License-MIT-0E8A16)](LICENSE)
[![Status](https://img.shields.io/badge/Status-P0%20Remediated-0A7D32)](README.md)

> AAR/ALC v1.0 baseline for production-grade AI agent auditing.
>
> 面向 AI Agent 生产场景的 AAR/ALC v1.0 审计基线实现。

## Overview | 项目概览

`aro-audit` turns plain logs into independently verifiable evidence:

- Verifiable statements (`AAR`)
- Liability chain (`ALC`) via `prev_digest`
- Checkpoint sealing (`range + merkle_root + store_fingerprint + checkpoint_sig`)
- Org accountability through Ed25519 signatures
- Public-key-only verification for third-party auditors

`aro-audit` 将普通日志升级为可独立复核的证据链：

- 可核验陈述（`AAR`）
- 通过 `prev_digest` 形成责任链（`ALC`）
- 区间封签（`range + merkle_root + store_fingerprint + checkpoint_sig`）
- 使用 Ed25519 签名完成组织责任绑定
- 验证端仅需公钥材料

## Why It Matters | 价值点

| Capability | 中文 | English |
| --- | --- | --- |
| Tamper evidence | `sequence_no + prev_digest` 线性链路防篡改 | Linear chain protects event ordering and integrity |
| Independent verification | 第三方只需 `journal + pubkey` 即可验签 | Verifiers need only `journal + public key` |
| Compliance export | 自动生成 `AAR-Manifest.json` 与校验命令 | Exportable manifest for compliance workflows |
| Deliverable packet | 产出 `audit_packet.zip` 可直接交付复核 | Ready-to-share packet for review and handoff |

## Quickstart (1 minute) | 1 分钟跑通

### 1) Environment setup | 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

### 2) Generate demo journal | 生成 demo 日志

```bash
aro gen-demo
```

### 3) Export manifest + clean audit packet | 导出清单与审计包

```bash
aro export
```

### 4) Verify with public key only | 仅用公钥验证

```bash
python3 sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_pubkey_ed25519.pem
```

Expected output | 预期输出：

```text
VERIFY_OK: demo/out/journal.jsonl statements= 10
```

## CLI Commands | 命令说明

| Command | 中文 | English |
| --- | --- | --- |
| `aro gen-demo` | 生成 demo `journal` 与 `checkpoint`，并导出公钥 | Generate demo journal/checkpoints and export public key |
| `aro verify` | 使用公钥进行完整校验 | Run end-to-end verification with public key |
| `aro export` | 生成 `AAR-Manifest.json` 与 `audit_packet.zip` | Export manifest and build audit packet |

## Artifact Outputs | 产物说明

### `demo/out/`

- `journal.jsonl`: append-only fact source
- `AAR-Manifest.json`: summary, checkpoint index, verify command
- `org_pubkey_ed25519.pem`: public key for independent verification
- `verify.sh`: one-command verification script
- `README.txt`: packet usage instructions
- `audit_packet.zip`: clean deliverable package (no private key)

### `release/submission/`

- `AAR-Manifest.json`
- `audit_packet.zip`
- `README_submissions.txt`
- paper/spec files for submission packaging

Top-level submission bundle:

- `release/aro_submission_bundle.zip`

## Business Assets | 商业化资产

- `business/README.md`
- `business/templates/PR_template.md`
- `business/templates/email_design_partner.txt`
- `business/templates/release_checklist.md`

## Security Boundary (P0) | 安全边界（P0）

- Verification is public-key-only.
- `manifest` stores `org_pubkey_path` (not private key path).
- CLI execution uses `subprocess.run(..., shell=False)` (no `os.system`).
- Private keys are for local signing only and are excluded from deliverable zips.
- `.gitignore` excludes `.venv/`, `demo/out/*.pem`, `demo/out/*.zip`, `__pycache__/`, `*.pyc`, `.DS_Store`.

## Repository Layout | 目录结构

```text
sdk/
  cli/            aro CLI
  journal/        WORM JSONL writer
  keys/           Ed25519 key utilities
  verify/         digest/chain/checkpoint verification
pro/
  export/         AAR manifest exporter
demo/
  gen_journal.py  demo generator
spec/
  AAR_v1.0.md     frozen rules + vectors
release/
  submission/     release artifacts
```

## v1.0 Frozen Rules | v1.0 冻结规则

1. Redact first, then sign canonicalized statement bytes.
2. Checkpoint must include explicit coverage and signature material.
3. Single-writer per trace (`sequence_no` strictly monotonic, `prev_digest` linked).

## FAQ

### Do verifiers need private keys? | 验证方是否需要私钥？

No. Verification uses public key only.  
不需要。验证仅依赖公钥。

### Is demo private key shipped in release bundles? | 交付包里会包含 demo 私钥吗？

No. Deliverable packets are built without private keys.  
不会。交付包已排除私钥材料。

## Legal and IP | 法律与知识产权

- License: `MIT` (`LICENSE`)
- Copyright: `COPYRIGHT`
- Notice and third-party marks: `NOTICE`
- Project trademark usage: `TRADEMARK_POLICY.md`
- Contribution IP rules: `CONTRIBUTING.md`
- IP/license commercialization boundary: `docs/IP_AND_LICENSE_STRATEGY.md`

Copyright strengthening for this repository:

- All source contributions are licensed under MIT.
- Third-party trademarks are identified in `NOTICE` and are not claimed.
- Contributors must only submit code and content they have rights to use.

Run legal baseline checks:

```bash
tools/check_legal.sh
```

本仓库已强化版权与知识产权治理：

- 统一采用 MIT 许可并落地到 `LICENSE`。
- 第三方商标归属与使用边界在 `NOTICE` 中明确。
- 贡献者需保证提交内容具备合法权利，规则见 `CONTRIBUTING.md`。

## License

MIT
