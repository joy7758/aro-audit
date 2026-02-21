#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Quickstart: AAR-MCP-2.0 30s Demo ==="

if [ ! -d ".venv" ]; then
  echo "[FAIL] .venv 不存在。请先在仓库根目录创建虚拟环境。"
  exit 2
fi

# shellcheck source=/dev/null
source .venv/bin/activate

mkdir -p quickstart/out
OUT_DIR="quickstart/out"

echo "[1/4] 生成演示日志（AAR + CHECKPOINT）与公钥"
python - <<'PY'
from pathlib import Path
import shutil
import subprocess
import sys

# 复用仓库现成 demo（自包含）
demo_dir = Path("demo/high_risk_authority")
run_demo = demo_dir / "run_demo.py"
if not run_demo.exists():
    print("[FAIL] demo/high_risk_authority/run_demo.py 不存在。")
    sys.exit(2)

out_dir = Path("quickstart/out")
out_dir.mkdir(parents=True, exist_ok=True)

# 在 demo 目录执行，确保产物落在 demo 目录下
subprocess.run([sys.executable, "run_demo.py"], cwd=str(demo_dir), check=True)

src_journal = None
src_pub = None

candidates = [
    demo_dir / "journal.jsonl",
    demo_dir / "output" / "journal.jsonl",
    Path("demo/out/journal.jsonl"),
]
pub_candidates = [
    demo_dir / "public.pem",
    demo_dir / "output" / "public.pem",
    Path("demo/out/org_pubkey_ed25519.pem"),
    Path("demo/out/org_pubkey_ed25519.pub.pem"),
]

for p in candidates:
    if p.exists():
        src_journal = p
        break
for p in pub_candidates:
    if p.exists():
        src_pub = p
        break

if not src_journal or not src_journal.exists():
    print("[FAIL] 找不到 journal.jsonl 产物（demo/high_risk_authority 或 demo/out）。")
    sys.exit(2)
if not src_pub or not src_pub.exists():
    print("[FAIL] 找不到公钥 pem 产物（public.pem 或 org_pubkey_ed25519.pem）。")
    sys.exit(2)

dst_journal = out_dir / "journal.jsonl"
dst_pub = out_dir / "public.pem"

shutil.copyfile(src_journal, dst_journal)
shutil.copyfile(src_pub, dst_pub)

print("[OK] journal:", dst_journal)
print("[OK] pubkey:", dst_pub)
PY

echo "[2/4] 正常样本：全链校验"
python -m sdk.verify.verify_chain "$OUT_DIR/journal.jsonl" "$OUT_DIR/public.pem"

echo "[3/4] 生成篡改样本（改金额/改内容）"
python - <<'PY'
from pathlib import Path
import json
import sys

src = Path("quickstart/out/journal.jsonl")
dst = Path("quickstart/out/journal.tampered.jsonl")

lines = src.read_text(encoding="utf-8").splitlines()
out = []
tampered = False

for line in lines:
    obj = json.loads(line)

    if not tampered and isinstance(obj, dict):
        # AAR-MCP v2 结构
        if obj.get("type") == "AAR":
            args = obj.get("args")
            if not isinstance(args, dict):
                args = {}
                obj["args"] = args

            if "amount" in args and isinstance(args["amount"], (int, float, str)):
                args["amount"] = "999999"
                tampered = True
            elif "content" in args and isinstance(args["content"], str):
                args["content"] = args["content"] + "TAMPER"
                tampered = True
            else:
                args["tamper"] = True
                tampered = True

        # AAR v1 statement 结构
        elif obj.get("_record_type") == "statement":
            pred = obj.get("predicate")
            if not isinstance(pred, dict):
                pred = {}
                obj["predicate"] = pred
            inv = pred.get("invocation")
            if not isinstance(inv, dict):
                inv = {}
            inv["tamper"] = True
            pred["invocation"] = inv
            obj["predicate"] = pred
            tampered = True

    out.append(json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True))

dst.write_text("\n".join(out) + "\n", encoding="utf-8")
print("[OK] tampered journal:", dst, "tampered=", tampered)
if not tampered:
    print("[FAIL] 未能构造篡改样本。")
    sys.exit(2)
PY

echo "[4/4] 篡改样本：应当失败（Merkle mismatch / digest mismatch / signature invalid）"
set +e
python -m sdk.verify.verify_chain "$OUT_DIR/journal.tampered.jsonl" "$OUT_DIR/public.pem"
RC=$?
set -e

if [ "$RC" -eq 0 ]; then
  echo "[FAIL] 篡改样本居然通过了校验（不符合预期）"
  exit 3
else
  echo "[OK] 篡改样本被拒绝（符合预期），rc=$RC"
fi

echo "=== DONE: Quickstart OK ==="
