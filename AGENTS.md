# LinSai-CoPilot — 林赛研究工作台

> 本文件供 AI 编码代理阅读。假设读者对本项目一无所知。
> 项目语言：中文（所有文档、注释、脚本输出均为中文）
> 最后更新：2026-11-20（v8.0.40 空转自动化退役：lc-zcode-worker 暂停 + ZCode 回补 automation 删除，cron 25→24）
> 提示：完整目录结构见 `docs/PROJECT-STRUCTURE.md`，v8 设计纲领见 `docs/WORKBENCH-ARCHITECTURE.md`，架构细节见 `docs/ARCHITECTURE.md`。

---

## 项目概述

**LinSai-CoPilot**（林赛研究工作台）是一个**研究工作台系统**——自动化负责文献阅读与深度研究，产出**课题启动包**；人负责选题、启动与正式研究的推进。

**v8 核心定位（用户裁决 2026-11-16）**：
- 自动化产出目标 = **课题启动包（proposal）**：文献阅读发掘有价值的科学问题 →
  单遍深度研究探索方案 → 整合参考文献与**课题报告**。
- 课题报告要求：**背景调研充分、问题定位清晰、方案分解明确**——为课题正式研究
  提供可以具体推进的方法和路线。
- **课题报告区分于项目书**：聚焦一个具体问题，不做完整申请书；不同课题报告可形成关联。
- **协作引擎简化为工作台**：林赛是工作台协作助手（响应式 1v1 会话），不是全流程
  自动的虚拟合作者；主动自动化仅剩文献链 + 每日深研 worker。

**为什么放弃 v7 全流程自动化**（用户裁决三条根因）：完整项目书内容庞杂难以自动化
优化好；多轮评审优化 token 消耗过大；上下文限制下自动化不擅长多方信息与跨时间
尺度的整合——这正是应由人主导的部分。

### 项目三大产出

| 资产 | 位置 | 定位 |
|------|------|------|
| **课题库** | `research_topics/` | **核心产出**。问题候选 → 深研 → 课题启动包（课题报告+参考文献+方法素材）→ 人工启动 → 归档 |
| **技能库** | `.hermes/skills/`（管线）+ `skills/`（会话） | 可复用能力资产，可服务于其它类似项目 |
| **知识库** | `knowledge/` | 经过验证的知识积累；文献链的沉淀，反哺深研链 |

三库关系：知识库支撑文献发现与深研究材 → 课题启动包生产 → 正式研究产出回流知识库。

### 与相关项目的关系

| 项目 | 角色 | 关系 |
|------|------|------|
| **virtu-LinSai** | 人格资产生产端 | 上游。本项目**引用但不修改**其资产（SOUL.md / 林赛-perspective）。 |
| **hermes** | 本地 agent 执行引擎 | 搭档。工作台通过 hermes CLI 调用 researcher/analyst/writer 等 profile 执行深研。 |
| **persona-discussion (Agora)** | 历史人物群聊应用 | 参考架构，交互模型不同。 |

---

## 核心设计决策

### D1：课题库申请人无关化（2026-10-30 用户确认，v8 延续）

课题库产出是**申请人无关的研究方案**——聚焦课题本身的科学内容，排除研究基础、
工作条件、团队构成、经费预算等章节，任何组件不得将其缺失列为缺陷。

### D2：自动化产出定位为课题启动包（2026-11-16 用户裁决，v8.0.0 核心）

- 全自动化**不再**生成完整项目书、**不做**多轮优化评审（v7 的章节评审/一致性修订/
  评审团/对抗奖惩机制停用，代码归档 `scripts/archive/v7-optimization/`）。
- 自动化边界到 `ready` 为止：**人不批准不启动**（ready → active 仅用户可触发）。
- 课题报告区分于项目书：聚焦一个具体问题；跨课题/跨时间的整合由人主导。
- 若未来转向真实 NSFC 申报，须由用户显式发起并升级本条决策。

### D3：复制不删除（迁移与清理纪律）

v7 存量课题全部**复制式迁移**入 `research_topics/`，旧域 `research_proposals/`
原位保留为只读 legacy（审计与回滚线索）；废弃代码**归档不删除**
（`scripts/archive/`、`scripts/tests/archive/`）。

---

## v8 工作流程（详见 docs/WORKBENCH-ARCHITECTURE.md）

```
【A 文献链】（保留 v7 全部设施）简报 4次/天 → Gate 评分 → 深读 → 蒸馏 → 聚类
  → topic_match → 周末输入链 compose → questions/ 问题收件箱（A2 新颖性硬门）

【B 深研链】（v8 核心）每日对队首问题候选单遍深研（配额默认 1 课题/天）：
  B1 背景调研（researcher profile）→ 01_background/literature-map.md
  B2 问题定位（analyst profile）→ 02_problem/problem.md
  B3 方案分解（writer profile）→ 03_scheme/scheme.md + references.bib
  B4 启动包集成（零 LLM 机械组装 + KB 方法素材包挂载）→ topic-report.md

【C 验收自检】（零 LLM）A1-A4 + G1-G2 六项判据 → 全过自动晋级 ready/

【人工节点 1】用户审阅启动包 → 一键启动 → active/（进 task_manager，1v1 会话推进）
【人工节点 2】研究完成/搁置 → archive/（关键知识萃取回知识库）
```

### 课题启动包验收标准（零 LLM 可查证）

| 编号 | 标准 | 判据 |
|------|------|------|
| A1 | 背景调研充分 | 笔记/知识卡 ≥8 篇（近 24 个月 ≥3）+ KB wikilink ≥3 |
| A2 | 问题定位清晰 | problem.md 含一句话陈述 + 新颖性对照；相似度 <0.50（2-gram Jaccard） |
| A3 | 方案分解明确 | ≥3 个步骤节、每步含判据、含首月路线、方法素材包已挂 |
| A4 | 参考文献真实 | bib 非空、每条带 source 溯源行、报告引用键与 bib 对得上 |
| G1 | 篇幅约束 | 报告 ≤8000 字（课题报告 ≠ 项目书） |
| G2 | 关联明确 | related 字段显式声明 + 报告 wikilink ≥5 |

同缺口补 2 次仍不过 → `needs_human` 挂起等人裁决。

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 运行环境 | Python 3（仅标准库） | 零第三方依赖，无 requirements.txt 等构建文件。 |
| 内容格式 | Markdown（.md） | 课题卡、课题报告、知识库笔记。 |
| 元数据 | JSON | topics 状态总线、管线状态。 |
| LLM 接口 | MiniMax-M3（主） / GLM-5.2 / Claude CLI | 经 hermes profile 管理；`llm_router.py`/`llm_gateway.py` 自动降级。 |
| Web 服务器 | Python `http.server.ThreadingHTTPServer` | REST API + SSE。 |
| 前端 | 原生 HTML/CSS/JS | 零框架，CSS 变量 + data-theme。 |
| 进程锁 | `fcntl.flock`（POSIX） | 跨进程锁 + 原子写入。 |

**关键约束**：仅标准库；敏感凭据只存 `.env` 与 `memory/llm-config.json`（已 gitignore）。

---

## 运行与构建

**无构建步骤**。Python 脚本直接运行。

### 课题工作台（v8 主入口）

```bash
python3 scripts/topic_pipeline.py --list                    # 课题看板
python3 scripts/topic_pipeline.py --register --title "..." --problem "..." --slug "..."
python3 scripts/topic_pipeline.py --daily                   # 每日深研 worker（cron 入口）
python3 scripts/topic_pipeline.py --deep-dive <topic_id>    # 手动深研（可 --steps background,problem）
python3 scripts/topic_pipeline.py --assemble <topic_id>     # 手动组装 B4
python3 scripts/topic_pipeline.py --check <topic_id>        # 验收自检
python3 scripts/topic_pipeline.py --activate <topic_id>     # 人工启动（ready→active）
python3 scripts/topic_pipeline.py --reject <topic_id> --reason "..."
python3 scripts/topic_pipeline.py --migrate-v7 [--dry-run]  # v7 存量迁移（已完成，幂等）
python3 scripts/topic_pipeline.py --setup-cron              # 安装 v8 cron（幂等）
python3 scripts/workbench_monitor.py                        # 轻量健康检查
```

### 启动 Web 工作台

```bash
python3 scripts/web_server.py              # 默认端口 8080
./scripts/launch.sh                        # 一键启动
```

### 启动 CLI 会话

```bash
python3 scripts/copilot_engine.py --start "主题"   # 工作台协作助手（1v1 会话）
python3 scripts/copilot_engine.py --continue
```

### 常用维护命令（文献/知识库链，保留）

```bash
python3 scripts/backup_manager.py                         # 手动备份
python3 scripts/kb_maintenance.py --weekly                # 知识库周维护
python3 scripts/kb_distill.py --dry-run                   # raw→wiki 蒸馏预览
python3 scripts/kb_methods_backfill.py --worklist 5       # 方法卡发射清单（ZCode 消费）
python3 scripts/sync_engine.py                            # 同步 hermes 产出
```

### 语法检查

```bash
python3 -m py_compile scripts/*.py
```

---

## 测试策略

三层测试体系（零污染 / 零成本 / 自动发现）：

1. **单元/核心回归**：`python3 scripts/self_test.py --module`（自动发现 `scripts/tests/test_*.py`）。
2. **模块自检**：多数脚本支持 `--self-check`。
3. **E2E**：`python3 scripts/test_e2e_learning_full.py`（非日常回归项）。

**当前基线（v8.0.100，2026-11-22）**：
- `--module`：**3640/3640 全量通过**（v8.0.0 迁移后：339 个 v7 优化环断言随模块归档移出回归，
  新增 test_topic_pipeline 24 + test_web_routes_topics 10 用例；周末链桥接、cron 幂等测试已适配 v8；
  2026-11-20 整点轮新增 test_workbench_monitor 7 + test_learning_source_links 7 +
  test_topic_cross_similarity 5 用例；48h 推进期新增 test_harness_metrics 15 +
  test_snapshot_bridge 5 + test_provenance_audit 3 用例）。
- `--scenario`：16/16；`--persona`：38/38；`--web-ci`：见 CHANGELOG；E2E 学习链 3/3（v8.0.33）。
- v8 新管线测试：`scripts/tests/test_topic_pipeline.py`（注册/新颖性硬门/深研 mock/组装/
  验收自检/迁移/周末桥接/每日调度，零 LLM 零 hermes）。

---

## 代码规范

### Python 脚本

- **仅标准库**；头部中文 docstring 含用法示例；含 `_self_check()`。
- 路径用 `pathlib.Path`；`PROJECT_ROOT` 由 `Path(__file__).parent.parent` 推导
  （topic_pipeline 包内为 `.parent.parent.parent`，注意层级）。
- JSON 输出 `ensure_ascii=False, indent=2`；时间戳 UTC ISO（`%Y-%m-%dT%H:%M:%SZ`）。
- 输出中文，状态图标：`✓` 成功、`✗` 失败、`⚠` 警告、`○` 待处理、`◐` 进行中。
- 原子写入 `common.save_json`；跨进程锁 `common.file_lock`。
- **新脚本准入检查清单**（docstring/自检/零依赖/路径/CHANGELOG 记录等）沿用 v7 约定。

### 模块分类与导入边界（v8 简化）

| 分类 | 说明 |
|------|------|
| **工作台核心** | `copilot_engine.py`、`session_manager.py`、`memory_manager.py`、`task_manager.py` 等 |
| **课题管线（v8）** | `topic_pipeline/` 包 + `topic_pipeline.py` shim + `workbench_monitor.py`；hermes 调用统一走 `topic_pipeline.hermes_runner`（含 API 错误特征检测 + step_usage 计量） |
| **文献/知识库链** | `deep_read_pipeline.py`、`literature_*.py`、`external_fetcher.py`、`kb_*.py`、`weekend_pipeline/`（输入端） |
| **共享基础设施** | `common.py`、`paths.py`、`llm_gateway.py`、`hermes_bridge.py`、`skill_loader.py`、`step_usage.py` |
| **Web 路由 Mixin** | `web_routes_*.py`，仅被 `web_server.py` 聚合 |

- 课题管线模块不导入会话/记忆/LLM 路由等核心模块（LLM 经 hermes CLI 或 `llm_gateway`）。
- 知识库对管线只读；写入经 `learning_engine` / `kb_wiki` 门面。
- `scripts/archive/v7-optimization/` 内模块已退役，保留代码不得引用。

### skill 层

5 个 SKILL.md（`.hermes/skills/`）仍是能力单一真相源，经 `skill_loader.py` 按节注入：
- 深研链使用：`literature-reading`（B1）、`research-proposal`（B2/B3）、`method-manual`（B3 参数溯源）。
- `nsfc-writing` / `quality-review` 标注 **legacy**（仅供人工项目书场景）。

### 变更记录

所有修改在 `CHANGELOG.md` 记录，格式：
```markdown
## vX.Y.Z - YYYY-MM-DD 简短描述
- 修改内容
- 验证结果
```

---

## 数据域

```
LinSai-CoPilot/
├── research_topics/       ← v8 活跃域：questions/kickoff/ready/active/archive + _audit/ + _rejected-questions/
│   └── {topic_id}/topic-card.md · topic-report.md · 01_background/ · 02_problem/ · 03_scheme/ · 04_references/
├── research_proposals/    ← v7 legacy 只读域（全部课题已迁出，保留审计线索）
├── knowledge/             ← 共享：知识库（raw→wiki→方法卡→图谱）
├── sessions/ memory/ tasks/  ← 工作台核心（用户数据，gitignore）
└── scripts/               ← 所有模块（archive/ 为退役代码）
```

- 课题状态由**目录位置 + 课题卡头域**承载；`research_topics/_topics.json` 只存轻量索引。
- 管线模块写入限定在 `research_topics/{topic_id}/` 与 `knowledge/` 经授权路径。

---

## hermes 协作架构（v8 精简）

| Profile | v8 职责 |
|---------|---------|
| `linsai` | 总控 profile（cron 宿主、会话） |
| `researcher` | B1 背景调研（文献检索与领域地图） |
| `analyst` | B2 问题定位（新颖性对照与判据） |
| `writer` | B3 方案分解（步骤/里程碑/首月路线） |
| `reviewer` / `critic` / `pipeline-runner` | legacy（优化环退役，保留可手动调用） |

调用方式：`hermes --profile <p> -z <prompt>`（oneshot agent loop）；
`topic_pipeline.hermes_runner.run_hermes` 统一封装（环境清洗 + API 错误特征检测 + 计量入账）。

### v8 cron 清单（hermes gateway，共 25：22 活跃 + 3 暂停）

| 组 | job |
|----|-----|
| 文献发现（保留） | 林赛简报×6（检索入池+知识库简报 00/06/12/18:23 / 候选判定 08:28 / 经典文献 14:23 / 高分深读 16:23 / 健康检查 23:30 / 每日汇总 20:00） |
| 知识库治理（保留） | lc-kb-sync、lc-kb-distill、lc-kb-distill-pm、lc-kb-distill-night(paused)、lc-kb-distill-sunday(paused) |
| 周末输入链（保留） | lc-weekend-input×10（input 周六 09:30 + n1-4 周六/周日晨 + r2-6 周日午后；发现链核心，new 路由已桥接到 topics 域） |
| 系统（保留） | lc-daily-backup（13:00 全量 zip）；lc-zcode-worker **已于 2026-11-20 用户裁决暂停**（回补收官 3929/3929，恢复：`hermes --profile linsai cron resume lc-zcode-worker`，审计：`memory/self-optimize/automation-decommission-2026-11-20.json`） |
| **v8 新增** | **lc-topic-daily**（工作日 09:30 深研 worker）、**lc-workbench-monitor**（6h 轻量监控） |

v7 优化环 14 个 cron 已于 2026-11-16 停用（审计：`memory/v8-cron-teardown.json`）；
安装入口统一为 `topic_pipeline.py --setup-cron`（幂等），不要再用 v7 的 `--setup-cron-v2`。

### 工作台辅助层

- **健康检查**：`workbench_monitor.py`（cron 对账 + kickoff 停滞 + needs_human 计数 + 备份产物新鲜度 + KB 告警复用）。
- **人机分工**：执行/修复/治理全自动（文献链+深研），**3 个法定节点人工**：
  问题候选否决（reject）、启动包采纳启动（activate）、课题收尾归档（archive）。
- **计量账本**：`step_usage`（JSONL 月分片）继续记录全部 LLM/hermes 调用。

---

## 安全与隐私

- **无敏感凭据入仓**；**本地优先**；`references/` 只读；知识库 `raw/` 保留原貌。
- 路径遍历防护（`_safe_join` 等）；并发安全（file_lock + 原子写入）；
  XSS 防护（escapeHtml）；命令执行白名单；记忆隔离。

---

## 版本与升级

### 版本号规范

- `VERSION` 文件唯一真相源（当前 `8.0.0`）；格式 `MAJOR.MINOR.PATCH`。
- **版本线纪律**：不得回退旧 minor 线；提交前以 CHANGELOG 最新条目对账。
- **版本号领取协议**：写 CHANGELOG 前先 `grep -E '^## v' CHANGELOG.md | head -3`，
  取严格更大号；提交前跑 `python3 -m unittest scripts.tests.test_version_monotonic` 守门。

### Git 管理策略

- 用户数据（sessions/memory/tasks/references/knowledge raw）已被 gitignore。
- `knowledge/raw/pdfs/` 不入 git（v7.0.2 裁决）。
- 每次功能迭代一个 commit：`vX.Y.Z - 简短描述`。

### 数据安全原则与 Git 操作红线（沿用 v7，全部有效）

| 原则 | 说明 |
|------|------|
| **用户数据无价** | 会话、记忆、任务、课题、知识库一旦丢失不可重建 |
| **备份优先 / 恢复可验证 / 升级可回滚** | 更新前先备份；备份包必须能完整恢复 |
| **产出即资产** | AI 生成的代码、文档、设计、数据均属用户资产，不得擅自处置 |

**永久禁止**：`git stash`+`drop`、冲突 force pop、`git reset --hard`、`git clean -fd`、
`git checkout .`、`rm -rf` 批量删除。需要对比时用 `cp -r` 临时副本或 `git diff`。
根因与教训见 v6.8.16 条目（stash drop 曾丢失 8 项功能改动）。

### 自动提交规则

用户授权的修改完成后立即 `git add -A && git commit`，测试通过即提交，不积攒。

---

## 参考文件优先级

1. `persona/lin-sai-persona.md` — 人格注入文件（项目内权威）
2. `AGENTS.md` — 本文件（项目架构与规范）
3. `docs/WORKBENCH-ARCHITECTURE.md` — v8 设计纲领与验收标准
4. `virtu-LinSai/PROJECT-STATE.md` — 上游角色锚点
5. `virtu-LinSai/PERSONA/` — 上游人格提炼

---

*版本：8.0.0*
*日期：2026-11-17*
*创建者：AI 编码代理*
*上游资产来源：virtu-LinSai v2.7*
