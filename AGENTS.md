# LinSai-CoPilot — 林赛协作引擎

> 本文件供 AI 编码代理阅读。假设读者对本项目一无所知。
> 项目语言：中文（所有文档、注释、脚本输出均为中文）
> 最后更新：2026-07-27

---

## 项目概述

**LinSai-CoPilot**（林赛协作引擎）是一个**虚拟合作者系统**——让林赛（Lin Sai）作为用户的专属 AI 协作者，1 对 1 深度协作，共同推进实际工作。

**核心比喻**：钢铁侠的贾维斯（J.A.R.V.I.S.）。不是群聊里的旁观者，而是随时待命、深度参与、主动感知的个人合作者。

**当前架构定位（v6.6+）**：
- CoPilot 是**操作台/监控层**：提供 Web 界面、会话管理、知识库、任务追踪、提案生命周期可视化和人工决策入口。
- hermes 是**执行端**：通过 7 个专业 profile 运行 agent loop，负责文献调研、缺口分析、申请书撰写、对抗优化等重脑力工作。
- 两者通过 `state_sync.py`（论文统一状态）、`memory_bridge.py`（记忆同步）、`hermes_pipeline.py`（管线派活）协同。

### 与相关项目的关系

| 项目 | 角色 | 关系 |
|------|------|------|
| **virtu-LinSai** | 人格资产生产端 | 上游。通过 190 万字自传叙事生长出林赛的完整人格（SOUL.md / SKILL.md / 林赛-perspective）。本项目**引用但不修改**其资产。 |
| **persona-discussion (Agora)** | 历史人物群聊应用 | 参考架构。Agora 是"多人会议室"，本项目是"专属办公室"。可复用其池管理/状态机思想，但交互模型完全不同。 |
| **hermes** | 本地 agent 执行引擎 | 下游/搭档。CoPilot 通过 hermes CLI 调用其 profile 完成多轮 agent loop 任务。 |
| **LinSai-CoPilot** | 虚拟合作者应用 | 本项目。消费 virtu-LinSai 人格资产，以 1v1 CoPilot 模式服务用户，并作为 hermes 的指挥台。 |

### 核心差异（为什么不是 Agora 的变体）

| 维度 | Agora | LinSai-CoPilot |
|------|-------|----------------|
| **交互模式** | 群聊 / @单独追问 | 1v1 持续对话，无旁观者 |
| **角色定位** | 历史人物旁观评论 | 当代同行并肩工作 |
| **关系深度** | 浅层、事件驱动 | 深层、长期记忆、持续学习用户偏好 |
| **主动性** | 被动响应用户提问 | 主动感知、主动提醒、主动推进 |
| **目标** | 获取多角度建议 | **一起完成具体工作** |
| **时间感** | 历史人物活在各自时代 | 林赛活在"当下"（2026 年），与用户同步时间 |
| **执行架构** | 单次 LLM 调用 | CoPilot 监控 + hermes agent loop 执行 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 运行环境 | Python 3（仅标准库） | 同 virtu-LinSai，零第三方依赖。无 `requirements.txt`、`pyproject.toml`、`package.json`、`Cargo.toml` 等构建文件。 |
| 内容格式 | Markdown（.md） | 对话记录、任务描述、记忆片段、知识库笔记。 |
| 元数据 | JSON | 会话状态、记忆索引、任务追踪、管线状态。 |
| LLM 接口 | GLM-5.2 / MiniMax-M3 / Kimi CLI / Claude CLI | 本地 CLI / API 路由，通过 `llm_router.py` / `llm_gateway.py` 自动降级。 |
| Web 服务器 | Python `http.server.ThreadingHTTPServer` | 零第三方依赖，REST API + SSE 流式输出。 |
| 前端 | 原生 HTML/CSS/JS | 零框架依赖，CSS 变量 + `data-theme` 切换深色/浅色/自动主题。 |
| 路径处理 | `pathlib.Path` | 禁止硬编码绝对路径（用户 home 下的 hermes 工作区除外，统一在 `paths.py` 中声明）。 |
| 进程锁 | `fcntl.flock`（POSIX） | macOS/Linux 跨进程锁；Windows 环境降级为无锁 + 原子写入。 |

**关键约束**：
- 所有 Python 脚本仅使用标准库，不引入第三方包。
- 敏感凭据（API Key）只存放在本地 `.env` 和 `memory/llm-config.json`，两者均已加入 `.gitignore`。

---

## 目录结构

```
LinSai-CoPilot/
│
├── AGENTS.md                  # 本文件。AI 代理必读指南
├── README.md                  # 人类可读的项目说明
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源（当前 6.7.0）
├── .env                       # 本地 API 密钥（gitignore，不提交）
├── .gitignore                 # Git 忽略规则：用户数据、自动生成文件、敏感配置
│
├── persona/                   # 林赛人格资产（注入材料）
│   ├── README.md              # 资产来源说明与更新规范
│   ├── lin-sai-persona.md     # 整合版人格注入文件（主 prompt 素材）
│   └── source-manifest.json   # 来源追踪：记录复制自 virtu-LinSai 的版本
│
├── sessions/                  # 对话会话存档
│   ├── README.md
│   └── YYYYMMDD-会话主题/     # 每次会话一个目录
│       ├── messages.json      # 消息日志
│       ├── state.json         # 会话状态
│       └── summary.md         # 会话摘要
│
├── memory/                    # 长期记忆与上下文
│   ├── README.md
│   ├── user-profile.json      # 用户画像（偏好、习惯、已知技能）
│   ├── working-context.json   # 当前工作上下文（进行中的项目、关键决策）
│   ├── long-term-memory.json  # 跨会话记忆索引
│   ├── autonomy-level.json    # 自主级别配置
│   ├── learning-config.json   # 学习引擎配置
│   ├── learning-cost.json     # 学习成本追踪
│   ├── llm-config.json        # LLM 路由配置（gitignore）
│   ├── nsfc-decisions.json    # NSFC 决策记录
│   ├── nsfc-standards.json    # NSFC 三类项目（面上/重点/重大）质量标准与模板
│   ├── feedback-standards.json# 反馈质量标准
│   ├── paper-feedback.json    # 论文反馈
│   ├── paper-pool.json        # 论文池
│   ├── pdf-library.json       # PDF 原文库索引
│   ├── project-dispatch.json  # 项目调度
│   ├── reflow-state.json      # 认知回流状态
│   ├── research-profile.json  # 研究方向画像
│   ├── sync-state.json        # 同步状态
│   ├── hermes-memory-snapshot.json # hermes 记忆原文快照
│   ├── alias-candidates.json  # 别名候选
│   ├── chat-archive-index.json # 聊天归档索引
│   └── snippets/              # 记忆片段（用户的名言、关键事件）
│       └── README.md
│
├── tasks/                     # 工作项与项目管理
│   ├── README.md
│   ├── active/                # 进行中任务
│   ├── backlog/               # 待办任务
│   └── completed/             # 已完成任务
│
├── references/                # 用户提供的参考资料（默认只读）
│   ├── README.md
│   ├── papers/                # 论文/文献
│   ├── notes/                 # 用户笔记
│   └── index.json             # 文献索引
│
├── knowledge/                 # 林赛的知识库（Obsidian Vault）
│   ├── README.md              # 知识库使用指南
│   ├── raw/                   # 用户原始材料（只读）
│   │   ├── papers/            # 论文 PDF/笔记
│   │   ├── notes/             # 用户手写笔记
│   │   ├── pdfs/              # PDF 原文库（v6.3）
│   │   └── webclips/          # 网页剪藏
│   ├── wiki/                  # LLM 管理的结构化知识
│   │   ├── concepts/          # 核心概念
│   │   ├── methods/           # 实验方法
│   │   ├── people/            # 学者评价
│   │   ├── papers/            # 论文精读
│   │   └── projects/          # 项目聚合
│   ├── captures/              # 对话自动捕获片段
│   ├── .obsidian/             # Obsidian 配置
│   ├── templates/             # Obsidian 笔记模板
│   ├── aliases.json           # 别名映射
│   ├── index.json             # 统一倒排索引
│   ├── graph.json             # 知识图谱
│   ├── growth-log.json        # 知识生长日志
│   ├── categories.json        # 分类管理数据
│   └── .cache/                # 搜索缓存
│
├── skills/                    # 技能目录（每个技能一个子目录）
│   ├── README.md
│   ├── self-test/             # 内测系统 skill 说明
│   └── {skill-name}/
│       └── SKILL.md           # 技能定义：触发词、心智模型、表达 DNA
│
├── projects/                  # v3.5 课题指导模块数据（当前为空，功能由 research_proposals 承接）
│   └── README.md
│
├── proposals/                 # 早期 proposal 草稿（历史目录，逐渐被 research_proposals 替代）
│
├── research_proposals/        # v6.2+ 研究管线数据域（独立，与 CoPilot 核心隔离）
│   ├── _lifecycle.json        # 提案生命周期总状态
│   ├── .config/               # 管线配置（品味模型等）
│   ├── drafts/                # 初稿区
│   ├── optimizing/            # 优化中区
│   ├── pending_review/        # 待校验区
│   ├── archived/              # 归档区
│   └── {proposal_id}/         # 单个提案目录
│       ├── 00_pipeline/       # 管线状态、产物注册表
│       ├── 01_literature/     # 文献调研产物（或 01_direction）
│       ├── 02_topic/          # 缺口分析、课题列表
│       ├── 03_question/       # 科学问题框架
│       ├── 04_proposal/       # 申请书章节、参考文献
│       └── 05_review/         # 自检报告、迭代历史
│
├── docs/                      # 项目文档与报告
│   ├── README.md
│   ├── CLAUDE-CLI-ADMIN.md    # Claude CLI 人工管理指南
│   ├── deepxiv-knowledge-workflow.md
│   ├── unified-state-sync-design.md
│   ├── v5-three-tier-unification-plan.md
│   ├── linsai-orchestrator-design.md # v6.7 林赛总控设计文档
│   ├── prompts/               # LLM prompt 模板
│   └── archive/               # 历史文档归档
│
├── linsai-copilot-manual/     # 项目使用手册（HTML）
├── pipeline-deep-design/      # 管线深度设计稿（HTML）
├── research-pipeline-architecture/ # 研究管线架构图（HTML）
│
├── scripts/                   # 工具脚本（Python 3，零依赖）
│   ├── __init__.py            # 包初始化
│   ├── common.py              # 公共工具：now_utc/load_json/save_json/safe_filename/file_lock
│   ├── paths.py               # 路径常量：PROJECT_ROOT 及所有数据目录
│   ├── logger.py              # 统一日志：控制台彩色输出 + 文件按日期轮转
│   │
│   ├── copilot_engine.py      # 核心引擎：prompt 构建、调用 LLM、响应解析、CLI 入口
│   ├── context_builder.py     # 上下文组装：人格 + 记忆 + 知识库 + 会话历史
│   ├── session_manager.py     # 会话创建、存档、加载
│   ├── memory_manager.py      # 记忆读写、索引、压缩
│   ├── task_manager.py        # 任务 CRUD、状态流转
│   ├── proactive_engine.py    # 主动感知、心跳扫描
│   ├── document_handler.py    # 文档读取、PDF 提取、代码分析
│   ├── skill_manager.py       # 技能系统：扫描、匹配、注入、配置
│   ├── slash_commands.py      # 斜杠命令系统
│   ├── tool_engine.py         # 工具注册：file_read/write, calc, task_create, knowledge_query, run_command, hermes_chat
│   ├── chat_archive.py        # 聊天记录归档浏览器
│   │
│   ├── knowledge_base.py      # 知识库引擎门面：re-export 子模块全部函数
│   ├── kb_text.py             # 文本工具：tokenize/chunk/IDF/frontmatter
│   ├── kb_graph.py            # 知识图谱：节点 CRUD、关联概念、wikilink 注入
│   ├── kb_index.py            # 索引：build_index/search/search_light/raw 管理
│   ├── kb_wiki.py             # wiki 页面：CRUD/stub 创建/生长阶段
│   ├── kb_health.py           # 知识库健康度
│   ├── kb_capture.py          # 对话自动捕获
│   ├── kb_maintenance.py      # 批处理维护
│   ├── kb_auto_sync.py        # 知识库自动同步
│   ├── kb_categories.py       # 分类管理
│   ├── kb_importer.py         # 批量导入
│   ├── kb_linker.py           # 关联链接
│   │
│   ├── alias_learner.py       # 别名学习器
│   ├── growth_engine.py       # 知识生长引擎
│   ├── paper_pool.py          # 论文池管理
│   ├── pdf_manager.py         # v6.3 PDF 原文库管理器
│   ├── research_profiler.py   # 研究方向感知器：TF-IDF 关键词、7 天自动重建
│   ├── external_fetcher.py    # 统一信息获取：deepxiv + 联网检索 + raw 扫描
│   ├── learning_engine.py     # 自主学习核心：蒸馏/精读/概念整合/成本追踪
│   ├── quality_evaluator.py   # 质量评估引擎
│   ├── usage_tracker.py       # Token 用量追踪
│   │
│   ├── agora_bridge.py        # Agora 群聊桥接
│   ├── hermes_bridge.py       # Hermes 桥接器：cron 控制 / oneshot 派活 / 团队 profile 状态
│   ├── hermes_pipeline.py     # v6.4 Hermes 驱动研究管线：导入 / 派活 / 执行 / cron
│   ├── sync_engine.py         # 多端同步
│   ├── briefing_sync.py       # v4.1 文献简报双向同步
│   ├── state_sync.py          # v5+ 论文统一状态总线（CoPilot ↔ hermes）
│   ├── memory_bridge.py       # hermes → CoPilot 记忆单向同步
│   │
│   ├── project_dispatch.py    # 项目总控：意见 + 执行追踪持久化
│   ├── project_manager.py     # v3.5 课题管理
│   ├── unit_manager.py        # v3.5 单元管理
│   ├── project_kb.py          # v3.5 课题知识库
│   ├── project_memory.py      # v3.5 课题记忆
│   ├── project_context.py     # v3.5 课题上下文
│   ├── project_workflow.py    # v3.5 课题工作流
│   ├── project_reader.py      # 项目文件读取器
│   ├── kanban_reader.py       # 看板数据读取
│   │
│   ├── llm_router.py          # 多模型路由：MiniMax API + Kimi CLI + Claude CLI，自动降级
│   ├── llm_gateway.py         # v6.3.2 共享 LLM 网关（核心与管线均可调用）
│   ├── backup_manager.py      # 数据备份/恢复
│   ├── upgrade.py             # 安全升级标准流程
│   ├── self_test.py           # 内测统一入口
│   ├── test_e2e_learning_full.py # 三来源端到端完整链路验证
│   │
│   ├── artifact_manager.py    # v6.2 产物版本管理
│   ├── lineage_tracker.py     # v6.2 血缘追踪
│   ├── taste_engine.py        # v6.2 学术品味引擎
│   ├── pipeline_orchestrator.py # v6.2 管线编排：六阶段状态机/六道门禁
│   ├── gap_analyzer.py        # v6.2 研究缺口分析
│   ├── citation_manager.py    # v6.2 引文管理
│   ├── topic_generator.py     # v6.2 课题生成
│   ├── question_architect.py  # v6.2 科学问题架构
│   ├── proposal_inspector.py  # v6.2 申请书自检
│   ├── proposal_writer.py     # v6.2 申请书撰写
│   ├── proposal_lifecycle.py  # v6.5+ 提案生命周期：四阶段 + writer-critic 对抗优化
│   ├── orchestrator.py        # v6.7 林赛总控核心：仪表盘 / 失败分析 / 策略建议 / 链路监控
│   ├── profile_health.py      # v6.7 profile 健康度：idle/working/blocked/offline + 成功率/耗时
│   ├── failure_analyzer.py    # v6.7 失败模式分析：8 种模式聚类 + prompt 修正建议
│   ├── strategy_optimizer.py  # v6.7 调度策略自调优：建议模式，人工确认后应用
│   ├── web_routes_orchestrator.py # v6.7 林赛总控路由 Mixin（8 条路由）
│   ├── methodology_manual.py  # v6.2.1 方法学手册
│   ├── agent_team.py          # v6.2.1 Agent 团队管理
│   ├── check_boundary.py      # v6.2.1 边界违规检测
│   │
│   ├── deepxiv_knowledge/     # deepxiv 论文获取流水线
│   ├── wiki_regenerator/      # wiki 报告重建
│   └── tests/                 # 自动化测试套件
│       ├── test_runner.py     # 零依赖轻量测试框架
│       ├── test_core.py       # 核心模块单元测试
│       ├── test_scenarios.py  # 场景剧本测试
│       ├── test_persona.py    # 人格一致性抽检
│       └── test_web_api.py    # Web API 接口测试
│
└── web/                       # 前端界面（零框架依赖）
    ├── index.html             # 单页应用入口
    ├── css/
    │   └── style.css          # 双主题样式
    └── js/
        ├── app.js              # 主入口
        ├── core.js             # 核心工具（API 请求/渲染/主题/toast）
        ├── chat.js             # 聊天逻辑
        ├── session.js          # 会话管理
        ├── task.js             # 任务面板
        ├── kb.js               # 知识库浏览器
        ├── skill.js            # 技能面板
        ├── settings.js         # 设置面板
        ├── projects.js         # 项目面板
        ├── hermes_console.js   # Hermes 控制台
        ├── learning.js         # 学习管理器
        ├── research.js         # 课题指导面板
        ├── pipeline.js         # 研究管线面板
        ├── dashboard.js        # v6.0 仪表盘首页
        ├── lifecycle.js        # v6.6 提案生命周期面板
        ├── orchestrator.js     # v6.7 林赛总控台（仪表盘 / Profile 健康 / 失败模式 / 策略 / 链路质量）
        └── paper_discussion.js # v4.1 文献独立讨论弹窗
```

---

## 运行与构建

**无构建步骤**。Python 脚本直接运行，无编译、无打包、无依赖安装。

### 启动 Web 界面（推荐）

```bash
# 方式一：直接启动（默认端口 8080）
python3 scripts/web_server.py

# 方式二：指定端口
python3 scripts/web_server.py --port 9000

# 方式三：一键启动（自动打开浏览器）
./scripts/launch.sh
./scripts/launch.sh 9000  # 指定端口
```

打开 `http://localhost:8080`。

### 启动 CLI 对话

```bash
# 新建会话
python3 scripts/copilot_engine.py --start "固体HHG实验方案设计"

# 继续上一个会话
python3 scripts/copilot_engine.py --continue

# 列出会话
python3 scripts/copilot_engine.py --list
```

### 常用维护命令

```bash
# 手动备份（自动备份每 24 小时触发一次）
python3 scripts/backup_manager.py
python3 scripts/backup_manager.py --list
python3 scripts/backup_manager.py --restore backups/2026-07-27T10-00-00Z.zip

# 安全升级（备份 → 拉取 → 验证 → 检查迁移）
python3 scripts/upgrade.py --check
python3 scripts/upgrade.py --simulate
python3 scripts/upgrade.py

# 知识库周维护
python3 scripts/kb_maintenance.py --weekly

# 认知回流
python3 scripts/memory_reflow.py --reflow

# 同步 hermes 产出
python3 scripts/sync_engine.py
```

### 语法检查

```bash
python3 -m py_compile scripts/*.py
```

---

## 测试策略

采用**三层测试体系**：

### 1. 单元/核心回归测试

```bash
# 全量（不含 Web API）
python3 scripts/self_test.py

# 分维度
python3 scripts/self_test.py --module     # 核心模块（当前 116 个检查点）
python3 scripts/self_test.py --scenario   # 场景剧本（当前 16 个检查点）
python3 scripts/self_test.py --persona    # 人格一致性（当前 38 个检查点）
python3 scripts/self_test.py --web        # Web API 专项（需启动子进程）
python3 scripts/self_test.py --web-ci     # CI 模式：全量 + Web API

# JSON 输出
python3 scripts/self_test.py --module --json

# 程序化调用
python3 -c "from self_test import run_tests; print(run_tests(['module'])['summary'])"
```

**当前基线**：
- `--module`：116/116 通过（含核心模块、课题链路、LLM 路由、工具引擎、安全、kb 子模块等）
- `--scenario`：16/16 通过
- `--persona`：38/38 通过
- `--web-ci`：Web API 虚拟用户测试（启动 web_server 子进程，覆盖所有主要 API 命名空间）

### 2. 模块自检

大量核心脚本和管线索脚本包含 `_self_check()`，可直接运行：

```bash
python3 scripts/{module}.py --self-check
```

例如：

```bash
python3 scripts/web_server.py --self-check
python3 scripts/pdf_manager.py --self-check
python3 scripts/hermes_pipeline.py --self-check
python3 scripts/proposal_lifecycle.py --self-check
python3 scripts/orchestrator.py --self-check
python3 scripts/profile_health.py --self-check
python3 scripts/failure_analyzer.py --self-check
python3 scripts/strategy_optimizer.py --self-check
python3 scripts/agent_team.py --self-check
python3 scripts/methodology_manual.py --self-check
```

### 3. E2E 集成测试

```bash
# 自主学习三来源端到端验证（需真实 Claude CLI 环境，非日常回归项）
python3 scripts/test_e2e_learning_full.py
```

### 测试设计原则

- **零污染**：所有测试在临时隔离目录运行，结束后自动清理，不触碰真实会话/任务/记忆。
- **零成本**：不调用 LLM API，纯本地代码逻辑验证。
- **自动发现**：在 `scripts/tests/` 下新增 `test_*.py` 并继承 `TestSuite` 即可自动纳入回归。

---

## 代码规范

### Python 脚本

- **仅使用标准库**，禁止新增 `requirements.txt` 或 `pyproject.toml`。
- 头部中文 docstring，说明用途和用法示例。
- 路径处理使用 `pathlib.Path`；`PROJECT_ROOT` 通过 `Path(__file__).parent.parent` 推导。
- JSON 文件必须 `ensure_ascii=False, indent=2`。
- 时间戳使用 UTC ISO 格式：`%Y-%m-%dT%H:%M:%SZ`。
- 输出使用中文，状态图标统一：
  - `✓` 成功
  - `✗` 失败
  - `⚠` 警告
  - `○` 待处理
  - `◐` 进行中
- 原子写入：`common.save_json` 使用 tempfile + fsync + `os.replace()`。
- 跨进程并发：使用 `common.file_lock("name")`（基于 `fcntl.flock`）。

### Web 前端

- **零框架依赖**：原生 HTML/CSS/JavaScript。
- **主题系统**：CSS 变量 + `data-theme` 属性切换（`light`/`dark`/`auto`）。
- **通信协议**：REST API + SSE（Server-Sent Events）流式输出，不引入 WebSocket。
- **移动端优先**：侧边栏可折叠、触摸目标 ≥ 40px、响应式断点 680px/900px。
- **无障碍**：语义化标签、键盘导航（Enter 发送、Shift+Enter 换行）。
- 前端工具类前缀统一，避免内联 style；新增 CSS 类优先于内联样式。

### 会话记录

- 每个会话独立目录：`sessions/YYYYMMDD-主题/`。
- `messages.json` 单条消息格式：
  ```json
  {
    "msg_id": "msg_001",
    "role": "user",
    "content": "...",
    "timestamp": "2026-07-27T09:00:00Z",
    "mode": "co-working"
  }
  ```
- `state.json` 记录会话元信息（主题、模式、开始时间、最后活跃）。

### 变更记录

- 所有修改在 `CHANGELOG.md` 中记录。
- 格式：
  ```markdown
  ## vX.Y.Z - YYYY-MM-DD 简短描述
  - 修改内容
  - 验证结果
  ```

---

## 架构说明

### 1. 模块分类与导入边界

| 分类 | 命名约定 | 可被谁导入 |
|------|----------|-----------|
| **CoPilot 核心** | 无前缀，如 `session_manager.py`、`copilot_engine.py` | 核心模块互相导入；研究管线模块**不可导入**。 |
| **研究管线** | 管线特有文件名，如 `pipeline_orchestrator.py`、`gap_analyzer.py` | 管线模块互相导入；核心模块**不可导入**（`web_server.py` 作为聚合器导入 `web_routes_pipeline.py` 除外）。 |
| **共享基础设施** | `common.py`、`paths.py`、`llm_gateway.py` | 双方均可导入。 |
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
| `/api/lifecycle/` | CoPilot 核心 (v6.5+) | 提案生命周期仪表盘、注册、流转、优化 |
| `/api/orchestrator/` | CoPilot 核心 (v6.7+) | 林赛总控：仪表盘、profile 健康、失败模式、调度策略、链路质量 |
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
| `linsai` | GLM-5.2 | 方向校准 / 总控 / 简报 |
| `pipeline-runner` | GLM-5.2 | 管线编排 / 每日触发 |
| `researcher` | MiniMax-M3 | 文献调研 / 定向检索 |
| `analyst` | GLM-5.2 | 缺口分析 / 科学问题 |
| `writer` | GLM-5.2 | 申请书撰写 / 修订 |
| `critic` | GLM-5.2 | 对抗式评审（红队） |
| `reviewer` | GLM-5.2 | 质量终审 |

关键协作文件：
- `state_sync.py`：论文统一状态总线（`item-status.json`），CoPilot 与 hermes 共享。
- `memory_bridge.py`：将 hermes `MEMORY.md` / `USER.md` 同步到 CoPilot `memory/`。
- `hermes_pipeline.py`：将六阶段派活给对应 profile，支持增量优化、产物检查、cron 自动化。
- `proposal_lifecycle.py`：四阶段（drafts → optimizing → pending_review → archived）+ writer-critic 对抗优化循环。

### 5. 提案生命周期

```
drafts（初稿）→ optimizing（优化中）→ pending_review（待校验）→ archived（归档）
```

- **命名规则**：`{项目类型}-{课题名称}-{YYYYMMDD}[-序号]`，项目类型 `general`/`key`/`major`。
- **对抗优化**：每天 pipeline-runner 触发 cron sweep，按章节（立项依据→研究内容→研究方案→整体审查）轮转，critic 4 维度评分（创新/可行/严谨/完整），writer 聚焦最弱维度修订；达标需全模块通过。
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

---

## 安全与隐私

- **无敏感凭据入仓**：API Key 只存于本地 `.env` 和 `memory/llm-config.json`，均已加入 `.gitignore`。
- **本地优先**：所有数据（会话、记忆、任务、论文池、提案）仅存于本地文件系统，不上传云端。
- **用户数据边界**：`references/` 目录默认只读；知识库 `raw/` 保留原貌。
- **路径遍历防护**：所有 Web 路由和文件操作使用安全校验（`_safe_join`、`_validate_proposal_id`、禁止 `..`）。
- **并发安全**：关键数据读写使用 `common.file_lock`（POSIX `fcntl.flock`）+ 原子写入。
- **XSS 防护**：前端使用 `escapeHtml` / `escapeAttr` 输出用户可控内容；事件处理避免内联 `onclick` 传递未转义参数。
- **命令执行白名单**：`tool_engine.run_command` 仅允许白名单命令前缀，禁止任意 shell。
- **记忆隔离**：不同用户（如有）的记忆完全隔离，不共享。

---

## 版本与升级

### 版本号规范

- **版本号来源**：`VERSION` 文件为唯一真相源（当前 `6.7.0`）。
- **格式**：`MAJOR.MINOR.PATCH`
  - `MAJOR`：不兼容的数据结构变更（需迁移脚本）
  - `MINOR`：新增功能（向后兼容）
  - `PATCH`：缺陷修复、文档更新、性能优化

### Git 管理策略

```bash
git init
git add .
git commit -m "v6.7.0 初始版本"
```

- 用户数据（`sessions/`、`memory/`、`tasks/`、`references/`）已被 `.gitignore` 排除，不会意外提交。
- 每次功能迭代一个 commit，消息格式：`vX.Y.Z - 简短描述`。
- 重要变更同步更新 `CHANGELOG.md`。

### 数据安全原则

| 原则 | 说明 |
|------|------|
| **用户数据无价** | 对话记录、记忆、任务一旦丢失不可重建 |
| **备份优先** | 任何更新操作前必须先备份 |
| **恢复可验证** | 备份包必须能完整恢复 |
| **升级可回滚** | 升级失败时能一键回到之前状态 |

### 标准升级流程

```bash
# 方式一：升级助手（推荐）
python3 scripts/upgrade.py --check
python3 scripts/upgrade.py --simulate
python3 scripts/upgrade.py

# 方式二：手动
python3 scripts/backup_manager.py
git pull
python3 -m py_compile scripts/*.py
# 如存在 scripts/migrate.py 且 VERSION 变化则执行
python3 scripts/migrate.py
```

### 新增脚本准入检查清单

任何新脚本合并前必须满足：
- [ ] 头部中文 docstring 含用法示例
- [ ] 包含 `_self_check()` 函数并通过
- [ ] 不引入第三方依赖
- [ ] 路径使用 `pathlib.Path`，`PROJECT_ROOT` 通过 `Path(__file__).parent.parent` 推导
- [ ] JSON 输出使用 `ensure_ascii=False, indent=2`
- [ ] 不破坏现有数据结构格式
- [ ] 研究管线模块遵守 §6 导入边界与数据隔离规则
- [ ] 已在 `CHANGELOG.md` 中记录

---

## 参考文件优先级

当信息冲突时，按以下优先级采纳（高优先覆盖低优先）：

1. `persona/lin-sai-persona.md` — 人格注入文件（项目内权威）
2. `AGENTS.md` — 本文件（项目架构与规范）
3. `virtu-LinSai/PROJECT-STATE.md` — 上游角色锚点
4. `virtu-LinSai/PERSONA/` — 上游人格提炼
5. `virtu-LinSai/CONTENT/` — 上游自传叙事（如需深度引用）

---

*版本：6.7.0*
*日期：2026-07-27*
*创建者：AI 编码代理*
*上游资产来源：virtu-LinSai v2.7*
