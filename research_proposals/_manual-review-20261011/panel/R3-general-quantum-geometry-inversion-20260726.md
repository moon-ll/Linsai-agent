# R3 引用审校评审报告 — general-quantum-geometry-inversion-20260726

> R3 引用审校（期刊文献编辑视角）
> 评审时间：2026-10-11
> 评审对象：research_proposals/optimizing/general-quantum-geometry-inversion-20260726/04_proposal/sections/references.md（55 条）

## ① 程序化对账表

| 指标 | 数值 |
|------|------|
| 正文引用集合（rationale/content/scheme 三节合并） | 54 个独立编号 [1–55]（[41] 缺失） |
| references.md 编号集合 | 55 个 [1–55]（[41] 在列） |
| 正文引用编号集合（去掉 [41]） | 54 个 |
| references.md 编号集合（含 [48] 双条） | 55 条（其中 [48] 占两条） |

**缺失（正文有但 references 无）**：无  
**孤立（references 有但正文无）**：[41]（Onida, Reining, Rubio 2002 RMP）  
**重复（references 内同一编号两次）**：[48] 出现两次——Wang et al. 2023 Nature（正文实际引用对象）+ de-la-Peña et al. 2025 arXiv:2512.03987（正文未引用）

| 维度 | 数值 |
|------|------|
| 正文覆盖率 | 54/54 = **100%** |
| references 中孤立条目占比 | 1/55 = 1.8% |
| 引用编号冲突（references 内） | 1/55 = 1.8%（[48]） |

## ② 联网核实记录（按风险降序抽样 14 条）

| 条目 | arXiv/DOI | 检索源 | 核实结果 |
|------|-----------|--------|----------|
| [4] Sala Nat. Mater. 2026 | 10.1038/s41563-026-02617-3 | https://www.nature.com/articles/s41563-026-02617-3 | DOI 可解析，真实存在。实验材料为 Sb₂Te₃（不是 Bi₂Te₃） |
| [9] Stammer arXiv:2605.28236 | 2605.28236 | https://arxiv.org/abs/2605.28236 | 真实，圆偏振量子光与石墨烯/MoS₂ |
| [12] Khurelbaatar arXiv:2605.21925 | 2605.21925 | https://arxiv.org/abs/2605.21925 | 真实，$e^{-2r}$ SQL + $r_\text{opt}\approx1.6$ |
| [13] Gothelf PRA 113, 063107 (2026) | 10.1103/cxff-kky6 | https://arxiv.org/abs/2602.04370 | arXiv 2602.04370 Journal ref: PRA 113, 063107 (2026)，Related DOI = 10.1103/cxff-kky6 ✓ |
| [15] Weber PRA 113, 063111 (2026) | 10.1103/d2pt-xp7x / arXiv:2510.12545 | https://arxiv.org/abs/2510.12545 | arXiv 真实，Picard-Lefschetz 理论 |
| [21] Du PRB 113, 245147 (2026) | 10.1103/n4gk-jxpc / arXiv:2605.01388 | https://arxiv.org/abs/2605.01388 | arXiv 真实，filling-dependent crossover |
| [22] Lange PRL 135, 043603 (2025) | 10.1103/wyk5-k8tk | https://arxiv.org/abs/2503.15932 | arXiv:2503.15932，作者 Lange/Hansen/Madsen ✓ |
| [29] Baykusheva Nat. Mater. 25, 937-943 (2026) | 10.1038/s41563-026-02517-6 / arXiv:2601.20695 | https://arxiv.org/abs/2601.20695 | arXiv 真实，Floquet 工程 Sr₂CuO₃ |
| [40] Cárdenas arXiv:2604.13901 | 2604.13901 | https://arxiv.org/abs/2604.13901 | 真实，MoS₂ vs NbSe₂ TD-HSEX |
| [43] Gothelf PRA 111, 063105 (2025) | 10.1103/PhysRevA.111.063105 / arXiv:2502.11803 | https://arxiv.org/abs/2502.11803 | arXiv 真实，"Harmonic Generation in a Crystal Driven by Quantum Light" |
| [47] Ilin arXiv:2604.20388 | 2604.20388 | https://arxiv.org/abs/2604.20388 | 真实，arXiv 标题含拼写错误 "opt-state High Armonics"，references.md 已修正为 "Solid-State High Harmonics" |
| [48] de-la-Peña arXiv:2512.03987 | 2512.03987 | https://arxiv.org/abs/2512.03987 | 真实，但与 Wang et al. 共用 [48] 编号 |
| [52] Kang Nat. Phys. 21, 110-117 (2024) | 10.1038/s41567-024-02678-8 / arXiv:2412.17809 | https://arxiv.org/abs/2412.17809 | arXiv 真实，CoSn kagome QGT |
| [28] Jabed npj Quantum Mater. 11, 12 (2026) | 10.1038/s41535-025-00842-8 / arXiv:2506.03251 | https://arxiv.org/abs/2506.03251 | arXiv 真实，Bi₂Te₃ 谷间散射 |

未做联网复核的（属于经典文献或风险低）：[1,2,3,7,8,10,11,14,16,17,18,19,20,24,25,26,27,30,32-39,42,44,45,46,49,50,51,53,54,55]。

## ③ 意见列表

| 编号 | severity | 条目 | 问题 | 原文摘录 | 核实结果/检索源 | 修改建议 |
|------|----------|------|------|----------|-----------------|----------|
| R3-01 | **critical** | [48] | 编号双重占用 | `[48] Wang et al. ... Nature 621, 487-492` 与 `[48] †de-la-Peña ... arXiv:2512.03987` 共用 | 正文仅 1 次引用 [48]（指向 Wang），de-la-Peña 未被引用 | 把 de-la-Peña 改为 [56]，插入 references.md 末尾 |
| R3-02 | **critical** | [41] | 孤立条目，正文未引用 | `[41] Onida, G., Reining, L. & Rubio, A. Rev. Mod. Phys., 2002, 74: 601-659` | 正文无 [41] 引用 | **建议删除 [41]**，或在正文某处补 [41] 引文 |
| R3-03 | **major** | [13]/[43] | 正文把两篇合并表述 | content.md `[13]在 2026 年证明近似正 P 表示...` | [13] Gothelf 2026 PRA 113, 063107 + [43] Gothelf 2025 PRA 111, 063105 均为独立工作 | 把 [13]/[43] 各归其具体论点 |
| R3-04 | **major** | [4] | 实验材料 Sb₂Te₃ 未在正文显式说明 | references.md `[4] Sala, G. ... Probing the quantum metric of 3D topological insulators. Nat. Mater., 2026` | https://www.nature.com/articles/s41563-026-02617-3 已核实 | 正文首句加"Sb₂Te₃ 薄膜"以避免 Bi₂Te₃ 误解 |
| R3-05 | **minor** | [47] | arXiv 原标题含拼写错误 | arXiv:2604.20388 标题含 "opt-state" 与 "High Armonics" 拼写错 | references.md 修正合理 | 若需严格誊写，应在条目末尾加 erratum 备注 |
| R3-06 | **minor** | [22] | DOI 未直接通过 PRA 站点抓取 | DOI 10.1103/wyk5-k8tk 被反爬 | arXiv 2503.15932 的"Related DOI" 字段二次确认 | 无需修改 |
| R3-07 | **minor** | [48] (de-la-Peña) | simulations 拼写复核 | references.md 用复数 simulations | arXiv 原文亦用复数 | 撤回怀疑，无错 |

## ④ 总体判断

| 维度 | 评价 |
|------|------|
| DOI/arXiv 真实性 | 高：所有抽检条目（14 条）均经 arXiv 摘要或 Nature 全文确认存在 |
| 正文—references 对账 | 正文覆盖率 100%（54/54），但存在 1 条孤立（[41]）+ 1 条编号冲突（[48]） |
| 事实归属 | 抽查中未发现作者顺序错误、年份错配、虚构条目 |

**critical 条数**：2 条（[48] 编号双重占用 + [41] 孤立条目）  
**建议删除条数**：1 条（[41]）  
**建议改号条目**：1 条（[48] de-la-Peña → [56]）  
**正文覆盖率**：54/54 = 100%

## 汇报

critical 条 2、建议删除条 1（[41]）、建议改号 1 条（[48]→[56]）、覆盖率 100%（54/54）。14 条联网核实全部通过真实性核查；本课题需在 M1 修改阶段处理 [48] 编号冲突与 [41] 孤立条目。
