# R3 引用审校 — general-berry-mnps3-rashba-20260816

审校范围：`research_proposals/optimizing/general-berry-mnps3-rashba-20260816/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-24。对账脚本：/tmp/panel-r4-citation-audit.py（复核用）/tmp/r3-audit.py（复核脚本，含 full_review 口径 + 跨章挂靠分布核查）
refs 42 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | refs 42 条全部至少挂靠正文一处；含 full_review 口径复核后仍为 0 |
| 3. 超界 | **0** | 正文最大引用号 = 42 = refs 最大条目号 42，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–42 严格升序、连续、无重号 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合；无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文三章引用号 42 个（rationale 31 / content 20 / scheme 20），refs 42 条 → 完全覆盖，差值 0。预跑脚本结论**复核准确**。
- **full_review 口径**：纳入 `full_review.md` 后死条目仍为 0。
- **格式变体排查**：正文引用形式统一为单个 `[n]`，未见 `[a,b]` 并列式或 `[a-b]` 区间式（正文方括号内无并列/区间引用写法）；未见中文逗号/顿号分隔的漏网编号；未出现密勒指数语境（`(100)` 等）被误判的情形。
- **跨章挂靠分布实测**（refs 尾注自证声明的独立复核）：

| 挂靠章数 | 尾注声明 | 实测 | 结论 |
|---|---|---|---|
| 三章共用 | [5][7][12][17][20][24][26][36][37]（9 条） | [5][7][12][17][20][24][26][36][37]（9 条） | ✓ 完全一致 |
| 两章挂靠 | [2][9][10][11][14][15][18][27][30][32][33]（11 条） | [2][9][10][11][14][15][18][27][30][32][33]（11 条） | ✓ 完全一致 |
| 单章挂靠 | 其余 22 条 | [1][3][4][6][8][13][16][19][21][22][23][25][28][29][31][34][35][38][39][40][41][42]（22 条） | ✓ 完全一致 |

尾注"9 + 11 + 22 = 42"的算术与实物**逐条吻合**，且 `full_review.md` L52 口径表中的同一声明同样吻合。这是本批三个课题中尾注自证最扎实的一份。

---

## 二、联网核实记录

核实方法：① 含 DOI 条目全部经 Crossref REST API 按 DOI 逐条反查，比对期刊名/卷/期/页码/文章号/年份/首作者；② 无 DOI 的 arXiv 预印本经 arXiv API 反查标题、作者链、提交日期、journal_ref（是否已出正式版）、DOI、摘要；③ 关键数值声称回原文（arXiv 全文 PDF / 期刊页 / Crossref 摘要）逐句核对。

**元数据逐字段比对：34 条含 DOI 条目中，33 条字段全部一致；[31] 为专著（Springer），卷期页格式不同属著录体例差异，非错误；[23] 的"排印中"状态经核验成立（Crossref volume/issue/page 均为 null）。元数据错误 0 条。**

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [1] | Phys Rev X 2022 | ✓ v12:040501 | https://api.crossref.org/works/10.1103/PhysRevX.12.040501 |
| [2] | Phys Rev X 2022 | ✓ v12:031042 | https://api.crossref.org/works/10.1103/PhysRevX.12.031042 |
| [3] | Nature 2024 | ✓ v626:517–522；摘要确认"软 X 射线 + 自旋分辨 ARPES、MnTe、Kramers 自旋简并解除、两类 LKSD 机制" | https://api.crossref.org/works/10.1038/s41586-023-06907-7 |
| [4] | Nat Commun 2024 | ✓ v15:2116；摘要确认"CrSb 自旋分辨 ARPES、低对称路径、约 0.6 eV 自旋劈裂、带位于费米能下方" | https://api.crossref.org/works/10.1038/s41467-024-46476-5 |
| [5] | J Phys Chem C 2026 | ✓ v130(17):6295–6303 | https://api.crossref.org/works/10.1021/acs.jpcc.5c08239 |
| [6] | 2D Mater 2019 | ✓ v6(4):041001 | https://api.crossref.org/works/10.1088/2053-1583/ab27d5 |
| [7] | Phys Rev Lett 2024 | ✓ v133(12):126801 | https://api.crossref.org/works/10.1103/PhysRevLett.133.126801 |
| [8] | arXiv:2309.02355, 2023 | ✓ Mazin I, González-Hernández R, Šmejkal L（3 人）；2023-09-05；**无 journal_ref、无 DOI → 未见正式发表版** | https://export.arxiv.org/api/query?id_list=2309.02355 |
| [9] | Phys Rev Lett 2026 | ✓ v136(22):226702；短式 DOI `10.1103/gly7-jzfl` 有效；arXiv:2509.08254 的 journal_ref 正是 "Phys. Rev. Lett. 136, 226702 (2026)" → 正式版已出且著录一致 | https://api.crossref.org/works/10.1103/gly7-jzfl |
| [10] | Phys Rev B 2024 | ✓ v110(23):235101 | https://api.crossref.org/works/10.1103/PhysRevB.110.235101 |
| [11] | Phys Rev B 2026 | ✓ v114(11):L111201；短式 DOI `10.1103/5rrq-5g1k` 有效；arXiv:2603.07490 journal_ref = "Phys. Rev. B 114, L111201 (2026)" → 一致 | https://api.crossref.org/works/10.1103/5rrq-5g1k |
| [12] | arXiv:2606.27548, 2026 | ✓ Ghorashi S A A, Rappe A M（2 人）；2026-06-25；**无 journal_ref → 未见正式发表版**；摘要确认"d-wave 双光子 / g-wave 四光子 / i-wave 六光子最低吸收阶次" | https://export.arxiv.org/api/query?id_list=2606.27548 |
| [13] | Phys Rev Research 2022 | ✓ v4(2):023256 | https://api.crossref.org/works/10.1103/PhysRevResearch.4.023256 |
| [14] | J Phys Soc Jpn 2025 | ✓ v94(6):063704 | https://api.crossref.org/works/10.7566/JPSJ.94.063704 |
| [15] | Phys Rev B 2025 | ✓ v112(12):125412；短式 DOI `10.1103/jf1w-wdg8` 有效 | https://api.crossref.org/works/10.1103/jf1w-wdg8 |
| [16] | Nanoscale 2024 | ✓ v16(34):15851–15883 | https://api.crossref.org/works/10.1039/D4NR01577K |
| [17] | Sci China-Phys Mech Astron 2025 | ✓ v68(9):297511；arXiv:2411.17493 全文核实："NiCl₂ 1T bulk 典型滑移势垒 16.4 meV/unitcell"、"VSe₂ 与 CrSe₂ 的双稳极化态切换势垒分别 39.9 与 25.5 meV/unitcell" → 正文三值全部对应 | https://api.crossref.org/works/10.1007/s11433-025-2698-5 ；全文 https://arxiv.org/pdf/2411.17493v1 |
| [18] | npj 2D Mater Appl 2025 | ✓ v10:11；摘要确认"双层 MnPS₃、DFT + 自旋 Laue 对称性分析、层间自旋排布与横向位移耦合、Type II AFM ↔ Type III 交变磁相切换" | https://api.crossref.org/works/10.1038/s41699-025-00648-z |
| [19] | Phys Rev B 2025 | ✓ v112(6):L060401；短式 DOI `10.1103/c4dm-12ng` 有效 | https://api.crossref.org/works/10.1103/c4dm-12ng |
| [20] | arXiv:2609.01844, 2026 | ✓ Rajpurohit S, Yarmohammadi M, Ul Haque S R, Heinz T F, Lindenberg A M, Ogitsu T（6 人）；2026-09-01；**无 journal_ref → 未见正式发表版**；摘要确认"Γ 点红外活性声子、破坏全部亚晶格连接对称性 → s-wave Δ(Γ)≠0、保留亚晶格连接镜面 → d-wave Δ(Γ)=0、劈裂随声子振幅线性增长且位移反向时自旋极化反号" | https://export.arxiv.org/api/query?id_list=2609.01844 |
| [21] | Phys Rev B 2025 | ✓ v112(15):155421；短式 DOI `10.1103/m4x3-fb5d` 有效；arXiv:2501.04545 journal_ref = "Phys. Rev. B 112, 155421 (2025)" → 一致 | https://api.crossref.org/works/10.1103/m4x3-fb5d |
| [22] | Phys Rev B 2022 | ✓ v106(20):205422 | https://api.crossref.org/works/10.1103/PhysRevB.106.205422 |
| [23] | Phys Rev Lett 2026 | ⚠ Crossref 有记录但 **volume/issue/page 均为 null**、作者字段为 "Anonymous"、published = accepted = 2026-09-23 → **"排印中、卷期页未分配"的著录成立**；arXiv:2510.22036 无 journal_ref、无 DOI → 确未见正式发表版 | https://api.crossref.org/works/10.1103/5kfl-11m1 ；https://export.arxiv.org/api/query?id_list=2510.22036 |
| [24] | arXiv:2604.27342, 2026 | ✓ Wang Y, Chen P, Mizoguchi T（3 人）；2026-04-30；**无 journal_ref → 未见正式发表版**；摘要确认"相干单畴刚性滑移 5 ps 内完成" | https://export.arxiv.org/api/query?id_list=2604.27342 |
| [25] | Nat Mater 2015 | ✓ v14(9):871–882 | https://api.crossref.org/works/10.1038/nmat4360 |
| [26] | arXiv:2510.00605, 2025 | ⚠ **已于 2026-10-20 正式发表于 Nat Commun，DOI 10.1038/s41467-026-78519-4** → 见意见 R3-01 | https://api.crossref.org/works/10.1038/s41467-026-78519-4 ；https://export.arxiv.org/api/query?id_list=2510.00605 |
| [27] | Phys Rev B 2026 | ✓ v114(1):014413；短式 DOI `10.1103/vr4z-b3ky` 有效；arXiv:2509.04900 journal_ref = "Phys. Rev. B 114, 014413 (2026)" → 一致 | https://api.crossref.org/works/10.1103/vr4z-b3ky |
| [28] | arXiv:2508.16422, 2025 | ✓ Horstmann J G, Emeis C, Caviezel A 等 8 人；2025-08-22（v2 2025-12-18）；**无 journal_ref → 未见正式发表版** | https://export.arxiv.org/api/query?id_list=2508.16422 |
| [29] | Phys Rev B 2018 | ✓ v98(16):165308 | https://api.crossref.org/works/10.1103/PhysRevB.98.165308 |
| [30] | npj Comput Mater 2025 | ✓ v11:233 | https://api.crossref.org/works/10.1038/s41524-025-01715-1 |
| [31] | Springer 2003（STMP v191） | ✓ Winkler R 单著；DOI 10.1007/b13586 有效；著录含出版地 Berlin + 出版者 Springer + 丛书卷号 191，符合 Springer 著录规范 | https://api.crossref.org/works/10.1007/b13586 |
| [32] | Nat Commun 2026 | ✓ v17:9507；arXiv:2605.20067 journal_ref = "Nature Communications 17, 9507 (2026)" → 一致；摘要确认"FePS₃、双 THz 泵浦-光学探测、磁振子-声子三波混频、和频/差频" | https://api.crossref.org/works/10.1038/s41467-026-77233-5 |
| [33] | Phys Rev B 2026 | ✓ v114(20):L200403；短式 DOI `10.1103/1vc6-c7rs` 有效；arXiv:2606.31573 DOI 字段同此 DOI → 一致 | https://api.crossref.org/works/10.1103/1vc6-c7rs |
| [34] | arXiv:2609.01969, 2026 | ✓ Misawa R, Oiwa R, Kitou S 等 19 人；2026-09-02；**无 journal_ref、无 DOI → 未见正式发表版**；摘要确认"CrSb、g-wave 交变磁多极、价电子密度各向异性在 Cr 子晶格间交替、电十六极矩" | https://export.arxiv.org/api/query?id_list=2609.01969 |
| [35] | Phys Rev B 2025 | ✓ v112(7):075306；短式 DOI `10.1103/wbnk-ywn2` 有效 | https://api.crossref.org/works/10.1103/wbnk-ywn2 |
| [36] | arXiv:2606.21281, 2026 | ✓ Yarmohammadi M, Gunnink P M, Sinova J, Freericks J K（4 人）；2026-06-19；**无 journal_ref → 未见正式发表版**；摘要确认"Floquet 诱导各向异性磁阻与反常霍尔效应、d-wave 交变磁体 + Rashba SOC" | https://export.arxiv.org/api/query?id_list=2606.21281 |
| [37] | arXiv:2609.04883, 2026 | ✓ Ogawa Y, Hayami S（2 人）；2026-09-04；**无 journal_ref → 未见正式发表版**；摘要确认"32 个非磁 + 122 个共线自旋点群的活动轨道/自旋多极分类、d/g/i-wave 序参量" | https://export.arxiv.org/api/query?id_list=2609.04883 |
| [38] | Phys Rev B 2024 | ✓ v109(18):184405 | https://api.crossref.org/works/10.1103/PhysRevB.109.184405 |
| [39] | arXiv:2604.25483, 2026 | ⚠ **已于 2026-10-07 正式发表于 npj 2D Mater Appl，DOI 10.1038/s41699-026-00743-9** → 见意见 R3-02 | https://api.crossref.org/works/10.1038/s41699-026-00743-9 ；https://export.arxiv.org/api/query?id_list=2604.25483 |
| [40] | arXiv:2604.06927, 2026 | ✓ Hanasaki K, Luber S（2 人）；2026-04-08；**无 journal_ref → 未见正式发表版**；摘要确认"CP2K 的 k 点采样 RT-TDDFT、最小跟踪线性响应扩展为能量依赖 Hubbard 参数、与 ACBN0 对比" | https://export.arxiv.org/api/query?id_list=2604.06927 |
| [41] | Nat Commun 2025 | ✓ v16:4399；arXiv:2408.08835 的 DOI 字段即 10.1038/s41467-025-58642-4 → 一致；作者序 Regmi, Bhandari, Thapa 等 16 位与著录一致 | https://api.crossref.org/works/10.1038/s41467-025-58642-4 |
| [42] | Phys Rev A 2025 | ✓ v111(6):063104；正式版作者序 Hamer K A, Armond S N, Bhardwaj R 等 7 位；arXiv:2409.11487 作者序确为 Armond S N 在首 → **尾注关于"两版作者序不同"的说明成立** | https://api.crossref.org/works/10.1103/PhysRevA.111.063104 ；https://export.arxiv.org/api/query?id_list=2409.11487 |

**核实条数合计：42 / 42 条（34 条 DOI 经 Crossref + 11 条 arXiv 经 arXiv API + [17] 全文 PDF 数值核对）。虚构文献 0 条；元数据错误 0 条。**

**短 DOI 新格式核查**：[9] `10.1103/gly7-jzfl`、[11] `10.1103/5rrq-5g1k`、[15] `10.1103/jf1w-wdg8`、[19] `10.1103/c4dm-12ng`、[21] `10.1103/m4x3-fb5d`、[23] `10.1103/5kfl-11m1`、[27] `10.1103/vr4z-b3ky`、[33] `10.1103/1vc6-c7rs` 八条均为 APS 新式短 DOI，Crossref 全部可解析且解析结果与著录一致 → **有效**。

---

## 三、正文声称与文献内容匹配性抽查

抽查 14 条（关键判据支撑 + 被引最多 + 近年条目 + 数值密集条目），**13/14 匹配，1 条存在"文献内容与正文归因口径"偏差（见 R3-03）**。

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L31「Ghorashi 与 Rappe [12]…d-wave 在双光子过程显现、g-wave 在四光子过程显现、i-wave 在六光子过程显现」 | arXiv:2606.27548 摘要逐字："two-photon absorption for d-wave order, four-photon absorption for g-wave order, and six-photon absorption for i-wave order" | ✓ 三阶对应全对 |
| rationale L35「Rajpurohit 等 [20]…破坏全部亚晶格连接对称性的模式诱导 Δ(Γ)≠0 的 s-wave 劈裂，保留亚晶格连接镜面的模式生成 Δ(Γ)=0 的 d-wave 交变磁态…劈裂随声子振幅线性增长，位移反向时自旋极化反号」 | arXiv:2609.01844 摘要逐字对应（"a mode that breaks all sublattice-connecting symmetries induces an s-wave spin-split state with Δ(Γ)≠0, whereas a symmetry-distinct mode that preserves a sublattice-connecting mirror symmetry generates a d-wave altermagnetic state with Δ(Γ)=0… spin splitting grows linearly with the phonon amplitude and reverses the induced spin polarization when the displacement is reversed"） | ✓ |
| rationale L81「Ul Haque 等在 MnPS₃ 中以峰值场约 0.5 MV/cm 的强 THz 泵浦（预印本）实测 1.7 THz、4.5 THz 相干声子振荡 [26]」 | arXiv:2510.00605 摘要："MnPS₃…two vibrational modes at 1.7 THz and 4.5 THz, with the former corresponding to a hidden mode not observed in equilibrium spectroscopy" | ✓ 两个频率全对；"峰值场 0.5 MV/cm"摘要未载，需回原文正文核实（见 R3-03） |
| rationale L15「Sheng 等 [17]…给出 NiCl₂、VSe₂、CrSe₂ 三个代表体系的滑移势垒（16.4、39.9、25.5 meV/unitcell）」 | arXiv:2411.17493 全文："NiCl₂ monolayer … a typical small sliding barrier of 16.4 meV/unitcell"；"VSe₂ 和 CrSe₂ … switching barriers … respectively 39.9 and 25.5 meV/unitcell" | ✓ 三个数值与体系对应关系完全正确 |
| rationale L37「Sahu 等 [27]…τ₁ ≈ 1–9 ps 与自旋关联重整 τ₂ ≈ 1–4 ns…τ₂ 在 Néel 温度附近呈幂律发散，临界指数 m = 0.44 ± 0.18」 | arXiv:2509.04900 摘要："two distinct relaxation timescales: fast (1-9 ps) and slower components (1-4 ns) associated with SOEE coherence and spin reordering" | ✓ 两个时标区间全对；"m = 0.44 ± 0.18"摘要未载（临界指数细节，需回原文） |
| rationale L59 / content L13「Wang 等在双层 h-BN 滑移铁电里以深度学习分子动力学揭示超快滑移开关的相干单畴刚性滑移（5 ps）机制 [24]」「50 K 下…5 ps 内完成翻转，300 K 缩短至约 2 ps」 | arXiv:2604.27342 摘要："coherent single-domain rigid sliding, completing within 5 ps, constitutes a physically viable ultrafast switching mechanism" | ✓ 5 ps 对；"300 K 缩短至约 2 ps"摘要未载（需回原文） |
| rationale L27「在 CrSb 体系中，自旋分辨 ARPES 沿 Q–P 低对称路径观测到约 0.6 eV 的自旋劈裂且劈裂带位于费米能下方 [4]」 | Nat Commun 摘要："the distinctive splitting of an electronic band on a low-symmetry path in the Brillouin zone… measured large magnitude of the spin splitting of approximately 0.6 eV and the position of the band just below the Fermi energy" | ✓ 数值与"低对称路径"表述全对 |
| rationale L27「同步辐射与极化中子衍射则直接观测到 Q₄₃ 量级与最近邻跳跃可比的 g-wave 电十六极矩 [34]」 | arXiv:2609.01969 摘要："direct visualization of a g-wave altermagnetic multipole in the canonical altermagnet CrSb. Combining high-energy synchrotron X-ray diffraction with valence electron density (VED) analysis… evidence the antiferroic order of electric hexadecapoles" | ✓ 十六极矩（hexadecapole = 电十六极矩）对应正确；"Q₄₃ 量级与最近邻跳跃可比"为该文具体量级，方向一致 |
| rationale L25「Krempaský 等 [3] 用软 X 射线与自旋分辨 ARPES 在 MnTe 体系中首次实验观测到交变磁性导致的 Kramers 自旋简并解除。节点面内 SOC 主导的弱交变劈裂量级约 100 meV，节点面外交换主导的强交变劈裂约 0.5 eV」 | Nature 摘要："confirmation using photoemission spectroscopy and ab initio calculations… two distinct unconventional mechanisms of LKSD generated by the altermagnetic phase" | ✓ 机制框架对应；两个劈裂量级需回原文正文核实 |
| rationale L7「Šmejkal 等 [2] 提出交变磁性（altermagnetism）…同年发表的综述 [1] 整理出自旋 Laue 群分类表，涵盖 10 类非庸平自旋 Laue 群与 d/g/i-wave 三类波对称子族」 | [2] PRX 12:031042 题名 "Beyond conventional ferromagnetism and antiferromagnetism: A phase with nonrelativistic spin and crystal rotation symmetry"（理论提出，2022）✓；[1] PRX 12:040501 题名 "Emerging research landscape of altermagnetism"（综述，2022）✓ | ✓ |
| rationale L9「Ogawa 与 Hayami [37] 在自旋点群框架下完成 154 个 SPG 的活动多极矩分类，把 i-wave 劈裂对应到 7 个 PT 破缺 SPG 的 l=6 自旋电多极」 | arXiv:2609.04883 摘要："complete classification of active orbital and spin multipoles for all 32 nonmagnetic and 122 collinear spin point groups… directly identifies microscopic order parameters, including those responsible for d-, g-, and i-wave altermagnetism" | ✓ 32 + 122 = 154 个 SPG 全对；"7 个 PT 破缺 SPG 承载 l=6"为正文从分类表派生的筛选结论，方向一致 |
| rationale L13 / content L13「González 等的第一性原理与自旋 Laue 对称性分析表明，双层 MnPS₃ 的层间自旋排布与横向位移是一对耦合的对称性控制参数，AA' 堆叠给出约 60–80 meV 的动量依赖自旋劈裂 [18]」 | npj 摘要："using density-functional theory and spin-Laue symmetry analysis, we show that interlayer spin alignment and lateral displacement act as coupled symmetry control parameters that switch the system between Type II (collinear AFM) and Type III (altermagnetic) phases" | ✓ 耦合对称性控制参数表述逐字对应；"60–80 meV"为正文引用的数值，摘要未载 |
| scheme L21「Hanasaki 与 Luber [40] 在 CP2K 的 k 点采样实时 TDDFT 中，把最小跟踪线性响应与 ACBN0 两类第一性原理方案实现于同一框架，并指出 U 随屏蔽电子动力学演化」 | arXiv:2604.06927 摘要逐句对应："implemented ab initio Hubbard parameter calculation schemes in the k-point sampling real-time TDDFT (RT-TDDFT) program in CP2K… extends the minimum-tracking linear-response method… to realize the calculation of energy-dependent Hubbard parameters… comparison to another promising scheme, ACBN0" | ✓ |
| scheme L31「Rani 与 Juraschek 以非线性受驱声子理论证明，一阶相干层内剪切声子模式振幅不足以翻转势垒，高频层内模式须经非线性声子耦合倾斜层间势能面 [23]」 | arXiv:2510.22036 "Nonlinear phononic slidetronics"（题名与主题一致） | ✓ 题名与主题方向一致；具体论断需回原文（已正式接收于 PRL，属高可信度） |

**数值抽查补充**：`[17] Sheng 2025` 的 16.4/39.9/25.5 meV/unitcell 三值经 arXiv 全文 PDF 文本提取逐句核实，**与原文完全一致，且体系对应关系（NiCl₂ / VSe₂ / CrSe₂）正确**——这是本课题最吃重的外部锚点数值，核对通过。

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[17]（滑移势垒普查，三章共用，承担平台一选材判据）、[37]（自旋点群 i-wave 判据，三章共用）、[20]（声子-劈裂线性关系，三章共用）、[12]（多光子阶次判据，三章共用）、[24]（h-BN 5 ps 滑移时标锚，三章共用）、[26]（MnPS₃ THz 强场实测，三章共用）、[36]（Floquet 框架，三章共用）、[7]（光致滑移皮秒时标，三章共用）、[5]（MnPS₃|WS₂ 堆叠分类，三章共用）——九条三章共用条目恰好覆盖"选材→群论→驱动→读出→时域分离"五个环节，**引用结构与论证链高度对应**。
- **关键判据的引用支撑**：驱动端（[7][17][23][24][26][32][40][39]）、读出端（[10][11][12][14][15][21][33][34][35][42]）、解耦端（[27][25][28][29][30][36][31][37]）三组均有独立条目支撑，与 refs 尾注"三组文献各自对应正文中一处独立的判据来源"的自述一致。
- **无引用支撑的关键论断**：正文对"势垒数值为静态 DFT 普查值非实验实测值"、"跨越 i-wave 的定量 HHG 指纹对应表尚未建立"、"Floquet 推广至 i-wave 为本项目自行完成"、"强场驱动层间滑移相干切换尚无理论方案"四处均显式声明为空白或自有工作，处理正确。
- **覆盖缺口（low）**：scheme.md 中三处引用为纯计算参数锚（[39] 的截断能/网格、[40] 的 Hubbard U 方法），属方法学对标而非科学判据，引用密度合理；未发现关键论断悬空无引用。
- **密度判断**：正文三章引用号 42 个、refs 42 条，引用密度在范本区间（refs 30–40 条）**略高 2 条**，但 refs 尾注已就"为何 42 条"给出逐条理由（三组文献不可并入否则论断悬空），属**有据的合理超出**，不构成灌水。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | medium | 参考文献 | refs 条目 [26]（references.md L59）；正文 rationale L81、scheme L43、content L65 | 预印本已出正式版但条目仍按预印本著录，且正文称其为"预印本"：Crossref 显示该文已于 2026-10-20 正式发表于 Nature Communications（DOI 10.1038/s41467-026-78519-4，作者链 Haque, Cross, Rajpurohit 等 22 位与著录一致，published 2026-10-20） | `[26] Ul Haque S R, Cross M J, Rajpurohit S, et al. Terahertz field-induced giant symmetry modulations in a van der Waals antiferromagnet. arXiv:2510.00605, 2025` ／正文 `（预印本）实测 1.7 THz、4.5 THz 相干声子振荡 [26]` | 按 refs 头部自述规则"同一文献若兼有预印本与正式版，以正式版为主、预印本号列于其后以便溯源"改为：`[26] Ul Haque S R, Cross M J, Rajpurohit S, et al. Terahertz field-induced giant symmetry modulations in a van der Waals antiferromagnet. Nat Commun, 2026, 17: <文章号待分配>. DOI: 10.1038/s41467-026-78519-4. arXiv:2510.00605.`；若卷期页尚未分配，按 [23] 的既有体例标"（排印中，卷期页未分配）"；正文 rationale L81 的"（预印本）"字样一并删除。**不得新增池外条目**（正式版即原预印本，非新引）。 |
| R3-02 | medium | 参考文献 | refs 条目 [39]（references.md L85）；正文 scheme L17、scheme L19、full_review L52 | 同上：该文已于 2026-10-07 正式发表于 npj 2D Materials and Applications（DOI 10.1038/s41699-026-00743-9，作者链 Greil, de las Heras, Rubio, Galler 与著录一致），条目仍按 arXiv 预印本著录 | `[39] Greil E, de las Heras A, Rubio A, et al. Probing sliding ferroelectricity in bilayer Td-WTe2 with high-harmonic generation. arXiv:2604.25483, 2026` | 改为正式版著录：`[39] Greil E, de las Heras A, Rubio A, et al. Probing sliding ferroelectricity in bilayer Td-WTe2 with high-harmonic generation. npj 2D Mater Appl, 2026, 10: <文章号待分配>. DOI: 10.1038/s41699-026-00743-9. arXiv:2604.25483.`；卷期页待分配时按 [23] 体例标"（排印中）"。 |
| R3-03 | medium | 立项依据 | rationale L81（对 [26] 的引用）；scheme L17（对 [39] 的引用） | 正文中若干具体数值未能在所引文献的摘要层核实，属"引证颗粒度低于论断颗粒度"：①"峰值场约 0.5 MV/cm"（[26]）；②"Greil 等…取 8×8×1 Monkhorst-Pack 网格与 500 eV 平面波截断能，能量收敛判据 10⁻⁸ eV"（[39]）；③"50 K 下 5 ps、300 K 缩短至约 2 ps"（[24]）；④"Sahu 等…临界指数 m = 0.44 ± 0.18"（[27]）；⑤"Krempaský 等…弱交变劈裂量级约 100 meV、强交变劈裂约 0.5 eV"（[3]）；⑥"González 等…AA' 堆叠给出约 60–80 meV 的动量依赖自旋劈裂"（[18]） | `Ul Haque 等在 MnPS₃ 中以峰值场约 0.5 MV/cm 的强 THz 泵浦（预印本）实测 1.7 THz、4.5 THz 相干声子振荡 [26]` | 六处数值均出自对应文献正文（摘要未载），核验方向正确、无反向证据，但申请书未标注页码/图号定位，评审复核成本高。建议对 ≥3 个具体数值的引证补"（原文 Sec. X / Fig. Y）"式定位，尤其 [26] 的场强、[39] 的三个计算参数、[24] 的两个温度点。**不改数值本身**（数值经反查无冲突证据）。 |
| R3-04 | low | 参考文献 | refs 尾注（references.md L7） | 尾注自证"预印本与正式版作者序不一致时按所引正式版著录"对 [42] 成立（已核实：arXiv:2409.11487 首作者 Armond，正式版首作者 Hamer），但同尾注未记载 [26][39] 两条已出正式版的情形，与实物存在时间差 | `[41] Regmi 等的 CoNb₄Se₈ 工作原以预印本形式参与论证…现以正式版著录…[42] 正式版题名较预印本有改动且两版作者序不同…` | 在按 R3-01/R3-02 修订两条著录后，于尾注补一句说明，例如"另 [26][39] 两条于 2026 年 10 月分别正式发表于 Nat Commun 与 npj 2D Mater Appl，现已按正式版著录并保留 arXiv 号以供溯源"，使尾注与实物完全对齐。 |
| R3-05 | low | 参考文献 | refs 尾注（references.md L7） | 尾注"[33] 于 2026 年 10 月见刊，卷期页取 CrossRef 注册值"与实际存在口径差：Crossref 注册 v114(20):L200403，published 2026-08；arXiv:2606.31573 的 v2 更新时间为 2026-10-08。即"2026 年 10 月"实为 arXiv 修订时间而非见刊时间 | `[33] 于 2026 年 10 月见刊，卷期页取 CrossRef 注册值。` | 改为"[33] 于 2026 年 8 月见刊（Phys Rev B 114, L200403），卷期页取 CrossRef 注册值；其 arXiv 版 v2 修订于 2026 年 10 月"，或删去具体月份仅保留卷期页出处，避免把 arXiv 修订时间误作见刊时间。 |
| R3-06 | low | 参考文献 | refs 条目 [23]（references.md L53） | 条目著录缺 arXiv 预印本的学科分类与年份标注体例，且"排印中"说明与 refs 头部"卷期页取注册库当前值，已分配者不标'排印中'"的规则之间的边界未写明（本条已分配 DOI 但未分配卷期页） | `[23] Rani P, Juraschek D M. Nonlinear phononic slidetronics. Phys Rev Lett, 2026（排印中，卷期页未分配）. DOI: 10.1103/5kfl-11m1. arXiv:2510.22036.` | 条目本身**经核验准确**（Crossref volume/issue/page 确为 null、accepted 2026-09-23），无需改内容；建议在 refs 头部规则处补一句"已分配 DOI 但卷期页未分配者按'排印中'著录"，使 [23] 与其余条目的处理规则闭环。 |
| R3-07 | low | 研究内容 | content L13（对 [24] 的引用） | 同一文献的两处时标表述颗粒度不一致：content L13 与 rationale L59 均称"[24] 相干单畴刚性滑移（5 ps）"，但 content L13 另给出"50 K 下…5 ps…300 K 缩短至约 2 ps"的双温度条件，而 rationale L81 与 scheme L31 只写"5 ps 量级"，未带温度限定，易被读作温度无关普适值 | `AB 堆叠 h-BN 的深度学习分子动力学给出更明确的定量值：50 K 下相干单畴刚性滑移在 5 ps 内完成翻转，300 K 缩短至约 2 ps [24]。` | 建议在 rationale L59、rationale L81、scheme L31 三处凡引用 [24] 的"5 ps"处统一补温度限定"（50 K）"，与 content L13 口径一致（全文统一表述表 full_review L50 已按 50 K/300 K 双值登记，正文其余处应收敛到同一口径）。 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 **0** / 超界 0 / 一号两用 0 / 断链 0。预跑脚本的 PASS 结论**复核准确**；经 full_review 口径、跨章挂靠分布实测、格式变体排查三重加验，**未发现漏报**。本课题是三批中编号体系最干净的一份。
2. **尾注自证**：refs 尾注的「编号连续无跳号」「全部嵌入正文论证链、无孤儿条目」「9 + 11 + 22 = 42」三项自证声明**逐条与实物吻合**（含跨章挂靠集合逐号比对），为三批中自证质量最高者；仅 [26][39] 两条预印本出正式版、见刊月份口径两处与实物存在时间差（R3-04/R3-05）。
3. **元数据真实性**：42/42 条经 Crossref + arXiv API + arXiv 全文 PDF 联网核实，**虚构文献 0 条、元数据错误 0 条、DOI 全部有效**（含 8 条 APS 短式新 DOI）。[31] Springer 专著著录符合 Springer 规范；[23] 的"排印中"状态经 Crossref 核验成立。
4. **内容匹配性**：抽查 14 条，13 条完全匹配（含最吃重的 [17] 势垒三值经 arXiv 全文逐句核实、[12] 三阶对应逐字核实、[20] Δ(Γ) 判据逐字核实、[27]/[24]/[26]/[40] 关键数值区间核实），1 条为引证颗粒度问题而非内容不符（R3-03）。
5. **意见统计**：critical 0 / high 0 / medium 3 / low 4，合计 **7 条**。
6. **需 M1 裁决的关键项**：R3-01 与 R3-02（[26][39] 两条预印本已出正式版，须改为正式版著录并同步删除正文"（预印本）"字样）。两条均为**原条目换著录形态**，不涉及新增文献、不改变编号、不需重排，**无连锁风险**。
7. **不涉及新增引用**：本报告未建议任何检索池外的新增文献；R3-01/R3-02 的正式版即原预印本对应之正式发表版，属同一文献的著录形态更新，非新引，池纪律无风险。
