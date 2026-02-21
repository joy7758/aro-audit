# aro-audit (AAR/ALC v1.0 Baseline)

**中文**：面向 AI 代理（Agent）生产环境的**责任审计底座**：把“日志”升级为**可核验陈述（AAR）+ 责任链（ALC）+ WORM 封签 + 组织子密钥签名**，支持第三方独立复核。  
**English**: A sovereign-grade auditing substrate for production AI agents: **verifiable statements (AAR) + liability chain (ALC) + WORM sealing + org sub-key signatures**, enabling independent third-party verification.

---

## 你能得到什么 / What you get

- **WORM JSONL Journal（事实源）**：append-only 记录，每条 action 都可重算 digest  
- **Chain Integrity（时间之箭）**：`prev_digest` 链防篡改  
- **Checkpoint Sealing（区间封签）**：`range + merkle_root + store_fingerprint`  
- **Org Accountability（组织责任归属）**：checkpoint 使用 Ed25519 子密钥签名（Level-1 证据）  
- **Independent Verification（独立复核）**：`verify` 工具可第三方重算与验签  
- **Compliance Export Kit（合规导出包）**：`AAR-Manifest.json`  
- **Audit Packet（可交付审计包）**：`audit_packet.zip`  
- **CLI 入口（开发者入口）**：`aro gen-demo / verify / export`

---

## 快速开始 / Quickstart

### 1) 创建虚拟环境与安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
2) 生成 demo（journal + checkpoint + 子密钥）
aro gen-demo
3) 复核（第三方独立验证）
aro verify
# 或：
python3 sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_pubkey_ed25519.pem
4) 导出 Manifest（合规交差包）
aro export
# 产物：demo/out/AAR-Manifest.json
产物说明 / Artifacts

demo/out/journal.jsonl：事实源（statement + checkpoint）

demo/out/AAR-Manifest.json：导出摘要（含复核命令、checkpoint 汇总）

demo/out/audit_packet.zip：审计包（journal + manifest + verify.sh + README + 公钥）

docs/preprint_arxiv.pdf：3页论文（可投递）

release/aro_submission_bundle.zip：投递包（论文 + 审计包 + 规范）

⚠️ 安全提示：验证只需 `demo/out/org_pubkey_ed25519.pem`。demo 私钥仅用于本地签名，不进入交付包。

目录结构 / Repo Layout
sdk/
  journal/        WORM journal writer (JSONL)
  verify/         verification (digest/chain/merkle/signature)
  keys/           org sub-key (Ed25519) utilities
  cli/            aro CLI
pro/export/       manifest exporter
spec/             AAR v1.0 spec + test_vectors
docs/             pitch + preprint (md/tex/pdf)
demo/             demo generator
release/          submission bundles
v1.0 冻结规则 / v1.0 Frozen Rules

Signing input: redact first; sign canonicalized statement excluding attestations and checkpoint

Checkpoint sealing: explicit coverage range + merkle_root + store_fingerprint + checkpoint_sig

Single-writer per trace: linear sequence_no and prev_digest

License

MIT
