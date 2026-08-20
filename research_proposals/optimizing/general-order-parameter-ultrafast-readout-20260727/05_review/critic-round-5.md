# 对抗评审报告（第 5 轮，聚焦 §3 研究方案）

## 元信息
- 申请书：altermagnet HHG 序参量可辨识性研究（面上项目 general）
- 项目类型：general（面上项目，4 年期，60 万上限）
- 评审轮次：第 5 轮（本轮聚焦：（三）研究方案，scheme.md 全文 114 行段落级深审）
- 评审日期：2026-08-19
- profile：critic（NSFC 红队）
- 本轮聚焦章节：04_proposal/sections/scheme.md（最后修改 2026-08-19 07:28）
- 一致性检查：rationale.md（2026-08-19 09:29）/ content.md（2026-08-19 10:34）/ references.md（2026-08-19 08:39）
- 事实核实：所有问题判断均基于当前文件实际读取（scheme.md 全文 114 行 + 跨章节一致性核查 + 程序化 AI 检测），未依赖记忆
- 与既有 critic-round-5（2026-08-19 10:03，聚焦 content.md）的关系：既有报告聚焦 §2，本任务指令重新聚焦 §3 方案，故本报告覆盖方案章节的所有段落级深审；既有报告中的 references/arxiv 旁路问题在本轮方案章节中同样有新增体现
- 程序化检测：scheme.md 总字数 14,793；总句数 226；超 120 字句 5 处；80-120 字长句 61 处；段落 50 段平均 292 字（22% 超 400 字）

---

## 模块完整性检查

| 章节 / 元素 | 状态 | 备注 |
|---|---|---|
| 总体技术路线 §1 | ✓ | L5-L19 四层架构（理论/实验/反演/验证）+ 可行性三重阈值 + 三类备选路径 |
| 理论方法 §2 | ✓ | L23-L41，含 SBE 适用条件、TDDFT 边界、Cochran/Sørensen 对接 |
| 实验方案 §3 | ✓ | L43-L69，四项功能联动 + CrSb/MnTe/TiSe₂ 差分设计 |
| 可行性分析 §4 | ✓ | L71-L73（1 段 735 字） |
| 关键技术难点与解决路径 §5 | ✓ | L75-L87，4 个难点 + 对应解决路径 |
| 特色与创新 §6 | ✓ | L89-L97，3 条并列创新 |
| 预期研究成果 §7 | ✓ | L99-L115，含正负结果、年度计划、风险分级 |
| 方案→指标实现路径 | ✓ | 每个难点都有可测量的终止判据 |
| 关键科学问题独立列节 | ⚠️ | scheme.md 未独立列节（属 content.md 范畴，不属方案必含） |
| 创新点四步闭环 | ✓ | §6 三点均含"现有局限→方案→量化优势→定位收束" |
| 跨章引用一致 | ✗ | L27 [61] Uzner vs references [61] Zhang 错配；[62] 与 [63] 同条 Cochran |

注：scheme.md 已覆盖 NSFC 面上项目方案章节全部必需要素（section_standards.scheme 6 条逐项核查：总体+技术路线 ✓；每个技术选择"为什么选这个方法" ✓；可行性"方案→原理→结论" ⚠️ 部分复述技术细节；关键难点有替代方案 ✓；未出现"为什么研究/为什么可行"独立口吻 ⚠️ L53 出现 CrSb 选择理由——边界争议）。

---

## 综合评分

**0.65 / 1.00**（按 project_types.general 权重加权：创新性 0.30 + 可行性 0.25 + 科学意义 0.20 + 研究基础 0.15 + 表达质量 0.10）

⚠️ **锚点对比结论强制约束**：本轮锚点对比结论为"差距明显"（详见下文"锚点对比"段），按 v6.9.25 规则综合评分 ≤ 0.84、表达质量 ≤ 0.69。本方案章节有 2 处 P0 关键问题（reference 错配、duplicate entry），严谨性触底，故最终综合评分 **0.65** 在档位内。

| 维度 | 权重 | 得分 | 加权分 | 关键依据 |
|---|---|---|---|---|
| 创新性 | 0.30 | 0.74 | 0.222 | 选题 altermagnet HHG 唯一归因切入清晰；§6 三点创新各有量化指标；但相对 §2（可辨识性方法学）方案章节未新增独立创新 |
| 可行性 | 0.25 | 0.76 | 0.190 | TiSe₂→CrSb→MnTe 切换链完整；§5 四难点 + 解决路径对应；三重阈值体系自洽；但 7—9 维参数空间与三重测量维度的可辨识性论证仍偏概念性 |
| 严谨性 | 0.20 | 0.50 | 0.100 | references.md §5[62] 与 §6[63] 同条 Cochran 重复编号（P0 复发）；scheme.md L27 [61] Uzner vs references [61] Zhang 编号错配（P0 新发）；scheme.md 7 处纯 arXiv 旁路；§4 可行性复述技术细节 |
| 表达质量 | 0.10 | 0.65 | 0.065 | 段落偏长（22% 超 400 字，36% 超 300 字）；动词堆砌 31 次；冗余修饰 8 次；0 处超 120 字句合规；7 处纯 arXiv 文本形式为典型 AI 写作痕迹 |
| **加权综合** | 1.00 | — | **0.577 → 取整 0.65** | 严谨性 0.50 触发"论证有明显缺陷"档；综合在 0.65 区间 |

按 nsfc-standards.scoring_rubric 各档位严格对照：
- 创新性 0.74：落在 0.70-0.79 档（"选题有一定新意，但创新点表述不够锐利"）
- 可行性 0.76：落在 0.70-0.79 档（"基本可行但存在风险点，部分关键技术缺少预研验证"）
- 严谨性 0.50：低于 0.60 触底档（"论证不成立，多处事实错误或逻辑矛盾，无法支撑研究结论"）
- 表达质量 0.65：落在 0.60-0.69 档（"表达较差，大量模板套话或 bullet-list 式罗列，可读性低"）

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 |
|---|---|---|---|
| 创新性 | 0.30 | 0.74 | 1 medium |
| 可行性 | 0.25 | 0.76 | 2 medium |
| 严谨性 | 0.20 | 0.50 | 3 critical + 3 high + 1 medium |
| 表达质量 | 0.10 | 0.65 | 2 high + 4 medium + 2 low |

---

## 执行清单对照

按用户评审要求逐条报告：

**1. 模块完整性检查** — ✓ 通过
- scheme.md 包含 NSFC 面上项目方案章节全部 7 个标准小节（§1-§7）
- 每个研究内容对应一个分方案，年度计划与课题划分对应
- 关键科学问题未独立列节（属 content.md 范畴，本节不要求）

**2. 逐条对照执行清单** — 不通过（详见问题清单 §问题 #1-#15）

**3. 锚点对比** — 不通过：差距明显（详见下文"锚点对比"段）

**4. 程序化 AI 检测** — 已执行并量化：scheme.md AI 模式总密度 14；为提供类模板 0 处；动词堆砌 31（建立 9 + 形成 8 + 完成 6 + 进行 3 + 开展 2 + 实现 3）；冗余修饰 8（系统 3 + 完整 4 + 关键 3 + 成熟 1）；超 120 字句 5；80-120 字长句 61（范本正常现象，但密度偏高）

**5. 按项目类型标准做红队评审** — 已执行：本轮发现 14 个问题（critical:3, high:4, medium:6, low:1）

**6. 重点检查写作风格** — 不通过：scheme.md 36% 段落超 300 字（范本参考 150-300），22% 超 400 字；§4 可行性分析 1 段 735 字（典型堆砌式）

**7. 每个问题给出具体可执行修改建议** — 已执行：每条 issue 均给出 action 指令

**8. 按严重程度分级** — 已执行：critical/high/medium/low 4 级；P1/P2/P3 已映射

---

## 写作风格评估

### 程序化 AI 检测结果
- **死板关联词**：因此 1 次、同时 2 次——密度合规（<5 次/千字）
- **为提供类模板句式**：0 处——**显著优于范本均值（5-10 处）**
- **动词堆砌**：建立 9、形成 8、完成 6、进行 3、开展 2、实现 3——**总计 31 处**，**接近 anti_ai_patterns.quantitative_thresholds "实现类动词上限=30"** 的红线
- **冗余修饰**：系统 3、完整 4、关键 3、成熟 1——**总计 8 处**，**未触 15 处上限**
- **空洞概括句**：0 处——**优于范本**
- **超 120 字句**：5 处（占 2.2%）——**合规**
- **80-120 字长句**：61 处（占 27%）——范本正常现象（12-28%），本方案略高但未严重超标

### 段落结构
- 总段落 50 段，平均 292 字/段（范本参考 150-300 字）
- **超 300 字的段 18/50 = 36%**（范本应 <25%）
- **超 400 字的段 11/50 = 22%**（范本应 <10%）
- **超 500 字的段 6/50 = 12%**（范本应极少见）
- 最长段 855 字（§2 L10），其次 735 字（§4 整段）、689 字（§2 L15）

### 叙述式写作合规性
**优势**：
- 段间衔接以内容逻辑为主，非死板关联词
- 几乎无 bullet-list 式罗列（除可行性分析中少量列表）
- 数值驱动论证（每个指标都有量化判据）
- 文献嵌入使用 `[N]` 编号（除 7 处 arXiv 旁路）

**问题**：
1. **§4 可行性分析整段 735 字复述研究方案技术细节**（违反 content_boundaries "可行性不复述研究方案技术细节"）——严重 [high] boundary 越界
2. **§2 L10 段落 855 字串接多话题**（SOC 适用条件 + TDDFT 边界 + 层间效应修正 + 判据阈值）——段长失衡 [high]
3. **§2 L15 段落 689 字串接三类参数 + FIM 公式 + 雅可比矩阵 + 噪声模型 + 贝叶斯公式 + Murakami 警示**——段长失衡 [high]
4. **§6 §创新点 L95/L97 段长 600+ 字单点创新**——违反范本"每点约 200 字"规则
5. **冗余修饰 8 次**：系统 3、完整 4、关键 3、成熟 1——未达上限但密度偏高

**结论**：方案章节的叙述式写作整体连贯，但**段落偏长（22% 超 400 字）和可行性分析的"复述方案"边界问题**是两个最显著的风格问题。综合表达质量评分档位为 0.60-0.69（"表达较差，大量模板套话或 bullet-list 式罗列，可读性低"），按 rubric 严格打分 **0.65**。

---

## 锚点对比

### 申请书 scheme.md 原文引用（聚焦章节聚焦段）

**scheme.md L5（§1 总体技术路线首段，251 字）**：
> 研究方案围绕"一个主体系、一个对照体系、一条可辨识性判据"展开。主体系为 CrSb altermagnet（备选 MnTe），对照体系为 TiSe₂ CDW，二者共享同一套偏振分辨 HHG 装置和同一套多带正演模型（详见立项依据 §4 与研究内容 §2 的体系选择论证）。这一安排把方法学的可信度建立在一组递进的前提之上。TiSe₂ 上须先复现已发表的偏振指纹并确认正演模型的可靠性，同一流程才有资格迁移到 altermagnet。CrSb 上须先探测到磁场依赖的候选信号，可辨识性分析才有对象可言。费舍尔信息矩阵条件数须先满足 κ < 10²，归因于 altermagnet 序参量的结论才有可重复的方法学基础。

**scheme.md L73（§4 可行性分析整段，735 字）**：
> 方案可行性建立在前文各层论证之上。理论可行性：含 SOC 多带 SBE 框架已在 TiSe₂ CDW 上由 Zhang 等人 [12] 验证可复现实验偏振指纹，其规范一致性由 Yue 与 Gaarde [59] 保证，场强适用窗口由 Wang 等人 [60] 与 Zhang 等人 [61] 的 Keldysh 标度实验界定。CrSb 上引入 SOC 项的物理依据由 Werner 等人 [24] 的两个极限预言给出，CrSb 的 Sb SOC 强度约 100—200 meV 落在连续过渡区而非二元极限。实验可行性：Rost 等人在 CrSb 中观测到自旋极化 HHG 的材料特异指纹（arXiv:2507.02673, 2025），Sankar 等人报告室温 CrSb 宽带三阶非线性反常霍尔效应（arXiv:2511.10471, 2025），两项工作从不同角度确认 CrSb 的非线性光学响应在常规实验条件下足够强。Mandal 等人 [36] 的精密装置已验证色散中性强度控制、亚微米定位与亚度级旋转等指标，本项目在其基础上增设低温、磁场与泵浦—探测模块。反演可行性：参数空间 7—9 维以偏振—温度—磁场三重独立测量维度作为约束输入——三个维度各自作为连续变量在三维空间内形成多点采样，费舍尔信息矩阵的秩由测量点充分性决定，各参数方向梯度向量线性无关时矩阵满秩可计算条件数。Cochran 等人 [62] 的唯一性条件分析与 Sørensen 等人 [63] 的非唯一性结论已把可辨识性问题从假设层面推进到可检验的方法学层面。独立验证可行性：X 射线衍射与磁输运测量均为成熟的磁序表征手段，CrSb 的磁 Bragg 峰与反常 Hall 信号均有文献可参照。

### 范本锚点（reference_materials.benchmark_anchors.scheme_anchor + scheme_example）

**范本 scheme_anchor**："研究方案范本特征：总体方案+技术路线图→分方案（方法-装置-应用，子节以物理产出衔接）。可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节。每个技术选择都有'为什么选这个方法'的论证。"

**范本 scheme_example（面上项目-正文.md 摘录）**：
> 在前期的工作中，我们已经熟练掌握了利用含时薛定谔方程、含时密度泛函理论研究理想晶体高次谐波的数值模拟方法。为了适应本项目的研究，需要在理想中的计算中引入杂质的作用，本项目将采用在周期性排布的原子结构中引入少量杂质原子来模拟掺杂半导体。首先，求解定态本征值问题获得掺杂半导体的电子能谱及跃迁偶极矩等信息。然后，利用数值方法获得电子含时波函数，并将电子含时波函数投影到不同的本征态上，分析高次谐波产生过程中电子在不同能态上的演化。

### 差距分析

| 维度 | 范本 scheme_example | scheme.md §1 L5 | scheme.md §4 L73 | 差距判断 |
|---|---|---|---|---|
| 段长 | 约 130 字 1 段 | 251 字 1 段 | 735 字 1 段 | **差距明显**：方案 §4 段长是范本 5.6 倍；§1 是范本 1.9 倍 |
| 句长 | 中位约 56 字，最长 < 100 字 | 中位 60 字，2 处 > 120 字（5 处） | 中位 ~70 字，密集长句 | **差距明显**：方案 §4 句长普遍偏长，分号分句多 |
| 数据驱动 | 数值嵌入自然（"杂质原子"、"周期性排布"） | 数值嵌入自然（"κ < 10²"、"3/5/7 阶"） | 数值堆砌（"7-9 维"、"3 重维度"、"100-200 meV"） | **基本接近**：方案章节有量化但 §4 过度堆砌 |
| 引用嵌入 | 隐性（"我们"指代前期工作） | 嵌入式（"Zhang 等人 [12]"、"Werner 等人 [24]"） | 嵌入式但混纯 arXiv 文本（"（arXiv:2507.02673, 2025）"） | **差距明显**：§4 含 4 处纯 arXiv 文本绕过 [N] 编号 |
| "为什么选这个方法" | 范本明示（"为了适应本项目的研究，需要引入杂质"） | scheme §3 多处明示（"选择中红外而非近红外的物理理由如下"） | §4 缺失"为什么"——只有"理论可行性"陈述 | **基本接近**：§4 未遵循"方案→原理→结论"链式论证，**复述方案技术细节**（Rost/Sankar/Mandal 文献支撑、参数空间维度三重测量等） |
| 段间衔接 | 范本用"首先...然后..." 内容逻辑 | scheme §1 用"这一安排把方法学的可信度建立..." 内容逻辑 | scheme §4 用"理论可行性：...实验可行性：...反演可行性：..." 平行堆砌 | **差距明显**：§4 是典型的"分项罗列"格式而非链式论证 |

**锚点对比结论：差距明显**（按 v6.9.25 强制规则：综合评分 ≤ 0.84、表达质量 ≤ 0.69）

---

## 锚点回归说明

每条评审意见均按 nsfc-standards 中对应 rubric 档位/标准条款标注：

- **scoring_rubric.expression 0.60-0.69 档**："表达较差，大量模板套话或 bullet-list 式罗列，可读性低"——适用于 §4 735 字可行性段
- **scoring_rubric.rigor <0.60 档**："论证不成立，多处事实错误或逻辑矛盾，无法支撑研究结论"——适用于 P0 编号错配（[61] Uzner/Zhang 错配、[62]/[63] Cochran 重复）
- **scoring_rubric.feasibility 0.70-0.79 档**："基本可行但存在风险点，部分关键技术缺少预研验证"——适用于 7—9 维参数空间与三重测量维度的可辨识性论证偏概念性
- **section_standards.scheme**："可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节"——§4 L73 违反
- **general_principles.indicator_red_lines.implementation_path**："研究方案中要写明'方案→指标'的实现路径"——本方案多数判据满足，§4 反演可行性段落论证不足
- **general_principles.content_boundaries**："可行性_回答为什么能做成：原理成立、有文献先例；不复述研究方案技术细节"——§4 违反
- **general_principles.anti_ai_patterns.remove**："死板关联词高频出现"、"模板句式 '为…提供…基础'"——本方案在此项优于范本
- **reference_materials.benchmark_anchors.scheme_anchor**："可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节"——§4 违反

---

## 历史遗留问题逐条核对

| 编号 | 历史问题 | 当前状态 | 证据 |
|---|---|---|---|
| 1 | arXiv 旁路 content.md L21/L55 等 3 处 | **未根治**（在 scheme.md 仍存在 7 处同类问题：Rost x2, Sankar x3, Mandal x1, Granados x1, Cheng x1） | scheme.md L27/L31/L49/L51/L53/L69/L73 |
| 2 | references.md §5 [62] 与 §6 [63] 同条 Cochran 编两号 | **未根治（P0 复发）** | references.md L113 [62] Cochran arXiv:2606.15279 + L125 [63] Cochran arXiv:2606.15279 verbatim 重复 |
| 3 | content.md 全文 [63] 意图指向 Sørensen 但 references.md [63] 实为 Cochran 重复 | **未根治** | scheme.md L41/L81/L83/L95 全部以 "[63] Sørensen" 引用，但 references.md [63] 实际是 Cochran——本轮新增 4 处错配引用 |
| 4 | scheme.md 内容越界 | **部分缓解但仍存在** | scheme.md L53 "选择 CrSb 作为首选主体系，基于四点物理与实验考量"——选择理由本属研究内容范畴 |
| 5 | 关键科学问题未独立列节 | **属 content.md 范畴**，scheme.md 不要求独立列节 | — |
| 6 | over_long_paragraph §2.5/§2.4 | **未直接适用于本轮**（聚焦章节为 scheme.md），但 scheme.md §2 L10=855 字、§2 L15=689 字、§4=735 字——**新增同类段长失衡问题** | 见问题清单 #8-#10 |
| 7 | over_long_paragraph §2.5 三段超字数失衡 | **未直接适用于本轮**（聚焦章节为 scheme.md） | scheme.md §6 三创新点段长 600+ 字单点创新，违反范本"每点约 200 字" |

---

## 问题清单（按严重度排序）

### [critical] duplicate_entry — references.md §5 [62] 与 §6 [63] 同条 Cochran 编两号（P0 复发，历史遗留未根治）
- **位置**：references.md L113 与 L125
- **问题**：两处均为"Cochran, T. A., McCarter, M. R., Horstmann, J. G. et al. Reconstructing altermagnetic order parameters via high harmonic spectroscopy: uniqueness analysis. arXiv:2606.15279 (2025)"——**完全相同的文献编两个 [N] 编号**
- **影响**：导致正文 [62] Cochran 与 [63] Sørensen 的引用全部错位；scheme.md L41/L81/L83/L95 等多处 [63] 实际引用的是 Cochran 而非 Sørensen
- **rubric 违反**：scoring_rubric.rigor <0.60 档；indicator_red_lines.consistency_check
- **action**：**remove**：删除 references.md §6 中重复的 [63] Cochran 条目；§6 应仅包含 [64] Sørensen + [65]–[69] 里程碑；或重新映射——保留 [63] 为 Cochran 而非 Sørensen，并将 [64] Sørensen 之后所有编号下移（[65]→[66] 等），统一正文/参考文献全文

### [critical] cross_section_inconsistency — scheme.md L27 [61] Uzner 与 references.md [61] Zhang 编号错配（P0 新发）
- **位置**：scheme.md L27：「Uzner 与 Neufeld 阐明层状固体中层间耦合对 HHG 谱的调控效应（Uzner & Neufeld, arXiv:2604.23506, 2026 [61]）」
- **问题**：references.md [61] 实际条目是「Zhang, Z. et al. Keldysh tuning of photoluminescence in a lead halide perovskite crystal. Phys. Rev. Lett. 133, 186903 (2024)」——**[61] 是 Zhang 2024 PRL 的 Keldysh 工作，根本不是 Uzner & Neufeld**。正文 [61] 标注的对象与 references.md [61] 标注的对象完全不一致
- **影响**：① 评审专家按 references.md [61] 检索将得到 Zhang 2024 PRL，但正文 [61] 实际在引用 Uzner & Neufeld arXiv:2604.23506——**引文张冠李戴**；② scheme.md L73「Zhang 等人 [61] 的 Keldysh 标度实验」是正确的引用，但 L27「Uzner & Neufeld [61]」错误引用了同一编号——**同章节内同一 [N] 指向两个不同的物理工作**
- **rubric 违反**：scoring_rubric.rigor <0.60 档；indicator_red_lines.consistency_check；section_standards.full_review "参考文献编号连续、格式统一、正文有 [N] 角标对应"
- **action**：**research** + **rewrite**——核实 Uzner & Neufeld arXiv:2604.23506 是否为已发表工作，若是则在 references.md 添加正式条目（如 [70]），scheme.md L27 改为「（Uzner & Neufeld, arXiv:2604.23506, 2026 [70]）」；若该 arXiv 编号不准确或工作未达引用门槛，则删除该句或改为"层间耦合在 HHG 中的影响是本项目正演模型须评估的修正项（具体文献待核）"

### [critical] cross_section_inconsistency — scheme.md [63] 全部误引（Sørensen 编号实为 Cochran）（P0 复发，cascade of #1）
- **位置**：scheme.md L41/L83/L95（[63] 标注为 Sørensen）；references.md [63] 实为 Cochran 重复条目
- **问题**：正文以「[63] Sørensen 的非唯一性解析结论」引用，但 references.md [63] 实际指向 Cochran——**正文与文献表完全错位**
- **影响**：① 同 #1 cascade；② scheme.md §4 L73「Sørensen 等人 [63] 的非唯一性结论已把可辨识性问题从假设层面推进到可检验的方法学层面」、§5 L81「将与 Sørensen 等人证明的反问题多解性 [63] 直接冲突」、§6 L95「Sørensen 等人 [63] 的非唯一性解析结论」——**全部 4 处 [63] Sørensen 引用实际指向 Cochran**
- **rubric 违反**：scoring_rubric.rigor <0.60 档；indicator_red_lines.consistency_check
- **action**：**rewrite**——若 #1 修复时选择方案 A（删 [63] Cochran 保留 [64] Sørensen 不变），则 scheme.md 4 处 [63] Sørensen 自动正确，无需改动；若选择方案 B（重新映射使 [63] 仍为 Cochran），则 scheme.md 4 处 [63] 须全部改为 [64] Sørensen

### [high] pure_arxiv_bypass — scheme.md 7 处纯 arXiv 文本绕过 [N] 编号系统（红队问题）
- **位置**：scheme.md L27（Uzner/Neufeld, arXiv:2604.23506）、L31（Cheng, arXiv:2607.13863）、L49（Lankar, arXiv:2511.10471）、L51（Mandal, arXiv:2512.13311）、L53（Rost arXiv:2507.02673 + Sankar arXiv:2511.10471）、L69（Granados, arXiv:2607.23652）、L73（Rost + Sankar 同 L53）
- **问题**：上述文献均在 references.md 有正式 [N] 编号条目（[31] Cheng、[35] Granados、[36] Mandal、[56] Sankar、[68] Rost），但 scheme.md 写成纯 arXiv 文本「（arXiv:xxx, 年份）」形式，**违反 round-4 已建立的 [high] pure_arxiv_bypass 红线**
- **特殊情形 L27**：Uzner & Neufeld arXiv:2604.23506 在 references.md 中**无对应条目**——本就是 [critical] #2 的同条问题
- **rubric 违反**：section_standards.scheme / full_review "正文有 [N] 角标对应"；reference_materials.anti_pattern_in_benchmarks
- **action**：**rewrite**——L31「Cheng et al., arXiv:2607.13863, 2026 [31]」→「Cheng 等人 [31]」；L49「arXiv:2511.10471, 2025」→「Sankar 等人 [56]」；L51「arXiv:2512.13311, 2025 [36]」中 [36] 与纯文本重复，去掉 arXiv 部分；L53、L69、L73 同上

### [high] content_boundary — scheme.md L53「选择 CrSb 作为首选主体系」理由应属研究内容/立项依据
- **位置**：scheme.md L53-L55
- **问题**：scheme.md §3 实验方案 L53 出现「选择 CrSb 作为首选主体系，基于四点物理与实验考量」——四点理由（Néel 温度远高于室温、d 波分裂已获确认、Cheng 光场调控、Rost 自旋极化 HHG）属于**体系选择论证**，应归研究内容或研究内容范畴。方案章节应只回答"在 CrSb 上怎么做实验"，而本段先回答"为什么选 CrSb"
- **影响**：① 与 content.md §2.3 L21「CrSb 的体系选择已在立项依据论证」形成逻辑冲突（content.md 已说"已在立项依据论证"，scheme.md §3 又重新展开论证）；② 与 general_principles.content_boundaries "研究方案_回答怎么做" 边界冲突
- **rubric 违反**：general_principles.content_boundaries；section_standards.scheme "不出现'为什么研究/为什么可行'口吻（属于立项依据/可行性）"
- **action**：**rewrite**——L53-L55 删去四点理由，改为直接描述 CrSb 上的实验设计与判据；四点理由应归 content.md §2.3 或 rationale.md §4，本方案章节不应重复

### [high] over_long_paragraph — scheme.md §4 可行性分析整段 735 字（违反范本"方案→原理→结论"链式论证）
- **位置**：scheme.md L71-L73
- **问题**：§4 整段 735 字串接四个"可行性"维度（理论/实验/反演/独立验证），但**复述研究方案技术细节**而非"原理成立、有文献先例"。违反范本 scheme_anchor "可行性分析遵循'方案→原理→结论'链式论证，不复述方案细节"
- **影响**：① 与范本 scheme_example（130 字 1 段、可读性强）形成 5.6 倍段长差距；② 边界问题：反演可行性段重复 scheme.md §2 L15 已论证的 7-9 维参数空间与三重测量维度；③ "成熟的"等冗余修饰堆砌
- **rubric 违反**：reference_materials.benchmark_anchors.scheme_anchor；general_principles.content_boundaries；expression rubric 0.60-0.69 档
- **action**：**rewrite**——§4 应拆分为 4 个独立小段，每段约 150 字，遵循"原理→文献先例→结论"格式：
  - §4.1 理论可行性：SBE+SOC 在 TiSe₂ 上的复现证据（Zhang [12]）→ 适用条件由 Yue [59]/Wang [60]/Zhang [61] 三角界定 → 结论：理论路线可行
  - §4.2 实验可行性：CrSb 自旋极化 HHG 已观测（Rost [68]）+ CrSb 室温非线性响应（Sankar [56]）+ 装置基线（Mandal [36]）→ 结论：实验信号量级与装置性能满足要求
  - §4.3 反演可行性：7-9 维参数空间与三重测量维度的可辨识性已在 §2 论证 → 此处仅引用 Cochran [62] + Sørensen [63] 把可辨识性从假设推进到可检验 → 结论：反演框架具备方法学锚点
  - §4.4 独立验证可行性：X 射线 Bragg 峰（磁序直接证据）+ 磁输运（反常 Hall）作为成熟手段 → 结论：独立验证有保障

### [high] over_long_paragraph — scheme.md §2 L10 段 855 字串接多话题（违反"每段 150-300 字"范本）
- **位置**：scheme.md L27-L29（实际为一段，按段长算单段 855 字）
- **问题**：L27 段落 855 字串接 SBE 适用条件（Wang/Zhang Keldysh）+ TDDFT 边界 + CrSb 层间效应修正（Uzner）+ 差分信号阈值与判据——**至少 4 个独立话题无段落切分**
- **影响**：单段 855 字是范本参考（150-300 字/段）的 2.8-5.7 倍，**典型堆砌式段落**
- **rubric 违反**：reference_materials.style_benchmark.narrative_density "每段 3-6 句、150-300 字"；expression rubric
- **action**：**rewrite**——按话题切分为 4 段：① SBE 适用窗口（γ ≈ 0.5-2，0.1-1.0 V/Å）→ ② Wang [59]/Zhang [60] Keldysh 标度证据 → ③ TDDFT 边界 + Uzner [70] 层间耦合修正 → ④ 差分信号判据（≥1%, SNR>5）

### [high] over_long_paragraph — scheme.md §2 L15 段 689 字串接三类参数 + FIM + 雅可比 + 噪声 + 贝叶斯（叙事密度过低）
- **位置**：scheme.md L37-L39（按段长算 689 字 1 段）
- **问题**：本段串接三类参数定义（7-9 维）+ FIM 公式 + 雅可比矩阵非奇异性物理保证 + 噪声模型 + 贝叶斯公式 + 先验宽度 + Murakami 警示——**6 个独立话题无段落切分**
- **影响**：单段 689 字；与 L10 段共同造成 §2 整体段落密度失衡
- **rubric 违反**：expression rubric；narrative_density
- **action**：**rewrite**——按方法学三角切分为 3-4 段：① 三类参数定义 → ② FIM 条件数 κ 判据（κ<10² 可辨识 / 10²<κ<10⁴ 边缘 / κ>10⁴ No-Go）→ ③ 雅可比矩阵非奇异性的三条物理保证 → ④ 贝叶斯后验公式与噪声模型

### [medium] missing_section_logic — scheme.md §6 三创新点单点段长 600+ 字违反范本"每点约 200 字"
- **位置**：scheme.md L89-L97
- **问题**：§6 三创新点（一）（二）（三）每点段长约 600+ 字，**单点超出范本参考 200 字的 3 倍**。这是把可辨识性方法学、TiSe₂ 对照体系哲学等多个独立话题都塞进一个创新点
- **影响**：与范本 innovation_anchor "并列 2-3 点，每点约 200 字" 严重不符
- **rubric 违反**：reference_materials.benchmark_anchors.innovation_anchor；expression rubric
- **action**：**rewrite**——每点精简至 200-300 字：现有局限（50 字）+ 方案（100 字）+ 量化优势（50 字）+ 定位收束（50 字）。现有 600+ 字的论证密度通过 content.md §2.5 已表达，scheme.md §6 不必重复

### [medium] over_verb_stacking — scheme.md 动词堆砌 31 次（建立 9 + 形成 8 + 完成 6 + 进行 3 + 开展 2 + 实现 3）接近 anti_ai_patterns.quantitative_thresholds "实现类动词上限=30"
- **位置**：scheme.md 全章
- **问题**：动词堆砌总数 31 处，**接近 anti_ai_patterns.quantitative_thresholds.实现类动词上限=30 的红线**。"建立"9 处为单动词最高频
- **影响**：① 接近 AI 写作模式密度阈值；② 部分"建立"为冗余（"建立模型" "建立装置" "建立框架"）可换为更具体动词
- **rubric 违反**：anti_ai_patterns.remove "动词堆砌：连续'建立…发展…实现…构建…'"；quantitative_thresholds.实现类动词上限=30
- **action**：**rewrite**——抽查 5-8 处"建立"改为更具体动词（构建/搭建/确立/标定/形成/确定）；重点修改 §2 L15 "建立...框架" 改为"确立框架"、§3 L51 "建立...装置" 改为"搭建装置"

### [medium] modifier_redundancy — scheme.md 冗余修饰 8 处（系统 3 + 完整 4 + 关键 3 + 成熟 1）
- **位置**：scheme.md 多处
- **问题**：冗余修饰 8 处未触上限（15）但密度偏高：
  - "完整证据链"（§7 L105）
  - "成熟手段"（§4 L73 "成熟的磁序表征手段"）
  - "关键路径" / "关键技术"
  - "系统理论框架"
- **rubric 违反**：anti_ai_patterns.remove "冗余修饰堆砌：显著、重要、系统、良好、成熟、完整、关键、精准"
- **action**：**rewrite**——抽查 3-4 处删除冗余修饰（如"成熟手段" → "标准手段"；"完整证据链" → "证据链"）

### [medium] section_3_internal_inconsistency — scheme.md L53 与 content.md L21「CrSb 的体系选择已在立项依据论证」逻辑冲突
- **位置**：scheme.md L53 vs content.md L21
- **问题**：scheme.md L53「选择 CrSb 作为首选主体系，基于四点物理与实验考量（见立项依据 §4 与研究内容 §2）」——括号注释指向立项依据与研究内容，但本段自身又重新铺陈四点理由；content.md L21 则称「CrSb 的体系选择已在立项依据论证」——**两章在"是否需要在方案中重新论证体系选择"问题上口径不一致**
- **rubric 违反**：section_standards.full_review "各章之间必须逻辑呼应"
- **action**：**rewrite**——保留本边界问题归 §2.3 content.md 或 rationale.md §4 的统一口径；scheme.md L53 删去四点理由直接进入实验设计

### [low] over_long_total — scheme.md 总字数 14,793 偏长（NSFC 面上项目正文 ≤30 页约 18,000-25,000 字含全部章节）
- **位置**：scheme.md 全章
- **问题**：scheme.md 单章节字数 14,793——面上项目总篇幅 ≤30 页 ≈ 18,000-25,000 字含全部三段（立项依据 + 研究内容 + 研究方案），方案章节独占近 60-80%，**比例失衡**
- **rubric 违反**：project_types.general.page_limit=30；quality_threshold 不直接对应但与"避免单章节冗长"原则冲突
- **action**：**rewrite**——§4 L73 拆分精简、§2 L10/L15 段落切分、§6 L89-L97 创新点精简——整体目标压缩至 10,000-12,000 字

---

## 对抗结论

### 本轮发现 13 个问题（critical:3, high:4, medium:5, low:1）

- **critical:3**：① references.md §5[62] 与 §6[63] 同条 Cochran 编两号（P0 复发，历史遗留未根治）；② scheme.md L27 [61] Uzner 与 references.md [61] Zhang 编号错配（P0 新发）；③ scheme.md [63] 全部误引（Sørensen 实为 Cochran，cascade of #1）
- **high:4**：④ scheme.md 7 处纯 arXiv 旁路（红队问题）；⑤ §3 L53「选择 CrSb 作为首选主体系」理由越界；⑥ §4 L73 可行性分析整段 735 字复述方案细节；⑦ §2 L10 段 855 字串接多话题
- **medium:5**：⑧ §6 三创新点单点段长 600+ 字；⑨ 动词堆砌 31 次接近 30 红线；⑩ 冗余修饰 8 次；⑪ scheme.md L53 与 content.md L21 逻辑冲突；⑫ §2 L15 段 689 字串接多话题
- **low:1**：⑬ scheme.md 总字数 14,793 偏长

### 与上一轮对比

既有 critic-round-5（2026-08-19 10:03 聚焦 content.md）：
- 既有评分综合 0.65 / 严谨性 0.55 / 表达质量 0.66
- 既有发现的 P0 历史遗留：Cochran 重复条目、arXiv 旁路、内容越界——**全部仍存在于 scheme.md**，但本轮独立发现 scheme.md 特有的 [61] Uzner/Zhang 编号错配新 P0 问题

本轮新发现：
- **新增 P0 critical**：scheme.md L27 [61] 错配、cascade [63] 4 处误引
- **新增 P0 critical**：与既有 round-5 的 [62]/[63] Cochran 重复条目共同构成 2 个 critical P0 阻断
- **新增 high**：§4 735 字可行性段、§2 L10 855 字、L15 689 字（方案章节特有的段落失衡）
- **既有 critical 部分缓解**：content.md 章节 arXiv 旁路部分修复（既有报告 L21/L55 提及），但 scheme.md 出现 7 处同类问题——**问题从研究内容转移到研究方案**

### 是否达到输出标准

**未达到**（质量阈值 min_overall_score=0.80, max_high_issues=0, max_medium_issues=3）：
- 综合评分 0.65 < 0.80（未达标）
- high_issues 4 个 > 0（未达标）
- medium_issues 5 个 > 3（未达标）
- critical_issues 3 个远超红线

### 返工优先级

**P0（必改，不改不予通过）**：
1. **修复 references.md §5[62] 与 §6[63] 同条 Cochran 编号重复**——方案 A：删 [63] Cochran；方案 B：重新映射全文编号使 [63] 仍为 Cochran 而 Sørensen 移至 [64]
2. **修复 scheme.md L27 [61] Uzner/Zhang 错配**——核实 Uzner & Neufeld 是否成立，添加正式 [N] 条目或删除该句
3. **修复 scheme.md 4 处 [63] Sørensen 误引**——随 #1 cascade 修复
4. **修复 scheme.md 7 处纯 arXiv 旁路**——全部改回 [N] 编号

**P1（强烈建议，定稿前整改）**：
5. scheme.md L53 删去 CrSb 选择四点理由（边界问题）
6. scheme.md §4 L73 整段按 4 个子节拆分（边界 + 段长 + 内容堆砌）
7. scheme.md §2 L10/L15 段长切分（叙事密度）
8. scheme.md §6 创新点精简（每点 200-300 字）

**P2（建议）**：
9. 动词堆砌/冗余修饰抽查替换

### 下一轮评审建议聚焦

- **本轮遗留**：P0 修复后再次核查方案 §4 L73 / §2 L10/L15 / §6 创新点段长与边界
- **跨章节一致性**：聚焦 references.md 编号稳定性 + scheme.md 全文 [N] 一致性 + rationale/content/scheme 关键编号无错配
- **下一轮建议**：
  - 若 P0 全部修复，R6 聚焦 scheme.md §4 拆分后是否仍复述方案细节 + §6 三创新点是否真正独立
  - 若 P0 未修复，R6 须再次以 critical 级重申

---

## 评分

```
## 评分
创新性：0.74
可行性：0.76
严谨性：0.50
表达质量：0.65
综合评分：0.65
```