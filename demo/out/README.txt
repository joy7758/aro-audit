AAR/ALC 审计包（demo）

包含：
- journal.jsonl：事实源（JSONL，append-only）
- AAR-Manifest.json：合规导出摘要（含 checkpoint 信息与复核命令）
- org_subkey_ed25519.pem：demo 子密钥（真实生产不建议打包）
- verify.sh：一键复核脚本（第三方可独立验证 journal 未被篡改）

复核方法：
1) 激活虚拟环境（或确保有 python + 依赖）
2) 执行：./verify.sh
