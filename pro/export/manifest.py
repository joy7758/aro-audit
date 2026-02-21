from __future__ import annotations
import json, os, time, hashlib
from typing import Any, Dict, List, Optional

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return "sha256:" + h.hexdigest()

def load_jsonl(path: str) -> List[Dict[str, Any]]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out

def main() -> int:
    journal_path = os.environ.get("JOURNAL", "demo/out/journal.jsonl")
    key_path = os.environ.get("KEY", "demo/out/org_subkey_ed25519.pem")
    out_path = os.environ.get("OUT", "demo/out/AAR-Manifest.json")

    rows = load_jsonl(journal_path)
    statements = [r for r in rows if r.get("_record_type") == "statement"]
    checkpoints = [r for r in rows if r.get("_record_type") == "checkpoint"]

    trace_id = None
    ts_list = []
    for s in statements:
        tc = s.get("trace_context", {})
        trace_id = trace_id or tc.get("trace_id")
        if tc.get("timestamp_ms") is not None:
            ts_list.append(int(tc["timestamp_ms"]))

    manifest = {
        "manifest_version": "v1.0",
        "generated_at_ms": int(time.time() * 1000),
        "trace_id": trace_id,
        "statement_count": len(statements),
        "time_start_ms": min(ts_list) if ts_list else None,
        "time_end_ms": max(ts_list) if ts_list else None,
        "artifacts": {
            "journal_path": journal_path,
            "journal_sha256": sha256_file(journal_path),
            "org_subkey_path": key_path,
        },
        "checkpoints": [
            {
                "range_start_seq": c.get("range_start_seq"),
                "range_end_seq": c.get("range_end_seq"),
                "merkle_root": c.get("merkle_root"),
                "store_fingerprint": c.get("store_fingerprint"),
                "key_fingerprint": c.get("key_fingerprint"),
                "checkpoint_sig": c.get("checkpoint_sig"),
                "timestamp_ms": c.get("timestamp_ms"),
            }
            for c in checkpoints
        ],
        "revocation_snapshot": {
            "key_fingerprint": checkpoints[-1].get("key_fingerprint") if checkpoints else None,
            "status": "VALID",
            "snapshot_ms": int(time.time() * 1000),
            "note": "v1.0 最小实现：仅声明当前 sub-key 有效；后续升级 CRL/OCSP/吊销列表。"
        },
        "verification": {
            "command": f"python sdk/verify/verify.py {journal_path} {key_path}"
        }
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("WROTE_MANIFEST:", out_path)
    print("TRACE:", manifest["trace_id"], "STATEMENTS:", manifest["statement_count"], "CHECKPOINTS:", len(manifest["checkpoints"]))
    print("VERIFY_CMD:", manifest["verification"]["command"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
