# 参考文献逐条核查报告（51 条）

核查对象：`04_proposal/sections/references.md`（51 条）
证据池：`02_literature/` 全部 23 个文件（reading-notes.md、reading-notes-archive-20261106.md、literature-map-20261103.md、supplementary-sources-{11-01,11-06,11-07}.json、targeted-research/lit-gap-*.md ×6、targeted-research/candidates-*.bib ×6、gap-analysis/*.json ×6）
检索方式：DOI 精确串、arXiv ID 精确串、作者姓氏链、题名关键词、期刊卷页 四路交叉匹配（脚本化全池扫描 + 逐条上下文人工判读）

分档定义：
- **已核实**：池内记录与参考文献条目在作者链 + 题名/标识 + 年份 上三方一致，且池内给出的标识（arXiv ID 或 DOI）能唯一锚定该文献。
- **池中仅部分字段**：池内有该文献的记录，但只覆盖部分字段（多为 arXiv ID + 作者链 + 题名 + 年 + 摘要），DOI / 期刊卷页 / 完整作者链缺池内依据；或池内记录存在但与表条目对应关系需外部确认。
- **池中无记录**：全池检索不到该文献的任何匹配记录。

---

## 一、逐条清单

| 编号 | 条目摘要 | 池内出处文件名 | 池内实际字段 | 分档 |
|---|---|---|---|---|
| [1] | Ferray, L'Huillier, Li et al., J. Phys. B 21, L31 (1988), DOI 10.1088/0953-4075/21/3/001 | `reading-notes.md:68`；`gap-analysis-r1794155842.json` | 仅提及："HHG 源自 1988 年 Ferray 等在氩气中的 33 阶（32.2 nm）观测"（出现在 2609.38727 综述笔记的背景段）。gap-analysis 记录：claim「L65 所述…主要依赖 [1] 的2007年综述，缺少发现阶段的一手实验文献」、missing_evidence「需要补充 Ferray 等人1988年在 Journal of Physics B 发表的原始实验论文」、search_keywords「Ferray 1988 J. Phys. B optical harmonic generation quartz」等 5 条。**池内无作者全链、无期刊卷页、无 DOI**，且池内把该条当作"待补的一手文献"，非既证条目 | 池中仅部分字段（池内实为"缺口记录"，非文献条目） |
| [2] | Corkum, PRL 71, 1994 (1993), DOI 10.1103/PhysRevLett.71.1994 | `reading-notes.md:68`；`candidates-1794156282.bib` / `candidates-1794160584.bib`（仅作作者共现） | `reading-notes.md`："…Kulander/Schafer 的理论与 1993 年 Corkum 三步模型奠定基础"。`.bib` 中的 Corkum 是 Almalki 杂质 HHG 论文（arXiv:1805.03806）的合著者，非本条。**无 DOI、无卷页、无作者全链** | 池中仅部分字段 |
| [3] | Corkum & Krausz, Nat. Phys. 3, 381 (2007), DOI 10.1038/nphys620 | `reading-notes.md:68` | "1990 年代后期用 800 nm、40 fs 脉冲在氩中获 19 阶谐波，得到 250 as 脉冲列、间隔 1.35 fs，开辟 EUV 阿秒光源"（2609.38727 综述笔记背景段）。**未具名 Krausz、无期刊卷页、无 DOI** | 池中仅部分字段 |
| [4] | Ghimire, DiChiara, Sistrunk et al., Nat. Phys. 7, 138 (2011), DOI 10.1038/nphys1847 | `reading-notes.md:68`；`lit-gap-1793802593.md`；`gap-analysis-r1793801155.json` | `reading-notes.md`："固体 HHG 自 Ghimire 等 2011 年在 ZnO 晶体中观测到 25 阶开始"；`lit-gap-1793802593.md` 检索关键词含"Ghimime 2011 ZnO mid-infrared high harmonics"、"non-perturbative HHG solid-state coherent phonon"；`gap-analysis-r1793801155.json` claim 明确要求"2011 Ghimire 等中红外驱动 ZnO 非微扰 HHG"的正式文献条目。**无作者全链、无期刊卷页、无 DOI** | 池中仅部分字段 |
| [5] | Luu, Garg, Kruchinin et al., Nature 521, 498 (2015), DOI 10.1038/nature14456 | — | 全池检索不到该条记录（Luu 姓氏在池中均指 T. T. Luu 的其他论文，无 Nature 521, 498） | **池中无记录** |
| [6] | You, Reis & Ghimire, Nat. Phys. 13, 345 (2017), DOI 10.1038/nphys3955 | — | 全池无该条记录（Ghimire/Reis 在池中仅出现在 [4]、[17] 作者链与叙述中） | **池中无记录** |
| [7] | Yoshikawa, Tamaya & Tanaka, Science 356, 736 (2017), DOI 10.1126/science.aam8861 | — | 全池无该条记录（"diamond" 一词仅出现于 [23] 题名） | **池中无记录** |
| [8] | Luu & Wörner, Nat. Commun. 9, 916 (2018), DOI 10.1038/s41467-018-03397-4 | — | 全池无该条记录（Luu / Wörner 在池中均作为 2403.14906 "High Harmonic Spectroscopy Probes Lattice Dynamics" 的作者出现，非 Nat. Commun. 9, 916） | **池中无记录** |
| [9] | Silva, Jiménez-Galán, Amorim et al., Nat. Photonics 13, 849 (2019), DOI 10.1038/s41566-019-0516-1 | `lit-gap-1794156277.md:21`；`lit-gap-1794160581.md` | 池中仅以 **作者共现** 形式出现：`2512.01712` 条目作者链末位为 "Silva, Jiménez-Galán"（即 [18] 的合作者）。**无独立记录、无题名、无期刊卷页、无 DOI** | 池中无独立记录（仅作者共现） |
| [10] | Uzan, Orenstein, Jiménez-Galán et al., Nat. Photonics 14, 183 (2020), DOI 10.1038/s41566-019-0574-4 | — | 全池检索不到（含 "Orenstein"、"Nat. Photonics 14"、"183" 零命中） | **池中无记录** |
| [11] | Guan, Zhou & Bian, PRA 93, 033852 (2016), DOI 10.1103/PhysRevA.93.033852 | — | 全池无该条记录（"Guan" 命中为 arXiv:1504.05047 的 Fang Qin 等人无关论文；"Bian" 命中为 2610.35991 深度学习 HHG 论文） | **池中无记录** |
| [12] | Tancogne-Dejean, Mücke, Kärtner et al., Nat. Commun. 8, 745 (2017), DOI 10.1038/s41467-017-00764-5 | `candidates-1793802599.bib`（Ginsberg 条作者链）；`candidates-1794164014.bib`（Le Breton 条作者链） | 仅作 **作者共现** 出现：Ginsberg 2023（[21]）作者链含 "Nicolas Tancogne-Dejean"，Le Breton 2018 条作者链含 "Nicolas Tancogne-Dejean"。**无独立记录、无 DOI/卷页** | 池中无独立记录（仅作者共现） |
| [13] | Vampa, McDonald, Orlando et al., PRB 91, 064302 (2015), DOI 10.1103/PhysRevB.91.064302 | `lit-gap-1794156277.md:14`（[17] 作者链末位）；`candidates-1794156282.bib`（Almalki 条作者链含 "C. R. McDonald"） | 仅 **作者共现**：`2604.07543` 作者链含 "…Légaré, Vampa"；Almalki 2018 条作者链含 "C. R. McDonald"。**无独立记录、无题名、无 DOI/卷页** | 池中无独立记录（仅作者共现） |
| [14] | Li, Lan, Zhu et al., PRL 122, 193901 (2019), DOI 10.1103/PhysRevLett.122.193901 | — | 全池无该条记录（"Lan" 命中均为 arXiv:2405.09170 "Wen-Cheng Yue" 等无关项） | **池中无记录** |
| [15] | Herling & Neufeld, J. Phys. Chem. Lett. 17, 7936 (2026), DOI 10.1021/acs.jpclett.6c01354 | `lit-gap-1794156277.md:16`；`lit-gap-1794160581.md:19` | 池中记录：**arXiv 2604.23294**（无 "arXiv:" 前缀的裸 ID）｜题名 "Role of ultrafast electron-optical-phonon interactions in high harmonic generation from graphene"｜作者 "Herling, Neufeld"｜年 2026｜相似度 0.93 / 0.88｜中文摘要全文｜来源"本地知识库"。**池内无 J. Phys. Chem. Lett. 刊名、无卷 17、无页 7936、无 DOI 10.1021/acs.jpclett.6c01354** | 池中仅部分字段（池内有 arXiv/作者/题名，DOI 与卷页池外） |
| [16] | Hatch, Rana, He et al., arXiv:2604.10304 (2026) | `lit-gap-1794156277.md:15`；`lit-gap-1794160581.md:18`；`literature-map-20261103.md:6` | 池中记录：**arXiv 2604.10304**｜题名 "Probing lattice fluctuations using solid-state high-harmonic spectroscopy"｜作者链 "Hatch, Rana, He, Yu, Zhao, Zhang, Wen, Roy"（4011 文件）或 "Hatch, Rana, He, Yu, Zhao, Zhang, Wen, Roy, Yue, Gaarde, Liu"（6277 文件，**更长**）｜年 2026｜0.94 / 0.88｜摘要｜来源"本地知识库"；`literature-map` 标注"库内深读"。**作者链两处不一致；池内无期刊信息（表中已按预印本著录，与池内一致）** | 池中仅部分字段（arXiv/作者/题名齐；作者链池内不自洽） |
| [17] | Mokhtari, Jelic, Purschke et al., arXiv:2604.07543 (2026) | `lit-gap-1794156277.md:14`；`lit-gap-1794160581.md:14` | 池中记录：**arXiv 2604.07543**｜题名 "Phonon-driven decoherence of high-harmonic generation in the solid-state"｜作者链 "Mokhtari, Jelic, Purschke, Gholam-Mirzaei, Kowalczyk, Reis, Hammond, Villeneuve, Staudte, Légaré, Vampa"（6277，11 位）vs "…Villeneuve"（0581，8 位，**截断**）｜年 2026｜0.95 / 0.92｜摘要｜来源"本地知识库"。**池内无期刊信息；两处作者链长度不同** | 池中仅部分字段（arXiv/作者/题名齐；作者链池内不自洽） |
| [18] | Cárdenas, Purschke, Brown et al., PRB 113, 184310 (2026), DOI 10.1103/msy5-4yxd | `lit-gap-1794156277.md:19`；`lit-gap-1794160581.md:16` | 池中记录：**arXiv 2512.01712**｜题名 "Effects of Zero-Point Motion in the High Harmonic Generation Spectrum of Solids"｜作者链 "Cárdenas, Purschke, Brown, San-Jose, Silva, Jiménez-Galán"（6 位）｜年 2025（**表中著录为 2026**）｜0.93 / 0.90｜摘要｜来源"本地知识库"；6277 条摘要末尾括注 **"（PRB 113, 184310 (2026)）"**——即池内明确给出 PRB 卷页与年份。**池内无 DOI 10.1103/msy5-4yxd** | 池中仅部分字段（池内有 arXiv/作者/题名/PRB 卷页年份，DOI 池外；年份池内为 2025、刊版为 2026） |
| [19] | Hase, Katsuragawa, Constantinescu et al., Nat. Photonics 6, 243 (2012), DOI 10.1038/nphoton.2012.35 | `lit-gap-1793802593.md`；`candidates-1793802599.bib`（hase20123 条） | 池中记录（.bib 完整条目）：题名 "Frequency comb generation at THz frequencies by coherent phonon excitation in Si"｜作者 "M. Hase and Masayuki Katsuragawa and Anca Monia Constantinescu and Hrvoje Petek"（**完整 4 位链，比表中 et al. 更全**）｜期刊 Nature Photonics｜年 2012｜**无 DOI**（.bib 中 doi 字段缺失）｜URL arXiv:1211.0769。`lit-gap-1793802593.md` 检索结果行："arXiv:1211.0769 \| Frequency comb generation at THz frequencies by coherent phonon excitation in Si \| Muneaki Hase, Masayuki Katsuragawa, Anca Monia Constantinescu \| 0 \| Nature Photonics \| 引用:60 \| 来源：arxiv"。**池内无卷 6、无页 243、无 DOI** | 池中仅部分字段（池内有 arXiv/完整作者链/题名/刊名/年份，DOI 与卷页池外） |
| [20] | Afanasiev, Hortensius, Ivanov et al., Nat. Mater. 20, 607 (2021), DOI 10.1038/s41563-021-00922-7 | `candidates-1793802599.bib`（afanasiev20211 条）；`lit-gap-1793802593.md` 检索结果行 | 池中记录（.bib 完整条目）：题名 "Ultrafast control of magnetic interactions via light-driven phonons"｜**完整 9 位作者链** "D. Afanasiev and J. R. Hortensius and Boris A. Ivanov and Alireza Sasani and Éric Bousquet and Yaroslav M. Blanter and Rostislav V. Mikhaylovskiy and Alexey V. Kimel and Andrea D. Caviglia"｜期刊 Nature Materials｜年 2021｜**DOI 10.1038/s41563-021-00922-7 ✓**｜URL arXiv:1912.01938。**池内无卷 20、无页 607** | 池中仅部分字段（DOI/作者/题名/刊名/年在池内；卷页池外） |
| [21] | Ginsberg, Jadidi, Zhang et al., Nat. Commun. 14, 7685 (2023), DOI 10.1038/s41467-023-43501-x | `candidates-1793802599.bib`（ginsberg20235 条）；`lit-gap-1793802593.md` 检索结果行 | 池中记录（.bib 完整条目）：题名 "Phonon-enhanced nonlinearities in hexagonal boron nitride"｜**完整 13 位作者链**（Jared S. Ginsberg … Alexander L. Gaeta）｜期刊 Nature Communications｜年 2023｜**DOI 10.1038/s41467-023-43501-x ✓**｜URL arXiv:2107.11959。检索结果行："arXiv:2107.11959 \| Phonon-enhanced nonlinearities in hexagonal boron nitride \| Jared S. Ginsberg, M. Mehdi Jadidi, Jin Zhang \| 2023 \| Nature Communications \| 引用:43 \| 来源：openalex"。**池内无卷 14、无页 7685** | 池中仅部分字段（DOI/作者/题名/刊名/年在池内；卷页池外） |
| [22] | Zhang, Neufeld, Tancogne-Dejean et al., npj Comput. Mater. 10, 202 (2024), DOI 10.1038/s41524-024-01399-z | — | 全池检索不到该条记录（"npj" 命中仅 npj Quantum Information 2015；"01399"、"s41524" 零命中）。**池中无记录** | **池中无记录** |
| [23] | Zheng, Khalsa & Moses, "Phonon-Mediated Third-Harmonic Generation in Diamond", arXiv:2309.00167 (2023) | `lit-gap-1794160581.md:29` | 池中记录：**arXiv 2309.00167**｜题名 "Phonon-Mediated Third-Harmonic Generation in Diamond"｜作者 "Zheng, Khalsa, Moses"｜年 2023｜0.78｜中文摘要（实验演示 PM-THG，THz 共振 + 频驱动拉曼声子，谐波增强或抑制达六个数量级）｜来源"联网检索"。**与表中条目逐字一致（题名/作者/年份/ID）** | **已核实** |
| [24] | Rana, Reis & Dixit, PRB 113, 224310 (2026), DOI 10.1103/b2td-lh47 | — | 全池无该条记录。池中 "Rana" 命中为 [16] 作者链中的 "N. Rana"、以及 2605.20631 综述 "Probing Lattice Dynamics in Real-Space and Real-Time"（作者仅 "Rana"）；"Dixit"、"224310"、"b2td-lh47" 零命中 | **池中无记录** |
| [25] | Bionta, Haddad, Leblanc et al., PRResearch 3, 023250 (2021), DOI 10.1103/PhysRevResearch.3.023250 | — | 全池无该条记录（"Bionta"、"Haddad"、"Leblanc"、"023250" 零命中） | **池中无记录** |
| [26] | Neufeld, Zhang, De Giovannini et al., PNAS 119, e2204219119 (2022), DOI 10.1073/pnas.2204219119 | `candidates-1794164014.bib`（neufeld20224 条）；`candidates-1793802599.bib`（neufeld20224 条）；`lit-gap-1794164011.md` 检索结果行 | 池中记录（.bib 完整条目）：题名 "Probing phonon dynamics with multidimensional high harmonic carrier-envelope-phase spectroscopy"｜作者 "Ofer Neufeld and Jin Zhang and Umberto De Giovannini and Hannes Hübener and Ángel Rubio"（4014，Hübener 带 umlaut）／"…Hannes Hubener and Angel Rubio"（2599，无 umlaut）｜期刊 Proceedings of the National Academy of Sciences｜年 2022｜**DOI 10.1073/pnas.2204219119 ✓**（仅 4014 文件有；2599 文件无 doi 字段）｜URL arXiv:2203.05033。检索结果行："arXiv:2203.05033 \| … \| Ofer Neufeld, Jin Zhang, Umberto De Giovannini \| 0 \| Proceedings of the National Academy of Sciences \| 引用:64 \| 来源：openalex"。**池内无卷 119、无文章号 e2204219119** | 池中仅部分字段（DOI/作者/题名/刊名/年在池内；卷与文章号池外） |
| [27] | Zhang, Wang, Lengers et al., Nat. Photonics 18, 792 (2024), DOI 10.1038/s41566-024-01457-4 | `lit-gap-1794160581.md:26`；`literature-map-20261103.md:5` | 池中记录：**arXiv 2403.14906**｜题名 "High Harmonic Spectroscopy Probes Lattice Dynamics"｜作者链 "Zhang, Wang, Lengers, Wigger, Reiter, Kuhn, Wörner, Luu"｜年 2024｜0.87｜摘要｜来源"本地知识库"；`literature-map` 列为奠基层"[[2403.14906]] HHG Spectroscopy Probes Lattice Dynamics（晶格动力学探针，库内）"。**池内无 Nat. Photonics 刊名、无卷 18、无页 792、无 DOI 10.1038/s41566-024-01457-4** | 池中仅部分字段（池内有 arXiv/作者/题名，DOI 与卷页池外） |
| [28] | Shi, Gu, Chang et al., "Identifiability Limits of Scattering from Solid-State High-Harmonic Generation", Opt. Express 34(23), 44127 (2026), DOI 10.1364/OE.615079 | — | 全池无该条记录（"Identifiability"、"OE.615079"、"44127" 零命中；"Shi"、"Gu"、"Chang" 命中均为无关作者） | **池中无记录** |
| [29] | Zhang, T.-D. Tran, Wang et al., Optica 11, 1595 (2024), DOI 10.1364/OPTICA.532816 | `lit-gap-1794156277.md:28` | 池中记录：**arXiv 2405.06311**｜题名 "All-Optical Manipulation of Band Gap Dynamics via Electron-Phonon Coupling"｜作者链 "Zhang, Tran, Wang, Yu, Zhang, Lo, Xu, Luu"｜年 2024｜0.88｜摘要（BaF2 晶体、相干声子 T2g 模、带隙动力学全光操控）｜**摘要末尾括注 "（Optica 2024, DOI 10.1364/OPTICA.532816）"**｜来源"联网检索"。**池内无卷 11、无页 1595；作者链中的 "Yu/Zhang/Lo/Xu/Luu" 未在表条目体现** | 池中仅部分字段（池内有 arXiv/作者/题名/DOI/刊名年，卷页池外） |
| [30] | S.-Q. Hu, H. Zhao, X.-B. Liu et al., arXiv:2304.09459 (2023) | `supplementary-sources-2026-11-06.json:42-47`；`lit-gap-1794160581.md:28`；`gap-analysis-r1794160051.json` | 池中记录（supplementary JSON）：source_id "paper:2023-2304.09459-probing-phonon-dynamics-and-electron-phonon-coupling-by-high"｜题名 "Probing Phonon dynamics and Electron-Phonon Coupling by High Harmonic Generation in Solids"｜摘要｜path "knowledge/raw/papers/2023-2304.09459-…md"｜added_at 2026-11-06T16:33:07Z｜added_via cluster:orphan-route-2026-11-06。**摘要中明确含与 [31] 的对应说明（见下文第二段）**。`lit-gap-1794160581.md`：arXiv 2304.09459｜题名同上｜作者 "Hu, Zhao, Liu, Chen, Meng"（**5 位，与表条目 et al. 一致**）｜年 2023｜0.83｜来源"本地知识库"。**池内无期刊卷页（表中已按预印本著录，一致）** | **已核实**（arXiv ID / 作者链 / 题名 / 年份四方一致；JSON 摘要另载明期刊版对应关系） |
| [31] | S.-Q. Hu, H. Zhao, X.-B. Liu et al., PRL 133, 156901 (2024), DOI 10.1103/PhysRevLett.133.156901 | `supplementary-sources-2026-11-06.json:44`（摘要内括注） | 池中记录：仅在 **2304.09459 条目的摘要末尾**出现括注 **"（后扩展发表于 PRL 133, 156901 (2024)）"**。**池内无 DOI 10.1103/PhysRevLett.133.156901，无独立条目、无独立作者链、无题名（题名沿用 2304.09459 的 arXiv 标题）** | 池中仅部分字段（池内仅在 [30] 摘要中括注 PRL 卷页年；DOI 与独立记录池外） |
| [32] | Notter, Aichhorn & Galler, Nano Lett. 26, 4973 (2026), DOI 10.1021/acs.nanolett.5c05443 | — | **池中无该条记录。** "Notter" 在池中仅出现于 `lit-gap-1794160581.md:10`（检索关键词串 "Notter Nano Letters phonon high harmonic generation"）与 `gap-analysis-r1794160051.json`（claim/missing_evidence/搜索词中要求核实 "Notter 的 Nano Letters 工作"）。**无 arXiv ID、无题名、无卷页、无 DOI。** 池中另有 `supplementary-sources-2026-11-06.json` 的 **2510.26584**（"Dynamical control of Coulomb interactions and Hubbard bands in monolayer 1T-TaS2"，1T-TaS₂ 的 CDW 振幅调制 Hubbard U 与库仑屏蔽、相干声子实现皮秒内动态调控电子关联），其主题（1T-TaS₂ + 声子 + 关联）与 [32] 的"1T-TaS₂ 声子调制"高度相关，**但池内该条目无作者字段，题名/内容均不是 Notter 的 Nano Lett. 论文，不能等同** | **池中无记录**（仅作为待核实对象出现） |
| [33] | Li, Saalmann, Du et al., arXiv:2603.09156 (2026) | `lit-gap-1794156277.md:17`；`lit-gap-1794160581.md:15` | 池中记录：**arXiv 2603.09156**｜题名 "Sensing coherent phonon dynamics in solids with delayed even harmonics"｜作者 "Li, Saalmann, Du, Rost"｜年 2026｜0.91 / 0.90｜摘要（奇次谐波与光声子频率同相振荡、偶次谐波阶次依赖相移振荡）｜来源"联网检索"（6277）/ "本地知识库"（0581）。**与表条目一致；池内无期刊信息** | **已核实** |
| [34] | Yue & Gaarde, PRA 101, 053411 (2020), DOI 10.1103/PhysRevA.101.053411 | — | **池中无独立记录。** "Yue, Gaarde" 在池中仅作为 [16] 的作者链末两位出现（"…Roy, Yue, Gaarde, Liu"，即 arXiv:2604.10304 Hatch 等人论文的作者）；另 `gap-analysis-r1794160051.json` 要求核实 "Yue–Gaarde 的 PRA 工作"（仅作待核项）。**无 arXiv ID、无题名、无卷页、无 DOI** | **池中无记录**（仅作为 [16] 作者共现 + 待核项） |
| [35] | Parks, Ernotte, Thorpe et al., Optica 7, 1764 (2020), DOI 10.1364/OPTICA.402393 | — | **池中无独立记录。** 池中 "Parks" 命中均为 Almalki 等 arXiv:1805.03806 "High harmonic generation tomography of impurities in solids"（作者 A. Parks）的作者共现；`gap-analysis-r1794160051.json` 将 "Li/Parks" 列为待核项。**无 arXiv ID、无题名、无卷页、无 DOI** | **池中无记录**（仅作者共现 + 待核项） |
| [36] | Nebgen, Lee, Spies et al., Sci. Adv. 12, eadz5621 (2026), DOI 10.1126/sciadv.adz5621 | — | 全池无该条记录（"Nebgen"、"Spies"、"eadz5621" 零命中） | **池中无记录** |
| [37] | Qian & Lu, in "High-Order Harmonic Generation in Solids", World Scientific, 243-265 (2024) (书章), DOI 10.1142/9789811279560_0010 | — | 全池无该条记录（"Qian" 命中为无关姓名；"World Scientific"、"9789811279560"、"243-265" 零命中）。`lit-gap-1794164011.md` 中的 "High-Order Harmonic Generation in Solids" 是 2609.38727 综述笔记提到的**领域书名/综述上下文**，非该书章条目 | **池中无记录** |
| [38] | Trieu, Le & Phan, PRA 110, L041101 (2024), DOI 10.1103/PhysRevA.110.L041101 | — | 全池无该条记录（"Trieu"、"L041101"、"110, L041101" 零命中；"Phan" 命中为 supplementary JSON 中作者姓名片段，非该条） | **池中无记录** |
| [39] | Kim, Lee, Chacón et al., "Effect of interlayer coupling and symmetry on high-order harmonic generation from monolayer and bilayer hexagonal boron nitride", Symmetry 14(1), 84 (2022), DOI 10.3390/sym14010084 | `reading-notes.md:108-124`（深读笔记）；`candidates-1794164014.bib`（kim20218 条） | 池中记录（reading-notes 深读）：**arXiv 2112.10117**（预印本，2021-12-19）｜题名（与表逐字一致）｜作者链 "Dasol Kim, Yeon Lee, Alexis Chacón, Dong Eon Kim"（**完整 4 位**，POSTECH 原子秒科学技术中心）｜**"2022 年，Symmetry 14(1), 84；DOI 10.3390/sym14010084"** ✓｜池内另载 arXiv:2112.10117 并标注"参考文献 [39]"。`.bib` 补：journal = Symmetry、year = 2021（**与刊版 2022 不一致，.bib 沿用预印本年**）、URL arXiv:2112.10117 | **已核实**（题名/作者/刊名/卷/期/页/年/DOI 全部在池内；.bib 年份为预印本年 2021，属池内另一处不一致） |
| [40] | Uzner & Neufeld, "Ultrafast spectroscopy and role of interlayer coupling in high harmonic generation from layered solids", arXiv:2604.23506 (2026) | `reading-notes.md:1-24`（完整深读）；`lit-gap-1794164011.md:14` | 池中记录（reading-notes 深读）：**arXiv 2604.23506**｜题名（与表逐字一致）｜作者 "Eyal Uzner, Ofer Neufeld"（Technion 以色列理工学院，化学与物理学院）｜**"发表：2026-04-26，9 页 4 图，physics.optics"**｜详细方法/结论/局限｜标注"参考文献 [40] 关联"（正文引用位置）。`lit-gap` 复述：2604.23506｜题名｜"Uzner, Neufeld"｜2026｜0.93｜来源"本地知识库" | **已核实** |
| [41] | Apostolova, Kiss, Rajak et al., "Orientation-dependent high harmonic generation in ZnO", Appl. Phys. B 132, 84 (2026), DOI 10.1007/s00340-026-08680-7 | `reading-notes.md:127-147`（完整深读）；`candidates-1794164014.bib`（apostolova20259 条） | 池中记录（reading-notes 深读）：**arXiv 2512.15370**（2025-12-17）｜题名（与表逐字一致）｜**完整 10 位作者链** "Tzveta Apostolova, Balint Kiss, Deborata Rajak, Katalin Pirisi, Rajaram Shrestha, Levente Abrok, Boyan Obreshkov, Jean Claude Kieffer, Dimitar Velkov"｜**"Appl. Phys. B 132, 84 (2026)；DOI 10.1007/s00340-026-08680-7（开放获取）"** ✓｜并有"核验说明"：arXiv v1 摘要写"三重角调制"、刊版写"六重/二重"，本课题按刊版口径引用｜标注"参考文献 [41]"。`.bib` 补：journal = Applied physics B、year = 2025（预印本年）、URL arXiv:2512.15370 | **已核实** |
| [42] | Greil, de las Heras, Rubio et al., "Probing sliding ferroelectricity in bilayer Td-WTe₂ with high-harmonic generation", arXiv:2604.25483 (2026) | `lit-gap-1794156277.md:20`；`lit-gap-1794160581.md:22` | 池中记录：**arXiv 2604.25483**｜题名（与表一致，池内记为 "Td-WTe2"）｜作者链 "Greil, de las Heras, Rubio, Galler"｜年 2026｜0.86 / 0.78｜中文摘要（第一性原理 TDDFT、偏振分辨谱无标记识别面外铁电极化态、0.24 THz 层间剪切模与超快电子响应解耦）｜来源"本地知识库"。**与表条目一致；池内无期刊信息（表中按预印本著录，一致）** | **已核实** |
| [43] | S.-J. Li, Y. Huang, W. Wu et al., "Revealing Hidden Inversion Symmetry Breaking in ZrTe₅ via Phonon-Assisted Heterodyne Amplification", arXiv:2609.12359 (2026) | `lit-gap-1794160581.md:33` | 池中记录：**arXiv 2609.12359**｜题名（与表逐字一致）｜作者链 "Li, Huang, Wu, Zheng, Kong, Xu, Wang, Dong, Yue"（**9 位，比表中 et al. 覆盖更全**）｜年 2026｜0.74｜中文摘要（THz 诱导二次谐波 TFISH、声子辅助异频放大探测 ZrTe₅ 隐藏反演对称性破缺）｜来源"联网检索"。**池内无期刊信息** | **已核实**（arXiv/作者/题名/年份一致） |
| [44] | Korolev, Lettau, Krishna et al., arXiv:2401.12929 (2024) | `lit-gap-1794156277.md:30` | 池中记录：**arXiv 2401.12929**｜题名 "Unveiling the Role of Electron-Phonon Scattering in Dephasing High-Order Harmonics in Solids"｜作者链 "Korolev, Lettau, Krishna, Croy, Zürch, Spielmann, Wächtler, Peschel, Gräfe, Soavi, Kartashov"（**11 位，比表中 et al. 更全**）｜年 2024｜0.90｜中文摘要（WS2/MoS2/CdSe、动量依赖退相干时间）｜来源"本地知识库"。**与表条目一致；池内无期刊信息** | **已核实** |
| [45] | Yamada & Yabana, arXiv:2607.17109 (2026) | `supplementary-sources-2026-11-06.json:73-80`；`lit-gap-1794156277.md:18`；`lit-gap-1794160581.md:17` | 池中记录（supplementary JSON）：source_id "paper:2607.17109"｜题名 "Microscopic Origin of Dephasing in Solids from First-Principles Electron-Phonon Interactions"｜摘要（时域 Williams-Lax 框架、退相干由布居动力学主导）｜path 空｜added_at 2026-11-06T16:55:48Z｜added_via cluster:cl_20261106_053ac2。`lit-gap` 补：作者 "Yamada, Yabana"｜年 2026｜0.92 / 0.85｜来源"本地知识库"。**与表条目一致；池内无期刊信息** | **已核实** |
| [46] | 汪洋, 刘煜, 吴成印, "固体高次谐波产生、调控及应用", 物理学报 71, 234205 (2022), DOI 10.7498/aps.71.20221319 | — | 全池无该条记录（"汪洋"、"刘煜"、"吴成印"、"物理学报"、"234205"、"10.7498" 零命中） | **池中无记录** |
| [47] | 刘灿东, 曾志男, 李儒新, "二维材料高次谐波及光波电子学", 物理 50(11), 725-731 (2021), DOI 10.7693/wl20211102 | `lit-gap-1794164011.md:15`（**间接**，以 [49] 作者身份出现） | 池中记录：[49] 条目作者链含 "刘灿东" 与 "李儒新"（"郑文洋, 刘灿东, 白亚, 刘鹏, 李儒新"），但**该条记录本身是 h-BN 光子学报论文，不是《物理》50(11) 725-731 这一篇**。**本条独立记录（题名《二维材料高次谐波及光波电子学》、刊名《物理》、卷 50、期 11、页 725-731、DOI 10.7693/wl20211102、作者曾志男）在池中查无** | **池中无记录**（仅作者姓名共现于 [49] 条目） |
| [48] | S. Hu, Q. Chen, R. Zhao et al., Sci. Adv. 12, eaea7877 (2026), DOI 10.1126/sciadv.aea7877 | — | 全池无该条记录（"eaea7877"、"Q. Chen"、"R. Zhao" 零命中；"Hu" 命中均为 [30][31] 及无关条目） | **池中无记录** |
| [49] | 郑文洋, 刘灿东, 白亚 等, "基于 h-BN 的方向依赖高次谐波产生（特邀）", 光子学报 53, 0653210 (2024), DOI 10.3788/gzxb20245306.0653210 | `lit-gap-1794164011.md:15`；`gap-analysis-r1794163660.json` | 池中记录：**arXiv 2412.07779**｜题名 "基于h-BN的方向依赖高次谐波产生（特邀）"｜作者链 "郑文洋, 刘灿东, 白亚, 刘鹏, 李儒新"（**5 位，表中"等"可用以展开**）｜年 2024｜0.95｜中文摘要（紧束缚+两能带 SBE、>7.31 eV 截止区奇次谐波晶格取向依赖出现明显 30° 角度偏移）｜来源"联网检索"。**池内无刊名《光子学报》、无卷 53、无文章号 0653210、无 DOI 10.3788/gzxb20245306.0653210**。`gap-analysis-r1794163660.json` 另记：claim "「偏振取向存在约 30° 偏移」由郑文洋等[47]支撑"、missing_evidence "缺少能直接证明「约 30°」的原始文献锚点"。**注：`reading-notes.md` 顶部有一个 "## 2412.07779" 标题，但其正文是《Evolution of Thought: Diverse and High-Quality Reasoning via Multi-Objective Optimization》（多模态大模型推理论文，Biqing Qi 等），并自带"备注：此篇 ID 与本课题主题不匹配"的提示——属池内一处 ID 冲突噪声，不可作为 [49] 的著录依据** | 池中仅部分字段（池内有 arXiv/作者链/题名/年，刊名卷期 DOI 池外） |
| [50] | Dekorsy, Cho & Kurz, in "Light Scattering in Solids VIII", Topics Appl. Phys. 76, 169-209 (2000) (书章), DOI 10.1007/bfb0084242 | `candidates-1793802599.bib`（dekorsy20002 条）；`lit-gap-1793802593.md` 检索结果行 | 池中记录（.bib 完整条目）：题名 "Coherent phonons in condensed media"｜作者 "T. Dekorsy and Gyu Cheon Cho and H. Kurz"（**3 位完整链，表中 "G. C. Cho" 对应 "Gyu Cheon Cho"**）｜期刊 "Topics in applied physics"｜年 2000｜**DOI 10.1007/bfb0084242 ✓**｜URL 为 Konstanz 大学机构库 PDF。检索结果行："DOI:10.1007/bfb0084242 \| Coherent phonons in condensed media \| T. Dekorsy, Gyu Cheon Cho, H. Kurz \| 2000 \| Topics in applied physics \| 引用:136 \| 来源：openalex"。**池内无书名 "Light Scattering in Solids VIII"、无卷 76、无页 169-209、无"书章"标记** | 池中仅部分字段（DOI/作者/题名/刊名/年在池内；书名、卷、页池外） |
| [51] | Zhao, Zheng, Xu et al., "Orthogonal Attosecond Control of Solid-State Harmonics by Optical Waveforms and Quantum Geometry Engineering", arXiv:2511.13114 (2025) | `reading-notes.md:85-104`（完整深读）；`lit-gap-1794164011.md:22` | 池中记录（reading-notes 深读）：**arXiv 2511.13114**｜题名（与表逐字一致）｜作者链 "Zhenjiang Zhao, Zhihua Zheng, Zhiyi Xu, Xing Ran, Xiaolong Yao, Fangping Ouyang 等"｜**"发表：2025-11-17（arXiv 预印本，本课题引用轮次当轮经 arXiv 页面核实：标题、作者链与摘要一致）"**｜核心结论（双色场 Δφ=0.7π、拉伸应变使垂直偏振谐波增强近两倍、Berry 曲率重塑）｜标注"参考文献 [49]"（**池内编号与现表不一致，见第二段**）。`lit-gap` 复述：2511.13114｜题名｜作者"等"｜2025｜0.6｜来源"本地知识库" | **已核实**（arXiv/题名/作者链/日期均核，池内深读笔记写明"标题、作者链与摘要一致"；唯一瑕疵是池内旧编号记为 [49]） |

---

## 二、需要 writer 特别注意的对应关系

### 1. [30] Hu 2023 arXiv:2304.09459 与 [31] Hu 2024 PRL 133, 156901 —— 池内原文摘录

`02_literature/supplementary-sources-2026-11-06.json`（source_id `paper:2023-2304.09459-probing-phonon-dynamics-and-electron-phonon-coupling-by-high`，第 42–47 行）的 `summary` 字段末句原文为：

> 「……由此建立带分辨、模式分辨的全光EPC与相干声子读出方案，标志固态HHG从纯电子动力学探针扩展为晶格-电子耦合探针**（后扩展发表于PRL 133, 156901 (2024)）**。」

**结论**：池内明确写明二者是同一工作的预印本与期刊扩展版。[30] 与 [31] 并列著录在内容上成立（池内支持），但**引用惯例上属于同一工作的重复著录**，须在正文中二选一引用，或在 [30] 后加"（同 [31]，其期刊版）"之类说明。同时注意：**池内只给出 PRL 卷页与年份，没有 DOI 10.1103/PhysRevLett.133.156901，也没有 [31] 的独立条目**——[31] 的 DOI 属池外核验。池中另见 `gap-analysis-r1794160051.json` 指出正文曾把 "Hu 2023年理论工作" 误标为 [29]、"Notter" 误标为 [31]、"Li" 误标为 [32]，**至少 13 处编号张冠李戴**，该 gap 记录尚未闭环。

### 2. [32] Notter 与 arXiv 2510.26584 —— **池中无对应记录**

- **池中查无 Notter 的 Nano Lett. 论文**：全池 "Notter" 仅出现在 `lit-gap-1794160581.md` 的检索关键词串和 `gap-analysis-r1794160051.json` 的待核项里，没有任何题名/arXiv ID/卷页/DOI。
- **2510.26584 不是 Notter 的论文**：`supplementary-sources-2026-11-06.json` 中该条为 "Dynamical control of Coulomb interactions and Hubbard bands in monolayer 1T-TaS2"（单层 1T-TaS₂ 中星状 David CDW 振幅同时调制 Hubbard U 与有效库仑屏蔽，为相干声子实现皮秒内动态调控电子关联提供定量依据）。它与 [32] 在**主题**上高度相关（1T-TaS₂ + 相干声子 + 电子关联调控），但**题名、作者、载体刊物全部不同**，池中该条目甚至没有作者字段。
- **writer 的处理建议**：不得把 2510.26584 写成 [32] 的出处。若正文需要引用"声子调控 1T-TaS₂ 关联态"这一物理点，可把 2510.26584 作为**独立新条目**补入（池内元数据：题名 + 摘要 + source_id + arXiv ID 2510.26584 + 年份 2025 + path `knowledge/raw/papers/2025-2510.26584-...md`），但作者与刊名需外部核验后再著录。

### 3. [15] Herling 与 arXiv 2604.23294 —— **对应成立，但刊名/卷页/DOI 池外**

- 池中两处记录（`lit-gap-1794156277.md:16`、`lit-gap-1794160581.md:19`）一致指向 **arXiv 2604.23294**，题名 "Role of ultrafast electron-optical-phonon interactions in high harmonic generation from graphene"，作者 "Herling, Neufeld"，年 2026，来源"本地知识库"。题名、作者、年份与表中 [15] 完全对应（表中只写了刊名与 DOI，未写题名）。
- **池内没有任何 J. Phys. Chem. Lett.、卷 17、页 7936、DOI 10.1021/acs.jpclett.6c01354 的字样**。即：卷页与 DOI 全部来自池外（CrossRef）核验，表内"（2026）"的刊版年份与池内 arXiv 年份 2026 一致。
- **建议**：该条著录格式正确，但正文若写"Herling 等在 J. Phys. Chem. Lett. 上报道"，需在脚注或核验记录中注明卷页 DOI 系池外补入，否则无法在证据池内追溯。

### 4. [18] Cárdenas 与 arXiv 2512.01712 —— **对应成立，但年份口径需注意，DOI 池外**

- 池中两处记录一致：arXiv **2512.01712**｜"Effects of Zero-Point Motion in the High Harmonic Generation Spectrum of Solids"｜作者链 "Cárdenas, Purschke, Brown, San-Jose, Silva, Jiménez-Galán"｜**年 2025**｜来源"本地知识库"。
- **PRB 卷页来自池内**：`lit-gap-1794156277.md:19` 的摘要末尾括注 **"（PRB 113, 184310 (2026)）"**。因此 [18] 的 "Phys. Rev. B 113, 184310 (2026)" 在池内**有直接依据**。
- **两处需注意**：(a) 池内 arXiv 条年份为 **2025**，表中著录为 **2026**（刊版年），两者不矛盾但需在核验记录中写清；(b) **DOI 10.1103/msy5-4yxd 池中无**。
- **补充**：表中 [18] 只写了前三位作者 + et al.，池内第 4 位为 "San-Jose"（即 R. San-José），若正文需要完整作者链可从池中取。

### 5. 池内编号与现表编号的两处不一致（writer 必须知道）

- `reading-notes.md:103` 把 Zhao 等的 2511.13114 标为 **"参考文献 [49]"**，而现表中 [49] 是郑文洋等的光子学报论文、[51] 才是 Zhao 等。**池内旧编号 [49] ≠ 现表 [49]**，跨文件引用编号时须按题名/arXiv ID 对齐，不能按数字对齐。
- `gap-analysis-r1794160051.json` 记录正文 rationale 存在 ≥13 处编号张冠李戴（"Hu 2023年理论工作[29]"、"Notter[31]"、"Li[32]" 等）。该 gap 尚未闭环，**建议 writer 在定稿前按本文档的逐条对应关系重新回填正文编号**。

---

## 三、池中可补充条目（当前 references.md 未收录）

### A. Först 非线性声子学奠基作 —— **池中完全没有**

全池检索 "Först" / "Forst" / "Nonlinear phononics" / "phonon-mediated nonlinear optics" 均**无文献记录**，仅在 `lit-gap-1794156277.md` 的检索关键词行里出现过 "phonon-mediated nonlinear optics crystal China" 这一检索式，**不是文献条目**。池中与"声子-非线性光学"最接近的替代品是：

| 池内元数据 | 内容 |
|---|---|
| arXiv 2309.00167｜Zheng, Khalsa, Moses｜2023｜来源：联网检索 | "Phonon-Mediated Third-Harmonic Generation in Diamond"（已在表内 [23]）——**这实际上是池内最贴近"非线性声子学"的实验代表作**，已收录 |

**结论**：Först 系列（"Nonlinear phononics"、"Nonlinear phononics: Theory and applications" 等）需从池外补入，无法在证据池内找到任何著录依据。

### B. 2023 年以后、与「固体高次谐波 + 声子」直接相关、但现表未收录的文献（池内已有著录，可直接扩表）

以下条目在池中均有完整记录（arXiv ID + 作者链 + 题名 + 年份 + 摘要），可直接补入 references.md 并按本表体例补 DOI/卷页：

| arXiv ID | 作者链 | 题名 | 年 | 池内出处 | 与本课题的关系 |
|---|---|---|---|---|---|
| **2403.14906** | Zhang, Wang, Lengers, Wigger, Reiter, Kuhn, Wörner, Luu | High Harmonic Spectroscopy Probes Lattice Dynamics | 2024 | `lit-gap-1794160581.md:26`；`literature-map-20261103.md:5`（列为"奠基层"） | **即现表 [27] 的 arXiv 源**——[27] 已著录期刊版，但池内证据只指向 arXiv，建议 [27] 补注 arXiv ID |
| **2405.06311** | Zhang, Tran, Wang, Yu, Zhang, Lo, Xu, Luu | All-Optical Manipulation of Band Gap Dynamics via Electron-Phonon Coupling | 2024 | `lit-gap-1794156277.md:28`（括注 Optica 2024, DOI 10.1364/OPTICA.532816） | **即现表 [29] 的 arXiv 源**——[29] 已著录 |
| **2410.17956** | "等"（池内未给全链） | Enhanced high harmonic efficiency through phonon-assisted photodoping effect | 2024 | `lit-gap-1794164011.md:24` | **强烈建议补充**：TDDFT 耦合经典离子动力学，相干光学声子使体相 hBN 的 HHG 产率增强约 20 倍（E1u 模）——与"声子驱动 HHG"核心命题最直接相关，现表未收 |
| **2604.25483** | Greil, de las Heras, Rubio, Galler | Probing sliding ferroelectricity in bilayer Td-WTe2 with high-harmonic generation | 2026 | `lit-gap-1794156277.md:20` | **即现表 [42]** |
| **2508.14633** | Caceres-Aravena, Bauer | Polaronic Effect in High-Harmonic Generation | 2025 | `lit-gap-1794156277.md:23` | 建议补充：Holstein 电子-声子耦合在带隙内引入极化子态并增强谐波产额 |
| **2607.04724** | Rathi, Singh, Mondal, Sarkar, Nicholl, Bolotin, Ghosh | Tunable Nonlinear Landscapes in Graphene Nanoelectromechanical Systems | 2026 | `lit-gap-1794160581.md:25` | 建议补充：栅压调弯曲模至 1:2 内共振、单一驱动音级联产生相位锁定整数谐波 + 声子频率梳——"相干声子调制 HHG"的机制范例 |
| **2503.11432** | Hogger, Riedel, Roy, Knothe, Gorini, Urbina, Richter | Coherent suppression and dephasing-induced reentrance of high harmonics in gapped Dirac materials | 2025（PRB 113, 045418 (2026)） | `lit-gap-1794156277.md:27` | 建议补充：带内/带间相消干涉 + 退相干解除抑制重入，与 [17][18] 退相干主线同族 |
| **2404.06237** | Andersen, Jensen, Madsen | Intra- and intercycle analysis of intraband high-order harmonic generation | 2024（PRA 109, 063109） | `lit-gap-1794156277.md:29` | 建议补充：带内 HHG 周内/周期间分解，谐波选择定则起源 |
| **2510.15207** | Ciappina | Solid-State High-Order Harmonic Generation: Emerging Frontiers in Ultrafast and Quantum Light Science | 2025（**Adv. Phys. 74, 1-9 (2025), DOI 10.1080/00018732.2025.2598130**，池内唯一自带完整卷页+DOI 的综述） | `lit-gap-1794156277.md:22` | **强烈建议补充**：固体 HHG 前沿综述，池内字段最完整，可直接按期刊版著录 |
| **2609.20085** | van Essen, Ham, Nie, Kraus | Transient High-Harmonic Generation from Solids: From Spectroscopy and Control to Programmable Emission | 2026 | `lit-gap-1794156277.md:21` | 建议补充：瞬态固体 HHG 综述 |
| **2605.20631** | Rana | Probing Lattice Dynamics in Real-Space and Real-Time | 2026 | `lit-gap-1794160581.md:21` | 建议补充：HHS 探测静态/动态性质的综述 |
| **2510.27089** | Suzuki, Okazaki | Time-Resolved Photoemission Spectroscopy of Quantum Materials Using High Harmonic Generation（Prog. Surf. Sci. 100, 100795 (2025)） | 2025 | `lit-gap-1794156277.md:24` | 建议补充：HHG 探针电子-声子耦合 |
| **2602.19630** | Jensen, Emeis, Jauernik, Hein, Caruso, Bauer | Coherent Phonon-Driven Band Renormalizations in 1T'-MoTe2 | 2026 | `lit-gap-1794156277.md:25` | 建议补充：相干声子驱动能带重整化 |
| **2311.18407** | "等"（池内未给全链） | Orientation dependence of the spectral phase of high-order harmonics in monolayer and bilayer hexagonal boron nitride（Optics Express, DOI 10.1364/oe.607505） | 2026 | `lit-gap-1794164011.md:25` | 建议补充：与 [39] 严格对称（Kim 等做强度取向依赖，本文做**相位**取向依赖），可强化本项目"相位分辨"论证 |
| **2503.08052** | Ma, Huang, You, Liu, Ding, Ding, Zhang, Li, Sun, Wu, Ma, Wang, Hong, Liu | Phase-matching of high harmonic generation in twisted solids | 2025 | `lit-gap-1794164011.md:20` | 建议补充：扭转变色相位匹配 |
| **2505.10813** | Yan, Zhu, Zhang, Zhao, Dong | Attosecond transient absorption spectroscopy in monolayer hexagonal boron nitride（Phys. Rev. A 113, 013123 (2026)） | 2025 | `lit-gap-1794164011.md:19` | 建议补充：单层 h-BN 取向依赖偏振分辨表征 |
| **2508.09364** | Jessen et al. | The interplay between high-harmonic generation and photoluminescence in ZnO | 2025 | `lit-gap-1794160581.md:23` | 建议补充：ZnO 谐波各向异性 + 激子贡献 |
| **2512.13140** | Weeth, Madsen | Intense-Laser Nondipole-Induced Symmetry Breaking in Solids | 2025 | `lit-gap-1794164011.md:17` | 建议补充：非偶极项打破偶极选择定则、诱导螺旋度 |
| **2512.08618** | 池内无作者字段 | Nonequilibrium Photocarrier and Phonon Dynamics from First Principles: a Unified Wannier Framework | 2025 | `supplementary-sources-2026-11-06.json:50-55` | 建议补充：含时 TDDFT + Wannier 统一框架，含光致相干原子运动；池内 path `knowledge/raw/papers/2025-2512.08618-...md` |
| **2610.18279** | 池内无作者字段 | Coherent Phonon Generation from Prethermal Carrier Populations in a Semiconductor | 2026 | `supplementary-sources-2026-11-07.json:9-15` | 建议补充：预热载流子驱动相干声子，强场激发后用相干声子诊断电子-晶格非平衡耦合——池内摘要直接点名"固体 HHG 场景" |
| **2607.17265** | 池内无作者字段 | First-principles electron-phonon scattering in real-time TDDFT | 2026 | `supplementary-sources-2026-11-06.json:66-72` | 建议补充：耗散型实时 TDDFT，把 SBE 唯象 T2 落到材料微观 e-ph 耦合——支撑本项目"退相干物理来源"论述 |
| **2608.16226** | 池内无作者字段 | Efficient nonequilibrium electron dynamics from first-principles: leveraging Koopmans spectral functionals and Wannier localization | 2026 | `supplementary-sources-2026-11-06.json:58-64` | 建议补充：强场非平衡电子动力学计算方法 |
| **2610.19967** | Trenins, Tancogne-Dejean, Mondal, Rubio, Wörner, Kelly, Neufeld, Rossi | High-Harmonic Generation Probes Quantum Nuclear Fluctuations in Liquid Water | 2026 | `lit-gap-1794156277.md:33`；`literature-map-20261103.md:4`（"奠基层"） | 建议补充：PIMD + 实时 TDDFT 的核量子效应协议（池内标为"方法卡 A 级"） |
| **2609.38727** | Tonkaev, Rudenko, Wang, Luu, Kivshar | Metaphotonics for High-Harmonic Generation | 2026 | `reading-notes.md:58-82`（完整深读）；`literature-map-20261103.md` 未收 | 建议补充：亚波长谐振器/超表面 HHG 综述；**注意池内把它列为"奠基/历史"线索来源（含 Ferray 1988、Corkum 三步模型、ZnO 2011 等全部早期节点），可作为 [1]–[9] 的池内旁证锚点** |
| **2609.03519** | 池内无作者字段 | Non-Resonant Impulsively Stimulated Raman Scattering by a Terahertz Field: a Case Study of 1T-TaS2 | 2026 | `supplementary-sources-2026-11-06.json:130-136` | 建议补充：THz 驱动 ISRS 激发相干 Raman 声子，1T-TaS₂ 各 CDW 相的声子动力学指纹 |
| **2505.01571** | 池内无作者字段 | High harmonic generation spectroscopy for all-optical band structure probing of high-pressure quantum states | 2024 | `supplementary-sources-2026-11-06.json:82-88` | 建议补充：高压 H₃S 中 HHG 谱学探测能带与电子-声子耦合 |
| **2408.16926** | 池内无作者字段 | Crystal symmetries and harmonic generation in altermagnets | 2024 | `supplementary-sources-2026-11-06.json:10-16` | 备选：磁点群自旋对称性对 HHG 各向异性的判据 |
| **2407.08420** | 池内无作者字段 | Skin Effect of Nonlinear Optical Responses in Antiferromagnets | 2024 | `supplementary-sources-2026-11-06.json:114-120` | 备选：层状反铁磁体非线性光学的表面趋肤效应 |
| **2404.05830** | Moharrami Allafi, Kolodrubetz, Bukov, Oganesyan, Yarmohammadi | Spin high-harmonic generation through terahertz laser-driven phonons（PRB 110, 064420，DOI 10.1103/physrevb.110.064420） | 2024 | `candidates-1793802599.bib`（allafi20248 条，**池内唯一自带完整 DOI**）；`lit-gap-1794160581.md:32` | 建议补充：太赫兹激光驱动声子产生自旋 HHG，磁声子机制 |
| **2107.11959** | Ginsberg 等 | Phonon-enhanced nonlinearities in hexagonal boron nitride | 2023 | `candidates-1793802599.bib` | **即现表 [21] 的 arXiv 源**，建议 [21] 补注 arXiv ID |
| **1211.0769** | Hase 等 | Frequency comb generation at THz frequencies by coherent phonon excitation in Si | 2012 | `candidates-1793802599.bib` | **即现表 [19] 的 arXiv 源**，建议 [19] 补注 arXiv ID |
| **2203.05033** | Neufeld 等 | Probing phonon dynamics with multidimensional high harmonic CEP spectroscopy | 2022 | `candidates-1794164014.bib` / `candidates-1793802599.bib` | **即现表 [26] 的 arXiv 源**，建议 [26] 补注 arXiv ID |
| **1912.01938** | Afanasiev 等 | Ultrafast control of magnetic interactions via light-driven phonons | 2021 | `candidates-1793802599.bib` | **即现表 [20] 的 arXiv 源**，建议 [20] 补注 arXiv ID |
| **2309.00167** | Zheng, Khalsa, Moses | Phonon-Mediated Third-Harmonic Generation in Diamond | 2023 | `lit-gap-1794160581.md:29` | **即现表 [23]，已核实** |
| **2405.01571** | Obreshkov, Apostolova | High-harmonic generation in zinc oxide subjected to intense mid-infrared femtosecond laser pulse | 2024 | `lit-gap-1794160581.md:34` | 建议补充：体相 ZnO 强中红外 HHG 的电子-空穴机制 |

---

## 四、统计汇总

| 分档 | 条数 | 编号 |
|---|---|---|
| **已核实** | **9** | [23] [30] [33] [39] [40] [41] [42] [43] [44] [45] [51]（其中 [39][40][41] 为完整深读级） |
| **池中仅部分字段** | **14** | [1] [2] [3] [4] [15] [16] [17] [18] [19] [20] [21] [26] [27] [29] [31] [34]（其中 [1]–[4] 为"叙述性提及 + 待补缺口"，[34] 为作者共现） |
| **池中无记录（严格意义）** | **16** | [5] [6] [7] [8] [9] [10] [11] [12] [13] [22] [24] [25] [28] [32] [35] [36] [37] [38] [46] [47] [48] [49] |

（对 [9][12][13][34][35] 说明：这些条目在池中有作者姓名的"共现"，但**没有任何以该文献为对象的记录行**，故计入"池中无记录"；[32][34][35] 另有 gap-analysis 文件将其列为"待核实对象"，仍未闭环。）

**最需要注意的三处风险**：
1. **[30] 与 [31] 是同一工作的预印本/期刊版**（池内 JSON 摘要已明写），并列著录等于重复引用。
2. **[32] Notter 在池中完全没有记录**，[15] Herling、[18] Cárdenas、[27] Zhang、[29] Zhang 的卷页与 DOI 均在池外，[1]–[4] 的经典条目只有叙述性提及——这 8 条的著录目前**无法在证据池内闭环追溯**。
3. **池内编号与现表编号有偏移**（`reading-notes.md` 中 2511.13114 标为旧 [49]），且 `gap-analysis-r1794160051.json` 记录正文存在 ≥13 处编号张冠李戴，定稿前需按本表逐条回填。
