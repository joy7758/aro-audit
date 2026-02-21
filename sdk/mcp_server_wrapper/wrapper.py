import sys
import json
import subprocess
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, UTC
import yaml
from cryptography.hazmat.primitives import serialization
from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig

PROTOCOL_VERSION = "AAR-MCP-2.0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def merkle_root(lines):
    hashes = [sha256(l.encode()) for l in lines]
    if not hashes:
        return None

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            sha256((hashes[i] + hashes[i+1]).encode())
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]


def load_policy(policy_path):
    with open(policy_path) as f:
        return yaml.safe_load(f)


def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def get_last_checkpoint_info(lines):
    for i in reversed(range(len(lines))):
        obj = json.loads(lines[i])
        if obj.get("type") == "CHECKPOINT":
            return i, obj
    return None, None


def write_aar(journal, tool_name, args):
    statement = {
        "version": PROTOCOL_VERSION,
        "type": "AAR",
        "tool": tool_name,
        "args": args,
        "timestamp": datetime.now(UTC).isoformat()
    }
    journal.append_statement(statement)
    journal.flush()


def write_checkpoint_segmented(journal_path, journal, private_key):
    path = Path(journal_path)
    lines = path.read_text().splitlines()

    last_cp_index, last_cp = get_last_checkpoint_info(lines)

    if last_cp is None:
        start_seq = 1
        prev_hash = None
        segment_lines = lines
    else:
        start_seq = last_cp.get("range")[1] + 1
        prev_hash = sha256(json.dumps(last_cp, sort_keys=True).encode())
        segment_lines = lines[last_cp_index+1:]

    if not segment_lines:
        return

    end_seq = start_seq + len(segment_lines) - 1
    root = merkle_root(segment_lines)

    payload = {
        "version": PROTOCOL_VERSION,
        "type": "CHECKPOINT",
        "range": [start_seq, end_seq],
        "merkle_root": root,
        "prev_checkpoint_hash": prev_hash,
        "timestamp": datetime.now(UTC).isoformat()
    }

    signature = private_key.sign(
        json.dumps(payload, sort_keys=True).encode()
    )

    payload["signature"] = signature.hex()

    journal.append_statement(payload)
    journal.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="config/mcp_policy.yaml")
    parser.add_argument("--journal", default="demo/out/journal.jsonl")
    parser.add_argument("--key", default="demo/out/org_subkey_ed25519.pem")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.command:
        print("Usage: mcp-aar <real_mcp_server_command>")
        sys.exit(1)

    policy = load_policy(args.policy)
    HIGH_RISK_TOOLS = set(policy.get("high_risk_tools", []))
    AUTO_CHECKPOINT = policy.get("auto_checkpoint", True)

    journal = JSONLJournal(JournalConfig(path=args.journal))
    private_key = load_private_key(args.key)

    proc = subprocess.Popen(
        args.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        bufsize=0
    )

    for line in sys.stdin:
        message = json.loads(line)

        if message.get("method") == "call_tool":
            tool_name = message.get("params", {}).get("name")
            tool_args = message.get("params", {}).get("arguments", {})

            if tool_name in HIGH_RISK_TOOLS:
                write_aar(journal, tool_name, tool_args)
                if AUTO_CHECKPOINT:
                    write_checkpoint_segmented(args.journal, journal, private_key)

        proc.stdin.write((json.dumps(message) + "\n").encode())
        proc.stdin.flush()

    proc.terminate()


if __name__ == "__main__":
    main()
