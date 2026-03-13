"""Example CrewAI integration that emits and validates an evidence object."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins.crewai_audit_plugin import CrewAIAuditPlugin
from validator import validate_evidence


def main() -> None:
    crew_execution = {
        "persona_id": "crew-finance-ops",
        "tasks": [
            {
                "agent": "researcher",
                "persona_id": "crew-finance-ops",
                "prompt": "Search procurement policy updates.",
                "response": "Dual approval is still required for purchases above the threshold.",
                "tool_calls": [
                    {
                        "tool": "web_search",
                        "status": "success",
                    }
                ],
            },
            {
                "agent": "reviewer",
                "persona_id": "crew-finance-ops",
                "prompt": "Check whether a finance review is required.",
                "response": "Finance review remains mandatory.",
                "tool_calls": [
                    {
                        "tool": "policy_lookup",
                        "status": "success",
                    }
                ],
            },
        ],
        "policy_decisions": [
            {
                "decision": "allow",
                "target": "web_search",
                "reason": "public_research",
            }
        ],
        "result_summary": "CrewAI run completed with two tasks and one governance decision.",
    }

    plugin = CrewAIAuditPlugin(
        agent_id="crewai-demo",
        persona_id="crew-finance-ops",
    )
    evidence = plugin.generate_evidence_object(crew_execution)

    output_path = Path(__file__).resolve().with_name("crewai_evidence_demo.json")
    output_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    validate_evidence(output_path)


if __name__ == "__main__":
    main()
