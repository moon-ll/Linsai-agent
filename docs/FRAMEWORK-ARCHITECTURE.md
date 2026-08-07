# LinSai-CoPilot 框架结构设计文档（v6.8.9）

> 本文档完整记录项目当前最新（v6.8.9）的框架结构、架构设计、模块边界与协作关系，供后续检查、改进、重构时参考。
> 权威数据源：`AGENTS.md`、`docs/ARCHITECTURE.md`、`memory/nsfc-standards.json`、`scripts/adversarial/constants.py`。
> 最后更新：2026-08-07

---

## 目录

1. [项目概述与核心比喻](#1-项目概述与核心比喻)
2. [技术栈](#2-技术栈)
3. [架构层次总览](#3-架构层次总览)
4. [模块分类与导入边界](#4-模块分类与导入边界)
5. [数据域隔离](#5-数据域隔离)
6. [目录结构](#6-目录结构)
7. [Web API 命名空间](#7-web-api-命名空间)
8. [hermes 协作架构](#8-hermes-协作架构)
9. [提案生命周期（核心）](#9-提案生命周期核心)
10. [评分体系（4 层）](#10-评分体系4-层)
11. [对抗纠偏机制（v6.8.9）](#11-对抗纠偏机制v689)
12. [Agent 分数机制](#12-agent-分数机制)
13. [辅助链路（健康/看板/修复/自成长）](#13-辅助链路健康看板修复自成长)
14. [Cron 调度框架](#14-cron-调度框架)
15. [安全与隐私](#15-安全与隐私)
16. [测试策略](#16-测试策略)
17. [版本与升级](#17-版本与升级)
18. [附录：关键常量速查](#18-附录关键常量速查)

---

## 1. 项目概述与核心比喻

**LinSai-CoPilot**（林赛协作引擎）是一个**虚拟合作者系统**——让林赛（Lin Sai）作为用户的专属 AI 协作者，1 对 1 深度协作，共同推进实际工作（主要是 NSFC 基金申请书撰写与研究课题管理）。

**核心比喻**：钢铁侠的贾维斯（J.A.R.V.I.S）。不是群聊里的旁观者，而是随时待命、深度参与、主动感知的个人合作者。

### 与相关项目的关系

| 项目 | 角色 | 关系 |
|------|------|------|
| **virtu-LinSai** | 人格资产生产端 | 上游。通过 190 万字自传叙事生长出林赛的完整人格（SOUL.md / SKILL.md / 林赛-perspective）。本项目**引用但不修改**其资产。 |
| **persona-discussion (Agora)** | 历史人物群聊应用 | 参考架构。Agora 是"多人会议室"，本项目是"专属办公室"。可复用其池管理/状态机思想，但交互模型完全不同。 |
| **hermes** | 本地 agent 执行引擎 | 下游/搭档。CoPilot 通过 hermes CLI 调用其 profile 完成多轮 agent loop 任务。 |
| **LinSai-CoPilot** | 虚拟合作者应用 | 本项目。消费 virtu-LinSai 人格资产，以 1v1 CoPilot 模式服务用户，并作为 hermes 的指挥台。 |

### 与 Agora 的核心差异

| 维度 | Agora | LinSai-CoPilot |
|------|-------|----------------|
| 交互模式 | 群聊 / @追问 | 1v1 持续对话，无旁观者 |
| 角色定位 | 历史人物旁观评论 | 当代同行并肩工作 |
| 关系深度 | 浅层、事件驱动 | 深层、长期记忆、持续学习用户偏好 |
| 主动性 | 被动响应 | 主动感知、主动提醒、主动推进 |
| 目标 | 获取多角度建议 | **一起完成具体工作** |
| 时间感 | 历史人物活在各自时代 | 林赛活在"当下"（2026），与用户同步时间 |
| 执行架构 | 单次 LLM 调用 | CoPilot 监控 + hermes agent loop 执行 |

---

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 运行环境 | Python 3（仅标准库） | 零第三方依赖。无任何构建文件。 |
| 内容格式 | Markdown（.md） | 对话记录、任务描述、记忆片段、知识库笔记。 |
| 元数据 | JSON | 会话状态、记忆索引、任务追踪、管线状态。 |
| LLM 接口 | MiniMax-M3（主）/ GLM-5.2 / Kimi CLI / Claude CLI | 通过 hermes profile 管理，CoPilot 侧 `llm_router.py` / `llm_gateway.py` 自动降级。 |
| Web 服务器 | Python `http.server.ThreadingHTTPServer` | 零第三方依赖，REST API + SSE 流式输出。 |
| 前端 | 原生 HTML/CSS/JS | 零框架依赖，CSS 变量 + `data-theme` 切换主题。 |
| 路径处理 | `pathlib.Path` | 禁止硬编码绝对路径，统一在 `paths.py` 中声明。 |
| 进程锁 | `fcntl.flock`（POSIX） | macOS/Linux 跨进程锁；Windows 降级为无锁 + 原子写入。 |

**关键约束**：
- 所有 Python 脚本仅使用标准库，不引入第三方包。
- 敏感凭据（API Key）只存放在本地 `.env` 和 `memory/llm-config.json`，两者均已加入 `.gitignore`。

---

## 3. 架构层次总览

```
┌─────────────────────────────────────────────────────────────────┐
│  Web 界面层（HTML/CSS/JS）                                      │
│  仪表盘 | 控制台 | 全链路 | 知识库 | 设置 | 对话式审核          │
│  REST API + SSE 流式通信                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  CoPilot 核心（操作台/监控层）                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ 会话管理     │ │ 记忆系统     │ │ 任务管理     │ │ 知识库    │ │
│  │ session_    │ │ memory_     │ │ task_       │ │ kb_*      │ │
│  │ manager     │ │ manager     │ │ manager     │ │           │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ LLM 路由    │ │ 自主引擎    │ │ 技能系统    │ │ 工具引擎  │ │
│  │ llm_router/ │ │ proactive_  │ │ skill_     │ │ tool_     │ │
│  │ llm_gateway │ │ engine      │ │ manager    │ │ engine    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  hermes 执行端（agent loop）                                     │
│  linsai → pipeline-runner → researcher → analyst → writer       │
│        ↔ critic → reviewer                                      │
│  7 个 profile，通过 hermes CLI 调用                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│  总控/监控层（orchestrator）                                     │
│  profile_health / failure_analyzer / strategy_optimizer          │
│  lifecycle_monitor / prompt_optimizer / retrospective            │
│  看板系统（system-kanban.json）                                   │
└─────────────────────────────────────────────────────────────────┘
```

**当前架构定位（v6.8+）**：
- **CoPilot** 是操作台/监控层：提供 Web 界面、会话管理、知识库、任务追踪、提案生命周期可视化和人工决策入口。
- **hermes** 是执行端：通过 7 个专业 profile 运行 agent loop，负责文献调研、缺口分析、申请书撰写、对抗优化等重脑力工作。
- 两者通过 `state_sync.py`（论文统一状态）、`memory_bridge.py`（记忆同步）、`hermes_pipeline.py`（管线派活）协同。
- 全自动链路以**课题生命周期**为核心：按 4 个时段轮转推进每个 optimizing proposal，每个时段聚焦一个课题直至完成完整一轮。

---

## 4. 模块分类与导入边界

| 分类 | 命名约定 | 可被谁导入 |
|------|----------|-----------|
| **CoPilot 核心** | 无前缀，如 `session_manager.py`、`copilot_engine.py` | 核心模块互相导入；研究管线模块**不可导入**。 |
| **研究管线** | 管线特有文件名，如 `pipeline_orchestrator.py` | 管线模块互相导入；核心模块**不可导入**（`web_server.py` 作为聚合器导入 `web_routes_pipeline.py` 除外）。 |
| **共享基础设施** | `common.py`、`paths.py`、`llm_gateway.py`、`hermes_memory.py` | 双方均可导入。 |
| **知识库引擎** | `kb_*.py` | 管线模块**只读导入**；写操作须通过 `learning_engine` 标准接口。 |
| **Web 路由 Mixin** | `web_routes_*.py` | 仅被 `web_server.py` 聚合器导入。 |

**研究管线模块禁止导入**：`session_manager`、`copilot_engine`、`context_builder`、`memory_manager`、`proactive_engine`、`llm_router`（须通过 `llm_gateway`）、`learning_engine`、`skill_manager`、`slash_commands`、`tool_engine`、`sync_engine`、`briefing_sync`、`agora_bridge`、`hermes_bridge`。

---

## 5. 数据域隔离

```
LinSai-CoPilot/
├── sessions/              ← CoPilot 核心：会话存档
├── memory/                ← CoPilot 核心：长期记忆、用户画像
├── tasks/                 ← CoPilot 核心：任务管理
├── knowledge/             ← 共享：知识库（管线只读）
├── projects/              ← CoPilot 核心：v3.5 课题管理（当前未启用）
├── research_proposals/    ← 研究管线：独立数据域
│   ├── drafts/optimizing/pending_review/archived  ← 四阶段
│   └── {proposal_id}/    ← 每个 proposal 的 00-05 阶段产物
│       ├── 00_pipeline/        ← 管线产物
│       ├── 01_analysis/        ← 分析产物
│       ├── 02_literature/      ← 文献产物
│       ├── 03_method/          ← 方法学手册
│       ├── 04_proposal/        ← 申请书（含 sections/ 分章节）
│       └── 05_review/          ← 评审报告（critic-round-N.md等）
└── scripts/               ← 所有模块
```

- 管线模块的所有写入操作限定在 `research_proposals/{proposal_id}/` 内。
- 管线模块不直接修改 `knowledge/` 和 `memory/` 下的文件。

---

## 6. 目录结构

```
LinSai-CoPilot/
├── AGENTS.md                  # AI 代理必读指南
├── README.md                  # 人类可读的项目说明
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源（当前 6.8.9）
├── .env                       # 本地 API 密钥（gitignore，不提交）
├── .gitignore                 # Git 忽略规则
│
├── persona/                   # 林赛人格资产（注入材料）
│   ├── lin-sai-persona.md     # 整合版人格注入文件
│   └── source-manifest.json   # 来源追踪
│
├── sessions/                  # 对话会话存档（gitignore）
├── memory/                    # 长期记忆与上下文（gitignore，含 llm-config.json）
│   ├── nsfc-standards.json    # NSFC 质量标准（唯一权威源）
│   ├── agent-scores.json      # agent 奖惩分数
│   ├── system-kanban.json     # 系统看板
│   └── ...
├── tasks/                     # 工作项（gitignore）
├── references/                # 用户提供的参考资料（只读）
├── knowledge/                 # 知识库（Obsidian Vault）
├── skills/                    # 技能定义
├── research_proposals/        # 研究管线数据域
├── docs/                      # 文档
│   ├── ARCHITECTURE.md        # 完整架构说明
│   ├── PROJECT-STRUCTURE.md   # 目录结构
│   ├── SCORING-STANDARDS.md   # 评分标准
│   └── FRAMEWORK-ARCHITECTURE.md  # 本文件
├── scripts/                   # 所有 Python 脚本
│   ├── web_server.py          # Web 服务器入口
│   ├── copilot_engine.py      # CoPilot 引擎
│   ├── common.py              # 共享基础设施
│   ├── paths.py               # 路径管理
│   ├── proposal_lifecycle/    # 生命周期包
│   │   ├── optimize.py        # 对抗优化
│   │   ├── completion.py      # 达标判定
│   │   ├── constants.py       # 生命周期常量
│   │   └── ...
│   ├── lifecycle/             # 生命周期 cron 框架
│   │   └── executor.py        # 单步执行器
│   ├── adversarial/           # 对抗纠偏包
│   │   ├── scoring.py         # 分数计算（含质量门槛）
│   │   ├── constants.py       # 对抗常量
│   │   ├── monitor.py         # monitor 步骤
│   │   ├── governance.py      # 组合类
│   │   └── prohibitions.py    # 禁止清单
│   ├── weekend_pipeline/      # 周末流水线
│   ├── web_routes_*.py        # Web 路由 Mixin
│   └── tests/                 # 单元测试
└── logs/                      # 日志（gitignore）
```

---

## 7. Web API 命名空间

Web 服务器以 Mixin 聚合 12 个路由模块，命名空间按功能归属分为 CoPilot 核心与研究管线。

| 命名空间 | 归属 | 说明 |
|----------|------|------|
| `/api/sessions/` | CoPilot 核心 | 会话管理、消息、聊天记录 |
| `/api/tasks/` | CoPilot 核心 | 任务 CRUD、状态流转、AI 辅助指派 |
| `/api/knowledge/` | CoPilot 核心 | 知识库搜索、wiki、图谱、健康、PDF |
| `/api/skills/` | CoPilot 核心 | 技能列表、配置 |
| `/api/learning/` | CoPilot 核心 | 学习日志、待审队列、统计 |
| `/api/projects/` | CoPilot 核心 | 项目面板、NSFC 决策、论文池 |
| `/api/research/` | CoPilot 核心 (v3.5) | 课题指导 |
| `/api/hermes/` | CoPilot 核心 | hermes cron、oneshot、团队 profile 状态 |
| `/api/sync/`、`/api/backup/` 等 | CoPilot 核心 | 系统状态 |
| `/api/lifecycle/` | CoPilot 核心 (v6.5+) | 提案生命周期仪表盘、注册、流转、优化、agent scores、monitor 历史、负反馈告警清除 |
| `/api/orchestrator/` | CoPilot 核心 (v6.7+) | 林赛总控：仪表盘、profile 健康、失败模式、调度策略、链路质量 |
| `/api/console/` | CoPilot 核心 (v6.7.7+) | 林赛控制台：流水线总览、Agent 工作状态、告警 inbox、一键修复/编排/优化 |
| `/api/settings/` | CoPilot 核心 (v6.7.7+) | 设置中心：7 类配置读写与变更预览 |
| `/api/pipeline/` | 研究管线 (v6.2+) | 管线编排、Agent 团队、缺口、课题、问题、申请书、自检、引文、方法学 |

Web 服务器使用 Mixin 架构聚合 12 个路由模块；`research` 和 `pipeline` 使用独立分派器，其余走统一路由表。

---

## 8. hermes 协作架构

7 个专业 profile 组成研究管线团队：

```
linsai（总控）          pipeline-runner（编排器）
  │                        │
  │ 简报 cron               │ 每日编排 cron
  ↓                        ↓
researcher ← analyst ← writer ↔ critic → reviewer
（文献调研）  （缺口分析）（撰写）  （对抗）（终审）
```

| Profile | 模型 | 职责 |
|---------|------|------|
| `linsai` | MiniMax-M3 | 方向校准 / 总控 / 简报 |
| `pipeline-runner` | MiniMax-M3 | 管线编排 / 每日触发 |
| `researcher` | MiniMax-M3 | 文献调研 / 定向检索 |
| `analyst` | MiniMax-M3 | 缺口分析 / 科学问题 |
| `writer` | MiniMax-M3 | 申请书撰写 / 修订 |
| `critic` | MiniMax-M3 | 对抗式评审（红队） |
| `reviewer` | MiniMax-M3 | 质量终审（monitor 角色） |

**关键协作文件**：
- `state_sync.py`：论文统一状态总线（`item-status.json`），CoPilot 与 hermes 共享。
- `memory_bridge.py`：将 hermes `MEMORY.md` / `USER.md` 同步到 CoPilot `memory/`。
- `hermes_pipeline.py`：将六阶段派活给对应 profile，支持增量优化、产物检查、cron 自动化。
- `proposal_lifecycle/` 包：四阶段生命周期 + writer-critic 对抗优化循环。薄 shim `proposal_lifecycle.py` 保留 CLI。
- `adversarial/` 包：对抗评审奖惩与监察引擎。薄 shim `adversarial_governance.py` 保留导入。
- `weekend_pipeline/` 包：周末输入/输出/反思小任务流水线。

---

## 9. 提案生命周期（核心）

### 9.1 四阶段流转

```
drafts（初稿）→ optimizing（优化中）→ pending_review（待校验）→ archived（归档）
```

**命名规则**：`{项目类型}-{课题名称}-{YYYYMMDD}[-序号]`，项目类型 `general`/`key`/`major`。

### 9.2 5 个申请书模块

| 模块 key | 中文名 | 说明 |
|----------|--------|------|
| `rationale` | 立项依据 | 回答"为什么要做" |
| `content` | 研究内容 | 回答"做什么" |
| `scheme` | 研究方案 | 回答"怎么做"（含特色创新与预期成果） |
| `full_review` | 整体一致性审查 | 跨模块逻辑衔接、术语一致性 |
| `references` | 参考文献校验 | 引文准确性、相关性、格式 |

### 9.3 一轮完整优化顺序

```
① 三章节并行撰写/评审（rationale + content + scheme）
  → ② 整篇一致性修订（full_review）
  → ③ 参考文献校验/补充（references）
  → ④ monitor meta-review（收尾）
```

### 9.4 4 个时段轮转

| 时段 | 时间 | 说明 |
|------|------|------|
| 1 | 00:30-03:30 | 深夜时段 |
| 2 | 04:00-08:00 | 清晨时段 |
| 3 | 08:30-12:30 | 上午时段 |
| 4 | 18:30-22:30 | 晚间时段 |

每个时段聚焦一个 proposal，未完成则下一时段继续，已完成则切换下一个。工作日按 4 时段轮转，周末暂停 worker，集中执行输入端/输出端/链路反思任务。

### 9.5 微调度器（Micro Scheduler）

- 每个时段开始时，微调度器决定哪个 proposal 本轮执行。
- 无条件清理 stale job（阈值 1800s）。
- 轮次完成后 break 防止同一时段内启动新轮次。
- 派生 job 优先级：`update_vision`(7) 和 `update_method_manual`(8) 在 `_CHAIN_ORDER` 中。
- `round_num` 作为 `_job_priority_key` 第一维度，确保当前轮次 job 优先于下一轮。

### 9.6 进入待评审的 3 个条件

`completion.py::_check_done`：

1. **条件 1（达标）**：5 模块全部通过（分数 ≥ 0.90 且各维度无短板）+ **monitor 独立评分复核通过**（v6.8.9 新增，防串通）。
2. **条件 2（逃生阀）**：连续 5 轮无显著提升（`DEFAULT_NO_IMPROVEMENT_LIMIT = 5`）。
3. **条件 3（逃生阀）**：达到最大轮数 8（`DEFAULT_MAX_ROUNDS = 8`）。

---

## 10. 评分体系（4 层）

一个课题的"质量分"由 4 层机制共同决定：

| 层 | 主体 | 分数区间 | 含义 |
|----|------|---------|------|
| critic 章节评分 | reviewer profile（critic） | 0-1 | 对申请书某一模块的深度评审得分 |
| agent 奖惩分 | monitor 规则层 | 0-150（初始 100） | writer/critic 的长期信誉分 |
| 达标判定 | 生命周期引擎 | 布尔 | 依阈值判定是否流转 |
| 程序化天花板 | 代码检测 | 0-1（硬上限） | AI 写作味检测，critic 表达分不得超此上限 |

> 注意：critic 对申请书的评分（0-1）与 critic agent 的奖惩分（0-150）是两套数据，勿混淆。

### 10.1 达标阈值

| 项目 | min_overall_score | max_high_issues | max_medium_issues |
|------|:---:|:---:|:---:|
| general 面上 | **0.90** | 0 | 3 |
| key 重点 | **0.90** | 0 | 2 |
| major 重大 | **0.90** | 0 | 1 |

### 10.2 维度权重

| 维度 | general 面上 | key 重点 | major 重大 |
|------|:---:|:---:|:---:|
| 创新性 | 0.30 | 0.25 | 0.15 |
| 可行性 | 0.25 | 0.10 | 0.10 |
| 严谨性 | 0.25 | 0.20 | — |
| 表达质量 | 0.20 | 0.10 | — |
| 系统性 | — | 0.20 | — |
| 战略意义 | — | 0.15 | 0.25 |
| 顶层设计 | — | — | 0.20 |
| 多学科交叉 | — | — | 0.15 |
| 团队实力 | — | — | 0.15 |

### 10.3 评分完整性规则（7 条）

1. **不准虚高**：程序化天花板 < 0.7 时综合分 ≤ 0.75；0.7-0.8 时 ≤ 0.80；0.8-0.9 时 ≤ 0.85。
2. **参考文献轮次**：创新性/可行性标记 N/A，综合分仅由严谨性+完整性等权平均。
3. **禁止纯机械评审**：缺"写作风格评估"与"范本对标"段落 → 评审无效。
4. **锚点对比强制**：评审必须含"锚点对比"段落，缺失即无效。
5. **表达天花板强制**：critic 表达分超过程序化天花板则程序强制 cap。
6. **逐条清单**：不通过条目 > 3 时该 section 分 ≤ 0.70。
7. **自引用封顶**：全文"详§X/见§X" > 10 次扣 0.05，> 15 次扣 0.10。

### 10.4 程序化表达质量天花板

`ceiling = 1.0`，逐项检测违规扣减，最低 0.5。

| 检测项 | 阈值 | 每超扣 |
|--------|:---:|:---:|
| AI 关联词（基础上/此外/同时/因此/然而/基于此） | > 8 | 0.02 |
| 模板句式（为…提供…基础/支撑/途径） | > 8 | 0.03 |
| 模板主语（本项目拟/将/计划/旨在句首） | > 5 | 0.02 |
| 冗余修饰词（显著/重要/系统/良好/成熟） | > 12 | 0.01 |
| 超长句（单句 > 120 字） | 每千字 > 1 | 0.02 |
| 元话语（沿着…主线/我们可以辨识/值得注意的是） | > 2 | 0.03 |
| 加粗过度 | 每千字 > 3 | 0.03 |
| 列表替代论述 | 每处 | 0.05 |

---

## 11. 对抗纠偏机制（v6.8.9）

### 11.1 监考者把关（monitor gate）

`completion.py::_check_done` 条件 1 新增 monitor 复核：

即使 5 模块对抗全胜，若 monitor 独立评分 < 达标线（0.90），**判定未达标，不予流转，继续优化**。防止 writer+critic 串通虚高通过。

### 11.2 Writer 质量门槛

`scoring.py::_writer_quality_gate`：

| monitor 独立评分 | 额外分 | 含义 |
|:---:|:---:|------|
| < 0.50 | **-5** | 质量过差，反向抑制表面微调 |
| 0.50-0.70 | **-2** | 质量欠佳，抑制正奖励 |
| ≥ 0.70 | 0 | 正常 |

### 11.3 Critic 评审质量门槛

`scoring.py::_critic_quality_gate`：

| 情形 | 额外分 | 含义 |
|------|:---:|------|
| monitor < 0.60 且 critic 给分 ≥ 0.75 | **-8** | 虚高放水 |
| monitor ≥ 0.75 且 critic 给分 < 0.55 | **-4** | 过度苛刻 |
| 其余 | 0 | 正常 |

### 11.4 维度提取修复（v6.8.9）

`optimize.py::_extract_dimension_scores`：

- 旧 bug：表格 `| 创新性（innovation） | 0.30 | 0.78 |`，正则匹配到第一个数字（权重 0.30）。
- 修复：取表格行内**最后一个** 0.x 数字作为得分列；非表格回退到行内格式。

---

## 12. Agent 分数机制

持久化于 `memory/agent-scores.json`，区间 **0-150**，初始 **100**。

### 12.1 Writer 分数构成

```
writer_delta = monitor_delta × 20              # monitor 独立评分变化
            + max(0, 高分问题减少数) × 3        # 实质消解问题
            + 违规扣分                           # 禁止清单
            + writer 质量门槛(monitor_score)     # v6.8.9
```

### 12.2 Critic 分数构成

```
critic_delta = monitor上升奖励(×15) + 高分问题检出奖励(×2)
             - monitor回归惩罚(5)
             + 违规扣分
             + 校准奖励/惩罚（误差<0.10 奖 3；>0.20 罚）
             + critic 评审质量门槛               # v6.8.9
```

### 12.3 其他机制

- **批评家恢复**：critic 分 < 20 且近 5 轮无严重违规，每次 +3。
- **串通惩罚**：collusion_risk medium/high 时，正奖励清零并额外 -5/-10。
- **负反馈告警**：monitor 独立分连续 3 轮下降、writer/critic 双降、串通连续 2 轮 ≥ medium、全局分 < 50 → 暂停自动流转，等待人工介入。
- **低分预警**：课题分 < 0.65 且趋势恶化时标记 `low_score_alert`。

### 12.4 禁止清单扣分

| writer 违规 | 扣分 | critic 违规 | 扣分 |
|-------------|:---:|-------------|:---:|
| fabrication 杜撰 | -12 | lazy_review 消极评审 | -10 |
| wrong_citation 错误引用 | -8 | rigid_scoring 僵化评分 | -8 |
| template_rigidity 僵化模板 | -6 | missed_major 遗漏重大问题 | -10 |
| unaddressed_issues 未解决 | -8 | unactionable 不可操作建议 | -6 |
| off_section 越界修改 | -5 | score_content_mismatch 评分矛盾 | -8 |
| placeholder 占位符 | -4 | | |
| surface_change 表面修改 | -5 | | |

---

## 13. 辅助链路（健康/看板/修复/自成长）

四条辅助链路保障全链路稳定运转：

### 13.1 健康检查

- `lifecycle_monitor.py`（每小时 cron `lc-hourly-monitor`）：检测 cron 缺失/陈旧、卡住课题、连续失败、零进展、API 限流。异常去重后飞书通知，cron 缺失自动修复。
- `profile_health.py`：计算 7 个 hermes profile 的健康度。
- `failure_analyzer.py`：从日志聚类 8 种失败模式。

### 13.2 看板系统

- `memory/system-kanban.json`：由微调度器（主写）和 `lifecycle_monitor`（合并写）协同维护。
- 包含：当前时段、聚焦课题、job 进度、执行历史、任务同步统计。
- 前端通过 `/api/console/flow` 展示。

### 13.3 定期修复

- `lc-repair` cron 每 6 小时执行：重置 stuck running（阈值 1800s）、重试 failed job（最多 3 次）、补齐缺失 worker、清理旧轮次 job。
- 微调度器每次执行前无条件清理 stale job。

### 13.4 自成长

- `strategy_optimizer.py`：基于 7 天历史给出调度参数建议（仅建议）。
- `prompt_optimizer.py`（每日 14:00 cron `lc-prompt-optimize`）：从 debug journal / agent scores / failure patterns 生成 prompt 修改建议并自动应用（备份原文件）。
- `retrospective.py`（每周一 15:00 cron `lc-retrospective`）：综合 5 个数据源生成结构化复盘报告。

---

## 14. Cron 调度框架

### 14.1 总览

| Cron 名称 | 频率 | 职责 |
|-----------|------|------|
| `lc-daily-orchestrate` | 每日 00:00 | 每日编排：生成 checkpoint、确保 worker 存在 |
| `lc-hourly-monitor` | 每小时 | 健康检查：检测异常、自动修复 cron 缺失 |
| `lc-repair` | 每 6 小时 | 定期修复：stuck/failed 恢复、补齐 worker |
| `lc-prompt-optimize` | 每日 14:00 | Prompt 自动优化 |
| `lc-retrospective` | 每周一 15:00 | 链路复盘 |
| worker cron（per-proposal） | 每个时段 | 每个 optimizing proposal 一个独立 worker |

### 14.2 设计原则

- 不再使用单一大型 `pipeline-runner` cron sweep。
- 小型化：每个 optimizing proposal 一个独立 worker cron，每次只执行下一个 pending 小步骤。
- 每日编排 cron 只生成 checkpoint、确保 worker 存在，自身不调用 LLM。
- checkpoint 持久化在 `_lifecycle.json` 的 `pipeline_jobs` 中，单步骤失败可单独重跑。
- worker cron 自动错开 6 分钟（基于 proposal_id hash 分配 47/53/59/05/11...）。

### 14.3 执行流程

```
每日编排 (lc-daily-orchestrate)
  → 生成并同步 checkpoint（micro scheduler）
  → 确保每个 optimizing proposal 有 worker cron
  → 注册缺失的 cron

worker cron（每个 proposal 独立）
  → 加锁 → pick_next_job → execute_job
  → 支持串行执行（同一 proposal 一次只有一个 job）
  → monitor 步骤成功后 sync_checkpoint 生成下一轮

修复 cron (lc-repair)
  → 扫描所有 proposal → 重置 stuck running
  → 重试 failed（最多 3 次）→ 补齐缺失 worker
  → 清理旧轮次 job
```

---

## 15. 安全与隐私

| 原则 | 说明 |
|------|------|
| 无敏感凭据入仓 | API Key 只存于本地 `.env` 和 `memory/llm-config.json`，均已 `.gitignore` |
| 本地优先 | 所有数据仅存于本地文件系统，不上传云端 |
| 用户数据边界 | `references/` 目录默认只读；知识库 `raw/` 保留原貌 |
| 路径遍历防护 | `_safe_join`、`_validate_proposal_id`、禁止 `..` |
| 并发安全 | `common.file_lock`（POSIX `fcntl.flock`）+ 原子写入 |
| XSS 防护 | 前端 `escapeHtml` / `escapeAttr` 输出用户可控内容 |
| 命令执行白名单 | `tool_engine.run_command` 仅允许白名单命令前缀 |
| 记忆隔离 | 不同用户记忆完全隔离，不共享 |

---

## 16. 测试策略

### 三层测试体系

1. **单元/核心回归测试**：`python3 scripts/self_test.py`，支持 `--module` / `--scenario` / `--persona` / `--web` / `--web-ci`。
2. **模块自检**：大量脚本支持 `--self-check`，运行 `python3 scripts/{module}.py --self-check`。
3. **E2E 集成测试**：`python3 scripts/test_e2e_learning_full.py`（需真实 Claude CLI 环境，非日常回归项）。

### 当前基线（v6.8.9）

| 测试套件 | 通过数 | 覆盖内容 |
|----------|:------:|----------|
| `--module` | **332/332** | 生命周期 cron、对抗评审、提案 KB 同步、周末任务流水线、章节评审/整体评审、微调度器、轮次 break、derived job 优先级、prompt 优化器、看板轮次统计、stale job 回收、monitor 看板时间戳、维度提取修复、质量门槛 |
| `--scenario` | 16/16 | 场景测试 |
| `--persona` | 38/38 | 人格测试 |
| `--web-ci` | 252/252 | Web API 虚拟用户测试覆盖所有主要 API 命名空间 |

**测试设计原则**：零污染（临时隔离目录运行）、零成本（不调用 LLM API）、自动发现（新增 `scripts/tests/test_*.py` 自动纳入回归）。

---

## 17. 版本与升级

### 版本号规范

- **版本号来源**：`VERSION` 文件为唯一真相源（当前 `6.8.9`）。
- **格式**：`MAJOR.MINOR.PATCH`。MAJOR：不兼容数据变更；MINOR：新增功能；PATCH：缺陷修复/文档/性能。

### Git 管理策略

- 用户数据已由 `.gitignore` 排除，不会意外提交。
- 每次功能迭代一个 commit，消息格式：`vX.Y.Z - 简短描述`。
- 重要变更同步更新 `CHANGELOG.md`。

### 数据安全原则

| 原则 | 说明 |
|------|------|
| 用户数据无价 | 对话记录、记忆、任务一旦丢失不可重建 |
| 备份优先 | 任何更新操作前必须先备份 |
| 恢复可验证 | 备份包必须能完整恢复 |
| 升级可回滚 | 升级失败时能一键回到之前状态 |

### 标准升级流程

```bash
# 推荐：升级助手
python3 scripts/upgrade.py --check
python3 scripts/upgrade.py --simulate
python3 scripts/upgrade.py

# 手动
python3 scripts/backup_manager.py
git pull
python3 -m py_compile scripts/*.py
```

---

## 18. 附录：关键常量速查

| 常量 | 值 | 位置 |
|------|:---:|------|
| `DEFAULT_MAX_ROUNDS` | 8 | `proposal_lifecycle/constants.py` |
| `DEFAULT_SCORE_THRESHOLD` | 0.90 | `proposal_lifecycle/constants.py` |
| `DEFAULT_NO_IMPROVEMENT_LIMIT` | 5 | `proposal_lifecycle/constants.py` |
| `LOW_SCORE_ALERT_THRESHOLD` | 0.65 | `adversarial/constants.py` |
| `DEFAULT_INITIAL_SCORE` | 100 | `adversarial/constants.py` |
| `SCORE_MIN` / `SCORE_MAX` | 0 / 150 | `adversarial/constants.py` |
| `MONITOR_DELTA_CAP` | 15 | `adversarial/constants.py` |
| `WRITER_PROGRESS_WEIGHT` | 20 | `adversarial/constants.py` |
| `CRITIC_PROGRESS_WEIGHT` | 15 | `adversarial/constants.py` |
| `WRITER_QUALITY_GATE_LOW` | 0.50 | `adversarial/constants.py`（v6.8.9） |
| `WRITER_QUALITY_GATE_MID` | 0.70 | `adversarial/constants.py`（v6.8.9） |
| `CRITIC_INFLATION_MONITOR_THRESHOLD` | 0.60 | `adversarial/constants.py`（v6.8.9） |
| `CRITIC_INFLATION_SCORE_THRESHOLD` | 0.75 | `adversarial/constants.py`（v6.8.9） |
| `CRITIC_OVERHARSH_MONITOR_THRESHOLD` | 0.75 | `adversarial/constants.py`（v6.8.9） |
| `CRITIC_OVERHARSH_SCORE_THRESHOLD` | 0.55 | `adversarial/constants.py`（v6.8.9） |
| `STALE_RUNNING_SECONDS` | 1800 | `lifecycle/constants.py` |
| `RECOVERY_BONUS` | 3.0 | `adversarial/constants.py` |
| 达标线（三类项目） | 0.90 | `memory/nsfc-standards.json` |
| 低分预警阈值 | 0.65 | `adversarial/constants.py` |
| agent 分区间 | 0-150 | `adversarial/constants.py` |
| 面上维度权重 | 0.30/0.25/0.25/0.20 | `memory/nsfc-standards.json` |