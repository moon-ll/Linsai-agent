# R3 引用审校 — general-attosecond-streaking-20260822

- 审校日期：2026-10-17
- 审校范围：04_proposal/sections/{rationale.md, content.md, scheme.md, references.md}
- 方法：程序化编号对账（/tmp 脚本，零 LLM 判断）+ 高风险条目联网反查 + 正文声称匹配性抽查
- 结论速览：47 条文献，编号体系完整（无断链/超界/一号两用），联网核实 8 条全部真实且与正文声称匹配；唯一结构性缺陷是 [46][47] 两条史学锚点为死条目。

## 编号对账（五项计数 + 明细）

| 项目 | 计数 | 明细 |
|---|---|---|
| 1) 占位符 | 0 | references 与三章正文均无 TBD/待补/占位标记 |
| 2) 死条目（列了未被引） | 2 | **[46] Keldysh 1965、[47] Corkum 1993**。三章正文以"Keldysh 于 1965 年建立的非微扰电离理论框架""Corkum 1993 年提出的三步模型"（rationale L5）人名+年份方式提及，未挂 [46][47] 编号；references 尾注自称"新增的 [46][47] 两条作为强场电离物理史学锚点"，与零引用事实矛盾 |
| 3) 超界（引了不存在编号） | 0 | 正文引用编号 1–45 全部存在 |
| 4) 一号两用（同一文献多条目） | 0 | DOI/arXiv 全表查重无重复。[29]/[35] 为同课题组不同成果（arXiv 25 as 版与 Nature Communications 18 as 正式版），分别标注预印本†与正式版，处理规范 |
| 5) 正文断链（编号在 references 缺失） | 0 | — |

被引次数 Top（供参考）：[3] Pabst-Dahlström 9 次、[2] Cousin 8、[7] Peschel 8、[8] Inzani 8、[9] Zhu 5、[18] Kheifets 4。

## 联网核实记录（8 条）

| 条目 | 检索证据 URL | 结论 |
|---|---|---|
| [2] Cousin et al., PRX 7, 041030 (2017) | https://journals.aps.org/prx/abstract/10.1103/PhysRevX.7.041030 | ✓ 真实。摘要确认"first streaking measurement of water-window photon-energy pulses…driven by sub-2-cycle CEP-stable laser pulses…1850 nm"，与正文"次 2 周波 1850 nm 驱动""首次水窗条纹测量"匹配；322 as 上限与 350 eV 覆盖未在摘要直接给出，量级无矛盾 |
| [8] Inzani et al., J. Phys. Photonics 6, 025007 (2024) | https://www.semanticscholar.org/paper/3321cd1908f8b6417d577f9b350cd8203650ef2f（DOI 一致） | ✓ 真实。rACE（refined Analytical Chirp Evaluation）同时重构泵浦-探测脉冲并与实验延迟轴建立直接关联，"验证以模拟数据集为主"与摘要一致；正文已自我声明"rACE 公开全文未见 8%–15% 表述、以 XCOM 核算估值代入"，引用边界诚实 |
| [18] Kheifets et al., PRA 113, 043103 (2026), DOI 10.1103/9jcm-8gd8 | https://atto.ethz.ch/people/group-leader.html 及 https://orcid.org/0000-0002-3323-006X | ✓ 真实。APS 短码 DOI 有效，作者 Kheifets/Serov/Vismarra/Wörner 与条目一致，卷页 113:043103 一致 |
| [29] Gao et al., arXiv:2508.14774 (2025) | https://www.phys.k-state.edu/personal/mengh/publications.html | ✓ 真实。KSU 组页第 5 条，标题"Bright 25-attosecond light pulses reach the one atomic unit of time"逐字匹配 |
| [30] Ardana-Lamas et al., Ultrafast Science 5, 0128 (2025) | https://www.icfo.eu/news/2594/ 及 https://spj.science.org/index/ultrafastscience | ✓ 真实。19.2 as 软 X 射线纪录及"对 PRX 7, 041030 (2017) 数据再分析"均获 ICFO/ICREA 与期刊页确认；正文三方归因链（Cousin 2017→VTGPA 再分析→Comment/Reply）成立 |
| [31] Han et al., Comment, Ultrafast Science 6, 0145 (2026) | https://spj.science.org/index/ultrafastscience（Comment 摘要确认"third substantially different…"） | ✓ 真实。Comment 存在且针对 [30] |
| [35] Gao et al., Nat. Commun. 17, 8810 (2026), DOI 10.1038/s41467-026-76827-3 | https://www.nature.com/articles/s41467-026-76827-3（KSU 组页第 2 条 + Google Scholar） | ✓ 真实。标题"Bright isolated light pulses reaching 18 attoseconds…post-compressed Yb lasers"、卷页 17:8810、作者序 Gao/Hasan/Liang 全部逐字匹配 |
| [39] Hasan et al., PRL 136, 163201 (2026), DOI 10.1103/578k-kmw6 | https://arxiv.org/html/2512.19965 及 KSU 组页第 3 条 | ✓ 真实。摘要确认"unexpected time shift of ~1.32 fs relative to the 4d photoelectrons"（Xe 4d 巨共振），与正文"约 1.32 fs 时间偏移"精确匹配；PRL 卷页与短码 DOI 一致 |

经典条目 [46] Keldysh（Sov. Phys. JETP 20, 1307 (1965)）与 [47] Corkum（PRL 71, 1994 (1993)）著录与通行元数据一致，无需反查。

## 意见清单

- [R3-01|medium] references｜[46][47] 两条｜死条目：史学锚点零引用，尾注声明与事实矛盾｜"新增的 [46] Keldysh 1965、[47] Corkum 1993 两条作为强场电离物理史学锚点"｜rationale §1 首段"Keldysh 于 1965 年…""Corkum 1993 年提出的三步模型"两处人名后补挂 [46][47]，或删去两条并改写尾注
- [R3-02|medium] rationale/content/scheme｜多处｜截面数据库数值核算无条目支撑（覆盖缺口）｜"按 NIST 光电离截面库（XCOM）与 FFAST 等独立截面数据库估算，多通道贡献升至 15%–30%""甲烷…核算为 18%–24%"｜XCOM/FFAST 作为多通道贡献分档（8/15/30/50%）与两靶核算值（18–24%、16–26%）的唯一数据源，建议补一条数据库引用（含访问日期）或于方法学手册注明核算口径，避免评审追问来源
- [R3-03|medium] references｜[18][20][23][39]｜APS 短码 DOI 形态说明可再加一句核验状态｜"DOI: 10.1103/9jcm-8gd8"等 4 处短码｜已抽查 [18][39] 短码有效；建议对 [20]（10.1103/ll25-15dm）与 [23]（10.1103/csvm-858f）在提交前做同样的 doi.org 解析确认，与头部声明一并归档

正面确认（不计意见）：[29]/[35] 预印本-正式版双条目处理规范；[30]/[31]/[38] 最短脉冲之争三方文献链完整且引用立场（"该争议在同行评议层面尚未裁决"）与检索证据一致；[8] rACE 基准点引用已显式声明数值非文献锚定，引用纪律良好。
