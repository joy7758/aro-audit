#!/usr/bin/env python3
from __future__ import annotations

import os, sys, json, hashlib
from typing import Any, Dict, List, Optional

# 关键：把项目根加入 sys.path，保证 from sdk... 永远可用
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from sdk.keys.org_keys import verify as verify_sig

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def jcs_bytes(obj: Dict[str, Any]) -> bytes:
    return rfc8785.dumps(obj)

def compute_digest(statement: Dict[str, Any]) -> str:
    s = dict(statement)
    for k in ("attestations", "checkpoint", "_digest", "_record_type"):
        s.pop(k, None)
    canonical = jcs_bytes(s)
    return "sha256:" + sha256_hex(canonical)

def merkle_root(digests: List[str]) -> str:
    if not digests:
        return "sha256:" + sha256_hex(b"")
    level = [d.encode("utf-8") for d in digests]
    while len(level) > 1:
        nxt: List[bytes] = []
        i = 0
        while i < len(level):
            left = level[i]
            right = level[i+1] if i+1 < len(level) else left
            nxt.append(hashlib.sha256(left + b"|" + right).digest())
            i += 2
        level = nxt
    return "sha256:" + level[0].hex()

def load_pubkey_from_priv(path: str) -> Ed25519PublicKey:
    data = open(path, "rb").read()
    priv = serialization.load_pem_private_key(data, password=None)
    pub = priv.public_key()
    assert isinstance(pub, Ed25519PublicKey)
    return pub

def checkpoint_message(start: int, end: int, root: str, store_fp: str, key_fp: str) -> bytes:
    msg_obj = {
        "range_start_seq": start,
        "range_end_seq": end,
        "merkle_root": root,
        "store_fingerprint": store_fp,
        "key_fingerprint": key_fp,
    }
    return jcs_bytes(msg_obj)

def fail(msg: str) -> int:
    print("VERIFY_FAIL:", msg)
    return 1

def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python sdk/verify/verify.py <journal.jsonl> <org_subkey_ed25519.pem>")
        return 2

    path = sys.argv[1]
    key_path = sys.argv[2]
    pub = load_pubkey_from_priv(key_path)

    prev: Optional[str] = None
    seq_expected = 0
    window_start: Optional[int] = None
    window_digests: List[str] = []

    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rtype = obj.get("_record_type")

            if rtype == "statement":
                tc = obj.get("trace_context", {})
                seq = tc.get("sequence_no")
                prev_digest = tc.get("prev_digest")
                if seq != seq_expected:
                    return fail(f"line {lineno}: sequence_no expected {seq_expected}, got {seq}")
                if prev_digest != prev:
                    return fail(f"line {lineno}: prev_digest mismatch. expected {prev}, got {prev_digest}")

                digest = compute_digest(obj)
                stored = obj.get("_digest")
                if stored != digest:
                    return fail(f"line {lineno}: digest mismatch. stored {stored}, computed {digest}")

                if window_start is None:
                    window_start = seq
                window_digests.append(digest)

                prev = digest
                seq_expected += 1

            elif rtype == "checkpoint":
                start = obj.get("range_start_seq")
                end = obj.get("range_end_seq")
                root = obj.get("merkle_root")
                store_fp = obj.get("store_fingerprint")
                sig_hex = obj.get("checkpoint_sig")
                key_fp = obj.get("key_fingerprint")

                if window_start is None:
                    return fail(f"line {lineno}: checkpoint but no pending window")
                if start != window_start or end != (seq_expected - 1):
                    return fail(f"line {lineno}: checkpoint range mismatch. got {start}..{end}, expected {window_start}..{seq_expected-1}")

                computed_root = merkle_root(window_digests)
                if root != computed_root:
                    return fail(f"line {lineno}: merkle_root mismatch. stored {root}, computed {computed_root}")

                if store_fp is None or sig_hex is None or key_fp is None:
                    return fail(f"line {lineno}: checkpoint missing store_fingerprint/checkpoint_sig/key_fingerprint")

                msg = checkpoint_message(start, end, root, store_fp, key_fp)
                if not verify_sig(pub, msg, sig_hex):
                    return fail(f"line {lineno}: checkpoint_sig verify failed")

                window_start = None
                window_digests = []

            else:
                return fail(f"line {lineno}: unknown _record_type: {rtype}")

    print("VERIFY_OK:", path, "statements=", seq_expected)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
