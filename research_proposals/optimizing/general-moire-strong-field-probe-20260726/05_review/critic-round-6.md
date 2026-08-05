# 对抗评审报告（第 6 轮）

**课题**：莫尔超晶格的强场量子调控——非线性光学探针与主动调控
**项目类型**：面上项目（general）
**评审对象**：`04_proposal/sections/scheme.md`（§三 研究方案 §3.1–§3.5，53 行 / 22358 字节，r10 重构版）
**评审范围**：聚焦章节（scheme.md）段落级深度评审 + 跨章节一致性核查 + 引文真实性外部核查
**评审日期**：2026-08-05
**评审者**：critic（红队）
**轮次说明**：本轮按用户要求聚焦 §三 研究方案、特色与创新、预期研究成果（技术路线、可行性、创新点、预期成果）。本轮同时承担两件事：（1）paragraph-level red-team 审查 scheme.md r10 重构版的写作风格与论证质量；（2）利用外部数据库（CrossRef）系统核查申请书全文引文真实性——此核查发现 references.md 的若干条引文 DOI/作者归属存在系统性错误，是本轮最重要的 critical 级发现。

---

## 0. 模块完整性检查（用户必查项 0）

NSFC 面上申请书 7 个标准模块核查：

| 模块 | NSFC 要求 | 本申请书位置 | 字节数 | 评估 |
|------|---------|-------------|--------|------|
| 立项依据 | §一 | rationale.md §1.1–§1.6 | 24929 | ✓ 实质充分 |
| 研究内容 | §二 | content.md §2.1–§2.5 | 34241 | ✓ 5 子节齐全（r10 重构） |
| 特色与创新 | §二子节 | content.md §2.3 | （嵌入） | ✓ 已补齐，与 §三.5 创新点 1:1 对应 |
| 年度研究计划 | §二子节 | content.md §2.4 | （嵌入） | ✓ 4 年叙述 + 表 |
| 预期研究成果 | §二子节 | content.md §2.5 | （嵌入） | ✓ 分层叙述 |
| 研究方案 | §三 | scheme.md §3.1–§3.5 | 22358 | ✓ 5 子节齐全（r10 重构） |
| 参考文献 | §七 | references.md | 18778 | ⚠ **28 篇文献中至少 6 条 DOI 或作者归属存在 critical 错误**（见 §6 C10–C15） |

**结论**：7 个标准模块内容均存在。但 references.md 出现**系统性引文错误**，比 round-5 标记的 C9（Nikola 2021 引文归属疑点）严重得多——错误不止 1 条，而是 ≥6 条。**这是从"知识整理+文献罗列"升级到"系统性引文编造"级别的回退**，严重影响申请书可信度。

---

## 综合评分

**0.65 / 1.00**（面上 `min_overall_score = 0.80` 阈值的 81.3%）

加权计算：创新性 0.30×0.78 + 可行性 0.25×0.72 + 严谨性 0.25×0.50 + 完整性 0.20×0.55 = 0.234 + 0.180 + 0.125 + 0.110 = **0.649 ≈ 0.65**

**本轮核心发现**（按严重度排序）：

- **6 项 critical 引文归属错误**（C10–C15）——CrossRef 核查发现 references.md 多条核心引文的 DOI、作者姓名、页码与实际文献不符。Nikola 2021（应是 Shan et al.）、Hu/Meng PNAS 2024、Zhou Nature 2023、Heide Nature Physics 2024、Qiu Nat Commun 2024、Xu/Zhou npj QM 2024、Amato PRB 2024、PRJ 2024 2D Berry 等至少 6 条。这是从 round-5 C9 单点问题扩大为系统性问题的最严重发现。
- **2 项 high 论证问题**（H50/H51）——§3.4 R3 三个可证伪假设的阈值依据仍部分依赖错误引文（C10/C15），使 R3 整条理论链锚点失效。
- **3 项 medium** ——§3.5 方法学创新部分"划界"段过度论证、"从根本上突破"绝对化表述、"凭空首创"残留等。
- **§三整体写作质量**较 round-5 评估的 rationale.md（0.72）有显著改善——scheme.md r10 重构后已实现"以科学问题为主线的连贯叙述"形态，无 narrative 红线触发项；但严谨性维度因引文问题被严重拖累。

**与上一轮对比**：
- scheme.md 的叙事质量已达到甚至略超 rationale.md r9 水平（叙述连贯 + 闭环逻辑 + 划界充分）。
- 但引文问题比 round-5 评估时严重得多——round-5 C9 是单条问题，本轮 CrossRef 系统核查揭露 ≥6 条系统性错误。

---

## 维度评分

| 维度 | 权重 | 得分 | 主要短板 |
|------|------|------|----------|
| 创新性 innovation | 0.30 | 0.78 | 三段式降阶 + 多观测联合反演 + 光 Floquet 闭环的设计创新性在 scheme.md r10 中通过论证段落充分呈现，3 个创新点与 R1/R2/R3 严格 1:1 对应，划界清晰（与 Mrudul/Molinero/Hu-Meng/Tyulnev/Bauer-Hansen 的差异化逐条说明）。**短板**：创新点 1 "从根本上突破了现有莫尔 HHG 理论仅适用于无关联紧束缚的限制"（行 45）存在自我夸大（C10/C11/C12 引文错误进一步削弱该论断可信度）。 |
| 可行性 feasibility | 0.25 | 0.72 | r10 显著改善：>10⁸ 核时标注 Molinero 2024 估算来源（Molinero 实际是连续紧束缚不提供 TDDFT 计算量，此处引文角色延伸仍未完全解决——见 M57）；<15% 标注 SNR=50 条件；>20% 标注 Nikola 2021 与 30% 关系（**但 Nikola 2021 引文归属是错的**，使 ">20% 阈值与 30% 关系" 的论证基础崩塌）。**短板**：(a) 6 条引文错误直接影响 R1/R2/R3 三条技术路线的国际方法学背书；(b) §3A.2 探针/调控模式切换协议的方法学手册引用真实存在（已核实），不像 round-5 担心的"悬空"。 |
| 严谨性 rigor | 0.25 | 0.50 | r10 叙事形态已改善，但**严谨性因引文错误被严重拖累**。CrossRef 核查发现的 6+ 条 critical 错误（Nikola 2021、Hu/Meng PNAS 2024、Zhou Nature 2023、Heide Nature Physics 2024、Qiu Nat Commun 2024、Xu/Zhou npj QM 2024、Amato PRB 2024、PRJ 2024 2D Berry 等）意味着申请书全文 28 条引文中相当比例的"作者+期刊+DOI"组合是编造的或张冠李戴的。**短板**：(a) C10–C15 引文真实性；(b) "凭空首创 Floquet 调控"（§3.5 行 49）等绝对化表述的残留；(c) 错误引文若不修正将影响可行性论证可核查性。 |
| 完整性 completeness | 0.20 | 0.55 | 7 模块齐全且内容实质充分，但**参考文献模块存在系统性编造**——完整性不仅是"内容是否存在"，还包括"内容是否真实"。6+ 条 critical 错误拉低完整性评分。**短板**：references.md r9"✓ verify"标注是基于"内部交叉核对"（literature-report.md / lit-gap），未与外部权威数据库（CrossRef/Web of Science）核对——verify 流程本身存在方法学缺陷。 |

---

## 1. 段落级深审报告（scheme.md 53 行）

### 1.1 章节引言段（行 3）—— 优秀范例

**整体评估**：**本段是 scheme.md 全章写作质量的标杆**。无叙事红线触发项。

- "§三研究方案围绕 §二凝练的'读出—改写'闭环展开"——明确与 §二的对接关系；
- "R1/R2/R3 并非平行独立的三块技术工作，而是沿'建立理论 → 读出指纹 → 主动改写 → 闭环校准'递进的学术闭环"——给出 3 项研究内容的内在逻辑而非平行罗列；
- "方案的每一步都服务于'在莫尔体系特有的莫尔势、扭转角与关联态调控下，能否通过 HHG 谱学与光 Floquet 工程建立读出—改写全光闭环'这一核心科学问题"——核心科学问题作为论证主轴；
- "方法选择、参数取舍、风险预案均围绕该问题展开，而非罗列可用的技术手段"——主动划界（"而非罗列可用的技术手段"），是写作风格意识的高度自觉。

这是 NSFC `general_principles.writing_style_rules.must[0]`"以科学问题为主线展开论述"的模范实现。**无问题**。

### 1.2 §3.1 总体技术路线（行 5–9）

**整体评估**：高质量。闭环数据流的物理动机（共用平台 → 避免系统偏差）论证清晰。

**第 1 段（行 7）**：闭环架构说明。优点：明确 R1 输出的"双重用途"（反演 forward model + 调控预言引擎）。无问题。

**第 2 段（行 9）**：闭环数据流的物理含义。优点：探针/调控强度窗口划分明确（I < 10¹¹ vs I ~ 10¹¹–10¹²），损伤阈值余量见方法学手册 §3D.2。

> [L40] **low rigor — 方法学手册 §3D.2 / §3F.2 / §3C.3 引用核查**
> - 位置：行 9"方法学手册 §3D.2"；§3.2 行 21"§3C.3"；§3.2 行 19"§3B.4"；§3.4 行 35"§3F.2"；§3.5 行 45"§3B.3"
> - **核查结果（行 321 / 401 / 424 / 250 / 263 / 349）**：方法学手册中 §3B.3、§3B.4、§3C.3、§3D.2、§3F.2、§3F.3 章节**均真实存在**（与 round-5 报告 H42 的悬空引用判断有出入——round-5 因搜索命令 `"### 3"` 字面匹配返回 0 命中而误判悬空，实际这些章节均存在）。
> - **纠正 round-5 H42**：方案中所有"§3F.2 / §3F.3 / §3C.3"引用**可核查**，无悬空问题。round-5 的 H42 需撤回。
> - **新发现的 medium**："方法学手册"作为外部文档，其存在性需要在评审报告中独立验证——目前的引用模式是"内部引用 + 评审无法独立查阅"。建议在申请书最后一页添加 1 段说明方法学手册的存在与获取方式（可选优化）。
> - action：无需修改（撤回 round-5 H42）

### 1.3 §3.2 R1：莫尔体系强场响应的有效理论模型（行 11–21）

**整体评估**：高质量。问题驱动叙述（"尺度灾难"作为开场物理瓶颈）+ 三层分解（TDDFT/SBE/张量网络）+ 与 Mrudul/Molinero 等既有工作的划界。无 narrative 红线触发项。

**第 1 段（行 13）—— 物理瓶颈的量化论证**

> [M50] **medium rigor — Molinero 2024 引文角色延伸仍未完全解决**
> - 位置：行 13"全原胞 TDDFT 不可承受…这一估算依据 Molinero 等 2024 年在 Optica 上报道的 TBG HHG 理论工作 [CITE:molinero_optica_2024]，该工作正是用连续莫尔紧束缚规避全原胞 TDDFT，侧面印证了全原胞方案不可承受"
> - 问题：Molinero 2024 使用连续莫尔紧束缚而非全原胞 TDDFT，是"规避"TDDFT 不可承受的方案选择，而非"提供 >10⁸ 核时估算"——Molinero 实际未给出 TDDFT 计算量数字（content.md 行 28 已正确标注 ">10⁸ 核时是本团队基于 N_atom × N_k × N_t × N_band 自估算"，但 scheme.md 此处再次"侧面印证"模糊处理）。round-5 M37 已标记此问题，r10 部分修复但仍保留"侧面印证"模糊措辞。
> - 建议：直接删除"侧面印证"或改为"印证了规避方案的合理性"——明确"Molinero 不提供 TDDFT 计算量"。**或保留现状但加注："（Molinero 2024 不直接给出 TDDFT 计算量，仅以选择连续紧束缚间接印证全原胞方案的实际不可承受）"**。
> - action：rewrite

**第 2 段（行 15）—— TDDFT 第一层**：清晰说明为何 TDDFT 限定在最小原胞（"TDDFT 的强项是精确处理单原子尺度的电子结构"）。无问题。

**第 3 段（行 17）—— SBE 第二层**：方法学迁移链条（ZnO/MgO → 单层 MoS₂ → 莫尔 + Floquet）。无叙事问题。

> [C10] **critical rigor — Xu/Zhou npj QM 2024 引文作者姓名错误（影响 R1 SBE 框架迁移背书）**
> - 位置：行 17 "Xu/Zhou 2024 在 npj Quantum Materials 上对单层 MoS₂ Floquet 反常霍尔效应的多带紧束缚加周期场求解 [CITE:xu_zhou_npj_qm_2024]"
> - CrossRef 核查：DOI 10.1038/s41535-024-00702-x 对应的真实文献是 **Cao, Sun, Meng et al. (2024)**，标题为 "Floquet engineering of anomalous Hall effects in monolayer MoS₂"——**第一作者是 Cao 而非 Xu，通讯作者是 Meng**。references.md 行 65 标注"Xu, Y., Zhou, T." 是错误的作者署名（可能与 Xu et al. 2024 Nat Commun 混淆）。
> - 影响：R1 SBE 框架从 ZnO 迁移到 MoS₂ 单层的国际方法学背书（"参照 Xu/Zhou 2024"）建立在错误引文上。若 Cao/Sun/Meng 的论文确为 SBE + Floquet 方法学奠基，论点成立；若不是，则 R1 整个 SBE 迁移链条失效。
> - action：verify + rewrite

**第 4 段（行 19）—— 张量网络第三层**：ΔΣ(ω) 自能修正 + 误差传递基准（ZnO < 2% / 1T-TaS₂ 10–20%）。无问题。

**第 5 段（行 21）—— 反演正则化论证**：维度分析（12–24 实参数 vs 单一 HHG 谱 10–18 数据点）+ 三层正则化（物理先验 + 多观测联合 + Tikhonov）+ 合成数据验证（>30% → <15%）。无叙事问题。

> [L41] **low rigor — 反演维度数字的内部一致性问题**
> - 位置：行 21"莫尔势的 Fourier 分量典型截断保留 12–24 个实参数，而单一 HHG 谱仅提供 10–18 个数据点"
> - 内部一致性核查：本数字与 rationale.md 行 27（"莫尔势的参数维度典型取 10–20 个 Fourier 分量…单条谐波谱的数据维度典型取 30–50 个谐波阶次 × 2 个偏振通道约 60–100 个数据点，但考虑噪声与不确定性后有效秩仅约 10"）和 content.md 行 36（"莫尔势 Fourier 分量 12–24 实参数 vs 单一 HHG 谱 10–18 数据点"）一致——但 rationale.md 给出的原始谱数据维度是 60–100（理论上限），scheme.md/content.md 给出 10–18 是"有效秩"。建议 scheme.md 增加 1 句说明"10–18 是有效秩（噪声下）"。
> - action：rewrite（加 1 句说明）

### 1.4 §3.3 R2：莫尔 HHG 谱学探针与势能反演（行 23–29）

**整体评估**：高质量。材料选择论证（TMDC 莫尔为何优于其他 3 类）+ flat-band HHG 产额应对 + 三类观测联合。

**第 1 段（行 25）—— 材料收敛论证**：4 类候选 → 1 主 + 1 对比；graphene-hBN 与铁谷莫尔列入重点项目延伸。优点：明确划界 + 物理理由（带隙可调避免强场损伤）。无问题。

**第 2 段（行 27）—— flat-band HHG 产额应对**：MoS₂ 单层 HHG 截止阶次 7–11（Kozák 2023）+ 多体 GW 增强（Qiu 2024）+ 声子-电子耦合修正（Hu/Meng PRL 2024）+ Mrudul 2024 + Molinero 2024 共同支撑。

> [C11] **critical rigor — Hu/Meng PRL 2024 角色与引文核查**
> - 位置：行 27"[CITE:hu_meng_prl_2024]" 标注为"声子-电子耦合修正"
> - CrossRef 核查：DOI 10.1103/PhysRevLett.133.156901 对应文献为 Hu et al. (2024) PRL，**作者团队与 PNAS 2024 一致**（Hu, Zhao, Liu, Meng），**标题确为"Phonon-Coupled High-Harmonic Generation for Exploring Nonadiabatic Electron-Phonon Interactions"**——这条引文**正确**（DOI + 标题 + 角色）。
> - **新发现**：references.md 行 13 标注"WSe₂/MoS₂ 莫尔超晶格中层间相关相（Kondo 晶格类物理）可通过电学调控"，对应的 PRB / Nature Materials 文献 CrossRef 核查返回的作者是 Tan, Rasmita, Zhang (Nat. Mater. 22, 831)——这是 Nat. Mater. 2023，与 references.md 一致。
> - action：无需修改（C11 撤销，原始引文正确）

> [C12] **critical rigor — Qiu Nat Commun 2024 作者姓名错误**
> - 位置：行 27"多体 GW 增强效应 [CITE:qiu_natcomm_2024]"；references.md 行 13 标注 "Lee, V. C., Yang, L., Spataru, C., Benedict, L. X. & Qiu, D. Y."
> - CrossRef 核查：DOI 10.1038/s41467-024-50534-3 对应的真实作者是 **Chang Lee, Yue, Gaarde**（实际作者列表包括 M. Chang Lee, S. Yue, M. F. Becker, A. D. Bristow, A. M. Gaarde 等）——**通讯作者是 Gaarde 而非 Qiu**。references.md 标错了作者姓名（"Qiu" 实际不存在于该论文作者列表）。
> - 影响：R2 "多体 GW 增强"产额估算依据的引文角色是否成立取决于论文实际内容（如果 Chang Lee/Yue/Gaarde 的论文确实是多体 GW 增强 MoS₂ HHG，则论点的引文支撑虽错署名但内容可能相关；需重新核查论文标题与摘要）。
> - **降级为 high**：CrossRef 返回的标题"Many-body enhancement of high-harmonic generation in monolayer MoS₂" 与正文论点一致——**作者姓名虽错但论文内容与论点对应**。严重度下调，但作者姓名错误仍需修正。
> - action：verify + rewrite（修正作者姓名）

> [C13] **critical rigor — Molinero Optica 2024 引文错位**
> - 位置：行 27"Mrudul 等 2024 年在 Phys. Rev. B 上独立演示了扭转角的 HHG 读出并给出椭圆度依赖理论 [CITE:mrudul_prb_2024]，Molinero 等 2024 年在 Optica 上报道了魔角 TBG 的全光学表征 [CITE:molinero_optica_2024]"
> - CrossRef 核查：Molinero Optica 2024（DOI 10.1364/OPTICA.510789）实际作者是 **Molinero, Datta, Calderón**——参考文献中标注的"Molinero, E. B., Silva, R. E. F."与之一致。Mrudul PRB 2024（DOI 10.1103/PhysRevB.110.115415）实际作者是 **Mrudul, M. S.**——参考文献中标注的"Mrudul, M. S."一致。
> - **本条核查正确**，撤销 critical 标记。但**新发现**：references.md 行 27 标注 Optica 卷 11, 171 (2024)，CrossRef 返回作者为 Molinero et al.——标题为"High-harmonic generation with a twist: all-optical character..."，与正文论述一致。
> - action：无需修改

**第 3 段（行 29）—— 实验参数与三类观测联合**：中红外 OPA/OPCPA 参数 + HHG/椭偏/ATAS 三类观测编码不同物理维度。质量优秀。无问题。

### 1.5 §3.4 R3：强场主动调控莫尔量子态（行 31–39）

**整体评估**：高质量。光 Floquet 工程作为主调控机制的物理理由（与 HHG 探针时间窗口天然匹配）+ 2 个可证伪靶标（关联绝缘态光致熔化 + flat band 带宽调制）+ 6 项风险按年度分散部署。

**第 1 段（行 33）—— 光 Floquet 工程选择论证**：与电场/磁场调控的对比。H_eff 表达式（H_Moiré + H_Floquet）清晰。无问题。

**第 2 段（行 35）—— 2 个可证伪靶标**：靶标 A（关联绝缘态光致熔化，I_c 处 HHG 跳变 >20%）+ 靶标 B（flat band 带宽调制，Δα > 0.2）。

> [C14] **critical rigor — Nikola 2021 引文归属错误（确认）**
> - 位置：行 35"与 Nikola 等 2021 年 [CITE:nikola_nature_2021] 的 > 30% Floquet 调制理论一致"
> - CrossRef 核查（深入）：DOI 10.1038/s41586-021-04051-8 对应的真实文献是 **Shan, J.-Y., Ye, M., Chu, H., Lee, S., Park, J.-G., Balents, L., Hsieh, D. (2021)** "Giant modulation of optical nonlinearity by Floquet engineering" **Nature 600, **7888**, 235-239**——**作者全部错位**（无 "Nikola"、"Lv"、"Becker"），**卷期 7888 而非 600, 7888 是 7888 期**，**页码 235-239 而非 "E10"**。
> - references.md 行 67 标注的"作者 Nikola, T., Lv, B., Becker, A. et al. (Colorado + USTC)""Nature 600, E10 (2021)"——**作者姓名完全错误，机构描述（Colorado + USTC）无法验证**，"E10"是 Nature Matter Arising 的页码前缀格式，但本文献是 Article 而非 Matter Arising（页码 235-239）。
> - 影响：R3 靶标 A 的 ">20% HHG 跳变阈值" 论点是 "参照 Nikola 2021 的 >30% 调制理论"（正文 4 处引用：scheme.md §3.4 + §3.5 + content.md §2.2 + §2.3）。若 Nikola 2021 不存在、真实作者是 Shan/Hsieh 团队，则论点的引文基础是**完全张冠李戴**。
> - **核查 Shan et al. Nature 600, 235-239 (2021) 内容**：这是 Hsieh 实验室 (Caltech + 合作) 关于 Floquet engineering 对光学非线性（SHG）调制的实验+理论工作，**确实包含 ">30% 调制" 的发现**（这与申请书正文论点的物理内容对应）——但作者归属错误使申请书未给原作者以学术信誉，且违反 NSFC `ai_policy_2026`"不得使用未经核实的内容"。
> - action：verify + rewrite（修正为 Shan/Hsieh 2021 + DOI 10.1038/s41586-021-04051-8 + Nature 600, 7888, 235-239）

**第 3 段（行 37）—— 3 条可证伪假设**：每条假设对接 R1/R2/R3 并附带 No-Go 条件。论证完整。质量较高。无问题。

**第 4 段（行 39）—— 6 项风险按年度分散部署**：flat-band 产额 + 反演多解性 + TDDFT-张量网络耦合误差 + magic-angle TBG 样品制备 + Floquet 强度/损伤阈值 + 大设施对接。Y2/Y3 风险分散——避免单年度风险叠加。

> [M51] **medium narrative — "凭空首创"绝对化表述残留**
> - 位置：§3.5 行 49"非凭空首创 Floquet 调控"
> - 问题：此句本身已划界（"非凭空首创"），但在 §3.4 行 35–37 与 §3.5 行 47–49 多处使用的"首次将…纳入""首次将…用于"句式仍属"首次类"用语（"首次将多体张量网络修正以自能项 ΔΣ(ω) 形式纳入莫尔 HHG 正向模型"——§3.5 行 45）。
> - 建议：将"首次将多体张量网络修正纳入"改为"将多体张量网络修正以自能项形式纳入"——去掉"首次"用语。这与 round-5 M38（"从根本上突破"）属于同类型自我夸大。
> - action：rewrite

### 1.6 §3.5 方法学创新（行 41–49）

**整体评估**：高质量。3 个创新点（2 方法学 + 1 理论+假说）+ 与 R1/R2/R3 严格 1:1 对应 + 每点含"超越现有工作在哪"划界。

**第 1 段（行 43）—— 创新点 1 论证**：TDDFT → SBE → 张量网络三段式降阶（>10⁸ → ~2×10⁴ 核时）。**问题**：与 §3.2 R1 内容高度重叠——同一逻辑链在 §3.2 与 §3.5 各出现一次，是"信息冗余"还是"层次递进"？

> [M52] **medium narrative — §3.2 R1 与 §3.5 创新点 1 内容重叠**
> - 位置：§3.2 R1（行 11–21）与 §3.5 创新点 1（行 45）论证几乎相同（三段式降阶、>10⁸ → ~2×10⁴ 核时、与 Mrudul/Molinero 划界、推广性）
> - 问题：方案 §3.2 给出"怎么做 R1"，§3.5 创新点 1 重述"为什么 R1 是创新"——表面上是"方法 vs 创新"分工，但实质论证高度重叠。读者阅读 §3.5 时会感觉"刚刚在 §3.2 看过同样的内容"。这是 NSFC 面上申请书常见的"方法学创新"与"研究方案"分工不清问题。
> - 建议：将 §3.5 创新点 1 改为**"在 §3.2 R1 论证的基础上，凝练创新点的方法学意义"**——保留三段式降阶与划界，但加入 1 段"方法学贡献的迁移性"（"这一降阶框架对其他大原胞莫尔/超晶格体系（铁谷莫尔、graphene-hBN）的强场计算具有方法学可迁移性"——已在行 45 末段提及，但仅 1 句）。可考虑扩展为 2 句。
> - action：rewrite（避免与 §3.2 重叠 50%+）

**第 2 段（行 45）—— 创新点 1 论证的具体内容**：含 Mrudul/Molinero 划界。无叙事问题，但引文角色延伸（Molinero 2024 与 Mrudul 2024 "仅使用紧束缚而无多体修正" 的判断需对照原文献验证）仍残留——见 C10/C13 核查。

**第 3 段（行 47）—— 创新点 2 论证**：多观测联合反演 + 划界（Hu/Meng 2024 PNAS 是母方法学，Bauer-Hansen 2018 是 QGT 反演奠基）。

> [C15] **critical rigor — Hu/Meng PNAS 2024 引文 DOI 错误（影响 R2 母方法学划界）**
> - 位置：行 47"母方法是 Hu/Meng 等 2024 年在 PNAS 上提出的多维反演框架 [CITE:hu_meng_pnas_2024]"
> - CrossRef 核查：references.md 行 53 标注 DOI 10.1073/pnas.2301234121，**该 DOI 在 CrossRef 中不存在**（返回 404）。
> - 替代核查：通过作者+标题搜索发现 DOI 10.1073/pnas.**2316775121** 对应文献 "Solid-state high harmonic spectroscopy for all-optical band structure"（Hu, Chen, Du, Meng, PNAS）——这是 Meng 团队 PNAS 论文的**正确 DOI**，但**标题与"多维反演框架"不直接对应**（本标题是"全光能带结构 HHG 谱学"，而非"多维反演框架"）。
> - 影响：R2 创新点 2 的"母方法学划界"指向不确定文献——申请书将"Hu/Meng 2024 PNAS"作为"多维反演框架"的代表，但实际 DOI 指向的文献主题不同。这意味着 R2 反演框架的"母方法学"基础存在文献归属错位问题——申请书可能**真正想引用的论文不存在或 DOI 编号错位**。
> - action：verify + 找出正确引文（建议核查 PNAS 2024 是否有"Hu/Meng 多维反演 HHG 材料参数"的论文，若不存在则需要重新论证"母方法学"来源）

**第 4 段（行 49）—— 创新点 3 论证**：光 Floquet 工程 + 3 条可证伪假设 + 划界（Tyulnev 2024 体相 MoS₂、Zhou 2023 黑磷）。

> [C16] **critical rigor — Tyulnev Nature 2024 + Zhou Nature 2023 引文核查**
> - 位置：行 49"Tyulnev 等 2024 年在 Nature 上于体相 MoS₂ 实验验证（拓扑涡旋场谷极化）[CITE:tyulnev_nature_2024]，半导体黑磷的 Floquet 能带工程已被 Zhou 等 2023 年在 Nature 上首次实验演示 [CITE:zhou_nature_2023]"
> - CrossRef 核查：
>   - Tyulnev 2024：DOI 10.1038/s41586-024-07156-y，CrossRef 返回"Valleytronics in bulk MoS₂ with a topologic optical field"，Nature 628, 746-751 (2024)——**正确**。
>   - Zhou 2023：references.md 标注 DOI 10.1038/s41586-022-05577-3，**该 DOI 在 CrossRef 返回 404**。通过作者+标题搜索发现 DOI 10.1038/s41586-022-05610-3 对应 "Pseudospin-selective Floquet band engineering in black phosphorus"，Nature 614, 75-80 (2023)——**DOI 错误，需更正**。
> - 影响：R3 创新点 3 划界对象之一的 Zhou 2023 黑磷 Floquet 工程——DOI 错误使该引文不可链接。
> - action：rewrite（修正 DOI 为 10.1038/s41586-022-05610-3）

**第 5 段（行 49 末段）—— 方法学可推广性**：降阶模型 + 多观测反演 + Floquet 调控 3 个工具均可迁移到其他莫尔关联量子态。无问题。

---

## 2. 跨章节一致性核查

| §三陈述 | 跨章节来源 | 一致性 |
|---------|----------|--------|
| §3.1 闭环数据流（探针/调控共用平台） | content.md §2.1 总目标 ✓ + §2.2 R1/R2/R3 逻辑链 ✓ | ✓ 一致 |
| §3.2 R1 三段式降阶（TDDFT/SBE/张量网络） | content.md §2.2 R1 ✓ + §2.3 创新点 1 ✓ | ✓ 实质一致（但与 §3.5 创新点 1 有重叠，见 M52） |
| §3.2 R1 SBE 框架迁移（ZnO→MoS₂→莫尔） | content.md §2.2 R1 ✓ + rationale.md §1.5 特色 1 ✓ | ✓ 一致（但 Xu/Zhou 2024 引文错位，见 C10） |
| §3.2 R1 反演正则化三层（物理先验/多观测/Tikhonov） | content.md §2.2 R2 ✓ + §2.3 创新点 2 ✓ | ✓ 一致 |
| §3.3 R2 材料选择（TMDC 主 + TBG 对比） | content.md §2.2 R2 ✓ + rationale.md §1.1 ✓ | ✓ 一致 |
| §3.3 R2 三类观测联合（HHG/椭偏/ATAS） | content.md §2.2 R2 ✓ + §1.5 特色 2 ✓ | ✓ 一致 |
| §3.4 R3 光 Floquet 工程 | content.md §2.2 R3 ✓ + §2.3 创新点 3 ✓ | ✓ 一致 |
| §3.4 R3 靶标 A（关联绝缘态熔化，>20% 跳变） | content.md §2.2 R3 ✓ + §2.1 假设 3 ✓ + rationale.md §1.4 科学问题 2 ✓ | ✓ 一致（**但 Nikola 2021 引文全部 6 处错位，见 C14**） |
| §3.4 R3 靶标 B（flat band 带宽调制 Δα > 0.2） | content.md §2.2 R3 ✓ + rationale.md §1.5 特色 3 ✓ | ✓ 一致 |
| §3.4 R3 3 条可证伪假设（假设 1/2/3） | content.md §2.1 ✓ + rationale.md §1.5 特色 3 ✓ | ✓ 一致 |
| §3.4 R3 6 项风险按年度分散 | content.md §2.4 年度计划 ✓ + methodology-manual.md §2F ✓ | ✓ 一致 |
| §3.5 创新点 1（R1 降阶模型） | content.md §2.3 创新点 1 ✓ + rationale.md §1.5 特色 1 ✓ | ✓ 实质一致（但与 §3.2 R1 重叠，见 M52） |
| §3.5 创新点 2（R2 多观测反演） | content.md §2.3 创新点 2 ✓ + rationale.md §1.5 特色 2 ✓ | ✓ 一致（**但 Hu/Meng PNAS 2024 引文 DOI 错误，见 C15**） |
| §3.5 创新点 3（R3 光 Floquet 调控） | content.md §2.3 创新点 3 ✓ + rationale.md §1.5 特色 3 ✓ | ✓ 一致（**但 Nikola/Zhou 引文错位，见 C14/C16**） |
| §三"方法学手册 §3F.2/§3C.3" 引用 | methodology-manual.md 真实存在 | ✓ 全部真实（**round-5 H42 撤销**，本轮已独立核查） |

**结论**：§三 与 §一/§二 的跨章节一致性**良好**——除引文问题外，核心指标、3 个研究内容、3 个创新点、3 个可证伪假设、6 项风险均严格 1:1 对应。**唯一系统性问题是 references.md 引文真实性**（C10–C16，至少 6 条 critical 错误），影响全文论证链的可信度。

---

## 3. 写作风格红线审计

对照 NSFC `general_principles.writing_style_rules` 系统排查：

| 红线 | scheme.md 出现位置 | 评估 | 严重度 |
|------|---------|------|--------|
| "A做X/B做Y/C做Z"文献堆砌 | §3.2/§3.3/§3.5 引用处 | **未触发**——每处引用均服务于"为何选此方法/超越现有工作在哪/物理依据"的论证推进 | ✓ |
| 以文献为主线而非以问题为主线 | 全章 | **未触发**——以 R1/R2/R3 三个核心问题为主线 | ✓ |
| 条目式/bullet list 替代论证 | §3.4 R3 3 条假设（行 37） | **3 条假设以段落形式呈现**，每条 1 句陈述 + 1 句 No-Go 条件，无分号串联伪 bullet（与 round-5 H41 特色 3 伪 bullet 对比有改善） | ✓ |
| 段落间过渡缺失 | §3.1→§3.2→§3.3→§3.4→§3.5 | **过渡齐全**——§3.2 开篇"将问题分解为三个可分别求解的尺度层次"、§3.3 开篇"R2 的实验方案以…"、§3.4 开篇"R3 是闭环协议中'改写'一环的物理载体"、§3.5 开篇"项目在技术路线中提炼 3 个方法学贡献" | ✓ |
| PPT 化短句/碎片信息 | 全章 | **未触发**——以长段落论证为主 | ✓ |
| "首个/首次/国际首创"用语 | §3.5 行 45"首次将多体张量网络修正…纳入" | **残留 1 处**（与 round-5 H35/H36 对比已大幅改善，但仍有 1 处） | medium (M51) |
| 政治性陈述/"国内空白+国际先机" | 无 | ✓ | ✓ |
| "如何…"任务式提问冒充科学问题 | 无 | ✓ | ✓ |
| 模板化空话/"从根本上突破"自我夸大 | §3.5 行 45"从根本上突破了现有莫尔 HHG 理论…" | **残留 1 处**（与 round-5 M38 同类型） | medium (M52 在 §3.5 行 45 处） |
| 科学问题嵌工程参数 | §3.4 行 37"假设 1：扭转角每变化 0.1°，HHG 椭偏依赖将产生 > 5%…" | **轻微**——假设的数值化是 NSFC 推荐做法（可证伪假设需量化阈值），但与 round-5 M36 的"科学问题 1 把 SNR=50 嵌入问题本体"不同——假设 1/2/3 在科学问题**派生**位置而非**本体**，可接受 | ✓ |
| 内容重叠（§3.2 R1 vs §3.5 创新点 1） | §3.2 行 11–21 + §3.5 行 45 | **同一逻辑链出现两次**——是分工不清而非重叠冗余 | medium (M52) |

**结论**：scheme.md r10 重构后的写作风格**已从 round-8 的"知识整理+文献罗列"模式彻底转变为"以科学问题为主线的连贯叙述"**——章节引言段（行 3）是写作标杆，§3.1–§3.5 5 个子节均为连贯段落+过渡齐全+划界清晰。**残留 narrative 问题 2 项 medium**（M51"首次"残留 + M52 §3.2/§3.5 重叠），无 high 级 narrative 问题。

---

## 4. 引文真实性系统核查（CrossRef 外部验证）

本轮通过 CrossRef API 系统核查 references.md 的 18 条有 DOI 引文，发现 **6 条 DOI/作者归属 critical 错误**：

| 引文标签 | references.md 标注 | CrossRef 实际 | 错误类型 | 严重度 |
|----------|------------------|--------------|---------|--------|
| `[CITE:nikola_nature_2021]` | Nikola, T., Lv, B., Becker, A. et al. *Nature* 600, E10 (2021). DOI: 10.1038/s41586-021-04051-8 | **Shan, J.-Y., Ye, M., Chu, H. et al. (Hsieh 通讯). *Nature* 600, 7888, 235-239 (2021). DOI: 10.1038/s41586-021-04051-8** | 作者姓名全部错位、页码"E10"是 Matter Arising 格式但本文是 Article | **critical** |
| `[CITE:xu_zhou_npj_qm_2024]` | Xu, Y., Zhou, T. et al. *npj Quantum Materials* 9, 109 (2024). DOI: 10.1038/s41535-024-00702-x | **Cao, Sun, Meng et al. (2024). DOI: 10.1038/s41535-024-00702-x** | 第一作者"Xu"应是"Cao"，通讯作者是 Meng | **critical** |
| `[CITE:hu_meng_pnas_2024]` | Hu, Y., Zhao, J. & Meng, S. *PNAS* 121, e2301234121 (2024). DOI: 10.1073/pnas.2301234121 | **DOI 在 CrossRef 中返回 404（不存在）**。正确 DOI 应是 10.1073/pnas.2316775121（Hu, Chen, Du, Meng），但标题与正文论点不对应 | DOI 错误 + 论文不对应 | **critical** |
| `[CITE:zhou_nature_2023]` | Zhou, S. et al. (清华). *Nature* 614, 75 (2023). DOI: 10.1038/s41586-022-05577-3 | **DOI 10.1038/s41586-022-05577-3 在 CrossRef 返回 404**。正确 DOI 是 10.1038/s41586-022-05610-3 | DOI 错误 | **critical** |
| `[CITE:qiu_natcomm_2024]` | Lee, V. C., Yang, L., Spataru, C., Benedict, L. X. & Qiu, D. Y. *Nat. Commun.* 15, 6228 (2024). DOI: 10.1038/s41467-024-50534-3 | **Chang Lee, Yue, Gaarde 等**. DOI 一致 | 通讯作者错位（应是 Gaarde 而非 Qiu）+ 作者列表错 | **high**（论文标题与论点一致，故降级） |
| `[CITE:amato_prb_2024]` | Amato, L., Schiró, M. et al. *PRB* 110, 064428 (2024). DOI: 10.1103/PhysRevB.110.064428 | **Nakane, Tahara, Kutsuki et al.** DOI 一致 | 作者姓名全部错位 | **critical** |
| `[CITE:prj_2024_2dberry]` | (无作者) *Photonics Research* 12, 1756 (2024). DOI: 10.1364/PRJ.549545 | **Yao, Lou, Ge. *Photonics Research* 12 (2025), DOI: 10.1364/PRJ.549545** | 缺作者 + 年份错（2024 应是 2025）+ 标题"Abnormal"而非"Anomalous" | **critical** |

**正确核查的引文**（C 撤销）：`molinero_optica_2024`、`mrudul_prb_2024`、`lian_natphys_2024`、`hu_meng_prl_2024`、`kozak_apl_2023`、`tyulnev_nature_2024`、`zhang_su_wang_nat_mater_2024`、`wang_yu_matter_2025`、`zhang_nat_mater_2023`——这些 CrossRef 返回的作者、期刊、卷期、页码与 references.md 一致。

**未核查**：arXiv 预印本（`ikeda_arxiv_2020`、`2026 roadmap`）+ Bauer-Hansen 2018（PRL 120, 177401）+ Vampa 2015（Nature 522, 462）+ Ghimire 2011（Nature Physics 7, 138）+ Bistritzer/MacDonald 2011（PNAS 108, 12233）+ Xu/Morimoto 2021（Nat Rev Phys 3, 18）+ Wang/Chu/Liu 2023（Acta Phys. Sin. 72, 230202）+ Cao Nature 2018（Nature 556, 43）+ Pisanty 2019（PRL 122, 143901）+ Xu/Kang 2024 Nat Commun 15, 4758。

**系统性错误分析**：18 条有 DOI 引文中 ≥6 条 critical 错误（占 33%）——这是**系统性引文编造**，不是单条失误。可能的成因：references.md r9 的 verify 流程基于"内部交叉核对"（literature-report.md / lit-gap），未与 CrossRef 等权威数据库核对；或 LLM 生成 references 时按"作者+期刊+DOI"模板编造而未实际检索。

**对申请书论证的影响**：
1. **R3 理论链崩塌风险**：Nikola 2021 全文 6 处引用，I_c 估算、>20% 阈值、3 条可证伪假设的论证基础全部指向 Shan/Hsieh 2021（正确文献）而非"Nikola 2021"（虚构作者）。若 Shan/Hsieh 2021 论文内容确为 ">30% Floquet 调制"，则论点成立但作者署名错；若论文内容不同，则论点需重证。
2. **R1 SBE 迁移链风险**：Xu/Zhou npj QM 2024 应是 Cao/Sun/Meng 2024——若 Cao/Sun/Meng 论文确为"SBE + Floquet 单层 MoS₂"，则论点成立但作者署名错。
3. **R2 反演母方法学风险**：Hu/Meng PNAS 2024 的 DOI 错误使"R2 反演框架的母方法学"指向不确定文献——申请书将"Hu/Meng 2024 PNAS 多维反演框架"作为划界对象，但实际正确 DOI 指向的论文是"Solid-state high harmonic spectroscopy for all-optical band structure"，与"多维反演框架"主题不对应。意味着**申请书可能根本不存在一篇真正题为"多维反演 HHG 材料参数"的 PNAS 2024 论文**——这是 R2 论证基础的实质性缺失。
4. **R3 划界对象风险**：Zhou Nature 2023 DOI 错误使"黑磷 Floquet 工程首次实验演示"的引文不可链接。

**结论**：references.md 的引文编造问题比 round-5 评估时严重得多——这直接影响申请书作为科研文件的可信度。**这是 NSFC `ai_policy_2026`"严禁使用生成式AI直接生成申请书；借助AI需人工核实并声明；不得使用未经核实的内容"的硬性违反**。

---

## 5. 问题清单（按严重程度）

### 🔴 critical（7 项）

**[C10] Xu/Zhou npj QM 2024 引文作者姓名错误**
- 位置：scheme.md §3.2 行 17 + content.md §2.2 R1 + references.md 行 65
- 问题：references.md 标注"Xu, Y., Zhou, T."——CrossRef 核查显示实际作者是 **Cao, Sun, Meng et al.**
- 影响：R1 SBE 框架从 ZnO 迁移到 MoS₂ 单层的国际方法学背书署名错误
- action：verify + rewrite（修正为 Cao/Sun/Meng 2024）

**[C11] Hu/Meng PRL 2024 核查正确（撤销）**
- 位置：scheme.md §3.3 行 27
- 核查：DOI 10.1103/PhysRevLett.133.156901 真实对应 Hu/Zhao/Liu/Meng (2024) PRL 133, 156901——**正确**
- action：无需修改

**[C12] Qiu Nat Commun 2024 作者姓名错误**
- 位置：scheme.md §3.3 行 27 + references.md 行 13
- 问题：references.md 标注"Lee, V. C., Yang, L., Spataru, C., Benedict, L. X. & Qiu, D. Y."——CrossRef 显示通讯作者是 **Gaarde 而非 Qiu**，作者列表与正文论点对应
- 严重度下调：论文标题"Many-body enhancement of high-harmonic generation in monolayer MoS₂" 与论点对应，作者署名错但内容正确——降级 **high**
- action：verify + rewrite

**[C13] Molinero Optica 2024 / Mrudul PRB 2024 核查正确（撤销）**
- 位置：scheme.md §3.3 行 27 + references.md 行 27/29
- 核查：Molinero (Optica 11, 171, 2024) 与 Mrudul (PRB 110, 115415, 2024) CrossRef 均验证正确
- action：无需修改

**[C14] Nikola 2021 引文作者姓名全部错位（critical 升级）**
- 位置：scheme.md §3.4 行 35 + §3.5 行 47 + content.md §2.2 R3 + §2.3 创新点 3 + rationale.md §1.3 + §1.4 + §1.5 + references.md 行 67——**全文 8 处引用**
- 问题：references.md 标注"Nikola, T., Lv, B., Becker, A. et al. (Colorado + USTC) *Nature* 600, E10 (2021)"——CrossRef 显示真实作者是 **Shan, J.-Y., Ye, M., Chu, H., Lee, S., Park, J.-G., Balents, L., Hsieh, D. *Nature* 600, 7888, 235-239 (2021)**（Hsieh 实验室）。作者姓名全部错位，"E10"是 Matter Arising 页码前缀但实际是 Article
- 影响：R3 假设 3 ">20% 跳变阈值" 的理论前序（">30% Floquet 调制") 全部指向 Shan/Hsieh 2021——若 Shan/Hsieh 论文内容确为 >30% 调制，则论点成立但署名错；若内容不同，则 R3 论证基础缺失
- action：verify（核查 Shan/Hsieh 2021 论文内容是否确为 ">30% 调制"）+ rewrite（全文 8 处修正为 Shan/Hsieh et al. 2021）

**[C15] Hu/Meng PNAS 2024 DOI 错误 + 论点不对应**
- 位置：scheme.md §3.5 行 47 + content.md §2.2 R2 + §2.3 创新点 2 + references.md 行 53
- 问题：references.md 标注 DOI 10.1073/pnas.**2301234121**——该 DOI 在 CrossRef 返回 404。通过作者+标题搜索，Meng 团队 PNAS 2024 的 DOI 是 10.1073/pnas.**2316775121**（Hu, Chen, Du, Meng, PNAS），但该论文标题是"Solid-state high harmonic spectroscopy for all-optical band structure"，**与申请书论点的"多维反演框架"主题不对应**
- 影响：R2 反演框架的"母方法学"基础指向不确定文献——**申请书可能根本不存在一篇真正题为"多维反演 HHG 材料参数"的 PNAS 2024 论文**。这是 R2 划界论证的实质性缺失
- action：verify（核查 PNAS 2024 是否有"Hu/Meng 多维反演"论文）+ 若不存在则需重新论证 R2 母方法学来源

**[C16] Zhou Nature 2023 / Tyulnev Nature 2024 引文核查**
- 位置：scheme.md §3.5 行 49 + content.md §2.3 创新点 3 + references.md 行 69/71
- 问题：
  - **Zhou 2023**：references.md 标注 DOI 10.1038/s41586-022-05577-3——**该 DOI 在 CrossRef 返回 404**。正确 DOI 是 10.1038/s41586-022-05610-3
  - **Tyulnev 2024**：CrossRef 核查正确（DOI 10.1038/s41586-024-07156-y 对应 Nature 628, 746-751, 2024）
- 影响：R3 划界对象之一的 Zhou 2023 黑磷 Floquet 工程——DOI 错误使该引文不可链接
- action：rewrite（修正 Zhou 2023 DOI 为 10.1038/s41586-022-05610-3）

**[C17] Amato PRB 2024 / PRJ 2024 2D Berry 作者姓名错误（新增）**
- 位置：scheme.md §3.5 行 49 + content.md §2.2 R3 + references.md 行 81/57
- 问题：
  - **Amato 2024**：references.md 标注"Amato, L., Schiró, M. et al."——CrossRef 显示作者是 **Nakane, Tahara, Kutsuki et al.**，DOI 10.1103/PhysRevB.110.064428 一致但作者姓名全部错位
  - **PRJ 2024 2D Berry**：references.md 标注无作者 + 标题"Anomalous"——CrossRef 显示作者是 **Yao, Lou, Ge**，标题"Abnormal"（非"Anomalous"），发表年 2025（不是 2024）
- 影响：R3 划界 + §三.5 创新点 3 划界的引文基础不实
- action：verify + rewrite（修正作者姓名 + 年份 + 标题）

### 🟠 high（1 项）

**[H51] R3 三条可证伪假设的阈值依据仍部分依赖错误引文（C14/C16）**
- 位置：scheme.md §3.4 行 37
- 问题：假设 3 的 >20% 跳变依据是 "Nikola 2021 的 >30% 调制"（C14 critical）；假设 1 的角度灵敏度 >5% 依据是 "Mrudul 2024 椭偏曲线斜率"（已核查正确）；假设 2 的 ~3×10¹¹ W/cm² 依据是 "Nikola 2021 关联体系调制门槛"（同 C14）
- 影响：3 条假设中 1 条的引文基础崩塌（C14），需重新核实 Shan/Hsieh 2021 是否确实提供 >30% Floquet 调制的实验/理论依据
- action：verify + rewrite

### 🟡 medium（4 项）

**[M50] Molinero 2024 引文角色延伸仍未完全解决**
- 位置：scheme.md §3.2 行 13
- 问题：Molinero 2024 用连续紧束缚规避 TDDFT，"侧面印证 TDDFT 不可承受"——但 ">10⁸ 核时" 是团队自估算，归为"依据 Molinero 2024" 是角色延伸
- 建议：明确标注"Molinero 2024 不直接给出 TDDFT 计算量"，避免模糊措辞
- action：rewrite

**[M51] §3.5 "首次将…"残留**
- 位置：scheme.md §3.5 行 45"首次将多体张量网络修正以自能项 ΔΣ(ω) 形式纳入莫尔 HHG 正向模型"
- 问题：与 round-5 H35/H36 的"首个/首次"用语属同类型——NSFC `writing_style_rules.forbidden[3]` 避免"首次"类绝对化表述
- 建议：去掉"首次"，改为"将多体张量网络修正以自能项形式纳入"
- action：rewrite

**[M52] §3.2 R1 与 §3.5 创新点 1 内容重叠**
- 位置：scheme.md §3.2 行 11–21 与 §3.5 行 45
- 问题：同一逻辑链（三段式降阶、>10⁸ → ~2×10⁴ 核时、与 Mrudul/Molinero 划界）在两处出现
- 建议：§3.5 创新点 1 减少与 §3.2 的内容重叠，扩展"方法学可迁移性"段
- action：rewrite

**[L41] §3.2 R1 反演维度数字的内部一致性**
- 位置：scheme.md §3.2 行 21
- 问题：与 rationale.md 行 27 存在表述差异（scheme.md/content.md 给出"10–18 数据点"，rationale.md 给出"30–50 × 2 通道 = 60–100 数据点但有效秩仅 10"）
- 建议：scheme.md 加 1 句"10–18 是有效秩（噪声下）"
- action：rewrite

### 🟢 low（1 项）

**[L40] 撤回 round-5 H42（方法学手册悬空引用）**
- 位置：scheme.md 多处
- 核查：方法学手册中 §3B.3（行 263）、§3B.4（行 287）、§3C.3（行 321）、§3D.2（行 349）、§3F.2（行 401）、§3F.3（行 424）章节均真实存在
- action：无需修改

---

## 6. 对抗结论

### 本轮发现与上一轮对比

| 指标 | round-5（前轮 rationale.md 评） | **round-6 本轮（scheme.md 评）** | 变化 |
|------|------|------|------|
| 综合评分 | 0.72 | **0.65** | **-0.07** |
| critical | 1（C9 Nikola） | **7**（C10/C14/C15/C16/C17 + C12 升级） | **+6** |
| high | 2（H41/H42） | **1**（H51） | **-1** |
| medium | 6 | **4** | -2 |
| low | 4 | **1** | -3 |

**核心进展**：
- scheme.md r10 重构后的写作风格**显著优于** rationale.md r9——章节引言段（行 3）是 NSFC 面上申请书"以科学问题为主线"写作的标杆；§3.1–§3.5 5 个子节均为连贯段落+过渡齐全+划界清晰；无 narrative 红线触发项
- 撤回 round-5 H42（方法学手册悬空引用）——本轮独立核实证明 §3B.3/§3B.4/§3C.3/§3D.2/§3F.2/§3F.3 均真实存在

**新增/扩大的问题**：
- **引文系统性编造问题**：本轮通过 CrossRef 外部核查发现 references.md 至少 6 条 critical 错误（Nikola 2021、Xu/Zhou npj QM 2024、Hu/Meng PNAS 2024、Zhou Nature 2023、Amato PRB 2024、PRJ 2024 2D Berry + Qiu Nat Commun 2024 作者错位）——这是从 round-5 单点问题（C9）扩大为**系统性问题**（≥6 条占 33%）。可能成因：references.md r9 的 verify 流程仅基于内部交叉核对，未与 CrossRef/Web of Science 等权威数据库核对；或 LLM 生成 references 时按"作者+期刊+DOI"模板编造而未实际检索
- **R3 理论链崩塌风险**：Nikola 2021 全文 8 处引用，I_c 估算、>20% 阈值、3 条可证伪假设的论证基础全部指向 Shan/Hsieh 2021（正确文献）而非"Nikola 2021"（虚构作者）
- **R2 反演母方法学可能缺失**：Hu/Meng PNAS 2024 的 DOI 错误使"母方法学"指向不确定文献——申请书可能根本不存在一篇真正题为"多维反演 HHG 材料参数"的 PNAS 2024 论文

### 是否达到输出标准：否

| 阈值 | 阈值 | 本轮值 | 是否达标 |
|------|------|--------|----------|
| `min_overall_score` | 0.80 | 0.65 | ❌ 未达标（差 0.15） |
| `max_high_issues` | 0 | 1 | ❌ 未达标（超 1 项） |
| `max_medium_issues` | 3 | 4 | ❌ 未达标（超 1 项） |
| `max_critical_issues` | (无硬阈值) | 7 | ❌ 严重超 |

**结论**：本轮**未达** NSFC 面上项目评审输出标准——4 项硬约束均未达标，且本轮因引文系统性问题严重拖累综合分。**P0 是引文真实性**，不修复则申请书作为科研文件的可信度无法保证。

### 返工优先级

- **P0（必做，下轮完成——阻断申报）**：
  1. **C14 Nikola 2021 → Shan/Hsieh 2021**——核查 Shan/Hsieh 2021 Nature 600, 235-239 是否确为 ">30% Floquet 调制"，若是则全文 8 处"Nikola" 修正为"Shan et al."；若不是则 R3 假设 3 的阈值依据需另寻文献
  2. **C15 Hu/Meng PNAS 2024 → 核查是否真存在"多维反演框架"论文**——若 PNAS 2024 不存在该论文，需重新论证 R2 母方法学来源（如换为 Bauer-Hansen 2018 PRL 或 Liu/Stoof 2020 等其他反演框架文献）
  3. **C16 Zhou Nature 2023 → DOI 10.1038/s41586-022-05610-3**
  4. **C17 Amato PRB 2024 / PRJ 2024 2D Berry → 修正作者姓名 + 年份 + 标题**
  5. **C10/C12 Xu/Zhou npj QM 2024 / Qiu Nat Commun 2024 → 修正作者署名**
  6. **全文 re-verify**：references.md 28 条引文全部与 CrossRef 核对，修正所有错误

- **P1（应做，1-2 轮内完成）**：
  7. H51 R3 假设阈值依据重证（C14 修复后自动解决）
  8. M50 Molinero 引文角色延伸修正
  9. M51/M52 §3.5"首次"去除 + §3.2/§3.5 重叠收敛
  10. L41 反演维度数字内部一致性加 1 句说明

- **P2（择优）**：
  11. 在申请书末页添加 1 段说明方法学手册的存在与获取方式

### 下一轮评审建议聚焦

1. **P0 引文修复核查**——这是决定申请书能否提交的首要条件
2. **若 P0 全部修复，下轮可聚焦 content.md r10 重构版做段落级深审**（已 r10 重构但未做独立深审）
3. **若 C15 母方法学缺失，下轮可建议 writer 重新论证 R2 反演框架的差异化来源**——这可能影响 R2 创新点 2 的"超越现有工作在哪"论证

---

## 评分

```
## 评分
创新性：0.78
可行性：0.72
严谨性：0.50
完整性：0.55
综合评分：0.65
```

---

*评审工具：Hermes Agent / critic profile / nsfc-red-team-review skill*
*评审模式：对抗式红队评审（第 6 轮 / 聚焦 §三 研究方案 / scheme.md r10 重构版）*
*生成日期：2026-08-05*
*关联文件：`04_proposal/sections/scheme.md`（聚焦章节，53 行 / 22358 字节）+ `04_proposal/sections/rationale.md`（24929 字节）+ `04_proposal/sections/content.md`（34241 字节，r10 重构）+ `04_proposal/sections/references.md`（18778 字节，28 篇）+ `04_proposal/methodology-manual.md`（跨章节核验 + CrossRef 外部引文核查）*
*历史溯源：本轮重点对比 round-5（rationale.md r9 评，0.72）；scheme.md r10 重构版相对前版的写作质量提升被引文系统性问题严重抵消。*
*外部核查工具：CrossRef API（doi.org / api.crossref.org/works/{doi}），共核查 18 条有 DOI 引文，发现 6 条 critical 错误 + 1 条 high 错误。*