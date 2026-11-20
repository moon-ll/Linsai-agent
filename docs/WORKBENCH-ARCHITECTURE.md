# v8 工作台架构：课题启动包生产链

> 本文件是 v8.0.0 架构迁移的设计文档与验收纲领（用户裁决 2026-11-16）。
> 本轮更新目标：全流程自动化的产出从「完整项目书 + 多轮优化」改为「课题启动包（proposal）」，
> 协作引擎简化为研究工作台。
> 最后更新：2026-11-16（v8.0.0）

---

## 1. 背景与用户裁决

### 1.1 v7 框架的三个结构性问题（用户裁决 2026-11-16）

1. **内容庞杂难优化**：直接生成完整项目书（申请书五模块 + 方法手册 + 评审记录），自动化多轮
   优化难以收敛，质量瓶颈长期存在（rigor 维度连续 71% 占最弱）。
2. **token 消耗过大**：多轮章节撰写/评审/一致性修订/评审团/对抗奖惩的机时成本高
   （实测单课题一轮数十万 token 级），投入产出比低。
3. **上下文限制下的整合短板**：自动化不擅长处理多方信息、跨时间尺度的整合——这正是
   完整项目书最需要的，恰恰应该由人来主导。

### 1.2 v8 核心定位（用户裁决）

> 发挥自动化的优势，将全自动化产出的目标定位为 proposal（课题启动包）：
> 全自动化通过**文献阅读**发掘有价值的科学问题，利用**深度研究**探索研究方案，
> 最后将相关参考文献和课题报告整合到一起，形成一份类似**课题启动包**的交付物。

对课题报告的要求：
- **背景调研充分**
- **问题定位清晰**
- **方案分解明确**——为课题正式研究提供可以具体推进的方法和路线
- **聚焦一个具体问题**（课题报告区分于项目书）；不同课题报告之间可以形成关联

### 1.3 协作引擎 → 研究工作台

| 维度 | v7 协作引擎 | v8 研究工作台 |
|------|------------|--------------|
| 自动化产出 | 完整项目书（五模块申请书） | 课题启动包（课题报告 + 参考文献 + 素材包） |
| 优化模式 | 多轮迭代（章节评审/一致性/评审团/对抗奖惩） | **单遍深度研究**，一步到位，不做多轮自主优化 |
| 人的角色 | 法定节点审核（立项/验收/策略） | **驾驶员**：选题、启动、推进、整合（跨课题/跨时间的整合由人主导） |
| 林赛角色 | 主动感知的虚拟合作者 | 工作台协作助手（响应式 1v1 协作 + 文献/调研引擎） |
| 自动化边界 | 全流程（写作→评审→晋级→归档） | 文献链 + 单课题深研 + 启动包组装，到 ready 为止 |

---

## 2. v8 工作流程

```
【A 文献链】（保留 v7 全部设施，自动化优势所在）
  简报 4次/天 → Gate 评分 → 深读 → 蒸馏 → 聚类 → topic_match
      ↓ 周末输入链（compose new 动作）
      ↓
  questions/ 问题收件箱（课题候选：知识卡 + 来源簇 + 方向校准）

【B 深研链】（v8 新核心，替代 v7 多轮优化环）
  每个工作日对队首问题执行单遍深度研究（配额默认 1 课题/天）：
    B1 背景调研（researcher profile）：领域地图 + 核心文献组 + KB 关联页 → 01_background/
    B2 问题定位（analyst profile）：单一具体问题陈述 + 新颖性对照 + 可检验判据 → 02_problem/
    B3 方案分解（writer profile）：可执行步骤分解 + 首月路线 → 03_scheme/
    B4 启动包集成（机械组装，零 LLM）：references 核验 + 素材包挂载 → topic-report.md

【C 验收自检】（零 LLM 结构自检；A2 新颖性用确定性相似度算法）
  A1-A4 + G1-G2 六项判据 → 通过 → ready/

──── 以下由人主导 ────

【人工节点 1：立项启动】用户审阅启动包 → 一键启动 → active/
  （正式研究开始：进 task_manager 追踪，1v1 会话协作推进）

【人工节点 2：收尾归档】研究完成/搁置 → archive/（关键知识萃取回知识库）
```

### 2.1 阶段定义

| 阶段 | 目录 | 含义 | 进入方式 |
|------|------|------|---------|
| `questions` | `research_topics/questions/` | 问题候选，等待深研 | 周末输入链 new 动作 / 人工 `--register` |
| `kickoff` | `research_topics/kickoff/` | 深研进行中 | `--deep-dive`（B1→B4 顺序执行） |
| `ready` | `research_topics/ready/` | 启动包完成，待人工启动 | 自检通过自动晋级 |
| `active` | `research_topics/active/` | 人工已启动，正式研究中 | 用户一键启动 / `--activate` |
| `archive` | `research_topics/archive/` | 收尾归档 | 用户 `--archive` |
| （否决） | `research_topics/_rejected-questions/` | 被否决的问题候选台账 | 用户 `--reject` |

关键纪律：
- **深研环没有"轮次"**：每个课题一次单遍深研，不做多轮迭代优化；自检不过则把缺口清单
  留在 `kickoff-check.json`，由下一次深研补齐（每个缺口只补一次，补两次仍不过即挂起等人裁决）。
- **A2 新颖性对照是硬门**：与既有课题（全阶段）确定性相似度 ≥0.50 的问题不进 kickoff。
- **人不批准不启动**：ready → active 只能由用户触发（工作台按钮 / CLI / 会话指令）。

---

## 3. 数据域：`research_topics/`

```
research_topics/
├── _topics.json                  ← 状态总线（轻量：id/title/stage/来源/时间戳/关联）
├── questions/                    ← 问题候选
│   └── {topic_id}/
│       └── topic-card.md         ← 课题卡：一句话问题 + 来源簇 + 知识卡 + 状态
├── kickoff/                      ← 深研中
│   └── {topic_id}/
│       ├── topic-card.md
│       ├── 01_background/        ← B1 产物：领域地图 literature-map.md + 阅读笔记
│       ├── 02_problem/           ← B2 产物：problem.md（问题陈述/判据/三标记）
│       ├── 03_scheme/            ← B3 产物：scheme.md（步骤分解/里程碑/首月路线）
│       │   └── kb-methods-pack.md ← 方法素材包（复用 kb_methods_pack）
│       ├── 04_references/        ← B4 产物：references.bib + 核验记录 sources.json
│       ├── topic-report.md       ← 课题报告（整合产出，正文 ≤ 8000 字）
│       └── kickoff-check.json    ← 验收自检结果（六项判据逐项证据）
├── ready/  active/  archive/     ← 同结构，阶段不同
└── _rejected-questions/          ← 否决台账
```

- `topic_id` 命名沿用 v7 习惯：`{scope}-{slug}-{YYYYMMDD}`。
- `_topics.json` 只存轻量元数据，正文一律落文件（与 v7 的 `_lifecycle.json` 60 字段
  状态机相反——v8 的状态由目录位置 + 卡片头域承载）。
- **课题关联**：topic-card 头域 `related: [...]` + 报告内 `[[wikilink]]`；同主题课题
  通过 knowledge_base 图谱与 topic_match 相似度建立关联。

### 3.1 课题报告模板（topic-report.md）

```markdown
# {课题名}

> 课题 ID / 状态 / 来源 / 创建与更新时间 / 关联课题（related 列表）

## 一、问题一句话陈述
（单一具体问题，A2 的核心）

## 二、背景调研摘要
（领域现状 → 已有工作 → 空白点；每段带文献锚点 [ref:N] / [[KB 页]]）

## 三、问题定位
（为什么是这个问题、与既有工作的新颖性对照、可检验判据 [V]/[P]/[D] 标记）

## 四、方案分解
（步骤 S1..Sn：方法 / 输入 / 输出 / 判据 / 预计工作量；里程碑 M1..Mk；首月路线）

## 五、风险与备选路线
（每个关键步骤一条 fallback）

## 六、参考文献
（[ref:N] 对照 04_references/references.bib，全部可溯源）
```

---

## 4. 课题启动包验收标准（v8 质量门）

四条硬标准 + 两条全局约束。自检脚本 `topic_pipeline.py --check <id>` 零 LLM 逐项取证，
结果落 `kickoff-check.json`；全过 → 自动晋级 ready。

| 编号 | 标准 | 判据（零 LLM 可查证部分） |
|------|------|--------------------------|
| **A1** | 背景调研充分 | `01_background/` 文献笔记/知识卡 ≥ 8 篇；其中近 24 个月 ≥ 3 篇；KB 页 wikilink ≥ 3 |
| **A2** | 问题定位清晰 | `02_problem/problem.md` 存在且含「问题一句话陈述」节；新颖性对照节非空；相似度 < 0.50（2-gram Jaccard 确定性算法，对全阶段既有课题） |
| **A3** | 方案分解明确 | `03_scheme/scheme.md` 含 ≥ 3 个步骤节（S1..Sn）；每步含「判据」字样；含「首月路线」节；`kb-methods-pack.md` 存在 |
| **A4** | 参考文献真实 | `04_references/references.bib` 非空；每条 bib 条目含 `source:` 溯源行（KB 页/raw 论文/检索池三源之一）；报告内 [ref:N] 与 bib 键一一对得上 |
| **G1** | 篇幅约束 | topic-report.md 正文 ≤ 8000 字（课题报告 ≠ 项目书，防庞杂） |
| **G2** | 关联明确 | topic-card 头域 related 字段存在（空列表须显式声明无关联）；报告内 [[wikilink]] ≥ 5 |

补齐机制：自检不过 → 缺口清单写回卡片 → 下次深研会话定向补齐；同一缺口补 2 次仍不过
→ 状态挂 `needs_human`，进工作台待办（等人裁决，不自动重试）。

---

## 5. v7 → v8 迁移方案（任务 2）

原则：**复制不删除**（产出即资产）。`research_proposals/` 整体保留并标注 legacy，
新域 `research_topics/` 为唯一活跃数据域。

| v7 存量 | 处理 | 优先级 |
|---------|------|--------|
| drafts（空） | 无需迁移 | - |
| optimizing（15） | `--migrate-v7` 逐个转 kickoff：00_research_idea→02_problem、02_literature+02_topic→01_background、04_proposal/sections/scheme + 03_method/method-manual→03_scheme、sections/references→04_references、三章节内容机械拼装为 topic-report（带出处标注，零 LLM） | P0 |
| pending_review（1） | 同上，且材料最全 → 迁后直接进 ready（仍需用户启动） | P0 |
| archived（5） | 转 archive（报告从已归档章节蒸馏，标注"源自 v7 项目书"） | P1 |
| rejected_ideas 台账 | 迁入 `_rejected-questions/`（保留否决理由，防重复立项） | P1 |
| `_lifecycle.json` 等 | 原位保留（legacy 审计线索），不再读写 | - |

迁移产物在 topic-card 标注 `migrated_from: research_proposals/{id}`；
自检照常运行，v7 材料不满足 A1-A4 的（如文献笔记 <8 篇）如实标缺口，
由深研补齐流程消化，不降低验收标准。

---

## 6. cron v8 清单（对账基准）

### 6.1 保留（文献/KB/备份链，25 个 —— 自动化优势所在）

简报×6（检索入池+知识库简报 00/06/12/18:23 / 候选判定 08:28 / 经典文献 14:23 / 高分深读 16:23 /
健康检查 23:30 / 每日汇总 20:00）、lc-kb-sync、lc-kb-distill、
lc-kb-distill-pm、lc-kb-distill-night（paused）、lc-kb-distill-sunday（paused）、
lc-weekend-input×10（input + n1-4 + r2-6，发现链核心）、lc-zcode-worker（方法卡回补
2026-11-19 收官清零，空转待裁决）、lc-daily-backup。

### 6.2 移除（v7 优化环，14 个 —— 2026-11-16 已执行，审计 `memory/v8-cron-teardown.json`）

lc-daily-orchestrate、lc-repair、lc-panel-review、lc-prompt-optimize、lc-self-optimize、
lc-retrospective、lc-micro-scheduler、lc-side-worker、lc-hourly-monitor、lc-daily-sync、
lc-weekend-weekend-output、lc-weekend-weekend-reflection、lc-weekend-summary、lc-weekend-worker。

### 6.3 新增（v8 深研链）

| job | schedule | 入口 |
|-----|----------|------|
| lc-topic-daily | 30 9 * * 1-5 | `topic_pipeline.py --daily`（取队首 question 深研→集成→自检→晋级；配额 1 课题/天，`memory/config/workbench.json` 可调） |
| lc-workbench-monitor | 0 */6 * * * | `workbench_monitor.py`（cron 对账 + topics 健康 + KB 告警复用 health_sensor） |

---

## 7. 代码处置清单（任务 3）

处置方式：**归档不删除**——v7-only 机制移入 `scripts/archive/v7-optimization/`（可还原），
配套测试移入 `scripts/tests/archive/`（self_test 只发现顶层 `test_*.py`，归档即退出回归）。

### 7.1 归档（v7 优化环专属）

- 优化环编排：`lifecycle_monitor.py`、`lifecycle_cron_framework.py`、`lifecycle/` 包中
  micro_scheduler/side_worker/executor 的 worker 路径、`proposal_lifecycle/` 包（多轮优化/晋级/评审团对接）、
  `panel_review.py`、`adversarial_governance.py` + `adversarial/`、`review_dossier.py`、
  `rotation_queue.py`、`round_machine_time.py`、`pilot_scorecard.py`、`restart_stalled_failed_job.py`、
  `rebuild_lifecycle.py`、`promote_proposal_to_focus.py`、`backfill_score_raw.py`、`backfill_manual_rereview.py`
- 自成长元环：`prompt_optimizer.py`、`apply_prompt_upgrades.py`、`self_optimizer.py`、
  `retrospective.py`、`stage_weekly_report.py`、`strategy_optimizer.py`、`failure_analyzer.py`、
  `profile_health.py`、`orchestrator.py`（总控层）
- 周末输出端（v7 归档萃取）：`weekend_orchestrator.py --output/--reflection` 路径、
  `weekend_summary.py`（输入端保留）
- 旧写作/管线：`proposal_writer.py`、`proposal_sections.py`、`proposal_structure_guard.py`、
  `proposal_inspector.py`、`proposal_kb_sync.py`、`methodology_manual.py`、`hermes_pipeline.py`、
  `pipeline_orchestrator.py`、`gap_analyzer.py`、`question_architect.py`、`idea_generator.py`、
  `import_hermes_topics.py`、`paper_pool.py`、`cleanup_cron_duplicates.py`
- 未启用层：`project_*.py`（v3.5 课题管理）、`agent_team.py`、`agora_bridge.py`、
  `proactive_engine.py`、`unit_manager.py`、`fix_input_chain_data.py`、`wiki_regenerator/`

### 7.2 保留并接入 v8

- 文献/KB 全链：`deep_read_pipeline.py`、`literature_service.py`、`literature_screener.py`、
  `literature_notes.py`、`external_fetcher.py`、`kb_*.py`、`knowledge_base.py`、`knowledge_output.py`、
  `growth_engine.py`、`learning_engine.py`、`housekeeping.py`、`weekend_pipeline/`（输入端）
- 工作台基础：`copilot_engine.py`（重定位为工作台助手）、`web_server.py` + 路由、
  `session_manager.py`、`memory_manager.py`、`task_manager.py`、`skill_loader.py`、`skill_manager.py`、
  `llm_router.py`/`llm_gateway.py`、`hermes_bridge.py`、`step_usage.py`、`backup_manager.py`、
  `sync_engine.py`（重定向到 topics 域）、`state_sync.py`（适配）
- skill 层 5 个 SKILL.md：research-proposal / literature-reading / method-manual 继续服务深研链；
  nsfc-writing / quality-review 标注 legacy（仅供人工项目书场景）

### 7.3 Web 端

- 新增「课题工作台」页（questions/kickoff/ready/active 看板 + 启动包详情 + 启动/否决按钮）
- 旧生命周期/优化环页面保留只读入口（legacy），不再提供触发按钮
- 定位文案改写：林赛协作引擎 → 林赛研究工作台

---

## 8. 本轮更新的验收标准（对用户五项任务的完成定义）

1. **任务 0**：本设计文档存在且被 AGENTS.md 引用。
2. **任务 1**：`topic_pipeline.py` 六个子命令（register/deep-dive/assemble/check/activate/reject）
   + `--daily` 可运行；单测覆盖注册/组装/自检/晋级/否决路径。
3. **任务 2**：21 个 v7 存量课题全部迁入 research_topics/ 并通过迁移核对（原内容零丢失，
   迁移报告落 `memory/v8-migration-report.json`）。
4. **任务 3**：v7-only 脚本/测试归档完成，cron 拓扑与 §6.3 清单一致，监控对账通过。
5. **任务 4**：AGENTS.md / README / docs/ARCHITECTURE.md / docs/PROJECT-STRUCTURE.md / VERSION /
   CHANGELOG 全部反映 v8；`self_test --module` 通过（归档模块的旧测试同步移出）。
6. **任务 5**：README 与 Web 定位改为「林赛研究工作台」；工作台页上线；
   copilot_engine docstring/入口重定位；主动自动化仅剩文献链 + 每日深研 worker。
