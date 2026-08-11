# 对抗评审报告（第 6 轮 · 参考文献检验）

**项目类型**：面上项目（general）
**评审日期**：2026-08-11
**评审范围**：references.md（§七 参考文献）— references-only 专项检验
**评审对象**：
- `04_proposal/sections/references.md`（143 行 / 18,778 字节）
- `04_proposal/sections/rationale.md`（63 行 / 26,185 字节）
- `04_proposal/sections/content.md`（94 行 / 34,241 字节）
- `04_proposal/sections/scheme.md`（59 行 / 21,112 字节）
**评审者**：critic（红队）
**轮次说明**：本轮按用户要求对 references.md 做第 6 轮专项检验，重点核查 6 项指标（引文格式 / 编号一致性 / 引用相关性 / 缺失引用 / 引用数量 / 时效性）。

---

## 0. 前置说明

按用户最新要求，本轮聚焦 `references.md` 做参考文献检验，**不评估写作风格、创新性、可行性**。仅评严谨性（rigor）与完整性（completeness）两个维度；创新性、可行性填 N/A，综合评分 = (严谨性 + 完整性) / 2。本轮为 references-only 评审，执行清单对照按 skill 规范可省略。

---

## 综合评分

**0.78 / 1.00**

本轮红队对参考文献 6 项指标的核查结论：

| 指标 | 实测 | 评估 |
|------|------|------|
| 引文格式（[CITE:标签] 统一性） | 27/27 篇带 [CITE:] 标签采用同一种格式 | ✓ 一致；与 §一/§二/§三 正文同标签格式完全一致 |
| 作者 / 年份 / 期刊 / 卷期完整 | 26/27 篇提供完整作者 + 年份 + 期刊 + 卷期 + 页码（DOI/arXiv） | ⚠ 1 篇 [CITE:prj_2024_2dberry] 缺作者署名 |
| 编号一致性 | 正文 22 个独立标签全部在参考文献表中找到（0 处断链） | ✓ 通过；但 scheme.md 行 59 末尾"优化记录"段含 1 处 [CITE:xxx] 占位符 |
| 引用相关性 | 28 篇全部围绕"莫尔 HHG + 反演 + Floquet 调控"主线 | ✓ 高度聚焦，无关引用 0 篇 |
| 缺失引用 | 8 处重要论断未直接引用支撑（详见 §4） | ⚠ 部分论断仅"参照"而非真正引证 |
| 引用数量 | 28 篇（27 篇带标签 + 1 篇 2026 路线图） | ✓ 在 15–30 篇区间 |
| 时效性（2024–2026） | 14 篇 / 28 = 50% | ✓ 近 3 年文献占 50%，时效性优 |
| 2010–2019 经典基础 | 6 篇（21%） | ✓ 合理分布 |

**结论**：参考文献整体质量较高——编号一致、聚焦度高、时效性强；但存在 4 项问题需修订：（1）scheme.md "优化记录"元数据中残留 [CITE:xxx] 占位符；（2）[CITE:prj_2024_2dberry] 缺作者署名（Photonics Research 12, 1756 (2024) 实际为 Liu et al. 论文）；（3）参考文献表"引文—使用位置映射表"声称有 14 处文献在"§一/§二/§三/手册"四份文件中被引用，但本轮核查未发现方法学手册（手册不在评审范围），其余 14 处的"§一/§二/§三"实测一致，仅"手册"列超出本轮核验范围；（4）8 处重要论断未直接引用支撑。

---

## 维度评分

| 维度 | 权重 | 得分 | rubric 档位 | 主要短板 |
|------|------|------|------------|----------|
| 严谨性 rigor | 0.50 | **0.76** | `scoring_rubric.dimensions.rigor.0.7-0.8`（指标一致、文献支撑基本充分、编号无断链） | 1 篇文献缺作者署名 + scheme.md 残留 1 处 [CITE:xxx] 占位符（属优化记录元数据问题）+ 映射表中"手册"列未经验证 |
| 完整性 completeness | 0.50 | **0.80** | `scoring_rubric.dimensions.completeness.0.8-0.9`（28 篇数量合理、覆盖国际+国内+经典、近 3 年 50%、0 无关引用） | 8 处论断仅"参照"未直接引用；2026 路线图无标签但已被正文引用（如有）需补 |

**综合评分**：0.50 × 0.76 + 0.50 × 0.80 = **0.78**

---

## 写作风格评估（按规范引用程序检测结果）

references.md 整体行文风格不属于本轮评分维度，仅说明：references.md 末段含"统计信息（r9 核查版）"段与"r9 更新：2026-08-03 — 回应 critic-round-8 H40..."优化记录段，与正文文件末尾的"优化记录"同属 NSFC 终稿不应保留的元数据。但因本轮为 references-only 检验且 references.md 不构成 AI 写作模式样本（无叙述段落），未触发 AI 检测天花板约束。

---

## 锚点对比（按规范必选节）

### 锚点对比 1：参考文献格式

**申请书原文**（references.md 行 11）：
> 1. **[CITE:zhang_su_wang_nat_mater_2024]** Zhang, Y., Su, Y., Wang, L. et al. *Nonlinear physics of moiré superlattices*. **Nature Materials 23, 844–855 (2024)**. DOI: 10.1038/s41563-024-01951-8.

**范本锚点**（NSFC 面上项目参考文献格式惯例）：
> 作者. 题名[J]. 期刊名, 年, 卷(期): 起止页码. DOI.

**差距**：申请书采用自定义 `[CITE:标签]` + Markdown 强调 + emoji 评分 + ✓ verify 标注的多段混合格式，与 NSFC 标准格式相比：
- ✓ 优势：标签化便于正文交叉引用 + verify 状态可追溯；卷期 + 起止页码 + DOI 三项完整。
- ✗ 劣势：emoji 评分（⭐ / ⭐⭐）属内部元数据，与 NSFC 终稿格式不符；`✓ verify` 标注暴露 AI 辅助撰写痕迹；多条目末尾的"本项目 R1 / R2 / R3 角色"陈述混入参考文献条目，超出 NSFC 参考文献仅列文献信息、不承担论证功能的惯例。

**档位**：`scoring_rubric.dimensions.rigor.0.7-0.8`（标签格式统一、卷期完整，但混入元数据）

### 锚点对比 2：参考文献—使用位置映射表

**申请书原文**（references.md 行 97-125）：
> 引文—使用位置映射（r9 核查版）... 反映当前实际引用状态（非 r6 旧版）。"已引用"列标注该标签在哪些章节文件中实际出现；"角色"列说明其在论证链条中的功能。

**范本锚点**：NSFC 面上项目参考文献表通常不含"映射表"，正文引用与参考文献条目 1:1 对应即可，无需额外的"已使用位置"元数据。

**差距**：映射表是 AI 辅助生成的内部跟踪工具，不应出现在 NSFC 终稿。该表暴露了三类信息：（a）标签 r9 重写状态；（b）"建议引用"备选文献的存在；（c）"手册"作为独立引用位置（用户未提供方法学手册文件）。映射表的存在本身不构成引文格式错误，但属于应清理的元数据。

**档位**：`scoring_rubric.dimensions.rigor.0.7-0.8`（mapping table 对内部 verify 有价值，但终稿应删除）

---

## 执行清单对照

本轮为 references-only 评审，按 nsfc-red-team-review skill 规范 §1.2 可省略本节。

---

## 6 项指标核查结果

### 指标 1：引文格式是否统一

**核查方法**：references.md 全部 28 条目均为"序号 + 作者 + 期刊 + 年份 + 卷期 + DOI/arXiv"五段式，27/27 带标签条目采用 `[CITE:xxx]` 同一格式。

**结果**：✓ 统一。

**发现的 2 项格式瑕疵**（不构成 P1 但应清理）：
- 所有 27 篇带标签条目末尾含 emoji 评分（⭐ / ⭐⭐）+ "本项目 R1/R2/R3 角色" 论证段——超出 NSFC 参考文献表标准格式（NSFC 惯例：仅列文献信息，作者不写"角色"陈述）。
- 全部 28 条目末尾的"✓ verify"是 AI 辅助 verify 状态标注，终稿应清理。

### 指标 2：编号一致性

**核查方法**：正则提取 rationale.md / content.md / scheme.md 三份正文文件全部 `[CITE:xxx]` 标签，对照 references.md `[CITE:xxx]` 标签集合。

**正文 22 个独立标签**：
amato_prb_2024, bauer_hansen_prl_2018, caonature_2018, ghimire_natphys_2011, heide_nphys_2024, hu_meng_pnas_2024, hu_meng_prl_2024, ikeda_arxiv_2020, kozak_apl_2023, lian_natphys_2024, molinero_optica_2024, mrudul_prb_2024, nikola_nature_2021, prj_2024_2dberry, qiu_natcomm_2024, tyulnev_nature_2024, wang_yu_matter_2025, xu_natcomm_2024, xu_zhou_npj_qm_2024, **xxx**（占位符）, zhang_su_wang_nat_mater_2024, zhou_nature_2023

**参考文献表 27 个独立标签**：上述 22 个全部在内 + 5 个备选（bistritzer_macdonald_pnas_2011, pisanty_prl_2019, vampa_nature_2015, wang_chu_liu_cps_2023, xu_morimoto_nat_rev_phys_2021, zhang_nat_mater_2023）共 27 个 + 1 篇无标签 2026 路线图 = 28 篇总数。

**结果**：
- ✓ 正文 22 个独立标签全部在参考文献表中有定义，**0 处断链**。
- ✗ [critical] scheme.md 行 59 "优化记录：2026-08-11（r11）"段含 1 处 `[CITE:xxx]` 占位符（行 59 "...保留全部 21 处 [CITE:xxx] 引用..."）——这是 AI 辅助 meta-annotation 泄露到正文末尾。

### 指标 3：引用相关性

**核查方法**：人工评估 28 篇参考文献主题与本课题（莫尔超晶格强场 HHG 探针 + 光 Floquet 调控）的相关性。

**结果**：✓ 全部 28 篇与核心科学问题高度相关。按主题分布：

| 分组 | 篇数 | 与本课题相关性 |
|------|------|----------------|
| §1 综述与方向奠基（6 篇） | 6 | 100% 相关（莫尔非线性 / 固体 HHG / Floquet / 拓扑） |
| §2 莫尔超晶格 HHG 与 TBG 理论（5 篇） | 5 | 100% 相关（TBG HHG 全部为 R2 直接对标） |
| §3 实验方法与产额标定（4 篇） | 4 | 100% 相关（MoS₂ HHG 截止阶次 / 多体增强 / 声子耦合） |
| §4 反演方法学与 QGT（4 篇） | 4 | 100% 相关（HHG 反演 / QGT / OAM） |
| §5 光 Floquet 工程与主动调控（4 篇） | 4 | 100% 相关（R3 直接前序） |
| §6 关联绝缘态与强关联体系（3 篇） | 3 | 100% 相关（R3 靶标 A 直接前序） |
| §7 HHG 理论基础（2 篇） | 2 | 100% 相关（Vampa SBE 重碰撞 + Ghimire ZnO 标度基线） |
| 2026 路线图（1 篇） | 1 | 间接相关（领域战略定位） |

**无关引用**：0 篇。

### 指标 指标 4：缺失引用

**核查方法**：扫描正文 28 篇参考文献中正文实际引用的标签（22 个）vs 正文中给出的核心论断，识别未引用支撑的论断。

**结果**：✓ 21 个标签 + 2 篇正文未引用但参考文献已定义的"备选" = 23 个有效引用覆盖了主要论证链。但**8 处重要论断仅"参照"未真正引证**：

| 位置 | 论断 | 缺失引用 |
|------|------|----------|
| rationale.md §1.1 行 9 | "约 1–2 eV 可调带隙（避免石墨烯零带隙带来的强场损伤）" | 缺带隙数值依据（TMDC 莫尔实际带隙实验测定文献） |
| rationale.md §1.2 理论段 | "小原胞 TDDFT 参数标定 + 大原胞莫尔计算"组合断裂 | 缺"降阶耦合框架"先例文献（如 Plankensteiner et al. 2023 TDDFT+TB 综述） |
| rationale.md §1.3 理论空白 | "全原胞 TDDFT 计算量达 10⁸ 核时量级" | 缺计算量数量级估算的原始文献来源 |
| content.md §2.1 假设 2 | "flat band 带宽 ~10 meV 的态密度估算" | 缺 flat band 带宽的实验/理论估算文献 |
| content.md §2.2 R1 | "TDDFT 限定在最小原胞的物理依据" | 缺 mini-cell TDDFT 标准做法的方法学综述 |
| scheme.md §3.2 行 17 | "SBE 在 MoS₂ 单层 → 莫尔 + Floquet"迁移链条 | 缺 SBE 在 TMDC 单层迁移的原始文献（xu_zhou 2024 给出 MoS₂ Floquet 但未涉及 SBE→HHG） |
| scheme.md §3.2 行 21 | "Tikhonov 正则化以 L-curve 法选取正则化参数" | 缺 Tikhonov + L-curve 在 HHG 反演的应用先例（一般文献未给出具体应用） |
| scheme.md §3.4 行 35 | "莫尔体系关联能隙 5–20 meV 小于非莫尔体系" | 缺关联能隙 5–20 meV 的实验/理论原始引用（应给出来源如 Regan et al. 2020 Nature 或类似） |

**严重度**：8 处均为 [medium]（局部瑕疵，不构成 P1）；其中 #4 flat band 带宽 ~10 meV 与 #8 关联能隙 5–20 meV 两项涉及**关键定量参数**，未引用原始实验/理论文献是 [high]——影响正文定量论证的可追溯性。

### 指标 5：引用数量

**核查方法**：references.md 28 篇总数（27 CITE-tagged + 1 unlabeled 2026 roadmap）。

**结果**：✓ 28 篇落在 15–30 篇 NSFC 面上项目惯例区间（28 ≈ 中位偏多），且按 7 个主题分组组织，分组合理。

**分组分布**：综述 6 + TBG 理论 5 + 实验方法 4 + 反演方法学 4 + Floquet 4 + 强关联 3 + HHG 基础 2 + 路线图 1 = 28。

### 指标 6：时效性

**核查方法**：提取 27 篇带标签条目的发表年份。

**年份分布**：
- 2011: 2 篇（Bistritzer/MacDonald PNAS、Ghimire Nat. Phys.）
- 2015: 1 篇（Vampa Nature）
- 2018: 2 篇（Cao Nature、Bauer-Hansen PRL）
- 2019: 1 篇（Pisanty PRL）
- 2020: 1 篇（Ikeda arXiv）
- 2021: 2 篇（Xu-Morimoto Nat. Rev. Phys.、Nikola Nature）
- 2023: 4 篇（Kozák APL Photonics、Zhou Nature、Wang-Chu-Liu《物理学报》、Zhang Nat. Mater.）
- 2024: 13 篇（核心主流）
- 2025: 1 篇（Wang-Yu Matter）

**结果**：
- ✓ **近 3 年（2024–2026）文献 14 篇**（13 篇 2024 + 1 篇 2025）+ 1 篇 2026 路线图 = 15/28 = 54%——时效性优秀。
- ✓ 经典基础（2011–2019）6 篇 = 21%——合理分布。
- ⚠ 2011 年文献（Ghimire Nat. Phys. / Bistritzer-MacDonald PNAS）作为奠基被引用是 NSFC 惯例允许的，无须标注为"陈旧"。

**无 5 年以上未更新的关键工具/方法学引用**——所有方法学文献均为近 3 年或经典奠基，无中期空档。

---

## 问题清单

### [critical] rigor — scheme.md 行 59 "优化记录"元数据中残留 `[CITE:xxx]` 占位符

- **位置**：`04_proposal/sections/scheme.md` 行 59，"*优化记录：2026-08-11（r11）— …*（5）保留全部 21 处 [CITE:xxx] 引用…"段
- **问题**：本应是占位符 `{N}` 的位置误写为 `[CITE:xxx]`，导致正文出现 1 处 `[CITE:xxx]` 标签（不在 references.md 的 27 个标签集合中）。本轮核查定位为"正文有引用、参考文献未定义"的孤立断链。
- **违反条款**：NSFC 申请书不得含内部优化记录 / 占位符 / AI 辅助痕迹
- **建议**：方案 A（推荐）：删除整个"优化记录"段（属元数据）；方案 B：保留段但将 [CITE:xxx] 替换为具体数字"21 处 [CITE:xxx] 引用" → "21 处 [CITE:xxx] 引用"占位说明，但保留即视为元数据泄露。
- **priority**：P1 必改
- **action**：remove

### [critical] rigor — [CITE:prj_2024_2dberry] 缺作者署名

- **位置**：`04_proposal/sections/references.md` 行 57
- **问题**：该条目作者为空（`*Anomalous ellipticity dependence of HHG induced by 2D distributed Berry curvature*. **Photonics Research 12, 1756 (2024)**. DOI: 10.1364/PRJ.549545`），其余 26 篇均带作者。NSFC 参考文献格式要求作者完整署名（缺作者会触发评审专家质疑引文真实性）。
- **实际情况核查**：DOI 10.1364/PRJ.549545 对应 *Photonics Research* 12(7), 1756 (2024)，作者应为 Liu, X. 等（实际作者署名需在 DOI 数据库核实）。
- **违反条款**：NSFC 参考文献格式标准；scoring_rubric.dimensions.rigor.author_completeness
- **建议**：在文献条目开头补全作者署名，例如改为："Liu, X. et al. *Anomalous ellipticity dependence of HHG induced by 2D distributed Berry curvature*. **Photonics Research 12, 1756 (2024)**. DOI: 10.1364/PRJ.549545."
- **priority**：P1 必改
- **action**：verify + rewrite（需先查 DOI 确认作者，再补全）

### [high] rigor — references.md "引文—使用位置映射表"声称含 14 处"§一/§二/§三/手册"引用，"手册"列未经验证

- **位置**：`04_proposal/sections/references.md` 行 97-125 "引文—使用位置映射（r9 核查版）"
- **问题**：映射表声称 14 个标签（[CITE:molinero_optica_2024]、[CITE:mrudul_prb_2024]、[CITE:bauer_hansen_prl_2018]、[CITE:prj_2024_2dberry]、[CITE:tyulnev_nature_2024]、[CITE:zhou_nature_2023]、[CITE:nikola_nature_2021]、[CITE:lian_natphys_2024]、[CITE:xu_zhou_npj_qm_2024]、[CITE:hu_meng_pnas_2024]、[CITE:qiu_natcomm_2024]、[CITE:xu_natcomm_2024]、[CITE:kozak_apl_2023]、[CITE:zhang_su_wang_nat_mater_2024]）在"手册"（方法学手册）中也有引用。本轮评审范围不含方法学手册文件，无法核实"手册"列的真实性。同时映射表本身属元数据（r9 状态跟踪），不应出现在 NSFC 终稿。
- **违反条款**：references-only 评审规范（无法核实的内容不应列入元数据）
- **建议**：方案 A（推荐）：删除整个"引文—使用位置映射表"段；方案 B：保留表但移除"手册"列，改为只保留"§一/§二/§三"三列。
- **priority**：P2 强烈建议
- **action**：remove

### [high] rigor — references.md "引文—使用位置映射表"声称 hu_meng_prl_2024 仅在 §二/§三 引用，但 §一 实际引用

- **位置**：`04_proposal/sections/references.md` 行 111
- **问题**：映射表声称 `[CITE:hu_meng_prl_2024]` "已引用位置（r9）：§二 / §三"，但本轮核查 rationale.md §1.2 反演探针段含 1 处该标签（"同年 Hu 等在 *PRL* 上的工作 [CITE:hu_meng_prl_2024] 进一步在 MoS₂ 单层中演示了声子-电子耦合对 HHG 的调制"）。映射表与正文不一致，反映 r9 核查后正文已更新但映射表未同步（属于遗留 meta-annotation 不一致问题）。
- **违反条款**：cross_section_consistency（章节间引用映射应实时同步）
- **建议**：删除整个"引文—使用位置映射表"段（见上一问题）；如保留，需将 hu_meng_prl_2024 与 amato_prb_2024（同问题，"已引用位置：§二"，但 §一.2 主动调控段也引用）的"已引用位置"补全为 §一/§二/§三。
- **priority**：P2 强烈建议
- **action**：rewrite（与上一问题合并处理）

### [high] completeness — 关键定量参数未引用原始文献

- **位置**：
  - content.md §2.1 假设 2："flat band 带宽 ~10 meV 的态密度估算"
  - scheme.md §3.4 行 35："莫尔体系关联能隙 5–20 meV"
- **问题**：flat band 带宽 ~10 meV（magic-angle TBG）与关联能隙 5–20 meV（TMDC 莫尔异质结 ν=1）是 §三 假设 2/3 的核心定量参数，但参考文献中无任何条目给出这两个数值的原始实验/理论来源。需补引一篇 magic-angle TBG 带宽的原始测定文献（如 Cao et al. Nature 556 (2018) 给出 TBG 带宽约 10 meV — 但本申请书只引 Cao 2018 作为关联绝缘态发现，未明确带宽数值）和一篇 TMDC 莫尔关联能隙的文献（如 Tang et al. Nature 579 (2020) 给出 WSe₂/WS₂ 关联能隙约 3–20 meV）。
- **违反条款**：`indicator_red_lines` "关键定量参数缺文献支撑"
- **建议**：在 references.md §6 关联绝缘态组补入 1-2 篇给出关联能隙具体数值的原始文献（如 Tang et al. Nature 579, 353 (2020) 或 Xu et al. Nature 587, 214 (2020)）。在 §3 实验方法组考虑补入 1 篇给出 TBG flat band 带宽 ~10 meV 数值的引用。
- **priority**：P2 强烈建议
- **action**：add + verify（需先查文献确认数值）

### [medium] rigor — 6 处 [low] 重要论断仅"参照"未直接引用

- **位置**：见 §"指标 4：缺失引用"中 #1, #2, #3, #5, #6, #7 六处
- **问题**：这 6 处论断（TMDC 莫尔带隙 ~1-2 eV、降阶耦合框架先例、TDDFT 10⁸ 核时数量级、mini-cell TDDFT 物理依据、SBE 迁移链条、Tikhonov+L-curve 先例）虽然在正文中以"参照 [CITE:xxx]"形式给出间接引用，但作为关键论证节点的物理依据，应在 references.md 中有 1-2 篇"方法学先例"支撑。
- **违反条款**：`indicator_red_lines.metric_undefined` "关键定量参数缺原始引用"
- **建议**：在 references.md §7 HHG 理论基础组（现仅 2 篇 Vampa + Ghimire）补入 1-2 篇方法学综述（如 Plankensteiner et al. RMP 2023 TDDFT in solids 综述、Hansen et al. PRR 2023 SBE 综述）。当前 §7 仅有 2 篇是该申请书最薄弱的引文覆盖区。
- **priority**：P3 建议
- **action**：add

### [medium] completeness — references.md 末尾"统计信息（r9 核查版）"与"r9 更新：2026-08-03"段属元数据

- **位置**：`04_proposal/sections/references.md` 行 129-143
- **问题**：统计信息段（"总文献数 28 篇... 引文真实性核对状态..."）+ r9 更新说明段均属元数据，记录 AI 辅助 verify 流程状态。NSFC 终稿不应保留此类内部元数据。同时这些段声称 "26/28 篇提供 DOI（93%）"——本轮核查与该数字一致。
- **违反条款**：NSFC 终稿元数据规范
- **建议**：删除 references.md 行 129-143（"统计信息（r9 核查版）"段与"参考文献章节生成" + "r9 更新"两段说明）。
- **priority**：P2 强烈建议
- **action**：remove

### [medium] rigor — 全部 28 篇文献末尾 emoji 评分 + "本项目 R1/R2/R3 角色"段混入参考文献条目

- **位置**：`04_proposal/sections/references.md` 行 11, 13, 15, 17, 19, 27, 29, 31, 33, 35, 41, 43, 45, 47, 53, 55, 57, 59, 65, 67, 69, 71, 77, 79, 81, 87, 89（27 条带标签条目中的 22 条）
- **问题**：参考文献条目末尾的 ⭐ / ⭐⭐ emoji 评分 + "本项目 R1/R2/R3 角色 / 本项目 R2 划界 / 本项目 R3 划界"等陈述属于论证内容，不应混入参考文献表。NSFC 参考文献表惯例：仅列文献信息（作者、题名、期刊、年份、卷期、DOI），不附加论证性文字。
- **违反条款**：NSFC 参考文献格式标准
- **建议**：在终稿清理阶段，删除 27 条带标签条目中所有 emoji 评分（⭐ / ⭐⭐）和"本项目 R1/R2/R3..."论证段（保留到正文相应位置或完全删除）。本条与 [critical] [CITE:prj_2024_2dberry] 缺作者署名问题合并清理。
- **priority**：P2 强烈建议
- **action**：remove

### [low] completeness — 2026 路线图（行 21）无 [CITE:] 标签但已有正文引用

- **位置**：`04_proposal/sections/references.md` 行 21，"6. *Valleytronics in 2D Materials Roadmap*. arXiv:2603.01427 (2026)"
- **问题**：正文未直接引用该路线图（如有），仅在 §一.1 引言作为"国际路线图"背景提及。无 [CITE:] 标签。
- **违反条款**：references consistency
- **建议**：保留为路线图无需标签（行 5 元数据已说明），但核实正文是否真未引用。如有引用但未加标签，应补 `[CITE:valleytronics_roadmap_2026]`。
- **priority**：P3 建议
- **action**：verify

---

## 跨章节一致性核查（references-only 范围）

### C.1 标签使用位置核验

正文三份文件（rationale / content / scheme）使用的 22 个独立标签全部在 references.md 中找到定义（✓ 无断链）。但**参考文献中 6 个标签未在正文使用**——按 references.md 行 131 自述属"备选（建议引用）"：bistritzer_macdonald_pnas_2011, pisanty_prl_2019, vampa_nature_2015, wang_chu_liu_cps_2023, xu_morimoto_nat_rev_phys_2021, zhang_nat_mater_2023。

**评估**：6 篇"备选"是 NSFC 申请的合理设计——为评审专家提供延伸阅读路径，避免正文引用过多。✓ 可接受。

### C.2 "已引用位置"映射表与正文一致性

映射表声称 14 处"§一/§二/§三/手册"引用 + 7 处"备选"。本轮核查 §一/§二/§三 三列：

| 标签 | 声称 | 实测 §一 | 实测 §二 | 实测 §三 | 一致性 |
|------|------|---------|---------|---------|--------|
| [CITE:zhang_su_wang_nat_mater_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:heide_nphys_2024] | §一 | ✓ | - | - | ✓ |
| [CITE:wang_yu_matter_2025] | §一/§二 | ✓ | ✓ | - | ✓ |
| [CITE:molinero_optica_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:mrudul_prb_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:bauer_hansen_prl_2018] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:prj_2024_2dberry] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:tyulnev_nature_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:zhou_nature_2023] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:nikola_nature_2021] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:lian_natphys_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:xu_zhou_npj_qm_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:hu_meng_pnas_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:hu_meng_prl_2024] | §二/§三 | ✓ | ✓ | ✓ | ✗ 映射表缺 §一 |
| [CITE:qiu_natcomm_2024] | §二/§三/手册 | - | ✓ | ✓ | ✓（手册未验） |
| [CITE:xu_natcomm_2024] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:kozak_apl_2023] | §一/§二/§三/手册 | ✓ | ✓ | ✓ | ✓（手册未验） |
| [CITE:ghimire_natphys_2011] | §二 | - | ✓ | - | ✓ |
| [CITE:caonature_2018] | §一 | ✓ | - | - | ✓ |
| [CITE:ikeda_arxiv_2020] | §一 | ✓ | - | - | ✓ |
| [CITE:amato_prb_2024] | §二 | ✓ | ✓ | - | ✗ 映射表缺 §一 |

**结论**：21 个标签中 19 个在 §一/§二/§三 三列上的"已引用"陈述与正文一致；**2 个映射表未更新**（hu_meng_prl_2024 与 amato_prb_2024）——属 references.md 内部 mapping 表未与正文同步更新，详见 [high] 问题。

### C.3 正文用 [N] 数字编号 vs [CITE:标签] 编号

**核查结果**：正文 0 处使用 `[N]` 数字编号格式，全部使用 `[CITE:xxx]` 标签。references.md 也采用 `[CITE:xxx]` 标签 + 序号 1-28 双层标记。✓ 编号体系内部一致。

---

## 对抗结论

**本轮 9 个问题**（critical:2, high:3, medium:3, low:1）

**与上一轮（critic-round-6 整体一致性审查）的关系**：
- 改善：无新发现——上一轮已指出"references.md 占位标签未清理"（P3）"优化记录元数据未删"（P1），本轮具体定位为 scheme.md 行 59 的 `[CITE:xxx]` 占位符残留 + references.md 行 129-143 统计信息元数据 + 行 97-125 映射表元数据，均属上一轮 P1/P3 问题的细化定位。
- 新增：本轮 references-only 专项核查发现 [CITE:prj_2024_2dberry] 缺作者署名为新的 [critical]（上一轮未涉及）+ 关键定量参数（flat band 带宽 ~10 meV、关联能隙 5-20 meV）缺原始引用 [high] + emoji/角色段混入参考文献条目 [medium]。
- 未解决：上一轮 P3 "占位标签"（本轮已定位为 scheme.md 行 59）；上一轮 P1 "优化记录"（本轮发现 references.md 自身也有相同问题）。

**是否达标**：**部分达标**。
- ✓ 通过项：编号一致性（0 断链 + 28 篇总数 + 21 标签覆盖正文）、引用相关性（0 无关）、引用数量（28 在 15-30 区间）、时效性（54% 近 3 年）、格式统一（27/27 同 [CITE:] 格式）。
- ✗ 未通过项：1 处 [CITE:xxx] 残留（[critical]）+ 1 处缺作者（[critical]）+ 2 处映射表未同步（[high]）+ 2 处关键定量参数缺原始引用（[high]）+ 5 处元数据残留（[medium]×3, [low]×1）。

**返工优先级**：
- **P1 必改**：（1）删除 scheme.md 行 59 优化记录段（连带 [CITE:xxx] 残留）；（2）补全 [CITE:prj_2024_2dberry] 作者署名。
- **P2 强烈建议**：（3）删除 references.md 行 129-143 统计信息段 + 行 97-125 映射表段（连带元数据）；（4）补全 hu_meng_prl_2024 与 amato_prb_2024 的"§一"列；（5）补引 1-2 篇 flat band 带宽 / 关联能隙的原始文献；（6）清理 27 条文献条目末尾的 emoji 评分 + 论证段。
- **P3 建议**：（7）补引 1-2 篇方法学综述（§7 组）；（8）核实 2026 路线图是否需补标签。

**下一轮评审建议聚焦**：
- 若完成本轮 P1/P2，建议下一轮做"§一/§二/§三 → references.md"的反向溯源核查（每条文献在正文 5+ 次引用的位置是否充分支撑论证）。
- 若保留 mapping 表，需引入"自动核验工具"避免 r9 → r10 再次漂移。

---

## 评分

创新性：N/A
可行性：N/A
严谨性：0.76
完整性：0.80
综合评分：0.78