# R3 引用审校 — general-moire-strong-field-probe-20260726

审校日期：2026-10-17 ｜ 审校人：R3 引用审校评审员（期刊文献编辑）
对象：`research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/sections/`（rationale.md / content.md / scheme.md / references.md，30 条含 [29][30] 研读基础文献）

## 编号对账

方法说明：终端执行环境故障，对账改为"Grep 提取 + 全量人工比对"（脚本 /tmp/r3_citation_audit.py 已备）。条目行按"行首 [n] 后非 -/–"识别；正文引用含 [n,m] 并引、[a]–[b] 区间式（rationale L107 "见 [1]–[28]" 为范围声明式引用，已按区间展开验证覆盖）与单引。

| 检查项 | 计数 | 明细 |
|---|---|---|
| 占位符 | 0 | 无 TODO/待补/空条目；[12] 为 arXiv 预印本但著录完整（含 v2 修订日期） |
| 死条目 | 0 | 30/30 条全部被正文引用：[1]–[28] 正文三章引用（其中 [27] 仅在 scheme §3.5 出现一次，成立）；[29][30] 在 scheme §3.5（L174）以 [N] 角标引用，与表头"另列分节"声明一致 |
| 超界 | 0 | 正文最大引用号 [30] = 条目最大号 |
| 一号两用 | 0 | 编号 [1]–[30] 连续唯一，物理顺序严格递增；无重复著录 |
| 断链 | 0 | 正文所有引用编号均有对应条目 |

附加核实：①表头统计声明"近三年（2024–2026）文献 19 条，占 63.3%；2011–2012 奠基文献 3 条（[5][23][24]）"——逐条清点：2024–2026 条目恰为 [2][3][4][6][8][9][10][12][14][16][18][19][20][21][25][27][28][29][30] = 19 条（63.3% ✓）；[5] 2011、[23] 2011、[24] 2012 ✓。声明与事实一致。②署名规则"前三作者+等、单/双作者不缀等"抽查 [7] Ikeda T. N.（单作者）、[8] Mrudul M. S.（单作者）均不缀"等" ✓。③[15] Shan 主文+Erratum 双著录结构合规（DOI 前缀均为 s41586-021 系列）。

## 联网核实记录（URL）

策略：核心计算基准（[6] 12,400 原子/10⁵ 核时）+ Δ_CI 量级差双锚（[12] 1.76 eV / [19] 32–44 meV）+ 2025–2026 新条目（[27][28]）+ 研读基础文献两条（[29][30]，§3.5 创新点三的实测参照）。共 7 条。

1. **[6] Molinero Optica 11(2),171 (2024) ✓**
   标题与作者逐字命中（Eduardo Bernal Molinero, Anushree Datta, M. J. Calderón, Elena Bascones, Rui E. F. da Silva）；Optica 补充材料托管于 opticapublishing.figshare（期刊归属确认）。正文声称"H₃、H₅、H₇ 在魔角附近谐波抑制"与原文摘要"drastic decrease of harmonic signal as we approach the magic angle"一致。
   http://arxiv.org/pdf/arXiv:2302.04127v1.pdf ｜ https://opticapublishing.figshare.com/articles/journal_contribution/Supplementary_document_for_High-Harmonic_Generation_with_a_twist_all-optical_characterization_of_magic-angle_twisted_bilayer_graphene_-_6809865_pdf/24936525
2. **[12] Ikeda arXiv:2508.00296 ✓**
   arXiv 摘要页命中："intense mid-infrared (MIR) pulse induces melting of a Mott-insulator state in a one-dimensional cuprate, Sr₂CuO₃…each harmonic frequency decreases from odd multiples of the MIR frequency"——正文"把该类位移归因于亚周期时间尺度的 Mott 熔化"声称匹配；作者 Ikeda/Murakami/Okamoto 与条目" Ikeda R., Murakami Y., Sakai D. 等"吻合（Semantic Scholar 条目佐证）。
   https://arxiv.org/abs/2508.00296
3. **[19] Lian Nat. Phys. 20(1),34–39 (2024) ✓（卷期页+DOI 全对）**
   NSF PAR 与 ACS 论文引用列表双源确认："Valley-polarized excitonic Mott insulator in WS₂/WSe₂ moiré superlattice. Nat. Phys. 2024, 20, 34–39, DOI: 10.1038/s41567-023-02266-2"——与条目逐字段一致；作者 Lian Zhen, Meng Yuze, Ma Lei 吻合。⚠ 正文引用的"激子-激子排斥能约 32–44 meV、Mott 态蓝移 9–41 meV"两组数值未在摘要层面复现（见 R3-05）。
   https://par.nsf.gov/search/author:%22Lian,%20Zhen%22 ｜ https://pubs.acs.org/doi/full/10.1021/acs.nanolett.4c02750
4. **[27] Kumar Nano Lett. 26(31),10547–10553 (2026) ◐**
   arXiv:2607.22532 "Supermoiré-trapped quadrupolar exciton"（WS₂/WSe₂/WS₂ heterotrilayer、超莫尔势阱捕获四极激子）真实存在，主题与条目/正文一致；但 Nano Letters 正式版卷期页与 DOI 10.1021/acs.nanolett.6c03005 未能独立核实，且正文引用的"δ ≈ 11.5 meV 势阱深度"未见于摘要（见 R3-02/03）。
   https://arxiv.org/html/2607.22532
5. **[28] Sun PRR 7(4),043288 (2025) ✓✓（含 DOI 短码真实性确认）**
   ORCID 双记录逐字命中："Self-consistent tensor network method for correlated super-moiré matter beyond one billion sites, Physical Review Research, 2025-12-12, DOI: 10.1103/krjp-mn4v, Contributors: Yitao Sun; Marcel Niedermeier; Tiago V. C. Antão; Adolfo O. Fumega; Jose L. Lado"——条目 DOI 10.1103/krjp-mn4v（此前视作格式可疑的 APS 短码）确认为真实注册 DOI；正文"N ~ 10⁹ 量级、QTCI 张量插值"声称与原文一致。
   https://orcid.org/0009-0002-9479-7147 ｜ https://arxiv.org/html/2503.04373v3
6. **[29] Seewald arXiv:2510.09548 ✓**
   arXiv 编号+标题逐字命中（"Mapping the moire potential in multi-layer rhombohedral graphene"）。⚠ 条目声称的"~60 mV 振幅与 0.56° 空间 mapping"数值未在检索摘要层面复现（见 R3-04）。
   https://jinhong-park.github.io/arxiv/2025/10/Oct2weeks
7. **[30] Klein Nature 650(8103),875–881 (2026) ✓**
   Paperity 收录 Nature 正式版（标题 "Imaging the sub-moiré potential using an atomic single electron transistor"，正式版较 arXiv 版删"Landscape"一词）；arXiv:2410.22277 摘要确认"quantum twisting microscope (QTM) 平台、graphene/hBN 界面、~60 mV 振幅"——与条目方法学关联注释（1 nm 分辨率、~60 mV）一致。
   https://paperity.org/p/370569867/ ｜ https://arxiv.org/pdf/2410.22277

核实结论：7 条中 5 条确认真实且支撑声称（[6][12][19][28][30]），[27] 预印本锚真实、正式版待核，[29] arXiv 锚真实、数值细节待复核；0 条伪引；0 条 citation_misattribution。未联网复核条目：[15] Shan（Nature 2021 成熟论文，风险低）、[1][5][23][24] 等奠基文献（领域公认）。

## 意见清单

[R3-01|suggestion] 研究方案｜scheme §3.4 TBG 臂（L134）｜[6] "1 meV THz 驱动"参数待复核｜"先期以 [6] 在 1 meV THz 驱动下的低损伤值作类比下限"｜Molinero 论文已核实真实，但其驱动光子能量在检索摘要中未出现；建议对照原文 Methods 复核"1 meV"量级，若不符需同步修改 TBG 损伤阈值类比下限。

[R3-02|suggestion] 参考文献｜[27]｜正式版卷期页与 DOI 待核｜"Nano Letters 26(31), 10547–10553 (2026). DOI: 10.1021/acs.nanolett.6c03005"｜arXiv:2607.22532 已核实存在；建议投稿前在 pubs.acs.org 终核卷期页与 DOI，若尚未见刊则改标 arXiv 体例。

[R3-03|suggestion] 研究方案｜scheme §3.5 前置工作（L172）｜[27] δ≈11.5 meV 数值待复核｜"Kumar 等 2026 年 [27] 在超莫尔势阱中观测到四极激子的鲁棒捕获（δ ≈ 11.5 meV 为超莫尔势阱深度…）"｜arXiv 摘要未见该值；建议对照原文图表核实后保留，或去数值化改述"深势阱捕获"。

[R3-04|suggestion] 参考文献｜[29]｜0.56°/60 mV 细节待复核｜"提供 ~60 mV 振幅与 0.56° 空间 mapping 数据"｜arXiv:2510.09548 已核实真实；建议对照原文确认 0.56° 归属（该角亦出现在 [30] 语境），避免两文数值串引。

[R3-05|suggestion] 立项依据｜rationale §1.5 判据演化（L83）｜[19] 两组能标数值待原文复核｜"激子-激子排斥能约 32–44 meV、Mott 态蓝移 9–41 meV"｜该两组数值是 Δ_CI 5–20 meV 工作区间的上游依据；卷期/DOI 已核实全对，建议对照 Nat. Phys. 20, 34 原文图注复核数值后定稿。

——总评：编号对账五项全零，[1]–[28]/[29]–[30] 分节结构与表头统计声明（19 条 2024–2026、63.3%）完全自洽；无 critical/major 问题，全部 5 条意见为建议级复核项，集中在"正式版著录终核"与"具体数值的原文出处"两类，无需删条或去引用化处理。
