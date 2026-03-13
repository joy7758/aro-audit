from validator import build_evidence_object, summarize_evidence, validate_evidence_data


def test_evidence_generation_passes_validation() -> None:
    evidence = build_evidence_object(
        agent_id="conformance-agent",
        persona_id="evidence-analyst",
        interaction_trace=[
            {
                "step": 1,
                "persona_id": "evidence-analyst",
                "content": "Search the approval matrix.",
            }
        ],
        policy_decisions=[
            {
                "decision": "allow",
                "target": "web_search",
                "reason": "public_lookup",
            }
        ],
        tool_calls=[
            {
                "tool": "web_search",
                "status": "success",
            }
        ],
        result_summary="An evidence object was generated for the governed run.",
    )
    ok, errors = validate_evidence_data(evidence)
    assert ok, errors
    summary = summarize_evidence(evidence)
    assert summary["tool_count"] == 1
    assert summary["audit_reconstruction_time"] > 0

