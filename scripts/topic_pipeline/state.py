# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——轻量状态总线 `_topics.json`。

v8 设计原则（对比 v7 `_lifecycle.json` 的 60 字段状态机）：状态由「目录位置 +
课题卡头域」承载，_topics.json 只存轻量元数据索引，正文一律落文件。

用法示例：
    from topic_pipeline import state
    with state.state_lock():
        st = state.load_state()
        state.set_stage(st, "general-mos2-hhg-20261116", "kickoff")
        state.save_state(st)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from common import file_lock, load_json, save_json

from . import constants as _C
from .constants import REJECTED_DIRNAME, STAGES


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def state_lock():  # noqa: ANN201
    """跨进程状态锁（写路径必须持有）。"""
    return file_lock("topic-pipeline")


def _state_file():
    """状态文件路径（动态取 TOPICS_ROOT，测试可重定向）。"""
    return _C.TOPICS_ROOT / "_topics.json"


def load_state() -> Dict[str, Any]:
    data = load_json(_state_file(), default=None)
    if not isinstance(data, dict):
        data = {}
    data.setdefault("topics", {})
    data.setdefault("rejected", {})
    return data


def save_state(data: Dict[str, Any]) -> None:
    data["updated_at"] = _now()
    save_json(_state_file(), data)


def get_topic(data: Dict[str, Any], topic_id: str) -> Optional[Dict[str, Any]]:
    t = data.get("topics", {}).get(topic_id)
    return t if isinstance(t, dict) else None


def upsert_topic(data: Dict[str, Any], topic_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    topics = data.setdefault("topics", {})
    rec = topics.setdefault(topic_id, {})
    rec.update({k: v for k, v in fields.items() if v is not None})
    rec.setdefault("created_at", _now())
    rec["updated_at"] = _now()
    return rec


def set_stage(data: Dict[str, Any], topic_id: str, stage: str, note: str = "") -> Dict[str, Any]:
    """更新课题阶段；stage 必须是五阶段之一。"""
    if stage not in STAGES:
        raise ValueError(f"非法阶段: {stage}（合法值 {STAGES}）")
    rec = upsert_topic(data, topic_id, {"stage": stage})
    history = rec.setdefault("stage_history", [])
    history.append({"stage": stage, "at": _now(), "note": note})
    return rec


def set_flag(data: Dict[str, Any], topic_id: str, key: str, value: Any) -> Dict[str, Any]:
    return upsert_topic(data, topic_id, {key: value})


def transition(topic_id: str, to_stage: str, note: str = "") -> Dict[str, Any]:
    """阶段流转唯一入口（v8.0.1）：状态 set_stage + 目录物理搬移。

    「阶段即目录」不变量：任何阶段变更必须同时改 _topics.json 与物理目录，
    否则 topic_dir 信任状态记录会指向不存在的目录（2026-11-17 全量验证发现的
    破缺点：acceptance 晋级 ready、CLI/Web activate、CLI archive 等 4 处只改状态）。

    Returns:
        {topic_id, from, to, dir}；课题不存在抛 KeyError。
    """
    if to_stage not in STAGES:
        raise ValueError(f"非法阶段: {to_stage}（合法值 {STAGES}）")
    with state_lock():
        data = load_state()
        rec = get_topic(data, topic_id)
        if not rec:
            raise KeyError(f"课题不存在: {topic_id}")
        from_stage = rec.get("stage", "")
        set_stage(data, topic_id, to_stage, note)
        save_state(data)
    moved = move_topic_dir(topic_id, to_stage)
    return {"topic_id": topic_id, "from": from_stage, "to": to_stage, "dir": moved}


def move_to_rejected(topic_id: str) -> Optional["Path"]:  # noqa: F821
    """否决流转的目录搬移：任意阶段 → _rejected-questions/（状态由 reject_topic 清）。"""
    from pathlib import Path
    import shutil as _shutil

    src = topic_dir(topic_id)
    if src is None:
        return None
    dst = _C.TOPICS_ROOT / REJECTED_DIRNAME / topic_id
    if Path(src).resolve() == dst.resolve():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return dst
    _shutil.move(str(src), str(dst))
    return dst


def reject_topic(data: Dict[str, Any], topic_id: str, reason: str) -> Dict[str, Any]:
    """问题候选否决：移入台账（保留否决理由，防重复立项）。"""
    rec = get_topic(data, topic_id) or {}
    data.setdefault("rejected", {})[topic_id] = {
        "title": rec.get("title", ""),
        "reason": reason,
        "rejected_at": _now(),
        "migrated_from": rec.get("migrated_from", ""),
    }
    data.get("topics", {}).pop(topic_id, None)
    return data["rejected"][topic_id]


def list_by_stage(data: Dict[str, Any], stage: str) -> List[str]:
    return [tid for tid, rec in sorted(data.get("topics", {}).items())
            if isinstance(rec, dict) and rec.get("stage") == stage]


def topic_dir(topic_id: str, stage: Optional[str] = None) -> Optional["Path"]:  # noqa: F821
    """课题目录定位：优先信任状态记录的阶段，状态缺失时按目录扫描。"""
    from pathlib import Path

    if stage:
        p = _C.TOPICS_ROOT / stage / topic_id
        return p if p.exists() else None
    data = load_state()
    rec = get_topic(data, topic_id)
    if rec and rec.get("stage"):
        p = _C.TOPICS_ROOT / rec["stage"] / topic_id
        if p.exists():
            return p
    for st in STAGES:
        p = _C.TOPICS_ROOT / st / topic_id
        if p.exists():
            return p
    if (_C.TOPICS_ROOT / REJECTED_DIRNAME / topic_id).exists():
        return _C.TOPICS_ROOT / REJECTED_DIRNAME / topic_id
    return None


def move_topic_dir(topic_id: str, to_stage: str) -> Optional["Path"]:  # noqa: F821
    """阶段即目录：物理搬移课题目录到目标阶段（幂等，不覆盖已有目标）。"""
    from pathlib import Path
    import shutil as _shutil

    src = topic_dir(topic_id)
    if src is None:
        return None
    dst = _C.TOPICS_ROOT / to_stage / topic_id
    if Path(src).resolve() == dst.resolve():
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return dst
    _shutil.move(str(src), str(dst))
    return dst


def all_topics_for_match() -> List[Dict[str, str]]:
    """供新颖性对照 / 周末输入链 topic_match 使用的全阶段课题清单。

    Returns:
        [{id, title, stage, dir, text}]（text = 标题 + 一句话问题）
    """
    data = load_state()
    out: List[Dict[str, str]] = []
    for tid, rec in sorted(data.get("topics", {}).items()):
        if not isinstance(rec, dict):
            continue
        d = topic_dir(tid, rec.get("stage"))
        out.append({
            "id": tid,
            "title": rec.get("title", ""),
            "stage": rec.get("stage", ""),
            "dir": str(d) if d else "",
            "text": f"{rec.get('title', '')} {rec.get('problem', '')}",
        })
    return out
