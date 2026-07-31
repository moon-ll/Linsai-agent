# 对抗评审报告（第 7 轮）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文不超过 30 页） |
| 本轮聚焦 | （七）参考文献（引文列表） |
| 用户指定文件 | `04_proposal/sections/references.md` |
| 实际文件状态 | **完全空白**（仅 1 行标题 + 1 行占位符"待 writer 补齐"；中文字符 8 个；正文 0 字） |
| 替代主审文本 | `04_proposal/sections/outcome.md` 第 49–63 行 `### 6.6 本节引用文献`（13 处 `[n]` 内嵌引用，编号 1–8，但无标准引文条目） |
| 跨章节简查 | §1.2 立项依据中的作者—年份引证（约 12 处，含 Rasputnyi 2024、Even Tzur 2024、Iskhakov 2012、Spasibko 2012、Szilard 2012、Silva 2018、Murakami 2018、Wu/Schafer/Gaarde 2016、Raab 2024、Li 2022、Rivera-Dean 2023、Peschel 2022、Wu 2024 等）；§2.3/§3.2 重复引用 |
| 质量标准 | `memory/nsfc-standards.json` → `project_types.general` |
| 质量门槛 | 综合分 ≥ 0.80；high = 0；medium ≤ 3 |
| 评审日期 | 2026-07-30 |

> 证据边界：本报告评的是当前磁盘中的申请书。本轮聚焦章节 `references.md` 仅 1 行占位符文字，模块完全缺失；正文无任何文献条目可供段落级深审。下文以"模块缺失 + 嵌入引文 vs. 规范引文条目差异 + 跨章节引文一致性"为评审对象。

---

## 0. 模块完整性检查（7 个标准模块）

| 标准模块 | 定位 | 中文字符数（约） | 是否 ≥200 字且有实质内容 | 结论 |
|---|---|---:|---|---|
| 立项依据 | `## （一）立项依据`（rationale.md） | 1833 | 是 | ✅ 完整 |
| 研究内容 | `## （二）研究内容`（content.md） | 2699 | 是 | ✅ 完整 |
| 研究方案 | `## （三）研究方案`（method.md） | 1559 | 是 | ✅ 完整 |
| 特色与创新 | `sections/innovation.md` | **0**（仅占位符"待 writer 补齐"） | **否** | ❌ **[critical] 模块缺失** |
| 年度研究计划 | `sections/plan.md` | **0**（仅占位符"待 writer 补齐"） | **否** | ❌ **[critical] 模块缺失** |
| 预期研究成果 | `sections/outcome.md` §6 | 2456 | 是 | ✅ 完整（已大幅扩展） |
| 参考文献 | `sections/references.md` | **0**（仅占位符"待 writer 补齐"） | **否** | ❌ **[critical] 模块缺失** |

**完整性结论：7 个标准模块中，4 个达到实质内容门槛（立项依据/研究内容/研究方案/预期研究成果）；3 个模块仍为占位符状态——特色与创新、年度研究计划、参考文献，全部 [critical] 级缺失。**

> 第 6 轮评审的 §6 "成果映射矩阵"已被 `outcome.md` 大幅补强（已含 7 行 C1–C7 表格），属有效改善。本轮聚焦的参考文献模块从第 6 轮起即被标注为 [critical]，到本轮仍未实质补齐——属于"未解决的关键缺陷"。

---

## 综合评分

**0.55 / 1.00**（四维评分；本轮以"参考文献模块完整性 + 嵌入引文规范度 + 跨章节引文一致性"为主）

面上项目标准要求"创新性 + 扎实基础、小切口深挖掘"，并明确"立项依据是否充分（前人局限性是否讲清楚）"作为评审清单之一。文献体系是支撑该清单的核心载体。本轮聚焦章节完全缺失，且全书存在大量"作者—年份/期刊片段"内嵌引证与 `outcome.md` §6.6 的局部编号引文混用的体系性问题，导致：

1. 关键论断（前人局限性）无法系统追溯；
2. 评审专家无法在 20 分钟内核查主张的文献支持；
3. 跨章节引文数量、引用密度、出版信息口径均不可控。

因此参考文献维度应作为独立扣分项。综合评分需在第 6 轮 0.65 的基础上进一步下调。

---

## 维度评分

| 维度 | 得分 | 问题数 | 主要短板 |
|---|---:|---:|---|
| 创新性（innovation） | 0.72 | 2 | "首例"声明与现有 Rasputnyi 2024 的边界仍依赖人工口径，未由文献体系兜底；嵌入引文创新点 2 引用 Boroumand 2025 与 Li 2019，前者在 §1.4、§2.8 与 outcome §6.3 同时出现但无完整出版信息 |
| 可行性（feasibility） | 0.62 | 5 | 关键方法学引文（Raab 2024、Li 2022、Rivera-Dean 2023、Peschel 2022）只有 arXiv 编号无正式出版/卷期/页码，无法由评审人核查成熟度；outcome §6.6 引入 8 条 arXiv 编号均为预印本（含 2026 年预印本），形式上属"未经同行评审引用" |
| 严谨性（rigor） | 0.42 | 9 | 参考文献模块完全空白（仅占位符）；引文体系存在"作者—年份片段 + 局部编号 + arXiv 孤号"三种格式并存；§6.6 引文 [3][4][5][7][8] 为 2026 年 arXiv 预印本，是否经过同行评审/最终出版无法确认；§1.2/§2.3/§3.2 中同一文献（如 Iskhakov 2012、Raab 2024）多处出现但格式不一致；参考文献数量过少（约 13 条外部引证），对"量子光 HHG 探针"系统性范式承诺而言支撑不足 |
| 完整性（completeness） | 0.40 | 4 | 7 个标准模块中 3 个仍为占位符状态（特色与创新 / 年度研究计划 / 参考文献），全部 [critical] 级缺失；references.md 0 字；6.6 节局部编号引文 8 条但未提供完整书目信息（无卷期页码/DOI/作者全名/期刊缩写规范）；引文格式未统一 |

综合评分按本项目面上项目的核心导向作四维映射加权：
`0.30×0.72 + 0.25×0.62 + 0.25×0.42 + 0.20×0.40 = 0.216 + 0.155 + 0.105 + 0.080 = 0.556 ≈ 0.55`。

---

## 聚焦章节段落级深审

### 文件级定位：`sections/references.md`

#### [critical] completeness — 参考文献模块完全缺失
- 位置：`04_proposal/sections/references.md`（整文件 3 行）
- 问题：用户指定的独立参考文献章节文件仅含 1 行 H2 标题 `## （七）参考文献` 与 1 行占位符 `（待 writer 补齐）`，无任何文献条目。这是申请书最低限度必备模块之一，对评审人核查"前人工作局限性""研究方法成熟度""优先权边界"具有不可替代作用。模块从第 6 轮评审起即被标为 [critical]，到本轮仍未补齐。
- 建议：完整重建该章节文件，按 NSFC 惯用格式（顺序编码制或作者—年份制二选一并全文统一）列出至少 30–50 条参考文献，覆盖：BSV/非经典光物理、固体 HHG、量子光 HHG 理论、关联体系 HHG、TMDC/莫尔/Mott、HHG 涨落统计、贝叶斯/反演方法、阿秒科学方法学。每条须含：作者全名（或前 3 人 + et al.）、题名、期刊缩写、卷（期）、起止页码/文章号、年份、DOI/arXiv。提交前逐条核实是否已正式发表，避免 arXiv 编号孤悬。
- action：add

#### [critical] rigor — 引文体系存在三种格式并存，未统一
- 位置：全书各章节；`outcome.md` §6.6 第 49–63 行；`rationale.md` 第 22、28、35、37、43 行；`content.md` 第 26、30、36、37、65、67、68、95、96、97 行；`method.md` 第 9、17、18、29 行
- 问题：申请书存在三种引文格式并存：
  1. **作者—年份片段**：如 `Iskhakov 2012`、`Spasibko 2012`、`Rasputnyi 2024`、`Even Tzur / Gorlach 2024`、`Wu/Schafer/Gaarde 2016`、`Rivera-Dean 2023`、`Peschel 2022`、`Wu 2024`、`Silva 2018`、`Murakami 2018`、`Raab 2024`、`Li 2022`、`Boroumand 2025`、`Iglesias 2024`、`Hu 2024`、`Lyu 2026`、`Stammer 2026`、`Awad 2026`、`Zou 2026`、`Goh 2015`、`Lange 2026`、`Borrego Varillas 2026` 等；
  2. **完整片段**：如 `[Iskhakov et al., Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]`；
  3. **局部编号**：`outcome.md` §6.6 用 `[1]–[8]` 引用 8 条 arXiv 编号，且仅在该节出现。

  三种格式混用导致：（a）同一文献在不同章节被不同方式引证（如 `Iskhakov 2012` vs `[Iskhakov et al., Opt. Lett. 37, 1919 (2012)]`）；（b）评审人无法把"作者—年份片段"映射到任何标准文献列表；（c）[n] 编号与正文其他位置无对应。
- 建议：选定一种格式（推荐顺序编码制，与 NSFC 面上项目惯例一致），全本统一：（1）正文中用 `[n]` 编号引用；（2）参考文献模块按编号顺序列出完整书目条目；（3）删除所有"作者—年份片段"和"完整片段"残留。如保留作者—年份制，须将所有文献条目按作者首字母排列，并保证正文片段与文献条目一一对应。
- action：rewrite

### 段落级深审：参考文献章内部无内容可审

由于 `references.md` 仅含占位符，下文转为对 `outcome.md` §6.6（局部编号引文唯一出现处）的逐条段落级审查。

#### §6.6 第 49 行（`[1]`）

> `[1] Rasputnyi A., et al. *High Harmonic Generation by Bright Squeezed Vacuum*. arXiv:2403.15337 (2024).`

#### [high] rigor — 关键支撑文献仅有 arXiv 编号，无正式出版信息
- 位置：§6.6 [1]；对照 §1.1 第 13 行、§1.2.2 第 35 行
- 问题：Rasputnyi 2024 是项目立项核心依据（"BSV 驱动固体 HHG 首例"），却被以仅含 arXiv 编号的形式列出，没有期刊/卷期/DOI。该文献在 2024–2026 年间是否已在 *Nature Photonics / PRL / Optica / Phys. Rev. X* 等期刊正式发表？需提交前核实；若未正式发表，须明确声明"arXiv 预印本，未同行评审"。
- 建议：补全期刊缩写、卷、页码、文章号、DOI；如确未发表，注明"preprint, not peer-reviewed"。同时核查 Rasputnyi 是否在 CLEO 2024 之后正式发表（§1.2.2 仅称"CLEO 2024 报道"，需明确为会议论文集还是正式期刊）。
- action：verify

#### [high] rigor — "首例"优先权主张与现有文献边界不清
- 位置：§6.6 [1] + §1.1 第 13 行 + §1.2.2 第 35 行
- 问题：项目文本称"BSV 驱动固体 HHG 首例 [Rasputnyi 2024]"，但 §2.7 Y2 与 §3.4 仍以"MoS₂ BSV-HHG 首例 / Nature Phys./PRL 首例论文"作为可交付。这种"已有首例但仍在申报体系内首例"的措辞由 [1] 文献支撑，但因无完整书目，评审人无法核查 Rasputnyi 工作的精确体系范围（气体？固体？TMDC？）。若 Rasputnyi 已在 MoS₂ 做过 BSV-HHG，则 §2.7/§3.4 的"首例"主张被自己的支撑文献推翻。
- 建议：明确"单层 TMDC 体系 BSV-HHG 首例"边界；若 Rasputnyi 已涵盖 TMDC，则删除"首例"措辞改为"系统化对照验证"。
- action：rewrite

#### §6.6 第 51 行（`[2]`）

> `[2] Lyu Z., Sun F., Yi S. *Attosecond quantum spectroscopy with entangled photon pairs*. arXiv:2604.06707 (2026).`

#### [high] rigor — 引用 2026 年预印本须警惕真实性与可获取性
- 位置：§6.6 [2]
- 问题：arXiv 编号 `2604.06707` 与 `2607.06395`/`2607.16477`/`2604.12838`/`2602.16454`/`2604.15085` 等本轮出现的 5 条 2026 年预印本，需核实：（a）是否真在 arXiv 公开可下载；（b）作者—题目对应是否准确；（c）是否经过同行评审。NSFC 评审对未发表的预印本引用相对宽容，但 arXiv 编号必须真实——若评审人检索失败，会严重损害可信度。
- 建议：提交前逐一打开 arXiv 链接核实标题、作者列表、摘要；若无法核实，替换为已正式发表的同类工作；若保留，须明确"preprint, 2026"。
- action：verify

#### [high] logic — [2] 的引用位置（§6.1）与支撑强度不匹配
- 位置：§6.6 [2] + outcome §6.1 第 7 行（核心科学成果）
- 问题：§6.1 称"本项目不主张笼统的 BSV-HHG 优先权……Lyu 等进一步预言谐波二阶关联的非单调阶次依赖可区分发射机制 [2]"。Lyu 等若为 2026 年预印本，且尚未正式发表，则其"预言"作为本项目核心成果的反证基线（"无论结果为增强、抑制或无显著差异，均报告效应量"）的引用强度偏弱——预印本可能后续被撤稿或修正。
- 建议：补充至少 1 篇已正式发表的支持性文献（如 *Nature Phys.* 2023–2024 上的阿秒量子光谱学论文），用正式发表工作做主基线，[2] 作为辅助参考。
- action：add

#### §6.6 第 53 行（`[3]`）

> `[3] Stammer P., Rivera-Dean J., Pisanty E. *Attosecond metrology of bright quantum light*. arXiv:2607.06395 (2026).`

#### [high] rigor — 关键理论锚点仅有 arXiv 编号
- 位置：§6.6 [3] + outcome §6.1 第 9 行（"压缩相位信息原则上可由亚周期观测提取[3]"）
- 问题：Stammer 等的工作在本项目中被用作"压缩相位信息可由亚周期观测提取"的理论基础；但只有 arXiv 编号，无期刊/DOI。若该工作未正式发表，作为方法学锚点的论证强度不足。
- 建议：核实是否已在 *Phys. Rev. Lett.* / *Phys. Rev. X* / *Nature Phys.* 发表；若仅 arXiv 预印本，标注年份与状态，并补充 1 条已正式发表的同类工作（如 Stammer 之前在 PRL 的工作）。
- action：verify

#### §6.6 第 55 行（`[4]`）

> `[4] Awad M., Späthe J., Yadav P. C., et al. *Measuring the dipole phase of Bloch-trajectory harmonics using a monolithic interferometer*. arXiv:2607.16477 (2026).`

#### [medium] rigor — 文献名称中"monolithic interferometer"需核实
- 位置：§6.6 [4]
- 问题：题目中含特殊字符（ä）、较长作者列表，需核实 arXiv 编号是否对应实际论文。Awad 等的具体工作是否真在 2026 年 arXiv 公开？题目与项目支撑点（"偶极相位恢复"）是否对应？
- 建议：核实 arXiv 链接；若项目论证不依赖该具体工作，可降低引用权重或替换。
- action：verify

#### §6.6 第 57 行（`[5]`）

> `[5] Zou X., Jurkovičová L., Weber A., et al. *2D quantum-path interference in high-harmonic generation driven by highly-bichromatic fields*. arXiv:2604.12838 (2026).`

#### [medium] rigor — "highly-bichromatic fields"应为"highly bichromatic fields"
- 位置：§6.6 [5]
- 问题：题目表述"highly-bichromatic"为复合形容词连字符用法，BibTeX 一般写作 "highly bichromatic"。若直接复制自 arXiv 元数据，需确认；若为项目撰写时手写，须核对。
- 建议：按 arXiv 实际标题为准；如需转写英文，按规范英文写作。
- action：verify

#### §6.6 第 59 行（`[6]`）

> `[6] Goh S. J., et al. *Single-shot fluctuations in waveguided high-harmonic generation*. arXiv:1507.04131 (2015).`

#### [high] rigor — 关键参考仅有 arXiv 编号，但 2015 年预印本应早已正式发表
- 位置：§6.6 [6]
- 问题：arXiv:1507.04131 为 2015 年预印本，至今已 11 年，按理应有正式发表版本（Goh 等常在 *Optics Express* / *Phys. Rev. STAB* 发表）。本项目以"单发统计设计参照 Goh 等的 HHG 涨落研究"使用该文献，但只列出 arXiv 编号，不规范。
- 建议：检索正式发表期刊，补全卷期页码 DOI。
- action：verify

#### §6.6 第 61 行（`[7]`）

> `[7] Lange C. S., Madsen L. B. *Edge states and quantum optical high-harmonic generation from topological insulators*. arXiv:2602.16454 (2026).`

#### [high] rigor — 2026 年预印本，且拓扑绝缘体与本项目体系对应度需论证
- 位置：§6.6 [7]
- 问题：Lange-Madsen 工作讨论"拓扑绝缘体边缘态的量子光 HHG"，与本项目核心体系（TMDC、莫尔、Mott）不完全一致。若引为"量子光 HHG 理论基础参照"，关联度较弱；若引为"拓扑体系对比"，需在正文中明确讨论该对比如何支撑项目结论。
- 建议：在正文中明确 Lange-Madsen 工作与本项目 TMDC 体系的对应关系（拓扑边界态 ↔ 谷极化 / Berry 曲率）；若论证不强，替换为更直接对应的固体量子光 HHG 理论文献。
- action：rewrite

#### §6.6 第 63 行（`[8]`）

> `[8] Borrego Varillas R., et al. *Roadmap on Attosecond Science*. arXiv:2604.15085 (2026).`

#### [high] rigor — Roadmap 类综述的引用方式与正式发表惯例不符
- 位置：§6.6 [8] + outcome §6.3 第 23 行
- 问题：Borrego Varillas 等的 "Roadmap on Attosecond Science" 通常发表于 *Journal of Physics B* 或 *New Journal of Physics*，且为综述性 roadmap，对单个研究项目的支撑度有限。arXiv:2604.15085 是否对应 2026 年最新版 roadmap，须核实。本项目引用其"将量子光学接口与协同数据分析框架列为重要发展方向"，但 roadmap 类文献作为"研究方法学合法性"的支撑偏弱——roadmap 是社区愿景，不等于同行评审结论。
- 建议：核实 arXiv 编号与正式发表状态；如用于"国际研究趋势判断"，保留但补充同行评审过的同类工作（如 *Nature Phys.* 2024–2026 上的阿秒科学综述）。
- action：verify

### 聚焦章节整体遗漏

#### [critical] rigor — 参考文献数量严重不足
- 位置：references.md 与全书引文
- 问题：可识别的外部引证约 13 条（含重复）：

  | 出现位置 | 文献 | 类型 |
  |---|---|---|
  | §1.2.1 | Wu/Schafer/Gaarde 2016 (PRA 94, 063403) | 已发表 |
  | §1.2.1 | Iglesias et al. 2024 (arXiv:2402.07850) | 预印本 |
  | §1.2.2 | Spasibko et al. 2012 (Opt. Express 20, 7507) | 已发表 |
  | §1.2.2 | Iskhakov et al. 2012 (Opt. Lett. 37, 1919) | 已发表 |
  | §1.2.2 | Rasputnyi 2024 (arXiv:2403.15337) | 预印本 |
  | §1.2.2 | Even Tzur et al. 2024 (PRR 6, 023064) | 已发表 |
  | §1.2.3 | Silva et al. 2018 (Nat. Photon. 12, 266) | 已发表 |
  | §1.2.3 | Murakami et al. 2018 (PRL 121, 057405) | 已发表 |
  | §2.3 | Rivera-Dean et al. 2023 (arXiv:2309.14435) | 预印本 |
  | §2.3 | Peschel et al. 2022 (PRB 106, L081408) | 已发表 |
  | §2.4 | Wu et al. 2024 (arXiv:2311.16655) | 预印本 |
  | §2.5 | Raab et al. 2024 (Opt. Express 32, 16284 / arXiv:2405.11859) | 已发表 |
  | §2.5 | Li et al. 2022 (PRL 129, 173001 / arXiv:2205.11161) | 已发表 |
  | §1.4 | Li et al. 2019 (arXiv:1908.07283) | 预印本 |
  | §1.4 | Boroumand et al. 2025 (arXiv:2505.22536) | 预印本 |
  | §3.1 | Hu et al. 2024 (PNAS 121, e2317656121) | 已发表 |
  | outcome §6.6 | Rasputnyi 2024 (重复) | 预印本 |
  | outcome §6.6 | Lyu 2026 (arXiv:2604.06707) | 预印本 |
  | outcome §6.6 | Stammer 2026 (arXiv:2607.06395) | 预印本 |
  | outcome §6.6 | Awad 2026 (arXiv:2607.16477) | 预印本 |
  | outcome §6.6 | Zou 2026 (arXiv:2604.12838) | 预印本 |
  | outcome §6.6 | Goh 2015 (arXiv:1507.04131) | 预印本 |
  | outcome §6.6 | Lange-Madsen 2026 (arXiv:2602.16454) | 预印本 |
  | outcome §6.6 | Borrego Varillas 2026 (arXiv:2604.15085) | 预印本 |

  合计外部文献 **~24 条**（去重后）。对于一个宣称建立"量子光 HHG 探针系统性方法论"的 4 年面上项目，参考文献数量应不少于 40–50 条（NSFC 面上项目惯例）。当前数量不足，且其中近一半为 arXiv 预印本（其中 6 条为 2026 年预印本，无法确认是否正式发表）。
- 建议：补全参考文献到 40–60 条，覆盖以下领域（每领域列举例）：
  - **BSV/非经典光物理基础**（≥5 条）：Slusher 1985、Wu 1987、Iskhakov 2012、Spasibko 2012、Manceau 2017 等；
  - **固体 HHG 基础**（≥5 条）：Ghimire 2011、Schubert 2014、Luu 2015、Ndabashimiye 2016、Vampa 2015、Hammond 2017 等；
  - **量子光 HHG 理论与实验**（≥8 条）：Pisanty 2019、Even Tzur 2024、Rasputnyi 2024、Boroumand 2025、Lyu 2026、Stammer 2026、Lewenstein 2021、Quintero-Britto 2023 等；
  - **TMDC / 莫尔 / Mott 体系 HHG**（≥5 条）：Liu 2017、Wu 2024、Silva 2018、Murakami 2018、Kogar 2020 等；
  - **多体 SBE 与 Bloch 形式化**（≥4 条）：Rivera-Dean 2023、Peschel 2022、Wu/Schafer/Gaarde 2016、de Abajo 2022 等；
  - **HHG 涨落统计与单发测量**（≥3 条）：Goh 2015、Hu 2024、Zou 2026 等；
  - **贝叶斯反演 / 神经网络反演**（≥3 条）：Baydin 2018、Karniadakis 2021、神经网络 surrogate for HHG 类工作；
  - **阿秒科学与量子光计量**（≥3 条）：Krausz 2009、Catoire 2018、Stammer 2026、Borrego Varillas 2026 等；
  - **国内同类工作**（≥3 条）：必须涵盖国内 BSV / 量子光 / TMDC HHG 同方向已发表工作，体现项目对国内研究现状的掌握。
- action：add

#### [critical] rigor — 6 条 2026 年 arXiv 预印本须核实真实性与可获取性
- 位置：outcome §6.6 [2][3][4][5][7][8]
- 问题：6 条引用为 2026 年 arXiv 编号（2602.16454、2604.06707、2604.12838、2604.15085、2607.06395、2607.16477）。其中至少 3 条为 2026 年 7 月（2607.xxxxx），而本年度为 2026 年 7 月底，引用当月新上传的预印本风险高——可能尚未被检索系统索引完整。
- 建议：
  1. 在提交前 1 周内逐条 arXiv 检索，核实编号、标题、作者、摘要；
  2. 检索失败者替换为已正式发表的同类工作；
  3. 若必须保留，标注"arXiv preprint, as of YYYY-MM-DD, not peer-reviewed"；
  4. 避免使用 2026 年下半年的极新预印本作为核心论断的唯一支撑。
- action：verify

#### [high] rigor — 关键支撑文献格式不完整，无 DOI/期刊卷期
- 位置：outcome §6.6 全部 8 条
- 问题：8 条 [n] 引文均仅含 `arXiv:xxxx.xxxxx (YYYY)`，没有期刊缩写、卷、页码、DOI。即使是预印本引用，也应在脚注或参考文献条目中包含 arXiv 永久链接（如 `https://arxiv.org/abs/2403.15337`），便于评审人直接访问。
- 建议：每条参考文献统一格式：
  ```
  [n] Author1 A. B., Author2 C. D., et al. Title of the paper.
       Journal Abbreviation Vol, Pages (Year). DOI: xx.xxxx/yyyy.
       arXiv:xxxx.xxxxx [quant-ph/physics.optics].
  ```
- action：rewrite

#### [high] rigor — 跨章节同一文献格式不一致
- 位置：全书
- 问题：同一文献在不同章节被不同方式引证，例如：
  - `Iskhakov 2012`：在 §1.2.2 第 28 行写 `[Iskhakov et al., Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]`；在 §2.1 第 26 行写 `参照 Iskhakov 2012 量化基线`；在 §3.1 第 7 行写 `参照 Iskhakov 2012, Spasibko 2012 的高增益参量下转换方案`；在 §3.2 第 17 行隐含提及。三种格式，且无完整条目映射。
  - `Rasputnyi 2024`：在 §1.1 第 13 行写 `[Rasputnyi 2024, arXiv:2403.15337]`；§1.2.2 第 35 行写 `[Rasputnyi A. et al., arXiv:2403.15337 (2024)]`；outcome §6.1 第 7 行写 `[1]`；outcome §6.6 第 49 行写 `[1] Rasputnyi A., et al. *High Harmonic Generation by Bright Squeezed Vacuum*. arXiv:2403.15337 (2024).`。
  - `Raab 2024`：在 §2.5 第 65 行写 `Raab 等 2024 的双色彩双色场合成方案 [arXiv:2405.11859]`；在 §3.2 第 18 行写 `Raab et al. 2024 [Opt. Express 32, 16284 (2024); arXiv:2405.11859]`。两种格式。
- 建议：选定一种引用格式，全文统一，并确保每条文献在正文出现的位置都用同一格式。
- action：rewrite

#### [high] rigor — 缺少国内同类工作引用
- 位置：references.md
- 问题：本项目为国内面上项目申请，立项依据（§1.2）声称"国内该方向几乎空白"，但全文未引用任何国内同方向工作。若国内确无相关工作，应在参考文献或正文中说明"作者检索日期为 YYYY-MM-DD，未发现国内同类工作"；若有（如国内量子光学/强场物理团队在 BSV、固体 HHG、阿秒方向的工作），则必须引用。
- 建议：
  1. 检索国内团队（中科院物理所、上海交大、清华、北大、国科大、华东师大等）在 BSV 制备、固体 HHG、阿秒科学方向 2020–2026 年的代表性论文；
  2. 在 §1.2 国内外研究现状中明确"国内该方向几乎空白"的判断依据（检索数据库、关键词、日期）；
  3. 至少引用 3–5 条国内相关工作以体现对国内研究现状的全面掌握。
- action：add

#### [medium] rigor — 部分文献引用与正文位置逻辑断裂
- 位置：outcome §6.6 + 正文各处
- 问题：outcome §6.6 列出的 8 条 [n] 引文仅在 outcome.md 自身使用；正文（§1.2、§2.3、§2.5 等）中所有"作者—年份片段"均无 [n] 编号对应。即同一文献在两套系统中重复登记，未形成统一索引。
- 建议：将 outcome §6.6 的 8 条编号引用合并进主参考文献列表，正文中相应位置改为 `[n]` 编号引用；或反之，将正文"作者—年份片段"全部纳入参考文献条目，删除 §6.6 独立编号。
- action：rewrite

#### [medium] rigor — 引用 arXiv 编号未注明学科分类
- 位置：outcome §6.6 全部 8 条；§1.2.2、§2.3、§2.5 等多处
- 问题：arXiv 编号应注明学科分类（如 `[quant-ph]`、`[physics.optics]`、`[cond-mat.mes-hall]`），便于评审人快速定位领域。当前仅列 `arXiv:xxxx.xxxxx`，无学科标注。
- 建议：每条 arXiv 引用后追加学科分类与永久链接，例如 `arXiv:2403.15337 [physics.optics]`。
- action：rewrite

#### [medium] rigor — 缺少作者全名规范
- 位置：outcome §6.6 [4] Awad M., Späthe J., Yadav P. C., et al.
- 问题：作者列表使用首字母缩写（`Awad M.`、`Späthe J.`、`Yadav P. C.`），符合 NSFC 惯例；但需核实姓名前缀（如 `Späthe` 含 ä）、作者完整名（首字母后是否需补全名）。
- 建议：NSFC 顺序编码制下，作者名通常仅列前 3 人 + et al.，且使用首字母缩写即可；保持当前格式即可，但须统一全文作者列表风格。
- action：verify

#### [low] rigor — [7] 与项目体系对应度偏弱，应替换或补充
- 位置：outcome §6.6 [7] Lange-Madsen
- 问题：Lange-Madsen 2026 涉及拓扑绝缘体边缘态的量子光 HHG，与本项目 TMDC/莫尔/Mott 体系不完全对应。若引为"量子光 HHG 一般理论参照"，可保留；若引为"具体体系对比"，需在正文 §1.2.3 或 §2.4 中明确讨论。
- 建议：在 §2.4 或新增小节"理论参照体系"中说明 Lange-Madsen 工作的拓扑边界态与本项目 Berry 曲率/谷极化的对应关系；否则替换为更直接对应的固体量子光 HHG 理论文献。
- action：rewrite

---

## 简要跨章节一致性检查

| 检查对 | 结论 | 说明 |
|---|---|---|
| references.md（独立章节）vs outcome §6.6（局部编号） | ❌ | 两套引文系统并存，未合并 |
| §1.2.2 完整片段 vs §2.1 作者—年份片段 | ⚠️ | 同一文献两种格式，需统一 |
| §1.4 创新点 2 引文 vs outcome §6.6 [n] | ❌ | §1.4 引用 `Li et al. 2019` `Boroumand et al. 2025` 未在 §6.6 编号内出现 |
| §3.4 探针方法学综述论文（投 Nat. Phys./PRL） vs outcome §6.4 论文 B | ⚠️ | 章节间成果类术语不完全对应（"综述论文"已被 §6.4 改写为"原创研究论文"），但 §3.4 文本未同步更新 |
| §1.2.2 Rasputnyi 2024 vs §2.7 Y2 "首例" | ⚠️ | 已有 BSV-HHG 首例文献 [Rasputnyi 2024]，[1] 又是该文献的支撑；"首例"边界需 §1.2.2 收紧 |
| §6.6 8 条 arXiv vs §1.2.2 已发表文献 | ⚠️ | §1.2.2 引用文献全部有期刊卷期，§6.6 全部仅 arXiv 编号，体系不一致 |
| 全文作者—年份片段（≥20 处）vs §6.6 编号引文（8 条） | ❌ | 两套系统不互通，评审人无法建立对应 |
| §6.6 [6] Goh 2015 仅 arXiv vs §3.1 Hu 2024 有 PNAS 完整信息 | ⚠️ | 体系不一致，Goh 应补正式发表信息 |
| §6.6 [8] Roadmap vs §6.3 论证强度 | ⚠️ | Roadmap 是社区愿景而非同行评审结论 |

---

## 上一轮问题修复确认（与第 6 轮相比）

| 第 6 轮相关问题 | 当前状态 | 证据 |
|---|---|---|
| 参考文献标准模块完全缺失（[critical]） | **未解决** | `references.md` 仍仅占位符 |
| `outcome.md` 缺失 | **已解决** | 文件已创建并扩展至 63 行 |
| 预期成果少于 200 字 | **已解决** | outcome.md 中文字符 2456，含成果矩阵 C1–C7 |
| `Q_F` 与 `QEF_vis` 层级不清 | **部分解决** | outcome §6.2 (3) 已明确"`Q_F` 为观测量，`QEF_vis` 为归一化指标"，但 §2.4、§1.4、§2.5 文本未完全同步更新 |
| 条件性 Mott 工作被包装为必达 | **已解决** | outcome §6.1/§6.5 已分层核心/条件性 |
| 实验方法无验收指标 | **已解决** | outcome §6.2 已给具体验收条件（σ_φ < 150 mrad、≥3 批重复、≥10⁴ 脉冲等） |
| Nature Phys./PRL 录用承诺 | **已解决** | outcome §6.4 明确"期刊仅作拟投方向，不作硬承诺" |
| "首例"优先权边界不清 | **部分解决** | outcome §6.1 明确"不主张笼统的 BSV-HHG 优先权"，但 §2.7/§3.4 仍有"首例论文"字样 |
| 数据集与代码成果缺失 | **已解决** | outcome §6.3 已含版本化数据集、代码、最小复现实例 |
| 期刊定位冲突（"综述论文投 PRL"） | **已解决** | outcome §6.4 明确"原创研究论文 2 篇，综述列为可选传播成果" |

相比上一轮：可确认改善 **6 项（5 项完全解决 + 1 项部分解决）**；新增本轮聚焦问题 **17 项**；未解决的旧问题 **1 项（参考文献模块）**。

---

## 问题清单（去重后）

### [critical] completeness — 参考文献模块完全缺失
- 位置：`references.md` 整文件
- 问题：仅含占位符，无任何文献条目
- 建议：完整重建，列出 40–60 条统一格式文献
- action：add

### [critical] rigor — 引文体系三种格式并存
- 位置：全书（作者—年份片段 / 完整片段 / 局部编号）
- 问题：评审人无法建立对应
- 建议：选定顺序编码制，全文统一
- action：rewrite

### [critical] rigor — 参考文献数量严重不足
- 位置：全书
- 问题：仅 ~24 条外部引证，远低于面上项目惯例
- 建议：补全至 40–60 条，覆盖各领域
- action：add

### [critical] rigor — 6 条 2026 年 arXiv 预印本须核实
- 位置：outcome §6.6 [2][3][4][5][7][8]
- 问题：可能未公开/未索引/未同行评审
- 建议：提交前逐一核实，失败者替换
- action：verify

### [high] rigor — 关键支撑文献 [1] Rasputnyi 2024 无正式出版信息
- 位置：§6.6 [1]
- 问题：项目核心依据仅有 arXiv 编号
- 建议：核实是否已在期刊正式发表
- action：verify

### [high] rigor — "首例"边界与 [1] Rasputnyi 边界需统一
- 位置：§1.1、§1.2.2、§2.7、§3.4 vs §6.6 [1]
- 问题：现有文献已支撑固体 BSV-HHG，但项目仍主张"MoS₂ 首例"
- 建议：收紧边界为"单层 TMDC 体系首例"，并在 §1.2.2 中检索证据
- action：rewrite

### [high] rigor — [2] Lyu 2026 预印本支撑强度不足
- 位置：§6.6 [2]
- 问题：作为核心成果反证基线，仅 2026 年预印本
- 建议：补充 1 条已正式发表的同类工作
- action：add

### [high] rigor — [3] Stammer 2026 方法学锚点须正式发表
- 位置：§6.6 [3]
- 问题：理论锚点仅有 arXiv 编号
- 建议：核实 PRL/PRX 发表状态
- action：verify

### [high] rigor — [6] Goh 2015 应有正式发表版本
- 位置：§6.6 [6]
- 问题：2015 年预印本不应仍无正式发表
- 建议：检索 Opt. Express/PRSTAB 等，补全卷期页码 DOI
- action：verify

### [high] rigor — [8] Roadmap 类引用支撑度偏弱
- 位置：§6.6 [8]
- 问题：综述类 roadmap 不等于同行评审结论
- 建议：保留作社区趋势参照，补充正式发表的同类综述
- action：add

### [high] rigor — 关键支撑文献格式不完整
- 位置：§6.6 全部 8 条
- 问题：均无期刊卷期 DOI/arXiv 永久链接
- 建议：统一格式，含全字段与永久链接
- action：rewrite

### [high] rigor — 跨章节同一文献格式不一致
- 位置：Iskhakov 2012、Rasputnyi 2024、Raab 2024 等多处
- 问题：同一文献在 3+ 种格式间切换
- 建议：选定一种格式，全文统一
- action：rewrite

### [high] rigor — 缺少国内同类工作引用
- 位置：references.md
- 问题：国内相关工作未引用
- 建议：检索并引用 3–5 条国内 BSV/HHG/阿秒方向论文
- action：add

### [medium] rigor — 引用 arXiv 编号未注明学科分类
- 位置：§6.6 全部 + 正文多处
- 问题：缺学科分类标注
- 建议：补 `[quant-ph]`、`[physics.optics]`、`[cond-mat.mes-hall]` 等
- action：rewrite

### [medium] rigor — 部分文献与正文位置逻辑断裂
- 位置：outcome §6.6 [n] vs 正文"作者—年份片段"
- 问题：两套系统并存
- 建议：合并为统一索引
- action：rewrite

### [medium] rigor — §3.4 论文类型与 §6.4 论文类型未同步
- 位置：method.md §3.4 vs outcome.md §6.4
- 问题：§3.4 仍写"探针方法学综述论文（投 Nat. Phys./PRL）"，§6.4 已改为"原创研究论文 2 篇"
- 建议：§3.4 同步更新
- action：rewrite

### [medium] rigor — [4] Awad、[5] Zou 标题表述需核实
- 位置：§6.6 [4][5]
- 问题：作者列表、特殊字符、复合形容词需核实
- 建议：核对 arXiv 实际标题
- action：verify

### [low] rigor — [7] Lange-Madsen 与项目体系对应度偏弱
- 位置：§6.6 [7]
- 问题：拓扑绝缘体与 TMDC/莫尔/Mott 不完全对应
- 建议：在正文补充对应关系论证，或替换文献
- action：rewrite

**去重后总计：18 个问题（critical: 4，high: 9，medium: 4，low: 1）。**

---

## 可执行的参考文献章重构指令

建议 writer 不要继续以"占位符"敷衍，而应按以下骨架一次重构：

### 1. 选定引用格式
推荐顺序编码制（NSFC 面上项目惯例）。全文统一：
- 正文中：`...机制[5,7]...`，`...已在文献[12]中报道...`
- 参考文献条目：按编号顺序排列，每条含完整字段

### 2. 参考文献数量与覆盖
至少 40–60 条，覆盖：

| 领域 | 最少条数 | 必含示例 |
|---|---:|---|
| BSV / 非经典光物理 | 5 | Slusher 1985、Wu 1987、Iskhakov 2012、Spasibko 2012、Manceau 2017 |
| 固体 HHG 基础 | 5 | Ghimire 2011、Schubert 2014、Luu 2015、Vampa 2015、Hammond 2017 |
| 量子光 HHG 理论与实验 | 8 | Pisanty 2019、Even Tzur 2024、Rasputnyi 2024、Boroumand 2025、Lyu/Stammer 2026、Lewenstein 2021 |
| TMDC / 莫尔 / Mott 体系 HHG | 5 | Liu 2017、Wu 2024、Silva 2018、Murakami 2018、Kogar 2020 |
| 多体 SBE / Bloch 形式化 | 4 | Rivera-Dean 2023、Peschel 2022、Wu/Schafer/Gaarde 2016、de Abajo 2022 |
| HHG 涨落 / 单发统计 | 3 | Goh 2015、Hu 2024、Zou 2026 |
| 贝叶斯 / 神经网络反演 | 3 | Baydin 2018、Karniadakis 2021、HHG 神经网络 surrogate 类 |
| 阿秒科学与量子光计量 | 3 | Krausz 2009、Catoire 2018、Borrego Varillas 2026 |
| 国内同类工作 | 3–5 | 中科院物理所 / 上海交大 / 清华 / 北大 / 国科大 / 华东师大 BSV/固体 HHG/阿秒方向 2020–2026 工作 |

### 3. 每条格式
```
[n] Author1 A. B., Author2 C. D., Author3 E. F., et al.
     Title of the paper in English sentence case.
     Journal Abbreviation, Vol(Issue): Start–End Pages (Year).
     DOI: xx.xxxx/yyyy.
     arXiv:xxxx.xxxxx [physics.optics].
```

### 4. 预印本处理
- 2015–2024 年 arXiv 预印本：必须检索是否有正式发表版本，如有则用正式发表条目，arXiv 作为备注；
- 2025 年预印本：尽量补正式发表版本，否则保留 arXiv + 注明"preprint"；
- 2026 年预印本：仅保留经独立核实可访问者，并在条目末尾注明"preprint, as of YYYY-MM-DD"。

### 5. 国内同类工作检索
- 检索数据库：CNKI、Web of Science、Scopus、arXiv（按国内机构筛选）；
- 关键词组合：`bright squeezed vacuum` + `中国 / 物理所 / 交大 / 清华`；`solid HHG` + `中国`；`高次谐波` + `TMDC / 莫尔 / 中国`；`量子光场` + `强场`；
- 检索日期：2026 年 X 月 X 日（提交前 1 周内）；
- 检索结果写入 §1.2 国内外研究现状末段，标注检索日期与结论。

### 6. 跨章节同步更新
- §1.4、§2.1–2.6、§3.1–3.2、outcome §6.1–§6.5 中所有"作者—年份片段"和"完整片段"全部替换为 `[n]` 编号引用；
- §3.4 "探针方法学综述论文（投 Nat. Phys./PRL）"改为"原创研究论文 2 篇（拟投方向 Nature Phys./PRL）"，与 outcome §6.4 对齐；
- §2.7、§3.4 中"首例"字样在 §1.2.2 检索证据基础上统一收紧为"单层 TMDC 体系首例"或删除。

---

## 对抗结论

- 本轮发现 **18 个去重问题**（critical: 4，high: 9，medium: 4，low: 1）。
- 模块完整性：7 个标准模块中，**4 个达到实质内容门槛，3 个仍为占位符状态（特色与创新 / 年度研究计划 / 参考文献，全部 [critical] 级缺失）**。
- 聚焦章节深审：references.md 完全空白，无文献条目可供段落级审查；outcome §6.6 局部编号 8 条引文存在格式不完整、2026 年预印本过多、跨章节不一致等问题。
- 相比上一轮：
  - 改善 **5 项**（完全解决：outcome.md 模块 / 预期成果内容 / 条件性 Mott 分层 / 验收指标 / Nature Phys. 承诺 / 期刊定位冲突；部分解决：`Q_F` 与 `QEF_vis` 层级、"首例"边界）；
  - 新增 **18 项**（主要来自参考文献模块深审，包括模块缺失、引文体系混乱、数量不足、预印本未核实、格式不完整、国内工作缺失、跨章节不一致等）；
  - 未解决 **1 项核心旧问题**：参考文献模块从第 6 轮到第 7 轮均未实质补齐，是当前最大短板。
- 是否达到输出标准：**否**。
  - 综合评分 0.55 < 0.80；
  - critical 4 个；
  - high 9 个 > 0；
  - medium 4 个 > 3。
- 返工优先级：
  - **P0（必须立即修复）**：
    1. 完整重建 `references.md`，列出 40–60 条统一格式文献；
    2. 统一全书引文格式（推荐顺序编码制），合并 outcome §6.6 与正文"作者—年份片段"；
    3. 同步修复 `sections/innovation.md` 与 `sections/plan.md` 两处占位符模块；
    4. 核实所有 2026 年 arXiv 预印本（6 条）的真实性、可访问性与同行评审状态。
  - **P1（重要修订）**：
    5. 补全 24 条 → 40+ 条文献，覆盖各领域；
    6. 引用 3–5 条国内同类工作；
    7. 收紧 §2.7、§3.4 "首例"边界；
    8. 同步 §3.4 与 outcome §6.4 的论文类型表述。
  - **P2（格式与表达）**：
    9. arXiv 编号加学科分类与永久链接；
    10. 作者—年份片段与 [n] 编号一一对应；
    11. 补全 §1.2 国内研究现状检索证据与日期。
- 下一轮建议：
  1. 先做参考文献章的全量重建与跨章节引文系统统一；
  2. 再做"特色与创新"与"年度研究计划"两章从占位符到实质内容的补齐；
  3. 最后做全书"成果—任务—年度—风险—参考文献"五位一体闭环检查。

---

## 评分
创新性：0.72
可行性：0.62
严谨性：0.42
完整性：0.40
综合评分：0.55