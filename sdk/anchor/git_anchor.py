import hashlib
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path
from typing import Any


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def anchor_checkpoint(journal_path: str, anchor_path: str = "anchor.log", push: bool = True):
    path = Path(journal_path)
    if not path.exists():
        return None

    lines = path.read_text(encoding="utf-8").splitlines()

    last_checkpoint = None
    for line in reversed(lines):
        obj = json.loads(line)
        if obj.get("type") == "CHECKPOINT":
            last_checkpoint = obj
            break

    if not last_checkpoint:
        return None

    checkpoint_hash = "sha256:" + sha256(canonical_json(last_checkpoint).encode("utf-8"))
    ts = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    anchor_file = Path(anchor_path)
    anchor_file.parent.mkdir(parents=True, exist_ok=True)
    with open(anchor_file, "a", encoding="utf-8") as fh:
        fh.write(f"{ts} {checkpoint_hash}\n")

    subprocess.run(["git", "add", str(anchor_file)], check=True)
    commit_msg = f"anchor: {checkpoint_hash}"
    commit = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        check=False,
        capture_output=True,
        text=True,
    )
    if commit.returncode == 0 and push:
        subprocess.run(["git", "push"], check=True)

    return checkpoint_hash
