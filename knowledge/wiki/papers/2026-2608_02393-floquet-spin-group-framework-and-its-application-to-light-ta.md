---
title: "2026-2608_02393-floquet-spin-group-framework-and-its-application-to-light-ta"
type: "papers"
created: "2026-08-29T05:23:56Z"
updated: "2026-11-15T15:09:19Z"
tags: []
related: ["2607.19303", "2608.02393", "Berry curvature dipole", "Berry 曲率", "PLAN", "arpes", "general-new-idea-20260822", "pump-probe", "交变磁体", "共线磁体中非相对论奇宇称自旋劈裂的完整分波谱系", "反常霍尔效应", "强场超快", "强场超快光学", "强场驱动", "拓扑绝缘体", "自旋劈裂", "莫尔超晶格", "量子几何", "阿秒瞬态吸收", "非共振驱动", "非线性光学", "高次谐波产生"]
source_raw: "2026-2608.02393-floquet-spin-group-framework-and-its-application-to-light-ta.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:57Z"
merged_from: ["wiki/papers/2608.02393.md"]
---

• # Floquet spin-group framework and its application to light-tailored spin splitting in collinear magnets

  ## 林赛的理解

  这项工作把 Floquet 工程与交变磁（altermagnet）的动量依赖自旋劈裂拧在了一起，给我们的强场超快光学研究提供了一个清晰的对称性语言。我们关心的是：用 HHG、阿秒瞬态吸收或自旋分辨光电子能谱这类强场驱动探针，能不能在 fs–as 时间尺度上“切换”材料的自旋劈裂对称性。这篇文章的核心贡献正是把“光场的动力学对称性”映射成“准能带自旋劈裂的对称性”，给出了一般性的光学选择定则。这意味着我们不再需要逐个材料试错，而是可以先看它的 spin point group，再选择 CPL 或 BLPL 的偏振、相位、谐波成分，去定向诱发奇宇称、偶宇称或混合宇称的自旋劈裂。对我们组来说，它直接连接到 HHG 探测交变磁、阿秒磁动力学、强场驱动量子几何（Berry curvature dipole / anomalous Hall）以及莫尔体系中的自旋群对称性等方向。特别是，这篇文章把材料分成五类（AFM、偶宇称 AM、奇宇称、混合宇称、类 FiM），并给出了 2D 63 个、3D 58 个 collinear spin point group 的完整分类表，相当于一本“光控自旋纹理”的对称性手册，可用于筛选我们手边的候选材料。

  ## 研究问题

  论文要回答的核心问题是：能否建立一个统一的对称性框架，把周期性光场的动力学对称性与驱动后 collinear magnet 自旋劈裂能带的对称性联系起来，从而在同一种材料中系统性地选择和切换奇宇称、偶宇称、混合宇称乃至类铁磁（FiM-like）的自旋劈裂？具体而言，作者要回答三个子问题：(1) 如何把晶体的静态 spin point group 与光场的 dynamical group 结合成 Floquet spin group？(2) 不同的驱动协议（CPL、BLPL 及其相对相位）会保留或破坏哪些自旋群操作，进而允许哪些类型的自旋劈裂？(3) 在二维和三维 collinear magnet 中，这种对称性分类能否预言并在第一性原理 / 紧束缚模型计算中实现新的光诱导自旋劈裂（包括更高阶的 h-wave 和 k-wave）？

  ## 研究背景

  交变磁（altermagnet）作为一类兼具动量依赖自旋劈裂和零净磁化的 collinear compensated magnet，近年来成为自旋电子学的热点。其自旋劈裂按动量宇称可分为偶宇称（ε_s,β(k)=ε_s,β(−k)）和奇宇称（ε↑,β(k)=ε↓,β(−k)）两类，后者此前主要在共面或非共线磁体的平衡态中讨论。在 collinear magnet 里，奇宇称劈裂可通过轨道序、子晶格电流、环流等平衡机制出现，但更引人注目的是周期驱动提供的非平衡路径：圆偏光（CPL）可在 collinear 反铁磁中破坏 [C₂T||E] 对称性，诱导奇宇称自旋劈裂。近期还有混合宇称劈裂的提议。Floquet 工程本身已在石墨烯、拓扑绝缘体表面态等材料中展现出打开能隙、诱导反常霍尔效应等能力，而 trARPES 实验也证实了周期驱动可重构材料的有效对称性和拓扑性质。

  然而，此前研究多是就具体材料和具体光场给出个案结果，缺少一个统一原则来回答：为什么某种光场会诱导某种自旋劈裂？如何在同一种材料里按需切换不同宇称？这正是本文要填补的空缺——把晶体的静态 spin point group 与光场的 dynamical symmetry group 结合起来，建立 Floquet dynamical spin point group 框架，从而系统决定驱动后自旋劈裂的允许宇称、动量依赖和节点结构。

  ## 研究方法

  作者采用对称性分析与数值计算相结合的方法。

  **理论框架**：在忽略自旋-轨道耦合（SOC）的极限下，将 collinear AFM 的静态 spin point group G_S 与光场的 dynamical group G_L 相交，得到驱动系统的 Floquet dynamical spin point group G_D = G̃_S ∩ G̃_L。其中静态 spin group 元素写作 [S||R]，S 作用于自旋空间（含自旋翻转 C₂ 与时间反演 T），R 为实空间点操作；光场的动力学对称操作写作 L̂ = [Θ||R]·τ_n，τ_n 表示驱动周期 T 的 1/n 分数平移。通过 Peierls 替换 k → k + A(t) 得到含时 Hamiltonian H_s(k,t)，并在扩展 Floquet 空间中定义 Floquet Hamiltonian H^F_s(k,t) = H_s(k,t) − iℏ∂_t，求解 Floquet 方程 H^F_s(k,t)|u_{s,β}(k,t)⟩ = ε_{s,β}(k)|u_{s,β}(k,t)⟩，由对称操作导出准能约束 ε_{χ_S s,β}(η_S R k) = ε_{s,β}(k) (mod ℏω)。

  **光场协议**：详细考察了两种光场——
  - 圆偏光（CPL）：A(t) = A_0(cosωt, ηsinωt, 0)，其动力学群由 [E||θ_001]·τ_θ、[T||m_x]·τ_2、[E||P]·τ_2 生成；
  - 双线性偏振光（BLPL）：A_α(t) = A_0(sinωt, sin(2ωt+α), 0)，重点讨论 α = 0、α = ±π/2 及一般相位。

  **材料与模型计算**：
  - 二维体系：用第一性原理计算 MnPSe₃（spin point group 13/m∞m1，No. 46）和 Mn₂P₂S₃Se₃（13^1m∞m1，已具 i-wave altermagnetic 基态）在不同光场下的 Fermi 面。驱动参数为 MnPSe₃：ℏω = 10 eV，Ã = 0.35 Å⁻¹；Mn₂P₂S₃Se₃：ℏω = 10 eV，Ã = 0.25 Å⁻¹。费米面能量分别为 MnPSe₃ 无光照 E_F = −0.3 eV、CPL 下 E_F = −0.3 eV、BLPL α = 0 下 E_F = −0.35 eV、BLPL α = π/4 下 E_F = −0.35 eV；Mn₂P₂S₃Se₃ 无光照 E_F = −0.2 eV，三种光照下均为 E_F = −0.335 eV。
  - 三维体系：构建两个代表性紧束缚模型——tetragonal 模型（spin point group 14/1m1m1m∞m1，磁原子在 Wyckoff 2e，非磁原子在 2f，每格点一个 s 轨道）和 hexagonal 模型（spin point group 16/1m∞m1，磁原子在 2e，非磁原子在 3f）。驱动参数均为 ℏω = 10 eV，Ãa = 2。费米面能量分别为 tetragonal 模型 E_F = 1.2 eV、hexagonal 模型 E_F = −2.4 eV。三维计算采用 high-frequency approximation。

  ## 主要发现与核心结论

  1. **统一分类框架**：提出 Floquet dynamical spin point group，把自旋反转、实空间点操作、时间反演和分数时间平移置于同等地位，为准能自旋劈裂提供光学选择定则。

  2. **五种自旋劈裂类别**：
     - 自旋简并 AFM：ε_{↑,β}(k) = ε_{↓,β}(k)；
     - 偶宇称 AM：ε_{↑,β}(η_S R k) = ε_{↓,β}(k) 且 ε_{s,β}(k) = ε_{s,β}(−k)；
     - 奇宇称：ε_{↑,β}(k) = ε_{↓,β}(−k)；
     - 混合宇称：ε_{↑,β}(η_S R k) = ε_{↓,β}(k)，但整体既非纯偶也非纯奇；
     - 类 FiM：无自旋群操作联系两自旋 sector，ε_{↑,β}(k) ≠ ε_{↓,β}(η_S R k)。

  3. **二维完整分类**：对 63 个 collinear spin layer point group，给出了无光照、CPL、BLPL α = 0、BLPL α = π/4 四类条件下的自旋劈裂类型表（Table I）。关键例证：
     - MnPSe₃（No. 46）无光照为 AFM；CPL 破坏 [C₂T||E]，产生 f-wave 奇宇称劈裂；BLPL α = 0 保留 [C₂T||E] 和 [C₂||m₁₀₀]、破坏 [C₂||P]，产生 d-wave 偶宇称劈裂；BLPL α = π/4 进一步破坏 [C₂T||E]，仅剩 [C₂||m₁₀₀] 作为自旋翻转对称性，得到混合宇称劈裂。
     - Mn₂P₂S₃Se₃ 基态为 i-wave altermagnet；CPL 下由于 k 与 −k 不再由任何对称性联系，变为混合宇称；BLPL α = 0 为 d-wave；BLPL α = π/4 仅剩 [C₂||m₀₁₀]，亦为混合宇称。

  4. **三维新奇劈裂**：CPL 可在全部 58 个 collinear 3D spin point group 中诱导自旋劈裂，并发现二维所没有的更高阶奇宇称劈裂：
     - h-wave 劈裂可出现在 14/1m1m1m∞m1（No. 26）、14/1m13^1_2/1m∞m1（No. 57）、14/1m13^1_2/1m∞m1（No. 58）；
     - k-wave 劈裂可出现在 16/1m∞m1（No. 42）、16/1m1m1m∞m1（No. 51）、16/1m1m1m∞m1（No. 52）。
     在 tetragonal 模型中，CPL 下 [C₂||4₀₀₁] 强制 E(k_x,k_y,k_z,↑) = E(−k_y,k_x,−k_z,↓)，固定 k_z 切面呈 g-wave，而自旋极化在镜像相关平面 k_z 与 −k_z 之间反号，确认为完整 3D h-wave。hexagonal 模型中 [C₂||6₀₀₁] 强制 k-wave 劈裂，固定 k_z 切面呈 i-wave，k_z 与 −k_z 自旋极化反号。

  5. **光场对称性与输运的对应**：
     - CPL 破坏 [C₂T||E]，可产生反常霍尔效应（anomalous Hall effect）；
     - BLPL 破坏 [C₂||P] 但保留 [C₂T||E]，禁止反常霍尔效应，但允许非零 Berry curvature dipole。

  6. **分数时间平移的可观测效应**：虽然半周期时间平移不改变准能谱，但会在 Floquet 波函数中引入附加相位因子；在泵浦-探测光电子能谱中，满足动力学对称性的动量会呈现不同的光电子发射强度。

  ## 潜在研究方向

  1. **超越忽略 SOC 近似**：文章在 negligible SOC 极限下建立框架。真实材料中 SOC 往往有限，它会如何修正或破坏上述对称性分类？尤其当 SOC 与光场同时存在时，自旋不再是好量子数，奇/偶宇称劈裂的严格定义需要推广。

  2. **有限脉冲与非完美周期驱动**：Floquet 理论假设严格周期驱动。实验上使用的是有限长脉冲，需研究 dephasing、载流子热化、电子-电子散射、声子耦合如何抹平或重塑这些光诱导自旋劈裂。

  3. **实验探测方案**：最直接的是自旋-时间分辨角分辨光电子能谱（spin- and time-resolved ARPES）。但飞秒/阿秒脉冲本身也带有时域结构，如何区分 Floquet-Volkov 干涉、边带与真正的光诱导准能带自旋劈裂仍是挑战。也可探索 Kerr/Faraday 旋转、反常霍尔、Berry curvature dipole 等输运信号。

  4. **非共线、非共面自旋群推广**：作者指出框架可向 noncollinear 和 noncoplanar spin groups 推广，但具体分类尚未完成。这类体系可能带来更丰富的光诱导自旋纹理和拓扑态。

  5. **材料筛选与材料设计**：目前主要用 MnPSe₃ 和 Mn₂P₂S₃Se₃ 做例证。可把 2D 63 个、3D 58 个 spin point group 分类表用于高通量筛选，寻找具有更大自旋劈裂、更低光强阈值、更易实验合成的候选材料；也可设计异质结、莫尔超晶格来进一步调控 spin group。

  6. **HHG 与自旋-轨道耦合的界面**：强场驱动下 HHG 对自旋纹理、Berry curvature、能带反转极为敏感。将本文的对称性预言与 HHG 产率、偏振、自旋极化的计算结合，可以发展非微扰光电子能谱之外的新一代超快磁探针。

  7. **多色光场与拓扑 Floquet 态**：BLPL 已展示相对相位 α 可调。更一般地，多色、多谐波、非共线偏振组合可能保护或破坏更精细的对称性，诱导 Floquet 拓扑相变，值得系统分类。

  ## 与林赛研究的关联

  **HHG 作为自旋纹理探针**：我们组发展的强场驱动 HHG 理论可直接用于计算 MnPSe₃、Mn₂P₂S₃Se₃ 及三维候选材料在 CPL/BLPL 驱动下的高次谐波产率与偏振。不同自旋劈裂类别（f-wave、d-wave、i-wave、g-wave、h-wave、k-wave）会给出特征性的动量依赖谐波谱，可作为 HHG“指纹”反推光诱导自旋对称性。

  **阿秒磁动力学**：光场切换奇/偶/混合宇称自旋劈裂意味着材料在 pump 后经历对称性破缺的瞬态演化。结合阿秒瞬态吸收或光电子能谱，可追踪自旋劈裂在 pump-probe 延迟内的建立、演化和弛豫过程，验证 Floquet 准能带的寿命与相干时间。

  **强场驱动量子几何**：文章提到的 Berry curvature dipole 与反常霍尔效应正是强场超快光学调控量子几何的接口。我们可用强场驱动下的非线性霍尔/反常霍尔响应，量化光诱导 Berry curvature 的时空演化，并探索在交变磁中实现光控整流、光电池效应。

  **交变磁与莫尔体系**：collinear spin point group 在莫尔超晶格中会因层间堆垛、转角、应变而被进一步限制或降低。把本文的 Floquet spin-group 分类与莫尔体系的 moiré 对称性结合，可预言转角交变磁双层在周期光场下的新奇自旋劈裂与关联拓扑态。

  **强场驱动能带工程**：本文的 Peierls 替换 + Floquet 框架与我们研究强场 dressing、动态局域化、Floquet 拓扑能带的经验直接对接。可把相同思路拓展到 HHG 驱动下的能带重构、自旋极化高次谐波产生，以及阿秒自旋流的产生与探测。

  ## 来源

  - 蒸馏自全文（deep-read）


## 合并自「2608.02393」

## 阅读笔记

### general-new-idea-20260822

全文已读完（正文 + 图表说明 + 讨论 + 参考文献）。以下为结构化笔记。

---

## 论文信息

- **标题**：Floquet spin-group framework and its application to light-tailored spin splitting in collinear magnets
- **作者**：Tongshuai Zhu（朱同帅，中国石油大学/宁波理工）, Zixuan Li, Huaiqiang Wang（南京师大）, Su-Huai Wei（魏苏淮）, Jiawei Ruan（阮佳伟，通讯，jwruan@eitech.edu.cn）
- **arXiv**：[2608.02393v1](https://arxiv.org/abs/2608.02393) [cond-mat.mes-hall]，2026-08-03 提交，8 页 3 图
- **备注**：作者团队即 CPL 诱导 MnPX₃ 奇宇称自旋劈裂的 PRL 136, 126704 (2026) 原班人马（ref [36]）

---

## 研究问题（Research Question）

论文要解决的核心问题是：**周期驱动（Floquet）光的动力学对称性与被驱动共线磁体自旋劈裂能带对称性之间，是否存在统一的对应原理**。此前的研究已分别证明圆偏光（CPL）、双色线偏光（BLPL）等可在交变磁体/反铁磁体中诱导奇宇称、偶宇称甚至混合宇称的自旋劈裂，但这些都是“一案一议”，缺少一个能系统性回答“给定材料 + 给定光场 → 允许什么宇称、什么动量依赖、什么节点结构”的统一理论。作者的目标是建立 **Floquet 自旋群（Floquet spin group）框架**，并在此基础上给出在同一材料内按需切换自旋劈裂类型（奇/偶/混合宇称、类亚铁磁）的普适设计原则，同时探索 3D 体系中是否存在 2D 没有的高阶自旋劈裂新类别。

## 研究背景（Background）

交变磁体（altermagnet）兼具动量依赖的自旋劈裂与零净磁化，是自旋电子学的研究热点（Šmejkal 系列PRX、Mazin 等）。共线交变磁体的自旋劈裂通常是**偶宇称**（动量反演下不变），而**奇宇称**劈裂（动量反演下变号）最初主要见于非共面/共面磁体的平衡态；后续工作发现共线磁体中也可通过轨道序、子晶格电流、环路电流在平衡态产生奇宇称劈裂。非平衡方面，2026 年多篇 PRL（refs [35-38]，含作者自己的 PRL 136, 126704）证明 CPL 可在共线反铁磁体中诱导奇宇称自旋劈裂，混合宇称劈裂也刚被提出（ref [41]）。Floquet 工程领域，CPL 打破时间反演在石墨烯/拓扑绝缘体表面开隙并诱导反常霍尔效应已被证实，且 Floquet–Bloch 态已获 tr-ARPES 实验观测（Nature 614, 75 等），说明光场可以作为“动力学对称性选择器”重构材料的对称性与拓扑。但**“光的对称性 → 自旋劈裂对称性”的映射规则缺失**，制约了非平衡自旋能带的系统设计——这正是本文的切入点。

## 研究方法（Methods）

理论核心是**群论构造**：将晶体静态自旋点群 $G_S$（元素 $[S||R]$，自旋空间操作 × 实空间操作）提升为含连续时间平移的动力学群 $\tilde{G}_S = T_L \rtimes G_S$；光场自身的动力学对称群 $G_L$ 由生成元 $[\Theta||R]\cdot\tau_n$（空间操作 + 周期分数时间平移）刻画，无 SOC 时 $\tilde{G}_L = G_L \times C$；驱动系统的对称群取交集 $G_D = \tilde{G}_S \cap \tilde{G}_L$（Eq. 2）。在扩展 Floquet 空间中（$H^F = H - i\hbar\partial_t$，Peierls 代换 $\mathbf{k}\to\mathbf{k}+\mathbf{A}(t)$），$G_D$ 的每个元素对准能量施加约束 $\varepsilon_{\chi_S s}(\eta_S R\mathbf{k}) = \varepsilon_s(\mathbf{k}) \pmod{\hbar\omega}$（Eq. 5），由此把自旋劈裂分为五类：自旋简并 AFM、偶宇称（AM）、奇宇称、混合宇称、无对称配对的类亚铁磁（FiM）。在此框架下作者完成了**穷举式分类**：2D 的 63 个共线自旋层群（Table 1）和 3D 的 58 个共线自旋点群（Table 2），分别在 CPL、BLPL(α=0)、BLPL(α=π/4) 三种驱动协议下的劈裂类型全部列出。验证手段包括：(i) 对 MnPSe₃、Mn₂P₂S₃Se₃ 的第一性原理 Floquet 计算（VASP/PBE/PAW + Wannier 化，高频近似，ℏω=10 eV，Ã=0.25–0.35 Å⁻¹）画自旋分辨费米面；(ii) 两个自定义 3D 紧束缚模型（四方群 No. 26、六角群 No. 42，磁原子占 Wyckoff 2e 位、s 轨道）；(iii) Floquet–Volkov 谱计算以对接光电子能谱实验信号。

## 主要发现与核心结论（Main Results）

**结论一：同一材料内可按需切换自旋劈裂宇称**（Fig. 2）。自旋简并 AFM MnPSe₃（自旋群 No. 46，$\mathcal{PT}$ 对称）：CPL 破坏 $[C_2\mathcal{T}||E]$ → 诱导 **f 波奇宇称**劈裂；BLPL(α=0) 破坏 $[C_2||\mathcal{P}]$ 但保留 $[C_2\mathcal{T}||E]$ → **d 波偶宇称**；BLPL(α=π/4) 进一步破坏 $[C_2\mathcal{T}||E]$ → **混合宇称**。平衡态已是 i 波交变磁体的 Mn₂P₂S₃Se₃（No. 61 类）同样可在混合宇称 ↔ d 波之间切换——即奇、偶、混合宇称三类劈裂可仅通过光场设计在同一材料中切换。**结论二：3D 涌现 2D 不存在的高阶自旋劈裂**（Fig. 3）。关键机制是 $[C_2||m_{001}]$ 在 2D 中把相反自旋联系在同一动量点（强制简并），但在 3D 中只联系 $(\mathbf{k}_\parallel, \pm k_z)$ 镜像面，因此 CPL 可在**全部 58 个**共线自旋点群中诱导自旋劈裂；并在四方群（No. 26/57/58）中发现 **h 波**、六角群（No. 42/51/52）中发现 **k 波**自旋劈裂——固定 $k_z$ 切面呈 g 波/i 波图案且自旋极化在 $\pm k_z$ 镜像面间变号，构成完整 3D 高阶纹理。**结论三：输运与光电子能谱预言**。CPL 驱动可产生反常霍尔效应，BLPL 则禁止反常霍尔但允许非零 Berry 曲率偶极；动力学对称中的分数时间平移虽不改变准能量谱，但会通过 Floquet–Volkov 干涉使对称关联动量点呈现不同光电子能谱强度，为实验探测提供指纹。

## 潜在研究方向（Future Directions）

**框架自身的扩展**：当前理论仅适用于**可忽略 SOC 的共线磁体**，作者明确指出可推广到非共线、非共面自旋群，这是最直接的理论后续；SOC 不可忽略的体系（自旋-空间群）尚待建立对应框架。**实验验证路径**：文中最直接的实验探针是自旋分辨、时间分辨 ARPES（spin-trARPES），且已给出 Floquet–Volkov 谱的可检验预言，但文中计算用的是 ℏω=10 eV 高频非共振驱动（Ã=0.25–0.35 Å⁻¹），与实际实验光强/频段的匹配、加热效应与有限寿命问题未讨论。**与竞态工作的关系**：作者在 Note added 中提到两项同期独立工作——3D 高阶自旋劈裂（arXiv:2607.19303）与共面磁体奇偶宇称切换（arXiv:2607.27335），说明该方向竞争激烈，后续可能出现框架融合或优先权之争。**对用户课题（general-new-idea-20260822）的启示**：本文给出的是**对称性选择定则**而非定量响应——光致自旋劈裂的幅度、h/k 波劈裂能否被 HHG 或非线性光学读出、以及“光场对称性设计 → 非平衡自旋纹理 → 超快光学探测”的完整链条，均是未解决问题；将此 Floquet 自旋群分类与自旋分辨 HHG 光谱学结合，是一个自然的开放方向。

---

**来源**：[arXiv:2608.02393](https://arxiv.org/abs/2608.02393) | [HTML 全文](https://arxiv.org/html/2608.02393v1) | 本地缓存：/tmp/paper_2608.02393.txt


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Floquet dynamical spin point group 群论构造 + 穷举对称性分类（2D 63 群 / 3D 58 群）

**原理**：把晶体静态 spin point group G_S（元素 [S||R]）提升为含时间平移的动力学群 T_L ⋊ G_S，与光场动力学群 G_L（生成元 [Θ||R]·τ_n，τ_n 为周期分数平移）取交集 G_D = G̃_S ∩ G̃_L；扩展 Floquet 空间 H^F = H − iℏ∂_t（Peierls 替换 k→k+A(t)）求解，由对称操作导出准能约束 ε_{χ_S s}(η_S Rk) = ε_s(k) (mod ℏω)，将自旋劈裂统一分为五类（简并 AFM/偶宇称/奇宇称/混合宇称/类 FiM）；穷举 2D 63 个 spin layer group 与 3D 58 个 spin point group 在 CPL/BLPL(α=0)/BLPL(α=π/4) 驱动下的完整分类表；VASP/PBE/PAW + Wannier 化第一性原理 Floquet 计算（高频近似）与紧束缚模型验证。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| MnPSe₃ 驱动参数 | ℏω = 10 eV，Ã = 0.35 Å⁻¹；E_F：无光/CPL −0.3 eV，BLPL −0.35 eV | 研究方法（材料与模型计算） |
| Mn₂P₂S₃Se₃ 驱动参数 | ℏω = 10 eV，Ã = 0.25 Å⁻¹；E_F：无光 −0.2 eV，光照 −0.335 eV | 研究方法（材料与模型计算） |
| 3D 模型参数 | ℏω = 10 eV，Ãa = 2；E_F：tetragonal 1.2 eV，hexagonal −2.4 eV | 研究方法（材料与模型计算） |
| 分类表覆盖 | 2D 63 个 spin layer point group；3D 58 个 spin point group | 主要发现 3/4 |
| 3D 高阶劈裂群 | h-wave：四方 No. 26/57/58；k-wave：六角 No. 42/51/52 | 主要发现 4 |
| 输运对应 | CPL 破坏 [C₂T||E] → 允许 AHE；BLPL 破坏 [C₂||P] 保 [C₂T||E] → 禁 AHE 允 Berry curvature dipole | 主要发现 5 |

**适用边界**：忽略 SOC 极限（有限 SOC 下自旋非好量子数，分类需推广）；严格周期驱动假设（有限脉冲 dephasing/载流子热化/声子耦合未含）；ℏω=10 eV 高频非共振驱动与实际实验光强/频段匹配及加热效应未讨论；非共线/非共面 spin group 推广未完成；给出对称性选择定则而非定量响应幅度。
**代表作**：Zhu et al., Floquet spin-group framework and its application to light-tailored spin splitting in collinear magnets（arXiv:2608.02393）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2607.19303]]
- [[2608.02393]]
- [[Berry curvature dipole]]
- [[Berry 曲率]]
- [[PLAN]]
- [[arpes]]
- [[general-new-idea-20260822]]
- [[pump-probe]]
- [[交变磁体]]
- [[共线磁体中非相对论奇宇称自旋劈裂的完整分波谱系]]
- [[反常霍尔效应]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[自旋劈裂]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[阿秒瞬态吸收]]
- [[非共振驱动]]
- [[非线性光学]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
