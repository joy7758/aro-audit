import hashlib
import json
import re
import sys
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from sdk.canonical.jcs import dumps as jcs_dumps

VERSION_RE = re.compile(r"^AAR-MCP-(\d+)\.(\d+)$")
SUPPORTED_MAJOR = 2
RECORD_AAR = "AAR"
RECORD_CHECKPOINT = "CHECKPOINT"
MAX_JSONL_LINE_CHARS = 1024 * 1024


class VerificationError(RuntimeError):
    """Raised when chain verification fails due to invalid input or structure."""


@dataclass(frozen=True)
class AAREntry:
    lineno: int
    raw: str
    obj: dict[str, Any]


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


def _load_public_key(pubkey_path: str) -> Ed25519PublicKey:
    try:
        with open(pubkey_path, "rb") as fh:
            key = serialization.load_pem_public_key(fh.read())
    except OSError as exc:
        raise VerificationError(f"Failed to read public key: {exc}") from exc
    except (TypeError, ValueError) as exc:
        raise VerificationError(f"Failed to parse public key: {exc}") from exc

    if not isinstance(key, Ed25519PublicKey):
        raise VerificationError("Public key must be Ed25519")
    return key


def _read_raw_lines(path: str) -> list[tuple[int, str]]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return [
                (lineno, line.rstrip("\n"))
                for lineno, line in enumerate(fh, start=1)
                if line.strip()
            ]
    except OSError as exc:
        raise VerificationError(f"Failed to read journal: {exc}") from exc


def _parse_json_record(lineno: int, raw: str) -> dict[str, Any]:
    if len(raw) > MAX_JSONL_LINE_CHARS:
        raise VerificationError(
            f"Line too large at line {lineno}: {len(raw)} chars > {MAX_JSONL_LINE_CHARS}"
        )
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"Invalid JSON at line {lineno}: {exc}") from exc

    if not isinstance(obj, dict):
        raise VerificationError(f"Invalid JSON object at line {lineno}: expected object")
    return obj


def _segment_for_checkpoint(
    *,
    start: int,
    end: int,
    checkpoint_line_no: int,
    aars_by_seq: dict[int, AAREntry],
) -> list[str]:
    segment: list[str] = []
    for seq in range(start, end + 1):
        entry = aars_by_seq.get(seq)
        if entry is None or entry.lineno >= checkpoint_line_no:
            raise VerificationError("Range mismatch")
        segment.append(entry.raw)
    return segment


def _verify_checkpoint_signature(
    *,
    checkpoint: dict[str, Any],
    signature_hex: str,
    public_key: Ed25519PublicKey,
) -> None:
    payload = dict(checkpoint)
    payload.pop("signature", None)
    to_verify = canonical_json_bytes(payload)
    try:
        public_key.verify(bytes.fromhex(signature_hex), to_verify)
    except (InvalidSignature, ValueError) as exc:
        raise VerificationError("Invalid signature") from exc


def verify_chain(path: str, pubkey_path: str) -> int:
    try:
        public_key = _load_public_key(pubkey_path)
        raw_lines = _read_raw_lines(path)

        if not raw_lines:
            return fail("Empty journal")

        aars_by_seq: dict[int, AAREntry] = {}
        checkpoints: list[tuple[int, dict[str, Any]]] = []
        for lineno, raw in raw_lines:
            obj = _parse_json_record(lineno, raw)
            record_type = obj.get("type")

            if not check_version(obj.get("version")):
                raise VerificationError("Unsupported protocol major version")

            if record_type == RECORD_AAR:
                seq = obj.get("seq")
                if not isinstance(seq, int):
                    raise VerificationError(f"Invalid AAR seq at line {lineno}")
                if seq in aars_by_seq:
                    raise VerificationError(f"Duplicate AAR seq {seq} at line {lineno}")
                aars_by_seq[seq] = AAREntry(lineno=lineno, raw=raw, obj=obj)
            elif record_type == RECORD_CHECKPOINT:
                checkpoints.append((lineno, obj))
            else:
                raise VerificationError(f"Unknown record type at line {lineno}: {record_type!r}")

        if not aars_by_seq:
            raise VerificationError("No AAR found")

        ordered_seqs = sorted(aars_by_seq.keys())
        if ordered_seqs[0] != 0:
            raise VerificationError(f"First AAR seq expected 0, got {ordered_seqs[0]}")
        if ordered_seqs != list(range(len(ordered_seqs))):
            raise VerificationError("AAR sequence not contiguous")

        if not checkpoints:
            raise VerificationError("No CHECKPOINT found")

        prev_hash_expected: str | None = None
        next_expected_start = 0

        for checkpoint_line_no, checkpoint in checkpoints:
            cp_range = checkpoint.get("range")
            signature_hex = checkpoint.get("signature")
            if not isinstance(cp_range, list) or len(cp_range) != 2:
                raise VerificationError("Range mismatch")
            if not isinstance(signature_hex, str):
                raise VerificationError("Invalid signature")

            start, end = cp_range
            if not isinstance(start, int) or not isinstance(end, int) or start > end:
                raise VerificationError("Range mismatch")
            if start != next_expected_start:
                raise VerificationError("Range discontinuity")

            segment = _segment_for_checkpoint(
                start=start,
                end=end,
                checkpoint_line_no=checkpoint_line_no,
                aars_by_seq=aars_by_seq,
            )
            root = merkle_root(segment)
            if root != checkpoint.get("merkle_root"):
                raise VerificationError("Merkle mismatch")

            if checkpoint.get("prev_checkpoint_hash") != prev_hash_expected:
                raise VerificationError("Checkpoint linkage broken")

            _verify_checkpoint_signature(
                checkpoint=checkpoint,
                signature_hex=signature_hex,
                public_key=public_key,
            )

            prev_hash_expected = checkpoint_hash(checkpoint)
            next_expected_start = end + 1

        if next_expected_start != len(ordered_seqs):
            raise VerificationError("Last AAR range not covered by checkpoints")
    except VerificationError as exc:
        return fail(str(exc))

    print("VERIFY_OK: full chain valid")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: verify_chain <journal> <pubkey>")
        return 1
    return verify_chain(argv[1], argv[2])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
