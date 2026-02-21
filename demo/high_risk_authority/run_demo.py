import json
import hashlib
import os
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

JOURNAL_PATH = "journal.jsonl"
PRIVKEY_PATH = "private.pem"
PUBKEY_PATH = "public.pem"

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def merkle_root(leaves):
    nodes = [sha256_hex(l.encode()) for l in leaves]
    if not nodes:
        return None
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        new_level = []
        for i in range(0, len(nodes), 2):
            combined = (nodes[i] + nodes[i+1]).encode()
            new_level.append(sha256_hex(combined))
        nodes = new_level
    return nodes[0]

def generate_keys():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    with open(PRIVKEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    os.chmod(PRIVKEY_PATH, 0o600)

    with open(PUBKEY_PATH, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    return private_key

def main():
    # 生成密钥
    private_key = generate_keys()

    # 清空旧 journal
    open(JOURNAL_PATH, "w").close()

    # 构造 AAR
    aar = {
        "version": "AAR-MCP-2.0",
        "type": "AAR",
        "seq": 0,
        "tool": "transfer_funds",
        "args": {
            "from": "corp_account",
            "to": "vendor_account",
            "amount": 100000
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    aar_line = canonical_json(aar)
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(aar_line + "\n")

    root = merkle_root([aar_line])

    checkpoint = {
        "version": "AAR-MCP-2.0",
        "type": "CHECKPOINT",
        "range": [0, 0],
        "merkle_root": root,
        "prev_checkpoint_hash": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    payload = canonical_json(checkpoint).encode()
    signature = private_key.sign(payload).hex()
    checkpoint["signature"] = signature

    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(canonical_json(checkpoint) + "\n")

    print("High-risk action recorded.")
    print("Amount transferred: 100000")
    print("Journal:", JOURNAL_PATH)
    print("Public key:", PUBKEY_PATH)

if __name__ == "__main__":
    main()
