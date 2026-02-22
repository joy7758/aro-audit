# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sdk.canonical.jcs import dumps as jcs_dumps
from sdk.verify.verify_chain import merkle_root, verify_chain


def _write_pubkey(path: Path, private_key: Ed25519PrivateKey) -> None:
    path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _build_aar(seq: int) -> dict[str, object]:
    return {
        "version": "AAR-MCP-2.0",
        "type": "AAR",
        "seq": seq,
        "tool": "write_file",
        "args": {"path": f"/tmp/{seq}.txt"},
        "timestamp": "2026-02-22T00:00:00Z",
    }


def _build_checkpoint(aar_lines: list[str], private_key: Ed25519PrivateKey, start: int, end: int) -> dict[str, object]:
    payload: dict[str, object] = {
        "version": "AAR-MCP-2.0",
        "type": "CHECKPOINT",
        "range": [start, end],
        "merkle_root": merkle_root(aar_lines),
        "prev_checkpoint_hash": None,
        "timestamp": "2026-02-22T00:00:01Z",
    }
    payload["signature"] = private_key.sign(jcs_dumps(payload)).hex()
    return payload


def _write_journal(path: Path, records: list[dict[str, object]]) -> None:
    lines = [jcs_dumps(rec).decode("utf-8") for rec in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_verify_chain_rejects_unknown_record_type(tmp_path: Path, capsys) -> None:
    private_key = Ed25519PrivateKey.generate()
    pubkey_path = tmp_path / "pub.pem"
    _write_pubkey(pubkey_path, private_key)

    aar = _build_aar(0)
    aar_line = jcs_dumps(aar).decode("utf-8")
    cp = _build_checkpoint([aar_line], private_key, 0, 0)
    unknown = {"version": "AAR-MCP-2.0", "type": "NOTE", "msg": "x"}

    journal = tmp_path / "journal.jsonl"
    _write_journal(journal, [aar, unknown, cp])

    rc = verify_chain(str(journal), str(pubkey_path))
    out = capsys.readouterr().out
    assert rc == 1
    assert "Unknown record type" in out


def test_verify_chain_rejects_duplicate_seq(tmp_path: Path, capsys) -> None:
    private_key = Ed25519PrivateKey.generate()
    pubkey_path = tmp_path / "pub.pem"
    _write_pubkey(pubkey_path, private_key)

    aar0 = _build_aar(0)
    aar_dup = _build_aar(0)
    line0 = jcs_dumps(aar0).decode("utf-8")
    cp = _build_checkpoint([line0], private_key, 0, 0)

    journal = tmp_path / "journal.jsonl"
    _write_journal(journal, [aar0, aar_dup, cp])

    rc = verify_chain(str(journal), str(pubkey_path))
    out = capsys.readouterr().out
    assert rc == 1
    assert "Duplicate AAR seq" in out


def test_verify_chain_rejects_last_range_not_covered(tmp_path: Path, capsys) -> None:
    private_key = Ed25519PrivateKey.generate()
    pubkey_path = tmp_path / "pub.pem"
    _write_pubkey(pubkey_path, private_key)

    aar0 = _build_aar(0)
    aar1 = _build_aar(1)
    line0 = jcs_dumps(aar0).decode("utf-8")
    cp = _build_checkpoint([line0], private_key, 0, 0)

    journal = tmp_path / "journal.jsonl"
    _write_journal(journal, [aar0, aar1, cp])

    rc = verify_chain(str(journal), str(pubkey_path))
    out = capsys.readouterr().out
    assert rc == 1
    assert "Last AAR range not covered by checkpoints" in out


def test_verify_chain_requires_first_seq_zero(tmp_path: Path, capsys) -> None:
    private_key = Ed25519PrivateKey.generate()
    pubkey_path = tmp_path / "pub.pem"
    _write_pubkey(pubkey_path, private_key)

    aar1 = _build_aar(1)
    aar_line = jcs_dumps(aar1).decode("utf-8")
    cp = _build_checkpoint([aar_line], private_key, 1, 1)

    journal = tmp_path / "journal.jsonl"
    _write_journal(journal, [aar1, cp])

    rc = verify_chain(str(journal), str(pubkey_path))
    out = capsys.readouterr().out
    assert rc == 1
    assert "First AAR seq expected 0, got 1" in out
