# R3 引用审校 — general-mos2-20260905

审校范围：`research_proposals/optimizing/general-mos2-20260905/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29（第四轮评审团，课题 r4）。对账复核：主代理预跑脚本结论（40/40 全被引）经独立脚本 /tmp/r3-audit.py（含 full_review 口径、区间/并列展开、密勒指数排除）复现。
refs 40 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。
上轮遗留复核点：① [6] Kim 2017 死条目已删（41→40），尾注声明已重写——本轮核对尾注与实物；② [37]（旧编号）Bondy 已换 Eur. Phys. J. D 78, 106 (2024) 刊版（现行编号 [36]）——本轮核对刊版著录与 scheme 正文内联 arXiv 号是否已删。

---

## 一、编号对账（五项）复核

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/空括号 |
| 2. 死条目 | **0** | 正文三章 distinct = 40；并入 full_review 后仍 = 40 = refs 条目数，无零引用条目 |
| 3. 超界 | **0** | 正文最大引用号 = 40 = refs 最大条目号，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–40 严格升序、连续、无重号 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

**复核确认预跑 PASS 结论准确，无漏报。** 脚本盲区人工补查：

- **区间/并列形式**：scheme L37 `[18, 19]`、content L23 `[12, 21]` 等并列式展开后均正确计入 distinct；正文密勒/点群记号（C₃、D₃d 等）与公式括号不产生假引用号。
- **full_review 藏引**：full_review 仅含 2 个引用 token（[39][40]，"平台范本为 [39]…"、"主动稳定构型由 [40] 报告支撑"），均落在正文已引集合内——纳入后五项计数不变。
- **注释行藏引**：refs [22] 条目下挂钩注释含"arXiv:1606.01858 与本条同文"说明（为溯源声明，非并列编号，合规）；正文无 HTML 注释藏编号。
- **上轮遗留核对**：① 死条目 Kim 2017 已彻底清除——现行 [6] 为 Yoshikawa 等 Science 356, 736 (2017) 石墨烯椭圆 HHG，被引于 rationale L31，全表无零引用条目 ✓；② Bondy 刊版——现行 [36] 著录 "Eur. Phys. J. D 78, 106 (2024); doi:10.1140/epjd/s10053-024-00900-z"，scheme §3.4 L75 引用处（"Bondy 等人[36]的三边带 RABBITT 计算…"）**无内联 arXiv 号** ✓，refs 条目亦无双标识并列 ✓。
- **尾注自证 vs 实物**（references.md L84）：尾注称"[2] 在立项依据章首引用，承担…奠基定位；**其余 39 条与正文编号引用一一对应**"——实物为 **40/40 全部编号引用**（[2] 亦在 rationale L7 以"Schubert 等人[2]"编号引用），二分表述与实物不符（见意见 R3-02）；"[22] 另附条目内挂钩注释" ✓ 与实物一致。
- **预印本标注**：5 条纯预印本 [26][27][30][37][39] 以 "arXiv preprint arXiv:XXXX" 著录；正文对 [30]（content §2.3 L59）显式声明"尚未经同行评议"、对 [39] 显式声明"其原文确认 CEP 稳定驱动事实，未报告 mrad 量级的 CEP 稳定度数值"——预印本引用边界声明诚实。scheme L77 "Rainbow RABBITT[37]（arXiv:2606.10272）"的内联编号与条目著录一致。
- **引用密度**：正文编号引用 token 合计 78（rationale 34 / content 16 / scheme 28）+ full_review 2，refs 40 条全部被引，密度合理无灌水。

---

## 二、联网核实记录（限量）

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐字段比对期刊/年/卷/期/页/首作者，APS 短式 DOI 一并验证解析；② arXiv 预印本经 arXiv API 反查标题、作者链、提交/更新日期、`journal_ref`/`<arxiv:doi>` 字段（出现即已出正式版，refs 仍标预印本则记意见）；③ 关键数值声称回 Crossref 摘要字段逐句核对。本轮正核 22 条（16 Crossref + 5 arXiv + 1 复核上轮已验条目），覆盖全部 5 条预印本、8 条 2024–2026 新刊条目、1 条 APS 短式 DOI 与全部关键判据条目。

| 编号 | 著录 | 核实结果 | 证据 URL |
|---|---|---|---|
| [36] | Eur. Phys. J. D 78, 106 (2024) | ✓ **上轮换刊版著录逐字段一致**：Bondy A; del Valle J; Saha S；EPJ D 78(8) 卷期文章号 106、2024 年全对；题名 "R-matrix with time-dependence calculations for **three-sideband RABBITT** in helium" 与"三边带 RABBITT"声称对应 | https://api.crossref.org/works/10.1140/epjd/s10053-024-00900-z |
| [27] | arXiv:2607.19937 (2026)"已接收 PRB 2026-09-28" | ⚠ Patra S; Cocchi C；arXiv v1 2026-07-22、v2 2026-09-29（与接收日衔接一致）；**但 DOI `10.1103/ldws-7yvc` 已于 2026-10-19 正式在线出版：Phys. Rev. B 114(22), 225412**——"已接收"口径滞后（见意见 R3-01） | https://api.crossref.org/works/10.1103/ldws-7yvc |
| [37] | arXiv:2606.10272 (2026) | ✓ Serov V V; Kheifets A S（2 人）；2026-06-09 提交；**无 journal_ref → 预印本著录成立**；摘要确认 "pronounced **intra-sideband phase structure** that remains hidden in conventional spectrally integrated RABBITT"（"相位沿谱宽变化近 π"为正文级数值） | https://export.arxiv.org/api/query?id_list=2606.10272 |
| [39] | arXiv:2508.14774 (2025) | ✓ Jingsong Gao 等 11 人；2025-08-20 提交；**无 journal_ref → 仍为预印本，著录成立**（上轮 attosecond 报告已核 25 as / 50–320 eV；正文"原文未报告 mrad 级 CEP 稳定度"的边界声明与原文状态一致） | https://export.arxiv.org/api/query?id_list=2508.14774 |
| [26] | arXiv:2604.13901 (2026) | ✓ Aday Cárdenas, Rui E. F. Silva, Álvaro Jiménez-Galán（3 人）逐位一致；2026-04-15 提交；**无 journal_ref → 预印本著录成立**；摘要确认 "multiband reduced-density-matrix equations including time-dependent electron-electron interaction within the time-dep[endent GW]"——"含时 GW 自能"声称对应 | https://export.arxiv.org/api/query?id_list=2604.13901 |
| [30] | arXiv:2604.11984 (2026) | ✓ Jessica O. de Almeida, Wilton J. M. Kort-Kamp, Mathias S. Scheurer（3 人）逐位一致；2026-04-13 提交；**无 journal_ref → 预印本著录成立**；题名 "…chiral Bloch states: application to **rhombohedral graphene**" 与"菱面体多层石墨烯缠绕数"声称对应 | https://export.arxiv.org/api/query?id_list=2604.11984 |
| [21] | PRL 135, 166902 (2025) | ✓ **短式 DOI `10.1103/kskc-qlb3` 有效**；Ma C; Huang C; You Y；题名 "Phase Matching of High Harmonic Generation in **Twisted van der Waals Crystals**"（hBN 扭转相位匹配声称对应；10⁻⁵ 效率为正文级） | https://api.crossref.org/works/10.1103/kskc-qlb3 |
| [24] | APL 126, 191101 (2025) | ✓ 题名 "Enhancement of high-harmonic generation from 2D materials by **distributed Bragg reflector**"；**全作者链 Liu X…Lan P, Lu P——末位 Lu Peixiang（陆培祥）在列，"陆培祥团队"归属核实成立** | https://api.crossref.org/works/10.1063/5.0266306 |
| [25] | PNAS 121, e2316775121 (2024) | ✓ Hu S; Chen D; Du L；题名 "Solid-state high harmonic spectroscopy for all-optical band structure probing of **high-pressure** [MoS₂]"——"高压能带探测方法学路线"声称对应 | https://api.crossref.org/works/10.1073/pnas.2316775121 |
| [20] | Nat. Commun. 15, 6228 (2024) | ✓ Chang Lee V; Yue L; Gaarde M；题名 "**Many-body enhancement** of high-harmonic generation in monolayer MoS₂"——"多体激子修正/非单调阶次依赖"声称对应 | https://api.crossref.org/works/10.1038/s41467-024-50534-3 |
| [38] | Nat. Commun. 16, 9825 (2025) | ✓ Kim M; Kim T; Galler A；题名 "**Quantum interference and occupation control** in high harmonic generation from monolayer WS₂"——"微扰共振增强量子干涉 + 谷布居占据控制"声称逐项对应 | https://api.crossref.org/works/10.1038/s41467-025-65725-9 |
| [14] | APL Photonics 8, 086103 (2023) | ✓ Peterka P; Slobodeniuk A; Novotný T；题名/摘要级声称核实见匹配抽查 | https://api.crossref.org/works/10.1063/5.0158995 |
| [16] | Sci. Adv. 12, eadz5621 (2026) | ✓ Nebgen B; Lee V; Spies J；题名 "**Isostructural electronic transition** in MoS₂"——"~15 GPa 电子结构变化"声称框架对应（2026 新条目） | https://api.crossref.org/works/10.1126/sciadv.adz5621 |
| [23] | Ultrafast Sci. 4, 0063 (2024) | ✓ Zhong H; Cai X; Bao C；摘要确认主题为 **TrARPES 用 HHG 光源**（极化选择 + 亚 100 μm 光斑 + MIR 泵浦）——但体裁为实验实现报告非综述（见意见 R3-03） | https://api.crossref.org/works/10.34133/ultrafastscience.0063 |
| [22] | APL 109, 101601 (2016) | ✓ Tan Y; Chen F; Ghosh A；题名 "First principles study and empirical parametrization of **twisted bilayer MoS₂** based on band [unfolding]"——"扭转角—能带映射/带边 50 meV"声称对应；条目内"预印本 arXiv:1606.01858 与本条同文，已刊 APL，仅保留刊版著录"的处理合规 | https://api.crossref.org/works/10.1063/1.4962438 |
| [40] | APL Photonics 10, 080803 (2025) | ✓ Csizmadia T; Gulyás Oldal L; Gilicze B；题名 "Active stabilization for ultralong acquisitions in an **attosecond pump–probe beamline**"——"双干涉仪 XUV-IR ±81 as"声称框架对应（±81 as 为正文级数值） | https://api.crossref.org/works/10.1063/5.0273558 |
| [13] | Nature 610, 290 (2022) | ✓ Freudenstein J; Bartz M; Meierhofer M；卷期页 610(7931):290-295 逐字段一致；题名 "Attosecond clocking of correlations between Bloch electrons" | https://api.crossref.org/works/10.1038/s41586-022-05190-2 |
| [15] | PRR 2, 032015 (2020) | ✓ Ikeda T 单作者；题名 "High-order nonlinear optical response of a **twisted bilayer graphene**"——"扭转双层石墨烯新谐波通道"声称对应 | https://api.crossref.org/works/10.1103/PhysRevResearch.2.032015 |
| [29] | PRB 110, 115415 (2024) | ✓ Mrudul M 单作者；题名 "Dependence of high-harmonic generation in **twisted bilayer graphene** on laser pulse ellipticity"——TBG 椭圆度依赖 AA/AB 声称对应 | https://api.crossref.org/works/10.1103/PhysRevB.110.115415 |
| [35] | PRB 106, 205422 (2022) | ✓ Bae G; Kim Y; Lee J；题名 "Revealing **Berry curvature of the unoccupied band** in high harmonic generation"——"未占据带圆二色推广"声称对应 | https://api.crossref.org/works/10.1103/PhysRevB.106.205422 |
| [31] | PRB 111, 045415 (2025) | ✓ Avetissian H; Matevosyan H; Mkrtchian G；题名 "Berry curvature and shift vector effects at high-order wave mixing in biased bilayer graphene" | https://api.crossref.org/works/10.1103/PhysRevB.111.045415 |

**正核 22 条：虚构文献 0 条；元数据错误 0 条；DOI 全部有效（含短式 `10.1103/kskc-qlb3`）；5 条预印本中 4 条确认未见正式版，1 条（[27] Patra）已出正式版未更新（R3-01）。** 其余 18 条（[1]–[12][17]–[19][24 部分][28][32]–[34] 奠基与标准 DOI 条目）按限量纪律未联网正核，著录经人工目检与知名事实比对未见异常（[8] Vampa PRB 2015、[34] Luu & Wörner NC 2018 等经典已知真实）。

---

## 三、正文声称与文献内容匹配性抽查（8 条重点）

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L9/L45 / content §2.1：「Peterka[14] 单层 MoS₂ 可见脉冲激发 A 激子（兼顾 B 激子）、0.62 eV 中红外驱动 5–10 阶，A 激子近共振产额抑制非单调，解释为双光子吸收引发电子—电子散射、进而动量散射」 | Crossref 摘要："resonant and near-resonant pulses in a pump–probe-like scheme…Due to **ultrafast dephasing caused by electron–electron scattering**, the HHG is suppressed…fast component…a consequence of **momentum scattering at carriers, which are excited by two-photon transition**" | ✓ 机制逐句对应 |
| rationale L15 / scheme §5：「Patra 与 Cocchi[27] 扭转 C₃ 构型下 SHG 极图方位角 φ₀ 刚性锁定为结构扭转角一半、与光子能量无关」 | arXiv:2607.19937 题名 "Symmetry-Based Design Rules for Second-Harmonic Generation in Stacked and Twisted MoS₂ Bilayers"、摘要 "comprehensive symmetry-based framework mapping the structural configuration"（φ₀=θ_tw/2 为正文级结论，框架一致）；刊版已于 2026-10-19 上线（R3-01） | ✓（框架；刊版待更新） |
| scheme §3.4 L75：「Bondy[36] 三边带 RABBITT 计算覆盖 IR 场强 5×10¹¹–12×10¹¹ W/cm²；多数边带相位弱依赖、阈值边带与低阶边带显著依赖」 | 题名 "…calculations for three-sideband RABBITT in helium" 逐字对应；场强区间与依赖分类为正文级 | ✓（题录级） |
| scheme §3.4 L77：「Rainbow RABBITT[37] 从头计算表明单个边带内相位沿谱宽可变化近 π，随 IR 脉宽缩短而增强」 | arXiv:2606.10272 摘要："pronounced intra-sideband phase structure that remains hidden in conventional spectrally integrated RABBITT"+ ab initio TDSE（"近 π"为正文级数值） | ✓ |
| scheme §3.3 L51/L109：「Gao[39] 工业级 CEP 稳定 Yb 激光（级联充气盒 3.7 fs、0.8 mJ、10 kHz）软 X 射线 50–320 eV；原文未报告 mrad 级 CEP 稳定度数值」 | 上轮 attosecond R3 报告已核（25 as、50–320 eV 摘要级）；本轮确认 arXiv:2508.14774 仍无 journal_ref；正文"原文未报告 mrad 级稳定度"的边界声明与原文状态一致 | ✓ 引用边界诚实 |
| rationale L15/L53 / content §2.1：「Ma[21] 扭转相位匹配在 hBN 验证，5 阶效率约 10⁻⁵」 | 题名 "Phase Matching of HHG in Twisted van der Waals Crystals"（hBN/效率为正文级，短 DOI 已验有效） | ✓（题录级） |
| rationale L95 / scheme §3.1：「Liu 等[24]（陆培祥团队）DBR 弱信号增强 + 干法转移—SHG 联合标定流程」 | Crossref 全作者链含末位 Lu P（陆培祥）与 Lan P；题名 DBR 增强二维材料 HHG | ✓ 归属与主题双对应 |
| rationale L9：「脉冲 38 fs、峰值强度最高约 5 TW/cm²，约合 3 GV/m」 | 数值换算不自洽：5 TW/cm² 按高斯场强公式对应 ≈6.1 GV/m；3 GV/m 反推 ≈1.2 TW/cm²——两个数字差约 4 倍（Peterka 摘要不含强度数值，需回原文定夺，见意见 R3-04） | ✗ 换算口径待核（R3-04） |

**8 条抽查：7 条匹配、1 条数值换算不自洽（R3-04）。** 关键数值链（A 激子 1.88 eV / NOPA 1.46–1.91 eV 窗口 / 13 阶 5.04 eV / φ₀=θ/2 / ±81 as 装置基准）除 R3-04 一处外部可回溯。

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[14] Peterka（激子基线之锚，全文约 9 次）、[27] Patra（扭转角—点群映射，约 7 次）、[12] Heide（层间相干累积 I∝N²，约 6 次）、[18][19]（A/B 激子窗口参照）、[24]（陆培祥工艺+DBR，约 5 次）、[10][17][35]（Berry 反演链三代方法）。引用结构与"基线—协同—反演"三方向数据链匹配。
- **关键判据的引用支撑**：α_syn 分母与近共振抑制幅度（[14]，且正文显式声明"其原文未量化上限，本项目按抑制为非协同通道归因的判据"——处理正确）、η(N) 相干累积（[12][21][22]）、点群与 φ₀ 锁定（[27][15][29]）、Ω(k) 反演三代框架（[34][10][17][11][35]）、Δt 装置链（[40][39][13]）、魔角 TBG 对照（[28][29]）均有对应条目。
- **无引用支撑的关键论断**：莫尔周期三数值（1.35/0.61/7.07 nm）、Ω_max 12/18/25–35 a.u.、耦合项 H_int 推导等均显式标注"由本项目 TDDFT/替代模型计算给出"或"详见方法学手册"——自设参数声明纪律良好，不属漏引。
- **覆盖判断**：40 条全部被引、五个主题簇（HHG 方法学四路线 / 激子调控 / 扭转角工程 / 反演与装置基准 / 国内工艺与标定）各有 3–10 条支撑，2024–2026 新文献占 12 条、时效性好。**覆盖充分。**

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | medium | 参考文献 | refs 条目 [27]（references.md L56） | 预印本已出正式版未更新：条目著录 arXiv:2607.19937 并注"已接收 Phys. Rev. B 2026-09-28"，实际该文已于 **2026-10-19 正式在线出版：Phys. Rev. B 114(22), 225412**（doi:10.1103/ldws-7yvc 经 Crossref 解析确认卷期文章号），"已接收"口径滞后 | `[27] S. Patra and C. Cocchi, arXiv preprint arXiv:2607.19937 (2026); 已接收 Phys. Rev. B 2026-09-28, doi:10.1103/ldws-7yvc.` | 更新为刊版著录：`[27] S. Patra and C. Cocchi, Phys. Rev. B 114, 225412 (2026); doi:10.1103/ldws-7yvc.`（正文引用处无需改动；上轮"投稿前终核"清单内 mos2 相关项就此销账） |
| R3-02 | low | 参考文献 | refs 尾注（references.md L84） | 尾注自证二分表述与实物不符："[2] 在立项依据章首引用…**其余 39 条**与正文编号引用一一对应"暗示 [2] 例外，实物为 **40/40 全部编号引用**（[2] 亦在 rationale L7 以"Schubert 等人[2]"编号引用）——系 [6] 死条目删除后重写尾注时保留的过时二分 | `其余 39 条与正文编号引用一一对应，承担论证主链` | 改为"全部 40 条与正文编号引用一一对应；其中 [2] 在立项依据章首承担 HHG 早期实验背景的奠基定位" |
| R3-03 | low | 立项依据/研究方案 | rationale L47/L97；scheme §6 L123 | 文献体裁表述偏差：三处称 Zhong 等[23]"**综述汇总**"HHG-TrARPES 联用实验条件，该文为实验实现报告（摘要 "In this work, **we report the implementation** of high-quality HHG probe source…for TrARPES"），非综述 | `HHG-TrARPES 联用作为时间分辨 HHG 与能带直接对照的实验条件已由 Zhong 等人[23]综述汇总` | 三处"综述汇总"改为"给出/实现"（如"实验条件已由 Zhong 等人[23]实现并汇总"），避免体裁误标 |
| R3-04 | low | 立项依据 | rationale L9 | 引文参数换算不自洽：Peterka 实验"峰值强度最高约 5 TW/cm²，约合 3 GV/m"——5 TW/cm² 按高斯场强换算约 6.1 GV/m，3 GV/m 反推约 1.2 TW/cm²，两数差约 4 倍；摘要无强度数值，须回原文定夺是强度誊写有误还是换算系数有误 | `脉冲 38 fs、峰值强度最高约 5 TW/cm²，约合 3 GV/m` | 回 Peterka APL Photonics 8, 086103 (2023) 原文核对强度口径后二选一修正（改强度或改场强换算），并与 R1 的数值链核查联动 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0——**复核确认预跑 PASS 结论准确**；区间/并列、full_review 藏引、注释行、尾注自证四类易漏情形排查后无漏报（唯一尾注瑕疵为二分表述，R3-02）。
2. **元数据真实性**：联网正核 22 条（16 Crossref + 5 arXiv + 1 跨轮复核），**虚构 0、元数据错误 0、DOI 全有效**（含短式 kskc-qlb3）；上轮换刊版的 Bondy（现 [36]）逐字段验证通过，scheme 正文内联 arXiv 号确认已删。
3. **上轮遗留复核**：① [6] Kim 死条目删除后无残留，现行 40/40 全被引；② 尾注已重写，唯二分表述与实物有轻微出入（R3-02）；③ Bondy 刊版著录与正文引用全部对齐——三项遗留中两项完全销账、一项降级为 low。
4. **内容匹配性**：抽查 8 条，7 条匹配、1 条数值换算不自洽（R3-04）；[39] Gao 的预印本边界声明（"原文未报告 mrad 级 CEP 稳定度"）与原文状态一致，引用纪律良好。
5. **意见统计**：critical 0 / high 0 / medium 1 / low 3，合计 **4 条**。
6. **需 M1 裁决的关键项**：R3-01（[27] 换刊版著录，一条改动即销账）；R3-04（强度/场强口径，建议与 R1 联动回原文核定）。
7. **不涉及新增引用**：本报告未建议任何新增文献；无池纪律风险。
