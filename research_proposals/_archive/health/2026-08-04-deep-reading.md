# 每日健康检查 · 深度阅读 · 2026-08-04

**触发**：用户指令"深度阅读今天推送的 2/4/5 并归档"
**范围**：2026-08-04 健康检查报告第 2/4/5 段（凭据 / Profile / 知识库）
**方法**：不只读当日数字，对比 7-31 / 8-03 / 8-04 三天趋势，找异常信号
**报告源**：`research_proposals/_archive/health/2026-08-04.{md,json}`
**归档路径**：`research_proposals/_archive/health/2026-08-04-deep-reading.md`

---

## 0. 三天趋势速览

| 段 | 7-31 | 8-03 | **8-04** | 趋势 |
|---|---|---|---|---|
| 2. 凭据 | ✓ 2/2 | ✓ 2/2 | **✓ 2/2** | 平稳 |
| 4. Profile | ✓ 全 idle/working | ✓ critic 100%/6 派活 | **⚠ writer/critic 双 blocked** | **↓ 急剧恶化** |
| 5. KB 综合分 | 0.789 ✓ | 0.673 ⚠ | **0.662 ⚠** | **↓ 持续下滑** |

**一句话结论**：凭据没问题，但**段 4（Profile）和段 5（KB）同步恶化**，且**恶化点都在对抗优化链路上**（writer + critic 是对抗轮的核心两个 profile，KB 综合分下滑的主因是 category_coverage 从 0.81 暴跌到 0.42）。

---

## 段 2 — Provider 凭据（看似 ✓，实则是核心矛盾）

### 当日数据

| Key | 状态 | 脱敏值 |
|---|---|---|
| `MINIMAX_API_KEY` | ✓ | `sk-c...mGDU` |
| `GLM_API_KEY` | ✓ | `1883...H7Qm` |

三天完全一致，`.env` 文件没动过。

### 深度解读：**这段绿是假绿**

**矛盾**：凭据在 `.env` 里存在（这段报告 ✓），但**段 4 显示 writer/critic 进入 blocked**。这意味着——

- `.env` 文件里有 key（daily_health_check.py 直接 read 文本，能拿到）
- 但 **hermes CLI 调用 writer/critic profile 时，这两个 key 没被正确加载到 provider 'zai' / 'minimax'**

这是 7-28 cron 报告里就已暴露的老问题：
> `No usable credentials found for provider 'zai'. Set GLM_API_KEY, ZAI_API_KEY, Z_AI_API_KEY.`

**根因不在 .env，在 hermes profile 配置 → provider 绑定**：
- writer profile 绑定了 `zai` provider，需要 `GLM_API_KEY` **或** `ZAI_API_KEY` **或** `Z_AI_API_KEY`
- `.env` 里有 `GLM_API_KEY`，但 hermes 可能要求的是 `ZAI_API_KEY`（命名空间不同）
- 或者 hermes 进程启动时没 source 这个 `.env`（环境变量没注入）

### 行动建议（按优先级）

1. **P0 验证 hermes 是否读到 key**：跑 `hermes --profile writer onesht "test"` 看是否仍报 `No usable credentials`。如果仍报，问题确认在 hermes 配置层
2. **P0 检查 hermes profile config**：`cat ~/.hermes/profiles/writer/config.yaml | grep -A2 provider` 看 writer 绑的是哪个 provider、需要哪个 env var
3. **P1 补加 `ZAI_API_KEY`**：如果 hermes 确实要这个命名，在 `.env` 加一行 `ZAI_API_KEY=<同 GLM_API_KEY 值>` 即可

**为什么这段报告显示 ✓ 不够**：daily_health_check.py 只检查"key 在 .env 里存在"，没检查"hermes 能否实际加载"。**这是脚本的盲点**——下次迭代应在段 2 加一条"hermes 可达性测试"。

---

## 段 4 — Profile 健康（恶化最严重的一段）

### 三天对比

| Profile | 7-31 | 8-03 | **8-04** |
|---|---|---|---|
| `linsai` | working | working | working |
| `pipeline-runner` | working | working | working |
| `researcher` | idle | idle | idle |
| `analyst` | idle | idle | idle |
| **`writer`** | idle (0 派活) | idle (0 派活) | **blocked, 83% 成功率, 6 派活** |
| **`critic`** | idle (0 派活) | **idle, 100%, 6 派活** | **blocked, 62% 成功率, 8 派活** |
| `reviewer` | idle | idle | idle |

### 深度解读

**关键变化 1**：writer 在 8-04 突然有了 6 次派活——**这是今天才发生的**（7-31 和 8-03 都是 0 派活）。说明：
- 自动优化链路在 8-03 到 8-04 之间**重新启动了**（可能是 v6.8 的微调度器 `lc-micro-scheduler` 跑起来了）
- 但启动后 **6 次里只成功了 5 次（83%）**，且 profile 状态被打成 blocked——**意味着最近一次失败**，触发了 blocked 判定

**关键变化 2**：critic 从 8-03 的 100%/6 派活，降到 8-04 的 62%/8 派活——
- 派活数从 6 → 8（多跑了 2 轮）
- 成功率从 100% → 62%（8 次里失败了 3 次）
- 状态从 idle → blocked

**这意味着**：对抗优化链路在 8-04 **跑得更多但失败更多**。可能是：
- (a) writer 凭证问题导致 writer 失败 → critic 被连锁触发但拿到空草稿 → critic 也失败
- (b) 某个 proposal 的优化进入死循环，反复重试（v6.8.1 的"失败自动重试 attempts<3"机制可能导致这个）
- (c) 5 个 optimizing proposal 里有 1-2 个的产物状态异常，触发连续失败

**`recent_error` 字段全是空**——这是脚本盲点。`profile_health.py` 的日志解析可能没抓到最新错误，或者错误被吞了。**下次迭代应让 recent_error 强制非空**（至少标"无最近错误"而不是空字符串）。

### 行动建议

1. **P0 看 linsai.log 最近的 writer/critic 错误**：`tail -200 logs/linsai.log | grep -E "writer|critic|error|失败"`
2. **P0 看 5 个 proposal 的 attempts 字段**：是否有 proposal 卡在"attempts=2 反复重试"状态
3. **P1 如果是连锁失败（writer 凭证问题）**：先修段 2 的 P0，writer 恢复后 critic 自然恢复

---

## 段 5 — 知识库（持续下滑，需关注）

### 三天综合分下滑

| 日期 | 综合分 | connectivity | category_coverage | alias_hit_rate | orphan_rate |
|---|---|---|---|---|---|
| 7-31 | **0.789 ✓** | 0.78 | **0.81** | 0.56 | 0.0 |
| 8-03 | **0.673 ⚠** | 0.61 | **0.59** | 0.56 | 0.0 |
| **8-04** | **0.662 ⚠** | 0.73 | **0.42** | 0.59 | 0.0 |

### 深度解读

**关键变化**：
- `raw_count` 从 208 → 231 → **233**（3 天涨 25 篇文献，今天 +2）
- `wiki_count` 从 121 → 154 → **155**（3 天涨 34 页，今天 +1）
- `graph_nodes` 从 72 → 99 → **105**（3 天涨 33 节点）
- `graph_edges` 从 238 → 245 → **291**（今天单日 +46 条边，图谱在快速连接）
- `graph_orphans` 始终 0（无孤儿，好）

**表面**：知识库在快速生长（节点+边都在涨）。

**但 `category_coverage` 从 0.81 → 0.59 → 0.42，三天腰斩**——这是综合分下滑的主因。

**根因分析**：
- `category_coverage = covered_pages / total_categories`
- 节点和边都在涨，但覆盖率反降——**意味着新增的文献/页面落在了**已覆盖类别之外的新类别**里
- 比如：今天推的 110 篇候选里有很多 altermagnet / Wigner crystal / chiral superconductivity 的论文（看 daily_candidates.md 第 40-55 行），**这些可能是 KB 之前没有的新类别**
- 新类别进来了，但还没有对应的"分类页"去覆盖它们——**覆盖率分母变大，分子没跟上**

**这不是坏事**——是知识库在扩展边界。但**综合分算法把"扩展"惩罚成了"下滑"**，这是算法设计的问题。

**`pending_distill` 从 208 → 231 → 233**——持续增长，说明**蒸馏（raw → wiki）速度跟不上入库速度**。3 天入了 25 篇，但 wiki 只增 34 页（含非论文的概念页），蒸馏积压在恶化。

### 行动建议

1. **P1 跑 KB 周维护**：`python3 scripts/kb_maintenance.py --weekly`——这会把 pending_distill 的积压处理一批
2. **P2 修正综合分算法**：`category_coverage` 不应单看"已覆盖类别占比"，而应看"新增类别的覆盖速度"——否则扩展边界的健康库永远被打低分
3. **P2 关注新类别**：今天的 daily_candidates 里 altermagnet / Wigner crystal / chiral SC 是新主题，看看 `knowledge/wiki/concepts/` 是否需要新建对应概念页

---

## 三段联读：一个隐藏的因果链

把段 2/4/5 联起来看，**有一个可能的因果链**：

```
段2: .env 有 key，但 hermes 没正确加载
      ↓
段4: writer/critic blocked → 对抗优化失败 → proposal 卡在优化中
      ↓
但段5: raw_count 持续涨（DeepXiv cron 每天自动入库新文献）
      ↓
蒸馏跟不上（pending_distill 233）→ wiki 增长慢
      ↓
新文献落在新类别 → category_coverage 暴跌
      ↓
综合分 0.662 ⚠
```

**也就是说**：段 5 的 KB 下滑**不是 KB 本身的问题**，是**输入端（DeepXiv cron）持续灌入 + 处理端（蒸馏/分类）跟不上**的失衡。而段 4 的 profile blocked 会让 writer 没法把新文献编入 wiki，进一步加剧失衡。

**根本解**：先修段 2 的 hermes 凭证加载 → 段 4 的 writer/critic 恢复 → 段 5 的蒸馏能跑起来 → KB 综合分回升。

---

## 脚本盲点（下次迭代修）

| 盲点 | 影响 | 建议修法 |
|---|---|---|
| 段 2 只查 .env 文本，不验证 hermes 实际可达 | 凭据假绿 | 加一条 `hermes --profile writer onesht "ping" 2>&1 \| grep -q "No usable credentials"` 失败则标 ⚠ |
| 段 4 `recent_error` 经常空 | 无法定位失败原因 | profile_health.py 解析 linsai.log 时，如果没找到 error，至少标"无最近错误（24h 内）"而非空字符串 |
| 段 5 `category_coverage` 算法惩罚扩展 | 健康库被打低分 | 改算法：要么看"覆盖速度"，要么把新类别 30 天宽限期 |

---

## 跨上下文指针

| 关联 | 位置 |
|---|---|
| 7-28 cron 报告（首次暴露 writer zai 凭证问题） | cron session `cron_0485e2e9ead5_20260728_085721` |
| 7-31 健康报告（基准日，全绿） | `_archive/health/2026-07-31.{md,json}` |
| 8-03 健康报告（KB 首次转 ⚠） | `_archive/health/2026-08-03.{md,json}` |
| 8-04 健康报告（本次深度阅读对象） | `_archive/health/2026-08-04.{md,json}` |
| daily_health_check.py 源码 | `scripts/daily_health_check.py` |
| 用户偏好"执行而非询问" | `memory/user-profile.json` |

---

## 决策清单（按优先级）

| 优先级 | 动作 | 预期效果 |
|---|---|---|
| **P0** | 验证 hermes 能否加载 GLM_API_KEY（`hermes --profile writer onesht "ping"`） | 确认段 2 假绿的真假 |
| **P0** | 看 linsai.log 最近 writer/critic 错误 | 定位段 4 blocked 根因 |
| P1 | 修 hermes 凭证配置（加 `ZAI_API_KEY` 或调整 profile provider 绑定） | 段 4 自动恢复 |
| P1 | 跑 `kb_maintenance.py --weekly` | 处理 pending_distill=233 积压 |
| P2 | 修 daily_health_check.py 段 2 加 hermes 可达性测试 | 凭据不再假绿 |
| P2 | 修 KB 综合分的 category_coverage 算法 | 综合分不再误判扩展 |
| P3 | 为 altermagnet / Wigner crystal 等新主题建概念页 | category_coverage 回升 |

---

_Powered by pipeline-runner · 2026-08-04T15:56:00Z_
_源数据: 3 天 6 份 JSON 报告对比（7-31 / 8-03 / 8-04）_