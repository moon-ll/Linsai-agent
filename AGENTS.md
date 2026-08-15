# LinSai-CoPilot — 林赛协作引擎

> 本文件供 AI 编码代理阅读。假设读者对本项目一无所知。
> 项目语言：中文（所有文档、注释、脚本输出均为中文）
> 最后更新：2026-08-15
> 提示：完整目录结构见 `docs/PROJECT-STRUCTURE.md`，完整架构说明见 `docs/ARCHITECTURE.md`。

---

## 项目概述

**LinSai-CoPilot**（林赛协作引擎）是一个**虚拟合作者系统**——让林赛（Lin Sai）作为用户的专属 AI 协作者，1 对 1 深度协作，共同推进实际工作。

**核心比喻**：钢铁侠的贾维斯（J.A.R.V.I.S）。不是群聊里的旁观者，而是随时待命、深度参与、主动感知的个人合作者。

**当前架构定位（v6.8+）**：
- CoPilot 是**操作台/监控层**：提供 Web 界面、会话管理、知识库、任务追踪、提案生命周期可视化和人工决策入口。
- hermes 是**执行端**：通过 7 个专业 profile 运行 agent loop，负责文献调研、缺口分析、申请书撰写、对抗优化等重脑力工作。
- 两者通过 `state_sync.py`（论文统一状态）、`memory_bridge.py`（记忆同步）、`hermes_pipeline.py`（管线派活）协同。
- 全自动链路（v6.8+）以**课题生命周期**为核心：按 4 个时段轮转推进每个 optimizing proposal，每个时段聚焦一个课题直至完成完整一轮（按章节评审 + 整体一致性评审 + 参考文献校验）。

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
| LLM 接口 | MiniMax-M3（主） / GLM-5.2 / Kimi CLI / Claude CLI | 通过 hermes profile 管理，CoPilot 侧 `llm_router.py` / `llm_gateway.py` 自动降级。 |
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
python3 scripts/kb_distill.py --dry-run                  # raw→wiki 蒸馏预览
python3 scripts/kb_distill.py --batch 5                  # 蒸馏最旧 5 篇（cron 每日 12:50）
python3 scripts/kb_linker.py --apply                     # 图谱补边（蒸馏尾部自动跑）
python3 scripts/kb_merger.py --dry-run                   # 重复页合并预览（周日限 5 对）
python3 scripts/kb_taxonomy.py                          # 分类候选预览
python3 scripts/memory_reflow.py --reflow                 # 认知回流
python3 scripts/sync_engine.py                            # 同步 hermes 产出
python3 scripts/rebuild_lifecycle.py --dry-run            # 修复 lifecycle 不一致（预览）
python3 scripts/rebuild_lifecycle.py
python3 scripts/import_hermes_topics.py --dry-run         # 导入 hermes 课题（预览）
python3 scripts/import_hermes_topics.py --activate
python3 scripts/proposal_lifecycle.py --setup-cron-v2                  # 安装 v2 cron 框架（每日编排 + 修复 + per-proposal workers + 周末任务）
python3 scripts/proposal_lifecycle.py --setup-weekend                  # 单独安装/重置周末任务 cron
python3 scripts/weekend_orchestrator.py --input --dry-run              # 周末输入端 dry-run
python3 scripts/weekend_orchestrator.py --output --dry-run             # 周末输出端 dry-run
python3 scripts/weekend_orchestrator.py --reflection --dry-run         # 周末链路反思 dry-run
python3 scripts/proposal_lifecycle.py --orchestrate                    # 手动执行每日编排
python3 scripts/proposal_lifecycle.py --micro-scheduler                # 手动触发微调度器
python3 scripts/proposal_lifecycle.py --repair --dry-run               # 链路修复 dry-run
python3 scripts/lifecycle_monitor.py --dry-run                         # 健康检查（预览，不通知）
python3 scripts/orchestrator.py --dashboard                            # 总控仪表盘
python3 scripts/prompt_optimizer.py analyze                             # Prompt 优化分析
python3 scripts/prompt_optimizer.py auto                                # Prompt 自动优化（cron 入口）
python3 scripts/retrospective.py --period 7d                            # 链路复盘（7 天）
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

**当前基线（v6.9.0）**：
- `--module`：590/590 通过（v6.9.1 新增心跳互查绑定与看板合并写回归；v6.9.2 新增 cron 陈旧检测星期域感知与首跑宽限回归并修正旧用例日期盲区；v6.9.3 新增范例注入可观测性回归；含生命周期 cron、对抗评审、提案 KB 同步、周末任务流水线、章节评审/整体评审、微调度器、轮次完成 break、derived job 优先级、prompt 优化器、看板轮次统计、stale job 回收、monitor 看板时间戳、维度提取修复、质量门槛、MOC 去重修复、标签提取修复、质量天花板收敛/下降检测、维度轮换、输入端熔断（v6.8.53 数据源修复）、审核反馈闭环、KB 健康评分、P0 跨轮持久化、prompt 优化器循环断裂、agent 分数奖惩闭环、nsfc 标准补全、范例注入修复、维度轮换修复、cross-proposal 数据源修复、研究设想质量门槛 idea_review、停滞课题检测修复、退回 idea_review 重触发修复、monitor 降级路径修复、writer 审核反馈注入、同步优化限制、KB 指标持久化、输入端熔断工作日检测、debug journal 压缩、输入端熔断数据源修复、cron 去重默认清单、周末跨周重置按阶段自身时间、告警防线可触发（v6.8.54 KB 四类告警端到端）、cron 拓扑对账（缺失/重复/漂移）、双上限终态自动解锁、error_history 裁剪、智能辅助验收（v6.9.0 验收决策包预审/一键采纳/diff 摘要、负反馈 24h 自愈、最佳轮次自动回退、立项决策包三档建议、策略分级自动应用、待人工队列聚合降噪催办））
- `--scenario`：16/16 通过
- `--persona`：38/38 通过
- `--web-ci`：732/732 通过（全量自动发现 46 个测试套件；Web API 虚拟用户测试覆盖所有主要 API 命名空间；v6.9.0 后持续全绿）

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
- **主导航（v6.8.0）**：仪表盘 / 控制台 / 全链路 / 知识库 / 设置。旧的 hermes / pipeline 页面入口已移除，相关能力并入控制台/全链路。
- **对话式审核（v6.8.0）**：待校验课题在独立 `review-page` 分屏展示（左侧申请书 5 模块 / 右侧讨论 / 底部审核操作），审核会话结束后自动归档。
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

由 `linsai`、`pipeline-runner`、`researcher`、`analyst`、`writer`、`critic`、`reviewer` 7 个 profile 组成。关键协作文件包括 `state_sync.py`（论文状态总线）、`memory_bridge.py`（记忆同步）、`hermes_pipeline.py`（六阶段派活）、`proposal_lifecycle/` 包（四阶段生命周期，薄 shim `proposal_lifecycle.py` 保留 CLI）、`adversarial/` 包（对抗奖惩，薄 shim `adversarial_governance.py` 保留导入）、`weekend_pipeline/` 包（周末输入/输出/反思小任务流水线）。详见 `docs/ARCHITECTURE.md` §4。

### 提案生命周期

四阶段：`drafts → optimizing → pending_review → archived`。v6.8+ 将申请书拆为 5 模块：立项依据（rationale）、研究内容（content）、研究方案含特色创新与预期成果（scheme）、整篇一致性审查（full_review）、参考文献校验（references）。一轮完整优化依次执行：① 三章节并行撰写/评审 → ② 整篇一致性修订 → ③ 参考文献校验/补充 → ④ monitor meta-review。工作日按 4 个时段轮转（00:30-03:30 / 04:00-08:00 / 08:30-12:30 / 18:30-22:30），每个时段聚焦一个 proposal，未完成则下一时段继续，已完成则切换下一个。v6.8.1 新增：失败任务自动重试（attempts < 3）、跨周轮转内容感知（`last_proposal_id` 校准）、系统看板文件（`memory/system-kanban.json`）、每轮优化报告（`05_review/optimization-report-round-N.md`）、**任务系统集成**（微调度器自动同步生命周期状态到 `task_manager`，每个 proposal 轮次自动创建/更新 task，支持 `--sync-lifecycle-tasks` / `--sync-lifecycle-history` CLI 命令和 `POST /api/lifecycle/sync-tasks` / `sync-task-history` Web API）。周末暂停 worker，集中执行输入端（研究设想发现）、输出端（归档知识萃取）与链路反思任务。v6.7.5+ 改为每个 optimizing proposal 一个独立 worker cron；v6.7.6+ 引入 monitor meta-review 与 agent 分数奖惩；v6.7.7+ 增加输入端 `idea_generator`、输出端 `knowledge_output` 与周末模式，并将 `proposal_lifecycle.py` 拆分为 `proposal_lifecycle/` 包。详见 `docs/ARCHITECTURE.md` §5。

### 林赛总控层（v6.7+）

在 hermes 之上新增监控/调优/失败分析/链路成长层，由 `orchestrator.py` 统一入口，整合 `profile_health.py`（profile 健康）、`failure_analyzer.py`（失败模式聚类）、`strategy_optimizer.py`（调度策略建议）。策略仅输出建议，人工确认后写入 `tuning-log.json`。详见 `docs/ARCHITECTURE.md` §6。

### 林赛控制台与设置中心（v6.7.7）

面向用户的统一操作界面：`web_routes_system.py` 提供 `/api/console/*`（流水线/Agent/告警），`web_routes_settings.py` 提供 `/api/settings/*`（7 类配置读写与变更预览）。前端对应 `web/js/console.js` 与 `web/js/settings_center.js`，支持一键触发 repair/orchestrate/optimize/clear-alert。详见 `docs/ARCHITECTURE.md` §7。

### 辅助链路（v6.8.3+）

保障全链路稳定运转的四条辅助链路：

- **健康检查**：`lifecycle_monitor.py`（每小时 cron `lc-hourly-monitor`）检测 cron 缺失/重复/漂移、卡住课题、连续失败、零进展、API 限流，异常去重后飞书通知，cron 异常自动修复；cron 拓扑以 `lifecycle/cron_manifest.py` 为单一真相源（8 个固定 cron 清单 + `validate_cron_topology()` 对账），monitor 启动时清理过期告警缓存条目；`profile_health.py` 计算 7 个 hermes profile 的健康度（单次失败标 degraded，连续 2 次失败才标 blocked）；`failure_analyzer.py` 从日志聚类 8 种失败模式。
- **看板系统**：`memory/system-kanban.json` 由微调度器（主写）和 `lifecycle_monitor`（合并写）协同维护，包含当前时段/聚焦课题/job 进度/执行历史/任务同步统计，前端通过 `/api/console/flow` 展示。
- **定期修复**：`lc-repair` cron 每 6 小时执行 `orchestrator.run_repair()`，重置 stuck running（阈值 1800s）、重试 failed job（最多 3 次）、补齐缺失 worker、清理旧轮次 job（删除前归档至 `research_proposals/_lifecycle_archive.json`，上限 5000 条）；双上限终态 job（attempts≥3 且 repair_attempts≥3）finished 超 24h 后自动解锁重跑一次（`should_auto_unlock`，每 job 限 1 次，`auto_unlock_count` 计数）；error_history 保存时裁剪至 10 条（`trim_error_history`）；微调度器在每次执行前无条件清理 stale job。
- **自成长**：`strategy_optimizer.py` 基于 7 天历史给出调度参数建议（仅建议）；`prompt_optimizer.py`（每日 14:00 cron `lc-prompt-optimize`）从 debug journal/agent scores/failure patterns 生成 prompt 修改建议并自动应用（备份原文件）；`retrospective.py`（每周一 15:00 cron `lc-retrospective`）综合 5 个数据源生成结构化复盘报告。
- **自检测/自成长增强（v6.8.16-v6.8.17）**：① 质量天花板检测（连续 3 轮 ≥0.80 且提升 <2% → 自动晋级 pending_review；连续 3 轮下降 → 暂停）② 停滞课题检测（48h 无进展 → stalled 告警）③ KB 笔记覆盖率检测（sync_all 中实时统计）④ 对抗评审维度轮换（连续 3 轮原地踏步 → 自动切换最弱维度）⑤ 输入端熔断（连续 2 周 ideas=0 → input_pipeline_broken 告警）⑥ 人工审核反馈闭环（审核对话意见自动提取 → critic prompt 注入，避免重蹈覆辙）⑦ KB 健康评分（每周反思时计算覆盖率/新鲜度/连通度）⑧ 研究趋势雷达（sync_all 中分析关键词频率趋势）⑨ Cross-proposal 范例注入（高分课题 ≥0.70 的段落注入低分课题 <0.75 的 writer prompt）。
- **研究设想质量门槛（v6.8.26）**：⑩ idea_review 前置评审（round 1 的 job 链最前端，researcher 对 `00_research_idea.md` 做独立评审，分数 ≥0.70 才允许进入优化；未达标 writer 修复后重审，最多 3 轮）⑪ 结构性缺陷退回（monitor 检测 content/scheme 文件级重复或模块空置 → 设置 `idea_review_required` 标志 → 下一轮自动退回研究设想评审）。
- **多源学术检索（v6.8.42-v6.8.45）**：`external_fetcher.py` 新增 OpenAlex/Semantic Scholar/PubMed/Crossref 检索源与 `search_academic()` 聚合（DOI/arXiv ID/标题三级去重，任一源失败自动降级）；无 key 匿名模式日均 20-50 次检索足够（OpenAlex 无 key 约 100 次/天 + 24h 缓存）。`literature_service` 支持无 arXiv ID 的期刊论文以 DOI 入库（`{year}-doi-{slug}-{title}.md`）；references 校验步骤在 hermes 检索后叠加多源补充，hermes 无结果时多源自动接管。
- **API 故障防线（v6.8.46-v6.8.48）**：`_run_hermes` 对 returncode=0 的输出做 API 错误特征检测（429/配额耗尽/余额不足等 10 种），命中即 success=False，防止 MiniMax Token Plan 耗尽期错误文本被解析成伪分数（实测案例：0.81→0.18 污染）；monitor 解析失败（0.0 非真实分）跳过奖惩不误扣；`_extract_dimension_scores` 对 <300 字符短输出不产生分数。
- **知识库每日治理（v6.8.51 + v6.9.5 + v6.9.6）**：`lc-kb-sync` cron（每日 12:40）执行 `kb_auto_sync.py`（多端同步 + 索引/图谱无条件重建）与 `growth_engine.py --apply`（生长阶段晋升）；`lc-kb-distill` cron（每日 12:50）执行 `kb_distill.py` 批量 raw→wiki 蒸馏（最旧优先 5 篇/天，`pending_distill_list` 清单口径与告警同源、排除 `raw/pdfs/_text_cache/`，产物强制注入纯文件名 `source_raw`，单篇失败跳过不中断批次）——此前 `distill_raw_to_wiki`/`save_distilled_wiki` 接口存在但无流水线生产者，351 项积压零消化，本 cron 补上编排缺失；蒸馏尾部追加 `kb_linker.py --apply`（关键词匹配补 related 边，零 LLM，幂等），治理 graph_connectivity（实测 0.45→0.70）。周日反思阶段（v6.9.6）新增 `reflection_kb_deep_health`（kb_health_weekend 重复概念检测 + derived>30d 降级 + 图谱孤儿清理 + kb_taxonomy 候选提示）与 `reflection_kb_merge_duplicates`（`kb_merger.py` 重复页合并执行器：LLM 融合正文失败降级附录并置、related/tags 边迁移、被并页转重定向 stub，周限 5 对）；`kb_taxonomy.py` 按 tags 频率聚类重建分类体系（clean_tag 清洗 + min_freq=5 + 上限 12，apply 后自动刷新 matched_paths，实测 coverage 0.23→0.70）。写入统一走 `kb_wiki` 门面（防双 frontmatter 污染）；索引格式 v2（扁平 chunk + 整型倒排 + 2-gram，157MB→20MB，两段式检索 + 进程内缓存）；简报同步兼容 `research_briefing_*`/`daily_memory_*` 双命名；`health_sensor` 新增 KB 四类告警（索引停更/生长断流/蒸馏积压/图谱失连）。详见 `docs/ARCHITECTURE.md` 知识库数据流转章节。
- **智能辅助验收与异常自愈（v6.9.0）**：人机分工实测为"执行/修复/治理全自动，仅 3 法定节点（立项激活、验收、策略 apply）+ 2 异常恢复需人"。本层让验收智能辅助、异常自动恢复、等人事项集中可视：① 验收决策包 `review_dossier.py`（pending_review 晋级时自动生成规则预审三档 approve_lean/attention/reject_lean + diff 摘要，审核会话自动注入节选，`POST /api/lifecycle/{id}/review-adopt` 守卫链通过后一键采纳归档，审计 `adopted_via="one_click"`；门槛 REJECT_SCORE_GATE=0.75 与自动晋级线 0.9 分离）② 负反馈 24h 冷却自愈（`should_auto_clear_negative_feedback`，每课题至多 1 次，清除同时降级 `idea_review_required=True`；冷却中不入人工队列降噪）③ 质量退化自动回退（两连降且距最佳 >0.03 → `perform_auto_rollback` 恢复最佳轮次草稿，原稿存 `-pre-rollback.md`，每课题至多 1 次）④ 立项决策包（`idea_generator.recommend_activation` 三档 hold/merge/activate + 可行性启发式，注册时写 `00_idea-dossier.md`）⑤ 策略分级自动应用（白名单 stagger_seconds/score_threshold，单向规则（threshold 只升不降）+ 7 天去重 + 单次上限 2 项 + `confirmed_by="auto:low-risk"`，周复盘后自动应用）⑥ 待人工队列 `human_queue.py`（聚合验收/立项/负反馈三类等人事项，超 72h 催办告警按天数桶去重，持久化 `memory/human-queue.json`，控制台右栏面板 + `GET /api/console/human-queue`）。

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

- **版本号来源**：`VERSION` 文件为唯一真相源（当前 `6.9.6`）。
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
| **产出即资产** | AI 生成的代码、文档、设计、数据均属用户资产，不得擅自处置 |

### Git 操作红线（v6.8.16 新增）

以下操作**永久禁止**在用户工作区直接执行：

| 禁止操作 | 原因 | 替代方案 |
|----------|------|----------|
| `git stash` + `git stash drop` | 临时移除工作区改动，drop 后不可恢复 | 用 `git diff` 对比或复制到临时目录 |
| `git stash pop` 有冲突时 force | 冲突文件会丢失 | 用 `git stash branch` 创建分支恢复 |
| `git reset --hard` | 丢弃所有未提交改动 | 用 `git checkout <file>` 逐文件恢复 |
| `git clean -fd` | 删除未跟踪文件（含知识库数据） | 手动检查后逐个删除 |
| `git checkout .` | 丢弃所有工作区修改 | 逐文件 `git checkout <file>` |
| `rm -rf` 批量删除 | 不可恢复 | 先移到临时目录，确认后再删 |

**根因**：v6.8.15 使用 `git stash` 对比测试基线，`stash pop` 失败后 `stash drop` 导致 v6.8.13-v6.8.14 全部代码改动丢失（8 项功能 + 知识库数据清理回退），耗费大量 token 才恢复。

**正确的心态**：如果需要对比"修改前"和"修改后"的状态，用 `cp -r` 创建临时副本，或用 `git diff` 查看差异——永远不要把用户的工作区当作临时实验场。

### 自动提交规则（v6.8.18 新增）

**用户授权的修改完成后，必须立即 `git add -A && git commit`，不要留在工作区等待用户提醒。**

- commit message 格式：`vX.Y.Z - 简短描述`，附关键改动要点
- 测试通过后即提交，不要积攒多个改动一次性提交
- 用户未明确授权的修改（如探索性实验、临时调试）不自动提交

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

*版本：6.9.6*
*日期：2026-08-15*
*创建者：AI 编码代理*
*上游资产来源：virtu-LinSai v2.7*
