# R3 引用审校 — general-ssh-weyl-20260920

审校范围：`research_proposals/optimizing/general-ssh-weyl-20260920/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29（第四轮评审团；本文件在同轮 10-28 稿基础上复核重写，补入 [16]/[26] 基准角色互斥与 [9] 体裁表述两项新发现）。对账复核：主代理预跑脚本（/tmp/panel-r4-citation-audit.py，本机不可达）结论经独立脚本 /tmp/r3-audit.py（含 full_review 口径、区间/并列展开、密勒指数排除）复现。
refs 40 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。
上轮遗留复核点：[20] 预印本 v1/v2 口径颠倒已修，本轮复核无复发；full_review 曾有 v1/v2 标记 6 处（已补丁），本轮核对现行骨架无残留标记。

---

## 一、编号对账（五项）复核

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/空括号 |
| 2. 死条目 | **0** | 正文三章 distinct = 40；并入 full_review 后仍 = 40 = refs 条目数，无零引用条目 |
| 3. 超界 | **0** | 正文最大引用号 = 40 = refs 最大条目号 40，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–40 严格升序、连续（复核脚本确认），每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

**复核确认预跑 PASS 结论准确，无漏报。** 脚本盲区人工补查：

- **区间/并列形式**：rationale 存在 `[31-34]`（区间）、`[2, 22]`、`[3, 4]`、`[9, 10]`（并列），scheme/full_review 存在 `[21, 30]`。展开后 31–34、21、30 均计入 distinct（合并 40/40），与 refs 头部自证"[31]–[34] 四条气相奠基文献在立项依据第 1 节以区间形式引用"（rationale L5 实物）一致。
- **full_review 藏引**：full_review 含 20 个引用 token / 12 distinct（[9][13][14][16][18][20][21][23][25][26][30][15]），全部落在正文三章已引集合内——纳入后五项计数不变。
- **注释行藏引**：refs 头部说明行（L3）出现的 `[7][8][12]…`、`[31]–[34]`、`[35][36]` 均为清单式自证而非条目行，不产生幻影条目；正文无 HTML 注释/行尾注释藏编号。
- **refs 头部自证 vs 实物**（references.md L3）逐项核对："1–40 连续无跳号" ✓；"预印本 9 条为 [7][8][12][13][15][17][18][20][37]" ✓（逐条清点纯 arXiv 无 DOI 条目恰为这 9 条）；"仅带 DOI 者 20 条" ✓；"DOI 与 arXiv 双挂 11 条" ✓（[11][14][16][19][22][23][24][26][29][30][40]）；"[4] 为已刊工作" ✓；9+20+11=40 总数自洽。**尾注自证与实物完全一致。**
- **预印本属性标注**：头部声明"预印本 9 条正文引用处均标注预印本属性"——grep 全量核查 9 条预印本每处正文引用（rationale L19/23/29/31/33/37/43/45/55、content L13/15/25/35/37/73、scheme L11/53/63/87/103/173/205/225/231/233），全部带"（预印本）"字样，无漏标、无回退。
- **引用密度**：正文编号引用 token 合计 147（rationale 51 / content 36 / scheme 60）+ full_review 20，refs 40 条全部被引，无灌水模式（[16] 被引最多约 17 次均为不同支撑点）。

---

## 二、联网核实记录（限量）

核实方法：① arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、v1/v2 日期、`<arxiv:doi>`/`<arxiv:journal_ref>` 字段（出现即已出正式版，refs 仍标预印本则记意见）；② DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐字段比对期刊/年/卷/期/页/首作者。本轮联网正核 19 条：9 条 2024–2026 预印本全查 + 10 条 DOI（含 3 条 APS 短式新格式 DOI、4 条 2025–2026 新刊条目、关键判据 [9] 与 [1]）。

| 编号 | 著录 | 核实结果 | 证据 URL |
|---|---|---|---|
| [7] | arXiv:2604.21121 (2026) | ✓ Sufyan & Neufeld（2 人）；2026-04-22 提交（v2 2026-10-11 更新）；**无 DOI/journal_ref → 未见正式版，预印本标注成立** | https://export.arxiv.org/api/query?id_list=2604.21121 |
| [8] | arXiv:2604.06051 (2026) | ✓ S. Li 等 12 人（Sha Li, Wenyi Zhou, Kazi A. Imroz, Yaguo Tang, Tiana A. Townsend, Vyacheslav Leshchenko, Larissa Boie, Pierre Agostini…）与 refs 全列逐位一致；2026-04-07 提交；**无 journal_ref → 预印本标注成立** | https://export.arxiv.org/api/query?id_list=2604.06051 |
| [12] | arXiv:2608.22136 (2026) | ✓ Chi-Ting Liu, J-S You, Hsiu-Chuan Hsu（3 人）；2026-08-22 提交；**无 journal_ref → 预印本标注成立** | https://export.arxiv.org/api/query?id_list=2608.22136 |
| [13] | arXiv:2602.16454 (2026) | ✓ **Christian Saugbjerg Lange**、Lars Bojer Madsen（2 人，全名经 arXiv 确认）；2026-02-18 提交；**无 journal_ref → 预印本标注成立**；首名与正文称谓口径见意见 R3-03 | https://export.arxiv.org/api/query?id_list=2602.16454 |
| [15] | arXiv:2405.16125 (2024) | ✓ X. Zhang, J. van den Brink, J. Li（3 人）；2024-05-25 提交，至今 **无 DOI/journal_ref → 预印本标注成立**（两年未刊出属实） | https://export.arxiv.org/api/query?id_list=2405.16125 |
| [17] | arXiv:2603.05346 (2026) | ✓ Alba de las Heras, Ofer Neufeld, Angel Rubio（3 人）；2026-03-05 提交；**无 journal_ref → 预印本标注成立** | https://export.arxiv.org/api/query?id_list=2603.05346 |
| [18] | arXiv:2609.06119 (2026) | ✓ Roshan Kumar Thakur, Prachi Venkat, Amar Bharti, Gopal Dixit（4 人）；2026-09-05 提交；**无 journal_ref → 预印本标注成立** | https://export.arxiv.org/api/query?id_list=2609.06119 |
| [20] | arXiv:2508.15631 (2025) | ✓ **上轮 v1/v2 口径问题未复发**：Bryan Lorenzo 等 10 人与 refs 全列一致；v1 2025-08-21、**v2 2026-05-24 与 refs"第二版，2026-05-24"精确一致**；**无 DOI/journal_ref → 预印本标注成立**；v2 摘要原文"reaching up to two orders of magnitude relative to trivial phases"逐字吻合（见匹配抽查） | https://export.arxiv.org/api/query?id_list=2508.15631 |
| [37] | arXiv:2606.02238 (2026) | ✓ Lior Faeyrman, Jianing Zhang, Misha Ivanov, Liang-You Peng（彭良友）, Nirit Dudovich, Riccardo Piccoli（6 人）与 refs 逐位一致；2026-06-01 提交；**无 journal_ref → 预印本标注成立** | https://export.arxiv.org/api/query?id_list=2606.02238 |
| [19] | PR Applied 24, L021001 (2025) | ✓ **短式 DOI `10.1103/3xs5-km1v` 有效**；Rana N 一作，期刊/卷(期)/文章号/年份全对 | https://api.crossref.org/works/10.1103/3xs5-km1v |
| [30] | PRB 112, 214311 (2025) | ✓ **短式 DOI `10.1103/b56l-hvgn` 有效**；Jessen S 一作；全对 | https://api.crossref.org/works/10.1103/b56l-hvgn |
| [38] | PRL 137, 116905 (2026) | ✓ **短式 DOI `10.1103/cpfx-c9h9` 有效**；Bai Y 一作；全对 | https://api.crossref.org/works/10.1103/cpfx-c9h9 |
| [16] | Nano Lett. 25, 16637–16642 (2025) | ✓ Pilch P; Zhu C; Kovalev S 一作链；期刊/年/卷(期)/页码逐字段一致（arXiv:2508.16166 摘要级核实另见匹配抽查） | https://api.crossref.org/works/10.1021/acs.nanolett.5c04143 |
| [26] | Nano Lett. 26, 10554–10560 (2026) | ✓ Duan S; Shi L; Pilch P 一作链；2026 年 26 卷 10554–10560 逐字段一致 | https://api.crossref.org/works/10.1021/acs.nanolett.6c03104 |
| [22] | Adv. Phys. 74, 1–9 (2025) | ✓ DOI `10.1080/00018732.2025.2598130` 有效；Adv. Phys. 74 卷 1–9 页、2025 年、Ciappina 单作者逐字段一致（该刊以文章号计页，著录合规） | https://api.crossref.org/works/10.1080/00018732.2025.2598130 |
| [29] | Comput. Mater. Sci. 268, 114641 (2026) | ✓ Fan Q; Lai K; Liu W 一作链；期刊/年/卷/文章号全对 | https://api.crossref.org/works/10.1016/j.commatsci.2026.114641 |
| [11] | PRB 111, 014308 (2025) | ✓ Pooyan S; Bauer D；全对 | https://api.crossref.org/works/10.1103/PhysRevB.111.014308 |
| [27] | PRB 111, 184314 (2025) | ✓ Liu X; Geng L; Kong X; Zhang J; Fang Y; **Peng L（彭良友，末位通讯）**——rationale L53"北京大学物理学院彭良友团队"归属核实成立；全对 | https://api.crossref.org/works/10.1103/PhysRevB.111.184314 |
| [9] | PRL 120, 177401 (2018) | ✓ D. Bauer & K. K. Hansen（Bauer 一作）；期刊/卷/年/文章号全对；注意该文为模型理论工作（见意见 R3-02） | https://api.crossref.org/works/10.1103/PhysRevLett.120.177401 |

**正核 19 条：虚构文献 0 条；元数据错误 0 条；DOI 全部有效（含 3 条 APS 短式新格式）；9 条预印本全部经 `journal_ref`/`<arxiv:doi>` 字段确认未见正式发表版，预印本标注无一失实。** 其余 21 条（[1]–[6][10][21][23]–[25][28][31]–[36][39][40]，2011–2026 标准长式 DOI 条目与 SSH/Haldane/气相奠基经典）按限量纪律未联网正核，著录经人工目检与知名事实比对未见异常（[1] Ghimire 2011 已顺手经 Crossref 抽验一致）。

---

## 三、正文声称与文献内容匹配性抽查（8 条重点）

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| rationale L31 / content §2.2 L13、L37 / scheme §2.2 L63 / full_review L24：「Kagome 拓扑相峰值增强两个数量级（预印本第二版摘要口径，原文 reaching up to two orders of magnitude）；首版二至三个数量级，第二版收敛」 | arXiv:2508.15631 **v2 摘要原文**："we identify significant enhancements of the harmonic intensity yields, **reaching up to two orders of magnitude** relative to trivial phases"；v2 更新 2026-05-24 | ✓ 逐字对应；五处（rationale/content/scheme/full_review/refs）口径完全统一，**上轮 v1/v2 颠倒修复后未复发** |
| rationale L41 / content §2.4 / scheme §3.1.2、§3.2.2：「Pilch[16] TaP THz 三次谐波严格立方功率律 $I_{3f}\propto I_f^{3}$；线偏振最强、随椭圆度单调衰减至圆偏振为零；Boltzmann 输运归因；峰值场强数十 kV/cm」 | arXiv:2508.16166（同工作预印本）摘要："**perturbative cubic power-law dependence** on the terahertz drive"、"varying the polarization of the drive pulse from linear to elliptical"、"Boltzmann transport theory…field-driven kinetics of the Weyl fermions"、"peak field strength of down to **tens of kV/cm**"；期刊版题录经 Crossref 本轮复核一致 | ✓ 四项声称全部对应（弱场窗 0.3–1 THz/数十 kV/cm 与实验窗口对齐成立） |
| rationale L47 / content §2.4 L37：「Duan[26] Cd₃As₂ 微腔：裸膜幂指数约 2.3，微腔幂指数由 0.9 渐降至 0.3 进入近饱和区；三次谐波增强超三个数量级、五次超两个数量级」 | 期刊版题录（Nano Lett. 26, 10554）与同工作 arXiv:2510.01760 摘要级一致："**near saturation regime**…giant enhancement of terahertz **third- and fifth-order** harmonic yields by cavity-engineering"（幂指数 2.3/0.9→0.3 为正文级数据，摘要级无矛盾） | ✓ |
| rationale L27 / content §2.3 / scheme §5.1：「Bauer 与 Hansen[9] 2018 PRL 120, 177401：SSH 拓扑相带隙下方谐波产额最高增强 14 个数量级」 | Crossref 题录确认标题 "High-Harmonic Generation in Solids with and without Topological Edge States"；14 个数量级为该文摘要著名结论 | ✓ 数值对应；但 full_review L12 将其称作"实验基准"见意见 R3-02 |
| rationale L33 / scheme L11：「Li 等[8] 6 nm 与 50 nm 厚度 Bi₂Se₃ 对比 + MIR-THz 双色场分离体态与 TSS 贡献」 | arXiv:2604.06051 标题 "Disentangling High Harmonic Generation from Surface and Bulk States of a Topological Insulator"、摘要 "topological surface states (TSSs)" | ✓ 标题+摘要级逐项对应 |
| rationale L43：「de las Heras[17] RhSi 手性 B20（空间群 198）TDDFT：谐波阶 3、4、9 相干叠加合成非零瞬时扭转的 3D 电场，分量周期 666 as 与 533 as」 | arXiv:2603.05346 摘要："The chiral crystal structure enables the generation of a local 3D electric field exhibiting an asymmetric instantaneous torsion on attosecond timescales"+ HHG selection rules in RhSi | ✓ 框架逐项对应（666/533 as 具体数值为正文级，摘要证实"阿秒时间尺度瞬时扭转"） |
| rationale L65 / scheme §2.2、§3.3：「Jessen[30] 2025 ZnO 第五次谐波强度驱动谱形转变 → I_threshold 基准；HHG（奇次、相干）与 PL（非相干、近带边）双通道」 | PRB 112, 214311 标题 "Interplay between high-harmonic generation and photoluminescence in ZnO: Anisotropic spectral properties of harmonic emission and the role of excitons" | ✓ 主题逐项对应（短 DOI 已验有效） |
| rationale L67 vs L103 vs content L39（[16]/[26] 作为 G3 分解基准的约束方向） | 文献本身成立；但正文三处对其约束角色的表述互斥（TaP→节点 X 上限 vs 散射 Z 下限；Duan→Z 下界 vs Z 上限） | ✗ **不匹配——正文内部角色互斥，见意见 R3-01** |

**8 条抽查：7 条匹配、1 条为正文内部角色互斥（R3-01）。** 关键数值链（two orders of magnitude → R=2 预标定；立方律 + tens of kV/cm → G3 校核基准与弱场窗）逐项回原文通过。

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[16] Pilch TaP（约 17 次，G3 校核基准贯穿三章）、[20] Lorenzo Kagome（约 12 次，R=2 阈值依据）、[9][12][13]（SSH 主线各 6–8 次）、[8]（体-边分离实验参照约 7 次）、[6] Neufeld（判别边界动机约 6 次）、[26]（约 8 次）。引用结构与"算法层→模型推广层→机制分解层→对照验证层"四方向论证链匹配。
- **关键判据的引用支撑**：R_HOTI 参照区间 10¹–10¹⁴（[9][10][11][14]）、R=2 下界（[20]）、I_threshold（[30]）、TaP 立方律（[16]）、Cd₃As₂ 上限（[26]）、T≥0.3 预估（[25] Bharti-Dixit 宇称规则）均有对应条目且数值链可回溯到文献原文。
- **自设阈值的声明纪律**：Δκ 20%、S_edge 0.2、SSH 边界态寿命 30 fs 参照量级四处均显式声明"本项目自定标/模型假设而非文献实测值"——处理方式正确，不属漏引。
- **国内现状支撑**：[27]（北大彭良友，末位作者 Peng L 经 Crossref 全作者链确认）、[28]（南大 β-WP₂）、[29]（半导体所）、[38][39]（上海光机所白亚团队）四组国内工作真实且归属无误。
- **覆盖判断**：40 条全部被引、五大主题簇（固体 HHG 起点 / SSH-HHG / Weyl-HHG / 国内现状 / 气相-阿秒谱系+ZnO 对照）各有 4–10 条支撑，无单条充数模式。**覆盖充分。**

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | high | 立项依据/研究内容 | rationale L67（§2.4 末）vs rationale L103（§5 问题 3）vs content L39（§2.4） | 同两条文献 [16][26] 作为 G3 三因素分解基准的约束角色在正文三处互斥：rationale L67 写"TaP 立方律约束**节点贡献上限**；Cd₃As₂…约束**散射贡献下界**"，而 rationale L103 与 content L39、scheme §3.2.2 L133 均写"TaP 立方律约束**散射 Z 的下限**"；Duan 的角色在 rationale L103 为"反推 Z 的**下界**"、在 content L39 为"界定 Z 的**上限**"，两两相反 | `TaP 太赫兹三次谐波的严格立方功率律约束节点贡献上限；Cd₃As₂ 微腔近饱和区的强度上限约束散射贡献下界`（rationale L67） | 统一为多数口径（content §2.4 + scheme §3.2.2：TaP 立方律→弱场区 Z 下限；Duan 强度上限→Z 上限/近饱和边界），据此改写 rationale L67 的概述句；rationale L103 末句"反推 Z 的占比下界"与 content"界定 Z 的上限"须二选一对齐。属跨章一致性项，建议与 R1 处置联动 |
| R3-02 | low | 整篇一致性审查 | full_review.md L12（章节衔接点首条） | 文献体裁表述与实物不符：full_review 称 [9] Bauer-Hansen 为"SSH-HHG 边界态增强的最高**实验**基准"，该文为 SSH 模型紧束缚理论计算（PRL 2018，无实验），rationale L27/content §2.3 均按理论工作报告 | `§2.2 给出 SSH-HHG 边界态增强的最高实验基准（14 个数量级，Bauer 与 Hansen[9] 2018 PRL 120, 177401）` | 改"最高实验基准"为"最高理论基准"或"最强基准（理论计算）"。全文其余位置（rationale/content/scheme/口径表）无此提法，仅此一处 |
| R3-03 | low | 立项依据/研究方案 | rationale L29；scheme L231（§5.2） | 正文称谓与 refs 著录形式不一致：作者全名 Christian **Saugbjerg** Lange（姓为 Lange，经 arXiv 确认），refs [13] 著录 "C. S. Lange and L. B. Madsen"，正文两处以中间名+姓领衔称"Saugbjerg Lange 与 Madsen[13]"/"Saugbjerg Lange 等人[13]"，与其余条目统一"姓+等人"体例不符，按"Saugbjerg Lange"检索姓氏会失配 | `Saugbjerg Lange 与 Madsen[13]于 2026 年（预印本）从量子光学角度扩展了同一问题` | 统一为"Lange 与 Madsen[13]"（rationale L29 与 scheme L231 两处同改）；若坚持该作者以"Saugbjerg Lange"为复合姓，则改 refs [13] 为 "C. S. Saugbjerg Lange" 并全文统一——二选一，消除两套口径 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 0 / 超界 0 / 一号两用 0 / 断链 0——**复核确认预跑 PASS 结论准确**；区间/并列展开、full_review 藏引、注释行藏引、尾注自证四类易漏情形逐一排查后均无漏报。
2. **元数据真实性**：联网正核 19 条（9 条 2024–2026 预印本全查 + 10 条 DOI 含 3 条 APS 短式新格式），**虚构 0、元数据错误 0、DOI 全有效**；9 条预印本经 `journal_ref`/`<arxiv:doi>` 逐条确认均未见正式发表版，预印本标注无一失实。
3. **上轮遗留复核**：[20] v1/v2 口径颠倒**未复发**——v2 摘要"up to two orders of magnitude"逐字证实、v2 日期与 refs 精确一致、五处口径统一；full_review 现行骨架无 v1/v2 残留标记。
4. **内容匹配性**：抽查 8 条，7 条匹配；1 条为正文内部对 [16]/[26] 约束角色的互斥表述（R3-01，本轮唯一实质问题）。
5. **意见统计**：critical 0 / high 1 / medium 0 / low 2，合计 **3 条**。
6. **需 M1 裁决的关键项**：R3-01（三处基准角色互斥——涉及 G3 终止判据的可解释性，建议与 R1 联动统一口径）；R3-02/R3-03 为低成本措辞修正。
7. **不涉及新增引用**：本报告未建议任何新增文献；无池纪律风险。
