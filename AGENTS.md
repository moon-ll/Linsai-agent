# LinSai-CoPilot — 林赛协作引擎

> 本文件供 AI 编码代理阅读。假设读者对本项目一无所知。
> 项目语言：中文（所有文档、注释、脚本输出均为中文）
> 最后更新：2026-07-28
> 提示：完整目录结构见 `docs/PROJECT-STRUCTURE.md`，完整架构说明见 `docs/ARCHITECTURE.md`。

---

## 项目概述

**LinSai-CoPilot**（林赛协作引擎）是一个**虚拟合作者系统**——让林赛（Lin Sai）作为用户的专属 AI 协作者，1 对 1 深度协作，共同推进实际工作。

**核心比喻**：钢铁侠的贾维斯（J.A.R.V.I.S）。不是群聊里的旁观者，而是随时待命、深度参与、主动感知的个人合作者。

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

## 运行与构建

**无构建步骤**。Python 脚本直接运行，无编译、无打包、无依赖安装。

### 启动 Web 界面（推荐）

```bash
python3 scripts/web_server.py              # 默认端口 8080
python3 scripts/web_server.py --port 9000  # 指定端口
./scripts/launch.sh                        # 一键启动（自动打开浏览器）
```

打开 `http://localhost:8080`。

### 启动 CLI 对话

```bash
python3 scripts/copilot_engine.py --start "固体HHG实验方案设计"
python3 scripts/copilot_engine.py --continue
python3 scripts/copilot_engine.py --list
```

### 常用维护命令

```bash
python3 scripts/backup_manager.py                         # 手动备份
python3 scripts/upgrade.py --check                        # 升级检查
python3 scripts/upgrade.py --simulate
python3 scripts/upgrade.py
python3 scripts/kb_maintenance.py --weekly                # 知识库周维护
python3 scripts/memory_reflow.py --reflow                 # 认知回流
python3 scripts/sync_engine.py                            # 同步 hermes 产出
python3 scripts/rebuild_lifecycle.py --dry-run            # 修复 lifecycle 不一致（预览）
python3 scripts/rebuild_lifecycle.py
python3 scripts/import_hermes_topics.py --dry-run         # 导入 hermes 课题（预览）
python3 scripts/import_hermes_topics.py --activate
python3 scripts/proposal_lifecycle.py --setup-cron "57 8 * * *"   # 每日编排 cron
python3 scripts/proposal_lifecycle.py --setup-weekend     # 周末任务 cron
python3 scripts/weekend_orchestrator.py --input --dry-run # 手动触发周末输入
python3 scripts/weekend_orchestrator.py --output --dry-run
python3 scripts/weekend_orchestrator.py --reflection --dry-run
python3 scripts/idea_generator.py --auto --dry-run        # 自动生成研究设想
```

### 语法检查

```bash
python3 -m py_compile scripts/*.py
```

---

## 测试策略

采用**三层测试体系**：

1. **单元/核心回归测试**：`python3 scripts/self_test.py`，支持 `--module`、`--scenario`、`--persona`、`--web`、`--web-ci`。
2. **模块自检**：大量脚本支持 `--self-check`，运行 `python3 scripts/{module}.py --self-check`。
3. **E2E 集成测试**：`python3 scripts/test_e2e_learning_full.py`（需真实 Claude CLI 环境，非日常回归项）。

**当前基线**：
- `--module`：116/116 通过
- `--scenario`：16/16 通过
- `--persona`：38/38 通过
- `--web-ci`：Web API 虚拟用户测试覆盖所有主要 API 命名空间

**测试设计原则**：零污染（临时隔离目录运行）、零成本（不调用 LLM API）、自动发现（新增 `scripts/tests/test_*.py` 自动纳入回归）。

---

## 代码规范

### Python 脚本

- **仅使用标准库**，禁止新增 `requirements.txt` 或 `pyproject.toml`。
- 头部中文 docstring，说明用途和用法示例。
- 路径处理使用 `pathlib.Path`；`PROJECT_ROOT` 通过 `Path(__file__).parent.parent` 推导。
- JSON 文件必须 `ensure_ascii=False, indent=2`。
- 时间戳使用 UTC ISO 格式：`%Y-%m-%dT%H:%M:%SZ`。
- 输出使用中文，状态图标统一：`✓` 成功、`✗` 失败、`⚠` 警告、`○` 待处理、`◐` 进行中。
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

## 架构说明（摘要）

模块与数据域、API、协作关系、生命周期、总控层、控制台等详细内容已拆分至 `docs/ARCHITECTURE.md`，本节仅保留摘要。AI 编码代理在涉及架构细节时应优先查阅该文件。

### 模块分类与导入边界

模块分为 **CoPilot 核心**、**研究管线**、**共享基础设施**、**知识库引擎**、**Web 路由 Mixin** 五类。核心模块与研究管线模块互相隔离，仅共享基础设施可双向导入；研究管线禁止直接导入会话、记忆、LLM 路由等核心模块，LLM 统一走 `llm_gateway`。详见 `docs/ARCHITECTURE.md` §1。

### 数据域隔离

- CoPilot 核心数据域：`sessions/`、`memory/`、`tasks/`。
- 共享只读域：`knowledge/`（管线只读，写须通过 `learning_engine`）。
- 研究管线独立域：`research_proposals/`（含 drafts/optimizing/pending_review/archived 及每个 proposal 的 00-05 阶段产物）。

详见 `docs/ARCHITECTURE.md` §2。

### Web API 命名空间

Web 服务器以 Mixin 聚合 12 个路由模块，命名空间按功能归属分为 CoPilot 核心（sessions/tasks/knowledge/skills/learning/projects/research/hermes/lifecycle/orchestrator/console/settings）与研究管线（pipeline）。详见 `docs/ARCHITECTURE.md` §3。

### hermes 协作架构

由 `linsai`、`pipeline-runner`、`researcher`、`analyst`、`writer`、`critic`、`reviewer` 7 个 profile 组成。关键协作文件包括 `state_sync.py`（论文状态总线）、`memory_bridge.py`（记忆同步）、`hermes_pipeline.py`（六阶段派活）、`proposal_lifecycle.py`（四阶段生命周期）、`adversarial_governance.py`（对抗奖惩）。详见 `docs/ARCHITECTURE.md` §4。

### 提案生命周期

四阶段：`drafts → optimizing → pending_review → archived`。采用 writer-critic 对抗优化，critic 4 维度评分，writer 聚焦最弱维度修订。v6.7.5+ 改为每个 optimizing proposal 一个独立 worker cron；v6.7.6+ 引入 monitor meta-review 与 agent 分数奖惩；v6.7.7+ 增加输入端 `idea_generator`、输出端 `knowledge_output` 与周末模式。详见 `docs/ARCHITECTURE.md` §5。

### 林赛总控层（v6.7+）

在 hermes 之上新增监控/调优/失败分析/链路成长层，由 `orchestrator.py` 统一入口，整合 `profile_health.py`（profile 健康）、`failure_analyzer.py`（失败模式聚类）、`strategy_optimizer.py`（调度策略建议）。策略仅输出建议，人工确认后写入 `tuning-log.json`。详见 `docs/ARCHITECTURE.md` §6。

### 林赛控制台与设置中心（v6.7.7）

面向用户的统一操作界面：`web_routes_system.py` 提供 `/api/console/*`（流水线/Agent/告警），`web_routes_settings.py` 提供 `/api/settings/*`（7 类配置读写与变更预览）。前端对应 `web/js/console.js` 与 `web/js/settings_center.js`，支持一键触发 repair/orchestrate/optimize/clear-alert。详见 `docs/ARCHITECTURE.md` §7。

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

- **版本号来源**：`VERSION` 文件为唯一真相源（当前 `6.7.7`）。
- **格式**：`MAJOR.MINOR.PATCH`
  - `MAJOR`：不兼容的数据结构变更（需迁移脚本）
  - `MINOR`：新增功能（向后兼容）
  - `PATCH`：缺陷修复、文档更新、性能优化

### Git 管理策略

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

*版本：6.7.7*
*日期：2026-07-28*
*创建者：AI 编码代理*
*上游资产来源：virtu-LinSai v2.7*
