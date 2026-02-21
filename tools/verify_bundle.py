#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import sys
import zipfile
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def decode_signature(sig: str) -> bytes:
    try:
        return bytes.fromhex(sig)
    except Exception:
        return base64.b64decode(sig + "==")


def normalize_root(root: str) -> str:
    if root.startswith("sha256:"):
        return root.split("sha256:", 1)[1]
    return root


def load_pubkey(pem_bytes: bytes) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(pem_bytes)
    if not isinstance(key, Ed25519PublicKey):
        raise RuntimeError("public key is not Ed25519")
    return key


def merkle_root_v1(statement_digests_hex: list[str]) -> str:
    if not statement_digests_hex:
        return sha256_hex(b"")
    level = [bytes.fromhex(h) for h in statement_digests_hex]
    while len(level) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(hashlib.sha256(left + b"|" + right).digest())
        level = nxt
    return level[0].hex()


def merkle_root_mcp2(aar_lines: list[str]) -> str:
    hashes = [sha256_hex(line.encode("utf-8")) for line in aar_lines]
    if not hashes:
        raise RuntimeError("no AAR leaves")
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            sha256_hex((hashes[i] + hashes[i + 1]).encode("utf-8"))
            for i in range(0, len(hashes), 2)
        ]
    return hashes[0]


def compute_statement_digest_v1(statement_obj: dict[str, Any]) -> str:
    s = dict(statement_obj)
    for k in ("attestations", "checkpoint", "_digest", "_record_type"):
        s.pop(k, None)
    return "sha256:" + sha256_hex(canonical_json_bytes(s))


def verify_v1(records: list[tuple[str, dict[str, Any]]], pub: Ed25519PublicKey) -> tuple[int, int]:
    statements: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    for _, obj in records:
        rtype = obj.get("_record_type")
        if rtype == "statement":
            statements.append(obj)
        elif rtype == "checkpoint":
            checkpoints.append(obj)

    if not statements:
        raise RuntimeError("no statements")
    if not checkpoints:
        raise RuntimeError("no checkpoints")

    seqs = [s.get("trace_context", {}).get("sequence_no") for s in statements]
    if not all(isinstance(x, int) for x in seqs):
        raise RuntimeError("statement sequence_no missing")
    if seqs != list(range(seqs[0], seqs[0] + len(seqs))):
        raise RuntimeError("range discontinuity")

    for i, s in enumerate(statements):
        stored = s.get("_digest")
        computed = compute_statement_digest_v1(s)
        if stored != computed:
            raise RuntimeError("statement digest mismatch")
        if i > 0:
            prev_expected = statements[i - 1].get("_digest")
            prev_got = s.get("trace_context", {}).get("prev_digest")
            if prev_got != prev_expected:
                raise RuntimeError("prev_digest mismatch")

    by_seq = {s["trace_context"]["sequence_no"]: s for s in statements}
    checkpoints = sorted(checkpoints, key=lambda c: c.get("range_start_seq", -1))

    covered_end = None
    for cp in checkpoints:
        start = cp.get("range_start_seq")
        end = cp.get("range_end_seq")
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise RuntimeError("checkpoint range invalid")
        if covered_end is not None and start != covered_end + 1:
            raise RuntimeError("checkpoint range discontinuity")

        digest_hexes: list[str] = []
        for seq in range(start, end + 1):
            st = by_seq.get(seq)
            if not st:
                raise RuntimeError("checkpoint refers missing statement")
            digest_hexes.append(st["_digest"].split("sha256:", 1)[1])

        root = merkle_root_v1(digest_hexes)
        if normalize_root(cp.get("merkle_root", "")) != root:
            raise RuntimeError("merkle mismatch")

        sig_hex = cp.get("checkpoint_sig") or cp.get("signature")
        if not isinstance(sig_hex, str):
            raise RuntimeError("checkpoint signature missing")

        # Prefer legacy v1 message schema if keys are present.
        if all(k in cp for k in ("range_start_seq", "range_end_seq", "merkle_root", "store_fingerprint", "key_fingerprint")):
            msg_obj = {
                "range_start_seq": cp["range_start_seq"],
                "range_end_seq": cp["range_end_seq"],
                "merkle_root": cp["merkle_root"],
                "store_fingerprint": cp["store_fingerprint"],
                "key_fingerprint": cp["key_fingerprint"],
            }
        else:
            msg_obj = dict(cp)
            msg_obj.pop("signature", None)
            msg_obj.pop("checkpoint_sig", None)

        try:
            pub.verify(decode_signature(sig_hex), canonical_json_bytes(msg_obj))
        except InvalidSignature as e:
            raise RuntimeError("checkpoint signature invalid") from e

        covered_end = end

    return len(statements), len(checkpoints)


def verify_mcp2(records: list[tuple[str, dict[str, Any]]], pub: Ed25519PublicKey) -> tuple[int, int]:
    aars: list[tuple[str, dict[str, Any]]] = []
    checkpoints: list[dict[str, Any]] = []

    for raw, obj in records:
        rtype = obj.get("type")
        if rtype == "AAR":
            aars.append((raw, obj))
        elif rtype == "CHECKPOINT":
            checkpoints.append(obj)

    if not aars:
        raise RuntimeError("no AAR records")
    if not checkpoints:
        raise RuntimeError("no checkpoints")

    by_seq: dict[int, tuple[str, dict[str, Any]]] = {}
    seqs: list[int] = []
    for raw, aar in aars:
        seq = aar.get("seq")
        if not isinstance(seq, int):
            raise RuntimeError("AAR seq missing")
        by_seq[seq] = (raw, aar)
        seqs.append(seq)
    seqs = sorted(seqs)
    if seqs != list(range(seqs[0], seqs[0] + len(seqs))):
        raise RuntimeError("range discontinuity")

    checkpoints = sorted(checkpoints, key=lambda c: c.get("range", [10**18])[0])
    next_start = seqs[0]
    prev_cp_hash: str | None = None

    for cp in checkpoints:
        cp_range = cp.get("range")
        if not isinstance(cp_range, list) or len(cp_range) != 2:
            raise RuntimeError("checkpoint range missing")
        start, end = cp_range
        if not isinstance(start, int) or not isinstance(end, int) or start > end:
            raise RuntimeError("checkpoint range invalid")
        if start != next_start:
            raise RuntimeError("checkpoint range discontinuity")

        leaves: list[str] = []
        for seq in range(start, end + 1):
            rec = by_seq.get(seq)
            if rec is None:
                raise RuntimeError("checkpoint refers missing AAR")
            leaves.append(rec[0])

        if normalize_root(cp.get("merkle_root", "")) != merkle_root_mcp2(leaves):
            raise RuntimeError("merkle mismatch")

        if cp.get("prev_checkpoint_hash") != prev_cp_hash:
            raise RuntimeError("checkpoint linkage broken")

        sig = cp.get("signature")
        if not isinstance(sig, str):
            raise RuntimeError("checkpoint signature missing")

        cp_body = dict(cp)
        cp_body.pop("signature", None)
        cp_body.pop("checkpoint_sig", None)
        try:
            pub.verify(decode_signature(sig), canonical_json_bytes(cp_body))
        except InvalidSignature as e:
            raise RuntimeError("checkpoint signature invalid") from e

        prev_cp_hash = "sha256:" + sha256_hex(canonical_json_bytes(cp))
        next_start = end + 1

    if next_start != seqs[-1] + 1:
        raise RuntimeError("last AAR range not covered by checkpoints")

    return len(aars), len(checkpoints)


def detect_format(records: list[tuple[str, dict[str, Any]]]) -> str:
    has_v1_statement = any(obj.get("_record_type") == "statement" for _, obj in records)
    has_mcp2_aar = any(obj.get("type") == "AAR" for _, obj in records)
    if has_v1_statement:
        return "v1"
    if has_mcp2_aar:
        return "mcp2"
    raise RuntimeError("unknown journal format")


def load_bundle(path: str) -> tuple[bytes, bytes]:
    with zipfile.ZipFile(path, "r") as z:
        journal_bytes = z.read("journal.jsonl")
        pub_bytes = None
        for name in ("org_pubkey_ed25519.pem", "public.pem"):
            try:
                pub_bytes = z.read(name)
                break
            except KeyError:
                pass
        if pub_bytes is None:
            raise RuntimeError("missing public key in bundle (expected org_pubkey_ed25519.pem or public.pem)")
        return journal_bytes, pub_bytes


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python tools/verify_bundle.py <audit_bundle.zip>")
        return 2

    try:
        journal_bytes, pub_bytes = load_bundle(sys.argv[1])
        records: list[tuple[str, dict[str, Any]]] = []
        for lineno, raw in enumerate(journal_bytes.splitlines(), start=1):
            line = raw.decode("utf-8").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                raise RuntimeError(f"line {lineno}: invalid json: {e}") from e
            records.append((line, obj))

        pub = load_pubkey(pub_bytes)
        fmt = detect_format(records)
        if fmt == "v1":
            n_stmts, n_cps = verify_v1(records, pub)
        else:
            n_stmts, n_cps = verify_mcp2(records, pub)

        print("VERIFY_OK: bundle valid")
        print("FORMAT:", fmt, "STATEMENTS:", n_stmts, "CHECKPOINTS:", n_cps)
        return 0
    except Exception as e:
        print("VERIFY_FAIL:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
