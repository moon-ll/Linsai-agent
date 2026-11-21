#!/usr/bin/env python3
"""产物版本管理器 — 研究全链路产物生命周期管理。

管理研究管线各阶段产物（proposal_section / scientific_question / self_check 等）
的版本快照、diff 对比、回滚、状态机与血缘关系。每个 proposal 目录下维护
`00_pipeline/artifacts.json` 注册表，记录全部产物元数据；同时将每个版本的文件
内容快照保存到 `00_pipeline/.artifacts/`，确保历史版本可 diff、可回滚。

产物生命周期状态机：
    draft → in_review → locked → downstream → superseded/archived
    （locked 状态内容不可变，下游引用此版本；superseded/archived 为终态，
      可经 rollback 恢复）

版本命名规则：
    v0.x   自动生成与优化阶段（create_artifact 自动递增）
    v1.0   Gate 5 通过后的最终版（可通过 version 参数显式指定）
    v2.0+  重大修订

用法:
    >>> from pathlib import Path
    >>> from artifact_manager import ArtifactManager
    >>> mgr = ArtifactManager(Path("/data/proposals/T1"))
    >>> mgr.create_artifact("sec01_v0.1", "proposal_section", 4,
    ...                     "# 立项依据\\n...", "04_proposal/sections/01.md",
    ...                     author="pipeline_stage4")
    >>> mgr.lock_artifact("sec01_v0.1")
    >>> mgr.create_artifact("sec01_v0.2", "proposal_section", 4,
    ...                     "# 立项依据（修订）\\n...", "04_proposal/sections/01.md",
    ...                     author="pipeline_stage4")
    >>> mgr.supersede("sec01_v0.1", "sec01_v0.2")
    >>> print(mgr.get_current_version("proposal_section")["version"])
    v0.2
    >>> diff_text = mgr.diff("sec01_v0.1", "sec01_v0.2")
    >>> mgr.rollback("sec01_v0.1")

命令行自检:
    python3 scripts/artifact_manager.py --self-check
"""

from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保可从 scripts/ 目录直接导入公共模块
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from common import now_utc, load_json, save_json, safe_filename, file_lock

__all__ = [
    "ArtifactManager",
    "ARTIFACT_STATUS_FLOW",
    "ARTIFACT_STATUS_LABELS",
]

# ---------------------------------------------------------------------------
# 产物状态机
# ---------------------------------------------------------------------------
# draft → in_review → locked → downstream → superseded/archived
ARTIFACT_STATUS_FLOW: Dict[str, set] = {
    "draft": {"in_review", "locked"},
    "in_review": {"locked", "draft"},
    "locked": {"downstream", "superseded", "archived"},
    "downstream": {"superseded", "archived"},
    "superseded": set(),  # 终态（可经 rollback 恢复）
    "archived": set(),    # 终态
}

ARTIFACT_STATUS_LABELS: Dict[str, str] = {
    "draft": "草稿",
    "in_review": "评审中",
    "locked": "已锁定",
    "downstream": "已下发下游",
    "superseded": "已替换",
    "archived": "已归档",
}

_VALID_DIRECTIONS = ("upstream", "downstream")


class ArtifactManager:
    """产物版本管理器。

    每个 proposal 目录对应一个 ArtifactManager 实例，管理该 proposal 下
    `00_pipeline/artifacts.json` 注册表与 `.artifacts/` 版本快照目录。

    线程安全：所有写操作通过 common.file_lock（fcntl.flock 跨进程锁）保护
    read-modify-write 临界区，锁键基于 proposal_dir 路径哈希，不同 proposal 互不阻塞。
    """

    def __init__(self, proposal_dir: Path | str) -> None:
        """初始化产物管理器。

        Args:
            proposal_dir: proposal 根目录（Path 或字符串），产物文件以此目录为根。
        """
        self.proposal_dir = Path(proposal_dir)
        self.pipeline_dir = self.proposal_dir / "00_pipeline"
        self.registry_path = self.pipeline_dir / "artifacts.json"
        self.versions_dir = self.pipeline_dir / ".artifacts"
        # 跨进程锁键：基于 proposal_dir 绝对路径哈希，避免不同 proposal 互相阻塞
        self._lock_name = (
            "artifacts-"
            + hashlib.md5(str(self.proposal_dir.resolve()).encode("utf-8")).hexdigest()[:12]
        )
        # 确保目录结构存在
        self.pipeline_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _compute_hash(self, content: str) -> str:
        """计算内容的 SHA-256 哈希，返回 'sha256:<hex>' 格式。"""
        return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _snapshot_path(self, artifact_id: str, file_path: str) -> Path:
        """返回某产物版本的内容快照路径。

        快照以 artifact_id 命名，保留原文件扩展名，存放于 .artifacts/ 目录。
        """
        ext = Path(file_path).suffix or ".md"
        return self.versions_dir / f"{safe_filename(artifact_id)}{ext}"

    def _safe_live_path(self, file_path: str) -> Path:
        """计算实时文件路径，并校验位于 proposal_dir 内（防路径遍历）。"""
        base = self.proposal_dir.resolve()
        live = (self.proposal_dir / file_path).resolve()
        try:
            live.relative_to(base)
        except ValueError:
            raise ValueError(f"file_path 必须位于 proposal_dir 内: {file_path}")
        return live

    def _load_registry(self) -> Dict[str, Any]:
        """加载 artifacts.json 注册表（纯读，不加锁）。"""
        data = load_json(self.registry_path, default=None)
        if not isinstance(data, dict) or "artifacts" not in data:
            return {"artifacts": {}}
        if not isinstance(data["artifacts"], dict):
            data["artifacts"] = {}
        return data

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """保存 artifacts.json 注册表（原子写入，应在锁内调用）。"""
        save_json(self.registry_path, data)

    def _next_version_locked(self, artifacts: Dict[str, Any], artifact_type: str) -> str:
        """根据同类型已有产物递增生成下一个 v0.x 版本号（须在锁内调用）。"""
        max_minor = 0
        for a in artifacts.values():
            if a.get("artifact_type") != artifact_type:
                continue
            v = str(a.get("version", "v0.0"))
            parts = v.lstrip("v").split(".")
            if len(parts) == 2:
                try:
                    minor = int(parts[1])
                    if minor > max_minor:
                        max_minor = minor
                except ValueError:
                    continue
        return f"v0.{max_minor + 1}"

    def _next_seq_locked(self, artifacts: Dict[str, Any]) -> int:
        """生成下一个单调递增序列号（须在锁内调用），用于可靠的版本时序排序。"""
        seqs = [a.get("seq", 0) for a in artifacts.values() if isinstance(a, dict)]
        return (max(seqs) + 1) if seqs else 1

    def _read_snapshot(self, artifact_id: str, file_path: str) -> str:
        """读取某版本的内容快照；快照缺失时降级读实时文件，再缺失返回空串。"""
        snap = self._snapshot_path(artifact_id, file_path)
        if snap.exists():
            return snap.read_text(encoding="utf-8")
        if file_path:
            live = self._safe_live_path(file_path)
            if live.exists():
                return live.read_text(encoding="utf-8")
        return ""

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------
    def create_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        stage: int,
        content: str,
        file_path: str,
        author: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建新产物：写入实时文件与版本快照，记录元数据。

        Args:
            artifact_id: 产物唯一标识（如同类型多版本，建议含版本号后缀）。
            artifact_type: 产物类型（如 proposal_section / self_check）。
            stage: 所属管线阶段编号。
            content: 产物文本内容。
            file_path: 相对 proposal_dir 的文件路径（实时文件位置）。
            author: 创建者标识（如 pipeline_stage4）。
            version: 显式版本号；为 None 时自动生成 v0.x。

        Returns:
            新产物的元数据（副本）。

        Raises:
            ValueError: artifact_id/type 为空、ID 已存在、file_path 越界。
        """
        if not artifact_id or not artifact_type:
            raise ValueError("artifact_id 和 artifact_type 不能为空")
        if not isinstance(content, str):
            content = str(content)

        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts: Dict[str, Any] = data["artifacts"]
            if artifact_id in artifacts:
                raise ValueError(f"产物ID已存在: {artifact_id}")

            if version is None:
                version = self._next_version_locked(artifacts, artifact_type)
            seq = self._next_seq_locked(artifacts)

            # 写入实时文件
            live_path = self._safe_live_path(file_path)
            live_path.parent.mkdir(parents=True, exist_ok=True)
            live_path.write_text(content, encoding="utf-8")

            # 写入版本快照（历史归档，供 diff/rollback 使用）
            snap = self._snapshot_path(artifact_id, file_path)
            snap.parent.mkdir(parents=True, exist_ok=True)
            snap.write_text(content, encoding="utf-8")

            content_hash = self._compute_hash(content)
            meta: Dict[str, Any] = {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "stage": stage,
                "version": version,
                "seq": seq,
                "status": "draft",
                "file_path": file_path,
                "content_hash": content_hash,
                "created_at": now_utc(),
                "locked_at": None,
                "author": author,
                "lineage": {"upstream": [], "downstream": []},
            }
            artifacts[artifact_id] = meta
            self._save_registry(data)
            return dict(meta)

    def lock_artifact(self, artifact_id: str) -> Dict[str, Any]:
        """锁定产物：状态置为 locked，记录 locked_at。锁定后内容不可变。

        已锁定则幂等返回；终态（superseded/archived）产物不可锁定。
        """
        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts = data["artifacts"]
            if artifact_id not in artifacts:
                raise KeyError(f"产物不存在: {artifact_id}")
            a = artifacts[artifact_id]
            if a["status"] == "locked":
                return dict(a)
            if a["status"] in ("superseded", "archived"):
                raise ValueError(f"终态产物不可锁定: {a['status']}")
            a["status"] = "locked"
            a["locked_at"] = now_utc()
            self._save_registry(data)
            return dict(a)

    def supersede(self, artifact_id: str, new_artifact_id: str) -> Dict[str, Any]:
        """将旧版本标记为 superseded，新版本成为当前版本。

        要求两者属于同一 artifact_type。旧版本的原状态记录在
        `pre_supersede_status`，供 rollback 恢复。
        """
        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts = data["artifacts"]
            if artifact_id not in artifacts:
                raise KeyError(f"旧产物不存在: {artifact_id}")
            if new_artifact_id not in artifacts:
                raise KeyError(f"新产物不存在: {new_artifact_id}")
            old = artifacts[artifact_id]
            new = artifacts[new_artifact_id]
            if old["artifact_type"] != new["artifact_type"]:
                raise ValueError("产物类型不一致，不可替换")

            old["pre_supersede_status"] = old["status"]
            old["status"] = "superseded"
            old["superseded_at"] = now_utc()
            old["superseded_by"] = new_artifact_id
            new["supersedes"] = artifact_id
            self._save_registry(data)
            return dict(new)

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """获取产物元数据（副本）；不存在返回 None。"""
        data = self._load_registry()
        a = data["artifacts"].get(artifact_id)
        return dict(a) if a else None

    def get_current_version(self, artifact_type: str) -> Optional[Dict[str, Any]]:
        """获取某类型产物的当前（非 superseded/archived）版本。

        若存在多个当前版本，返回 seq 最大（最新创建）者；无则返回 None。
        """
        data = self._load_registry()
        candidates = [
            a for a in data["artifacts"].values()
            if a.get("artifact_type") == artifact_type
            and a.get("status") not in ("superseded", "archived")
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x.get("seq", 0), reverse=True)
        return dict(candidates[0])

    def list_artifacts(
        self,
        stage: Optional[int] = None,
        artifact_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """列出产物，支持按 stage / artifact_type / status 过滤。"""
        data = self._load_registry()
        result: List[Dict[str, Any]] = []
        for a in data["artifacts"].values():
            if stage is not None and a.get("stage") != stage:
                continue
            if artifact_type is not None and a.get("artifact_type") != artifact_type:
                continue
            if status is not None and a.get("status") != status:
                continue
            result.append(dict(a))
        result.sort(key=lambda x: (x.get("artifact_type", ""), x.get("seq", 0)))
        return result

    def rollback(self, artifact_id: str) -> Dict[str, Any]:
        """回滚到指定版本：将同类型中更新的版本标记为 superseded，恢复该版本为 current。

        - 同类型且 seq 大于目标的产物 → 标记 superseded（记录 pre_supersede_status）。
        - 目标若处于 superseded → 恢复为 pre_supersede_status（无记录则按 locked_at 推断）。
        - 从目标快照还原实时文件内容，并刷新 content_hash。
        """
        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts = data["artifacts"]
            if artifact_id not in artifacts:
                raise KeyError(f"产物不存在: {artifact_id}")
            target = artifacts[artifact_id]
            atype = target.get("artifact_type")
            target_seq = target.get("seq", 0)

            # 1. 将同类型中更新的版本标记为 superseded
            for aid, a in artifacts.items():
                if aid == artifact_id:
                    continue
                if a.get("artifact_type") != atype:
                    continue
                if a.get("seq", 0) > target_seq and a.get("status") not in ("superseded", "archived"):
                    a["pre_supersede_status"] = a["status"]
                    a["status"] = "superseded"
                    a["superseded_at"] = now_utc()
                    a["superseded_by"] = artifact_id

            # 2. 恢复目标为 current
            if target.get("status") == "superseded":
                restored = target.get("pre_supersede_status")
                if not restored:
                    restored = "locked" if target.get("locked_at") else "draft"
                target["status"] = restored
                target.pop("pre_supersede_status", None)
                target.pop("superseded_at", None)
                target.pop("superseded_by", None)

            # 3. 从快照还原实时文件
            file_path = target.get("file_path")
            if file_path:
                snap = self._snapshot_path(artifact_id, file_path)
                if snap.exists():
                    content = snap.read_text(encoding="utf-8")
                    live = self._safe_live_path(file_path)
                    live.parent.mkdir(parents=True, exist_ok=True)
                    live.write_text(content, encoding="utf-8")
                    target["content_hash"] = self._compute_hash(content)

            self._save_registry(data)
            return dict(target)

    def diff(self, artifact_id_a: str, artifact_id_b: str) -> str:
        """返回两个版本文件内容的 unified diff（基于各自快照）。"""
        data = self._load_registry()
        arts = data["artifacts"]
        if artifact_id_a not in arts:
            raise KeyError(f"产物不存在: {artifact_id_a}")
        if artifact_id_b not in arts:
            raise KeyError(f"产物不存在: {artifact_id_b}")
        a = arts[artifact_id_a]
        b = arts[artifact_id_b]
        content_a = self._read_snapshot(artifact_id_a, a.get("file_path", ""))
        content_b = self._read_snapshot(artifact_id_b, b.get("file_path", ""))
        diff_lines = difflib.unified_diff(
            content_a.splitlines(keepends=False),
            content_b.splitlines(keepends=False),
            fromfile=f"{artifact_id_a} ({a.get('version', '?')})",
            tofile=f"{artifact_id_b} ({b.get('version', '?')})",
            lineterm="",
        )
        return "\n".join(diff_lines)

    def add_lineage(
        self, artifact_id: str, direction: str, lineage_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """添加血缘关系（upstream/downstream），按 (type, id) 去重。"""
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(f"direction 必须为 {('upstream', 'downstream')}")
        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts = data["artifacts"]
            if artifact_id not in artifacts:
                raise KeyError(f"产物不存在: {artifact_id}")
            a = artifacts[artifact_id]
            lineage = a.setdefault("lineage", {"upstream": [], "downstream": []})
            entry = dict(lineage_entry)
            key = (entry.get("type"), entry.get("id"))
            existing = lineage[direction]
            if not any((e.get("type"), e.get("id")) == key for e in existing):
                existing.append(entry)
            self._save_registry(data)
            return dict(a)

    def get_lineage(
        self, artifact_id: str, direction: Optional[str] = None
    ) -> Any:
        """获取血缘关系。

        Args:
            artifact_id: 产物ID。
            direction: 'upstream' / 'downstream'；为 None 时返回 {'upstream':..., 'downstream':...}。

        Raises:
            KeyError: 产物不存在。
            ValueError: direction 非法。
        """
        data = self._load_registry()
        a = data["artifacts"].get(artifact_id)
        if a is None:
            raise KeyError(f"产物不存在: {artifact_id}")
        lineage = a.get("lineage", {"upstream": [], "downstream": []})
        if direction is None:
            return {
                "upstream": list(lineage.get("upstream", [])),
                "downstream": list(lineage.get("downstream", [])),
            }
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(f"direction 必须为 {('upstream', 'downstream')}")
        return list(lineage.get(direction, []))

    def set_status(self, artifact_id: str, new_status: str) -> Dict[str, Any]:
        """显式设置产物状态（用于推进到 in_review / downstream / archived 等状态）。

        locked 状态在首次进入时自动记录 locked_at。
        """
        if new_status not in ARTIFACT_STATUS_FLOW:
            raise ValueError(f"非法状态: {new_status}")
        with file_lock(self._lock_name):
            data = self._load_registry()
            artifacts = data["artifacts"]
            if artifact_id not in artifacts:
                raise KeyError(f"产物不存在: {artifact_id}")
            a = artifacts[artifact_id]
            a["status"] = new_status
            if new_status == "locked" and not a.get("locked_at"):
                a["locked_at"] = now_utc()
            self._save_registry(data)
            return dict(a)


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：创建→锁定→新版本替换→diff→回滚→血缘关系，使用临时目录隔离。"""
    import tempfile

    print("=" * 50)
    print("◐ artifact_manager 自检")
    print("=" * 50)

    with tempfile.TemporaryDirectory() as tmp:
        proposal_dir = Path(tmp) / "T1_proposal"
        mgr = ArtifactManager(proposal_dir)

        # [1/6] 创建产物
        print("\n[1/6] 创建产物...")
        content_v1 = "# 立项依据\n\n本研究聚焦固体HHG相位匹配。\n"
        meta = mgr.create_artifact(
            "sec01_v0.1", "proposal_section", 4,
            content_v1, "04_proposal/sections/01.md",
            author="pipeline_stage4",
        )
        print(f"  版本: {meta['version']}")
        print(f"  状态: {meta['status']}")
        print(f"  哈希: {meta['content_hash'][:24]}...")
        assert meta["version"] == "v0.1", f"期望 v0.1，实际 {meta['version']}"
        assert meta["status"] == "draft"
        live_file = proposal_dir / "04_proposal" / "sections" / "01.md"
        assert live_file.exists(), "实时文件应已写入"
        assert live_file.read_text(encoding="utf-8") == content_v1, "实时文件内容应一致"
        got = mgr.get_artifact("sec01_v0.1")
        assert got is not None and got["artifact_id"] == "sec01_v0.1"
        assert mgr.get_artifact("not_exist") is None
        print("  ✓ 文件写入 + 元数据记录")

        # [2/6] 锁定产物
        print("\n[2/6] 锁定产物...")
        locked = mgr.lock_artifact("sec01_v0.1")
        print(f"  状态: {locked['status']}")
        print(f"  锁定时间: {locked['locked_at']}")
        assert locked["status"] == "locked"
        assert locked["locked_at"] is not None
        # 幂等：再次锁定不报错
        locked2 = mgr.lock_artifact("sec01_v0.1")
        assert locked2["status"] == "locked"
        print("  ✓ 状态变更 draft → locked（幂等）")

        # [3/6] 创建新版本并替换
        print("\n[3/6] 创建新版本并替换...")
        content_v2 = "# 立项依据\n\n本研究聚焦固体HHG相位匹配机制。\n补充拓扑绝缘体方案。\n"
        meta2 = mgr.create_artifact(
            "sec01_v0.2", "proposal_section", 4,
            content_v2, "04_proposal/sections/01.md",
            author="pipeline_stage4",
        )
        print(f"  新版本: {meta2['version']}")
        assert meta2["version"] == "v0.2", f"期望 v0.2，实际 {meta2['version']}"
        mgr.supersede("sec01_v0.1", "sec01_v0.2")
        old = mgr.get_artifact("sec01_v0.1")
        new = mgr.get_artifact("sec01_v0.2")
        print(f"  旧版本状态: {old['status']}")
        print(f"  新版本状态: {new['status']}")
        assert old["status"] == "superseded"
        assert old.get("superseded_by") == "sec01_v0.2"
        assert old.get("pre_supersede_status") == "locked"
        cur = mgr.get_current_version("proposal_section")
        assert cur["artifact_id"] == "sec01_v0.2", f"当前版本应为 sec01_v0.2，实际 {cur['artifact_id']}"
        print("  ✓ 旧版本 superseded，新版本成为 current")

        # [4/6] diff 对比
        print("\n[4/6] diff 对比...")
        diff_text = mgr.diff("sec01_v0.1", "sec01_v0.2")
        diff_lines = diff_text.splitlines()
        print(f"  diff 行数: {len(diff_lines)}")
        assert diff_text, "diff 不应为空（内容不同）"
        assert "相位匹配机制" in diff_text or "拓扑绝缘体" in diff_text, "diff 应包含新增内容"
        # 相同产物 diff 应为空
        assert mgr.diff("sec01_v0.1", "sec01_v0.1") == "", "相同产物 diff 应为空"
        print("-" * 40)
        print(diff_text)
        print("-" * 40)
        print("  ✓ 返回差异（相同产物 diff 为空）")

        # [5/6] 回滚
        print("\n[5/6] 回滚到 v0.1...")
        restored = mgr.rollback("sec01_v0.1")
        print(f"  恢复后状态: {restored['status']}")
        assert restored["status"] == "locked", f"回滚后应恢复为 locked，实际 {restored['status']}"
        v2_after = mgr.get_artifact("sec01_v0.2")
        assert v2_after["status"] == "superseded", "v0.2 应被标记为 superseded"
        cur_after = mgr.get_current_version("proposal_section")
        assert cur_after["artifact_id"] == "sec01_v0.1", "回滚后当前版本应为 v0.1"
        # 实时文件应恢复为 v0.1 内容
        assert live_file.read_text(encoding="utf-8") == content_v1, "实时文件应恢复为 v0.1 内容"
        print("  ✓ 版本恢复 + 实时文件还原")

        # [6/6] 血缘关系
        print("\n[6/6] 血缘关系添加与查询...")
        mgr.add_lineage(
            "sec01_v0.1", "upstream",
            {"type": "scientific_question", "id": "T1-Q1", "contribution": "提供问题框架"},
        )
        mgr.add_lineage(
            "sec01_v0.1", "downstream",
            {"type": "self_check", "id": "check_01_v0.1"},
        )
        # 去重测试：相同 (type, id) 不重复添加
        mgr.add_lineage(
            "sec01_v0.1", "upstream",
            {"type": "scientific_question", "id": "T1-Q1", "contribution": "重复条目应被忽略"},
        )
        lineage = mgr.get_lineage("sec01_v0.1")
        print(f"  upstream: {len(lineage['upstream'])} 条")
        print(f"  downstream: {len(lineage['downstream'])} 条")
        assert len(lineage["upstream"]) == 1, "upstream 去重后应为 1 条"
        assert len(lineage["downstream"]) == 1
        up = mgr.get_lineage("sec01_v0.1", direction="upstream")
        assert up[0]["id"] == "T1-Q1"
        assert up[0]["contribution"] == "提供问题框架", "去重应保留首次条目"
        print("  ✓ 血缘添加 + 去重 + 定向查询")

        # 附加：list_artifacts 过滤
        print("\n[附加] list_artifacts 过滤...")
        all_arts = mgr.list_artifacts()
        print(f"  全部产物: {len(all_arts)}")
        assert len(all_arts) == 2
        locked_list = mgr.list_artifacts(status="locked")
        print(f"  locked 状态: {len(locked_list)}")
        assert len(locked_list) == 1 and locked_list[0]["artifact_id"] == "sec01_v0.1"
        stage4 = mgr.list_artifacts(stage=4, artifact_type="proposal_section")
        assert len(stage4) == 2
        print("  ✓ 过滤正确")

        # 附加：路径越界防护
        print("\n[附加] 路径越界防护...")
        try:
            mgr.create_artifact(
                "bad_v0.1", "proposal_section", 4,
                "x", "../../../etc/bad.md", author="test",
            )
            raise AssertionError("应拒绝越界 file_path")
        except ValueError as e:
            print(f"  ✓ 拒绝越界路径: {e}")

    print("\n" + "=" * 50)
    print("✓ artifact_manager 自检全部通过")
    print("=" * 50)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="产物版本管理器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    else:
        parser.print_help()
