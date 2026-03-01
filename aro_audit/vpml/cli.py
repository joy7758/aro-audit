from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


def _resolve_repo_root(start_dir: Optional[str] = None) -> str:
    """
    Best-effort resolve repository root.
    Priority:
    1) Search upward for pyproject.toml from start_dir (or this file's directory)
    2) Search upward from current working directory
    3) Fall back to absolute start_dir / cwd
    """

    def _scan_upward(origin: str) -> Optional[str]:
        cur = os.path.abspath(origin)
        for _ in range(8):
            if os.path.isfile(os.path.join(cur, "pyproject.toml")):
                return cur
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
        return None

    base = start_dir or os.path.dirname(__file__)
    found = _scan_upward(base)
    if found:
        return found

    found = _scan_upward(os.getcwd())
    if found:
        return found

    return os.path.abspath(base)


try:
    from aro_audit.vpml.scorer import VPMLScorer
    from aro_audit.vpml import explainer, viz
except ImportError:
    REPO_ROOT = _resolve_repo_root()
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from aro_audit.vpml.scorer import VPMLScorer
    from aro_audit.vpml import explainer, viz


def _read_repo_version(repo_root: str) -> str:
    """
    Best-effort parse version from pyproject.toml.
    """
    import re

    path = os.path.join(repo_root, "pyproject.toml")
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        m = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', txt, re.M)
        return m.group(1) if m else "unknown"
    except Exception:
        return "unknown"


def _read_git_hash(repo_root: str) -> str:
    """
    Best-effort get git short hash.
    """
    import subprocess

    try:
        r = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip() or "nogit"
    except Exception:
        return "nogit"


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_repro_footer(
    *,
    utc: str,
    version: str,
    git_hash: str,
    graph: str,
    domain: str,
    sources: str,
    max_depth: int,
    max_paths: int,
    top_k: int,
    edge_types: str,
) -> str:
    return (
        "\n---\n"
        "## Reproducibility / 可追溯信息\n\n"
        f"- UTC: `{utc}`\n"
        f"- Version: `{version}`\n"
        f"- Git: `{git_hash}`\n"
        f"- Graph: `{graph}`\n"
        f"- Domain: `{domain}`\n"
        f"- Sources: `{sources}`\n"
        f"- MaxDepth: `{max_depth}`\n"
        f"- MaxPaths: `{max_paths}`\n"
        f"- TopK: `{top_k}`\n"
        f"- EdgeTypes: `{edge_types}`\n"
    )


def _load_summary_text(path: str) -> str:
    if not path:
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def _summary_block(summary_txt: str) -> str:
    if not summary_txt:
        return ""
    return "\n\n### SUMMARY.txt\n\n```text\n" + summary_txt + "\n```\n"


def _sanitize_bundle_name(name: str) -> str:
    safe = name.replace(":", "-").strip()
    safe = "".join(ch if (ch.isalnum() or ch in ("-", "_", ".")) else "-" for ch in safe)
    safe = safe.strip("-_.")
    return safe or "vpml_bundle"


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_manifest(
    bundle_path: str,
    metadata: Dict[str, Any],
    file_names: Iterable[str],
) -> str:
    entries: List[Dict[str, Any]] = []
    for name in file_names:
        p = os.path.join(bundle_path, name)
        if not os.path.isfile(p):
            continue
        try:
            entries.append(
                {
                    "name": name,
                    "bytes": os.path.getsize(p),
                    "sha256": _sha256_file(p),
                }
            )
        except Exception:
            continue

    entries = sorted(entries, key=lambda x: x["name"])
    manifest = dict(metadata)
    manifest["files"] = entries
    manifest_path = os.path.join(bundle_path, "MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest_path


def _build_report_markdown(
    *,
    report_title: str,
    graph_path: str,
    domain_nodes: Iterable[str],
    sources: Optional[Iterable[str]],
    sci_result: Dict[str, Any],
    explanations: Dict[str, Any],
    top_assets: int = 3,
    top_paths: int = 3,
) -> str:
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    nodes = sci_result.get("nodes", {}) if isinstance(sci_result, dict) else {}
    sci = float(sci_result.get("SCI", 0.0)) if isinstance(sci_result, dict) else 0.0

    ranked_assets = sorted(
        ((asset_id, item) for asset_id, item in nodes.items() if isinstance(item, dict)),
        key=lambda kv: float(kv[1].get("contribution", 0.0)),
        reverse=True,
    )
    top_ranked = ranked_assets[: max(0, int(top_assets))]

    lines: List[str] = []
    lines.append(f"# {report_title}")
    lines.append("")
    lines.append(f"- Generated At: `{generated_at}`")
    lines.append(f"- Graph: `{graph_path}`")
    lines.append(f"- Domain Nodes: `{','.join(domain_nodes)}`")
    lines.append(f"- Source Nodes: `{','.join(sources) if sources else '(all)'}`")
    lines.append(f"- SCI: `{sci:.6f}`")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    if not top_ranked:
        lines.append("No domain asset results were produced.")
    else:
        lines.append("Top contributors by `contribution`:")
        lines.append("")
        for idx, (asset_id, item) in enumerate(top_ranked, start=1):
            cp = float(item.get("cp", 0.0))
            contribution = float(item.get("contribution", 0.0))
            criticality = float(item.get("criticality", 0.0))
            blast_radius = float(item.get("blast_radius", 0.0))
            lines.append(
                f"{idx}. `{asset_id}`: contribution `{contribution:.6f}`, CP `{cp:.6f}`, "
                f"criticality `{criticality:.3f}`, blast radius `{blast_radius:.1f}`"
            )

    lines.append("")
    lines.append("## Propagation Evidence")
    lines.append("")
    if not top_ranked:
        lines.append("No propagation paths available.")
    else:
        for asset_id, item in top_ranked:
            lines.append(f"### {asset_id}")
            top_path_rows = (item.get("top_paths") or [])[: max(0, int(top_paths))]
            if not top_path_rows:
                lines.append("- No top paths captured.")
                lines.append("")
                continue
            for rank, row in enumerate(top_path_rows, start=1):
                try:
                    p = float(row[0])
                    node_path = row[1]
                except Exception:
                    p = 0.0
                    node_path = []
                path_str = " -> ".join(str(x) for x in node_path) if isinstance(node_path, list) else str(node_path)
                lines.append(f"- Path {rank}: `P={p:.6f}` | `{path_str}`")
            lines.append("")

    lines.append("## Control Priorities")
    lines.append("")
    if not top_ranked:
        lines.append("No control priorities available.")
    else:
        for asset_id, _ in top_ranked:
            lines.append(f"### {asset_id}")
            ex = explanations.get(asset_id)
            control_lines = getattr(ex, "control_priorities", []) if ex is not None else []
            if not control_lines:
                lines.append("- No control priorities generated.")
                lines.append("")
                continue
            for row in control_lines:
                lines.append(f"- {row}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="ARO-Audit VPML Scorer v0.1 (Risk Propagation & SCI)",
        prog="python -m aro_audit.vpml.cli",
    )
    ap.add_argument("--graph", required=True, help="Path to VPML YAML graph file")
    ap.add_argument("--domain", required=True, help="Comma-separated domain node IDs (Assets)")
    ap.add_argument("--sources", default="", help="Comma-separated source node IDs (Threat Origins)")
    ap.add_argument("--max-depth", type=int, default=5, help="Max propagation depth")
    ap.add_argument("--max-paths", type=int, default=1000, help="Max paths to enumerate per source (circuit breaker)")
    ap.add_argument("--top-k", type=int, default=5, help="Top contributing paths to explain")
    ap.add_argument(
        "--edge-types",
        default="TrustEdge,PrivilegeEdge,ExecFlowEdge,DataFlowEdge",
        help="Filter: Comma-separated allowed edge types",
    )

    ap.add_argument("--pretty", action="store_true", help="Format output as pretty JSON")
    ap.add_argument("--explain", action="store_true", help="Generate natural language explanation (CISO report)")
    ap.add_argument("--json-out", help="Path to save JSON output (Audit Trail)")
    ap.add_argument("--report-md", help="Path to save Markdown report (Executive + Evidence + Controls)")
    ap.add_argument("--report-title", default="VPML SCI Report", help="Title for the Markdown report")
    ap.add_argument("--summary-file", default="", help="Optional path to artifacts/SUMMARY.txt to append into report")
    ap.add_argument("--bundle-dir", default="", help="Optional output directory for audit bundle")
    ap.add_argument("--bundle-name", default="", help="Optional bundle folder name")
    ap.add_argument("--dot", help="Path to export Graphviz DOT file (Risk Heatmap)")
    ap.add_argument("--dot-title", default="VPML Risk Propagation Graph", help="Title for the DOT graph")

    args = ap.parse_args()
    repo_root = _resolve_repo_root()
    version = _read_repo_version(repo_root)
    git_hash = _read_git_hash(repo_root)
    utc = _utc_now()

    try:
        scorer = VPMLScorer.from_yaml(args.graph)
    except FileNotFoundError:
        print(f"Error: Graph file not found: {args.graph}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pragma: no cover - CLI guard
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

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[+] JSON audit trail saved to: {os.path.abspath(args.json_out)}", file=sys.stderr)

    summary_txt = _load_summary_text(args.summary_file)
    report_md_final: Optional[str] = None
    explanations = None
    if args.explain or args.report_md or args.bundle_dir:
        explanations = explainer.explain_sci_result(
            scorer,
            result,
            top_k_paths=args.top_k,
        )

    if args.explain and explanations is not None:
        print("\n" + "=" * 60, file=sys.stderr)
        print("VPML RISK EXPLANATION REPORT", file=sys.stderr)
        print("=" * 60 + "\n", file=sys.stderr)
        print(explainer.render_explanations_text(explanations), file=sys.stderr)

    if args.report_md or args.bundle_dir:
        report_md = _build_report_markdown(
            report_title=args.report_title,
            graph_path=args.graph,
            domain_nodes=domain_nodes,
            sources=sources,
            sci_result=result,
            explanations=explanations or {},
            top_assets=3,
            top_paths=min(3, max(1, int(args.top_k))),
        )
        footer = _build_repro_footer(
            utc=utc,
            version=version,
            git_hash=git_hash,
            graph=args.graph,
            domain=args.domain,
            sources=args.sources,
            max_depth=args.max_depth,
            max_paths=args.max_paths,
            top_k=args.top_k,
            edge_types=args.edge_types,
        )
        report_md_final = report_md + footer + _summary_block(summary_txt)

    if args.report_md and report_md_final is not None:
        with open(args.report_md, "w", encoding="utf-8") as f:
            f.write(report_md_final)
        print(f"[+] Markdown report saved to: {os.path.abspath(args.report_md)}", file=sys.stderr)

    dot_output_path = ""
    if args.dot:
        dot_content = viz.to_dot(scorer, result, title=args.dot_title)
        viz.save_dot(args.dot, dot_content)
        dot_output_path = args.dot
        print(f"[+] Graphviz DOT saved to: {os.path.abspath(args.dot)}", file=sys.stderr)

    if args.bundle_dir:
        try:
            safe_utc = utc.replace(":", "-")
            default_name = f"vpml_bundle_{safe_utc}_{git_hash or 'nogit'}"
            bundle_name = _sanitize_bundle_name(args.bundle_name or default_name)
            bundle_path = os.path.join(args.bundle_dir, bundle_name)
            os.makedirs(bundle_path, exist_ok=True)

            bundled_files: List[str] = []

            result_bundle_path = os.path.join(bundle_path, "result.json")
            with open(result_bundle_path, "w", encoding="utf-8") as f:
                if args.pretty:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(result, f, ensure_ascii=False)
            bundled_files.append("result.json")

            if report_md_final is None:
                report_md_final = _build_report_markdown(
                    report_title=args.report_title,
                    graph_path=args.graph,
                    domain_nodes=domain_nodes,
                    sources=sources,
                    sci_result=result,
                    explanations=explanations or {},
                    top_assets=3,
                    top_paths=min(3, max(1, int(args.top_k))),
                )
                report_md_final += _build_repro_footer(
                    utc=utc,
                    version=version,
                    git_hash=git_hash,
                    graph=args.graph,
                    domain=args.domain,
                    sources=args.sources,
                    max_depth=args.max_depth,
                    max_paths=args.max_paths,
                    top_k=args.top_k,
                    edge_types=args.edge_types,
                )
                report_md_final += _summary_block(summary_txt)

            report_bundle_path = os.path.join(bundle_path, "report.md")
            with open(report_bundle_path, "w", encoding="utf-8") as f:
                f.write(report_md_final)
            bundled_files.append("report.md")

            if summary_txt:
                summary_bundle_path = os.path.join(bundle_path, "summary.txt")
                with open(summary_bundle_path, "w", encoding="utf-8") as f:
                    f.write(summary_txt + "\n")
                bundled_files.append("summary.txt")

            if dot_output_path and os.path.isfile(dot_output_path):
                try:
                    shutil.copyfile(dot_output_path, os.path.join(bundle_path, "graph.dot"))
                    bundled_files.append("graph.dot")
                except Exception:
                    pass

            manifest_metadata = {
                "utc": utc,
                "version": version,
                "git": git_hash,
                "commandline": sys.argv,
                "inputs": {
                    "graph": args.graph,
                    "domain": args.domain,
                    "sources": args.sources,
                    "max_depth": args.max_depth,
                    "max_paths": args.max_paths,
                    "top_k": args.top_k,
                    "edge_types": args.edge_types,
                },
            }
            manifest_path = _write_manifest(bundle_path, manifest_metadata, bundled_files)
            print(f"[+] Bundle saved to: {os.path.abspath(bundle_path)}", file=sys.stderr)
            print(f"[+] Manifest: {os.path.abspath(manifest_path)}", file=sys.stderr)
        except Exception as e:
            print(f"[!] Bundle generation skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
