# v5.0 三端统一架构 · 策划书

> 版本：v5.0.0-pre
> 创建：2026-07-19
> 状态：执行中
> 设计依据：`docs/v5-three-tier-unification-architecture.md`（修订版架构）

---

## 一、项目目标

将当前"飞书↔hermes 闭环 + hermes→CoPilot 单向流"的碎片化架构，升级为"hermes 总控后端 + CoPilot 可视化操作台 + 飞书移动端"的三端统一架构。

### 核心原则

1. **各自存储不合并**：尊重现有格式差异（Markdown vs JSON，.md 单文件 vs .json+.pdf+.txt），不做破坏性合并
2. **每类数据只有一个权威源**：其他端只读或通过权威源写入，避免 lost-update
3. **跨进程并发用 fcntl/SQLite WAL**：不依赖 threading.Lock
4. **渐进实施**：每个阶段独立交付价值，前一阶段失败不阻塞后续

### 四个子系统的权威源

| 子系统 | 权威源 | CoPilot 角色 | 飞书角色 |
|--------|--------|-------------|---------|
| 论文+知识库 | hermes `AI_wiki/` | 扩展索引 + 只读 | 间接（通过 hermes） |
| 记忆 | 各自存储 | 单向同步（hermes→CoPilot） | 间接（通过 hermes session） |
| 统一状态 | `item-status.json`（共享） | 读写（fcntl 锁） | 读写（通过 hermes） |
| 任务 | hermes `kanban.db` | 读写（SQLite 客户端） | 读写（通过 hermes） |

---

## 二、阶段规划

### P0：路径错配修复 + fcntl 锁封装（半天）【✅ 已完成】

**问题**：`briefing_sync.py` 第 44 行硬编码 `HERMES_STATUS_PATH = .../briefings/status.json`，但该文件从不存在。实际状态文件是 `briefings/item-status.json`。

**任务清单**：
- [x] P0.1 修复 `briefing_sync.py` 的 `HERMES_STATUS_PATH`，指向 `item-status.json`（实际方案：移除该常量，委托 `state_sync.ITEM_STATUS_PATH`）
- [x] P0.2 适配 `item-status.json` 的 schema（items 字典 + 9 级状态枚举 + history 数组）
- [x] P0.3 在 `common.py` 新增 `file_lock(lock_name)` 上下文管理器（fcntl.flock，跨进程独占锁）
- [x] P0.4 `state_sync.update_item_status` / `initialize_from_existing` 使用 `file_lock("item-status")` 保护 read-modify-write
- [x] P0.5 更新 `_self_check()` 和 `test_core.py::BriefingSyncTests` 适配新 schema（28 检查点，新增 `_test_new_paper_register`）
- [x] P0.6 全量测试：核心 116/116 + Web API 70/70 + 人格 38/38 + 场景 16/16 = **240/240 全绿**

**验收标准**：
- [x] `briefing_sync._self_check()` 5/5 通过
- [x] `self_test --module` 全绿（116/116）
- [x] `sync_to_hermes()` 能正确读写 `item-status.json`（state_sync 自检 155 篇论文）
- [x] `sync_from_hermes()` 能从 `item-status.json` 读取状态升级 CoPilot paper-pool
- [x] `state_sync._self_check()` 通过（12 篇已处理）

**实际变更文件**：`common.py`、`state_sync.py`、`briefing_sync.py`、`tests/test_core.py`

**风险**：低。纯路径替换 + 锁封装，不改业务逻辑。

---

### 阶段 1：CoPilot 检索引擎索引 hermes wiki（1 天）

**问题**：hermes `AI_wiki/02-wiki/`（~30 篇结构化 wiki）和 CoPilot `knowledge/wiki/`（~113 篇）完全独立，CoPilot 检索不到 hermes 的 wiki 内容。

**任务清单**：
- [ ] 1.1 `kb_index.py::build_index()` 增加外部目录扫描参数 `extra_wiki_dirs`
- [ ] 1.2 索引 hermes `AI_wiki/02-wiki/`（concepts/methods/entities/topics/projects）
- [ ] 1.3 frontmatter 兼容：对缺失的 `growth_stage`/`aliases`/`related` 提供默认值
- [ ] 1.4 `doc_type` 白名单扩展：新增 `entities`、`topics`（hermes 独有子目录）
- [ ] 1.5 搜索结果标注来源（`[hermes-wiki]` vs `[copilot-wiki]`）
- [ ] 1.6 前端知识库浏览器展示来源标签
- [ ] 1.7 测试：验证 hermes wiki 内容可被 CoPilot 检索命中

**验收标准**：
- 搜索"HHG"能命中 hermes 的 `high-harmonic-generation.md`
- 搜索结果含来源标签，区分 hermes wiki 和 CoPilot wiki
- 知识库健康度不下降（无孤儿节点增加）
- `self_test --module` 全绿

**风险**：低。只读扩展，不修改 hermes 文件，不破坏现有索引。

---

### 阶段 2：hermes cron 消费 item-status.json（1 天）

**问题**：hermes cron 检索入池时重复推送已处理论文；推送后不更新状态；CoPilot 写入的 `item-status.json` hermes 不读。

**任务清单**：
- [ ] 2.1 改造 `select_candidates.py`：读取 `item-status.json`，跳过 `status ≥ viewed` 的论文
- [ ] 2.2 改造推送 cron：推送后调用 `update_item_status(updated_by="hermes-cron", status="pushed")`
- [ ] 2.3 改造深度分析 cron：分析后调用 `update_item_status(updated_by="hermes-cron", status="interested")`
- [ ] 2.4 改造归档 cron：归档后调用 `update_item_status(updated_by="hermes-cron", status="archived")`
- [ ] 2.5 验证：模拟 cron 执行，确认状态文件正确更新

**验收标准**：
- 已归档论文不再被推送
- 推送/分析/归档操作后 `item-status.json` 的 `updated_by` 字段正确标记
- `state_sync.py` 的 `get_processed_ids()` 返回的 ID 被 cron 正确跳过

**风险**：中。改 hermes 端脚本，需在测试环境验证后灰度切换。需读取 `~/.hermes/profiles/linsai/cron/jobs.json` 确认 cron 调用的脚本路径。

---

### 阶段 3：CoPilot 任务看板读 kanban.db（1.5 天）

**问题**：hermes `kanban.db`（22 个任务）和 CoPilot `tasks/`（空目录）完全隔离。

**任务清单**：
- [ ] 3.1 新建 `scripts/kanban_reader.py`：SQLite 读取层
  - `list_tasks(status_filter)` → 列表
  - `get_task(task_id)` → 单任务详情
  - `create_task(title, assignee, created_by)` → INSERT
  - `update_task_status(task_id, status)` → UPDATE
  - 状态映射：todo↔backlog, blocked↔paused, done↔completed, in_progress↔active
- [ ] 3.2 `kanban_reader.py::_self_check()` 验证读取真实 kanban.db
- [ ] 3.3 改造 `web_routes_tasks.py`：GET /api/tasks 读 kanban.db
- [ ] 3.4 改造 `web/js/task.js`：渲染 kanban 任务，状态映射展示
- [ ] 3.5 CoPilot 新建任务 → INSERT kanban.db（`created_by="copilot"`）
- [ ] 3.6 废弃 CoPilot `tasks/` 目录的本地存储（保留兼容降级）
- [ ] 3.7 测试：Web 界面展示 hermes 22 个任务，新建任务在两端可见

**验收标准**：
- CoPilot 任务看板显示 hermes 的 22 个任务
- 状态映射正确（todo 显示为 backlog，done 显示为 completed）
- CoPilot 新建任务后，hermes kanban 能查询到
- hermes 完成任务后，CoPilot 看板刷新可见

**风险**：中。SQLite WAL 并发安全，但需验证 CoPilot 写入不干扰 hermes worker。降级方案：若 kanban.db 不可读，回退到本地 tasks/。

---

### 阶段 4：memory_bridge.py 记忆单向同步（1 天）

**问题**：hermes `MEMORY.md` + `USER.md`（Markdown 自由文本）和 CoPilot `memory/*.json`（结构化 JSON）完全独立，飞书操作更新 hermes 记忆后 CoPilot 不感知。

**任务清单**：
- [ ] 4.1 新建 `scripts/memory_bridge.py`：
  - `sync_user_profile()`：读 hermes `USER.md`，解析 Markdown 章节，merge 到 CoPilot `user-profile.json`
  - `sync_working_context()`：读 hermes `MEMORY.md`，提取"当前工作"段落，更新 CoPilot `working-context.json`
  - hermes 优先，CoPilot 独有字段保留（`interaction_history`、`research_field` TF-IDF 提取结果）
  - 记录 `hermes_synced_at` 时间戳
- [ ] 4.2 集成到 `sync_engine.sync_all()`：新增 `[1.5/5] memory_bridge.sync()`
- [ ] 4.3 `_self_check()` 验证 Markdown 解析正确性
- [ ] 4.4 测试：手动修改 hermes `USER.md`，执行 sync_all，验证 CoPilot 画像更新

**验收标准**：
- hermes `USER.md` 中的研究领域更新后，CoPilot `user-profile.json` 的 `research_field` 同步更新
- hermes `MEMORY.md` 中的工作上下文更新后，CoPilot `working-context.json` 的 `active_projects` 同步
- CoPilot 独有字段（`interaction_history`、`_confidence`）不被覆盖

**风险**：低。单向只读同步，不修改 hermes 文件。Markdown 解析可能不完美，但保留 CoPilot 原有字段作为兜底。

---

### 阶段 5：.copilot-sync.json 落地 + 项目决策同步（2 天）

**问题**：`state_sync.py` 设计了 `.copilot-sync.json` 机制但从未创建；NSFC 决策纯本地。

**任务清单**：
- [ ] 5.1 `state_sync.py::register_project()` 对 hermes NSFC 项目目录执行注册
- [ ] 5.2 CoPilot NSFC 决策操作（approve/reject/discuss）写入 `.copilot-sync.json`
- [ ] 5.3 hermes BRAIN cron 读取 `.copilot-sync.json` 同步 CoPilot 决策
- [ ] 5.4 前端 NSFC 面板展示决策来源（copilot/hermes/feishu）
- [ ] 5.5 测试：CoPilot approve 一个决策 → hermes 感知 → hermes 修改 → CoPilot 可见

**验收标准**：
- `.copilot-sync.json` 在 hermes NSFC 项目目录下创建
- CoPilot 决策操作实时同步到 hermes
- hermes 决策变更 CoPilot 可见
- `decided_by` 字段正确标记来源

**风险**：中。双向同步需处理冲突（CoPilot 优先），需在 hermes BRAIN cron 中增加读取逻辑。

---

## 三、看板状态总览

| 阶段 | 状态 | 进度 | 负责模块 |
|------|------|------|---------|
| P0 路径修复+fcntl锁 | ⬜ 待开始 | 0/6 | briefing_sync, common |
| 阶段 1 索引 hermes wiki | ⬜ 待开始 | 0/7 | kb_index |
| 阶段 2 hermes cron 消费状态 | ⬜ 待开始 | 0/5 | hermes scripts |
| 阶段 3 kanban 任务桥接 | ⬜ 待开始 | 0/7 | kanban_reader, task.js |
| 阶段 4 记忆单向同步 | ⬜ 待开始 | 0/4 | memory_bridge |
| 阶段 5 项目决策同步 | ⬜ 待开始 | 0/5 | state_sync, hermes BRAIN |

---

## 四、中断接续指引

### 如何判断当前进度

1. 查看本文件的看板状态总览（上面）
2. 查看各阶段任务清单的勾选状态
3. 查看代码变更：`git log --oneline -20`
4. 查看测试状态：`python3 scripts/self_test.py --module`

### 每阶段的接续检查点

| 阶段 | 接续时先检查 | 然后执行 |
|------|------------|---------|
| P0 | `briefing_sync.py` 第 44 行是否已改路径 | 若未改，从 P0.1 开始 |
| 阶段 1 | `kb_index.py::build_index` 是否有 `extra_wiki_dirs` 参数 | 若无，从 1.1 开始 |
| 阶段 2 | hermes `select_candidates.py` 是否读取 `item-status.json` | 若无，从 2.1 开始 |
| 阶段 3 | `scripts/kanban_reader.py` 是否存在 | 若无，从 3.1 开始 |
| 阶段 4 | `scripts/memory_bridge.py` 是否存在 | 若无，从 4.1 开始 |
| 阶段 5 | hermes NSFC 目录下是否有 `.copilot-sync.json` | 若无，从 5.1 开始 |

### 回滚策略

每个阶段独立 commit，失败时 `git revert <commit>` 回滚单阶段，不影响其他阶段。

---

## 五、版本计划

| 版本 | 内容 |
|------|------|
| v5.0.0 | P0 + 阶段 1（路径修复 + 索引扩展） |
| v5.1.0 | 阶段 2（hermes cron 状态闭环） |
| v5.2.0 | 阶段 3（kanban 任务桥接） |
| v5.3.0 | 阶段 4（记忆单向同步） |
| v5.4.0 | 阶段 5（项目决策同步） |

---

*最后更新：2026-07-19*
