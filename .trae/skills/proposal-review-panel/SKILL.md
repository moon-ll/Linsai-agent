---
name: "proposal-review-panel"
description: "Runs an independent multi-reviewer panel (R1 science / R2 language / R3 citation / R4 style benchmark) plus per-proposal revision agents to deep-review and revise NSFC proposals, aligned with the dual-channel promotion pipeline (v7.2.24+). Invoke when user asks for manual/panel review of optimizing proposals, '评审团', '多角色评审', or systematic revision of 申请书."
---

# 申请书评审团模式（Proposal Review Panel）

对一批申请书执行"多评审员独立深审 + 逐篇修改 agent 裁决执行 + 总验收"的三段式流程。核心原则：**评审员互相独立（并行派发、互不可见意见），只有修改 agent 做汇总**；意见必须具体到位置与原文摘录，修改建议必须可直接落笔；引用元数据与量化锚数字只信检索原文。

输出语言跟随用户（本项目默认中文）。

## 适用场景与双轨分工

- **本 skill（人工评审团）**：R1-R4 四维独立深审，用户指令触发。适用：自动管线多轮无效的平台期根因诊断（如 rigor 反复卡点）、负反馈课题（monitor 连降）根因修复、通道 B 验收前的最后防线深审。
- **自动评审团（`scripts/panel_review.py`）**：hermes 三角色（researcher/critic/reviewer）+ writer 深改 + critic 验清单，`panel_review_requested` 自动触发。常规平台期课题优先走自动通道，人工介入留给它消化不掉的硬骨头。
- 不适用：单篇快速迭代（走管线 critic/writer）、纯评分（直接综合评审）。

## 阶段 0：对象盘点（按链路状态定优先级）

数据源：`research_proposals/_lifecycle.json`（`proposals.{slug}`）+ `memory/human-queue.json`。

优先级从高到低：
1. **负反馈课题**（`negative_feedback_alert` / monitor 独立分连续 3 轮下降）——链路已停摆等人工，必进本轮
2. **`panel_review_requested=True`** 平台期课题（0.70-0.85 主平台带自动转入，调度已让出机时）
3. **骤降/异常课题**（章节分相对 monitor 分大幅背离、单轮跌 >0.10）
4. **通道 B 临界课题验收前深审**（末 3 轮章节分贴 0.82 线 + monitor ≥0.80，晋级 pending_review 前的最后人工防线）

盘点输出：每课题的轮次 / 末 3 轮章节分 / monitor 分 / `open_critical_issues` 未解决数 / panel 与负反馈标志。跳过轮次 0 模块空课题。

**开工前置（防并发写冲突，必须执行）**：目标课题若 `panel_review_requested=False`，开工前先置 True——调度器会自动跳过该课题（micro_scheduler 让出机时），避免 writer 与 M1 并发写同一文件。写法：`common.file_lock("lifecycle")` 下读改写 `_lifecycle.json` 原子落盘（禁止裸写，v7.2.27 测试污染教训）。完工后按结论处置标志（见阶段 3）。

## 阶段 1：四路独立评审

R1+R2+R3 三路并发（subagent 并发 ≤3）→ R4 单独一轮。评审员只读不写（Explore 类 subagent 不能落盘，报告由主代理汇总落盘）。

| 角色 | 人格 | 唯一职责 | 关键要求 |
|---|---|---|---|
| R1 科学性 | 领域资深 PI | 科学意义/创新性/可行性 | 物理硬错（对称性/守恒律/换算）、创新点真实性、判据有据、跨模块口径一致；**量化锚逐条联网反查原文**（见硬约束 1） |
| R2 语言表达 | 学术写作专家 | 准确/逻辑/自然/严谨 | **每条附完整可替换修改文本**；超长句/堆砌段/过程性残留逐条列（与 writer 写后自检门同口径：写前写后对比回弹） |
| R3 引用审校 | 期刊文献编辑 | 引用准确/真实/覆盖 | 程序化编号对账 + 高风险条目联网反查；新增/修正引用**逐字段对照检索池三源**（`02_literature/lit-gap`、`candidates.bib`、reading-notes），池中无记录不得写入 |
| R4 范本风格 | 评审老手 | 对标范本标杆 | 指标程序统计（字数/引用次数/罗列处/主语混用/空泛词），逐项给数字 |

意见统一格式：`[Rn-序号|severity] 模块｜位置｜问题(≤40字)｜原文摘录(≤60字)｜修改建议(≤80字或完整替换文本)`

**评分锚定纪律（与管线 critic 同锚，v7.2.18）**：R1 打分先数档再打分——rigor 五项核查（数值链一致 / 指标定义可操作 / 文献支撑真实 / 逻辑闭环 / 模块自洽）按过项数定档，五项全过 = 0.90+；禁 0.75 折中摇摆；每条扣分意见映射到五项清单编号。分数带语境：0.82 = 通道 B 验收线，0.90 = 免检线，评审团深改目标态 = 亲审通过质量（0.90+ 锚）。

## 阶段 2：M1 逐课题修改

每课题一个 M1 实例（分轮执行，每轮 ≤3 并发，各课题文件互不相交；同一文件内多处编辑串行）。

M1 输入：该课题 4 份意见节选 + **上轮已修清单（防回退防重复）** + 待改文件路径 + 该课题 `04_proposal/params.json`（若存在）。

M1 职责与裁决：
- 逐项裁决（采纳/改后采纳/驳回+理由）→ 执行修改 → 润色 → 落逐项确认表
- 裁决优先级：**R1 科学正确 > R3 引用准确 > R2 语言 > R4 风格**；冲突时高优先级胜出并注明
- **口径播种（v7.2.19）**：凡修复跨章数值/机制表述口径，把确认的 canonical（允许整句规范表述）播种进该课题 `04_proposal/params.json`（`key/canonical/stale_patterns/note` 四字段，旧值正则进 stale_patterns）——后续 writer prompt 自动携带、落盘后 grep 校验，根治"改一崩二"打地鼠循环

## 阶段 3：总验收与链路回灌

程序化抽查：
- [ ] 每课题逐项确认表完整（含驳回理由）
- [ ] 引用对账终态：占位符/死条目/超界/一号两用/断链全部为 0（抽 3-5 课题 grep）
- [ ] `python3 scripts/lifecycle/params_registry.py --check <课题>`：stale_patterns 残留归零（若播种了口径）
- [ ] **`open_critical_issues` 未解决 P0 清零**（通道 B 硬门槛，不清零永远触发不了晋级）
- [ ] git status 干净、提交链完整（每课题改完即提交，消息含课题名与要点）
- [ ] 遗留项清单写入执行报告

完工后课题处置：
- **深改通过** → 清 `panel_review_requested`（file_lock 下原子改），课题回自动循环重新积累末 3 轮章节分走通道 B
- **达标待验收** → 留给管线自然晋级 pending_review（review_dossier 三档预审 + 审核会话，一键采纳门槛 0.85）
- **P0/P1 未尽事项 + 角色级教训** → 写入 `06_feedback/feedback-N-raw.md` 并在 file_lock 下递增 `_lifecycle.json` 的 `human_feedback_count`（下轮 critic/writer prompt 经 `load_review_feedback_for_optimization` 自动注入闭环）
- writer/critic 表现评价 → `memory/agent-feedback-YYYYMMDD.md`（供 retrospective/prompt_optimizer 拾取）
- 与自动管线冲突时：引用密度收敛等工程项可驳回留给程序化后处理，报告中注明

## 硬约束（实战教训，违反必出事故）

1. **引用元数据与量化锚禁止凭记忆生成**。两层：① DOI/卷期/arXiv 号当轮检索核实，无法核实即删条目或去引用化；② **量化锚数字必须反查原文真含该数字**——文献真实 ≠ 锚定成立（M2.2.1 教训：Pabst/Kheifets 摘要仅定性，被用作 2% 残余阈值量化锚站不住，四层挂靠回退 6 处）。原文无量化数字的锚降级为机理/方法锚，或改"方案设定值，第一阶段实测标定"。
2. **编号重排必须程序化**（临时 python 脚本放系统临时目录，勿入仓库）：两阶段占位替换 + 五项对账校验（零占位符/零死条目/零超界/零一号两用/零断链）。
3. **并发纪律**：subagent 同轮 ≤3；M1 各课题文件互不相交才可并发；同一文件内多处编辑串行（并行编辑曾互相覆盖）；目标课题开工前置 panel 标志让调度让位。
4. **防回退机制**：M1 输入必须含上轮已修清单，改完 grep 复核已修项未被回退。
5. **大改保守原则**：科学内容按 R1 文本改、不确定就降保守表述；补写内容只用现有列表可核实文献支撑，禁止编造新文献编号。
6. **过程性残留清扫**：审校注记、内部文件名引用、检索时间戳、评审框架自指、英文年度标记（Year 1→第 1 年）在 M1 内一并清理。
7. **`_lifecycle.json` 只在 file_lock 下读改写**（register 污染守卫同源教训）；不裸写、不在测试上下文写。

## 参数化示例

- 目标集合：`research_proposals/optimizing/*/04_proposal/sections/`（跳过模块空课题）
- 范本标杆：`memory/nsfc-standards.json` 的 `reference_materials.style_benchmark`（读文件，勿凭记忆复述）
- 产出目录：`research_proposals/_manual-review-YYYYMMDD/`（含 panel/R{1,2,3,4}-*.md、总报告、执行报告）；每课题逐项确认表 `05_review/manual-revision{-roundN}-YYYYMMDD.md`
- 日期：执行当天 `YYYYMMDD`；同日多轮加 `-roundN` 后缀复用同一目录
