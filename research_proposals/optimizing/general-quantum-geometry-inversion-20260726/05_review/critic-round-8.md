# 对抗评审报告（第 8 轮 · 整体一致性审查）

**申请书**：general-quantum-geometry-inversion-20260726
**项目类型**：面上项目（general）
**评审日期**：2026-08-11
**本轮聚焦**：三章节（rationale / content / scheme）整体一致性审查 + references 引文核对
**评审 profile**：critic
**标准依据**：memory/nsfc-standards.json（project_types.general + general_principles）
**范本锚点**：reference_materials.style_benchmark + benchmark_anchors（范本提炼特征）

---

## 综合评分

**0.78 / 1.00**

- 程序化 AI 检测天花板估计：0.75（主要扣分项：超长句密度过高，content.md 有 52 句 >120 字）
- 天花板约束：ceiling 0.75 → 表达质量 ≤ 0.75 → 综合评分受表达质量拖累
- general 面上项目阈值 min_overall_score = 0.80 → **当前 0.78 未达标**，差距 0.02
- 核心拉低因素：[critical] 引文编号系统性互换（Silva/Liu-Fu-Kais）+ [high] R3' 启动时间跨章节矛盾 + 超长句密度

---

## 维度评分

| 维度 | 权重 | 得分 | rubric 档位依据 | 主要短板 |
|------|------|------|----------------|----------|
| 创新性（innovation） | 0.30 | 0.85 | 科学问题新颖、Q1/Q2 可证伪闭环设计扎实，BSV×量子几何反演×CDW 三维交叉确有创新性 | 无重大短板，三项创新点（BSV-SBE 框架 / Ω/g 可辨识性边界 / CDW 相图）定位清晰 |
| 可行性（feasibility） | 0.25 | 0.82 | Go/No-Go 判据体系完整、降级路径诚实、预研数据支撑复现验证 | R3' 启动时间跨章节不一致影响执行计划可信度 |
| 严谨性（rigor） | 0.35 | 0.70 | 引文编号 Silva[4]↔Liu-Fu-Kais[3] 系统性互换（6 处），违反 indicator_red_lines.consistency_check | 引文归属错误属 P0 红线，严谨性直接扣至 0.6–0.7 区间 |
| 表达质量（expression） | 0.10 | 0.72 | 叙述式主线良好、关联词控制优秀；但超长句密度严重超标（content 52 句>120字、scheme 35 句>120字） | 超长句违反 anti_ai_patterns「超长句上限每段 3」；ceiling 0.75 约束下不得 ≥0.75 |

---

## 执行清单对照

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 模块完整性（7 模块） | ✅ 通过 | rationale §1.1–§1.6 + content §2.1–§2.6 + scheme §3.1–§3.5/特色创新/预期成果 + references [1]–[27]，7 模块齐备 |
| 立项依据五层递进 | ✅ 通过 | §1.1 大背景→§1.2 领域脉络+核心问题→§1.3 国内现状+首创性边界→§1.4 四年框架→§1.5 预研基础→§1.6 定位总结，五层完整 |
| 研究目标含量化指标 | ✅ 通过 | §2.1 主问题含 r≤1.5、U/W≤1.0 量化边界；R1–R4 每项均有 Go/No-Go 量化判据（差异<10%、截止提升≥15%、Fisher 比<1.2/≥2 等） |
| 特色创新四步闭环 | ✅ 通过 | scheme 特色与创新三段式（前人空白→本项目填补→4 年内可证伪条件），round-7 P0-2 已修复 |
| 叙述式主线（非文献堆砌） | ✅ 通过 | rationale §1.2 文献嵌入论证链（"Ghalgaoui 等[5]证明…Rasputnyi 等[7]随后…"），无 A做了X/B做了Y 堆砌 |
| 死板关联词高频 | ✅ 通过 | "在此基础上"全文 0 次、"此外"0 次、"基于此"1 次——远低于 anti_ai_patterns 阈值 |
| 模板句式「为…提供…」 | ✅ 通过 | rationale 1 次、content 2 次、scheme 0 次——远低于 15 次上限 |
| 「本项目拟/将」句首滥用 | ✅ 通过 | 全文 0 次以"本项目拟/本项目将"起句 |
| 超长句控制（>120 字每段≤3） | ❌ **不通过** | content.md 检出 52 句>120 字（远超每段 3 句上限）；scheme.md 检出 35 句>120 字。详见问题清单 R8-H3 |
| 引文编号一致性 | ❌ **不通过** | Silva 与 Liu-Fu-Kais 编号在 6 处被互换。详见问题清单 R8-C1 |
| 指标跨章节口径一致 | ⚠ 部分不通过 | R3' 启动时间 Year 2 Q3 vs Year 3 Q1 矛盾；PINN 预算 full_review "50 GPU-day" vs content/scheme "48 GPU·天" |
| 理论框架失效边界标注 | ✅ 通过 | BSV-SBE 三层近似(a)(b)(c)有效性边界明确（差异>10% 关闭条件）；单电子紧束缚 U/W 适用边界明确 |
| 「首次/尚未见」有检索支撑 | ✅ 通过 | §1.3 + §1.6 元规则：限定"arXiv+WoS+CNKI，2018-01 至 2026-07 检索范围内"，附关键词组合 |
| 内容越界（方案↔可行性） | ✅ 通过 | scheme §3.1–§3.4 以"科学问题→方法选择→判据→失败降级"四段式组织，未出现"为什么研究"口吻越界 |

**执行清单失败项统计：3 项不通过 + 1 项部分不通过**。失败项 >3，触发评分上限约束：受影响章节评分不得超过 0.70。严谨性已因引文红线扣至 0.70。

---

## 写作风格评估

### 程序化 AI 检测结果

| 检测项 | rationale | content | scheme | 阈值 | 判定 |
|--------|-----------|---------|--------|------|------|
| 在此基础上 | 0 | 0 | 0 | — | ✅ 优秀 |
| 此外 | 0 | 0 | 0 | — | ✅ 优秀 |
| 同时(不含与此同时) | 8 | 5 | 0 | <10 | ✅ 通过 |
| 因此 | 1 | 1 | 3 | <10 | ✅ 通过 |
| 然而 | 3 | 0 | 0 | <10 | ✅ 通过 |
| 为…提供…(基础/支撑/途径等) | 1 | 2 | 0 | <15 | ✅ 远低于阈值 |
| 本项目拟/将(句首) | 0 | 0 | 0 | <8 | ✅ 优秀 |
| 本项目(全文) | 17 | 12 | 16 | — | ✅ 范本要求"以本项目为主语" |
| 显著 | 0 | 14 | 4 | <15 | ⚠ content 接近上限 |
| 完整 | 2 | 7 | 6 | <15 | ✅ 通过 |
| 关键 | 4 | 4 | 6 | <15 | ✅ 通过 |
| >120 字超长句 | 6 | **52** | **35** | 每段≤3 | ❌ **严重超标** |
| 80–120 字长句 | 27 | 38 | 52 | — | ⚠ 偏多 |

### 风格评估结论

**优点**：关联词控制极为出色——"在此基础上""此外""基于此"等死板关联词几乎为零，"为…提供…"模板句式仅 3 次（全文），"本项目拟/将"句首滥用完全消除。这表明前 7 轮的去 AI 味工作在关联词和模板句式层面已取得实质效果。叙述式主线清晰，文献嵌入论证链而非堆砌。

**核心问题**：超长句密度严重超标。content.md 的 52 句>120 字远超「每段≤3」的 anti_ai_patterns 上限。许多句子把"科学问题→判据→降级路径→合作依赖"压缩在一句之内，单句长达 150–200 字。这虽非典型"AI 味"（关联词/模板句式），但属于 anti_ai_patterns 明确列出的「超长句超过 120 字属严重超长句」红线。

**ai_detection_ceiling 估计：0.75**。基于超长句密度（主要扣分项），表达质量不得超此天花板。

---

## 锚点对比

### 对比 1：立项依据开篇——科学故事切入 vs 范本锚点

**申请书原文**（rationale §1.1 第 1–2 段）：
> 凝聚态物理过去十年的一个核心进展，是认识到固体电子结构的几何属性——Berry 曲率 $\Omega_{ab}(\mathbf{k})$ 与量子度规 $g_{ab}(\mathbf{k})$——承载了量子材料对外界扰动响应的微观信息 [19]。这些"内禀几何量"不仅决定了霍尔效应、非线性输运等可观测量，也支撑了量子材料在阿秒尺度上对超快探测的全响应描述。把它们从材料中提取出来，构成量子几何计量学的核心问题。

**范本锚点**（style_benchmark.structure_pattern.立项依据 + citation_style）：
> 范本开篇：大背景（领域意义）→ 研究沿革（由远及近），"文献引用嵌入论证链：'某人等人[N]在期刊上报道了X'，正文引用 35-47 次"

**差距分析**：
- ✅ 行文风格：以"凝聚态物理过去十年的一个核心进展"切入大背景，符合范本"大背景→领域脉络"递进
- ✅ 文献嵌入：[19] 嵌入论证链（"承载了…微观信息 [19]"），非堆砌
- ⚠ 论证密度：范本要求每段 3–6 句、150–300 字；申请书第 1 段 3 句约 120 字，略短于范本密度
- ⚠ 引文密度：范本正文引用 35–47 次，申请书全文（3 章节）[n] 引用约 60 次，但集中在 rationale，content/scheme 引文密度偏低

**档位**：`scoring_rubric` 表达质量 0.7–0.8 档（叙述式主线对标范本，但段落密度略低 + 超长句拉低）

### 对比 2：研究方案方法选择——"为什么选这个方法" vs 范本锚点

**申请书原文**（scheme §3.1 R1 截止阶次部分）：
> 经典三步模型给出 $N_\text{cutoff}^\text{class} \approx (I_p + 3.17 U_p)/\hbar\omega$，该系数 3.17 来自原子体系 KFR 势垒电离机制；固体 HHG 的截止位置由能带色散、Bloch 轨迹与带间 Landé-Zener 跃迁共同决定，并不普适存在 3.17 这一常数。R1 的修正公式不以"3.17 经典极限"为对照基线，而以**同一固体能带模型下**经典 SBE 的截止位置为对照基线

**范本锚点**（style_benchmark + writing_style_rules.must：「研究方案要讲清楚'为什么选这个方法'」）：
> 范本要求：研究方案说明方法选择的物理理由，而非罗列步骤

**差距分析**：
- ✅ 方法选择理由：明确解释"为什么不沿用原子 3.17"（KFR 势垒电离 vs 固体能带色散），符合范本"为什么选这个方法"
- ✅ 物理论证：Bloch 轨迹 + Landé-Zener 跃迁的物理图像清晰
- ⚠ 句式节奏：该段连续 3 句均 >80 字，节奏偏密，与范本"短句为主，单句一般不超过 60 字"有差距

**档位**：`scoring_rubric` 表达质量 0.7–0.8 档（方法选择论证对标范本，但句式节奏偏离范本短句风格）

---

## 问题清单

### [critical] red_line — R8-C1：Silva [4] 与 Liu-Fu-Kais [3] 引文编号系统性互换

- **位置**：
  - rationale.md L9：「经典相干态（$g^{(2)}(0) = 1$）下的 HHG 谱与 Berry/度规之间的解析关系建立在 Floquet 平均之上 **[4]**」→ [4] = Silva（Sr₂CuO₃ Mott 绝缘体 HHG），但上下文说的是 Berry/度规反演解析关系，这是 Liu-Fu-Kais 的工作 → **应标 [3]**
  - rationale.md L15：「**Silva 等 [3]** 在 Sr₂CuO₃ 上建立了一维 Mott 绝缘体 HHG 的奠基性观察」→ [3] = Liu-Fu-Kais（量子几何反演），但主语是 Silva → **应标 [4]**
  - content.md L38：「团队已复现 **Liu、Fu 与 Kais [4]** 的 ZnO 偶次谐波偏振响应」→ [4] = Silva，但主语是 Liu-Fu-Kais → **应标 [3]**
  - scheme.md L29：「团队已复现 **Liu-Fu-Kais 2022 [4]** 的 ZnO 5 阶 14.2° / 7 阶 9.5° 偏振响应」→ 同上 → **应标 [3]**
  - scheme.md L165：「**Liu-Fu-Kais 2022 [4]** 与 Verma 2024 [9] 的固体 HHG 量子几何反演框架」→ 同上 → **应标 [3]**
  - scheme.md L173：「**Liu-Fu-Kais 2022 [4]** 与 Verma 2024 [9] 均指出经典单色场下 Ω/g 在偏振响应中几何混叠」→ 同上 → **应标 [3]**
- **问题**：references.md 明确标注 [3] = Liu-Fu-Kais（Phys. Rev. Res. 2022，量子几何反演框架）、[4] = Silva（Nat. Photonics 2018，Sr₂CuO₃ Mott HHG）。但正文中 6 处将两者编号互换。这是 P0 级引文归属错误——领域专家评审对照引文表即可发现，直接判定"作者对核心文献不熟悉"。
- **违反条款**：`indicator_red_lines.consistency_check`（同一指标/文献在不同章节口径必须一致）+ `indicator_red_lines.novelty_claim_cautious`（引文归属错误影响首创性论证可信度）
- **建议**：全文检索"Silva"和"Liu-Fu-Kais"/"Liu、Fu"，逐条核对每处引用编号。具体修正：
  - rationale L9：[4] → [3]
  - rationale L15：[3] → [4]
  - content L38：[4] → [3]
  - scheme L29/L165/L173：[4] → [3]
- **priority**：P1 必改
- **action**：verify + rewrite

### [high] red_line — R8-H1：R3' 启动时间跨章节不一致（Year 2 Q3 vs Year 3 Q1）

- **位置**：
  - rationale §1.4 Year 3（L79–83）：「启动 BSV 增强验证（R3'）」列在 **Year 3**；L81 明确「若 BSV 源 Phase 1 于 Year 2 Q3 前上线，R3' 在 **Year 3 Q1** 启动」
  - content §2.6 Year 2（L136）：「BSV 增强验证（R3'）推迟至 **Year 3 Q1**」
  - content §2.6 Year 3（L138）：「R3' 启动（Year 2 Q3 已上线 BSV 源）」——此处隐含 R3' 在 Year 3 启动
  - content §2.2（L44）：「**阶段二**（R3'，**Year 2 Q3** 启动）」← 与年度计划矛盾
  - scheme §3.1（L27）：「阶段二（R3'，**Year 2 Q3** 启动）」← 与年度计划矛盾
  - scheme §3.3（L63）：「R3 的 R3' 子任务（BSV 增强验证，**Year 2 Q3** 启动）」← 与年度计划矛盾
- **问题**：在"两阶段证据链"的叙述语境中（content §2.2、scheme §3.1/§3.3），R3' 启动时间写为 Year 2 Q3；但在年度研究计划中（rationale §1.4、content §2.6），R3' 启动时间写为 Year 3 Q1。两者相差一个季度。逻辑上 BSV 源 Year 2 Q3 上线后需要调试耦合，R3' 实际启动在 Year 3 Q1 更合理——但"两阶段证据链"段落中的"Year 2 Q3 启动"表述未与年度计划对齐。
- **违反条款**：`indicator_red_lines.consistency_check` + `general_principles.writing_style_rules.must`（各章之间必须逻辑呼应：研究方案↔年度计划）
- **建议**：统一为"Year 3 Q1 启动（Year 2 Q3 BSV 源上线后经一个季度耦合调试）"。修正 content §2.2 L44、scheme §3.1 L27、scheme §3.3 L63 的"Year 2 Q3 启动"为"Year 3 Q1 启动"。
- **priority**：P1 必改
- **action**：rewrite

### [high] anti_ai — R8-H2：content.md 超长句密度严重超标（52 句 >120 字）

- **位置**：content.md 全文，典型如：
  - L30（137 字）：条件单模态密度矩阵定义 + 偏迹物理含义压缩在一句
  - L44（>150 字）：加性/乘性两阶段证据链 + 三档分类 + 阶段一二逻辑压缩在一句
  - L104（>130 字）：训练阶段四阶段 + 数据增强 + MC Dropout + benchmark 数字压缩在一句
- **问题**：anti_ai_patterns.quantitative_thresholds 明确规定「超长句上限每段 3」（>120 字）。content.md 检出 52 句>120 字，平均每段远超 3 句上限。许多超长句的成因是把"判据 + 分类 + 降级路径 + 合作依赖"压缩在单句内，虽信息密度高但严重影响可读性。
- **违反条款**：`anti_ai_patterns.remove`「超长句：单句超过 80 字应拆分，超过 120 字属严重超长句」+ `quantitative_thresholds.超长句上限每段: 3`
- **建议**：对 content.md 的 52 句>120 字逐句拆分。拆分策略：
  1. 判据与分类分句：「Go 判据为 X。据此分为三档：…」
  2. 证据链叙述按阶段分句：「阶段一（Year 1 Q3）：…。阶段二（Year 3 Q1）：…」
  3. 合作依赖独立成句：「样品由 X 提供。tdDMFT 计算由 Y 提供。」
- **priority**：P2 强烈建议
- **action**：rewrite

### [high] anti_ai — R8-H3：scheme.md 超长句密度超标（35 句 >120 字）

- **位置**：scheme.md 全文，典型如 L13（条件单模态物理含义，>130 字）、L39（异常速度项 sin/cos 论证，161 字）、L67（靶标选择三点考量，>130 字）
- **问题**：同 R8-H2，scheme.md 35 句>120 字，平均每段超 3 句上限。
- **违反条款**：同 R8-H2
- **建议**：同 R8-H2 拆分策略
- **priority**：P2 强烈建议
- **action**：rewrite

### [medium] red_line — R8-M1：PINN 训练预算数字 full_review vs content/scheme 不一致

- **位置**：
  - full_review.md §3 数字表 L78：「PINN 总训练预算 | §2.5 第 96 行 | **50 GPU-day**」
  - content.md L106：「5 次完整训练 × ~9.5 GPU·天/次 ≈ **48 GPU·天**」
  - scheme.md L99：「5 次完整训练 × ~9.5 GPU·天/次 ≈ **48 GPU·天**」
- **问题**：full_review 的数字一致性核查表声称"17 项关键数字全部一致 ✓"，但 PINN 预算一项 full_review 自身记录为 50 GPU-day，而 content/scheme 实际写 48 GPU·天。full_review 的核查结论与实际文本不符。
- **违反条款**：`indicator_red_lines.consistency_check`
- **建议**：将 full_review.md L78 的"50 GPU-day"修正为"48 GPU·天"，与 content/scheme 一致。
- **priority**：P2 强烈建议
- **action**：verify + rewrite

### [medium] narrative — R8-M2：rationale §1.1 引文 [4] 上下文归属错误

- **位置**：rationale.md L9：「经典相干态（$g^{(2)}(0) = 1$）下的 HHG 谱与 Berry/度规之间的解析关系建立在 Floquet 平均之上 **[4]**」
- **问题**：此处论述的是"经典相干态下 Berry/度规反演的解析关系"，这是 Liu-Fu-Kais [3] 的核心贡献（Phys. Rev. Res. 2022，"Quantum geometry of the Berry curvature and quantum metric tensor from the high harmonic spectrum of solids"）。但标注为 [4]（Silva, Nat. Photonics 2018，Sr₂CuO₃ Mott HHG），Silva 的工作与"Berry/度规反演解析关系"无关。此归属错误与 R8-C1 属同一系统性问题的不同表现。
- **违反条款**：`indicator_red_lines.consistency_check`（已纳入 R8-C1）
- **建议**：已纳入 R8-C1 统一修正。[4] → [3]。
- **priority**：P1（随 R8-C1 统一修复）
- **action**：rewrite

### [medium] narrative — R8-M3：rationale.md 超长句偏多（6 句 >120 字 + 27 句 80–120 字）

- **位置**：典型如 L19（149 字，BSV 增强迁移判定标准）、L27（168 字，Faeyrman + arXiv:2606.06999 + Yang 综述证据链）、L71（126 字，R1 任务 4 编排）
- **问题**：同 content/scheme 超长句问题，但 rationale 严重程度较低（6 句>120 字 vs content 52 句）。
- **违反条款**：`anti_ai_patterns.remove`「超长句」+ `quantitative_thresholds.超长句上限每段: 3`
- **建议**：对 rationale 的 6 句>120 字逐句拆分，重点拆分 L19（判定标准分为"若…则…"和"若…则…"两句）和 L27（证据链按文献分句）。
- **priority**：P3 建议
- **action**：rewrite

### [medium] narrative — R8-M4：scheme §3.5 经费表 + 人力配置属"研究基础"内容，三段式下位置待确认

- **位置**：scheme.md L137–155（经费合理性论证表 + 经费明细边界澄清 + 人员费分层口径 + 人力配置）
- **问题**：NSFC 2026 面上三段式瘦身提质为"立项依据 + 研究内容 + 研究基础"，正文≤30 页。经费表和人力配置传统上属于"研究基础/可行性"模块。scheme 作为"研究方案"章节包含经费明细表和人员配置，在三段式框架下位置需确认——若提交系统的"研究基础"模块独立，此处经费表可能需迁移。
- **违反条款**：`content_boundaries`「内容放错了位置」+ `structural_reform_2026`「三段式」
- **建议**：确认 NSFC 2026 提交系统是否将经费/人员纳入"研究基础"独立模块。若是，scheme §3.5 经费表 + 人力段迁移至研究基础章节；若经费仍嵌入研究方案，保留但加注"（经费与人力配置详见研究基础章节）"。
- **priority**：P3 建议
- **action**：verify

### [low] anti_ai — R8-L1：content.md "显著"一词 14 次，接近上限

- **位置**：content.md 全文 14 处"显著"
- **问题**：anti_ai_patterns.quantitative_thresholds「冗余修饰词上限: 15」，14 次接近上限。"显著"在统计检验语境（"统计显著""显著差异"）有确切含义，但部分用法属冗余修饰。
- **违反条款**：`anti_ai_patterns.remove`「冗余修饰堆砌：显著」
- **建议**：区分"统计显著"（保留）与"显著提升/显著改善"（改为具体倍数或百分比）。
- **priority**：P3 建议
- **action**：rewrite

---

## 跨章节一致性专项审查

### 已确认一致的项（✅）

| 检查项 | rationale | content | scheme | 一致性 |
|--------|-----------|---------|--------|--------|
| BSV HHG 效率提升 10²–10³ 倍 | §1.1 L13 | §2.1/§2.2 | §3.1/§3.5 | ✅ |
| ZnO 5 阶偏振 14.2°（~5%） | §1.5 L103 | §2.2 L38 | §3.1 L29 | ✅ |
| ZnO 7 阶偏振 9.5°（~5%） | §1.5 L103 | §2.2 L38 | §3.1 L29 | ✅ |
| BSV g⁽²⁾(0) > 1.5 | — | §2.2 L42 | §3.1 L31 | ✅ |
| Si 耦合效率 ≥ 10⁻⁵ | — | §2.2 L42 | §3.1 L31 | ✅ |
| TiSe₂ CDW 相变 ~200 K | §1.4 | §2.4 L78 | §3.3 L59 | ✅ |
| 偏振各向异性突变 ≥ 2° | — | §2.4 L78 | §3.3 L73 | ✅ |
| PINN 单次训练 ~9 小时 V100 | — | §2.5 L104 | §3.4 L95 | ✅ |
| BSV 源 BBO type-II 非简并参量下转换 | §1.5 L99 | §2.2 L30/42 | §3.1 L13/31 | ✅ |
| 1T-TaS₂ Mott-CDW 红移 Δω/ω > 2% | — | §2.4 L82 | §3.3 L73 | ✅ |
| Bi₂Te₃ 体带隙 ~0.15 eV / 1.5 μm 非共振 | — | §2.3 L68 | §3.2 L51 | ✅ |
| R4 三档分层 Go 判据 | — | §2.5 L116–120 | §3.4 L107–111 | ✅ |
| f-sum rule 标度律 (1+0.5·U/W) | — | §2.5 L119 | §3.4 L111 | ✅ |
| 范围限定（不含 Mott/altermagnet/莫尔） | §1.3 | §2.1 L20 | §3.3 L67 | ✅ |

### 不一致的项（❌/⚠）

| 检查项 | 位置 A | 位置 B | 状态 |
|--------|--------|--------|------|
| Silva 引文编号 | rationale L15 标 [3] | references [4] | ❌ R8-C1 |
| Liu-Fu-Kais 引文编号 | content L38/scheme L29,165,173 标 [4] | references [3] | ❌ R8-C1 |
| R3' 启动时间 | content §2.2/scheme §3.1,§3.3 标 Year 2 Q3 | rationale §1.4/content §2.6 标 Year 3 Q1 | ❌ R8-H1 |
| PINN 总预算 | full_review L78 标 50 GPU-day | content/scheme 标 48 GPU·天 | ⚠ R8-M1 |

---

## 对抗结论

### 本轮问题统计

- **总计 9 个问题**（critical: 1, high: 3, medium: 4, low: 1）
- critical：R8-C1（引文编号系统性互换，6 处）
- high：R8-H1（R3' 时间矛盾）、R8-H2（content 超长句 52 句）、R8-H3（scheme 超长句 35 句）
- medium：R8-M1（PINN 预算数字）、R8-M2（rationale L9 引文归属，随 C1 修复）、R8-M3（rationale 超长句）、R8-M4（经费表位置）
- low：R8-L1（"显著"14 次）

### 相比上一轮（round-7）

- **改善**：round-7 识别的 5 项 medium + 2 项 low 问题中，C8-0（元话语块清除）、P0-1（占位符清除）、P0-2（特色创新精简）、P1-3（PINN 创新定位）均已确认修复。F-1/F-2/F-3/F-4 遗留问题也已在 content/scheme 中同步完成。
- **新发现**：本轮新发现 1 个 critical（引文编号互换——此前各轮均未检出，可能是 round-7 漏报或在编号调整后新引入）+ 1 个 high（R3' 时间矛盾——前几轮核查"17 项数字一致 ✓"时遗漏了启动时间维度）+ 2 个 high（超长句密度——此前各轮聚焦关联词/模板句式，未系统量化超长句）。
- **未解决**：超长句问题在 round-3/round-6 的写作风格核查中曾被定性提及（"工程化呈现扎实但论证骨架偏弱"），但未量化为"52 句>120 字"的硬数据，因此未触发 anti_ai_patterns 的定量阈值约束。本轮首次系统量化。

### 是否达标

**否**。综合评分 0.78 < general 面上阈值 0.80。

核心拉低因素：
1. [critical] R8-C1 引文编号互换 → 严谨性扣至 0.70（indicator_red_lines 触发）
2. [high] 超长句密度 → 表达质量 ai_detection_ceiling 0.75，实际 0.72
3. [high] R3' 时间矛盾 → 可行性受影响

### 返工优先级

| 优先级 | 问题 | 预计工时 |
|--------|------|----------|
| P1 | R8-C1：全文检索 Silva/Liu-Fu-Kais，逐条修正引文编号（6 处） | 30 分钟 |
| P1 | R8-H1：统一 R3' 启动时间为 Year 3 Q1（3 处） | 15 分钟 |
| P2 | R8-H2/R8-H3：拆分 content/scheme 超长句（87 句>120 字） | 3–4 小时 |
| P2 | R8-M1：full_review PINN 预算 50→48 | 5 分钟 |
| P3 | R8-M3/R8-M4/R8-L1 | 1 小时 |

### 下一轮（round-9）建议聚焦

1. **引文联网核实**：references.md 中 14 条预印本（[8] Tyulnev、[9] Verma、[11] Faeyrman、[12] Bauer、[13] Ikeda、[14] Sala、[15] Schätti、[16] Lange、[17]/[18] 作者待核实、[20] Lange、[21] Khurelbaatar、[22] Rivera-Dean、[23] Yang、[24] Sumaya-Martinez）的 arXiv 编号、作者、正式发表状态需逐条联网核实。优先核实 [14] Sala（正文 R2 验证依赖其样品体系）和 [13] Ikeda（R3 红移判据依据）。
2. **超长句拆分后的回归核查**：确认拆分后信息无遗漏、逻辑连贯性未降。
3. **R3' 时间线统一后的年度计划回归**：确认 rationale §1.4 / content §2.6 / scheme §3.1–§3.3 的 Year 2–Year 3 任务编排与 R3' 启动时间完全对齐。

---

## 评分
创新性：0.85
可行性：0.82
严谨性：0.70
表达质量：0.72
综合评分：0.78
