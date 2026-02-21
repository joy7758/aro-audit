from __future__ import annotations
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sdk.journal.jsonl_journal import JSONLJournal, JournalConfig
from sdk.keys.org_keys import load_or_create_keypair
from cryptography.hazmat.primitives import serialization

PRIVKEY_PATH = os.path.join("demo", "out", "org_subkey_ed25519.pem")
PUBKEY_PATH = os.path.join("demo", "out", "org_pubkey_ed25519.pem")

def make_statement(i: int) -> dict:
    return {
        "_type": "https://aro-audit.org/statement/v1.0",
        "trace_context": {"trace_id": "trace-demo-001"},
        "subjects": [{"name": f"file://demo/{i}.txt", "digest": {"sha256": f"deadbeef{i}"}}],
        "predicateType": "https://aro-audit.org/predicate/action/v1.0",
        "predicate": {
            "invocation": {"tool": "mcp://filesystem/write_file", "parameters_hash": f"sha256:params{i}"},
            "policy_eval": {"decision": "ALLOW", "triggered_rules": []},
            "result": {"status": "OK", "result_digest": f"sha256:res{i}", "rollback": {"state": "NOT_AVAILABLE"}},
        },
        "attestations": [],
    }

def main() -> int:
    out_path = os.path.join("demo", "out", "journal.jsonl")
    if os.path.exists(out_path):
        os.remove(out_path)
    j = JSONLJournal(JournalConfig(path=out_path, checkpoint_every=4, org_subkey_path=PRIVKEY_PATH))
    for i in range(10):
        j.append_statement(make_statement(i))
    j.close()
    kp = load_or_create_keypair(PRIVKEY_PATH)
    pub_pem = kp.pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open(PUBKEY_PATH, "wb") as f:
        f.write(pub_pem)
    print("WROTE:", out_path)
    print("WROTE:", PUBKEY_PATH)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
