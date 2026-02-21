#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jcs_canonical_bytes(obj: Any) -> bytes:
    # Minimal canonical JSON: sorted keys, no whitespace, utf-8
    # (RFC 8785 full JCS has more edge rules, but for our v1.0 receipts we keep it deterministic)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def merkle_root_hex(digests_hex: List[str]) -> str:
    # digests_hex: list of hex strings (already sha256 outputs)
    if not digests_hex:
        return sha256_hex(b"")
    level = [bytes.fromhex(h) for h in digests_hex]
    while len(level) > 1:
        nxt: List[bytes] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            nxt.append(hashlib.sha256(left + right).digest())
        level = nxt
    return level[0].hex()


@dataclass
class Statement:
    obj: Dict[str, Any]
    digest_hex: str


@dataclass
class Checkpoint:
    obj: Dict[str, Any]
    start: int
    end: int
    merkle_root_hex: str
    signature_b64_or_hex: str | None


def compute_statement_digest_hex(statement_obj: Dict[str, Any]) -> str:
    # signature input excludes attestations & checkpoint; also exclude internal fields
    obj = dict(statement_obj)
    obj.pop("attestations", None)
    obj.pop("checkpoint", None)
    obj.pop("_digest", None)
    obj.pop("_record_type", None)
    return sha256_hex(jcs_canonical_bytes(obj))


def parse_journal_lines(journal_bytes: bytes) -> Tuple[List[Statement], List[Checkpoint]]:
    stmts: List[Statement] = []
    cps: List[Checkpoint] = []

    for lineno, raw in enumerate(journal_bytes.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"line {lineno}: invalid json: {e}") from e

        rtype = obj.get("_record_type") or obj.get("type")  # tolerate both
        if rtype in ("statement", "AAR"):
            digest = obj.get("_digest")
            if not digest or not isinstance(digest, str) or not digest.startswith("sha256:"):
                raise RuntimeError(f"line {lineno}: missing _digest sha256:...")

            computed = "sha256:" + compute_statement_digest_hex(obj)
            if digest != computed:
                raise RuntimeError(f"line {lineno}: digest mismatch stored={digest} computed={computed}")

            stmts.append(Statement(obj=obj, digest_hex=digest.split("sha256:", 1)[1]))

        elif rtype in ("checkpoint", "CHECKPOINT"):
            start = obj.get("range_start_seq")
            end = obj.get("range_end_seq")
            root = obj.get("merkle_root")
            sig = obj.get("signature") or obj.get("checkpoint_sig")
            if not isinstance(start, int) or not isinstance(end, int):
                raise RuntimeError(f"line {lineno}: checkpoint missing range")
            if not isinstance(root, str) or not root.startswith("sha256:"):
                raise RuntimeError(f"line {lineno}: checkpoint missing merkle_root sha256:...")
            cps.append(
                Checkpoint(
                    obj=obj,
                    start=start,
                    end=end,
                    merkle_root_hex=root.split("sha256:", 1)[1],
                    signature_b64_or_hex=sig,
                )
            )
        else:
            raise RuntimeError(f"line {lineno}: unknown record type: {rtype}")

    return stmts, cps


def verify_chain(stmts: List[Statement], cps: List[Checkpoint], pub: Ed25519PublicKey) -> None:
    if not stmts:
        raise RuntimeError("no statements")
    if not cps:
        raise RuntimeError("no checkpoints")

    # Verify seq continuity + prev_digest chain
    # We accept seq starting at 0 or 1; use first seq as base.
    first_seq = stmts[0].obj.get("trace_context", {}).get("sequence_no")
    if not isinstance(first_seq, int):
        raise RuntimeError("first statement missing trace_context.sequence_no")
    expected_seq = first_seq
    prev = stmts[0].obj.get("trace_context", {}).get("prev_digest")
    # first prev_digest may be null/empty; we only enforce from second statement
    for i, s in enumerate(stmts):
        tc = s.obj.get("trace_context", {})
        seq = tc.get("sequence_no")
        if seq != expected_seq:
            raise RuntimeError(f"range discontinuity: expected seq={expected_seq} got={seq}")
        if i > 0:
            pd = tc.get("prev_digest")
            expected_prev = "sha256:" + stmts[i - 1].digest_hex
            if pd != expected_prev:
                raise RuntimeError(f"prev_digest mismatch at seq={seq}: got={pd} expected={expected_prev}")
        expected_seq += 1

    # Verify each checkpoint covers exact contiguous ranges and merkle roots match
    stmt_by_seq: Dict[int, Statement] = {}
    for s in stmts:
        seq = s.obj["trace_context"]["sequence_no"]
        stmt_by_seq[seq] = s

    cps_sorted = sorted(cps, key=lambda c: c.start)
    covered_end = None
    for cp in cps_sorted:
        if cp.start > cp.end:
            raise RuntimeError(f"checkpoint invalid range {cp.start}..{cp.end}")
        # ranges must be contiguous across checkpoints
        if covered_end is None:
            pass
        else:
            if cp.start != covered_end + 1:
                raise RuntimeError(f"checkpoint range discontinuity: prev_end={covered_end} next_start={cp.start}")
        # gather digests for range
        digests: List[str] = []
        for seq in range(cp.start, cp.end + 1):
            if seq not in stmt_by_seq:
                raise RuntimeError(f"checkpoint refers to missing statement seq={seq}")
            digests.append(stmt_by_seq[seq].digest_hex)
        computed_root = merkle_root_hex(digests)
        if computed_root != cp.merkle_root_hex:
            raise RuntimeError(f"merkle mismatch for range {cp.start}..{cp.end}")
        # verify checkpoint signature: sign over canonical checkpoint body WITHOUT signature field
        if not cp.signature_b64_or_hex:
            raise RuntimeError(f"checkpoint missing signature for range {cp.start}..{cp.end}")

        cp_body = dict(cp.obj)
        cp_body.pop("signature", None)
        cp_body.pop("checkpoint_sig", None)

        msg = jcs_canonical_bytes(cp_body)

        # signature format: accept hex or base64url-ish; here we try hex first then base64
        sig_bytes = None
        sgn = cp.signature_b64_or_hex
        if isinstance(sgn, str):
            try:
                sig_bytes = bytes.fromhex(sgn)
            except Exception:
                # try base64 (standard)
                import base64
                try:
                    sig_bytes = base64.b64decode(sgn + "==")
                except Exception as e:
                    raise RuntimeError(f"invalid signature encoding for range {cp.start}..{cp.end}: {e}") from e

        try:
            pub.verify(sig_bytes, msg)
        except InvalidSignature as e:
            raise RuntimeError(f"checkpoint signature invalid for range {cp.start}..{cp.end}") from e

        covered_end = cp.end


def load_pubkey(pem_bytes: bytes) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(pem_bytes)
    if not isinstance(key, Ed25519PublicKey):
        raise RuntimeError("public key is not Ed25519")
    return key


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python tools/verify_bundle.py <audit_bundle.zip>")
        return 2
    bundle_path = sys.argv[1]
    with zipfile.ZipFile(bundle_path, "r") as z:
        # required files
        try:
            journal_bytes = z.read("journal.jsonl")
            pub_bytes = z.read("org_pubkey_ed25519.pem")
        except KeyError as e:
            print("VERIFY_FAIL: missing required file in bundle:", e)
            return 1

    pub = load_pubkey(pub_bytes)
    stmts, cps = parse_journal_lines(journal_bytes)
    verify_chain(stmts, cps, pub)
    print("VERIFY_OK: bundle valid")
    print("STATEMENTS:", len(stmts), "CHECKPOINTS:", len(cps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
