AAR/ALC 审计包（demo）

包含：
- journal.jsonl：事实源（JSONL，append-only）
- AAR-Manifest.json：合规导出摘要（含 checkpoint 信息与复核命令）
- org_pubkey_ed25519.pem：用于第三方独立验签的公钥
- verify.sh：一键复核脚本（使用 tools/python + 公钥）

复核方法：
1) 激活虚拟环境（或确保有 python + 依赖）
2) 执行：./verify.sh
