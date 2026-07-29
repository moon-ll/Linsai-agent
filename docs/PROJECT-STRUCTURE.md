> 本文件由 AGENTS.md 的目录结构一节拆分而来，供快速查阅。

## 目录结构

```
LinSai-CoPilot/
│
├── AGENTS.md                  # 本文件。AI 代理必读指南
├── README.md                  # 人类可读的项目说明
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源（当前 6.7.7）
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
│   ├── proposal_lifecycle.py  # v6.7.7 薄 shim：提案生命周期 CLI/导入入口，实现位于 proposal_lifecycle/ 包
│   ├── proposal_lifecycle/    # v6.7.7 提案生命周期包：state/naming/registration/optimize/cron 等 mixin
│   ├── adversarial_governance.py # v6.7.7 薄 shim：对抗评审奖惩导入入口，实现位于 adversarial/ 包
│   ├── adversarial/           # v6.7.7 对抗评审奖惩包
│   ├── lifecycle_cron_framework.py # v6.7.7 薄 shim：生命周期 cron 导入入口，实现位于 lifecycle/ 包
│   ├── lifecycle/             # v6.7.7 生命周期 cron 包：controller/scheduler/orchestrator/executor/utils
│   ├── rebuild_lifecycle.py   # v6.7.1+ 基于 critic 报告重建 _lifecycle.json / 规范化轮次编号
│   ├── import_hermes_topics.py # v6.7.3 将 hermes workspace 课题雏形导入全自动链路
│   ├── idea_generator.py      # v6.7.7 输入端薄 shim：--auto 委托给 weekend_pipeline input 阶段；--manual 保留
│   ├── knowledge_output.py    # v6.7.7 输出端薄 shim：--weekly 委托给 weekend_pipeline output 阶段；其他模式保留
│   ├── weekend_orchestrator.py # v6.7.7 周末总控薄 shim：调用 weekend_pipeline 各阶段
│   ├── weekend_pipeline.py    # v6.7.7 周末任务流水线入口脚本（供 hermes cron 调用）
│   ├── weekend_pipeline/      # v6.7.7 周末任务流水线包：input/output/reflection 小任务与 KB 联动
│   ├── kb_health_weekend.py   # v6.7.7 周末 KB 深度健康检查（基础检查复用 knowledge_output）
│   ├── orchestrator.py        # v6.7 林赛总控核心：仪表盘 / 失败分析 / 策略建议 / 链路监控
│   ├── profile_health.py      # v6.7 profile 健康度：idle/working/blocked/offline + 成功率/耗时
│   ├── failure_analyzer.py    # v6.7 失败模式分析：8 种模式聚类 + prompt 修正建议
│   ├── strategy_optimizer.py  # v6.7 调度策略自调优：建议模式，人工确认后应用
│   ├── web_routes_orchestrator.py # v6.7 林赛总控路由 Mixin（8 条路由）
│   ├── web_routes_system.py   # v6.7.7 生命周期输入/输出端路由（incoming/weekend）
│   ├── web_routes_settings.py # v6.7.7 设置中心路由 Mixin（链路/模板/Agent/任务/学习/自主/KB输出）
│   ├── methodology_manual.py  # v6.2.1 方法学手册
│   ├── agent_team.py          # v6.2.1 Agent 团队管理
│   ├── check_boundary.py      # v6.2.1 边界违规检测
│   │
│   ├── deepxiv_knowledge/     # deepxiv 论文获取流水线
│   ├── wiki_regenerator/      # wiki 报告重建
│   └── tests/                 # 自动化测试套件
│       ├── test_runner.py            # 零依赖轻量测试框架
│       ├── test_core.py              # 核心模块单元测试
│       ├── test_scenarios.py         # 场景剧本测试
│       ├── test_persona.py           # 人格一致性抽检
│       ├── test_web_api.py           # Web API 接口测试
│       ├── test_lifecycle_cron.py    # 生命周期 cron 框架测试
│       └── test_weekend_pipeline.py  # 周末任务流水线测试
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
        ├── console.js          # v6.7.7 林赛控制台：全链路流水线 / Agent 状态 / 告警 / 快捷操作
        ├── settings_center.js  # v6.7.7 设置中心：链路/模板/Agent/任务/学习/自主/KB输出可视化配置
        └── paper_discussion.js # v4.1 文献独立讨论弹窗
```
