from validator import build_evidence_object, validate_evidence_data


def test_persona_consistency_mismatch_fails() -> None:
    evidence = build_evidence_object(
        agent_id="conformance-agent",
        persona_id="locked-persona",
        interaction_trace=[
            {
                "step": 1,
                "persona_id": "locked-persona",
                "content": "Answer in the approved persona.",
            },
            {
                "step": 2,
                "persona_id": "drifted-persona",
                "content": "Now switch personas without approval.",
            }
        ],
        policy_decisions=[
            {
                "decision": "deny",
                "target": "persona_switch",
                "reason": "persona_lock",
            }
        ],
        tool_calls=[],
        result_summary="The interaction trace contains a persona mismatch.",
    )
    ok, errors = validate_evidence_data(evidence)
    assert not ok
    assert any("persona_id mismatch" in error for error in errors)

