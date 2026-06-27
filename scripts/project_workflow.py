#!/usr/bin/env python3
"""课题工作流编排引擎 — 规划→执行→验收→报告循环。

协调 project_manager / unit_manager / task_manager / project_kb / project_memory，
驱动课题按单元循环推进。

工作流状态::

    课题创建 → 总体规划(林赛拆分单元) → 单元循环:
      单元规划(沟通确认验收标准) → 任务分工 → 执行 → 验收讨论 → 单元报告 → 下一单元
    → 课题总结报告 → 结题

用法:
    >>> from project_workflow import plan_units, start_unit_execution, review_unit
    >>> units = plan_units(pid, unit_specs)  # 林赛拆分单元
    >>> start_unit_execution(pid, unit_id)    # 开始执行
    >>> review_unit(pid, unit_id)             # 验收
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc

_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from project_manager import (
    get_project, update_project, transition_project,
    get_project_overview, append_to_project_memory,
    _project_dir,
)
from unit_manager import (
    create_unit, get_unit, update_unit, transition_unit,
    list_units, add_acceptance_criteria, check_acceptance_criterion,
    get_acceptance_status, add_risk, add_task_to_unit, get_unit_tasks,
    add_deliverable, set_progress_report,
)
from project_kb import add_document, get_kb_stats
from project_memory import (
    save_conversation, create_snippet, add_decision,
    add_risk_record, update_progress_in_memory,
    update_kb_summary_in_memory, get_project_context,
)


def plan_units(project_id: str, unit_specs: List[dict]) -> List[str]:
    """根据林赛制定的单元规划，批量创建单元。

    Args:
        project_id: 课题ID
        unit_specs: [{title, acceptance_criteria: [str], description, risks: [str]}]
            每个spec描述一个单元的标题、验收标准和风险

    Returns:
        创建的 unit_id 列表

    创建后自动：
        1. 为每个单元创建 unit 记录
        2. 添加验收标准
        3. 添加风险
        4. 更新课题 phase 为 unit_1
        5. 在 PROJECT-MEMORY.md 追加规划信息
    """
    unit_ids = []
    for i, spec in enumerate(unit_specs):
        title = spec.get("title", f"单元{i+1}")
        criteria = spec.get("acceptance_criteria", [])
        description = spec.get("description", "")
        risks = spec.get("risks", [])

        unit_id, _ = create_unit(project_id, title, acceptance_criteria=criteria, description=description)
        unit_ids.append(unit_id)

        # 添加风险
        for risk_desc in risks:
            add_risk(unit_id, risk_desc, severity="medium")

        # 更新 PROJECT-MEMORY.md
        update_progress_in_memory(project_id, unit_id, title, status="planning")

    # 设置课题为 active 状态
    try:
        transition_project(project_id, "active")
    except ValueError:
        pass  # 可能已经是 active

    # 更新课题 phase
    if unit_ids:
        update_project(project_id, phase=f"unit_1", current_unit=unit_ids[0])

    # 追加规划信息到长期记忆
    plan_summary = f"总体计划: {len(unit_ids)} 个单元"
    for uid in unit_ids:
        unit = get_unit(uid)
        plan_summary += f"\n- {uid}: {unit.get('title', '')}"
    append_to_project_memory(project_id, "知识库要点", f"- 课题规划: {len(unit_ids)} 个单元")

    print(f"✓ 已创建 {len(unit_ids)} 个单元: {', '.join(unit_ids)}")
    return unit_ids


def start_unit_execution(project_id: str, unit_id: str, task_specs: List[dict]) -> List[str]:
    """开始单元执行阶段，创建任务并分工。

    Args:
        project_id: 课题ID
        unit_id: 单元ID
        task_specs: [{title, assignee: "user"|"lin_sai", description, due_date, priority}]

    Returns:
        创建的 task_id 列表
    """
    # 状态流转: planning → executing
    try:
        transition_unit(unit_id, "executing")
    except ValueError as e:
        print(f"⚠ 状态流转失败: {e}")

    task_ids = []
    for spec in task_specs:
        title = spec.get("title", "")
        assignee = spec.get("assignee", "user")
        # 映射 assignee: user → myself, lin_sai → hermes
        assignee_mapped = "myself" if assignee == "user" else "hermes" if assignee == "lin_sai" else "none"

        # 动态导入 task_manager
        try:
            import task_manager as tm
            task_id, _ = tm.create_task(
                title=title,
                description=spec.get("description", ""),
                due_date=spec.get("due_date", ""),
                priority=spec.get("priority", "medium"),
                project=project_id,
                assignee=assignee_mapped,
                unit_id=unit_id,
            )
            add_task_to_unit(unit_id, task_id)
            task_ids.append(task_id)
        except Exception as e:
            print(f"⚠ 创建任务失败 '{title}': {e}")

    # 更新 PROJECT-MEMORY.md
    unit = get_unit(unit_id)
    update_progress_in_memory(project_id, unit_id, unit.get("title", ""), status="active")

    print(f"✓ 单元 {unit_id} 进入执行阶段，创建 {len(task_ids)} 个任务")
    return task_ids


def review_unit(project_id: str, unit_id: str) -> dict:
    """启动单元验收流程。

    Returns:
        {
            unit_id, title,
            acceptance_status: {total, met, unmet, criteria},
            tasks: [...],
            risks: [...],
            ready_for_review: bool  # 是否所有验收标准已满足
        }
    """
    # 状态流转: executing → review
    try:
        transition_unit(unit_id, "review")
    except ValueError as e:
        print(f"⚠ 状态流转失败: {e}")

    unit = get_unit(unit_id)
    ac_status = get_acceptance_status(unit_id)
    tasks = get_unit_tasks(unit_id)
    risks = unit.get("risks", [])

    # 风险回看：标记是否命中
    risk_review = []
    for risk in risks:
        risk_review.append({
            "description": risk.get("description", ""),
            "severity": risk.get("severity", ""),
            "hit": risk.get("hit"),
        })

    result = {
        "unit_id": unit_id,
        "title": unit.get("title", ""),
        "acceptance_status": ac_status,
        "tasks": [{"title": t.get("title", ""), "status": t.get("status", ""), "assignee": t.get("assignee", "")} for t in tasks],
        "risks": risk_review,
        "ready_for_review": ac_status.get("met", 0) == ac_status.get("total", 0),
    }

    print(f"✓ 单元 {unit_id} 进入验收阶段")
    print(f"  验收标准: {ac_status.get('met', 0)}/{ac_status.get('total', 0)} 已满足")
    print(f"  风险回顾: {len(risk_review)} 项")
    return result


def complete_unit(project_id: str, unit_id: str, review_notes: str = "",
                  report_content: str = "") -> dict:
    """完成单元，生成进展报告并推进到下一单元。

    1. 流转单元状态: review → completed
    2. 生成单元进展报告（写入知识库 summary 层）
    3. 更新 PROJECT-MEMORY.md
    4. 检查是否还有下一单元，如有则设为 current_unit
    """
    # 保存验收备注
    if review_notes:
        update_unit(unit_id, review_notes=review_notes)

    # 状态流转
    try:
        transition_unit(unit_id, "completed")
    except ValueError as e:
        print(f"⚠ 状态流转失败: {e}")

    unit = get_unit(unit_id)

    # 生成单元进展报告
    if report_content:
        report_path = f"summary/unit-reports/{unit_id}-report.md"
        add_document(project_id, "summary", "unit-reports",
                     f"{unit_id} 进展报告", report_content,
                     tags=["进展报告", unit_id], unit=unit_id)
        set_progress_report(unit_id, report_path)

    # 更新 PROJECT-MEMORY.md
    update_progress_in_memory(project_id, unit_id, unit.get("title", ""),
                             status="completed", summary=report_content[:200] if report_content else "")

    # 记录决策
    if review_notes:
        add_decision(project_id, f"{unit_id} 验收结论", rationale=review_notes, unit_id=unit_id)

    # 检查下一单元
    project = get_project(project_id)
    units = project.get("units", [])
    try:
        current_idx = units.index(unit_id)
        if current_idx + 1 < len(units):
            next_unit_id = units[current_idx + 1]
            update_project(project_id, current_unit=next_unit_id, phase=f"unit_{current_idx + 2}")
            print(f"✓ 单元 {unit_id} 已完成，下一单元: {next_unit_id}")
            return {"completed": True, "next_unit": next_unit_id, "all_done": False}
        else:
            # 所有单元完成
            update_project(project_id, phase="completed")
            print(f"✓ 所有单元已完成，课题可以结题")
            return {"completed": True, "next_unit": None, "all_done": True}
    except ValueError:
        return {"completed": True, "next_unit": None, "all_done": False}


def get_project_status(project_id: str) -> dict:
    """获取课题完整状态概览（含所有单元和任务）。

    Returns:
        {
            project: {name, goal, status, phase, ...},
            units: [{unit_id, title, status, acceptance, tasks, progress}],
            stats: {total_units, completed_units, total_tasks, ...},
        }
    """
    project = get_project(project_id)
    units_data = []

    for unit_id in project.get("units", []):
        try:
            unit = get_unit(unit_id)
            ac_status = get_acceptance_status(unit_id)
            tasks = get_unit_tasks(unit_id)

            units_data.append({
                "unit_id": unit_id,
                "title": unit.get("title", ""),
                "status": unit.get("status", ""),
                "sequence": unit.get("sequence", 0),
                "acceptance": ac_status,
                "tasks": [{"title": t.get("title", ""), "status": t.get("status", ""),
                          "assignee": t.get("assignee", "")} for t in tasks],
                "task_count": len(tasks),
                "risks": len(unit.get("risks", [])),
                "deliverables": len(unit.get("deliverables", [])),
            })
        except Exception:
            continue

    # 统计
    total_units = len(units_data)
    completed_units = sum(1 for u in units_data if u["status"] == "completed")
    total_tasks = sum(u["task_count"] for u in units_data)

    # 知识库统计
    try:
        kb_stats = get_kb_stats(project_id)
    except Exception:
        kb_stats = {"total": 0}

    return {
        "project": {
            "project_id": project.get("project_id", ""),
            "name": project.get("name", ""),
            "goal": project.get("goal", ""),
            "status": project.get("status", ""),
            "phase": project.get("phase", ""),
            "current_unit": project.get("current_unit", ""),
        },
        "units": units_data,
        "stats": {
            "total_units": total_units,
            "completed_units": completed_units,
            "total_tasks": total_tasks,
            "kb_documents": kb_stats.get("total", 0),
        },
    }


def generate_project_summary(project_id: str) -> str:
    """生成课题总结报告（所有单元完成后调用）。

    汇总所有单元报告、决策日志、风险回顾，生成课题级总结。
    """
    status = get_project_status(project_id)

    parts = []
    parts.append(f"# 课题总结报告：{status['project']['name']}\n")
    parts.append(f"课题ID: {status['project']['project_id']}")
    parts.append(f"目标: {status['project']['goal']}")
    parts.append(f"完成日期: {_now_utc()}\n")

    parts.append("## 单元完成情况\n")
    for unit in status["units"]:
        ac = unit.get("acceptance", {})
        parts.append(f"### {unit['unit_id']}: {unit['title']}")
        parts.append(f"- 状态: {unit['status']}")
        parts.append(f"- 验收标准: {ac.get('met', 0)}/{ac.get('total', 0)} 满足")
        parts.append(f"- 任务数: {unit['task_count']}")
        parts.append(f"- 风险数: {unit['risks']}")
        parts.append("")

    parts.append(f"## 统计\n")
    stats = status["stats"]
    parts.append(f"- 总单元数: {stats['total_units']}")
    parts.append(f"- 完成单元: {stats['completed_units']}")
    parts.append(f"- 总任务数: {stats['total_tasks']}")
    parts.append(f"- 知识库文档: {stats['kb_documents']}")

    summary = "\n".join(parts)

    # 写入知识库 summary 层
    add_document(project_id, "summary", "project-summary", "课题总结报告", summary, tags=["总结"])

    # 结题
    try:
        transition_project(project_id, "completed")
    except ValueError:
        pass

    return summary


def _self_check() -> None:
    """自检：完整工作流链路。"""
    from project_manager import create_project, delete_project

    print("=" * 50)
    print("◐ project_workflow 自检")
    print("=" * 50)

    # 1. 创建课题
    print("\n[1/6] 创建测试课题...")
    pid, _ = create_project("工作流自检课题", goal="验证完整工作流")

    # 2. 规划单元
    print("\n[2/6] 规划单元...")
    unit_ids = plan_units(pid, [
        {"title": "文献调研", "acceptance_criteria": ["完成5篇文献精读", "产出综述笔记"], "risks": ["关键文献获取困难"]},
        {"title": "模型建立", "acceptance_criteria": ["完成理论推导"], "risks": ["模型在低对称性下失效"]},
    ])
    print(f"  创建 {len(unit_ids)} 个单元")

    # 3. 开始执行第一个单元
    print("\n[3/6] 开始执行单元1...")
    task_ids = start_unit_execution(pid, unit_ids[0], [
        {"title": "查阅HHG综述", "assignee": "lin_sai"},
        {"title": "精读Ghimire2011", "assignee": "user"},
    ])
    print(f"  创建 {len(task_ids)} 个任务")

    # 4. 验收
    print("\n[4/6] 验收单元1...")
    # 标记验收标准满足
    unit = get_unit(unit_ids[0])
    for ac in unit.get("acceptance_criteria", []):
        check_acceptance_criterion(unit_ids[0], ac["id"], met=True)
    review = review_unit(pid, unit_ids[0])
    print(f"  验收: {review['acceptance_status']['met']}/{review['acceptance_status']['total']}")

    # 5. 完成单元
    print("\n[5/6] 完成单元1...")
    result = complete_unit(pid, unit_ids[0], review_notes="文献调研完成",
                          report_content="# 单元1进展报告\n完成了5篇文献精读。")
    print(f"  完成: {result['completed']}, 下一单元: {result.get('next_unit', '无')}")

    # 6. 课题状态
    print("\n[6/6] 课题状态...")
    status = get_project_status(pid)
    print(f"  单元数: {status['stats']['total_units']}")
    print(f"  完成数: {status['stats']['completed_units']}")
    print(f"  任务数: {status['stats']['total_tasks']}")

    # 清理
    delete_project(pid, confirm=True)
    print("\n✓ project_workflow 自检完成")


if __name__ == "__main__":
    _self_check()
