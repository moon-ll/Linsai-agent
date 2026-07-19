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

### 阶段 1：CoPilot 检索引擎索引 hermes wiki（1 天）【✅ 已完成】

**问题**：hermes `AI_wiki/02-wiki/`（~67 篇结构化 wiki）与 CoPilot `knowledge/wiki/`（~115 篇）完全独立，CoPilot 检索引擎无法命中 hermes 侧知识。

**任务清单**：
- [x] 1.1 `kb_index.py::build_index()` 增加 `extra_wiki_dirs` 参数（`List[(Path, source_label)]`）
- [x] 1.2 默认包含 hermes `AI_wiki/02-wiki/`（concepts/methods/entities/topics/projects），69 文档入库
- [x] 1.3 frontmatter 兼容：hermes wiki 缺失 `growth_stage` 时默认 `"growing"`，`summary`/`description` 加入索引文本
- [x] 1.4 `search()` doc_type 过滤支持 `hermes-wiki/` 前缀，新增 `entities`/`topics` 类型
- [x] 1.5 搜索结果标注 `source: "hermes-wiki"`，wiki 加权 1.2× 同等适用
- [x] 1.6 前端搜索结果展示来源标签（紫色 `hermes` / 绿色 `wiki`），`file-content` API 支持 hermes-wiki 路径只读访问
- [x] 1.7 测试：`kb_index._self_check()` 6/6 通过（新增外部 wiki 测试），全量 116+70=186 通过

**验收标准**：
- [x] `build_index()` 默认索引 hermes wiki（384 文档 = 200 raw + 115 wiki + 69 hermes-wiki）
- [x] 搜索"阿秒科学"命中 `hermes-wiki/methods/three-step-model.md`（score=1.14）
- [x] `GET /api/knowledge` 返回 `hermes_wiki_count: 69`
- [x] `GET /api/knowledge/file-content?path=hermes-wiki/concepts/...` 返回 hermes wiki 内容
- [x] 前端搜索结果显示来源标签

**实际变更文件**：`paths.py`、`kb_index.py`、`web_routes_kb.py`、`web/js/kb.js`、`web/css/style.css`

**风险**：低。索引为只读，不修改 hermes wiki 原文件。

---

### 阶段 2：hermes cron 消费 item-status.json（1 天）【✅ 已完成】

**问题**：hermes cron 检索入池时重复推送已处理论文；推送后不更新状态；CoPilot 写入的 `item-status.json` hermes 不读。

**任务清单**：
- [x] 2.1 改造 `select_candidates.py`：读取 `item-status.json`，跳过 `status ≥ viewed` 的论文（v4.2 已实现，v5.0 改用 helper 统一锁机制）
- [x] 2.2 改造推送 cron：推送后调用 `update_item_status(updated_by="hermes-cron", status="pushed")`（v4.2 已实现，v5.0 改用 helper 统一锁机制）
- [x] 2.3 改造深度分析 cron：分析后调用 `update_item_status(updated_by="hermes-cron", status="interested")`（v5.0 新增）
- [x] 2.4 改造归档 cron：归档后调用 `update_item_status(updated_by="hermes-cron", status="archived")`（v5.0 新增）
- [x] 2.5 验证：三个脚本均通过功能测试，item-status.json 正确更新

**验收标准**：
- [x] 已归档论文不再被推送（`get_processed_ids()` 返回 11 篇，select_candidates 正确跳过 1 篇）
- [x] 推送/分析/归档操作后 `item-status.json` 的 `updated_by` 字段正确标记为 `hermes-cron`
- [x] `state_sync.py` 的 `get_processed_ids()` 返回的 ID 被 cron 正确跳过
- [x] 新建 `item_status_helper.py` 共享模块：与 CoPilot 共用 `/tmp/linsai-copilot-item-status.lock` 锁文件
- [x] select_candidates.py 的 v4.2 并发安全隐患已修复（从无锁 json 读写改为 fcntl 锁保护）
- [x] CoPilot 侧测试无回归：核心 116/116 + Web API 70/70

**实际变更文件**（hermes 端）：
- `knowledge_base/scripts/item_status_helper.py`（新建，hermes 端统一状态助手）
- `knowledge_base/scripts/select_candidates.py`（改用 helper，加 fcntl 锁）
- `knowledge_base/scripts/mark_deep_analyzed.py`（新增 item-status 同步 → interested）
- `knowledge_base/scripts/archive_discussion.py`（新增 item-status 同步 → archived）

**风险**：低。hermes 端原文件已备份到 `.v5-backup-20260719/`。

---

### 阶段 3：kanban_reader + 任务看板桥接（2 天）【✅ 已完成】

**问题**：CoPilot 任务面板只显示本地 JSON 文件任务，看不到 hermes kanban.db 的 22 个任务。用户在两端各自维护任务列表，状态不同步。

**任务清单**：
- [x] 3.1 新建 `scripts/kanban_reader.py`：SQLite 读取层
  - [x] `list_tasks(status_filter)` → 11 个非归档任务（hermes 9 态 → CoPilot 4 态映射）
  - [x] `get_task(task_id)` → 单任务详情
  - [x] `create_task(title, assignee, created_by)` → INSERT kanban.db
  - [x] `update_task_status(task_id, status)` → UPDATE（CoPilot 4 态 → hermes 9 态）
- [x] 3.2 `kanban_reader.py::_self_check()` 验证读取真实 kanban.db（6/6 通过）
- [x] 3.3 改造 `web_routes_tasks.py`：`GET /api/tasks` 合并 hermes kanban + 本地任务
- [x] 3.4 改造 `web/js/task.js`：渲染 kanban 任务，来源标签（紫色 hermes badge）
- [x] 3.5 CoPilot 新建任务（assignee=hermes）→ INSERT kanban.db（created_by="copilot"）
- [x] 3.6 保留本地 tasks/ 目录兼容降级（kanban.db 不可用时回退本地）
- [x] 3.7 测试：Web API 返回 14 任务（11 hermes + 3 本地），核心 116/116 + Web API 70/70

**验收标准**：
- [x] Web 界面展示 hermes 11 个非归档任务（22 总计，11 归档已过滤）
- [x] hermes 任务状态正确映射（todo→backlog, running→active, blocked→paused, done→completed）
- [x] 任务卡片显示来源标签（hermes 紫色 badge）
- [x] CoPilot 新建任务（assignee=hermes）写入 kanban.db
- [x] kanban 任务状态更新可通过 CoPilot Web 界面拖拽
- [x] kanban.db 不可用时回退本地任务（兼容降级）

**实际变更文件**：
- `scripts/kanban_reader.py`（新建，SQLite 读写层 + 状态映射）
- `scripts/web_routes_tasks.py`（_task_list/_task_get/_task_create/_task_update 集成 kanban）
- `web/js/task.js`（来源标签 + hermes assignee 显示）
- `web/css/style.css`（.task-source-badge 样式）

**技术决策**：
- SQLite 连接用 `PRAGMA query_only=ON` 保护读取连接（而非 `mode=ro` URI，因 WAL 模式需要访问 -wal/-shm 文件）
- 写入连接用 WAL 模式 + `busy_timeout=5000`，与 hermes worker 并发安全
- 状态映射：hermes 9 态 → CoPilot 4 态（triage/todo/scheduled/ready→backlog, running/review→active, blocked→paused, done/archived→completed）
- kanban 任务 ID 以 `t_` 前缀识别，路由到 kanban_reader；本地任务 ID 以 `TASK-` 前缀识别，路由到 task_manager

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
| P0 路径修复+fcntl锁 | ✅ 已完成 | 6/6 | briefing_sync, common |
| 阶段 1 索引 hermes wiki | ✅ 已完成 | 7/7 | kb_index |
| 阶段 2 hermes cron 消费状态 | ✅ 已完成 | 5/5 | hermes scripts |
| 阶段 3 kanban 任务桥接 | ✅ 已完成 | 7/7 | kanban_reader, task.js |
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
