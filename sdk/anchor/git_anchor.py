import json
import subprocess
import hashlib
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def anchor_checkpoint(journal_path):
    path = Path(journal_path)
    if not path.exists():
        return None

    lines = path.read_text().splitlines()

    last_checkpoint = None
    for line in reversed(lines):
        obj = json.loads(line)
        if obj.get("type") == "CHECKPOINT":
            last_checkpoint = obj
            break

    if not last_checkpoint:
        return None

    checkpoint_hash = sha256(
        json.dumps(last_checkpoint, sort_keys=True).encode()
    )

    anchor_file = Path("anchor.log")
    anchor_file.write_text(checkpoint_hash + "\n")

    subprocess.run(["git", "add", "anchor.log"])
    subprocess.run(["git", "commit", "-m", f"anchor: {checkpoint_hash}"])
    subprocess.run(["git", "push"])

    return checkpoint_hash
