# 数据流动路径图谱

> 全链路数据流向的权威参考。记录当前已验证通畅的路径，标注已废弃路径。
> 最后验证：2026-08-20（v6.9.28）
> AI 编码代理在涉及数据流向变更前应先查阅本文件。
> 维护约定：本文件只维护**结构流向**，不维护具体数据量（如 PDF/简报/论文数量），
> 数量会随运行增长而过期，请勿在此记录硬编码计数。

---

## 总览

系统有 **7 条核心数据链**，以知识库为汇聚中心：

```
                    ┌─────────────────────────────────────────────────┐
                    │              knowledge/（知识库）                 │
                    │  raw/papers  wiki/papers  wiki/reviews  pdfs    │
                    └────────────────────┬────────────────────────────┘
                                         │
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                              │
    ① PDF 同步                     ② 简报同步                    ③ 深度分析转换
  hermes pdfs/ ──→ raw/pdfs/    hermes briefings/ ──→ wiki/reviews/   hermes deep_analysis ──→ wiki/papers/
           │                             │                              │
    ④ 元数据汇聚                   ⑤ 统一状态                     ⑥ KB 反哺
  hermes papers/ ──→ raw/papers/   item-status.json              literature_service KB-first
           │                             │                              │
           └─────────────────────────────┼──────────────────────────────┘
                                         │
                                  ⑦ 每日定时同步
                                  sync_engine.sync_all()
                                  cron: lc-daily-sync 23:00
```

---

## 链 ①：PDF 原文同步

**源** → **目标**：
```
~/Desktop/hermes_workspace/knowledge_base/AI_wiki/03-raw/papers/pdfs/*.pdf
  ──→ knowledge/raw/pdfs/*.pdf
  ──→ knowledge/raw/pdfs/_text_cache/*.txt（文本提取缓存）
  ──→ knowledge/raw/pdfs/_pdf-library.md（索引页）
```

| 项目 | 值 |
|------|-----|
| 执行模块 | `sync_engine.sync_pdf_library()` |
| 路径常量 | `HERMES_RAW_PAPERS_DIR`（sync_engine 内定义） |
| 触发方式 | `sync_all()` / `--sync-pdf` / lc-daily-sync cron |
| 质量过滤 | 仅同步有对应 PDF 文件的条目 |

**状态**：通畅。PDF 从 hermes workspace 复制到知识库，同时提取文本缓存。

---

## 链 ②：每日文献简报同步

**源** → **目标**：
```
~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/research_briefing_*.md
  ──→ knowledge/wiki/reviews/briefing-YYYY-MM-DD.md
  ──→ knowledge/wiki/reviews/briefing-index.md（索引页）
```

| 项目 | 值 |
|------|-----|
| 执行模块 | `sync_engine.sync_research_briefings()` |
| 路径常量 | `BRIEFINGS_DIR`（sync_engine 内定义） |
| 触发方式 | `sync_all()` / `--sync-briefings` / lc-daily-sync cron |
| 质量过滤 | 仅同步 `research_briefing_` 前缀的详细版简报 |

**状态**：通畅。简报正文去重后写入 wiki/reviews/，自动更新索引页。

---

## 链 ③：深度分析 → 5 维度笔记

**源** → **目标**：
```
~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/deep_analysis_*.json
  ──→ knowledge/wiki/papers/{arxiv_id}.md（5 维度结构化笔记）
```

**5 维度结构**：Research Question / Background / Methods / Main Results / Future Directions

| 项目 | 值 |
|------|-----|
| 执行模块 | `kb_importer.import_deep_analysis_all()` |
| 路径常量 | `BRIEFINGS_DIR`（kb_importer 内定义） |
| 触发方式 | `sync_all()` step [3/5] / `--sync-all` |
| 质量过滤 | 仅处理有完整 5 维度字段的 JSON |

**状态**：通畅。JSON 深度分析自动转换为 Markdown 结构化笔记。

---

## 链 ④：论文元数据汇聚

**源（三路）** → **目标**：
```
路径 A：~/Desktop/hermes_workspace/.../briefings/papers/*.md
路径 B：~/Desktop/hermes_workspace/.../03-raw/papers/*.md
路径 C：knowledge/raw/papers/*.md（CoPilot 原有）
  ──→ knowledge/raw/papers/*.md（统一存储，YAML frontmatter）
  ──→ memory/item-status.json（状态索引）
```

| 项目 | 值 |
|------|-----|
| 统一状态文件 | `memory/item-status.json` |
| 状态模块 | `state_sync.py`（读写 item-status.json） |
| 周末汇聚 | `weekend_pipeline/sources.py` 三路读取 |

**状态**：通畅。论文元数据以 YAML frontmatter 形式存储，状态统一在 item-status.json 管理。

---

## 链 ⑤：统一状态总线

**核心文件**：`memory/item-status.json`

```
item-status.json
  ├── items: { "arxiv_id": { status, title, direction, updated_by, history } }
  └── updated_at: ISO 时间戳
```

**9 级状态枚举**：`pool → candidate → pushed → viewed → interested → discussing → skipped → discussed → archived`

| 方向 | 模块 | 函数 |
|------|------|------|
| 用户操作 → 统一状态 | `briefing_sync.py` | `sync_to_hermes()` |
| 统一状态 → 水位标记 | `briefing_sync.py` | `sync_from_hermes()` |
| hermes 初始化导入 | `state_sync.py` | `initialize_from_existing()` |
| 失败重试 | `briefing_sync.py` | `flush_pending_reverse()` |

**状态**：通畅。item-status.json 作为论文状态的唯一真相源，双向同步正常。

---

## 链 ⑥：知识库反哺（KB-first 检索）

**流向**：知识库 → 任务执行（文献检索）

```
literature_service.search(keywords)
  ├── 1. 查询 knowledge/raw/papers/ + knowledge/wiki/papers/（本地 KB）
  │     → 如果结果 >= 60% max_results，直接返回
  └── 2. 不足时 fallback 到 hermes researcher（在线检索）
```

| 项目 | 值 |
|------|-----|
| 执行模块 | `literature_service.py` → `_search_kb_papers()` |
| 调用方 | `lifecycle/executor.py` → `_run_lit_search_step()` |
| 注入方式 | `_kb_context_block` 注入到任务 prompt |

**状态**：通畅。本地知识库优先，减少在线检索成本，同时保证覆盖率。

---

## 链 ⑦：每日定时同步

**编排函数**：`sync_engine.sync_all()`

| 步骤 | 函数 | 说明 |
|------|------|------|
| [0/5] | `flush_pending_reverse()` | 重试失败的反向同步 |
| [1/5] | `sync_hermes_sessions()` | 同步 hermes 会话摘要 |
| [2/5] | `sync_hermes_outputs()` | 同步 hermes 产出 |
| [2.6/5] | `sync_pdf_library()` | PDF 原文同步（链 ①） |
| [3/5] | `sync_research_briefings()` | 简报同步（链 ②） |
| [3.5/5] | `import_deep_analysis_all()` | 深度分析转换（链 ③） |
| [4/5] | `sync_from_hermes()` | 统一状态水位更新（链 ⑤） |
| [5/5] | `_reindex()` | 重建知识库索引 |

| 项目 | 值 |
|------|-----|
| cron 注册 | `lc-daily-sync`（23:00 每日） |
| wrapper 脚本 | `scripts/lc_daily_sync.sh`（`cd /` 前缀） |
| CLI 入口 | `python3 scripts/sync_engine.py --sync-all` |

**状态**：通畅。全链路同步由单一编排函数驱动，每日定时执行。

---

## 提案生命周期数据流

独立于知识库链路，以 `research_proposals/` 为核心：

```
drafts/ → optimizing/ → pending_review/ → archived/
              │
              ├── 00_imported/     导入元数据
              ├── 00_pipeline/     管线状态
              ├── 01_topic/        课题定义
              ├── 02_literature/   文献检索 + 缺口分析
              ├── 03_writing/      撰写产出
              ├── 04_proposal/     申请书正文（5 模块）
              ├── 05_review/       评审报告 + 优化报告
              ├── 06_feedback/     对抗反馈
              └── 06_monitor/      monitor meta-review
```

| 项目 | 值 |
|------|-----|
| 状态文件 | `research_proposals/_lifecycle.json` |
| 任务同步 | `memory/lifecycle-task-map.json` → `tasks/` |
| 看板 | `memory/system-kanban.json` |

**状态**：通畅。四阶段生命周期 + 5 模块申请书 + 4 时段轮转正常运转。

---

## 周末管线数据流

工作日暂停 worker，执行三条特殊链路：

| 链路 | 输入 | 输出 | 模块 |
|------|------|------|------|
| 输入端 | 研究设想发现 | 新课题草稿 | `weekend_pipeline/input_jobs.py` |
| 输出端 | 归档课题知识萃取 | knowledge/wiki/ 知识笔记 | `weekend_pipeline/output_jobs.py` |
| 链路反思 | 7 天执行历史 | 复盘报告 | `weekend_pipeline/reflection_jobs.py` |

**数据源读取**（`sources.py`，v6.8.13 修正后）：
- `RAW_PAPERS_DIR` = `knowledge/raw/papers/`
- `HERMES_BRIEFINGS_PAPERS_DIR` = `~/Desktop/hermes_workspace/.../briefings/papers/`
- `BRIEFING_DIR` = `knowledge/wiki/reviews/`

**状态**：通畅。输入端前置调用 `sync_engine.sync_hermes_outputs()` 确保数据已汇聚。

---

## 已废弃路径（v6.8.14 清理）

以下路径/规则已在 v6.8.14 清理，不再使用：

### 废弃数据文件

| 文件 | 原因 | 替代方案 |
|------|------|----------|
| `memory/paper-pool.json` | papers 字段为空，数据已迁移 | `memory/item-status.json` + `knowledge/raw/papers/` frontmatter |

### 废弃路径常量（paths.py）

| 常量 | 原指向 | 处理 |
|------|--------|------|
| `DOCS_DIR` | `PROJECT_ROOT / "docs"` | 未使用，已删除 |
| `QA_PAPER_DIR` | `QA_DIR / "paper-discussions"` | 未使用，已删除 |
| `QA_PROPOSAL_DIR` | `QA_DIR / "proposal-discussions"` | 未使用，已删除 |
| `QA_PROJECT_DIR` | `QA_DIR / "project-discussions"` | 未使用，已删除 |
| `BRIEFINGS_DIR` | `~/.kimi/...` | 已删除（.kimi → .hermes 迁移遗留） |

### 废弃写入行为

| 行为 | 模块 | 处理 |
|------|------|------|
| `sync_from_hermes()` 写 paper-pool.json | `briefing_sync.py` | 已移除，只更新水位标记 |
| `initialize_from_existing()` 读 paper-pool.json | `state_sync.py` | 已移除，从 daily_candidates.json 导入 |

### 废弃路径前缀

| 旧前缀 | 新前缀 | 说明 |
|--------|--------|------|
| `~/.kimi/` | `~/.hermes/` | hermes-agent 从 kimi 改名为 hermes |

---

## 关键路径常量速查（paths.py）

```python
# 核心数据目录
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
MEMORY_DIR    = PROJECT_ROOT / "memory"
SESSIONS_DIR  = PROJECT_ROOT / "sessions"
TASKS_DIR     = PROJECT_ROOT / "tasks"

# 知识库三层结构
RAW_DIR       = KNOWLEDGE_DIR / "raw"       # 原始数据（只读引用）
WIKI_DIR      = KNOWLEDGE_DIR / "wiki"      # AI 管理的结构化知识
QA_DIR        = KNOWLEDGE_DIR / "qa"        # 问答讨论
CAPTURES_DIR  = KNOWLEDGE_DIR / "captures"  # 采集

# PDF 文库
PDF_DIR       = RAW_DIR / "pdfs"

# Hermes 数据源
HERMES_WORKSPACE          = ~/Desktop/hermes_workspace
HERMES_BRIEFINGS_DIR      = HERMES_WORKSPACE / "knowledge_base" / "AI_wiki" / "briefings"
HERMES_BRIEFING_PAPERS_DIR = HERMES_BRIEFINGS_DIR / "papers"

# Hermes 运行时
HERMES_HOME     = ~/.hermes
LINSAI_PROFILE  = HERMES_HOME / "profiles" / "linsai"

# 研究管线
RESEARCH_PROPOSALS_DIR = PROJECT_ROOT / "research_proposals"
```

---

## 数据域隔离规则

| 数据域 | 目录 | 写入方 | 读取方 |
|--------|------|--------|--------|
| CoPilot 核心 | `sessions/` `memory/` `tasks/` | CoPilot 核心模块 | 全部（只读） |
| 共享只读 | `knowledge/raw/` | `learning_engine` / `sync_engine` | 全部 |
| AI 管理 | `knowledge/wiki/` | `kb_importer` / `learning_engine` | 全部 |
| 研究管线 | `research_proposals/` | 管线模块 | CoPilot（只读展示） |
| Hermes 产出 | `~/Desktop/hermes_workspace/` | hermes-agent | `sync_engine`（只读拉取） |

**导入边界**：研究管线模块禁止直接导入 CoPilot 核心模块（会话、记忆、LLM 路由），LLM 统一走 `llm_gateway`。

---

## v6.8.16-v6.8.17 新增数据链路

### 自检测链路

| 链 | 名称 | 触发条件 | 执行函数 |
|----|------|----------|----------|
| ⑧ | 质量天花板检测 | 连续 3 轮 ≥0.80 且提升 <2% | `completion.py::_check_done()` → 自动晋级 pending_review |
| ⑨ | 质量下降检测 | 连续 3 轮分数下降 | `completion.py::_check_done()` → 暂停 + quality_warning |
| ⑩ | 停滞课题检测 | 48h 无新 done job | `lifecycle_monitor._check_proposals()` → stalled 告警 |
| ⑪ | 输入端熔断 | 连续 2 周 ideas=0 | `reflection_jobs._analyze_collected_state()` → input_pipeline_broken |

### 自成长链路

| 链 | 名称 | 触发条件 | 执行函数 |
|----|------|----------|----------|
| ⑫ | 维度轮换 | 连续 3 轮同一维度原地踏步 | `optimize.py::optimize_cycle()` → 切换最弱维度 |
| ⑬ | 审核反馈闭环 | 人工审核退回 | `feedback_archive._append_session_summary_to_feedback()` → critic prompt 注入 |
| ⑭ | Cross-proposal 范例 | 当前 <0.75 且存在 ≥0.80 课题 | `optimize._load_cross_proposal_exemplar()` → writer prompt 注入 |
| ⑮ | KB 健康评分 | 每周反思 | `reflection_jobs._calculate_kb_health()` → 覆盖率/新鲜度/连通度 |
| ⑯ | 研究趋势雷达 | 每次 sync_all | `sync_engine._detect_research_trends()` → 关键词频率趋势 |
| ⑰ | 笔记覆盖率检测 | 每次 sync_all [3.6/5] | 统计 raw/papers → wiki/papers 转化率 |

---

*维护者：AI 编码代理*
*关联文档：`docs/ARCHITECTURE.md`（完整架构）、`AGENTS.md`（项目规范）*
