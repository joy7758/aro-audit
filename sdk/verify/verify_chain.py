import hashlib
import json
import re
import sys
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

VERSION_RE = re.compile(r"^AAR-MCP-(\d+)\.(\d+)$")
SUPPORTED_MAJOR = 2


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checkpoint_hash(checkpoint_obj: dict[str, Any]) -> str:
    return "sha256:" + sha256_hex(canonical_json(checkpoint_obj).encode("utf-8"))


def merkle_root(leaves: list[str]) -> str | None:
    nodes = [sha256_hex(leaf.encode("utf-8")) for leaf in leaves]
    if not nodes:
        return None
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        nodes = [
            sha256_hex((nodes[i] + nodes[i + 1]).encode("utf-8"))
            for i in range(0, len(nodes), 2)
        ]
    return nodes[0]


def check_version(version: Any) -> bool:
    if not isinstance(version, str):
        return False
    m = VERSION_RE.match(version)
    if not m:
        return False
    major = int(m.group(1))
    return major == SUPPORTED_MAJOR


def fail(msg: str) -> int:
    print(msg)
    return 1


def verify_chain(path: str, pubkey_path: str) -> int:
    with open(pubkey_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip("\n") for line in f if line.strip()]

    if not raw_lines:
        return fail("Empty journal")

    aars_by_seq: dict[int, dict[str, Any]] = {}
    checkpoints: list[tuple[int, dict[str, Any]]] = []
    for line_index, raw in enumerate(raw_lines):
        obj = json.loads(raw)
        record_type = obj.get("type")
        if not check_version(obj.get("version")):
            return fail("Unsupported protocol major version")
        if record_type == "AAR":
            seq = obj.get("seq")
            if not isinstance(seq, int):
                return fail("Range discontinuity")
            aars_by_seq[seq] = {"raw": raw, "line_index": line_index, "obj": obj}
        elif record_type == "CHECKPOINT":
            checkpoints.append((line_index, obj))

    if not aars_by_seq:
        return fail("No AAR found")

    ordered_seqs = sorted(aars_by_seq.keys())
    if ordered_seqs != list(range(len(ordered_seqs))):
        return fail("Range discontinuity")

    if not checkpoints:
        return fail("No CHECKPOINT found")

    prev_hash_expected: str | None = None
    next_expected_start = 0

    for cp_line_index, cp in checkpoints:
        cp_range = cp.get("range")
        signature_hex = cp.get("signature")
        if not isinstance(cp_range, list) or len(cp_range) != 2:
            return fail("Range mismatch")
        if not isinstance(signature_hex, str):
            return fail("Invalid signature")

        start, end = cp_range
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            return fail("Range mismatch")
        if start != next_expected_start:
            return fail("Range discontinuity")

        segment = []
        for seq in range(start, end + 1):
            entry = aars_by_seq.get(seq)
            if entry is None:
                return fail("Range mismatch")
            if entry["line_index"] >= cp_line_index:
                return fail("Range mismatch")
            segment.append(entry["raw"])

        root = merkle_root(segment)
        if root != cp.get("merkle_root"):
            return fail("Merkle mismatch")

        if cp.get("prev_checkpoint_hash") != prev_hash_expected:
            return fail("Checkpoint linkage broken")

        payload = dict(cp)
        payload.pop("signature", None)
        to_verify = canonical_json(payload).encode("utf-8")
        try:
            public_key.verify(bytes.fromhex(signature_hex), to_verify)
        except (InvalidSignature, ValueError):
            return fail("Invalid signature")

        prev_hash_expected = checkpoint_hash(cp)
        next_expected_start = end + 1

    if next_expected_start != len(ordered_seqs):
        return fail("No CHECKPOINT found")

    print("VERIFY_OK: full chain valid")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: verify_chain <journal> <pubkey>")
        raise SystemExit(1)
    raise SystemExit(verify_chain(sys.argv[1], sys.argv[2]))
