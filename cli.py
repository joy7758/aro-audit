from __future__ import annotations

import argparse
import json
import sys
import os

# Ensure we can import from the package even if running as script
try:
    from aro_audit.vpml.scorer import VPMLScorer
    from aro_audit.vpml import explainer, viz
except ImportError:
    # Fix: Go up 3 levels (aro_audit/vpml/cli.py -> repo_root) to ensure package resolution
    REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from aro_audit.vpml.scorer import VPMLScorer
    from aro_audit.vpml import explainer, viz

def main() -> None:
    ap = argparse.ArgumentParser(
        description="ARO-Audit VPML Scorer v0.1 (Risk Propagation & SCI)",
        prog="python -m aro_audit.vpml.cli"
    )
    ap.add_argument("--graph", required=True, help="Path to VPML YAML graph file")
    ap.add_argument("--domain", required=True, help="Comma-separated domain node IDs (Assets)")
    ap.add_argument("--sources", default="", help="Comma-separated source node IDs (Threat Origins)")
    ap.add_argument("--max-depth", type=int, default=5, help="Max propagation depth")
    ap.add_argument("--max-paths", type=int, default=1000, help="Max paths to enumerate per pair (circuit breaker)")
    ap.add_argument("--top-k", type=int, default=5, help="Top contributing paths to explain")
    ap.add_argument("--edge-types", default="TrustEdge,PrivilegeEdge,ExecFlowEdge,DataFlowEdge", help="Filter: Comma-separated allowed edge types")
    ap.add_argument("--pretty", action="store_true", help="Format output as pretty JSON")
    
    # New arguments
    ap.add_argument("--explain", action="store_true", help="Generate natural language explanation (CISO report)")
    ap.add_argument("--json-out", help="Path to save JSON output (Audit Trail)")
    ap.add_argument("--dot", help="Path to export Graphviz DOT file (Risk Heatmap)")
    ap.add_argument("--dot-title", default="VPML Risk Propagation Graph", help="Title for the DOT graph")

    args = ap.parse_args()

    try:
        scorer = VPMLScorer.from_yaml(args.graph)
    except FileNotFoundError:
        print(f"Error: Graph file not found: {args.graph}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading graph: {e}", file=sys.stderr)
        sys.exit(1)

    domain_nodes = [x.strip() for x in args.domain.split(",") if x.strip()]
    sources = [x.strip() for x in args.sources.split(",") if x.strip()] or None
    allowed_edge_types = [x.strip() for x in args.edge_types.split(",") if x.strip()] or None

    result = scorer.sci(
        domain_nodes=domain_nodes,
        sources=sources,
        max_depth=args.max_depth,
        max_paths=args.max_paths,
        top_k_paths=args.top_k,
        allowed_edge_types=allowed_edge_types,
    )

    # 1. JSON Output (Standard)
    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

    # 1.1 JSON File Output (Audit Trail)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    # 2. Explanation Output (Optional)
    if args.explain:
        print("\n" + "="*60, file=sys.stderr)
        print("VPML RISK EXPLANATION REPORT", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        
        explanations = explainer.explain_sci_result(
            scorer, 
            result, 
            top_k_paths=args.top_k
        )
        text = explainer.render_explanations_text(explanations)
        print(text, file=sys.stderr)

    # 3. DOT Output (Optional)
    if args.dot:
        dot_content = viz.to_dot(scorer, result, title=args.dot_title)
        viz.save_dot(args.dot, dot_content)
        print(f"\n[+] Graphviz DOT saved to: {args.dot}", file=sys.stderr)

if __name__ == "__main__":
    main()