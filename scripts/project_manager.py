#!/usr/bin/env python3
"""课题管理器 — 课题CRUD、状态机、多课题并行管理。

课题是课题指导模块的顶层实体。每个课题包含独立的知识库子库、记忆库、
长期记忆文件(PROJECT-MEMORY.md)和单元序列。课题推进保持独立，
讨论阶段可通过 @课题知识库 跨课题共享信息。

用法:
    >>> from project_manager import create_project, get_project, list_projects
    >>> pid, path = create_project("固体HHG相位匹配机制研究",
    ...     goal="阐明拓扑绝缘体中HHG的相位匹配条件，建立理论模型")
    >>> proj = get_project(pid)
    >>> print(proj["status"])  # planning
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc, load_json as _read_json, save_json as _write_json, safe_filename

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# 日志接入（可选，logger 模块不存在时降级为静默）
try:
    from logger import get_logger
    _log = get_logger("project_manager")
except Exception:
    _log = None

# 课题数据存储根目录
PROJECTS_DIR = _PROJECT_ROOT / "projects"


# ---------------------------------------------------------------------------
# 课题状态机
# ---------------------------------------------------------------------------
PROJECT_STATUS_FLOW: Dict[str, set] = {
    "planning": {"active"},
    "active": {"paused", "completed"},
    "paused": {"active", "completed"},
    "completed": {"active"},  # 允许重新激活（如结题后发现新问题）
}

PROJECT_STATUS_LABELS = {
    "planning": "规划中",
    "active": "推进中",
    "paused": "已暂停",
    "completed": "已结题",
}


def _ensure_dirs() -> None:
    """确保课题目录结构存在。"""
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _gen_project_id(name: str) -> str:
    """生成课题ID: PRJ-YYYYMMDD-名称前10字。"""
    date_prefix = _now_utc()[:10].replace("-", "")
    safe_name = safe_filename(name)[:10]
    return f"PRJ-{date_prefix}-{safe_name}"


def _project_path(project_id: str) -> Path:
    """课题数据文件路径。"""
    return PROJECTS_DIR / f"{project_id}.json"


def _project_dir(project_id: str) -> Path:
    """课题工作目录（知识库/记忆库/长期记忆存放于此）。"""
    return PROJECTS_DIR / project_id


def _ensure_project_dirs(project_id: str) -> Path:
    """创建课题工作目录结构。"""
    pdir = _project_dir(project_id)
    (pdir / "kb" / "raw" / "proposals").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "raw" / "references").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "raw" / "data").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "parsed" / "concepts").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "parsed" / "methods").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "parsed" / "literature").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "summary" / "unit-reports").mkdir(parents=True, exist_ok=True)
    (pdir / "kb" / "summary" / "milestone-reviews").mkdir(parents=True, exist_ok=True)
    (pdir / "memory" / "conversations").mkdir(parents=True, exist_ok=True)
    (pdir / "memory" / "snippets").mkdir(parents=True, exist_ok=True)
    return pdir


def create_project(
    name: str,
    goal: str = "",
    description: str = "",
) -> Tuple[str, Path]:
    """创建新课题，返回 (project_id, project_file_path)。

    Args:
        name: 课题名称（如"固体HHG相位匹配机制研究"）
        goal: 课题目标（一句话描述最终交付物）
        description: 课题详细描述

    课题创建后自动：
        1. 建立工作目录（kb/raw, kb/parsed, kb/summary, memory/conversations, memory/snippets）
        2. 生成 PROJECT-MEMORY.md 骨架文件
        3. 状态设为 planning
    """
    _ensure_dirs()
    project_id = _gen_project_id(name)

    # ID 去重
    counter = 1
    base_id = project_id
    while _project_path(project_id).exists():
        project_id = f"{base_id}-{counter}"
        counter += 1

    pdir = _ensure_project_dirs(project_id)

    project = {
        "project_id": project_id,
        "name": name,
        "goal": goal,
        "description": description,
        "status": "planning",
        "phase": "init",  # init / unit_N / completed
        "created_at": _now_utc(),
        "updated_at": _now_utc(),
        "completed_at": None,
        "knowledge_vault": f"projects/{project_id}/kb/",
        "memory_archive": f"projects/{project_id}/memory/",
        "project_memory": f"projects/{project_id}/PROJECT-MEMORY.md",
        "current_unit": None,
        "units": [],
        "milestones": [],
        "members": {"user": "PI", "lin_sai": "副导师"},
        "tags": [],
    }

    path = _project_path(project_id)
    _write_json(path, project)

    # 生成 PROJECT-MEMORY.md 骨架
    _init_project_memory(project_id, name, goal)

    if _log:
        _log.info(f"课题已创建: {project_id} | 名称={name} | 状态=planning")
    return project_id, path


def _init_project_memory(project_id: str, name: str, goal: str) -> None:
    """生成 PROJECT-MEMORY.md 骨架文件（≤100行核心记忆）。"""
    pdir = _project_dir(project_id)
    mem_path = pdir / "PROJECT-MEMORY.md"
    content = f"""# 课题记忆：{name}

## 核心信息
- 课题ID: {project_id}
- 目标: {goal}
- 当前阶段: 初始化
- 知识库: projects/{project_id}/kb/
- 记忆库: projects/{project_id}/memory/

## 课题进展
- [○] 初始化阶段，等待林赛制定总体计划

## 关键决策
（暂无）

## 用户偏好（本课题）
（暂无）

## 知识库要点
（暂无）
"""
    mem_path.write_text(content, encoding="utf-8")


def get_project(project_id: str) -> dict:
    """读取课题信息，返回课题字典。"""
    path = _project_path(project_id)
    if not path.exists():
        raise FileNotFoundError(f"✗ 未找到课题: {project_id}")
    return _read_json(path, default={})


def update_project(project_id: str, **fields) -> dict:
    """更新课题字段，自动更新 updated_at。

    status 字段会走状态机校验，其余字段直接更新。
    """
    path = _project_path(project_id)
    if not path.exists():
        raise FileNotFoundError(f"✗ 未找到课题: {project_id}")

    project = _read_json(path, default={})
    if not project:
        raise ValueError(f"✗ 课题文件损坏: {project_id}")

    # status 走状态机
    if "status" in fields:
        new_status = fields["status"]
        old_status = project.get("status", "planning")
        if new_status not in PROJECT_STATUS_FLOW.get(old_status, set()):
            raise ValueError(
                f"✗ 状态流转不允许: {old_status} → {new_status}。"
                f"允许的后续状态: {PROJECT_STATUS_FLOW.get(old_status, set())}"
            )

    for key, value in fields.items():
        project[key] = value

    project["updated_at"] = _now_utc()
    if fields.get("status") == "completed":
        project["completed_at"] = _now_utc()

    _write_json(path, project)
    return project


def transition_project(project_id: str, new_status: str) -> dict:
    """课题状态流转。"""
    return update_project(project_id, status=new_status)


def list_projects(status: str = "all") -> List[dict]:
    """列出所有课题，可按状态过滤。

    Args:
        status: "all" | "planning" | "active" | "paused" | "completed"
    """
    _ensure_dirs()
    projects = []
    for path in sorted(PROJECTS_DIR.glob("PRJ-*.json")):
        try:
            proj = _read_json(path, default={})
            if not proj:
                continue
            if status == "all" or proj.get("status") == status:
                projects.append(proj)
        except Exception:
            continue
    return projects


def delete_project(project_id: str, confirm: bool = False) -> bool:
    """删除课题。

    Args:
        confirm: 必须为 True 才执行删除（安全机制）
    """
    if not confirm:
        if _log:
            _log.warning("删除课题需要 confirm=True")
        return False

    # 删除课题文件
    path = _project_path(project_id)
    if not path.exists():
        if _log:
            _log.error(f"未找到课题: {project_id}")
        return False

    path.unlink()

    # 删除工作目录
    pdir = _project_dir(project_id)
    if pdir.exists():
        import shutil
        shutil.rmtree(pdir, ignore_errors=True)

    if _log:
        _log.info(f"课题已删除: {project_id}")
    return True


def get_project_memory(project_id: str) -> str:
    """读取课题长期记忆文件 (PROJECT-MEMORY.md) 内容。"""
    pdir = _project_dir(project_id)
    mem_path = pdir / "PROJECT-MEMORY.md"
    if not mem_path.exists():
        return ""
    return mem_path.read_text(encoding="utf-8")


def update_project_memory(project_id: str, content: str) -> None:
    """覆写课题长期记忆文件。"""
    pdir = _project_dir(project_id)
    pdir.mkdir(parents=True, exist_ok=True)
    mem_path = pdir / "PROJECT-MEMORY.md"
    mem_path.write_text(content, encoding="utf-8")


def append_to_project_memory(project_id: str, section: str, line: str) -> None:
    """向课题长期记忆文件的指定区域追加一行。

    Args:
        section: "课题进展" | "关键决策" | "用户偏好" | "知识库要点"
        line: 要追加的文本行
    """
    content = get_project_memory(project_id)
    if not content:
        _init_project_memory(project_id, "未命名课题", "")
        content = get_project_memory(project_id)

    # 找到 section 位置
    section_marker = f"## {section}"
    lines = content.split("\n")
    insert_idx = None
    for i, line_text in enumerate(lines):
        if line_text.strip() == section_marker:
            insert_idx = i + 1
            break

    if insert_idx is not None:
        lines.insert(insert_idx, line)
    else:
        # section 不存在，追加到末尾
        lines.append(f"\n## {section}")
        lines.append(line)

    new_content = "\n".join(lines)

    # 如果超过 100 行，压缩最早的单元进展（保留结构）
    if len(new_content.split("\n")) > 100:
        new_content = _compact_project_memory(new_content)

    update_project_memory(project_id, new_content)


def _compact_project_memory(content: str) -> str:
    """压缩课题记忆文件，保持 ≤100 行。

    策略：将已完成的早期单元进展压缩为单行摘要。
    """
    lines = content.split("\n")
    if len(lines) <= 100:
        return content

    # 找到课题进展区域，压缩已完成的行
    compacted = []
    in_progress_section = False
    completed_count = 0
    for line in lines:
        if "## 课题进展" in line:
            in_progress_section = True
            compacted.append(line)
            continue
        if in_progress_section and line.startswith("## "):
            # 如果有压缩的已完成项，加摘要行
            if completed_count > 0:
                compacted.append(f"- [✓] 前 {completed_count} 个单元已完成（已压缩）")
            in_progress_section = False
            compacted.append(line)
            continue
        if in_progress_section and "[✓]" in line:
            completed_count += 1
            continue  # 跳过已完成的行
        compacted.append(line)

    # 如果还是太长，截断到 100 行
    if len(compacted) > 100:
        compacted = compacted[:97] + ["", "...(已截断)...", ""]

    return "\n".join(compacted)


def add_milestone(project_id: str, name: str, target_unit: str = "", description: str = "") -> dict:
    """添加里程碑节点。"""
    project = get_project(project_id)
    milestone = {
        "name": name,
        "target_unit": target_unit,
        "description": description,
        "status": "pending",  # pending | reached
        "created_at": _now_utc(),
    }
    project.setdefault("milestones", []).append(milestone)
    update_project(project_id, milestones=project["milestones"])
    if _log:
        _log.info(f"里程碑已添加: {name}（课题 {project_id}）")
    return milestone


def get_project_overview(project_id: str) -> dict:
    """获取课题概览信息（含单元/任务统计）。"""
    project = get_project(project_id)
    overview = {
        "project_id": project["project_id"],
        "name": project["name"],
        "goal": project["goal"],
        "status": project["status"],
        "status_label": PROJECT_STATUS_LABELS.get(project["status"], project["status"]),
        "phase": project.get("phase", "init"),
        "current_unit": project.get("current_unit"),
        "unit_count": len(project.get("units", [])),
        "milestone_count": len(project.get("milestones", [])),
        "created_at": project.get("created_at"),
        "updated_at": project.get("updated_at"),
    }
    return overview


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：验证课题管理链路完整性。"""
    print("=" * 50)
    print("◐ project_manager 自检")
    print("=" * 50)

    print("\n[1/5] 检查目录结构...")
    _ensure_dirs()
    print(f"  projects 目录: {'✓' if PROJECTS_DIR.exists() else '✗'}")

    print("\n[2/5] 创建测试课题...")
    pid, path = create_project("自检测试课题", goal="验证课题管理链路")
    print(f"  课题ID: {pid}")
    print(f"  文件存在: {'✓' if path.exists() else '✗'}")

    print("\n[3/5] 读取课题...")
    proj = get_project(pid)
    print(f"  名称: {proj['name']}")
    print(f"  状态: {proj['status']}")
    print(f"  工作目录存在: {'✓' if _project_dir(pid).exists() else '✗'}")

    print("\n[4/5] 状态流转...")
    proj = transition_project(pid, "active")
    print(f"  planning → active: {'✓' if proj['status'] == 'active' else '✗'}")
    proj = transition_project(pid, "completed")
    print(f"  active → completed: {'✓' if proj['status'] == 'completed' else '✗'}")

    print("\n[5/5] 列出课题...")
    projects = list_projects()
    print(f"  课题总数: {len(projects)}")

    # 清理
    delete_project(pid, confirm=True)
    print("\n✓ project_manager 自检完成")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="课题管理器")
    parser.add_argument("--list", action="store_true", help="列出所有课题")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    elif args.list:
        for p in list_projects():
            print(f"  {p['project_id']} | {p['name']} | {PROJECT_STATUS_LABELS.get(p['status'], p['status'])}")
