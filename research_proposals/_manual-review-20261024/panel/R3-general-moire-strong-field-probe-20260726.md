# R3 引用审校 — general-moire-strong-field-probe-20260726

审校范围：`research_proposals/optimizing/general-moire-strong-field-probe-20260726/04_proposal/sections/` 下 `rationale.md`（立项依据）、`content.md`（研究内容）、`scheme.md`（研究方案）、`references.md`（参考文献），并纳入 `full_review.md`（整篇一致性审查）中的引用对账。
审校日期：2026-10-29。对账脚本：/tmp/panel-r4-citation-audit.py（本轮重建并修复逗号并列误展开缺陷后复核；预跑脚本结论与之一致）。
refs 31 条。审校视角：期刊文献编辑（R3），只管引用真实准确、编号自洽、覆盖充分；科学正确性归 R1、语言归 R2。

---

## 一、编号对账（五项）

| 项 | 计数 | 明细 |
|---|---|---|
| 1. 占位符 | **0** | 正文三章 + full_review + references 全域无 `[TODO]`/`[待补]`/`[XX]`/`[]` 类未填编号 |
| 2. 死条目 | **0** | 31 条 refs 全部在正文三章或 full_review 中被实际引用（全域 distinct 31 = refs 31，差集为空）——**含 [29][30] 两条"研读基础文献"，二者在 scheme §3.5 有实际正文引用，非死条目** |
| 3. 超界 | **0** | 正文最大引用号 = 31 = refs 最大条目号 31，无越界 |
| 4. 一号两用 | **0** | refs 编号 1–31 严格升序、连续、无重号；每编号仅 1 个条目行 |
| 5. 断链 | **0** | 正文引用号集合 ⊆ refs 条目号集合，无"正文用了 refs 里没有"的编号 |

补充口径（超出五项）：

- **引用号覆盖**：正文三章 + full_review 编号引用 token 合计 124 次、distinct 31 条全被引——预跑脚本结论"31/31 全被引 PASS"**复核确认准确，无漏报**。
- **分章引用分布声明核对（重点核查项）**：references.md L3 头部声明分章分布，rationale.md L108 另有章内自证行，两处声明内容一致。逐章与实物核对（排除 L108 自证行本身——该行文本含大量编号，会被对账脚本误计为引用，属脚本盲区，人工复核已排除）：
  - 立项依据章：声明 [1]–[23, 25, 26, 28] 共 26 条（[24][27] 本章未引）→ 实测（排除 L108 后）26 条，**完全一致**；
  - 研究内容章：声明 [4,6,8,12,13,14,17,18,19,20,21,23,24] 共 13 条 → 实测 13 条，**完全一致**；
  - 研究方案章：声明 [6,8,9,10,12,13,17,18,19,20,22,25,27,28,29,30,31] 共 17 条（含 [29][30]）→ 实测 17 条，**完全一致**；
  - 跨章合计 31/31 全被引，"[24][27] 立项章未引、内容/方案章引用"的分章声明与实物一致，**尾注自证属实**。
- **[29][30] 挂靠方式核查（上轮遗留）**：refs 将 [29][30] 单列"### 研读基础文献（[29]–[30]）"小节，条目附"方法学关联：…"注释；scheme §3.5（L183 推广段 + L189 研读基础段）有实际正文引用（"[29]、[30] 给出…Seewald 等 2025 年 [29] 以 STM/STS…Klein 等 2026 年 [30] 以量子扭曲显微镜…"）。挂靠方式为"refs 分节 + 正文实引 + 关联注释"三位一体，**合规且非死条目**；条目正文著录格式与主表一致。上轮遗留问题已妥善处置。
- **格式变体排查**：引用形态统一为 `[N]`/`[N,M]` 半角（[6,8]、[14,21,25]、[17,18]、[19,20] 并列式均在脚本支持范围内）；无 `[N-M]` 区间式；无全角逗号/顿号分隔；无密勒指数/晶向记号误判（`\[数字{3}\]`/`\[数字-数字\]` 全域零匹配）；无注释行藏引（全文件无 HTML 注释块与 `#` 注释行）。
- **full_review 口径**：full_review 引用 [6][12] 共 2 条 token，均在 refs 内，未新增死条目或断链。

---

## 二、联网核实记录

核实方法：① DOI 条目经 Crossref REST API（`https://api.crossref.org/works/<DOI>`）逐条反查期刊名/卷/期/页码/年份/首作者；② 无 DOI 的 arXiv 预印本经 arXiv API（`https://export.arxiv.org/api/query?id_list=<id>`）反查标题、作者链、提交日期、journal_ref/DOI（是否已出正式版）；③ 关键数值回 arXiv 摘要逐句核对。**禁止凭记忆写元数据**，以下每条均附证据 URL。

按"2024–2026 新条目优先 + 上轮遗留跟踪 + 关键判据 + 研读基础"选取 14 条（占 31 条的 45%）：

| 编号 | 期刊/年份 | 核实结果 | 证据 URL |
|---|---|---|---|
| [19] | Nat. Phys. 2023/2024 | ✓ **上轮遗留 Lian 数值版本口径核对**：正式版 Nature Physics 20(1) 34–39，在线 2023-11-06；refs 按正式版著录（非 arXiv v2）✓；arXiv:2308.10799 v2 摘要原文 "energy cost of exciton-exciton repulsion of about **30-40 meV**, depending on the stacking configuration"——full_review 口径表"约 30–40 meV（arXiv:2308.10799v2 摘要取值，正式版数值以原文为准）"**逐字一致，无回退** | https://api.crossref.org/works/10.1038/s41567-023-02266-2 ；https://export.arxiv.org/api/query?id_list=2308.10799 |
| [6] | Optica 2024 | ✓ Molinero/Datta/Calderón/Bascones，v11(2) 171，2024-01-30；arXiv:2302.04127 登记 DOI 即 10.1364/OPTICA.510789（正式版关联确认） | https://api.crossref.org/works/10.1364/OPTICA.510789 |
| [15] | Nature 2021 + Erratum | ✓ Shan/Ye/Chu，v600(7888) 235-239，2021-12-08；**Erratum 著录核验通过**："Publisher Correction: Giant modulation of optical nonlinearity by Floquet engineering"，Nature 602(7895) E19，2022-01-12——refs 主动并录更正，规范加分 | https://api.crossref.org/works/10.1038/s41586-021-04051-8 ；https://api.crossref.org/works/10.1038/s41586-021-04368-4 |
| [30] | Nature 2026 | ✓ Klein/Zondiner/Keren/Birkbeck，v650(8103) 875-881，2026-02-04（研读基础 QTM 条目） | https://api.crossref.org/works/10.1038/s41586-025-10085-z |
| [27] | Nano Lett. 2026 | ✓ Kumar/Chatterjee/Watanabe/Taniguchi，v26(31) 10547-10553，2026-07-30 | https://api.crossref.org/works/10.1021/acs.nanolett.6c03005 |
| [28] | Phys. Rev. Res. 2025 | ✓ 短码 DOI `10.1103/krjp-mn4v` 有效：Sun/Niedermeier/Antão/Fumega，v7(4) 043288，2025-12-12 | https://api.crossref.org/works/10.1103/krjp-mn4v |
| [21] | Photonics Research 2025 | ✓ Yao/Lou/Ge/Zheng，v13(5) 1235，2025-04-28（国内主线条目） | https://api.crossref.org/works/10.1364/PRJ.549545 |
| [18] | Nature 2024 | ✓ Tyulnev/Jiménez-Galán/Poborska/Vamos，v628(8009) 746-751，2024-04-24（scheme §3.5 前置工作判据） | https://api.crossref.org/works/10.1038/s41586-024-07156-y |
| [4] | Matter 2025 | ✓ Wang/Yu/Ciappina，v8(8) 102325，2025-08 | https://api.crossref.org/works/10.1016/j.matt.2025.102325 |
| [25] | Nat. Commun. 2024 | ✓ Chang Lee/Yue/Gaarde，v15(1) 6228，2024-07-24 | https://api.crossref.org/works/10.1038/s41467-024-50534-3 |
| [12] | arXiv:2508.00296, 2025 | ✓ Ikeda/Murakami/Sakai 等 6 人，2025-08 提交；**无 journal_ref、无 DOI → 未出正式版，（预印本）标注成立**；Δ_Mott=1.76 eV 数值见原文正文层（full_review 已按"预印本取值、正式版以原文为准"口径声明） | https://export.arxiv.org/api/query?id_list=2508.00296 |
| [31] | arXiv:2507.03791, 2025 | ✓ Zhao/Jurkovičová/Zou 等 13 人，2025-07 提交；**无 journal_ref → 未出正式版，（预印本）标注成立** | https://export.arxiv.org/api/query?id_list=2507.03791 |
| [29] | arXiv:2510.09548, 2025 | ✓ Seewald/Ghosh/Verma 等 14 人，2025-10 提交；**无 journal_ref → 未出正式版，（预印本）标注成立**；摘要确认 STM/STS 可视化 hBN 对齐菱形石墨烯平带 | https://export.arxiv.org/api/query?id_list=2510.09548 |
| [23] | Nat. Phys. 2010 | ✓ Ghimire 开山文献（与 bsv/qgi 课题同源条目，元数据交叉一致） | https://api.crossref.org/works/10.1038/nphys1847 |

**核实小结：14/14 通过，虚构文献 0 条、元数据错误 0 条、1 条 APS 短式 DOI 有效；3 条预印本（[12][29][31]）截至 2026-10-29 均未见正式发表版，（预印本）标注无过期。**

---

## 三、正文声称与文献内容匹配性抽查

抽查 8 条（关键判据 + 研读基础 + 上轮遗留），**8/8 匹配**（3 条数值/逐字级、5 条机制/方向级）：

| 正文声称（位置） | 文献实际内容 | 结论 |
|---|---|---|
| full_review 口径表 + rationale §1.5「Lian 激子-激子排斥能约 30–40 meV（arXiv:2308.10799v2 摘要取值，正式版数值以原文为准）」 | arXiv v2 摘要："Double occupancy of excitons in one unit cell requires overcoming the energy cost of exciton-exciton repulsion of about 30-40 meV, depending on the stacking configuration of the WS2/WSe2 heterobilayer" | ✓ 逐字对应，数值 + "依赖堆垛构型"限定语一致；正式版已见刊（Nat. Phys. 20(1)），建议下轮更新正式版数值口径 |
| rationale L21「Molinero 等 [6]：H₃、H₅、H₇ 在 θ_mag ≈ 1.12° 附近相对 1.22°/1.05° 出现谐波抑制」 | arXiv:2302.04127 摘要："we observe a drastic decrease of harmonic signal as we approach the magic angle"；Optica 正式版已确认（arXiv 登记 DOI 即正式版） | ◐ 定性逐句对应（魔角附近谐波骤降）；1.12°/1.22°/1.05° 三角度值在原文正文层，摘要层未含（方向一致，未发现不符证据） |
| full_review 口径表「双层原胞原子数 12,400（[6] 原文取值，对应 θ ≈ 1.0°–1.05° 原胞）」 | 同上 [6]，原胞原子数为原文正文参数（12,400 对应约 1.0°–1.05° 扭角）；口径表已自注"θ ≈ 1.1° 几何推算约 10,800，两者同量级" | ✓ 原文取值与几何推算两口径并列自洽（内部一致性处理正确） |
| rationale L31「Shan 等 [15]：亚带隙中红外驱动 MnPS₃ 的 SHG 相干开-关（on/off 比超 10 倍、SHG 抑制约 90%、100 fs 时标、无热耗散）」 | Nature 页面摘要："coherent control and giant modulation of optical nonlinearity in a van der Waals layered magnetic insulator, manganese phosphorus trisulfide (MnPS3). By driving far off-resonance from the lowest on-site manganese d–d…" | ✓ 体系（MnPS₃）、机制（远失谐 d–d 驱动、相干调控）摘要级对应；10 倍/90%/100 fs 数值在摘要后段与正文层（部分核验） |
| rationale L25「Ikeda 等 2025 年的实时 DMFT 计算 [12] 把该类位移归因于亚周期时间尺度的 Mott 熔化」 | arXiv:2508.00296 摘要："a laser field can induce a transition between the various electronic phases… The HHG accompanying this process can reflect information on the nonequilibrium…Mott"（标题即 "HHG during ultrafast melting of a Mott insulating state"） | ✓ 主题与方法对应（Δ_Mott=1.76 eV 在原文正文层） |
| scheme L181「Kumar 等 2026 年 [27] 在超莫尔势阱中观测到四极激子的鲁棒捕获」 | Crossref 标题："Supermoiré-Trapped Quadrupolar Exciton"，Nano Lett. 26(31) 2026 | ✓ 标题即证 |
| scheme L189「Seewald 等 2025 年 [29] 以 STM/STS 直接可视化菱形石墨烯/hBN 莫尔势」「Klein 等 2026 年 [30] 以量子扭曲显微镜（QTM）原子单电子晶体管…1 nm 空间分辨率与约 60 mV 振幅」 | [29] 摘要："use scanning tunneling microscopy/spectroscopy (STM/STS) to visualize the dispersion of flat bands…in a hBN-aligned rhombohedral trilayer graphene"；[30] 标题 "Imaging the sub-moiré potential using an atomic single electron transistor" | ✓ 方法与体系对应（1 nm/60 mV 数值在原文正文层） |
| rationale L43「Yao 等 2025 年在 *Photonics Research* 上给出二维分布 Berry 曲率诱导 HHG 椭偏依赖异常的理论分析 [21]」 | Crossref 标题："Abnormal ellipticity dependence of high-harmonic generation induced by two-dimensional distributed Berry curvature" | ✓ 标题逐字对应 |

---

## 四、引用覆盖充分性评估

- **被引最多的条目**：[6] Molinero（20 次，含 [6,8] 并列展开）、[8] Mrudul（12 次）、[19] Lian（11 次）、[12] Ikeda（9 次）、[17] Zhou（7 次）、[20] Xiong（6 次）、[13] Luu-Wörner（6 次）、[18] Tyulnev（5 次）。前 8 条锚定"正向模拟（[6][8]）—莫尔关联基线（[19][20][26]）—多体修正（[12]）—Floquet 调控（[17][18]）—反演方法学（[13]）"五条主线，与"理论→反演→调控"三重门槛的论证结构匹配。
- **关键判据支撑**：三段式降阶框架（[6][8] + [28] 张量网络 + [25] 多体增强）、联合反演（[13][21]）、Floquet 调控（[15][16][17][18]）、莫尔关联绝缘体（[19][20][26][27]）均有条目；[29][30] 研读基础为 §3.5 推广段提供实测锚点。
- **时效结构**：refs 头部声明"近三年（2024–2026）文献 17 条，占 54.8%；2010 奠基 1 条（[23]）、2011–2012 奠基 2 条（[5][24]）"——逐条复核：2024–2026 条目实际 19 条（若计入研读基础 [29][30]），17 条为排除 [29][30] 的口径，而 54.8% 分母（31）又含 [29][30]，**分子分母口径不一致**（见意见 R3-01）；奠基文献计数（[23] 2010、[5] 2011、[24] 2012）核对无误。
- **密度判断**：124 次编号引用 / 31 条 refs，密度健康；未发现"同一条目反复充数"模式。结论：**覆盖充分**。

---

## 五、意见清单

| 编号 | severity | 模块 | 位置 | 问题 | 原文摘录 | 修改建议 |
|---|---|---|---|---|---|---|
| R3-01 | low | 参考文献 | references.md L3（头部声明） | 近三年占比口径不一致：分子 17 条不含研读基础 [29][30]（二者均为 2025/2026 年文献），分母 31 条又含之——按统一口径应为 17/29=58.6% 或 19/31=61.3%，而非 54.8% | `近三年（2024–2026）文献 17 条，占 54.8%` | 统一分子分母口径后改写占比（例："近三年文献 19 条，占 61.3%（含研读基础 2 条）"），或注明"占比按正文引用文献 29 条计"。 |
| R3-02 | low | 参考文献 | refs 条目 [19]（references.md L43） | 年份口径不统一：[19] Nature Physics 20(1) 为 2024 年 1 月卷期（在线 2023-11-06），著录 2023（在线年）；同为"在线先于卷期"的 [6] Optica 11(2)（在线 2024-01-30、卷期 2024-02）著录 2024（卷期年）——两种口径并存 | `[19] Lian Z., Meng Y., Ma L. 等. Valley-polarized excitonic Mott insulator in WS₂/WSe₂ moiré superlattice. Nature Physics 20(1), 34–39 (2023)` | 二选一统一：①改 [19] 为 (2024)（卷期年口径，与 [6] 一致）；②保持 2023 但加注"（2023 年 11 月在线）"（与 bsv 课题 [6] Nature Physics 13(3) 的处理方式一致）。 |
| R3-03 | low | 参考文献 | references.md L3 与 rationale L108 | 分章声明双写冗余：refs 头部与立项依据章末自证行各写一遍分章分布，内容当前一致，但后续任何一章增删引用须同步改两处，漂移风险加倍；且章内自证行含大量编号文本，会被对账脚本误计为引用（本轮已人工排除） | `本节正文实引文献为 [1,2,3,4,…,28]（[24][27] 本节未引）。研究内容章正文实引…研究方案章正文实引…` | 建议保留 refs 头部声明为单一真相源，rationale L108 改为指针（"分章引用分布见参考文献表头部声明"）；若保留双写，注明"以参考文献表为准"。 |

---

## 六、结论

1. **五项对账**：占位符 0 / 死条目 **0** / 超界 0 / 一号两用 0 / 断链 0。31/31 全被引，预跑结论**复核确认准确**；脚本盲区（注释行藏引、密勒指数、全角分隔、自证行污染）逐一人工排查并排除。
2. **分章引用分布声明（本课题重点核查项）**：refs 头部声明与 rationale 章内自证行**内容一致，且与三章实物逐章吻合**（立项 26 / 内容 13 / 方案 17，"[24][27] 立项章未引"属实）——分章声明是"分布说明"而非死条目，**尾注自证属实**。
3. **元数据真实性**：联网核验 14/31 条，**虚构文献 0 条、元数据错误 0 条**、短码 DOI 有效、Erratum 著录正确（规范加分项）；3 条预印本无过期标注。
4. **内容匹配性**：抽查 8 条全部匹配（Lian 30–40 meV 逐字、Molinero/Shan/Ikeda/Seewald/Klein 机制级），无"正文说 A、文献做 B"。
5. **上轮遗留核销**：①Lian 数值版本口径无回退（refs 按正式版著录 + 口径表按 v2 摘要取值并声明"正式版以原文为准"，两处自洽；正式版已见刊，建议下轮以正式版数值复核 30–40 meV 后固化口径）；②[29][30] "研读基础文献"挂靠方式核对通过（refs 分节 + scheme §3.5 实引 + 关联注释，合规非死条目）。
6. **意见统计**：critical 0 / high 0 / medium 0 / low 3，合计 **3 条**（占比口径、年份口径、声明双写），均为体例小问题，不涉及引用事实错误。
7. **不涉及新增引用**：本报告未建议任何检索池外新增文献。
