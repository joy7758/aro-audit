提交包说明（v1.0）

包含：
1) preprint_arxiv.pdf / preprint_arxiv.tex：3页论文（可投递）
2) audit_packet.zip：可复现实证据包（journal + manifest + verify.sh）
3) AAR-Manifest.json：合规导出摘要与复核命令
4) AAR_v1.0.md：协议冻结规范（硬规则）

复核命令（见 manifest 也可）：
python sdk/verify/verify.py demo/out/journal.jsonl demo/out/org_pubkey_ed25519.pem

备注：
- 验证只需公钥材料（org_pubkey_ed25519.pem）；私钥不在交付包内
