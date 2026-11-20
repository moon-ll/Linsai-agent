# -*- coding: utf-8 -*-
"""课题启动包管线（v8）——常量与路径。

v8.0.0 架构（用户裁决 2026-11-16）：全自动化产出的目标定位为课题启动包
（proposal）——文献阅读发掘科学问题 → 单遍深度研究探索方案 → 整合参考文献
与课题报告。设计文档：docs/WORKBENCH-ARCHITECTURE.md。

用法示例：
    from topic_pipeline.constants import TOPICS_ROOT, STAGES
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据域根目录（测试可用 LINSAI_TOPICS_ROOT 环境变量重定向到临时目录）
TOPICS_ROOT = Path(os.environ.get("LINSAI_TOPICS_ROOT") or (PROJECT_ROOT / "research_topics"))

# v8 五阶段 + 否决台账（阶段即目录，状态由目录位置承载）
STAGES = ("questions", "kickoff", "ready", "active", "archive")
REJECTED_DIRNAME = "_rejected-questions"
AUDIT_DIRNAME = "_audit"

STATE_FILE = TOPICS_ROOT / "_topics.json"

# 项目类型前缀（命名规则沿用 v6.5.4：{scope}-{slug}-{YYYYMMDD}）
SCOPE_SHORT = ("general", "key", "major")

# ---------------------------------------------------------------------------
# 验收标准参数（docs/WORKBENCH-ARCHITECTURE.md §4）
# ---------------------------------------------------------------------------
A1_MIN_SOURCES = 8          # A1 背景调研：文献笔记/知识卡 ≥ 8 篇
A1_MIN_RECENT = 3           # A1：近 24 个月文献 ≥ 3 篇
A1_RECENT_MONTHS = 24
A2_NOVELTY_THRESHOLD = 0.50  # A2：与既有课题相似度上限（2-gram Jaccard）
A3_MIN_STEPS = 3            # A3：方案分解 ≥ 3 个步骤
G1_REPORT_MAX_CHARS = 8000  # G1：课题报告正文上限
G2_MIN_WIKILINKS = 5        # G2：报告内 KB wikilink 下限

# 同一缺口补齐次数上限：补 2 次仍不过 → needs_human 挂起等人裁决
GAP_REPAIR_LIMIT = 2

# 每日深研配额（memory/config/workbench.json 可覆盖）
DEFAULT_DAILY_QUOTA = 1

# 深研各步 hermes profile 映射（B1 背景调研 / B2 问题定位 / B3 方案分解）
STEP_PROFILE_MAP = {
    "background": "researcher",
    "problem": "analyst",
    "scheme": "writer",
}

# 深研步骤 → 预期产物（相对课题目录）
STEP_ARTIFACTS = {
    "background": ["01_background/literature-map.md"],
    "problem": ["02_problem/problem.md"],
    "scheme": ["03_scheme/scheme.md", "04_references/references.bib"],
}

# hermes 单步超时（秒）——v8.0.2 按步差异化：首跑实测 B1（检索+领域地图+bib）
# 900s 超时零产物（2026-11-17 09:45 attosecond 课题），检索型任务给足预算
STEP_TIMEOUT_S = 900
STEP_TIMEOUTS = {
    "background": 1800,
    "problem": 1200,
    "scheme": 1500,
}
