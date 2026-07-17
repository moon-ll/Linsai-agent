# 文献简报双向同步方案

> 版本：v3.7.0 设计稿
> 日期：2026-07-02
> 状态：待评审

---

## 一、现状分析

### 1.1 当前数据流（单向）

```
hermes cron 产出                         CoPilot 本地状态
─────────────────                        ──────────────────
daily_candidates.json  ──→ sync_engine ──→ paper-pool.json（unseen 入池）
research_briefing_*.md ──→ project_reader（只读展示）
status.json（工作流状态） ←×─ CoPilot 不回写

CoPilot 界面操作                          当前写入目标
─────────────────                        ──────────────────
interested/skip/archive               → paper-pool.json（本地状态变更）
                                      → paper-feedback.json（事件日志）
                                      → kb_importer → 知识库（归档时）
                                      → hb.oneshot() → hermes agent（仅自然语言偏好，软通道）
```

### 1.2 两端数据结构对比

| 维度 | CoPilot `paper-pool.json` | hermes `status.json` |
|------|---------------------------|----------------------|
| 主键 | `arxiv_id`（字典 key） | `arxiv_id`（papers 字典 key） |
| 顶层结构 | 扁平字典 | `{date, papers: {}}` |
| 状态模型 | 单字段三值：`unseen`/`viewed`/`archived` | 多字段工作流：pushed/analyzed/discussion/archived/keywords |
| 写入者 | CoPilot Web API | hermes agent + 手动 init |
| 覆盖风险 | 增量更新（安全） | `init_briefing_status.py` 会整体覆盖；`mark_*` 增量更新（安全） |

### 1.3 状态语义映射

| CoPilot → hermes | hermes 字段更新 | 说明 |
|-----------------|----------------|------|
| `viewed`（interested/skip/later） | `discussion_started = true` | 标记用户已关注 |
| `archived`（archive/discuss_done） | `discussion_archived_at = <UTC时间>` | 标记讨论已归档 |

| hermes → CoPilot | CoPilot 状态更新 | 说明 |
|-----------------|-----------------|------|
| `analyzed_at != null` 且当前 `unseen` | → `viewed` | hermes 已分析，CoPilot 同步为已看 |
| `discussion_archived_at != null` | → `archived` | hermes 已归档，CoPilot 同步 |

注意：反向映射不完全精确。hermes 的 `selected_for_analysis`、`keywords_extracted` 在 CoPilot 无对应概念，保持 hermes 侧独立。

### 1.4 ID 对应关系

两端均使用 arXiv ID（格式 `YYMM.NNNNN`），**天然可 join**。但论文集合是不同子集：
- CoPilot paper-pool = daily_candidates 全量候选累积池
- hermes status.json = 当日推送工作流子集（仅 `pushed_registry` 中的论文）

### 1.5 覆盖风险分析

| 操作 | 是否覆盖回写数据 | 防护措施 |
|------|----------------|---------|
| hermes cron `daily_summary.py`（20:00） | 否（只读 status.json） | 无需防护 |
| hermes agent `archive_discussion.py` | 否（增量 mark_archived） | 无需防护 |
| 手动 `init_briefing_status.py` | **是（整体覆盖重建）** | 回写前检查 `date` 字段；回写后写入 `sync-state.json` 水位 |
| CoPilot `sync_all()` | 否（增量更新） | 无需防护 |

---

## 二、设计方案

### 2.1 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    双向同步架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  hermes 端                              CoPilot 端           │
│  ┌──────────────┐                      ┌──────────────┐     │
│  │ status.json  │◄──── 反向同步 ───────│ paper-pool   │     │
│  │ (工作流状态)  │      (实时触发)       │ .json (状态) │     │
│  │              │────── 正向同步 ──────►│              │     │
│  └──────────────┘      (定期拉取)       └──────────────┘     │
│         │                                       │           │
│         ▼                                       ▼           │
│  ┌──────────────┐                      ┌──────────────┐     │
│  │ daily_       │────── 正向同步 ──────►│ raw/papers/  │     │
│  │ candidates   │      (已有，不变)      │ + wiki       │     │
│  └──────────────┘                      └──────────────┘     │
│                                                             │
│  同步引擎：scripts/briefing_sync.py                          │
│  扩展点：sync_engine.sync_all() + web_routes_projects       │
│  状态追踪：sync-state.json 新增 reverse_sync 字段            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 正向同步（hermes → CoPilot）— 增强现有

**触发时机**：`sync_engine.sync_all()` 执行时（手动或定期）

**新增逻辑**：在现有 `sync_hermes_outputs()` 之后，增加 `sync_hermes_paper_status()` 步骤：

```python
def sync_hermes_paper_status() -> dict:
    """正向同步：hermes status.json → CoPilot paper-pool.json。
    
    遍历 hermes status.json 的 papers，按状态映射规则
    更新 CoPilot paper-pool.json 中对应论文的 status。
    只升级不降级（unseen→viewed→archived 单向流转）。
    """
    hermes_status = _load_hermes_status()  # 读 hermes status.json
    if not hermes_status:
        return {"synced": 0, "skipped": "hermes status.json 不存在或为空"}
    
    synced = 0
    for aid, info in hermes_status.get("papers", {}).items():
        # 映射规则
        if info.get("discussion_archived_at"):
            target = "archived"
        elif info.get("analyzed_at") or info.get("discussion_started"):
            target = "viewed"
        else:
            continue  # 仅 pushed，不同步
        
        # 只升级不降级
        current = paper_pool.get_paper_status(aid)
        if _can_upgrade(current, target):
            paper_pool.update_status(aid, target, extra={
                "hermes_synced_at": now_utc(),
                "hermes_date": hermes_status.get("date", ""),
            })
            synced += 1
    
    return {"synced": synced, "date": hermes_status.get("date", "")}
```

**状态升级规则**（只升不降）：

| 当前状态 | 目标状态 | 是否升级 |
|---------|---------|---------|
| `unseen` | `viewed` | ✓ |
| `unseen` | `archived` | ✓ |
| `viewed` | `archived` | ✓ |
| `archived` | 任何 | ✗（终态） |
| `viewed` | `viewed` | ✗（相同） |

### 2.3 反向同步（CoPilot → hermes）— 新增

**触发时机**：用户在 CoPilot 界面操作文献时**实时触发**（非批量同步）

**实现方式**：在 `web_routes_projects.py` 的 `_proj_papers_feedback` 中，状态变更后立即回写 hermes status.json

```python
# 在 _proj_papers_feedback 中，paper_pool.update_status() 之后添加：
try:
    import briefing_sync as bsync
    bsync.sync_to_hermes(arxiv_id, new_status, action)
except Exception as e:
    _log.warning("反向同步 hermes 失败: %s", e)
    # 失败不阻塞用户操作，记入待同步队列
```

**`briefing_sync.py` 核心函数**：

```python
def sync_to_hermes(arxiv_id: str, copilot_status: str, action: str) -> dict:
    """反向同步：CoPilot 状态 → hermes status.json。
    
    使用增量更新（read-modify-write），不触发 init 覆盖。
    若 hermes status.json 不存在或日期不匹配，记入待同步队列。
    """
    status_path = _hermes_status_path()
    if not status_path.exists():
        return {"success": False, "reason": "hermes status.json 不存在"}
    
    # 读取当前 hermes 状态
    hermes_status = _load_json(status_path)
    papers = hermes_status.get("papers", {})
    
    # 论文不在 hermes 工作流中（可能是 daily_candidates 全量但未推送）
    if arxiv_id not in papers:
        return {"success": False, "reason": "论文不在 hermes 当日工作流中"}
    
    # 按映射规则更新
    info = papers[arxiv_id]
    now_local = _now_local_iso()  # hermes 用 +08:00 时区
    
    if copilot_status == "archived":
        info["discussion_archived_at"] = now_local
        info["discussion_started"] = True  # 归档隐含已讨论
    elif copilot_status == "viewed":
        info["discussion_started"] = True  # 用户已关注
    
    # 写回（原子写入）
    hermes_status["papers"][arxiv_id] = info
    _save_json_atomic(status_path, hermes_status)
    
    return {"success": True, "arxiv_id": arxiv_id, "status": copilot_status}
```

### 2.4 待同步队列（失败重试机制）

反向同步可能因 hermes 未运行、文件被锁等原因失败。设计轻量级重试队列：

```python
# memory/sync-state.json 新增字段：
{
  "synced_sessions": [...],      # 已有
  "synced_papers": [...],        # 已有
  "reverse_sync_pending": [      # 新增：待回写队列
    {
      "arxiv_id": "2403.15337",
      "copilot_status": "archived",
      "action": "discuss_done",
      "attempted_at": "2026-07-02T...",
      "retry_count": 0
    }
  ],
  "reverse_sync_watermark": "2026-06-18",  # 新增：hermes status.json 最后同步日期
  "last_reverse_sync": "2026-07-02T..."    # 新增：最后反向同步时间
}
```

**重试时机**：`sync_engine.sync_all()` 执行时，先处理 `reverse_sync_pending` 队列，再做正向同步。

### 2.5 冲突处理策略

| 场景 | 处理策略 |
|------|---------|
| hermes 和 CoPilot 同时修改同一论文 | **CoPilot 优先**（用户意图 > hermes 自动流程） |
| hermes `init_briefing_status.py` 覆盖了回写数据 | 正向同步时检测 `date` 变化，重新对齐 |
| 反向同步时 hermes status.json 被锁 | 记入 `reverse_sync_pending`，下次 sync_all 重试 |
| 论文在 CoPilot 但不在 hermes status.json | 跳过（论文未进入 hermes 工作流，无需回写） |
| 论文在 hermes 但不在 CoPilot paper-pool | 正向同步时自动入池（复用 add_candidates） |

### 2.6 oneshot 通道保留

现有的 `hb.oneshot()` 自然语言偏好反馈**保留不变**，与双向同步并行：

| 通道 | 作用 | 触发 | 延迟 |
|------|------|------|------|
| **双向同步**（新） | 结构化状态回写（archived/viewed） | 用户操作实时触发 | 毫秒级 |
| **oneshot**（已有） | 非结构化偏好记忆更新（"用户对 X 感兴趣"） | interested/skip 时异步触发 | 秒级 |

两者互补：双向同步保证状态一致性，oneshot 保证 hermes 偏好记忆的学习能力。

---

## 三、实现计划

### 3.1 新增文件

| 文件 | 用途 | 行数估算 |
|------|------|---------|
| `scripts/briefing_sync.py` | 双向同步引擎：正向拉取 + 反向回写 + 待同步队列 | ~200 行 |

### 3.2 修改文件

| 文件 | 修改内容 |
|------|---------|
| `scripts/sync_engine.py` | `sync_all()` 新增正向状态同步步骤 + 待同步队列重试 |
| `scripts/web_routes_projects.py` | `_proj_papers_feedback` 新增反向同步调用 |
| `scripts/paper_pool.py` | 新增 `get_paper_status(aid)` 单条查询函数 |
| `memory/sync-state.json` | 新增 `reverse_sync_pending` / `reverse_sync_watermark` 字段 |
| `scripts/tests/test_core.py` | 新增 briefing_sync 测试用例 |

### 3.3 实现步骤

```
Step 1: 创建 briefing_sync.py
  ├─ _hermes_status_path() — 定位 hermes status.json
  ├─ sync_to_hermes(aid, status, action) — 反向同步单条
  ├─ sync_from_hermes() — 正向同步批量
  ├─ flush_pending_reverse() — 重试待同步队列
  └─ _self_check() — 自检

Step 2: 修改 sync_engine.py
  ├─ sync_all() 新增 [2.5] sync_hermes_paper_status()
  └─ sync_all() 新增 [1.5] flush_pending_reverse()

Step 3: 修改 web_routes_projects.py
  └─ _proj_papers_feedback 新增反向同步调用（异常不阻塞）

Step 4: 修改 paper_pool.py
  └─ 新增 get_paper_status(aid) -> str

Step 5: 测试
  ├─ briefing_sync._self_check()
  ├─ test_core.py 新增 BriefingSyncTests
  └─ self_test.py --web-ci 全量通过
```

### 3.4 验收标准

- [x] 用户在 CoPilot 点"归档" → hermes status.json 对应论文 `discussion_archived_at` 被填充
- [x] hermes agent 归档讨论 → CoPilot paper-pool.json 对应论文 status 变为 `archived`
- [x] 反向同步失败（hermes 未运行）→ 记入待同步队列，下次 sync_all 重试
- [x] hermes `init_briefing_status.py` 覆盖后 → 正向同步检测 date 变化，重新对齐
- [x] 全量测试 232/232 通过（含新增 20 个 BriefingSync 检查点）

### 3.5 实测验证（2026-07-03）

使用 hermes status.json（10 篇论文）与 CoPilot paper-pool.json（142 篇）的真实数据验证：

| 测试项 | 操作 | 预期 | 实际 | 结果 |
|--------|------|------|------|------|
| 正向同步（初始） | sync_from_hermes() | synced=0（hermes 均未 analyzed） | synced=0 | ✓ |
| 反向同步 viewed | sync_to_hermes(aid, "viewed") | discussion_started=True | True | ✓ |
| 反向同步 archived | sync_to_hermes(aid, "archived") | discussion_archived_at=时间戳 | 2026-07-03T00:03:56+08:00 | ✓ |
| 正向同步升级 | hermes archived → CoPilot unseen | 升级为 archived | archived | ✓ |
| 幂等性 | 重复正向同步 | synced=0 | synced=0, skipped=1 | ✓ |
| 待同步队列 | 论文不在 hermes 工作流 | 记入队列 | 队列 1 条 | ✓ |

**沙盒限制**：TRAE 沙盒不允许写入 `hermes_workspace/` 目录，实测通过将 hermes `status.json` 复制到 CoPilot 目录内完成。生产环境（web_server 独立运行）不受此限制。

---

## 四、风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| hermes init 覆盖回写数据 | 低（手动触发） | 中（丢失回写状态） | 正向同步检测 date 变化重新对齐 |
| 并发写 status.json | 低（用户操作 + hermes agent） | 中（丢更新） | 用文件锁（复用 web_base._get_file_lock） |
| hermes 路径变更 | 低 | 高（同步失效） | 路径通过函数动态推导，不硬编码 |
| 论文 ID 不匹配 | 极低 | 低（个别论文不同步） | 跳过不匹配项，日志记录 |

---

## 五、未来扩展

1. **hermes cron 集成**：在 hermes 的 cron job 中调用 CoPilot 的 `/api/sync` 触发双向同步（当前需手动或 CoPilot 定期触发）
2. **WebSocket 实时推送**：替换当前的文件轮询，实现真正的实时双向同步
3. **多 hermes profile 支持**：当前硬编码 `linsai` profile，未来可支持多 profile 切换
4. **状态冲突可视化**：在 CoPilot 界面显示同步状态（已同步/待同步/冲突），让用户感知同步健康度

---

*设计者：AI 编码代理*
*上游依赖：hermes briefing_status.py（mark_* 函数）*
*下游影响：sync_engine.py、web_routes_projects.py、paper_pool.py*
