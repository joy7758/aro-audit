import sys
import json
import subprocess
import threading
import hashlib
import argparse
import signal
import os
from pathlib import Path
from datetime import datetime, UTC
import yaml
from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig

PROTOCOL_VERSION = "AAR-MCP-1.0"
RUNNING = True

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_policy(policy_path):
    with open(policy_path) as f:
        return yaml.safe_load(f)

def safe_flush(file_obj):
    file_obj.flush()
    os.fsync(file_obj.fileno())

def write_aar(journal, tool_name, args):
    statement = {
        "version": PROTOCOL_VERSION,
        "type": "AAR",
        "tool": tool_name,
        "args": args,
        "timestamp": datetime.now(UTC).isoformat()
    }
    journal.append_statement(statement)
    safe_flush(journal._file)

def write_checkpoint(journal_path, journal):
    path = Path(journal_path)
    if not path.exists():
        return

    with open(path, "rb") as f:
        content = f.read()

    checkpoint = {
        "version": PROTOCOL_VERSION,
        "type": "CHECKPOINT",
        "digest": sha256(content),
        "size": path.stat().st_size,
        "timestamp": datetime.now(UTC).isoformat()
    }

    journal.append_statement(checkpoint)
    safe_flush(journal._file)

def send_error_response(req_id, message):
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32000,
            "message": message
        }
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()

def handle_sigint(signum, frame):
    global RUNNING
    RUNNING = False

def main():
    signal.signal(signal.SIGINT, handle_sigint)

    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default="config/mcp_policy.yaml")
    parser.add_argument("--journal", default="demo/out/journal.jsonl")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.command:
        print("Usage: mcp-aar [--policy file] [--journal path] <real_mcp_server_command>", file=sys.stderr)
        sys.exit(1)

    policy = load_policy(args.policy)

    HIGH_RISK_TOOLS = set(policy.get("high_risk_tools", []))
    FAIL_CLOSED = policy.get("fail_closed", True)
    AUTO_CHECKPOINT = policy.get("auto_checkpoint", True)

    journal_path = args.journal
    journal = JSONLJournal(JournalConfig(path=journal_path))

    proc = subprocess.Popen(
        args.command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        bufsize=0
    )

    def read_from_client():
        while RUNNING:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                message = json.loads(line)

                if message.get("method") == "call_tool":
                    params = message.get("params", {})
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    req_id = message.get("id")

                    if tool_name in HIGH_RISK_TOOLS:
                        try:
                            write_aar(journal, tool_name, tool_args)
                            if AUTO_CHECKPOINT:
                                write_checkpoint(journal_path, journal)
                        except Exception as e:
                            if FAIL_CLOSED:
                                send_error_response(req_id, f"AAR enforcement failed: {e}")
                                continue

                proc.stdin.write((json.dumps(message) + "\n").encode())
                proc.stdin.flush()

            except Exception as e:
                print(f"Wrapper error: {e}", file=sys.stderr)

        try:
            proc.stdin.close()
        except:
            pass

    t1 = threading.Thread(target=read_from_client)
    t1.daemon = True
    t1.start()

    for line in iter(proc.stdout.readline, b""):
        if not RUNNING:
            break
        sys.stdout.buffer.write(line)
        sys.stdout.flush()

    proc.terminate()

if __name__ == "__main__":
    main()
