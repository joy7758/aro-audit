from validator import build_evidence_object, validate_evidence_data


def test_policy_enforcement_decision_is_captured() -> None:
    evidence = build_evidence_object(
        agent_id="conformance-agent",
        persona_id="policy-locked",
        interaction_trace=[
            {
                "step": 1,
                "persona_id": "policy-locked",
                "content": "Write the report to a restricted path.",
            }
        ],
        policy_decisions=[
            {
                "decision": "deny",
                "target": "write_file",
                "reason": "restricted_tool",
            }
        ],
        tool_calls=[],
        result_summary="The agent refused the restricted tool call.",
    )
    ok, errors = validate_evidence_data(evidence)
    assert ok, errors
    assert evidence["policy_decisions"][0]["decision"] == "deny"

