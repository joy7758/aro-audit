import json
import hashlib
import sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

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

def verify_chain(path, pubkey_path):
    with open(pubkey_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    aars = []
    checkpoints = []

    for line in lines:
        obj = json.loads(line)
        if obj["type"] == "AAR":
            aars.append((line, obj))
        elif obj["type"] == "CHECKPOINT":
            checkpoints.append(obj)

    if not aars:
        print("No AAR found")
        return 1

    # 验证 seq 连续性
    expected_seq = 0
    for _, aar in aars:
        if aar["seq"] != expected_seq:
            print("Range discontinuity")
            return 1
        expected_seq += 1

    if not checkpoints:
        print("No CHECKPOINT found")
        return 1

    # 验证 checkpoint
    prev_hash = None
    for cp in checkpoints:
        start, end = cp["range"]

        if start != 0 or end != len(aars)-1:
            print("Range mismatch")
            return 1

        # 计算 merkle
        leaves = [line for line, _ in aars]
        root = merkle_root(leaves)
        if root != cp["merkle_root"]:
            print("Merkle mismatch")
            return 1

        # 验证签名
        signature = bytes.fromhex(cp["signature"])
        payload = cp.copy()
        del payload["signature"]
        data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

        try:
            public_key.verify(signature, data)
        except InvalidSignature:
            print("Invalid signature")
            return 1

        # 验证 prev hash
        cp_hash = sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
        if prev_hash is not None and cp["prev_checkpoint_hash"] != prev_hash:
            print("Checkpoint linkage broken")
            return 1

        prev_hash = cp_hash

    print("VERIFY_OK: full chain valid")
    return 0

if __name__ == "__main__":
    sys.exit(verify_chain(sys.argv[1], sys.argv[2]))
