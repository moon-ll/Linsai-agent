> 本文件由 AGENTS.md 的目录结构一节拆分而来，供快速查阅。
> 最后更新：2026-11-17（v8.0.0 工作台架构：research_topics 新域 + v7 遗留归档）
> 维护原则：只保留**顶层结构 + 数据域 + 关键目录**，避免逐文件枚举（脚本细节见 `scripts/README.md`，会随文件变动同步更新）。

## 目录结构

```
LinSai-CoPilot/
│
├── AGENTS.md                  # AI 代理必读指南（v8 规则唯一真相源）
├── README.md                  # 人类可读的项目说明（工作台定位）
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源（当前 8.0.0）
├── .env                       # 本地 API 密钥（gitignore，不提交）
├── .gitignore                 # Git 忽略规则：用户数据、自动生成文件、敏感配置
│
├── persona/                   # 林赛人格资产（注入材料，引用 virtu-LinSai 不修改）
│   ├── lin-sai-persona.md     # 整合版人格注入文件（主 prompt 素材）
│   └── source-manifest.json   # 来源追踪
│
├── sessions/                  # 对话会话存档（YYYYMMDD-主题/，gitignore）
├── memory/                    # 长期记忆与系统状态（gitignore，含 llm-config.json）
│   ├── config/workbench.json  # v8 工作台配置（深研配额/开关/周末注册模式）
│   ├── nsfc-standards.json    # NSFC 质量标准（legacy 场景引用）
│   ├── v8-cron-teardown.json  # v7 优化环 cron 停用审计
│   ├── workbench-monitor.json # 轻量监控产出
│   └── ...                    # 完整清单见 memory/README.md
│
├── tasks/                     # 工作项与项目管理（active/backlog/completed，gitignore）
├── references/                # 用户提供的参考资料（默认只读）
│
├── research_topics/           # ★ v8 课题库（活跃数据域，核心产出）
│   ├── _topics.json           # 轻量状态索引（状态由目录位置 + 课题卡头域承载）
│   ├── questions/             # 问题候选收件箱（文献链发现 / 人工注册）
│   ├── kickoff/               # 深研中：01_background/ 02_problem/ 03_scheme/ 04_references/
│   │                          #   + topic-card.md + topic-report.md + kickoff-check.json
│   ├── ready/                 # 启动包就绪（待人工启动，验收 A1-A4+G1-G2 全过）
│   ├── active/                # 正式研究中（人工启动后）
│   ├── archive/               # 收尾归档
│   ├── _rejected-questions/   # 否决台账（防重复立项）
│   └── _audit/                # v7 迁移报告 / cron 停用审计
│
├── research_proposals/        # v7 legacy 只读域（21 课题已迁出；README-v7-LEGACY.md 标注）
│
├── knowledge/                 # 林赛的知识库（Obsidian Vault）
│   ├── raw/                   # 用户原始材料（只读：papers/notes/pdfs/webclips）
│   ├── wiki/                  # 结构化知识（concepts/methods/people/papers/projects/reviews）
│   ├── captures/              # 对话自动捕获片段
│   ├── index.json             # 统一倒排索引（v2 格式）
│   ├── graph.json             # 知识图谱
│   └── growth-log.json        # 知识生长日志
│
├── .hermes/                   # hermes 项目本地 trusted 目录（agent 会话自动发现）
│   └── skills/                # 管线技能库（单一真相源，skill_loader.py 按节注入）
│       ├── literature-reading/SKILL.md  # 深研 B1 使用
│       ├── research-proposal/SKILL.md   # 深研 B2/B3 使用
│       ├── method-manual/SKILL.md       # 深研 B3 使用（参数溯源）
│       ├── nsfc-writing/SKILL.md        # legacy（人工项目书场景）
│       └── quality-review/SKILL.md      # legacy
│
├── skills/                    # 会话技能库（见 skills/README.md）
│
├── scripts/                   # 工具脚本（Python 3，零依赖）
│   ├── topic_pipeline/        # ★ v8 课题启动包管线（14 模块，见 docs/ARCHITECTURE.md §3）
│   ├── topic_pipeline.py      # CLI shim（import 解析到同名包）
│   ├── workbench_monitor.py   # 轻量健康检查（cron 对账/topics/KB；v8.0.46 起告警恒 exit 0）
│   ├── harness_metrics.py     # ★ v8.0.41 运转指标采集（六路+monitor_state，半点轮数据入口，快照+有界趋势历史）
│   ├── snapshot_bridge.py     # ★ v8.0.44 snapshot 桥接恢复点保鲜（main 历史阻断期间，orphan 快照推送）
│   ├── copilot_engine.py      # 1v1 会话引擎（工作台协作助手）
│   ├── web_server.py          # Web 聚合器（Mixin 路由，含 /api/topics/*）
│   ├── deep_read_pipeline.py · literature_service.py · literature_screener.py
│   ├── external_fetcher.py    # 多源学术检索
│   ├── kb_*.py                # 知识库引擎（蒸馏/图谱/方法卡/治理）
│   ├── weekend_pipeline/      # 周末输入端（文献发现链，new 路由桥接 topics 域）
│   ├── hermes_bridge.py       # hermes CLI 桥接（cron/oneshot）
│   ├── skill_loader.py        # skill 注入器
│   ├── step_usage.py          # 全链调用计量账本
│   ├── common.py · paths.py · llm_router.py · llm_gateway.py
│   ├── archive/v7-optimization/   # ★ v7 优化环退役代码（28 个，归档不删除）
│   ├── proposal_lifecycle/ + lifecycle/ + adversarial/   # v7 legacy（保留可导入，不再调度）
│   ├── weekend_orchestrator.py · sync_engine.py          # legacy 输出端/同步（保留）
│   └── tests/                 # 自动化测试（archive/ 子目录为退役测试）
│
├── docs/                      # 项目文档
│   ├── WORKBENCH-ARCHITECTURE.md  # ★ v8 设计纲领（工作流程/验收标准/迁移/清理）
│   ├── ARCHITECTURE.md        # v8 架构说明（权威）
│   ├── PROJECT-STRUCTURE.md   # 本文件
│   ├── SKILL-ARCHITECTURE.md  # skill 层说明
│   └── archive/               # 历史文档归档
│
├── web/                       # 前端界面（零框架依赖）
│   ├── index.html             # 单页应用入口（含课题工作台导航）
│   └── js/                    # workbench.js（课题看板）/ 会话/任务/知识库等面板
│
├── logs/ backups/ notes/ outputs/ tmp/   # 运行日志 / 备份 / 笔记 / 产出 / 临时
└── outputs/                   # 深研 worker 日志等运行产出
```
