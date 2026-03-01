# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any

DEFAULT_JOURNAL_PATH = "demo/out/journal.jsonl"
DEFAULT_KEY_PATH = "demo/out/org_pubkey_ed25519.pem"
DEFAULT_OUT_PATH = "demo/out/AAR-Manifest.json"


def sha256_file(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {lineno}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Invalid JSONL at line {lineno}: expected object")
            rows.append(obj)
    return rows


def main() -> int:
    journal_path = os.environ.get("JOURNAL", DEFAULT_JOURNAL_PATH)
    key_path = os.environ.get("KEY", DEFAULT_KEY_PATH)
    out_path = os.environ.get("OUT", DEFAULT_OUT_PATH)

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

    manifest: dict[str, Any] = {
        "manifest_version": "v1.0",
        "generated_at_ms": int(time.time() * 1000),
        "trace_id": trace_id,
        "statement_count": len(statements),
        "time_start_ms": min(ts_list) if ts_list else None,
        "time_end_ms": max(ts_list) if ts_list else None,
        "artifacts": {
            "journal_path": journal_path,
            "journal_sha256": sha256_file(journal_path),
            "org_pubkey_path": key_path,
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
            "note": "v1.0 minimal implementation; CRL/OCSP support can be added later.",
        },
        "verification": {"command": f"python sdk/verify/verify.py {journal_path} {key_path}"},
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print("WROTE_MANIFEST:", out_path)
    print(
        "TRACE:",
        manifest["trace_id"],
        "STATEMENTS:",
        manifest["statement_count"],
        "CHECKPOINTS:",
        len(manifest["checkpoints"]),
    )
    print("VERIFY_CMD:", manifest["verification"]["command"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
