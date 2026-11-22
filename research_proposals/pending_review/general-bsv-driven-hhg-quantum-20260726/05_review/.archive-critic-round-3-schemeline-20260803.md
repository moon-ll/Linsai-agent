# 对抗评审报告（第 3 轮 · 研究方案聚焦）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文≤30 页） |
| 本轮聚焦 | （三）研究方案、特色与创新、预期研究成果——技术路线/可行性/创新点/预期成果，段落级深审 |
| 用户指定文件 | `04_proposal/sections/scheme.md`（48 行，约 7980 字符；§3.1–§3.4） |
| 跨章节简查 | rationale.md（§1.1–§1.4）、content.md（§2.0–§2.9）、references.md |
| 质量标准 | `memory/nsfc-standards.json` → `project_types.general`（min_overall=0.80；max_high=0；max_medium=3）+ `general_principles.writing_style_rules` |
| 评审日期 | 2026-08-03 |
| profile | critic |
| 历史脉络 | round-1（全文骨架）→ round-2（研究内容 content.md，给分 0.62，26 问题）→ 历史整体一致性轮（给分 0.63）→ 本轮聚焦 scheme.md |

> **本轮定位**：scheme.md 是项目"怎么做"的核心章节。按 `writing_style_rules.must`，"研究方案要讲清楚'为什么选这个方法、如何解决关键难点'，而不是罗列实验步骤"。本轮深审发现：**scheme.md §3.1/§3.2 仍以编号/项目符号列表为主要呈现形式，缺"为什么选这个方法"的方法学论证**；更严重的是 **cutoff 律数值在三章节间出现"二错一对"的不一致**（scheme + rationale 用错误的"3-5×带隙=30-40 eV"，content 已改为正确的"7-13 阶/8-20 eV"），以及**综述论文投稿期刊跨章矛盾**（scheme 写"Nat Phys/PRL"，content 写"Rev Mod Phys/Physics Reports"，而 PRL 根本不发表综述）。

---

## 0. 模块完整性检查（7 个标准模块）

按本轮用户指令核查 7 个标准模块（立项依据/研究内容/研究方案/特色与创新/年度研究计划/预期研究成果/参考文献）。**用户预警缺失 innovation / plan / 参考文献**——逐文件核查结果如下：

| 标准模块 | 定位 | 字符数（约） | 是否 ≥200 字且有实质内容 | 结论 |
|---|---|---:|---|---|
| 立项依据 | rationale.md（§1.1–§1.4） | 1838 | 是 | ✅ 完整 |
| 研究内容 | content.md（§2.0–§2.6） | ~2400 | 是 | ✅ 完整 |
| 研究方案 | scheme.md（§3.1–§3.4） | 1580 | 是 | ✅ 完整 |
| 特色与创新 | content.md §2.8（**非独立模块**） | ~520 | 是 | ⚠️ **内容存在但归属错位**——scheme.md 标题声称含"特色与创新"却未在该文件交付，实际位于 content.md |
| 年度研究计划 | content.md §2.7（**非独立模块**） | ~600 | 是 | ⚠️ **内容存在但归属错位**——同上，实际位于 content.md |
| 预期研究成果 | content.md §2.9（**非独立模块**） | ~720 | 是 | ⚠️ **内容存在但归属错位**——scheme.md 标题声称含"预期研究成果"却未交付，实际位于 content.md |
| 参考文献 | references.md | **0** | **否** | ❌ **[critical] 模块完全缺失**——整文件仅"（待 writer 补齐）"占位符 |

**完整性核查结论（红队复核用户预警）**：
- **参考文献**：经核实确属 [critical] 完全缺失，正文（rationale + content + scheme）引用了 Iskhakov 2012、Spasibko 2012、Wu/Schafer/Gaarde 2016、Silva 2018、Murakami 2018、Liu 2017、Rasputnyi 2024、Even Tzur/Gorlach 2024、Rivera-Dean 2023、Peschel 2022、Li 2019、Li 2022、Raab 2024、Wu 2024、Boroumand 2025、Hu 2024、Iglesias、Wilkinson 2016、Karniadakis 2019、Borrego-Varillas 等 ≥20 篇文献，但参考文献章空白——NSFC 硬规范红线。
- **特色与创新 / 年度计划 / 预期成果**：**经核实内容并非完全缺失**——三者均有实质内容且分别位于 content.md §2.7/§2.8/§2.9（特色与创新约 520 字符、年度计划约 600 字符、预期成果约 720 字符，均超 200 字阈值）。**真正的问题是"归属错位 + 标题虚假承诺"**：scheme.md 章节标题为"（三）研究方案、特色与创新、预期研究成果"，但正文仅交付研究方案（§3.1–§3.4），特色与创新/预期成果实际位于 content.md——**标题与内容错位造成评审专家"翻开第三章找不到特色创新与预期成果"的结构性混乱**。按用户"缺 2 个及以上不高于 0.3"的完整性扣分规则，结合 references [critical] 硬缺失 + 三个模块归属错位（非独立成节、标题虚假承诺），完整性维度评为 **0.35**。

---

## 综合评分

**0.60 / 1.00**（按面上项目加权；本轮聚焦研究方案段落级深审，其他章节做一致性回扫）

面上项目核心要求"创新性 + 扎实基础、小切口深挖掘"。scheme.md 相对早期版本的进展：
- §3.3 风险评估表（7 行）结构完整，每环节给出主要风险/触发条件/Plan B/升级判定/缺口对应——**这是本章最好的部分**，体现成熟的项目管理与科研诚信；
- §3.1 item 3 内嵌"BSV 单脉冲 g(2)>>1 信噪比差 → 需 10⁴–10⁵ 脉冲统计平均"的物理推理，是难得的"为什么选这个方法"论证片段；
- §3.3/§3.4 给出可量化验收指标（QEF 三维度、Q_F 全景图、RSD<10%、系统偏差<5% 等），交付标准清晰。

但本轮深审发现以下严重问题：
1. **写作风格红线**：§3.1（编号列表 1-5）、§3.2（4 条 bullet）以条目式罗列替代方法学论证，违反 `writing_style_rules.forbidden`"条目式罗列替代论证"与 `must`"研究方案要说明'为什么选这个方法'"——2 处 [high] narrative。
2. **cutoff 律"二错一对"跨章不一致**：scheme §3.1 与 rationale §1.2.1 都用"3-5 倍带隙 cutoff 律 → 30-40 eV / EUV 20-80 eV"，但 3-5×1.6 eV（MoS₂ 带隙）= 4.8–8 eV，**根本算不出 30-40 eV**——cutoff 律表述或计算错误；而 content §2.2 已改为物理正确的"7-13 阶/8-20 eV"。三章节出现"两处错误且互相一致、一处正确"的最坏不一致。
3. **综述论文投稿期刊跨章矛盾 + 类别错误**：scheme §3.4 写综述"投 Nat. Phys. 或 PRL"，content §2.9 写"投 Rev Mod Phys / Physics Reports"——**PRL 不发表综述**，scheme 的表述是期刊类别错误。
4. **章节标题虚假承诺**：scheme.md 标题声称含特色与创新 + 预期成果，正文却无。
5. **参考文献 [critical] 完全缺失**。

综合评分在 round-2（0.62，聚焦 content）基础上，因 cutoff 律错误从 content 蔓延到 scheme 且未被纠正、综述期刊矛盾、章节标题虚假承诺，给出 **0.60**。

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要短板 |
|---|---:|---:|---:|---|
| 创新性（innovation） | 0.30 | 0.72 | 2 | QEF 三维度/双光路干涉/风险表 No-Go 判据有方法学创新与科研诚信；但 cutoff 数学错误削弱"EUV 20-80 eV"创新叙事，综述期刊类别错误降低成果可信度 |
| 可行性（feasibility） | 0.25 | 0.72 | 3 | 风险评估表（7 行 Plan B + 触发条件）完善；conditional/contingent 三级分层清晰；4K 闭循环恒温器已有；但 NOPA/OPA 术语含混、BSV-固体耦合工程难度论证偏薄 |
| 严谨性（rigor） | 0.25 | 0.55 | 9 | cutoff 律数值自相矛盾且跨章"二错一对"；综述期刊类别错误；Rivera-Dean 2023 预印本作核心锚点；Wu 2024 预印本支撑关键论断；Murakami 2018 范式引用模糊；QEF 维度数跨章不一；Mott 时间点 Y4/Y5 内部矛盾；Hu 2024 新引文待核实 |
| 完整性（completeness） | 0.20 | 0.35 | 4 | 参考文献 [critical] 完全缺失；scheme 标题虚假承诺特色创新+预期成果（三者实际在 content.md 但归属错位）；§3.3/§3.4 表格缺叙述导引 |

**加权综合分**：
= 0.30×0.72 + 0.25×0.72 + 0.25×0.55 + 0.20×0.35
= 0.216 + 0.180 + 0.1375 + 0.070
= **0.6035 ≈ 0.60**

> 说明：cutoff 律错误（scheme+rationale 错、content 对）与综述期刊矛盾是本轮最突出的严谨性硬伤；参考文献 [critical] 缺失 + 章节标题虚假承诺直接拉低完整性。

---

## 一、研究方案段落级深度评审（聚焦章节）

> **评审原则**：每段先列作者声称，再列红队质询，再列修复确认（✅ 已被前轮修复）+ 本轮新增/残留问题。每个问题给出可执行的修改指令。

### §3.1 研究方案与技术路线（第 3–11 行）

> **作者声称**：采用"光源 → 样品 → 谱学 → 理论 → 反演"五段式路线（与 §2.0 一一对应），随后以编号列表 1-5 展开：①BSV 光源 + 经典光对照光路（NOPA/OPA 后置产生 BSV，标定 g(2)/r/关联函数）；②样品平台（单层 TMDC + 扭转双层 MoS₂ 莫尔超晶格，4K 恒温器已有，9T 磁体 conditional）；③HHG 谱学（近红外 0.8–1.5 μm + EUV 20–80 eV，3-5 倍带隙 cutoff → 30-40 eV，10⁴–10⁵ 脉冲统计平均）；④理论建模（量子光 SBE + Bloch 形式化 + 密度矩阵 + 量子轨迹）；⑤探针有效性验证（QEF 三维度）。

**红队解读**：
- **item 3 内嵌物理推理是好的**："BSV 单脉冲光子数涨落 g(2)>>1，单脉冲信噪比差，不适用单脉冲采集 → 拟用 10⁴–10⁵ 脉冲统计平均"——这是难得的"为什么选这个采集方案"论证，符合 `writing_style_rules.must`"研究方案要说明'为什么选这个方法'"。**应作为全章改写的范式样板**。
- 但整体仍以编号列表 1-5 呈现——item 1/2/4/5 多为描述性罗列，未论证方法选择逻辑。
- **item 3 cutoff 律数值错误（核心严谨性问题）**："3-5 倍带隙 cutoff 律，截止能量预期 30-40 eV"——MoS₂ 带隙 ~1.6 eV，3-5 倍 = 4.8–8 eV，**根本算不出 30-40 eV**。且"30-40 eV"与"EUV 20-80 eV"两个区间关系不明。round-2 已在 content §2.2 标记此问题，content 已改为"7-13 阶/8-20 eV"（物理正确），**但 scheme §3.1 item 3 仍是错误的旧表述，rationale §1.2.1 也是同样的错误表述**——形成"两处错误且互相一致、一处正确"的最坏跨章不一致。
- item 1 "NOPA/OPA 后置于非线性晶体产生 BSV"——表述含混。NOPA/OPA 本身就是非线性晶体中的参量过程，"后置于非线性晶体"语义不清；rationale §1.2.2/content §2.1 统一用"高增益参量下转换（PDC）"，术语不一致。
- item 3 新出现引文"Hu et al., PNAS 121, e2317656121 (2024)"——仅 scheme.md 引用，未在 rationale/content 出现，需核实。

**修复确认**：round-3（历史整体轮）标记的"BSV 光源产生机制表述错误（NOPA/OPA 后置）"——scheme §3.1 item 1 已补充"参照 Iskhakov 2012, Spasibko 2012 的高增益参量下转换方案"作限定，部分改善 ✅，但"NOPA/OPA 后置于非线性晶体"主表述仍含混。

**本轮新增/残留问题**：

#### [high] narrative — §3.1 整节编号列表 1-5 替代方法学论证
- 位置：§3.1 第 5–11 行
- 问题：按 `writing_style_rules.forbidden`"条目式罗列：'1. ... 2. ... 3. ...' 替代论证"和 `must`"研究方案要说明'为什么选这个方法、如何解决关键难点'"。当前 5 条编号项多为"做什么"的描述（光源参数/样品/谱学参数/理论工具列表/QEF 指标），未论述：为什么选 NOPA/OPA 而非其他 BSV 产生方案？为什么选 TMDC 作为初步示范（content §2.2 已论证带隙匹配，scheme 应承接）？为什么 SBE + Bloch + 密度矩阵 + 量子轨迹四种理论工具要组合使用、各自解决什么？item 3 的"为什么多脉冲平均"是好样板，但其余 item 缺同类论证。
- 建议：将编号列表改写为连贯叙述，以"五段式路线"为主线串联，每段补充"方法选择理由 → 关键难点 → 解决路径"。例如 item 4 理论建模应说明"SBE 处理带间/带内跃迁、Bloch 形式化提供量子光推广锚点、密度矩阵演化描述电子-空穴-光子复合系统、量子轨迹方法解读实空间动力学——四者各司其职、缺一不可"。
- action：rewrite

#### [high] rigor — §3.1 item 3 cutoff 律数值自相矛盾且与 content 跨章"二错一对"
- 位置：§3.1 item 3 第 9 行
- 问题：同一句给出"3-5 倍带隙 cutoff 律""截止能量预期 30-40 eV""EUV 20-80 eV"三个数值。MoS₂ 带隙 ~1.6 eV，3-5 倍 = 4.8–8 eV，**算不出 30-40 eV**——cutoff 律表述或计算有误。更严重的是 content §2.2 已改为物理正确的"7-13 阶奇次谐波/8-20 eV"，**但 scheme §3.1 与 rationale §1.2.1 仍是错误的"30-40 eV"旧表述**——writer 修了 content 却未同步 scheme 与 rationale，且 scheme 与 rationale 共享同一个错误，形成"两错一对"。
- 建议：§3.1 item 3 统一为与 content §2.2 一致的表述——"对于带隙约 1.6 eV 的单层 MoS₂，近红外驱动下实验可观测的奇次谐波通常延伸至 7-13 阶（约 8-20 eV，VUV-EUV 低能端）"；删除"3-5 倍带隙 cutoff 律 → 30-40 eV"与"EUV 20-80 eV"两处错误数值；同步修正 rationale §1.2.1 的同一错误。
- action：recalculate + rewrite

#### [medium] rigor — §3.1 item 1 "NOPA/OPA 后置于非线性晶体"表述含混且与 PDC 术语不一致
- 位置：§3.1 item 1 第 7 行
- 问题：NOPA（非简并光参量放大）/OPA 本身即非线性晶体中的参量过程，"后置于非线性晶体"语义不清（后置于什么？）。rationale §1.2.2 与 content §2.1 统一用"高增益参量下转换（PDC）"，scheme 用"NOPA/OPA 后置"——术语漂移。
- 建议：改为"基于高增益参量下转换（PDC）在非线性晶体（如 BBO/BiBO）中产生 BSV（参照 Iskhakov 2012、Spasibko 2012）"，与 rationale/content 术语统一。
- action：rewrite

#### [medium] rigor — §3.1 item 3 新引文 Hu 2024 仅见于 scheme，待核实
- 位置：§3.1 item 3 第 9 行"Hu et al., Proc. Natl. Acad. Sci. U.S.A. 121, e2317656121 (2024) 范式"
- 问题：该引文仅 scheme.md 引用，未在 rationale/content 出现，用作"HHG shot-by-shot 关联分析范式"的方法学支撑。PNAS 卷号格式（e-notation）看似合理，但需联网核实作者、标题与 e-编号准确性，确认是否真为 HHG 逐脉冲关联分析工作。
- 建议：核实后保留；若不准确则替换为已核实的 shot-by-shot HHG 关联分析文献。
- action：verify

---

### §3.2 关键技术与可行性（第 13–18 行）

> **作者声称**：以 4 条 bullet 论证可行性：①BSV 光源技术成熟（Iskhakov/Spasibko 2012），风险=高反射/散射损耗；②固体 HHG 平台本课题组已有，风险=时空模式失配；③Even Tzur/Gorlach 2024 [PRR 6, 023064] 已给量子光 HHG 框架，拓展到固体多带多体是核心创新，风险=多体非微扰发散；④双光路干涉参照 Raab 2024 + Li 2022，SLM 锁相<150 mrad 可达，风险=时空重合。

**红队解读**：
- 4 条 bullet 是"可行性论断清单"——每条结构都是"X 已成熟/已有 → 低风险；风险点=…"，**缺"如何解决关键难点"的论述**。按 `writing_style_rules.must`"研究方案要讲清楚如何解决关键难点"，风险点全部以"（详风险评估）"打发到 §3.3，本节本身无难点解决论证。
- **Even Tzur 2024 框架不可直接移植性**：round-2 已在 content §2.3 标记，content 已补充"需引入晶体动量、贝里相位、激子、强关联修正"。scheme §3.2 item 3 也写了"需引入晶体动量自由度、贝里相位、激子效应、强关联修正"——✅ 这一点 scheme 已同步。但 item 3 把这一核心理论创新压缩在一条 bullet 内，未展开"为什么这是核心创新而非增量移植"。
- **Rivera-Dean 2023 [arXiv:2309.14435] 仍为预印本**，却被用作"量子光 Bloch 形式化方法学锚点"——核心理论支柱依赖未正式发表的工作。
- item 4 Li 2022 [PRL 129, 173001 (2022); arXiv:2205.11161]——scheme 给了完整卷期页码（比 content §2.5 的缺卷期版完整），但需核实 129, 173001 是否准确。

**本轮问题**：

#### [high] narrative — §3.2 整节 4 条 bullet 罗列可行性论断，缺"如何解决关键难点"论述
- 位置：§3.2 第 15–18 行
- 问题：4 条 bullet 结构统一为"X 成熟/已有 → 风险点（详风险评估）"，把所有难点解决论证推给 §3.3。按 `writing_style_rules.must`"研究方案要讲清楚如何解决关键难点，而不是罗列实验步骤"，本节应论述每个关键技术的可行性边界与难点突破路径，而非可行性断言清单。
- 建议：改写为连贯论述，按"技术成熟度 → 本项目增量 → 关键难点 → 突破路径"展开。例如 item 3 应论述"Even Tzur 2024 框架建立在气体原子三步模型上，处理单动量点连续态-基态耦合；本项目面对固体多带多体，涉及晶体动量积分、Bloch 态带间/带内跃迁、Berry 相位修正——因此不是直接移植，而是将其形式化方法（winding trail 量子态模型）拓展到固体多带语境，属核心理论创新"（与 content §2.3 对齐）。
- action：rewrite

#### [medium] rigor — Rivera-Dean 2023 [arXiv:2309.14435] 预印本作为核心理论锚点
- 位置：§3.2 item 3 第 17 行
- 问题：Rivera-Dean 2023 仍是 arXiv 预印本，却在 scheme §3.1 item 4 / §3.2 item 3 / content §2.3 三处被用作"量子光 Bloch 形式化方法学锚点"——核心理论支柱。按 `physics-domain-checks.md` 第 6 项"预印本依赖度"，核心论断依赖未正式发表工作需显著降权或核实。
- 建议：联网核实 Rivera-Dean 2023 是否已正式发表；若已发表补全期刊卷期；若仍为预印本，改用"预印本"限定语（"据目前检索，Rivera-Dean 等的 Bloch 形式化方案尚未正式发表，本项目以其预印本为方法学参照"）。
- action：verify

#### [medium] rigor — §3.2 item 4 Murakami 2018"范式"引用模糊（与 §3.3 row 3 联动）
- 位置：§3.2 item 3 末"沿用 Rivera-Dean 2023 ... + Peschel 2022 ..."及 §3.3 row 3"Floquet 平均场 [Murakami 2018 范式]"
- 问题：§3.3 row 3 Plan B 写"截断库仑势 + Floquet 平均场 [Murakami 2018 范式]"——Murakami 2018 [PRL 121, 057405] 是 Mott 绝缘体 HHG 工作，是否同时提出"Floquet 平均场"收敛方案需核实；"范式"一词过于模糊，评审专家会追问具体方法对应关系。
- 建议：核实 Murakami 2018 是否含 Floquet 平均场方法；若有则注明具体章节/方法名；若无则替换为真正支持 Floquet 平均场收敛方案的文献。
- action：verify

---

### §3.3 关键技术风险评估与替代方案（第 20–30 行）

> **作者声称**：7 行风险表，每行给出环节/主要风险/触发条件/Plan B/风险升级判定/对应缺口。覆盖 BSV 光源、固体 HHG 平台兼容、SBE 多体拓展、多体态样品、QEF 方法学+双光路干涉、低温强磁场平台、Y4 反馈式升级。

**红队解读**：
- **风险评估表是本章结构最完善的部分**——每环节都有明确的量化触发条件（g(2) 复现度<70%、产额比<50%、SBE 不收敛、信号比<10%、系统偏差>5%、采购延期>6 月、RSD>10%）与对应 Plan B，体现成熟的风险管理与科研诚信。✅
- **No-Go 判据设计良好**：符合 `physics-domain-checks.md` 第 4 项"科学问题需有 No-Go 路径"。
- 但 row 1 触发条件"g(2)(0) 偏离 Iskhakov 2012 基线 > 30%"——未指明是哪一配置基线（非简并=2 还是简并=3+1/N）。round-2/round-7 已在 rationale/content 澄清 g(2)(0) 是两个独立单值而非区间，scheme §3.3 此处仍用模糊"基线"。
- 表格缺 1-2 句叙述性导引（风险哲学/分级逻辑）。

**本轮问题**：

#### [medium] rigor — §3.3 row 1 g(2)(0) 触发条件未指明配置基线（与 rationale/content 不同步）
- 位置：§3.3 row 1 第 24 行"g(2)(0) 偏离 Iskhakov 2012 基线 > 30%"
- 问题：round-7/round-2 已澄清 g(2)(0) 在非简并 PDC 下=2、简并 PDC 下=3+1/N，是两个独立实验体系的单值。scheme §3.3 row 1 用模糊"Iskhakov 2012 基线"，评审专家无法判断 30% 偏离是相对哪个值。
- 建议：改为"g(2)(0) 偏离对应配置基线（非简并 PDC 的 2 或简并 PDC 的 3+1/N）> 30%"，与 rationale §1.2.2/content §2.1 表述同步。
- action：rewrite

#### [medium] narrative — §3.3 风险表缺叙述性导引
- 位置：§3.3 第 20–30 行
- 问题：表格直接呈现，缺 1-2 句说明风险分级逻辑（如"按物理层/方法学层/工程层三类风险分级，每类设定量化触发阈值"）。
- 建议：表格前补 1 句——"本项目按物理层（机制/材料空白）、方法学层（框架空白）、工程层（平台稳定性）三类风险分级管理，每环节设定量化触发阈值与 Plan B"。
- action：add

---

### §3.4 关键交付时间表与可量化指标（第 32–44 行）

> **作者声称**：5 行交付表（QEF 三维度基线标定 / Q_F 全景图 / 莫尔超晶格 BSV-HHG 首例 / 探针方法学综述论文 / Nature Phys.-PRL 首例论文），每行给出时点/量化指标/验收标准，末附与 §2.8 分工说明。

**红队解读**：
- 量化验收指标清晰（QEF 三维度、Q_F 全景图 R∈[0.1,10]、经典极限自洽性、q_ref=7或9、RSD<10%）——✅ 好。
- **row 4 综述论文投稿期刊矛盾（核心跨章问题）**：scheme §3.4 row 4 写"探针方法学综述论文（投 Nat. Phys. 或 PRL）"，但 content §2.9 写"探针方法学综述（拟投 Reviews of Modern Physics / Physics Reports 或受邀综述）"。**PRL 不发表综述论文**（PRL 只发表 Letter），scheme 的"投 PRL 综述"是期刊类别错误；Nat. Phys. 虽有 Review/N&V 但不做完整方法学综述。content §2.9 的 Rev Mod Phys/Physics Reports 才是综述正途。
- **row 4/5 论文预期乐观**：row 5"Nature Phys./PRL 首例论文 Y2 末至 Y3 初"——round-2/3 已标记此预期乐观，scheme 仍未给可行性论证。
- **Mott 时间点内部矛盾**：row 1"Mott 可推迟至 Y4" vs §3.3 row 6"低温实验推迟至 Y5 拓展" vs content §2.7"Y4 conditional，推迟至 Y5 拓展期"。scheme 内部 Y4/Y5 不一致。
- row 2 验收"经典极限 Q_F → V_classical ≈ 1 自洽性通过"——✅ 与 rationale §1.3/content §2.5 已修复的物理表述一致。

**本轮问题**：

#### [high] cross-chapter — §3.4 row 4 综述论文投稿期刊与 content §2.9 矛盾 + PRL 类别错误
- 位置：§3.4 row 4 第 41 行"探针方法学综述论文（投 Nat. Phys. 或 PRL）" vs content §2.9 第 99 行"拟投 Reviews of Modern Physics / Physics Reports 或受邀综述"
- 问题：两处对同一篇综述论文的投稿期刊表述直接矛盾。更严重的是 **PRL 不发表综述论文**（PRL 仅 Letter），scheme 写"投 PRL 综述"是期刊类别错误；Nat. Phys. 的综述体例也不适配完整方法学综述。content §2.9 的 Rev Mod Phys / Physics Reports 才是综述正途。
- 建议：§3.4 row 4 统一为与 content §2.9 一致的"探针方法学综述论文（拟投 Reviews of Modern Physics / Physics Reports 或受邀综述）"，删除"PRL"。
- action：rewrite

#### [medium] rigor — Mott 时间点 scheme 内部矛盾（Y4 vs Y5）
- 位置：§3.4 row 1 第 38 行"Mott 可推迟至 Y4" vs §3.3 row 6 第 29 行"低温实验推迟至 Y5 拓展" vs §3.1 item 2 第 8 行"延期则推迟至 Y5"
- 问题：同一文件内 Mott/低温实验推迟时点不一致（row 1 说 Y4，row 6 与 §3.1 item 2 说 Y5）。content §2.7 统一为"Y4 conditional，推迟至 Y5 拓展期"。
- 建议：§3.4 row 1 改为"Mott 可推迟至 Y5 拓展期（与 §3.3 row 6、§3.1 item 2、content §2.7 一致）"。
- action：rewrite

#### [medium] rigor — §3.4 row 4/5"Nature Phys./PRL"论文预期乐观（继承未修）
- 位置：§3.4 row 4 第 41 行、row 5 第 42 行
- 问题：round-2/3 已标记"Nature Phys./PRL 1-2 篇"预期乐观，scheme §3.4 仍写"Y2 末至 Y3 初"首例论文，未给可行性论证（BSV-固体 HHG 首例实验本身有发表竞争力，但 Y2-Y3 的时间节点需结合 BSV 光源搭建+TMDC HHG 测量+理论解读的完整周期评估）。
- 建议：补 1 句可行性说明，或将时点放宽至"Y2 末至 Y3 末"。
- action：rewrite

#### [medium] narrative — §3.4 交付表缺叙述导引
- 位置：§3.4 第 34–44 行
- 问题：表格前仅有"与 2.7 年度计划的进度对齐"一句，缺交付逻辑叙述（如"核心交付聚焦 Y3 末 QEF 三维度 + Q_F 全景图，Mott 与反馈式升级为 conditional/contingent"）。
- 建议：表格前补 1-2 句交付逻辑。
- action：add

---

## 二、写作风格红线集中审查（重点检查）

按本轮用户指令重点检查"叙述式 vs 堆砌式"红线，scheme.md 全章违规点如下：

| 位置 | 违规类型 | 严重度 |
|---|---|---|
| §3.1（第 5–11 行） | 编号列表 1-5 替代方法学论证，item 1/2/4/5 多为描述性罗列，缺"为什么选这个方法"（item 3 有好样板但其余缺） | [high] |
| §3.2（第 15–18 行） | 4 条 bullet 可行性论断清单，风险点全推给 §3.3，本节无"如何解决关键难点"论述 | [high] |
| §3.3（第 20–30 行） | 风险表（表格形式可接受）+ 缺叙述性导引 | [medium] |
| §3.4（第 34–44 行） | 交付表（表格形式可接受）+ 缺叙述性导引 | [medium] |

**统计**：4 个子节中，**§3.1/§3.2 以编号/bullet 为主要呈现形式**（2 处 [high] narrative），§3.3/§3.4 表格可接受但缺叙述导引（2 处 [medium]）。相比 round-2 发现 content.md"9 个子节中 7 个 bullet 化"，scheme.md 的列表化程度略轻（且 item 3 内嵌物理推理是好样板），但仍违反 `writing_style_rules.core`"申请书必须是连贯的叙述/论述式研究故事"。**改写范本已在 §3.1 item 3 给出**——writer 应将 item 3 的"为什么多脉冲平均"推理模式推广到其余 item 与 §3.2 各条。

---

## 三、跨章节一致性审查（简要）

| 检查对 | 结论 | 证据定位 |
|---|---|---|
| scheme §3.1 "3-5倍带隙cutoff→30-40 eV/EUV 20-80 eV" vs content §2.2 "7-13阶/8-20 eV" | ❌ **二错一对**：scheme 与 rationale §1.2.1 都错（3-5×1.6=4.8-8≠30-40），content 已改正 | scheme 第 9 行 vs content 第 32 行 vs rationale 第 19 行 |
| scheme §3.4 row 4 综述"投 Nat Phys/PRL" vs content §2.9 "Rev Mod Phys/Physics Reports" | ❌ **跨章矛盾 + PRL 类别错误** | scheme 第 41 行 vs content 第 99 行 |
| scheme §3.4 row 1 "Mott 推迟 Y4" vs scheme §3.3 row 6 "推迟 Y5" vs content §2.7 "Y5 拓展" | ⚠️ **scheme 内部矛盾 + 跨章不一** | scheme 第 38/29 行 vs content 第 81 行 |
| scheme §3.1/§3.4 QEF"三维度" vs rationale §1.4"双指标" vs content §2.4"两核心+一辅助=三维" | ⚠️ **指标数量表述需统一**（继承 round-2） | scheme 第 11/38 行 vs rationale 第 59 行 vs content 第 48 行 |
| scheme §3.1 item 1 "NOPA/OPA 后置" vs rationale §1.2.2/content §2.1 "高增益 PDC" | ⚠️ **术语漂移** | scheme 第 7 行 vs rationale 第 23 行 |
| scheme §3.3 row 1 g(2)(0)"Iskhakov 基线" vs rationale/content "两类独立单值" | ⚠️ **触发条件不同步** | scheme 第 24 行 vs rationale 第 23 行 |
| scheme §3.2 Even Tzur 不可移植性"需引入晶体动量/贝里相位/激子/强关联" vs content §2.3 | ✅ **一致**（scheme 已同步） | scheme 第 17 行 vs content 第 38 行 |
| scheme §3.4 row 2 Q_F"→V_classical≈1" vs rationale §1.3/content §2.5 | ✅ **一致**（物理正确） | scheme 第 39 行 vs rationale 第 49 行 |
| scheme §3.1 item 3 "多脉冲统计平均"推理 vs content §2.2 | ✅ 一致（且 scheme 论证更细） | scheme 第 9 行 |

**跨章节一致性结论**：9 对检查中，3 对 ✅ 一致、2 对 ❌ 矛盾、4 对 ⚠️ 需修订。最突出的是 **cutoff 律"二错一对"**（scheme+rationale 错、content 对）与**综述期刊矛盾**——这两个是评审专家会直接用红笔圈出的硬伤。

---

## 四、物理领域专项检查（physics-domain-checks.md 8 项）

| 检查项 | 命中位置 | 状态 |
|---|---|---|
| 1. BSV 增强与反演精度 | scheme §3.2"BSV 产生技术已成熟"，未声称产额→精度 | ✅ 通过（rationale §1.2.2 已拆分三层） |
| 2. Berry 曲率/量子度规辨识性 | scheme 未涉及 Berry 反演 | N/A |
| 3. CDW/Mott/拓扑分类 | scheme §3.3 row 4/6 莫尔/Mott 分类 | ✅ 通过（分层正确） |
| 4. Q1/Q2 可证伪性 | scheme §3.3 风险表 No-Go 触发条件 | ✅ 通过（量化阈值清晰） |
| 5. 双色场 sin/cos 强假设 | scheme §3.3 row 5 Plan B"单束双色ω+2ω" | ✅ 通过（作 Plan B 而非主假设） |
| 6. 预印本依赖度 | Rivera-Dean 2023（核心锚点）、Wu 2024（关键论断）仍 arXiv；Iskhakov/Spasibko/Even Tzur/Peschel/Raab/Li/Murakami 均已正式发表 | ⚠️ 2/11≈18%，但 Rivera-Dean 作核心锚点需核实 |
| 7. 驱动波长与带隙匹配 | scheme §3.1 item 3 0.8-1.5 μm 与 TMDC 1.5-2 eV 匹配，但 cutoff 律数值错 | ⚠️ 匹配正确，cutoff 计算错 |
| 8. 关键预印本核实 | Wu 2024（莫尔室温）、Rivera-Dean 2023（Bloch 锚点） | ⚠️ 需核实正式发表状态 |

**物理专项结论**：8 项中 4 项 ✅、2 项 N/A、2 项 ⚠️。scheme 在风险分级（第 4 项）、材料分类（第 3 项）、BSV-精度拆分（第 1 项）上处理正确；主要短板是 cutoff 律计算（第 7 项）与两个核心预印本（第 6/8 项）。

---

## 五、问题清单（按严重度分级）

### Critical（必须立即修复）

1. **[critical] completeness** — 参考文献 references.md 完全缺失（仅"（待 writer 补齐）"占位符，0 字符）。正文（rationale + content + scheme）引用 Iskhakov 2012、Spasibko 2012、Wu/Schafer/Gaarde 2016、Silva 2018、Murakami 2018、Liu 2017、Rasputnyi 2024、Even Tzur/Gorlach 2024、Rivera-Dean 2023、Peschel 2022、Li 2019、Li 2022、Raab 2024、Wu 2024、Boroumand 2025、Hu 2024、Wilkinson 2016、Karniadakis 2019 等 ≥20 篇，但参考文献章空白。NSFC 硬规范红线，评审专家会直接判定"不完整"。必须补齐完整参考文献列表（作者/期刊/卷期页码/年份/arXiv）。
- action：add

### High（必须修复）

2. **[high] narrative** — §3.1 整节编号列表 1-5 替代方法学论证，item 1/2/4/5 缺"为什么选这个方法"论述（第 5–11 行）。item 3 的"为什么多脉冲平均"是好样板，应推广。
- action：rewrite
3. **[high] narrative** — §3.2 整节 4 条 bullet 可行性论断清单，风险点全推给 §3.3，本节无"如何解决关键难点"论述（第 15–18 行）。
- action：rewrite
4. **[high] rigor** — §3.1 item 3 cutoff 律数值自相矛盾（3-5×1.6 eV=4.8-8 eV ≠ 30-40 eV）且与 content §2.2 已修版"7-13 阶/8-20 eV"跨章"二错一对"（scheme+rationale 错、content 对）（第 9 行）。
- action：recalculate + rewrite
5. **[high] cross-chapter** — §3.4 row 4 综述论文"投 Nat. Phys. 或 PRL"与 content §2.9"Rev Mod Phys/Physics Reports"矛盾；PRL 不发表综述，属期刊类别错误（第 41 行）。
- action：rewrite
6. **[high] completeness/structure** — scheme.md 标题"（三）研究方案、特色与创新、预期研究成果"承诺三项，正文仅交付研究方案（§3.1–§3.4）；特色与创新（§2.8）、年度计划（§2.7）、预期成果（§2.9）实际位于 content.md，标题与内容错位造成模块边界混乱。
- action：rewrite（标题改为"（三）研究方案"，或在 scheme 内补齐特色创新/预期成果并从 content 移出）

### Medium（应当修复）

7. **[medium] rigor** — Rivera-Dean 2023 [arXiv:2309.14435] 仍为预印本，却作"量子光 Bloch 形式化方法学锚点"（核心理论支柱）（第 17 行）。
- action：verify
8. **[medium] rigor** — §3.1 item 2 Wu 2024 [arXiv:2311.16655] 仍仅 arXiv，支撑"扭转双层 MoS₂ 莫尔超晶格室温可工作"关键论断（第 8 行）。
- action：verify
9. **[medium] rigor** — §3.3 row 3"Floquet 平均场 [Murakami 2018 范式]"引用模糊，Murakami 2018 [PRL 121, 057405] 是否含 Floquet 平均场方法需核实（第 26 行）。
- action：verify
10. **[medium] cross-chapter** — §3.3 row 1 g(2)(0) 触发条件"偏离 Iskhakov 2012 基线 > 30%"未指明配置基线（非简并=2/简并=3+1/N），与 rationale/content 已澄清表述不同步（第 24 行）。
- action：rewrite
11. **[medium] cross-chapter** — QEF 指标数量表述不一：scheme"三维度" vs rationale §1.4"双指标" vs content §2.4"两核心+一辅助"，需全文统一（第 11/38 行）。
- action：rewrite
12. **[medium] rigor** — Mott 时间点 scheme 内部矛盾：§3.4 row 1"Mott 推迟 Y4" vs §3.3 row 6"推迟 Y5" vs §3.1 item 2"Y5"（第 38/29/8 行）。
- action：rewrite
13. **[medium] rigor** — §3.1 item 1"NOPA/OPA 后置于非线性晶体产生 BSV"表述含混，与 rationale/content"高增益 PDC"术语不一致（第 7 行）。
- action：rewrite
14. **[medium] narrative** — §3.3/§3.4 两个表格缺叙述性导引句（风险分级逻辑/交付逻辑）（第 20、34 行）。
- action：add
15. **[medium] rigor** — §3.1 item 3 新引文 Hu 2024 [PNAS 121, e2317656121 (2024)] 仅见于 scheme，待核实（第 9 行）。
- action：verify
16. **[medium] rigor** — §3.4 row 4/5"Nature Phys./PRL"论文预期乐观（Y2末-Y3初首例），继承 round-2/3 未修（第 41-42 行）。
- action：rewrite

### Low（建议修复）

17. **[low] rigor** — 两篇"Li et al."引文（Li 2019 [PRL 123, 153201] / Li 2022 [PRL 129, 173001]）跨章均称"Li 等"，易混淆，建议加首字母或主题区分。
- action：rewrite
18. **[low] expression** — §3.1 item 2"4 K 闭循环低温恒温器为 Y2 末已具备"语序拗口，建议"Y2 末已配备"（第 8 行）。
- action：rewrite
19. **[low] expression** — 章节交叉引用格式混用"2.5 节""3.3""§2.0""1.2.3"，全书不统一。
- action：rewrite

**去重后总计：19 个问题（critical: 1，high: 5，medium: 10，low: 3）**

---

## 六、对抗结论

- **本轮发现 19 个独立问题**（critical: 1，high: 5，medium: 10，low: 3）。
- **模块完整性**：经逐文件核查，参考文献确属 [critical] 完全缺失；特色与创新/年度计划/预期成果**内容并非完全缺失**（均在 content.md §2.7/2.8/2.9 有实质内容），但 **scheme.md 标题虚假承诺特色创新+预期成果却未交付**，造成模块归属错位与评审专家"翻第三章找不到"的结构性混乱。
- **聚焦章节深审**：scheme.md（48 行，7980 字符）风险评估表（§3.3）与量化交付（§3.4）结构完善、No-Go 判据清晰、§3.1 item 3 内嵌物理推理是好样板；但存在三类系统性问题：
  - **写作风格红线**：§3.1/§3.2 以编号/bullet 替代方法学论证（2 处 [high] narrative）；
  - **cutoff 律"二错一对"跨章不一致**：scheme+rationale 错、content 对，writer 修了 content 未同步 scheme/rationale；
  - **综述期刊矛盾 + 章节标题虚假承诺**。

- **相比上一轮**（round-2 聚焦 content，给分 0.62，26 问题）：
  - **改善 3 项**：scheme §3.2 已同步 Even Tzur 不可移植性论述（与 content §2.3 一致）；§3.3 风险表 No-Go 判据完整；§3.1 item 3 多脉冲平均推理是好样板。
  - **未解决/跨章未同步 5 项**：
    1. [high] cutoff 律数值错误从 content 蔓延且 scheme/rationale 仍未修（content 已改正）
    2. [medium] QEF 维度数跨章不一（rationale 双/scheme-content 三维）
    3. [medium] g(2)(0) 配置基线 scheme §3.3 未同步
    4. [medium] NOPA/OPA vs PDC 术语漂移
    5. [medium→high] Nature Phys./PRL 论文预期乐观
  - **新增 8 项**：综述期刊跨章矛盾（high）；§3.1/§3.2 narrative（high）；章节标题虚假承诺（high）；Murakami 范式引用模糊；Mott Y4/Y5 内部矛盾；Hu 2024 新引文待核实；两 Li 引文混淆；表格缺叙述导引等。

- **是否达到输出标准**：**否**。
  - 综合评分 0.60 < 0.80 门槛；
  - critical 1 个 > 0（参考文献缺失）；
  - high 5 个 >> max_high_issues 0；
  - medium 10 个 >> max_medium_issues 3；
  - 四个指标全部不达标。

- **返工优先级**：
  - **P0（critical）**：
    1. 补齐参考文献章——将正文 ≥20 篇引用整理为完整列表。
  - **P1（high）**：
    2. **修正 cutoff 律**：scheme §3.1 item 3 + rationale §1.2.1 统一为 content §2.2 的"7-13 阶/8-20 eV"，删除"3-5 倍带隙→30-40 eV"与"EUV 20-80 eV"错误数值；
    3. **统一综述期刊**：scheme §3.4 row 4 改为"Rev Mod Phys/Physics Reports"，删除 PRL；
    4. **修正章节标题**：scheme.md 标题改为"（三）研究方案"，或在 scheme 内补齐特色创新/预期成果并从 content 移出，消除标题虚假承诺；
    5. **§3.1/§3.2 叙述式改写**：将编号/bullet 改为连贯论述，每节补"为什么选这个方法/如何解决关键难点"，以 §3.1 item 3 的推理模式为样板。
  - **P2（medium）**：
    6. 核实 Rivera-Dean 2023 / Wu 2024 / Murakami 2018 范式 / Hu 2024 四处引文；
    7. 同步 g(2)(0) 配置基线、QEF 维度数、NOPA/OPA→PDC 术语、Mott Y4/Y5 时间点；
    8. §3.3/§3.4 表格补叙述导引。

- **下一轮评审建议聚焦**：
  1. **先补参考文献 + 修 cutoff 律**——一个是 critical 硬规范，一个是物理计算错误且三章联动；
  2. **再做 scheme §3.1/§3.2 叙述式改写**——2 处 [high] narrative；
  3. **然后做跨章同步**——综述期刊、QEF 维度、g(2) 基线、术语、Mott 时间点 5 处；
  4. **最后核实 4 处引文**。

---

## 评分
创新性：0.72
可行性：0.72
严谨性：0.55
完整性：0.35
综合评分：0.60
