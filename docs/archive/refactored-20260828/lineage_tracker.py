#!/usr/bin/env python3
"""研究全链路血缘追踪器。

用途：
    维护研究全链路中所有产物（论文、科学问题、申请书段落、wiki 概念等）之间的
    血缘关系图，支持双向溯源查询和影响分析。

    回答两个核心问题：
      1. 正向（downstream）：这篇论文影响了哪些申请书段落？
      2. 反向（upstream）：这段内容基于什么？

数据存储：
    {proposal_dir}/00_pipeline/lineage.json
    结构：{"nodes": {id: {...}}, "edges": [{from, to, relation, ...}]}

边的方向约定：
    from → to 表示 from 指向 to。
    - derived_from: A 从 B 推导而来，from=A(段落), to=B(论文)
      → 段落的 upstream 是论文（沿 from→to 正方向追溯）
      → 论文的 downstream 是段落（沿 to→from 逆方向追溯）

    trace_upstream   沿 from→to 正方向 BFS（找"基于什么"）
    trace_downstream 沿 to→from 逆方向 BFS（找"影响了什么"）

用法示例：
    >>> from lineage_tracker import LineageTracker
    >>> from pathlib import Path
    >>> tracker = LineageTracker(Path("/path/to/proposal"))
    >>> tracker.register_node("sec1", "proposal_section", "研究内容1", stage=4)
    >>> tracker.register_node("paperA", "paper", "arxiv:2401.xxxxx")
    >>> tracker.add_edge("sec1", "paperA", "derived_from", "提供实验数据支撑")
    >>> tracker.trace_upstream("sec1")        # 段落基于什么
    >>> tracker.trace_downstream("paperA")    # 论文影响了什么
    >>> tracker.get_evidence_chain("sec1")    # 段落的论文证据链
    >>> tracker.export_dot()                  # 导出 Graphviz 可视化

规范：仅标准库，JSON ensure_ascii=False，时间戳 UTC ISO。
"""

from __future__ import annotations

import hashlib
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc, load_json, save_json, file_lock


# 支持的边关系类型
RELATION_DERIVED_FROM = "derived_from"   # A 从 B 推导而来（段落 ← 论文）
RELATION_SUPPORTS = "supports"           # A 的证据支撑 B（论文 → 概念）
RELATION_CONTRADICTS = "contradicts"     # A 的证据与 B 矛盾
RELATION_EXTENDS = "extends"             # A 扩展了 B
RELATION_BELONGS_TO = "belongs_to"       # A 属于 B（子集关系）
RELATION_RELATED = "related"             # 一般关联
VALID_RELATIONS = {
    RELATION_DERIVED_FROM, RELATION_SUPPORTS, RELATION_CONTRADICTS,
    RELATION_EXTENDS, RELATION_BELONGS_TO, RELATION_RELATED,
}


class LineageTracker:
    """血缘追踪器，维护研究全链路产物间的血缘关系图。"""

    def __init__(self, proposal_dir: Path | str):
        """初始化追踪器。

        Args:
            proposal_dir: 课题/proposal 根目录，lineage.json 位于其下的 00_pipeline/。
        """
        self.proposal_dir = Path(proposal_dir)
        self.pipeline_dir = self.proposal_dir / "00_pipeline"
        self.lineage_path = self.pipeline_dir / "lineage.json"
        # 基于 proposal_dir 生成稳定锁名，不同 proposal 互不阻塞
        digest = hashlib.md5(str(self.proposal_dir.resolve()).encode("utf-8")).hexdigest()[:8]
        self._lock_name = f"lineage-{digest}"

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def _load_graph(self) -> Dict[str, Any]:
        """加载血缘图（使用 file_lock 保护读取）。

        Returns:
            {"nodes": {id: {...}}, "edges": [{...}]}
        """
        with file_lock(self._lock_name):
            data = load_json(self.lineage_path, {})
        if not isinstance(data, dict):
            data = {}
        if not isinstance(data.get("nodes"), dict):
            data["nodes"] = {}
        if not isinstance(data.get("edges"), list):
            data["edges"] = []
        return data

    def _save_graph(self, data: Dict[str, Any]) -> None:
        """保存血缘图（使用 file_lock 保护写入，原子落盘）。"""
        if not isinstance(data, dict):
            data = {}
        data.setdefault("nodes", {})
        data.setdefault("edges", [])
        with file_lock(self._lock_name):
            save_json(self.lineage_path, data)

    # ------------------------------------------------------------------
    # 节点 / 边管理
    # ------------------------------------------------------------------

    def register_node(self, node_id: str, node_type: str, label: str,
                      stage: Optional[int] = None) -> Dict[str, Any]:
        """注册节点。已存在则更新 type/label/stage，保留 created_at。

        Args:
            node_id: 节点唯一标识
            node_type: 节点类型（proposal_section/paper/wiki_concept/...）
            label: 人类可读名称
            stage: 可选阶段编号

        Returns:
            注册后的节点 dict
        """
        data = self._load_graph()
        node = data["nodes"].get(node_id, {})
        node["id"] = node_id
        node["type"] = node_type
        node["label"] = label
        if stage is not None:
            node["stage"] = stage
        if "created_at" not in node:
            node["created_at"] = now_utc()
        data["nodes"][node_id] = node
        self._save_graph(data)
        return node

    def add_edge(self, from_id: str, to_id: str, relation: str,
                 contribution: str = "") -> Dict[str, Any]:
        """添加边，自动确保两端节点存在（缺失则创建占位节点）。

        若相同的 from+to+relation 边已存在，则更新 contribution（若提供）。

        Args:
            from_id: 起点节点 id
            to_id: 终点节点 id
            relation: 关系类型（见 VALID_RELATIONS）
            contribution: 可选，该关系的贡献说明

        Returns:
            边 dict
        """
        data = self._load_graph()
        # 自动创建缺失节点
        for nid in (from_id, to_id):
            if nid not in data["nodes"]:
                data["nodes"][nid] = {
                    "id": nid,
                    "type": "unknown",
                    "label": nid,
                    "created_at": now_utc(),
                }
        # 查重：相同 from+to+relation 视为同一条边
        for edge in data["edges"]:
            if (edge.get("from") == from_id and edge.get("to") == to_id
                    and edge.get("relation") == relation):
                if contribution:
                    edge["contribution"] = contribution
                self._save_graph(data)
                return edge
        edge = {
            "from": from_id,
            "to": to_id,
            "relation": relation,
            "contribution": contribution,
            "created_at": now_utc(),
        }
        data["edges"].append(edge)
        self._save_graph(data)
        return edge

    def remove_node(self, node_id: str) -> Dict[str, Any]:
        """移除节点及其所有关联边。

        Returns:
            {"removed_node": bool, "removed_edges": int}
        """
        data = self._load_graph()
        existed = node_id in data["nodes"]
        data["nodes"].pop(node_id, None)
        before = len(data["edges"])
        data["edges"] = [
            e for e in data["edges"]
            if e.get("from") != node_id and e.get("to") != node_id
        ]
        removed_edges = before - len(data["edges"])
        self._save_graph(data)
        return {"removed_node": existed, "removed_edges": removed_edges}

    # ------------------------------------------------------------------
    # 邻接表 / BFS 内部工具
    # ------------------------------------------------------------------

    @staticmethod
    def _build_adjacency(edges: List[Dict[str, Any]],
                         reverse: bool = False) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
        """构建邻接表。

        Args:
            edges: 边列表
            reverse: False=正方向(from→to)，True=逆方向(to→from)

        Returns:
            {node_id: [(neighbor_id, edge_dict), ...]}
        """
        adj: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        for edge in edges:
            src = edge.get("to") if reverse else edge.get("from")
            dst = edge.get("from") if reverse else edge.get("to")
            if src is None or dst is None:
                continue
            adj.setdefault(src, []).append((dst, edge))
        return adj

    def _bfs(self, data: Dict[str, Any], start: str,
             reverse: bool, max_depth: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """BFS 遍历，返回 (result_nodes, result_edges)。

        result_nodes 不含 start 自身，depth 从 1 开始。
        每个节点记录到达路径 path（含 start）。
        """
        nodes = data["nodes"]
        adj = self._build_adjacency(data["edges"], reverse=reverse)
        visited = {start}
        queue: deque = deque([(start, 0, [start])])
        result_nodes: List[Dict[str, Any]] = []
        result_edges: List[Dict[str, Any]] = []
        while queue:
            current, depth, path = queue.popleft()
            if depth >= max_depth:
                continue
            for nxt, edge in adj.get(current, []):
                if nxt in visited:
                    continue
                visited.add(nxt)
                new_path = path + [nxt]
                result_nodes.append({
                    "id": nxt,
                    "type": nodes.get(nxt, {}).get("type", "unknown"),
                    "depth": depth + 1,
                    "path": new_path,
                })
                result_edges.append(edge)
                queue.append((nxt, depth + 1, new_path))
        return result_nodes, result_edges

    # ------------------------------------------------------------------
    # 溯源查询
    # ------------------------------------------------------------------

    def trace_upstream(self, node_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """反向溯源：这个产物基于什么？（沿 from→to 正方向 BFS）

        Args:
            node_id: 起始节点
            max_depth: 最大追溯深度

        Returns:
            {"start":..., "direction":"upstream", "nodes":[...], "edges":[...]}
        """
        data = self._load_graph()
        if node_id not in data["nodes"]:
            return {"start": node_id, "direction": "upstream",
                    "nodes": [], "edges": []}
        result_nodes, result_edges = self._bfs(
            data, node_id, reverse=False, max_depth=max_depth)
        return {
            "start": node_id,
            "direction": "upstream",
            "nodes": result_nodes,
            "edges": result_edges,
        }

    def trace_downstream(self, node_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """正向溯源：这个产物影响了什么？（沿 to→from 逆方向 BFS）

        Args:
            node_id: 起始节点
            max_depth: 最大追溯深度

        Returns:
            {"start":..., "direction":"downstream", "nodes":[...], "edges":[...]}
        """
        data = self._load_graph()
        if node_id not in data["nodes"]:
            return {"start": node_id, "direction": "downstream",
                    "nodes": [], "edges": []}
        result_nodes, result_edges = self._bfs(
            data, node_id, reverse=True, max_depth=max_depth)
        return {
            "start": node_id,
            "direction": "downstream",
            "nodes": result_nodes,
            "edges": result_edges,
        }

    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """查找两个节点之间的最短路径（BFS，沿 from→to 正方向）。

        Args:
            from_id: 起点
            to_id: 终点

        Returns:
            节点 id 列表（含首尾），不存在路径时返回 None
        """
        data = self._load_graph()
        if from_id not in data["nodes"] or to_id not in data["nodes"]:
            return None
        if from_id == to_id:
            return [from_id]
        adj = self._build_adjacency(data["edges"], reverse=False)
        visited = {from_id}
        queue: deque = deque([(from_id, [from_id])])
        while queue:
            current, path = queue.popleft()
            for nxt, _edge in adj.get(current, []):
                if nxt in visited:
                    continue
                if nxt == to_id:
                    return path + [nxt]
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
        return None

    # ------------------------------------------------------------------
    # 分析
    # ------------------------------------------------------------------

    def impact_analysis(self, node_id: str) -> Dict[str, Any]:
        """影响分析：统计该节点直接/间接影响的下游节点数量和类型分布。

        下游 = trace_downstream 全量追溯结果。

        Returns:
            {"node_id":..., "total_impacted":int,
             "by_type":{type:count}, "by_depth":{depth:count},
             "impacted_nodes":[ids]}
        """
        data = self._load_graph()
        if node_id not in data["nodes"]:
            return {"node_id": node_id, "total_impacted": 0,
                    "by_type": {}, "by_depth": {},
                    "impacted_nodes": []}
        result_nodes, _ = self._bfs(data, node_id, reverse=True, max_depth=1000)
        by_type: Dict[str, int] = {}
        by_depth: Dict[str, int] = {}
        impacted: List[str] = []
        for n in result_nodes:
            t = n["type"]
            by_type[t] = by_type.get(t, 0) + 1
            d = str(n["depth"])
            by_depth[d] = by_depth.get(d, 0) + 1
            impacted.append(n["id"])
        return {
            "node_id": node_id,
            "total_impacted": len(result_nodes),
            "by_type": by_type,
            "by_depth": by_depth,
            "impacted_nodes": impacted,
        }

    def get_evidence_chain(self, artifact_id: str) -> List[Dict[str, Any]]:
        """获取某产物的完整证据链：递归向上查找所有 paper 类型的源头节点。

        沿 upstream 方向全量追溯，过滤出 type==paper 的节点。

        Returns:
            [{"id":..., "label":..., "depth":..., "path":[...]}]
        """
        data = self._load_graph()
        if artifact_id not in data["nodes"]:
            return []
        result_nodes, _ = self._bfs(
            data, artifact_id, reverse=False, max_depth=1000)
        chain: List[Dict[str, Any]] = []
        for n in result_nodes:
            if n["type"] == "paper":
                chain.append({
                    "id": n["id"],
                    "label": data["nodes"].get(n["id"], {}).get("label", n["id"]),
                    "depth": n["depth"],
                    "path": n["path"],
                })
        return chain

    def find_orphans(self) -> List[Dict[str, Any]]:
        """查找无任何边的孤立节点。

        Returns:
            [{"id":..., "type":..., "label":...}]
        """
        data = self._load_graph()
        connected = set()
        for edge in data["edges"]:
            connected.add(edge.get("from"))
            connected.add(edge.get("to"))
        orphans: List[Dict[str, Any]] = []
        for nid, node in data["nodes"].items():
            if nid not in connected:
                orphans.append({
                    "id": nid,
                    "type": node.get("type", "unknown"),
                    "label": node.get("label", nid),
                })
        return orphans

    # ------------------------------------------------------------------
    # 导出
    # ------------------------------------------------------------------

    @staticmethod
    def _dot_escape(s: str) -> str:
        """转义 DOT 字符串字面量中的特殊字符（反斜杠、双引号）。"""
        return s.replace("\\", "\\\\").replace('"', '\\"')

    def export_dot(self) -> str:
        """导出 Graphviz DOT 格式（用于可视化）。

        Returns:
            DOT 格式字符串，可直接交由 graphviz 渲染。
        """
        data = self._load_graph()
        lines = ["digraph lineage {", "    rankdir=LR;"]
        for nid, node in data["nodes"].items():
            label = node.get("label", nid)
            ntype = node.get("type", "unknown")
            lines.append(
                f'    "{self._dot_escape(nid)}" '
                f'[label="{self._dot_escape(label)} ({ntype})"];'
            )
        for edge in data["edges"]:
            f = self._dot_escape(edge.get("from", ""))
            t = self._dot_escape(edge.get("to", ""))
            rel = edge.get("relation", "related")
            lines.append(f'    "{f}" -> "{t}" [label="{rel}"];')
        lines.append("}")
        return "\n".join(lines)


def _self_check() -> None:
    """自检：在临时目录中隔离测试 8 个核心场景。"""
    import shutil
    import tempfile

    print("=" * 50)
    print("◐ lineage_tracker 自检")
    print("=" * 50)

    tmp = Path(tempfile.mkdtemp(prefix="lineage_test_"))
    try:
        tracker = LineageTracker(tmp)

        # [1/8] 注册节点
        print("\n[1/8] 注册节点...")
        tracker.register_node("sec1", "proposal_section", "研究内容1", stage=4)
        tracker.register_node("Q1", "scientific_question", "科学问题1")
        tracker.register_node("paperA", "paper", "arxiv:2401.xxxxx")
        data = tracker._load_graph()
        assert "sec1" in data["nodes"], "节点 sec1 应存在"
        assert data["nodes"]["sec1"]["label"] == "研究内容1"
        assert data["nodes"]["sec1"]["stage"] == 4
        assert "created_at" in data["nodes"]["sec1"]
        print("  ✓ 节点注册成功，字段完整")

        # [2/8] 添加边（自动创建节点）
        print("\n[2/8] 添加边（自动创建缺失节点）...")
        tracker.add_edge("sec1", "Q1", "derived_from", "由科学问题推导")
        tracker.add_edge("Q1", "paperA", "derived_from", "基于该论文")
        tracker.add_edge("paperA", "conceptX", "supports", "支撑概念X")
        data = tracker._load_graph()
        assert len(data["edges"]) == 3, f"应有 3 条边，实际 {len(data['edges'])}"
        # conceptX 自动创建为 unknown
        assert "conceptX" in data["nodes"], "conceptX 应被自动创建"
        assert data["nodes"]["conceptX"]["type"] == "unknown"
        # 重复边不新增
        tracker.add_edge("sec1", "Q1", "derived_from", "更新说明")
        data = tracker._load_graph()
        assert len(data["edges"]) == 3, "重复边不应新增"
        print("  ✓ 边添加成功，缺失节点自动创建，重复边不新增")

        # [3/8] 反向溯源 upstream
        # 图: sec1 -> Q1 -> paperA -> conceptX (from->to)
        print("\n[3/8] 反向溯源 (upstream)...")
        up = tracker.trace_upstream("sec1", max_depth=5)
        assert up["start"] == "sec1"
        assert up["direction"] == "upstream"
        ids = [n["id"] for n in up["nodes"]]
        depth_map = {n["id"]: n["depth"] for n in up["nodes"]}
        assert "Q1" in ids and depth_map["Q1"] == 1, "Q1 应在 depth 1"
        assert "paperA" in ids and depth_map["paperA"] == 2, "paperA 应在 depth 2"
        assert "conceptX" in ids and depth_map["conceptX"] == 3, "conceptX 应在 depth 3"
        # 验证 path
        q1_node = [n for n in up["nodes"] if n["id"] == "Q1"][0]
        assert q1_node["path"] == ["sec1", "Q1"], f"path 错误: {q1_node['path']}"
        # 验证 edges 数量
        assert len(up["edges"]) == 3, f"应经过 3 条边，实际 {len(up['edges'])}"
        print("  ✓ upstream BFS 遍历正确（depth/path/edges）")

        # [4/8] 正向溯源 downstream
        # conceptX 下游: paperA(d1) -> Q1(d2) -> sec1(d3)
        print("\n[4/8] 正向溯源 (downstream)...")
        down = tracker.trace_downstream("conceptX", max_depth=5)
        assert down["direction"] == "downstream"
        ids = [n["id"] for n in down["nodes"]]
        depth_map = {n["id"]: n["depth"] for n in down["nodes"]}
        assert "paperA" in ids and depth_map["paperA"] == 1
        assert "Q1" in ids and depth_map["Q1"] == 2
        assert "sec1" in ids and depth_map["sec1"] == 3
        print("  ✓ downstream BFS 遍历正确")

        # [5/8] 影响分析
        print("\n[5/8] 影响分析...")
        impact = tracker.impact_analysis("conceptX")
        assert impact["total_impacted"] == 3, f"应影响 3 个节点，实际 {impact['total_impacted']}"
        assert impact["by_type"].get("paper") == 1
        assert impact["by_type"].get("scientific_question") == 1
        assert impact["by_type"].get("proposal_section") == 1
        assert set(impact["impacted_nodes"]) == {"paperA", "Q1", "sec1"}
        print(f"  ✓ 影响分析: {impact['total_impacted']} 节点, 类型分布 {impact['by_type']}")

        # [6/8] 证据链
        print("\n[6/8] 证据链...")
        chain = tracker.get_evidence_chain("sec1")
        # sec1 上游所有 paper：仅 paperA
        assert len(chain) == 1, f"应找到 1 篇论文，实际 {len(chain)}"
        assert chain[0]["id"] == "paperA"
        assert chain[0]["label"] == "arxiv:2401.xxxxx"
        assert chain[0]["depth"] == 2
        print(f"  ✓ 证据链: 找到 {len(chain)} 篇论文源头 (paperA)")

        # [7/8] DOT 导出
        print("\n[7/8] DOT 导出...")
        dot = tracker.export_dot()
        assert dot.startswith("digraph lineage"), "应以 digraph lineage 开头"
        assert dot.rstrip().endswith("}"), "应以 } 结尾"
        assert "rankdir=LR" in dot
        assert "->" in dot, "应包含边"
        assert "derived_from" in dot, "应包含关系标签"
        assert "supports" in dot
        assert "arxiv:2401.xxxxx" in dot, "应包含节点 label"
        print("  ✓ DOT 格式正确")

        # [8/8] 孤立节点检测
        print("\n[8/8] 孤立节点检测...")
        tracker.register_node("orphan1", "note", "孤立笔记")
        orphans = tracker.find_orphans()
        orphan_ids = [o["id"] for o in orphans]
        assert "orphan1" in orphan_ids, "orphan1 应为孤立节点"
        assert "sec1" not in orphan_ids, "sec1 有边，不应为孤立"
        print(f"  ✓ 检测到 {len(orphans)} 个孤立节点: {orphan_ids}")

        # 附加：移除节点
        print("\n[附加] 移除节点...")
        tracker.add_edge("sec1", "paperA", "related", "额外关联")
        result = tracker.remove_node("sec1")
        data = tracker._load_graph()
        assert result["removed_node"] is True
        assert "sec1" not in data["nodes"]
        assert all(e["from"] != "sec1" and e["to"] != "sec1" for e in data["edges"])
        # sec1 相关边: (sec1->Q1) + (sec1->paperA related) = 2 条
        assert result["removed_edges"] == 2, f"应删除 2 条边，实际 {result['removed_edges']}"
        print(f"  ✓ 移除节点成功，连带删除 {result['removed_edges']} 条边")

        # 附加：路径查找
        print("\n[附加] 路径查找...")
        # 当前图: Q1 -> paperA -> conceptX (正方向)
        path = tracker.find_path("Q1", "conceptX")
        assert path == ["Q1", "paperA", "conceptX"], f"路径错误: {path}"
        # 反方向无路径
        path2 = tracker.find_path("conceptX", "Q1")
        assert path2 is None, "conceptX 到 Q1 正方向无路径，应返回 None"
        print(f"  ✓ 路径查找: Q1 -> conceptX = {path}")

        # 附加：不存在节点查询返回空
        assert tracker.trace_upstream("nonexist")["nodes"] == []
        assert tracker.find_path("nonexist", "Q1") is None
        assert tracker.get_evidence_chain("nonexist") == []
        print("  ✓ 不存在节点查询返回空")

        print("\n✓ lineage_tracker 自检通过")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print("(已清理临时目录)")


if __name__ == "__main__":
    _self_check()
