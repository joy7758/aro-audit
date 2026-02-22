#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

MANIFEST_PATH = "manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def canonical_json(obj: Any, *, sort_keys: bool = True, separators: tuple[str, str] = (",", ":"), ensure_ascii: bool = False) -> str:
    return json.dumps(obj, sort_keys=sort_keys, separators=separators, ensure_ascii=ensure_ascii)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_manifest() -> dict[str, Any]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest(manifest: dict[str, Any]) -> None:
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_last_entry(journal_path: str) -> dict[str, Any] | None:
    if not os.path.exists(journal_path) or os.path.getsize(journal_path) == 0:
        return None
    last: dict[str, Any] | None = None
    with open(journal_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if raw:
                last = json.loads(raw)
    return last


def append_entry(journal_path: str, entry: dict[str, Any], policy: dict[str, Any]) -> None:
    canon = canonical_json(
        entry,
        sort_keys=bool(policy["canonical_json"]["sort_keys"]),
        separators=tuple(policy["canonical_json"]["separators"]),
        ensure_ascii=bool(policy["canonical_json"]["ensure_ascii"]),
    )
    with open(journal_path, "a", encoding="utf-8") as f:
        f.write(canon + "\n")


def compute_entry_hash(prev_entry_hash: str, entry_without_hash: dict[str, Any], policy: dict[str, Any]) -> str:
    canon = canonical_json(
        entry_without_hash,
        sort_keys=bool(policy["canonical_json"]["sort_keys"]),
        separators=tuple(policy["canonical_json"]["separators"]),
        ensure_ascii=bool(policy["canonical_json"]["ensure_ascii"]),
    )
    payload = (prev_entry_hash + canon).encode("utf-8")
    return sha256_bytes(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append an ARO-Audit lifecycle event for DPP demo.")
    parser.add_argument("--event", required=True, help="Event name, e.g., created / updated / shipped / recycled.")
    parser.add_argument("--actor", default="operator", help="Actor label, e.g., manufacturer / logistics / recycler.")
    args = parser.parse_args()

    manifest = load_manifest()
    policy = manifest["audit_policy"]

    target_path = manifest["targets"][0]["path"]
    journal_path = manifest["journal"]["path"]

    target_sha = sha256_file(target_path)

    last = read_last_entry(journal_path)
    prev_hash = last["entry_hash"] if last else ("0" * 64)
    seq = (last["seq"] + 1) if last else 1

    entry = {
        "seq": seq,
        "timestamp": utc_now_iso(),
        "event": args.event,
        "actor": args.actor,
        "target_path": target_path,
        "target_sha256": target_sha,
        "prev_entry_hash": prev_hash,
    }

    entry_hash = compute_entry_hash(prev_hash, entry, policy)
    entry["entry_hash"] = entry_hash

    append_entry(journal_path, entry, policy)

    journal_sha = sha256_file(journal_path)
    manifest["integrity"]["target_sha256"] = target_sha
    manifest["integrity"]["journal_sha256"] = journal_sha
    manifest["integrity"]["last_entry_hash"] = entry_hash

    now = utc_now_iso()
    if not manifest["provenance"].get("created_at"):
        manifest["provenance"]["created_at"] = now
    manifest["provenance"]["last_modified_at"] = now

    write_manifest(manifest)

    print("OK: event recorded")
    print(f"  seq={seq}")
    print(f"  target_sha256={target_sha}")
    print(f"  entry_hash={entry_hash}")
    print(f"  journal_sha256={journal_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
