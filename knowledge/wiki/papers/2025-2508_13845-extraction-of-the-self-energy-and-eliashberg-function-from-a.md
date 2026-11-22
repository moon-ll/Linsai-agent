---
title: "2025-2508.13845-extraction-of-the-self-energy-and-eliashberg-function-from-a"
type: "papers"
created: "2026-11-01T20:11:59Z"
updated: "2026-11-15T15:09:20Z"
tags: []
related: ["2025-2508_13845-extraction-of-the-self-energy-and-eliashberg-function-from-arpes", "2508.13845", "ARPES", "Eliashberg-函数", "SrTiO3", "arpes", "moire-强场探测", "wikilink", "强场超快", "最大熵法", "石墨烯", "贝叶斯反演", "贝叶斯推断", "超快"]
source_raw: "2025-2508.13845-extraction-of-the-self-energy-and-eliashberg-function-from-a.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
updated_at: "2026-11-08T01:02:39Z"
merged_from: ["wiki/papers/2025-2508_13845-extraction-of-the-self-energy-and-eliashberg-function-from-arpes.md", "wiki/papers/2508.13845.md"]
---

• 蒸馏完成。产物已落盘：

  - 路径：`knowledge/wiki/papers/2025-2508_13845-extraction-of-the-self-energy-and-eliashberg-function-from-arpes.md`
  - 结构：五要素齐全（研究问题 / 背景 / 方法 / 发现 / 局限与开放方向），摘要级（digest_hint=abstract），无 frontmatter，供管线注入 `source_raw` / `digest_level`
  - 纪律核对：
    - 全文档约 1200 字，超过 200 字质量门
    - 引用均用 `[[wikilink]]`（[[ARPES]]、[[最大熵法]]、[[贝叶斯推断]]、[[Eliashberg-函数]]、[[SrTiO3]]、[[石墨烯]] 等）
    - 唯一保留的数值 `npj Comput. Mater. 12, 172 (2026)` 直接来自 raw 原文，未编造任何摘要未给出的参数
    - 方法节按摘要级从简：未虚构温度/分辨率等参数表，并在开放方向节明确标注「如需方法卡须回全文核对原值」
    - 挂课题点：ΔΣ(ω) 重构方法可作文案 `general-moire-strong-field-probe-20260726` 的定量反演工具储备


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：xARPES（最大熵-贝叶斯 ARPES 自能/Eliashberg 函数反演）

**原理**：ARPES 直接测得的是谱函数，而自能 Σ(ω) 以实部（色散重整化）与虚部（寿命展宽）的形式编码了电声子、电电子、电杂质三类相互作用贡献；从谱函数反演 Eliashberg 函数是典型病态逆问题，旧做法须把能带线性化并对参数手工赋值，主观误差大。xARPES 把最大熵法（MEM）推广到 curved dispersion（弯曲色散）体系：以最大熵先验对反演解做正则化，在拟合谱函数的同时求解 Eliashberg 函数；再引入贝叶斯推断对模型参数与超参数做联合优化，得到自洽且带不确定度估计的解，从而把 ΔΣ(ω) 及各散射通道贡献一致地提取出来。在 SrTiO3 二维电子液与锂掺杂石墨烯两套独立高质量实验数据上，分别提取的 Eliashberg 函数达到前所未有的一致性，验证了该数值流程的稳健性。

**林赛理解**：

在 general-moire-strong-field-probe-20260726 的语境里，这套 ΔΣ(ω) 重构是少数能把实验谱定量反演为微观散射核（Eliashberg 函数）的工具：若把强场/超快探测得到的瞬态谱函数变化喂给同类最大熵-贝叶斯反演，就有望把瞬态电声耦合强度做成可标定、带误差棒的观测量，为莫尔体系强场探针提案提供定量反演的方法学储备；它同时提醒我，ARPES 端任何『耦合变强/变弱』的结论都应走这种贝叶斯反演路线，而不是目测色散与展宽就下判断。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 方法载体 | xARPES 代码 | 本文 |
| 反演目标量 | 自能 ΔΣ(ω) 与 Eliashberg 函数 | 本文 |
| 散射通道分解 | 电声子 / 电电子 / 电杂质 三通道 | 本文 |
| 核心数值手段 | 最大熵法推广至弯曲色散 + 贝叶斯推断联合优化 | 本文 |
| 验证体系 | SrTiO3 二维电子液与锂掺杂石墨烯（两套独立高质量数据） | 本文 |
| 发表信息 | npj Comput. Mater. 12, 172 (2026) | 本文 |
| arXiv 编号 | 2508.13845 | 2508.13845 |

**适用边界**：适用于拥有高质量 ARPES 谱函数并能给出可靠色散模型的体系（弱信号或色散建模差时病态性会放大）；本卡基于摘要级信息撰写、未含温度/分辨率等具体数值参数，引用任何原值前须回 arXiv 2508.13845 全文核对。
**代表作**：van Waas, Berthod, Berges, Marzari, Dil, Poncé, npj Comput. Mater. 12, 172 (2026)（arXiv:2508.13845）
*方法卡回补 2026-11-01*


## 合并自「2025-2508_13845-extraction-of-the-self-energy-and-eliashberg-function-from-arpes」

# Extraction of the self energy and Eliashberg function from angle resolved photoemission spectroscopy using the xARPES code

## 研究问题（Research Question）

能否从 [[ARPES]] 谱函数出发，系统性地一致提取自能 ΔΣ(ω)（电声子 / 电电子 / 电杂质各项贡献），而不是依赖线性化能带近似与手工参数赋值的旧有流程？本文以 xARPES 代码为工具，核心目标是实现 Eliashberg 函数（[[Eliashberg-函数]]，电声耦合谱函数 α²F(ω)）从实验数据中的自动化、可复现重构。

## 背景（Background）

[[ARPES]] 测得的谱函数隐含电子自能信息，但传统提取 ΔΣ(ω) 的方法受限于两处人为环节：能带需先线性化处理，各贡献项权重靠手工赋值，导致结果对操作者敏感、难以跨数据集比对。已有 [[最大熵法]]（maximum entropy method）用于谱分析，但推广到 curved dispersion（弯曲色散）真实能带体系的 Eliashberg 函数提取仍是空白。本文已发表于 npj Comput. Mater. 12, 172 (2026)。

## 方法（Data & Method）

作者将 [[最大熵法]] 推广到 curved dispersion 体系用于 Eliashberg 函数提取，并引入 [[贝叶斯推断]] 对提取流程做联合优化，消除线性化与手工赋值两处人为环节。方法在 xARPES 代码中实现，并在两组独立高质量实验数据上验证：[[SrTiO3]] 二维电子液与锂掺杂 [[石墨烯]]。

## 发现（Main Results & Findings）

- 提出从 ARPES 谱函数一致提取自能 ΔΣ(ω)（电声子/电电子/电杂质贡献）的系统性方法，摆脱线性化能带与手工赋值的旧局限。
- 在 [[SrTiO3]] 二维电子液和锂掺杂 [[石墨烯]] 两组独立实验数据上验证：两套数据各自提取出的 Eliashberg 函数达到前所未有的一致性，说明方法不依赖特定材料体系，可跨数据集复现。
- 该工作是 ΔΣ(ω) 重构精度方法论的最直接支撑。

## 局限与开放方向（Limitations & Open Questions）

本文为摘要级蒸馏，未含定量参数（温度、能量分辨率、动量网格等），如需按方法卡格式整理 xARPES 提取流程的装置/序列/参数表，须回到全文核对原值。方法当前针对平衡态 ARPES 谱；将其推广到 [[超快]] 时间分辨 ARPES 或强场扰动下的自能演化提取，是摘要中未覆盖的开放方向。与课题（[[强场超快]] / [[moire-强场探测]]）的关联点：ΔΣ(ω) 高精度重构方法可作为强场条件下电子关联信号定量反演的工具储备。

## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：xARPES 最大熵法 + 贝叶斯推断的 ARPES 自能与 Eliashberg 函数一致提取

**原理**：将最大熵法推广到 curved dispersion 真实能带体系，引入贝叶斯推断对提取流程联合优化，从 ARPES 谱函数系统性一致提取自能 ΔΣ(ω)（电声子/电电子/电杂质各项贡献）并自动重构 Eliashberg 函数 α²F(ω)——摆脱线性化能带近似与手工参数赋值两处人为环节；在 SrTiO₃ 二维电子液与锂掺杂石墨烯两组独立实验数据上验证，提取结果达到前所未有的跨数据集一致性（方法不依赖特定材料体系、可复现）。

**适用边界**：摘要级：温度/能量分辨率/动量网格等定量参数在全文；方法针对平衡态 ARPES 谱，推广到超快时间分辨 ARPES 或强场扰动下的自能演化提取为开放方向；ΔΣ(ω) 高精度重构可作为强场条件电子关联信号定量反演的工具储备。
**代表作**：Extraction of the self energy and Eliashberg function from ARPES using the xARPES code, npj Comput. Mater. 12, 172 (2026), arXiv:2508.13845
*方法卡回补 2026-11-01*


## 合并自「2508.13845」

## 深度解析

（来自简报深度分析）

## 阅读笔记

### general-moire-strong-field-probe-20260726

**标题**：Extraction of the self energy and Eliashberg function from angle resolved photoemission spectroscopy using the xARPES code
**作者**：Thomas P. van Waas、Christophe Berthod、Jan Berges、Nicola Marzari、J. Hugo Dil、Samuel Poncé（欧洲理论光谱设施/日内瓦大学/不来梅大学/PSI）
**出处**：npj Comput. Mater. 2025-08-19；arXiv:2508.13845

### 研究问题（Research Question）
如何从角分辨光电子能谱（ARPES）band map 中**一致地**提取电子自能 Σ(E) 与 Eliashberg 函数 α²F(ω)，特别是当色散关系是弯曲（非线性）时。既有方法依赖能带线性化（Lorentzian 拟合）并靠人工指定各散射通道（电子-声子/电子-电子/电子-杂质）的量级，作者要解决的核心是：自能三分量分解此前是"目视判断"而非定量、无偏流程。

### 研究背景（Background）
ARPES 是唯一能给出**各向异性**电子-声子耦合（EPC）的实验手段（光学电导、隧穿只能给出各向同性 Eliashberg 函数）。Shi 等 2004 年用最大熵法（MEM）从 Be 表面态首次反演出 α²F(ω)，此后该方法被用于 MgB₂、掺杂石墨烯、CsV₃Sb₅、杯状氧化物等众多体系。但现有 ARPES 工具（PyARPES、pesto、NavARP、ERLabPy）多体功能有限：仅支持单一**线性**色散、无矩阵元修正、无法把 Σ 分解为 Σ^ph、Σ^el、Σ^imp。Chien 2009 已指出用 Lorentzian 拟合弯曲色散会引入偏置，这一缺口一直悬置。

### 研究方法（Methods）
工作流三段式：费米边拟合 → MDC 拟合 → MEM + 贝叶斯推断优化循环。核心是引入**矩阵元修正（MEC）**，拟合光强 P(E,η) = ∫dη' Q(η-η')·{B̃ + Σ_n |M_n(η')|²·A_n}，其中非相互作用色散用多项式描述；经巧妙改写，抛物线色散只需 1 个拟合参数 η_n^c（线性色散则无需参数），用无量纲拟合量 {r̃_n(E_j), γ̃_n(E_j)} 拟合后按式 (10)(11) 反解 Σ′、−Σ″。Σ 按 Matthiessen 规则分解为 Σ^ph+Σ^el+Σ^imp，其中 Σ^el 采用满足 Fermi液体行为、粒子-空穴对称、Kramers-Kronig 一致性及 |E|⁻² 衰减的解析形式（式 13，紫外标度 W_n 由用户指定），Σ^imp 取静态虚部 −iΓ_n^imp。α²F(ω) 由 Fan-Migdal 核 K(E,ω)（digamma 函数）反演得到，先验函数 m_n(ω) 保证半正定，hyperparameter a 用 "chi2kink" 方法确定。贝叶斯推断（Bryan 算法）把五个模型参数 m_n^b/v_n^F、k_n^F、Γ_n^imp、λ_n^el、h_n 全部纳入优化，消除人工偏置。代码以 GPL-v3 发布为 Python 包 xARPES（Python ≥3.10，依赖 LMFIT 与 scipy.optimize.minimize）。

### 主要发现与核心结论（Main Results）
模型数据验证（ΔE=2.5 meV、Δη=0.1°、噪声 0.025%）：ΔE→0 时 Σ̃(E) 与真值达到 **95% 置信区间重叠**；用线性色散拟合则 χ²≈7.7 N_L（真值应为 ≈N_L），量化了 Lorentzian 方法的偏置。参数恢复精度：k^F 误差 0.004%、m^b 误差 0.5%、Γ^imp 误差 0.4%，λ^el 偏低 6%、λ^ph 偏高 7%（二者互补，总 λ 误差仅 3%）。**SrTiO₃ 用例**（0.7% Nb 掺杂，SrTi₀.₉₉₃Nb₀.₀₀₇O₃，T=20 K）：优化得 m_IR^b=0.59 m_e、k_IR^F=0.141 Å⁻¹、Γ_IR^imp=16.5 meV、λ_IR^ph=0.46（对比外支 λ_OR^ph=0.63、λ_OL^ph=0.68）；LO4/TO4模在 2 meV 内重现（ω_TO4=69 meV、ω_LO4=84 meV）；左右支 Eliashberg 函数欧氏距离 **M=0.0099**。**省略矩阵元会使 Σ(E) 改变超过2 倍**（Σ_OR^NM≈2×Σ_OR，且 IL/IR 的 Σ^ph 出现非物理负值）。**石墨烯用例**（Li 掺杂、Si 插层、Co(0001) 衬底，取自 Usachov 2018）：α²F 峰在 ω=166 meV，另有 ω=35 meV、85 meV 谱重；λ_L^ph=0.48、λ_R^ph=0.53，Γ_L^imp=115.6 meV、Γ_R^imp=120.9 meV，λ^el=0；两支欧氏距离 **M=0.0067**，而省略费米边修正后 M 恶化至 0.022（>3 倍）。

### 潜在研究方向（Future Directions）
物理模型上三条路线：实现更高阶多项式色散；引入高阶声子过程（自能层面的自洽计算、或直接对谱函数做 cumulant 展开）；把目前仅限 Fermi 液体的 Kramers-Kronig 一致唯象模型库扩展到边缘 Fermi 液体、强等离激元耦合等量子材料。实现层面：当前只拟合孤立 MDC、未处理有限能量分辨率的卷积效应，下一步应直接从二维光强提取 α²F(ω)；扩展文件格式支持、实验几何适配、与既有可视化代码接口；引入机器学习自动选择拟合窗口、以神经网络替代优化循环。作者也点明：实验提取的 α²F(ω) 只依赖能带与交换声子能量，而理论上还依赖电子初始能量与动量，故比较须满足特定条件（"费米面 Eliashberg 函数"近似）。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：xARPES：从 ARPES 一致提取自能与 Eliashberg 函数的开源流程（矩阵元修正 + MEM/贝叶斯）

**原理**：三段式工作流（费米边拟合→MDC 拟合→MEM+贝叶斯优化）从 ARPES band map 一致提取自能 Σ(E) 与 Eliashberg 函数 α²F(ω)：引入矩阵元修正消除弯曲色散的 Lorentzian 拟合偏置，Σ 按 Matthiessen 规则分解为电声/电子-电子/杂质三分量，五个模型参数全部纳入贝叶斯优化消除人工指定——GPL-v3 Python 包发布。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 模型数据验证精度 | ΔE→0 时 Σ̃(E) 与真值 95% 置信区间重叠；k^F 误差 0.004%、m^b 误差 0.5%、总 λ 误差 3% | 主要发现 |
| SrTiO₃ 用例 | λ_IR^ph = 0.46，ω_TO4 = 69 meV/ω_LO4 = 84 meV（2 meV 内重现），两支 Eliashberg 距离 M = 0.0099 | 主要发现 |
| 矩阵元修正必要性 | 省略 MEC 使 Σ(E) 改变超 2 倍（含非物理负值） | 主要发现 |
| 石墨烯用例 | α²F 主峰 166 meV，λ_L/R^ph = 0.48/0.53；省略费米边修正 M 恶化 3 倍（0.0067→0.022） | 主要发现 |

**适用边界**：仅拟合孤立 MDC（未处理有限能量分辨率卷积）；Σ^el 唯象模型限 Fermi 液体；实验 α²F 只依赖能带与交换声子能量（与理论对比须满足费米面近似）；高阶声子过程/强等离激元体系未覆盖。
**代表作**：van Waas et al., Extraction of the self energy and Eliashberg function from ARPES using the xARPES code, npj Comput. Mater. (2025)（arXiv:2508.13845）
*方法卡回补 2026-10-29*

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2508_13845-extraction-of-the-self-energy-and-eliashberg-function-from-arpes]]
- [[2508.13845]]
- [[ARPES]]
- [[Eliashberg-函数]]
- [[SrTiO3]]
- [[arpes]]
- [[moire-强场探测]]
- [[wikilink]]
- [[强场超快]]
- [[最大熵法]]
- [[石墨烯]]
- [[贝叶斯反演]]
- [[贝叶斯推断]]
- [[超快]]
<!-- /linsai-wikilinks -->
