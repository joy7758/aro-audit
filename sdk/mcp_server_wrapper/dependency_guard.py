import json
from pathlib import Path

def get_latest_checkpoint_root(journal_path: str):
    p = Path(journal_path)
    if not p.exists():
        return None
    last_root = None
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") == "CHECKPOINT":
                last_root = obj.get("merkle_root")
    return last_root

def check_dependency(incoming: dict, journal_path: str, risk_level: str, mode: str = "soft"):
    # only high-risk enforced
    if risk_level != "high":
        return True, None

    mode = (mode or "soft").lower()
    required = incoming.get("required_checkpoint_root")
    latest = get_latest_checkpoint_root(journal_path)

    # no checkpoint yet
    if latest is None:
        if mode == "strict":
            return False, "No previous checkpoint found (strict-deny)."
        return True, "No previous checkpoint found (soft-allow)."

    # missing required root
    if required is None:
        if mode == "strict":
            return False, "Missing required_checkpoint_root (strict-deny)."
        return True, "Missing required_checkpoint_root (soft-allow)."

    # mismatch
    if required != latest:
        return False, f"Checkpoint root mismatch. expected={latest}, got={required}"

    return True, None
