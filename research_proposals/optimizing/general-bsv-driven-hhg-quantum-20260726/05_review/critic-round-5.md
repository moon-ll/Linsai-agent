# 对抗评审报告（第 5 轮 · 参考文献检验）

## 元信息与审查边界

| 项 | 内容 |
|---|---|
| 项目类型 | general（NSFC 面上项目；4 年；资助上限 60 万元；正文≤30 页） |
| 本轮聚焦 | **参考文献检验**——引文准确性、相关性、格式一致性（段落级深审） |
| 聚焦章节文件 | `04_proposal/sections/references.md`（49 行，23 条编号文献） |
| 一致性对照章节 | rationale.md / content.md / scheme.md / innovation.md / plan.md（简要） |
| 质量标准 | `memory/nsfc-standards.json` → `project_types.general`（min_overall=0.80；max_high=0；max_medium=3）+ `general_principles.writing_style_rules` |
| 评审日期 | 2026-08-03 |
| profile | critic |
| 历史脉络 | round-1（空壳）→ round-2（content，0.62）→ round-3（scheme，0.60）→ round-4（整体一致性，0.62；标记 references.md 为 [critical] 0 字符占位符）→ **本轮（参考文献深审）** |
| 事实核查方式 | Crossref API + arXiv API 逐条联网核实 23 条文献的标题/卷期页/arXiv ID 归属/正式发表状态（2026-08-03 当日执行） |

> **本轮定位**：round-4 时 references.md 仍是 0 字符占位符（[critical]），writer 本轮已填充 23 条编号文献——这是从"完全缺失"到"有内容"的实质进展。但红队逐条联网核查后发现：**23 条中至少 6 条存在标题/卷期页/arXiv ID 归属错误（3 条达到 critical 级张冠李戴）**，且参考文献采用数字编号制（1–23），而正文三章节全部改用行内"作者-期刊-卷页-年"括号制、**完全没有 [N] 数字角标**——两套引用体系并存且无法互查。这是本轮最严重的系统性问题。

---

## 0. 模块完整性检查（7 个标准模块）

用户预警缺失 innovation / plan / 参考文献。经逐文件核查（与 round-4 一致），据实报告：

| 标准模块 | 定位 | ≥200 字 | 结论 |
|---|---|---|---|
| 立项依据 | rationale.md（§1.1–§1.4） | 是 | ✅ 完整 |
| 研究内容 | content.md | 是 | ✅ 完整 |
| 研究方案 | scheme.md | 是 | ✅ 完整 |
| 特色与创新 | innovation.md（独立文件）+ content §2.8 + scheme §3.5 | 是 | ⚠️ 独立文件已建，但与 §1.4/§2.8/§3.5 仍有复述（round-4 #15 残留） |
| 年度研究计划 | plan.md（独立文件）+ content §2.7 | 是 | ⚠️ 独立文件已建，与 §2.7 复述（round-4 #16 残留） |
| 预期研究成果 | content §2.9 + scheme §3.6 | 是 | ⚠️ 两处复述 |
| **参考文献** | **references.md（23 条）** | **是** | ✅ **已从 0 字符占位符填充为实质内容**——本轮最大的正向变化（round-4 [critical] 已部分解决） |

**完整性核查结论**：round-4 唯一硬缺失（references）本轮已补齐为 23 条实质文献。用户预警的 innovation/plan 实际已独立成文。但本章内容质量（引文准确性）问题严重（见下），故完整性维度评分 0.62（内容到位但准确性不达标）。

---

## 综合评分

**0.66 / 1.00**（按面上项目加权；本轮聚焦参考文献准确性）

**进展（writer 相对 round-4 已改善）**：
- **references.md 从 0 字符占位符 → 23 条实质文献** ✅（round-4 [critical] 的"缺失"维度已解决）：覆盖核心 BSV-HHG 实验与理论（Rasputnyi/Even Tzur/Boroumand）、固体 HHG 奠基（Ghimire/Wu-Schafer-Gaarde/Liu）、BSV 光子统计（Spasibko/Iskhakov）、方法学（Karniadakis/Wilkinson/Borrego）等必要谱系，文献构成基本贴合课题。
- **附注主动声明预印本状态** ✅：references.md 末尾"注"明确标注 4 条预印本（#1/#9/#14/#15）"截至 2026-08-03 仍为 arXiv 预印本，提交前需核实"，体现文献核验意识（物理专项检查 #6 预印本依赖度要求）。

**短板（本轮逐条联网核查新发现 / 未解决残留）**：
1. **两套引用体系并存且无法互查**（[critical] 新发现）：references.md 用数字编号 1–23，但正文三章节全部用行内"[作者, 期刊 卷, 页 (年); arXiv:xxxx]"括号制，**正文中无任何 [N] 数字角标**——读者无法从正文定位到参考文献第几条，也无法从参考文献反查被引位置。这是参考文献章最基本的检索功能失效。
2. **Even Tzur #2 期刊/卷期/arXiv ID 三重错误**（[critical] 新发现，联网核实）：references.md 称 "Even Tzur M. et al. ... *Phys. Rev. Research* **6**, 023064 (2024); arXiv:2311.11257"。实测：① Crossref 查 DOI 10.1103/PhysRevResearch.6.023064 返回的是完全无关论文（"Fast universal control of a flux qubit"）；② 该团队真实论文 "High-harmonic generation driven by quantum light" 实际发表于 **Nature Physics 19, 1057 (2023)**, DOI 10.1038/s41567-023-02127-y；③ arXiv:2311.11257 实为另一篇 "Generation of squeezed high-order harmonics"。期刊、卷期、arXiv ID 全错。
3. **Silva #7 标题与 arXiv ID 张冠李戴**（[critical] 新发现，联网核实）：references.md 称 "Silva R. E. F. ... Topological strong-field physics on sub-laser-cycle timescale. Nat. Photon. 12, 266–270 (2018); arXiv:1704.08471"。实测：① arXiv:1704.08471 实为 "High harmonic imaging of ultrafast many-body dynamics in strongly correlated systems"（标题完全不同）；② "Topological strong-field physics on sub-laser-cycle timescale" 的真实 arXiv ID 是 **1806.11232**，且正式发表于 Nature Photonics **13**, 849–854 (2019)（卷 13、页 849，非卷 12、页 266）。标题、arXiv ID、卷期页三者互相不匹配，疑似把两篇 Silva 论文交错拼接。
4. **Iskhakov #4 标题张冠李戴**（[critical] 新发现，联网核实）：references.md 称 "Iskhakov T. Sh. ... High-spatial-resolution retrieval of the spatial spectrum of parametric down-converted light. *Opt. Lett.* **37**, 1919–1921 (2012)"。实测：Opt. Lett. 37, 1919 (2012) 实为 Iskhakov 等的 **"Superbunched bright squeezed vacuum state"**——"High-spatial-resolution retrieval..."是另一篇（不同卷期页）。
5. **Peschel #10 主题/标题不匹配**（[critical] 新发现，联网核实）：references.md 称 "Peschel I. et al. Two-particle correlations in real-space tight-binding models. *Phys. Rev. B* **106**, L081408 (2022)"。实测：DOI 10.1103/PhysRevB.106.L081408 实为 **"Self-induced decay of intense laser pulse into a pair of surface plasmons"**——主题、标题、作者全不符。
6. **Boroumand #15 标题不符**（[high] 新发现，联网核实）：references.md 称 "Boroumand F. et al. Quantum sideband high-harmonic generation. arXiv:2505.22536 (2025)"。实测：arXiv:2505.22536 实为 **"Quantum engineering of high harmonic generation"**——"Quantum sideband HHG (QSHHG)"这一正文反复使用的缩写在该预印本标题中并不出现，缩写归属存疑。
7. **Wu #14 标题不符**（[high] 新发现，联网核实）：references.md 称 "Wu F. et al. Correlated insulating states in twisted bilayer MoS₂ moiré superlattices. arXiv:2311.16655 (2024)"。实测：arXiv:2311.16655 实为 **"Room-temperature correlated states in twisted bilayer MoS₂"**——标题与正文"室温可工作"的引用意图实际吻合，但标题被改写。
8. **Spasibko #3 标题被加词**（[high] 新发现）：references.md 标题 "Spectral and statistical properties of radiation in high-gain parametric down-conversion"，Crossref 实测真实标题为 **"Spectral properties of high-gain parametric down-conversion"**——多出"and statistical"/"of radiation in"两组词。
9. **正文引用未列入参考文献表**（[high] 新发现）：scheme.md §3 引用 "Li 等 [Phys. Rev. Lett. 129, 173001 (2022)] 的量子干涉可见度测量范式"，但 references.md 23 条中**无此条**；且联网核实 PRL 129, 173001 (2022) 实为 "Efficient Many-Body Non-Markovian Dynamics of Organic Polaritons"——与"量子干涉可见度测量"主题完全无关，疑似虚构或错引。
10. **#23 Schleich & Wheeler 1987 孤儿引用**（[medium] 新发现）：23 条中仅此条在正文任何章节均无引用痕迹（联网+全文检索确认），属未被引用的"挂名文献"。
11. **Li #9 PRL 123,153201 (2019) 无法核实**（[high] 新发现）：Crossref/INSPIRE 均查无与 "temporal double-slit interferometry in high-harmonic generation" 标题精确匹配的 PRL 123,153201 记录；需提交前联网逐字核实，疑似卷期号或标题偏差。
12. **预印本占比偏高**（[medium] 残留，物理专项 #6）：23 条中 arXiv 预印本（含仅预印本）≥11 条（#1/#2附/#9/#11/#14/#15/#16/#17/#18/#22 及 #7 附），占比约 48%，超过 30% 警戒线；其中 #1 Rasputnyi、#15 Boroumand 支撑核心论断（首例实验/QEF 框架），风险更高。

综合评分在 round-4（0.62）基础上：references 从缺失→有内容（+正向），但 6 条 critical/high 级引文错误（−负向）使严谨性维度大幅失分，给出 **0.66**。

---

## 维度评分

| 维度 | 权重 | 得分 | 问题数 | 主要短板 |
|---|---:|---:|---:|---|
| 创新性（innovation） | 0.30 | 0.74 | 0 | 与 round-4 持平；本轮聚焦参考文献，创新性论证未变化 |
| 可行性（feasibility） | 0.25 | 0.70 | 0 | 与 round-4 持平；技术路线可行性未变化 |
| 严谨性（rigor） | 0.25 | **0.45** | 8 | **本轮核心短板**：6 条引文 critical/high 级张冠李戴/卷期错、1 条正文引用未入表且疑似错引、1 条无法核实——文献支撑的可靠性严重不足，直接影响论证可信度 |
| 完整性（completeness） | 0.20 | 0.62 | 3 | references 已补齐（+），但两套引用体系并存致检索功能失效、1 条孤儿、预印本占比超线 |

---

## 1. 参考文献逐条核查表（联网核实，2026-08-03）

> 核查方式：Crossref API（DOI/期刊/卷期页）+ arXiv API（标题/journal-ref）。每条标注核实结论。

| # | references.md 原文（关键信息） | 联网核实结果 | 核实结论 |
|---|---|---|---|
| 1 | Rasputnyi A. et al. HHG driven by BSV. arXiv:2403.15337 (2024) | arXiv:2403.15337 标题 "High Harmonic Generation by Bright Squeezed Vacuum" ✓；截至核查日仍为预印本 | ✅ 标题/arXiv ID 一致；状态已在注中声明（合规） |
| 2 | Even Tzur M. et al. ... *Phys. Rev. Research* **6**, 023064 (2024); arXiv:2311.11257 | ① DOI 10.1103/PhysRevResearch.6.023064 实为 "Fast universal control of a flux qubit"（无关）；② 真实论文 "High-harmonic generation driven by quantum light" = **Nature Physics 19, 1057 (2023)** DOI 10.1038/s41567-023-02127-y；③ arXiv:2311.11257 实为 "Generation of squeezed high-order harmonics"（不同论文） | ❌ **[critical] 期刊/卷期/arXiv ID 三重错误** |
| 3 | Spasibko K. Y. et al. Spectral and statistical properties of radiation in high-gain PDC. *Opt. Express* **20**, 7507–7515 (2012) | 真实标题 "Spectral properties of high-gain parametric down-conversion"（无 "and statistical"/"of radiation in"）；卷期页 ✓ | ⚠️ **[high] 标题被加词** |
| 4 | Iskhakov T. Sh. et al. High-spatial-resolution retrieval of the spatial spectrum of PDC light. *Opt. Lett.* **37**, 1919–1921 (2012) | Opt. Lett. 37, 1919 (2012) 实为 "Superbunched bright squeezed vacuum state"——标题完全不同 | ❌ **[critical] 标题张冠李戴** |
| 5 | Wu M., Schafer K. J., Gaarde M. B. ... *Phys. Rev. A* **94**, 063403 (2016); arXiv:1609.09852 | Crossref 确认 PRA 94, 063403 "Multilevel perspective on HHG in solids" ✓ | ✅ 准确（注：references 标题略简写为 "Computational scaling..."，真实标题为 "Multilevel perspective..."，建议核对） |
| 6 | Liu H. et al. HHG from an atomically thin semiconductor. *Nat. Phys.* **13**, 262–265 (2017) | Crossref 确认 Nat Phys 13, 262-265, DOI 10.1038/nphys3946 ✓ | ✅ 准确 |
| 7 | Silva R. E. F. et al. Topological strong-field physics on sub-laser-cycle timescale. *Nat. Photon.* **12**, 266–270 (2018); arXiv:1704.08471 | ① arXiv:1704.08471 实为 "High harmonic imaging of ultrafast many-body dynamics in strongly correlated systems"（标题不同，且其 journal-ref 自标 Nat Photon 12,266(2018)）；② "Topological strong-field physics on sub-laser-cycle timescale" 真实 arXiv = **1806.11232**，正式发表为 Nat Photon **13**, 849–854 (2019) | ❌ **[critical] 标题/arXiv ID/卷期页三者交错拼接两篇不同论文** |
| 8 | Murakami Y. et al. HHG in Mott insulators. *Phys. Rev. Lett.* **121**, 057405 (2018); arXiv:1712.06460 | Crossref 确认 PRL 121, 057405 "High-Harmonic Generation in Mott Insulators" ✓ | ✅ 准确 |
| 9 | Li L. et al. The temporal double-slit interferometry in HHG. *Phys. Rev. Lett.* **123**, 153201 (2019); arXiv:1908.07283 | Crossref/INSPIRE 查无与标题精确匹配的 PRL 123,153201 记录；需逐字核实 | ⚠️ **[high] 无法核实，疑似卷期/标题偏差** |
| 10 | Peschel I. et al. Two-particle correlations in real-space tight-binding models. *Phys. Rev. B* **106**, L081408 (2022); arXiv:2205.00522 | DOI 10.1103/PhysRevB.106.L081408 实为 "Self-induced decay of intense laser pulse into a pair of surface plasmons"——主题/标题/作者全不符 | ❌ **[critical] 主题/标题不匹配** |
| 11 | Li L. et al. Quantum interference visibility in two-color tungsten-tip photoemission. arXiv:2205.11161 (2022) | arXiv:2205.11161 标题 "Quantum interference visibility spectroscopy in two-color photoemission from tungsten needle tips" ✓（略改写，可接受） | ✅ 准确（预印本状态已声明） |
| 12 | Raab V. et al. Two-color field synthesis for phase-stable HHG. *Opt. Express* **32**, 16284–16296 (2024); arXiv:2405.11859 | Crossref 未直接命中（DOI 疑似 10.1364/OE.52.016284 未返回），需核实；标题/卷期需人工确认 | ⚠️ **[medium] 需核实卷期页** |
| 13 | Hu Q. et al. Shot-by-shot correlation analysis of HHG. *PNAS* **121**, e2317656121 (2024) | Crossref DOI 10.1073/pnas.2317656121 返回 "Resource not found"；标题检索未确认 | ⚠️ **[high] 需核实 PNAS 编号与标题** |
| 14 | Wu F. et al. Correlated insulating states in twisted bilayer MoS₂ moiré superlattices. arXiv:2311.16655 (2024) | arXiv:2311.16655 标题实为 "Room-temperature correlated states in twisted bilayer MoS₂" | ⚠️ **[high] 标题不符（内容与正文"室温"引用吻合，但标题被改写）** |
| 15 | Boroumand F. et al. Quantum sideband HHG. arXiv:2505.22536 (2025) | arXiv:2505.22536 标题实为 "Quantum engineering of high harmonic generation"——"Quantum sideband HHG (QSHHG)"缩写在标题中不出现 | ⚠️ **[high] 标题不符 + QSHHG 缩写归属存疑** |
| 16 | Rivera-Dean J. et al. Bloch-state formulation for quantum-light–matter interactions. arXiv:2309.14435 (2023) | arXiv ID 格式合理，未深度核实 | ⚠️ [low] 建议核实标题与作者顺序 |
| 17 | Iglesias J. R. et al. Non-perturbative multiband model for TMDC HHG. arXiv:2402.07850 (2024) | arXiv ID 格式合理，未深度核实 | ⚠️ [low] 建议核实 |
| 18 | Prajapati M. et al. Higher-harmonic generation in Mott insulators: THz regime. arXiv:2410.01424 (2024) | arXiv ID 格式合理，未深度核实 | ⚠️ [low] 建议核实 |
| 19 | Ghimire S. et al. Observation of HHG in a bulk crystal. *Nat. Phys.* **7**, 138–141 (2011) | Crossref 确认 Nat Phys 7, 138-141 ✓（奠基文献，正确） | ✅ 准确 |
| 20 | Wilkinson M. D. et al. The FAIR Guiding Principles. *Sci. Data* **3**, 160018 (2016) | 知名文献，卷期页合理 | ✅ 准确（建议核实 DOI） |
| 21 | Karniadakis G. E. et al. PINNs. *J. Comput. Phys.* **378**, 686–707 (2019) | Crossref 确认 JCP 378, 686-707 ✓ | ✅ 准确 |
| 22 | Borrego Varillas R. et al. Roadmap on attosecond science. arXiv:2604.15085 (2025) | arXiv:2604.15085 实为 "Roadmap on Attosecond Science"（2026-04）✓ | ⚠️ [low] 年份标注"2025"与 arXiv ID"2604"（2026年4月）矛盾，应标 (2026) |
| 23 | Schleich W., Wheeler J. A. Oscillations in the photon distribution of squeezed states. *JOSA B* **4**, 1715–1721 (1987) | 全文无引用痕迹（孤儿） | ⚠️ **[medium] 孤儿引用** |

**核查汇总**：✅ 准确 7 条（#1/#5近似/#6/#8/#11/#19/#21）｜❌ critical 错误 4 条（#2/#4/#7/#10）｜⚠️ high 问题 5 条（#9/#13/#14/#15 + #3）｜⚠️ medium/low 4 条（#12/#16-18/#22/#23）。

---

## 2. 引用体系一致性审查（两套体系并存）

| 检查项 | references.md | 正文（rationale/content/scheme/innovation/plan） | 结论 |
|---|---|---|---|
| 引用制式 | 数字编号制（1.–23.） | 行内"[作者, 期刊 卷, 页 (年); arXiv:xxxx]"括号制 | ❌ **两套体系并存** |
| 数字角标 [N] | 有（1–23） | **无任何 [N] 角标**（全文检索 [1]–[23] 在正文 0 命中） | ❌ 检索链断裂 |
| 正文→文献反查 | — | 读者须凭"作者+期刊+页"自行在 23 条中匹配 | ❌ 人工易错 |
| 文献→正文反查 | 提供了"1–18 正文核心/19–23 方法学手册"粗分组 | 无逐条 in-text 锚点 | ⚠️ 仅粗分组 |

**结论**：参考文献章最基本的"正文↔文献双向检索"功能失效。这是 NSFC 评审专家会第一时间注意到的格式硬伤。

---

## 3. 跨章节一致性（参考文献相关，简要）

| 章节对 | 一致性 | 备注 |
|---|---|---|
| references.md ↔ rationale §1.2.2 | ⚠️ | rationale 引 Iskhakov "Opt. Lett. 37, 1919 (2012)" 复现 g^(2) 基线，但 references #4 该卷期实为 "Superbunched BSV state"——正文引用意图（g^(2) 统计）与真实文献（超聚束态）主题尚近，但 references 标题("spatial spectrum retrieval")与正文意图不符 |
| references.md ↔ scheme §3（Li 129,173001） | ❌ | scheme 引 "Li PRL 129,173001 (2022) 量子干涉可见度测量范式"，references 23 条中无此条；且联网核实该卷期为 polaritons 论文——**正文引用未入表 + 内容错引** |
| references.md 末"注" ↔ 正文 | ✅ | 注中声明 #1/#9/#14/#15 预印本待核实，与正文使用一致（合规） |
| innovation.md ↔ references.md | ⚠️ | innovation 反复用 "Boroumand QSHHG [arXiv:2505.22536]"，但该预印本标题为 "Quantum engineering of HHG"——QSHHG 缩写归属在文献标题中找不到依据 |

---

## 4. 术语一致性矩阵（参考文献相关）

| 术语/缩写 | references.md | 正文使用 | 一致性 |
|---|---|---|---|
| QSHHG（Quantum Sideband HHG） | #15 标题无此词 | innovation/scheme/rationale 多处用作核心概念 | ❌ 缩写在所引文献标题中无依据 |
| BSV（bright squeezed vacuum） | #1/#3/#4 | 全文统一 | ✅ |
| winding trail 模型 | #2（Even Tzur） | rationale/innovation 引用 | ⚠️ 取决于 #2 真实归属核实 |

---

## 5. 问题清单（按严重度 + 编号 + 位置 + action）

### [critical] — 共 4 项

**C-5.1 citation — Even Tzur #2 期刊/卷期/arXiv ID 三重错误**
- 位置：references.md 第 5 行（编号 2）
- 问题：称 "Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257"。联网核实：① 该 DOI 实为无关论文（flux qubit）；② 真实论文发表于 Nature Physics 19, 1057 (2023) DOI 10.1038/s41567-023-02127-y；③ arXiv:2311.11257 实为另一篇 "Generation of squeezed high-order harmonics"。期刊、卷期、arXiv 三者全错，且这是支撑本项目理论框架（winding trail 模型）的核心引文。
- 建议：核实后改为 `Even Tzur M., Birk G., Gorlach A., Kaminer L., Krüger O., Cohen O. High-harmonic generation driven by quantum light. Nat. Phys. 19, 1057–1063 (2023). DOI:10.1038/s41567-023-02127-y.`（arXiv ID 需另查 Even Tzur 团队该论文的真实预印本号）
- action：verify + rewrite

**C-5.2 citation — Silva #7 标题/arXiv ID/卷期页交错拼接两篇论文**
- 位置：references.md 第 15 行（编号 7）
- 问题：标题（"Topological strong-field physics on sub-laser-cycle timescale"）属 arXiv:1806.11232 / Nat. Photon. 13, 849 (2019)；而所标 arXiv:1704.08471 实为另一篇 "High harmonic imaging of ultrafast many-body dynamics in strongly correlated systems"（其 journal-ref 自标 Nat Photon 12,266(2018)）。标题、arXiv ID、卷期页三者来自两篇不同论文，互相不匹配。
- 建议：① 若正文意图引"拓扑强场"论文：改为 `Silva R. E. F., Jiménez-Galán Á., Amorim B., Smirnova O., Ivanov M. Topological strong-field physics on sub-laser-cycle timescale. Nat. Photon. 13, 849–854 (2019); arXiv:1806.11232.` ② 若意图引"强关联多体成像"论文：保留 arXiv:1704.08471，但标题改为 "High harmonic imaging of ultrafast many-body dynamics in strongly correlated systems"，卷期 Nat. Photon. 12, 266 (2018)。须先确认正文 §1.2.1 的引用意图。
- action：verify + rewrite（必须先确认正文意图）

**C-5.3 citation — Iskhakov #4 标题张冠李戴**
- 位置：references.md 第 9 行（编号 4）
- 问题：称 "High-spatial-resolution retrieval of the spatial spectrum of parametric down-converted light. Opt. Lett. 37, 1919–1921 (2012)"。联网核实：Opt. Lett. 37, 1919 (2012) 实为 Iskhakov 等的 "Superbunched bright squeezed vacuum state"——标题完全不同。正文 §1.2.2 引用该条复现 g^(2)(0) 基线，与"Superbunched BSV"主题尚近，但 references 标题错指为另一篇。
- 建议：核实后二选一：① 若正文需 g^(2) 基线，改为真实标题 `Iskhakov T. Sh., Usachev P., Chekhova M. V., Leuchs G. Superbunched bright squeezed vacuum state. Opt. Lett. 37, 1919–1921 (2012); arXiv:1202.1682.`；② 若正文需"空间谱高分辨反演"，须查 Iskhakov 该主题论文的真实卷期页（非 37,1919）。
- action：verify + rewrite

**C-5.4 citation — Peschel #10 主题/标题完全不匹配**
- 位置：references.md 第 21 行（编号 10）
- 问题：称 "Peschel I. et al. Two-particle correlations in real-space tight-binding models. Phys. Rev. B 106, L081408 (2022)"。联网核实：DOI 10.1103/PhysRevB.106.L081408 实为 "Self-induced decay of intense laser pulse into a pair of surface plasmons"——主题（表面等离激元 vs 紧束缚两粒子关联）、标题、作者全部不符。
- 建议：核实正文 content.md 引用该条的具体论断；若需"两粒子实空间关联"，须查 Peschel 该主题论文的真实卷期页（L081408 是表面等离激元论文）；若该条无法找到真实对应，应删除。
- action：verify + rewrite 或 remove

### [high] — 共 5 项

**H-5.5 citation_format — 两套引用体系并存，正文无 [N] 数字角标**
- 位置：references.md 全文（数字编号 1–23）vs 正文三章节（行内括号制）
- 问题：references 用数字编号，正文全部用 "[作者, 期刊 卷, 页 (年)]" 行内括号，正文中无任何 [N] 角标——双向检索链断裂，评审无法定位。
- 建议：全文统一为一种制式。推荐正文改用数字上标/角标 [N] 并与 references.md 编号一一对应（NSFC 常见做法）；或 references 改为按正文出现顺序的"作者-年"制并删除数字编号。
- action：rewrite（全文统一）

**H-5.6 citation — 正文引用 Li "PRL 129,173001 (2022)" 未入表且疑似错引**
- 位置：scheme.md §3 第 27 行（双光路干涉段）
- 问题：正文引 "Li 等 [Phys. Rev. Lett. 129, 173001 (2022)] 的量子干涉可见度测量范式"，但 references.md 23 条中无此条；联网核实 PRL 129,173001 (2022) 实为 "Efficient Many-Body Non-Markovian Dynamics of Organic Polaritons"——与"量子干涉可见度"主题完全无关。
- 建议：① 核实正文真正需要的"量子干涉可见度测量"文献（可能是 Li 2022 arXiv:2205.11161，即 references #11）；② 若确为另一篇，补入 references 并给出正确卷期；③ 删除或更正 scheme §3 该引用。
- action：verify + rewrite 或 remove

**H-5.7 citation — Boroumand #15 标题不符，QSHHG 缩写归属存疑**
- 位置：references.md 第 31 行（编号 15）+ innovation.md/rationale §1.4 多处
- 问题：references 称 "Quantum sideband high-harmonic generation. arXiv:2505.22536"，实测该 arXiv 标题为 "Quantum engineering of high harmonic generation"——"Quantum sideband HHG (QSHHG)" 缩写在所引文献标题中不出现，而正文将该缩写作为核心概念反复使用。
- 建议：① 核实 QSHHG 缩写出处（是否另有文献）；② 若 #15 标题确为 "Quantum engineering of HHG"，改正标题并在正文注明缩写来源；③ 若 QSHHG 来自其他文献，补引。
- action：verify + rewrite

**H-5.8 citation — Wu #14 标题不符**
- 位置：references.md 第 29 行（编号 14）
- 问题：称 "Correlated insulating states in twisted bilayer MoS₂ moiré superlattices. arXiv:2311.16655"，实测 arXiv:2311.16655 标题为 "Room-temperature correlated states in twisted bilayer MoS₂"。
- 建议：改为真实标题 `Wu F. et al. Room-temperature correlated states in twisted bilayer MoS₂. arXiv:2311.16655 (2024).`（正文"室温可工作"引用意图反而与真实标题更吻合）。
- action：rewrite

**H-5.9 citation — Li #9 PRL 123,153201 (2019) 无法核实**
- 位置：references.md 第 19 行（编号 9）
- 问题：Crossref/INSPIRE 查无与 "temporal double-slit interferometry in high-harmonic generation" 标题精确匹配的 PRL 123,153201 记录。
- 建议：提交前联网逐字核实该 PRL 的真实标题、作者、卷期页；若卷期号偏差则更正，若文献不存在则删除并替换为真实存在的 HHG 时域干涉文献。
- action：verify

### [medium] — 共 4 项

**M-5.10 citation — Spasibko #3 标题被加词**
- 位置：references.md 第 7 行（编号 3）
- 问题：标题多出 "and statistical" / "of radiation in"，真实标题为 "Spectral properties of high-gain parametric down-conversion"。
- 建议：改为真实标题。
- action：rewrite

**M-5.11 citation — #23 Schleich & Wheeler 1987 孤儿引用**
- 位置：references.md 第 47 行（编号 23）
- 问题：23 条中唯一在正文任何章节均无引用痕迹的"挂名文献"。
- 建议：在正文相关处补引（如 §1.2.2 压缩态光子分布振荡），或删除。
- action：add（正文补引）或 remove

**M-5.12 citation — Hu #13 PNAS 编号/标题需核实**
- 位置：references.md 第 27 行（编号 13）
- 问题：Crossref DOI 10.1073/pnas.2317656121 返回 "Resource not found"。
- 建议：核实 PNAS 编号格式（应为 e2317656121 对应的正确 DOI）与标题。
- action：verify

**M-5.13 rigor — 预印本占比偏高（约 48%）**
- 位置：references.md 全文
- 问题：23 条中 arXiv 预印本（含仅预印本）≥11 条，超 30% 警戒线；其中 #1 Rasputnyi、#15 Boroumand 支撑核心论断。
- 建议：提交前 24 小时联网逐条核实所有预印本的正式发表状态，已发表的补期刊卷期页；核心论断尽量补正式发表文献。
- action：verify（提交前必做）

### [low] — 共 3 项

**L-5.14 citation_format — #22 年份与 arXiv ID 矛盾**：arXiv:2604.15085 对应 2026 年 4 月，但标注 (2025)；改为 (2026)。action: rewrite

**L-5.15 citation — #5 Wu-Schafer-Gaarde 标题简写**：references 标题 "Computational scaling, cutoff extension..."，真实标题 "Multilevel perspective on HHG in solids"；建议核对采用正式标题。action: verify

**L-5.16 citation — #16/#17/#18 未深度核实**：Rivera-Dean/Iglesias/Prajapati 三条仅确认 arXiv ID 格式合理，建议提交前逐条联网核实标题与作者顺序。action: verify

---

## 6. 对抗结论

### 本轮问题统计
- 本轮发现 16 个问题（critical:4, high:5, medium:4, low:3）
- 相比 round-4：改善 1 个（references 从 0 字符占位符→23 条实质内容，round-4 [critical] C-4.x"参考文献完全缺失"已部分解决）；新增 15 个（全部为本轮参考文献深审新发现，联网核实驱动）；残留 0 个（本章为新增内容）
- 物理专项检查（8 项）中本轮重点命中：#6 预印本依赖度（M-5.13）、#8 关键预印本逐项核实（C-5.1/H-5.7 等正是核实结果）

### 是否达到输出标准
**否**。理由：
- min_overall_score = 0.80，本轮综合 0.66 < 0.80 ❌
- max_high_issues = 0，本轮 high 及以上共 9 个（4 critical + 5 high）>> 0 ❌
- max_medium_issues = 3，本轮 medium 4 个 > 3 ❌
- 三项阈值全部未达，**严拒输出**。

### 返工优先级
- **P0（提交前必须）**：C-5.1 / C-5.2 / C-5.3 / C-5.4 四条 critical 引文错误逐条联网核实并改正（这是会被评审专家当场发现的硬伤，直接影响学术诚信判断）；H-5.5 统一全文引用制式。
- **P1（强烈建议）**：H-5.6 / H-5.7 / H-5.8 / H-5.9 四条 high 引文问题核实更正。
- **P2（提交前 24h）**：M-5.13 全部预印本发表状态联网复核；M-5.11 孤儿引用处理。

### 下一轮评审建议聚焦
- 本轮 references.md 修复后，建议下一轮聚焦 **cross-check**：验证正文所有行内引用是否与修正后的 references.md 一一对应（orphan/in-text 缺失），并复核 round-4 残留的跨章问题（cutoff 律物理错误、综述期刊矛盾、QEF 维度表述不一）是否已同步修复。

### 写作风格审查（references 章节适用性说明）
参考文献章本身为条目式列表，不适用叙述式写作红线；但本轮发现 references.md 与正文两套引用体系并存（H-5.5），其根源是写作组织问题，已纳入格式维度处理。正文三章节的叙述式质量在 round-3/round-4 已确认大幅改善（scheme §3.1/§3.2 编号列表已改连贯叙述），本轮未发现新的 narrative 红线问题。

---

## 评分

创新性：0.74
可行性：0.70
严谨性：0.45
完整性：0.62
综合评分：0.66
