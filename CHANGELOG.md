# 变更记录

## v6.7.7 - 2026-07-28 自动化链路输入/输出端重构 + 周末任务模式

### 问题根因
- 全自动链路只有中段（optimizing 对抗循环），缺少清晰的**输入端**（研究设想从哪里来）和**输出端**（归档后知识如何回流到 KB）。
- worker cron 每天运行，周末也在消耗模型限额，但周末更适合做批量输入发现、输出萃取和链路反思。
- 新研究设想如果直接注册进 optimizing，会跳过人工确认，风险不可控。

### 新增内容
- **输入端：研究设想生成器** — `scripts/idea_generator.py`
  - 自动模式：读取近期文献简报/论文池/已归档讨论，识别研究缺口，生成多个研究设想。
  - 手动模式：接收用户粗略思路，LLM 辅助完善为规范研究设想。
  - 与现有课题对比：标题/核心问题/技术路线相似度 + 是否可融合到已有 proposal 的判定。
  - 新课题自动注册为 `drafts`（不直接进入 optimizing），融合建议写入已有 proposal 的 `扩展建议`。
  - 句子级去重：追加到已有 draft 前去除重复句子，避免内容膨胀。
- **输出端：可靠知识萃取与 KB 生长** — `scripts/knowledge_output.py`
  - 归档 proposal 知识萃取：标题、核心问题、创新点、关键产物、达标章节写入 `knowledge/wiki/projects/NSFC-强场超快/proposals/`。
  - 日常可靠来源萃取：从简报/论文池/归档讨论提取有来源的信息，按 `reliable`/`derived`/`unverified` 三级可信度写入 KB。
  - 禁止污染：无来源或不可靠信息不进入 KB；AI 生成内容标记为 `derived`。
- **周末总控器** — `scripts/weekend_orchestrator.py`
  - 周六上午跑输入端（`weekend-input`），周六下午跑输出端（`weekend-output`），周日上午跑链路反思（`weekend-reflection`）。
  - 维护 `memory/weekend-jobs.json` 任务状态；失败任务由 `lc-repair` 周末扫描重试。
- **周末 KB 健康检查** — `scripts/kb_health_weekend.py`
  - derived 内容过期降级、重复概念检测、unverified claims 汇总报告。
- **Cron 框架改造** — `scripts/lifecycle_cron_framework.py` + `scripts/proposal_lifecycle.py`
  - worker cron 默认 schedule 改为 `Mon-Fri`（`{minute} * * * 1-5`），周末暂停。
  - 新增 `--setup-weekend` / `--teardown-weekend` CLI，自动创建/删除 3 个周末 cron。
  - `run_repair()` 区分工作日与周末：工作日修复 worker/编排，周末修复输入/输出/反思任务。
  - 多个 worker 自动按 proposal_id hash 错开 6 分钟（47/53/59/05/11...）。
- **Web API 扩展** — `scripts/web_routes_system.py`
  - `GET /api/lifecycle/incoming`：列出 drafts/新设想。
  - `POST /api/lifecycle/incoming/register`：从设想注册 draft。
  - `POST /api/lifecycle/incoming/enrich`：将设想融合到已有 proposal。
  - `GET/POST /api/lifecycle/weekend/jobs`：查看/触发周末任务。

### 验证结果
- `python3 -m py_compile scripts/*.py scripts/tests/*.py` 通过
- `python3 scripts/self_test.py --module` 181/181 通过
- `python3 scripts/proposal_lifecycle.py --repair`：5 个 optimizing proposal 的 worker schedule 从 `* * * *` 更新为 `* * * * 1-5`
- `python3 scripts/proposal_lifecycle.py --setup-weekend`：成功创建 3 个周末 cron
  - `lc-weekend-weekend-input`: `0 9 * * 6`
  - `lc-weekend-weekend-output`: `0 14 * * 6`
  - `lc-weekend-weekend-reflection`: `0 9 * * 0`

### 设计原则
- **输入端先草稿后优化**：所有新设想必须先进入 `drafts`，人工确认后再进 `optimizing`。
- **输出端可靠优先**：KB 只接收有可靠来源的知识，AI 生成内容明确降级为 `derived`。
- **周末集中处理批量任务**：工作日专注课题对抗优化，周末做输入发现、输出萃取和链路反思。
- **LLM 失败自动降级**：输入/输出端调用 `llm_gateway`，超时或解析失败时返回空结果，不阻塞链路。

### v6.7.7 代码结构拆分：proposal_lifecycle.py → 包

#### 问题根因
- `scripts/proposal_lifecycle.py` 长达 2625 行，单体文件难以维护。
- 状态管理、命名注册、优化循环、反馈归档、cron 编排等职责耦合在同一类中。

#### 拆分方案
- 新建 `scripts/proposal_lifecycle/` 包：
  - `constants.py` — 常量与默认参数
  - `state.py` — 生命周期状态管理
  - `naming.py` — 课题 ID 命名与校验
  - `registration.py` — 注册 / 从设想导入 / 有机融合
  - `metadata.py` — proposal 元信息提取
  - `transitions.py` — 四阶段流转与仪表盘
  - `optimize.py` — writer-critic 对抗优化循环
  - `completion.py` — 达标判定与自动推进
  - `feedback_archive.py` — 人工反馈 / 归档 / 知识库回流
  - `cron.py` — cron 编排 / 健康检查 / 负反馈告警
  - `cli.py` — 命令行入口
  - `__init__.py` — `ProposalLifecycle` 类聚合所有 mixin
- `scripts/proposal_lifecycle.py` 保留为 6 行薄 shim，向后兼容：`from proposal_lifecycle import ProposalLifecycle, LIFECYCLE_STAGES, main`。
- `scripts/lifecycle/orchestrator.py` 补全缺失的 `HERMES_PROFILE` 导入（修复 `--repair` 在删除 stale worker 时的 `NameError`）。

#### 验证结果
- `python3 -m py_compile scripts/proposal_lifecycle.py` 通过
- `python3 scripts/self_test.py --module` 181/181 通过
- `python3 scripts/proposal_lifecycle.py --dashboard` 正常输出 4 optimizing + 1 pending_review
- `python3 scripts/proposal_lifecycle.py --repair` 4 个真实 proposal 均为 `ok`

### v6.7.7 前端重构：林赛控制台 + 设置中心

#### 问题根因
- 总控层（orchestrator）只有只读仪表盘，缺乏「看状态 → 直接操作」的闭环入口。
- 链路/模板/Agent/任务等关键配置分散在多个 JSON 文件，用户无法在前端统一调整。
- 聊天侧缺少快速查看系统状态或唤起配置的斜杠命令。

#### 新增内容
- **林赛控制台** — `web/js/console.js` + `scripts/web_routes_system.py` `/api/console/*`
  - 流水线视图：`/api/console/flow` 聚合输入端 → drafts → optimizing → pending_review → archived → 输出端六阶段，高亮负反馈告警。
  - Agent 视图：`/api/console/agents` 聚合 profile 健康度与当前 cron 任务，显示运行中/卡住/离线状态。
  - 告警视图：`/api/console/alerts` 汇总负反馈告警、cron 失败、待人工确认的 drafts/设想。
  - 快捷操作：`/api/console/action` 支持 `repair`、`orchestrate`、`optimize`、`clear-alert`、`weekend-input/output/reflection`。
- **设置中心** — `web/js/settings_center.js` + `scripts/web_routes_settings.py` `/api/settings/*`
  - 7 类配置：pipeline、templates、agents、tasks、learning、autonomy、kb_output。
  - 每个分类支持 GET 读取、POST 保存、POST `/preview` 差异预览。
  - 保存前自动备份旧文件到 `memory/.settings-backup/`，失败不覆盖原文件。
- **导航与首页改造** — `web/index.html` + `web/js/dashboard.js`
  - 左侧导航扩展为 6 项：仪表盘、控制台、知识库、课题生命周期、hermes 工作台、设置。
  - 仪表盘瘦身为首页，添加快捷入口卡片和状态概览。
  - 生命周期从弹窗升级为独立页面。
- **聊天斜杠命令** — `web/js/slash_commands.js` + `web/js/chat.js`
  - `/status`：查看当前链路状态。
  - `/config`：快速打开设置中心指定分类。
  - `/template`：查看/编辑 NSFC 模板要求。
  - `/pipeline`：查看流水线或触发编排/修复。
- **核心工具增强** — `web/js/core.js`
  - 新增 `PollService` 统一轮询，控制台/设置中心共享自动刷新与暂停逻辑。
  - 新增 `statusColorClass` / `statusDot` 统一状态着色。

#### 验证结果
- `python3 -m py_compile scripts/*.py scripts/tests/*.py` 通过。
- `python3 scripts/self_test.py --web-ci` 235/235 通过。
- 手动 curl 验证：`/api/settings/categories`、`/api/settings/pipeline`、`/api/settings/pipeline/preview` 返回正常。

### v6.7.7 修复（cron 框架）
- **critic / researcher 步骤超时**：`lifecycle_cron_framework.py` 中 critic 与定向 researcher 的 hermes oneshot 超时仅 300s，实际 critic 需读取申请书全文并输出多维度评审报告，复杂 proposal 频繁超时，导致所有 worker cron 最近状态为 error。已统一延长至 600s（与 writer 一致）。
- **worker schedule 不稳定**：`_compute_worker_minute` 使用 Python 内置 `hash()`，受 `PYTHONHASHSEED` 随机化影响，每次 orchestrator/repair 运行会重新分配分钟，实际观察到 17/35/47/29 等不规律分布。改为 `hashlib.md5` 稳定哈希，确保错开 6 分钟（47/53/59/05/11/17/23/29/35/41）。
- **修复后状态**：清除 5 个 optimizing proposal 的持久化 `worker_minute`，运行 `--repair` 后 worker schedule 已更新为稳定值。

### v6.7.7 修复（LLM 调用）
- **timeout 参数未生效**：`llm_gateway.py` 的 `llm_complete`/`llm_chat` 声明了 `timeout` 参数，但调用 `llm_router.call_llm` 时未传递，导致实际始终使用配置默认 60s，复杂 prompt 易超时。
- **kimi CLI 命令格式错误**：`llm_router.py` 使用 `kimi -c <prompt>`，但 `-c` 在 kimi CLI 中表示"继续上回会话"，应使用 `-p <prompt> --output-format text`。
- **provider 实际使用与 fallback 降级日志缺失**：`llm_router.py` 的 `call_llm()` 在自动策略下未打印最终选中的 provider 及是否发生 fallback，难以排查 cron 中模型调用路径。已增加日志：自动策略打印可用 providers 列表与主模型；每次成功调用后打印 `LLM 路由成功: provider={name}` 并标注主模型、降级或 fallback；强制指定 provider 时同样输出实际使用 provider。
- **新增 Kimi/Moonshot API 支持**：`llm_router.py` 的 `_build_config()` 现在自动读取 `.env` 中的 `KIMI_API_KEY`/`KIMI_MODEL`/`KIMI_BASE_URL`/`KIMI_PRIORITY`，注册为 `kimi-api` provider（与本地 `kimi` CLI 区分），默认模型 `kimi-k2-7-code`、默认 base_url `https://api.moonshot.cn/v1`、默认 priority 3（与 GLM 同级备选，排在 MiniMax 之后）。
- **修复结果**：`idea_generator.py --auto --dry-run` 从"生成 0 个设想/解析失败"变为稳定生成 2 个结构化研究设想；`kimi` CLI 单独调用正常返回。

### v6.7.7 周末任务流水线重构
- **目标**：将大而全的周末任务（`idea_generator --auto`、`knowledge_output --weekly`、`kb_health_weekend`、`weekend_orchestrator --reflection`）拆分为可独立执行、可失败重试、可依赖 Knowledge Base 的小 checkpoint job。
- **新增 `scripts/weekend_pipeline/` 包**：
  - `constants.py`：任务状态、阶段、默认路径、可靠性标签。
  - `state.py`：加载/保存 `memory/weekend-pipeline.json`，记录 `processed_sources`，提供 job 查找/更新 helper。
  - `jobs.py`：定义 input/output/reflection 三阶段的 job 模板与依赖图。
  - `sources.py`：统一收集简报、论文池、captures、参考笔记，并通过 `knowledge_base.list_wiki_pages()`/`search()` 拉取现有 concepts/methods/papers。
  - `pipeline.py`：`WeekendPipeline` 类，提供 `sync_stage_jobs()`、`run_next()`、`run_stage()`、`repair()`。
  - `executor.py`：`pick_next_job()`、job 执行、stale/failed 检测与重试。
  - `input_jobs.py` / `output_jobs.py` / `reflection_jobs.py`：各阶段 job 的具体实现，每个 LLM 调用拆成独立 job。
  - `cli.py` / `scripts/weekend_pipeline.py`：CLI 入口 `--stage/--ensure-jobs/--run-next/--run-all/--list/--repair`。
- **向后兼容**：
  - `idea_generator.py --auto` 委托给 WeekendPipeline input 阶段，`--manual` 保留原行为。
  - `knowledge_output.py --weekly` 委托给 WeekendPipeline output 阶段，`--archive/--daily/--health` 保留原行为。
  - `weekend_orchestrator.py --input/--output/--reflection/--weekly` 调用 `WeekendPipeline` 对应阶段。
  - `kb_health_weekend.py` 保留独立 deep-health wrapper，复用 `knowledge_output.run_kb_health_check` 作为基础检查。
- **生命周期 cron 集成**：
  - `lifecycle/controller.py` 新增 `lc_weekend_worker.sh` 包装脚本，执行 `python3 scripts/weekend_pipeline.py --run-next`。
  - `lifecycle/framework.py` `setup_weekend_crontab()` 保留 input/output/reflection 入口 cron，并新增 `lc-weekend-worker`（`*/20 * * * 6,0`）。
  - `lifecycle/orchestrator.py` `_run_weekend_repair()` 扩展为同时扫描 `memory/weekend-pipeline.json`，处理 stale running 与 failed job 重试。
- **Knowledge Base 联动**：
  - 来源收集阶段读取 KB concepts/methods/papers，避免重复处理。
  - `input_retrieve_supplementary` 优先 `knowledge_base.search()` 检索，复用已有 paper 页面。
  - `input_direction_select` 读取 `knowledge/wiki/projects/NSFC-强场超快/proposals/*.md` 与现有课题对比。
  - `output_sync_proposals_to_kb` 调用 `proposal_kb_sync` 同步全部 proposal。
  - `output_extract_daily_knowledge` 调用 `knowledge_base.check_similar_concepts()`，相似则追加而非新建。
- **验证**：`python3 -m py_compile scripts/weekend_pipeline/*.py` 通过；`python3 scripts/self_test.py --module` 全量通过（198/198）；`python3 scripts/weekend_pipeline.py --stage input --dry-run --ensure-jobs` 可正确创建 input job；`python3 scripts/proposal_lifecycle.py --repair` 对 weekday proposals 仍正常工作。

### 已知限制
- 自动输入端依赖 `llm_gateway` 可用性；若 LLM 连续失败，当次周末输入可能为空。
- 前端 `weekend.js` 尚未实现，当前通过 CLI / API 管理周末任务。

## v6.7.6-fix - 2026-07-28 轮次计数逻辑修复

### 问题根因
- `lifecycle_cron_framework.py` 中 `_run_writer_step` 在 writer 完成后就把
  `optimization_rounds` 推进到当前 round，并立即调用 `sync_checkpoint` 生成下一轮 jobs。
- 这导致一轮完整的 critic → writer → monitor 闭环还没结束，轮次就已经 +1；
  如果 monitor 随后触发负反馈告警，统计上仍显示该轮已完成，造成轮次失真。

### 修复内容
- **writer 不再推进轮次**：仅记录本轮输出质量（`last_score`、`score_history`、
  `section_passes`），不修改 `optimization_rounds`。
- **monitor 作为轮次收尾**：`_run_monitor_step` 成功且未触发负反馈告警时，
  才将 `optimization_rounds` 推进到当前 round，并调用 `sync_checkpoint` 生成下一轮 checkpoint。
- **降级兼容**：若 `adversarial_governance` 未加载，monitor 跳过但仍推进轮次，
  避免链路因模块缺失而僵死。

### 验证结果
- `python3 -m py_compile scripts/*.py` 通过
- `python3 scripts/self_test.py --module` 181/181 通过
- `python3 scripts/proposal_lifecycle.py --repair` 全部 5 个 optimizing proposal 状态正常

## v6.7.6 - 2026-07-28 对抗评审奖惩与监察机制

### 问题根因
- writer-critic 对抗循环只有「critic 评分 → writer 修改」两端，缺乏第三方独立评估，容易出
  现：writer 表面修改、critic 消极/僵化评分、双方串通放水、质量持续走低无法及时发现。

### 新增内容
- **对抗评审奖惩与监察引擎** — `scripts/adversarial_governance.py`
  - `AdversarialGovernance`：管理 writer/critic 全局奖惩分数（初始 100，上限 150，下限 0）。
  - 全局监察员 `monitor`：调用独立 reviewer profile 对每轮修改做 meta-review，输出独立评分
    与 4 维度分数、writer/critic 评估、串通风险、负反馈判定。
  - 上下文敏感禁止清单：writer（占位符、模板僵化、表面修改）、critic（消极评审、僵化评分、
    评分与内容矛盾）由规则层兜底，monitor 可结合质量上下文做最终判定。
  - 奖惩计算：规则层 delta（进度、问题减少、违规扣分、校准奖励/惩罚）与 monitor 建议混合
    （±15 限制）；串通风险 medium/high 额外惩罚。
  - 负反馈检测：monitor 独立分数连续下降 / 本地双降 / 连续串通 / 全局分数低于 50 触发告警。
- **生命周期 cron 接入 monitor 步骤** — `scripts/lifecycle_cron_framework.py`
  - 每轮 checkpoint 拆为 critic → writer → monitor 三个串行小步骤。
  - writer 优化前自动备份当前申请书，供 monitor 比对。
  - monitor 作为每轮收尾：更新 agent 分数、记录 monitor history、判定负反馈；未触发负反馈
    时才检查达标并移入 `pending_review`。
  - worker cron 自动错开：基于 proposal_id hash 分配触发分钟（47/53/59/05/11...），多个
    worker 之间间隔 6 分钟，避免同时触发造成资源争抢；`--repair` 自动更新已有 worker。
- **负反馈告警与清除** — `scripts/proposal_lifecycle.py`
  - `run_health_check()` 新增 `negative_feedback` 告警。
  - CLI/API 支持 `--clear-negative-feedback <proposal_id>` 与
    `POST /api/lifecycle/<id>/clear-alert`，人工确认后恢复链路。
- **Web API / 前端**
  - 新增 `GET /api/lifecycle/agent-scores`、`GET /api/lifecycle/monitor/<id>`、
    `POST /api/lifecycle/<id>/clear-alert`。
  - `web/js/lifecycle.js` 增加 agent scores 概览、课题卡片「监察」按钮、monitor 历史弹窗、
    负反馈告警清除按钮。
- **Proposal 知识库同步**
  - 新增 `scripts/proposal_kb_sync.py`：将 `research_proposals/` 下各课题状态、核心问题、
    创新点、关键产物同步到 `knowledge/wiki/projects/NSFC-强场超快/proposals/`，并生成
    `proposals-index.md` 索引，实现生命周期数据与全链路知识库聚合。
- **测试**
  - 新增 `scripts/tests/test_adversarial_governance.py`（14 个检查点），纳入 `--module` 维度。
  - 新增 `scripts/tests/test_proposal_kb_sync.py`（11 个检查点）。
  - 更新 `test_lifecycle_cron.py` 以适配 critic/writer/monitor 三步骤结构。

### 验证结果
- `python3 -m py_compile scripts/*.py scripts/tests/*.py` 通过
- `python3 scripts/self_test.py --module` 164/164 通过
- `python3 -c "from adversarial_governance import _self_check; print(_self_check())"` 通过

## v6.7.5 - 2026-07-28 生命周期 cron 小型化与自修复框架

### 问题根因
- 原来的每日编排是一个**大而全的单一 cron**：`python3 scripts/proposal_lifecycle.py --daily-orchestrate` 内部串行执行健康检查、文献匹配、多 proposal 多轮 `optimize_cycle`。
- 单点失败会导致当天所有课题优化丢失；critic/writer/researcher 虽然走了不同 profile，但没有在 cron 层显式拆分；无法对单个失败步骤做细粒度修复。

### 新增内容
- **生命周期 cron 框架** — `scripts/lifecycle_cron_framework.py`
  - `LifecycleCronController`：在 `ProposalLifecycle` 之上增加 checkpoint（`pipeline_jobs`）+ worker + repair。
  - 每个 optimizing proposal 拥有独立 worker cron，每次只执行**下一个 pending 小步骤**（critic / researcher / writer）。
  - 每日编排 cron（`lc-daily-orchestrate`）只负责生成 checkpoint 与确保 worker 存在，自身不调用 LLM。
  - 修复 cron（`lc-repair`）每 6 小时扫描一次：重置 stuck running、重试 failed（<3 次）、补齐缺失 worker、超过重试次数则告警。
- **Hermes no-agent cron 支持** — `scripts/hermes_bridge.py`
  - 新增 `cron_list_profile()`、`cron_create_no_agent()`、`cron_delete()`、`cron_delete_by_name_prefix()`。
  - lifecycle cron 统一挂在 `linsai` profile，使用 `--script --no-agent` 模式直接执行本地脚本，不经过 LLM agent。
- **CLI 扩展** — `scripts/proposal_lifecycle.py`
  - 新增 `--worker-step <id>`、`--orchestrate`、`--repair [--dry-run]`、`--setup-cron-v2`、`--teardown-cron-v2`。
- **Web API / 前端**
  - 新增 `GET /api/lifecycle/checkpoints/{id}`、`POST /api/lifecycle/orchestrate`、`POST /api/lifecycle/repair`、`GET /api/lifecycle/jobs`。
  - `web/js/lifecycle.js` 增加 checkpoints 展开、手动编排/修复/查看 cron 按钮。
- **测试**
  - 新增 `scripts/tests/test_lifecycle_cron.py`（19 个检查点），纳入 `--module` 维度。

### 验证结果
- `python3 -m py_compile scripts/*.py scripts/tests/*.py` 通过
- `python3 scripts/self_test.py --module` 135/135 通过（原 116 + 新增 19）

## v6.7.4 - 2026-07-28 修复 critic 超时导致 lifecycle 状态污染

### 问题根因
- `proposal_lifecycle.optimize_cycle()` 中，critic profile 默认 300s 超时；超时返回 `success=False` 后，代码**未检查**该状态，继续执行 writer 并递增 `optimization_rounds`、写入 `score_history`（score=0）。
- 结果：`_lifecycle.json` 记录轮次/分数与实际 `05_review/critic-round-*.md` 文件严重脱节，一致性检查出现 `round_mismatch` / `score_lost` / `round_gap` 等 9 处不一致。

### 修复内容
- `scripts/proposal_lifecycle.py`：在 critic 返回 `success=False` 时提前返回，**不递增轮次、不写 score_history、不调用 writer**，避免状态污染。
- 使用 `scripts/rebuild_lifecycle.py --normalize-rounds` 重建 `_lifecycle.json` 并规范化 critic 文件编号：
  - `general-quantum-geometry-inversion-20260726`: rounds 4→1, last_score 0.0→0.58
  - `key-transient-quantum-phase-optical-20260726`: rounds 5→2, last_score 0.0→0.54
  - `general-bsv-driven-hhg-quantum-20260726`: rounds 5→4, last_score 0.71→0.71
  - `general-order-parameter-ultrafast-readout-20260727`: rounds 4→3, last_score 0.0→0.42

### 验证结果
- `python3 -m py_compile scripts/*.py` 通过
- `python3 scripts/self_test.py --module` 116/116 通过
- `orchestrator.check_lifecycle_consistency()`: inconsistent_count=0

## v6.7.3 - 2026-07-27 导入 hermes workspace 课题雏形并激活全自动链路

### 新增内容
- **Hermes 课题导入脚本** — `scripts/import_hermes_topics.py`
  - 扫描 hermes workspace `research_proposals/2026_NSFG_strongfield_ultrafast/topics/`
  - 将 T1（量子几何）、T2（能谷/莫尔）、T3（能带动力学）、T4（序参量读出）内容映射到标准六阶段目录
  - 注册新 proposal `general-order-parameter-ultrafast-readout-20260727`
  - 充实 BSV 驱动 HHG 申请书（覆盖原占位符草稿）
  - 支持 `--dry-run` / `--import` / `--activate` / `--self-check`

### 数据与链路状态
- 5 个 proposal 全部迁移到 `optimizing` 区：
  - `general-quantum-geometry-inversion-20260726`
  - `general-moire-strong-field-probe-20260726`
  - `key-transient-quantum-phase-optical-20260726`
  - `general-bsv-driven-hhg-quantum-20260726`
  - `general-order-parameter-ultrafast-readout-20260727`
- 已启动 cron sweep（后台 PID 43658）执行每日全模块对抗
- 已配置每日编排 cron：`57 8 * * *`（`pipeline-runner` profile）
- `orchestrator.check_lifecycle_consistency()`：inconsistent_count=0

### 验证结果
- `python3 -m py_compile scripts/*.py` 通过
- `python3 scripts/self_test.py --module` 116/116 通过
- `python3 scripts/import_hermes_topics.py --self-check` 通过

## v6.7.2 - 2026-07-27 链路架构修复（死锁 + 生命周期一致性 + 数据清理）

### 修复内容
- **后台任务锁死锁修复** — `scripts/web_base.py`
  - `_bg_tasks_lock` 由 `threading.Lock()` 改为 `threading.RLock()`
  - 解决 `_save_bg_tasks()` 在 `with _bg_tasks_lock:` 块内被嵌套调用导致的死锁风险
- **生命周期一致性检查增强** — `scripts/orchestrator.py`
  - `check_lifecycle_consistency()` 新增轮次缺口检测（如 [1,3] 缺 2）
  - 新增异常大轮次编号检测（如 round-99）
  - 新增孤儿 proposal 目录检测（含 research_proposals/ 根目录下非阶段目录）
  - `_self_check()` 增加对一致性检查的验证
- **critic 报告轮次规范化工具** — `scripts/rebuild_lifecycle.py`
  - 新增 `detect_round_anomalies()` 扫描轮次异常
  - 新增 `normalize_critic_rounds()` 按 mtime 重命名 critic 文件为连续编号
  - CLI 新增 `--normalize-rounds` / `--normalize-rounds --dry-run`
- **数据清理**
  - 运行 `rebuild_lifecycle.py --normalize-rounds` 修复当前数据：
    - `key-transient-quantum-phase-optical-20260726`: round-3 → round-2
    - `general-moire-strong-field-probe-20260726`: round-3 → round-1
    - `general-bsv-driven-hhg-quantum-20260726`: round-99 → round-1
  - `_lifecycle.json` 已重建，optimization_rounds / score_history 与实际 critic 文件一致
  - 将未注册的遗留空壳 `2026_NSFG_strongfield_ultrafast` 移至 `research_proposals/archived/`

### 验证结果
- `python3 -m py_compile scripts/*.py` 通过
- `python3 scripts/self_test.py --module` 116/116 通过
- `scripts/web_server.py --self-check` / `profile_health.py --self-check` / `orchestrator.py --self-check` / `rebuild_lifecycle.py --self-check` 全部通过
- `check_lifecycle_consistency()` 报告：inconsistent_count=0，仅剩 1 个归档孤儿目录（预期内）

## v6.7.1 - 2026-07-27 生命周期状态一致性修复

### 修复内容
- `scripts/proposal_lifecycle.py`: 移除嵌套锁、增加状态写入校验与重试、critic 返回后等待报告文件稳定、stdout 截断阈值提升至 50KB
- `scripts/web_base.py` + `scripts/web_routes_system.py`: 后台任务状态持久化到 `memory/background-tasks.json`，异常记录到日志
- `scripts/profile_health.py`: 修复 duration_s 解析，匹配 v6.7.1 日志格式
- `scripts/orchestrator.py`: 新增 `check_lifecycle_consistency()` 与 dashboard 集成
- `scripts/rebuild_lifecycle.py`: 新建基于 critic 报告重建 `_lifecycle.json` 的修复工具
- `research_proposals/_lifecycle.json`: 已重建，与实际 critic 报告一致

### 验证结果
- 单元测试 116/116 通过
- 各模块 `--self-check` 通过

## v6.7.0 - 2026-07-27 林赛总控能力（监控 + 调优 + 失败分析 + 链路成长）

### v6.7.0 核心变更
- **林赛总控核心模块** — `scripts/orchestrator.py`（400 行）
  - `compute_dashboard()` — 4 区合一的总仪表盘（profile 健康 + 失败分析 + 策略建议 + 链路质量）
  - `monitor_pipeline()` — 监控所有 proposal 的 6 阶段产物质量 + 自动生成成长建议
  - `apply_strategies()` — 建议模式下应用调度策略（人工确认 + tuning-log 记录）
- **profile 健康度** — `scripts/profile_health.py`（250 行）
  - 读取 hermes_bridge.list_team_profiles()（status / gateway / heartbeat）
  - 解析 linsai.log 最近 24h 派活记录（成功率/平均耗时/最近错误）
  - 派生 4 态：working / idle / blocked / offline
  - 关联 _lifecycle.json 的 cron_failures
- **失败模式分析** — `scripts/failure_analyzer.py`（240 行）
  - 8 个内置模式（score-zero-streak / empty-draft / env-pollution / profile-timeout /
    file-missing / code-bug / rate-limit / low-content-after-rewrite）
  - 每个模式关联：occurrences / 涉及 proposals / 建议 prompt 修改 / 预期效果
  - v6.6.3 的 env-pollution 模式标记为"已修复"
- **调度策略自调优** — `scripts/strategy_optimizer.py`（220 行）
  - 5 条调优规则：高频派活 → +stagger / 频繁超时 → +timeout / 成功率低 → -max_rounds /
    评分低 → -threshold / 评分高 → +threshold
  - 风险分级：low / medium / high
  - 仅建议，不自动应用（人工通过 Web API 确认）
- **Web API 路由** — `scripts/web_routes_orchestrator.py`（220 行，OrchestratorRoutesMixin）
  - 8 条路由：dashboard / profiles/health / failures/patterns / strategies / pipeline/quality（+id）/
    tuning-log / strategies/apply
  - 集成到 web_server.py 的 GET/POST 分派器
- **前端总控台** — `web/js/orchestrator.js`（432 行）+ `web/css/style.css` 新增 orch-* 样式
  - 5 个子面板：总仪表盘 / Profile 健康 / 失败模式 / 调度策略 / 链路质量
  - "应用建议"按钮触发 POST /api/orchestrator/strategies/apply
  - 调优历史从 /api/orchestrator/tuning-log 实时读取
- **设计文档** — `docs/linsai-orchestrator-design.md`（260 行）

### v6.7.0 测试结果
- 4 个新模块 _self_check 全部通过
- 8 条 Web API 路由集成测试通过
- orchestrator.compute_dashboard() 端到端测试：4 区数据全部填充
- profile_health.compute_profile_health()：7 个 profile 全部有状态
- failure_analyzer.analyze_failures()：检测出 3 次"empty-draft"模式
- strategy_optimizer.suggest_strategies()：当前无建议（活动数据不足）
- 0 回归

### v6.7.0 设计原则
- **建议模式** — orchestrator 只输出建议，人工通过 Web API `POST /api/orchestrator/strategies/apply` 确认
- **可观测优先** — 4 区仪表盘是所有调优的起点
- **模式而非规则** — 失败分析用模式聚类（pattern_id + suggested_prompt_change），让用户/AI 决定如何应用
- **链路可成长** — monitor_pipeline 自动给低质量产物生成 growth_actions，提示人工或自动重跑

## v6.6.3 - 2026-07-27 调度关键 bug 修复

### v6.6.3 核心修复
- **TRAE 集成环境导致 hermes 子进程崩溃** — 三大模块的环境清理全部从 `pop("PYTHONHOME")/pop("PYTHONPATH")` 改为 `clean_subprocess_env()`
  - **根因**：TRAE 在 shell 里设了 `PYTHONHOME=.../python@3.13/...`，hermes 用了 venv 内的 python3.11 解释器，被宿主的 PYTHONHOME 误导去 `lib/python3.11/` 找 stdlib，但 hermes venv 只有它自己的版本 → `No module named 'encodings'` → 子进程崩溃
  - **修复**：`scripts/common.py` 新增 `clean_subprocess_env()`，pop 22 个 Python 相关变量（PYTHONHOME/PYTHONPATH/PYTHONIOENCODING/PYTHONUTF8/PYTHONBREAKPOINT/__PYVENV_LAUNCHER__ 等），保留 PATH/HOME/LANG 等必要变量
  - **影响范围**：`proposal_lifecycle.py`（_run_hermes + run_daily_orchestrator）、`hermes_pipeline.py`（_execute_hermes_oneshot + setup_cron）、`hermes_bridge.py`（cron_control + oneshot）
  - **验证**：18:27 之前所有 cron 调用从第 2 轮开始全部失败；修复后 hermes oneshot 100% 跑通（用时 112-655 秒），GLM-5.2 正常返回
- **critic 评分提取正则扩展** — 兼容 GLM-5.2 的简化输出
  - 综合评分正则新增 `综合分`、`overall_score`、`0.07 / 1.00` 等格式
  - 维度分数正则新增 markdown 表格 `| 创新性（innovation） | 0.05 |`、括号别名 `（innovation）` 等格式
- **score_after 优先从 critic 报告文件读取** — `_extract_score` 不再依赖 hermes stdout 摘要
  - hermes stdout 摘要只截取前 8000 字符，常遗漏 critic 写在文件末尾的 `## 评分` 代码块
  - 修复：先读 `critic-round-N.md` 文件内容，文件不存在/空才回退到 stdout 摘要

### v6.6.3 调度验证
- `clean_subprocess_env` 单元测试：6 个变量全部 pop，PATH/HOME 保留
- hermes oneshot 端到端：GLM-5.2 返回 `综合评分：0.10` 等评分内容（之前返回的 stdout 因污染为空）
- 完整 `optimize_cycle` 链路：critic 评审 + writer 优化 + 报告写入全通，elapsed 600s
- 评分提取：用 critic-round-3.md 真实文件（21148 字节）验证能正确提取 score=0.54 + 4 维度分数

## v6.6.2 - 2026-07-27 文献驱动优化体系 + GLM-5.2 升级

### v6.6.2 核心变更
- **文献驱动课题筛选** — `proposal_lifecycle.py` 新增 `match_proposals_with_brief()`
  - 每日编排前，读取最新简报提取关键词，匹配 optimizing 课题
  - 只优化与当天文献相关的课题（非全量扫描），节省模型限额
  - 无命中时 fallback 返回全部课题（保证不空转）
  - 测试：最新简报 45 关键词，命中 3/4 个课题
- **分模块单轮对抗** — `run_cron_sweep` 重构
  - 回退深度连续对抗（避免触顶 GLM Coding Plan 限额）
  - 每课题每天 4 轮（立项依据→研究内容→研究方案→整体审查）
  - 中途达标提前结束，课题间错峰 90 秒
- **达标条件改为全模块胜利（P1-3）** — `_check_done` 重写
  - 4 个模块（3 章节 + 整体审查）全部对抗胜利才算达标
  - 单模块胜利 = 分数达标 + 4 维度无短板
  - 追踪 `section_passes` 状态，未通过模块继续在后续日期优化
- **多维度评分（P0-2）** — critic 输出 4 维度（创新/可行/严谨/完整）
  - 达标需各维度都达到 floor（创新/可行/严谨 ≥0.65，完整 ≥0.60）
  - writer 聚焦最弱维度针对性改进
- **分章节对抗（P1-1）** — critic/writer 按章节轮转聚焦
  - 章节定义：立项依据→研究内容→研究方案→整体审查循环
  - 上下文短，评审更细，修订更聚焦
- **文献定向补充（P1-2）** — 严谨性 <0.70 或有文献缺口时触发 researcher
  - 按缺口检索 2-3 篇近 2 年论文，写入 targeted-research 目录
- **方法学手册联动（P2）** — writer 按章节同步更新方法学手册
- **GLM-5.2 + MiniMax-M3 升级** — 全团队模型升级
  - 6 个 profile（linsai/runner/analyst/writer/critic/reviewer）使用 GLM-5.2（1M 无损上下文，长程任务更稳定）
  - researcher 使用 MiniMax-M3（编码与智能体评测行业顶尖）
  - analyst/writer/reviewer 补充 zai provider 配置
  - 实际 hermes oneshot 测试全部通过

### v6.6.0 核心变更
- **CoPilot 团队 Profile 状态面板** — `hermes_bridge.py` 新增 `list_team_profiles()`
  - 7 个 profile 的网关/cron/心跳/会话状态可视化
  - 后端 API `GET /api/hermes/profiles`
  - 前端 Hermes 工作台新增「团队 Profile 状态」区
- **proposal-brief 贯穿全生命周期** — 自动提取标题/核心问题/创新点
- **CoPilot 生命周期操作台** — 仪表盘四阶段统计 + 课题列表 + 流转/优化/反馈/注册操作
- **修复 5 个规范漏洞** — 撰写按项目类型读模板、register 创建标准目录、自动初始化 brief、强制生成方法学手册、归档纳入知识库

## v6.4.1 - 2026-07-26 Hermes 管线完善：独立 profile + 已有 proposal 导入 + 增量优化 + Web API

### v6.4.1 核心变更
- **pipeline-runner 独立 profile** — 新建 hermes profile 专职管线编排
  - SOUL.md 定义角色：研究管线编排器，协调六阶段，委派给专业 profile
  - config.yaml 复制自 analyst（配置完整），与简报子系统隔离
  - 阶段0 方向校准改由 pipeline-runner 执行（不再占用 linsai）
  - 全自动链路 cron 在 pipeline-runner 上创建，不干扰 linsai 的 4 个简报 cron
- **已有 proposal 导入** — `hermes_pipeline.py` 新增 `import_existing_proposal()`
  - 从 hermes_workspace/research_proposals/ 选择性导入高价值文件（草稿/精读报告/立项依据/课题方向）
  - 按优先级模式筛选：drafts > reports > 立项依据 > candidate_directions > topics > knowledge_base
  - 避免全量复制（日报等历史文件意义不大），默认最多 50 文件
  - 导入元信息记录到 `00_imported/import-meta.json`
  - 测试：从 2026_NSFG_strongfield_ultrafast 成功导入 44 个文件
- **增量优化模式** — `hermes_pipeline.py` 新增 `_build_incremental_context()`
  - 每阶段派活前自动构建上下文：已有产物 + 导入内容 + 上游依赖
  - 产物已存在时提示 agent"先读取理解，再融合最新信息优化，不推倒重来"
  - 导入内容按阶段相关性筛选（方向/论文/缺口/问题/申请书/验收）
  - 上游产物作为本阶段输入自动提示
- **Web API 路由** — `web_routes_pipeline.py` 新增 7 个 hermes 管线路由
  - `GET /api/pipeline/hermes/proposals` — 列出可导入的已有 proposal
  - `GET /api/pipeline/hermes/{id}/status` — hermes 管线状态
  - `GET /api/pipeline/hermes/{id}/check/{stage}` — 阶段产物检查
  - `POST /api/pipeline/hermes/{id}/import` — 导入已有 proposal
  - `POST /api/pipeline/hermes/{id}/dispatch/{stage}` — 派活指定阶段
  - `POST /api/pipeline/hermes/{id}/run` — 一键执行全链路
  - `POST /api/pipeline/hermes/{id}/cron` — 配置 cron 自动触发

### v6.4.1 测试结果
- hermes_pipeline 自检：6/6 通过
- 导入测试：从 2026_NSFG_strongfield_ultrafast 导入 44 文件成功
- 单元回归：116/116 通过
- Web CI 回归：170/170 通过（含新增 7 条 hermes 路由）
- 零回归

### v6.4.1 完整工作流
```
1. 用户创建 proposal：POST /api/pipeline/hermes/nsfc-2026-hhg/import
   → 导入 2026_NSFG_strongfield_ultrafast 的 44 个高价值文件

2. 一键执行：POST /api/pipeline/hermes/nsfc-2026-hhg/run
   → pipeline-runner 协调六阶段，每阶段委派给专业 profile
   → 增量优化：读取已有产物 + 导入内容，融合最新信息
   → 产物检查：每阶段 ≥50 字节才推进

3. 自动化：POST /api/pipeline/hermes/nsfc-2026-hhg/cron
   → 在 pipeline-runner 上创建 cron job（每周一 09:00）
   → 与 linsai 的简报 cron 完全隔离
```

## v6.4.0 - 2026-07-26 Hermes 驱动的管线架构（CoPilot=操作台，hermes=执行端）

### v6.4.0 核心架构变更
- **架构定位重塑** — 从"CoPilot 自己干活"转向"hermes 执行，CoPilot 监控"
  - **此前**：pipeline_orchestrator 在 Python 进程内直接调用模块 + llm_gateway 裸 LLM API
  - **此后**：hermes_pipeline 通过 hermes CLI 派活给 agent profiles（agent loop 自主规划+调工具）
  - **智能升级**：从单次 LLM API 调用 → 完整 agent loop（多轮规划+工具链+自主纠错）
- **新增 hermes_pipeline.py** — Hermes 驱动的研究管线操作台（480 行）
  - `HermesPipeline` 类：将六阶段任务派给对应 hermes profile
  - 阶段→profile 映射：linsai(方向校准) / researcher(文献) / analyst(缺口+问题) / writer(撰写) / reviewer(自检)
  - `dispatch_stage()`：派活给 hermes profile（subprocess 调 `hermes --profile X -z <prompt>`）
  - `check_stage()`：产物文件检查（存在 + ≥50 字节）
  - `run_pipeline()`：一键全链路（依次派活 + 产物检查 + 状态追踪）
  - `setup_cron()`：配置 hermes cron 实现自动化（`hermes cron create`）
  - `dispatch_to_profile()`：直接派活给任意 profile（不限预定义阶段）
  - 状态持久化：`hermes-pipeline-state.json`（阶段状态/派活时间/完成时间/输出预览）
  - 清除 PYTHONHOME/PYTHONPATH 环境变量，避免 hermes venv 冲突
- **agent_team.py 增强** — 每个 agent 新增 `hermes_profile` 字段
  - agent_001 方向校准官 → hermes_profile: linsai
  - agent_002 文献调研员 → hermes_profile: researcher
  - agent_003 课题凝练师 → hermes_profile: analyst
  - agent_004 问题架构师 → hermes_profile: analyst
  - agent_005 申请书撰写员 → hermes_profile: writer
  - agent_006 质量审查官 → hermes_profile: reviewer
  - delegate_module 保留（指向 CoPilot 模块，作为降级回退）

### v6.4.0 Hermes Profile 能力映射
| Profile | SOUL.md 职责 | 管线角色 | agent loop 能力 |
|---------|-------------|---------|----------------|
| linsai | 总控/人格锚点 | 方向校准 | 自主规划+调工具+深度推理 |
| researcher | 搜索/阅读/总结论文 | 文献调研 | web_search + DeepXiv + 结构化输出 |
| analyst | 综合/去重/排名/提炼 | 缺口分析+问题架构 | 综合分析 + 明确结论 |
| writer | 按风格撰写报告 | 申请书撰写 | 逻辑连贯 + 精炼表达 |
| reviewer | 审阅/找错/给建议 | 质量自检 | 严格核查 + 分级标注 |

### v6.4.0 自动化机制
- **hermes cron 驱动**：通过 `setup_cron()` 在 linsai profile 创建定时任务
  - cron 表达式触发 → hermes agent loop 自主执行全链路
  - 产物文件检查保证链路畅通（产物到位才推进下一阶段）
  - 已有 cron 基础：linsai 已运行 4 个 cron job（每日简报/检索入池/推送/健康检查）

### v6.4.0 测试结果
- hermes_pipeline 自检：6/6 通过
- agent_team 自检：全部通过（含 hermes_profile 字段验证）
- 单元回归测试：116/116 通过，零回归

### v6.4.0 架构关系
```
CoPilot 操作台（hermes_pipeline.py）
  ├── dispatch_stage()     → 派活给 hermes profile
  ├── check_artifacts()    → 产物文件检查（≥50字节）
  ├── get_status()         → 实时状态追踪
  └── setup_cron()         → 配置 hermes cron 自动化

hermes 执行端（5 个 profile，agent loop 自主执行）
  ├── linsai profile      → 方向校准（读取画像，校准方向）
  ├── researcher profile  → 文献调研（web_search + DeepXiv）
  ├── analyst profile     → 缺口分析 + 问题架构
  ├── writer profile      → 申请书撰写（NSFC 格式）
  └── reviewer profile    → 质量自检（六维审查）

双引擎共存：
  ├── hermes_pipeline.py  → 主引擎（hermes agent loop，智能上限高）
  └── pipeline_orchestrator.py → 降级引擎（CoPilot 模块 + llm_gateway，离线可用）
```

## v6.3.2 - 2026-07-26 管线关键环节接入 LLM"大脑"

### v6.3.2 核心变更
- **LLM 网关（共享基础设施层）** — 新增 `scripts/llm_gateway.py`（330 行）
  - 定位为「共享基础设施」（同 common.py / paths.py），CoPilot 核心与管线模块均可导入
  - 封装 llm_router 降级策略（MiniMax API → Kimi CLI → Claude CLI），对调用方透明
  - 提供 `llm_complete()` / `llm_chat()` / `safe_llm_complete()` / `llm_json()` 四个接口
  - 永不抛异常：LLM 失败时返回结构化错误，调用方可降级到模板模式
  - `llm_json()` 支持 markdown 代码块包裹的 JSON 解析
  - 解决 AGENTS.md §6 边界隔离下管线模块无法调用 LLM 的设计悖论
- **边界规则更新** — AGENTS.md §6.1/§6.2 将 `llm_gateway.py` 归入共享基础设施层
  - 管线模块允许导入 llm_gateway，但仍禁止直接导入 llm_router
  - llm_gateway 内部导入 llm_router，对外只暴露纯函数
- **选题环节 LLM 增强** — `topic_generator.py` 新增 `_llm_enrich_topic()`
  - LLM 基于研究缺口优化课题标题（体现"现象+机制+方法"）与研究问题（具体、可检验）
  - 输出 JSON 校验：标题长度 ≤80 字、研究问题非空才采纳，否则回退模板
- **科学问题 LLM 增强** — `question_architect.py` 新增 `_llm_enrich_questions()`
  - LLM 批量优化五要素科学问题表述（立项依据/科学问题/研究内容/研究方案/特色与创新）
  - 保留各要素侧重点，输出更具体、可检验、有科学深度的问题
- **申请书撰写 LLM 增强** — `proposal_writer.py` 新增 `_llm_enhance_section()` + 4 章节增强指令
  - 立项依据/研究内容/研究方案/特色与创新：LLM 基于模板草稿重写实质内容
  - 引文占位符保护：LLM 输出若丢失 [CITE:xxx] 则自动降级回模板，保证引用完整性
  - 章节记录新增 `llm_enhanced` / `llm_provider` 元数据字段
- **自检 LLM 语义评审** — `proposal_inspector.py` 新增 `_llm_semantic_review()`
  - LLM 从学术深度/逻辑严密性/创新性/可行性四维语义评审（规则引擎无法覆盖的语义层）
  - 总分融合：规则 0.6 + LLM 0.4，输出优点/不足/改进建议
  - 输出 `score_breakdown` 记录规则分与 LLM 分的融合过程

### v6.3.2 端到端验证（真实 LLM 调用）
- **选题**：LLM 生成标题"量子度规与Berry联络调制固体高次谐波偏振特性的理论研究"（非模板）
- **科学问题**：五要素全部 LLM 优化（JSON 解析偶有失败时自动回退模板，无阻塞）
- **立项依据**：LLM 重写 1162 字实质内容（含物理机制论述、Berry 联络/量子度规专业术语），非占位文本
- **自检**：LLM 语义评审总分 0.412，识别 5 项不足 + 5 条改进建议（如"创新点章节为问题列表非创新陈述"）

### v6.3.2 测试结果
- llm_gateway 自检：5/5 通过
- 边界检查：通过（21 条警告均为静态分析假阳性）
- 单元回归测试：116/116 通过（1.4s），零回归

### v6.3.2 设计原则
- **锦上添花模式**：所有 LLM 增强均支持降级——LLM 成功用 LLM 内容，失败则保留模板输出
- **永不被 LLM 阻塞**：LLM 调用失败/超时/JSON 解析失败时，全部自动回退到规则模式
- **引文完整性保护**：申请书 LLM 重写后校验引文占位符，丢失则降级
- **边界合规**：通过共享基础设施层 llm_gateway 间接调用 LLM，不破坏 §6 隔离原则

### v6.3.2 补充：学术品味 LLM 辅助（taste_engine.py）
- **定性品味评估** — `taste_engine.py` 新增 `llm_qualitative_assessment()`
  - 余弦相似度只能比较数值向量，LLM 从语义层面评估课题与品味的匹配度
  - 输出 match_score / match_reason / 五维逐项 alignment / 改进建议
  - 端到端验证：LLM 评估"量子度规对固体HHG偏振特性的调制"match_score=0.38，给出"过于激进和抽象"的定性判断与具体调整建议
  - LLM 不可用时返回空 dict，调用方降级为纯数值相似度

## v6.3.1 - 2026-07-26 研究管线全链路联通

### v6.3.1 核心变更
- **管线状态机联通执行模块** — `pipeline_orchestrator.py` 新增 `execute_stage()` 方法
  - 实现 6 个阶段专属执行器（`_execute_stage_0` ~ `_execute_stage_5`），将状态机与委托模块打通
  - 阶段 0（方向校准）：读取 `research_profiler` 研究方向画像，生成方向校准报告
  - 阶段 1（文献调研）：读取 `external_fetcher` + `paper_pool` 论文池，汇总文献清单
  - 阶段 2（缺口分析）：调用 `gap_analyzer.analyze_gaps()`，生成缺口报告
  - 阶段 3（科学问题）：调用 `question_architect.build_question_framework()`，构建问题框架
  - 阶段 4（申请书撰写）：调用 `proposal_writer.assemble_proposal()`，组装六章节
  - 阶段 5（自检优化）：调用 `proposal_inspector.inspect_proposal()`，生成自检报告
- **一键全链路执行** — 新增 `run_full_pipeline()` 方法
  - 循环执行 `run_stage()`（执行→门禁→推进）直至完成或失败
  - 安全上限 12 次迭代（6 阶段 × 2 容错），防止死循环
  - 返回完整执行结果链（每阶段的执行/门禁/推进状态）
- **产物自动注册** — 每个阶段执行后自动通过 `artifact_manager` 注册产物
  - 写入实时文件 + 版本快照，支持 diff/回滚
  - 记录 author、stage、content_hash 等元数据

### v6.3.1 测试结果
- **全链路端到端测试**：从阶段 0 执行至阶段 5，6 阶段全部通过
  - 生成 182 个产物（文献清单/缺口报告/问题框架/申请书章节/自检报告等）
  - 门禁检查全部通过，状态机推进正常
- **产出质量验证**：
  - 缺口报告：识别 10 个研究缺口（1 理论 + 9 方法），平均优先级 0.532
  - 自检报告：总分 0.70，检测出 3 个问题（2 重要 + 1 次要），建议定向修复
  - 申请书章节：六章节结构完整，模板拼接可用，待 LLM 集成提升内容质量
- **回归测试**：pipeline_orchestrator 自检通过 + 单元 116/116 + Web CI 170/170，零回归
- **清理**：测试产物目录 `research_proposals/link-test-001/` 保留作为联通验证证据

### v6.3.1 已知限制
- 当前管线为「规则驱动 + 模板拼接」模式，零 LLM 调用
- 申请书内容为模板占位文本，需后续集成 LLM 生成实质内容
- 缺口分析依赖知识库现有数据，无法主动检索外部文献填补缺口
- 自检为格式规则检查，未接入 LLM 语义评估

## v6.3.0 - 2026-07-26 文献 PDF 原文管理

### v6.3.0 新增功能
- **PDF 原文库管理器** — `scripts/pdf_manager.py`（817 行）
  - `PdfLibrary` 类：管理文献 PDF 原文的存储、检索、文本提取与元数据维护
  - 三级来源积累：arXiv 自动下载 / 用户上传 / 工作流产出
  - SHA-256 去重：相同内容 PDF 不重复存储，节省磁盘空间
  - 三级文本提取策略：deepxiv PyPDF2 → 系统 pdftotext → 正则回退
  - 文本缓存：提取后缓存为 .txt，避免重复解析大文件
  - 知识库关联：自动查找已有 wiki 摘要页面并关联，支持手动链接
  - 论文池关联：`list_with_paper_pool()` 合并展示 PDF 原文与简报卡信息
  - 自检 23 项检查点全部通过
- **Web API 路由** — `web_routes_kb.py` 新增 10 个 PDF 管理路由
  - `GET /api/knowledge/pdfs` — 列出所有 PDF（含论文池关联）
  - `GET /api/knowledge/pdfs/stats` — PDF 库统计信息
  - `GET /api/knowledge/pdfs/{id}/info` — 单篇 PDF 元数据
  - `GET /api/knowledge/pdfs/{id}/text` — 提取的全文文本
  - `GET /api/knowledge/pdfs/{id}/download` — 下载 PDF 原文
  - `GET /api/knowledge/pdfs/{id}/summary` — 关联的知识库摘要
  - `POST /api/knowledge/pdfs/upload` — 上传 PDF（base64）
  - `POST /api/knowledge/pdfs/ensure` — 下载 arXiv PDF
  - `POST /api/knowledge/pdfs/{id}/link` — 关联 PDF 与 wiki 摘要
  - `DELETE /api/knowledge/pdfs/{id}` — 删除 PDF 及元数据
- **论文池扩展** — `paper_pool.py` 新增 `has_local_pdf()` / `get_pool_with_pdf_status()`
- **学习引擎集成** — `learning_engine.py` 的 `distill_arxiv_paper()` 蒸馏前自动下载 PDF
  - PDF 全文注入蒸馏 prompt（前 8000 字符），提升精读笔记质量
  - 自动关联 PDF 与生成的 wiki 摘要页面
- **前端 PDF 管理面板** — `web/js/kb.js` 新增 `openPdfManager()` 模态框
  - PDF 列表（含来源/大小/文本缓存/摘要关联状态）
  - 上传 PDF（文件选择器 + base64 编码）
  - 下载 arXiv PDF（输入 ID）
  - 查看/下载/删除操作
  - 全文文本查看 + 知识库摘要查看
- **基础设施** — `paths.py` 新增 `PDF_DIR` / `PDF_LIBRARY_PATH`；`common.py` 新增 `file_sha256()` / `copy_file()`

### v6.3.0 测试结果
- pdf_manager.py 自检：23/23 通过
- paper_pool.py 自检：通过（含 has_local_pdf 验证）
- 单元回归测试：116/116 通过（1.6s）
- Web CI 回归测试：170/170 通过（1.4s），零回归

## v6.2.2 - 2026-07-26 全链路测试验证 + 使用手册

### v6.2.2 测试验证
- **全链路测试**：12 个管线模块自检全部通过（累计 ~150+ 检查点）
- **边界检测**：14 个管线模块零严重违规（21 条警告均为静态分析假阳性）
- **核心回归**：116/116 单元测试通过（1.7s）
- **Web CI 回归**：170/170 测试通过（1.4s），零回归
- **Web API 实测**：54 条管线路由全部正常响应
  - 智能体团队：任务分配/完成/状态流转/性能统计全部验证
  - 方法学手册：生成（3 方法检测）/持久化/Markdown 导出/统计全部验证
  - 管线编排：门禁检查/推进阻塞/暂停/恢复全部验证
- **前端验证**：9 个子面板渲染函数完整确认
- **文档**：新增项目使用手册（HTML 格式），覆盖全部功能模块与操作指南

## v6.2.1 - 2026-07-26 方法学手册 + Agent 团队管理

### v6.2.1 新增模块（2 个 Python + 路由扩展 + 前端扩展）
- **方法学手册** — `methodology_manual.py`：每个课题/申请书配合专门的方法学参考文档
  - 内置 17 种方法数据库（理论 7 + 计算 3 + 实验 4 + 分析 3），每种含理论背景/实现细节/数据分析/局限性四段详细中文描述
  - 从申请书章节自动扫描方法关键词（支持中英文混排空格归一化匹配）
  - 知识库关联（KB 只读检索）、引文关联、Markdown 导出
  - 非内置方法自动生成占位条目供用户丰富
- **Agent 团队管理** — `agent_team.py`：12 个智能体（6 核心 + 4 支撑 + 2 成长槽）
  - 核心管线：方向校准官/文献调研员/课题凝练师/问题架构师/申请书撰写员/质量审查官
  - 支撑团队：品味顾问/血缘记录员/产物管理员/引文管理员
  - 成长槽位：审稿模拟员/实验方案设计师（待激活）
  - 状态机（idle→working→blocked→offline）、性能追踪（成功率/平均耗时/近期任务）、团队扩展（新增/升级/激活）
- **Web 路由扩展** — `web_routes_pipeline.py` 从 39 条扩展到 54 条（+10 Agent + 5 方法学）
- **前端面板扩展** — `pipeline.js` 从 7 个扩展到 9 个子面板（+团队面板+方法学面板）
  - 团队面板：三层结构卡片网格、状态徽章、任务分配/完成/升级/激活/添加成员
  - 方法学面板：左右布局（方法列表+详情）、Markdown 渲染、生成/导出/编辑
- **边界检测更新** — `check_boundary.py` 覆盖 14 个管线模块
- **测试**：methodology_manual 15/15 + agent_team 20/20 + 全量回归 116/116 + Web CI 170/170，零回归

## v6.2.0 - 2026-07-26 研究全链路自动化管线

### v6.2.0 研究管线系统（12 个新模块 + 1 个前端面板）
- **架构**：六阶段管线（方向校准→文献调研→课题凝练→科学问题构建→申请书撰写→自检优化），六道门禁，四波交付
- **Wave 1 基础层**（3 模块）：
  - `artifact_manager.py` — 产物版本管理器：生命周期状态机（draft→in_review→locked→downstream→superseded/archived）、版本快照、diff 对比、回滚
  - `lineage_tracker.py` — 血缘追踪器：双向溯源（上游/下游）、影响分析、BFS 遍历、DOT 导出
  - `taste_engine.py` — 学术品味引擎：五维模型（新颖性/方法论三维/理论深度/跨学科/风险偏好）、WMA 更新算法、余弦相似度匹配
- **Wave 2 调度层**（3 模块）：
  - `pipeline_orchestrator.py` — 管线编排器：六阶段状态机、六道门禁（规则/LLM/用户三类评审）、推进/回滚/暂停/恢复、进度计算、时间线导出
  - `gap_analyzer.py` — 研究缺口分析器：知识库覆盖度扫描、四类缺口识别（概念/方法/理论/实验）、优先级评分、方向对比
  - `citation_manager.py` — 引文管理器：参考文献库、NSFC GB/T 7714 格式化、引文扫描与验证、占位符注入、BibTeX 导出
- **Wave 3 课题层**（3 模块）：
  - `topic_generator.py` — 课题生成器：缺口→课题映射、品味引擎评分（0.35*taste+0.25*novelty+0.20*feasibility+0.20*alignment）、课题演化
  - `question_architect.py` — 科学问题架构师：五要素体系（立项依据/科学问题/研究内容/研究方案/特色与创新）、问题分解、五维验证
  - `proposal_inspector.py` — 申请书自检器：六维检查（逻辑一致性/证据充分性/创新性/可行性/学术规范/表达质量）、四级优化策略、迭代追踪
- **Wave 4 撰写层**（3 模块）：
  - `proposal_writer.py` — 申请书撰写引擎：NSFC 面上项目格式六章节、规则模板组装、品味风格调整、引文占位符注入
  - `web_routes_pipeline.py` — 管线 Web 路由 Mixin（39 路由）：管线编排/缺口/课题/问题/申请书/自检/引文全链路 HTTP API
  - `web/js/pipeline.js` — 管线前端面板：七子面板（概览/缺口/课题/问题/申请书/自检/引文）、六阶段进度条、Markdown 渲染
- **集成**：`web_server.py` 新增 PipelineRoutesMixin 继承（11 个 Mixin）、`_dispatch_pipeline_routes` 分派器
- **测试**：10 个 Python 模块自检全部通过（累计 159 个检查点），全量回归 116/116 单元 + 170/170 Web CI，零回归

## v6.1.0 - 2026-07-25 知识库结构重构 + 界面精简

### v6.1.0 知识库结构重构
- 目录迁移：papers→reviews / 讨论记录→discussions / 论文→analyses / T1-T5→topics
- type 统一：113 个文件复数→单数、管道符→单值
- 图谱重建：116 节点 374 边（从 0 边恢复）
- 模板补充：新增方法/人物/讨论/深度分析 4 个模板
- 索引重建：384 文档

### v6.0.0 界面精简
- 仪表盘首页（dashboard.js）：打开看到今日待处理（文献/任务/决策/hermes状态）
- 3 导航（🏠仪表盘/📚知识库/🔧hermes）替代 8 按钮工具栏
- 删除右侧栏（任务看板+文档引用），知识库预览更宽
- hermes 工作台页面（任务管理+cron+手动派活）
- 后端新增 /api/dashboard 聚合 API

### v5.5.0 统一文献简报
- item-status.json 为单一真相源（Copilot+hermes 共用）
- hermes 推送的论文自动出现在 Copilot，无需手动同步
- pushed/candidate/interested 归入未看组

### v5.4.0-v5.0.0 三端统一架构
- CoPilot 检索引擎索引 hermes wiki
- hermes cron 状态闭环 + kanban 桥接 + 记忆单向同步 + 项目决策同步

## v5.4.0 - 2026-07-19 三端统一架构 阶段5：项目决策同步

### 阶段 5：.copilot-sync.json 项目决策同步
- **CoPilot Web API 新增 2 条路由**（`web_routes_research.py`）：
  - `GET /api/research/projects/{pid}/sync-decisions`：获取项目的同步决策列表
  - `POST /api/research/projects/{pid}/sync-decisions`：创建决策（写入 `.copilot-sync.json`）
  - 复用 `state_sync.py` 已有的 `update_decision_status()` / `load_project_sync()`
  - 路径遍历保护：通过 `pjm._project_dir(pid)` 校验 project_id
- **新建 hermes 消费脚本 `consume_copilot_decisions.py`**（hermes_workspace/knowledge_base/scripts/）：
  - 扫描 CoPilot `projects/*/` 目录下的 `.copilot-sync.json`
  - 发现 `decided_by=copilot` 且未消费的 pending 决策
  - 写回 `consumed_by_hermes_at` + `consumed_by=hermes` + `last_hermes_update` 时间戳
  - 采用"只标记消费时间戳，不改变 status"策略，避免与 CoPilot 的 status 流转冲突
  - 原子写入：`tempfile.mkstemp` + `f.flush()` + `os.fsync(f.fileno())` + `os.replace`
  - `--dry-run` 模式 + `_self_check()` 5/5 通过
- **端到端链路测试**（`test_stage5_flow.py`）：
  - CoPilot 创建决策 → `.copilot-sync.json`
  - hermes 扫描 → 发现 pending 决策
  - hermes 消费 → 写回 `consumed_by_hermes_at`
  - CoPilot 读取 → 验证状态已回传
  - 幂等性验证：已消费决策不再重复处理
- **测试**：核心 116/116 + 全量 240/240（无回归）

### 变更文件
- `scripts/web_routes_research.py`（新增 2 条路由 + 2 个 handler）
- `docs/v5-three-tier-unification-plan.md`（Stage 5 标记完成 + 完成总结）
- hermes 侧：`knowledge_base/scripts/consume_copilot_decisions.py`（新建）

## v5.3.0 - 2026-07-19 三端统一架构 阶段4：记忆单向同步

### 阶段 4：memory_bridge 记忆单向同步
- **新建 memory_bridge.py**：hermes → CoPilot 记忆单向同步
  - 读取 hermes linsai profile 的 MEMORY.md（3064B）+ USER.md（2704B）
  - 原文快照保存到 `memory/hermes-memory-snapshot.json`（含 mtime + 同步时间）
  - 关键词提取（预定义研究关键词库匹配）→ 合并到 `user-profile.json` 的 research_field
  - 增量跳过：文件 mtime 未变时跳过同步
  - `get_hermes_memory_text()` 供 context_builder 注入 prompt
- **集成 sync_engine.py**：sync_all() 新增 `[5/5]` 记忆同步步骤
- **路径修正**：hermes 实际在 `~/.hermes`（非 paths.py 中的旧版 `~/.kimi`）
- **测试**：_self_check 5/5 + 核心 116/116（无回归）

### 变更文件
- `scripts/memory_bridge.py`（新建）
- `scripts/sync_engine.py`（sync_all 新增 [5/5] 步骤）

## v5.2.0 - 2026-07-19 三端统一架构 阶段3：任务看板桥接

### 阶段 3：kanban_reader + 任务看板桥接
- **新建 kanban_reader.py**：hermes kanban.db SQLite 读写层
  - 只读连接用 `PRAGMA query_only=ON`（WAL 模式无法用 mode=ro）
  - 写入连接用 WAL + `busy_timeout=5000`，与 hermes worker 并发安全
  - 状态映射：hermes 9 态 → CoPilot 4 态（triage/todo/scheduled/ready→backlog, running/review→active, blocked→paused, done/archived→completed）
  - 逆向映射：CoPilot 4 态 → hermes（backlog→todo, active→running, paused→blocked, completed→done）
  - `list_tasks()` / `get_task()` / `create_task()` / `update_task_status()` 四个接口
  - `_self_check()` 6/6 通过（读取真实 kanban.db 22 任务，11 非归档）
- **改造 web_routes_tasks.py**：
  - `_task_list`：合并 hermes kanban + 本地任务，添加 `source` 字段
  - `_task_get`：`t_` 前缀路由到 kanban_reader，`TASK-` 前缀路由到 task_manager
  - `_task_create`：assignee=hermes 时写入 kanban.db（created_by="copilot"）
  - `_task_update`：kanban 任务状态更新写入 kanban.db
- **改造 task.js**：来源标签（紫色 hermes badge）+ hermes assignee 显示
- **新增 CSS**：`.task-source-badge.hermes` 样式
- **测试**：Web API 返回 14 任务（11 hermes + 3 本地）+ 核心 116/116 + Web API 70/70（无回归）

### 变更文件
- `scripts/kanban_reader.py`（新建）
- `scripts/web_routes_tasks.py`（4 个路由方法集成 kanban）
- `web/js/task.js`（来源标签 + assignee 显示）
- `web/css/style.css`（.task-source-badge 样式）

## v5.1.0 - 2026-07-19 三端统一架构 阶段2：hermes cron 状态闭环

### 阶段 2：hermes cron 消费 item-status.json
- **新建 hermes 端共享模块**：`item_status_helper.py`（hermes_workspace/knowledge_base/scripts/），与 CoPilot `state_sync.py` 共用 `/tmp/linsai-copilot-item-status.lock` 锁文件，确保跨进程安全
- **修复 v4.2 并发安全隐患**：`select_candidates.py` 的 item-status.json 读写从无锁 json 模块改为通过 helper 的 fcntl 锁保护
- **深度分析状态同步**（v5.0 新增）：`mark_deep_analyzed.py` 分析完成后调用 `update_item_status(status="interested")`，CoPilot 可感知 hermes 已深度分析的论文
- **归档状态同步**（v5.0 新增）：`archive_discussion.py` 归档成功后调用 `update_item_status(status="archived", discussion_path=...)`，CoPilot 看板可同步归档状态
- **只升不降规则**：hermes 端与 CoPilot 端使用完全一致的 STATUS_ORDER + 只升不降逻辑，避免状态回退
- **测试**：helper 自检 5/5 + 三个脚本功能验证 + CoPilot 核心测试 116/116 + Web API 70/70（无回归）

### 变更文件（hermes 端，原文件备份在 .v5-backup-20260719/）
- `knowledge_base/scripts/item_status_helper.py`（新建）
- `knowledge_base/scripts/select_candidates.py`（改用 helper，加 fcntl 锁）
- `knowledge_base/scripts/mark_deep_analyzed.py`（新增 item-status → interested 同步）
- `knowledge_base/scripts/archive_discussion.py`（新增 item-status → archived 同步）

## v5.0.0 - 2026-07-19 三端统一架构 P0：路径修复 + 跨进程锁

### 阶段 1：CoPilot 检索引擎索引 hermes wiki
- **跨库检索**：`kb_index.build_index()` 新增 `extra_wiki_dirs` 参数，默认索引 hermes `AI_wiki/02-wiki/`（69 篇结构化 wiki）
- **frontmatter 兼容**：hermes wiki 缺失 `growth_stage` 时默认 `"growing"`，`summary`/`description` 纳入索引文本
- **搜索加权**：`source="hermes-wiki"` 与 `"wiki"` 同等享受 1.2× 加权，`doc_type` 过滤支持 `hermes-wiki/` 前缀
- **前端来源标签**：搜索结果展示紫色 `hermes` / 绿色 `wiki` 徽章，`file-content` API 支持 hermes-wiki 路径只读访问
- **路径遍历防护**：hermes-wiki 文件读取含 `resolve().relative_to()` 安全检查
- **测试**：`kb_index._self_check()` 5→6 检查点（新增外部 wiki 索引验证），全量 186/186 通过

### P0：briefing_sync 路径错配修复 + fcntl 跨进程锁
- **修复 v4.1 重大 bug**：`briefing_sync.py` 的 `HERMES_STATUS_PATH` 指向从未存在的 `status.json`，导致 v4.1 双向同步完全失效
- **委托 state_sync**：briefing_sync 不再维护独立路径，直接委托 `state_sync.update_item_status()` / `_load_item_status()` 读写共享的 `item-status.json`
- **状态映射重构**：基于 item-status.json 的 9 级状态枚举（pool→archived），替代旧版的时间戳字段推断
- **跨进程锁**：`common.py` 新增 `file_lock(lock_name)` 上下文管理器（fcntl.flock 独占锁），保护 CoPilot web_server 与 hermes cron 的并发写
- **state_sync 加锁**：`update_item_status` / `initialize_from_existing` 的 read-modify-write 临界区使用 `file_lock("item-status")` 保护
- **测试扩展**：BriefingSyncTests 从 20→28 检查点（新增 `_test_new_paper_register`），全量 240/240 通过

### 变更文件
- `scripts/common.py`：新增 `file_lock()` fcntl 上下文管理器
- `scripts/state_sync.py`：`update_item_status` / `initialize_from_existing` 加锁
- `scripts/briefing_sync.py`：v5.0 完整重构（移除 HERMES_STATUS_PATH，委托 state_sync）
- `scripts/tests/test_core.py`：BriefingSyncTests 适配 item-status.json schema

## v4.2.2 - 2026-07-17 统一状态同步 + 文献独立讨论 + AI辅助指派 + 清理

### 统一状态同步架构（Copilot = hermes 操作台）
- **state_sync.py**（410行）：统一论文状态（item-status.json），Copilot 和 hermes 共用
- 9种状态枚举（pool→archived），不可逆状态优先
- Copilot 操作（感兴趣/归档/跳过）→ 实时写回 item-status.json
- hermes select_candidates.py 改造：检索跳过已处理论文 + 推送标记 pushed
- NSFC 决策同步写 .copilot-sync.json（hermes BRAIN 可读）
- 前端文献卡片显示 📡已推送飞书标记

### 文献独立讨论窗口（v4.1）
- 大弹窗模式：论文信息+讨论区+检索面板（双栏）
- 检索增强：本地知识库优先，deepxiv 检索兜底
- 归档链路：全文→整理→凝练→概念（全自动+半自动）
- 归档产出：讨论记录.md + 概念 seedling 笔记

### AI 辅助任务指派
- 只说目标+要求，AI 自动生成任务描述 + hermes 执行指令
- 自动填充表单（标题/描述/优先级/hermes prompt）

### 清理
- 删除空壳配置（llm-config.json）
- 归档4篇 cron 机器日志讨论（JSON 混入正文）
- 归档已执行完的计划文档
- 清理旧日志（>7天）

## v4.1.0 - 2026-07-02 文献简报双向同步引擎

### 核心特性：CoPilot ↔ hermes 状态双向同步

此前 CoPilot 与 hermes 的文献简报状态完全隔离（CoPilot 在 `paper-pool.json`，hermes 在 `status.json`），用户在 Web 界面标记的"感兴趣/归档"等操作不会同步到 hermes 工作流，反之亦然。本次实现双向同步，打通两端状态。

### 新增文件
- **`scripts/briefing_sync.py`**（417 行）：双向同步引擎
  - `sync_to_hermes()`：反向同步（CoPilot→hermes），用户操作时实时回写 hermes `status.json`
  - `sync_from_hermes()`：正向同步（hermes→CoPilot），`sync_all()` 执行时批量拉取 hermes 工作流状态
  - `flush_pending_reverse()`：待同步队列重试（max 5 次），处理 hermes 未运行时的失败请求
  - 状态映射：`viewed → discussion_started=true`，`archived → discussion_archived_at=<时间戳>`
  - 只升不降规则：`unseen(0) → viewed(1) → archived(2)` 单向流转
  - 冲突策略：CoPilot 优先（用户意图 > hermes 自动流程）
  - 文件锁 + 原子写入，线程安全

### 修改文件
- **`scripts/paper_pool.py`**：新增 `get_paper_status(arxiv_id)` 函数，供正向同步查询当前状态
- **`scripts/sync_engine.py`**：`sync_all()` 新增 `[0/5] flush_pending_reverse()`（前置重试）+ `[2.5/5] sync_from_hermes()`（正向同步），自检新增 briefing_sync 就绪检查
- **`scripts/web_routes_projects.py`**：`_proj_papers_feedback` 在 `pp.update_status()` 后调用 `bsync.sync_to_hermes()`，失败不阻塞用户操作
- **`scripts/tests/test_core.py`**：新增 `BriefingSyncTests`（20 个检查点），覆盖状态升级判断、反向同步、待同步队列、重试、正向同步、幂等性

### 验证
- `briefing_sync._self_check()`：5/5 通过
- `self_test --module`：108/108 通过（含新增 20 个 BriefingSync 测试）
- `self_test --web-ci`：232/232 通过

## v4.0.0 - 2026-07-01 认知层清洗 + 记忆去重防护

### 阶段1：数据清洗（让记忆可信）
- **snippets 去重**：26条→5条高质量记忆（删除16条重复+碎片）
  - 7组重复（"飞书消息限制"重复7次、"达标文章"重复5次等）全部合并
  - 碎片（"？请从物理机制出发解释"等半句话）移除
- **pending_decisions 清洗**：3条→2条（移除碎片）
- **key_insights 清洗**：12条→9条（移除纯路径记录/工程操作日志）
- **语义级去重**：同主题变体合并（飞书限制4种表述→1条）

### 阶段2：对话体验确认（已在v3.4实现，无需重做）
确认以下功能在v3.4已完整实现且正常工作：
- ✅ 知识库命中可视化（chat.js消费kb_hits metadata，气泡底部显示引用来源）
- ✅ 浅输入人格锚定（_is_small_talk + _build_persona_anchor）
- ✅ 开场即主动（heartbeat→injectProactiveOpening，会话首加载注入主动消息）
- ✅ 记忆引用（snippets注入system_prompt）

### 阶段3：记忆提取去重防护（防止未来再产垃圾）
- **memory_reflow.py 增加 snippet 去重**：写入前检查前60字符相似度，已有则跳过
- **质量过滤**：<20字的碎片不写入
- **决策去重**：pending_decisions 也加前40字符去重
- 验证：模拟重复写入测试通过（重复跳过、新内容写入）

### 验证
- self_test 142/142 + web_api 70/70 全绿
- snippets 5条0重复，去重逻辑验证通过

## v3.6.0 - 2026-06-28 知识库分区策略 + 基础设施增强

### 知识库分区策略（核心特性）
- **后端分区检索**：`kb_index.py search()` 新增 `doc_type`/`tag`/`stage`/`offset` 参数，支持五维分区过滤（source/project/type/tag/stage）+ 分页，返回 `{results, total, offset, limit}` 字典格式
- **API 暴露分区参数**：`GET /api/knowledge/search` 支持 `project`/`type`/`tag`/`stage`/`offset` 查询参数（原仅 `q`/`top_k`/`source`）
- **项目感知检索**：`context_builder.py` 会话关联课题时，全局 KB 检索自动传入 `project_id` 过滤，优先返回课题相关知识；不足时补充全局检索
- **课题 KB 分页**：`project_kb.py search()` 增加 `offset` 参数，返回字典格式
- **前端统一搜索+筛选**：`kb.js` 搜索与筛选下拉框联动，搜索时自动携带当前筛选条件
- **前端分页控件**：搜索结果底部显示页码导航（上一页/页码窗口/下一页），支持键盘可达
- **前端分区选择器**：知识库管理器顶部新增 6 选项分区下拉框（全部/课题库/论文库/概念库/方法库/学者库），一键切换检索范围

### captures/ 空目录修复
- **根因**：`kb_capture.capture_from_session()` 只在 CLI 模式调用，Web SSE 流程未接入
- **修复**：`web_base.py _update_memory_async()` 中接入 capture 调用，Web 流程与 CLI 一致

### paths.py 迁移收尾
- 28 个文件（23 个 scripts/ 直接子文件 + 5 个子目录文件）全部改为 `from paths import PROJECT_ROOT, ...`
- `scripts/` 目录下已无任何 `PROJECT_ROOT = Path(__file__)` 遗留定义

### 健康检查端点
- 新增 `GET /api/health`：聚合版本号、LLM Provider 状态、知识库统计、关键目录可访问性，返回 `ok`/`degraded`

### 日志与配置
- `logger.py` 日志保留天数 14→30 天
- `.gitignore` 新增 `knowledge/.obsidian/`，取消追踪 4 个 Obsidian 配置文件

### 测试扩展（141+211）
- 单元测试 137→141（+4：kb_index search 字典格式、project_kb search 分页）
- Web API 测试 207→211（+4：分区参数透传、分页返回格式）

## v3.5.9 - 2026-06-28 冗余内容清理

### 后端死代码清理
- **删除 version.py**：经确认完全未被任何文件 import，upgrade.py 自行实现了 read_version()
- **合并 _safe_filename**：kb_text.py/kb_capture.py 的本地定义改为从 common.py 导入
- **合并 _STOPWORDS**：kb_text.py（权威版）、research_profiler.py、project_kb.py 三处重复定义合并为 kb_text 统一导出
- **修正 fetch_wikipedia 弃用标注**：learning_engine.py 仍在调用，移除"【已弃用】"标记

### 前端死代码清理
- **删除 ~230 行死 CSS**：19 类未使用规则（旧 KB 列表/健康/统计视图、旧任务优先级徽标、旧进度条、旧技能行等）
- **删除 2 个死 JS 函数**：settings.js switchProvider()、skill.js getSelectedSkillNames()
- **移除死 HTML 元素**：context-info/context-panel 从未被 JS 引用
- **修复 skill-count ID 不匹配 bug**：skill.js 查找 'skill-count' 但 HTML 定义 'skill-active-count'，技能激活计数从不更新

### 数据残留清理
- 删除 3 个空测试会话目录（messages.json 为空）
- 删除 2 对重复 backlog 任务文件
- 清理 graph.json 中 2 个孤儿节点（测试概念/门面测试）和 1 条关联边
- git rm --cached knowledge/raw/checkpoint.json（.gitignore 已忽略但仍被追踪）
- 删除 59 个 __pycache__ 缓存文件
- 删除空 sessions/archived/ 目录、1 个旧备份、6 个旧日志

### 文档清理
- 归档 stability-ux-plan.md、kb-smart-management-plan.md 到 docs/archive/
- 更新 4 个 README：版本号 3.5.0→3.5.8、统计数据修正（论文 61→106、图谱 27→141 节点）、路径修正（solid-HHG 从 docs/ 到 raw/notes/）、删除不存在的文件引用（version.py/learning_quality_tracker.py）、行数修正（web_server.py 2544→321、knowledge_base.py 1780→534）

### 验证
- 137/137 单元测试 + 207/207 Web API 测试全量通过

## v3.5.8 - 2026-06-28 第三轮安全修复与质量优化

### P0 灾难性漏洞修复
- **project_manager 路径遍历**：新增 `_validate_project_id()` 安全校验，`DELETE /api/research/projects/..` 不再能删除项目目录
- **unit_manager 路径遍历**：新增 `_validate_unit_id()` 安全校验
- **_send_static 路径遍历**：`GET /web/../../.ssh/id_rsa` 不再能读取任意文件，改用 `_safe_join`
- **research 路由统一安全捕获**：`_dispatch_research_routes` 添加 ValueError 捕获，非法 ID 返回 400

### P1 后端安全
- **文件锁保护**：kb_graph/task_manager/project_manager/unit_manager 的读-改-写操作全部加锁，防止并发丢更新
- **tool_engine 导入清理**：5 处 `importlib.util` 动态导入改为静态 import
- **wiki 删除顺序修复**：先读取 title 再 rename，图谱节点正确清理

### P1 前端安全
- **escapeAttr 函数**：`core.js` 新增 `escapeAttr()` 转义单引号+双引号，专门用于 onclick 属性
- **onclick 注入全面修复**：hermes_console.js(3处)、task.js(1处)、projects.js(14处)、research.js(24处) 共 42 处内联事件处理器修复
- **kb.js escapeHtml 补全**：6 处 innerHTML 注入点补全转义
- **CSS 重复选择器合并**：.drawer-overlay/.chat-archive-header/.kb-list-item 3 个重复块合并

### P1 测试扩展（137+207）
- `test_core.py` 新增 `SecurityTests` 类（8 检查点：_safe_join 路径遍历 + save_json 原子写入）
- `test_web_api.py` 新增 5 个测试方法（28 检查点：research/tasks/skills/system/kb 路由）
- 路由覆盖率 18%→26%（42/160 唯一路由）

### P1 文档修正
- AGENTS.md "每个核心脚本包含 _self_check()" 虚假声明修正
- test_core.py 检查点数修正（34→83）
- --web-ci 检查点数补充标注（207）

### P2 代码质量
- `_bg_tasks` 内存泄漏修复：新增 `_prune_bg_tasks()` 自动清理已完成超 1 小时的任务
- `projects.js`(6处)/`research.js`(3处) async 函数补充 try-catch
- `session.js`/`chat.js` null 检查补全
- CSS 硬编码 `#c9a227` 改为 `var(--warning-color)`
- 浅色主题 `--text-tertiary` 对比度修复（#888→#6b6b，满足 WCAG AA 4.5:1）

### P3 优化
- `web_routes_hermes.py` 新增服务端最大 timeout 上限（600s）
- `kb_graph.py` _self_check 缓存重置
- `app.js` debounce 绑定添加可选链
- pycache 清理

### 验证结果
- 单元测试：137/137 通过（1.154s）
- Web API 测试：207/207 通过（2.903s）

## v3.5.7 - 2026-06-28 全面安全修复与质量优化

### P0 安全修复
- **hermes 线程安全**：`web_routes_hermes.py` 后台线程直接写 `wfile` 改为 `queue.Queue` 模式，主线程负责所有 SSE 写入，避免 `BrokenPipeError` 和数据损坏
- **路径遍历漏洞**：新增 `web_base._safe_join()` 通用路径安全函数，修复 `web_routes_kb.py`（wiki_rel）、`web_routes_sessions.py`（session_id）、`web_routes_upload.py`（category）三处路径遍历，防止任意文件读取/删除

### P1 安全与质量
- **原子化写入**：10+ 处 `json.dump` 迁移到 `common.save_json`（原子写入），覆盖用户消息、别名映射、知识图谱、索引、用量追踪、LLM 配置、技能配置、归档索引
- **JSON 解析容错**：`web_base._read_json_body` 添加异常处理，损坏 JSON 返回空字典而非 500 错误
- **前端 XSS 修复**：`kb.js` frontmatter 的 tags/wikiPath/error 均补充 `escapeHtml` 转义
- **onclick 注入修复**：`kb.js` 路径参数改用 `data-*` 属性 + 事件委托，替代脆弱的单引号替换
- **CSS 重复定义**：删除 `.btn-primary` 第 2353 行重复定义
- **chat.js null 安全**：12 处 `getElementById().value/.style` 添加可选链或 null 守卫
- **debounce 提取**：`core.js` 新增通用 `debounce()` 函数，`app.js` 3 处手动防抖替换

### P1 测试扩展（120→129 + 146→171）
- 新增 6 个模块 `_self_check()`：kb_text(5) + kb_graph(5) + kb_index(5) + kb_wiki(5) + kb_health(5) + web_base(4) = 29 个检查点
- `test_core.py` 新增 `KbSubmoduleTests` 类（9 个检查点）
- `test_web_api.py` 新增 16 个路由测试断言（research/learning/upload/system/kb），覆盖率 17.5%→26.3%

### P1 文档修正
- AGENTS.md 路由数修正（130→160）、memory/ 目录补全（5→17 个文件）、knowledge/ 目录补全（categories.json + .cache/）
- CHANGELOG 补录内联样式清理（426/554，v3.5.4 延后项）
- `web_server.py` self-check 路由阈值提升（80→120）
- `index.html` 10 个按钮补充 `aria-label`

### P2 代码质量
- `copilot_engine.py`：6 处 `importlib.util` 动态导入改为静态 `import`，保留 `try/except ImportError` 降级
- `kb_graph.py`：`_load_graph` 添加 mtime 缓存，避免频繁磁盘 I/O
- `web_routes_research.py`：路由表预编译正则，与其他 9 个路由模块一致
- `web_routes_projects.py`：删除 7 处函数内重复导入
- `kb_health.py`：函数内导入提到模块级
- `knowledge_base.py`：`distill_raw_to_wiki` 返回类型标注修正
- CSS 语义色提取为变量（badge/priority），删除 8 处深色模式重复覆盖

### 验证结果
- 单元测试：129/129 通过（1.144s）
- Web API 测试：171/171 通过（2.109s）
- 语法验证：全部通过

## v3.5.6 - 2026-06-28 web_server.py Mixin 架构拆分（10 路由 Mixin + 1 基础模块）

### 架构重构：Web 服务器模块化

将 `scripts/web_server.py`（2576 行）按业务域物理拆分为 11 个子模块，原文件瘦身为 321 行聚合器（87.5% 缩减），使用 Mixin 模式确保零破坏性。

**新增子模块**：
- `scripts/web_base.py` — 共享基础设施：全局状态（`_file_locks`/`_kb_busy`/`_bg_tasks`）、工具函数（`_get_file_lock`/`split_response_stream`/`_update_memory_async`）、`BaseRequestHandler` 基类（`_send_json`/`_send_sse`/`_send_static`/`_read_json_body`）
- `scripts/web_routes_sessions.py` — 会话/消息路由（9 条）：`SessionRoutesMixin`，含 SSE 流式输出、`_edit_message`/`_delete_message` 模块级函数
- `scripts/web_routes_tasks.py` — 任务路由（8 条）：`TaskRoutesMixin`，含 `_do_dispatch_hermes` 方法
- `scripts/web_routes_kb.py` — 知识库路由（33 条）：`KbRoutesMixin`，18 GET + 14 POST + 1 DELETE
- `scripts/web_routes_system.py` — 系统状态路由（19 条）：`SystemRoutesMixin`，版本/心跳/LLM状态/Provider/用量/同步/备份
- `scripts/web_routes_skills.py` — 技能路由（5 条）：`SkillRoutesMixin`
- `scripts/web_routes_learning.py` — 学习路由（7 条）：`LearningRoutesMixin`，lazy_load 延迟导入
- `scripts/web_routes_projects.py` — 项目/NSFC/论文池路由（33 条）：`ProjectRoutesMixin`，含 `_write_dispatch_to_hermes_plans`/`_dispatch_hermes_async` 模块级函数
- `scripts/web_routes_hermes.py` — Hermes 路由（4 条）：`HermesRoutesMixin`，修复 `_send_sse_raw` 未定义 bug
- `scripts/web_routes_upload.py` — 上传/文件路由（5 条）：`UploadRoutesMixin`，含 `_handle_upload`/`_list_references` 模块级函数
- `scripts/web_routes_research.py` — 课题指导模块路由（37 条）：`ResearchRoutesMixin`，整体迁移自原 `_RESEARCH_ROUTES` + 37 个 `_rg_*` handler + 独立分派器

### 关键设计决策

- **Mixin 模式**：每个域创建一个 Mixin 类，提供路由表和 handler 方法。`RequestHandler` 继承所有 Mixin + `BaseRequestHandler` + `BaseHTTPRequestHandler`。`do_GET`/`do_POST`/`do_PUT`/`do_DELETE` 依次调用各路由表的 `_dispatch_all` 方法。
- **统一路由表格式**：`(HTTP方法, re.compile(正则), handler名)`，handler 签名 `GET/DELETE → (self, parsed, body=None, **path_params)` / `POST/PUT → (self, parsed, body, **path_params)`，正则使用命名捕获组提取路径参数。
- **课题模块混合分派**：Research 路由保留原有字符串模式 + `match.group(N)` handler 签名，通过独立 `_dispatch_research_routes` 优先分派，与统一路由表互不干扰。
- **`--root` 覆盖传播**：`_PROJECT_ROOT`/`_WEB_DIR` 定义在 `web_base.py` 中，`main()` 的 `--root` 参数直接修改 `web_base._PROJECT_ROOT`/`web_base._WEB_DIR`，所有 Mixin 通过 `web_base._PROJECT_ROOT` 引用（非 `from web_base import _PROJECT_ROOT`），确保隔离测试环境正确覆盖。
- **POST 重复路由处理**：原 `do_POST` 中约 12 条 GET 路由的重复端点（如 `/api/projects`、`/api/knowledge/files`），通过在同一路由表中注册 GET+POST 两个条目指向同一 handler 实现，handler 签名统一为 `(self, parsed, body=None)`。
- **`_send_sse_raw` bug 修复**：Hermes SSE 中 `self._send_sse_raw("data: [DONE]\n\n")` 改为 `self._send_sse({"type": "done"})`。
- **不修改任何业务逻辑**，仅做物理分文件 + 路由表格式统一。

### 验证结果

- `py_compile` 12 个文件全部通过
- `self_test.py` 全量 120/120 通过（耗时 1.092s）
- `self_test.py --web-ci` 全量 146/146 通过（含 26 个 Web API 虚拟用户测试，耗时 2.240s）
- `from web_server import RequestHandler` 导入正常，MRO 继承链正确
- Web 服务器启动成功，`/api/version`、`/api/skills`、`/api/knowledge`、`/api/research/projects`、`/api/heartbeat`、静态文件、404 全部响应正确
- `--self-check` 6 项全部通过（WEB_DIR/流式切分/代码块/空文本/路由表完整性 123 条/继承完整性）

### 文件规模

| 文件 | 行数 |
|------|------|
| web_server.py（原 2576 行） | 321 |
| web_base.py | 227 |
| web_routes_sessions.py | 292 |
| web_routes_tasks.py | 181 |
| web_routes_kb.py | 447 |
| web_routes_system.py | 264 |
| web_routes_skills.py | 74 |
| web_routes_learning.py | 168 |
| web_routes_projects.py | 470 |
| web_routes_hermes.py | 78 |
| web_routes_upload.py | 200 |
| web_routes_research.py | 458 |
| **合计** | **3180** |

### 内联样式清理（v3.5.4 延后项，已完成）
- 426/554（76.8%）内联 style 替换为 CSS 类
- 新增 ~180 个工具类（按钮/卡片/模态框/表单/状态指示器/原子工具类）
- 涉及文件：research.js（189处）、projects.js（157处）、kb.js、learning.js、chat.js 等

## v3.5.5 - 2026-06-28 knowledge_base.py 门面化拆分（5 子模块）

### 架构重构：知识库引擎模块化

将 `scripts/knowledge_base.py`（1792 行）按职责物理拆分为 5 个子模块，原文件保留为门面（Facade）确保向后兼容，外部模块 `import knowledge_base as kb` 无需任何改动。

**新增子模块**：
- `scripts/kb_text.py` — 文本处理基础工具：`_tokenize` / `_chunk_document` / `_compute_idf` / `parse_frontmatter` / `build_frontmatter` / `_safe_filename` / `_STOPWORDS` / `_FRONTMATTER_RE`
- `scripts/kb_graph.py` — 知识图谱管理：`_load_graph` / `_save_graph` / `_remove_graph_node` / `update_graph_node` / `add_graph_edge` / `get_related_concepts` / `get_graph_summary` / `_inject_wikilinks` / `_extract_wikilinks` / `_get_aliases_for_concept`
- `scripts/kb_index.py` — 索引与检索：`build_index` / `search` / `search_light` / `get_index_status` / `get_enriched_context` / `add_document` / `_should_index` / `list_raw_files` / `ingest_raw`
- `scripts/kb_wiki.py` — Wiki 页面管理：`build_wiki_page` / `get_wiki_page` / `list_wiki_pages` / `save_wiki_page` / `delete_wiki_page` / `check_similar_concepts` / `create_wiki_stub` / `grow_wiki_prompt` / `apply_growth`
- `scripts/kb_health.py` — 健康度与维护：`get_kb_health` / `_compute_graph_connectivity` / `_compute_category_coverage` / `_compute_alias_hit_rate` / `_count_graph_orphans`

**门面保留的跨职责函数**：别名管理（`_load_aliases` / `_expand_query_with_aliases` / `_exact_concept_match` / `_has_tech_terms` / `should_search_knowledge`）、raw 蒸馏编排（`distill_raw_to_wiki` / `_build_distill_prompt` / `save_distilled_wiki`）、生长日志（`_load_growth_log` / `_save_growth_log` / `log_growth` / `get_growth_log` / `get_growth_candidates`）、目录初始化（`_ensure_dirs`）。

### 关键设计决策

- **门面注入模式解决子模块→门面依赖**：子模块不反向 `import knowledge_base`（兼容 `spec_from_file_location` 动态加载场景，避免双重实例），改由门面在加载完成后向子模块全局命名空间注入 `_ensure_dirs` / `log_growth` / `_load_aliases` / `distill_raw_to_wiki` / `get_wiki_page` / `get_growth_candidates` / `get_growth_log` / `_log`。函数体零改动。
- **分层加载消除循环依赖**：`kb_text → kb_graph → kb_index → kb_wiki → kb_health → 门面`，kb_wiki↔kb_index 的互依赖通过单向 import + 门面注入 `get_wiki_page` 解决。
- **私有函数全部 re-export**：`_load_graph` / `_save_graph` / `_remove_graph_node` / `_inject_wikilinks` / `_build_distill_prompt` / `_expand_query_with_aliases` 等被 kb_maintenance / alias_learner / test_e2e / context_builder 直接导入的私有函数，均通过门面 re-export 保持可用。
- **sys.path 自举**：门面顶部将 `scripts/` 注入 `sys.path`，确保 `from kb_text import ...` 在任意加载上下文可用。

### 验证结果

- `py_compile` 6 个文件全部通过
- `self_test.py` 全量 120/120 通过（耗时 0.996s）
- 公开函数 29 个 + 私有函数 22 个 + 常量/路径 15 个，门面 re-export 完整
- 动态加载（`spec_from_file_location`）场景下子模块注入生效，`search` / `get_kb_health` / `save_wiki_page` / `get_enriched_context` 运行时调用正常
- `from knowledge_base import _load_graph, _save_graph, _remove_graph_node, _inject_wikilinks, _build_distill_prompt, _expand_query_with_aliases` 私有函数导入 OK

## v3.5.4 - 2026-06-28 全面质量优化：P0修复+P1安全+P2架构+P3打磨

### P0 功能性 Bug 修复

- **settings.js DOM ID 修复** — 主动提醒横幅和开场白注入引用了不存在的 `chat-messages` ID，导致 v3.4 认知闭环功能静默失效。修正为正确的 `messages` ID。
- **sendMessage 重试按钮修复** — 空回复时的重试按钮 `onclick="sendMessage()"` 会因 content 为 undefined 抛 TypeError。改为 addEventListener 并传递原始内容。
- **AGENTS.md 虚假声明修正** — 测试策略段声称"167 检查点 E2E 课题测试"实际不存在，修正为准确的 `test_e2e_learning_full.py` 描述。

### P1 数据完整性与安全

- **common.save_json 原子写入** — 改为 `tempfile.mkstemp` + `os.fsync` + `os.replace` 模式，保证写入要么完整成功要么不变。7 个文件的重复 `_save_json/_load_json` 定义统一到 common，自动获得原子写入。
- **backup_manager 补全** — `BACKUP_TARGETS` 新增 `projects` 和 `persona`，restore 改为原子恢复模式（先解压到临时目录再逐目录替换），新增 pre-restore 应急备份。
- **run_command 安全加固** — `shell=True` 改为优先 `shell=False`（shlex.split），`_check_escape` 对复合命令每一段都校验，新增 `python -c`/`eval`/`exec` 拦截规则。
- **web_server 并发写加锁** — 4 处 daemon 线程 JSON 写入（paper-feedback/nsfc-decisions）加 `_get_file_lock` + `common.save_json` 原子写入。
- **ModuleLoader 落地** — 修正 `init()` 与 `bindEvents()` 的事件重复绑定：ModuleLoader 统一在 `bindEvents` 前初始化，移除 `bindEvents` 中的三个重复 `bindXxx()` 调用。

### P2 架构与代码质量

- **paths.py 推广采纳** — 10 个文件的 `PROJECT_ROOT = Path(__file__).parent.parent` 替换为 `from paths import PROJECT_ROOT`，消除 50+ 处重复定义。
- **except Exception:pass 收窄** — web_server（17处）、context_builder（7处）、external_fetcher（14处）的静默吞错改为具体异常类型或 debug 日志。
- **logger 升级** — `FileHandler` 改为 `TimedRotatingFileHandler(when='midnight', backupCount=14)`，新增 `_JsonFormatter`。knowledge_base/project_manager/unit_manager 接入 logger。
- **测试补齐** — 新增 32 个检查点（课题模块 19 + LLM 路由 5 + 工具引擎 8），test_web_api 通过 `--web-ci` 纳入回归。全量 120/120 通过，`--web-ci` 模式 146/146 通过。
- **hermes SSE 加固** — 新增 res.ok 检查、120s 超时、reader 引用保存（closeHermesConsole 可取消流）。
- **MutationObserver 修复** — chat.js 和 app.js 的 observer 保存引用并在重复调用时 disconnect，防止内存累积。
- **API 路径参数编码** — task.js/chat.js 的 taskId/msgId 路径参数补全 encodeURIComponent。
- **前端无障碍改进** — research.js 3 处可点击 div 添加 tabindex/role/键盘事件，settings.js 关闭按钮添加无障碍属性。
- **CSS 工具 class** — 新增 `.btn-sm`/`.doc-item`/`.research-card:focus-visible` 等可复用 class，CSS 硬编码 `#e74c3c` 改为 `var(--error-color)`。
- **输入防抖** — session-search 和 skill-search-input 添加 300ms 防抖。
- **aria-label 补全** — history-search-input 添加 aria-label。

### 延后项（高风险，需独立迭代）

- web_server.py（2567行）和 knowledge_base.py（1780行）的文件拆分
- 51 处内联 onclick 全量迁移到事件委托
- 554 处内联 style 全量抽 CSS class

### 验证结果

- ✅ `python3 scripts/self_test.py` 全量 120/120 通过（0.925s）
- ✅ `python3 scripts/self_test.py --web-ci` 146/146 通过
- ✅ 14 个 Python 文件 py_compile 全部通过
- ✅ 原子写入、命令注入拦截、并发锁专项验证通过

## v3.5.3 - 2026-06-28 测试加固：v3.5 课题模块隔离用例 + Web API 回归接入

### 测试补齐

- **v3.5 课题模块链路隔离测试** — `scripts/tests/test_core.py` 新增 `ProjectModuleTests` 套件（19 个检查点）：使用 `create_isolated_env()` 创建隔离环境，重置并 monkey-patch 6 个课题模块（project_manager / unit_manager / project_kb / project_memory / project_context / project_workflow）根路径，覆盖「创建课题 → 创建单元 → 单元状态流转 planning→executing→review→completed → 知识库导入 import_raw_file → 知识库搜索 → 记忆保存 save_conversation → 记忆读取 get_project_context → @语法解析 resolve_at_references → 工作流规划 plan_units → 删除课题」全链路。
- **LLM 路由器测试** — `test_core.py` 新增 `LLMRouterTests` 套件（5 个检查点）：模块导入、router 对象存在、providers 列表、get_status 返回字典、status 含 providers 键（不实际调用 LLM）。
- **工具引擎测试** — `test_core.py` 新增 `ToolEngineTests` 套件（8 个检查点）：`_TOOL_REGISTRY` 注册表完整性（file_read/file_write/calc/run_command）、calc 求值、file_write/file_read 往返、`_is_command_safe` 拦截危险命令。patch PROJECT_ROOT 时使用 `.resolve()` 以兼容 macOS `/var`→`/private/var` 符号链接下的 `_safe_path` startswith 校验。

### Web API 回归接入

- **self_test.py 不再无条件跳过 test_web_api** — `run_tests()` 新增 `web_ci` 参数；全量模式由硬编码 `continue` 改为有条件跳过：默认打印「○ 跳过 test_web_api（需启动子进程；使用 --web-ci 在全量中纳入）」并跳过，`web_ci=True` 时纳入全量回归。
- **新增 `--web-ci` 选项** — `main()` 新增 `--web-ci` 参数。单独使用触发「全量回归 + Web API」（走全量分支 `web_ci=True`）；与 `--module`/`--scenario`/`--persona` 组合时将 web 加入 filters 专项运行。`--web` 行为不变（仅 Web API）。

### 验证结果
- ✅ `python3 scripts/self_test.py` 全量 120/120 通过（1.037s，跳过 web）
- ✅ `python3 scripts/self_test.py --module` 66/66 通过（原 34 + 新增 32）
- ✅ `python3 scripts/self_test.py --web` 26/26 通过（仅 Web API）
- ✅ `python3 scripts/self_test.py --web-ci` 146/146 通过（全量 + Web API）
- ✅ `python3 scripts/self_test.py --web-ci --module` 92/92 通过（module + web）
- ✅ `python3 scripts/self_test.py --json` 输出含 6 个套件（新增 3 个）
- ✅ 新增 32 个检查点（课题链路 19 + LLM 路由 5 + 工具引擎 8）

## v3.5.2 - 2026-06-28 数据安全加固：save_json 原子写入 + 工具函数去重

### 数据安全

- **common.save_json 原子写入** — `scripts/common.py` 的 `save_json` 改为原子写入模式：先写入同目录 `.tmp` 临时文件并 `fsync`，再 `os.replace()` 到目标路径（POSIX 原子操作），保证文件要么完整更新要么保持不变，避免写入中途崩溃导致 JSON 损坏。新增 `atomic_save_json` 别名供语义化调用。

### 代码去重

- 消除 7 个脚本中与 `common` 模块重复的 `_load_json` / `_save_json` / `_safe_filename` / `_now` 定义，统一改用 `common.load_json` / `save_json`（原子写入） / `safe_filename` / `now_utc`：
  - `learning_engine.py`：删除 `_load_json` / `_save_json` / `_safe_filename`，15 处调用改为公共函数
  - `quality_evaluator.py`：删除 `_load_json` / `_save_json`，11 处调用改为公共函数
  - `research_profiler.py`：删除 `_load_json` / `_save_json`，4 处调用改为公共函数
  - `memory_manager.py`：删除 `_load_json`，5 处调用改为 `load_json`（`_write_json` 已是 `save_json` 别名，自动获得原子写入）
  - `context_builder.py`：删除 `_load_json`（改用更健壮的 `common.load_json`，异常时返回 default 而非崩溃），8 处调用改为公共函数
  - `agora_bridge.py`：删除 `_load_json`，4 处调用改为公共函数
  - `paper_pool.py`：删除 `_now`，`_load` / `_save` 改为委托 `common` 函数（`_save` 自动获得原子写入），清理未使用的 `json` / `datetime` 导入

### 验证结果
- ✅ Python 编译全部通过（common.py + 7 个修改文件）
- ✅ 全量测试 88/88 通过（0.886s）
- ✅ 原子写入功能验证通过（内容正确、无残留临时文件、别名可用）
- ✅ 7 个模块导入正常

## v3.5.1 - 2026-06-27 架构优化：8 项改进全部落地

### 新增功能

- **课题 AI 主动规划** — `project_workflow.ai_plan_units()`：读取课题知识库 raw 层材料，调用 LLM 生成单元拆分建议，返回 JSON 供用户确认后执行 `plan_units`。新增 API 路由 `/api/research/projects/{id}/workflow/ai-plan`。
- **知识库统一检索** — `context_builder.py` 扩展：会话关联课题时同时检索全局知识库和课题知识库，课题 KB 结果降权 0.9 后合并注入 `[课题知识库]` 段落，kb_hits 同时返回两库来源。
- **学习成本 SVG 趋势图** — `learning.js` 新增 `renderCostChart()`：纯 SVG 绘制最近 14 天 token 消耗柱状图，含预算线、超预算红色标记、月度汇总，适配深色/浅色主题。`web_server.py` 的 `/api/learning/status` 补充 `cost_daily`/`cost_monthly`/`daily_budget` 返回字段。

### 架构优化

- **web_server.py 路由表重构** — 课题模块 37 条路由从 if-elif 迁移到 `_RESEARCH_ROUTES` 路由表，新增 `_dispatch_research_routes()` 分发方法和 37 个 `_rg_*` handler 方法，删除约 430 行重复路由代码。`([^/]+)$` 正则天然排除子路径，消除原有守卫条件。其余路由保持 if-elif 不变，为后续全量迁移铺路。
- **前端模块加载器** — `core.js` 新增 `ModuleLoader`（register/init），9 个模块 JS 自注册初始化函数，`app.js` 统一调用 `ModuleLoader.init()`。现有手动绑定保持不变，向后兼容。

### 文档治理

- `docs/` 目录治理：3 个 `solid-HHG-*.md` 调研材料移入 `knowledge/raw/notes/`，4 个历史版本文档移入 `docs/archive/`
- `AGENTS.md` 测试策略更新为三层体系：单元回归（88）+ 模块自检（40）+ E2E 集成（167）
- `AGENTS.md` docs/ 目录结构、头部日期同步更新

### 验证结果
- ✅ Python 编译全部通过
- ✅ 12 个 JS 文件语法检查全部通过
- ✅ 全量测试 88/88 通过（0.833s）
- ✅ 6 个课题模块自检全部通过
- ✅ web_server API 端到端验证通过（路由表 + 非 research 路由）

## v3.5.0 - 2026-06-27 课题指导模块：结构化科研课题全流程管理

### 维护：项目全面评估与清理
- 清理冗余文件：4 个 `__pycache__` 目录（73 个 .pyc）、6 个 `.DS_Store`、`knowledge/.cache/`、2 份冗余备份、2 个测试报告目录、7 天前旧日志
- 清理测试残留：8 个 `hhg_*.json` 数据文件（污染 tasks/active/）、23 个 E2E 测试任务、13 个测试会话（含归档）
- 修复代码问题：清理 `project_context.py`/`project_workflow.py`/`test_e2e_learning_full.py` 的死导入；移除 `app.js`/`chat.js` 的 2 处 `console.log` 调试输出
- 修复 `project_memory.py` 的 `get_project_context()` bug（units 列表按字符串 ID 处理而非字典）
- 文档同步：更新 README.md（v3.1.2→v3.5.0，补全 Phase 8-10）、AGENTS.md（修正脚本清单+docs 结构+web/js 清单）、scripts/README.md（整体重写）、memory/README.md（补全 17 个文件）、skills/README.md（补 self-test）、docs/README.md（补 3 个文件）、新建 projects/README.md
- 修复 CHANGELOG.md 重复版本号（v2.1.0→v2.1.1、v2.2.0→v2.0.1）

### 核心新增：课题指导模块（Research Project Guidance）

让林赛以"课题副导师"角色，协助用户将研究课题拆分为验收标准清晰的最小单元，分工推进、验收循环、自主管理分层知识库与课题记忆。

### 新增模块（8 个文件）

| 模块 | 职责 |
|------|------|
| `project_manager.py` | 课题 CRUD、状态机（planning→active→paused/completed）、PROJECT-MEMORY.md 自动维护与压缩 |
| `unit_manager.py` | 单元 CRUD、验收标准结构化数组、风险追踪、交付物管理、状态机（planning→executing→review→completed） |
| `project_kb.py` | 分层知识库引擎（raw/parsed/summary）、TF-IDF 倒排索引、标签索引、外部文件导入 |
| `project_memory.py` | 三级记忆（对话全文/记忆片段/核心记忆）、决策记录、风险记录、上下文组装（≤2000字符） |
| `project_context.py` | @课题知识库语法解析、跨课题检索、课题上下文构建（≤3000字符） |
| `project_workflow.py` | 工作流编排：plan_units → start_unit_execution → review_unit → complete_unit → generate_project_summary |
| `web/js/research.js` | 前端课题管理面板（课题列表/详情/单元时间线/知识库浏览器/记忆面板/工作流操作） |

### 扩展现有模块（4 个文件）

- **`task_manager.py`**：`create_task()` 新增 `unit_id` 参数，关联课题单元
- **`session_manager.py`**：`create_session()` 新增 `project_id` 参数，关联课题
- **`context_builder.py`**：新增课题上下文注入（会话关联课题时自动注入 PROJECT-MEMORY.md + 知识库概览）；新增 @课题知识库语法解析（用户输入含 `@PRJ-xxx` / `@课题知识库` 时自动检索跨课题知识）；新增 `project` 预算类别（2000 字符）
- **`web_server.py`**：新增 37 个 API 路由（16 GET / 13 POST / 6 PUT / 2 DELETE），统一 `/api/research/` 前缀

### 前端更新（3 个文件）

- **`web/index.html`**：新增 🔬 课题工具栏按钮、课题指导模态框、research.js 脚本加载
- **`web/js/app.js`**：新增课题按钮事件绑定与工具栏 active 联动
- **`web/js/research.js`**（新建，~770 行）：4 tab 详情视图（单元/知识库/记忆/工作流），单元时间线带验收标准 checkbox，知识库浏览器带层级/类型/标签筛选 + Markdown 预览

### 数据结构

```
projects/
├── {project_id}.json              # 课题元数据
└── {project_id}/
    ├── PROJECT-MEMORY.md          # 核心记忆（≤100行，自动压缩）
    ├── units/
    │   └── UNIT-001.json          # 单元（含验收标准数组/风险/任务引用）
    ├── kb/
    │   ├── raw/                   # 原始材料（proposals/references/data）
    │   ├── parsed/                # 林赛解析笔记（concepts/methods/literature）
    │   ├── summary/               # 成果汇总（unit-reports/milestone-reviews/project-summary）
    │   ├── index.json             # 倒排索引
    │   └── tags.json              # 标签索引
    └── memory/
        ├── conversations/         # 对话全文存档
        ├── snippets/              # 记忆片段
        ├── decisions.md           # 决策记录
        └── risks.md               # 风险记录
```

### 设计决策

- **知识库隔离**：复用现有 knowledge_base 系统设计，每个课题独立子库，通过 `@课题知识库` 语法跨课题共享
- **单元=任务容器**：单元是 task_manager 任务的逻辑分组，不另建任务系统
- **验收标准=结构化数组**：`[{id, text, met, notes}]`，支持勾选/备注
- **无课题模板**：不同课题的单元划分根据具体情况判断，通过课题推进积累经验

### 验证结果
- ✅ 全部 Python 文件通过 `py_compile`
- ✅ 核心模块测试 34/34 通过
- ✅ 人格一致性抽检 38/38 通过
- ✅ 场景剧本测试 16/16 通过
- ✅ 全量 88/88 通过（0.857s）
- ✅ 6 个新模块自检全部通过（project_manager 5/5, unit_manager 8/8, project_kb 8/8, project_memory 9/9, project_context 4/4, project_workflow 6/6）
- ✅ 前端 JS 语法检查通过

## v3.4.1 - 2026-06-26 代码结构优化：消除系统性重复

### 核心变更：激活已有的 common.py/paths.py，消除 50+ 处重复工具函数

项目此前已建好 `common.py`（集中工具函数）和 `paths.py`（统一路径常量），但**零引用**——22 个脚本各自重复定义 `_now_utc`、`_read_json`、`_write_json`，web_server.py 有 6 处 importlib 动态加载样板。本次优化系统性消除了这些重复。

### Python 后端（25 个文件）

- **创建 `scripts/__init__.py`**：使 scripts/ 成为 Python 包，为后续标准 import 语法铺路
- **激活 `common.py`**（22 个文件）：
  - 23 处 `_now_utc` 定义 → `from common import now_utc as _now_utc`（消除 22 处重复）
  - 5 处 `_write_json` 定义 → `from common import save_json as _write_json`
  - 3 处 `_read_json` 定义 → `from common import load_json as _read_json`
- **新增 `common.lazy_load()`**：统一懒加载函数，消除 importlib 样板
- **`context_builder.py`**：3 段重复的 `_try_xxx` 懒导入块（24 行）→ 3 行 `from common import lazy_load` 调用
- **`web_server.py`**（14 处清理）：
  - 6 处 `importlib.util` 动态加载 → `lazy_load("module")` 单行调用
  - 4 处 `import json as _json` 冗余导入 → 使用顶层 `json`
  - 1 处 `from pathlib import Path as _Path` 冗余导入 → 使用顶层 `Path`
  - 3 处局部 `import backup_manager as bm` → 提升为顶层导入

### 前端 JavaScript（5 个文件）

- **删除 `projects.js` 中的 `escapeHtml` 死代码**：core.js 已定义，兜底定义永不执行
- **统一 Markdown 渲染**：
  - `core.js` `renderMarkdown()` 增强：新增 h1/h2/h3 标题支持
  - `kb.js` `openWikiDetail`：9 行内联正则 → `renderMarkdown()` + wikilink 后处理
  - `kb.js` `openRawDetail`：8 行内联正则 → `renderMarkdown()`（XSS 防护完整保留）
  - 3 套不一致的 Markdown 实现 → 1 套统一实现
- **任务状态更新注释**：`task.js updateTaskStatus` 与 `projects.js cycleTaskStatus` 添加关系注释（差异较大，保持独立）
- **`style.css`**：补充 `.message-bubble` 内标题尺寸约束

### 量化改进

| 指标 | 优化前 | 优化后 | 消除数 |
|------|--------|--------|--------|
| `_now_utc` 定义 | 23 处 | 1 处（common.py） | 22 |
| `_write_json` 定义 | 5 处 | 0 处 | 5 |
| `_read_json` 定义 | 3 处 | 0 处 | 3 |
| web_server importlib 样板 | 6 处 | 0 处 | 6 |
| web_server 冗余 json 导入 | 4 处 | 0 处 | 4 |
| 前端 Markdown 实现 | 3 套 | 1 套 | 2 |
| 前端死代码 | 1 处 | 0 处 | 1 |

### 验证结果
- ✅ 全部 Python 文件通过 `py_compile`
- ✅ 核心模块测试 34/34 通过
- ✅ 人格一致性抽检 38/38 通过
- ✅ 场景剧本测试 16/16 通过
- ✅ 总计 88/88 全量通过（0.869s）

### 修改文件清单（28 个）
- 新建：`scripts/__init__.py`
- 修改 Python（23）：`common.py`、`context_builder.py`、`web_server.py`、`memory_reflow.py`、`sync_engine.py`、`knowledge_base.py`、`project_dispatch.py`、`task_manager.py`、`growth_engine.py`、`alias_learner.py`、`kb_categories.py`、`kb_auto_sync.py`、`kb_maintenance.py`、`kb_importer.py`、`session_manager.py`、`research_profiler.py`、`learning_engine.py`、`external_fetcher.py`、`quality_evaluator.py`、`proactive_engine.py`、`kb_capture.py`、`usage_tracker.py`、`memory_manager.py`、`agora_bridge.py`
- 修改前端（5）：`core.js`、`kb.js`、`projects.js`、`task.js`、`style.css`
- 更新：`VERSION`、`CHANGELOG.md`

## v3.4.0 - 2026-06-25 认知闭环：从"功能完备"到"认知活跃"

### 核心变更：打通 hermes→记忆→对话的认知回流通道

林赛此前"建好了但没运行"——记忆系统空置、心跳信号被前端忽略、hermes 的 124 个会话从未反哺记忆。v3.4 让沉睡的资产在真实对话中活跃起来。

### Phase 1：认知回流（5 项，涉及 8 个文件）

- **P1-1 hermes→记忆提炼** — `scripts/memory_reflow.py`（新建）
  - 扫描 hermes 会话，提取 memory 工具调用、用户决策、研究方向、CONTEXT COMPACTION 目标
  - 从 112 个会话中提取 26 条记忆片段、6 条用户决策、10 个研究方向关键词
  - 集成到 `sync_engine.py`：`sync_all()` 新增第 4 步认知回流，新同步会话自动触发记忆提炼
  - CLI：`--cold-start`（回溯全部）/ `--reflow`（增量）/ `--status`（状态）/ `--self-check`（自检）

- **P1-2 记忆冷启动** — 执行 `memory_reflow.py --cold-start`
  - `user-profile.json`：research_field 从 [] → 10 个关键词，known_skills 从 [] → 7 个，preferences 新增 general + paper_interests
  - `long-term-memory.json`：snippets 从 0 → 26 条，snippets_index 同步建立
  - `working-context.json`：pending_decisions 从 1 条(含垃圾) → 3 条有效，key_insights 从 0 → 12 条

- **P1-3 开场即主动** — `web_server.py` + `web/js/settings.js` + `web/js/session.js`
  - `/api/heartbeat` 增强：返回 `proactive_messages` 数组（格式化中文文案，前端可直接展示）
  - `checkHeartbeat()` 消费提醒：去重后展示 banner，30 秒轮询
  - `injectProactiveOpening()`：会话加载时注入林赛主动消息气泡

- **P1-4 补全主动感知配置** — `memory/autonomy-level.json` + `memory/learning-config.json`（新建）
  - autonomy-level.json：默认 suggest 级别（observe/suggest/act 三级）
  - learning-config.json：arXiv 关键词、日配额、成本限制、统计计数器

- **P1-5 浅输入人格锚定** — `scripts/context_builder.py`
  - `_is_small_talk()`：检测问候/闲聊/极短输入（7 类模式 + 长度阈值）
  - `_build_persona_anchor()`：从记忆文件提取研究方向、活跃项目、最近记忆片段（去重），注入 system_prompt
  - 浅输入时跳过技能匹配和知识库检索，避免无关开销
  - 效果：用户说"你好"时，林赛能说"上次你提到固体HHG相位匹配，进展如何？"而非机械回复

### Phase 2：知识库价值兑现（3 项，涉及 4 个文件）

- **P2-1 知识库命中埋点** — `scripts/context_builder.py`
  - `build_context()` 返回 `kb_hits` 数组：每条命中记录 title/source/stage/score/doc
  - 同时返回 `is_small_talk` 标志，供调用方决策

- **P2-2 回复标注引用来源** — `web_server.py` + `web/js/chat.js` + `web/css/style.css`
  - SSE 流新增 `metadata` 事件类型：在 token 之前发送 kb_hits
  - `chat.js` 处理 metadata 事件：在消息气泡下方渲染引用标签（📚 raw / 📝 wiki / 🔗 graph）
  - CSS 样式：圆角标签，hover 高亮，深色/浅色主题适配

- **P2-3 主动检索增强** — `scripts/context_builder.py`
  - 接入 `knowledge_base.should_search_knowledge()`：休眠代码激活
  - 5 级判断：长度过滤 → 闲聊过滤 → 明确请求 → 精确概念匹配 → 模式+技术术语
  - 效果：非技术讨论（如"今天天气不错"）不再触发知识库检索，减少噪声注入

### 新增 API 端点（2 个）

- `GET /api/memory/status`：返回记忆系统状态摘要
- `GET /api/memory/reflow`：手动触发认知回流

### 验证结果
- ✅ 全部 Python 文件通过 `py_compile`
- ✅ 核心模块测试 34/34 通过
- ✅ memory_reflow.py 自检通过（5 项检查）
- ✅ 浅输入检测 7/7 测试用例通过
- ✅ 记忆冷启动：112 会话 → 26 片段 + 10 研究方向 + 7 技能

### 修改文件清单（13 个）
- 新建：`scripts/memory_reflow.py`、`memory/autonomy-level.json`、`memory/learning-config.json`、`memory/reflow-state.json`
- 修改：`scripts/context_builder.py`、`scripts/sync_engine.py`、`scripts/web_server.py`、`web/js/settings.js`、`web/js/session.js`、`web/js/chat.js`、`web/css/style.css`、`memory/user-profile.json`、`memory/working-context.json`、`memory/long-term-memory.json`、`VERSION`

## v3.3.4 - 2026-06-24 第五轮端到端测试修复：2 个功能 bug

### 修复内容（2 项，涉及 2 个文件）

- **P5-1 (MEDIUM)**：任务创建 API 响应缺少字段，新建任务不渲染到看板
  - **问题**：`POST /api/tasks` 返回 `{success, task_id, title, dispatch_id}`，缺少 `status`/`priority`/`description` 等字段，前端 `createNewTask()` 将不完整对象 push 到 `State.tasks`，`renderTaskBoard()` 因 `task.status` 为 undefined 无法匹配列
  - **修复**：`web_server.py` 创建任务后调用 `tm.get_task(tid)` 返回完整任务对象；`task.js` `createNewTask()` 增加防御性合并，确保 `status`/`priority` 等字段存在
  - **验证**：浏览器实测新建任务即时渲染到 backlog 列

- **P5-2 (HIGH)**："在编辑器中打开"按钮无响应 — `subprocess` 模块未导入
  - **问题**：`web_server.py` 第 1253 行使用 `subprocess.run(["open", str(full)])` 打开本地文件，但文件顶部未 `import subprocess`，导致 `NameError: name 'subprocess' is not defined`，API 返回 500 错误
  - **修复**：`web_server.py` 导入区添加 `import subprocess`
  - **影响范围**：Wiki 预览页"📂 在编辑器中打开"按钮、Raw 文件预览页"📂 在编辑器中打开"按钮
  - **验证**：浏览器实测点击按钮显示"✓ 已打开本地文件"，文件在系统编辑器中打开

### 验证结果
- ✅ Python 文件通过 `py_compile`
- ✅ 浏览器实测："在编辑器中打开"按钮正常工作
- ✅ 浏览器实测：新建任务即时渲染到看板
- ✅ 端到端测试 20 个功能模块中 19 个通过（此前 18 个通过 + 本次修复 1 个）

## v3.3.3 - 2026-06-24 彻底检查修复：3 类遗留 bug

### 修复内容（3 类 bug，涉及 7 个文件）
- **Bug1 (P3-5 未完成)**：raw 文件树项目(30个)和 action 项目(3个)缺少 `tabindex="0"` 和 `role="button"`，键盘用户无法聚焦 → 全部补齐
- **Bug2 (P0-9 未完成)**：6 个 `confirm()`/`prompt()` 调用未替换为模态框 → 新增 `confirmModal()`/`promptModal()` Promise 辅助函数，全部替换
  - `kb.js`：删除分类确认、移除标签确认、新增标签输入
  - `task.js`：删除任务确认
  - `projects.js`：派发 hermes 任务确认
  - `skill.js`：重置技能配置确认
- **Bug3 (空指针防护)**：3 个函数缺少 null 检查，DOM 元素不存在时崩溃
  - `core.js`：`showToast()` 检查 `toast-container` 存在性
  - `core.js`：`applyTheme()` 检查 `theme-toggle` 按钮存在性
  - `session.js`：`switchSession()` 检查 4 个 DOM 元素存在性

### 验证结果
- ✅ 11 个 JS 模块全部通过 `node --check`
- ✅ 3 个 Python 文件通过 `py_compile`
- ✅ 浏览器实测：raw/action 项目 tabindex=0(126个)、aria-label(150个)、confirmModal/promptModal 函数可用
- ✅ self_test 86/86 全部通过
- ✅ 控制台无应用错误

## v3.3.2 - 2026-06-24 第三轮用户测试反馈修复

### 修复内容（8 项全部完成）
- **P1-16**：28 个 wiki 文件标签去重 + `build_frontmatter()` 写入去重逻辑防止复发
- **P1-17**：移动端 `.kb-main` 占满宽度，右侧栏固定抽屉模式不挤压主内容
- **P2-19**：SSE 流结束后检测空回复，显示错误提示 + 🔄 重试按钮 + toast
- **P2-20**：深色模式 placeholder 对比度提升（`#9ca3af` opacity:0.8，符合 WCAG AA）
- **P2-21**：窄屏工具栏改横向滚动（`flex-wrap:nowrap; overflow-x:auto`）
- **P3-5**：知识库树项目加 `tabindex="0" role="button"` + Enter/Space 键盘事件
- **P3-6**：标签列表 flex+gap 布局 + line-height:1.8 消除"文字墙"
- **P3-7**：LLM Provider SSL 证书验证降级 + URLError 明确提示 SSL/网络错误

### 验证结果
- ✅ 11 个 JS 模块全部通过 `node --check`
- ✅ Python `knowledge_base.py` / `llm_router.py` / `web_server.py` 通过 `py_compile`
- ✅ 标签重复文件数：28 → 0
- ✅ self_test 88/88 不回归

## v3.3.1 - 2026-06-23 稳定性优化两轮完成 + 用户模拟测试

### 稳定性优化（stability-ux-plan.md）
- **第一轮 30 项全部完成**：P0 功能损坏 8 项 + P1 布局稳定性 8 项 + P2 功能融洽 7 项 + P3 视觉协调 4 项
- **第二轮 14 项全部完成**：数据安全(P0-9/10) + 并发安全(P1-9/10/11) + 性能(P1-12) + XSS 防护(P1-13/14) + 状态一致性(P1-15) + 断网/超时(P2-14/16) + 无障碍(P2-10/11) + 术语词典(P2-18)
- **第三轮用户模拟测试完成**：8 个模块端到端测试通过，发现 8 个新问题（P1×2, P2×3, P3×3）

### 用户模拟测试结果
- ✅ 首屏/布局/移动端 tab 正常
- ✅ 会话/聊天/SSE 流式正常（LLM 后端环境问题除外）
- ✅ 知识库文件树/预览/搜索正常
- ✅ 任务看板/设置/备份/学习配置正常
- ✅ 无障碍(aria-label 24 个, role=log, ESC 关模态)正常
- ✅ XSS 链接阻断正常
- ✅ 深色主题 A- 评级
- 🔧 8 个新问题待修复（详见 stability-ux-plan.md 第十节）

### 新发现问题（待修复）
- **P1-16**：28 个 wiki 文件标签重复（#status/mature 重复 6-8 次）
- **P1-17**：移动端右侧栏未隐藏，挤压主内容区
- **P2-19**：LLM 超时后前端 typing indicator 持续显示无错误提示
- **P2-20**：深色模式搜索框占位文字对比度不足
- **P2-21**：工具栏按钮窄屏溢出无法点击
- **P3-5**：知识库树项目不可键盘聚焦
- **P3-6**：标签列表区域过于密集
- **P3-7**：LLM Provider SSL 错误处理不足

## v3.3.0 - 2026-06-23 项目总控中心：进度追踪+任务+意见+hermes 执行闭环

### 核心定位
📂 项目面板升级为「项目总控中心」——前端不只是看进度，还能**添加项目任务、提出项目意见、派活给后端 hermes 执行并全程追踪**。林赛 Web 正式成为双 hermes 工作流的指挥台。

### 新布局（弹窗内 7 tab）
```
[📊总览] [📋项目任务] [💭项目意见] [⚡执行追踪] [🔬NSFC] [📄文献] [🔄同步]
```

### 新增能力

**1. 📊 总览**（聚合仪表盘）
- 4 张统计卡：NSFC 进度 / 任务 待办·进行·完成 / 待处理意见 / hermes 执行进行中
- 任务按项目分布条形图 + 最近 5 条 hermes 执行记录
- 快捷入口：新建任务 / 提意见 / 查执行

**2. 📋 项目任务**（核心：任务↔项目↔hermes 三者打通）
- 完整新建表单：标题/项目下拉/优先级(含紧急)/截止/描述/**执行者(我自己/派hermes/先不执行)**
- 选「派 hermes」→ 创建即自动派发 + 跳执行追踪页
- 任务卡片按项目分组，含进度条、子任务数、**⚡派给hermes 按钮**

**3. 💭 项目意见**（独立于任务的想法沉淀）
- 项目下拉 + 文本框 + ☑反馈给hermes
- 意见列表（按项目分组，可标记解决、转讨论）

**4. ⚡ 执行追踪**（补齐 oneshot fire-and-forget 缺口）
- 时间线：状态(running◐/done✓/failed✗/timeout⏱)/耗时/可展开查看 hermes 完整输出

### 后端改造

**新增 `scripts/project_dispatch.py`**（意见+执行追踪持久化层）
- `memory/project-dispatch.json`：opinions[] + dispatches[] 双数组，原子写
- 7 个函数 + 6/6 自检通过

**任务模型扩展 `scripts/task_manager.py`**
- `create_task` 新增 `project` + `assignee` 字段
- `list_tasks` 新增 `project` 过滤参数
- 新增 `update_task_fields` 通用更新

**`scripts/project_reader.py`** 新增 `get_projects_list()`
- 聚合三来源去重：NSFC + 知识库子库 + working-context active_projects

**`scripts/web_server.py`** 新增 7 API + 改造 2 个
- `GET /api/projects/list|overview` / `GET|POST /api/projects/opinions` / `PUT /api/projects/opinions/<id>/resolve`
- `GET /api/projects/dispatches` / `POST /api/tasks/<id>/dispatch`（核心派活闭环）
- 改造 `POST /api/tasks`（补 project/assignee + 创建即派发）
- 补 `PUT /api/tasks/<id>`（修复拖拽 404）

**hermes 反馈闭环**（复刻 discuss-summary 四步模板）
- 接收 → 持久化 → 写 hermes plans/ 目录（`{date}_linSai-dispatch.md`，hermes 已声明"For Hermes: 按 task 顺序执行"契约）→ daemon 线程 oneshot → 回写结果

### 顺带修复的 Bug
- **task.js 字段名 bug**：`task.id` → `task.task_id`（看板渲染/拖拽/详情全失效）
- **PUT `/api/tasks/<id>` 路由缺失**：拖拽改状态一直 404
- **priority 下拉值被丢弃**：app.js 只传 title
- **task-add-form 提交后未清空**

### 验证
- `py_compile` 全量通过 + `self_test` 88/88 不回归 + `project_dispatch` 自检 6/6
- 端到端 API：任务CRUD + 项目过滤 + 状态流转 + 意见CRUD + 派活记录 + 执行追踪 全链路通过

## v3.2.0 - 2026-06-21 代码简化与冗余清理

### Bug 修复（P0）
- **`loadKbPage` 未定义**：3 处调用改为 `openWikiDetail`，修复筛选器和标签编辑崩溃
- **`launch.sh` 语法错误**：Python docstring `"""` 改为 bash 注释 `#`
- **CSS 变量缺失**：补全 `--surface`/`--accent`/`--info-color`（浅色+深色主题），修复 20+ 处样式失效

### 代码简化
- **删除 599 行前端死代码**：17 个废弃 `kb-manager-overlay` 相关死函数 + 2 个死 HTML 弹窗
- **删除 3 个死脚本**：`test_e2e_learning.py`（子集）、`learning_quality_tracker.py`（从未运行）、`deep_audit.py`（一次性）
- **提取公共函数**：`STAGE_LABELS_FULL`/`STAGE_ICONS` 常量（3 处重复→1 处）、`openModal`/`closeModal`（12 处重复→1 处）
- **CSS 合并**：`.modal-overlay` 重复定义合并、3 处 blockquote 样式合并、删除 7 组未使用的 CSS 类
- **创建公共模块**：`scripts/common.py`（`now_utc`/`load_json`/`save_json`/`safe_filename`）、`scripts/paths.py`（统一路径常量）

### 配置修复
- 版本号同步：README.md / AGENTS.md / scripts/README.md 的 `3.0.1` → `3.1.2`
- `.gitignore`：新增 `knowledge/raw/checkpoint.json`，`knowledge/captures` → `knowledge/captures/`
- README.md 启动说明：修复两个"方式一"自相矛盾

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿

## v3.1.2 - 2026-06-20 智能增强（迭代 3）

### 新功能
- **别名自动发现**：`alias_learner.py` 从三个来源发现别名候选
  - `[[WikiLink|别名]]` 用法
  - frontmatter 的 `aliases` 字段
  - 图谱 `same_as` 边
  - 候选存储在 `memory/alias-candidates.json`，`--apply` 写入 `aliases.json`
  - 实测发现 11 个新候选
- **growth_stage 自动晋升**：`growth_engine.py` 规则引擎
  - seedling → growing：被 ≥3 篇 raw 引用，或内容 >500 字且有 related
  - growing → mature：被 ≥5 篇引用 + 检索命中 ≥10 次，或内容 >2000 字且有 related
  - 只升不降，手动设置的 mature 不被覆盖
  - 晋升记录写入 `growth-log.json`
- **导入时自动连边**：`kb_linker.py` 自动提取主题关键词连接 related 边
  - 从 `[[WikiLink]]` 和标题提及两个来源发现关联
  - 不覆盖已有 related，只追加新发现的
  - 实测发现 62 个页面可补充 169 条新边
- **健康检查增强**：`get_kb_health()` 新增 3 个维度
  - 图谱连通性（最大连通分量占比）
  - 分类覆盖率（被自定义分类覆盖的 wiki 比例）
  - 别名命中率（aliases.json 中的别名在 wiki 中被使用的比例）
  - 前端健康弹窗同步增强显示

### 新增文件
- `scripts/alias_learner.py` — 别名自动发现引擎
- `scripts/growth_engine.py` — growth_stage 自动晋升规则引擎
- `scripts/kb_linker.py` — 导入时自动连边引擎

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿

## v3.1.1 - 2026-06-20 灵活分类系统（迭代 2）

### 新功能
- **自定义分类系统**：用户可创建基于关键词规则的虚拟分类
  - 支持任一匹配（any）和全部匹配（all）两种逻辑
  - 自动扫描全库，匹配 wiki 页面
  - 分类是虚拟的：不移动文件，删除分类不影响文件
  - 存储在 `knowledge/categories.json`
- **分类管理弹窗**：前端 🏷️ 分类按钮，支持创建/删除/重新扫描
- **搜索筛选器**：4 个下拉筛选器（类型/阶段/子库/标签）
  - 实时过滤文件树
  - 一键清除筛选
- **标签内联编辑**：文件预览区显示标签 chip
  - 点击 ✕ 移除标签/子库归属
  - 点击"+ 标签"添加新标签
  - 通过 `/api/knowledge/wiki` POST meta-only 更新

### 新增 API 端点
- `GET /api/knowledge/categories` — 列出全部分类
- `GET /api/knowledge/filters` — 获取筛选器选项
- `POST /api/knowledge/categories/create` — 创建分类
- `POST /api/knowledge/categories/update` — 更新分类
- `POST /api/knowledge/categories/delete` — 删除分类
- `POST /api/knowledge/categories/scan` — 重新扫描全部分类
- `POST /api/knowledge/filter` — 按条件过滤 wiki 页面

### 改进
- `POST /api/knowledge/wiki` 支持 meta-only 更新（无需 content）
- 新增 `scripts/kb_categories.py` 模块（CRUD + 匹配 + 筛选）
- 前端新增分类管理、筛选器、标签编辑器 JS 函数

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：创建"固体HHG"分类，自动匹配 74 篇 wiki 页面

## v3.1.0 - 2026-06-20 知识库自维护闭环（迭代 1）

### 新功能
- **`sync_all()` 自动重建**：同步完成后自动触发 reindex + rebuild_graph，无需手动重建
- **`kb_auto_sync.py` 定时同步脚本**：支持 macOS LaunchAgent 每日 09:00 自动同步
  - `--install`：安装 LaunchAgent
  - `--uninstall`：卸载 LaunchAgent
  - `--status`：查看自动同步状态和历史
  - 失败自动记录到 `sync-state.json` 的 `auto_sync_history`
- **`/api/sync/auto-status` API**：返回 LaunchAgent 安装状态和自动同步历史
- **前端管理工具栏**：知识库文件树顶部新增
  - 🔄 同步按钮：一键触发 sync_all（含自动重建）
  - 📊 健康按钮：快速查看知识库健康度
  - 同步状态指示器：显示自动同步是否开启

### 改进
- `sync_engine.py` 新增 `_import_kb_helper()` 辅助函数
- `web_server.py` 新增 `/api/sync/auto-status` GET 端点
- `web/index.html` 新增 `.kb-toolbar` 管理工具栏
- `web/css/style.css` 新增工具栏和指示器样式
- `web/js/app.js` 新增 `handleKbSync`、`handleKbHealth`、`loadSyncIndicator` 函数

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：工具栏渲染正常，同步按钮功能正常，指示器正确显示"手动同步"

## v3.0.2 - 2026-06-20 BUG-A 修复 + 知识库维护增强

### BUG 修复
- **BUG-A（Web 端聊天功能异常）**：修复 v3.0.0 布局重构引入的聊天侧栏问题
  - `.upload-zone` 默认隐藏（此前始终可见，占用输入区 64px 空间）
  - `.chat-sidebar` 添加 `align-self: stretch` + `overflow: hidden` 高度保护
  - `.chat-sidebar-inner` 添加 `min-height: 0` 防止 flex 子元素高度塌陷
  - 上传按钮改为切换上传区域显示/隐藏（此前直接弹文件选择器）
- **Web API 测试超时**：`_wait_for_server` 超时从 20s 增至 30s，轮询超时从 2s 增至 3s

### 知识库维护增强
- **`kb_importer.py`**：补全 `import_all_candidates()` 函数定义（此前 def 行缺失，函数体悬空）
- **`kb_maintenance.py`**：新增 `cmd_rebuild_graph()` 子命令（`--rebuild-graph`）
  - 从所有 wiki frontmatter 的 related/project 字段反向重建知识图谱
  - 解决 import_candidate/import_deep_analysis 绕过 save_wiki_page 导致的图谱断层
  - 已集成到 `--weekly` 周维护流程

### 验证
- self_test 88/88 全绿
- Web API 测试 26/26 全绿
- 浏览器验证：消息区从 377px 增至 441px，输入区从 212px 降至 148px
- 图谱重建：88 节点成功导入

## v3.0.1 - 2026-06-19 每日简报+NSFC项目正式纳入知识库管理

### 导入内容（47 篇）
- **23 份每日简报** → wiki/papers/briefing-*.md（带 frontmatter，可检索可浏览）
- **15 份深度解析** → wiki/projects/deepxiv-论文库/（结构化：核心发现/林赛理解/开放问题）
- **5 个 NSFC 课题报告** → wiki/projects/NSFC-强场超快/（T1-T5 立项依据镜像）
- **5 份 NSFC 决策记录** → wiki/projects/NSFC-强场超快/decisions/

### 成果
- wiki 从 33 → 89 篇，raw 从 61 → 106 篇
- 搜索"每日简报"/"NSFC"/"带动力学"全部可检索命中
- 知识库主区文件树现在显示全部内容（简报/深分析/课题/决策）
- 所有导入内容带 project 标签 + source 标记，纳入子库分类

### 验证
- self_test 88/88 全绿
- 检索验证通过

## v3.0.0 - 2026-06-19 知识库升为主舞台：独立界面 + 聊天降为侧栏

### 架构重构（核心）
知识库从"聊天框的弹窗附属"升级为**主舞台**，聊天降为**右侧可折叠侧栏**。
符合 Obsidian/Notion 的科研知识库体验。

### 新布局
```
左:会话栏 │ 中:知识库主区(文件树+内容预览双栏) │ 右:聊天侧栏(可折叠)
```

### 知识库主区（中间双栏）
- 左半文件树（280px）：🗺️MOC / 📐概念 / 🛠️方法 / 👤人物 / 📚综述 / 📁项目 / 📄论文库
- 右半内容预览：复用 openWikiDetail（[[]]双链/related chip/反向关联均可点击）
- 搜索框实时搜索，结果替换树

### 聊天侧栏（右侧可折叠）
- 聊天功能全部移入，收起时变 40px 细条，状态存 localStorage
- 聊天逻辑不退化（sendMessage/SSE/@注入不变）

### 验证：self_test 88/88 全绿，三栏布局正确

## v2.9.5 - 2026-06-19 知识库交互修复：双链可点击+搜索+raw预览+7个bug

### 核心修复：让知识网络真正连通
之前数据层建好了（MOC/双链/related/图谱），但展示层把所有关联渲染成纯文本，
知识网络在 UI 里是断的。本次让所有关联都可点击跳转。

### 7 个 Bug 修复
- **BUG-1** 打开文件夹 404：openLocalFile 裸 'knowledge' 被错加前缀 → 修复判断
- **BUG-2** MOC 详情 [[]] 双链不可点击（最严重）→ 渲染成可点击链接，点击跳转
- **BUG-3** related 字段纯文本 → 渲染成可点击 chip
- **BUG-4** raw 列表点击无反应 → 新增 openRawDetail 预览弹窗
- **BUG-5** .kb-tab 选择器跨面板冲突（污染学习面板）→ scope 到 #kb-manager-overlay
- **BUG-6** confidence NaN → 兜底 `?? 0`
- **BUG-7** onclick 路径未转义 → 统一转义单引号

### 新功能
- **知识库搜索框**：wiki tab 顶部加搜索框，接已有 /api/knowledge/search，支持跨类型按关键词找概念
- **按标题跳转 openWikiByTitle**：[[wikilink]] 和 related chip 共用，模糊匹配 title/path
- **反向关联展示**：wiki 详情底部显示"被哪些笔记关联"（调 /api/knowledge/related）
- **CSS 双链样式**：.kb-wikilink 虚线下划线 + .kb-related-chip 圆角标签

### 验证
- self_test 88/88 全绿
- 搜索 API 返回正确结果（三步模型 3 条）
- MOC 双链、related chip、raw 预览均可点击

## v2.9.4 - 2026-06-19 知识库专项优化：修bug+分层结构+MOC+标签体系

### 第一层：修 Bug
- **打开文件 404 修复**：openLocalFile 补 knowledge/ 路径前缀
  - 根因：wiki/raw 列表传的路径相对 knowledge/，后端按项目根拼接（缺前缀）
  - 修复后点知识库面板里的文件能正常打开

### 第二层：数据治理（一致性）
- **6 篇综述补 frontmatter**：hhg-methods/principles/comprehensive/systems/technology/teams
  - 全部补全 type/tags/related/growth_stage/confidence（之前完全无或残缺）
- **图谱治理**：
  - 26 条边补 type 字段（related/pioneered/same_as）
  - 9 个节点 type 统一为复数（concept→concepts, method→methods, person→people）
  - 连接孤立节点 attosecond → 高次谐波产生
- 结果：27 节点 27 边 0 孤立，33 篇 wiki 全有 frontmatter

### 第三层：分层结构（让知识库"好用"）
- **MOC 索引页（Map of Content）**：
  - `wiki/concepts/MOC-HHG.md` — HHG 知识地图（理论/材料/方法/人物/应用/综述）
  - `wiki/projects/NSFC-强场超快/MOC.md` — NSFC 课题入口（T1-T5/概念/方法/论文）
  - `wiki/projects/deepxiv-论文库/MOC.md` — 论文库索引（61篇/归档说明）
- **标签体系规范化**：33 篇 wiki 追加分类维度标签
  - `#type/concept` `#type/method` `#type/person` `#type/report` `#type/MOC`
  - `#topic/HHG` `#topic/固体HHG`
  - `#status/mature` `#status/growing`
- **前端分层浏览**：loadKbWiki 重写
  - 顶部 MOC 知识地图入口（主题漫游起点）
  - 按 type 折叠分组（概念/方法/人物/综述/项目）
  - 每组按 growth_stage 排序（mature 优先）
  - 显示 project 子库标签

### 成果
- 知识库从"平铺列表"升级为"分层结构 + MOC 主题入口"
- 符合好知识库标准：原子化笔记 + 双向链接 + MOC + 标签体系
- 94 文档（61 raw + 33 wiki），27 节点 27 边 0 孤立

### 验证
- self_test 88/88 全绿
- 33 篇 wiki 全有 frontmatter，图谱 0 孤立
- 打开文件不再 404

## v2.9.3 - 2026-06-18 知识库整理 + 文献流程修正（感兴趣≠归档）

### 知识库整理（确保 hermes 工作连贯性）
- **清理**：删除 1 篇无深度解析的 hermes 简报、移动 1 篇边缘量子光学笔记到 _archive/
- **图谱清理**：删除 16 个悬空 paper_2026 节点 + 5 个孤立英文冗余节点（48→27 节点）
- **标签重命名**：raw/papers 的 project 从"文献简报"→"deepxiv-论文库"（消除命名误导）
  - 这 55 篇是 deepxiv 真实论文元数据，不是简报
- **子库目录**：wiki/projects/文献简报 → wiki/projects/deepxiv-论文库
- **文档更新**：knowledge/README.md 重写，明确 project 字段与子库分类规范
- 图谱：27 节点 26 边，仅 1 孤立节点

### 文献流程修正（核心逻辑修复）
**之前（错误）**：👍感兴趣 → 立即归档（归档了不充分理解的内容）
**现在（正确）**：
```
未看 → [👍感兴趣] → 已看未讨论 → [💬讨论完成] → 归档（深度沉淀）
```
- 👍 感兴趣：仅记录偏好 + 移入"已看未讨论"池，**不归档**
- 💬 讨论：注入知识库 → 林赛讨论（充分理解论文）
- 📥 归档沉淀：讨论完成后的最终动作，归档+深分析+wiki建议
- 归档 = 对论文有足够了解后的知识沉淀，不是瞬间的感兴趣

### 候选池状态机重构
- `interested` → viewed（不再 archived）
- 新增 `discuss_done` 动作 → archived（讨论完成后归档）
- 已看未讨论区：💬讨论 + 📥归档沉淀 两个操作
- 状态标签优化：🔔未看 / 📖已看未讨论 / ✅已归档（深度沉淀）

### 验证
- self_test 88/88 全绿
- hermes 连贯性：SOUL.md 软链接正常、4 cron 活跃、45 篇候选可读

## v2.9.2 - 2026-06-18 NSFC 面板重构 + 异步协作框架（hermes干活↔知识库↔林赛讨论）

### NSFC 面板三区重构
- **区域1 课题产物**：T1-T5 + 共性顶层，卡片网格展示（进度/版本/大小/参考数），点击展开文档
- **区域2 调研资料**：references(16篇) + knowledge_base(concepts/methods) + daily_brief(7份)，折叠列表
- **区域3 待决策项**：从 state.md 提取，每项可 ✓通过/✗否决/💬讨论
- 替换了原来照搬 state.md 区块的混乱展示

### 通用异步协作框架
**hermes 干活 → 知识库 → 林赛讨论 → 反馈 → hermes 再干活**
- 待决策项「💬 讨论」：注入该课题知识库到聊天框 → 林赛基于知识库讨论 → 总结写 discussions/ → 异步反馈 hermes
- 通过/否决：持久化到 memory/nsfc-decisions.json + 异步反馈 hermes
- 林赛和 hermes 不直接交互，通过知识库（discussions 文件）异步通信

### 讨论→反馈闭环
- `POST /api/projects/nsfc/pending/<id>` — 决策（approve/reject/discuss）
- `POST /api/projects/nsfc/discuss-summary` — 总结讨论 → 写 discussions/ + 反馈 hermes
- 讨论工具栏：显示"📝总结讨论"按钮 → 林赛生成总结 → "✓提交总结到discussions"
- 决策状态持久化：memory/nsfc-decisions.json（approved/rejected 不再显示）

### 新增后端数据
- `get_nsfc_topics()` — 6 课题卡片（T1-T4 mature 100KB+，T5 seedling）
- `get_nsfc_references()` — 16 references + 7 概念/方法 + 7 简报
- `get_nsfc_pending()` — 结构化待决策项（合并持久化状态）
- 新增 API：/nsfc/topics /nsfc/references /nsfc/pending /nsfc/pending/<id> /nsfc/discuss-summary

### 验证
- self_test 88/88 全绿
- 6 课题卡片渲染、23 调研资料、待决策项通过/讨论闭环

## v2.9.1 - 2026-06-18 候选池三状态 + @知识库文件讨论 + 智能分类回填

### 候选池三状态持久化
- **新增 `scripts/paper_pool.py`**：候选论文生命周期管理（unseen→viewed→archived）
- 未看的候选**累积保留**在池中，不因新一天而清空——你随时回来继续
- 新增「⏰ 稍后」操作：标记为 viewed（已看未讨论），留待后续
- 前端按三状态分组渲染（🔔未看 / ⏰已看未讨论 / ✅已归档）
- 新增 API：`GET /api/projects/papers/pool`（支持 status 过滤）

### @知识库文件讨论
- **🗂️ 按钮**：点击弹出知识库文件树（按类型分组），勾选 1-N 个文件注入讨论上下文
- **@补全**：输入框打 @ 触发文件名补全，选中后用 `[文件名]` 标记
- 发送消息时自动读取选中文件内容（截断 2000 字）拼接到消息后
- 新增 API：`GET /api/knowledge/files`（文件列表）、`GET /api/knowledge/file-content`（读内容）
- 文献卡的「💬 讨论」按钮：一键把文献信息填入聊天框 + 注入知识库上下文

### 智能分类回填
- 给现有 61 篇 raw 论文批量补 `project` frontmatter 字段
- 按方向自动分类：55 篇→文献简报子库，6 篇→NSFC-强场超快子库
- 知识库检索现在支持按子库过滤（search 的 project 参数）

### feedback 端点增强
- 新增 `later` 动作（稍后讨论）
- 所有动作联动候选池状态流转
- skip/later 均标记为 viewed（保留可追溯）

### 验证
- self_test 88/88 全绿
- 候选池 45 篇入池，三状态正确
- 知识库文件 API + 内容读取正常

## v2.9.0 - 2026-06-18 以知识库为核心的科研协作工作流

### 用户需求重构
界面是基本需求（文献卡+进度展开），知识库是核心（反馈→深读→归档→分类→生长），讨论是轻量的。

### 文献卡小红书式卡片流
- 每篇候选文献一张卡片（标题/作者/方向/评分/TL;DR），纵向滚动流
- 三个操作按钮：👍感兴趣 / 👎跳过 / 📥归档，操作后卡片淡出移除
- 👍 触发：归档 raw + 导入深分析 + 生成 wiki 笔记建议 + 异步反馈 hermes 偏好

### 申请书进度层次展开
- 新增 `parse_nsfc_state_hierarchical()`：state.md → 三层结构（区块→表格行→文件路径）
- 前端渲染为可折叠 `<details>` 树，关键区块默认展开（当前Phase/待决策/风险）
- 表格行/列表项提取文件路径，点击 📄 按钮加载文档内容（第3层）

### 知识库智能生长（归档自动 + wiki 确认）
- `suggest_wiki_notes(arxiv_id)`：从深分析的 core_findings/linsai_connection 提取概念和关联建议
- 👍 处理后弹出确认弹窗：勾选要生成的概念笔记和图谱关联，确认后生成
- 生成的笔记标记 seedling（confidence 0.4），邀请用户补充
- `grow_from_suggestion()`：按确认结果生成 wiki 笔记 + 连图谱边

### 子库自动分类
- `infer_project(direction)`：按方向关键词自动归入对应子库
  - "固体HHG"/"2D材料"/"拓扑" → NSFC-强场超快 子库
  - 默认 → 文献简报 子库
- import_candidate/import_deep_analysis 自动使用

### hermes 偏好反馈闭环
- 👍/👎 时异步调 `hermes_bridge.oneshot()` 反馈用户偏好（fire-and-forget，不阻塞 UI）
- 本地 `memory/paper-feedback.json` 累积偏好数据

### 新增 API
- `GET /api/projects/nsfc/tree` — 层次结构树（12 区块）
- `POST /api/projects/papers/feedback` — 文献反馈（interested/skip/archive）
- `POST /api/knowledge/suggest` — 查询 wiki 建议
- `POST /api/knowledge/grow` — 按确认生成 wiki 笔记

### 验证
- self_test 88/88 + web_api 26/26 全绿
- 实测：tree 返回 12 区块、feedback(skip/archive) 正常、suggest 返回 8 概念

## v2.8.0 - 2026-06-17 虚拟用户测试 + 前端 bug 修复 + 知识库全套整理

### 第一块：Web API 虚拟用户测试框架
- **新增 `scripts/tests/test_web_api.py`**：基于 test_runner 框架的 HTTP 虚拟用户测试套件
  - ApiClient（urllib 零依赖）：GET/POST/PUT/DELETE + JSON 编解码 + 状态码断言
  - WebApiSuite：启动 web_server 子进程（隔离环境），26 个测试用例覆盖所有 API
  - 接入 self_test：`python3 scripts/self_test.py --web`（26/26 通过）
  - web_server.py 加 `--root` 参数支持隔离测试环境

### 第二块：前端 bug 修复
- **P0 崩溃修复**：补全 learning manager 4 个缺失函数（openLearningManager/closeLearningManager/renderLearningManager/switchLearningTab），点击🌱自主学习按钮不再报错
- **P1 任务按钮**：修复 `.task-panel`/`.right-panel` 选择器 → `getElementById`
- **P1 任务新建/删除**：task-panel 加「+新建」表单 + createNewTask/deleteTask 函数 + 后端 POST/DELETE /api/tasks 路由
- **P2 导出会话**：实现 export-btn 真导出（生成 .md 下载，不再是"开发中"）
- **P2 死代码**：删除 #back-to-current 遗留绑定

### 第三块：知识库数据修复
- **methods-report 重复 bug**：截断 hhg-methods-report.md（1510→735 行，删除 775 行重复）
- **graph 悬空边**：清理 16 条全空 source/target 的坏边
- **principles 标题 bug**：修复 Python list 字面量未解包的标题

### 第四块：知识库全套整理（补 HHG 核心原子笔记）
- **concepts 新增 8 篇**：三步模型/截止定律/相位匹配/水窗口/Lewenstein模型/固体高次谐波/液体高次谐波/高次谐波产生（HHG总论）
- **methods 新增 8 篇**：RABBITT/FROG/瞬态吸收光谱/VMI/COLTRIMS/阿秒条纹相机/协方差映射/TDSE求解器
- **people 新增 5 篇**：Corkum/Krausz/LHuillier/Ghimare-Reis/北大HHG团队
- **拓扑绝缘体补完**：seedling(0.3) → growing(0.7)，补充实质内容
- **aliases.json**：从空 → 25 组中英/缩写对照（HHG=高次谐波产生、三步模型=three-step-model 等）
- **图谱重建**：48 节点 26 边（原 32 节点 0 边），0 孤儿，核心概念/方法/人物互联
- **growth-log**：补充 8 条整理事件记录

### 成果数据
- wiki 条目：9 → 30（mature 12 / growing 5 / seedling 1）
- 知识库检索：别名扩展生效（"HHG"→高次谐波产生、"RABBITT"→重建阿秒拍频干涉）
- 测试：self_test 88/88 + web_api 26/26，全绿不回归

## v2.7.0 - 2026-06-17 hermes 协作中枢：林赛 Web 作为双 hermes 工作流的指挥台

### 架构定位
hermes（+ profile linsai）是"大脑和手脚"——自主执行论文简报 cron、NSFC 工作流 cron。
林赛 CoPilot Web 升级为"指挥台和档案室"——可视化产出、控制 cron、沉淀知识、多端汇聚。

### 新增 5 个核心脚本
- `scripts/project_reader.py`：解析 NSFC state.md（进度/待决策/路线图）、discussions（决策卡）、topics（申请书章节）、文献候选/简报
- `scripts/kb_importer.py`：把 hermes 产出（daily_candidates/deep_analysis JSON）转换为林赛知识库 markdown，沉淀到「文献简报」子库
- `scripts/hermes_bridge.py`：控制 hermes cron（list/pause/resume/run）+ 手动派活（oneshot agent loop）
- `scripts/sync_engine.py`：多端同步层，扫描 hermes 248 个会话/文献产出 → 导入林赛（幂等去重）
- 知识库子库改造：`knowledge_base.py` 支持 projects/ 子目录、project 字段过滤检索、图谱 belongs_to 边

### 新增 12 个 API 端点
- **项目数据**：`/api/projects`、`/api/projects/nsfc/{dashboard,decisions,chapters,proposal}`、`/api/projects/papers/{candidates,briefings}`
- **hermes 控制**：`/api/hermes/cron`、`/api/hermes/cron/<id>/{pause,resume,run}`、`/api/hermes/run`（SSE 流式）
- **导入沉淀**：`/api/import/paper`、`/api/sync/{status,run}`

### 新增前端
- 工具栏加 📂 项目面板 + ⚡ hermes 控制台两个按钮
- `web/js/projects.js`：NSFC 仪表盘（阶段/待决策/风险/路线图/决策时间轴）+ 文献候选表格（勾选导入）+ 多端同步
- `web/js/hermes_console.js`：cron 列表（启停/触发）+ 手动派活（hermes agent loop 流式输出）

### 知识库子库架构
- `knowledge/wiki/projects/文献简报/` 和 `NSFC-强场超快/` 两个子库
- frontmatter 新增 `project` 字段，search() 支持 `project=` 过滤
- 图谱自动连接 项目节点→子内容（belongs_to 边）
- 文献简报子库可作为 NSFC 项目的知识来源（跨子库互联）

### 写回策略（安全）
- 林赛讨论结论只写 hermes 的 `discussions/`（BRAIN 必读输入），不直接改申请书内容
- 文献讨论沉淀写林赛自己的 `knowledge/wiki/projects/文献简报/`

### 验证
- `py_compile` 全量通过 + `self_test` 88/88 全绿
- 5 个新脚本自检全部通过
- web_server 实测：12 个 API 返回 200，前端面板渲染正常
- NSFC 仪表盘：3 BRAIN 区块 / 5 待决策 / 20 路线图行 / 5 条决策
- 文献候选：55 篇可导入，子库检索验证通过
- hermes cron：6 个 job 正确读取，网关 running

## v2.6.2 - 2026-06-17 代码瑕疵修复 + 知识库索引重建 + 会话摘要链路接通

### 修复 3 处代码瑕疵
- `tool_engine.py`：删除 `tool_run_command` 的死代码（return/except 后重复的整段函数体 L709-766，永不执行）
- `learning_engine.py`：自检 `[4/5]` 调用未定义的 `_build_wikipedia_distill_prompt` → 改用运行时实际使用的 `_build_web_search_distill_prompt`（之前手动自检会 NameError）
- `research_profiler.py`：漂移分支调用未定义的 `_import_kb()` → 改用 `import knowledge_base as kb`（之前被 try/except 静默吞掉，导致生长日志少记）

### 重建知识库索引（修复严重脱节）
- `knowledge/index.json`：死链 74 → **0**（74 条引用不存在文件的陈旧索引已清除），doc_count 8 → 739，built_at 更新至今日
- `knowledge/graph.json` + `index.json` 的 `graph_summary`：**完全同步**（节点 32 / 边 16，之前 index 缓存的 summary 停在 2 节点/3 边）
- 清理 17 个指向不存在论文的孤儿图谱节点
- 检索功能恢复可信：`search("三步模型")` → principles-report score=0.44（TF-IDF 真实打分）

### 接通会话摘要链路（CoPilot 记忆能力起点）
- `session_manager.archive_session()`：归档时自动调用 `memory_manager.generate_session_summary()`，替代创建时的占位符 `"> 会话摘要预留位置"`
- 摘要生成失败不阻塞归档（降级保留占位）
- 端到端验证通过：创建→加消息→归档→摘要含真实内容 + 长期记忆索引同步更新

### 验证
- `py_compile` 全量通过 + `self_test` 88/88 全绿
- `learning_engine` 自检 5/5 通过（之前 [4/5] NameError）

## v2.6.1 - 2026-06-17 项目健康度清理：补回幽灵脚本 + 恢复 Web + 修包 import

### 补回缺失脚本（被 4d3969e 误删或从未实现）
- **新增 `scripts/version.py`**：集中读取 VERSION 文件，提供 `get_version()` / `__version__` / `parse_version()` / `is_newer()`，消除三处人工版本号同步点
- **补回 `scripts/backup_manager.py`**：数据备份/恢复（zip 打包 + `auto_backup()` 24h 跳过 + `--list/--restore/--only` + 恢复前应急备份），修复 `copilot_engine.py` 的 `from backup_manager import auto_backup` 静默失效
- **补回 `scripts/upgrade.py`**：安全升级流程（备份→语法验证→迁移→自测→可回滚），支持 `--check/--simulate/--self-check`，修复 README/AGENTS 的 SOP 命令照抄报错
- **从 git 历史（30b12d7）恢复** 4d3969e 误删的脚本：
  - `scripts/web_server.py`（1165 行）+ `web/` 前端三件套（index.html/css/js，4533 行）—— Web 界面能力恢复
  - `scripts/deep_audit.py`（622 行）：9 维度架构稳定性审查
  - `scripts/learning_quality_tracker.py`（501 行）：交互质量追踪
  - `scripts/test_e2e_learning.py` / `test_e2e_learning_full.py`（共 578 行）：端到端测试

### 修复包 import 模式（可被作为 Python 包 import）
- `scripts/deepxiv_knowledge/{paper_writer,pdf_enricher,run}.py`：绝对 import → `try/except` 双模式（包模式优先，脚本模式回退），修复 `import deepxiv_knowledge` 崩溃
- `scripts/wiki_regenerator/{report_writer,run}.py`：同上处理

### 文档与版本号同步
- **版本号统一到 2.6.0**：`VERSION`（2.1.0→2.6.0）、`README.md`（2.0.0→2.6.0）、`AGENTS.md`（2.0.0→2.6.0）、`scripts/README.md`（2.2.0→2.6.0）
- **修文档失实**：
  - `README.md` / `AGENTS.md` 目录树按磁盘真实情况重写（补 slash_commands/version/deepxiv_knowledge/wiki_regenerator，删不存在的 upgrade_wiki_for_obsidian）
  - `docs/README.md`：取消 v2.1.0 计划"当前有效"声明（改为"已实现，归档"），补齐 4 份 HHG 调研报告清单
  - `scripts/README.md`：脚本统计口径更新（23 主脚本 + 两个流水线包）
- **修代码注释**：`tool_engine.py:14` 残留的 `v2.1.0 Phase 0` 注释修正

### 第一代草稿脚本清理（v2.6.0 已由第二代流水线取代）
- 删除 6 个第一代 HHG 脚本：`hhg_paper_fetcher.py` / `fetch_hhg_new_papers.py` / `ss_search_hhg.py` / `extend_papers.py`（含语法错误 + 编造数据）/ `hhg_batch_writer.py` / `update_graph.py`

### 验证
- `py_compile` 全量通过（含恢复的 web_server/deep_audit 等 + 两个子包）
- `import deepxiv_knowledge` / `import wiki_regenerator.paper_reader` 包模式 import 成功
- `backup_manager --self-check` / `upgrade --self-check` / `version` 自检通过

## v2.6.0 - 2026-05-22 方法完备性评估（按方法逐一要素级审查）

### 完备性评估集成
- 替换通用检查清单（第 785-796 行）为 **12 个方法的逐一要素级完备性评估**（来自 `solid-HHG-completeness-by-method.md`）
- 每个方法含：动力学方程、观测量计算、近似、参数 → ✅/❌ 状态 + 原文内容 + 复现障碍说明
- 关键缺失项（影响复现）：
  - 双层石墨烯 SBE：k 点网格密度、时间步长
  - Na₃Bi TDDFT：时间步长
  - Cd₃As₂ Boltzmann：数值积分格式、动量采样密度
  - Rashba SOC TDSE：系统格点数、时间步长
  - 莫特 Hubbard DMFT：DMFT solver 类型、晶格大小
  - YBCO 准 Hubbard：基态求解格式、EOM 积分格式、U_eff
  - 扭转 h-BN：χ 系数（唯象理论，无从头算参数）
- 新增 **完备性总表**（第 980-995 行）：12 方法 × 4 要素矩阵

### 文件变更
- `docs/solid-HHG-by-material-system.md`：831 → 1029 行（+198 行）

## v2.5.0 - 2026-05-21 凝聚态 HHG 计算方法调研（按材料体系分类，v3，全文原文提取）

### 调研报告重建（v3）

- `docs/solid-HHG-by-material-system.md`（**31 KB，831 行**）：按材料体系分类的凝聚态 HHG 计算与分析方法调研
- **全面联网检索**（arXiv API）确认凝聚态 HHG 已覆盖的 9 个材料体系类别
- **全部内容严格来自已获取论文原文**，无任何生成内容，每节末尾标注来源 arXiv ID

### 调研覆盖的 9 个材料体系

**体系一：宽禁带介电体/绝缘体**
- `1807.02961` — Le Breton et al. (2018)：h-BN，Octopus TDDFT，Δx=0.28 Bohr，k: 32²–54³
- `1607.00747` — Otobe (2016)：α-石英，mBJ，Δt=0.02 a.u.，HH19(30 eV)
- `2508.15076` — Kuzkova et al. (2025)：MgO，XUV 干涉偶极子相位测量，三层次 SBE/Wannier

**体系二：传统半导体**
- `1805.10453` — Klemke et al. (2018)：Si，TDDFT，偏振分辨，HH5 纯带内，HH7 耦合，HH9 主要带内
- `2004.04492` — (2020)：GaAs，Luttinger-Kohn 模型，非扰动 HHG

**体系三：2D 材料**
- `2011.12252` — (2020)：石墨烯，SBE 紧束缚，t₀=2.7 eV，t⊥=0.48 eV，双层石墨烯
- `2111.10986` — Lee et al. (2021)：MoS₂，Berry 曲率公式，伪自旋谷选择定则
- `1807.02961` — 单层 h-BN 原子样 HHG，E_c = E_w + 3.17U_p

**体系四：拓扑材料**
- `1806.11232` — Silva et al. (2018)：Haldane 模型，Chern 数控制谐波螺旋度
- `2103.09322` — Tancogne-Dejean et al. (2021)：Na₃Bi，Octopus SOC TDDFT，Δr=0.36 Bohr
- `2405.16125` — Zhang et al. (2024)：TaAs，Jones 矩阵形式，晶体对称性 vs 拓扑
- `1911.01476` — Kovalev et al. (2019)：Cd₃As₂，Boltzmann 输运，τ=10 fs，THz HHG

**体系五：扭转/双层材料**
- `2503.08052` — Ma et al. (2025)：扭转 h-BN，相位匹配，效率 ~1.5×10⁻⁵
- `2011.12252` — AA/AB 堆垛双层石墨烯（已在上方体系三中）

**体系六：磁性/SOC 材料**
- `1906.10224` — Mrudul S. et al. (2019)：自旋极化缺陷，TDDFT
- `2104.04001` — Ly & Manchon (2021)：Rashba SOC，紧束缚 TDSE，谐振条件 α_R k_F/J ≈ 1

**体系七：关联电子材料**
- `2203.01029` — Murakami et al. (2022)：莫特绝缘体，DMFT + Hubbard，U
- `2409.04216` — Tyulnev et al. (2024)：TiSe₂ CDW，HH5 异常各向异性，Tc=205 K
- `2201.09515` — Alcalà et al. (2022)：YBCO，两带准 Hubbard + BCS，Tc=88 K，T*=173 K

**体系八：手性 HHG**
- `2306.02313` — (2023)：石墨烯，ω+2ω co-rotating，产生同螺旋度圆谐波

**体系九：气体相位匹配**
- `2404.01325` — Popmintchev et al. (2024)：Δk 方程，η_CR ∝ λ_L⁻²，He ~330 eV（水窗）

### 方法论改进

- 增加体系分类（9 大类）而非理论模型分类
- 每个体系均包含计算方法、软件、关键参数（数值）
- 增加跨体系方法对比树：拿到一个材料 → 确定体系 → 选择方法
- 增加方法完备性检查清单（k 点、网格、时间步长、带数、CAP、SOC、关联）

## v2.4.0 - 2026-05-19 固体 HHG 计算方法调研（按材料体系分类，v2）

### 调研报告重建（v2）

- `docs/solid-HHG-computation-by-material.md` → **完全重写**（28.7 KB，850 行）
- **全部内容严格来自已获取论文原文**，无任何生成内容
- 每节末尾标注来源 arXiv ID

### 本次重新获取的论文（共 8 篇）

**体系一：h-BN**
- `1807.02961` — Le Breton, Rubio, Tancogne-Dejean (2018)：Octopus TDDFT 参数（Δx=0.28 Bohr，k: 32²–54³），激光 1600 nm，面内/层方向 HHG，带隙 4.50–4.87 eV

**体系二：α-石英**
- `1607.00747` — Otobe (2016)：实时 TDDFT，mBJ 交换势，网格 26×44×38，k: 8³，Δt=0.02 a.u.，HH19（30 eV），主导机制：电子-空穴复合

**体系三：Si / 石英偏振分辨**
- `1805.10453` — Klemke, Tancogne-Dejean et al. (2018)：实验参数（Si: 2 μm，(100)，2.1 μm，120 fs，0.6 TW/cm²；石英: 50 μm，z-cut，40 TW/cm²），HH5 纯带内，HH7 耦合，HH9 主要带内

**体系四：拓扑材料**
- `1806.11232` — Silva, Jiménez-Galán, Smirnova, Ivanov (2018)：Haldane 模型参数，Chern 数 ν 控制谐波螺旋度，λ=3 μm，E₀=4×10⁹ V/m

**体系五：2D 材料与谷电子学**
- `2203.10253` — Luu (2022)：SBE vs TDDFT 对比，有隙/无隙石墨烯，谷极化
- `1906.10224` — Mrudul S., Tancogne-Dejean, Rubio, Dixit (2019)：h-BN 自旋极化空位缺陷，TDDFT，电子-电子相互作用必须包含

**体系六：气体 HHG 相位匹配**
- `2404.01325` — Popmintchev et al. (2024)：Δk 方程，η_CR 公式（∝λ_L⁻²），相位匹配截止 ∝ λ_L^1.6-1.7，He: ~330 eV，λ→3 μm: ~1 keV

**体系七：量子光学**
- `1910.13791` — Gorlach, Lewenstein et al. (2019)：SFQED 框架，三步方案，组合波函数（纠缠态），每个 HHG 光子是整个频谱的叠加

**体系八：分子自探测**
- `2103.16228` — Haessler, Caillat, Salières (2021)：自探测范式，ADK + Lewenstein，轨道断层成像，多电子动力学

### 方法论改进

- 明确区分哪些内容来自哪些具体论文
- 每个体系的参数均为原文提取（如 h-BN 的 Δx=0.28 Bohr，α-石英的网格 26×44×38）
- 删除了所有凭记忆补充的内容（ZnO SBE 参数、MoS₂ Berry 曲率具体公式等）

## v2.3.0 - 2026-05-19 固体 HHG 计算方法调研（按材料体系分类）

### 调研报告新增

- `docs/solid-HHG-computation-by-material.md`（**20.3 KB**）：按 6 大材料体系组织的 HHG 计算与分析方法调研

### 体系一：宽禁带介电体

- h-BN（单层→体材料层数演化，TDDFT 参数，Octopus 设置，Le Breton 2018）
- α-石英（Otobe 2016）：mBJ 赝势，TDDFT 设置，HH19（30 eV）

### 体系三：传统半导体

- Si（Klemke et al. 2018）：(100)取向，2 μm 厚度，2.1 μm 驱动，TDDFT 参数，偏振分辨

### 体系四：拓扑材料

- Haldane 模型（Silva et al. 2018）：Haldane Hamiltonian，拓扑相变条件，Chern 数→谐波椭圆率切换

## v2.2.0 - 2026-05-19 固体 HHG 理论调研报告重建（正确检索流程）

### 调研报告重建

- 重写 `docs/solid-HHG-theory-methods-survey.md`：从 285 KB 原始文件提炼为 **23.5 KB** 结构化报告
- **全部内容均直接来自论文原文**，通过 arXiv API 检索 → deepxiv CLI 逐篇获取，无任何生成内容
- 纠正前期 ID 漂移问题：所有 13 篇论文均经检索验证 arXiv ID 正确性

### 新增核心文献（SBE 理论方向）

- `2102.11964` — Yue & Gaarde (2021)：全 BZ 隧穿 + 不完美回碰，SBE 鞍点方程
- `2003.02961` — Yue & Gaarde (2020)：速度/长度规范系统比较，h-BN 实例，Berry 联络规范依赖
- `2508.07869` — Thümmler & Lettau (2025)：Wannier 规范 SBE + 平滑退相干算符（SDO），FFT 加速
- `1904.00283` — Silva, Martín, Ivanov (2019)：MLWF 构造平滑偶极矩阵元，h-BN 2 带收敛性

### 新增核心文献（量子光学+Berry 方向）

- `2312.08942` — Lange, Hansen, Madsen (2023)：Fermi-Hubbard 模型，电子关联→非经典光（压缩态/纠缠）
- `2111.10986` — Lee, Kim (2021)：MoS₂ 单层/双层 Berry 曲率公式，伪自旋 HHG 选择定则
- `1902.03421` — Yoshikawa et al. (2019)：谷极化 e-h 对，带间共振，MoSe₂/WSe₂/MoS₂/WS₂ 实验参数

### 新增核心文献（相位匹配+隧穿方向）

- `2404.01325` — Popmintchev et al. (2024)：相位失配公式，临界电离度，水窗（~330 eV），3 μm 驱动→多 keV
- `2104.06144` — Wang et al. (2021)：attoclock 隧穿时间，TCCSFA（Feynman 路径积分），24–58 as 隧穿延迟

### 检索方法规范化

- 确立正确流程：**arXiv 检索 → 人工验证 → deepxiv 获取**，摒弃凭记忆猜 arXiv ID 的做法（ID 复用导致漂移）
- 检索关键词：solid high harmonic generation theory Berry curvature semiconductor Bloch / high harmonic phase matching / high harmonic quantum optics
- deepxiv reader.py 编码 bug 修复（latin-1 → utf-8）已在本轮调研前完成

## v2.1.1 - 2026-05-19 deepxiv 知识库 v6 + PDF 全文增强

### 新增（deepxiv 流水线）

- `scripts/deepxiv_knowledge/pdf_extractor.py` — PDF 全文提取模块（PyPDF2）：碎片化检测、affiliation 过滤、章节解析、要点提取
- `scripts/deepxiv_knowledge/pdf_enricher.py` — PDF 增强流水线：`--all`（top 20）/ `--rebuild`（全量 61 篇）
- 扩展调研：新增 20 篇论文（实验方法 8 篇 + 光谱学原理 12 篇），总数 41 → **61 篇**

### 改进（fetch_core.py）

- 新增 `_extract_sections_from_head()`：优先使用 deepxiv 官方 section TLDR 解析（46 篇已用）
- 节名过滤：排除 Acknowledgment / References / Appendix 等非实质节
- 降级策略：head sections → preview → tldr 兜底
- `paper_reader.py` YAML 列表解析：修复 `"a, b, c"` 被逐字拆分的 bug

### 改进（run.py）

- v5 → **v6**：新增 `--rebuild` 强制重建标志
- 新增分支：sections 存在但无匹配节 → 回退 preview（无需重新获取 head）

### 内容质量（61 篇平均）

| 指标 | 增强前 | + PDF 增强后 |
|------|---------|---------------|
| 关键科学问题 | 1.0 条/篇 | **3.0 条/篇** |
| 核心发现 | 2.6 条/篇 | **6.0 条/篇** |
| 完全为空 | >0 篇 | **0 篇** |
| raw papers 大小 | ~40 KB | **285 KB** |

### 文档更新

- `docs/deepxiv-knowledge-workflow.md`：v5 → v6，新增 PDF 增强章节、数据源优先级 v6
- `scripts/README.md`：新增 deepxiv_knowledge / wiki_regenerator 模块清单

### 配置

- `~/.kimi/config.toml`：`max_steps_per_turn` 100 → **200**

### 已知问题

- `physics/9906053`（1999 年）无 PDF 存档，仅保留 abstract + tldr

---

## v2.0.0 - 2026-05-12 林赛自主学习引擎（5 阶段完整实施）

### 新增（自主学习引擎）

- `scripts/research_profiler.py` — 研究方向感知器：从用户画像/任务/会话动态提取研究关键词
- `scripts/external_fetcher.py` — 统一信息获取接口：deepxiv(arXiv) + Wikipedia API + raw/ 扫描 + 优先级排序
- `scripts/learning_engine.py` — 自主学习核心编排器：蒸馏/精读/概念提取/知识整合/图谱扩展/成本追踪/一键回滚
- `scripts/quality_evaluator.py` — 质量评估引擎：规则评估 + LLM 评估 + 对抗性多轮蒸馏 + 用户反馈闭环
- `memory/learning-config.json` — 学习策略与配额配置（自动开关/策略/来源/成本上限）
- `memory/research-profile.json` — 研究方向关键词（动态更新）
- `memory/learning-cost.json` — 学习成本追踪（日/月/按来源/按 Provider）
- `memory/learning-quality-log.json` — 质量评分历史
- `memory/learning-pending-queue.json` — 待审队列
- `memory/learning-user-edits.json` — 用户编辑追踪
- `knowledge/.cache/` — 网络获取结果缓存（arXiv 24h / Wikipedia 7d）
- `knowledge/.backup/auto-grown/` — 生长前自动备份

### 新增（Web 前端）

- 侧边栏工具栏新增 🌱 学习管理器入口
- 学习管理器模态框：3 标签页（📜 学习日志 / 📝 待审内容 / 📊 统计）
- 设置面板新增学习策略配置：自动开关、保守/平衡/激进策略、来源勾选、日配额、成本上限
- 手动触发学习按钮（带进度反馈）

### 新增（API 端点）

- `GET /api/learning/config` — 获取学习配置
- `POST /api/learning/config` — 更新学习配置
- `GET /api/learning/status` — 学习状态（成本/配额/调用次数）
- `GET /api/learning/queue` — 待审队列
- `GET /api/learning/log` — 质量评估日志
- `POST /api/learning/trigger` — 手动触发学习周期
- `POST /api/learning/review` — 审批/拒绝待审内容

### 新增（配套文档）

- `docs/CLAUDE-CLI-ADMIN.md` — Claude CLI 人工管理指南
- `docs/prompts/quality-audit.txt` — 质量审查 prompt 模板
- `docs/prompts/maintenance-audit.txt` — 维护审查 prompt 模板
- `docs/prompts/concept-merge.txt` — 概念合并 prompt 模板
- `docs/prompts/paper-deep-read.txt` — 论文精读 prompt 模板

### 改造

- `scripts/proactive_engine.py` — heartbeat() 新增第 5 类信号 `learning_opportunity`
- `scripts/knowledge_base.py` — 扩展图谱边类型（`supported_by`/`supports`/`extends`/`contradicts`）
- `scripts/web_server.py` — 新增 `/api/learning/*` 端点
- `web/index.html` — 新增学习管理器 DOM
- `web/js/app.js` — 新增学习管理器渲染逻辑

### 验证

- 5 个新模块自检全部通过
- **全量自测 88/88 通过** ✅
- 零破坏性：所有现有功能不受影响

---

## v2.1.0 - 2026-05-15 工具协作者 + 知识库三工作流

### Phase 0 — 工具协作者（v2.1.0）
- `scripts/tool_engine.py` — 新增 `tool_run_command()` + `tool_hermes_chat()`
  - run_command: subprocess 调用 CLI（kimi/claude/hermes/python/git），cwd 限制 + 危险命令黑名单
  - hermes_chat: 调用 `hermes --profile linsai -z`，获得 LinSai 完整人格 + 记忆的深度回答
  - 权限模型：禁止逃离项目目录的命令组合

### Phase 1 — 子代理工具（v2.1.0）
- `scripts/tool_engine.py` — 新增 `tool_agent()`，通过 `claude --agent explore/coder/plan` 调用子代理
- 8 个工具完整注册：calc / file_read / file_write / task_create / knowledge_query / run_command / hermes_chat / agent

### Phase 2 — 记忆加载自动化（v2.1.0）
- `scripts/context_builder.py` — `_read_lt_mem()` 返回实际内容（最近 10 条），`_read_work_ctx()` 过滤已逾期项目

### 知识库三工作流（v2.1.0）
- `tool_knowledge_research` — 工作流1-自动增加：Hermes调研 → 编译 → 写入wiki → 建双向链接
- `tool_knowledge_ingest` — 工作流2-手动增加：编译raw文件夹 → 建立双向链接 → 健康检查
- `tool_knowledge_create` — 工作流3-对话生长：创建概念存根 → 记录上下文
- 外部导入规范：raw/ 三级分类（papers/notes/webclips），林赛负责所有后续编译管理

### 斜杠命令系统（v2.1.0）
- `scripts/slash_commands.py` — 统一命令入口（719行）
  - 解析器支持 `/research` 和 `/research:topic:depth` 两种格式
  - 44 个思维视角动态加载（~/.claude/skills/）
  - `/skill:<name>` 激活视角，session state 注入 prompt
  - `/research` / `/ingest` / `/check` / `/session` / `/mode` / `/read` / `/help` / `/list`
- `scripts/copilot_engine.py` — chat_loop 统一拦截 `/` 前缀

### 修复
- `knowledge_base.py` — `_load_graph()` 处理 graph.json 为空对象 `{}` 的情况
- `.gitignore` — 补充 `knowledge/captures`

---

## v1.7.3 - 2026-05-12 Obsidian 前端兼容性改造

### 新增（Obsidian 兼容）

- `knowledge/.obsidian/` — 开箱即用的 Obsidian Vault 配置
  - `app.json`：新建文件默认放入 `wiki/concepts/`，附件放入 `assets/`
  - `appearance.json`：强调色 `#2563eb`（林赛品牌蓝）
  - `core-plugins.json`：启用图谱、反向链接、标签面板、页面预览等核心插件
- `knowledge/templates/概念笔记.md` — Obsidian 模板，frontmatter 结构完整
- `knowledge/README.md` — 知识库使用指南（含 Obsidian 使用说明）
- `scripts/upgrade_wiki_for_obsidian.py` — 一次性升级脚本，为现有 wiki 文件注入双向链接

### 改造（知识库引擎）

- `scripts/knowledge_base.py` — 全面支持 Obsidian 双向链接 `[[WikiLink]]`
  - 新增 `_extract_wikilinks()` — 从正文提取 `[[链接]]`
  - 新增 `_get_aliases_for_concept()` — 从 `aliases.json` 反向查找别名
  - 新增 `_inject_wikilinks()` — 自动在正文末尾注入 `<!-- linsai-wikilinks -->` 区域，同步 frontmatter `related` 与正文 `[[链接]]`
  - `build_frontmatter()` — 优化 YAML 输出格式，字符串转义更安全，空数组正确输出 `[]`
  - `save_wiki_page()` — 保存后自动注入 wikilinks 并同步图谱
  - `save_distilled_wiki()` — 蒸馏后自动注入 wikilinks
  - `apply_growth()` — 生长后自动注入 wikilinks
  - `build_index()` / `list_raw_files()` — 新增 `_should_index()` 过滤器，排除 `.obsidian/`、`.git/`、`__pycache__/` 等隐藏目录

### 影响

- 现有 2 个 wiki 页面已通过升级脚本注入 wikilinks 区域
- 新建/更新的 wiki 页面自动获得 `[[双向链接]]`，Obsidian 图谱可正确显示概念间连接
- frontmatter 新增 `aliases` 字段（来自 `aliases.json` 映射），Obsidian 别名搜索可用
- 全量自测 88/88 通过 ✅

## v1.7.2 - 2026-05-11 内测系统 — 影子用户自动化回归测试

### 新增

- `scripts/self_test.py` — 内测统一入口，支持命令行与程序化双接口
  - 命令行：`--module` / `--scenario` / `--persona` / `--json`
  - 程序化：`from self_test import run_tests; result = run_tests(["module"])`
- `scripts/tests/test_runner.py` — 零依赖轻量级测试框架，支持隔离环境、Monkey-patch、中文报告
- `scripts/tests/test_core.py` — 核心模块单元测试（会话 / 知识库 / 技能 / 任务 / 记忆 / 上下文）
- `scripts/tests/test_scenarios.py` — 场景剧本测试（5 类影子用户：并肩工作 / 深度对话 / 快速验证 / 任务驱动 / 主动感知）
- `scripts/tests/test_persona.py` — 人格一致性静态抽检（锚点 / 结构 / 表达 DNA / 反模式）
- `skills/self-test/SKILL.md` — 内测技能封装，触发词：内测/测试/回归测试/影子用户/健康检查

### 新增（深度评估与功能测试）

- `scripts/deep_audit.py` — 9维度深度评估脚本（代码质量 / 架构拓扑 / 数据完整性 / 边界条件 / 前端资产 / LLM引擎 / 安全审查 / 文档一致性 / 性能基线）
- `docs/DEEP-AUDIT-REPORT.md` — 深度评估报告（风险评分 150/1000，0 严重 0 高 0 中）
- `docs/FUNCTIONAL-TEST-REPORT.md` — 子代理模拟用户功能测试报告（65 个检查点，Web API 15/15 通过）

### 修复

- `scripts/copilot_engine.py:461` — `call_llm()` 返回值从单值改为 3 元组解包，修复 `AttributeError`
- `scripts/copilot_engine.py:108` — `detect_llm_cli()` 遍历 `status["providers"]` 而非字典键，修复 CLI 入口崩溃
- `scripts/web_server.py` — 新增 `PUT /api/tasks/{id}/subtasks` 和 `/progress` 路由，修复前端 API 调用失败
- `scripts/web_server.py` — `os.system` 替换为 `subprocess.run`，消除命令注入风险
- `web/index.html` — 版本标签 `v1.1.0` → `v1.7.2`
- `tasks/` — 修复 8 个任务文件状态与目录不一致
- `sessions/agora_exports/` — 修复 `invited_personas` 数据类型（字符串 `"t"` → 列表 `["费曼"]`）

### 验证

- 全量测试 88/88 通过（核心 34 + 人格 38 + 场景 16），总耗时 ~0.06s
- 深度评估：0 严重 / 0 高 / 0 中 / 150 低，风险评分 150/1000
- 子代理功能测试：Web API 15/15 通过，CLI 入口恢复正常
- 测试隔离：所有写入操作在临时目录进行，零污染真实数据
- 零第三方依赖，仅使用 Python 3 标准库

---

## v1.7.1 - 2026-05-09 知识库精细化 — 从"建库"到"浮现"

### 核心改进
- **对话自动捕获** — `scripts/kb_capture.py`
  - 检测技术参数（3个以上数字+单位）、用户明确请求（"记下来"）、工作模式长消息
  - 零 LLM 开销，保存到 `knowledge/captures/`
- **智能检索触发器** — `scripts/knowledge_base.py` 的 `should_search_knowledge()`
  - 闲聊/问候自动跳过，技术讨论才检索知识库
  - 节省 40-100% 的每轮对话知识库上下文开销
- **分级上下文注入** — `scripts/context_builder.py`
  - 高相关（score≥0.8）：注入全文摘要 300 字
  - 中相关（0.4≤score<0.8）：只注入标题 + 一句话 + 路径链接
  - 低相关（score<0.4）：不注入
- **紧凑注入格式** — `[KB] 标题 [source:stage]: 摘要`（节省 ~30% prompt 空间）
- **别名映射系统** — `knowledge/aliases.json`
  - 查询时自动展开同义词（如 HHG → 高次谐波产生）
- **相似概念检测** — 创建 wiki stub 前检测 score>0.9 的相似条目，防膨胀
- **批处理维护窗口** — `scripts/kb_maintenance.py`
  - `--weekly` 一键维护：重建索引 + 清理孤儿 + 候选报告 + 健康度
  - `--reindex` / `--orphans` / `--candidates` / `--health` / `--captures`
- **知识库健康仪表盘** — Web 界面新增"健康度"和"别名"标签页
  - 健康度：总条目、生长分布、图谱状态、本周新增、待处理项
  - 别名管理：增删改别名映射，实时保存
- **移除 auto_distill 默认触发** — 蒸馏/生长改为用户控制，节省 80%+ LLM 调用

### 文件变更
- 新增：`scripts/kb_capture.py`（317 行，自检通过）
- 新增：`scripts/kb_maintenance.py`（260 行，自检通过）
- 新增：`knowledge/aliases.json`
- 修改：`scripts/knowledge_base.py`（+216 行：别名、相似检测、健康度、智能触发）
- 修改：`scripts/context_builder.py`（分级注入、紧凑格式、预算 2000→1200）
- 修改：`scripts/copilot_engine.py`（对话后自动调用 capture）
- 修改：`scripts/web_server.py`（+94 行：aliases/captures/health/maintenance API）
- 修改：`web/js/app.js`（+158 行：健康度/别名标签页、维护按钮、相似概念提示）
- 修改：`web/css/style.css`（+69 行：仪表盘和别名样式）
- 修改：`web/index.html`（新增 2 个标签页和面板）

---

## v1.7.0 - 2026-05-08 知识库系统重构（raw/wiki 分层 + 知识图谱 + 生长机制）

### 架构重构（借鉴 Karpathy 笔记系统）
- **目录结构重组**：`knowledge/` 分为 `raw/`（用户原始材料）和 `wiki/`（林赛研究笔记）
  - `raw/papers/` — 论文 PDF/笔记
  - `raw/notes/` — 用户手写笔记
  - `raw/webclips/` — 网页剪藏
  - `wiki/concepts/` — 核心概念
  - `wiki/methods/` — 实验方法
  - `wiki/people/` — 学者评价
  - `wiki/papers/` — 论文精读
  - `wiki/projects/` — 项目聚合

### 新增核心模块
- **Wiki 页面管理**（`scripts/knowledge_base.py`）
  - `parse_frontmatter()` / `build_frontmatter()` — YAML frontmatter 解析与生成
  - `get_wiki_page()` / `list_wiki_pages()` / `save_wiki_page()` / `delete_wiki_page()` — CRUD
  - 标准 wiki 格式：YAML frontmatter + Markdown，林赛第一人称视角
  - 关键字段：`growth_stage`（seedling/growing/mature/archived）、`confidence`（0-1）、`related`（关联概念）

- **知识图谱**（`knowledge/graph.json`）
  - `update_graph_node()` / `add_graph_edge()` — 节点/边管理
  - `get_related_concepts()` — 通过图谱拉取关联知识（支持深度遍历）
  - `get_graph_summary()` — 图谱概览（节点数、边数、生长阶段分布）

- **生长日志**（`knowledge/growth-log.json`）
  - `log_growth()` — 记录每次创建/更新/关联/提炼/纳入事件
  - `get_growth_log()` — 按目标或时间范围查询
  - `get_growth_candidates()` — 获取待生长概念列表（seedling 阶段）

- **raw → wiki 提炼流程**
  - `ingest_raw()` — 将 raw 文件纳入系统，记录日志，可选自动触发提炼
  - `distill_raw_to_wiki()` — 生成提炼 prompt（供 LLM 使用）
  - `save_distilled_wiki()` — 保存 LLM 提炼结果，自动更新图谱和日志
  - 五种 wiki 类型的提炼模板：concepts / methods / people / papers / projects

- **交互触发生长机制**
  - `create_wiki_stub()` — 对话中遇到新概念时自动创建 seedling stub
  - `grow_wiki_prompt()` — 生成 wiki 丰满 prompt（供 LLM 使用）
  - `apply_growth()` — 应用 LLM 生成的丰满内容，更新生长阶段

### 索引系统增强
- `build_index()` — 统一索引 raw + wiki 目录
- `search()` — 支持 `source="all"|"raw"|"wiki"` 过滤，wiki 结果加权（×1.2），mature 再加权（×1.1）
- `get_enriched_context()` — 增强上下文：搜索结果 + 图谱关联知识 + 缺失概念检测
- `get_index_status()` — 返回 raw_count / wiki_count / chunks / graph 概览

### 上下文构建增强
- `context_builder.py` — `_read_knowledge_context()` 使用 `get_enriched_context()`
  - 搜索结果标注来源（📚 raw / 📝 wiki）和生长阶段
  - 通过图谱拉取关联知识（轻量注入）
  - **缺失概念检测**：如果用户提到知识库中没有的概念，林赛会标注"认知边界"，邀请一起记录
  - 体现"知识库是林赛的可靠知识来源，而非额外记忆负担"

### API 端点（大量新增）
- `GET /api/knowledge/raw` — 列出 raw 文件
- `GET /api/knowledge/wiki` — 列出 wiki 页面（支持 `?type=` 过滤）
- `GET /api/knowledge/wiki/{path}` — 获取单个 wiki 页面（含 frontmatter + body）
- `DELETE /api/knowledge/wiki/{path}` — 删除 wiki 页面（清理图谱关联）
- `GET /api/knowledge/graph` — 知识图谱概览
- `GET /api/knowledge/related?q=...` — 关联概念查询
- `GET /api/knowledge/growth-log?limit=N` — 生长日志
- `GET /api/knowledge/growth-candidates` — 待生长概念
- `GET /api/knowledge/enriched?q=...` — 增强上下文（搜索+关联+缺失检测）
- `POST /api/knowledge/ingest` — 纳入 raw 文件
- `POST /api/knowledge/wiki` — 创建/更新 wiki 页面
- `POST /api/knowledge/stub` — 创建概念 stub
- `GET /api/knowledge/search` — 增强：支持 `?source=` 和 `?top_k=` 参数

### Web 前端增强
- 设置面板新增"📚 知识库管理器"按钮
- 知识库管理器模态框：5 个标签页
  - 📊 **概览**：统计卡片（raw/wiki/段落/节点/边/待生长）+ 生长阶段分布
  - 📄 **Raw**：按分类（论文/笔记/剪藏）浏览 raw 文件
  - 📝 **Wiki**：按类型过滤浏览 wiki 页面，点击打开详情
  - 🔗 **图谱**：节点/边统计 + 生长阶段分布
  - 🌱 **生长**：待生长概念列表 + 最近生长日志
- Wiki 详情模态框：frontmatter 元信息 + Markdown 渲染（标题/列表/引用/代码）
- 支持"➕ 新建概念 Stub"交互

### 文档
- `knowledge/README.md` — 完整知识库使用指南（设计理念、目录结构、wiki 格式、使用方式）

## v1.6.0-M3 - 2026-05-08 子代理调用系统

### 新增
- **子代理调用系统**
  - `scripts/tool_engine.py` — 新建模块（300行）
    - 工具注册表：`file_read`, `file_write`, `calc`, `task_create`, `knowledge_query`
    - 严格安全边界：
      - `file_read`: 只能读项目目录内文件
      - `file_write`: 只能写 `memory/`, `sessions/`, `tasks/`, `knowledge/`
      - `calc`: `ast.parse` 白名单机制，仅允许数学运算节点，禁止导入/系统调用
    - 工具调用协议：`@@tool:name@@\n{json}\n@@end@@`
    - `parse_tool_calls()` / `execute_tool_calls()` / `strip_tool_calls()`
  - `scripts/copilot_engine.py` — 新增 `call_llm_with_tools()`
    - 执行流程：注入工具说明 → 第一次 LLM 调用 → 解析工具调用 → 执行工具 → 结果回传 → 第二次 LLM 调用 → 最终回复
    - 无工具调用时只消耗一次 LLM 调用（性能无损）
  - `scripts/web_server.py` — SSE 流式支持工具事件
    - 前端收到 `{"type": "tools", "calls": [...]}` 事件时显示工具调用提示
  - `persona/lin-sai-persona.md` — 追加"子代理调用"角色说明
    - 教会林赛何时使用工具、如何分解任务、调用格式
  - Web 界面：消息气泡旁显示 `🔧 调用工具: calc, knowledge_query` 提示
  - API：`GET /api/tools` — 列出可用工具

### 新增
- **本地知识库**
  - `scripts/knowledge_base.py` — 新建模块（300行）
    - 纯标准库实现：中文分词（单字+双字+四字窗口）、英文单词提取
    - 文档分块：按段落切分，每块 ≤500 字符
    - 倒排索引 + TF-IDF 检索
    - 增量索引：只更新修改过的文档
    - 数据存储：`knowledge/index.json`
  - `knowledge/` 目录：用户放入 .md/.txt/.rst 文件即可被索引
  - 示例文档：`knowledge/solid_hhg_basics.md`（固体HHG基础）
  - `context_builder.py` 自动检索：用户输入自动匹配 Top-2 相关知识段落注入 system_prompt
  - Web 界面：设置面板显示索引状态，支持一键重建索引
- **任务进度跟踪增强**
  - `scripts/task_manager.py` 增强：
    - 任务 JSON 新增 `progress` (0-100)、`subtasks`、 `milestones` 字段
    - `update_progress()` — 更新进度，自动检测完成（progress=100 → status=completed）
    - `add_subtask()` / `toggle_subtask()` — 子任务 CRUD
    - `_recalc_progress()` — 根据子任务完成数自动计算父任务进度
  - Web 界面：
    - 右侧任务面板改为**三列看板**（待办 / 进行中 / 已完成）
    - 任务卡片显示进度条 + 子任务完成数（如 `2/5`）
    - 点击任务展开详情模态框：进度滑块、子任务勾选、里程碑列表
  - API 端点：
    - `GET /api/tasks/{id}` — 任务详情
    - `PUT /api/tasks/{id}/progress` — 更新进度
    - `PUT /api/tasks/{id}/subtasks` — 添加/切换子任务
- **知识库 API**
  - `GET /api/knowledge` — 索引状态
  - `GET /api/knowledge/search?q=...` — TF-IDF 检索
  - `POST /api/knowledge/reindex` — 重建索引

### 修改
- `scripts/context_builder.py` — 新增 `knowledge` 预算项（2000字符），知识检索结果参与预算分配
- `scripts/web_server.py` — 新增知识库和任务管理 API

## v1.6.0-M1 - 2026-05-08 Token 统计 + 技能系统

### 新增
- **Token 用量统计**
  - `scripts/usage_tracker.py` — 新建模块（200行）
    - API Provider 精确统计（从 HTTP 响应解析 usage 字段）
    - CLI Provider 字符估算（utf-8 字节数 // 3）
    - 五维统计：daily / monthly / by_session / by_provider / total
    - 数据存储：`memory/usage/usage.json`
  - Web 界面：设置面板显示今日用量、总用量、各 Provider 分布
  - 顶部栏不显示（避免干扰），在设置面板中展示详细统计
- **技能系统**
  - `scripts/skill_manager.py` — 新建模块（150行）
    - 扫描 `skills/` 目录下的 SKILL.md 文件
    - 关键词触发匹配：根据用户输入自动激活相关技能
    - 技能上下文注入到 system_prompt，参与预算分配
  - `skills/` 目录结构：
    - `math-derivation/` — 数学推导辅助（量纲检查、标注假设、极限验证）
    - `code-review/` — 代码审查（可读性、边界情况、性能）
    - `experiment-design/` — 实验方案设计（先画框图、风险预判、备用方案）
  - Web 界面：
    - 设置面板显示所有可用技能及触发条件
    - 输入框实时检测：顶部栏显示 `🎯 math-derivation` 等激活技能
    - 300ms 防抖，避免频繁请求
- **API 端点**
  - `GET /api/usage` — 用量摘要（daily + total + by_provider）
  - `GET /api/usage/daily` — 今日用量
  - `GET /api/skills` — 列出所有技能
  - `GET /api/skills/active?q=...` — 查询输入激活的技能

### 修改
- `scripts/llm_router.py` — `call_llm()` 返回 `(text, usage_dict, provider_name)`，支持用量追踪
- `scripts/copilot_engine.py` — 适配新返回值格式
- `scripts/context_builder.py` — 新增 `skills` 预算项（2000字符），技能上下文参与分配与截断
- `scripts/web_server.py` — 对话后自动记录 token 用量；新增 usage/skills API

## v1.5.2 - 2026-05-08 think 过滤 + CLI/API 切换 + 聊天记录查看

### 新增
- **过滤 LLM 推理标签 `<think>`**
  - `scripts/llm_router.py` 新增 `_strip_think_tags()` 函数，使用栈算法处理嵌套标签
  - 所有 Provider（CLI + API）返回的内容自动过滤 think 标签，对话更干净
- **Provider 选择持久化**
  - 手动切换的 Provider 保存到 `memory/llm-config.json`，服务器重启后保留
  - 新增 `💻 CLI 自动` 选项：强制使用第一个可用的 CLI Provider（claude/kimi）
  - 设置面板同时显示所有 Provider（包括不可用的），灰色标记，让用户知道有哪些选择
- **聊天记录查看优化**
  - 修复遗漏的 `chat-archive-header` HTML 元素（v1.4.1 引入的 `viewArchiveSession` 功能）
  - 点击会话加载后，消息数 > 3 时显示提示条：`↑ 已加载 X 条消息，向上滚动查看历史`（8 秒后自动消失）
  - 归档浏览头部显示会话主题、消息数、模式，提供 `✕ 关闭浏览` 按钮返回对话

### 修复
- `scripts/copilot_engine.py` / `scripts/web_server.py` — 补全遗漏的 `import llm_router as lr`
- `scripts/copilot_engine.py` — `detect_llm_cli()` 延迟初始化，避免模块导入时循环依赖
- `scripts/web_server.py` — `POST /api/switch-provider` 支持 `cli_auto` 特殊值
- **`scripts/llm_router.py` — 修复 CLI 检测被 API 配置阻塞的 bug**：原逻辑"没有 API 时才检测 CLI"改为"始终检测 CLI"，确保同时配置了 API 和安装了 CLI 时，两者都能被识别

## v1.5.1 - 2026-05-08 手动 Provider 切换

### 新增
- **Web 界面手动切换 Provider**
  - 顶部栏新增 `provider-badge`，实时显示当前使用的模型/CLI（点击打开设置面板）
  - 设置面板中 LLM Provider 区域改为 radio 按钮列表，支持选择：
    - `🔄 自动选择`（默认）
    - 每个可用 Provider（显示 ✓/✗ 可用状态、API/CLI 类型、模型名）
  - 切换后即时生效，下次对话使用新 Provider
- **新 API 端点**
  - `GET /api/providers` — 返回所有 Provider 状态列表
  - `GET /api/providers/current` — 返回当前选中的 Provider（`auto` 或具体名称）
  - `POST /api/switch-provider` — 手动切换 Provider（与 `/api/llm-provider` 兼容）

### 修复
- `scripts/web_server.py` / `scripts/copilot_engine.py` — 补全遗漏的 `import llm_router as lr`
- `scripts/copilot_engine.py` — `detect_llm_cli()` 改为延迟初始化，避免模块导入时循环依赖

## v1.5.0 - 2026-05-08 多模型路由 + MiniMax API 支持

### 新增
- `scripts/llm_router.py` — 多模型路由管理器（350行）
  - 支持 CLI 后端：claude, kimi
  - 支持 HTTP API 后端：OpenAI 兼容格式（MiniMax, DeepSeek, Groq 等）
  - 自动检测 `.env` 文件中的 API Key，自动注册 Provider
  - **策略系统**：priority（优先级）/ round_robin（轮询）/ 自动降级
  - **限流自动降级**：HTTP 429 触发自动切换到下一个 Provider
  - 健康检查与失败计数
- **零第三方依赖**：HTTP API 调用使用 Python 标准库 `urllib.request`
- **安全配置**：
  - `.env` 和 `memory/llm-config.json` 已加入 `.gitignore`，API Key 永不进入 Git
  - 环境变量优先于配置文件

### 接入修改
- `copilot_engine.py` — `call_llm()` 迁移到 llm_router，保留兼容接口
- `chat_archive.py` — 关键词提炼改用 llm_router
- `web_server.py` — 新增 `GET /api/llm-status` 接口
- Web 界面 — 设置面板显示当前 LLM Provider 状态

### 使用方式
```bash
# 方式 1：项目根目录创建 .env 文件
cat > .env << 'EOF'
MINIMAX_API_KEY=your_key_here
MINIMAX_MODEL=MiniMax-M2.7
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
EOF

# 方式 2：环境变量
export MINIMAX_API_KEY=your_key_here

# 启动后自动检测并优先使用 API
python3 scripts/web_server.py
```

---

## v1.4.0 - 2026-05-08 聊天记录浏览器 + 智能归档

### 新增
- `scripts/chat_archive.py` — 聊天记录智能归档系统（400行，4项自检通过）
  - **关键词提炼**：本地词频统计 + LLM 语义提炼，双阶段合并去重
  - **跨会话搜索**：遍历所有 sessions/ 全文匹配，按匹配度排序
  - **全局索引**：`memory/chat-archive-index.json` 汇总所有会话元信息
  - 每个会话目录下自动生成 `keywords.json` 缓存
- **Web 界面聊天记录浏览器**
  - 左侧会话列表显示关键词标签（hover 可点击搜索）
  - 点击任意历史会话 → 进入只读模式查看完整聊天记录
  - "返回当前会话"按钮，一键切回活跃对话
  - 新增"聊天记录"侧边栏：跨会话全文搜索，结果点击跳转
- **后端 API 扩展**
  - `GET /api/sessions/<id>/keywords` — 获取会话关键词
  - `GET /api/history?q=...` — 跨会话全文搜索
  - `GET /api/archive-index` — 获取归档索引

### 设计决策
- **存档与记忆分离**：聊天记录 = 微信历史（完整保留，随时翻阅）；林赛记忆 = 人脑提炼（精简、会遗忘）
- 中文分词采用简单正则（英文术语 + 中文2-8字词组），零第三方依赖
- LLM 关键词提炼仅在首次访问时触发，后续读缓存

---

## v1.3.0 - 2026-05-08 Web 界面第二批 + 启动快捷方式

### 新增
- **文件上传图形化**
  - 拖拽上传区域 + 点击选择按钮
  - 支持文本文件（.md/.txt）直接读取，二进制文件 Base64 传输
  - 上传进度条，完成后自动在对话中插入文件引用卡片
  - 上传后自动更新文献索引和右侧栏引用列表
- **Agora 集成按钮**
  - 点击 `/agora` 弹出 20 位历史人物选择面板（费曼、狄拉克、爱因斯坦等）
  - 多选人物，一键导出到 Agora 群聊格式
- **消息编辑/删除**
  - 用户消息 hover 显示编辑/删除按钮
  - 编辑后实时更新 DOM 和持久化存储
  - 删除前确认，避免误操作
- **启动快捷方式**
  - `scripts/launch.sh` — 一键启动脚本，检测端口占用，自动打开浏览器
  - `scripts/LinSai-CoPilot.command` — macOS 双击启动（可放桌面）
- **文献列表 API** — `/api/references` 实时显示已上传文档

### 后端增强
- `web_server.py` 新增 API：
  - `POST /api/upload` — 文件上传（JSON base64 方式）
  - `POST /api/agora` — Agora 上下文导出
  - `PUT /api/sessions/<id>/messages/<msg_id>` — 消息编辑
  - `DELETE /api/sessions/<id>/messages/<msg_id>` — 消息删除
  - `GET /api/references` — 文献列表
- 新增辅助函数：`_handle_upload`、`_edit_message`、`_delete_message`、`_list_references`

---

## v1.2.0 - 2026-05-08 Web 界面与浏览器交互

### 新增
- `scripts/web_server.py` — Web 服务器（HTTP + SSE + API路由，330行，4项自检通过）
  - ThreadingHTTPServer 并发处理，零第三方依赖
  - REST API：会话 CRUD、消息历史、任务列表、主动提醒、版本信息
  - SSE 流式输出：LLM 回复逐句切分模拟打字效果
  - 复用现有引擎：context_builder + copilot_engine.call_llm()
- `web/index.html` — 单页应用入口（6大功能区块）
- `web/css/style.css` — 双主题样式系统（深色/浅色/自动跟随系统）
  - CSS 变量驱动，切换无闪烁
  - 消息气泡、代码块、Markdown 渲染、滚动条美化
  - 响应式布局：移动端侧边栏折叠、触摸优化
- `web/js/app.js` — 原生 JavaScript 前端逻辑（450行）
  - 会话管理：搜索、新建、切换、侧边栏渲染
  - 聊天界面：消息气泡、Markdown 轻量渲染器、流式 SSE 接收
  - 主题管理：localStorage 持久化、系统主题监听
  - 快捷命令：/mode /read /agora /summary 按钮触发
  - 主动提醒：Toast 弹窗通知

### 设计决策
- 前端零框架：不引入 React/Vue/Angular，保持项目极简哲学
- SSE 替代 WebSocket：Python 标准库原生支持，无需额外依赖
- 模拟流式输出：现有 call_llm() 为同步调用，先获取完整回复再逐句推送

---

## v1.1.0 - 2026-05-08 版本管理与数据安全体系

### 新增
- `VERSION` 文件 — 单一版本号真相源（SemVer 规范）
- `scripts/backup_manager.py` — 用户数据备份/恢复/自动清理（243行，6项自检通过）
  - 支持手动备份、自动备份（24h间隔）、备份列表、恢复指定备份
  - 恢复前自动创建应急备份，可一键回滚
  - 自动清理旧备份（默认保留最近10个）
- `scripts/upgrade.py` — 安全升级标准流程（234行，4项自检通过）
  - 升级前强制备份 → git pull → 脚本语法验证 → 迁移检查
  - 支持 `--check` 查看版本、`--simulate` 模拟升级、`--verify` 验证完整性
- `.gitignore` — 隔离用户数据（sessions/、memory/、tasks/、references/）与代码
- `copilot_engine.py` 启动时集成自动备份（失败不阻塞主流程）

### 规范
- 版本号统一为 `1.0.0`，`source-manifest.json` 同步更新
- 用户数据与代码分离原则：所有用户生成数据永不进入版本控制

---

## v1.0.0 - 2026-05-08 Phase 1-4 全部完成

### 新增
- 项目基础目录结构（`persona/`、`sessions/`、`memory/`、`tasks/`、`references/`、`scripts/`）
- `AGENTS.md`：AI 代理开发指南，定义项目定位、架构、开发规范
- `README.md`：人类可读的项目说明
- `persona/lin-sai-persona.md`：整合版人格注入文件，从 virtu-LinSai v2.7 的 5 个源文件提炼
- `persona/source-manifest.json`：来源追踪与版本锁定
- 各目录 `README.md`：说明用途和格式规范

### 设计决策
- 定位为"专属合作者"（CoPilot），区别于 Agora 的"群聊会议室"
- 采用 1v1 持续对话 + 长期记忆 + 主动感知的交互模型
- 人格资产单向引用 virtu-LinSai，禁止反向修改
- 技术栈：Python 3 标准库 + Markdown + JSON，零第三方依赖

### Phase 1 启明 — 2026-05-08
- `scripts/session_manager.py` — 会话创建、加载、追加、列出、归档（382行，自检通过）
- `scripts/context_builder.py` — Prompt组装、动态预算分配（30000字符）、分层截断（304行，自检通过）
- `scripts/copilot_engine.py` — LLM调用封装（Claude/Kimi CLI）、交互式对话循环、CLI参数解析（465行，自检通过）
- 端到端集成测试通过：创建会话 → 构建上下文 → 调用LLM → 林赛回复 → 消息持久化

### Phase 2 长河 — 2026-05-08
- `scripts/memory_manager.py` — 用户画像提取、工作上下文、长期记忆索引、记忆片段、会话摘要（439行，自检通过）
- `scripts/task_manager.py` — 任务CRUD、状态流转、截止日期追踪、逾期检测（380行，自检通过）
- 集成：context_builder 自动加载相关记忆，copilot_engine 对话后自动更新画像/上下文
- Phase 2 集成测试通过：6轮对话 → 自动提取技能/偏好/待决策事项

### Phase 3 觉醒 — 2026-05-08
- `scripts/proactive_engine.py` — 心跳扫描、主动提醒、压力信号检测、三级自主、模式识别（465行，自检通过）
- 集成：copilot_engine 启动时运行 heartbeat 显示提醒，对话中自动识别交互模式
- Phase 3 集成测试通过：截止日期提醒 + 压力信号关怀均符合林赛人格

### Phase 4 灵犀 — 2026-05-08
- `scripts/document_handler.py` — Markdown/TXT读取、PDF基础提取、代码分析、文档摘要、参考文献索引（486行，自检通过）
- `scripts/agora_bridge.py` — Agora群聊系统桥接，支持上下文导出/导入（208行，自检通过）
- 集成：copilot_engine 新增 `/read` 和 `/agora` 命令
- Phase 4 集成测试通过：文档读取 → LLM摘要 → 代码分析 → Agora导出

### 修复
- `memory_manager.py` 用户画像提取规则调优
  - 移除宽泛关键词 `"实验"`（避免误匹配"实验室"→"室最安静"）
  - 新增6条精确模式：支持"我是做"、"从事...的"、"在...领域"等变体
  - 添加后缀边界（"的"、"方向"、"领域"）确保正确截断
  - 技能去重：子串重复自动合并（"MATLAB"+"MATLAB编程"→"MATLAB编程"），长度差>3保留（"Java"/"JavaScript"共存）

### 项目状态
- ✅ Phase 0-4 全部完成
- ✅ 8个核心脚本，总计3307行，全部语法正确
- ✅ 零第三方依赖，仅使用Python标准库
- ✅ 全部通过自检与集成测试

---

## v2.0.1 - 2026-05-08 固体 HHG 理论方法文献调研

### 新增（knowledge base）

- `docs/solid-HHG-theory-methods-survey.md` — **34 KB 调研报告**，覆盖 10 个理论方向（A/B/C/D/E/F/G/H/I/J），所有内容直接来自 arXiv 论文真实文本

### 调研方向（10 个）

| 方向 | 主题 | 主要文献 |
|------|------|----------|
| A | Berry 相位/联络/结构规范 | 2111.08669 |
| B | SFQED 量子光学框架 | 1910.13791 |
| C | 半导体布洛赫方程（SBE）| 2304.12547 |
| D | 倒空间轨迹方法（RST）| 1809.08109 |
| E | 拓扑 HHG（Berry 曲率/陈数）| 1806.11232 |
| F | 阿秒条纹/隧穿时间测量 | 1707.05445 |
| G | 自旋/谷电子学 HHG | 1906.10224 |
| H | SFA 强场近似完整理论 | 1812.11447 |
| I | 偏振分辨 HHG 光谱（固体）| 1805.10453 |
| J | 分子自探测/轨道断层成像 | 2103.16228 |

### 关键方程提取（可复现性）

- Berry 曲率数值公式（Eq. 11）
- SFQED 三步量子化方案（分解 $A_c(t)$ + $A_q$）
- SBE 方程（密度矩阵形式，含退相干 $T_2$ 项）
- RST 四步模型（新增 pre-acceleration 步骤）
- Berry 曲率反常速度（$\dot{r} = \nabla_k\varepsilon + eE\times\Omega$）
- ADK 隧穿率公式
- Keldysh 参数 $\gamma = \omega\sqrt{2I_p/E_0}$

### 数值参数汇总

- ZnO SBE 计算：$\omega=0.014$ a.u., $F_{x0}=0.004$ a.u., 2D ($k_z=0$)
- Si HHG：2 μm 厚，2.1 μm，120 fs，0.6 TW/cm²，TDDFT 验证
- H 原子 attoclock：770 nm，6 fs，$0.84$ 椭圆率，$1.65$–$3.9\times10^{14}$ W/cm²

### 技术修复

- deepxiv SDK (`reader.py`) encoding bug：response.content.decode("utf-8", errors="replace") + json.loads() 替换 response.json()

