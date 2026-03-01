# SPDX-License-Identifier: MIT
# Copyright (c) 2026 joy7758 contributors
from __future__ import annotations

from aro_audit.vpml.scorer import VPMLEdge, VPMLNode, VPMLScorer


def _build_scorer() -> VPMLScorer:
    nodes = {
        "src": VPMLNode(
            id="src",
            type="Agent",
            attrs={
                "trust": {"assurance": 0.2},
                "obs": {"coverage": 0.4},
            },
        ),
        "dst": VPMLNode(
            id="dst",
            type="DomainAsset",
            attrs={
                "asset": {"criticality": 0.8, "blast_radius": 80.0},
                "trust": {"assurance": 0.6},
                "obs": {"coverage": 0.7},
            },
        ),
    }
    edges = [
        VPMLEdge(
            src="src",
            dst="dst",
            type="DataFlowEdge",
            attrs={"edge": {"assurance": 0.4, "mediation": 0.3, "observability": 0.5, "latency": 20}},
        )
    ]
    return VPMLScorer(nodes=nodes, edges=edges)


def test_cascading_probability_detects_simple_path() -> None:
    scorer = _build_scorer()
    cp, top_paths = scorer.cascading_probability("dst", sources=["src"], max_depth=2, top_k_paths=3)

    assert cp > 0.0
    assert cp <= 1.0
    assert top_paths
    assert top_paths[0][1] == ["src", "dst"]


def test_cascading_probability_respects_allowed_edge_types() -> None:
    scorer = _build_scorer()
    cp, top_paths = scorer.cascading_probability(
        "dst",
        sources=["src"],
        max_depth=2,
        allowed_edge_types=["TrustEdge"],
    )

    assert cp == 0.0
    assert top_paths == []


def test_sci_contains_domain_contribution_and_meta() -> None:
    scorer = _build_scorer()
    result = scorer.sci(
        domain_nodes=["dst"],
        sources=["src"],
        max_depth=3,
        max_paths=50,
        top_k_paths=2,
    )

    assert "SCI" in result
    assert result["SCI"] > 0.0
    assert result["nodes"]["dst"]["contribution"] > 0.0
    assert result["meta"]["max_depth"] == 3
    assert result["meta"]["max_paths"] == 50
