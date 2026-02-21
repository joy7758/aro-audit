提交包说明（v1.0）

包含：
1) preprint_arxiv.pdf / preprint_arxiv.tex：3页论文（可投递）
2) audit_packet.zip：可复现实证据包（journal + manifest + verify.sh）
3) AAR-Manifest.json：合规导出摘要与复核命令
4) AAR_v1.0.md：协议冻结规范（硬规则）

复核命令（见 manifest 也可）：
python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_subkey_ed25519.pem

备注：
- demo 包含子密钥 pem 仅用于复现；生产环境不建议外发私钥
