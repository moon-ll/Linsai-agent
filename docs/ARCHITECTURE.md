# 架构说明（v8.0.0）

> 本文件是 v8「研究工作台」架构的权威说明。v8 设计纲领、工作流程推导与验收标准
> 见 `docs/WORKBENCH-ARCHITECTURE.md`；v7 历史架构（全流程自动化优化环）见
> `docs/archive/` 与 CHANGELOG v7.x 系列。
> 最后更新：2026-11-17（v8.0.0）

---

## 1. 顶层架构

```
┌──────────────────────────  自动化（无人值守） ──────────────────────────┐
│                                                                        │
│  【A 文献链】（保留 v7 设施）                                            │
│   简报 cron ×4/天 → Gate 评分 → 深读 → 蒸馏(kb_distill) → 聚类          │
│   → topic_match → 周末输入链 compose ──→ research_topics/questions/     │
│                                          （问题收件箱，A2 新颖性硬门）   │
│                                                                        │
│  【B 深研链】lc-topic-daily（工作日 09:30，配额 1 课题/天）               │
│   B1 背景调研(researcher) → B2 问题定位(analyst) → B3 方案分解(writer)   │
│   → B4 启动包集成（零 LLM 机械组装 + KB 方法素材包挂载）                  │
│                                                                        │
│  【C 验收自检】（零 LLM）A1-A4 + G1-G2 → 全过自动晋级 ready/             │
│                                                                        │
│  【辅助】workbench_monitor（6h）· backup · kb-sync · step_usage 计量     │
└────────────────────────────────────────────────────────────────────────┘
              │ research_topics/ready/（启动包就绪）
              ▼
┌──────────────────────────  人工（法定节点） ────────────────────────────┐
│   ① 问题候选否决（reject）  ② 启动包采纳启动（activate）                 │
│   ③ 课题收尾归档（archive）  ④ 正式研究推进（1v1 会话 + task_manager）   │
│   ⑤ 跨课题/跨时间整合（人主导）                                          │
└────────────────────────────────────────────────────────────────────────┘
```

**定位转变**：v7 是「虚拟合作者全流程自动化」（自动产完整项目书+多轮优化评审）；
v8 是「研究工作台」——自动化产出**课题启动包**，人启动正式研究。裁决依据见
`docs/WORKBENCH-ARCHITECTURE.md` §1。

## 2. 模块分类与导入边界

| 分类 | 命名约定 | 说明 |
|------|----------|------|
| **工作台核心** | 无前缀（`copilot_engine.py`、`session_manager.py`、`memory_manager.py`、`task_manager.py`） | 核心互相导入；管线模块不可导入 |
| **课题管线（v8）** | `topic_pipeline/` 包 + `topic_pipeline.py` shim + `workbench_monitor.py` | hermes 调用统一走 `topic_pipeline.hermes_runner`（环境清洗 + API 错误特征检测 + step_usage 计量）；状态写入经 `file_lock` |
| **文献/知识库链** | `deep_read_pipeline.py`、`literature_*.py`、`external_fetcher.py`、`kb_*.py`、`weekend_pipeline/`（输入端） | 对知识库只读，写经 `learning_engine`/`kb_wiki` 门面 |
| **共享基础设施** | `common.py`、`paths.py`、`llm_gateway.py`、`hermes_bridge.py`、`skill_loader.py`、`step_usage.py`、`logger.py` | 双方均可导入 |
| **Web 路由 Mixin** | `web_routes_*.py` | 仅被 `web_server.py` 聚合导入 |
| **退役代码** | `scripts/archive/v7-optimization/`（28 个） | 不得被保留代码引用；回溯时拷回 |

**数据域**：`research_topics/`（v8 活跃，状态=目录位置+课题卡头域；`_topics.json` 仅轻量索引）、
`knowledge/`（共享只读）、`research_proposals/`（v7 legacy 只读）、`sessions/ memory/ tasks/`（核心用户数据）。

## 3. topic_pipeline 包（v8 核心）

```
scripts/topic_pipeline/
├── constants.py      路径/阈值/配额（LINSAI_TOPICS_ROOT 环境变量可重定向，测试用）
├── similarity.py     零 LLM 相似度（中文 2-gram + 拉丁词 Jaccard，A2 硬门）
├── state.py          _topics.json 轻量状态总线（锁内读改写；阶段即目录 move_topic_dir）
├── card.py           课题卡渲染/解析/事件追加
├── registration.py   问题候选注册（ID 命名 + A2 新颖性硬门 + 否决台账对照）
├── hermes_runner.py  hermes oneshot 执行器（继承 v6.8.46 API 错误防线 + 计量入账）
├── deep_research.py  单遍深研 B1→B3（skill 注入、产物校验、缺口计数、needs_human）
├── assemble.py       B4 组装（报告模板 + G1 自适应收缩 + KB 方法素材包挂载）
├── acceptance.py     六项验收自检（kickoff-check.json 落盘 + 缺口写回）
├── migration.py      v7→v8 复制式迁移（幂等，迁移报告落 _audit/）
├── daily.py          每日调度（配额/开关经 memory/config/workbench.json）
├── cron.py           v8 cron 安装（幂等，wrapper 写入 hermes profile scripts/）
├── weekend_bridge.py 周末输入链桥接（register/enrich/supplementary/两域数据源）
└── cli.py            命令行入口（register/daily/deep-dive/assemble/check/activate/reject/
                     archive/migrate-v7/list/setup-cron）
```

CLI 经薄 shim `scripts/topic_pipeline.py` 调用（import 解析到同名包，与
`proposal_lifecycle.py`/`proposal_lifecycle/` 同模式）。

## 4. 数据流与产物契约

**深研产物契约**（缺失即该步未完成，缺口留待下次补齐）：

| 步骤 | profile | 产物 |
|------|---------|------|
| B1 | researcher | `01_background/literature-map.md`（≥8 篇文献组 + KB 关联）+ bib |
| B2 | analyst | `02_problem/problem.md`（一句话陈述/新颖性对照/判据三标记 [V]/[P]/[D]） |
| B3 | writer | `03_scheme/scheme.md`（S1..Sn 步骤含判据 + 首月路线）+ `04_references/references.bib`（source 溯源行） |
| B4 | —（零 LLM） | `topic-report.md`（五节模板）+ `03_scheme/kb-methods-pack.md` |

**阶段流转**：`questions → kickoff（物理搬移目录）→ ready（自检全过）→ active（人工）→ archive（人工）`；
否决候选进 `_rejected-questions/` 台账（防重复立项）。

**skill 注入**：B1/B2/B3 的 prompt 经 `skill_loader.inject_block` 注入对应纪律节
（literature-reading / research-proposal / method-manual），fail-open。

## 5. cron 拓扑（v8）

hermes gateway 承载（`~/.hermes/profiles/linsai/cron/`），25 个活跃 job：

- **保留（文献/KB/备份）**：简报×6（含每日汇总 20:00）、lc-kb-sync、lc-kb-distill(+pm/night/sunday)、
  lc-weekend-input×10、lc-daily-backup、lc-zcode-worker（方法卡回补已于 2026-11-19 收官清零，空转待裁决）
- **新增（v8）**：lc-topic-daily（`topic_pipeline.py --daily`）、lc-workbench-monitor（`workbench_monitor.py`）
- **已停用（v7 优化环 14 个）**：审计见 `memory/v8-cron-teardown.json`

cron 对账由 `workbench_monitor.V8_CRON_EXPECTED` 承担（v7 的 `lifecycle/cron_manifest.py`
+ `lifecycle_monitor.py` 随优化环退役，保留代码不再调度它们）。

## 6. Web 层（v8）

- **新增**：`web_routes_topics.py`（`/api/topics/*`：看板/详情/启动/否决/归档/触发深研/自检）
  + 前端「课题工作台」页（四列看板 + 启动包详情 + 法定节点按钮）。
- **保留**：sessions/tasks/knowledge/skills/learning/hermes/settings 命名空间。
- **legacy 只读**：lifecycle/orchestrator/console/pipeline 命名空间保留只读入口
  （v7 数据域已冻结，不再提供触发按钮）。

## 7. 韧性防线（继承 v7，全部有效）

- **API 错误特征检测**（v6.8.46）：hermes 配额/限流错误文本（10 特征）在
  `topic_pipeline.hermes_runner` 源头拦截，不产生伪产物。
- **产物校验**：done 必有产物（`_verify_artifacts` 三阶段通用语义的 v8 版）。
- **计量账本**（v6.10.55）：`step_usage` 记录每次 hermes/LLM 调用（测试入口自动拒绝记账）。
- **缺口补齐上限**：同缺口补 2 次 → needs_human，杜绝无限重试烧 token。
- **并发安全**：`file_lock` + `save_json` 原子写；per-topic 目录级隔离。
- **零 LLM 优先**：组装/自检/相似度全部确定性实现，LLM 只用于深研三步。

## 8. 测试基线

`python3 scripts/self_test.py --module`：**3576/3576**（v8.0.0，2026-11-17）。
v7 优化环 339 个断言随模块归档移出；新增 `test_topic_pipeline` 16 用例
（零 LLM 零 hermes：mock runner + 临时数据域 `LINSAI_TOPICS_ROOT`）。
