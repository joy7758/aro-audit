from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
from pathlib import Path

@dataclass
class DependencyDecision:
    ok: bool
    code: str
    message: str


def get_latest_checkpoint_root(journal_path: str) -> Optional[str]:
    p = Path(journal_path)
    if not p.exists():
        return None
    last_root: Optional[str] = None
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

def _get(d: Dict[str, Any], path: str, default=None):
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def resolve_mode(policy: Dict[str, Any], tool_name: str) -> str:
    dep = (policy or {}).get("dependency") or {}
    tools = dep.get("tools") or {}
    mode = tools.get(tool_name) or dep.get("default") or "soft"
    if mode not in ("soft", "strict", "off"):
        mode = "soft"
    return mode

def hard_gate_enabled(policy: Dict[str, Any]) -> bool:
    dep = (policy or {}).get("dependency") or {}
    return bool(dep.get("hard_gate", False))

def check_dependency(
    *,
    required_checkpoint_root: Optional[str],
    current_checkpoint_root: Optional[str],
    tool_name: str,
    policy: Dict[str, Any],
) -> DependencyDecision:
    mode = resolve_mode(policy, tool_name)

    # off: 永不拦截
    if mode == "off":
        return DependencyDecision(True, "ok", "dependency check disabled")

    # strict: 必须对齐
    if mode == "strict":
        if not current_checkpoint_root:
            # 没有 checkpoint 的链，strict 默认不允许高风险执行
            return DependencyDecision(False, "no-checkpoint", "strict mode requires an existing checkpoint")
        if not required_checkpoint_root:
            # Hard Gate：命中 strict 的工具必须携带 required root
            if hard_gate_enabled(policy):
                return DependencyDecision(False, "missing-required-root", "hard gate: required_checkpoint_root is mandatory for this tool")
            # 非 hard_gate 时，旧行为可选：当作不匹配拒绝
            return DependencyDecision(False, "missing-required-root", "strict mode: required_checkpoint_root missing")
        if required_checkpoint_root != current_checkpoint_root:
            return DependencyDecision(False, "root-mismatch", f"checkpoint root mismatch: required={required_checkpoint_root} current={current_checkpoint_root}")
        return DependencyDecision(True, "ok", "strict dependency satisfied")

    # soft: 有 root 才检查；没 root 放行
    if not required_checkpoint_root:
        return DependencyDecision(True, "soft-allow", "soft mode: no required root provided")
    if not current_checkpoint_root:
        return DependencyDecision(True, "soft-allow", "soft mode: no checkpoint yet")
    if required_checkpoint_root != current_checkpoint_root:
        return DependencyDecision(False, "root-mismatch", f"checkpoint root mismatch: required={required_checkpoint_root} current={current_checkpoint_root}")
    return DependencyDecision(True, "ok", "soft dependency satisfied")
