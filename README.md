# 林赛协作引擎（LinSai-CoPilot）

> **林赛不是你的搜索引擎，他是你的合作者。**

---

## 这是什么？

**林赛协作引擎**让林赛（Lin Sai）成为你的专属虚拟合作者——不是群聊里的旁观者，而是坐在你对面、一起推进实际工作的同行。

### 一句话定位

类似钢铁侠的贾维斯（J.A.R.V.I.S.）：
- 他记得你们上周讨论到一半的实验方案
- 他会追问你光路设计的物理假设
- 他会在你连续三天失眠时提醒你"不在疲惫时做重大决定"
- 他不会替你做决定，但会分享"我当时试了 Y，结果是 Z"

### 与 Agora 的区别

| | **Agora（历史人物群聊）** | **LinSai-CoPilot（林赛协作引擎）** |
|---|---|---|
| 场景 | 物理学家微信群，众人围观 | 你的专属办公室，一对一 |
| 关系 | 浅层、事件驱动 | 深层、长期记忆、持续学习 |
| 主动性 | 你提问，他回答 | 他也可能主动问你 |
| 目标 | 获取多角度建议 | **一起完成具体工作** |

---

## 林赛是谁？

- **31 岁**，强场超快光学独立 PI，刚拿到第一个 DFG 经费
- **工人家庭出身**（父亲钳工/母亲纺织工），从珠海走到国际学术舞台
- **核心信条**："What I cannot create, I do not understand"
- **人格五维**：认知驱动 / 坚持力 / 务实主义 / 碰撞意识 / 边界意识
- **他会什么**：实验设计、理论与实验迭代、学术写作、学生培养、挫折应对
- **他不会什么**：替你算数值、替代文献综述、给标准答案式建议

完整人格画像见 [`persona/lin-sai-persona.md`](persona/lin-sai-persona.md)。

---

## 快速开始

```bash
# 1. 进入项目目录
cd ~/Desktop/LinSai-CoPilot

# 方式一：Web 界面（推荐 — 浏览器交互，支持主题切换、流式输出、任务面板）
python scripts/web_server.py
# 打开 http://localhost:8080

# 方式二：一键启动（自动打开浏览器）
./scripts/launch.sh

# 方式三：终端 CLI（轻量、脚本化）
python scripts/copilot_engine.py --start "固体HHG实验方案设计"
python scripts/copilot_engine.py --continue
python scripts/copilot_engine.py --list

# 会话中的特殊命令（Web 界面和 CLI 均支持）
> /mode deep-talk      # 切换为深度对话模式
> /read notes/paper.md # 读取文档
> /agora 费曼, 狄拉克  # 导出到Agora群聊
> /summary             # 显示会话摘要
> /exit                # 退出并保存
```

### 备份与升级

```bash
# 手动备份（自动备份每24小时触发一次）
python scripts/backup_manager.py

# 查看备份列表
python scripts/backup_manager.py --list

# 恢复指定备份（会自动创建当前状态的应急备份）
python scripts/backup_manager.py --restore backups/2026-05-08T10-00-00Z.zip

# 检查当前版本
python scripts/upgrade.py --check

# 安全升级（备份 → 拉取 → 验证 → 检查迁移）
python scripts/upgrade.py
```

---

## 项目结构

```
LinSai-CoPilot/
├── AGENTS.md                  # AI 代理开发指南
├── README.md                  # 本文件
├── CHANGELOG.md               # 变更记录
├── VERSION                    # 版本号唯一真相源
│
├── persona/                   # 林赛人格资产
│   ├── lin-sai-persona.md     # 整合版人格注入文件
│   └── source-manifest.json   # 来源追踪
│
├── sessions/                  # 对话会话存档
│   └── YYYYMMDD-主题/         # 每次会话一个目录
│       ├── messages.json      # 消息日志
│       ├── state.json         # 会话状态
│       └── summary.md         # 会话摘要
│
├── memory/                    # 长期记忆与上下文
│   ├── user-profile.json      # 用户画像
│   ├── working-context.json   # 工作上下文
│   ├── long-term-memory.json  # 跨会话记忆索引
│   ├── autonomy-level.json    # 自主级别配置
│   └── snippets/              # 记忆片段
│
├── tasks/                     # 工作项与项目管理
│   ├── active/                # 进行中
│   ├── backlog/               # 待办
│   └── completed/             # 已完成
│
├── references/                # 用户提供的参考资料
│   ├── papers/                # 论文/文献
│   ├── notes/                 # 用户笔记
│   └── index.json             # 文献索引
│
├── knowledge/                 # 林赛的知识库（Obsidian Vault）
│   ├── raw/                   # 用户原始材料（只读）
│   ├── wiki/                  # 结构化知识（concepts/methods/people/papers/projects）
│   ├── .obsidian/             # Obsidian 配置
│   ├── templates/             # 笔记模板
│   ├── captures/              # 对话自动捕获片段
│   ├── aliases.json           # 别名映射
│   ├── index.json             # 倒排索引
│   ├── graph.json             # 知识图谱
│   └── growth-log.json        # 知识生长日志
│
├── skills/                    # 技能目录（8+ 个思维顾问技能）
│   └── {skill-name}/
│       └── SKILL.md
│
├── projects/                  # v3.5 课题指导模块数据
│   ├── {project_id}.json      # 课题元数据
│   └── {project_id}/          # 课题工作目录
│       ├── PROJECT-MEMORY.md  # 核心记忆（≤100行，自动压缩）
│       ├── units/             # 单元（验收标准/风险/任务引用）
│       ├── kb/                # 分层知识库（raw/parsed/summary）
│       └── memory/            # 课题记忆（对话存档/片段/决策/风险）
│
├── docs/                      # 项目文档与报告
│   ├── README.md              # 本目录说明与文件清单
│   ├── CLAUDE-CLI-ADMIN.md    # Claude CLI 人工管理指南
│   ├── cognitive-loop-plan.md # v3.4 认知闭环设计稿
│   ├── deepxiv-knowledge-workflow.md   # deepxiv 知识库流水线设计
│   ├── archive/               # 历史版本文档归档
│   └── prompts/               # LLM prompt 模板
│
├── scripts/                   # 工具脚本（Python 3，零依赖，48 个主脚本 + 子包）
│   ├── session_manager.py     # 会话管理
│   ├── context_builder.py     # 上下文构建（Prompt组装）
│   ├── copilot_engine.py      # 核心引擎（LLM调用 + CLI）
│   ├── memory_manager.py      # 记忆系统
│   ├── task_manager.py        # 任务管理
│   ├── proactive_engine.py    # 主动感知
│   ├── document_handler.py    # 文档与代码协作
│   ├── agora_bridge.py        # Agora群聊桥接
│   ├── llm_router.py          # 多模型路由与自动降级
│   ├── usage_tracker.py       # Token 用量追踪
│   ├── skill_manager.py       # 技能系统管理
│   ├── slash_commands.py      # 斜杠命令系统
│   ├── tool_engine.py         # 子代理工具引擎
│   ├── knowledge_base.py      # 知识库引擎
│   ├── kb_capture.py          # 对话自动捕获
│   ├── kb_maintenance.py      # 知识库批处理维护
│   ├── research_profiler.py   # 研究方向感知器
│   ├── external_fetcher.py    # 统一信息获取
│   ├── learning_engine.py     # 自主学习核心
│   ├── quality_evaluator.py   # 质量评估引擎
│   ├── logger.py              # 统一日志系统
│   ├── chat_archive.py        # 聊天记录归档浏览器
│   ├── memory_reflow.py       # 认知回流引擎（hermes→记忆提炼）
│   ├── sync_engine.py         # 多端同步（会话/文献→知识库+认知回流）
│   ├── project_dispatch.py    # 项目总控（意见+执行追踪持久化）
│   ├── project_manager.py     # v3.5 课题管理（CRUD/状态机/PROJECT-MEMORY）
│   ├── unit_manager.py        # v3.5 单元管理（验收标准/风险/状态机）
│   ├── project_kb.py          # v3.5 课题知识库（分层/TF-IDF/标签）
│   ├── project_memory.py      # v3.5 课题记忆（对话/片段/决策/核心记忆）
│   ├── project_context.py     # v3.5 课题上下文（@语法/跨课题检索）
│   ├── project_workflow.py    # v3.5 课题工作流（规划→执行→验收→总结）
│   ├── web_server.py          # Web 服务器聚合器（Mixin 架构，321 行 + 10 路由 Mixin）
│   ├── backup_manager.py      # 数据备份/恢复
│   ├── upgrade.py             # 安全升级流程
│   ├── self_test.py           # 内测统一入口
│   ├── deepxiv_knowledge/     # deepxiv 论文获取流水线（8 模块）
│   ├── wiki_regenerator/      # wiki 报告重建（4 模块）
│   └── tests/                 # 自动化测试套件
│       ├── test_runner.py
│       ├── test_core.py
│       ├── test_scenarios.py
│       └── test_persona.py
│
└── web/                       # 前端界面（零框架依赖）
    ├── index.html             # 单页应用入口
    ├── css/
    │   └── style.css          # 双主题样式（深色/浅色/自动）
    └── js/
        ├── app.js             # 主入口（会话/聊天/流式SSE）
        ├── core.js            # 核心工具（请求/渲染/主题）
        ├── chat.js            # 聊天交互
        ├── session.js         # 会话管理
        ├── task.js            # 任务面板
        ├── kb.js              # 知识库浏览器
        ├── skill.js           # 技能面板
        ├── settings.js        # 设置面板
        ├── projects.js        # 课题面板
        ├── hermes_console.js  # Hermes 深度对话控制台
        ├── learning.js        # 自主学习管理
        └── research.js        # v3.5 课题指导面板（单元时间线/知识库/记忆/工作流）
```

---

## 核心功能

### 已完成（Phase 0-10）

| 功能 | 状态 | 说明 |
|------|------|------|
| 会话管理 | ✅ | 创建、续接、归档、消息持久化 |
| CLI对话 | ✅ | 交互式对话、多行输入、命令系统 |
| 人格注入 | ✅ | 完整林赛人格、30000字符上下文预算 |
| 长期记忆 | ✅ | 用户画像、工作上下文、记忆片段 |
| 会话摘要 | ✅ | 自动摘要生成、跨会话记忆索引 |
| 任务管理 | ✅ | CRUD、状态流转、逾期检测 |
| 主动感知 | ✅ | 心跳扫描、截止日期提醒、压力信号检测 |
| 自主级别 | ✅ | observe / suggest / act 三级控制 |
| 模式识别 | ✅ | 自动识别 co-working / deep-talk / quick-check |
| 文档协作 | ✅ | Markdown/TXT读取、代码分析、LLM摘要 |
| Agora集成 | ✅ | 上下文导出/导入、历史人物群聊桥接 |
| **Web 界面** | ✅ | 浏览器交互、双主题、流式输出、任务面板 |
| **聊天记录浏览器** | ✅ | 历史会话查看、关键词标签、跨会话搜索 |
| **多模型路由** | ✅ | CLI + HTTP API，自动降级，限流切换 |
| **Token 统计** | ✅ | API 精确统计 + CLI 字符估算，多维度查询 |
| **技能系统** | ✅ | 8+ 个技能（数学推导/代码审查/实验设计/文献蒸馏/项目规划/群聊会议/HPC/自测），关键词触发 |
| **任务看板增强** | ✅ | 三列看板、进度条、子任务、里程碑 |
| **子代理调用** | ✅ | 5 工具（file_read/write, calc, task_create, knowledge_query），安全白名单 |
| **智能知识库** | ✅ | raw/wiki 分层、知识图谱、交互触发生长、林赛视角 |
| **内测系统** | ✅ | 137+207 检查点自动化回归测试（单元+Web API），零依赖轻量框架 |
| **深度评估** | ✅ | 9 维度架构稳定性审查，风险评分 150/1000 |
| **Obsidian 兼容** | ✅ | 双向链接 `[[WikiLink]]`、frontmatter、Vault 配置、模板 |
| **自主学习引擎** | ✅ | arXiv/联网检索/raw 自动蒸馏、质量评估、概念整合、成本安全 |
| **Claude CLI 配套** | ✅ | 人工管理指南 + 4 个 prompt 模板（质量审查/维护审查/概念合并/论文精读） |
| **工具协作者** | ✅ | run_command（执行 CLI 命令）、hermes_chat（Hermes 深度对话）、人格软链接、工具引擎接入 copilot_engine |
| **认知回流引擎** | ✅ | hermes 会话→记忆提炼、记忆冷启动（112 会话→26 记忆片段+10 研究方向+7 技能） |
| **开场即主动** | ✅ | heartbeat 增强 + 前端 banner + 会话注入主动提醒 |
| **浅输入人格锚定** | ✅ | 问候/闲聊注入记忆锚点，避免通用 AI 客服腔 |
| **知识库命中埋点** | ✅ | build_context 返回 kb_hits，SSE metadata 事件传递、引用来源 UI |
| **主动检索增强** | ✅ | should_search_knowledge() 5 级智能判断 |
| **课题管理** | ✅ | 课题 CRUD、状态机（planning→active→paused/completed）、PROJECT-MEMORY.md 自动压缩 |
| **单元管理** | ✅ | 单元 CRUD、验收标准结构化数组、风险追踪、状态机 |
| **课题分层知识库** | ✅ | raw/parsed/summary 三层、TF-IDF 倒排索引、标签索引、外部文件导入 |
| **课题记忆** | ✅ | 三级记忆（对话全文/片段/核心记忆）、决策记录、风险记录 |
| **跨课题检索** | ✅ | @课题知识库语法、跨课题搜索、课题上下文构建 |
| **课题工作流** | ✅ | 规划→执行→验收→完成→总结 全流程编排 |
| **课题 Web 面板** | ✅ | 37 个 API 路由 + 前端面板（单元时间线/知识库浏览器/记忆面板/工作流操作） |
| **知识库主舞台** | ✅ | 独立界面（文件树+预览双栏），聊天降为可折叠侧栏，MOC 知识地图 |
| **文献独立讨论** | ✅ | 大弹窗讨论模式（论文+对话+检索面板），归档沉淀链路（全文→摘要→凝练→概念） |
| **AI辅助任务指派** | ✅ | 只说目标+要求，AI自动生成任务描述+hermes执行指令 |
| **统一状态同步** | ✅ | Copilot与hermes共享item-status.json，操作双向同步（Copilot=hermes操作台） |
| **知识库自维护** | ✅ | 五维过滤/分页/自定义分类/别名发现/阶段晋升/自动连边 |

---

## 上游资产

林赛的人格资产来源于 [`virtu-LinSai`](~/Desktop/hermes_workspace/sandbox/virtu-LinSai) 项目：
- 190 万字自传叙事（0-31 岁）
- 16 篇大师学习日志
- 5 篇人格提炼文件
- 3 篇最终产出文件（SOUL.md / SKILL.md / WORKSTYLE.md）

本项目是 `virtu-LinSai` 的**消费端应用**，引用但不修改上游资产。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 运行环境 | Python 3（仅标准库） | 零第三方依赖 |
| 内容格式 | Markdown（.md） | 对话记录、任务描述、记忆片段 |
| 元数据 | JSON | 会话状态、记忆索引、任务追踪 |
| LLM接口 | Kimi CLI / Claude CLI | 通过 subprocess 调用本地 CLI，不直接调 API |
| 路径处理 | pathlib.Path | 禁止硬编码绝对路径 |

---

## 开发阶段

| 阶段 | 目标 | 状态 |
|------|------|------|
| Phase 0 | 基础框架 + 人格资产 | ✅ 完成 |
| Phase 1 | MVP：会话管理 + CLI对话 | ✅ 完成 |
| Phase 2 | 长期记忆 + 用户画像 + 任务管理 | ✅ 完成 |
| Phase 3 | 主动感知 + 自主提醒 + 模式识别 | ✅ 完成 |
| Phase 4 | 文档协作 + 代码协作 + Agora集成 + Web界面 | ✅ 完成 |
| Phase 5 | Token统计 + 技能系统 + **知识库精细化** + 子代理调用 | ✅ 完成 |
| Phase 5.5 | **内测系统** — 影子用户自动化回归测试（137+207 检查点） | ✅ 完成 |
| Phase 6 | **自主学习引擎** — 感知/蒸馏/评估/调度/展示（5 阶段） | ✅ 完成 |
| Phase 7 | 性能优化 + 生态扩展 | ⏳ 待开发 |
| Phase 8 | **工具协作者（v2.1.0）** — run_command/hermes_chat 工具、人格软链接、工具引擎接入 | ✅ 完成 |
| Phase 9 | **认知闭环（v3.4.0）** — 认知回流引擎、记忆冷启动、开场即主动、浅输入人格锚定、知识库命中埋点、主动检索增强 | ✅ 完成 |
| Phase 10 | **课题指导模块（v3.5.0）** — 课题/单元管理、分层知识库、课题记忆、跨课题检索、工作流编排、Web API + 前端面板 | ✅ 完成 |
| Phase 11 | **知识库主舞台+认知闭环（v3.6-v4.0）** — 知识库独立界面、MOC/双链/自维护、记忆清洗+去重防护 | ✅ 完成 |
| Phase 12 | **协作操作台（v4.1-v4.2）** — 文献独立讨论、AI辅助指派、统一状态同步（Copilot↔hermes） | ✅ 完成 |

### Web 界面特性

| 特性 | 说明 |
|------|------|
| 双主题 | 深色 / 浅色 / 自动跟随系统 |
| 会话管理 | 侧边栏搜索、新建、切换 |
| 流式输出 | SSE 实时打字效果 |
| Markdown 渲染 | 代码块、引用、列表、粗体、斜体 |
| 快捷命令 | /mode /read /agora /summary 一键触发 |
| 任务面板 | 右侧栏三列看板，进度条 + 子任务 + 里程碑 |
| 技能检测 | 输入框实时检测激活技能，顶部显示技能徽章 |
| Token 统计 | 设置面板显示今日/累计用量，按 Provider 分组 |
| 知识库管理器 | 7 标签页模态框：概览 / Raw / Wiki / 图谱 / 生长 / **健康度** / **别名** |
| **技能面板** | 🎯 自动/手动模式 + 模糊搜索 + 技能开关（侧边栏工具栏入口） |
| 子代理工具日志 | 消息旁显示工具调用提示，可展开查看执行详情 |
| **侧边栏工具栏** | 📚 知识库 / 🎯 技能 / 📋 任务 / 📊 用量 独立快捷入口 |
| **本地软连接** | Wiki/Raw 文件一键在系统编辑器中打开，支持复制路径 |
| **引用来源标签** | 消息气泡下方显示知识库引用标签，点击跳转 |
| **主动提醒 banner** | 会话开场注入主动提醒，前端横幅展示 |
| **学习管理器** | 学习日志/待审队列/统计面板，策略设置与手动触发 |
| **Hermes 控制台** | 调用 Hermes LinSai profile 进行深度对话 |
| **课题指导面板** | 课题列表/详情、单元时间线、知识库浏览器、记忆面板、工作流操作 |
| 移动端适配 | 侧边栏折叠、触摸优化 |

---

## 贡献与维护

- 所有 Python 脚本仅使用标准库
- 修改前必读 `AGENTS.md`
- 所有变更记录在 `CHANGELOG.md`

---

*版本：4.2.2*  
*日期：2026-07-17*
