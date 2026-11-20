---
title: "2024-2402_14321-non-relativistic-spin-splitting-in-compensated-magnets-that"
type: "papers"
created: "2026-08-29T04:51:14Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["2402.14321", "Berry 曲率", "arpes", "general-order-parameter-ultrafast-readout-20260727", "交变磁性（Altermagnetism）", "交变磁性（altermagnetism）", "反铁磁自旋电子学", "强场超快", "强场超快光学", "强场驱动", "自旋劈裂", "莫尔超晶格", "超快自旋动力学", "量子几何", "非线性光学"]
source_raw: "2024-2402.14321-non-relativistic-spin-splitting-in-compensated-magnets-that.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:41:57Z"
merged_from: ["wiki/papers/2402.14321.md"]
---

• # Non-relativistic spin splitting in compensated magnets that are not altermagnets

  ## 林赛的理解

  这篇工作对我们的强场超快光学与阿秒探测研究意味着一类新的“零净磁化但强自旋劈裂”靶材正在进入视野。传统交错磁体（altermagnets）因为旋转对称性保护，在布里渊区中心 Γ 点仍保持自旋简并；而 Yuan 等人指出的这类“非交错磁体”补偿反铁磁体，由于相反自旋子晶格之间不存在任何晶体对称性连接，无自旋-轨道耦合（SOC）时 Γ 点就直接劈裂。从实验角度看，Γ 点的劈裂最容易被光场访问：强场近红外或中红外脉冲可以直接在 Γ 点附近驱动自旋分辨的带间跃迁，产生自旋极化的电子布居或非线性光学响应；同时零净磁化保证了样品在超快时间尺度上的鲁棒性，避免了铁磁体中杂散场和磁畴运动带来的复杂性。三元氮化物 MnXN₂ 体系兼具高 Néel 温度、宽可调带隙（0.19–2.45 eV）和强共价键，是连接量子几何（Berry 曲率、量子度量）与强场驱动超快自旋动力学的理想材料平台。特别是 Mn₂SiSnN₄ 在 Γ 点的 332 meV 劈裂，为我们探测“补偿磁体中的纯自旋电流”和阿秒尺度的自旋翻转动力学提供了具体可计算的体系。

  ## 研究问题

  论文要回答的核心问题是：是否存在一类补偿反铁磁体（AFMs），它们表现出非相对论自旋劈裂（NRSS），却不能被归类为当前文献中流行的“交错磁体”（altermagnets）？如果存在，它们的对称性指纹是什么？能否在真实材料体系中通过第一性原理计算加以验证？进一步地，这类材料在 Γ 点的自旋劈裂是否会带来比传统交错磁体更优越的、不被交替自旋极化抵消的自旋电流生成能力？

  ## 研究背景

  反铁磁体长期被认为具有净零宏观磁化并因此具有自旋简并能带，在自旋电子学中主要扮演被动角色。1964 年 Pekar 和 Rashba 首次提出自旋劈裂反铁磁体的概念。近年来，理论和实验工作重新发现了这种“自旋劈裂反铁磁体”：Yuan 等人用磁对称性条件将 NRSS 反铁磁体划分为第四类自旋劈裂原型 SST-4；Šmejkal 等人随后引入“altermagnetism”一词，强调通过 proper 或 improper 晶体旋转操作连接相反自旋子晶格，导致动量空间中自旋劈裂符号交替变化，且在 Γ 点保持自旋简并。然而，SST-4 分类同时包含共线性和非共线性自旋 AFMs，而 altermagnetism 仅用于共线自旋磁体；并且，旋转对称性对产生 NRSS 并非必要。论文由此提出：存在相反自旋子晶格之间没有任何晶体对称性连接的补偿 AFMs，它们也呈现 NRSS，但属于与交错磁体不同的新子类。

  ## 研究方法

  研究结合磁对称性分析与密度泛函理论（DFT）计算：

  - **对称性框架**：引入“无 SOC 的磁空间群”（MSG without SOC）概念，将 NRSS AFM 区分为两个子类：子晶格由对称性连接的属 III 型 MSG（交错磁体），子晶格无对称性连接的属 I 型 MSG（非交错磁体）。
  - **计算材料**：三元锰氮化物 MnXN₂（X = Si, Ge, Sn）及其阳离子有序变体，重点研究 MnSiN₂ 和有序 Mn₂SiSnN₄。
  - **第一性原理**：采用 DFT-SCAN 泛函计算（非）相对论自旋极化能带结构；对 MnSiN₂ 采用实验 Rietveld 精修中子散射确定的 G 型共线反铁磁序（沿 c 轴）。
  - **结构筛选**：对 Mn₂SiSnN₄ 比较 wurtzite-kesterite 与 wurtzite-stannite 两种阳离子有序结构，确定能量更低且动力学稳定的 kesterite 相（声子色散等细节见支持材料）。

  ## 主要发现与核心结论

  1. **MnSiN₂ 作为交错磁体候选**：其含 SOC 的 MSG 为 Pn′a₂2′₁，无 SOC 的 MSG 为 Pna′2′₁（III 型）。两个相反自旋的 MnN₄ 四面体通过 `{2001|0, 0, 1/2}`（二重旋转加平移）连接，满足交错磁体定义。计算得到的非相对论能带在高对称 k 路径（如 Γ−Y、Γ−X−S−Y 等）上保持自旋简并，而在对角路径上出现 NRSS。

  2. **Mn₂SiSnN₄ 作为“非交错磁体”NRSS 材料**：由于 Si⁴⁺（配位数 4 的 Shannon-Prewitt 半径 0.26 Å）与 Sn⁴⁺（0.55 Å）的显著尺寸差异，形成有序的 wurtzite-kesterite 相。结构弛豫给出 Si−N 键长 1.75 Å、Sn−N 键长 2.06 Å；黑、白两种 MnN₄ 单元的平均 Mn−N 键长分别为 2.11 Å 和 2.09 Å，导致可忽略的净磁化 6×10⁻³ μB 每原子。阳离子有序破坏了原先连接相反自旋子晶格的二重旋转和镜面对称性，使无 SOC 的 MSG 降为 Pc（I 型），不存在连接相反自旋子晶格的任何对称性。

  3. **Γ 点自旋劈裂的定量结果**：Mn₂SiSnN₄ 的 SCAN 带隙为 1.13 eV，比 MnSiN₂（2.45 eV）和 MnSnN₂（0.19 eV）的平均带隙小 0.19 eV。由于整体晶体对称性降低，Wyckoff 位从 4a（Pna2₁）分裂为 2a（Pc），自旋劈裂在整个布里渊区被解锁，包括高对称方向 Γ 点；价带顶在 Γ 点仅高于带边 140 meV。定量地，Γ 点的自旋劈裂达到 332 meV，与文献中 MnF₂ 预言的巨自旋劈裂相当。

  4. **SOC 的影响**：对 MnSiN₂，加入 SOC 后 MSG 变为 Pn′a₂2′₁，其中 `{m₀₁₀|1/2, 1/2, 0}` 和 `{2′₀₀₁|0, 0, 1/2}` 操作保证高对称 k 路径上的自旋简并不会被移除，与相对论 DFT 计算一致。对 Mn₂SiSnN₄，无 SOC 时已无保护对称性，SOC 会进一步降低对称性并消除简并。此外，在 MnSiN₂ 中，Dzyaloshinskii-Moriya 相互作用可能诱导沿 b 轴的弱铁磁性，中子散射测得的 canting 角小于 1°；这种弱铁磁性也会移除 Γ 点简并，但自旋极化方向沿 b 轴，与 AFM 诱导的 NRSS 贡献不同。

  ## 潜在研究方向

  1. **实验验证**：利用自旋分辨角分辨光电子能谱（spin-resolved ARPES）或输运测量直接探测 Mn₂SiSnN₄ 在 Γ 点的 332 meV 自旋劈裂，确认其非交错磁体身份。
  2. **薄膜与器件化**：探索 MnXN₂ 及有序三元氮化物的薄膜外延生长、界面工程及其在自旋流生成、自旋劈裂力矩器件中的应用。
  3. **超快自旋动力学**：用强场激光研究这类材料中带间相干、自旋极化电流的飞秒/阿秒动力学，尤其是 Γ 点大劈裂带来的直接光致自旋极化。
  4. **对称性驱动的材料筛选**：基于无 SOC 的 MSG I 型（子晶格无对称性连接）与 III 型（有旋转对称性连接）开发高通量筛选流程，寻找更多非交错磁体 NRSS 材料。
  5. **弱铁磁性与多铁耦合**：在极性 MnSiN₂ 类材料中，深入研究 SOC 诱导的弱铁磁序如何与 NRSS 竞争或协同，探索磁电耦合与多铁效应。
  6. **拓扑与关联物理**：检验这些三元氮化物是否存在拓扑能带反转、Weyl 点或莫尔/低维极限下的新奇关联态。

  ## 与林赛研究的关联

  - **HHG 与阿秒探测**：Γ 点的直接自旋劈裂为强场驱动提供了“动量锚点”，圆偏振或偏振整形的强场脉冲可优先驱动一个自旋支，产生自旋分辨的高次谐波，用于阿秒尺度的自旋动力学成像。
  - **强场驱动与量子几何**：这些半导体/小带隙体系的强场带间/带内动力学与 Berry 曲率、量子度量紧密耦合，可用于设计新型非线性光-物质相互作用和光致反常霍尔/能斯特效应。
  - **交变磁与新自旋纹理**：Mn₂SiSnN₄ 代表的“非交错磁体”NRSS 类扩展了交变磁研究范畴，其自旋纹理不再受旋转对称性交替约束，可能产生不同于 d 波交错磁体的强场响应。
  - **莫尔与低维体系**：将这类三元氮化物剥离或构建莫尔超晶格，可在保持零净磁化的同时调控 Γ 点劈裂与关联强度，为量子模拟和新型量子器件提供平台。
  - **项目关联**：本工作已被 used_by_proposals 标记为 `general-order-parameter-ultrafast-readout-20260727`，其 Γ 点劈裂与可调带隙直接服务于“序参量超快读出”课题中基于强场光学读取反铁磁序参量的实验设计。

  ## 来源

  - 蒸馏自全文（deep-read）


## 合并自「2402.14321」

## 阅读笔记

### general-order-parameter-ultrafast-readout-20260727

以下是论文 **2402.14321** 的结构化笔记：

---

**论文基本信息**
- 标题：*Non-relativistic spin splitting in compensated magnets that are not altermagnets*
- 作者：Lin-Ding Yuan, Alexandru B. Georgescu, James M. Rondinelli（西北大学+印第安纳大学）
- 发表：Phys. Rev. Lett. 133, 216701 (2024)
- 领域：凝聚态物理 / 材料科学 / 自旋电子学

---

## 研究问题（Research Question）

该论文旨在回答一个核心问题：**交变磁性（altermagnetism）是否穷尽了所有具有非相对论性自旋分裂（NRSS）的反铁磁（AFM）材料？** 作者认为并非如此——存在一类 NRSS 反铁磁体，其自旋结构 motif 对（spin-structure motif pair）**不通过任何空间旋转操作相连**，因此不在 altermagnet 范畴之内。这类材料在 Γ 点处呈现出自旋分辨能带的**简并解除**（即 NRSS 存在于 Γ 点），这是 altermagnets 所不具备的特征。作者试图通过对称性分析确定这类"超越 altermagnet 描述"的 NRSS 反铁磁体的存在条件、特征指纹，并验证其在三元锰氮化物 MnXN₂（X=Si, Ge, Sn）及其阳离子有序变体中的可实现性。

---

## 研究背景（Background）

反铁磁体曾被认为不具备净磁矩，其电子能带必然自旋简并，因此在自旋电子学中仅扮演被动角色。然而 2020 年前后的一系列理论与实验工作（Yuan et al. 2020, Šmejkal et al. 2020 等）打破了这一偏见：某些反铁磁体在**不含自旋轨道耦合（SOC）**的条件下即可出现动量依赖的自旋分裂（即 NRSS），这种分裂源于材料内部不均匀的固有磁场（包括磁偶极子和高阶磁八极子）。这类材料被称为"altermagnet"（交变磁性），其特征是自旋极化带在 Γ 点保持简并（受 UR 对称性保护），而交替改变符号于其他 k 路径。

然而，作者指出 altermagnet 的定义包含一个额外约束——要求 opposite-spin 子格之间存在**空间旋转操作**连接。这意味着存在 NRSS AFMs 可以不满足该旋转对称性要求，但仍具备 NRSS 特性，此前被文献所忽略。三元锰氮化物 MnXN₂ 是一类高 Neel 温度（MnSiN₂ 的 T_N = 443 K）、强共价键的磁性半导体，是验证该假设的理想平台。

---

## 研究方法（Methods）

1. **对称性分析**：作者引入"无 SOC 时的磁空间群（MSG without SOC）"概念，在非相对论极限下对磁对称操作进行分类。通过分析 ΘI 和 UT 对称性的同时破缺，推导出 NRSS 出现的必要条件，并区分两类 NRSS AFM：MSG type III（子格由旋转操作连接 = altermagnet）和 MSG type I（子格无旋转连接 = 非 altermagnet 的 NRSS）。

2. **DFT 计算**：使用 VASP + SCAN 泛函对 MnSiN₂（母相）和 Mn₂SiSnN₄（阳离子有序变体）进行非相对论和相对论能带结构计算，验证对称性分析结论。计算细节见补充材料。

3. **晶体结构搜索**：通过 Si/Sn 替换（利用二者显著的离子半径差异）降低晶体对称性，构建具有 Pna21→Pc 对称性破缺的有序 Mn₂SiSnN₄（wurtzite-kesterite 结构），预期其属于 MSG type I。

---

## 主要发现与核心结论（Main Results）

- **发现一：MnSiN₂ 属于 altermagnet（SST-4 / MSG type III）**：其自旋极化带沿高对称路径（如 Γ-X, Γ-Y）保持简并，但沿对角路径（如 Γ-S）出现明显的 NRSS 分裂。这与已知的 altermagnet 行为一致——Γ 点保持简并。

- **发现二：有序 Mn₂SiSnN₄ 属于非 altermagnet 的 NRSS 材料（MSG type I）**：Sn 替换 Si 打破了原有的 {2001|0,0,1/2} 旋转对称性，使 MSG without SOC 从 Pna′2′1 降为 Pc。**最关键的结果是：价带顶在 Γ 点出现 332 meV 的大幅自旋分裂**，而 altermagnet 在 Γ 点无此分裂。

- **发现三：Γ 点 NRSS 的物理意义**：由于非 altermagnet 的 NRSS AFM 在 Γ 点不受 UR 对称性保护，其自旋电流产生不会受到"交替自旋极化"的抵消效应影响，理论上可实现更强的自旋流。

- **定性结论**：两类 NRSS AFM 的本质区别在于 opposite-spin motif pair 是否由空间旋转操作连接；这一区别可通过"无 SOC 时的 MSG 类型"（type I vs type III）有效判别。

---

## 潜在研究方向（Future Directions）

- **实验验证**：当前工作为理论预测，332 meV 的 Γ 点分裂量级与 MnF₂ 中的巨大自旋分裂相当，实验上可通过 ARPES 直接观测 Γ 点自旋劈裂来验证。
- **材料拓展**：可搜索更多具有 wurtzite-kesterite 或类似结构的阳离子有序化合物，特别是探索不同 X 位元素（X=Si, Ge, Sn）的混溶度及对 NRSS 的调控。
- **SOC 效应的细致研究**：SOC 会进一步降低对称性（如在 RuF₄ 中甚至可移除 Γ 点简并），需系统评估各向异性磁电阻、自旋霍尔效应等与 SOC 相关的输运行为。
- **自旋流应用**：非 altermagnet NRSS 材料因无交替自旋极化补偿，理论上更适合产生高自旋极化电流，是设计新型反铁磁自旋电子学器件的候选材料库。
- **弱铁磁耦合的贡献**：MnSiN₂ 中 Dzyaloshinskii-Moriya 相互作用诱导的弱铁磁（约 <1° 倾斜角）可能在 SOC 存在时对 Γ 点分裂有额外贡献，值得进一步量化。

---

来源：arXiv:2402.14321v1, Phys. Rev. Lett. 133, 216701 (2024)


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：无 SOC 磁空间群分类 + DFT-SCAN 验证（补偿磁体非相对论自旋劈裂的 MnXN₂ 体系）

**原理**：引入'无 SOC 的磁空间群'（MSG without SOC）框架：非相对论极限下分析 ΘI 与 UT 对称性同时破缺推导 NRSS 出现条件，区分 type III MSG（子格由旋转连接=交错磁体）与 type I MSG（子格无旋转连接=非交错的 NRSS）；DFT-SCAN 泛函计算 MnSiN₂（G 型共线 AFM，Rietveld 精修中子散射结构，磁矩沿 c 轴）与阳离子有序变体 Mn₂SiSnN₄（Si/Sn 离子半径差降对称，wurtzite-kesterite vs stannite 比较，声子色散确认 kesterite 相能量更低且动力学稳定，预期 MSG type I）的非相对论/相对论能带验证。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 体系 | MnXN₂（X=Si, Ge, Sn）；重点 MnSiN₂ 与有序 Mn₂SiSnN₄（wurtzite-kesterite 相） | §计算材料 |
| 泛函 | DFT-SCAN（非相对论+相对论能带） | §第一性原理 |

**适用边界**：计算细节在补充材料（正文未给截断/k 网格）；SCAN 泛函对氮化物关联处理的通用性依赖经验；磁结构取自中子散射精修（未独立验证交换参数）。
**代表作**：本文（arXiv:2402.14321）；工具链：VASP + SCAN
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2402.14321]]
- [[Berry 曲率]]
- [[arpes]]
- [[general-order-parameter-ultrafast-readout-20260727]]
- [[交变磁性（Altermagnetism）]]
- [[交变磁性（altermagnetism）]]
- [[反铁磁自旋电子学]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[莫尔超晶格]]
- [[超快自旋动力学]]
- [[量子几何]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
