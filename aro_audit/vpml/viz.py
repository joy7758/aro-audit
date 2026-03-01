from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _escape(s: str) -> str:
    return s.replace('"', '\\"')


def to_dot(
    scorer: Any,
    sci_result: Optional[Dict[str, Any]] = None,
    *,
    title: str = "VPML Risk Propagation Graph",
    show_edge_risk: bool = True,
    show_node_cp: bool = True,
) -> str:
    """
    Export DOT for Graphviz. If sci_result is provided, node labels can include CP.
    """
    nodes = getattr(scorer, "nodes", {})
    edges = getattr(scorer, "edges", [])

    cp_map: Dict[str, float] = {}
    if sci_result and isinstance(sci_result, dict):
        for nid, item in (sci_result.get("nodes") or {}).items():
            try:
                cp_map[nid] = float(item.get("cp", 0.0))
            except Exception:
                cp_map[nid] = 0.0

    # Build DOT
    lines: List[str] = []
    lines.append('digraph RTP {')
    lines.append(f'  label="{_escape(title)}";')
    lines.append('  labelloc="t";')
    lines.append('  fontsize=18;')
    lines.append('  rankdir=LR;')
    lines.append('  node [shape=box, style="rounded,filled", fontname="Helvetica"];')
    lines.append('  edge [fontname="Helvetica"];')

    # Nodes
    for nid, n in nodes.items():
        ntype = getattr(n, "type", None) or (n.get("type") if isinstance(n, dict) else "Node")
        cp = cp_map.get(nid, None)

        label = f"{nid}\\n{ntype}"
        if show_node_cp and cp is not None:
            label += f"\\nCP={cp:.3f}"

        # Heat as grayscale fill: higher CP => darker
        # (kept neutral; Graphviz expects colors; using grayXX keeps it unobtrusive)
        if cp is None:
            fill = "gray95"
        else:
            # cp=0 -> gray95, cp=1 -> gray35
            g = int(round(95 - 60 * _clamp01(cp)))
            fill = f"gray{g}"

        lines.append(f'  "{_escape(nid)}" [label="{_escape(label)}", fillcolor="{fill}"];')

    # Edges
    for e in edges:
        src = getattr(e, "src", None) or e.get("src")
        dst = getattr(e, "dst", None) or e.get("dst")
        et = getattr(e, "type", None) or e.get("type", "Edge")

        if show_edge_risk:
            try:
                pe = float(scorer.edge_risk(e))
            except Exception:
                pe = 0.0
            elabel = f"{et}\\nP_e={pe:.3f}"
        else:
            elabel = f"{et}"

        lines.append(f'  "{_escape(src)}" -> "{_escape(dst)}" [label="{_escape(elabel)}"];')

    lines.append("}")
    return "\n".join(lines)


def save_dot(path: str, dot: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(dot)