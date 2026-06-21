#!/usr/bin/env python3
"""LinSai-CoPilot 统一路径常量。

集中定义各脚本中重复的 PROJECT_ROOT / KNOWLEDGE_DIR / MEMORY_DIR 等路径常量，
消除 30+ 处重复定义。

用法:
    from paths import PROJECT_ROOT, KNOWLEDGE_DIR, MEMORY_DIR, SCRIPTS_DIR
"""

from __future__ import annotations

from pathlib import Path

# 脚本目录和项目根目录（统一使用 .resolve() 消除符号链接差异）
SCRIPTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_DIR.parent

# 核心数据目录
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
MEMORY_DIR = PROJECT_ROOT / "memory"
SESSIONS_DIR = PROJECT_ROOT / "sessions"
LOGS_DIR = PROJECT_ROOT / "logs"
TASKS_DIR = PROJECT_ROOT / "tasks"
DOCS_DIR = PROJECT_ROOT / "docs"

# 知识库子目录
WIKI_DIR = KNOWLEDGE_DIR / "wiki"
RAW_DIR = KNOWLEDGE_DIR / "raw"
CAPTURES_DIR = KNOWLEDGE_DIR / "captures"

# 知识库核心文件
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
GRAPH_PATH = KNOWLEDGE_DIR / "graph.json"
ALIASES_PATH = KNOWLEDGE_DIR / "aliases.json"
GROWTH_LOG_PATH = KNOWLEDGE_DIR / "growth-log.json"
CATEGORIES_PATH = KNOWLEDGE_DIR / "categories.json"

# Hermes 工作区
HERMES_HOME = Path.home() / ".kimi"
LINSAI_PROFILE = HERMES_HOME / "profiles" / "linsai"
BRIEFINGS_DIR = LINSAI_PROFILE / "briefings" if LINSAI_PROFILE.exists() else HERMES_HOME / "briefings"
