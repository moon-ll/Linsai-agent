#!/usr/bin/env python3
"""单元管理器 — 课题内任务容器的 CRUD、状态机、验收/风险/交付物管理。

单元是课题内的任务容器。每个课题由多个单元组成，单元按序推进。
单元包含验收标准（结构化数组）、任务列表（复用 task_manager）、
风险登记、交付物。

单元状态机: planning → executing → review → completed
- planning:  与用户沟通确认验收标准
- executing: 任务分工执行
- review:    验收讨论
- completed: 报告完成

用法示例:
    >>> from unit_manager import create_unit, transition_unit, add_acceptance_criteria
    >>> from project_manager import create_project
    >>>
    >>> pid, _ = create_project("固体HHG相位匹配机制研究", goal="建立理论模型")
    >>> uid, path = create_unit(pid, "Lewenstein模型适用性分析",
    ...     acceptance_criteria=["完成推导", "识别失效区间"])
    >>> add_acceptance_criteria(uid, "对比数值模拟")
    >>> transition_unit(uid, "executing")
    >>> transition_unit(uid, "review")
    >>> transition_unit(uid, "completed")
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common import now_utc as _now_utc, load_json as _read_json, save_json as _write_json

_SCRIPT_DIR = Path(__file__).parent.resolve()
_PROJECT_ROOT = _SCRIPT_DIR.parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from project_manager import get_project, update_project, _project_dir  # noqa: E402

# 日志接入（可选，logger 模块不存在时降级为静默）
try:
    from logger import get_logger
    _log = get_logger("unit_manager")
except Exception:
    _log = None

# 课题数据存储根目录（与 project_manager 保持一致）
PROJECTS_DIR = _PROJECT_ROOT / "projects"


# ---------------------------------------------------------------------------
# 单元状态机
# ---------------------------------------------------------------------------
UNIT_STATUS_FLOW: Dict[str, set] = {
    "planning": {"executing"},
    "executing": {"review", "planning"},  # 允许退回规划补充验收标准
    "review": {"completed", "executing"},  # 允许返工
    "completed": {"review"},  # 结题后发现问题可重新验收
}

UNIT_STATUS_LABELS = {
    "planning": "规划中",
    "executing": "执行中",
    "review": "验收中",
    "completed": "已完成",
}

RISK_SEVERITIES = {"low", "medium", "high"}


# ---------------------------------------------------------------------------
# 路径辅助
# ---------------------------------------------------------------------------
def _units_dir(project_id: str) -> Path:
    """单元文件存放目录: projects/{project_id}/units/"""
    return _project_dir(project_id) / "units"


def _validate_unit_id(unit_id: str) -> str:
    """校验 unit_id 安全性，防止路径遍历。"""
    if not unit_id or not isinstance(unit_id, str):
        raise ValueError("unit_id 不能为空")
    if "/" in unit_id or "\\" in unit_id or ".." in unit_id:
        raise ValueError(f"非法 unit_id: {unit_id}")
    return unit_id


def _unit_path(project_id: str, unit_id: str) -> Path:
    """单元 JSON 文件路径。"""
    _validate_unit_id(unit_id)
    return _units_dir(project_id) / f"{unit_id}.json"


def _find_unit_file(unit_id: str) -> Optional[Path]:
    """在全课题范围内搜索单元文件，返回路径或 None。

    单元文件存储在 projects/{project_id}/units/{unit_id}.json，
    由于 unit_id 在课题内自增，跨课题可能重复，故需全局搜索。
    """
    if not PROJECTS_DIR.exists():
        return None
    for pdir in PROJECTS_DIR.iterdir():
        if not pdir.is_dir():
            continue
        candidate = pdir / "units" / f"{unit_id}.json"
        if candidate.exists():
            return candidate
    return None


def _load_unit(unit_id: str) -> Tuple[dict, Path]:
    """加载单元，返回 (unit_dict, path)。找不到则抛 FileNotFoundError。"""
    path = _find_unit_file(unit_id)
    if path is None:
        raise FileNotFoundError(f"✗ 未找到单元: {unit_id}")
    unit = _read_json(path, default={})
    if not unit:
        raise ValueError(f"✗ 单元文件损坏: {unit_id}")
    return unit, path


def _save_unit(unit: dict, path: Path) -> None:
    """保存单元 JSON 文件。"""
    _write_json(path, unit)


def _unit_file_lock():
    """获取单元写入锁（延迟导入 web_base，避免循环依赖）。

    使用独立的单元锁键（PROJECTS_DIR + "::units"），与 project_manager 的课题锁键
    区分，避免 create_unit/delete_unit 内部调用 update_project 时发生不可重入死锁
    （threading.Lock 不可重入）。单元操作恒以 单元锁→课题锁 顺序获取，无反向，安全。
    """
    import web_base
    return web_base._get_file_lock(str(PROJECTS_DIR) + "::units")


def _gen_ac_id(unit: dict) -> str:
    """生成验收标准 ID: ac_{N}。"""
    existing = unit.get("acceptance_criteria", [])
    return f"ac_{len(existing) + 1}"


def _gen_risk_id(unit: dict) -> str:
    """生成风险 ID: risk_{N}。"""
    existing = unit.get("risks", [])
    return f"risk_{len(existing) + 1}"


def _normalize_criteria(criteria: Any) -> List[dict]:
    """将验收标准归一化为结构化数组。

    接受:
        - None → 空列表
        - list[str] → 转为 [{id, text, met, notes}, ...]
        - list[dict] → 补全缺失字段
    """
    if criteria is None:
        return []
    result: List[dict] = []
    for idx, item in enumerate(criteria, start=1):
        if isinstance(item, str):
            result.append({
                "id": f"ac_{idx}",
                "text": item,
                "met": False,
                "notes": "",
            })
        elif isinstance(item, dict):
            result.append({
                "id": item.get("id", f"ac_{idx}"),
                "text": item.get("text", ""),
                "met": bool(item.get("met", False)),
                "notes": item.get("notes", ""),
            })
    return result


# ---------------------------------------------------------------------------
# 单元 CRUD
# ---------------------------------------------------------------------------
def create_unit(
    project_id: str,
    title: str,
    acceptance_criteria: Any = None,
    description: str = "",
) -> Tuple[str, Path]:
    """创建新单元，返回 (unit_id, unit_file_path)。

    Args:
        project_id: 所属课题 ID
        title: 单元标题（如"Lewenstein模型适用性分析"）
        acceptance_criteria: 验收标准，可为 None / list[str] / list[dict]
        description: 单元详细描述

    创建逻辑:
        1. 读取课题信息，获取当前 units 列表
        2. 序号 = len(units) + 1，生成 unit_id = f"UNIT-{seq:03d}"
        3. 创建单元目录 projects/{project_id}/units/
        4. 写入单元 JSON 文件
        5. 更新课题: units 列表追加 unit_id, current_unit 设为新 unit_id,
           phase 设为 f"unit_{seq}"
        6. 如果 acceptance_criteria 为 None，初始化为空列表
    """
    # 加锁保护 读取课题→生成unit_id→写单元文件→更新课题 的读-改-写，
    # 防止并发创建产生重复 unit_id 或 units 列表互相覆盖。
    # 内部调用 update_project 会获取课题锁，锁键不同，无死锁。
    with _unit_file_lock():
        # 1. 读取课题信息（验证课题存在）
        project = get_project(project_id)
        existing_units = project.get("units", [])

        # 2. 生成 unit_id（课题内自增）
        seq = len(existing_units) + 1
        unit_id = f"UNIT-{seq:03d}"

        # 3. 创建单元目录
        udir = _units_dir(project_id)
        udir.mkdir(parents=True, exist_ok=True)

        # 6. 初始化验收标准
        criteria = _normalize_criteria(acceptance_criteria)

        # 4. 构造单元数据
        now = _now_utc()
        unit = {
            "unit_id": unit_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "sequence": seq,
            "status": "planning",
            "acceptance_criteria": criteria,
            "tasks": [],  # task_id 列表，引用 task_manager 的任务
            "risks": [],
            "deliverables": [],
            "review_notes": "",
            "progress_report": "",
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }

        path = _unit_path(project_id, unit_id)
        _save_unit(unit, path)

        # 5. 更新课题: units / current_unit / phase
        new_units = list(existing_units)
        new_units.append(unit_id)
        update_project(
            project_id,
            units=new_units,
            current_unit=unit_id,
            phase=f"unit_{seq}",
        )

    if _log:
        _log.info(f"单元已创建: {unit_id} | 课题={project_id} | 序号={seq} | 验收标准={len(criteria)} | 状态=planning")
    return unit_id, path


def get_unit(unit_id: str) -> dict:
    """读取单元信息，返回单元字典。"""
    unit, _ = _load_unit(unit_id)
    return unit


def update_unit(unit_id: str, **fields) -> dict:
    """更新单元字段，自动更新 updated_at。

    status 字段走状态机校验（调用 transition_unit），
    unit_id / project_id / created_at 为只读字段。
    """
    # 加锁保护 读取-修改-写回，防止并发更新互相覆盖。
    # status 分支调用 transition_unit（未单独加锁），在持锁状态下执行，安全。
    with _unit_file_lock():
        unit, path = _load_unit(unit_id)

        readonly = {"unit_id", "project_id", "created_at"}

        # status 单独走状态机
        if "status" in fields:
            new_status = fields.pop("status")
            old_status = unit.get("status", "planning")
            if new_status != old_status:
                return transition_unit(unit_id, new_status)

        for key, value in fields.items():
            if key in readonly:
                if _log:
                    _log.warning(f"字段 '{key}' 只读，已跳过")
                continue
            unit[key] = value

        unit["updated_at"] = _now_utc()
        _save_unit(unit, path)
    if _log:
        _log.info(f"单元已更新: {unit_id}")
    return unit


def transition_unit(unit_id: str, new_status: str) -> dict:
    """单元状态流转: planning → executing → review → completed。

    校验状态机，只允许合法的 state transition。
    """
    unit, path = _load_unit(unit_id)
    old_status = unit.get("status", "planning")

    if new_status == old_status:
        if _log:
            _log.info(f"单元已是该状态: {unit_id} ({old_status})")
        return unit

    if new_status not in UNIT_STATUS_FLOW.get(old_status, set()):
        raise ValueError(
            f"✗ 状态流转不允许: {old_status} → {new_status}。"
            f"允许的后续状态: {UNIT_STATUS_FLOW.get(old_status, set())}"
        )

    unit["status"] = new_status
    unit["updated_at"] = _now_utc()
    if new_status == "completed":
        unit["completed_at"] = _now_utc()

    _save_unit(unit, path)
    if _log:
        _log.info(f"状态流转: {unit_id} {old_status} → {new_status}")
    return unit


def list_units(project_id: str) -> List[dict]:
    """列出课题下所有单元，按 sequence 排序。"""
    project = get_project(project_id)
    unit_ids = project.get("units", [])

    udir = _units_dir(project_id)
    units: List[dict] = []
    for uid in unit_ids:
        path = udir / f"{uid}.json"
        if not path.exists():
            # 兼容全局搜索（目录被移动等异常情况）
            found = _find_unit_file(uid)
            if found is None:
                continue
            path = found
        unit = _read_json(path, default={})
        if unit:
            units.append(unit)

    units.sort(key=lambda u: u.get("sequence", 0))
    return units


def delete_unit(unit_id: str, confirm: bool = False) -> bool:
    """删除单元。

    Args:
        confirm: 必须为 True 才执行删除（安全机制）

    删除后会从所属课题的 units 列表中移除引用，
    若被删除的是 current_unit，则 current_unit 置为 None。
    """
    if not confirm:
        if _log:
            _log.warning("删除单元需要 confirm=True")
        return False

    # 加锁保护 删除单元文件 + 同步课题 units 列表的读-改-写。
    # 内部调用 update_project 会获取课题锁，锁键不同，无死锁。
    with _unit_file_lock():
        unit, path = _load_unit(unit_id)
        project_id = unit.get("project_id", "")

        # 删除单元文件
        path.unlink()

        # 从课题 units 列表移除引用
        if project_id:
            try:
                project = get_project(project_id)
                units_list = [u for u in project.get("units", []) if u != unit_id]
                update_fields: Dict[str, Any] = {"units": units_list}
                if project.get("current_unit") == unit_id:
                    update_fields["current_unit"] = None
                update_project(project_id, **update_fields)
            except FileNotFoundError:
                pass

    if _log:
        _log.info(f"单元已删除: {unit_id}")
    return True


# ---------------------------------------------------------------------------
# 验收标准管理
# ---------------------------------------------------------------------------
def add_acceptance_criteria(unit_id: str, text: str) -> dict:
    """添加一条验收标准。"""
    unit, path = _load_unit(unit_id)
    criteria = unit.get("acceptance_criteria", [])
    ac = {
        "id": _gen_ac_id(unit),
        "text": text,
        "met": False,
        "notes": "",
    }
    criteria.append(ac)
    unit["acceptance_criteria"] = criteria
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    print(f"✓ 验收标准已添加: {ac['id']} → {text}")
    return unit


def check_acceptance_criterion(
    unit_id: str,
    ac_id: str,
    met: bool = True,
    notes: str = "",
) -> dict:
    """标记某条验收标准是否满足。"""
    unit, path = _load_unit(unit_id)
    criteria = unit.get("acceptance_criteria", [])
    found = False
    for ac in criteria:
        if ac.get("id") == ac_id:
            ac["met"] = met
            if notes:
                ac["notes"] = notes
            found = True
            break
    if not found:
        raise KeyError(f"✗ 未找到验收标准: {ac_id}")

    unit["acceptance_criteria"] = criteria
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    status_str = "满足" if met else "未满足"
    print(f"✓ 验收标准 {ac_id} 标记为{status_str}")
    return unit


def get_acceptance_status(unit_id: str) -> dict:
    """获取单元验收状态汇总。

    返回 {total, met, unmet, criteria}。
    """
    unit, _ = _load_unit(unit_id)
    criteria = unit.get("acceptance_criteria", [])
    met_list = [c for c in criteria if c.get("met")]
    unmet_list = [c for c in criteria if not c.get("met")]
    return {
        "total": len(criteria),
        "met": len(met_list),
        "unmet": len(unmet_list),
        "criteria": criteria,
    }


# ---------------------------------------------------------------------------
# 风险管理
# ---------------------------------------------------------------------------
def add_risk(unit_id: str, description: str, severity: str = "medium") -> dict:
    """添加一条风险登记。

    Args:
        severity: "low" | "medium" | "high"
    """
    if severity not in RISK_SEVERITIES:
        severity = "medium"
    unit, path = _load_unit(unit_id)
    risks = unit.get("risks", [])
    risk = {
        "id": _gen_risk_id(unit),
        "description": description,
        "severity": severity,
        "hit": None,  # None=未验证, True=已发生, False=未发生
    }
    risks.append(risk)
    unit["risks"] = risks
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    print(f"✓ 风险已登记: {risk['id']} [{severity}] → {description}")
    return unit


def resolve_risk(unit_id: str, risk_id: str, hit: bool = True) -> dict:
    """标记风险的命中情况。

    Args:
        hit: True=风险已发生, False=风险未发生
    """
    unit, path = _load_unit(unit_id)
    risks = unit.get("risks", [])
    found = False
    for r in risks:
        if r.get("id") == risk_id:
            r["hit"] = hit
            found = True
            break
    if not found:
        raise KeyError(f"✗ 未找到风险: {risk_id}")

    unit["risks"] = risks
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    hit_str = "已发生" if hit else "未发生"
    print(f"✓ 风险 {risk_id} 标记为{hit_str}")
    return unit


# ---------------------------------------------------------------------------
# 任务关联
# ---------------------------------------------------------------------------
def add_task_to_unit(unit_id: str, task_id: str) -> dict:
    """将 task_manager 的任务关联到单元。

    单元 tasks 字段存储 task_id 列表（引用 task_manager 的任务）。
    """
    unit, path = _load_unit(unit_id)
    tasks = unit.get("tasks", [])
    if task_id in tasks:
        print(f"○ 任务已关联: {task_id}")
        return unit
    tasks.append(task_id)
    unit["tasks"] = tasks
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    print(f"✓ 任务已关联: {task_id} → {unit_id}")
    return unit


def get_unit_tasks(unit_id: str) -> List[dict]:
    """获取单元关联的任务详情列表。

    通过 task_manager.get_task 读取任务数据，容忍任务缺失。
    """
    unit, _ = _load_unit(unit_id)
    task_ids = unit.get("tasks", [])

    # 懒加载 task_manager，避免硬依赖
    tasks: List[dict] = []
    try:
        import importlib.util
        tm_path = _SCRIPT_DIR / "task_manager.py"
        if tm_path.exists():
            spec = importlib.util.spec_from_file_location("task_manager", tm_path)
            tm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tm)
            for tid in task_ids:
                try:
                    tasks.append(tm.get_task(tid))
                except (FileNotFoundError, Exception):
                    tasks.append({"task_id": tid, "title": "(任务缺失)", "status": "missing"})
        else:
            # task_manager 不存在，仅返回 ID 引用
            tasks = [{"task_id": tid, "title": "(task_manager不可用)"} for tid in task_ids]
    except Exception:
        tasks = [{"task_id": tid, "title": "(加载失败)"} for tid in task_ids]

    return tasks


# ---------------------------------------------------------------------------
# 交付物
# ---------------------------------------------------------------------------
def add_deliverable(
    unit_id: str,
    name: str,
    path: str = "",
    description: str = "",
) -> dict:
    """添加交付物。"""
    unit, fpath = _load_unit(unit_id)
    deliverables = unit.get("deliverables", [])
    deliverable = {
        "id": f"del_{len(deliverables) + 1}",
        "name": name,
        "path": path,
        "description": description,
        "added_at": _now_utc(),
    }
    deliverables.append(deliverable)
    unit["deliverables"] = deliverables
    unit["updated_at"] = _now_utc()
    _save_unit(unit, fpath)
    print(f"✓ 交付物已添加: {deliverable['id']} → {name}")
    return unit


# ---------------------------------------------------------------------------
# 单元报告
# ---------------------------------------------------------------------------
def set_progress_report(unit_id: str, report_path: str) -> dict:
    """设置单元进度报告路径。"""
    unit, path = _load_unit(unit_id)
    unit["progress_report"] = report_path
    unit["updated_at"] = _now_utc()
    _save_unit(unit, path)
    print(f"✓ 进度报告已设置: {unit_id} → {report_path}")
    return unit


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """自检：创建测试课题→创建单元→验收检查→状态流转→清理。"""
    from project_manager import create_project, delete_project

    print("=" * 50)
    print("◐ unit_manager 自检")
    print("=" * 50)

    print("\n[1/8] 创建测试课题...")
    pid, _ = create_project("单元自检测试课题", goal="验证单元管理链路")
    print(f"  课题ID: {pid}")

    print("\n[2/8] 创建单元（无初始验收标准）...")
    uid, upath = create_unit(pid, "Lewenstein模型适用性分析")
    print(f"  单元ID: {uid}")
    print(f"  文件存在: {'✓' if upath.exists() else '✗'}")
    unit = get_unit(uid)
    print(f"  序号: {unit['sequence']}")
    print(f"  初始验收标准为空: {'✓' if unit['acceptance_criteria'] == [] else '✗'}")
    # 验证课题已更新
    proj = get_project(pid)
    print(f"  课题 units 含新单元: {'✓' if uid in proj.get('units', []) else '✗'}")
    print(f"  课题 current_unit 正确: {'✓' if proj.get('current_unit') == uid else '✗'}")
    print(f"  课题 phase 正确: {'✓' if proj.get('phase') == 'unit_1' else '✗'}")

    print("\n[3/8] 创建第二个单元（带初始验收标准）...")
    uid2, _ = create_unit(
        pid, "能带结构对HHG的影响",
        acceptance_criteria=["完成能带计算", "对比实验数据"],
    )
    unit2 = get_unit(uid2)
    print(f"  单元ID: {uid2}")
    print(f"  序号自增: {'✓' if unit2['sequence'] == 2 else '✗'}")
    print(f"  验收标准数: {len(unit2['acceptance_criteria'])}")
    print(f"  验收标准结构正确: {'✓' if all('id' in c and 'text' in c and 'met' in c for c in unit2['acceptance_criteria']) else '✗'}")

    print("\n[4/8] 添加验收标准...")
    add_acceptance_criteria(uid, "完成推导")
    add_acceptance_criteria(uid, "识别失效区间")
    add_acceptance_criteria(uid, "对比数值模拟")
    unit = get_unit(uid)
    print(f"  验收标准总数: {len(unit['acceptance_criteria'])}")
    print(f"  ID 自增正确: {'✓' if [c['id'] for c in unit['acceptance_criteria']] == ['ac_1', 'ac_2', 'ac_3'] else '✗'}")

    print("\n[5/8] 检查验收标准...")
    check_acceptance_criterion(uid, "ac_1", met=True, notes="推导已完成")
    check_acceptance_criterion(uid, "ac_2", met=True)
    status = get_acceptance_status(uid)
    print(f"  总数: {status['total']}")
    print(f"  已满足: {status['met']}")
    print(f"  未满足: {status['unmet']}")
    print(f"  汇总正确: {'✓' if status['total'] == 3 and status['met'] == 2 and status['unmet'] == 1 else '✗'}")

    print("\n[6/8] 添加风险并标记命中...")
    add_risk(uid, "能带非抛物线效应", severity="high")
    add_risk(uid, "数值发散", severity="low")
    unit = get_unit(uid)
    print(f"  风险总数: {len(unit['risks'])}")
    resolve_risk(uid, "risk_1", hit=True)
    unit = get_unit(uid)
    print(f"  风险1已标记命中: {'✓' if unit['risks'][0]['hit'] is True else '✗'}")
    print(f"  风险2未验证: {'✓' if unit['risks'][1]['hit'] is None else '✗'}")

    print("\n[7/8] 状态流转 planning → executing → review → completed...")
    unit = transition_unit(uid, "executing")
    print(f"  planning → executing: {'✓' if unit['status'] == 'executing' else '✗'}")
    unit = transition_unit(uid, "review")
    print(f"  executing → review: {'✓' if unit['status'] == 'review' else '✗'}")
    unit = transition_unit(uid, "completed")
    print(f"  review → completed: {'✓' if unit['status'] == 'completed' else '✗'}")
    print(f"  completed_at 已设置: {'✓' if unit.get('completed_at') else '✗'}")

    # 非法流转校验
    print("\n  非法流转校验...")
    try:
        # completed 只能回 review，不能直接到 planning
        transition_unit(uid, "planning")
        print(f"  completed → planning 应被拒绝: {'✗' if False else '✗(未拦截)'}")
    except ValueError:
        print(f"  completed → planning 已拦截: {'✓'}")

    print("\n[8/8] 列出课题单元与清理...")
    units = list_units(pid)
    print(f"  单元总数: {len(units)}")
    print(f"  按序号排序: {'✓' if [u['sequence'] for u in units] == [1, 2] else '✗'}")

    # 添加交付物测试
    add_deliverable(uid, "推导手稿", path="docs/derivation.md", description="Lewenstein模型完整推导")
    unit = get_unit(uid)
    print(f"  交付物已添加: {'✓' if len(unit['deliverables']) == 1 else '✗'}")

    # 进度报告测试
    set_progress_report(uid, "reports/unit-001-progress.md")
    unit = get_unit(uid)
    print(f"  进度报告已设置: {'✓' if unit['progress_report'] == 'reports/unit-001-progress.md' else '✗'}")

    # 任务关联测试
    add_task_to_unit(uid, "TASK-TEST-001")
    unit = get_unit(uid)
    print(f"  任务已关联: {'✓' if 'TASK-TEST-001' in unit['tasks'] else '✗'}")

    # 删除单元测试：先删除 UNIT-002（当前 current_unit）验证置空，再删 UNIT-001
    ok = delete_unit(uid2, confirm=True)
    print(f"  删除 UNIT-002 成功: {'✓' if ok else '✗'}")
    proj = get_project(pid)
    print(f"  课题 units 仅剩 UNIT-001: {'✓' if proj.get('units') == [uid] else '✗'}")
    print(f"  current_unit 已置空(删除当前单元): {'✓' if proj.get('current_unit') is None else '✗'}")

    ok = delete_unit(uid, confirm=True)
    print(f"  删除 UNIT-001 成功: {'✓' if ok else '✗'}")
    proj = get_project(pid)
    print(f"  课题 units 已清空: {'✓' if proj.get('units') == [] else '✗'}")

    # 清理测试课题
    delete_project(pid, confirm=True)
    print("\n✓ unit_manager 自检完成")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="单元管理器")
    parser.add_argument("--self-check", action="store_true", help="运行自检")
    parser.add_argument("--list", metavar="PROJECT_ID", help="列出课题下所有单元")
    args = parser.parse_args()

    if args.self_check:
        _self_check()
    elif args.list:
        for u in list_units(args.list):
            print(f"  {u['unit_id']} | {u['title']} | {UNIT_STATUS_LABELS.get(u['status'], u['status'])} | 序号{u['sequence']}")
