# 统一状态同步架构设计（v4.2）

> 状态：**设计方案，待审批**
> 日期：2026-07-17
> 目标：Copilot 作为 hermes 的操作台，所有状态双向同步，等价于飞书操作

## 一、当前问题诊断

### 两套独立状态系统

```
hermes 侧                          Copilot 侧
┌──────────────────┐              ┌──────────────────┐
│ briefing_state   │              │ paper-pool.json  │
│ daily_candidates │──搬运候选──▶│ (142篇)          │
│ NSFC state.md    │              │ paper-feedback   │
│ cron jobs (4个)  │              │ nsfc-decisions   │
└──────────────────┘              │ sync-state       │
       ↑                          └──────────────────┘
       │ 异步oneshot通知（但cron不消费）    │
       └────────────────────────────────--┘
                    断裂点
```

**核心断裂**：
1. Copilot 归档/讨论 → hermes cron 不知道（重复推送已处理论文）
2. hermes 推送/筛选 → Copilot 不知道推送状态
3. 两套状态文件（briefing_state vs paper-pool），数据重叠但不互通
4. NSFC 决策在 Copilot 的 nsfc-decisions.json，hermes 的 BRAIN 读 discussions/ 目录——两套写入点

## 二、设计原则

1. **单一状态源**：每篇论文/每个任务只有一个权威状态文件
2. **双向同步**：Copilot 操作 → hermes 可见；hermes 操作 → Copilot 可见
3. **向后兼容**：不破坏现有 cron 逻辑，新增同步层
4. **可扩展**：新项目/任务自动纳入同步协议

## 三、统一状态协议

### 3.1 论文状态（文献简报工作流）

**权威状态文件**：`~/Desktop/hermes_workspace/knowledge_base/AI_wiki/briefings/item-status.json`

```json
{
  "version": "1.0",
  "updated_at": "2026-07-17T12:00:00Z",
  "items": {
    "2403.15337": {
      "arxiv_id": "2403.15337",
      "title": "...",
      "status": "discussed",          // unified: pool/candidate/pushed/viewed/interested/discussing/discussed/archived/skipped
      "direction": "固体HHG",
      "score": 0.95,
      "first_seen": "2026-06-19T08:23:00Z",
      "last_updated": "2026-07-17T12:00:00Z",
      "updated_by": "copilot",        // copilot / hermes-cron / feishu
      "history": [                    // 状态变更历史
        {"status":"pool", "by":"hermes-cron", "at":"2026-06-19T08:23:00Z"},
        {"status":"pushed", "by":"hermes-cron", "at":"2026-06-19T08:28:00Z"},
        {"status":"viewed", "by":"copilot", "at":"2026-07-01T10:00:00Z"},
        {"status":"discussed", "by":"copilot", "at":"2026-07-04T15:00:00Z"}
      ],
      "discussion_path": "knowledge/wiki/projects/deepxiv-论文库/讨论记录/讨论-20260704-2403.15337.md",
      "archived_to": "raw/papers/2024-2403.15337-xxx.md"
    }
  }
}
```

**统一状态枚举**（覆盖完整生命周期）：
```
pool → candidate → pushed → viewed → interested → discussing → discussed → archived
                                                                    ↗
                                                              skipped
```

### 3.2 任务/项目状态

**权威状态文件**：每个项目目录下的 `.copilot-sync.json`

```
hermes_workspace/research_proposals/2026_NSFG_strongfield_ultrafast/.copilot-sync.json
hermes_workspace/knowledge_base/.copilot-sync.json
```

```json
{
  "project": "2026_NSFG_strongfield_ultrafast",
  "last_hermes_update": "2026-07-17T08:00:00Z",  // hermes cron 最后更新时间
  "last_copilot_view": "2026-07-17T12:00:00Z",   // Copilot 最后查看时间
  "decisions": {
    "pd_001": {
      "title": "T3 采用 SBE 还是 TDDFT",
      "status": "discussed",         // pending/approved/rejected/discussing/discussed
      "decided_by": "copilot",       // copilot / hermes / feishu
      "decided_at": "2026-07-04T15:00:00Z",
      "discussion_path": "discussions/2026-07-04_decisions.md"
    }
  },
  "tasks": {
    "task_001": {
      "title": "调研 MoS2 圆偏振 HHG",
      "status": "in_progress",       // created/assigned/in_progress/completed/failed
      "assignee": "hermes",
      "dispatch_id": "dispatch_xxx",
      "created_by": "copilot",
      "created_at": "2026-07-04T10:00:00Z"
    }
  }
}
```

## 四、同步机制

### 4.1 Copilot → hermes（操作台写回）

**触发点**：Copilot 的每个状态变更操作

| Copilot 操作 | 写回 hermes 的 |
|-------------|---------------|
| 👍感兴趣 | `item-status.json` 该论文 status→interested |
| 💬讨论 | `item-status.json` status→discussing + discussion_path |
| 讨论归档 | `item-status.json` status→discussed/archived + archived_to |
| 👎跳过 | `item-status.json` status→skipped |
| NSFC 通过/否决 | `.copilot-sync.json` decisions 状态更新 |
| NSFC 讨论→总结 | `.copilot-sync.json` + discussions/ 写回 |
| 任务派 hermes | `.copilot-sync.json` tasks 新增 |

**实现**：`scripts/state_sync.py` 统一状态同步层

```python
def sync_item_status(arxiv_id, new_status, updated_by="copilot", **extra):
    """更新论文统一状态，写入 hermes 的 item-status.json"""
    path = HERMES_BRIEFINGS / "item-status.json"
    data = load_json(path)
    item = data["items"].setdefault(arxiv_id, {})
    item["status"] = new_status
    item["last_updated"] = now()
    item["updated_by"] = updated_by
    item["history"].append({"status": new_status, "by": updated_by, "at": now()})
    item.update(extra)
    save_json(path, data)
```

### 4.2 hermes → Copilot（cron 产出同步）

**已有**：`sync_engine.sync_all()` 搬运候选论文 → paper-pool（保留）

**新增**：
- hermes cron 推送论文到飞书时，`item-status.json` 标记 pushed
- Copilot 读 `item-status.json` 同步到 paper-pool（pushed 的论文在 Copilot 标记"已推送飞书"）
- hermes cron 检索入池时，**跳过 item-status 里 status≥viewed 的论文**（避免重复推送已处理论文）

### 4.3 状态合并规则

当 Copilot 和 hermes 对同一论文有不同状态时：
- **以最新时间为准**（`last_updated` 更新的覆盖）
- 不可逆状态优先：`archived > discussed > skipped > viewed > pushed > candidate > pool`
- 冲突记录到 `history` 供追溯

## 五、对现有 cron 的改造

### 5.1 文献简报 cron 改造

**检索入池 cron（4次/天）**：新增一步——读 `item-status.json`，跳过 status≥viewed 的论文
```python
# 在 select_candidates.py 里加
processed = load_processed_arxiv_ids()  # 读 item-status.json
candidates = [c for c in candidates if c["arxiv_id"] not in processed]
```

**推送 cron（08:28）**：推送后更新 `item-status.json` 标记 pushed
```python
# 推送成功后
for paper in pushed_papers:
    state_sync.sync_item_status(paper["arxiv_id"], "pushed", updated_by="hermes-cron")
```

**汇总 cron（23:30）**：读 `item-status.json` 生成日报（含 Copilot 操作的论文状态变化）

### 5.2 NSFC 项目改造

**BRAIN cron**：读 `.copilot-sync.json` 的 decisions，知道哪些决策已在 Copilot 讨论过
- 不重复提议已 approved/rejected 的决策
- Copilot 讨论总结写回 `discussions/` 后，BRAIN 下次运行时自动读取

## 六、新项目/任务的自动纳入

### 6.1 新项目注册

当 hermes 或 Copilot 创建新项目时，自动生成 `.copilot-sync.json`：
```python
def register_project(project_dir, project_name):
    sync_file = project_dir / ".copilot-sync.json"
    if not sync_file.exists():
        save_json(sync_file, {"project": project_name, "decisions": {}, "tasks": {}})
```

### 6.2 新任务类型

新任务（如审稿回复/实验设计）只需：
1. 在 `.copilot-sync.json` 的 `tasks` 里注册
2. 遵循统一状态枚举（created→assigned→in_progress→completed）
3. 产出沉淀到知识库的约定路径

### 6.3 新文献产出源

如果未来有新的文献来源（不只是 arXiv/deepxiv），只需在 `item-status.json` 的 item 里加 `source` 字段，同步逻辑不变。

## 七、前端改造

### 7.1 文献简报面板增强

- 每篇论文卡片显示**统一状态**（来自 item-status.json，而非仅 paper-pool）
- 显示"已推送飞书"标记（pushed 状态）
- 状态变更时实时同步（不需手动点"同步"按钮）

### 7.2 NSFC 面板增强

- 待决策项显示**来源**（hermes BRAIN 提议 / Copilot 讨论 / 飞书）
- 决策状态变更实时写回 `.copilot-sync.json`

### 7.3 任务面板增强

- 派给 hermes 的任务显示执行状态（读 `.copilot-sync.json` 的 task status）
- hermes 完成后状态自动更新

## 八、实施路线（3 个迭代）

### 迭代 1：统一状态层（核心突破）
1. 新建 `scripts/state_sync.py`（统一状态读写）
2. 创建 `item-status.json`（从现有 paper-pool + briefing_state 合并初始化）
3. Copilot 操作接入 state_sync（写回 hermes 的 item-status.json）
4. hermes cron 推送后更新 item-status.json

### 迭代 2：cron 改造
5. 检索入池 cron 跳过已处理论文
6. 推送 cron 更新 pushed 状态
7. NSFC BRAIN 读 .copilot-sync.json

### 迭代 3：前端实时同步
8. 文献卡片显示统一状态 + 推送标记
9. 任务面板显示 hermes 执行状态
10. 自动同步（去掉手动同步按钮）

## 九、向后兼容

- `paper-pool.json` 保留（作为 Copilot 本地缓存），但权威状态在 `item-status.json`
- `briefing_state.json` 保留（hermes cron 继续用），但同步层会双向更新
- `sync_engine.sync_all()` 保留（搬运候选），新增状态同步步骤
- 现有 cron prompt 不大改，只在脚本层（select_candidates.py 等）加状态过滤

## 十、成功指标

- ✅ Copilot 归档一篇论文后，hermes 推送 cron 不再重复推送
- ✅ hermes 推送到飞书后，Copilot 文献卡片显示"已推送"
- ✅ NSFC 决策在 Copilot 通过后，hermes BRAIN 不再重复提议
- ✅ 新项目自动纳入同步（无需手动配置）
- ✅ 状态变更可追溯（history 记录）

---

*核心洞察：当前是"两套独立系统，一个搬运点"。目标是"一套状态协议，两个操作面（Copilot Web + 飞书/hermes CLI），状态实时双向同步"。Copilot 不仅是可视化界面，而是和飞书等价的操作台。*
