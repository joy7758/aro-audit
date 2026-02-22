import hashlib
import json
import re
import sys
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from sdk.canonical.jcs import dumps as jcs_dumps

VERSION_RE = re.compile(r"^AAR-MCP-(\d+)\.(\d+)$")
SUPPORTED_MAJOR = 2


def canonical_json_bytes(obj: Any) -> bytes:
    # RFC8785 canonicalization for stable digest/signature input across implementations.
    return jcs_dumps(obj)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checkpoint_hash(checkpoint_obj: dict[str, Any]) -> str:
    return "sha256:" + sha256_hex(canonical_json_bytes(checkpoint_obj))


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
    if not isinstance(public_key, Ed25519PublicKey):
        return fail("Public key must be Ed25519")

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [(lineno, line.rstrip("\n")) for lineno, line in enumerate(f, start=1) if line.strip()]

    if not raw_lines:
        return fail("Empty journal")

    aars_by_seq: dict[int, dict[str, Any]] = {}
    checkpoints: list[tuple[int, dict[str, Any]]] = []
    for lineno, raw in raw_lines:
        try:
            obj = json.loads(raw)
        except Exception as exc:
            return fail(f"Invalid JSON at line {lineno}: {exc}")
        record_type = obj.get("type")
        if not check_version(obj.get("version")):
            return fail("Unsupported protocol major version")
        if record_type == "AAR":
            seq = obj.get("seq")
            if not isinstance(seq, int):
                return fail(f"Invalid AAR seq at line {lineno}")
            if seq in aars_by_seq:
                return fail(f"Duplicate AAR seq {seq} at line {lineno}")
            aars_by_seq[seq] = {"raw": raw, "lineno": lineno, "obj": obj}
        elif record_type == "CHECKPOINT":
            checkpoints.append((lineno, obj))
        else:
            return fail(f"Unknown record type at line {lineno}: {record_type!r}")

    if not aars_by_seq:
        return fail("No AAR found")

    ordered_seqs = sorted(aars_by_seq.keys())
    if ordered_seqs[0] != 0:
        return fail(f"First AAR seq expected 0, got {ordered_seqs[0]}")
    if ordered_seqs != list(range(len(ordered_seqs))):
        return fail("AAR sequence not contiguous")

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
            if entry["lineno"] >= cp_line_index:
                return fail("Range mismatch")
            segment.append(entry["raw"])

        root = merkle_root(segment)
        if root != cp.get("merkle_root"):
            return fail("Merkle mismatch")

        if cp.get("prev_checkpoint_hash") != prev_hash_expected:
            return fail("Checkpoint linkage broken")

        payload = dict(cp)
        payload.pop("signature", None)
        to_verify = canonical_json_bytes(payload)
        try:
            public_key.verify(bytes.fromhex(signature_hex), to_verify)
        except (InvalidSignature, ValueError):
            return fail("Invalid signature")

        prev_hash_expected = checkpoint_hash(cp)
        next_expected_start = end + 1

    if next_expected_start != len(ordered_seqs):
        return fail("Last AAR range not covered by checkpoints")

    print("VERIFY_OK: full chain valid")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: verify_chain <journal> <pubkey>")
        raise SystemExit(1)
    raise SystemExit(verify_chain(sys.argv[1], sys.argv[2]))
