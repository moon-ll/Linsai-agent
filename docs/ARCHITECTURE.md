> 本文件由 AGENTS.md 的架构说明一节拆分而来，供快速查阅。

## 架构说明

### 1. 模块分类与导入边界

| 分类 | 命名约定 | 可被谁导入 |
|------|----------|-----------|
| **CoPilot 核心** | 无前缀，如 `session_manager.py`、`copilot_engine.py` | 核心模块互相导入；研究管线模块**不可导入**。 |
| **研究管线** | 管线特有文件名，如 `pipeline_orchestrator.py`、`gap_analyzer.py` | 管线模块互相导入；核心模块**不可导入**（`web_server.py` 作为聚合器导入 `web_routes_pipeline.py` 除外）。 |
| **共享基础设施** | `common.py`、`paths.py`、`llm_gateway.py`、`hermes_memory.py` | 双方均可导入。 |
| **知识库引擎** | `kb_*.py` | 管线模块**只读导入**；写操作须通过 `learning_engine` 标准接口。 |
| **Web 路由 Mixin** | `web_routes_*.py` | 仅被 `web_server.py` 聚合器导入。 |

**研究管线模块禁止导入**：`session_manager`、`copilot_engine`、`context_builder`、`memory_manager`、`proactive_engine`、`llm_router`（须通过 `llm_gateway`）、`learning_engine`、`skill_manager`、`slash_commands`、`tool_engine`、`sync_engine`、`briefing_sync`、`agora_bridge`、`hermes_bridge`。

### 2. 数据域隔离

```
LinSai-CoPilot/
├── sessions/              ← CoPilot 核心：会话存档
├── memory/                ← CoPilot 核心：长期记忆、用户画像
├── tasks/                 ← CoPilot 核心：任务管理
├── knowledge/             ← 共享：知识库（管线只读）
├── projects/              ← CoPilot 核心：v3.5 课题管理（当前未启用）
├── research_proposals/    ← 研究管线：独立数据域
│   ├── drafts/optimizing/pending_review/archived  ← 生命周期四阶段
│   └── {proposal_id}/00_pipeline ... 05_review    ← 六阶段产物
└── scripts/               ← 所有模块
```

- 管线模块的所有写入操作限定在 `research_proposals/{proposal_id}/` 内。
- 管线模块不直接修改 `knowledge/` 和 `memory/` 下的文件。

### 3. Web API 命名空间

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
| `/api/sync/`、`/api/backup/`、`/api/usage/` 等 | CoPilot 核心 | 系统状态 |
| `/api/lifecycle/` | CoPilot 核心 (v6.5+) | 提案生命周期仪表盘、注册、流转、优化、agent scores、monitor 历史、负反馈告警清除 |
| `/api/orchestrator/` | CoPilot 核心 (v6.7+) | 林赛总控：仪表盘、profile 健康、失败模式、调度策略、链路质量 |
| `/api/console/` | CoPilot 核心 (v6.7.7+) | 林赛控制台：流水线总览、Agent 工作状态、告警 inbox、一键修复/编排/优化 |
| `/api/settings/` | CoPilot 核心 (v6.7.7+) | 设置中心：链路/模板/Agent/任务/学习/自主/KB输出 7 类配置读写与变更预览 |
| `/api/pipeline/` | 研究管线 (v6.2+) | 管线编排、Agent 团队、缺口、课题、问题、申请书、自检、引文、方法学、hermes 驱动管线 |

Web 服务器使用 Mixin 架构聚合 12 个路由模块；`research` 和 `pipeline` 使用独立分派器，其余走统一路由表。

### 4. hermes 协作架构

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
| `reviewer` | MiniMax-M3 | 质量终审 |

关键协作文件：
- `state_sync.py`：论文统一状态总线（`item-status.json`），CoPilot 与 hermes 共享。
- `memory_bridge.py`：将 hermes `MEMORY.md` / `USER.md` 同步到 CoPilot `memory/`。
- `hermes_pipeline.py`：将六阶段派活给对应 profile，支持增量优化、产物检查、cron 自动化。
- `proposal_lifecycle/` 包（薄 shim `proposal_lifecycle.py` 保留 CLI 与导入）：四阶段（drafts → optimizing → pending_review → archived）+ writer-critic 对抗优化循环。
- `adversarial/` 包（薄 shim `adversarial_governance.py` 保留导入）（v6.7.6）：对抗评审奖惩与监察引擎，管理 agent 分数、禁止清单、monitor meta-review、负反馈检测。
- `weekend_pipeline/` 包（薄入口 `weekend_pipeline.py`）（v6.7.7）：周末输入/输出/反思小任务流水线，由 `lc-weekend-worker` 每 20 分钟执行一个 pending job。

### 5. 提案生命周期

```
drafts（初稿）→ optimizing（优化中）→ pending_review（待校验）→ archived（归档）
```

- **命名规则**：`{项目类型}-{课题名称}-{YYYYMMDD}[-序号]`，项目类型 `general`/`key`/`major`。
- **对抗优化**：按章节（立项依据→研究内容→研究方案→整体审查）轮转，critic 4 维度评分（创新/可行/严谨/完整），writer 聚焦最弱维度修订；达标需全模块通过。
- **小型化 cron 框架（v6.7.5+）+ 微调度器（v6.8.0+）**：
  - 不再使用单一大型 `pipeline-runner` cron sweep；改为每个 optimizing proposal 一个独立 worker cron，每次只执行下一个 pending 小步骤。
  - 每日编排 cron（`lc-daily-orchestrate`）只生成 checkpoint、确保 worker 存在，自身不调用 LLM。
  - 修复 cron（`lc-repair`）每 6 小时扫描：重置 stuck running、重试 failed（最多 3 次）、补齐缺失 worker、超过重试则告警。
  - checkpoint 持久化在 `_lifecycle.json` 的 `pipeline_jobs` 中，单步骤失败可单独重跑，不污染整体状态。
  - v6.7.6：worker cron 自动错开 6 分钟（基于 proposal_id hash 分配 47/53/59/05/11...），`--repair` 会检测 schedule 变化并自动更新。
  - v6.7.7：worker cron 默认仅工作日运行（schedule = `{minute} * * * 1-5`），周末暂停；新增 `--setup-weekend` / `--teardown-weekend` 创建/删除 3 个周末任务入口 cron（输入/输出/反思）以及 `lc-weekend-worker`（每 20 分钟执行一个 pending 小任务）。
  - v6.7.7：`run_repair()` 区分工作日与周末：工作日修复 worker/编排，周末修复输入/输出/反思任务及 `weekend-pipeline.json` 中的 checkpoint job。
  - **v6.8.0 微调度器**：`scripts/lifecycle/micro_scheduler.py` 引入全局微调度器，工作日按 4 个时段（00:30-03:30 / 04:00-08:00 / 08:30-12:30 / 18:30-22:30）轮流聚焦单个 proposal，每个时段只执行聚焦 proposal 的 pending job，保证同一 proposal 连贯推进。
  - **v6.8.1 微调度器增强**：失败任务自动重试（attempts < MAX_JOB_ATTEMPTS）、跨周轮转内容感知（`last_proposal_id` 校准）、系统看板文件（`memory/system-kanban.json`）同步任务进展、每轮优化完成后自动生成优化报告（`05_review/optimization-report-round-N.md`）。
  - **v6.8.1 任务系统集成**：微调度器与 task_manager 打通，每次执行后自动同步生命周期状态到任务系统。每个 optimizing proposal 的当前轮次自动创建/更新 task，支持 `backlog → active → completed` 状态流转。提供 `--sync-lifecycle-tasks` / `--sync-lifecycle-history` CLI 命令和 `POST /api/lifecycle/sync-tasks` / `sync-task-history` Web API。看板（`system-kanban.json`）增强 `task_sync` 字段，包含全局统计和映射数量。
- **对抗评审奖惩与监察（v6.7.6）**：
  - 每轮 checkpoint 拆为 critic → writer → monitor 三步骤，monitor 作为独立第三方 reviewer 做 meta-review。
  - `memory/agent-scores.json` 维护 writer/critic 全局奖惩分数（初始 100，上限 150，下限 0）。
  - 禁止清单（writer：占位符/模板僵化/表面修改；critic：消极评审/僵化评分/评分与内容矛盾）由规则层兜底，monitor 结合上下文判定。
  - 奖惩计算综合规则层 delta、monitor 建议、串通惩罚、校准奖励/惩罚。
  - 负反馈检测：monitor 独立分数连续下降 / 本地双降 / 连续串通 / 全局分数低于 50 触发告警，暂停自动流转，等待人工清除。
- **生命周期与知识库聚合（v6.7.6）**：
  - `scripts/proposal_kb_sync.py` 将各生命周期阶段 proposal 的核心信息（标题、状态、分数、核心问题、创新点、关键产物）同步到 `knowledge/wiki/projects/NSFC-强场超快/proposals/`，并自动生成索引，实现链路数据与全链路知识库聚合。
  - 已归档（approved）的 proposal 仍会通过 `proposal_lifecycle._archive_proposal` 生成独立归档元信息。
- **输入端与输出端重构（v6.7.7）**：
  - 输入端：`scripts/idea_generator.py`（`--auto` 已委托给 `weekend_pipeline` input 阶段）从文献简报/论文池/归档讨论/知识库识别研究缺口，生成研究设想；新设想先进入 `drafts`，人工确认后再进 `optimizing`；若与现有课题关联，给出有机融合建议。
  - 输出端：`scripts/knowledge_output.py`（`--weekly` 已委托给 `weekend_pipeline` output 阶段）归档 proposal 知识萃取，并将可靠来源信息写入 KB；AI 生成内容标记为 `derived`，无来源信息禁止入库。
  - 周末模式：worker cron 仅工作日运行（`Mon-Fri`），周末由 `weekend_pipeline/` 小任务流水线执行输入发现、输出萃取、链路反思和 KB 健康检查；`lc-weekend-worker` 每 20 分钟推进一个 pending job。
- **文献驱动**：优先优化与当天简报关键词匹配的课题，节省模型限额。
- **质量标准**：`memory/nsfc-standards.json` 定义面上/重点/重大三类项目的评分权重、页数限制、模板结构。

### 6. 林赛总控层（v6.7+）

在 hermes 执行层之上新增**监控 + 调优 + 失败分析 + 链路成长**总控层，由 `orchestrator.py` 统一入口：

| 子模块 | 职责 | 输出 |
|--------|------|------|
| `profile_health.py` | 读取 hermes profile 状态、`linsai.log` 派活记录、`_lifecycle.json` cron 失败记录 | 7 个 profile 的 idle/working/blocked/offline 状态、24h 成功率、平均耗时、最近错误 |
| `failure_analyzer.py` | 聚类日志失败模式 | 8 种模式（score-zero-streak / empty-draft / env-pollution / profile-timeout / file-missing / code-bug / rate-limit / low-content-after-rewrite）+ 建议 prompt 修改 |
| `strategy_optimizer.py` | 基于历史数据给出调度参数建议 | stagger / max_rounds / score_threshold / timeout 等调优建议（仅建议，不自动应用） |
| `orchestrator.py` | 整合以上 + pipeline 质量监控 | `compute_dashboard()` 4 区合一总仪表盘；`monitor_pipeline()` 生成低质量产物 growth_actions |

**交互入口**：
- Web API：`/api/orchestrator/dashboard`、`/api/orchestrator/profiles/health`、`/api/orchestrator/failures/patterns`、`/api/orchestrator/strategies`、`/api/orchestrator/strategies/apply`、`/api/orchestrator/pipeline/quality`、`/api/orchestrator/tuning-log`
- 前端：`web/js/orchestrator.js` 五子面板（总仪表盘 / Profile 健康 / 失败模式 / 调度策略 / 链路质量）

**设计原则**：
- **建议模式**：`strategy_optimizer` 只输出建议，人工通过 `POST /api/orchestrator/strategies/apply` 确认后写入 `tuning-log.json`。
- **可观测优先**：所有调优以 4 区仪表盘为起点。
- **模式而非规则**：失败分析用模式聚类，给出 `suggested_prompt_change`，由用户/AI 决定如何应用。
- **链路可成长**：`monitor_pipeline` 自动给低质量产物生成 `growth_actions`，提示人工重跑或自动优化。

### 7. 林赛控制台与设置中心（v6.7.7）

在总控层之上新增**面向用户的统一操作界面**，把「看状态」和「调配置」合并到一个入口：

| 子模块 | 职责 | 输出 |
|--------|------|------|
| `web_routes_system.py`（`/api/console/*`） | 流水线 / Agent / 告警 三视图 API | `/api/console/flow` 六阶段流水线；`/api/console/agents` profile + cron 状态；`/api/console/alerts` 负反馈/失败/待审 inbox |
| `web_routes_settings.py`（`/api/settings/*`） | 7 类配置统一读写 | `/api/settings/categories` 分类列表；`/:category` 读取/保存；`/:category/preview` 变更差异预览 |
| `web/js/console.js` | 控制台前端 | 流水线看板、Agent 卡片、告警列表、一键操作（修复/编排/优化/清除告警） |
| `web/js/settings_center.js` | 设置中心前端 | 7 类配置表单化编辑、JSON 源码切换、保存前差异预览、自动备份提示 |

**配置分类**：
- `pipeline`：达标分数、最大轮数、维度短板阈值、worker 错峰间隔。
- `templates`：NSFC 三类项目质量标准、撰写模板、方法学手册要求。
- `agents`：各 profile 默认 Provider、超时、模型、路由策略。
- `tasks`：默认任务参数、hermes 自动派活开关。
- `learning`：自主学习引擎参数、来源、配额。
- `autonomy`：CoPilot 自主决策级别与提醒频率。
- `kb_output`：可靠来源规则、derived 内容过期时间、归档萃取字段。

**交互入口**：
- Web API：`/api/console/flow`、`/api/console/agents`、`/api/console/alerts`、`/api/console/action`、`/api/settings/categories`、`/api/settings/:category`、`/api/settings/:category/preview`
- 前端：`index.html` 导航栏新增「控制台」「课题生命周期」入口；`settings.js` 抽屉保留轻量设置，`settings_center.js` 提供完整配置页面。
- 聊天斜杠命令：`/status`、`/config`、`/template`、`/pipeline` 可快速查看状态或唤起配置。

**设计原则**：
- **可观测 + 可操作合一**：控制台不仅能看，还能直接触发 repair/orchestrate/optimize/clear-alert。
- **配置变更可控**：设置中心保存前强制 preview，写操作前自动备份旧文件到 `memory/.settings-backup/`。
- **Agent 辅助配置**：用户可在前端手动调整，也可在聊天中通过 `/config` 等命令让林赛辅助完成配置修改。
