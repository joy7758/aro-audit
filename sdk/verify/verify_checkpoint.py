import sys
import json
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization


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
            sha256((hashes[i] + hashes[i + 1]).encode())
            for i in range(0, len(hashes), 2)
        ]

    return hashes[0]


def main():
    if len(sys.argv) != 3:
        print("Usage: verify_checkpoint <journal.jsonl> <org_pubkey.pem>")
        sys.exit(1)

    journal_path = Path(sys.argv[1])
    pubkey_path = Path(sys.argv[2])

    if not journal_path.exists():
        print("Journal not found")
        sys.exit(1)

    if not pubkey_path.exists():
        print("Public key not found")
        sys.exit(1)

    lines = journal_path.read_text().splitlines()
    checkpoint = None
    checkpoint_index = None

    for i in reversed(range(len(lines))):
        obj = json.loads(lines[i])
        if obj.get("type") == "CHECKPOINT":
            checkpoint = obj
            checkpoint_index = i
            break

    if not checkpoint:
        print("No CHECKPOINT found")
        sys.exit(1)

    data_lines = lines[:checkpoint_index]

    computed_root = merkle_root(data_lines)
    stored_root = checkpoint.get("merkle_root")

    if computed_root != stored_root:
        print("VERIFY_FAIL: Merkle root mismatch")
        sys.exit(1)

    with open(pubkey_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    signature = bytes.fromhex(checkpoint.get("signature"))

    payload = {
        "version": checkpoint.get("version"),
        "type": checkpoint.get("type"),
        "range": checkpoint.get("range"),
        "merkle_root": checkpoint.get("merkle_root"),
        "timestamp": checkpoint.get("timestamp"),
    }

    try:
        public_key.verify(
            signature,
            json.dumps(payload, sort_keys=True).encode()
        )
    except Exception:
        print("VERIFY_FAIL: Signature invalid")
        sys.exit(1)

    print("VERIFY_OK: checkpoint valid")
    sys.exit(0)


if __name__ == "__main__":
    main()
