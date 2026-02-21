import argparse
import hashlib
import json
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives import serialization

from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig

PROTOCOL_VERSION = "AAR-MCP-2.0"
TOOL_CALL_METHODS = {"tools/call", "call_tool"}
SENSITIVE_KEYS = {"password", "passwd", "token", "secret", "api_key", "authorization"}


@dataclass
class JournalState:
    next_seq: int = 0
    next_segment_start: int = 0
    prev_checkpoint_hash: str | None = None
    pending_aar_lines: list[str] = field(default_factory=list)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_json(obj: Any) -> str:
    return "sha256:" + sha256_hex(canonical_json(obj).encode("utf-8"))


def checkpoint_hash(checkpoint_obj: dict[str, Any]) -> str:
    return "sha256:" + sha256_hex(canonical_json(checkpoint_obj).encode("utf-8"))


def merkle_root(lines: list[str]) -> str | None:
    hashes = [sha256_hex(line.encode("utf-8")) for line in lines]
    if not hashes:
        return None
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            sha256_hex((hashes[i] + hashes[i + 1]).encode("utf-8"))
            for i in range(0, len(hashes), 2)
        ]
    return hashes[0]


def load_policy(policy_path: str) -> dict[str, Any]:
    with open(policy_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_private_key(path: str):
    with open(path, "rb") as fh:
        return serialization.load_pem_private_key(fh.read(), password=None)


def sanitize_args(args: Any) -> dict[str, Any]:
    if not isinstance(args, dict):
        return {"_args_hash": hash_json(args)}

    redacted: dict[str, Any] = {}
    for key, value in args.items():
        key_s = str(key)
        key_lower = key_s.lower()
        if key_lower in SENSITIVE_KEYS:
            redacted[key_s] = {"redacted": True, "hash": hash_json(value)}
            continue
        # Keep simple scalar telemetry, hash everything else to avoid plaintext leakage.
        if isinstance(value, (bool, int, float)) or value is None:
            redacted[key_s] = value
        else:
            redacted[key_s] = {"hash": hash_json(value)}
    return redacted


def load_journal_state(journal_path: str) -> JournalState:
    path = Path(journal_path)
    if not path.exists():
        return JournalState()

    aars: dict[int, str] = {}
    checkpoints: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        obj = json.loads(raw)
        if obj.get("type") == "AAR":
            seq = obj.get("seq")
            if not isinstance(seq, int):
                raise ValueError("AAR seq must be int")
            aars[seq] = raw.strip()
        elif obj.get("type") == "CHECKPOINT":
            checkpoints.append(obj)

    seqs = sorted(aars.keys())
    if seqs and seqs != list(range(len(seqs))):
        raise ValueError("existing journal has non-contiguous AAR seq")

    next_seq = len(seqs)
    if checkpoints:
        last_cp = checkpoints[-1]
        cp_range = last_cp.get("range")
        if not isinstance(cp_range, list) or len(cp_range) != 2:
            raise ValueError("checkpoint range must be [start, end]")
        start_seq = int(cp_range[1]) + 1
        prev_cp_hash = checkpoint_hash(last_cp)
    else:
        start_seq = 0
        prev_cp_hash = None

    pending = [aars[seq] for seq in range(start_seq, next_seq) if seq in aars]
    return JournalState(
        next_seq=next_seq,
        next_segment_start=start_seq,
        prev_checkpoint_hash=prev_cp_hash,
        pending_aar_lines=pending,
    )


def write_aar(journal: JSONLJournal, state: JournalState, tool_name: str, tool_args: Any) -> None:
    statement = {
        "version": PROTOCOL_VERSION,
        "type": "AAR",
        "seq": state.next_seq,
        "tool": tool_name,
        "args": sanitize_args(tool_args),
        "args_hash": hash_json(tool_args),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    line = journal.append_statement(statement)
    journal.flush()

    state.pending_aar_lines.append(line)
    state.next_seq += 1


def write_checkpoint_segmented(
    journal: JSONLJournal,
    state: JournalState,
    private_key,
) -> None:
    if not state.pending_aar_lines:
        return

    start_seq = state.next_segment_start
    end_seq = start_seq + len(state.pending_aar_lines) - 1
    root = merkle_root(state.pending_aar_lines)
    if root is None:
        return

    payload = {
        "version": PROTOCOL_VERSION,
        "type": "CHECKPOINT",
        "range": [start_seq, end_seq],
        "merkle_root": root,
        "prev_checkpoint_hash": state.prev_checkpoint_hash,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    signature = private_key.sign(canonical_json(payload).encode("utf-8")).hex()
    checkpoint = dict(payload)
    checkpoint["signature"] = signature

    journal.append_statement(checkpoint)
    journal.flush()

    state.prev_checkpoint_hash = checkpoint_hash(checkpoint)
    state.next_segment_start = end_seq + 1
    state.pending_aar_lines.clear()


def send_error_response(req_id: Any, message: str) -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32000, "message": message},
    }
    sys.stdout.write(canonical_json(payload) + "\n")
    sys.stdout.flush()


def extract_tool_call(message: dict[str, Any]) -> tuple[str | None, Any] | None:
    method = message.get("method")
    if method not in TOOL_CALL_METHODS:
        return None
    params = message.get("params", {})
    if not isinstance(params, dict):
        return None
    return params.get("name"), params.get("arguments", {})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="config/mcp_policy.yaml")
    parser.add_argument("--journal", default="demo/out/journal.jsonl")
    parser.add_argument("--key", default="demo/out/org_subkey_ed25519.pem")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.command:
        print("Usage: mcp-aar [--policy file] [--journal file] [--key pem] <real_mcp_server_command>", file=sys.stderr)
        return 1

    policy = load_policy(args.policy)
    high_risk_tools = set(policy.get("high_risk_tools", []))
    auto_checkpoint = bool(policy.get("auto_checkpoint", True))
    fail_closed = bool(policy.get("fail_closed", True))

    try:
        journal = JSONLJournal(JournalConfig(path=args.journal))
        state = load_journal_state(args.journal)
        private_key = load_private_key(args.key)
    except Exception as exc:
        print(f"Failed to initialize evidence engine: {exc}", file=sys.stderr)
        return 1

    proc = subprocess.Popen(
        args.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        bufsize=0,
    )

    def read_from_client() -> None:
        try:
            for raw in sys.stdin:
                line = raw.strip()
                if not line:
                    continue
                try:
                    message = json.loads(line)
                except Exception as exc:  # pragma: no cover - defensive path
                    if fail_closed:
                        send_error_response(None, f"Invalid JSON-RPC payload: {exc}")
                    continue

                req_id = message.get("id")
                tool_call = extract_tool_call(message)
                if tool_call:
                    tool_name, tool_args = tool_call
                    if tool_name in high_risk_tools:
                        try:
                            write_aar(journal, state, tool_name, tool_args)
                            if auto_checkpoint:
                                write_checkpoint_segmented(journal, state, private_key)
                        except Exception as exc:
                            if fail_closed:
                                send_error_response(req_id, f"AAR enforcement failed: {exc}")
                                continue

                if proc.stdin is None:
                    break
                proc.stdin.write((canonical_json(message) + "\n").encode("utf-8"))
                proc.stdin.flush()
        finally:
            if proc.stdin:
                proc.stdin.close()

    t = threading.Thread(target=read_from_client, daemon=True)
    t.start()

    if proc.stdout is not None:
        for out_line in iter(proc.stdout.readline, b""):
            sys.stdout.buffer.write(out_line)
            sys.stdout.flush()

    rc = proc.wait()
    t.join(timeout=1)
    journal.close()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
