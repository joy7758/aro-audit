from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml


@dataclass
class VPMLNode:
    id: str
    type: str
    attrs: Dict[str, Any]


@dataclass
class VPMLEdge:
    src: str
    dst: str
    type: str
    attrs: Dict[str, Any]


class VPMLScorer:
    """VPML risk propagation scorer with SCI aggregation and path circuit-breaker support."""

    _DEFAULT_NORMS: Dict[str, float] = {
        "edge_latency_hi": 3600.0,
        "priv_entropy_hi": 10.0,
        "priv_scope_hi": 1000.0,
    }

    _DEFAULT_WEIGHTS: Dict[str, float] = {
        "a_trust_assurance": 1.0,
        "a_priv_entropy": 0.9,
        "a_priv_scope": 0.9,
        "a_obs_coverage": 0.9,
        "a_phy_sidechannel": 0.8,
        "a_phy_fingerprint": 0.8,
    }

    def __init__(
        self,
        nodes: Dict[str, VPMLNode],
        edges: List[VPMLEdge],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.nodes = nodes
        self.edges = edges

        config = config or {}
        cfg_norms = (config.get("norms") or {}) if isinstance(config, dict) else {}
        cfg_weights = (config.get("weights") or {}) if isinstance(config, dict) else {}

        self.norms: Dict[str, float] = {**self._DEFAULT_NORMS, **cfg_norms}
        self.weights: Dict[str, float] = {**self._DEFAULT_WEIGHTS, **cfg_weights}

        self.adj: Dict[str, List[int]] = {}
        for idx, e in enumerate(self.edges):
            self.adj.setdefault(e.src, []).append(idx)

    @classmethod
    def from_yaml(cls, path: str) -> "VPMLScorer":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        graph = raw.get("graph") or {}
        raw_nodes = graph.get("nodes") or []
        raw_edges = graph.get("edges") or []

        nodes: Dict[str, VPMLNode] = {}
        for item in raw_nodes:
            if not isinstance(item, dict):
                continue
            node_id = str(item.get("id", "")).strip()
            if not node_id:
                continue
            nodes[node_id] = VPMLNode(
                id=node_id,
                type=str(item.get("type", "Node")),
                attrs=item.get("attrs") or {},
            )

        edges: List[VPMLEdge] = []
        for item in raw_edges:
            if not isinstance(item, dict):
                continue
            src = str(item.get("src", "")).strip()
            dst = str(item.get("dst", "")).strip()
            if not src or not dst:
                continue
            edges.append(
                VPMLEdge(
                    src=src,
                    dst=dst,
                    type=str(item.get("type", "Edge")),
                    attrs=item.get("attrs") or {},
                )
            )

        return cls(nodes=nodes, edges=edges, config=raw.get("config") or {})

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    def _norm(self, value: float, hi: float) -> float:
        if hi <= 0:
            return 0.0
        return self._clamp01(value / hi)

    def _node_attr(self, node: VPMLNode, path: Tuple[str, str], default: float) -> float:
        section, key = path
        sec = node.attrs.get(section, {}) if isinstance(node.attrs, dict) else {}
        raw = sec.get(key, default) if isinstance(sec, dict) else default
        try:
            return float(raw)
        except Exception:
            return float(default)

    def node_risk(self, node_id: str) -> float:
        node = self.nodes.get(node_id)
        if node is None:
            return 0.5

        trust_assurance = self._clamp01(self._node_attr(node, ("trust", "assurance"), 0.5))
        priv_entropy = self._norm(
            self._node_attr(node, ("priv", "entropy"), 0.0),
            float(self.norms.get("priv_entropy_hi", 10.0)),
        )
        priv_scope = self._norm(
            self._node_attr(node, ("priv", "scope_size"), 0.0),
            float(self.norms.get("priv_scope_hi", 1000.0)),
        )
        obs_coverage = self._clamp01(self._node_attr(node, ("obs", "coverage"), 0.5))
        phy_sidechannel = self._clamp01(self._node_attr(node, ("phy", "sidechannel_exposure"), 0.0))
        phy_fingerprint = self._clamp01(self._node_attr(node, ("phy", "fingerprint_strength"), 0.5))

        components = {
            "a_trust_assurance": 1.0 - trust_assurance,
            "a_priv_entropy": priv_entropy,
            "a_priv_scope": priv_scope,
            "a_obs_coverage": 1.0 - obs_coverage,
            "a_phy_sidechannel": phy_sidechannel,
            "a_phy_fingerprint": 1.0 - phy_fingerprint,
        }

        num = 0.0
        den = 0.0
        for key, value in components.items():
            w = float(self.weights.get(key, 1.0))
            num += w * self._clamp01(value)
            den += max(0.0, w)

        return self._clamp01(num / den) if den > 0 else 0.0

    def edge_risk(self, edge: VPMLEdge) -> float:
        raw_edge = edge.attrs.get("edge", {}) if isinstance(edge.attrs, dict) else {}

        def _edge_num(name: str, default: float) -> float:
            raw = raw_edge.get(name, default) if isinstance(raw_edge, dict) else default
            try:
                return float(raw)
            except Exception:
                return float(default)

        assurance = self._clamp01(_edge_num("assurance", 0.5))
        mediation = self._clamp01(_edge_num("mediation", 0.5))
        observability = self._clamp01(_edge_num("observability", 0.5))
        latency = _edge_num("latency", 0.0)
        latency_norm = self._norm(latency, float(self.norms.get("edge_latency_hi", 3600.0)))

        edge_base = (
            0.35 * (1.0 - assurance)
            + 0.25 * (1.0 - mediation)
            + 0.25 * (1.0 - observability)
            + 0.15 * latency_norm
        )

        src_risk = self.node_risk(edge.src)
        dst_risk = self.node_risk(edge.dst)

        return self._clamp01(0.65 * edge_base + 0.15 * src_risk + 0.20 * dst_risk)

    def _edge_path_to_nodes(self, start: str, edge_path: List[int]) -> List[str]:
        nodes = [start]
        cur = start
        for ei in edge_path:
            e = self.edges[ei]
            if e.src != cur:
                break
            cur = e.dst
            nodes.append(cur)
        return nodes

    def _dfs_paths(
        self,
        start: str,
        max_depth: int,
        allowed_edge_types: Optional[Iterable[str]] = None,
        max_paths: int = 1000,
    ) -> List[List[int]]:
        allowed: Optional[Set[str]] = set(allowed_edge_types) if allowed_edge_types else None
        paths: List[List[int]] = []

        # Stack entries: (current_node, edge_path, visited_nodes)
        stack: List[Tuple[str, List[int], Set[str]]] = [(start, [], {start})]

        while stack:
            if len(paths) >= max_paths:
                break

            cur, edge_path, visited = stack.pop()

            if edge_path:
                paths.append(edge_path)

            if len(edge_path) >= max_depth:
                continue

            for ei in self.adj.get(cur, []):
                if len(paths) >= max_paths:
                    break

                e = self.edges[ei]
                if allowed is not None and e.type not in allowed:
                    continue
                if e.dst in visited:
                    continue

                stack.append((e.dst, edge_path + [ei], visited | {e.dst}))

        return paths

    def _path_probability(self, source: str, edge_path: List[int]) -> float:
        if not edge_path:
            return 0.0

        p = self.node_risk(source)
        for ei in edge_path:
            e = self.edges[ei]
            hop = self.edge_risk(e) * self.node_risk(e.dst)
            p *= self._clamp01(hop)

        return self._clamp01(p)

    def cascading_probability(
        self,
        domain_node: str,
        sources: Optional[Iterable[str]] = None,
        max_depth: int = 5,
        max_paths: int = 1000,
        top_k_paths: int = 5,
        allowed_edge_types: Optional[Iterable[str]] = None,
    ) -> Tuple[float, List[Tuple[float, List[str]]]]:
        if domain_node not in self.nodes:
            return 0.0, []

        source_nodes = list(sources) if sources is not None else [
            nid for nid in self.nodes if nid != domain_node
        ]

        all_paths: List[Tuple[float, List[str]]] = []

        for s in source_nodes:
            if s not in self.nodes:
                continue

            edge_paths = self._dfs_paths(
                s,
                max_depth=max_depth,
                allowed_edge_types=allowed_edge_types,
                max_paths=max_paths,
            )

            for edge_path in edge_paths:
                if not edge_path:
                    continue
                if self.edges[edge_path[-1]].dst != domain_node:
                    continue

                node_path = self._edge_path_to_nodes(s, edge_path)
                if not node_path or node_path[-1] != domain_node:
                    continue

                p = self._path_probability(s, edge_path)
                if p <= 0.0:
                    continue
                all_paths.append((p, node_path))

        if not all_paths:
            return 0.0, []

        cp_fail = 1.0
        for p, _ in all_paths:
            cp_fail *= 1.0 - self._clamp01(p)
        cp = self._clamp01(1.0 - cp_fail)

        top_paths = sorted(all_paths, key=lambda x: x[0], reverse=True)[: max(0, int(top_k_paths))]
        return cp, top_paths

    def sci(
        self,
        domain_nodes: Iterable[str],
        sources: Optional[Iterable[str]] = None,
        max_depth: int = 5,
        max_paths: int = 1000,
        top_k_paths: int = 5,
        allowed_edge_types: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        result_nodes: Dict[str, Any] = {}
        sci_total = 0.0

        source_nodes = list(sources) if sources is not None else None

        for nid in domain_nodes:
            node = self.nodes.get(nid)
            if node is None:
                result_nodes[nid] = {
                    "cp": 0.0,
                    "criticality": 0.0,
                    "blast_radius": 0.0,
                    "contribution": 0.0,
                    "top_paths": [],
                }
                continue

            cp, top_paths = self.cascading_probability(
                nid,
                sources=source_nodes,
                max_depth=max_depth,
                max_paths=max_paths,
                top_k_paths=top_k_paths,
                allowed_edge_types=allowed_edge_types,
            )

            asset = node.attrs.get("asset", {}) if isinstance(node.attrs, dict) else {}
            try:
                criticality = self._clamp01(float(asset.get("criticality", 0.5)))
            except Exception:
                criticality = 0.5
            try:
                blast_radius = max(0.0, float(asset.get("blast_radius", 1.0)))
            except Exception:
                blast_radius = 1.0

            blast_norm = self._clamp01(blast_radius / 100.0)
            contribution = cp * criticality * (0.5 + 0.5 * blast_norm)
            sci_total += contribution

            result_nodes[nid] = {
                "cp": cp,
                "criticality": criticality,
                "blast_radius": blast_radius,
                "contribution": contribution,
                "top_paths": [[p, path] for (p, path) in top_paths],
            }

        return {
            "SCI": sci_total,
            "nodes": result_nodes,
            "meta": {
                "max_depth": max_depth,
                "max_paths": max_paths,
                "sources": source_nodes,
                "allowed_edge_types": list(allowed_edge_types) if allowed_edge_types is not None else None,
            },
        }
