# R3 引用审校 — general-attosecond-streaking-20260822

审校范围：`research_proposals/optimizing/general-attosecond-streaking-20260822/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-24。对账脚本：/tmp/panel-r4-citation-audit.py（复核用）/tmp/r3-audit.py（复核脚本，含 full_review 口径）
refs 48 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **1** | `[40]† Xia M, Nishimiya K, Dong D, et al. Complex-gate all-optical FROG…`（arXiv:2608.30516, 2026）——正文三章零引用，full_review 零引用，全文仅在 references.md L83 出现 |
| 3. 超界 | **0** | 正文最大引用号 = 48 = refs 最大条目号 48，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–48 严格升序、连续、无重号；每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文三章引用号 47 个（rationale 42 token / 37 distinct，content 14 token / 13 distinct，scheme 38 token / 26 distinct），refs 48 条 → 差值 1 即 `[40]`，与预跑脚本结论一致，**复核确认预跑结果准确，无漏报**。
- **full_review 口径**：把 `full_review.md` 纳入引用集合后，死条目仍为 `[40]`（未新增/减少），说明整篇一致性审查未引用任何正文未用条目，也未遗留正文未引条目。
- **格式变体排查**：正文引用形式统一为单个 `[n]`，未见 `[a,b]` 并列式、`[a-b]` 区间式（正文唯一形如 `[1 − cos 2(ωt + φ_CEP)]` 为公式，非引用）；无中文逗号/顿号分隔的漏网编号。预跑脚本的密勒指数排除逻辑（`(100)`）在本课题无需触发（正文未出现三字密勒指数语境）。
- **引用密度**：正文编号引用 token 合计 94 次（rationale 42 + content 14 + scheme 38），落在范本区间（正文 10–20 次编号引用）之上；refs 48 条 vs 范本 30–40 条亦偏高但可接受——多出的 8 条集中在近三年（2024–2026）与方法学支撑（水源/重建/评审争议），属实质覆盖而非灌水。

---

## 二、联网核实记录

核实方法：① DOI 条目全部经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）按 DOI 逐条反查，逐字段比对期刊名/卷/期/页码/文章号/年份/首作者；② 无 DOI 的 arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、journal_ref（是否已出正式版）、DOI；③ 关键数值声称回原文（arXiv 全文 / 期刊页 / PMC）逐句核对。

**元数据逐字段比对结果：41 条含 DOI 的条目，期刊名 / 年份 / 卷号 / 页码或文章号 / 首作者五个字段全部一致，不符数 = 0。** 6 条无 DOI 条目（[21][24][29][38][40][48]）经 arXiv 反查，标题与作者链全部一致，年份一致。

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [1] | Nature 2010 | ✓ 卷 466 / 739-743 / 作者链 12 位一致 | https://api.crossref.org/works/10.1038/nature09212 |
| [2] | Phys. Rev. X 2017 | ✓ v7:041030；Published 2 Nov 2017；摘要确认"首次水窗条纹测量""1850 nm sub-2-cycle CEP-stable" | https://journals.aps.org/prx/abstract/10.1103/PhysRevX.7.041030 |
| [3] | Phys. Rev. A 2016 | ✓ v94:013411 | https://api.crossref.org/works/10.1103/PhysRevA.94.013411 |
| [4] | Science 2010 | ✓ v328:1658-1662 | https://api.crossref.org/works/10.1126/science.1189401 |
| [5] | Phys. Rev. A 2005 | ✓ v71:011401 | https://api.crossref.org/works/10.1103/PhysRevA.71.011401 |
| [6] | Journal of Optics 2018 | ✓ v20:023001 | https://api.crossref.org/works/10.1088/2040-8986/aaa394 |
| [7] | Nat. Commun. 2022 | ✓ v13:5205；摘要确认"Ne 外壳层分波角动量通道的相位与幅度" | https://api.crossref.org/works/10.1038/s41467-022-32780-5 |
| [8] | J. Phys. Photonics 2024 | ✓ v6:025007；摘要确认 rACE 方法与"优于原子单位时间的绝对延迟确定度" | https://api.crossref.org/works/10.1088/2515-7647/ad252a |
| [9] | Chinese Physics B 2026 | ✓ v35:054204；published 2026-05-01 | https://api.crossref.org/works/10.1088/1674-1056/ae3474 |
| [10] | Phys. Rev. Research 2025 | ✓ v7:L022074；Published 24 June 2025；摘要确认"ATAS + 强场电离诱导偶极相移的时间演化，Xe 4d–5p 离子跃迁" | https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.7.L022074 |
| [11] | Optics Express 2019 | ✓ v27(4):4799-4807 | https://api.crossref.org/works/10.1364/OE.27.004799 |
| [12] | Rev. Sci. Instrum. 2015 | ✓ v86(12):123106 | https://api.crossref.org/works/10.1063/1.4937623 |
| [13] | Nat. Commun. 2014 | ✓ v5:3331 | https://api.crossref.org/works/10.1038/ncomms4331 |
| [14] | Science 2008 | ✓ v322:1525-1529 | https://api.crossref.org/works/10.1126/science.1163439 |
| [15] | Science 2017 | ✓ v356:1150-1153 | https://api.crossref.org/works/10.1126/science.aam8393 |
| [16] | Phys. Rev. Lett. 2011 | ✓ v106:143002；Published 5 April 2011；正文确认"Ar 3s 与 3p 壳层、32–42 eV"；**注意该文有 Erratum PRL 106, 169904 (2011)** | https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.106.143002 |
| [17] | Light: Sci. Appl. 2024 | ✓ v13:250 | https://api.crossref.org/works/10.1038/s41377-024-01600-4 |
| [18] | Phys. Rev. A 2026 | ✓ v113:043103；**Published 2 April 2026**；摘要确认"rainbow 风格计时、连续提取相位与时延、He/Ar/Xe 三靶" | https://journals.aps.org/pra/abstract/10.1103/9jcm-8gd8 |
| [19] | Phys. Rev. A 2025 | ✓ v111:013119；**短式 DOI `10.1103/PhysRevA.111.013119` 有效** | https://api.crossref.org/works/10.1103/PhysRevA.111.013119 |
| [20] | Phys. Rev. Lett. 2025 | ✓ v135:183202；短式 DOI `10.1103/ll25-15dm` 有效（APS 新格式） | https://api.crossref.org/works/10.1103/ll25-15dm |
| [21] | arXiv:2503.21976, 2025 | ✓ Tarrant J, Kolorenč P, Khokhlova M, Ruberti M, Averbukh V（5 人）；2025-03-27 提交；**无 journal_ref、无 DOI → 确未见正式发表版，† 标注成立** | https://export.arxiv.org/api/query?id_list=2503.21976 |
| [22] | J. Phys. B 2026 | ✓ v59(12):125601；published 2026-06-26；摘要确认"Gaussian/Airy/五阶相位 XUV 脉冲的条纹时延依赖光谱相位" | https://api.crossref.org/works/10.1088/1361-6455/ae7acf |
| [23] | Phys. Rev. Accel. Beams 2025 | ✓ v28(7):074601 | https://api.crossref.org/works/10.1103/csvm-858f |
| [24] | arXiv:1804.09583, 2018 | ✓ Zimmermann T, Ortmann L, Hofmann C, Rost J-M, Landsman A S（5 人）；2018-04-25 提交；**无 journal_ref、无 DOI → 确未见正式发表版，† 标注成立** | https://export.arxiv.org/api/query?id_list=1804.09583 |
| [25] | New J. Phys. 2023 | ✓ v25(8):083003 | https://api.crossref.org/works/10.1088/1367-2630/ace8b3 |
| [26] | Phys. Rev. A 2022 | ✓ v105:013111 | https://api.crossref.org/works/10.1103/PhysRevA.105.013111 |
| [27] | Rep. Prog. Phys. 2024 | ✓ v87(8):086401 | https://api.crossref.org/works/10.1088/1361-6633/ad6278 |
| [28] | Phys. Rev. Lett. 2002 | ✓ v88:173903 | https://api.crossref.org/works/10.1103/PhysRevLett.88.173903 |
| [29] | arXiv:2508.14774, 2025 | ✓ Gao J, Hasan M, Liang H 等 11 人；2025-08-20 提交；**无 journal_ref → 确未见正式发表版**；摘要确认"25±2 as、50–320 eV、跨越碳 K 边、光子通量 >10¹² /s、氦气角分辨条纹相机 + 介质滤波片补偿 attochirp" | https://export.arxiv.org/api/query?id_list=2508.14774 |
| [30] | Ultrafast Science 2025 | ✓ v5:0128 | https://api.crossref.org/works/10.34133/ultrafastscience.0128 |
| [31] | Ultrafast Science 2026 | ✓ v6:0145；published 2026-01-01；摘要确认质疑三点：Auger 电子未计入、低能谐波未滤除、本征啁啾未补偿 | https://api.crossref.org/works/10.34133/ultrafastscience.0145 |
| [32] | Phys. Rev. Lett. 2024 | ✓ v133:163201 | https://api.crossref.org/works/10.1103/PhysRevLett.133.163201 |
| [33] | Phys. Rev. Lett. 2024 | ✓ v133:183201 | https://api.crossref.org/works/10.1103/PhysRevLett.133.183201 |
| [34] | AAAI 2026 | ✓ v40(16):14014-14021；published 2026-03-14 | https://api.crossref.org/works/10.1609/aaai.v40i16.38412 |
| [35] | Nat. Commun. 2026 | ✓ v17:8810；published 2026-08-21 | https://api.crossref.org/works/10.1038/s41467-026-76827-3 |
| [36] | Chinese Physics B 2024 | ✓ v33:013201 | https://api.crossref.org/works/10.1088/1674-1056/ad0e5d |
| [37] | Nature 2024 | ✓ v632:762-767；摘要确认"NO 分子氧 K 阈附近时延高达 700 as、延迟谱调制、shape 共振瞬态俘获 + Auger-Meitner 电子碰撞 + 多电子散射" | https://api.crossref.org/works/10.1038/s41586-024-07771-9 |
| [38] | arXiv:2511.08391, 2025 | ✓ Ardana-Lamas F, Cousin S L, Lignieres J, Biegert J（4 人）；2025-11-11 提交；**无 journal_ref → 确未见正式发表版** | https://export.arxiv.org/api/query?id_list=2511.08391 |
| [39] | Phys. Rev. Lett. 2026 | ✓ v136:163201；短式 DOI `10.1103/578k-kmw6` 有效；published 2026-04-20；摘要确认"Xenon/krypton、atto-SXR 中心 130 eV、CEP 稳定少周期 Yb、Auger 电子相对 4d 光电子 ~1.32 fs 时间偏移" | https://api.crossref.org/works/10.1103/578k-kmw6 |
| [40] | arXiv:2608.30516, 2026 | ✓ Xia M, Nishimiya K, Dong D, Fu Y, Takahashi E J（5 人）；2026-08-31 提交；**无 journal_ref → 确未见正式发表版，† 标注本身合规**；但正文零引用（见意见 R3-01） | https://export.arxiv.org/api/query?id_list=2608.30516 |
| [41] | Optica 2020 | ✓ v7(2):168-171 | https://api.crossref.org/works/10.1364/OPTICA.379846 |
| [42] | Structural Dynamics 2024 | ✓ v11(5):054303；published 2024-09-01；全文核实：10 kHz MIR OPCPA、中心波长 **2.1 µm**、27 fs；能区"across the water window from 200 to 600 eV" | https://arxiv.org/abs/2407.05964 |
| [43] | Optics Express 2025 | ✓ v33(13):28071-28080；摘要确认"2.1 µm 压缩至 6.9 fs、2.35 mJ、10 kHz、CEP 稳定 131 mrad" | https://api.crossref.org/works/10.1364/OE.564364 |
| [44] | Commun. Phys. 2020 | ✓ v3:92；摘要确认"TW 级中红外 + loose focusing HHG，较前人强 100 倍以上" | https://api.crossref.org/works/10.1038/s42005-020-0355-x |
| [45] | New J. Phys. 2016 | ✓ v18(7):073009 | https://api.crossref.org/works/10.1088/1367-2630/18/7/073009 |
| [46] | Sov. Phys. JETP 1965 | ⚠ 俄文原件 ЖЭТФ 47, 1945 (1964) ✓ 与 APS 官方转引格式一致；英译本页码 1307-1314 ✓；**但见意见 R3-05（转引年份双写）** | https://inspirehep.net/literature/1793133 |
| [47] | Phys. Rev. Lett. 1993 | ✓ v71(13):1994-1997 | https://api.crossref.org/works/10.1103/PhysRevLett.71.1994 |
| [48] | arXiv:2610.24891, 2026 | ✓ Gao J, Hasan M, Eisenhutt Z, Serov V, Liang H, Han M, Kheifets A（7 人）；2026-10-17 提交；**无 journal_ref → 确未见正式发表版**；摘要确认"P1+P3 Legendre 分量 → 等效 s/d 双光子振幅比、多通道双电子 TDSE 验证 Fano 选择定则存活" | https://export.arxiv.org/api/query?id_list=2610.24891 |

**核实条数合计：48 / 48 条（41 条 DOI 经 Crossref + 6 条 arXiv 经 arXiv API + [46] 俄文转引经 INSPIRE/APS 交叉确认）。虚构文献 0 条；元数据错误 0 条。**

**短 DOI 新格式核查**：[18] `10.1103/9jcm-8gd8`、[20] `10.1103/ll25-15dm`、[23] `10.1103/csvm-858f`、[39] `10.1103/578k-kmw6` 四条均为 APS 2024 年起启用的短式 DOI，Crossref 均可正常解析且解析结果与著录完全一致 → **有效，非虚构**。

---

## 三、正文声称与文献内容匹配性抽查

抽查 12 条（被引最多 + 支撑关键判据 + 近年条目 + 争议链条），**12/12 全部匹配，未发现"正文说 A、文献做 B"的情况**。

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L11「Cousin 等[2]于 2017 年…把软 X 射线阿秒脉冲的谱覆盖推进至 350 eV，并首次在水窗低段实现阿秒条纹测量，给出 322 as 的孤立脉冲上限」 | 原文（arXiv:1710.02208v1 全文）："photon energy in the soft X-ray range up to 350 eV"、"confirm an upper limit of the duration of the isolated pulse of 322 as" | ✓ 三个数值（350 eV / 322 as / 首次）全部逐字对应 |
| rationale L7「Goulielmakis 等[1]…以阿秒瞬态吸收光谱实现氪原子价电子运动」 | Nature 466:739，"Real-time observation of valence electron motion" | ✓ |
| rationale L9「Klünder 等[16]…对氩原子 3s 与 3p 壳层在 32–42 eV 区间的相对延迟进行提取」 | PRL 摘要："difference in time delays between electrons emitted from the 3s² and from the 3p⁶ shell, at different excitation energies ranging from 32 to 42 eV" | ✓ 壳层与能区数值全对 |
| rationale L13 / scheme L43「Cousin 等[2]的水窗条纹实验以氖为高次谐波产生气、以氪为条纹探测靶气，其氖 3 bar 背压氖气腔产气体制」 | 原文："a backing pressure of 3 bar of neon"、"krypton" | ✓（Han [31] 摘要独立佐证 "krypton atoms" 与 "Phys Rev X 7, 041030 (2017)"） |
| rationale L29「Peschel 等[7]2022 年以角分辨 RABBIT 实验测量 Ne 价壳层各分波通道的相位与幅度」 | Nat. Commun. 摘要："we measure the phase and amplitude of the individual angular momentum channels as a function of kinetic energy in the outer-shell photoionization of neon" | ✓ |
| rationale L33「Driver 等[37]于 2024 年在 Nature 报道 NO 分子中氮、氧两 K 壳层间的相对芯态光电离时延，在氧 K 阈附近测得高达 700 as 的延迟…shape 共振…Auger-Meitner 电子碰撞…多电子散射」 | Nature 摘要逐条对应："delays, ranging up to 700 as in NO near the oxygen K-shell threshold"、"transient trapping of the photoelectron owing to shape resonances, collisions with the Auger–Meitner electron"、"multi-electron scattering effects" | ✓ 四项机制全对 |
| rationale L59「Hutcheson 等[10]结合阿秒瞬态吸收光谱与 R 矩阵含时计算，追踪了氙 4d–5p 离子跃迁偶极相移的时间演化…分解为电离累积、瞬态激发与基态极化可逆布居三个过程」 | PRResearch 摘要："time-dependent evolution of the dipole phase shift induced by strong-field ionization (SFI) using attosecond transient absorption spectroscopy (ATAS)"、"ionic 4d-5p in xenon"、"we attribute the complex dynamics to the contribution of three d[istinct]…" | ✓ 方法（ATAS + 理论）、体系（Xe 4d–5p）、三过程分解全部对应 |
| rationale L53「Inzani 等[8]…提出 rACE 非线性拟合方法…重构 XUV 强度包络与 IR 矢量势…在其报道的验证场景获得了优于原子单位时间（约 24.2 as）的绝对延迟确定度」 | J. Phys. Photonics 摘要："rACE (refined Analytical Chirp Evaluation), which retrieves both pump and probe pulses while establishing a direct relation between the reconstructed time axis and the experimental delay"、"achieves a precise absolute delay calibration with an accuracy better than the atomic unit of time" | ✓ |
| content L11 / rationale L57「Aygun 等[22]2026 年的 1D-TDSE 计算则揭示光谱相位结构（三阶 Airy、五阶相位）对条纹时移的修正」 | J. Phys. B 摘要："we compare streaking time delays for Gaussian, Airy, and fifth order phase extreme ultraviolet (XUV) pulses" | ✓（三阶 Airy / 五阶相位表述与摘要一致） |
| scheme L21「Gao 等[48]…以宇称—频率滤波分离出等效 s/d 双光子振幅比，并由多通道两电子 TDSE 计算验证电子关联下的选择定则存活」 | arXiv:2610.24891 摘要："filtering the inversion-odd response in helium streaking data at the IR fundamental… isolate an angular distribution dominated by the P₁ and P₃ Legendre components, whose complex coefficients yield an effective s/d two-photon amplitude ratio. Multichannel, two-electron time-dependent Schrödinger equation calculations demonstrate that the characteristic Fano propensity survives electron correlation" | ✓ 逐句对应 |
| scheme L21「Tarrant 等[21]†2025 年通过高精度 ab initio 计算理论预言…shake-up 通道可呈现相干激发特征并以『呼吸离子』形式给出可测信号」 | arXiv:2503.21976 摘要："high-accuracy ab initio theoretical methods…coherent shake-up…radial expansion and contraction of the electron density which we term 'breathing ions'" | ✓ |
| rationale L39 / scheme L98「Ardana-Lamas 等[30]…检索给出 19.2 as（−2.1/+4.6 as）表征，谱中心 243 eV、上沿 390 eV」；「Han 等[31]…质疑涉及 Auger 电子污染、未滤除低能谐波、本征啁啾未补偿」；「Ardana-Lamas 等[38]随后以预印本†形式逐条答辩」 | arXiv:2510.04086 摘要："duration of 19.2 attoseconds… spectrum centred at 243 eV, extending up to 390 eV"；[31] 摘要："without accounting for the contribution of Auger electrons or employing filters to remove low-energy harmonics and compensate for the intrinsic pulse chirp"；arXiv:2511.08391 comment 字段："Reply to arXiv:2510.17949" | ✓ 19.2 as / 243 eV / 390 eV 与三项质疑全部对应；答辩与质疑的 arXiv 配对关系确认 |

**数值抽查**：`[42] Jarecki 2024` —— 正文称"2.1 μm、10 kHz OPCPA，覆盖 284–531 eV 水窗能区"；原文实测"MIR OPCPA, 10 kHz, 27 fs, central wavelength 2.1 µm"，能区原文为"across the water window from **200 to 600 eV**"。→ 驱动波长与重复频率 ✓，但能区数值 284–531 eV 系正文自取的水窗定义（C K 边–O K 边），与原文 200–600 eV 口径不同（见意见 R3-06）。
`[43] Blöchl 2025` —— 正文称"2.1 μm 压缩至 6.9 fs 单周期、10 kHz、2.35 mJ"；摘要"compression of few-cycle 2.1 µm… to 6.9 fs with 2.35 mJ pulse energy at a 10 kHz repetition rate… single cycle light field oscillation" ✓ 全对。

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[2]（Cousin 2017，水窗条纹实验，全文引用 5 次：rationale L11/L23/L27、scheme L43/L65/L108、full_review L5）、[3]（Pabst & Dahlström，6 次）、[7]（Peschel，4 次）、[27]（Ortmann & Landsman，3 次）、[13]（Ishii，3 次）、[9]/[11]/[23]（CNN 路径，2–3 次）。被引最高的前 10 条承担了「单通道失效机理—偶极相位解耦原理—算法起点—水窗实验—评审争议」五条主线，引用结构与论证链匹配。
- **关键判据的引用支撑**：R1 修正项的物理入口（[2][7][27]）、R2 角积分压制机理（[3]）、R3 跨能区标定（[30][31][38][39][45]）、替代路径 A 的网络选型（[9][11][34]）、光源选型先例（[13][41][42][43][44]）、史学根基（[46][47]）均有对应条目。
- **无引用支撑的关键论断**：正文对"rACE 公开全文未见该数值表述"、"Pabst 与 Dahlström 未给出残余量化上界"、"Kheifets 等[18]同样未报告残余区间数字"、"2%/10%/100 eV/40% 四项为方案设定值"四处，均**显式声明了"文献未给出"并自标为设计阈值**——处理方式正确，不属漏引。
- **覆盖缺口（low）**：rationale L21 讨论"Schultze 等的 Ne 2s-2p 相对延迟测量…Klünder 等的 Ar 3s-3p 相对延迟测量…二者给出的均为壳层间相对光电离延迟"这一谱系论证中，两条文献在同段内**均未带编号**（Schultze 对应 [4]、Klünder 对应 [16]），读者需回溯前文 L7/L9 自行配对。属编号可读性缺陷，非断链。
- **密度判断**：正文 94 次编号引用 / 48 条 refs，引用密度显著高于范本下限，且未见"同一条目反复充数"的模式（[3] 6 次、[2] 5 次均有实质不同的支撑点）。结论：**覆盖充分**。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | high | 参考文献 | refs 条目 [40]（references.md L83）；正文三章零引用 | 死条目：预印本条目全篇零引用 | `[40]† Xia M, Nishimiya K, Dong D, et al. Complex-gate all-optical frequency-resolved optical gating…` | 二选一：①在 rationale §2.5「脉冲表征方法在解析拟合与数据驱动两个方向上各有推进」段或 §2.2 末段，就"全光频率分辨光门控（AO-FROG）表征超宽带孤立脉冲"补一句正文引用 [40]（该文在检索池 lit-gap-1790890315.md 有记录：RIKEN 团队 AO-FROG 实验演示，适用于水窗 SXR 区，与本项目"水窗低段脉冲表征"直接相关）；②若不引用，删除 [40] 条目并将其后编号（[41]–[48]）前移。注意：池中已有该条目记录，允许引用；但**不得新增池外条目**。 |
| R3-02 | medium | 参考文献 | refs 尾注（references.md L103） | 尾注自证与实物不一致：声明"文献条目 48 条…编号 1–48 连续"但未声明"全部被引用"，同时存在死条目 [40]，条目数与实际被引数不符，读者无法从尾注察觉死条目 | `文献条目 48 条，覆盖阿秒条纹理论与实验…本申请书文献检索截止于 2026 年 9 月。` | 在尾注中补一句实际口径，与修完 R3-01 后的实物保持一致，例如："文献条目 48 条，编号 1–48 连续，其中 47 条为正文引用条目，1 条（[40]）为待接入条目"；或在解决 R3-01 后改写为"全部 48 条均已在正文对应位置引用"。 |
| R3-03 | medium | 立项依据 | rationale L37；scheme L98 | 检索截止时间声明与实际收录条目时间不符：refs 尾注与 rationale L13 均声明"文献检索截止于 2026 年 9 月"，但 [48] 为 2026-10-17 提交的 arXiv 预印本、[35] 为 2026-08-21 正式发表、[39] 为 2026-04-20 正式发表——其中 [48] 的提交时间已越截止线 | `本申请书文献检索截止于 2026 年 9 月。`（references.md L103）／`文献检索截止 2026 年 9 月`（rationale L13） | 将截止时间统一更新为"文献检索截止于 2026 年 10 月"（rationale L13 与 references 尾注两处同步），或在 [48] 条目后注明"（2026 年 10 月补充检索获得）"。二选一，不可两处口径不一。 |
| R3-04 | medium | 参考文献 | refs 条目 [29]（references.md L61）；正文 rationale L37、scheme L98 | 预印本 † 标注规范不完整：refs 头部声明"编号后标 † 者为 arXiv 预印本，未见正式发表版；正式发表后另行替换"，但同一课题的同一系列工作已有正式发表版 [35]（Nat. Commun. 2026, 17:8810，"Bright isolated light pulses reaching 18 attoseconds…"），[29] 与 [35] 为同组同系列（25 as 预印本 → 18 as 正式版），条目本身仍标 † 且正文以"预印本†"称引，未标注其与正式版的关系 | `[29]† Gao J, Hasan M, Liang H, et al. Bright 25-attosecond light pulses reach the one atomic unit of time. arXiv:2508.14774…` | 核验后（arXiv:2508.14774 无 journal_ref，2026-10-25 查证）† 标注成立，保留条目不改；但应在 [29] 条目尾补注"同系列后续正式发表版见 [35]"，正文 rationale L37 现有"该课题组后续将脉宽压缩至 18 as（正式发表版[35]）"已作交代，scheme L98 同句亦已交代——**建议仅在 refs 条目 [29] 内补一句同系列指向，保持 refs 自洽**，不改正文。 |
| R3-05 | low | 参考文献 | refs 条目 [46]（references.md L95） | 条目年份双写易生歧义：主著录年份 1965（英译本 Sov. Phys. JETP 20(5):1307-1314），括注俄文原件"ЖЭТФ 47, 1945, 1964"——同年给出三个年份（1965 / 1945 / 1964），读者与评审易误判年份错误 | `[46] Keldysh L V. Ionization in the field of a strong electromagnetic wave. Soviet Physics JETP, 1965, 20(5): 1307-1314.（俄文原件 ЖЭТФ 47, 1945, 1964）` | 改为括注单一权威年份，如"（俄文原件：ЖЭТФ 47, 2189 (1964)，英译本 Sov. Phys. JETP 20, 1307 (1965)）"；正文 rationale L5 已写"Keldysh[46] 于 1965 年建立"（英译本口径），二者对齐即可。 |
| R3-06 | low | 研究方案 | scheme L43 | 引用文献能区数值与原文口径不一致：[42] 原文为"200–600 eV"，正文写"覆盖 284–531 eV 水窗能区"——284–531 eV 是本项目自定义的水窗分段口径（C K 边–O K 边），但以 [42] 的措辞直接陈述，读者会误以为该数值出自 Jarecki 原文 | `Jarecki 等[42]于 2024 年以 2.1 μm、10 kHz OPCPA 系统演示水窗软 X 射线衍射，覆盖 284–531 eV 水窗能区。` | 改为"覆盖 200–600 eV、完整贯穿水窗能区"（依原文），或"覆盖 284–531 eV 水窗能区（本项目分段口径）"以明示数值来源为本项目定义而非原文。 |
| R3-07 | low | 立项依据 | rationale L21 | 同段两个关键文献仅以作者名出现、未带编号：Schultze（对应 [4]）与 Klünder（对应 [16]）在该段论证"Ne 2s-2p 与 Ar 3s-3p 同属 XUV 多壳层相对时延谱系"时均未标编号，读者需回溯 L7/L9 自行配对 | `Schultze 等的 Ne 2s-2p 相对延迟测量所用条纹技术，与 Klünder 等的 Ar 3s-3p 相对延迟测量所用干涉度量技术，同属 XUV 能区多壳层相对时延谱系` | 补编号：`Schultze 等[4]的 Ne 2s-2p 相对延迟测量…与 Klünder 等[16]的 Ar 3s-3p 相对延迟测量…`。 |
| R3-08 | low | 参考文献 | refs 条目 [16]（references.md L35） | 元数据不完整：该文存在出版方更正（Erratum: Phys. Rev. Lett. 106, 169904 (2011)），refs 未注明；正文引用其 32–42 eV Ar 3s/3p 时延数据，若更正涉及数值则引证风险 | `[16] Klünder K, Dahlström J M, Gisselbrecht M, et al. Probing single-photon ionization on the attosecond time scale. Physical Review Letters, 2011, 106: 143002.` | 核对 Erratum 内容后，于条目尾补注"（出版方更正：Phys. Rev. Lett. 106, 169904 (2011)）"。证据：https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.106.143002 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 **1**（[40]）/ 超界 0 / 一号两用 0 / 断链 0。预跑脚本结论**复核准确**，且经 full_review 口径与格式变体排查**未发现漏报**（预跑脚本可能漏掉的"漏引/变体/注释行藏引"三类已单独排查，结论为零）。
2. **元数据真实性**：48/48 条经 Crossref + arXiv API + INSPIRE 联网核实，**虚构文献 0 条、元数据错误 0 条、DOI 全部有效**（含 4 条 APS 短式新 DOI）。作者折断格式与 refs 头部自述规则存在**全篇统一偏差**（自述"5 人及以上自第六位起折 et al."，实为"统一折到第 3 位 + et al."，33 条受影响）——因全篇一致、不构成事实错误，未单列意见，建议 M1 一并决定是改条目还是改头部规则声明。
3. **内容匹配性**：抽查 12 条全部匹配，**无"正文声称 vs 文献内容"不符**，关键数值（322 as / 350 eV / 19.2 as / 243 eV / 390 eV / 1.32 fs / 130 eV / 6.9 fs / 2.35 mJ）逐项回原文核对通过。
4. **意见统计**：critical 0 / high 1 / medium 3 / low 4，合计 **8 条**。
5. **需 M1 裁决的关键项**：R3-01（死条目 [40] 的接入或删除——注意删除会牵动 [41]–[48] 全部重编号，是本轮唯一有连锁效应的改动）与 R3-03（检索截止时间口径统一，rationale L13 与 references L103 两处须同改）。
6. **不涉及新增引用**：本报告未建议任何检索池外的新增文献；R3-01 的引用建议已在池内（`02_literature/targeted-research/lit-gap-1790890315.md`）查得记录，R3-07 属既有条目补编号，无池纪律风险。
