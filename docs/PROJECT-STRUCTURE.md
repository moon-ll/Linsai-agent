> 本文件由 AGENTS.md 的目录结构一节拆分而来，供快速查阅。
> 维护原则：只保留**顶层结构 + 数据域 + 关键目录**，避免逐文件枚举（脚本细节见 `scripts/README.md`，会随文件变动同步更新）。

## 目录结构

```
LinSai-CoPilot/
│
├── AGENTS.md                  # 本文件。AI 代理必读指南（规则唯一真相源）
├── README.md                  # 人类可读的项目说明
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源（当前 6.9.28）
├── .env                       # 本地 API 密钥（gitignore，不提交）
├── .gitignore                 # Git 忽略规则：用户数据、自动生成文件、敏感配置
│
├── persona/                   # 林赛人格资产（注入材料，引用 virtu-LinSai 不修改）
│   ├── lin-sai-persona.md     # 整合版人格注入文件（主 prompt 素材）
│   └── source-manifest.json   # 来源追踪
│
├── sessions/                  # 对话会话存档（YYYYMMDD-主题/，gitignore）
├── memory/                    # 长期记忆与系统状态（gitignore，含 llm-config.json）
│   ├── nsfc-standards.json    # NSFC 三类项目质量标准（唯一权威源）
│   ├── agent-scores.json      # writer/critic 对抗奖惩记录
│   ├── system-kanban.json     # 系统看板（微调度器+监控协同写）
│   ├── human-queue.json       # 待人工队列（验收/立项/负反馈聚合）
│   ├── prompt-suggestions.json # prompt 优化建议
│   └── ...                    # 完整清单见 memory/README.md
│
├── tasks/                     # 工作项与项目管理（active/backlog/completed，gitignore）
├── references/                # 用户提供的参考资料（默认只读）
├── projects/                  # v3.5 课题指导模块数据（当前未启用，功能由 research_proposals 承接）
│
├── knowledge/                 # 林赛的知识库（Obsidian Vault）
│   ├── raw/                   # 用户原始材料（只读：papers/notes/pdfs/webclips）
│   ├── wiki/                  # LLM 管理的结构化知识（concepts/methods/people/papers/projects/reviews）
│   ├── captures/              # 对话自动捕获片段
│   ├── qa/                    # 问答讨论（paper/project/proposal-discussions）
│   ├── research_proposals/    # 提案镜像（设计例外，允许直写）
│   ├── index.json             # 统一倒排索引（v2 格式）
│   ├── graph.json             # 知识图谱
│   └── growth-log.json        # 知识生长日志
│
├── skills/                    # 技能目录（每个技能一个子目录 + SKILL.md）
│
├── research_proposals/        # 研究管线数据域（独立，与 CoPilot 核心隔离）
│   ├── _lifecycle.json        # 提案生命周期总状态
│   ├── drafts/optimizing/pending_review/archived  ← 生命周期四阶段
│   └── {proposal_id}/         # 单个提案目录（00_pipeline ... 05_review 阶段产物）
│
├── docs/                      # 项目文档（瘦身：仅保留权威文档，历史归档至 archive/）
│   ├── README.md              # 本目录说明与文件清单
│   ├── ARCHITECTURE.md        # 完整架构说明（AGENTS.md 指向的权威架构文档）
│   ├── PROJECT-STRUCTURE.md   # 目录结构（本文件）
│   ├── DATA-FLOW-MAP.md       # 数据流动路径图谱
│   ├── archive/               # 历史文档归档（已实现/已废弃的旧版计划与报告）
│   └── prompts/               # LLM prompt 模板
│
├── scripts/                   # 工具脚本（Python 3，零依赖；逐脚本清单见 scripts/README.md）
│   ├── common.py / paths.py / logger.py   # 共享基础设施
│   ├── copilot_engine.py / session_manager.py / memory_manager.py / task_manager.py  # CoPilot 核心
│   ├── knowledge_base.py + kb_*.py        # 知识库引擎（门面 + 20 子模块）
│   ├── proposal_lifecycle/ + proposal_lifecycle.py   # 提案生命周期包（薄 shim 保留 CLI）
│   ├── adversarial/ + adversarial_governance.py      # 对抗评审奖惩包（薄 shim 保留导入）
│   ├── lifecycle/ + lifecycle_cron_framework.py      # 生命周期 cron 包（薄 shim 保留导入）
│   ├── weekend_pipeline/ + weekend_pipeline.py       # 周末任务流水线包（薄 shim 保留入口）
│   ├── orchestrator.py / profile_health.py / failure_analyzer.py / strategy_optimizer.py  # 林赛总控层
│   ├── prompt_optimizer.py / retrospective.py / lifecycle_monitor.py / human_queue.py / review_dossier.py  # 辅助链路
│   ├── web_server.py + web_routes_*.py    # Web 服务器（Mixin 聚合 12 路由模块）
│   ├── llm_router.py / llm_gateway.py     # LLM 路由与网关
│   └── tests/                 # 自动化测试套件（52 个 test_*.py，零污染隔离运行）
│
├── web/                       # 前端界面（零框架依赖）
│   ├── index.html             # 单页应用入口
│   ├── css/style.css          # 双主题样式
│   └── js/                    # app/core/chat/session/task/kb/skill/settings/projects/
│                              # pipeline/dashboard/lifecycle/orchestrator/console/settings_center 等面板
│
├── logs/                      # 运行日志（linsai.log + healthchecks/）
├── backups/                   # 自动备份
└── notes/                     # 工作笔记区
```

## 数据域隔离

| 数据域 | 目录 | 写入方 | 读取方 |
|--------|------|--------|--------|
| CoPilot 核心 | `sessions/` `memory/` `tasks/` | CoPilot 核心模块 | 全部（只读） |
| 共享只读 | `knowledge/raw/` | `learning_engine` / `sync_engine` | 全部 |
| AI 管理 | `knowledge/wiki/` | `kb_*` 门面（`kb_wiki.save_wiki_page`） | 全部 |
| 研究管线 | `research_proposals/` | 管线模块 | CoPilot（只读展示） |
| Hermes 产出 | `~/Desktop/hermes_workspace/` | hermes-agent | `sync_engine`（只读拉取） |

**导入边界**：研究管线模块禁止直接导入 CoPilot 核心模块（会话、记忆、LLM 路由），LLM 统一走 `llm_gateway`。详见 `docs/ARCHITECTURE.md` §1。

## 文档维护约定

- `docs/` 只保留**权威/活跃**文档；已实现或已废弃的旧版计划与报告移入 `docs/archive/`。
- 架构细节以 `docs/ARCHITECTURE.md` 为准，规则以 `AGENTS.md` 为准，评分标准以 `memory/nsfc-standards.json` 为准。
- 脚本逐文件清单由 `scripts/README.md` 维护，本文件不重复枚举。
