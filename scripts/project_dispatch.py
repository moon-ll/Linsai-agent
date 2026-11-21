#!/usr/bin/env python3
"""项目意见与执行追踪持久化层 —— 林赛 CoPilot 项目总控的数据底座。

用途：
    项目总控中心需要记录两类「用户意图 → hermes 执行」数据：
    1. 项目意见（opinion）：用户对某项目的想法/建议/反馈，独立于任务，
       可选地反馈给 hermes 作为上下文输入。
    2. 执行追踪（dispatch）：用户把任务（或意见）派给后端 hermes 执行，
       需要持久化「派了什么、状态如何、结果摘要」，补齐 oneshot 的
       fire-and-forget 缺口。

    本模块是这两类数据的 CRUD 底座，采用与 paper_pool.json /
    nsfc-decisions.json 一致的轻量 JSON 文件模式（零依赖、原子写）。

数据存储：
    memory/project-dispatch.json
    {
      "opinions":   [{id, project, content, created_at, status, fed_to_hermes}],
      "dispatches": [{id, task_id, prompt, project, started_at, finished_at,
                      status, output_snippet, source, triggered_by}]
    }

架构关系：
    林赛 Web（指挥台）→ 本模块（记录/追踪）→ hermes_bridge.oneshot（执行）
    本模块只负责「记录与查询」，不直接调用 hermes；派活动作由 web_server
    组合本模块 + hermes_bridge 完成（解耦：本模块可单独自检通过）。

用法示例：
    >>> from project_dispatch import add_opinion, record_dispatch, finish_dispatch
    >>> op = add_opinion("NSFC-强场超快", "建议 T1 课题补充量子几何推导")
    >>> did = record_dispatch("TASK-20260623-...", "深分析 arXiv 2403.15337",
    ...                        "NSFC-强场超快", source="manual")
    >>> finish_dispatch(did, success=True, output="...")

规范：
    - 仅使用 Python 3 标准库
    - PROJECT_ROOT 通过 Path(__file__).parent.parent 推导
    - JSON 输出 ensure_ascii=False, indent=2
    - 时间戳 UTC ISO 格式：%Y-%m-%dT%H:%M:%SZ
    - 原子写（先写临时文件再 rename，避免 daemon 线程写坏文件）
"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import now_utc as _now_utc

from paths import PROJECT_ROOT, MEMORY_DIR
DATA_FILE = MEMORY_DIR / "project-dispatch.json"

# 意见状态
OPINION_OPEN = "open"
OPINION_RESOLVED = "resolved"

# 执行状态
DISPATCH_RUNNING = "running"
DISPATCH_DONE = "done"
DISPATCH_FAILED = "failed"
DISPATCH_TIMEOUT = "timeout"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _gen_id(prefix: str) -> str:
    """生成带微秒时间戳 + 随机后缀的 ID，避免并发/快速调用冲突。

    历史 bug：原先 [:16] 截断到百分秒(10ms)精度，同一 10ms 窗口内多次调用
    会撞 ID（实测 20 次连续调用全相同），导致 finish_dispatch 改错记录、
    第二条记录永远卡在 running。现改为完整 20 位时间戳(含 6 位微秒) +
    6 位十六进制随机后缀，单机冲突概率可忽略。
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")  # 20 位
    suffix = secrets.token_hex(3)  # 6 位随机十六进制
    return f"{prefix}_{ts}{suffix}"


def _ensure_file() -> None:
    """确保数据文件与目录存在，初始化空结构。"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        _atomic_write({"opinions": [], "dispatches": []})


def _atomic_write(data: dict) -> None:
    """原子写：先写 .tmp 再 rename，防止 daemon 线程中途崩溃写坏文件。"""
    tmp = DATA_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(DATA_FILE)


def _load() -> dict:
    """加载数据文件，失败则返回空结构（降级，不抛异常）。"""
    if not DATA_FILE.exists():
        return {"opinions": [], "dispatches": []}
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"opinions": [], "dispatches": []}
        data.setdefault("opinions", [])
        data.setdefault("dispatches", [])
        return data
    except (json.JSONDecodeError, OSError):
        return {"opinions": [], "dispatches": []}


def _save(data: dict) -> None:
    _atomic_write(data)


# ============================================
# 项目意见（opinion）
# ============================================
def add_opinion(project: str, content: str, fed_to_hermes: bool = False) -> Dict[str, Any]:
    """新增一条项目意见。

    Args:
        project: 所属项目（如 "NSFC-强场超快"），允许空串表示通用
        content: 意见正文
        fed_to_hermes: 是否已反馈给 hermes（由 web_server 在调用 hermes 后回填）

    Returns:
        新建的意见字典
    """
    _ensure_file()
    data = _load()
    opinion = {
        "id": _gen_id("op"),
        "project": project.strip(),
        "content": content.strip(),
        "created_at": _now_utc(),
        "status": OPINION_OPEN,
        "fed_to_hermes": fed_to_hermes,
    }
    data["opinions"].append(opinion)
    _save(data)
    print(f"✓ 意见已记录: {opinion['id']} → {project or '通用'}")
    return opinion


def list_opinions(project: str = "", status: str = "") -> List[Dict[str, Any]]:
    """查询意见列表，支持按项目和状态过滤。新→旧排序。"""
    data = _load()
    items = data.get("opinions", [])
    if project:
        items = [o for o in items if o.get("project") == project]
    if status:
        items = [o for o in items if o.get("status") == status]
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items


def resolve_opinion(op_id: str) -> Optional[Dict[str, Any]]:
    """标记意见为已解决。返回更新后的意见，未找到返回 None。"""
    data = _load()
    for o in data.get("opinions", []):
        if o.get("id") == op_id:
            o["status"] = OPINION_RESOLVED
            o["resolved_at"] = _now_utc()
            _save(data)
            print(f"✓ 意见已标记解决: {op_id}")
            return o
    return None


def mark_opinion_fed(op_id: str) -> None:
    """标记意见已反馈给 hermes（反馈动作成功后调用）。"""
    data = _load()
    for o in data.get("opinions", []):
        if o.get("id") == op_id:
            o["fed_to_hermes"] = True
            _save(data)
            return


# ============================================
# 执行追踪（dispatch）
# ============================================
def record_dispatch(
    task_id: str,
    prompt: str,
    project: str,
    source: str = "manual",
    triggered_by: str = "",
) -> Dict[str, Any]:
    """记录一条派活（派发前调用，status=running）。

    Args:
        task_id: 关联任务 ID（可空，纯意见派活时为空）
        prompt: 派给 hermes 的实际指令文本
        project: 所属项目
        source: 派活来源 "manual"(卡片按钮) | "create"(创建即派) | "opinion"(意见派发)
        triggered_by: 触发源标识（如意见 ID），便于反查

    Returns:
        dispatch 字典，含 id（供 finish_dispatch 回写）
    """
    _ensure_file()
    data = _load()
    dispatch = {
        "id": _gen_id("dsp"),
        "task_id": task_id,
        "prompt": prompt.strip(),
        "project": project.strip(),
        "started_at": _now_utc(),
        "finished_at": None,
        "status": DISPATCH_RUNNING,
        "output_snippet": "",
        "source": source,
        "triggered_by": triggered_by,
    }
    data["dispatches"].append(dispatch)
    _save(data)
    print(f"✓ 派活已记录: {dispatch['id']} → {project or '通用'}")
    return dispatch


def finish_dispatch(dispatch_id: str, success: bool, output: str, timeout: bool = False) -> Optional[Dict[str, Any]]:
    """派活完成后回写结果。

    Args:
        dispatch_id: record_dispatch 返回的 id
        success: hermes 是否成功返回
        output: hermes stdout（会被截断到 2000 字符存 snippet）
        timeout: 是否因超时结束
    """
    data = _load()
    for d in data.get("dispatches", []):
        if d.get("id") == dispatch_id:
            d["finished_at"] = _now_utc()
            if timeout:
                d["status"] = DISPATCH_TIMEOUT
            elif success:
                d["status"] = DISPATCH_DONE
            else:
                d["status"] = DISPATCH_FAILED
            # 截断保存输出摘要（完整输出可能很长，只存前 2000 字符）
            d["output_snippet"] = (output or "")[:2000]
            _save(data)
            print(f"✓ 派活回写完成: {dispatch_id} [{d['status']}]")
            return d
    return None


def list_dispatches(project: str = "", status: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    """查询执行记录，新→旧排序，支持项目和状态过滤。"""
    data = _load()
    items = data.get("dispatches", [])
    if project:
        items = [d for d in items if d.get("project") == project]
    if status:
        items = [d for d in items if d.get("status") == status]
    items.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return items[:limit]


def get_task_dispatches(task_id: str) -> List[Dict[str, Any]]:
    """查询某任务的所有派活记录（用于卡片显示「执行中/查看输出」）。"""
    data = _load()
    items = [d for d in data.get("dispatches", []) if d.get("task_id") == task_id]
    items.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return items


# ============================================
# 项目总览（聚合）
# ============================================
def get_project_overview_stats() -> Dict[str, Any]:
    """返回意见和执行两类的统计（任务统计由 web_server 聚合 task_manager）。

    Returns:
        {open_opinions, fed_opinions, running_dispatches,
         done_dispatches, failed_dispatches, recent_dispatches}
    """
    data = _load()
    opinions = data.get("opinions", [])
    dispatches = data.get("dispatches", [])
    return {
        "open_opinions": sum(1 for o in opinions if o.get("status") == OPINION_OPEN),
        "fed_opinions": sum(1 for o in opinions if o.get("fed_to_hermes")),
        "total_opinions": len(opinions),
        "running_dispatches": sum(1 for d in dispatches if d.get("status") == DISPATCH_RUNNING),
        "done_dispatches": sum(1 for d in dispatches if d.get("status") == DISPATCH_DONE),
        "failed_dispatches": sum(1 for d in dispatches if d.get("status") in (DISPATCH_FAILED, DISPATCH_TIMEOUT)),
        "total_dispatches": len(dispatches),
        "recent_dispatches": list_dispatches(limit=5),
    }


def _self_check() -> None:
    """自检：意见与派活的完整 CRUD 闭环（隔离临时文件，跑完恢复）。"""
    print("=" * 50)
    print("◐ project_dispatch 自检")
    print("=" * 50)

    # 备份原文件（如有），用隔离环境测试
    backup = None
    if DATA_FILE.exists():
        backup = DATA_FILE.read_bytes()
        DATA_FILE.unlink()

    try:
        print("\n[1/6] 新增意见...")
        op = add_opinion("NSFC-强场超快", "测试意见：T1 推导需补充")
        assert op["id"].startswith("op_"), "意见 ID 格式错"
        assert op["status"] == OPINION_OPEN, "初始状态应为 open"
        print(f"  ✓ 创建意见 {op['id']}")

        print("\n[2/6] 查询意见...")
        ops = list_opinions(project="NSFC-强场超快")
        assert len(ops) == 1, f"应查到 1 条，实际 {len(ops)}"
        print(f"  ✓ 查到 {len(ops)} 条意见")

        print("\n[3/6] 标记意见已反馈 + 已解决...")
        mark_opinion_fed(op["id"])
        resolved = resolve_opinion(op["id"])
        assert resolved and resolved["fed_to_hermes"] is True, "反馈标记未生效"
        assert resolved["status"] == OPINION_RESOLVED, "解决状态未生效"
        print(f"  ✓ 意见标记完成")

        print("\n[4/6] 记录派活（running）...")
        disp = record_dispatch("TASK-TEST", "深分析 arXiv 测试", "NSFC-强场超快", "manual")
        assert disp["status"] == DISPATCH_RUNNING, "初始状态应为 running"
        assert disp["id"].startswith("dsp_"), "派活 ID 格式错"
        print(f"  ✓ 记录派活 {disp['id']}")

        print("\n[5/6] 回写派活结果...")
        finished = finish_dispatch(disp["id"], success=True, output="这是 hermes 的输出结果")
        assert finished and finished["status"] == DISPATCH_DONE, "派活状态未更新"
        assert finished["output_snippet"] == "这是 hermes 的输出结果", "输出摘要丢失"
        print(f"  ✓ 派活回写完成 [{finished['status']}]")

        print("\n[6/7] 聚合统计...")
        stats = get_project_overview_stats()
        assert stats["total_opinions"] == 1, "意见统计错"
        assert stats["done_dispatches"] == 1, "派活统计错"
        assert stats["total_dispatches"] == 1, "派活总数错"
        print(f"  ✓ 意见 {stats['total_opinions']} / 派活 {stats['total_dispatches']}")

        print("\n[7/7] 快速连续派活 ID 唯一性（回归 _gen_id 撞 ID bug）...")
        fast_ids = [record_dispatch("TASK-ID-UNIQ", "[SELF-CHECK] 唯一性测试",
                                     "[SELF-CHECK]")["id"] for _ in range(50)]
        assert len(set(fast_ids)) == 50, (
            f"_gen_id 撞 ID！50 次调用仅 {len(set(fast_ids))} 个唯一。"
            f"示例：{fast_ids[:3]}"
        )
        # 全部回写清理（避免污染）
        for fid in fast_ids:
            finish_dispatch(fid, success=True, output="self-check 清理")
        print(f"  ✓ 50 次快速派活 ID 全唯一（示例 {fast_ids[0]}）")

        print("\n✓ project_dispatch 自检通过")
    finally:
        # 恢复原文件
        if backup is not None:
            DATA_FILE.write_bytes(backup)
        elif DATA_FILE.exists():
            DATA_FILE.unlink()


if __name__ == "__main__":
    _self_check()
