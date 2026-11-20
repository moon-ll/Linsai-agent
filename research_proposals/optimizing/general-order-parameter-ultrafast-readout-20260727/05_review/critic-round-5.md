对抗评审报告（第 5 轮 · 参考文献专项检验）

项目类型：general（面上项目）
审查日期：2026-08-21
审查范围：references.md（参考文献列表）+ rationale.md / content.md / scheme.md（正文 [N] 引用位置）
审查模式：参考文献专项（按用户指令：不做写作风格 / 创新性 / 可行性评估）

警告：05_review/critic-round-5.md 同名文件原属 2026-08-21 整体一致性审查产物（27747 bytes）。本次为避免覆盖上一轮报告，已先备份至 .archive-critic-round-5-overall-consistency-20260821.md，再以本份参考文献专项报告覆盖同名文件。

────────────────────────────────────────
1. 综合评分（按用户指定的两维度）

0.50 / 1.00（严谨性 0.40 + 完整性 0.60 两维度均值；评分依据见 §2）

| 维度       | 权重 | 得分 | 问题数 |
|------------|------|------|--------|
| 严谨性     | 0.50 | 0.40 | 6（含 critical 2） |
| 完整性     | 0.50 | 0.60 | 4 |
| 综合评分   | 1.00 | 0.50 | 10 |
| 创新性     | —    | N/A  | —     |
| 可行性     | —    | N/A  | —     |

评分依据摘要：本轮发现参考文献存在 2 项 critical 编号一致性错误（Cochran [62]/[63] 在 references.md 与正文之间编号错位；Cochran 同一论文在 references.md 内被同时列为 [62] 与 [63] 两个独立条目）+ 1 项 critical 虚构论文条目 [69] Weber（标题含虚构元素符号 "NdMu2Si₂"，与 arXiv:2408.05187 真实标题 "All optical excitation of spin polarization in d-wave altermagnets" 完全不符）+ scheme.md L27 中 Wang 2022 与 Zhang 2024 的 [N] 内联引用错位。完整性方面，参考文献总数 42 条（含一处重复计数），落在 general 项目范本区间 30—40 条略偏上但合理；时效性以 2023—2026 年文献占 83% 为优；唯 arXiv 预印本占核心论证比重 12/29 偏高的现象已在 references.md L163 自行标注。综合 0.50 反映 critical 编号 bug 占项目类型红线问题，单项即触发严档。

────────────────────────────────────────
2. 引文格式与编号一致性逐项核查

2.1 [N] 引用编号 → 参考文献列表 一一对应表

正文（rationale + content + scheme）实际出现的 [N] 共 39 个唯一编号：
[1] [2] [3] [5] [7] [9] [10] [11] [12] [13] [15] [16] [20] [22] [23] [24] [25] [26] [27] [28] [29] [30] [31] [35] [36] [39] [56] [57] [58a] [58b] [59] [60] [61] [62] [63] [65] [66] [67] [68]

其中按引用频次排序（≥2 次的高频条目，反映方法学锚点）：
[63] 16 次（按正文标记为 Sørensen）
[11] 16 次（Tyulnev）
[12] 12 次（Zhang）
[62] 10 次（按正文标记为 Cochran）
[68] 8 次（Rost）
[25] 6 次（Šmejkal）
[24] 6 次（Werner）
[16] 6 次（Murakami）
[59] 5 次（Yue）
[56] 4 次（Sankar）
[31] 4 次（Cheng）
[26] 4 次（Leeb）
[61] 3 次（Zhang Keldysh）
[58b] 3 次（Qiu）
[58a] 3 次（Leeb HHG）
[35] 3 次（Granados）
[60] 2 次（Wang）
[5] 2 次（Puviani）
[36] 2 次（Mandal）
[20] 2 次（Jensen）

正文 [N] → references.md 条目映射（按 references.md 行号）：
| 正文 [N] | 正文语义 | references.md 条目 | references.md 内的语义 | 映射一致性 |
|-----------|---------|--------------------|----------------------|----------|
| [62] | Cochran（唯一性框架） | L113 [62] | Cochran arXiv:2606.15279（唯一性） | ✓ |
| [63] | Sørensen（非唯一性） | L127 [64] | Sørensen arXiv:2605.14873（非唯一性） | ⚠ 错位（references.md 把 Sørensen 编为 [64] 而非 [63]） |

references.md 自身还含编号 [63]（L125），但其条目内容与 [62] 同一篇 Cochran 论文（L113），构成同一论文的双编号重复。

2.2 关键冲突点（critical bug）

【冲突 A】正文 [63] 恒指 Sørensen，references.md 把 Sørensen 编为 [64]
- 证据：rationale.md 行 39、45、51、53、63、83、85（共 7 次 [63] = Sørensen）；content.md 行 27、43、55（共 3 次 [63] = Sørensen）；scheme.md 行 41、73、81、83、95（共 5 次 [63] = Sørensen）—— 累计 15 次 [63] = Sørensen，1 次出现在 content.md L27 之外的 scheme.md L73。
- 反证：references.md 行 127 把 Sørensen 编为 [64]，并在 L121、L153、L157、L159、L165 的元叙述中把 Cochran 编为 [63]、Sørensen 编为 [64]。
- 影响：references.md [64] Sørensen 条目与正文 [63] Sørensen 指代同一论文，但编号不一致，审稿人若按正文 [63] 反查参考文献表将找不到 Sørensen，按 references.md [64] 又找不到正文对应位置。

【冲突 B】Cochran 同一论文 arXiv:2606.15279 在 references.md 内被同时编为 [62]（L113）与 [63]（L125）
- 证据：references.md L113 与 L125 的标题、作者、arXiv ID、注释文字完全一致，是同一篇论文被复制为两个 [N] 条目。
- 影响：references.md 自称"41 条（含 [58a]、[58b] 双编号）/ 正文 [N] 编号条目 41 个"——但实际同一论文占两个 [N] 编号，正文实际引用 39 个唯一 [N]，编号与条目数差 2 而非差 1，逻辑不自洽。

2.3 scheme.md L27 内联引用错位（critical bug）
- scheme.md L27 出现三处引文 + [N] 编号交叉错位：
  - "(Wang et al., *Opt. Express* 30, 46417, 2022 [59])" — Wang 2022 在 references.md [60]，不是 [59]（[59] = Yue & Gaarde 2020）
  - "(Zhang et al., *Phys. Rev. Lett.* 133, 186903, 2024 [60])" — Zhang 2024 Keldysh 在 references.md [61]，不是 [60]（[60] = Wang 2022）
  - "(Uzner & Neufeld, arXiv:2604.23506, 2026 [61])" — Uzner & Neufeld 完全不在 references.md 任何 [N] 条目中（搜遍 [1]–[69] 均无），是正文幽灵编号；同时 [61] 实际是 Zhang 2024 Keldysh。
- 影响：scheme.md L27 整段 SBE 适用条件的方法学三角论证的引文支撑链全部错位；其中 Uzner & Neufeld 更是凭空出现的论文，未在任何参考文献条目中存在。

2.4 [69] Weber 条目疑似虚构（critical bug）
- references.md L137：[69] Weber, F. et al. *Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics*. *Phys. Rev. X* **16**, 021051 (2026). DOI: 10.1103/PhysRevX.16.021051; arXiv:2408.05187 (2024).
- 反查 arXiv:2408.05187 实为 Weber, M. et al. **"All optical excitation of spin polarization in d-wave altermagnets"**（2024-08-09 v1，最新 v3 修订于 2026-06-09），实验材料为 **RuO₂** 薄膜，时间分辨 MOKE 实验；第一作者是 Marius Weber 不是 "F. Weber"。
- 三个致命不符：① 标题 "Spin eigenmodes of NdMu2Si₂" 含虚构元素符号 "Mu"（Mu 在元素周期表不存在）；② 实际论文研究对象是 RuO₂ 不是 Nd 系化合物；③ 标题关键词 "spin eigenmodes" 与原论文 "all-optical excitation" 主题完全不同。
- 进一步：DOI 10.1103/PhysRevX.16.021051 在 2026 年 8 月时点能否定位到 Weber altermagnet 工作（即便存在正式发表），与 arXiv:2408.05187 的预印本内容是否对应同一组实验，需要正式发表版核对。仅凭 arXiv 预印本核实，无法确认该 Phys. Rev. X 2026 条目是真实存在的正式发表版，还是被改写的占位条目。
- 影响：references.md [69] 是 references.md 自称 "正文无 [N] 引用，以附录形式收录于 §6 末尾" 的纯文献基础条目，但条目本身真实性存疑；如果正文（rationale.md L31）以纯文本形式再次引用 "Weber et al., arXiv:2408.05187, 2024；2026 年正式发表"，正文与参考文献表给出的发表信息（标题、作者首字母）已经不一致。

2.5 编号统计自洽性核查
- 正文唯一引用 [N] 数：39 个
- references.md 唯一填入条目的 [N] 数：42 个（含 [69] Weber）
- 但 references.md [62] 与 [63] 为同一论文双编号，故独立论文数实际为 41 篇
- references.md 自称"参考文献总数 41 条"——以独立论文计为 41，以 [N] 编号计为 42，正文引用 39。差异源于 [62]/[63] 双编号与 [69] Weber 无引用条目并存。

────────────────────────────────────────
3. 引用相关性、时效性、缺失引用

3.1 引用相关性（每条 vs 申请书科学问题）
正文 39 个 [N] 与申请书核心主线（altermagnet HHG 序参量辨识 + 可辨识性分析）的相关性：
- 高度相关（核心论证基础）：[11][12][24][25][26][62][63][68][58a][58b][65][66][67] 共 13 条
- 中度相关（方法学/对照/可行性支撑）：[9][10][13][15][16][20][22][35][36][39][56][57][59][60][61] 共 15 条
- 背景类（仅作背景使用，正文 §1 自述"超导体系面临的替代解释……不共享同一可辨识性框架"）：[1][2][3][5][7] 共 5 条
- 候选信号机制补充：[23][27][28][29][30][31] 共 6 条
- 综述：[39]

引用相关性总体上：所有 39 个正文引用均与 altermagnet HHG 序参量辨识主轴可建立明确语义关联，无纯装饰性 / 无关引用。背景类 5 条已由 references.md §1 自行声明"非核心论证基础"，审稿人若审视可接受。无关引用数：0。

3.2 时效性核查（按 references.md 自身声明与实际数）
- 2023—2026 年文献数（[N] 编号条目）：按 references.md L161 自称 34 条 / 41 条 = 83%。
  - 实际清点：正式发表条目中 2023 年 [39]、2024 年 [5][7][20][22][59 标 2020 但引用频次高的方法学][60 标 2022][61 标 2024][62 标 2025][63 标 2025][64 标 2025]、2025 年 [10][11][12][15? 标 2022][16]、2026 年 [24][69 标 2026]。arXiv 预印本条目多数为 2025—2026 年（[27]–[31]、[35][36]、[55]–[57]、[58a][58b]、[63]–[68]）。
  - 单独看：≥2024 年的条目占主体（约 70%），含全部 2025—2026 年里程碑；2017—2022 年条目仅 [2] Matsunaga 2017、[23] Takayoshi 2019、[3] Alcalá 2022、[15] Hansen 2022、[59] Yue 2020、[60] Wang 2022、[69] Weber 2024(arXiv)/2026(PRX) 等 6—7 条，均有 references.md L161 自身声明的"方法学经典锚点"用途。
- 总体时效性：优（2023—2026 占主体）。
- 预印本占比：12/29 ≈ 41%（正式发表 29 条 / 预印本 12 条 / [69] Weber 待定）。预印本条目集中在 §6 方法学锚点与 2025—2026 实验里程碑——这是 altermagnet HHG 是新兴领域（2022 年 Šmejkal 理论、2024—2025 年实验爆发）的客观事实。references.md L163 已自行标注"正式发表 29 条、预印本 12 条"，并声明正文均以 [N] 编号引用。

3.3 缺失引用 / 论断缺文献支撑
- rationale.md L11 "截至 2026 年 8 月，按 Web of Science 与 arXiv 检索（关键词 'order parameter' 与 'high harmonic generation' 组合，时间范围 2015—2026），在亚周期、体相、可归因三个维度同时具备的非平衡序参量测量手段，尚未见实验报道"——该论断仅给出检索式与时间范围但未列出任何引用，参考文献表也未对应。medium 风险：审稿人会质疑检索式覆盖度。
- rationale.md L19 "Altermagnet 中的磁场—序参量耦合并非简单的'翻转'关系，其自旋 flop 场强和取向依赖仍属活跃的研究课题 [58a]"——[58a] Leeb 2025 是 altermagnet HHG 理论，但自旋 flop 场强与取向依赖是磁学一般问题；正文更直接的需求是 altermagnet 自旋 flop 的实验测量或综述，例如 Šmejkal 2022 [25] 或具体材料的磁晶各向异性数据。medium 风险：单引 [58a] 一篇不足以覆盖"自旋 flop 场强和取向依赖"这一一般性论断。
- scheme.md L19 "样品匹配阈值为 CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）"——CrSb 带隙数值未给文献引用。references.md [25] Šmejkal 2022 与正文 [68] Rost 2025 是 CrSb 体系相关条目，但均未明确给出 CrSb 带隙数值。medium 风险：审稿人会要求引用 CrSb 带隙的实验/计算原始来源。
- scheme.md L47 "CrSb 的 d 波自旋分裂能量在数百毫电子伏特量级（典型值 100—500 meV）"——同一未给文献；[25] Šmejkal 2022 PRX 与 [24] Werner 2026 PRB 是 altermagnet 理论，但 CrSb 特定自旋分裂幅值需引用 CrSb 专属 DFT 或实验测量。medium 风险。

3.4 Biegert 提及的处理
- references.md L23 与 L167 各自声明"Biegert 2024 YBCO HHG 仅有机构新闻稿，不纳入本表"——正文（rationale.md / content.md / scheme.md）均无 Biegert 提及。该声明属于"已知但排除"的元叙述，对正文论证无影响，仅作为评审可追溯的核验记录保留。

────────────────────────────────────────
4. 锚点对比（聚焦 references.md）

引用：references.md L137 "[69] Weber, F. et al. *Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics*. *Phys. Rev. X* **16**, 021051 (2026). DOI: 10.1103/PhysRevX.16.021051; arXiv:2408.05187 (2024)."

对比：arXiv:2408.05187 真实论文标题为 "All optical excitation of spin polarization in d-wave altermagnets"（Weber, M. et al. 2024-08-09 v1，2026-06-09 v3 修订），实验材料为 RuO₂ 薄膜，第一作者为 Marius Weber。

差距：① 标题主题不同（spin eigenmodes of Nd-compound vs all-optical excitation in RuO₂）；② 元素符号 "NdMu2Si₂" 含虚构元素 Mu；③ 第一作者首字母 F. vs 实际 M.；④ DOI 10.1103/PhysRevX.16.021051 与 arXiv:2408.05187 v3 修订日期 2026-06-09 时间窗接近，理论上可对应正式发表，但标题内容与预印本完全不符。结论：[69] 条目须整体重写。

锚点对比结论：差距明显。references.md [69] 条目需重新核实 Weber 2026 正式发表版的真实标题、第一作者、卷期与 DOI，并与 arXiv:2408.05187 v3 修订内容对应；当前文本与公开 arXiv 记录在标题、第一作者、研究对象三方面不一致。

────────────────────────────────────────
5. 问题清单（按严重度 + 编号 + 位置 + 详见 + action）

### [critical] number_mismatch — 正文 [63] = Sørensen，但 references.md 把 Sørensen 编为 [64]
- 位置：references.md L127（条目 [64]）+ rationale.md L39, L45, L51, L53, L63, L83, L85 + content.md L27, L43, L55 + scheme.md L41, L73, L81, L83, L95
- 问题：正文累计 15 次 [63] = Sørensen（rationale 7 + content 3 + scheme 5），但 references.md 把 Sørensen 放在 [64]。审稿人按 [63] 反查参考文献表将找不到 Sørensen。
- 建议：将 references.md [64] Sørensen 改为 [63]，并删除原 [63] 位置上的重复 Cochran 条目（L125）；同时更新 references.md L101 / L121 / L153 / L157 / L159 / L165 所有元叙述中"§6 [64] Sørensen"为"§6 [63] Sørensen"；正文 [63] Sørensen 引用保留不动。
- action：rewrite（references.md 单文件批改）

### [critical] duplicate_entry — references.md 内同一论文（Cochran arXiv:2606.15279）被同时编为 [62] 与 [63]
- 位置：references.md L113（[62]）与 L125（[63]）
- 问题：两行条目在标题、作者、arXiv ID、注释段落上完全一致，是同一篇论文被复制为两个 [N] 编号。删除其中一行才能恢复"41 条独立论文"的声明。
- 建议：保留 L113 [62] Cochran（与正文 [62] 引用一致），删除 L125 [63] Cochran 重复条目；保留 L127 [64] Sørensen 改为 [63]（配合上一条 critical 修复）。
- action：rewrite（references.md 删除 + 改号）

### [critical] fabricated_citation — [69] Weber 条目标题与作者署名与 arXiv:2408.05187 真实内容不符
- 位置：references.md L137
- 问题：当前标题 "Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics" 包含虚构元素符号 "NdMu2Si₂"；arXiv:2408.05187 真实论文为 "All optical excitation of spin polarization in d-wave altermagnets"，材料为 RuO₂，第一作者 Marius Weber。DOI 10.1103/PhysRevX.16.021051 与 PRX 2026 卷期能否对应此论文待正式发表版核实。
- 建议：将 [69] Weber 替换为："[69] Weber, M. et al. All-optical excitation of spin polarization in d-wave altermagnets. *Phys. Rev. X* **16**, 021051 (2026). DOI: 10.1103/PhysRevX.16.021051; arXiv:2408.05187 (2024, v3 revised 2026-06-09)." 并在注释中说明"v3 修订日期与 PRX 2026 发表日期一致，正式发表版以 PRX 为准"；rationale.md L31 正文纯文本引用的"F. Weber"需同步改为"M. Weber"；正文"Spin eigenmodes of NdMu2Si₂ and last touch of altermagnetic kinetics"如有引用需整段重写。
- action：verify（先确认 PRX 16, 021051 (2026) 真实存在与标题相符）+ rewrite

### [critical] inline_citation_mismatch — scheme.md L27 内三处"作者 + [N]"交叉错位
- 位置：scheme.md L27
- 问题：① "(Wang et al., *Opt. Express* 30, 46417, 2022 [59])" 应为 [60]；② "(Zhang et al., *Phys. Rev. Lett.* 133, 186903, 2024 [60])" 应为 [61]；③ "(Uzner & Neufeld, arXiv:2604.23506, 2026 [61])" 中的 Uzner & Neufeld 在 references.md 中无对应 [N] 条目，是正文幽灵编号，且 [61] 实际是 Zhang 2024 Keldysh，不是 Uzner & Neufeld。
- 建议：将 scheme.md L27 三处替换为："Wang et al., *Opt. Express* **30**, 46417 (2022) [60]；Zhang et al., *Phys. Rev. Lett.* **133**, 186903 (2024) [61]；Uzner & Neufeld, arXiv:2604.23506 (2026) [待补 — 见下]"。其中 Uzner & Neufeld arXiv:2604.23506 不在 references.md 中，建议二选一：① 在 references.md §5 实验方法组补加 [61a] Uzner & Neufeld 条目（将原 [61] Zhang Keldysh 顺延为 [61a]，后续编号顺延）；② 或在 scheme.md L27 删除 Uzner & Neufeld 句子（"在 CrSb 层间效应修正方面……"），仅保留 Wang 与 Zhang 的 SBE 适用条件方法学三角论证。推荐方案②，因为 layer-coupling 论证对 R1/R2/R3 主线非核心，删除对论证链无实质影响。
- action：rewrite（scheme.md L27 修订 + 视情况补 references.md 条目）

### [high] metadata_inconsistency — references.md 元叙述内部不自洽
- 位置：references.md L101, L121, L153, L157, L159, L165
- 问题：L101 称 "Cochran 2025 [62]" 与 "§6 [64] Sørensen"；L121 称 "[63] Cochran" 与 "[64] Sørensen"；L153 称 "§5 自 [35] 起至 [36]、[59]、[60]、[61]、[62]"——与 L101 一致——但 L157 称 "§6 唯一性/非唯一性分析与里程碑 6 条（[63]–[68]）" 且把 Cochran 列入 §6 而 Sørensen 在 [64]；L159 称 "[63] Sørensen 在 rationale.md 行 39 与行 45 引用"——把 Sørensen 编为 [63]；L165 称 "§6 组共 6 条编号文献（[63]–[68]），为方法学锚点（[63] Cochran、[64] Sørensen）"——又把 Cochran 编为 [63]。同一份 references.md 内 L121、L157、L165 与 L101、L159 在 Cochran / Sørensen 的 [N] 归属上完全相反。
- 建议：在 critical 编号修复后（删除重复 [63] Cochran、把 Sørensen 从 [64] 移到 [63]），把所有元叙述统一为 "§6 方法学锚点 [63] Cochran 唯一性 / [64] Sørensen 非唯一性" 或 "§6 方法学锚点 [62] Cochran 唯一性 / [63] Sørensen 非唯一性"（选哪一种取决于是否同意把 Cochran 移到 §6 与 Sørensen 并列）。
- action：rewrite（references.md 元叙述统一）

### [medium] unanchored_assertion — 多处核心数据未引用文献支撑
- 位置：rationale.md L11、L19；scheme.md L19、L47
- 问题：① rationale L11 "在亚周期、体相、可归因三个维度同时具备的非平衡序参量测量手段，尚未见实验报道" 仅给出检索式但未引用任何文献；② rationale L19 "altermagnet 自旋 flop 场强和取向依赖" 仅引 [58a] Leeb 2025（HHG 理论），与磁晶各向异性一般论断不直接对应；③ scheme L19 "CrSb 带隙 0.13 eV（间接）与 0.6 eV（直接）" 未给文献；④ scheme L47 "CrSb 的 d 波自旋分裂能量在数百毫电子伏特量级（典型值 100—500 meV）" 未给文献。
- 建议：① rationale L11 增列 [58a] Leeb 2025、[62] Cochran 2025、[63] Sørensen 2025 三条作为"既有方法学的局限性"代表文献；② rationale L19 增列 Šmejkal 2022 [25] 或 altermagnet 综述支撑自旋 flop 论断；③ scheme L19 与 L47 增列 CrSb DFT/实验带隙与自旋分裂的原始来源（建议 [25] Šmejkal 2022 PRX 或具体 CrSb DFT 计算文献）。
- action：research（补充检索）+ add（references.md + 正文同时补）

### [medium] format_inconsistency — references.md 元叙述与正文引用位置行号不匹配
- 位置：references.md L159 "具体引用位置：[65] Fuchs 在 rationale.md 行 31 引用"
- 问题：rationale.md L31 实际为 Fuchs 提及的 arXiv 文本引用（"Fuchs et al., arXiv:2503.04431, 2025"），并未使用 [65] 编号；[65] 在正文仅在 content.md L55 出现一次。L159 的行号映射基于 [65] = 正文 [65] 行号，但实际正文 [65] 引用位置在 content.md L55 而非 rationale.md。
- 建议：核校 references.md L159 的全部行号映射，特别是 [65] Fuchs、[66] McCarter、[67] Horstmann 三条只出现在 rationale.md L35 与 content.md L55 的文本引用（同时使用 arXiv 文本与 [N] 编号），不能简单归为"rationale.md 行 XX 引用"。
- action：verify（references.md 元叙述核对正文实际行号）

### [low] preprint_ratio — 12/29 预印本占比偏高
- 位置：references.md §3、§4、§5、§6 共 12 条预印本（[9][13][27][28][29][30][31][35][36][55][56][57][58a][58b][62][63][64][65][66][67][68] 共 21 条预印本中，其中正文直接引用 12 条纯预印本）
- 问题：预印本占比偏高（41%），全部核心方法学锚点（[62][63][65][66][67][68]）均为预印本，审稿人会要求正式发表后再申报或至少在 references.md 中明确标注"以下方法学锚点截至 2026-08-21 仅有预印本，正式发表状态待核验"。
- 建议：references.md 已在 §5、§6 组首叙述中标注【预印本】，但 [62] Cochran、[63] Sørensen 等核心方法学锚点若在本项目申请窗口（NSFC 2027 申报）前完成正式发表，须替换 DOI 与卷期；若未发表，须在 rationale.md §2 中增加"以下方法学锚点仅有预印本支撑，审稿人须独立判断其结论强度"的限定语。
- action：verify（追踪 2026 Q4 与 2027 Q1 的 PRX/PRL/Phys. Rev. B 发表动态）

### [low] formatting_drift — [58a]/[58b] 字母编号与纯数字编号混用
- 位置：references.md L93, L95；正文 rationale L19, L29, L35, L77；content L23
- 问题：references.md 与正文均使用 [58a] [58b] 字母编号，与其他条目的纯数字 [N] 不统一；且 [58b] 条目的注释段落里又引用 "Qiu et al. arXiv:2508.16166" 这一独立预印本（未给新 [N] 编号），形成"条目内嵌套 arXiv 文本引用"的混合格式。
- 建议：考虑在 references.md 重排时把 [58a] 改为 [58]，[58b] 改为 [59]，并把 arXiv:2508.16166 的 Qiu 群论工作作为新独立条目 [59a] 或合并进 [58b] 条目的作者列表（若为同一团队），避免字母编号。
- action：rewrite（references.md 重排 + 顺延编号）

────────────────────────────────────────
6. 对抗结论

- 本轮发现 10 个问题（critical: 3, high: 1, medium: 3, low: 3），其中 critical 3 项全部聚焦 references.md 与正文 [N] 编号的内部一致性，单独任一项即足以触发评审人对申请书严谨性的严重质疑。
- 与上一轮对比：上一轮（2026-08-21 整体一致性审查）评 0.65，未聚焦参考文献；本轮参考文献专项评 0.50，反映参考文献专项是该项目当前最大的方法学风险点。上一轮未触及的 [62]/[63]/[64] 编号错位与 [69] Weber 标题虚构问题在本轮首次被系统发现。
- 是否达到输出标准：否。critical 3 项中任意一项未修复即不达 general 项目阈值（min_overall 0.80，本轮 0.50）。修复路径明确且工作量可控：① 删除 references.md L125 重复 [63] Cochran 条目；② 把 references.md [64] Sørensen 改为 [63]，更新正文 15 处 [63] 引用保持不变；③ scheme.md L27 三处内联引用 [59]/[60]/[61] 重排（[59]→[60]、[60]→[61]、删除 Uzner & Neufeld 句或新增 [N] 条目）；④ 重写 [69] Weber 条目标题、第一作者、研究对象；⑤ 统一 references.md L101/L121/L153/L157/L159/L165 元叙述中 Cochran/Sørensen 的 [N] 归属。
- 返工优先级 P0：critical 3 项。
- 下一轮评审建议聚焦：参考文献与正文交叉一致性修复完成后的复核（应聚焦 [N] 编号一对一对应、scheme.md L27 重排、references.md 元叙述统一），以及正文 §1 / §5 / §7 中"截至 2026-08-21 仅有预印本"的限定语补强。

────────────────────────────────────────
7. 评分块

## 评分
创新性：N/A
可行性：N/A
严谨性：0.40
完整性：0.60
综合评分：0.50
