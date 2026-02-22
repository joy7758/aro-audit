#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Iterator

MANIFEST_PATH = "manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def canonical_json(obj: Any, *, sort_keys: bool = True, separators: tuple[str, str] = (",", ":"), ensure_ascii: bool = False) -> str:
    return json.dumps(obj, sort_keys=sort_keys, separators=separators, ensure_ascii=ensure_ascii)


def load_manifest() -> dict[str, Any]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def iter_journal(journal_path: str) -> Iterator[dict[str, Any]]:
    if not os.path.exists(journal_path):
        raise FileNotFoundError(journal_path)
    with open(journal_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if raw:
                yield json.loads(raw)


def compute_entry_hash(prev_entry_hash: str, entry_without_hash: dict[str, Any], policy: dict[str, Any]) -> str:
    canon = canonical_json(
        entry_without_hash,
        sort_keys=bool(policy["canonical_json"]["sort_keys"]),
        separators=tuple(policy["canonical_json"]["separators"]),
        ensure_ascii=bool(policy["canonical_json"]["ensure_ascii"]),
    )
    payload = (prev_entry_hash + canon).encode("utf-8")
    return sha256_bytes(payload)


def fail(message: str) -> None:
    print(f"VERIFY_FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"VERIFY_OK: {message}")


def main() -> int:
    manifest = load_manifest()
    policy = manifest["audit_policy"]

    target_path = manifest["targets"][0]["path"]
    journal_path = manifest["journal"]["path"]

    target_sha = sha256_file(target_path)
    journal_sha = sha256_file(journal_path)

    declared = manifest.get("integrity", {})
    declared_target = declared.get("target_sha256", "")
    declared_journal = declared.get("journal_sha256", "")
    declared_last = declared.get("last_entry_hash", "")

    if declared_target and declared_target != target_sha:
        fail(f"target_sha256 mismatch: manifest={declared_target} computed={target_sha}")
    if declared_journal and declared_journal != journal_sha:
        fail(f"journal_sha256 mismatch: manifest={declared_journal} computed={journal_sha}")

    required = set(policy["required_fields_in_entry"])

    prev_hash = "0" * 64
    last_entry_hash: str | None = None
    last_target_sha: str | None = None
    expected_seq = 1

    any_entry = False
    for entry in iter_journal(journal_path):
        any_entry = True

        missing = [k for k in required if k not in entry]
        if missing:
            fail(f"journal entry missing fields: {missing}")

        seq = entry.get("seq")
        if not isinstance(seq, int) or seq != expected_seq:
            fail(f"seq continuity broken: expected={expected_seq} got={seq}")

        if entry["target_path"] != target_path:
            fail(f"target_path mismatch at seq={seq}: {entry['target_path']} != {target_path}")

        if entry["prev_entry_hash"] != prev_hash:
            fail(f"hash chain broken at seq={seq} (prev mismatch)")

        entry_without_hash = dict(entry)
        entry_hash = entry_without_hash.pop("entry_hash")
        recomputed = compute_entry_hash(prev_hash, entry_without_hash, policy)
        if entry_hash != recomputed:
            fail(f"entry_hash mismatch at seq={seq}")

        prev_hash = entry_hash
        last_entry_hash = entry_hash
        last_target_sha = entry["target_sha256"]
        expected_seq += 1

    if not any_entry:
        fail("journal is empty (no lifecycle proof). Run record_event.py to create entries.")

    if last_target_sha != target_sha:
        fail(f"target file hash does not match last journal entry: last={last_target_sha} current={target_sha}")

    if declared_last and declared_last != last_entry_hash:
        fail(f"last_entry_hash mismatch: manifest={declared_last} computed={last_entry_hash}")

    ok("Lifecycle integrity intact (hash chain + file hashes + last-state match).")
    print("DETAILS:")
    print(f"  target_sha256={target_sha}")
    print(f"  journal_sha256={journal_sha}")
    print(f"  last_entry_hash={last_entry_hash}")
    print(f"  profile_handle={manifest.get('profile_handle', '')}")
    print(f"  public_key_fingerprint={manifest.get('identity_anchor', {}).get('public_key_fingerprint', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
