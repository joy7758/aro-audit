from __future__ import annotations
import json
import os
import time
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

import rfc8785
from sdk.keys.org_keys import load_or_create_keypair, pubkey_fingerprint, sign

def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _now_ms() -> int:
    return int(time.time() * 1000)

def _jcs_bytes(obj: Dict[str, Any]) -> bytes:
    return rfc8785.dumps(obj)

def compute_statement_digest(statement: Dict[str, Any]) -> str:
    s = dict(statement)
    s.pop("attestations", None)
    s.pop("checkpoint", None)
    s.pop("_digest", None)
    s.pop("_record_type", None)
    canonical = _jcs_bytes(s)
    return "sha256:" + _sha256_hex(canonical)

def merkle_root(digests: List[str]) -> str:
    if not digests:
        return "sha256:" + _sha256_hex(b"")
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

@dataclass
class JournalConfig:
    path: str
    checkpoint_every: int = 256
    org_subkey_path: str = "demo/out/org_subkey_ed25519.pem"

class JSONLJournal:
    def __init__(self, cfg: JournalConfig):
        self.cfg = cfg
        os.makedirs(os.path.dirname(cfg.path) or ".", exist_ok=True)
        self._fh = open(cfg.path, "a", buffering=1, encoding="utf-8")
        self._seq = 0
        self._prev_digest: Optional[str] = None
        self._pending_digests: List[str] = []
        self._range_start_seq: Optional[int] = None

        kp = load_or_create_keypair(cfg.org_subkey_path)
        self._priv = kp.priv
        self._pub_fp = pubkey_fingerprint(kp.pub)

    def append_statement(self, statement: Dict[str, Any]) -> Dict[str, Any]:
        tc = statement.setdefault("trace_context", {})
        tc.setdefault("sequence_no", self._seq)
        tc.setdefault("timestamp_ms", _now_ms())
        tc.setdefault("prev_digest", self._prev_digest)

        digest = compute_statement_digest(statement)
        statement["_record_type"] = "statement"
        statement["_digest"] = digest

        self._fh.write(json.dumps(statement, ensure_ascii=False) + "\n")

        if self._range_start_seq is None:
            self._range_start_seq = self._seq
        self._pending_digests.append(digest)
        self._prev_digest = digest
        self._seq += 1

        if (self._seq % self.cfg.checkpoint_every) == 0:
            self._append_checkpoint()

        return {"digest": digest, "sequence_no": tc["sequence_no"]}

    def _store_fingerprint(self) -> str:
        self._fh.flush()
        data = open(self.cfg.path, "rb").read()
        return "sha256:" + _sha256_hex(data)

    def _checkpoint_message(self, start: int, end: int, root: str, store_fp: str) -> bytes:
        # 固定可复现签名输入：JCS + sha256 前，先直接对 JCS bytes 签名（Ed25519）
        msg_obj = {
            "range_start_seq": start,
            "range_end_seq": end,
            "merkle_root": root,
            "store_fingerprint": store_fp,
            "key_fingerprint": self._pub_fp,
        }
        return _jcs_bytes(msg_obj)

    def _append_checkpoint(self) -> None:
        if self._range_start_seq is None or not self._pending_digests:
            return
        start = self._range_start_seq
        end = self._seq - 1
        root = merkle_root(self._pending_digests)
        store_fp = self._store_fingerprint()

        msg = self._checkpoint_message(start, end, root, store_fp)
        sig_hex = sign(self._priv, msg)

        ck = {
            "_record_type": "checkpoint",
            "range_start_seq": start,
            "range_end_seq": end,
            "merkle_root": root,
            "store_fingerprint": store_fp,
            "checkpoint_sig": sig_hex,
            "key_fingerprint": self._pub_fp,
            "timestamp_ms": _now_ms(),
        }
        self._fh.write(json.dumps(ck, ensure_ascii=False) + "\n")

        self._pending_digests = []
        self._range_start_seq = None

    def close(self) -> None:
        if self._pending_digests:
            self._append_checkpoint()
        self._fh.close()
