# 林赛总控能力设计稿 v6.7

> **版本**：v6.7
> **日期**：2026-07-27
> **作者**：AI 编码代理
> **状态**：设计阶段

## 1. 目标

让 **林赛（linsai profile）** 从"方向校准官"升级为"研究管线总控"，具备：

1. **跨 profile 仪表盘** — 实时查看 7 个 profile 的运行状态、性能、错误
2. **调度策略自动调优** — 基于历史数据自动调整错峰间隔、超时、重试
3. **失败模式分析 + prompt 优化** — 从失败日志中提取模式，给出 prompt 修正建议
4. **Pipeline 状态机成长** — 监控 pipeline-runner 质量，必要时追加调优环节

## 2. 架构

### 2.1 新增模块

| 模块 | 路径 | 职责 |
|------|------|------|
| `orchestrator.py` | `scripts/orchestrator.py` | 总控核心：仪表盘 + 调优 + 失败分析 + 链路监控 |
| `profile_health.py` | `scripts/profile_health.py` | 单 profile 健康度计算：成功率/平均耗时/最近错误 |
| `strategy_optimizer.py` | `scripts/strategy_optimizer.py` | 调度策略自调优：基于历史自动调整参数 |
| `failure_analyzer.py` | `scripts/failure_analyzer.py` | 失败模式分析：聚类错误、生成 prompt 修正建议 |
| `tuning_log.json` | `memory/tuning-log.json` | 调优历史记录（每次调整的策略+原因+效果） |
| `failure_patterns.json` | `memory/failure-patterns.json` | 失败模式库（聚类后的模式 + 推荐 prompt 修改） |

### 2.2 与现有模块的关系

```
proposal_lifecycle.py（业务执行）
        │
        │ 每次 optimize_cycle / run_cron_sweep
        ▼
orchestrator.py（总控协调）
        │
        ├── profile_health.py   （读取 hermes_bridge / 输出 profile 健康度）
        ├── strategy_optimizer.py（读取 proposal_lifecycle / 输出调度参数）
        ├── failure_analyzer.py  （读取 linsai.log / 输出 prompt 建议）
        └── pipeline_monitor.py  （读取 hermes_pipeline / 输出链路质量）
```

### 2.3 Web API 扩展

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/orchestrator/dashboard` | GET | 总仪表盘（4 区合一：profile 健康 + 链路质量 + 调度状态 + 调优建议） |
| `/api/orchestrator/profiles/health` | GET | 7 个 profile 的详细健康度 |
| `/api/orchestrator/strategies` | GET/POST | 当前调度策略 / 应用新策略 |
| `/api/orchestrator/failures/patterns` | GET | 失败模式聚类 + 修正建议 |
| `/api/orchestrator/pipeline/quality` | GET | pipeline-runner 最近 5 次运行质量 |
| `/api/orchestrator/tuning-log` | GET | 调优历史 |

### 2.4 前端面板

- `web/js/orchestrator.js` — 总控仪表盘（4 个子面板）
- 在 index.html 导航增加"🎛️ 总控"入口

## 3. 四大能力详细设计

### 3.1 跨 profile 仪表盘

**数据来源**：
- `hermes_bridge.list_team_profiles()` — 7 个 profile 状态
- `logs/linsai.log` 最近 100 行 — 派活成功/失败记录
- `memory/usage_tracker.json` — token 用量

**计算指标**（每个 profile）：
- 状态：idle / working / blocked / offline
- 最近 24h 成功率：success_count / (success_count + fail_count)
- 平均耗时（基于日志时间戳差）
- 最近错误（最近一次失败的前 200 字符）
- 建议：如"成功率 < 80% → 切换 fallback provider"

**输出**：
```json
{
  "profiles": {
    "linsai": {"status": "idle", "success_rate_24h": 1.0, "avg_duration_s": 240, "recent_error": ""},
    "researcher": {"status": "offline", "success_rate_24h": 0.4, "avg_duration_s": 180, "recent_error": "timeout 300s"},
    "writer": {"status": "working", "success_rate_24h": 0.9, "avg_duration_s": 600, "recent_error": ""},
    ...
  },
  "alerts": [
    {"level": "warning", "type": "low_success_rate", "profile": "researcher", "msg": "成功率仅 40%，建议检查网络或切换 provider"},
    ...
  ]
}
```

### 3.2 调度策略自动调优

**可调参数**（`proposal_lifecycle.DEFAULT_*` 常量）：
- `DEFAULT_STAGGER_SECONDS`（课题间错峰间隔）— 当前 90
- `DEFAULT_MAX_ROUNDS`（单 proposal 最大轮数）— 当前 10
- `DEFAULT_SCORE_THRESHOLD`（达标分数）— 当前 0.7
- `DEFAULT_NO_IMPROVEMENT_LIMIT`（连续无提升轮数）— 当前 3
- critic_timeout / writer_timeout — 当前 300 / 600

**调优算法**：
```
if (过去7天每天平均派活次数 * 单次平均耗时) > 16小时 (GLM 限额):
    建议 stagger_seconds += 30
if (最近5天成功率 < 0.5):
    建议降低 max_rounds（避免重复无效轮次）
if (某 profile 连续3次超时):
    建议把该 profile 的 timeout 增加 50%
```

**输出**：
```json
{
  "current": {"stagger_seconds": 90, "max_rounds": 10, ...},
  "suggested": {"stagger_seconds": 120, "max_rounds": 8, ...},
  "reason": "过去7天每天平均派活 12 次 × 600s = 7200s，叠加错峰后接近 GLM 限额，建议加 stagger",
  "apply_action": "POST /api/orchestrator/strategies"
}
```

**应用策略**：通过 `POST /api/orchestrator/strategies` 触发，修改 `proposal_lifecycle.DEFAULT_*` 常量（运行时 monkey patch），并记录到 `tuning_log.json`。

### 3.3 失败模式分析 + prompt 优化

**数据源**：
- `logs/linsai.log` 全部失败行（[ERROR] / [WARNING]）
- `proposal_lifecycle` 的 `cron_failures` 字段
- 各 proposal 的 `score_history` 异常模式（如：连续 5 轮 score 相同）

**聚类规则**（按关键词正则分桶）：
- "score = 0" 模式 → critic 给了 0 分
- "申请书不存在" 模式 → proposal 草稿为空
- "hermes oneshot 失败" 模式 → 子进程崩溃
- "PYTHONHOME" / "encodings" 模式 → 环境变量问题（v6.6.3 已修）
- "timeout" 模式 → 超时

**Prompt 优化建议生成**：
```
pattern: "score = 0" 连续 3 轮
建议: 修改 _run_critic 的 prompt：
  旧: "请评审申请书"
  新: "请评审申请书。重要：如果申请书内容不完整（仅占位符），请在评分块中明确标注
       '本轮因内容缺失无法准确评分，建议先补充实质内容'，综合分应按现有实质内容评估，"
```

**输出**：
```json
{
  "patterns": [
    {
      "id": "score-zero-streak",
      "label": "连续 0 分",
      "occurrences": 12,
      "proposals": ["general-quantum-geometry-inversion-20260726", ...],
      "suggested_prompt_change": "在 critic prompt 中加 '内容缺失时给出 0.10 而非 0.00'",
      "expected_impact": "score_history 能区分 '空草稿' vs '完全失败'"
    }
  ]
}
```

### 3.4 Pipeline 状态机成长

**监控对象**：
- `hermes_pipeline.run_pipeline()` 的 6 阶段产物质量
- 每阶段产物大小、章节完整度、与预期模板的匹配度

**质量评分**：
- 产物文件存在 ✓
- 文件 ≥ 50 字节（基础）
- 文件 ≥ 2000 字节（实质内容）
- 关键章节标题全部存在（章节数 ≥ 6）
- 引用占位符 [CITE:xxx] 数量 ≥ 30

**成长机制**：
```
if (阶段 3 产物质量 < 0.6):
    自动追加阶段 3.5：调 analyst 重做
if (阶段 4 产物章节不完整):
    通知 writer profile，附加缺失章节列表
if (阶段 5 自检分 < 0.7):
    自动追加阶段 5.5：调 reviewer 二次审查
```

**输出**：
```json
{
  "proposal_id": "nsfc-2026-hhg",
  "stages": [
    {"stage": 0, "quality": 0.85, "issues": []},
    {"stage": 1, "quality": 0.72, "issues": ["文献综述缺少 2026 文献"]},
    {"stage": 2, "quality": 0.65, "issues": ["缺口分析深度不足"]},
    ...
  ],
  "growth_actions": [
    {"stage": 2, "action": "auto_retry", "reason": "quality 0.65 < 0.7", "next_attempt": "analyst + 增量上下文"}
  ]
}
```

## 4. 实施路线

| 阶段 | 任务 | 依赖 | 估时 |
|------|------|------|------|
| 1 | `profile_health.py`（读 log → 健康度） | 无 | 30 min |
| 2 | `failure_analyzer.py`（聚类 + 建议） | 1 | 30 min |
| 3 | `strategy_optimizer.py`（参数建议） | 1 | 30 min |
| 4 | `orchestrator.py`（统一入口 + 调度） | 1, 2, 3 | 45 min |
| 5 | `web_routes_orchestrator.py`（API） | 4 | 30 min |
| 6 | `web/js/orchestrator.js`（前端面板） | 5 | 45 min |
| 7 | 端到端测试 + 文档 | 全部 | 30 min |

**总估时**：4 小时

## 5. 兼容性

- 不破坏现有 proposal_lifecycle / hermes_pipeline / hermes_bridge 的 API
- 调度策略调优通过 monkey patch 运行时修改，不改源码
- 新增模块遵循 v6.2 边界规范：只依赖 common.py / paths.py / llm_gateway.py / hermes_bridge.py

## 6. 自检与回归

- 每个新模块必须含 `_self_check()` 函数
- `self_test.py --module` 扩展到 122+ 检查点（含 6 个新增）
- Web CI 扩展到 180+ 检查点（含 6 条新路由）
- 端到端：用真实 linsai.log（最近 7 天）做"事后调优"演示
