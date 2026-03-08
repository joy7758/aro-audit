<p align="center">
  <img src="docs/assets/aro-audit-logo.svg" alt="ARO Audit logo" width="460" />
</p>

# ARO Audit

一句话：`ARO Audit` 不是单纯记录工具，而是高风险 AI 动作治理控制面（CI 门禁 + 动作边界收据 + 事后复验）。

## Digital Biosphere Ecosystem

This repository is part of the **Digital Biosphere Architecture**.

Architecture overview:
[digital-biosphere-architecture](https://github.com/joy7758/digital-biosphere-architecture)

<!-- SEARCH_VISIBILITY_BEGIN -->
## Discoverability Snapshot / 检索曝光摘要

- Standard ID / 标准编号: `RR-ARO`
- Repository / 仓库: `aro-audit`
- Canonical URL / 主链接: `https://github.com/joy7758/aro-audit`
- Positioning / 定位: `AI action governance control plane`
- DOI: `10.5281/zenodo.18728568`
- Onepager / 一页纸: [`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- Citation / 引用元数据: [`CITATION.cff`](CITATION.cff)
- Security / 安全策略: [`SECURITY.md`](SECURITY.md)

### AI-Readable Abstract / AI 可读摘要
- EN: `ARO Audit` is a governance control plane for high-risk AI actions: pre-release CI trust-boundary enforcement (`god-spear`), in-action policy receipts (`safety-valve-spec`), and post-action cryptographic replay verification (`aro-audit`).
- CN: `ARO Audit` 是高风险 AI 动作的治理控制面：上线前用 `god-spear` 做 CI 信任边界门禁，执行中用 `safety-valve-spec` 输出策略收据，事后用 `aro-audit` 做密码学复验。

### Search Keywords / 检索关键词
`ai action governance`, `governance control plane`, `ci trust boundary enforcement`, `shift-left security`, `policy gate`, `action receipt`, `tamper-evident audit trail`, `merkle checkpoint`, `replay verification`, `high-risk ai compliance`

### Suggested Search Phrases (EN)
- ai governance control plane for high-risk agent actions
- god-spear trust boundary ci gate safety-valve receipts aro-audit
- tamper-evident replay verification with merkle checkpoint ed25519

### 建议检索短语（中文）
- 高风险 AI 动作 治理控制面 CI 门禁
- god-spear trust boundary safety-valve 收据 aro-audit
- 可验证审计证据链 Merkle checkpoint 重放验证
<!-- SEARCH_VISIBILITY_END -->

## LLM / RAG 快速读取块

```yaml
project: aro-audit
standard_id: RR-ARO
category: ai action governance control plane
core_value: prevent + constrain + verify
layers:
  - build_time: god-spear trust-boundary gate in CI
  - action_time: safety-valve-spec verifiable ALLOW/DENY/DEGRADE receipts
  - post_action: aro-audit tamper-evident chain and replay verification
who_cares:
  - ciso and internal control teams
  - ai platform engineering
  - audit and compliance
verifier_output_success: "VERIFY_OK: full chain valid"
doi: 10.5281/zenodo.18728568
```

## 为什么这不是“日志工具”

普通日志解决“看见了什么”，我们解决“能不能阻断、能不能定责、能不能第三方复验”。

- 上线前：`god-spear` 把信任边界检查前移到 CI，规则不完整直接失败。
- 执行中：`safety-valve-spec` 要求边界动作带可验收据（ALLOW / DENY / DEGRADE）。
- 事后：`aro-audit` 生成不可篡改证据链，支持独立重放与验签。

## god-spear 在本仓库的落地证据

- CI 工作流：[`.github/workflows/spear.yml`](.github/workflows/spear.yml)
- 规则文件：[`.github/security/.spear-rules.json`](.github/security/.spear-rules.json)
- 当前检查命令：

```bash
npx -y --package god-spear@0.2.0 spear check .github/security/.spear-rules.json
```

- 合并证据快照（2026-02-24 UTC，本地生成）显示 `spear-check adoption count: 18`：[`competition/hicool-2026/EVIDENCE.md`](competition/hicool-2026/EVIDENCE.md)

## 你会得到什么业务结果

- 风险前移：问题在发布前暴露，而不是事故后补救。
- 问责明确：关键动作有标准化、可验证、可复核的收据链。
- 对外可信：客户、合作方、审计方都能独立验证，不依赖口头承诺。

## 快速开始（30 秒）

```bash
bash quickstart/run.sh
```

成功标志：

- baseline 样本输出 `VERIFY_OK: full chain valid`
- 篡改样本会被拒绝（`Merkle mismatch` 或签名/摘要失败）

## Quickstart / 快速开始（推荐：虚拟环境）

> EN: Some systems enforce PEP 668 (externally-managed environment). Use a virtual environment to install and run ARO-Audit safely.  
> 中文：部分系统启用 PEP 668（externally-managed environment）限制，请使用虚拟环境进行安装与运行，避免环境冲突。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

aro-vpml --help
examples/run_ab_compare.sh
```

### Generate a CISO-ready Markdown report / 生成 CISO 可读的 Markdown 报告

```bash
aro-vpml \
  --graph examples/pFDO_controlplane_case.yaml \
  --domain "CP_IAM,CP_CICD,pFDO_KERNEL_PERMS,pFDO_OBJECT_REGISTRY" \
  --sources "DEV_PUF_WEAK,DEV_PUF_STRONG,WORKLOAD_ID" \
  --max-depth 5 --max-paths 1000 --top-k 5 \
  --pretty \
  --report-md /tmp/vpml_report.md \
  --report-title "VPML AB Evidence Report"
```

> EN: JSON is printed to stdout (machine-readable). The Markdown report is saved to `--report-md` for audit delivery.
> 中文：JSON 始终输出到 stdout（便于管道/自动化）。Markdown 报告独立落盘到 `--report-md`（适合审计交付/邮件附件）。

## Audit Bundle (Manifest + SHA256) / 审计交付包（清单 + SHA256 校验）

**EN**  
`--bundle-dir` produces a self-contained audit deliverable: results, report, optional summary/dot, and a `MANIFEST.json` with SHA256 checksums and byte sizes for integrity verification.

**中文**  
`--bundle-dir` 会生成一个“自包含”的审计交付包：结果 JSON、报告 Markdown、可选的 summary/dot，以及带 SHA256/字节数的 `MANIFEST.json`，用于完整性校验与归档复核。

### What’s inside / 包内内容

**EN**
- `result.json` — machine-readable scoring output (same content as stdout JSON)
- `report.md` — CISO-ready narrative report (generated even if `--report-md` not provided)
- `summary.txt` — optional, appended from `--summary-file` when available
- `graph.dot` — optional, copied from `--dot` when available
- `MANIFEST.json` — metadata + per-file `{bytes, sha256}`

**中文**
- `result.json` —— 机器可读的评分输出（与 stdout JSON 同内容）
- `report.md` —— CISO 可读的叙事报告（即使不传 `--report-md` 也会在 bundle 中生成）
- `summary.txt` —— 可选：当提供 `--summary-file` 且可读取时写入
- `graph.dot` —— 可选：当启用 `--dot` 且文件存在时写入
- `MANIFEST.json` —— 元数据 + 每个文件的 `{bytes, sha256}`

### Generate a bundle / 生成审计包

```bash
aro-vpml \
  --graph examples/pFDO_controlplane_case.yaml \
  --domain "CP_IAM,CP_CICD,pFDO_KERNEL_PERMS,pFDO_OBJECT_REGISTRY" \
  --sources "DEV_PUF_WEAK,DEV_PUF_STRONG,WORKLOAD_ID" \
  --max-depth 5 --max-paths 1000 --top-k 5 \
  --pretty \
  --summary-file artifacts/SUMMARY.txt \
  --dot artifacts/vpml_graph.dot \
  --bundle-dir artifacts
```

> EN: The bundle name defaults to `vpml_bundle_<UTC>_<git>`. Use `--bundle-name` to override.
> 中文：bundle 名称默认 `vpml_bundle_<UTC>_<git>`，可用 `--bundle-name` 自定义。

### Verify MANIFEST / 校验 MANIFEST（完整性验真）

**EN**  
Run the following script inside the bundle directory to verify each file’s SHA256 and byte size against `MANIFEST.json`.

**中文**  
进入 bundle 目录后运行下列脚本，可按 `MANIFEST.json` 对每个文件进行 SHA256/字节数验真。

```bash
cd artifacts/vpml_bundle_<UTC>_<git>

python - <<'PY'
import json, hashlib, os, sys
from pathlib import Path

bundle = Path(".")
m = bundle / "MANIFEST.json"
if not m.exists():
    print("ERROR: MANIFEST.json not found in current directory", file=sys.stderr)
    sys.exit(1)

manifest = json.loads(m.read_text(encoding="utf-8"))
ok_all = True

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

for item in manifest.get("files", []):
    name = item["name"]
    expected_sha = item["sha256"]
    expected_bytes = item["bytes"]
    p = bundle / name
    if not p.exists():
        print(f"[FAIL] missing: {name}")
        ok_all = False
        continue
    actual_bytes = p.stat().st_size
    actual_sha = sha256_file(p)
    ok = (actual_bytes == expected_bytes) and (actual_sha == expected_sha)
    print(f"[{'OK' if ok else 'FAIL'}] {name} bytes={actual_bytes} sha256={actual_sha}")
    ok_all = ok_all and ok

print("ALL_OK =", ok_all)
sys.exit(0 if ok_all else 2)
PY
```

- **EN**: The manifest is the source of truth for reproducibility and integrity of the audit deliverable.
- **中文**：`MANIFEST.json` 是审计交付包的可复现与完整性“真源”。

## 全栈验证入口

- Evidence / 证据页: [VPML A/B Evidence (Physical Anchor → SCI ↓) / 物理锚点增强使 SCI 下降](docs/vpml/AB_EVIDENCE.md)
- 一页纸：[`docs/ONEPAGER_CN.md`](docs/ONEPAGER_CN.md)
- 快速体验：[`quickstart/README.md`](quickstart/README.md)
- 协议规范：[`spec/AAR_v1.0.md`](spec/AAR_v1.0.md)
- 一致性向量与守门规则：[`spec/CONFORMANCE.md`](spec/CONFORMANCE.md)
- 高风险权限演示：[`demo/high_risk_authority/README.md`](demo/high_risk_authority/README.md)
- HICOOL 合并叙事：[`competition/hicool-2026/README.md`](competition/hicool-2026/README.md)

## 关联项目

- `safety-valve-spec`: <https://github.com/joy7758/safety-valve-spec>
- `god-spear`: <https://github.com/joy7758/god-spear>

## 推荐引用

- 引用文件：[`CITATION.cff`](CITATION.cff)
- DOI：`https://doi.org/10.5281/zenodo.18728568`

```bibtex
@software{aro_audit_2026,
  title = {aro-audit},
  author = {Zhang, Bin},
  year = {2026},
  url = {https://github.com/joy7758/aro-audit},
  doi = {10.5281/zenodo.18728568}
}
```

## 当前凭证

- FDO Testbed ID: `21.T11966/aro-audit-profile-v1`
- Machine-readable metadata: [`machine-readable/repository.json`](machine-readable/repository.json)

## 许可证

本项目采用 [`LICENSE`](LICENSE) 中定义的许可条款。
