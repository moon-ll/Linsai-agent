# 参考文献专项检验报告（第 2 轮 · references 版本线）

- **项目类型**：面上项目（general），课题 ID `general-new-idea-20260822`
- **本轮聚焦**：references.md 专项检验——引文格式、引用相关性、缺失引用、数量与时效性；不做写作风格/创新性/可行性评估
- **评审日期**：2026-08-25（实测 references.md 5267 B / 61 行 / 30 条）
- **评审 profile**：critic（红队）
- **上一轮文件处理情况**：05_review/critic-round-2.md 原被"整体一致性版本线"占用（37383 B，聚焦三章节跨章逻辑），本轮开工前已整体归档为 `.archive-critic-round-2-consistency-line-20260825.md`，未发生覆盖丢失
- **编号一致性**：直接采信程序预检（24 个正文编号、30 条列表、无缺口、无幽灵编号、未引用 [11, 13, 14, 27, 29, 30]、数量达标），本轮不重复核对
- **预检膨胀告警**：预检结果中未出现膨胀告警标记，按指令不列"工作日志污染"问题

## 核验方法与数据来源

1. Crossref API 逐条反查 17 个正式发表 DOI（[1]–[17]、[24]），比对返回的标题/首作者/期刊/卷页与条目是否为同一篇论文
2. arXiv API（export.arxiv.org）批量核验 10 个 arXiv ID（[18]–[23]、[25]–[28]）
3. [29] DOI 含占位符 XXXX，无法反查；[11]/[30] 共享同一 DOI，一并核验
4. 正文关键词 grep（激子/Floquet/自旋群/综述/泵浦）用于缺失引用与相关性判断，未读全文

## 逐条核验结果表

| [N] | 核验渠道 | 结果 | 判定 |
|---|---|---|---|
| [1] Šmejkal PRX 12, 031042 (2022) | Crossref | 标题/首作者/卷页全符 | ✓ 相符 |
| [2] Krempaský Nature 626, 517 (2024) | Crossref | 全符 | ✓ 相符 |
| [3] Werner PRB 110, 235101 (2024) | Crossref | 论文存在，但首作者为 Werner **Philipp**（非 "Werner J"） | △ 首作者缩写不符 |
| [4] Ghimire Nat Phys 7, 138 (2011) | Crossref | DOI 解析到 Amselem 2010 "Reply to 'Experimental bound entanglement?'"（Nat Phys 6, 827） | ✗ DOI 指向他文 |
| [5] Yoshikawa PRB 92, 201401 (2015) | Crossref | DOI 解析到 Veldhorst "Spin-orbit coupling and operation of multivalley spin qubits"；且石墨烯 HHG 真实发表于 Nature 529, 262 (2016)，非 PRB 92, 201401 | ✗ DOI+卷页双错 |
| [6] Liu Nat Phys 13, 262 (2017) | Crossref | DOI 解析到 Stern "Photons taught new tricks"（Nat Phys 13, 110 观点文章）；真实论文页码为 728–736 | ✗ DOI+页码双错 |
| [7] Li Opt Express 28, 30486 (2020) | Crossref | DOI 10.1364/OE.401437 **404 Not Found** | ✗ 死链 |
| [8] Langer Nature 541, 488 (2017) | Crossref | DOI 解析到 Riek "Subcycle quantum electrodynamics"（Nature 541, 376） | ✗ DOI 指向他文 |
| [9] Vampa PRL 113, 073901 (2014) | Crossref | 全符 | ✓ 相符 |
| [10] Kim Science 375, 1294 (2022) | Crossref | DOI 10.1126/science.abg8109 **404 Not Found**；该卷页组合未检索到对应论文 | ✗ 死链+存疑 |
| [11] Ly JPCM (2026)（未引用） | Crossref | DOI 解析到 Ly O "High-harmonic spin and charge pumping in altermagnets" JPCM 38, 175803 (2026)——**与 [30] 为同一篇**，且 [11] 自身标题 "Scaling laws of magnetically driven HHG in spin-orbit coupled systems" 与该 DOI 不符 | ✗ 双编号重复+题文不符 |
| [12] Silva PRL 123, 207201 (2019) | Crossref | DOI 解析到 "Noncollinear Ordering of the Orbital Magnetic Moments in Magnetite"；"High-harmonic spectroscopy of topological phase transitions" 查无实据 | ✗ 条目存疑 |
| [13] Luu & Wörner Nat Rev Phys 2, 342 (2020)（未引用） | Crossref | DOI 解析到 Schäfer "Tools for quantum simulation with ultracold atoms in optical lattices"（NRP 2, 411） | ✗ DOI 指向他文 |
| [14] Kang PRB 104, L161302 (2021)（未引用） | Crossref | DOI 解析到 Luo "Stability of even-denominator fractional quantum Hall states…"；"Excitonic effects in monolayer MoS₂ HHG" 查无实据 | ✗ 条目存疑 |
| [15] Tancogne-Dejean PRX 10, 041008 (2020) | Crossref | DOI 解析到 Si "Unconventional Superconductivity…Iron-Selenium-Based Mott Insulator" | ✗ DOI 指向他文 |
| [16] Hancock PRL 124, 177401 (2020) | Crossref | DOI 解析到 Krainova "Polaron Photoconductivity…"；"Polarization-resolved HHG in monolayer MoS₂" 查无实据 | ✗ 条目存疑 |
| [17] Luu Nature 577, 659 (2020) | Crossref | DOI 10.1038/s41586-019-1904-8 **404 Not Found**（论文本身真实存在，DOI 错） | ✗ 死链 |
| [18] Suzuki arXiv:2510.27089 | arXiv | 标题/首作者/年份全符 | ✓ 相符 |
| [19] Long arXiv:2601.14526 | arXiv | 全符（标题含 "$g$-wave" LaTeX 残留） | ✓ 相符 |
| [20] Mizuno arXiv:2606.31573 | arXiv | 全符 | ✓ 相符 |
| [21] Sasabe arXiv:2603.09074 | arXiv | 全符 | ✓ 相符 |
| [22] Sun arXiv:2604.22751 | arXiv | 全符 | ✓ 相符 |
| [23] Zhang arXiv:2606.13395 | arXiv | 全符 | ✓ 相符 |
| [24] Liu Sci China Phys Mech 66, 247011 (2023) | Crossref | DOI 10.1007/s11433-023-2380-6 **404 Not Found** | ✗ 死链 |
| [25] Che arXiv:2605.25128 | arXiv | arXiv 真实标题为 "Harmonic Hierarchy of Altermagnetic Spin Splitting from Symmetry-Adapted Wavefunctions"，**非**条目所写 "Symmetry analysis and topological indicators" | ✗ 题文不符 |
| [26] Haag arXiv:2505.13415 | arXiv | 标题/首作者/年份全符（6 作者与 API 一致） | ✓ 相符（样板条目） |
| [27] Zhu arXiv:2608.02393（未引用） | arXiv | 标题/首作者全符；缺 DOI 字段 | ✓ 相符 |
| [28] Yu arXiv:2605.03026 | arXiv | 全符；缺 DOI 字段 | ✓ 相符 |
| [29] Li PRL 134, XXXX (2025)（未引用） | 无法核验 | DOI 含占位符 XXXX，无页码/文章号 | ✗ 占位符 |
| [30] Ly JPCM (2026)（未引用） | Crossref | 与 [11] 同 DOI 同论文（JPCM 38, 175803） | ✗ 双编号重复 |

核验总计：30 条中 3 条 Crossref 完全相符（[1][2][9]）、11 条解析到无关论文或题文不符（[4][5][6][8][11][12][13][14][15][16][25]）、4 条 404 死链（[7][10][17][24]）、1 条占位符（[29]）、1 条双编号重复（[30]，与 [11]）；10 条 arXiv 条目 ID 全部真实。**涉假/不可用条目共 16/30（53.3%）**。

## 问题清单

### [critical] citation_integrity — DOI 大面积指向无关论文，正式文献条目真实性崩塌
- 位置：references.md L11 [5]、L13 [6]、L19 [9] 之外几乎全线；重灾区 L9–L33（[4]–[16]）
- 问题：17 条正式 DOI 经 Crossref 反查仅 3 条相符。[5] 的 DOI 解析到自旋量子比特论文、[6] 到观点文章 "Photons taught new tricks"、[8] 到 "Subcycle quantum electrodynamics"、[15] 到铁基超导论文、[12][14][16] 的标题在对应卷页查无实据。这种"标题/作者取自真实 HHG 文献、DOI 却指向别处"的模式意味着任何评审人点开 DOI 都会看到完全无关的论文，属于逐条可证伪的硬伤。其中 [7][10][17][24] 四条为正文正在引用的死链。
- 建议：逐条重建，落盘前必须用 Crossref/出版社页复核"标题+首作者+期刊+卷+页+DOI"六件套。可用的修正方向（均为候选，落盘前须再验）：
  - [5] → Yoshikawa N, Tamaya T, Tanaka K. High-harmonic generation in graphene. Nature 529, 262–266 (2016). DOI 10.1038/nature16517
  - [6] → Liu H, et al. Nat Phys 13, **728–736** (2017). DOI 10.1038/nphys4291
  - [4] → Ghimire **G**（非 "Smejkal 式缩写错误"：当前拼写 Ghimire S 亦与真实首作者 Ghimire G 不符）, et al. Nat Phys 7, 138–143 (2011)，真实 DOI 从出版社页重取
  - [8] → Langer F, et al. Nature 541, 488–495 (2017)，真实 DOI 重取（nature21024 已被证伪）
  - [13] → Luu T T, Wörner H J. NRP 2, 342–354 (2020)，真实 DOI 从 Springer Nature 页重取
  - [15] → 可替换为 Tancogne-Dejean N, Mücke O D, Kärtner F X, Rubio A. Phys Rev Lett 118, 087403 (2017). DOI 10.1103/PhysRevLett.118.087403（候选）
  - [7][10][24] → 从 Optica/Science/SCPMA 出版社页重取真实 DOI；[10][24] 若整条无法溯源则整条替换为可验证的同主题文献（[10] 为正文引用，不可直接删除）
  - [12][14][16] → 标题查无实据，整条重造：检索确认真实存在的"拓扑相变 HHG 谱学""单层 MoS₂ 激子 HHG""偏振分辨 MoS₂ HHG"文献后落盘
- action：verify（逐条联网复核后重写）

### [critical] zombie_references — 6 条未引用条目中藏双编号重复与占位符 DOI
- 位置：L23 [11]、L27 [13]、L29 [14]、L55 [27]、L59 [29]、L61 [30]
- 问题：预检证实 [11, 13, 14, 27, 29, 30] 六条正文零引用（占列表 20%）。其中 [11] 与 [30] 是**同一篇论文（同 DOI 10.1088/1361-648x/ae6385，Ly O, JPCM 38, 175803 (2026)）被编成两个号**，且 [11] 所标标题与该 DOI 实际论文不符；[13][14] 本身就是上条 critical 中的存疑条目；[29] DOI 为占位符。六条全部是"负资产"。
- 建议：删除 [11][13][14][29][30] 五条（零引用 + 存疑/重复/占位，删除即同时消灭双编号、占位符、题文不符三类问题且不动正文角标）；[27]（Floquet 自旋群，arXiv 核验为真）保留并在 scheme.md 的 Floquet/自旋群表述处补挂角标（见缺失引用条目）。删除后全表重新连续编号，正文角标同步平移。
- action：remove + renumber（[27] 例外：add 到正文）

### [high] format_consistency — 条目要素与截断方式三重不统一
- 位置：全表；典型 L55 [27]、L57 [28]（缺 DOI 字段）vs L39–L53（arXiv 条目带 DOI: 10.48550/…）；L9 [4] 全作者后又缀 "et al."；L19 [9] 作者列至第八人 abruptly 截断；L59 [29] 无卷页
- 问题：(a) arXiv 条目 DOI 字段有无不一：[18]–[26] 有、[27][28] 无；(b) 作者列表三种风格混用——全列（[1][9]）、三/四人+et al.（多数）、全列+et al. 冗余（[4]）；(c) 正式发表条目 [11] 无卷页（实为 v38 p175803，可补全）、[29] 无卷页无文章号。同一列表内格式漂移会被形式审查直接扣印象分。
- 建议：统一为"前 3 位作者 + et al.（≤6 人全列）；正式文献必须有卷+页/文章号；arXiv 条目一律带 DOI: 10.48550/arXiv.XXXX.XXXXX"；按此规则全表过一遍（[4][9][11][27][28] 必改）。
- action：rewrite

### [high] citation_relevance — 3 条 2025–2026 文献与"交变磁体 HHG"主题仅边缘相关
- 位置：L37 [18]（trARPES 时间分辨光电子能谱综述）、L45 [22]（二维超导/交磁体的量子退相干噪声谱）、L47 [23]（CrSb Andreev 反射输运探测）
- 问题：三条研究对象分别为光电子能谱方法学、噪声谱学、输运探测，均非高次谐波产生本身。作为"探测手段旁证"引用勉强成立，但 [22] 的"Symmetry-resolved noise spectroscopy"与 HHG 自旋动力学的科学问题距离最远，若正文没有明确承接句（如"亦可经噪声谱学交叉验证"），属于凑时效性的弱相关引用。
- 建议：在正文为 [18][23] 各补一句方法学承接；[22] 二选一——补承接句或替换为一条已核实的交变磁体 HHG 理论/实验文献（替换时保持 2025–2026 年份，不损时效性）。
- action：verify + rewrite

### [high] validity_placeholder — [29] DOI 含 "XXXX" 占位符且无卷页
- 位置：L59 [29]
- 问题："DOI: 10.1103/PhysRevLett.134.XXXX" 不是可解析的 DOI，PRL 134 卷为 2025 年卷，条目无页码/文章号。正式申请书出现占位符 DOI 属于形式审查一票否决级瑕疵。
- 建议：该条正文零引用，直接删除（与 zombie_references 处置合并执行）；若 writer 坚持保留该文献（交磁自旋进散/自旋晶体管），须先在 PRL 134 (2025) 检索定位真实条目并补全卷页 DOI。
- action：remove（或 verify 后补全）

### [medium] citation_first_author — [3] 首作者缩写与公开记录不符
- 位置：L7 [3] "Werner J, Wang F, Linz P, et al."
- 问题：Crossref 记录该文（PRB 110, 235101）首作者为 Werner **Philipp**，条目写 "Werner J"；第三作者 "Linz P" 与记录中的 Linz **Philipp** 也呈同型错位，疑似作者首字母整体臆写。
- 建议：改为 Werner P, Wang F, Linz P, et al.（若后续作者首字母亦有出入，以出版社页为准逐个修正）。
- action：verify

### [medium] missing_citation — 两项正文论断缺乏可用的文献支撑
- 位置：依据预检（rationale 引用 23 个编号）+ 关键词 grep：rationale.md "激子" ×2、"综述" ×1；scheme.md "自旋群" ×1
- 问题：(a) **HHG 综述缺位**：列表中唯一综述 [13]（Luu & Wörner NRP）恰好是零引用+DOI 错误条目，正文"综述"表述实际无有效支撑；(b) **激子机制**：rationale 两处"激子"论述对应的 [14] 恰是零引用+查无实据条目，修复后须在正文挂角标，否则删论断；(c) **Floquet 自旋群**：scheme.md 有自旋群/Floquet 表述，而最对口的 [27] 未被引用。
- 建议：修复 [13] DOI 后在 rationale 综述句挂 [13]；[14] 替换为真实激子-HHG 文献后在"激子"两处挂角标；scheme.md 自旋群/Floquet 句挂 [27]。
- action：add（正文补挂角标，与条目修复联动）

### [medium] reference_freshness_balance — 时效性达标但缓冲薄
- 位置：全表年份分布
- 问题：2023–2026 年文献 16/30（53.3%），越过 50% 红线但仅 3.3 个百分点缓冲；若按上述建议删除 5–6 条僵尸条目，比例升至约 54%，仍属"贴线达标"。经典奠基文献（2011–2020）占近半属正常，但 2024–2026 交变磁体 HHG 方向只有 [3][25]（加边缘的 [18]–[23]），核心方向近年密度不足。
- 建议：修复/替换死链时优先选用 2024–2026 年交变磁体 HHG 或超快自旋动力学文献（如替换 [10][24] 时），把近 3 年占比抬到 60% 左右。
- action：research

### [low] format_style — 残留格式瑕疵
- 位置：L39 [19] 标题含 "$g$-wave" LaTeX 残留；L35 [17] 标题用 Title Case 与其余条目 Sentence case 不一致；L53 [26] "Leckron K" 等非常见拼写建议按 arXiv 原文复核
- 问题：LaTeX 美元符在 PDF 汇编时会裸露；大小写风格混排。
- 建议："$g$-wave"→"g-wave"；[17] 标题改 Sentence case；[26] 作者拼写对照 arXiv:2505.13415 原页面逐字复核。
- action：rewrite

## 锚点对比

1. **引用**（references.md L53）：
   "[26] Haag L, Weber M, Leckron K, Šmejkal L, Sinova J, Schneider H C. Optical signatures of bulk g-wave altermagnetism in MnTe. *arXiv* **2505.13415** (2025). DOI: 10.48550/arXiv.2505.13415."
2. **对比**（arXiv API 实测返回）：
   标题 "Optical signatures of bulk g-wave altermagnetism in MnTe"；首作者 Luca Haag；共 6 位作者；2025 年——五件套（标题/首作者/作者数/年份/ID）全符。
3. **差距**：无实质差距。[26] 是全表唯一"真实性核验+格式要素（arXiv 条目带 DOI、作者列出规整、年份完整）双达标"的样板。其余 arXiv 条目应向 [26] 看齐补 DOI 字段（[27][28]），所有正式发表条目则必须重走 [26] 级别的真实性核验流程后方可定稿。

锚点对比结论：达标

## 维度评分表

| 维度 | 权重说明 | 得分 | 问题数 |
|---|---|---|---|
| 严谨性 | 引文格式、作者信息完整性、条目真实性 | 0.38 | 5（#1 #3 #5 #6 #9） |
| 完整性 | 引用数量、时效性、缺失引用 | 0.72 | 4（#2 #4 #7 #8） |
| 创新性 | 本轮不评 | N/A | — |
| 可行性 | 本轮不评 | N/A | — |

评分依据：严谨性方面，30 条中 16 条（53.3%）存在 DOI 指向他文、死链、占位符、双编号或题文不符——超过半数条目不可信，按评分纪律落入虚构/失真条目区间（0.3–0.4），因条目标题多数确有真实原型（非凭空捏造）取区间上限 0.38；完整性方面，数量 30 条达标、近 3 年 53.3% 贴线达标、10 条 arXiv 条目 ID 全真支撑了主题骨架，但 6 条僵尸引用、两项论断缺支撑、3 条弱相关拉低完整性至 0.72。

## 对抗结论

- 本轮发现 9 个问题（critical:2, high:3, medium:3, low:1）
- 相比上一轮（整体一致性版本线，references 真实性按约定移交本轮）：本轮为 references 专轮首查，新增 9 个问题，其中 DOI 大面积失真为此前任何轮次未暴露的最重问题
- 是否达到输出标准：**否**。数量与 arXiv 骨架达标，但 16/30 条目涉假/不可用、正文引用中的 4 条死链（[7][10][17][24]）与 2 个 critical 未解决前，该参考文献列表不可用于任何提交版本
- 返工优先级：① 逐条重建正式发表条目（#1，先修正文在引的 [4]–[10][12][15]–[17][24]）→ ② 删除五条僵尸条目并重排编号（#2 #5）→ ③ 统一格式（#3 #9）→ ④ 正文补挂 [13][27] 及激子文献角标（#7）→ ⑤ 替换弱相关条目并增厚近三年密度（#4 #8）
- 下一轮建议：writer 重建后，critic 第 3 轮对全表 30（或重排后 25 左右）条做逐条 Crossref+arXiv 复验，并抽验正文角标平移是否随重编号同步更新

## 评分
创新性：N/A
可行性：N/A
严谨性：0.38
完整性：0.72
综合评分：0.55
