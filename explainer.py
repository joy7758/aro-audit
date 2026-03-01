from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import math


@dataclass
class Explanation:
    asset_id: str
    headline: str
    summary: str
    top_path_explanations: List[str]
    control_priorities: List[str]


def _fmt_pct(x: float) -> str:
    return f"{max(0.0, min(1.0, x)) * 100:.1f}%"


def _risk_band(cp: float) -> str:
    if cp >= 0.75:
        return "CRITICAL"
    if cp >= 0.5:
        return "HIGH"
    if cp >= 0.25:
        return "MEDIUM"
    return "LOW"


def _get_node_label(nodes: Dict[str, Any], node_id: str) -> str:
    n = nodes.get(node_id)
    if not n:
        return node_id
    t = getattr(n, "type", None) or (n.get("type", "Node") if isinstance(n, dict) else "Node")
    return f"{node_id}<{t}>"


def _control_hint_from_edge(edge_type: str) -> str:
    # Neutral, non-weaponized control guidance: mediation/observability/least privilege
    if edge_type.lower().endswith("trustedge"):
        return "加强信任链中介（证据链/证明/撤销传播）并提升该链路可观测性。"
    if edge_type.lower().endswith("privilegeedge"):
        return "收敛权限边界（最小权限/缩小作用域）并提高授权变更审计覆盖。"
    if edge_type.lower().endswith("execflowedge"):
        return "对执行流启用强策略门（批准/签名/可追溯）并提升执行事件遥测。"
    if edge_type.lower().endswith("dataflowedge"):
        return "对数据流启用强访问控制与溯源，并提高异常数据流可观测性。"
    return "提升该链路的中介强度与观测覆盖，降低传播概率。"


def explain_sci_result(
    scorer: Any,
    sci_result: Dict[str, Any],
    *,
    top_k_paths: int = 5,
    max_controls: int = 6,
) -> Dict[str, Explanation]:
    """
    Convert scorer.sci(...) output to CISO-ready narrative.
    Requires scorer to access nodes/edges for labels and per-edge risk.
    """
    explanations: Dict[str, Explanation] = {}

    nodes = getattr(scorer, "nodes", {})
    edges = getattr(scorer, "edges", [])

    total_sci = float(sci_result.get("SCI", 0.0))

    for asset_id, item in (sci_result.get("nodes") or {}).items():
        cp = float(item.get("cp", 0.0))
        crit = float(item.get("criticality", 0.0))
        blast = float(item.get("blast_radius", 0.0))
        contrib = float(item.get("contribution", 0.0))
        
        contrib_pct = (contrib / total_sci) if total_sci > 0 else 0.0
        band = _risk_band(cp)

        headline = (
            f"[{band}] 资产 {asset_id} 的级联风险 CP={_fmt_pct(cp)}，"
            f"贡献值={contrib:.4f}（占比 {_fmt_pct(contrib_pct)}，关键性={crit:.2f}，影响半径={blast:.0f}）"
        )

        summary = (
            "该结论来自 RTP 图谱上的风险传播度量：风险沿信任/权限/执行/数据链路扩散，"
            "并受权限熵、作用域规模、观测覆盖、信任保障度与物理锚点强度等属性调制。"
        )

        # Build path explanations
        top_paths: List[Tuple[float, List[str]]] = item.get("top_paths") or []
        top_paths = top_paths[:top_k_paths]

        path_expls: List[str] = []
        control_scores: Dict[str, float] = {}

        for rank, (p, node_path) in enumerate(top_paths, start=1):
            p = float(p)
            if not node_path or len(node_path) < 2:
                continue

            # Reconstruct edge types along node_path
            edge_types: List[str] = []
            edge_risks: List[float] = []
            for a, b in zip(node_path[:-1], node_path[1:]):
                found = None
                for e in edges:
                    if getattr(e, "src", None) == a and getattr(e, "dst", None) == b:
                        found = e
                        break
                if found is None:
                    edge_types.append("Edge")
                    edge_risks.append(0.0)
                else:
                    et = getattr(found, "type", "Edge")
                    edge_types.append(et)
                    try:
                        edge_risks.append(float(scorer.edge_risk(found)))
                    except Exception:
                        edge_risks.append(0.0)

            # Path string
            labeled_nodes = " → ".join(_get_node_label(nodes, nid) for nid in node_path)
            et_chain = " / ".join(edge_types) if edge_types else "Edge"
            avg_er = sum(edge_risks) / max(1, len(edge_risks))

            # Control priorities: aggregate per "edge hop"
            for hop_idx, (et, er) in enumerate(zip(edge_types, edge_risks), start=1):
                key = f"{node_path[hop_idx-1]}→{node_path[hop_idx]}::{et}"
                control_scores[key] = control_scores.get(key, 0.0) + (p * er)

            path_expls.append(
                f"{rank}. 贡献路径概率={_fmt_pct(p)}（链路平均传播倾向≈{_fmt_pct(avg_er)}）\n"
                f"   路径：{labeled_nodes}\n"
                f"   主要链路类型：{et_chain}\n"
                f"   含义：该资产的风险主要由上游节点通过上述链路‘结构性可达’，"
                f"建议优先在链路处提升中介强度与观测覆盖、并收敛授权范围。"
            )

        # Build control priority list
        ranked_controls = sorted(control_scores.items(), key=lambda kv: kv[1], reverse=True)[:max_controls]
        control_lines: List[str] = []
        for i, (k, score) in enumerate(ranked_controls, start=1):
            try:
                hop, et = k.split("::", 1)
            except ValueError:
                hop, et = k, "Edge"
            control_lines.append(
                f"{i}. 控制点 {hop}（{et}），优先级分数={score:.4f}：{_control_hint_from_edge(et)}"
            )

        explanations[asset_id] = Explanation(
            asset_id=asset_id,
            headline=headline,
            summary=summary,
            top_path_explanations=path_expls,
            control_priorities=control_lines,
        )

    return explanations


def render_explanations_text(explanations: Dict[str, Explanation]) -> str:
    """
    Render explanations into a single human-readable report section.
    """
    lines: List[str] = []
    for asset_id, ex in explanations.items():
        lines.append(ex.headline)
        lines.append(ex.summary)
        if ex.top_path_explanations:
            lines.append("Top 传播路径解释：")
            lines.extend(ex.top_path_explanations)
        if ex.control_priorities:
            lines.append("优先控制点（建议先做这些能最快降 SCI）：")
            lines.extend(ex.control_priorities)
        lines.append("-" * 80)
    return "\n".join(lines)