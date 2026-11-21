# R3 引用审校 — general-quantum-geometry-inversion-20260726

审校日期：2026-10-17 ｜ 审校人：R3 引用审校评审员（期刊文献编辑）
对象：`research_proposals/optimizing/general-quantum-geometry-inversion-20260726/04_proposal/sections/`（rationale.md / content.md / scheme.md / references.md，55 条）
特别任务：检查 2026-10-11 程序化重排（[48]→[56] + 删 [41]）的巩固性 + 全表审校。

## 编号对账

方法说明：终端执行环境故障，对账改为"Grep 提取 + 全量人工比对"（脚本 /tmp/r3_citation_audit.py 已备）。条目行按"行首 [n] 后非 -/–"识别；正文引用含 [n,m] 并引（如 [8,22]、[26,20]），无 [a-b] 区间式。

| 检查项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无 TODO/待补/空条目；9 条 † 预印本著录完整 |
| 死条目 | 0 | 55/55 条全部被正文引用——表头"全部 55 条均被正文引用，利用率 100%"声明经全量比对属实（含 [41] 空号外的全部编号） |
| 超界 | 0 | 正文最大引用号 [56] = 条目最大号；[41] 未被任何正文引用（与表头"预留为编号衔接"声明一致，不构成断链） |
| 一号两用 | 0 | 编号集合 {1–40, 42–56} 唯一；无重复著录（[13] Gothelf PRA 113,063107 与 [43] Gothelf PRA 111,063105 经核实为两篇不同论文，见联网记录） |
| 断链 | 0 | 正文所有引用编号均有对应条目 |

**重排巩固性专项检查（上轮 [48]→[56] + 删 [41]）**：
1. **编号-内容一致性：已巩固 ✓**。正文 [48] 唯一引用点 rationale L9（"Wang 等 2023 年在偶数层 MnBi₂Te₄ 中观测到量子度规诱导的非线性输运[48]"）指向现 [48] Wang Nature 621,487 条目，内容匹配；正文 [56] 唯一引用点 content L31（de-la-Peña arXiv:2512.03987 纠缠随功率振荡[56]）指向现 [56] 条目，内容匹配。编号层面重排无残留错位。
2. **[41] 空号处理：合规 ✓**。无条目、无正文引用，表头声明与实际状态一致。
3. **物理顺序：未完全巩固 ⚠**。references.md 条目行物理顺序为 …[38](L81)、**[48](L83)**、[39](L85)、[40](L87)、[42](L90)…[47](L100)、**[56](L102)**、[49](L104)…[55](L116)——两处乱序：[48] 插于 [38]/[39] 之间、[56] 插于 [47]/[49] 之间。上轮程序化重排更新了编号标签与正文引用，但未同步移动条目行位置（或未重排到底）。不影响编号对账正确性，属规范性缺陷，见 R3-03。

## 联网核实记录（URL）

策略：被引最多（[8] Rasputnyi，正文 10 处）+ 关键判据锚（[12] e^{-2r} 截止方差、[11] TiSe₂ CDW 基准、[4] 量子度规实测）+ 重排涉及条目（[48]/[56]）+ 2026 新条目（[13] Gothelf、[2] Yang）+ 相邻卷期疑点（[52] 年份-卷号不匹配、[49] 与他文同页冲突排查）。共 11 条。

1. **[8] Rasputnyi Nat. Phys. 20,1960–1965 (2024)（被引最多）✓**
   arXiv:2403.15337 Related DOI 字段给出 10.1038/s41567-024-02659-x，与条目一致；摘要确认 0–2×10¹³ photons/pulse、±1 V/Å。
   https://arxiv.org/abs/2403.15337
2. **[11] Tyulnev Commun. Mater. 6,152 (2025) ✓✓（DOI 直达全文）**
   DOI 10.1038/s43246-025-00873-5 打开全文：标题/作者（Tyulnev, I., Zhang, L., Vamos, L. et al.）/卷期页与条目逐字段一致；正文引用的关键声称逐项核实——"Tc=197.3±3.5 K"原文逐字出现；"以 H3/H5/H7 偏振扫描峰强比量化各向异性、未报告旋转角量纲突变区间"的自我限定声明属实（原文通篇以峰强比/不对称度量化，无旋转角突变报告）；"含速度规范密度矩阵方程的平均场紧束缚模型"与原文 Methods（velocity gauge equation of motion in the Bloch basis）一致。
   https://doi.org/10.1038/s43246-025-00873-5
3. **[12] Khurelbaatar arXiv:2605.21925 ✓（公式细节待复核）**
   arXiv 页面命中：Tsendsuren Khurelbaatar（Griffith University）"Nonclassical Cutoff Fluctuations in Squeezed-Light-Driven High-Harmonic Generation"，主题（squeezed light 驱动 HHG 截止涨落非经典指纹）与正文判据用途吻合。⚠ 正文多处引用的封闭形式 ΔH²(r)/ΔH²_SQL=e^{-2r} 与 r_opt≈1.6 未在摘要层面复现（见 R3-05）。
   https://arxiv.org/html/2605.21925v1
4. **[4] Sala Nat. Mater. (2026) ✓**
   Google Scholar/ICMAB 官网双源确认："Probing the quantum metric of 3D topological insulators, G Sala, E Longo, MT Mercaldo, S Gariglio, M Cuoco, R Mantovan, C Ortix, AD Caviglia, Nature Materials"——条目 8 位作者全列且顺序一致；Sb₂Te₃ 拓扑表面态量子度规、非线性磁阻（time-reversal-odd、与散射时间无关）与正文声称方向一致。⚠ 正文"栅压可调"表述未获原文支持（见 R3-02）。
   https://arxiv.org/html/2509.17135v1 ｜ https://icmab.es/news?start=950
5. **[48] Wang Nature 621,487–492 (2023)（重排条目）✓**
   USTC 蔡宏兵教师主页逐字命中完整作者列表（Wang Naizhou, Kaplan Daniel, Zhang Zhaowei, Holder Tobias, … Yan Binghai & Gao Weibo, Nature 2023）；NTU 报道确认 MnBi₂Te₄、2023 年 6 月 Nature——正文"偶数层 MnBi₂Te₄ 量子度规非线性输运"声称匹配。
   https://faculty.ustc.edu.cn/Caihongbing/en/zhym/195226/list/index.htm
6. **[49] Gao Science 381,181–186 (2023) ✓✓（同页冲突排查后确认）**
   曾疑 Science 381,181–186 被他文占据，核实排除：Science 官网确认 DOI 10.1126/science.adf1506 为 Gao Anyuan, Liu Yu-Fei, … Qiu Jian-Xiang 等"Quantum metric nonlinear Hall effect in a topological antiferromagnetic heterostructure"（Scilit/PubMed 佐证）；摘要确认 even-layered MnBi₂Te₄/黑磷异质结、AFM 自旋反转符号翻转、与散射时间无关标度——正文 rationale §1.0 声称逐点匹配；381,181–186 卷期页由他文（Science 383, ado6049, 2025）参考文献列表中的引用格式佐证。
   https://www.science.org/doi/full/10.1126/science.adf1506 ｜ https://pubmed-d.ncbi.m.nih.gov/37319246/
7. **[56] de-la-Peña arXiv:2512.03987（重排条目）✓✓**
   arXiv 摘要页命中：作者 Sebastián de-la-Peña, Heiko Appel, Angel Rubio, Ofer Neufeld（与条目 4 人全列一致）；摘要确认"HHG entanglement oscillates with the driving laser power and exhibits multiple local maxima"——正文 content L31 声称（纠缠参数 R 随激光功率振荡、多功率位置局域极大值）与原文吻合。⚠ 原文为"阈值上谐波之间"与"阈值上-下谐波之间"两类情形，正文仅述"低于阈值谐波间"，归纳不完整（见 R3-04）。
   https://arxiv.org/abs/2512.03987
8. **[13] Gothelf PRA 113,063107 (2026)（2026 新条目+与 [43] 相近性排查）✓✓**
   ORCID 记录逐字命中："Limitations of an approximative phase-space description in strong-field quantum optics, Physical Review A 2026-06-09, DOI: 10.1103/cxff-kky6, Rasmus Vesterager Gothelf; Lars Bojer Madsen; Christian Saugbjerg Lange"——条目 DOI 短码与作者顺序均一致；他文引用格式佐证 PRA 113, 063107 (2026)。内容（近似正 P 表示把驱动场误作非相干经典混合、无法产生 sub-Poisson 统计与压缩）与正文"结构性失真"声称一致。与 [43]（Gothelf PRA 111,063105, 2025，晶体量子光 HHG）确认为两篇不同论文，非重复著录。
   https://orcid.org/0009-0008-7046-937X ｜ https://arxiv.org/html/2602.04370v1
9. **[21] Du PRB 113,245147 (2026)（顺带核实）✓**
   arXiv:2605.01388 "Tracking doublon-holon dynamics in high-harmonic generation from Mott insulators"命中；摘要确认"filling-dependent crossover—from Bloch-like intraband response at low filling"（带内→混合→带间跨越），与正文 [21] 用途（doublon 布居随填充度跨越）一致。
   https://arxiv.org/html/2605.01388
10. **[52] Kang Nat. Phys. 21,110–117（卷期年疑点）→ 确认年份著录错误 ✗**
    exaly 出版列表与 Google Scholar（作者 Yuting Qian 页）双源逐字确认："Measurements of the quantum geometric tensor in solids, Nature Physics, **2025**, 21, 110-117"（Nat. Phys. 21(1), 110-117, 2025）；arXiv:2412.17809（2024-12 预印本）→ 2025-01 刊出。条目误写"Nat. Phys., **2024**, 21: 110-117"——卷 21 对应 2025 年（2024 年为卷 20），作者 Kang, M., Kim, S., Qian, Y. et al. 与 CoSn/kagome 金属 QGT 重建内容本身无误。详见 R3-01。
    https://exaly.com/author-pdf/952764/min-gu-kang-publications-by-citations.pdf ｜ https://scholar.google.com/citations?user=EBF572oAAAAJ
11. **[2] Yang Chin. Phys. Lett. 43,020712 (2026) ◐**
    arXiv:2512.24553 "From Berry curvature to quantum metric: a new era of quantum geometry metrology for Bloch electrons in solids"真实存在，标题与条目一致；CPL 正式版 DOI 10.1088/0256-307X/43/2/020712 结构合规（43 卷=2026、issue 2、文章号 020712）但未独立打开核实（见 R3-06）。
    https://arxiv.org/pdf/2512.24553

核实结论：11 条中 9 条确认真实且支撑声称（[4][8][11][12][13][21][48][49][56]，其中 [4] 存在一处正文表述超前、[56] 存在一处归纳不完整），[2] 预印本锚真实、正式版待核，[52] 确认一处年份著录错误；0 条伪引；0 条 citation_misattribution 达 critical 级（[4]"栅压可调"为 minor 级表述超前，未达"真实但不支撑声称"的 critical 门槛——原文确证量子度规磁阻可观测性这一核心声称）。

## 意见清单

[R3-01|major] 参考文献｜[52]｜年份著录错误（卷 21 对应 2025）｜"Kang, M., Kim, S., Qian, Y. et al. Measurements of the quantum geometric tensor in solids. Nat. Phys., 2024, 21: 110-117. DOI: 10.1038/s41567-024-02678-8"｜经 Scholar/exaly 双源核实正式版为 Nature Physics 21(1), 110–117 (2025)；DOI 前缀 s41567-024 亦指向 2024 年接收。建议年份改 2025；若引用格式要求以在线首发年计仍需与 DOI 年份协调统一。

[R3-02|minor] 立项依据｜rationale §1.0（L9）｜[4] "栅压可调"表述超前于原文｜"Sala 等 2026 年在 Sb₂Te₃ 薄膜拓扑表面态中实现栅压可调的量子度规磁阻[4]"｜原文证实的是 time-reversal-odd 非线性磁阻、与温度/散射时间无关（30 K 以下），未报告栅压调制。建议删"栅压可调"，改"实现量子度规的非线性磁阻探测"。

[R3-03|minor] 参考文献｜条目物理顺序｜上轮重排后两处乱序未巩固｜[48] 行位于 L83（[38]/[39] 之间）、[56] 行位于 L102（[47]/[49] 之间）｜编号-正文引用已一致、[41] 预留合规，仅条目行未按编号归位。建议按 [1]…[56] 重排物理行序，或整体重编为连续 1–55 并同步正文（后者可顺带消除 [41] 跳号）。

[R3-04|minor] 研究内容｜content §2.2（L31）｜[56] 谐波通道归纳不完整｜"低于阈值谐波间的纠缠参数 $R$ 随激光功率振荡，并在多个功率位置出现局域极大值[56]"｜原文为"阈值上谐波之间"与"阈值上-下谐波之间"两类通道均现振荡局域极大。建议改述为"含低于阈值通道在内的谐波间纠缠随激光功率振荡"，与原文两类通道对齐。

[R3-05|suggestion] 研究方案｜scheme §2.3/§7.1 等多处｜[12] e^{-2r} 封闭式未独立复核｜"$\Delta H^2(r)/\Delta H^2_\text{SQL} = e^{-2r}$ … 最优压缩点 $r_\text{opt}\approx1.6$"｜arXiv:2605.21925 已核实真实且主题吻合，但该式与 r_opt 数值是全文判据链锚（rationale §1.2/§1.5、scheme §2.3/§3.1、创新点一），摘要层面未见。建议对照原文公式编号逐字复核后引用。

[R3-06|suggestion] 参考文献｜[2]｜CPL 正式版未独立打开｜"Chin. Phys. Lett., 2026, 43: 020712. DOI: 10.1088/0256-307X/43/2/020712"｜arXiv:2512.24553 已核实、DOI 结构合规；建议投稿前在 CPL 官网终核卷期与文章号。

——总评：上轮程序化重排在"编号-内容"层面已巩固（[48]/[56] 正文引用点均指向正确条目，[41] 预留合规），遗留缺陷为条目物理行序两处乱序；全表 55 条利用率 100% 属实、五项对账零缺陷。唯一实质性著录错误为 [52] 年份（2024→2025，major）；另有 3 处 minor 表述/顺序问题与 2 处建议级复核项。无需删条；[4] 与 [56] 属表述修正而非去引用化。
