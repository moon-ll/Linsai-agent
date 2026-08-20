# 对抗评审报告（第 3 轮 · 参考文献专项）

项目路径：general-order-parameter-ultrafast-readout-20260727
聚焦章节：references.md（参考文献表） vs. rationale.md / content.md / scheme.md（正文）
项目类型：general（面上项目）
评审日期：2026-08-19
profile：critic
本轮范围：参考文献专项（引文格式、编号一致性、引用相关性、缺失引用、引用数量、时效性）
不在本轮范围：写作风格、创新性、可行性（按任务定义标 N/A）

================================================================
## 综合评分

0.40 / 1.00（严谨性 0.30 × 0.50 + 完整性 0.50 × 0.50；评分公式自洽）

================================================================
## 维度评分

| 维度 | 权重 | 得分 | 问题数 | rubric 档位依据 |
|------|------|------|--------|---------------|
| 严谨性（引文格式、编号一致性、作者信息完整性） | 0.50 | 0.30 | critical:3, high:3, medium:2, low:2 | §6 系统性编号错位未根治（R2 报告 4 条 critical 中 0 条解决，新增 2 条反向错位）；references.md 自检段反向固化错位 |
| 完整性（引用数量、时效性、缺失引用） | 0.50 | 0.50 | critical:0, high:2, medium:1, low:2 | 数量 40 条达标；时效性 33/40 = 82.5%（pre-2023 仅 7 条合理保留）；但 [55] [64] 两条孤儿条目 + CrSb/Rost 仍缺失条目 + 关键材料参数无独立引用，完整性受拖累 |
| 创新性 | N/A | N/A | — | 本轮不评 |
| 可行性 | N/A | N/A | — | 本轮不评 |

================================================================
## 问题清单

### [critical] systematic_offset — references §6 与正文 [62]—[67] 编号系统性 +1 错位（R2 报告未根治）

- **位置**（跨章节 18+ 处）：
  - 正文用 [62] 指 Cochran：rationale.md L51, L83, L85；content.md L41, L53；scheme.md L41, L73, L95（合计 8 处）
  - 正文用 [63] 指 Sørensen：rationale.md L45, L51, L63, L83, L85；content.md L27, L41, L51, L53；scheme.md L41, L73, L81, L83, L95（合计 14 处）
  - references.md 中：[62] = Uzner（层间耦合）；[63] = Cochran（唯一性分析）；[64] = Sørensen（非唯一性）
- **问题**：body → references 的映射关系与 R2 报告状态完全一致——正文 [62]/[63] 在 references.md 中实为 Uzner/Cochran，而 body 实际想引的是 Cochran/Sørensen。这是 §5 与 §6 边界处的系统性 +1 错位：正文假设 §5 末尾停在 [61] Uzner，§6 从 [62] Cochran 开始；但 references.md 把 [62] 给了 Uzner、把 §6 的 Cochran/Sørensen 整体推迟到 [63]/[64]。R2 报告已指出此问题并给出方案 A（references 整组前移 1 位并补 [67] Rost），但本轮核查显示 references.md §6 编号未动，正文编号亦未动，错位原封不动保留。
- **违反条款**：`indicator_red_lines.consistency_check`；`scoring_rubric.rigor.0.60-69` 之"存在事实错误"档；`section_standards.references`"无张冠李戴"。
- **后果**：NSFC 评审专家对照 references.md 表核对编号时，会在 rationale.md L39 第一处 "Cochran [62]" 即发现"按 references [62] 应是 Uzner"，引文系统立即 fail-fast。这是 NSFC 评审中最容易识别的硬伤。
- **建议（rewrite）**：
  - 方案 A（推荐）：把 references.md §6 整组向前挪 1 位：Cochran [63]→[62]、Sørensen [64]→[63]、Fuchs [65]→[64]、McCarter [66]→[65]、Horstmann [67]→[66]；并在 [66] 后新增 [67] = Rost et al. CrSb HHG arXiv:2507.02673 (2025)；同步更新 references.md L121、L123、L125、L127、L131、L133、L149、L153、L155、L161 全部编号映射与状态说明。
  - 方案 B（保守）：保留 references.md 编号不动，把正文 18 处 [62]→[63]、[63]→[64]，并在 references.md 新增 [68] = Rost et al. 条目。
- **action**：rewrite

### [critical] systematic_offset — content.md §2.3 L23 [65][66] 反向错位（McCarter/Horstmann）

- **位置**：content.md L23 "Leeb 等人 2025 年 [58a]、McCarter 等人 2025 年 [65]、Horstmann 等人 2025 年 [66] 三项工作..."
- **问题**：按 references.md，[65] = Fuchs（MnTe 自旋极化 HHG），[66] = McCarter（ab initio），[67] = Horstmann（选择定则）。该句把 McCarter 标 [65]、Horstmann 标 [66]——与 #1 的 +1 错位**方向相反**（-1 错位），即同一项目内两套错位互相叠加。该句实际应为 "Leeb 等人 2025 年 [58a]、McCarter 等人 2025 年 [66]、Horstmann 等人 2025 年 [67]"。
- **违反条款**：`indicator_red_lines.consistency_check`；`section_standards.references`"无张冠李戴"。
- **建议**：content.md L23 改为 "Leeb 等人 2025 年 [58a]、McCarter 等人 2025 年 [66]、Horstmann 等人 2025 年 [67] 三项工作把候选信号的对称性约束从二元极限推广到连续参数区间"。
- **action**：rewrite

### [critical] orphan_citation — Rost arXiv:2507.02673 在 references.md 仍无独立条目

- **位置**：
  - 正文 6 处用 [67] 指 Rost：rationale.md L33, L63, L77（3 处）；content.md L21, L51（2 处）；另 1 处 content.md L51（"Rost 等人 2025 年 [67]"）
  - references.md 全文搜索 "Rost" / "2507.02673" **0 命中**
  - scheme.md L53, L73 已用纯 arXiv 文本绕过（"Rost 等人（arXiv:2507.02673, 2025）"），但 rationale.md/content.md 6 处仍用 [67] 编号引用
- **问题**：Rost 工作是本项目"CrSb 信号可探测前提"的核心实验依据，被正文 6 处用 [67] 编号引用，但 references.md 完全没有该工作的正式条目。按 references.md 现在的编号体系，[67] = Horstmann（理论选择定则），正文用 [67] 指 Rost 完全错位。这是 R2 报告 #3 遗留问题，本轮未解决。
- **违反条款**：`indicator_red_lines.novelty_claim_cautious`；`section_standards.references`"参考文献 30-40 篇，编号连续无跳号"。
- **建议**：与 #1 一并处理。在 references.md §6 末尾新增 [68] = "Rost, S. M. et al. Intercalated magnetic fingerprints in CrSb from spin-resolved high-harmonic generation. arXiv:2507.02673 (2025). 【预印本】" 条目，并把正文 6 处 [67]→[68]。若采用 #1 方案 A，则 Rost 占位为 [67]、正文 6 处不动。
- **action**：rewrite + research（须先核实 arXiv:2507.02673 是否存在）

### [high] numbering_doc_contradiction — references.md §6 自检段反向固化错位编号映射

- **位置**：
  - references.md L121 "§6 本组共 5 条文献（[63]—[67]），... [63] Cochran 给出唯一性条件分析框架；... [64] Sørensen 从解析与数值两方面..."
  - references.md L123 "三条 altermagnet HHG 实验 / 理论里程碑... [65] Fuchs... [66] McCarter... [67] Horstmann..."
  - references.md L155 "具体引用位置：[63] Cochran 在 rationale.md:49 引用；[64] Sørensen 在 rationale.md:49 引用；[65] Fuchs 在 rationale.md:31 以纯 arXiv 文本引用；[66] McCarter 在 rationale.md:35 以纯 arXiv 文本引用；[67] Horstmann 在 rationale.md:35 以纯 arXiv 文本引用；[58b] Qiu 在 rationale.md:35 与 content.md:33 引用。"
- **问题**：references.md 内部 L121/L123/L155 自述的 [63] Cochran / [64] Sørensen / [65] Fuchs / [66] McCarter / [67] Horstmann 编号体系，**与 references.md L125/L127/L129/L131/L133 实际条目 [63]=Cochran/[64]=Sørensen/[65]=Fuchs/[66]=McCarter/[67]=Horstmann 一致**——但 references.md 把 [63][64] 描述为"在 rationale.md:49 引用"，实际 rationale.md L49 是孟胜/李亮兰鹏飞段，**完全不出现 Cochran 或 Sørensen**。Cochran/Sørensen 实际出现在 rationale.md L39, L45, L51, L63, L83, L85——references.md 自检段把行号也写错了。
- **违反条款**：`indicator_red_lines.consistency_check`；`section_standards.full_review`"无跨章节内容重复"。
- **建议**：与 #1 一并处理。在 references.md §6 整组前移 1 位后，重写 L121、L123、L155、L161 的所有编号映射与行号引用，确保 references.md 自检段与正文引用位置严格一致。
- **action**：rewrite

### [high] year_inconsistency — [24] Werner 在 references.md 与正文跨文档年份不一致（2024 vs 2026）

- **位置**：
  - references.md 条目 L71 "[24] Werner, P., Lysne, M. & Murakami, Y. High harmonic generation in altermagnets. *Phys. Rev. B* **114**, 035107 **(2026)**. DOI: 10.1103/PhysRevB.114.035107; arXiv:2407.07752. 【正式发表】"
  - references.md 自述段 L63 "[24] Werner **2024** PRB 系统预言..."（**2024 错**）
  - references.md 自述段 L123 "[24] Werner **2024** 框架相互印证"（**2024 错**）
  - content.md L23 "Werner 等人 **2024 年** [24]..."（**2024 错**）
  - scheme.md L77 "Werner et al., **2026** [24]..."（**2026 对**）
  - scheme.md L25, L73 "Werner 等人 [24]"（无年份）
  - rationale.md L29 仅写 "Werner 等人的理论工作... [24]"（无年份）
- **问题**：references.md 条目给出 PRB 114, 035107 (2026) 是正确刊期，但 references.md 自述段 L63、L123 与 content.md L23 三处写"2024"，scheme.md L77 写"2026"。**5 处正文/自述与 references 条目年份冲突**，评审按 references 条目核对时会发现正文"2024"为误。
- **违反条款**：`indicator_red_lines.consistency_check`；`section_standards.references`"作者、年份、期刊、卷页是否完整"。
- **建议**：把 references.md L63、L123 与 content.md L23 三处"2024"统一改为"2026"，与 references.md 条目及 scheme.md L77 一致。
- **action**：rewrite

### [high] unused_entry — [55] Jita 与 [64] Sørensen 两条参考文献正文未以 [N] 引用

- **位置**：
  - references.md L87 "[55] Jita, Y. et al. Magnon harmonic generation in antiferromagnets: Dynamical symmetry enriched by symmetry breaking. arXiv:2604.06700 (2026). 【预印本】"
  - references.md L127 "[64] Sørensen, L. K. K., Silva, M. M. S. F., Johansen, A. S. et al. Non-uniqueness in high harmonic spectroscopy of magnetic order. arXiv:2605.14873 (2025). 【预印本】"
  - 正文（rationale.md/content.md/scheme.md）grep "[55]" → **0 命中**；grep "[64]" → **0 命中**
- **问题**：
  - [55] Jita 在正文无任何引用，仅在 references.md §4 自述段 L63 被提到一次（"Jita 2026 与 [56] Sankar 2025 分别给出反铁磁三相选择定则..."），属于"研读基础"性质。
  - [64] Sørensen 在正文无任何 [N] 引用——这是最严重的问题，因为正文反复需要 Sørensen 的非唯一性结论（rationale.md 7 处 Sørensen 描述、content.md 6 处、scheme.md 7 处）但全部用 [63]（实为 Cochran 编号）指代。**Sørensen 工作实际被引述却无对应编号条目**。
  - 注：references.md §6 自述段 L121 写 "[64] Sørensen 从解析与数值两方面..."，但正文未用 [64] 引用 Sørensen——[64] 是孤儿条目。
- **违反条款**：`section_standards.references`"无幽灵编号"；"正文有 [N] 角标与参考文献对应"。
- **建议**：采用 #1 方案 A 即可一并解决——前移后 [63] = Sørensen 即对应正文所有 [63] Sørensen 引用；Jita [55] 转入正文使用（如 rationale.md §2 末段加一句"反铁磁 magnon HHG 三相选择定则详见 Jita 等人 [55]"），或保留为研读基础但在 references.md §8 自检段显式声明"[55] Jita 为研读基础，正文未直接引用"。
- **action**：rewrite

### [medium] metadata_inconsistency — references.md 自报"参考文献总数 39 条"与实测 40 条不一致

- **位置**：
  - references.md L5 "正文（rationale.md、content.md、scheme.md）以 [N] 编号直接引用的文献共 **39 条**"
  - references.md L153 "全表 39 个 [N] 条目（含 [58a]、[58b] 双编号）..."
  - references.md L161 "参考文献总数 **39 条**（正文 [N] 编号条目 39 个，含 [58a]、[58b] 双编号；...）"
  - 实测：references.md 实际有 40 个 [N] 起始行（[58a] 与 [58b] 算两条独立条目）
- **问题**：references.md 自报"39 条"是把 [58a]/[58b] 视为"双编号 = 1 条"的语义合并，但实际文献表里这两条是分行列出的两个独立条目（[58a] Leeb 2025 与 [58b] Qiu 2025 是两篇不同的工作）。计数与"39 条"差 1。
- **违反条款**：`section_standards.references`"参考文献 30-40 篇"（数量合规，但自报数与实测不一致）；`scoring_rubric.completeness`。
- **建议**：将 references.md L5、L153、L161 三处"39 条"改为"40 条（含 [58a]、[58b] 两个独立条目）"或保留"39 条正文以 [N] 引用"但显式标注"文献表共 40 个 [N] 起始行（含 [58a]/[58b] 拆分）"。
- **action**：rewrite

### [medium] missing_citation — CrSb 关键材料参数独立句无文献支撑（R1/R2 报告遗留）

- **位置**：
  - rationale.md §4 L77 "CrSb 带隙约 0.13 eV（间接）与 0.6 eV（直接）"
  - rationale.md §4 L77 "中红外 3—5 μm 驱动光对应的光子能量 0.25—0.41 eV"
  - scheme.md §1 L19 "CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）vs. 中红外 3—5 μm 驱动的 0.25—0.41 eV 光子能量"
  - scheme.md §3 L53, L67 "CrSb 的 Néel 温度约 720 K"
- **问题**：CrSb 的带隙、Néel 温度、Sb 原子 SOC 强度（100—200 meV）这些实验条件选择判据的参数，在正文以独立句形式给出但无独立文献支撑。NSFC 评审会问"0.13/0.6 eV / 720 K / 100—200 meV 引自哪里"。R1/R2 报告均已标记，本轮仍未补。
- **违反条款**：`indicator_red_lines.indicator_measurable`；`section_standards.references`"引用集合完备"。
- **建议**：在 references.md §6 末尾新增 CrSb 物性参数原始文献条目，例如：
  - [新] Reimers, S. et al. Altermagnetic band structure of CrSb. Phys. Rev. B (2025) 或类似第一性原理 / ARPES 实验的 CrSb 物性来源。
  - 若实在无法补原始文献，至少在 rationale.md §4 与 scheme.md §1、§3 紧邻参数处加注"CrSb 物性参数参见 Šmejkal et al., 2022 [25] 附录 / CrSb ARPES 实验原文 [新增条目]"。
- **action**：add + research

### [low] preprint_ratio — 预印本占比 20/40 = 50%（与 R1 报告持平）

- **位置**：references.md L159 "证据等级：正式发表 20 条（含综述 1 条：[39]）、预印本 19 条..."
- **实测**：正式发表 20 条（含综述 1 条）、预印本 20 条，合计 40 条；预印本占 50%（与 R1 报告持平）
- **问题**：50% 预印本比例高于面上项目评审人期望（通常 ≤ 30%）。但 altermagnet HHG 是 2024—2026 年才起步的新兴领域，§6 整组（[63]—[67] 现编号）和 §5 部分（[35][36][62]）均为 arXiv 预印本，是该领域的客观事实。该项不构成"违反规则"，但应在评审口径下提示。
- **违反条款**：`anti_ai_patterns.quantitative_thresholds.preprint_ratio`（无强制约束）；属评审偏好提示。
- **建议**：保留现状，但在 references.md 时效性说明段补充一条"§6 中预印本 5 条均为 altermagnet HHG 2025—2026 年里程碑工作，建议项目执行期内持续跟踪正式发表状态"。
- **action**：rewrite

### [low] numbering_strategy_documentation — 编号策略自述与"非连续 + 字母后缀"冲突未澄清

- **位置**：references.md L149 "组间预留空号 21 个"；L5 "组间预留空号 21 个"
- **实测**：references.md 实际空号 27 个：[4, 6, 8, 14, 17, 18, 19, 21, 25（注：§4 中 [25] 已被 Šmejkal 占用）、32, 33, 34, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]——共 28 个空号位（[25] 已被占用故不计）。
- **问题**：references.md 自报"21 个空号位"与实际"27+ 个空号位"差 6+。同时 [58a]/[58b] 字母后缀与"组内连续编号"原则（references.md L147）冲突——[58a] 与 [58b] 之间插入了 [59] Yue 的位置（实际 references.md §5 中 [59] 是 Yue，§4 中 [58a]/[58b] 之后跳号至 [55]）。编号体系"组内连续 + 组间预留"是 references.md 自定的设计原则，但 [58a]/[58b] 是 §4 内部的字母后缀且实际跨组（§5 紧接 [59]），违反组内连续原则。
- **违反条款**：`section_standards.references`"编号策略自洽"。
- **建议**：将 references.md L5、L149 的"21 个空号位"改为实际计数（"27+ 个预留空号"）；并在 §4 编号策略自述段补充一条说明 [58a]/[58b] 字母后缀的合法理由（共享第一作者 Leeb，2025 年两篇独立工作的姊妹条目）。
- **action**：rewrite

================================================================
## 评分细则说明

### 严谨性（rigor）— 0.30
- 引文格式：基本统一使用 [N] 编号，作者、年份、期刊、卷期、DOI/arXiv 双标识完整（得 0.85）。
- 但编号一致性严重失败：
  - references.md §6 与正文 +1 系统错位（critical #1，18+ 处）
  - content.md §2.3 [65][66] 反向错位（critical #2，1 处）
  - [24] Werner 年份 5 处跨文档不一致（high #5）
  - references.md 自检段反向固化错位（high #4）
  - 元数据自报计数与实测差 1（medium #7）
- 推导：基础格式 0.85 × 0.3 + 一致性 0.05 × 0.7 ≈ 0.30。

### 完整性（completeness）— 0.50
- 数量 40 条，处于 NSFC 标杆区间（30—50）（得 0.85）。
- 时效性：40 条中 33 条在 2023—2026 年（82.5%），pre-2023 仅 7 条且均为方法学经典锚点（[2] 2017、[23] 2019、[1] 2020、[3] 2022、[15] 2022、[59] 2020、[10] 2024 标注 2025）（得 0.90）。
- 但 [55] [64] 两条孤儿条目（high #6）+ Rost CrSb 实验仍缺失条目（critical #3）+ CrSb 关键材料参数无独立引用（medium #8），完整性受拖累。
- 推导：数量 0.85 × 0.3 + 时效性 0.90 × 0.3 + 引用集合完备性 0.10 × 0.4 ≈ 0.50。

================================================================
## 锚点对比（参考文献一致性专项）

### 引用样本 1 — references.md §6 第 1 条（Cochran）

**references.md 原文**：
> [63] Cochran, T. A., McCarter, M. R., Horstmann, J. G. et al. Reconstructing altermagnetic order parameters via high harmonic spectroscopy: uniqueness analysis. arXiv:2606.15279 (2025). 【预印本】

**正文对应**（按 references 编号体系）：
- rationale.md L51 "Cochran [62]"；L83 "Cochran 等人... [62]"；L85 "Cochran et al. [62]"
- content.md L41 "Cochran 等人 2025 年 [62]"；L51 "Cochran [62]"；L53 "Cochran 等人 [62]"
- scheme.md L41 "Cochran 等人的... [62]"；L73 "Cochran 等人... [62]"；L95 "Cochran 等人 [62]"

**差距**：
- 正文全部用 [62] 指 Cochran，但 references [63] 才是 Cochran，差 1。
- 正文 [62] 在 references 中实为 Uzner & Neufeld（层间耦合工作），形成系统性错位。
- 后果：评审按 references 表查 [62] 不会找到 Cochran 工作，会按 Uzner 工作去读——评审在核对 Cochran 唯一性分析框架时会发现 references 表里没有 [62] Cochran 条目，**引文系统 fail-fast**。

### 引用样本 2 — references.md §5 第 1 条（Yue）

**references.md 原文**：
> [59] Yue, L. & Gaarde, M. B. Structure- and laser-gauges for the semiconductor Bloch equations in high harmonic generation in solids. *Phys. Rev. A* **102**, 013119 (2020). DOI: 10.1103/PhysRevA.102.013119; arXiv:2003.02961. 【正式发表】

**正文对应**（按 references 编号体系）：
- scheme.md L25 "Yue 与 Gaarde... [59]"（一致 ✓）
- content.md L35 "其适用条件在文献 [59]—[61] 的 SBE 规范、场强窗口、Keldysh 区间方法学三角内"（一致 ✓）
- scheme.md L73 "其规范一致性由 Yue 与 Gaarde [59] 保证"（一致 ✓）
- scheme.md L49 "Wang 等人实验观测到... [59]"——按 references，[59] = Yue 而非 Wang ❌（与本表内 scheme.md L25 一致，但 scheme.md L49 行内嵌入的是 "Wang et al., *Opt. Express* 30, 46417, 2022 [59]"，按 references [59] 是 Yue 不是 Wang，**正文内部也不一致**）

**差距**：
- references.md §5 内编号 [59]=Yue、[60]=Wang、[61]=Zhang、[62]=Uzner 与 scheme.md L25/L73 完全一致 ✓
- 但 scheme.md L49 "Wang et al., *Opt. Express* 30, 46417, 2022 [59]" 中 [59] 编号与 "Wang" 作者不匹配——L49 的 [59] 实际应为 [60]。
- 这是 scheme.md 单章内部 + 跨 references 表的双重不一致，需单独检查。

### 引用样本 3 — references.md §6 第 5 条（Horstmann）与正文 [67] Rost 错位

**references.md 原文**：
> [67] Horstmann, J. G., Reutzel, M., Schütte, M. et al. Theory of high harmonic generation in spin-split antiferromagnets and altermagnets. arXiv:2505.08930 (2025). 【预印本】

**正文对应**：
- rationale.md L33 "Rost 等人... [67]"（错位：按 references [67] = Horstmann）
- rationale.md L63 "Rost 等人... [67]"（错位）
- rationale.md L77 "Rost 等人... [67]"（错位）
- content.md L21 "Rost 等人 2025 年 [67]"（错位）
- content.md L51 "Rost 等人 2025 年 [67]"（错位）

**差距**：
- 正文 5 处用 [67] 指 Rost，references [67] 是 Horstmann——Rost 工作（arXiv:2507.02673）在 references.md 中**完全没有独立条目**。
- 这是 R2 报告 #3 遗留问题，本轮核查仍未补。

### 改写方向（程序化建议）

1. **方案 A（推荐）**：references.md §6 整组前移 1 位 + 补 [67] Rost
   - Cochran [63]→[62]、Sørensen [64]→[63]、Fuchs [65]→[64]、McCarter [66]→[65]、Horstmann [67]→[66]
   - 新增 [67] = Rost et al., arXiv:2507.02673 (2025)
   - 同步更新 references.md L121, L123, L125, L127, L131, L133, L149, L153, L155, L161 全部编号映射
   - 正文 18+ 处不动（正文已用 [62]/[63]/[67] 对齐新表）

2. **方案 B（保守）**：正文 18+ 处后移 1 位 + references.md 新增 [68] Rost
   - 正文 [62]→[63]（Cochran）、[63]→[64]（Sørensen）、[67]→[68]（Rost）
   - 同时修 content.md L23 [65]/[66]→[66]/[67]（McCarter/Horstmann）
   - references.md 编号不动，新增 [68] Rost 条目

3. **统一 [24] Werner 年份**：所有"2024"改为"2026"（references.md L63, L123；content.md L23；保留 scheme.md L77 已正确为"2026"）

4. **修复 scheme.md L49 内部不一致**：将 "Wang et al., *Opt. Express* 30, 46417, 2022 [59]" 改为 [60]

5. **更新 references.md §8 自检段**：行号引用 "rationale.md:49" 应改为实际行号（L39, L83, L85）；"rationale.md:31/35/45" 同样需校准

================================================================
## 对抗结论

- **本轮发现**：10 个问题（critical: 3, high: 3, medium: 2, low: 2）
- **相比第 2 轮（references 专项 0.55）**：
  - R2 报告 4 条 critical（幽灵 [58]、§6 系统错位、§5 系统错位、Rost 孤儿）：本轮核查仅 §5 编号 [58] 幽灵已解决（正文已改 [59]），但 §6 系统错位、Rost 孤儿未解决（事实升级为更严重的 18+ 处系统性错位）。
  - 新发现 2 条 critical：content.md §2.3 [65][66] 反向错位 + [24] Werner 5 处年份不一致。
- **是否达到输出标准**：**否**。原因：
  - 3 个 critical 问题中至少 2 个涉及 references.md 与正文 18+ 处编号系统的不一致，必须在提交前修订；
  - 1 个 critical 涉及 Rost CrSb 实验的参考文献缺失；
  - NSFC 评审专家按 references.md 编号表逐条核对时，会在 rationale.md L39 第一处 "Cochran [62]" 即发现"按 references [62] 应是 Uzner"，几乎不可能漏掉。
- **优先级建议**：
  1. （必须）critical #1 / #2 / #3 一并处理（references §6 前移 + [24] 年份统一 + Rost 条目补登）；
  2. （必须）high #4 / #5 / #6 同步修订（references 自检段重写、[55][64] 孤儿条目处理）；
  3. （建议）medium #7 改自报计数；medium #8 补 CrSb 物性参数原始引用；
  4. （可选）low #9 改预印本占比说明；low #10 改空号位计数。
- **下一轮评审建议**：聚焦 (a) §6 系统错位 + Rost 补登 + content.md L23 [65][66] 修复；(b) [24] Werner 跨文档年份统一；(c) CrSb 物性参数原始引用补齐。

================================================================
## 评分

```
## 评分
创新性：N/A
可行性：N/A
严谨性：0.30
完整性：0.50
综合评分：0.40
```
