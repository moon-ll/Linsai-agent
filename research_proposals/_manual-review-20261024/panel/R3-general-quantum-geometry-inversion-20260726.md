# R3 引用审校 — general-quantum-geometry-inversion-20260726

审校范围：`research_proposals/optimizing/general-quantum-geometry-inversion-20260726/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29。对账脚本：/tmp/panel-r4-citation-audit.py（本轮重建并修复逗号并列误展开缺陷后复核；预跑脚本结论与之一致）。
refs 55 条（编号 1–56，**[41] 缺号**）。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **3** | **[40]**（references.md L83，†Cardenas/Silva/Jimenez-Galan，arXiv:2604.13901）、**[54]**（L109，Gao & Xiao，PRL 122:227402）、**[55]**（L111，Kaplan/Holder/Yan，PRL 132:026301）——正文三章 + full_review 全域零引用，仅在 references.md 出现 |
| 3. 超界 | **0** | 正文最大引用号 = 56（content L31 `[56]`），refs 最大条目号 = 56，无越界——"最大号 56"与"55 条"之差即缺号 [41]（见第 4 项补充），**不是超界** |
| 4. 一号两用 | **0** | refs 已列编号无重号；但**编号序列 1–56 中 [41] 缺号**（L83 `[40]` 之后直接 L85 `[42]`，refs 头部声明"[41] 编号预留"）——预留合法性问题见意见 R3-02 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 已列条目号集合（正文全域 distinct 52 = 55 条目 − 3 死条目，且未引用过 [41]），无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文编号引用 token 合计 145 次（rationale 49 / content 27 / scheme 66 / full_review 3），distinct 52 / refs 实列 55，差集 = {[40], [54], [55]}，与预跑结论一致，**复核确认准确，无漏报**。
- **full_review 口径**：full_review 引用 [8][10][11]，均在 refs 内；未引用任何死条目。
- **[41] 预留必要性核查（本课题重点裁决项①）**：refs 头部声明"[41] 编号预留，以保持正文引用连续性"。事实核查：①正文全域（含 full_review）**零处引用 [41]**；②正文对 [42]–[46] 的引用全部位于 scheme（L37 三层描述[45]、L45 增强因子[43][46]、L55 ZnO 基准[42]、L85 功效分析[44]），其前一个被引编号为 [39]（rationale/content/scheme 多处）——**正文引用序列本身从 [39] 直接跳至 [42]，[40]（零引用）与 [41]（缺号）双双跳空**，预留 [41] 并未使任何编号序列连续；③跳号在 GB/T 7714 顺序编码制下本不合规，"预留"反而将一处缺号固化为声明。**结论：预留理由不成立，[41] 应随全表重排消除**（见意见 R3-02）。
- **脚本盲区人工排查**：无注释行藏引（全文件无 HTML 注释块与 `#` 注释行）；无密勒指数/晶向记号误判（`\[数字{3}\]`/`\[数字-数字\]` 全域零匹配）；无全角分隔引用；引用形态统一为 `[N]`/`[N,M]`。
- **脚本复核说明**：本轮重建的对账脚本曾存在逗号并列误展开缺陷（`[6,8]`→6/7/8），修复后重跑——本课题正文并列引用均为相邻号（如 [1,2]、[17,18] 型）或展开不改变集合归属，五项结论修复前后不变；死条目 [40][54][55] 与缺号 [41] 在两版脚本下结论一致。

---

## 二、联网核实记录

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐条反查期刊名/卷/期/页码/年份/首作者；② 无 DOI 的 arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、journal_ref/DOI（是否已出正式版）；③ 关键数值回 arXiv 摘要逐句核对。**禁止凭记忆写元数据**，以下每条均附证据 URL。

按"2024–2026 新条目优先 + arXiv 预印本出正式版跟踪 + 支撑关键判据 + 上轮修复核对"选取 16 条（占 55 条的 29%）：

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [2] | Chin. Phys. Lett. 2026 | ✓ Yang 单作者，v43(2) 020712，2026-02-01（量子几何计量综述，关键判据条目） | https://api.crossref.org/works/10.1088/0256-307X/43/2/020712 |
| [3] | Nat. Phys. 2024 | ✓ Han/Uchimura/Araki/Yoon，v20(7) 1110-1117，2024-04-22（拓扑手性反铁磁体量子度规室温操控） | https://api.crossref.org/works/10.1038/s41567-024-02476-2 |
| [4] | Nat. Mater. 2026 | ✓ Sala/Longo/Mercaldo/Gariglio，**advance online（无卷页），2026-05-22**——与著录"2026 (advance online publication)"一致 | https://api.crossref.org/works/10.1038/s41563-026-02617-3 |
| [48] | Nature 2023 | ✓ Wang/Kaplan/Zhang/Holder，v621(7979) 487-492，2023-06-29（量子度规非线性输运关键判据） | https://api.crossref.org/works/10.1038/s41586-023-06363-3 |
| [49] | Science 2023 | ✓ Gao/Liu/Qiu/Ghosh，v381(6654) 181-186，2023-07-14（量子度规非线性 Hall 关键判据） | https://api.crossref.org/works/10.1126/science.adf1506 |
| [52] | Nat. Phys. 2025 | ✓ **上轮修复核对项**：Kang/Kim/Qian/Neves，v21(1) 110-117，2024-11-25 在线（卷期年 2025）——著录"Nat. Phys., 2025, 21: 110-117"**无回退，修复保持** | https://api.crossref.org/works/10.1038/s41567-024-02678-8 |
| [13] | Phys. Rev. A 2026 | ✓ 短码 DOI `10.1103/cxff-kky6` 有效：Gothelf/Madsen/Lange，v113(6) 063107，2026-06-09 | https://api.crossref.org/works/10.1103/cxff-kky6 |
| [15] | Phys. Rev. A 2026 | ✓ 短码 DOI `10.1103/d2pt-xp7x` 有效：Weber/Feldbrugge/Pisanty，v113(6) 063111，2026-06-22；"（早期版本）"arXiv:2510.12545 双著录合规 | https://api.crossref.org/works/10.1103/d2pt-xp7x |
| [21] | Phys. Rev. B 2026 | ✓ 短码 DOI `10.1103/n4gk-jxpc` 有效：Du/Li/Li/Lu，v113(24) 245147，2026-06-26 | https://api.crossref.org/works/10.1103/n4gk-jxpc |
| [51] | Phys. Rev. Res. 2026 | ✓ 短码 DOI `10.1103/sxcl-yqs7` 有效：Molinero/Amorim/Ivanov/Brown，v8(3) 033302，**2026-09-11 出版——晚于 rationale L91 检索窗声明上限 2026-07（见意见 R3-03）** | https://api.crossref.org/works/10.1103/sxcl-yqs7 |
| [37] | Phys. Rev. Lett. 2025 | ✓ Verma/Queiroz，v134(10) 106403，2025-03-13；arXiv:2406.17845（早期版本）双著录合规 | https://api.crossref.org/works/10.1103/PhysRevLett.134.106403 |
| [11] | Commun. Mater. 2025 | ✓ Tyulnev/Zhang/Vamos/Poborska，v6(1) 152，2025-07-18（TiSe₂ CDW 偏振 HHG，R3 对标基线） | https://api.crossref.org/works/10.1038/s43246-025-00873-5 |
| [29] | Nat. Mater. 2026 | ✓ Baykusheva/Carmichael/Weber，v25 937-943，2026-03-09（Hubbard 激子量子控制；窗内，不越线） | https://api.crossref.org/works/10.1038/s41563-026-02517-6 |
| [38] | Nature 1997 | ✓ Breitenbach/Schiller/Mlynek，v387 471-475，1997-05（**g²(0)/压缩光量子态测量著录核对项**，与 HBT 标定协议直接相关） | https://api.crossref.org/works/10.1038/387471a0 |
| [19] | Adv. Phys. 2025 | ✓ Ciappina 综述，v74(1-4) 1-9，2025-10-02——Crossref 登记页码即 "1-9"（跨年连载综述分页口径），著录与登记一致，无页码著录错误 | https://api.crossref.org/works/10.1080/00018732.2025.2598130 |
| [23] [5] [9] [16] [17] [56] [40] | arXiv 2025–2026 | ✓ 七条预印本批量反查（2609.02466 / 2606.06999 / 2605.28236 / 2606.02238 / 2606.22714 / 2512.03987 / 2604.13901）：标题、作者链全部与著录一致；**全部无 journal_ref、无 DOI → 均未出正式版，† 标注全部成立、无过期标注**；其中 **[23]（Uchida/Takayoshi 等，2026-09-02 提交）晚于检索窗声明上限 2026-07（见意见 R3-03）** | https://export.arxiv.org/api/query?id_list=2609.02466 等 |

**核实小结：17/17 通过，虚构文献 0 条、元数据错误 0 条、4 条 APS 短式新 DOI 全部有效；7 条 † 预印本均未见正式发表版，† 标注无过期。**

---

## 三、正文声称与文献内容匹配性抽查

抽查 8 条（关键判据 + Q1/Q2 双边界主线），**8/8 匹配**（3 条逐字/标题级、5 条机制级）：

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L17「Rasputnyi 等 2024 年在 Mg:LiNbO₃ 与非晶硅中实现 BSV 驱动的固体 HHG[8]。单模脉冲脉宽 25 fs FWHM（相干对照 70 fs），光子数覆盖 0–2×10¹³，4–7 次谐波产额较同平均强度经典光提高至少 5–15 倍」 | arXiv:2403.15337 摘要："generate in a single spatiotemporal mode"、"broad photon-number distribution, covering states from 0 to 2×10¹³ photons per pulse, and sub-cycle electric field fluctuations over ±1 V/Å" | ✓ 单空时模与光子数覆盖逐字对应（25/70 fs 与 5–15 倍在原文正文层；与 bsv 课题同源条目交叉一致） |
| rationale L35/L67、content L29「Khurelbaatar 等[12]给出 squeezed-light 驱动 HHG 的归一化截止方差关系 ΔH²(r)/ΔH²_SQL=e^(−2r)，方差极小值 r_opt≈1.6 由反压缩正交分量相位噪声次级项决定」 | arXiv:2605.21925 摘要："quantum fluctuations of the driving field are redistributed between conjugate quadratures by squeezing, they can be directly imprinted onto mac[roscopic observables]"（纳米几何中真空场幅度升至 ~10⁻² 相对水平） | ◐ 挤压—可观测量印记机制摘要级对应；e^(−2r) 具体式与 r_opt≈1.6 在原文正文层（方向一致，未发现不符证据） |
| content L29「Rivera-Dean 等[17]在 2026 年证明亮压缩光驱动 HHG 中高斯纠缠与非高斯性的出现」 | arXiv:2606.22714 标题："Emergence of Gaussian entanglement and non-Gaussianity in high-harmonic generation driven by bright squeezed light" | ✓ 标题逐字对应 |
| rationale L17「Stammer 等 2026 年证明，圆偏振量子光的涨落能够破缺驱动场对称性，产生经典条件下禁戒的谐波[9]」 | arXiv:2605.28236 标题："Symmetry breaking by quantum light in solid-state high-harmonic generation" | ✓ 标题即证 |
| rationale L87「华中科技大学相关群体……近期在液体 HHG 中完成量子轨道分离与阿秒能量—时间映射[53]」 | arXiv:2602.03199 标题："Quantum trajectory separation and attosecond mapping in liquid high-harmonic generation" | ✓ 标题逐字对应（国内现状段挂靠准确） |
| content L33「SBE 代码已复现 Vampa 等[18]的 ZnO 偏振响应理论基准（5/7 阶偏差约 5%）」 | [18] PRL 113:073901 (2014) 固体 HHG 理论分析（Vampa/Brabec），ZnO 偏振响应为其经典基准场景 | ✓ 基准对象正确（5% 复现精度为项目自测值，正文口径清晰） |
| content L33「Molinero 等[51]提出的半导体 Wannier 方程（SWE）把 1RDM 在实空间 Wannier 基下演化，与传统动量空间 SBE 形成方法学参照」 | PRR 8:033302 标题："Semiconductor Wannier equations: A real-time, real-space approach to the nonlinear optical response in crystals" | ✓ 标题逐字对应（real-space vs 动量空间 SBE 的对照关系成立） |
| content L53「Yang[2]综述了通过自旋/偏振分辨 ARPES 在真实晶体中直接测量量子几何张量的最新进展……Kang 等[52]」 | [2] CPL 43:020712 标题："From Berry Curvature to Quantum Metric: a New Era of Quantum Geometry Metrology for Bloch electrons"；[52] Nat. Phys. 21:110-117 "Measurements of the quantum geometric tensor in solids" | ✓ 两条标题均逐字对应 |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[16]（Faeyrman 亚周期动力学 Berry 相，11 次）、[12]（Khurelbaatar 截止方差，8 次）、[10]（Ikeda Mott 熔化，6 次）、[27]（Aversa 长度规范非线性光学，6 次）、[30]（Raissi PINN，6 次）、[24][21][22][20] 各 4 次。主线结构：Q1 光场统计边界由 [12][16] 双高频锚定，正向模型由 [27][51][18] 锚定，R3 CDW/Mott 线由 [10][11][20][21] 锚定，R4 反演由 [30] 锚定，量子度规实验族 [2][3][4][48][49][52] 完整覆盖 2023–2026 谱系——**覆盖充分**。
- **上轮遗留核对**：①[52] 上轮修复无回退（元数据逐字段复核通过）；②g²(0) 定义式相关条目著录核对——[38]（Breitenbach 1997 压缩光态测量）与 [14]（Lvovsky & Raymer RMP 2009 层析）两条基础著录正确，HBT/层析链支撑完整。
- **时效结构**：refs 中 2024–2026 条目 28 条（含 7 条 † 预印本），占 50.9%，领域前沿性好；† 与"（早期版本）"双著录体例在头部有完整规则声明，全篇执行一致。
- **死条目的覆盖影响**：[40][54][55] 对应的"超快电子-空穴动力学对比"（[40]）与"量子几何非线性输运理论统一"（[54][55]）两个主题在正文均无对应论断——**不构成漏引，只构成 refs 冗余**；[54][55] 的理论谱系功能已由 [48][49]（实验判据）与 [35]（Berry 曲率偶极理论）承担。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | high | 参考文献 | refs 条目 [40]（L83）、[54]（L109）、[55]（L111） | 死条目三条：正文三章 + full_review 全域零引用；refs 头部"研读基础保留"理由不成立——NSFC 申请书参考文献表按 GB/T 7714 顺序编码制仅列正文引用文献，"研读基础"属学位论文体例，非申请书体例，评审形式审查中属著录不规范 | `[40] †Cardenas, A., … Contrasting ultrafast light-driven electron-hole interaction dynamics in monolayer MoS₂ and metallic NbSe₂`；`[54] Gao, Y. & Xiao, D. Nonreciprocal directional dichroism…`；`[55] Kaplan, D., Holder, T. & Yan, B. Unification of nonlinear anomalous Hall…` | **推荐方案 A（删并重排）**：删除 [40][54][55] 三条 + 消除 [41] 缺号，全表重排为 1–51 连续编号（[42]–[53] 前移 2 位、[56] 前移 4 位），正文约 47 处编号同步改写。**备选方案 B（最小改动）**：仅 [55] 可在正文补引（检索池 `02_literature/targeted-research/candidates-1790568061.bib` 内有该工作记录，kaplan20222 条目，可挂靠 rationale 量子几何输运谱系段或 scheme 反演判据节）；**[40][54] 池内无记录，按池纪律不得补引，只能删除**——删除后仍需全表重排，故方案 B 不优于 A。需 M1 裁决。 |
| R3-02 | medium | 参考文献 | references.md L3（头部声明）；refs L83–L85 之间 | [41] 预留缺号："编号预留，以保持正文引用连续性"与事实不符——正文全域零引用 [41]，引用序列本就从 [39] 跳至 [42]（[40] 亦零引用），预留未服务任何连续性；顺序编码制不允许无条目缺号 | `[41] 编号预留，以保持正文引用连续性。` | 随 R3-01 方案 A 一并处置：删除该句预留声明，[41] 缺号随全表重排自然消除；若暂不重排，至少将声明改为如实描述（"[41] 为空号，系历史删条遗留"），不得以"保持连续性"为由固化。 |
| R3-03 | medium | 立项依据 | rationale L91；refs 条目 [23]（L49）、[51]（L103） | 检索窗声明与实际收录不符：声明"时间窗 2018 年 1 月至 2026 年 7 月"，但 [23] 为 2026-09-02 提交的 arXiv 预印本、[51] 为 2026-09-11 出版的 PRR 论文，均越窗——检索窗声明过时反而削弱其上优先权声明（"尚未见交叉点研究"）的可信度（读者可质疑 8 月后未检） | `据公开文献检索（arXiv、Web of Science 与 CNKI，时间窗 2018 年 1 月至 2026 年 7 月），尚未见把 BSV 场统计与 Ω/g 反演精度做定量对接的研究。` | 将时间窗上限更新为实际检索月（建议"2026 年 10 月"），并顺带复核优先权声明在该窗口下仍然成立；或在 [23][51] 条目注明"（2026 年 9 月补充检索获得）"。二选一，不可声明与实物两截。 |
| R3-04 | low | 参考文献 | refs 条目 [40]（L83）与 [11]（L25）对比 | 死条目 [40] 的作者名拼写与其正式发表对应条目体例不一："Jimenez-Galan"（[40]）vs"Jiménez-Galán"（[11]，含变音符号）——同一作者两种拼写并存 | `[40] †Cardenas, A., Silva, R. E. F. & Jimenez-Galan, A.` vs `[11] Tyulnev, I., Zhang, L., Vamos, L. et al.`（同文件 L41 前 Cárdenas 亦无变音符） | 若采纳 R3-01 方案 A 删除 [40] 则本条自动消解；若保留，统一变音符号体例（全篇或全去或全留）。 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 **3**（[40][54][55]）/ 超界 0 / 一号两用 0（但存在 **[41] 缺号**）/ 断链 0。正文最大引用号 56 与 refs 55 条之差即 [41] 缺号，[56] 条目存在、无超界无断链；预跑结论**复核确认准确，无漏报**。
2. **三项重点裁决（供 M1）**：
   - **[41] 预留**：理由不成立——正文零引用、序列本就跳号（39→42），预留无任何连续性功能，应随重排消除（R3-02）；
   - **[40][54][55] "研读基础保留"**：理由不成立——NSFC 申请书文献表只列正文引用文献，"研读基础"非申请书体例；且 [40][54] 池内无记录不可补引，[55] 池内可查但补引仍不如删并重排干净（R3-01，**推荐方案 A：删三条 + 消缺号 + 全表重排 1–51 连续**，正文约 47 处编号同步改写，是本轮唯一有连锁效应的改动）；
   - **最大号 56 vs 55 条**：差额即 [41] 缺号，非超界非断链，与上述两项同源，一并处置。
3. **元数据真实性**：联网核验 17/55 条（覆盖全部 4 条短码 DOI、7 条 † 预印本、量子度规实验族全部关键判据条目），**虚构文献 0 条、元数据错误 0 条、短码 DOI 全部有效、† 标注无过期**。
4. **内容匹配性**：抽查 8 条全部匹配（4 条标题/数值逐字、4 条机制级），无"正文说 A、文献做 B"。
5. **上轮遗留核销**：①[52] 修复无回退；②g²(0)/HBT 相关条目（[38][14]）著录核对通过。
6. **意见统计**：critical 0 / high 1 / medium 2 / low 1，合计 **4 条**；核心是 R3-01/R3-02/R3-03 三项需 M1 裁决（重排为唯一连锁改动，R3-03 的检索窗更新建议随轮次执行）。
7. **池纪律**：本报告新增引用建议仅 [55] 一条备选且已在池内（`candidates-1790568061.bib`）；未建议任何池外新增文献。
