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

# 方式一（快捷）：一键启动并自动打开浏览器
./scripts/launch.sh

# macOS 用户可使用 ./scripts/launch.sh 一键启动

# 方式二：终端 CLI（轻量、脚本化）
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
├── docs/                      # 项目文档与报告
│   ├── PROJECT-PLAN.md        # 项目总策划案
│   ├── DEEP-AUDIT-REPORT.md   # 深度评估报告
│   ├── FUNCTIONAL-TEST-REPORT.md # 功能测试报告
│   └── prompts/               # LLM prompt 模板
│
└── scripts/                   # 工具脚本（Python 3，零依赖，23 个）
    ├── session_manager.py     # 会话管理
    ├── context_builder.py     # 上下文构建（Prompt组装）
    ├── copilot_engine.py      # 核心引擎（LLM调用 + CLI）
    ├── memory_manager.py      # 记忆系统
    ├── task_manager.py        # 任务管理
    ├── proactive_engine.py    # 主动感知
    ├── document_handler.py    # 文档与代码协作
    ├── agora_bridge.py        # Agora群聊桥接
    ├── llm_router.py          # 多模型路由与自动降级
    ├── usage_tracker.py       # Token 用量追踪
    ├── skill_manager.py       # 技能系统管理
    ├── tool_engine.py         # 子代理调用引擎
    ├── knowledge_base.py      # 知识库引擎
    ├── kb_capture.py          # 对话自动捕获
    ├── kb_maintenance.py      # 知识库批处理维护
    ├── logger.py              # 统一日志系统
    ├── chat_archive.py        # 聊天记录归档浏览器
    ├── backup_manager.py      # 数据备份/恢复
    ├── upgrade.py             # 安全升级流程
    ├── upgrade_wiki_for_obsidian.py  # wiki 双向链接升级
    ├── web_server.py          # Web 服务器
    ├── self_test.py           # 内测统一入口
    ├── deep_audit.py          # 深度评估脚本
    └── tests/                 # 自动化测试套件
        ├── test_runner.py
        ├── test_core.py
        ├── test_scenarios.py
        └── test_persona.py
```

---

## 核心功能

### 已完成（Phase 0-5）

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
| **内测系统** | ✅ | 88 检查点自动化回归测试（影子用户），零依赖轻量框架 |
| **深度评估** | ✅ | 9 维度架构稳定性审查，风险评分 150/1000 |
| **Obsidian 兼容** | ✅ | 双向链接 `[[WikiLink]]`、frontmatter、Vault 配置、模板 |

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
| 内容格式 | Markdown + JSON | 对话记录、记忆、任务 |
| LLM接口 | Claude CLI / Kimi CLI | 本地subprocess调用 |
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
| Phase 5.5 | **内测系统** — 影子用户自动化回归测试（88 检查点） | ✅ 完成 |
| Phase 6 | 性能优化 + 生态扩展 | ⏳ 待开发 |

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
| 移动端适配 | 侧边栏折叠、触摸优化 |

---

## 贡献与维护

- 所有 Python 脚本仅使用标准库
- 修改前必读 `AGENTS.md`
- 所有变更记录在 `CHANGELOG.md`

---

*版本：1.7.3*  
*日期：2026-05-12*
