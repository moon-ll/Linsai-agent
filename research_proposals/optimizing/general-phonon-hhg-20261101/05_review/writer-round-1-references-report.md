# writer 处置报告（第 1 轮·参考文献专项）

- 项目类型：general（面上）｜聚焦章节：`04_proposal/sections/references.md`｜日期：2026-11-05
- 评审报告：`05_review/critic-round-1-references.md`（10 条问题：critical 0 / high 3 / medium 4 / low 3）
- 核实方式：CrossRef API（`api.crossref.org/works/<DOI>` 逐字段取题名、作者链、期刊、卷、期、页/文章号、出版年）、arXiv API（`export.arxiv.org/api/query` 取作者链、题名、提交日期、journal_ref）、出版社官网（物理学报、激光与光电子学进展、光子学报、《物理》期刊页与 PDF 首页）。全部 57 条逐字段反查，无一条凭记忆生成。
- 重点维度：严谨性（0.70 → 目标 ≥0.90）

## 一、评审问题逐条处置

| # | 问题 | 级别 | 处置 | 修改位置 | 说明 |
|---|---|---|---|---|---|
| 1 | 全表 33 条无 DOI/arXiv 标识符，不可程序化溯源 | high | **已修** | references.md 全部 57 条 | 每条期刊文献补 DOI，预印本保留 arXiv 号，书章标注（书章）并补 DOI。标识符覆盖率 0/57 → **57/57 = 100%**。DOI 全部经 CrossRef 反查确认存在且元数据匹配 |
| 2 | [21] TAP 83, 85 (2000) 出处错误 | high | **已修** | references.md [21] | 原条目卷码与页码均错。实为 Dekorsy, Cho, Kurz, "Coherent phonons in condensed media", 收于 *Light Scattering in Solids VIII*, Topics Appl. Phys. **76**, 169-209 (2000)，DOI 10.1007/bfb0084242。卷号 76 经 Springer 丛书页、Konstanz 机构库引文、RWTH 图书馆书目三源独立确认 |
| 3 | [37] 刊名错误（"光学"应为《物理》） | high | **已修** | references.md [37]；00_research_idea.md 来源表第 20 条 | 该文载《物理》**50(11), 725-731 (2021)**，DOI 10.7693/wl20211102。刊名与卷期经《物理》官网 2021 年 50 卷 11 期栏目页与文章页确认，DOI 由期刊页元数据确认 |
| 4 | [12] 卷码漏 L（PRB 103 实为 L161406） | medium | **已修** | references.md [12] | 改为 Phys. Rev. B **103, L161406** (2021)，DOI 10.1103/physrevb.103.l161406。CrossRef 记录 article-number = L161406、issue = 16 |
| 5 | [34] 已见刊 Optica 7, 1764 (2020) 仍标 arXiv 预印本 | medium | **已修** | references.md [34] | 改引刊版 Optica **7(12), 1764 (2020)**，DOI 10.1364/OPTICA.402393；作者链经 CrossRef 逐位核对为 Parks, Ernotte, Thorpe, McDonald, Corkum, Taucer, Brabec 共 7 位 |
| 6 | [29] 与 [30] 疑为同组同工作双版本 | medium | **驳回（内容不同，两条均保留）** | references.md [29][30] | 已比对内容：[29] arXiv:2304.09459 题名 "Probing Phonon dynamics and Electron-Phonon Coupling by High Harmonic Generation in Solids"（5 作者，理论工作）；[30] PRL 133, 156901 题名 "Phonon-Coupled High-Harmonic Generation for Exploring Nonadiabatic Electron-Phonon Interactions"（7 作者，实验工作）。作者链首位相同但题名、作者数、性质均不同，非同一工作双版本，裁一留一会造成正文证据链断裂 |
| 7 | 近 3 年占比 30%（2023 起 35%）低于 50% 标杆 | medium | **已修** | references.md [41]-[57]；rationale.md §1/§2.1/§2.2/§2.3/§2.4/§2.5 | 新增 17 条 2024–2026 文献（全部经 CrossRef/arXiv 逐字段核实），近 3 年（2024–2026）占比 30% → **50.9%**；2023 起 **54.4%**。新增条目全部在正文挂钩引用，无孤儿条目 |
| 8 | 折著双规则并存；Photon./Photonics 混用 | low | **已修** | references.md 全表 | 统一为"≥4 位作者取前三位加 et al."；期刊缩写统一（Nat. Photonics 不再用 Nat. Photon.，Sci. Adv. 不再用 Sci. Adv，Proc. Natl. Acad. Sci. USA 不再用 PNAS） |
| 9 | 中文条目无 DOI，刊名缩写不统一 | low | **已修** | references.md [36][37][38][40] | 四条中文文献 DOI 全部补齐并经期刊页确认：10.7498/aps.71.20221319、10.7693/wl20211102、10.3788/lop202259.1302001、10.3788/gzxb20245306.0653210。刊名统一为中文全称（物理学报/物理/激光与光电子学进展/光子学报） |
| 10 | [23] 相邻论证位可补非线性声子学奠基综述 Först et al. | low | **不适用（改用等价且更贴题的来源）** | references.md [41] | 评审建议的 Först et al. (Nat. Phys. 13, 863 (2017)) 经核对其主题为非线性声子学谱学综述，与本课题论证位（声子作为可控激发手段 + 参与谐波产生）并非同一物理层。改为补入 Allafi et al., Phys. Rev. B 110, 064420 (2024)（太赫兹驱动声子参与自旋高次谐波产生），该文正面支撑"声子可作为谐波产生的参与变量"这一论证位，且正文原已提及该工作却无编号挂靠（见下方 P0-2） |

## 二、本轮额外发现并修复的错挂（评审未列出，独立核验发现）

核实过程中发现以下条目存在与正文论述不匹配的错挂，均已按出版社记录改正，未沿用原稿：

| 条目 | 原稿 | 核实结果 | 处置 |
|---|---|---|---|
| [10] | Silva et al., **Nat. Phys. 15, 752 (2019)** | 该 5 作者组合的唯一匹配为 Silva, Jiménez-Galán, Amorim, Smirnova, Ivanov, "Topological strong-field physics on sub-laser-cycle timescale", **Nat. Photonics 13(12), 849-854 (2019)**，DOI 10.1038/s41566-019-0516-1。已按 Nature Physics 1745-2473 期刊路由拉取 2019 全年卷 15 条目核验：第 750-753 页为 Verresen et al. "Avoided quasiparticle decay from strong quantum interactions"，不含该作者组合 | 已改为 Nat. Photonics 13, 849 (2019)。正文引用位置（"能带几何、量子度规与节点几何逐步进入强场光谱的读出对象[10-12]"）与该文实际内容相容 |
| [14] | Tancogne-Dejean et al., Nat. Commun. 8, 745 (2017) | 卷期页与 4 位作者均正确，但原条目未标题名，核对后确认该文实为 "Ellipticity dependence of high-order harmonic generation in solids originating from coupled intraband and interband dynamics" | 卷期页与作者保留，补 DOI 10.1038/s41467-017-00764-5 |
| [16] | "L. Li, P. Lan, X. Zhu, and P. Lu"（4 人） | 实为 7 位作者：Li, Lan, Zhu, Huang, Zhang, Lein, Lu | 改为前三位加 et al. |
| [23] | Afanasiev et al.（作者不全） | 实为 9 位作者 | 改为前三位加 et al. |
| [27] | Bionta et al.（作者不全） | 实为 15 位作者 | 改为前三位加 et al. |
| [31] | Notter et al., Nano Lett. 26, 4973 (2026)（无题名） | 实为 "Dynamical Control of Coulomb Interactions and Hubbard Bands in Monolayer 1T-TaS₂" | 补题名与 DOI 10.1021/acs.nanolett.5c05443 |
| [35] | Nebgen et al., Sci. Adv. 12, adz5621 (2026)（无题名） | 实为 "Isostructural electronic transition in MoS₂ probed by solid-state high-harmonic generation spectroscopy" | 补题名与 DOI 10.1126/sciadv.adz5621 |
| [38] | 汪洋, 苗翔阳, **受主**掺杂半导体... | 刊载题名为"**受体**掺杂半导体高次谐波产生的理论研究"，作者为汪艳锋、苗向阳 | 改正题名与作者，加 DOI |
| [17] | arXiv:2604.23294（预印本） | 刊版已出版：J. Phys. Chem. Lett. **17(28), 7936-7944 (2026)**，DOI 10.1021/acs.jpclett.6c01354 | 改引刊版 |
| [20] | arXiv:2512.01712（预印本） | 刊版已出版：Phys. Rev. B **113(18), 184310 (2026)**，DOI 10.1103/msy5-4yxd | 改引刊版 |

## 三、跨章节 P0 修复（本轮聚焦章节的直接相关项）

| # | 问题 | 处置 | 说明 |
|---|---|---|---|
| P0-1 | rationale.md 末尾内嵌了一份与 references.md 完全重复的参考文献表。组装器（`scripts/proposal_sections.py::assemble_draft`）按 `PROPOSAL_SECTIONS` 顺序拼接五个模块，references 已是独立模块，两份并存会在组装后的申请书中产生两份重复文献表 | **已修** | rationale.md 中的重复文献表整体迁出，只保留正文论证。文件行数由 167 降至 91 |
| P0-2 | rationale.md §2.1 提到"Allafi 等人则从理论上提出以太赫兹激光驱动的声子参与自旋高次谐波产生"，但无编号挂靠，评审所列"文献支撑真实"风险项 | **已修** | 补 [41] 挂靠（Allafi et al., PRB 110, 064420 (2024)） |
| P0-3 | 冗余修复指令：三条判据依据句在 rationale/content/scheme 三章重复 | **已修** | 母本保留在 rationale §5；content 改为章节指代 + 本章视角（ZnO 极性/非极性模检验）；scheme 改为章节指代 + 本章执行形式（核对表、互相关测量、γ 扫描参数） |
| P0-4 | 冗余修复指令："理论侧的通道分解与实验侧的份额表互为约束"在 content/scheme 重复 | **已修** | content 保留论证并指向研究方案第 4.6 节；scheme 改为比较协议的执行描述 |
| P0-5 | full_review.md 记 "参考文献 [1]-[50]"，与实际条目数不符 | **已修** | 改为 [1]-[57] |

## 四、终检实测数据（本轮当场复算，非沿用旧值）

| 检查项 | 结果 |
|---|---|
| 参考文献条目数 | 57（[1]-[57]，编号连续无跳号） |
| 正文引用悬空（引用了列表中不存在的编号） | 0 |
| 孤儿条目（列出但正文未引用） | 0 |
| DOI/arXiv 标识符覆盖率 | 57/57 = **100%**（评审前 7/40 = 17.5%） |
| 无标识符条目 | 0 |
| 无出版年条目 | 0 |
| 近三年（2024–2026）占比 | 27/57 = **50.9%**（评审前 12/40 = 30%） |
| 2023 年起占比 | 31/57 = **54.4%**（评审前 14/40 = 35%） |
| 折著规则 | 统一：≥4 位作者取前三位加 et al. |
| 刊名缩写 | 统一（Nat. Photonics / Sci. Adv. / Proc. Natl. Acad. Sci. USA） |

正文表达质量（对 rationale/content/scheme 三章逐句扫描）：

| 检查项 | 结果 |
|---|---|
| 超长句（>120 字） | **0 处**（评审前 10 处，扣 0.08） |
| 句长中位数 | rationale 54 / content 49 / scheme 46 字（范本中位数约 56 字） |
| 禁用词命中（交付物/硬门控/口径/锚定/边界一/详§…） | 0 |
| 模板句式"为…提供…" | 3 处（阈值 8–15） |
| 死板关联词（在此基础上/此外/与此同时/因此/然而） | 0 |
| 元话语 | 0 |
"| 冗余修饰词（按词分别计数，阈值 ≤12 次/词） | 显著 4 / 完整 4 / 关键 3 / 系统 3 / 有效 1 / 其余 0——各项均远低于阈值 |
| 冗余修饰词的逐处性质核查 | 4 处"显著"全为 χ² 检验的统计显著性（固定术语）；4 处"完整"全为"完整声子周期"（数量描述）；3 处"关键"全为"关键科学问题"（法定术语）；3 处"系统"为中红外强场系统、系统误差、系统梳理（实义）；1 处"有效"为"有效电子退相干时间"（实义）。剔除法定术语与统计术语后，真实冗余修饰为 0 |

## 五、遗留与边界说明

1. **评审第 6 条（[29]/[30] 双版本）驳回**：已比对题名、作者数与工作性质，两者为不同工作。若强行裁一留一，将使正文"Hu 等人的两项工作"（rationale §2.3）在论证上失去一支，与正文表述直接矛盾。此项属评审判断有误，按"指令与事实冲突时以原始文献为准"处理。
2. **评审第 10 条（[23] 相邻论证位）不适用**：建议补入的 Först et al. 综述主题为非线性声子学谱学，与该论证位不属同一物理层；改补 Allafi et al.，理由见上表。
3. **[50] Shi et al., Opt. Express (2026) 无卷期页**：CrossRef 记录该文 article-number 与卷期字段尚未分配（2026 年新刊文章常见），DOI 10.1364/OE.615079 已确认存在并可解析。按"卷期待刊版分配"的常规写法著录，未编造卷页。
4. **未新增研究基础/工作条件/团队/经费内容**：本轮修改全部落在文献著录与论证链引用，未越界。

## 六、产物同步

| 产物 | 更新内容 |
|---|---|
| `04_proposal/sections/references.md` | 全表重写（57 条，逐字段核实） |
| `04_proposal/sections/rationale.md` | 移除重复文献表；补 [41] 挂靠；新增 7 段前沿文献论证（[42]-[47][52][55][56][57]） |
| `04_proposal/sections/content.md` | 三条判据依据句改为章节指代；理论-实验互约束段改为章节指代 |
| `04_proposal/sections/scheme.md` | 三条判据依据句改为执行参数/执行形式视角；理论-实验互约束段改为协议执行描述 |
| `04_proposal/sections/full_review.md` | 参考文献区间 [1]-[50] → [1]-[57] |
| `00_research_idea.md` | 来源表补 17 条经核实条目；[8][11] 改刊版；[37] 刊名改《物理》；[38] 题名/作者改正；恢复被误撤销的 qnxw-xh8m 条目并说明恢复依据 |
| `02_literature/reading-notes.md` | 追加 20 条核实笔记（含题名、来源、核心结论、与课题关联、已引用位置） |
| `03_method/method-manual.md` | 未改动（方法学手册为单一真相源，由轮末专职步骤维护） |
