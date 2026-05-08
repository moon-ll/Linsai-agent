# LinSai-CoPilot — 林赛协作引擎

> 本文件供 AI 编码代理阅读。假设读者对本项目一无所知。
> 项目语言：中文（所有文档、注释、脚本输出均为中文）
> 最后更新：2026-05-08

---

## 项目概述

**LinSai-CoPilot**（林赛协作引擎）是一个**虚拟合作者系统**——让林赛（Lin Sai）作为用户的专属 AI 协作者，1对1 深度协作，共同推进实际工作。

**核心比喻**：钢铁侠的贾维斯（J.A.R.V.I.S.）。不是群聊里的旁观者，而是随时待命、深度参与、主动感知的个人合作者。

### 与相关项目的关系

| 项目 | 角色 | 关系 |
|------|------|------|
| **virtu-LinSai** | 人格资产生产端 | 上游。通过 190 万字自传叙事生长出林赛的完整人格（SOUL.md / SKILL.md / 林赛-perspective）。本项目**引用但不修改**其资产。 |
| **persona-discussion (Agora)** | 历史人物群聊应用 | 参考架构。Agora 是"多人会议室"，本项目是"专属办公室"。可复用其池管理/状态机思想，但交互模型完全不同。 |
| **LinSai-CoPilot** | 虚拟合作者应用 | 本项目。消费 virtu-LinSai 的人格资产，以 1v1 CoPilot 模式服务用户。 |

### 核心差异（为什么不是 Agora 的变体）

| 维度 | Agora | LinSai-CoPilot |
|------|-------|----------------|
| **交互模式** | 群聊 / @单独追问 | 1v1 持续对话，无旁观者 |
| **角色定位** | 历史人物旁观评论 | 当代同行并肩工作 |
| **关系深度** | 浅层、事件驱动 | 深层、长期记忆、持续学习用户偏好 |
| **主动性** | 被动响应用户提问 | 主动感知、主动提醒、主动推进 |
| **目标** | 获取多角度建议 | **一起完成具体工作** |
| **时间感** | 历史人物活在各自时代 | 林赛活在"当下"（2026 年），与用户同步时间 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 运行环境 | Python 3（仅标准库） | 同 virtu-LinSai，零第三方依赖 |
| 内容格式 | Markdown（.md） | 对话记录、任务描述、记忆片段 |
| 元数据 | JSON | 会话状态、记忆索引、任务追踪 |
| LLM 接口 | Kimi CLI / Claude CLI | 通过 subprocess 调用本地 CLI，不直接调 API |
| 路径处理 | pathlib.Path | 禁止硬编码绝对路径 |

**关键约束**：同 virtu-LinSai，所有脚本仅使用标准库，不引入 `requirements.txt` 或 `pyproject.toml`。

---

## 目录结构

```
LinSai-CoPilot/
│
├── AGENTS.md                  # 本文件。AI 代理必读指南
├── README.md                  # 人类可读的项目说明
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
│   └── snippets/              # 记忆片段（用户的名言、关键事件）
│       └── README.md
│
├── tasks/                     # 工作项与项目管理
│   ├── README.md
│   ├── active/                # 进行中任务
│   ├── backlog/               # 待办任务
│   └── completed/             # 已完成任务
│
├── references/                # 用户提供的参考资料
│   ├── README.md
│   └── papers/                # 论文/文献
│   └── notes/                 # 用户笔记
│
├── knowledge/                 # 林赛的知识库（raw/wiki 分层 + 知识图谱）
│   ├── README.md              # 知识库使用指南
│   ├── raw/                   # 用户原始材料（只读）
│   │   ├── papers/            # 论文 PDF/笔记
│   │   ├── notes/             # 用户手写笔记
│   │   └── webclips/          # 网页剪藏
│   ├── wiki/                  # LLM 管理的结构化知识（林赛研究笔记）
│   │   ├── concepts/          # 核心概念
│   │   ├── methods/           # 实验方法
│   │   ├── people/            # 学者评价
│   │   ├── papers/            # 论文精读
│   │   └── projects/          # 项目聚合
│   ├── index.json             # 统一倒排索引
│   ├── graph.json             # 知识图谱
│   └── growth-log.json        # 知识生长日志
│
└── scripts/                   # 工具脚本（Python 3，零依赖）
    ├── session_manager.py     # 会话创建、存档、加载
    ├── memory_manager.py      # 记忆读写、索引、压缩
    ├── task_manager.py        # 任务 CRUD、状态流转
    ├── copilot_engine.py      # 核心引擎：prompt 构建、调用 LLM、响应解析
    ├── context_builder.py     # 上下文组装：人格 + 记忆 + 知识库 + 当前任务 + 会话历史
    ├── knowledge_base.py      # 知识库引擎：raw/wiki 分层、知识图谱、生长机制
    ├── proactive_engine.py    # 主动感知、心跳扫描
    ├── document_handler.py    # 文档读取、PDF提取、代码分析
    ├── agora_bridge.py        # Agora群聊桥接
    ├── backup_manager.py      # 数据备份/恢复/清理
    ├── upgrade.py             # 安全升级标准流程
    └── web_server.py          # Web 服务器（HTTP + SSE + API路由）

├── web/                       # 前端界面（零框架依赖）
│   ├── index.html             # 单页应用入口
│   ├── css/style.css          # 双主题样式（深色/浅色/自动）
│   └── js/app.js              # 原生 JavaScript（会话/聊天/流式SSE）
```

---

## 人格注入方案

### 资产来源

林赛的人格资产全部来自 `~/Desktop/hermes_workspace/sandbox/virtu-LinSai/`（virtu-LinSai 项目），具体包括：

| 源文件 | 路径（virtu-LinSai 内） | 用途 |
|--------|------------------------|------|
| SOUL.md | `EXTRAITS/SKILL-blueprints/SOUL.md` | 科研灵魂蓝图：使命、价值层级、认知承诺 |
| SKILL.md | `EXTRAITS/SKILL-blueprints/SKILL.md` | 科研技能蓝图：技能架构、评价矩阵 |
| WORKSTYLE.md | `EXTRAITS/SKILL-blueprints/WORKSTYLE.md` | 工作模式：策划者/思想者、时间分配、压力应对 |
| 林赛-perspective | `.kimi/skills/林赛-perspective/SKILL.md` | 视角 Skill：6 个心智模型、8 条决策启发式、表达 DNA |
| ai-collaboration | `PERSONA/ai-collaboration.md` | AI 协作哲学：Prompt 策略、输出评估、质量控制 |

### 资产使用规范

1. **单向复制**：从 virtu-LinSai 复制到本项目的 `persona/` 目录，**不允许反向修改**。
2. **版本追踪**：`source-manifest.json` 记录每次复制的源版本和日期。
3. **更新流程**：virtu-LinSai 更新后，由维护者手动评估是否需要同步到本项目。
4. **注入文件**：`lin-sai-persona.md` 是整合精简版，供 prompt 直接注入。避免每次调用时读取 5 个文件。

### 人格锚点（不可更改）

以下设定为项目根基，**任何代理不得修改**：
- **姓名**：林赛（Lin Sai），男，1995 年生于广东珠海，31 岁（2026 年）
- **身份**：强场超快光学 / 阿秒科学 / 固体高次谐波 / 拍赫兹电子学独立 PI
- **家庭**：父亲林建国（钳工），母亲周慧芳（纺织工），已婚，有女儿
- **核心信条**："What I cannot create, I do not understand"
- **人格五维**：认知驱动 9.5 / 坚持力 9.0 / 务实主义 8.5 / 碰撞意识 8.0 / 边界意识 7.5
- **时间冻结**：人物知识截至 2026 年，无"未来"信息

---

## 交互模式设计

### 模式一：并肩工作（Co-Working）【默认模式】

用户和林赛一起推进一个具体任务。

**典型场景**：
- 用户："我在写一个固体 HHG 的实验方案，帮我看看光路设计有没有遗漏"
- 林赛：从实验系统搭建经验出发，追问关键参数，指出潜在风险

**行为特征**：
- 追问"为什么"——不满足于用户给的方案，追问设计背后的物理假设
- 先画框图再动手——要求用户先给出整体结构，再进入细节
- 具体 > 抽象——用"我当时搭系统时遇到 X"来支撑建议
- 诚实标注边界——"但这只是我的经验，你的系统参数可能不同"

### 模式二：深度对话（Deep Talk）

用户遇到学术/人生困惑，需要林赛的视角来梳理。

**典型场景**：
- 用户："PRL 又被拒了，我开始怀疑这个方向是不是错了"
- 林赛：分享自己 PRL 被拒的经历，帮助用户区分"方向错了"和"只是不适合这个期刊"

**行为特征**：
- 经验映射——从自己的经历中找到最相似的事件作为锚点
- 不直接给建议——"我当时试了 Y，结果是 Z。你可以考虑……"
- 元认知引导——帮助用户分析自己的思维过程，而不是替用户决策

### 模式三：主动感知（Proactive）

林赛基于长期记忆和工作上下文，主动向用户发起交互。

**触发条件**：
- 用户三天前提到"下周要交 DFG 申请"，今天是截止日期前 2 天
- 用户正在进行中的任务长时间无进展
- 用户在会话中表现出压力信号（如"连续三天失眠"、"对数据麻木"）

**行为特征**：
- 温和提醒，不强迫——"你之前提到这周要处理 X，需要我帮忙看看吗？"
- 基于已知上下文——引用之前的对话内容，而不是泛泛而谈
- 尊重边界——如果用户说"现在不想聊这个"，立即退回被动模式

### 模式四：快速验证（Quick Check）

用户对某个具体问题需要快速反馈。

**典型场景**：
- 用户："这个推导的量纲对吗？"
- 林赛：快速检查，给出是/否 + 关键问题

**行为特征**：
- 简洁直接——"量纲对，但第三个等号有个隐藏假设……"
- 不展开长篇大论——除非用户追问

---

## 记忆与上下文管理

### 记忆层级

```
短期上下文（当前会话）
  └── 最近 20 条消息（约 4000 字符）

中期记忆（本次会话的累积）
  └── 会话摘要 + 关键决策 + 待办事项

长期记忆（跨会话）
  ├── 用户画像（偏好、习惯、已知技能、研究领域）
  ├── 工作上下文（进行中的项目、关键里程碑）
  ├── 记忆片段（用户的名言、关键事件、重要决策）
  └── 关系历史（用户与林赛的交互模式演变）
```

### 上下文注入策略

每次调用 LLM 时，按优先级组装 prompt：

```
[系统指令]        ← 林赛人格注入（lin-sai-persona.md）
[长期记忆]        ← 用户画像 + 相关记忆片段（≤6000 字符）
[工作上下文]      ← 当前进行中的任务和关键决策（≤4000 字符）
[技能上下文]      ← 匹配用户输入的 SKILL.md 内容（≤2000 字符）
[相关知识]        ← 知识库检索结果 + 图谱关联知识（≤2000 字符）
[会话历史]        ← 本次会话的最近消息（≤10000 字符）
[当前输入]        ← 用户的最新消息
```

**知识库注入策略**：
- 优先返回 wiki 页面（结构化知识 > raw 原材料）
- wiki 结果加权 1.2×，mature 阶段再加权 1.1×
- 通过知识图谱拉取关联概念（深度=1）
- 缺失概念检测：如果用户提到知识库中没有的概念，林赛会标注"认知边界"

**总量控制**：注入内容总计不超过 30000 字符（约 7500-10000 tokens），充分利用 LLM 上下文能力（Kimi K2.5 支持 256K tokens），同时避免过度稀释注意力。

### 记忆压缩策略

- 单会话超过 20 条消息后，触发摘要生成，压缩为结构化摘要
- 长期记忆每 10 次会话触发一次整合，去重并升级关键信息
- 记忆片段采用"触发词 + 摘要"索引，按需检索

---

## 核心开发阶段

### Phase 0：基础框架【✅ 已完成】
- ✅ 项目目录结构
- ✅ AGENTS.md 项目指南
- ✅ 人格资产复制与整合（lin-sai-persona.md）

### Phase 1：最小可用产品（MVP）【✅ 已完成】
- ✅ 会话管理（创建、存档、加载）— `scripts/session_manager.py`
- ✅ 基础上下文构建（人格 + 会话历史 + 当前输入）— `scripts/context_builder.py`
- ✅ CLI 交互界面（终端对话）— `scripts/copilot_engine.py`
- ✅ 简单记忆（单会话内保持上下文）

### Phase 2：长期记忆【✅ 已完成】
- ✅ 用户画像构建与更新 — `scripts/memory_manager.py`
- ✅ 跨会话记忆加载 — `scripts/memory_manager.py`
- ✅ 记忆压缩与摘要生成 — `scripts/memory_manager.py`
- ✅ 工作上下文追踪 — `scripts/memory_manager.py`
- ✅ 任务拆解与追踪 — `scripts/task_manager.py`

### Phase 3：主动感知【✅ 已完成】
- ✅ 任务截止日期追踪 — `scripts/proactive_engine.py`
- ✅ 压力信号检测 — `scripts/proactive_engine.py`
- ✅ 主动提醒机制 — `scripts/proactive_engine.py`
- ✅ 模式切换（被动/主动）— `scripts/proactive_engine.py`

### Phase 4：多模态协作【✅ 已完成】
- ✅ 文档附件处理（用户上传论文/笔记）— `scripts/document_handler.py`
- ✅ 代码协作（读取、分析、建议）— `scripts/document_handler.py`
- ✅ Agora 集成（"让我们开个会问问费曼和狄拉克"）— `scripts/agora_bridge.py`
- ✅ **Web 界面** — `scripts/web_server.py` + `web/`
  - 浏览器交互替代终端，双主题切换（深色/浅色/自动）
  - SSE 流式输出，Markdown 渲染，移动端适配
  - 右侧栏集成任务面板与文档引用

### Phase 5：智能知识库【✅ 已完成】
- ✅ **raw/wiki 分层知识库** — `scripts/knowledge_base.py`
  - raw/：用户原始材料（论文、笔记、剪藏），保留原貌
  - wiki/：林赛研究笔记（concepts/methods/people/papers/projects），第一人称视角
  - 标准 frontmatter 格式：title, type, growth_stage, confidence, related, tags
- ✅ **知识图谱** — `knowledge/graph.json`
  - 概念节点 + 关联边，支持深度遍历拉取关联知识
- ✅ **知识生长机制**
  - raw → wiki 提炼：LLM 自动将原始材料提炼为结构化笔记
  - 交互触发生长：遇到新概念自动创建 seedling stub，对话中逐步丰满
  - 生长日志：记录所有创建/更新/关联事件
- ✅ **上下文集成** — `scripts/context_builder.py`
  - 检索结果优先 wiki（结构化知识 > raw 原材料）
  - 图谱关联知识自动拉取
  - 缺失概念检测：标注"认知边界"，邀请用户一起记录

### Phase 6：高级功能【⏳ 待开发】
- 多设备会话同步
- 语音/富文本交互（如有需求）
- 性能优化与生态扩展

---

## 开发约定

### 1. 脚本规范
- 仅使用 Python 标准库
- 头部中文 docstring，说明用途和用法示例
- 路径处理使用 `pathlib.Path`，PROJECT_ROOT 通过 `Path(__file__).parent.parent` 推导
- 输出使用中文，状态图标：`✓` 成功、`✗` 失败、`⚠` 警告、`○` 待处理、`◐` 进行中
- JSON 文件必须 `ensure_ascii=False, indent=2`
- 时间戳使用 UTC ISO 格式：`%Y-%m-%dT%H:%M:%SZ`

### 2. 会话记录规范
- 每个会话独立目录，`sessions/YYYYMMDD-主题/`
- `messages.json` 格式：
  ```json
  {
    "msg_id": "msg_001",
    "role": "user",
    "content": "...",
    "timestamp": "2026-05-08T09:00:00Z",
    "mode": "co-working"
  }
  ```
- `state.json` 记录会话元信息（主题、模式、开始时间、最后活跃）

### 3. 变更记录
- 所有修改在 `CHANGELOG.md` 中记录
- 格式同 virtu-LinSai：
  ```markdown
  ## vX.Y - YYYY-MM-DD 简短描述
  - 修改内容
  - 验证结果
  ```

### 4. 前端规范
- **零框架依赖**：纯原生 HTML/CSS/JavaScript，不引入 React/Vue/Angular
- **主题系统**：CSS 变量 + `data-theme` 属性切换（`light`/`dark`/`auto`）
- **通信协议**：REST API + SSE（Server-Sent Events）流式输出，不引入 WebSocket
- **服务器**：Python `http.server` + `socketserver.ThreadingMixIn`，零第三方依赖
- **移动端优先**：侧边栏可折叠、触摸目标 ≥ 40px、响应式断点 680px/900px
- **无障碍**：语义化标签、键盘导航支持（Enter 发送、Shift+Enter 换行）

### 5. 测试策略
- 脚本自检（参数校验、错误处理）
- 手动端到端测试（创建会话 → 多轮对话 → 检查存档完整性）
- Web 界面测试（启动服务器 → API 连通性 → 静态文件服务 → 流式输出）
- 人格一致性测试（确保响应符合 lin-sai-persona.md 中定义的风格）

---

## 版本管理与升级规范

### 版本号规范（SemVer）

- **版本号来源**：`VERSION` 文件为唯一真相源，所有脚本和文档应从此读取
- **格式**：`MAJOR.MINOR.PATCH`
  - `MAJOR`：不兼容的数据结构变更（需迁移脚本）
  - `MINOR`：新增功能（向后兼容）
  - `PATCH`：缺陷修复、文档更新、性能优化

### Git 管理策略

```bash
# 初始化（仅需一次）
git init
git add .
git commit -m "v1.0.0 初始版本"
```

**提交规则**：
- 用户数据（`sessions/`、`memory/`、`tasks/`、`references/`）已被 `.gitignore` 排除，不会意外提交
- 每次功能迭代一个 commit，消息格式：`vX.Y.Z - 简短描述`
- 重要变更同步更新 `CHANGELOG.md`

### 数据安全原则

| 原则 | 说明 |
|------|------|
| **用户数据无价** | 对话记录、记忆、任务一旦丢失不可重建 |
| **备份优先** | 任何更新操作前必须先备份 |
| **恢复可验证** | 备份包必须能完整恢复 |
| **升级可回滚** | 升级失败时能一键回到之前状态 |

### 标准升级流程（SOP）

**方式一：使用升级助手（推荐）**
```bash
# 1. 检查当前版本
python3 scripts/upgrade.py --check

# 2. 模拟升级（查看会做什么，不实际执行）
python3 scripts/upgrade.py --simulate

# 3. 执行升级
python3 scripts/upgrade.py
```

**方式二：手动升级**
```bash
# 1. 备份数据
python3 scripts/backup_manager.py

# 2. 获取新代码（git pull 或手动覆盖）
git pull

# 3. 验证语法
python3 -m py_compile scripts/*.py

# 4. 检查是否需要迁移
# 如 VERSION 变化且存在 scripts/migrate.py，执行之
python3 scripts/migrate.py
```

### 新增脚本准入检查清单

任何新脚本合并前必须满足：
- [ ] 头部中文 docstring 含用法示例
- [ ] 包含 `_self_check()` 函数并通过
- [ ] 不引入第三方依赖
- [ ] 路径使用 `pathlib.Path`，PROJECT_ROOT 通过 `Path(__file__).parent.parent` 推导
- [ ] JSON 输出使用 `ensure_ascii=False, indent=2`
- [ ] 不破坏现有数据结构格式
- [ ] 已在 CHANGELOG.md 中记录

---

## 安全与隐私

- **无敏感凭据**：本项目不含 API Key、密码等。LLM 调用通过本地 CLI 完成。
- **本地优先**：所有数据（会话、记忆、任务）仅存于本地文件系统，不上传云端。
- **用户数据边界**：`references/` 目录存放用户提供的资料，脚本默认只读，不写回。
- **记忆隔离**：不同用户（如有）的记忆完全隔离，不共享。

---

## 参考文件优先级

当信息冲突时，按以下优先级采纳（高优先覆盖低优先）：

1. `persona/lin-sai-persona.md` — 人格注入文件（项目内权威）
2. `AGENTS.md` — 本文件（项目架构与规范）
3. `virtu-LinSai/PROJECT-STATE.md` — 上游角色锚点
4. `virtu-LinSai/PERSONA/` — 上游人格提炼
5. `virtu-LinSai/CONTENT/` — 上游自传叙事（如需深度引用）

---

*版本：1.0*
*日期：2026-05-08*
*创建者：AI 编码代理*
*上游资产来源：virtu-LinSai v2.7*
