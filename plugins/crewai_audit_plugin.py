"""Minimal CrewAI audit plugin that emits portable evidence objects."""

from __future__ import annotations

from typing import Any

from validator import build_evidence_object


def capture_crew_execution_trace(crew_execution: dict[str, Any]) -> dict[str, Any]:
    tasks = list(crew_execution.get("tasks", []))
    interaction_trace: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []

    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            continue
        agent_name = str(task.get("agent", "unknown-agent"))
        persona_id = str(task.get("persona_id", crew_execution.get("persona_id", "crew-persona")))
        prompt = str(task.get("prompt", ""))
        interaction_trace.append(
            {
                "step": index,
                "agent": agent_name,
                "persona_id": persona_id,
                "prompt": prompt,
                "response": str(task.get("response", "")),
            }
        )

        for call in task.get("tool_calls", []):
            if isinstance(call, dict):
                normalized_call = dict(call)
                normalized_call.setdefault("agent", agent_name)
                tool_calls.append(normalized_call)

    policy_decisions = list(crew_execution.get("policy_decisions", []))
    if not policy_decisions:
        policy_decisions.append(
            {
                "decision": "observe",
                "reason": "crewai_trace_capture",
            }
        )

    return {
        "interaction_trace": interaction_trace,
        "policy_decisions": policy_decisions,
        "tool_calls": tool_calls,
        "result_summary": str(
            crew_execution.get(
                "result_summary",
                crew_execution.get("final_output", "Crew execution completed."),
            )
        ),
    }


def generate_evidence_object(
    crew_execution: dict[str, Any],
    *,
    agent_id: str,
    persona_id: str,
) -> dict[str, Any]:
    trace = capture_crew_execution_trace(crew_execution)
    return build_evidence_object(
        agent_id=agent_id,
        persona_id=persona_id,
        interaction_trace=trace["interaction_trace"],
        policy_decisions=trace["policy_decisions"],
        tool_calls=trace["tool_calls"],
        result_summary=trace["result_summary"],
    )


class CrewAIAuditPlugin:
    """Convenience wrapper for CrewAI integrations."""

    def __init__(self, *, agent_id: str, persona_id: str) -> None:
        self.agent_id = agent_id
        self.persona_id = persona_id

    def capture_crew_execution_trace(self, crew_execution: dict[str, Any]) -> dict[str, Any]:
        return capture_crew_execution_trace(crew_execution)

    def generate_evidence_object(self, crew_execution: dict[str, Any]) -> dict[str, Any]:
        return generate_evidence_object(
            crew_execution,
            agent_id=self.agent_id,
            persona_id=self.persona_id,
        )
