# 林赛自主研究助手 — 实现计划 v2.0

> **版本**: v2.0  
> **日期**: 2026-05-15  
> **目标**: 让林赛成为有记忆、能自主执行研究议程的"初级研究实习生"  
> **范围**: Phase 1（自主研究议程管理）+ Phase 2（沙箱执行器）  
> **前提条件**: 用户明确授权开启、已验证 Phase 1

---

## 一、项目概述

### 1.1 背景问题

当前 LinSai-CoPilot 的架构是**纯被动响应型**：

```
用户发消息 → 林赛响应 → 结束
```

这意味着：
- 用户不说话，林赛不动
- 林赛无法主动推进自己的研究目标
- 林赛无法对知识库的变化做出反应
- 林赛的记忆无法驱动其自主行动

### 1.2 目标定义（Goal）

让林赛具备：

1. **研究议程（Research Agenda）**：林赛有自己记录和维护的研究目标列表
2. **自主行动回路（Autonomous Loop）**：林赛能定期检查议程、执行预设研究任务、写回知识库
3. **结果汇报（Findings Reporting）**：林赛有重大发现时主动找用户

### 1.3 成功标准

| 维度 | 指标 | 目标值 |
|------|------|--------|
| 自主执行率 | agenda 到期任务中，林赛实际执行的比率 | ≥ 80% |
| 知识库增量 | 每周自动新增 wiki 页面 | 1–3 篇 |
| 用户控制感 | 用户可在任何时候暂停/删除 agenda | 100% 可控 |
| 成本稳定性 | 自动执行不触发日 $0.50 上限 | ≤ $0.20/次 |
| 知识库质量 | auto-grown wiki 通过质量评估率 | ≥ 70% |
| 林赛主动性 | 用户无需提示，林赛主动汇报 findings 的次数 | ≥ 1次/周 |

---

## 二、架构设计

### 2.1 高层架构

```
┌─────────────────────────────────────────────────────┐
│           LinSai-CoPilot 自主研究系统                    │
│                                                     │
│  ┌──────────────────┐   ┌───────────────────────┐  │
│  │  research_agenda │◄──│ proactive_engine       │  │
│  │  （研究议程）     │   │  heartbeat()          │  │
│  └────────┬─────────┘   │  (定期触发检查)        │  │
│           │              └───────────────────────┘  │
│           │                      ▲                 │
│           ▼                      │                 │
│  ┌──────────────────────────────┴───────────────┐  │
│  │          research_cycle.py                   │  │
│  │          （自主行动主循环）                  │  │
│  │                                           │  │
│  │  1. OBSERVE  → 检查到期 agenda             │  │
│  │  2. PLAN      → 制定执行计划               │  │
│  │  3. EXECUTE   → 执行研究任务               │  │
│  │  4. RECORD    → 写回知识库/记忆            │  │
│  │  5. ASSESS    → 评估是否需要通知用户         │  │
│  └──────────────────────┬──────────────────────┘  │
│                         │                          │
│          ┌──────────────┼──────────────────┐     │
│          ▼              ▼                       ▼     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │external_fetcher│ │learning_    │ │sandbox_      ││
│  │（搜索文献）   │ │engine（蒸馏）│ │executor（执行）││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│                         │                          │
│                         ▼                          │
│               ┌─────────────────┐               │
│               │  knowledge_base │               │
│               │  （知识库写入）   │               │
│               └─────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户授权开启自主研究
         │
         ▼
用户向 agenda 添加研究目标
  e.g. "跟踪固体HHG最新进展，每周一执行"
         │
         ▼
proactive_engine.heartbeat() 定期触发
         │
         ▼
research_cycle.main() 执行自主循环
  ① 检查 agenda 中到期的 goals
  ② 对每个 goal：
       a. external_fetcher.search()
       b. learning_engine.distill() × N
       c. knowledge_base.save()
       d. agenda.update_findings()
       e. 如果有重大发现 → notify_user()
         │
         ▼
结果写入 memory/research-agenda.json
       │
       ▼
用户收到林赛的消息："我这一周跟踪了固体HHG，有3篇值得注意..."
```

### 2.3 核心新增模块

| 模块 | 路径 | 职责 |
|------|------|------|
| `research_agenda.py` | `scripts/` | Agenda CRUD、操作日志、到期检测 |
| `research_cycle.py` | `scripts/` | 自主行动主循环（Observe-Plan-Execute-Record-Assess） |
| `sandbox_executor.py` | `scripts/` | 沙箱脚本执行（Phase 2） |
| `research-agenda.json` | `memory/` | 研究议程持久化存储 |
| `auto-grown/` | `knowledge/wiki/` | 自主产生的 wiki 页面存放 |

---

## 三、Phase 1 任务分解（WBS）

### 3.1 任务层级

```
Phase 1: 自主研究议程系统
│
├── 1.1 基础设施
│   ├── 1.1.1 新增 research_agenda.py 核心模块
│   │   ├── Agenda 数据结构定义
│   │   ├── _load_agenda() / _save_agenda()
│   │   ├── create_goal() — 创建研究目标
│   │   ├── list_goals() — 列出所有目标
│   │   ├── update_goal() — 更新目标状态
│   │   ├── delete_goal() — 删除目标
│   │   ├── get_due_goals() — 获取到期目标
│   │   └── _notify_user() — 通知用户
│   │
│   ├── 1.1.2 新增 memory/research-agenda.json
│   │   ├── 初始空模板
│   │   └── _ensure_agenda() — 首次使用时创建
│   │
│   └── 1.1.3 新增 memory/research-agenda-log.json
│       └── 操作日志（create/update/delete/cycle_run）
│
├── 1.2 自主行动循环
│   ├── 1.2.1 新增 research_cycle.py
│   │   ├── observe() — 检查到期目标
│   │   ├── plan() — 生成执行计划（调用 LLM）
│   │   ├── execute_goal() — 对单个 goal 执行完整研究
│   │   │   ├── external_fetcher.search()
│   │   │   ├── learning_engine.distill_*()
│   │   │   ├── knowledge_base.save()
│   │   │   └── check_cost_limit()
│   │   ├── record_findings() — 写入 agenda.findings
│   │   ├── assess_significance() — 判断是否重大发现
│   │   ├── main() — OODA 主循环
│   │   └── _safe_run() — 异常捕获 + 优雅降级
│   │
│   └── 1.2.2 研究任务模板系统
│       ├── TASK_TEMPLATES — 预设研究任务模板
│       │   ├── "literature_review" — 文献调研模板
│       │   ├── "concept_deep_dive" — 概念深挖模板
│       │   └── "trend_analysis" — 趋势分析模板
│       └── 用户自定义 goal
│
├── 1.3 主动通知集成
│   ├── 1.3.1 通知触发条件
│   │   ├── 重大发现（sig_score ≥ 0.7）
│   │   ├── 任务执行失败（记录 + 通知）
│   │   └── 每周汇总（可选）
│   │
│   ├── 1.3.2 通知格式
│   │   └── 研究发现格式模板（见 3.3）
│   │
│   └── 1.3.3 通知路由（Q1-B 已确认）
│       ├── 主路径：写入活跃会话作为林赛的新消息（copilot_engine.inject_message）
│       └── Fallback：无活跃会话时跳过本次通知（不写入文件，不打扰用户）
│
├── 1.4 与现有系统集成
│   ├── 1.4.1 proactive_engine 集成
│   │   └── heartbeat() 新增 research_cycle 触发
│   │
│   ├── 1.4.2 learning_engine 集成
│   │   └── 确保 auto-grown wiki 含 `auto_grown: true`
│   │
│   ├── 1.4.3 knowledge_base 集成
│   │   ├── auto-grown wiki 写入 knowledge/wiki/papers/ 和 concepts/
│   │   └── 知识图谱边自动扩展
│   │
│   └── 1.4.4 memory_manager 集成
│       └── agenda findings 同步到 long-term-memory.json
│
├── 1.5 安全与控制机制
│   ├── 1.5.1 用户授权开关
│   │   └── memory/learning-config.json 新增字段
│   │       { "auto_research_enabled": false }
│   │
│   ├── 1.5.2 执行频率限制
│   │   ├── 单个 goal 最小执行间隔：24h
│   │   ├── 单日最大执行次数：2 次
│   │   └── 冷却期：cooldown = max(24h, 目标周期/4)
│   │
│   ├── 1.5.3 预算安全
│   │   └── 自主执行视为普通 LLM 调用，受 learning_config.json 成本上限约束
│   │
│   └── 1.5.4 行动边界
│       └── 明确禁止：修改 sessions/、memory/ 用户数据、执行未经用户授权的操作
│
└── 1.6 测试与验收
    ├── 1.6.1 单元测试
    ├── 1.6.2 集成测试（mock agenda + 假数据）
    ├── 1.6.3 手动端到端测试（用真实 agenda）
    └── 1.6.4 成本与性能基准测试
```

### 3.2 Agenda 数据结构

```json
// memory/research-agenda.json
{
  "meta": {
    "version": "1.0",
    "created": "2026-05-14T00:00:00Z",
    "last_updated": "2026-05-14T00:00:00Z"
  },
  "settings": {
    "auto_research_enabled": false,   // 用户必须主动开启
    "notifications_enabled": true,
    "max_goals": 10,
    "max_cycles_per_day": 2
  },
  "goals": [
    {
      "id": "goal_001",
      "title": "跟踪固体HHG最新进展",
      "description": "每周一执行一次，搜索arXiv固体HHG相关论文，蒸馏前3篇",
      "strategy": "literature_review",
      "params": {
        "query": "solid state high harmonic generation",
        "max_results": 3,
        "sources": ["arxiv"]
      },
      "schedule": {
        "interval_hours": 168,    // 每周
        "next_due": "2026-05-20T00:00:00Z",
        "last_run": null,
        "last_result": null
      },
      "status": "active",
      "findings": [],
      "created_by": "user",
      "created_at": "2026-05-14T00:00:00Z"
    }
  ],
  "findings_history": [],
  "cycle_log": []
}
```

### 3.3 研究发现通知格式

```markdown
## 🔬 林赛的研究发现 | {goal_title}

**时间**: {timestamp}  
**来源**: {sources}

### 概要
{3句话内的核心发现}

### 值得关注的 {N} 篇

| # | 标题 | arXiv ID | 关键发现 |
|---|------|----------|----------|
| 1 | ... | 2605.xxxxx | ... |

### 林赛的判断
{persona风格：林赛认为这些发现意味着什么，对你的研究有什么关联}

### 开放问题
- {林赛提出的新问题}

---
*由 LinSai 自主执行 · [查看完整笔记 →](wiki/papers/xxx.md)*  
*如需调整研究方向或暂停此任务，告诉我。*
```

---

## 四、验收标准体系

### 4.1 验收检查表（Acceptance Checklist）

#### P0 必须通过（阻断发布）

| # | 检查项 | 验证方法 | 通过标准 |
|---|--------|----------|----------|
| P0-1 | `research_agenda.py` 无语法错误 | `python3 -m py_compile` | 编译通过 |
| P0-2 | `research_cycle.py` 无语法错误 | `python3 -m py_compile` | 编译通过 |
| P0-3 | `self_test.py` 全量 88/88 仍通过 | `python3 scripts/self_test.py` | 88/88 通过 |
| P0-4 | `research_cycle` 不读写 `sessions/`、`memory/` 以外的路径 | 代码路径审查 | 零违规读写 |
| P0-5 | `auto_research_enabled: false` 默认关闭 | 代码审查 + 手动测试 | 用户不主动开启则不执行 |
| P0-6 | 成本超限自动暂停 | 模拟触发 `$0.50` 限额 | 日限额达到后循环停止 |
| P0-7 | 异常不泄漏到用户 | `try/except` 包裹所有 `cycle` 调用 | 主循环异常 → 静默记录 + 用户友好提示 |
| P0-8 | 端到端链路跑通（mock） | 用 mock 数据执行一次 `main()` | 创建至少 1 篇 wiki，无报错 |

#### P1 质量门禁（发布质量）

| # | 检查项 | 验证方法 | 通过标准 |
|---|--------|----------|----------|
| P1-1 | wiki 页面格式正确 | 读取保存的文件 | YAML frontmatter 完整，`## 来源` 存在 |
| P1-2 | `agenda.findings` 正确追加 | 执行后读取 JSON | findings 条目 +1 |
| P1-3 | 通知格式符合模板 | 检查通知内容 | 含林赛 persona、具体发现、无幻觉 |
| P1-4 | 自主执行后 agenda `last_run` 更新 | 检查 JSON | timestamp 为 ISO 格式 |
| P1-5 | cost 计入 `learning-cost.json` | 检查成本文件 | 自主执行产生成本被追踪 |
| P1-6 | 用户可随时 `delete_goal` | CLI 删除 + 检查 JSON | 目标被移除，无残留 |
| P1-7 | 重复执行不产生重复 wiki | 两次执行相同 goal | second 执行跳过已存在页面 |
| P1-8 | 文档齐全 | `docs/` 目录检查 | README + API 参考存在 |

#### P2 体验优化（非阻断）

| # | 检查项 | 验证方法 | 通过标准 |
|---|--------|----------|----------|
| P2-1 | 首次执行时间 < 60s | `time.time()` 计时 | ≤ 60s（含 1 次 LLM 调用）|
| P2-2 | 日志可追溯 | 检查 `research-agenda-log.json` | 每次操作有 timestamp + goal_id + action |
| P2-3 | 进度可见 | 检查通知内容 | 用户能看懂林赛在做什么 |
| P2-4 | `learning_quality_tracker` 可评估自主 wiki | 执行 tracker | 评分 < 0.6 的 wiki 标记 warnings |

### 4.2 回归测试套件

```python
# tests/test_research_agenda.py
class TestResearchAgenda:
    def test_goal_crud(self): ...
    def test_due_goals_filter(self): ...
    def test_safe_path_enforcement(self): ...
    def test_cost_limit_integration(self): ...

class TestResearchCycle:
    def test_cycle_runs_without_user_trigger(self): ...   # Mock heartbeat
    def test_creates_wiki_with_source(self): ...
    def test_findsings_appended(self): ...
    def test_notification_triggered_on_significant(self): ...
    def test_graceful_degradation_on_llm_failure(self): ...
    def test_no_sessions_or_memory_access(self): ...
    def test_deduplication(self): ...
```

---

## 五、风险管理

### 5.1 风险登记册（Risk Register）

| ID | 风险描述 | 可能性 | 影响 | 风险值 | 应对策略 | 缓解后 |
|----|----------|--------|------|--------|----------|--------|
| R-01 | LLM API 超时导致循环中断，异常写入错误 findings | 高 | 中 | 🟡 中 | try/except 包裹每个 LLM 调用；失败写日志不通知用户 | 🟢 低 |
| R-02 | 自主执行产生大量低质量 wiki，污染知识库 | 中 | 高 | 🟡 中 | quality_evaluator 默认 pending，用户手动审批 | 🟢 低 |
| R-03 | 成本超限（用户忘记 agenda 在跑）| 中 | 低 | 🟢 低 | learning_config 已有日$0.50 上限 | 🟢 低 |
| R-04 | 路径穿越漏洞导致读写禁止目录 | 低 | 极高 | 🟡 中 | research_cycle 使用白名单 TRUSTED_PATHS；sandbox_executor 额外沙箱 | 🟢 低 |
| R-05 | 用户开启后林赛频繁打扰 | 中 | 低 | 🟢 低 | 通知阈值 sig_score ≥ 0.7；可配置通知频率 | 🟢 低 |
| R-06 | agenda 数据损坏导致循环异常 | 低 | 中 | 🟢 低 | `_save_agenda` 前先写 `.tmp`，rename 原子化 | 🟢 低 |
| R-07 | deepxiv API 不可用，循环静默失败 | 高 | 低 | 🟢 低 | 自动降级到 DuckDuckGo；API 失败记录日志不中断 | 🟢 低 |
| R-08 | 用户忘记 agenda 在跑，误以为林赛"有意识" | 中 | 中 | 🟡 中 | UI 明确标注"自动执行"标记；prompt 不伪装成人工 | 🟡 中 |

### 5.2 安全设计原则

```
原则 1：最小权限
  research_cycle 只读写 knowledge/、experiments/、analysis/
  绝对不读写 sessions/（用户隐私）、memory/用户数据

原则 2：用户主权
  auto_research_enabled = false 是硬编码默认值
  用户必须主动开启；任何时候可暂停

原则 3：透明可溯
  所有自主行动写入 research-agenda-log.json
  用户可查阅林赛"背着自己"做了什么

原则 4：优雅降级
  任何单点失败不导致循环崩溃
  失败 → 静默记录 → 继续下一个 goal
```

---

## 六、版本管理方案

### 6.1 发布节奏

```
实验阶段（用户测试期）
  Phase 1.0  → 内部测试，用户观察，不公开
  Phase 1.1  → 根据反馈修复，默认关闭
  Phase 1.2  → 公开默认关闭，用户可选开启

正式发布
  v2.1.0     → Phase 1 正式功能，learning_config 默认 auto_research=false
  v2.2.0     → Phase 2 沙箱执行器（需要额外安全审查）

版本兼容性
  memory/research-agenda.json 格式通过 version 字段管理
  模块升级时读取旧版本数据，自动迁移
```

### 6.2 配置管理

```json
// memory/learning-config.json 新增字段
{
  "auto_research_enabled": false,
  "auto_research": {
    "notifications_enabled": true,
    "notification_threshold": 0.7,
    "max_goals": 10,
    "max_cycles_per_day": 2,
    "preferred_schedule_hours": [9, 21],
    "strategies": {
      "literature_review": { "max_results": 3, "sources": ["arxiv"] },
      "concept_deep_dive": { "depth": "standard" },
      "trend_analysis": { "min_papers": 5 }
    }
  }
}
```

### 6.3 数据迁移策略

```
当 research-agenda.json 的 version 字段 < 当前版本：
  1. 备份当前文件到 .backup/
  2. 运行 _migrate_vX_to_vY()
  3. 验证迁移后文件可读
  4. 删除备份
```

---

## 七、优化迭代路线图

### 7.1 版本路线图

```
v2.1.0 [Phase 1 完成]
  林赛 = 有记忆的研究实习生（Agenda 驱动）
  - 用户定义研究目标 → 林赛定期执行 → 写回知识库 → 有重大发现通知
  - 自测覆盖率 ≥ 90%
  - 知识库质量：auto_grown wiki ≥ 70% 通过 quality_evaluator

v2.2.0 [Phase 2 完成]
  林赛 = 能跑脚本的初级研究员
  - + sandbox_executor（受信任路径）
  - + 实验数据分析（CSV/JSON → 图表）
  - 林赛能主动读实验数据 → 分析 → 报告异常

v2.3.0 [Phase 3 探索]
  林赛 = 主动探索者（受限）
  - 林赛自主设定调查问题（需 LLM Function Calling）
  - 限制：只在自己管理的数据范围内探索
  - 重大限制：无法主动发邮件、操作 APP

v4.0.0 [未来愿景]
  林赛 = 真正的 AI 合作者
  - 长期目标：与林赛共同管理一个研究项目
  - 需要：更复杂的记忆系统、主动对话能力、外部世界接口
```

### 7.2 迭代改进机制

```
每完成一个 cycle 后自动记录：
  - 执行时间、总耗时
  - 发现的论文数、新增 wiki 数
  - 质量评分
  - 异常记录

用户反馈闭环：
  用户在 agenda UI 点击 👍/👎 → 记录到 findings_history
  👍 → 下次类似 goal 增加 max_results
  👎 → 下次降低执行频率或建议用户修改 goal

每月自动报告（可配置）：
  "林赛这个月跟踪了 N 个方向，
   产生了 M 篇笔记，其中你觉得哪些有用？"
```

---

## 八、技术债务清单

| 债务项 | 现状 | 清理方案 | 优先级 |
|--------|------|----------|--------|
| agenda 数据无原子写入 | 直接覆写 | `_save_agenda()` 改用 rename 策略 | P0 |
| deepxiv wsearch 常返回空 | 无降级通知 | 增加降级日志，用户可选 DuckDuckGo fallback | P1 |
| knowledge_base 索引手动重建 | 需手动触发 | `research_cycle` 执行后自动 `kb_maintenance --reindex` | P2 |
| 自主 wiki 与手动 wiki 混放 | 同目录 | ✅ 已确认：Phase 1 纳入 `knowledge/auto-grown/` 子目录（Q4-C） | P0 |
| learning_cost.json 无 cycle 维度 | 只追踪 API 调用 | 新增 `cycle_id` 标签 | P2 |

---

## 九、执行计划

### 9.1 时间估算（单人开发）

| 任务 | 预计工时 | 实际可并行 |
|------|---------|-----------|
| 1.1 research_agenda.py | 6h | — |
| 1.2 research_cycle.py | 12h | 1.1 完成后 |
| 1.3 通知集成 | 4h | 1.2 完成后 |
| 1.4 现有系统集成 | 6h | 1.1 完成后 |
| 1.5 安全机制 | 4h | 1.2 完成后 |
| 1.6 测试套件 | 6h | 1.1/1.2 完成后 |
| 自测 + 手动验证 | 4h | 全部完成后 |
| **合计** | **~42h（1–2周）** | |

### 9.2 关键路径（不可并行）

```
research_agenda.py（1.1）
       │
       ▼
research_cycle.py（1.2）← 核心依赖 1.1
       │
       ▼
现有系统集成（1.4）← 依赖 1.2
       │
       ▼
安全机制验证（1.5）← 依赖 1.4
       │
       ▼
端到端测试（1.6） ← 依赖 1.5
```

### 9.3 验收流程

```
开发者自测（1.6 全量通过）
       │
       ▼
你（用户）手动验证
  - 开启 agenda
  - 添加 1 个 goal
  - 等待/手动触发 cycle
  - 检查 wiki 生成
  - 检查通知格式
       │
       ▼
你决定是否合并到 main
  - 通过 → tag v2.1.0
  - 不通过 → 回退，开发组修复
```

---

## 十、已确认决策

| # | 问题 | 决策 | 说明 |
|---|------|------|------|
| Q1 | Phase 1 的通知方式 | **B** | 林赛主动在活跃会话中发消息 |
| Q2 | 初始 agenda 定义方式 | **C** | 林赛先建议 3 个方向，用户补充修改 |
| Q3 | Phase 2 是否纳入 | **B** | Phase 1 验证通过后再评估 |
| Q4 | auto wiki 命名规范 | **C** | `knowledge/auto-grown/` 子目录隔离 |
| Q5 | 通知频率上限 | **C** | 无硬上限，sig_score 质量门禁自然过滤 |

---

## 十一、完整更新路线图

> 本节记录 v2.1.0 之后所有已规划但尚未实现的阶段，供 Phase 1 完成后继续讨论，避免信息丢失。

### 11.1 完整版本树

```
v2.0.0  (当前)
│
├─ v2.1.0 [Phase 1]  ★ 正在实现
│    研究议程驱动：research_agenda + research_cycle + 通知
│    目标：林赛 = 有记忆的研究实习生
│
├─ v2.2.0 [Phase 2]  ☆ 待 Phase 1 验证后启动
│    沙箱执行器：sandbox_executor + 数据分析
│    目标：林赛 = 能跑脚本的初级研究员
│
├─ v2.3.0 [Phase 3]  ☆ 概念规划中
│    主动探索者（受限）：LLM Function Calling 自主设定调查问题
│    目标：林赛 = 主动探索者（受限）
│
└─ v3.0.0 [未来愿景]  ○ 远期目标
     与林赛共同管理一个研究项目
```

---

### 11.2 Phase 2 — 沙箱执行器（v2.2.0）

> **前置条件**：v2.1.0 验收通过后再启动

#### 核心能力
- 林赛能执行放置在特定目录的脚本（`data/` 或 `sandbox/`）
- 支持 CSV/JSON 数据分析 → 图表 → 写入知识库
- 林赛发现数据异常时主动汇报

#### 待确认事项（Phase 2 启动前回答）

| # | 问题 | 选项 |
|---|------|------|
| **P2-Q1** | 执行目录限制 | (A) 只允许 `data/` 子目录 / (B) 用户可配置白名单路径 / (C) 禁止执行，只读分析 |
| **P2-Q2** | 脚本类型限制 | (A) 仅 Python / (B) Python + shell / (C) Python + shell + R |
| **P2-Q3** | 执行结果展示 | (A) 文字摘要写入 wiki / (B) 生成图表图片存入 `data/figures/` / (C) 同时文字+图表 |
| **P2-Q4** | 执行触发方式 | (A) agenda 中预设"分析 X 数据"任务 / (B) 林赛判断数据变化后自动执行 / (C) 两者都有 |
| **P2-Q5** | 网络访问 | (A) 禁止网络请求 / (B) 允许 GET 请求 / (C) 无限制 |

---

### 11.3 Phase 3 — 主动探索者（v2.3.0）

> **前置条件**：v2.2.0 稳定运行 2 周后启动

#### 核心能力
- 林赛不再等待 agenda 到期，主动识别"知识空白"
- 用 LLM Function Calling 生成新的调查问题
- 只能在林赛管理的数据范围内探索（sessions/ memory/ knowledge/）

#### Phase 3 已知约束
- **不涉及**：主动发邮件、操作 APP、修改外部系统
- **不涉及**：读取不在白名单目录下的用户文件
- **需要**：Function Calling 支持（Claude CLI / Kimi CLI）

#### 待确认事项（Phase 3 启动前回答）

| # | 问题 | 选项 |
|---|------|------|
| **P3-Q1** | "知识空白"识别方式 | (A) 林赛根据 wiki 的开放问题反向推断 / (B) 用户在 wiki 页面点击"❓请求林赛调查" / (C) 两者都有 |
| **P3-Q2** | 探索范围边界 | (A) 仅限 `knowledge/` 目录 / (B) `knowledge/` + `memory/` / (C) 全部项目文件 |
| **P3-Q3** | 探索频率 | (A) 每 heartbeat 最多 1 次探索 / (B) 每 heartbeat 最多 3 次 / (C) 无限制 |
| **P3-Q4** | 探索结果处理 | (A) 必须写入 `knowledge/auto-grown/`，需 sig_score ≥ 0.7 才通知 / (B) sig_score ≥ 0.5 即通知 / (C) 探索结果静默，仅在用户主动询问时展示 |

---

### 11.4 v3.0.0 — 长期愿景

> 远期目标，不设具体时间表

#### 目标定义
- 与林赛共同管理一个研究项目
- 林赛能主动提出研究计划草稿
- 林赛能识别用户长期目标并为之储备知识

#### 预计需要的能力
- 更复杂的记忆系统（跨会话目标追踪）
- 主动发起对话的能力
- 外部世界接口（邮件/日历/文献管理器）

---

### 11.5 文档维护约定

- Phase N 启动前，必须先回答该阶段的"待确认事项"
- 答案记录在本文件对应章节，替代 Q 表格
- 不完整回答的章节标记 `☆ 待讨论`，不影响已完整的章节执行

---

*本计划版本：v2.0*
*创建日期：2026-05-14*
*最后更新：2026-05-15（Q1-Q5 已确认，v3.0.0→v2.x 重编号，完整路线图加入）*
*下次审查：Phase 1 实现开始前*
