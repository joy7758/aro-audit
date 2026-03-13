"""Validation helpers for the portable audit evidence object."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "schema" / "evidence.schema.json"
REQUIRED_FIELDS = [
    "agent_id",
    "persona_id",
    "interaction_trace",
    "policy_decisions",
    "execution_hash",
    "timestamp",
    "tool_calls",
    "result_summary",
]
_HEX64 = re.compile(r"^[a-f0-9]{64}$")


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_execution_hash(payload: dict[str, Any]) -> str:
    material = {
        "interaction_trace": payload.get("interaction_trace", []),
        "policy_decisions": payload.get("policy_decisions", []),
        "tool_calls": payload.get("tool_calls", []),
        "result_summary": payload.get("result_summary", ""),
    }
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def build_evidence_object(
    *,
    agent_id: str,
    persona_id: str,
    interaction_trace: list[dict[str, Any]],
    policy_decisions: list[dict[str, Any]],
    tool_calls: list[dict[str, Any]],
    result_summary: str,
    timestamp: str | None = None,
    execution_hash: str | None = None,
) -> dict[str, Any]:
    payload = {
        "agent_id": agent_id,
        "persona_id": persona_id,
        "interaction_trace": interaction_trace,
        "policy_decisions": policy_decisions,
        "tool_calls": tool_calls,
        "result_summary": result_summary,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    }
    payload["execution_hash"] = execution_hash or compute_execution_hash(payload)
    return payload


def estimate_reconstruction_time(payload: dict[str, Any]) -> float:
    trace_len = len(payload.get("interaction_trace", []))
    decision_len = len(payload.get("policy_decisions", []))
    tool_len = len(payload.get("tool_calls", []))
    return round(3.0 + trace_len * 0.35 + decision_len * 0.45 + tool_len * 0.55, 2)


def summarize_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    tool_names = [str(call.get("tool", "unknown")) for call in payload.get("tool_calls", [])]
    return {
        "agent_id": payload.get("agent_id"),
        "persona_id": payload.get("persona_id"),
        "tool_count": len(tool_names),
        "tools": tool_names,
        "policy_decision_count": len(payload.get("policy_decisions", [])),
        "audit_reconstruction_time": estimate_reconstruction_time(payload),
    }


def _validate_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_evidence_data(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return False, ["payload must be a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")

    if errors:
        return False, errors

    for field in ("agent_id", "persona_id", "result_summary"):
        if not isinstance(payload.get(field), str) or not str(payload.get(field)).strip():
            errors.append(f"{field} must be a non-empty string")

    for field in ("interaction_trace", "policy_decisions", "tool_calls"):
        if not isinstance(payload.get(field), list):
            errors.append(f"{field} must be an array")

    execution_hash = payload.get("execution_hash")
    if not isinstance(execution_hash, str) or not _HEX64.fullmatch(execution_hash):
        errors.append("execution_hash must be a 64-character lowercase sha256 hex string")

    if _validate_timestamp(payload.get("timestamp")) is False:
        errors.append("timestamp must be an ISO 8601 datetime string")

    if isinstance(payload.get("interaction_trace"), list):
        persona_id = payload.get("persona_id")
        for index, item in enumerate(payload["interaction_trace"]):
            if not isinstance(item, dict):
                errors.append(f"interaction_trace[{index}] must be an object")
                continue
            trace_persona = item.get("persona_id")
            if trace_persona is not None and trace_persona != persona_id:
                errors.append(
                    f"interaction_trace[{index}] persona_id mismatch: {trace_persona} != {persona_id}"
                )

    if not errors and execution_hash != compute_execution_hash(payload):
        errors.append("execution_hash does not match the trace, policy, tool, and result content")

    return len(errors) == 0, errors


def validate_evidence(file: str | Path) -> bool:
    path = Path(file)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL")
        print(f"file not found: {path}")
        return False
    except json.JSONDecodeError as exc:
        print("FAIL")
        print(f"invalid json: {exc}")
        return False

    ok, errors = validate_evidence_data(payload)
    if ok:
        print("PASS")
        return True

    print("FAIL")
    for error in errors:
        print(error)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an ARO Audit evidence object.")
    parser.add_argument("file", help="Path to evidence JSON file")
    args = parser.parse_args()
    return 0 if validate_evidence(args.file) else 1


if __name__ == "__main__":
    sys.exit(main())
