# 对抗评审报告（第 4 轮 · 整体一致性审查）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文≤30 页） |
| 本轮聚焦 | 整体一致性审查——跨模块衔接与连贯性（段落级） |
| 聚焦章节文件 | `04_proposal/sections/full_review.md`（3 行占位符，writer 未产出整体审查） |
| 实际评审对象 | 全部 5 个章节文件：rationale.md / content.md / scheme.md / references.md / full_review.md |
| 质量标准 | `memory/nsfc-standards.json` → `project_types.general`（min_overall=0.80；max_high=0；max_medium=3）+ `general_principles.writing_style_rules` |
| 评审日期 | 2026-08-03 |
| profile | critic |
| 历史脉络 | round-1（空壳）→ round-2（content 聚焦，0.62）→ round-3（scheme 聚焦，0.60）→ round-5（rationale 聚焦，0.71）→ meta-review-5（独立监察，0.68）→ **本轮（整体一致性，跨章深审）** |

> **本轮定位**：full_review.md 仍是占位符（"待本轮 writer-critic 循环结束后统一审查"），writer 未产出整体审查。因此本轮红队评审以"跨章节一致性"为核心抓手——构建 16 对章节一致性矩阵，逐对核查衔接是否连贯、术语是否统一、数值是否自洽、逻辑是否递进。**本轮最突出的发现**：writer 在 round-3 之后对 scheme.md 做了实质改写（§3.1/§3.2 编号列表已改为连贯叙述，2 处 [high] narrative 大幅改善 ✅），但**多处跨章不一致在修复 content/scheme 后未同步 rationale**，形成"修了两章漏了一章"的系统性同步失败——其中 rationale §1.2.1 的 cutoff 律物理计算错误（3-5×1.6 eV ≠ 30-40 eV）跨 round-3/round-5 至今未修，是最严重的残留。

---

## 0. 模块完整性检查（7 个标准模块）

按用户指令核查 7 个标准模块。**用户预警缺失 innovation / plan / 参考文献**——经逐文件核查，实际情况与预警存在偏差，红队据实报告：

| 标准模块 | 定位 | 字符数（约） | ≥200 字且有实质内容 | 结论 |
|---|---|---:|---|---|
| 立项依据 | rationale.md（§1.1–§1.4） | ~16500 | 是 | ✅ 完整 |
| 研究内容 | content.md（§2.0–§2.9） | ~23600 | 是 | ✅ 完整 |
| 研究方案 | scheme.md（§3.1–§3.6） | ~20000 | 是 | ✅ 完整 |
| 特色与创新 | content.md §2.8 + scheme.md §3.5（**两处重复**） | ~520 + ~2600 | 是 | ⚠️ **内容存在但跨章重复**——用户预警"缺失 innovation"与实际不符：创新点在 §1.4 / §2.8 / §3.5 三处出现（§1.4 科学层面、§2.8 研究内容层面、§3.5 技术方案层面），内容齐全但**归属分散、存在冗余复述** |
| 年度研究计划 | content.md §2.7 | ~2000 | 是 | ⚠️ **用户预警"缺失 plan"与实际不符**：§2.7 含完整 4 年里程碑表 + 核心层/conditional/contingent 三级分层说明，内容齐全，仅归属在 content.md 内 |
| 预期研究成果 | content.md §2.9 + scheme.md §3.6（**两处重复**） | ~3000 + ~2200 | 是 | ⚠️ **内容存在但跨章重复**——§2.9（论文/方法学/数据/人才四维）与 §3.6（可行性角度补充）实质重叠 |
| 参考文献 | references.md | **0** | **否** | ❌ **[critical] 模块完全缺失**——整文件仅"（待 writer 补齐）"占位符 |

**完整性核查结论（红队复核用户预警）**：

1. **参考文献**：经核实确属 [critical] 完全缺失。正文三章节引用了 Iskhakov 2012、Spasibko 2012、Wu/Schafer/Gaarde 2016、Silva 2018、Murakami 2018、Liu 2017、Rasputnyi 2024、Even Tzur/Gorlach 2024、Rivera-Dean 2023、Peschel 2022、Li 2019、Li 2022、Raab 2024、Wu 2024、Boroumand 2025、Hu 2024、Iglesias 2024、Wilkinson 2016、Karniadakis 2019、Borrego-Varillas 等 ≥20 篇文献，但参考文献章空白——NSFC 硬规范红线。
2. **特色与创新 / 年度计划**：**用户预警与实际不符**——两者均有实质内容（均超 200 字阈值）。真正的问题不是"缺失"而是"跨章重复 + 归属分散"：创新点在 §1.4/§2.8/§3.5 三处复述、预期成果在 §2.9/§3.6 两处复述，造成**模块边界模糊与内容冗余**（详见问题清单 #15/#16）。
3. **full_review.md**：本轮聚焦章节文件本身是占位符（3 行），writer 未执行整体一致性审查——这意味着跨章衔接的系统性检查完全依赖 critic 本轮完成。

按用户"缺 2 个及以上不高于 0.3"规则：严格意义上仅 references 属硬缺失（1 个），但创新/预期成果的跨章重复 + full_review 占位 + 三章 cutoff/期刊/QEF 维度等系统性同步失败，实质拉低完整性。完整性维度评为 **0.42**。

---

## 综合评分

**0.62 / 1.00**（按面上项目加权；本轮聚焦整体一致性与跨章衔接）

本轮相对历史轮次的进展与短板：

**进展（writer 在 round-3/round-5 后已实质改善的）**：
- **scheme.md §3.1/§3.2 叙述式改写** ✅（round-3 标记的 2 处 [high] narrative 已大幅修复）：§3.1 不再是编号列表 1-5，改为"光源环节→样品环节→谱学环节→理论环节→反演环节"五段连贯论述，每段含方法选择理由；§3.2 不再是 4 条 bullet，改为"四项关键技术逐一分析可行性依据与风险点"的连贯段落。这是本轮最大的正向变化。
- **Q_F 经典极限物理错误已修复** ✅（round-5 critical）：rationale §1.3 问题 3、content §2.5、scheme §3.5 三处均已统一为"$Q_F \to V_{\rm classical} \approx 1$"，物理正确，三章一致。
- **章节内部矛盾已修复** ✅（round-5 critical）：rationale §1.1/§1.2.1 不再说"经典光 HHG 只探测单粒子"，改为"局限于单粒子与部分多体修正层面，对多体关联/量子涨落灵敏度有限"，与 §1.2.3 自洽。
- **TMDC 分类错误已修复** ✅（round-5 high）：rationale §1.2.3 已明确分三类（弱关联 TMDC / 中等关联莫尔 / 强关联 Mott），不再把 TMDC 列入"强关联"。
- **g(2)(0) 两配置基线已澄清** ✅：rationale §1.2.2 / content §2.1 已明确"非简并 PDC=2、简并 PDC=3+1/N，两类独立实验体系"。
- **"调控"概念已降级为"参数依赖性研究"** ✅：content §2.6 / scheme §3.1 已统一术语澄清。

**短板（本轮跨章深审新发现 / 未解决的残留）**：
1. **rationale §1.2.1 cutoff 律物理计算错误跨 3 轮未修**（[high] 残留）：仍写"3-5 倍带隙 cutoff 律 → 截止能量 30-40 eV，对应 EUV 20-80 eV"，而 3-5×1.6 eV=4.8-8 eV，根本算不出 30-40 eV；content/scheme 已改为正确的"7-13 阶/8-20 eV"——**writer 修了 content+scheme 漏了 rationale**。
2. **综述论文投稿期刊跨章矛盾 + PRL 类别错误未修**（[high] 残留）：scheme §3.4 row 4 仍写"投 Nat. Phys. 或 PRL"，content §2.9 写"Rev Mod Phys/Physics Reports"——PRL 不发表综述。
3. **QEF 指标数量跨章表述不一未修**（[medium] 残留）：rationale"双指标" vs content"两核心+一辅助" vs scheme"三维度"。
4. **Mott 时间点跨章 + scheme 内部矛盾未修**（[medium] 残留）：scheme §3.4"Mott 推迟 Y4" vs scheme §3.3"Y5 拓展" vs content §2.7"Y5 拓展期"。
5. **NOPA/OPA vs PDC 术语漂移未修**（[medium] 残留）。
6. **创新点/预期成果跨章重复复述**（[medium] 新发现）。
7. **参考文献 [critical] 完全缺失 + full_review 占位**。

综合评分在 round-3（0.60，scheme 聚焦）基础上：scheme 叙述改写为正向（+），但 cutoff 错误/综述期刊/QEF 维度等跨章残留是负向（−），且参考文献 [critical] 仍在，给出 **0.62**。

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要短板 |
|---|---:|---:|---:|---|
| 创新性（innovation） | 0.30 | 0.74 | 2 | QEF 三维度/双光路干涉/winding trail 固体拓展有方法学创新；但"首次系统化"差异化论证偏弱（rationale §1.4），创新点在 §1.4/§2.8/§3.5 三处复述稀释聚焦度 |
| 可行性（feasibility） | 0.25 | 0.70 | 3 | scheme §3.3 风险表（7 行 Plan B + 量化触发条件）+ conditional/contingent 三级分层完善；多脉冲平均物理推理是好样板；但 references 缺失使可行性无法独立核实、NOPA/OPA 术语含混、Y4 反馈式升级过载设计倾向仍存 |
| 严谨性（rigor） | 0.25 | 0.58 | 8 | rationale cutoff 律物理计算错误（3-5×1.6≠30-40）跨 3 轮未修；综述期刊 PRL 类别错误；QEF 维度跨章不一；Mott 时间点跨章+内部矛盾；Rivera-Dean/Wu 预印本作核心锚点；2.4"QEF 单调上升"物理未论证 |
| 完整性（completeness） | 0.20 | 0.42 | 4 | 参考文献 [critical] 完全缺失；full_review.md 占位（writer 未做整体审查）；创新点/预期成果跨章重复复述；模块归属分散 |

**加权综合分**：
= 0.30×0.74 + 0.25×0.70 + 0.25×0.58 + 0.20×0.42
= 0.222 + 0.175 + 0.145 + 0.084
= **0.626 ≈ 0.62**

> 说明：scheme 叙述式改写是本轮正向变化，但跨章一致性是本轮核心考核维度，而 cutoff 错误（rationale 漏修）、综述期刊矛盾、QEF 维度不一三项 [high/medium] 跨章残留直接拉低严谨性；参考文献 [critical] 缺失 + full_review 占位 + 模块重复拉低完整性。

---

## 一、整体一致性段落级深审（聚焦章节 + 跨章衔接）

> **评审原则**：full_review.md 为占位符，故本轮以"跨章节一致性"为核心，构建 16 对章节衔接检查矩阵，逐对核查连贯性、术语统一、数值自洽、逻辑递进。每对给出 ✅一致 / ⚠️需修订 / ❌矛盾 + 精确定位。

### 1.1 跨章节一致性矩阵（16 对）

| # | 检查对（章节↔章节） | 一致性项 | 结论 | 证据定位 |
|---|---|---|---|---|
| 1 | rationale §1.2.1 ↔ content §2.2 ↔ scheme §3.1 | HHG 截止能量数值 | ❌ **二对一错**：rationale 仍"3-5×带隙→30-40 eV/EUV 20-80 eV"（错），content/scheme 已"7-13 阶/8-20 eV"（对） | rationale L19 vs content L32 vs scheme L11 |
| 2 | scheme §3.4 row4 ↔ content §2.9 | 综述论文投稿期刊 | ❌ **跨章矛盾 + PRL 类别错误**：scheme"投 Nat. Phys. 或 PRL"，content"Rev Mod Phys/Physics Reports"；PRL 不发表综述 | scheme L54 vs content L99 |
| 3 | rationale §1.4 ↔ content §2.4 ↔ scheme §3.1 | QEF 指标数量 | ⚠️ **三处表述不一**：rationale"双指标"，content"两核心+一辅助"，scheme"三维度" | rationale L59 vs content L48 vs scheme L15 |
| 4 | scheme §3.4 ↔ scheme §3.3 ↔ content §2.7 | Mott/低温实验推迟时点 | ❌ **scheme 内部矛盾 + 跨章不一**：scheme §3.4"Mott 推迟 Y4"，§3.3"Y5 拓展"，content"Y5 拓展期" | scheme L53/L40 vs content L81 |
| 5 | rationale §1.3 ↔ content §2.5 ↔ scheme §3.5 | Q_F 经典极限回归 | ✅ **一致且物理正确**（round-5 critical 已修） | rationale L49 vs content L60 vs scheme L67 |
| 6 | rationale §1.2.3 ↔ content §2.4 ↔ scheme §3.1 | TMDC/莫尔/Mott 三类关联体系分类 | ✅ **一致**（round-5 high 已修，三章统一分弱/中/强三类） | rationale L35 vs content L46 vs scheme L9 |
| 7 | rationale §1.2.2 ↔ content §2.1 ↔ scheme §3.1 | BSV 光源产生机制术语 | ⚠️ **术语漂移**：rationale/content"高增益 PDC"，scheme"NOPA/OPA 后置于非线性晶体" | rationale L23 vs content L22 vs scheme L7 |
| 8 | rationale §1.2.2 ↔ content §2.1 ↔ scheme §3.3 | g(2)(0) 两配置基线 | ⚠️ **部分不同步**：rationale/content 已明确"非简并=2/简并=3+1/N"，scheme §3.3 row1 仍用模糊"Iskhakov 2012 基线" | scheme L35 |
| 9 | rationale §1.2.2 ↔ content §2.3 ↔ scheme §3.1 | Even Tzur 2024 不可直接移植性 | ✅ **一致**（三章统一"需引入晶体动量/Berry 相位/激子/强关联修正"） | rationale L31 vs content L38 vs scheme L13 |
| 10 | rationale §1.4 ↔ content §2.8 ↔ scheme §3.5 | 创新点论述 | ⚠️ **跨章重复复述**：创新点在 §1.4/§2.8/§3.5 三处出现，内容重叠度高，稀释聚焦 | rationale L55-61 vs content L87-93 vs scheme L61-67 |
| 11 | content §2.9 ↔ scheme §3.6 | 预期研究成果 | ⚠️ **跨章重复**：§2.9（四维完整论述）与 §3.6（可行性角度补充）实质重叠 | content L97-105 vs scheme L69-77 |
| 12 | rationale §1.3 ↔ content §2.6 | "调控"vs"参数依赖性研究" | ✅ **一致**（content §2.6 已澄清术语，rationale §1.3 问题4已降级为"参数依赖性研究"） | rationale L51 vs content L66 |
| 13 | content §2.0 ↔ scheme §3.1 | 六子方向↔五段式路线对应 | ✅ **一致**（content 六子方向串联闭环，scheme 五段式与之一一对应，术语约定一致） | content L7-18 vs scheme L5 |
| 14 | content §2.7 ↔ scheme §3.4 | 年度里程碑↔关键交付节点 | ✅ **基本一致**（核心/conditional/contingent 三级分层对齐） | content L76-83 vs scheme L49-55 |
| 15 | rationale §1.1 ↔ content §2.0 | 探针操作性定义 | ✅ **一致**（§1.1 定义，§2.0 引用不重复定义） | rationale L9 vs content L18 |
| 16 | content §2.4 ↔ scheme §3.3 | No-Go 降级判据 | ✅ **一致**（QEF 不单调/反演偏离>2σ 两处表述统一） | content L50 vs scheme L39 |

**跨章节一致性结论**：16 对检查中，**7 对 ✅ 一致、4 对 ⚠️ 需修订、5 对 ❌ 矛盾**。

最突出的硬伤集中在 3 项：
- **#1 cutoff 律"二对一错"**（rationale 错、content/scheme 对）——物理计算错误跨 3 轮未同步；
- **#2 综述期刊矛盾 + PRL 类别错误**——评审专家会直接用红笔圈出；
- **#4 Mott 时间点 scheme 内部 Y4/Y5 自相矛盾**——同一文件内打架。

这 3 项的共同特征是"writer 修复时只改了部分章节、未做全文同步扫描"——这正是整体一致性审查要抓的系统性同步失败。

### 1.2 段落级衔接连贯性深审（叙述弧线 / 过渡 / 逻辑递进）

按 `writing_style_rules.must`"段落之间形成逻辑递进""研究内容要围绕核心问题组织，突出内在逻辑而非平行堆砌"，逐章核查衔接：

**rationale.md（立项依据）——叙事弧线评估**：
- §1.1→§1.2→§1.2.3→§1.3→§1.4 的"引子→背景→矛盾→科学问题→创新"弧线**完整且递进**，§1.2.3 三个缺口（机制/材料/框架）与 §1.3 四个科学问题、§1.4 三个创新点有明确对应映射（§1.3 段首明确写出"§1.2.3 识别的机制空白对应问题1…"）——✅ 逻辑递进良好。
- 但 §1.2.1 段1（经典光 HHG 三类能力）与 §1.2.3 段1（物理层两层局限）之间存在**信息重复**：§1.2.1 已详述"Berry 曲率/能谷/cutoff 律三类能力"，§1.2.3 又复述"机制空白+材料空白"——两节对"经典光 HHG 能做什么/不能做什么"的论述有 30% 重叠，建议 §1.2.3 删减复述、直接切入"本项目切入点"。

**content.md（研究内容）——内在逻辑评估**：
- §2.0 总览→§2.1-§2.6 六子方向→§2.7-§2.9 的组织**清晰且串联**，§2.0 表格给出"子方向↔核心交付↔风险"对应，六子方向按"光源→实验→理论→探针→干涉→参数依赖"递进——✅ 不是平行堆砌。
- 但 §2.8（特色与创新）与 §1.4（创新性）**实质重复**：§2.8 三个创新点（系统化/探针化/量子化）与 §1.4 三个创新点几乎逐条对应，仅措辞略变。按 NSFC 三段式（立项依据+研究内容+研究方案），创新点应在 §1.4 集中论述、§2.8 仅做"研究内容层面的特色"差异化补充——目前两节重叠度过高（~70%），稀释聚焦。

**scheme.md（研究方案）——改写后评估**：
- **§3.1 已从编号列表改为连贯叙述** ✅（round-3 [high] narrative 已修）：五段（光源/样品/谱学/理论/反演）每段含"方法选择理由→关键难点→与科学问题对应"，其中"BSV 单脉冲 g(2)>>1 信噪比差→需 10⁴-10⁵ 脉冲统计平均"的物理推理是好样板。
- **§3.2 已从 bullet 改为连贯段落** ✅（round-3 [high] narrative 已修）：四项关键技术按"技术成熟度→本项目增量→关键难点→突破路径"展开。
- 但 §3.5（方法学创新）/§3.6（预期成果）与 §2.8/§2.9 重复（见检查对 #10/#11）。

**references.md**：占位符，无内容可评。

**full_review.md**：占位符，writer 未产出整体审查——这意味着申请书目前**没有任何一份文档系统性地检查过跨章一致性**，本轮 critic 报告是首份整体一致性审查。

---

## 二、写作风格红线集中审查（叙述式 vs 堆砌式）

按 `writing_style_rules.forbidden`（文献堆砌/条目式罗列/概念清单/PPT 化）与 `must`（连贯叙述/逻辑递进/方法选择论证），逐章核查：

| 章节 | 违规类型 | 严重度 | 状态 |
|---|---|---|---|
| rationale §1.2.1 | 段1"三类已成熟能力"以分号并列展开（Berry 曲率/能谷/cutoff 律），偏概念清单式，但每条有物理限定语，勉强可接受 | [low] | 残留 |
| rationale §1.2.2 | 段4 Rasputnyi/Even Tzur 引证较连贯，无堆砌 | — | ✅ |
| content §2.0 | 表格（子方向↔交付↔风险）可接受，但表格前后的叙述导引充分 | — | ✅ |
| content §2.4 | 三类对照体系以"第一类/第二类/第三类"展开，但每类有物理依据论证，非平行堆砌 | — | ✅ |
| scheme §3.1 | **round-3 [high] narrative 已修**：编号列表→连贯五段叙述 | — | ✅ 已修 |
| scheme §3.2 | **round-3 [high] narrative 已修**：bullet→连贯段落 | — | ✅ 已修 |
| scheme §3.3 | 风险表（表格形式可接受）+ 已有叙述导引句（round-3 [medium] 已补） | — | ✅ 已修 |
| scheme §3.4 | 交付表（表格形式可接受）+ 已有叙述导引 | — | ✅ |

**写作风格红线结论**：相比 round-3（scheme §3.1/§3.2 两处 [high] narrative），**本轮写作风格显著改善**——scheme 两处编号/bullet 已改写为连贯论述。残留仅 rationale §1.2.1 段1 的轻度概念清单倾向（[low]）。**这是 writer 在叙述式写作上最实质的进步，应予肯定。**

但需注意：写作风格的改善不等于内容一致性的达标——scheme 改写后引入的新表述（如"7-13 阶/8-20 eV"）未回灌 rationale，反而制造了新的跨章不一致。

---

## 三、修复确认表（round-3 / round-5 → round-4 本轮）

### 3.1 已修复（writer 实质采纳）

| # | 问题 | 来源轮次 | 本轮核查 | 证据 |
|---|---|---|---|---|
| 1 | scheme §3.1 编号列表替代方法学论证 | round-3 [high] | ✅ **已修**：改为五段连贯叙述 | scheme L5-15 |
| 2 | scheme §3.2 bullet 罗列可行性论断 | round-3 [high] | ✅ **已修**：改为连贯段落 | scheme L19-27 |
| 3 | Q_F 经典极限 → 0 物理错误 | round-5 [critical] | ✅ **已修**：三章统一为 → V_classical ≈ 1 | rationale L49 / content L60 / scheme L67 |
| 4 | 章节内部矛盾（经典光 HHG 多体探测能力） | round-5 [critical] | ✅ **已修**：rationale 统一为"单粒子与部分多体修正层面，对量子关联/涨落灵敏度有限" | rationale L5/L19 |
| 5 | TMDC 列入"强关联材料"分类错误 | round-5 [high] | ✅ **已修**：分弱/中/强三类 | rationale L35 |
| 6 | "调控"概念物理边界不清 | round-5 [high] | ✅ **已修**：降级为"参数依赖性研究" | content L66 / rationale L51 |
| 7 | scheme §3.3/§3.4 表格缺叙述导引 | round-3 [medium] | ✅ **已修** | scheme L31/L47 |
| 8 | scheme 标题虚假承诺（声称含特色创新+预期成果） | round-3 [high] | ⚠️ **部分修**：scheme 现含 §3.5/§3.6，标题与内容基本对应，但与 content §2.8/§2.9 形成跨章重复 | scheme L1 |

### 3.2 未解决 / 跨章未同步（残留）

| # | 问题 | 来源轮次 | 本轮状态 | 证据 |
|---|---|---|---|---|
| R1 | cutoff 律数值错误（3-5×1.6≠30-40 eV） | round-3 [high] | ❌ **rationale 仍未修**（content/scheme 已修） | rationale L19 |
| R2 | 综述论文投稿期刊跨章矛盾 + PRL 类别错误 | round-3 [high] | ❌ **scheme §3.4 仍未修** | scheme L54 vs content L99 |
| R3 | QEF 指标数量跨章不一（双/两核心一辅助/三维） | round-3 [medium] | ❌ **三处仍不一** | rationale L59 / content L48 / scheme L15 |
| R4 | Mott 时间点 scheme 内部 Y4/Y5 矛盾 | round-3 [medium] | ❌ **仍未修** | scheme L53/L40 |
| R5 | NOPA/OPA vs PDC 术语漂移 | round-3 [medium] | ❌ **scheme §3.1 仍未修** | scheme L7 |
| R6 | g(2)(0) 触发条件未指明配置基线 | round-3 [medium] | ❌ **scheme §3.3 仍未修** | scheme L35 |
| R7 | 参考文献 [critical] 完全缺失 | round-3 [critical] | ❌ **仍为占位符** | references.md |
| R8 | Rivera-Dean 2023 / Wu 2024 预印本作核心锚点 | round-3 [medium] | ❌ **仍未核实/限定** | 多处 |

---

## 四、物理领域专项检查（physics-domain-checks.md 8 项）

| 检查项 | 命中位置 | 状态 |
|---|---|---|
| 1. BSV 增强与反演精度是否被等同 | rationale §1.2.2 已拆分"光源层/观测层/反演层"，明确"不预设产额增益→反演精度增益" | ✅ 通过 |
| 2. Berry 曲率/量子度规可独立辨识性 | rationale §1.1 已加限定"带间/带内贡献需在双色场微扰一阶近似下分通道解读" | ✅ 通过 |
| 3. CDW/Mott/拓扑分类是否混用 | 三章统一分弱关联TMDC/中等关联莫尔/强关联Mott三类 | ✅ 通过（round-5 已修） |
| 4. Q1/Q2 是否真正可证伪 | 四个科学问题均有量化指标 + No-Go 降级判据 | ✅ 通过 |
| 5. 双色场 sin/cos 强假设是否论证 | scheme §3.3 row5 单束双色 ω+2ω 仅作 Plan B | ✅ 通过 |
| 6. 预印本引文占比 | Rivera-Dean 2023（核心锚点）、Wu 2024、Rasputnyi 2024、Boroumand 2025、Iglesias 2024 仍 arXiv；正式发表：Iskhakov/Spasibko/Even Tzur/Peschel/Liu/Silva/Murakami/Raab/Li×2/Hu | ⚠️ 5/≥20≈25%，Rivera-Dean 作核心锚点需核实 |
| 7. 驱动波长与材料带隙匹配 | 0.8-1.5 μm 与 TMDC 1.5-2 eV 匹配正确；但 rationale cutoff 计算错 | ⚠️ 匹配对、cutoff 错 |
| 8. 关键预印本核实 | Rivera-Dean 2023（Bloch 锚点）、Wu 2024（莫尔室温）、Rasputnyi 2024（首例实验） | ⚠️ 需核实正式发表状态 |

**物理专项结论**：8 项中 5 项 ✅、3 项 ⚠️。BSV-精度拆分（#1）、Berry 辨识限定（#2）、材料分类（#3）、可证伪性（#4）、双色场假设（##5）均处理正确——这些是 round-5 后的实质改善。主要短板是预印本依赖（#6/#8）与 rationale cutoff 计算（#7）。

---

## 五、问题清单（按严重度分级）

### Critical（必须立即修复）

**1. [critical] completeness — 参考文献完全缺失**
- 位置：references.md 全文（仅"（待 writer 补齐）"占位符，0 字符）
- 问题：正文三章节引用 Iskhakov 2012、Spasibko 2012、Wu/Schafer/Gaarde 2016、Silva 2018、Murakami 2018、Liu 2017、Rasputnyi 2024、Even Tzur/Gorlach 2024、Rivera-Dean 2023、Peschel 2022、Li 2019、Li 2022、Raab 2024、Wu 2024、Boroumand 2025、Hu 2024、Iglesias 2024、Wilkinson 2016、Karniadakis 2019、Borrego-Varillas 等 ≥20 篇文献，但参考文献章空白。NSFC 硬规范红线，评审专家会直接判定"不完整"。
- 建议：将正文全部引用整理为完整参考文献列表（作者/期刊/卷/页码/年/DOI/arXiv），按出现顺序编号。预印本标注"preprint"。
- action：add

### High（必须修复）

**2. [high] rigor — rationale §1.2.1 cutoff 律物理计算错误，跨 3 轮未同步**
- 位置：rationale.md L19"3-5 倍带隙 cutoff 律 → 截止能量 30-40 eV，对应 EUV 谱段 20-80 eV"
- 问题：MoS₂ 带隙 ~1.6 eV，3-5 倍 = 4.8-8 eV，**根本算不出 30-40 eV**。content §2.2（L32）与 scheme §3.1（L11）均已改为物理正确的"7-13 阶奇次谐波/8-20 eV（VUV-EUV 低能端）"，**唯独 rationale §1.2.1 仍是错误旧表述**——writer 修了 content+scheme 漏了 rationale，形成"二对一错"。这是物理计算错误 + 跨章不一致的双重硬伤。
- 建议：rationale §1.2.1 统一为"多 plateau 截止能量可由 Wu/Schafer/Gaarde 多能级量子模型定量预测（对于带隙约 1.6 eV 的单层 MoS₂，近红外驱动下实验可观测的奇次谐波延伸至 7-13 阶，约 8-20 eV，VUV-EUV 低能端）"，删除"3-5 倍带隙→30-40 eV"与"EUV 20-80 eV"两处错误数值。
- action：recalculate + rewrite

**3. [high] cross-chapter — 综述论文投稿期刊跨章矛盾 + PRL 类别错误**
- 位置：scheme.md L54"探针方法学综述论文（投 Nat. Phys. 或 PRL）" vs content.md L99"拟投 Reviews of Modern Physics / Physics Reports 或受邀综述"
- 问题：两处对同一篇综述论文的投稿期刊直接矛盾。更严重的是 **PRL 不发表综述论文**（PRL 仅 Letter），scheme 写"投 PRL 综述"是期刊类别错误；Nat. Phys. 的 Review/N&V 体例也不适配完整方法学综述。content §2.9 的 Rev Mod Phys/Physics Reports 才是综述正途。
- 建议：scheme §3.4 row4 统一为"探针方法学综述论文（拟投 Reviews of Modern Physics / Physics Reports 或受邀综述）"，删除"PRL"。
- action：rewrite

**4. [high] completeness — full_review.md 为占位符，writer 未执行整体一致性审查**
- 位置：full_review.md 全文（3 行"待本轮 writer-critic 循环结束后统一审查"）
- 问题：整体一致性审查章节是申请书交付的必要组成部分，writer 将其留空意味着申请书目前没有任何一份文档系统性检查过跨章衔接。本轮 critic 报告（本文件）是首份整体一致性审查，但 writer 应自行产出 full_review 作为申请书自洽性证明。
- 建议：writer 应在 full_review.md 产出实质性整体一致性自审文档，至少包含：(a) 跨章术语统一矩阵；(b) 关键数值（cutoff/QEF/g(2)/Mott 时间点）三章对照表；(c) 章节衔接逻辑图。不应依赖 critic 代劳。
- action：add

### Medium（应当修复）

**5. [medium] cross-chapter — QEF 指标数量跨章表述不一**
- 位置：rationale §1.4 L59"双指标" vs content §2.4 L48"两个核心指标+一个辅助验证指标=三维" vs scheme §3.1 L15/scheme §3.5 L65"三维度"
- 问题：同一 QEF 指标体系在三章用"双/两核心一辅助/三维"三种表述。物理上 content 的"两核心（QEF_vis + QEF_yield^(q_ref)）+ 一辅助（QEF_yield^(Σ)）"最准确，应全文统一。
- 建议：三章统一为"QEF 由两个核心指标（QEF_vis、QEF_yield^(q_ref)）与一个辅助验证指标（QEF_yield^(Σ)）构成"，删除 rationale"双指标"与 scheme 裸"三维度"。
- action：rewrite

**6. [medium] rigor — Mott 时间点 scheme 内部矛盾 + 跨章不一**
- 位置：scheme §3.4 L53"第三体系（Mott）可推迟至 Y4" vs scheme §3.3 L40"低温实验推迟至 Y5 拓展" vs content §2.7 L81"Y4 conditional…推迟至 Y5 拓展期"
- 问题：scheme §3.4 说 Mott 推迟至 Y4，但 scheme §3.3 与 content §2.7 都说 Y5——scheme 内部自相矛盾，且与 content 不一致。
- 建议：scheme §3.4 row1 改为"第三体系（Mott）可推迟至 Y5 拓展期（与 §3.3 row6、content §2.7 一致）"。
- action：rewrite

**7. [medium] rigor — NOPA/OPA vs PDC 术语漂移**
- 位置：scheme §3.1 L7"基于 NOPA/OPA 后置于非线性晶体（β-BBO 或 PPKTP）产生高增益参量下转换（PDC）" vs rationale §1.2.2/content §2.1"高增益参量下转换（PDC）"
- 问题：NOPA/OPA 本身即非线性晶体中的参量过程，"后置于非线性晶体"语义不清（后置于什么？）。rationale/content 统一用"高增益 PDC"，scheme 用"NOPA/OPA 后置"——术语漂移。
- 建议：scheme §3.1 改为"基于高增益参量下转换（PDC）在非线性晶体（β-BBO 或 PPKTP）中产生 BSV（参照 Iskhakov 2012、Spasibko 2012）"，与 rationale/content 术语统一。
- action：rewrite

**8. [medium] cross-chapter — g(2)(0) 触发条件未指明配置基线**
- 位置：scheme §3.3 L35"g(2)(0) 偏离 Iskhakov 2012 基线 > 30%"
- 问题：rationale/content 已澄清 g(2)(0) 在非简并 PDC=2、简并 PDC=3+1/N 是两个独立单值，scheme §3.3 仍用模糊"Iskhakov 2012 基线"，评审专家无法判断 30% 偏离相对哪个值。
- 建议：改为"g(2)(0) 偏离对应配置基线（非简并 PDC 的 2 或简并 PDC 的 3+1/N）> 30%"。
- action：rewrite

**9. [medium] narrative — 创新点跨章重复复述（§1.4/§2.8/§3.5）**
- 位置：rationale §1.4 L55-61 / content §2.8 L87-93 / scheme §3.5 L61-67
- 问题：三个创新点（系统化/探针化/量子化）在三章重复论述，重叠度 ~70%。按 NSFC 三段式，创新点应集中于立项依据 §1.4，研究内容 §2.8 仅做"研究内容层面的特色"差异化补充，研究方案 §3.5 仅做"技术方案体现"——目前三节近乎逐条复述，稀释聚焦、增加冗余。
- 建议：§2.8 改为"承接 §1.4 三个创新点，本节从研究内容组织角度说明其落地路径"（删减复述、突出与 §1.4 的差异）；§3.5 已较好地定位为"从技术方案与可行性角度补充"，可保留但应进一步与 §1.4/§2.8 去重。
- action：rewrite

**10. [medium] narrative — 预期研究成果跨章重复（§2.9/§3.6）**
- 位置：content §2.9 L97-105 / scheme §3.6 L69-77
- 问题：§2.9（论文/方法学/数据/人才四维完整论述）与 §3.6（"从可执行性角度补充"）实质重叠，§3.6 重复列举论文目标、方法学产出、降级机制。
- 建议：§3.6 应严格限定为"可行性保障与风险边界"，删除与 §2.9 重复的成果类型列举，仅保留"成果承诺的降级机制"与"技术可行性保障"两类 §2.9 未覆盖内容。
- action：rewrite

**11. [medium] rigor — Rivera-Dean 2023 / Wu 2024 预印本作核心锚点未核实**
- 位置：Rivera-Dean 2023 [arXiv:2309.14435]（scheme §3.1/§3.2、content §2.3 三处作"Bloch 形式化方法学锚点"）；Wu 2024 [arXiv:2311.16655]（scheme §3.1、content §2.4 作"莫尔超晶格室温可工作"关键论断）
- 问题：核心理论支柱与关键实验论断依赖未正式发表工作。按 physics-domain-checks #6，核心论断依赖预印本需显著降权或核实。
- 建议：联网核实是否已正式发表；若已发表补全期刊卷期；若仍预印本，加"预印本"限定语。
- action：verify

**12. [medium] rigor — 2.4 节"QEF 三体系单调上升"物理未充分论证**
- 位置：content §2.4（meta-review-5 遗漏 β）；rationale §1.3 问题2 No-Go 判据已部分缓解（content §2.4 已改为"不预设单调上升、如实报告"）
- 问题：content §2.4 已从"预期单调上升"改为"既不预设单调上升、如实报告效应量与95%CI"——✅ 这一表述已较严谨。但 No-Go 判据仍隐含"若不单调则降级"，而 Mott gap 可能导致强关联体系 HHG 信号本身微弱（scheme §3.3 row4 已识别此风险），"单调性"作为判据的物理前提需要更强论证。
- 建议：在 §2.4 补一句"Mott 体系 HHG 信号强度本身可能因 Mott gap 而受限，故单调性检验以效应量+置信区间报告为主，不作为唯一判据"。
- action：add

**13. [medium] narrative — scheme §3.3/§3.4 表格叙述导引已补但偏简**
- 位置：scheme §3.3 L31 / §3.4 L47
- 问题：round-3 标记的"表格缺叙述导引"已部分修复（§3.3 有风险分级逻辑句、§3.4 有分工说明句），但导引仍偏简，未说明"核心交付聚焦 Y3 末"的优先级逻辑。
- 建议：§3.4 表格前补一句"核心交付聚焦 Y3 末 QEF 三维度 + Q_F 全景图；Mott 与反馈式升级为 conditional/contingent，不纳入核心验收"。
- action：add

### Low（建议修复）

**14. [low] narrative — rationale §1.2.1 段1"三类能力"分号并列偏概念清单**
- 位置：rationale §1.2.1 L19
- 问题：段1以"在…方面…；在…方面…；在…方面…"分号并列展开三类能力，偏概念清单式（每条虽有物理限定语，勉强可接受）。
- 建议：可保留，或改写为"固体 HHG 的探测能力沿三条主线成熟：首先是…进而…最后…"的递进叙述。
- action：rewrite

**15. [low] rigor — 两篇"Li et al."引文跨章均称"Li 等"，易混淆**
- 位置：Li 2019 [PRL 123, 153201] / Li 2022 [PRL 129, 173001]
- 问题：两篇 Li 引文跨章均称"Li 等"，读者需查上下文区分。
- 建议：加首字母或主题区分（如"Li 等 2019（HHG 时域干涉反演）"与"Li 等 2022（量子干涉可见度）"）。
- action：rewrite

**16. [low] expression — 章节交叉引用格式混用**
- 位置：全文
- 问题：混用"2.5 节""3.3""§2.0""1.2.3"，全书不统一。
- 建议：统一为"§X.X"格式。
- action：rewrite

**17. [low] rigor — 2.6 Y4 反馈式升级过载设计倾向**
- 位置：content §2.6 L70 / scheme §3.3 row7
- 问题：meta-review-5 遗漏 α。Y4 反馈式升级涉及反馈延迟<50 mrad + SLM 实时写入 + 反馈环稳定性（g(2)>>1 × 延迟）+ 9T 磁体采购（已 conditional）——4 项叠加，在 4 年面上项目上倾向过载（contingent on contingent）。content §2.6 已明确"Y4 后段并非必须项、Y3 末数据饱和则取消"，缓解了风险，但表述上仍给人"项目承诺过满"印象。
- 建议：在 §2.6 / §3.4 进一步强调"反馈式升级为纯可选项，不纳入核心交付验收，不影响项目结题"。
- action：rewrite

---

## 六、对抗结论

- **本轮发现 17 个独立问题**（critical: 1，high: 3，medium: 9，low: 4）。
- **模块完整性**：经逐文件核查，**参考文献确属 [critical] 完全缺失**（用户预警正确）；但**用户预警"缺失 innovation / plan"与实际不符**——特色与创新（§1.4/§2.8/§3.5）、年度计划（§2.7）均有实质内容，真正问题是"跨章重复复述 + 归属分散"而非缺失。full_review.md 为占位符，writer 未执行整体审查。
- **整体一致性深审**：16 对章节检查中 7 对 ✅ 一致、4 对 ⚠️ 需修订、5 对 ❌ 矛盾。最突出的系统性问题是 **"writer 修复时只改部分章节、未做全文同步扫描"**——cutoff 错误修了 content+scheme 漏 rationale、综述期刊矛盾修了 content 漏 scheme，这正是整体一致性审查要抓的同步失败。

- **相比上一轮**（round-3 聚焦 scheme，0.60，19 问题；round-5 聚焦 rationale，0.71，meta 0.68）：
  - **改善 8 项**（实质性）：scheme §3.1/§3.2 两处 [high] narrative 已改写为连贯叙述；Q_F 经典极限物理错误（round-5 critical）三章已统一修复；章节内部矛盾（round-5 critical）已修复；TMDC 分类（round-5 high）已修；"调控"术语（round-5 high）已降级；表格叙述导引已补。**writer 在 round-3/round-5 后做了实质修订，应予肯定。**
  - **未解决/跨章未同步 8 项**（R1-R8）：cutoff 错误（rationale 漏修）、综述期刊（scheme 漏修）、QEF 维度、Mott 时间点、NOPA/OPA 术语、g(2) 基线、参考文献缺失、预印本核实——**这 8 项的共同特征是"局部修复未配套全文同步"**。
  - **新增 3 项**：创新点跨章重复（#9）、预期成果跨章重复（#10）、full_review 占位（#4）——均为整体一致性视角下新发现的结构性问题。

- **是否达到输出标准**：**否**。
  - 综合评分 0.62 < 0.80 门槛；
  - critical 1 个 > 0（参考文献缺失）；
  - high 3 个 >> max_high_issues 0；
  - medium 9 个 >> max_medium_issues 3；
  - 四个指标全部不达标。

- **返工优先级**：
  - **P0（critical）**：
    1. 补齐参考文献章——将正文 ≥20 篇引用整理为完整列表。
  - **P1（high）**：
    2. **全文同步 cutoff 律**：rationale §1.2.1 统一为"7-13 阶/8-20 eV"，删除"3-5×带隙→30-40 eV"与"EUV 20-80 eV"；
    3. **全文同步综述期刊**：scheme §3.4 row4 改为"Rev Mod Phys/Physics Reports"，删除 PRL；
    4. **writer 产出 full_review.md**：实质性整体一致性自审（术语矩阵 + 数值对照 + 衔接逻辑图）。
  - **P2（medium）**：
    5. 同步 QEF 维度数、Mott 时间点、NOPA/OPA→PDC 术语、g(2) 基线 4 处；
    6. 去重创新点（§1.4/§2.8/§3.5）与预期成果（§2.9/§3.6）；
    7. 核实 Rivera-Dean 2023 / Wu 2024 预印本发表状态。

- **下一轮评审建议聚焦**：
  1. **先补参考文献 + 全文同步 cutoff/综述期刊**——一个是 critical 硬规范，两个是物理/类别错误且跨章联动；
  2. **再做全文术语/数值同步扫描**——建议 writer 在修订后跑一次"全文搜索关键术语（cutoff/QEF/Mott/NOPA/g(2)/综述期刊）+ 三章对照表"的自检流程，避免再次"修两章漏一章"；
  3. **然后去重创新点/预期成果**——明确 §1.4（科学）/§2.8（内容）/§3.5（技术）的差异化分工；
  4. **最后核实预印本**。

---

## 评分
创新性：0.74
可行性：0.70
严谨性：0.58
完整性：0.42
综合评分：0.62
