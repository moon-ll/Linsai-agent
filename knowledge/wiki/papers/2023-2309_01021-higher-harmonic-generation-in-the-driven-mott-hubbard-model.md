---
title: "2023-2309_01021-higher-harmonic-generation-in-the-driven-mott-hubbard-model"
type: "papers"
created: "2026-08-29T05:11:51Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["2309.01021", "Berry 曲率", "dmft", "general-quantum-geometry-inversion-20260726", "交变磁体", "强关联体系", "强场超快", "强场驱动", "拓扑绝缘体", "莫尔超晶格", "量子几何", "量子度规", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2023-2309.01021-higher-harmonic-generation-in-the-driven-mott-hubbard-model.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:41:54Z"
merged_from: ["wiki/papers/2309.01021.md"]
---

• # Higher-harmonic generation in the driven Mott-Hubbard model

  ## 林赛的理解

  这篇工作把 Floquet 理论和关联层次展开结合起来，处理强关联 Mott 绝缘体在周期光场下的非平衡动力学，并给出了一个可计算的 HHG 电流表达式。对我来说，它的价值在于把“强关联”真正嫁接到了“强场驱动 / HHG”的语言里：不是用单粒子能带去拟合非线性响应，而是直接从 doublon-holon 关联函数出发，追踪驱动场如何逐阶打开多光子通道。我们组如果要在莫尔超晶格、交变磁或量子几何材料里做 HHG，这篇文章提供了两个可直接借用的技术接口：一是把 Peierls 替换后的含时跃迁做 Floquet 通道分解，二是用关联层次在有限配位数下计算双点电流。特别是式 (26) 给出的近共振电流标度律和“三倍频处信号最强”这一结论，可以直接放进申请书的“物理图像”和“预期成果”里，用来论证强关联体系 HHG 的选择定则与半导体能带图像不同。

  ## 研究问题

  论文要回答的核心问题是：在强相互作用极限下的 Fermi-Hubbard 模型中，当 Mott 绝缘体受到谐振电场驱动时，高次谐波产生（HHG）的物理机制、选择定则和定量标度是什么？具体来说，作者追问：驱动频率与 Mott 能隙 U 之间的共振关系如何决定谐波阶数？电流响应随驱动场强、跃迁强度 T 和能隙 U 如何标度？以及，Floquet 指数如何刻画关联激发的特征时间尺度？

  ## 研究背景

  Fermi-Hubbard 模型被视为强关联多体系统的“果蝇”，其非平衡动力学在泵浦激光驱动下已展现出丰富的现象：光致 doublon-holon 对产生（介电击穿）、Floquet 工程抑制耗散、预热处理等。此前研究大多采用 Floquet + DMFT 或时间依赖微扰理论，但这些方法要么把系统映射到单格点（DMFT 的无限维极限），要么难以给出稳态下的非微扰电流响应。实验上，人们在 1T-TaS₂ 等 Mott 绝缘体中已观测到超快 doublon 动力学，但强场 HHG 的理论描述仍缺乏一个同时保留强关联和动量分辨的方法。在此背景下，作者提出将 Floquet 理论应用于含时关联函数（而非直接对量子态做 Floquet 展开），以研究 doublon-holon 准粒子激发的稳态高次谐波辐射。

  ## 研究方法

  - **理论框架**：Fermi-Hubbard 模型，哈密顿量如式 (1)，包含最近邻跃迁项（跃迁率 T，配位数 Z）和 on-site 库仑排斥 U，外场以标量势 Vμ(t) = qxμ·E(t) 引入，再通过 Peierls 替换转化为含时复跃迁 Tμν(t)，如式 (2)-(3)。
  - **近似方法**：采用 **hierarchy of correlations**（关联层次）展开，按 1/Z 展开约化密度矩阵。在强耦合极限 U ≫ T 下，取无自旋序的 Mott 绝缘体背景，ρμ⁰ = (|↑⟩⟨↑| + |↓⟩⟨↓|)/2，并保留 doublon-holon 两格点关联到 O(1/Z) 阶，如式 (4)-(7)。
  - **Floquet 技术**：对含时关联函数做 Fourier-Floquet 展开，定义 Floquet 指数 νk 和 Floquet 态，求解无限维 Floquet 矩阵 Mk 的本征值问题 (16)。
  - **材料/晶格示例**：主要给出二维方晶格（晶格常数 ℓ）的解析结果，电场沿主轴方向，跃迁矩阵元的 Floquet 系数用第一类 Bessel 函数 Jn(qE0ℓ/ω) 表示。
  - **观测量**：通过最近邻粒子流 J = i∑s⟨c†μ,s cν,s⟩ + h.c. (23) 计算辐射电流，其中对方晶格简化为式 (24)。

  ## 主要发现与核心结论

  1. **Floquet 指数标度律**：在强耦合与小跃迁极限 T/ω ≪ 1、T/U ≪ 1 下，Floquet 指数满足式 (21)：
     \[
     \sin^2(\pi\nu_k) = \sin^2\!\left(\frac{\pi U}{\omega}\right) + \sin\!\left(\frac{2\pi U}{\omega}\right)\frac{\pi^2}{2\omega}\left(\frac{(T_k^\perp)^2}{U} + \frac{2T_k^\perp T_{k,0}^\parallel}{U} + \sum_n \frac{|T_{k,n}^\parallel|^2 U}{U^2 - \omega^2 n^2}\right) + O(T^4)
     \]
     表观奇点 ω = U/n 被 sin(2πU/ω) 因子抵消。

  2. **n 阶共振附近的指数标度**：近第 n 阶共振 ω ≈ U/n 且小场 qE0ℓ ≪ U 时，Floquet 指数按场强的 n 次幂标度（式 22）：
     \[
     \nu_k \approx \frac{\sqrt{2n}T}{ZU}\frac{1}{2^n n!}\left(\frac{qE_0\ell n}{U}\right)^n
     \begin{cases}
     \cos(k_\parallel\ell), & n\ \text{even}\\
     \sin(k_\parallel\ell), & n\ \text{odd}
     \end{cases}
     \]
     关联建立的特征时间尺度 τk ∼ (ω/E0)^n (Z/T)。

  3. **HHG 选择定则**：对方晶格，电流表达式 (24) 的反对称性导致只有奇次谐波出现：
     \[
     J(t) = \sum_{n=1,3,5,\dots} J_n \sin(n\omega t)
     \]

  4. **近共振电流的主导 correlator**：在 ωn = U 附近，电流由单个 Floquet 关联分量主导（式 25）：
     \[
     F_{k,n}^{10} \approx -\frac{U T_{k,n}^\parallel}{2\sqrt{T_k^4 + 4U^2|T_{k,n}^\parallel|^2}}
     \]
     其他分量被 T/U 抑制。

  5. **三倍频处信号最强**：对小场 qE0ℓ/U ≪ 1，共振电流近似为式 (26)：
     \[
     J(t) \approx 1.4\sqrt{\frac{U}{2T}}\left(\frac{n qE_0\ell}{U}\right)^n \frac{1}{2^n n!}\sin(Ut)
     \]
     基频共振 ω = U 时电流按 √(qE0ℓ/U) 标度；要产生更高频率，可使用三次谐波 ω = U/3，但电流额外被 qE0ℓ/U 抑制。

  6. **方法学优势**：相比 DMFT 等将系统映射到单格点的方法，本文方法能直接计算涉及两个格点算符的双点关联函数和电流，保留了动量分辨和有限配位数效应。

  ## 潜在研究方向

  - **能量收支与稳态**：作者指出下一步应研究 Floquet 稳态的能量平衡——泵浦激光吸收如何被辐射（含高次谐波）补偿。这需要把电流结果与能量流、热化机制自洽耦合。
  - **从稳态到非稳态**：当前结果是绝热打开激光达到的 νk = 0 稳态。突然开启（quantum quench）会激发多个 Floquet 态的叠加，可用于研究预热处理（pre-thermalization）和更一般的非平衡弛豫。
  - **更高维度与不同晶格**：解析结果主要针对方晶格和电场沿主轴的情形。三角、蜂窝、莫尔超晶格等具有非平庸量子几何和 Berry 曲率的体系，其高次谐波选择定则和极化依赖仍是开放问题。
  - **自旋序的影响**：背景假设为自旋无序 Mott 绝缘体。有限温度或磁有序会如何改变 doublon-holon 关联和 Floquet 指数，进而调制 HHG 效率，尚未处理。
  - **与实验定量对接**：式 (26) 给出了具体数值系数 1.4 和标度指数，但实验上 1T-TaS₂、Ta₂NiSe₅ 等强关联材料的具体参数（U、T、ℓ、E0）是否落在本文假设的 T/U ≪ 1、qE0ℓ/U ≪ 1 区间，需要进一步校验。
  - **包含耗散与退相位**：当前理论未显式包含电子-声子、杂质散射等耗散通道，这些过程会改变稳态电流谱和谐波线宽。

  ## 与林赛研究的关联

  - **HHG / 阿秒 / 强场驱动**：本文直接给出 Mott 绝缘体 HHG 的电流表达式和奇次谐波选择定则，可作为我们设计强场超快泵浦-探测实验的理论参照。特别是“ω = U/3 处信号最强”可用于指导中红外驱动源的选择。
  - **莫尔（moiré）**：莫尔超晶格中的 Hubbard 模型具有可调 U/T 和 Berry 曲率 dipole。本文的 Floquet + 关联层次方法可作为起点，研究 moiré 平带中强关联如何调制 HHG 的极化和阶数。
  - **交变磁（altermagnetism）**：交变磁体的自旋-动量锁定会引入各向异性跃迁相位，可借鉴本文的 Peierls 替换和 Floquet 通道分解，分析自旋极化 doublon-holon 激发产生的高次谐波。
  - **量子几何**：方晶格结果中的 sin(k∥ℓ)、cos(k∥ℓ) 和 Bessel 函数依赖本质上由跃迁矩阵的几何相位决定。推广到具有非零 Berry 曲率和量子度规的能带，可望建立“量子几何 → Floquet 通道权重 → HHG 强度”的定量映射。

  ## 来源

  - 蒸馏自全文（deep-read）


## 合并自「2309.01021」

## 阅读笔记

### general-quantum-geometry-inversion-20260726

现在我已经获取了论文的完整 TeX 源代码。以下是基于深度阅读的完整结构化笔记：

---

## 论文信息

| 字段 | 内容 |
|------|------|
| **标题** | Higher-harmonic generation in the driven Mott-Hubbard model |
| **arXiv ID** | 2309.01021 |
| **作者** | Friedemann Queisser, Ralf Schützhold |
| **机构** | Helmholtz-Zentrum Dresden-Rossendorf (HZDR) & TU Dresden, Germany |
| **投稿日期** | 2023-09-02 |
| **方向** | Condensed Matter > Strongly Correlated Electrons |
| **资助** | DFG SFB 1242 (Project-ID 278162697) |

---

## 研究问题（Research Question）

本文的核心研究问题是：**在受周期调制的外加电场（即泵浦激光）驱动下，Mott 绝缘体态的 Fermi-Hubbard 模型会产生怎样的高次谐波辐射？其物理机制是什么？**

具体而言，作者希望回答：
- Mott 绝缘体在 Floquet 驱动下的非平衡动力学如何用关联层次（hierarchy of correlations）方法描述；
- 高次谐波产生的共振条件是什么；
- 与传统的单粒子图像（如半导体 Bloch 方程）相比，关联电子系统的高次谐波有哪些独特特征。

---

## 研究背景（Background）

**Mott 绝缘体与 Hubbard 模型**：强关联电子系统的"果蝇"——Fermi-Hubbard 模型——是理解金属-绝缘体相变、反铁磁性、超导等强关联现象的标准理论框架。当在位库仑排斥能 $U$ 大于带宽时，系统进入 Mott 绝缘态，每个格点恰好占据一个电子（双占据被禁止）。

**Floquet 理论与泵浦-探测**：近年来，用周期调制的强激光场（泵浦光）驱动量子多体系统成为研究非平衡动力学的主流手段。通过 Floquet 理论可以将时间周期系统映射到等效的准能量本征值问题。前人已在 Hubbar d模型中研究了介质击穿（doublon-holon 对产生）、Floquet 工程（抑制耗散、修改预热化动力学）等现象。

**高次谐波产生（HHG）的延拓**：HHG 传统上在原子气体中被研究，近年来拓展到固体（半导体、拓扑绝缘体等）。半导体 HHG 可用 Aversa-Sipe 等半经典理论理解；但在强关联材料（如 Mott 绝缘体）中，HHG 的机制尚不清楚。Mott 绝缘体的 HHG 由双占据（doublon）和空穴（holon）的相干产生与运动主导，而非单电子带间跃迁。

**方法选择**：作者选择将 Floquet 理论与**关联层次方法（hierarchy of correlations）**结合，而不是直接对量子态做 Floquet 展开（区别于 DMFT 等单格点平均场方法），这样可以保留相邻格点间的关联信息。

---

## 研究方法（Methods）

**理论框架**：Floquet 理论 + 关联层次方法

1. **模型 Hamiltonian**（式 \ref{extHubb}）：
   $$\hat{H}(t) = -\frac{1}{Z}\sum_{\mu\nu s} T_{\mu\nu}(t)\hat{c}_{\mu s}^\dagger\hat{c}_{\nu s}^{} + U\sum_\mu \hat{n}_{\mu\uparrow}\hat{n}_{\mu\downarrow}$$
   其中通过 Peierls 替换将时间依赖电场编码到复数 hopping 矩阵 $T_{\mu\nu}(t)$ 的相位中。

2. **强耦合近似**（$U\gg T$）：Mott 绝缘态每个格点近似单占据（忽略 $T^2/U^2$ 量级的虚跃迁修正），选择自旋无序背景（式 \ref{disorder}）：
   $$\hat{\rho}_\mu^0 = \frac{|\uparrow\rangle\langle\uparrow| + |\downarrow\rangle\langle\downarrow|}{2}$$

3. **关联层次展开**：在一阶层次近似下，各动量模式 $\mathbf{k}$ 分解独立演化，满足 $4\times4$ 矩阵微分方程（式 \ref{firstorder}）。

4. **Floquet 分解**：将时间周期矩阵 ${\cal M}_\mathbf{k}(t)$ 和关联函数 ${\cal F}_\mathbf{k}s(t)$ 展开为 Floquet 通道（式 \channels），系数包含 Bessel 函数 $\mathcal{J}_n(qE_0\ell/\omega)$。

5. **稳态条件**：采用绝热开启泵浦激光（而非 sudden quench），系统最终处于 $\nu_\mathbf{k}=0$ 的 Floquet 态。

**谐振条件**：外加电场 $\mathbf{E}=\mathbf{E}_0\cos(\omega t)$，当谐振条件 $\omega n = U$（$n=1,3,5,\ldots$）满足时，特定关联函数主导电流响应。

---

## 主要发现与核心结论（Main Results）

**1. 电流表达式（式 \ref{current}）**

相邻格点间电流：
$$J = i\sum_s \langle \hat{c}_{\mu,s}^\dagger \hat{c}_{\nu,s}\rangle + \text{h.c.}$$

经推导得到稳态电流：
$$J(t) = \sum_{n=1,3,5,\ldots} J_n \sin(n\omega t)$$

**2. 共振电流幅度（关键结果）**

在 $\omega n = U$ 的共振附近，电流近似为：
$$J(t) \approx 1.4\,\sqrt{\frac{U}{2T}\left(\frac{nqE_0\ell}{U}\right)^n \frac{1}{2^n n!}}\,\sin(Ut)$$

**3. 关键物理发现**

- **只有奇数次谐波**：由于电流积分对 $k^\parallel$ 的反对称性，只有 $n=1,3,5,\ldots$ 的奇数次谐波出现。
- **最强信号在 $n=3$ 共振**：当驱动频率等于 Mott 间隙的 $1/3$（$\omega = U/3$）时，**三次谐波信号最强**——这是论文的核心结论之一。
- **非微扰标度关系**：电流对 $U$、$T$、$E_0$ 的依赖是非多项式的，表明微扰论无法得到此结果。
- **基频共振（$\omega=U$）**：电流按 $\sqrt{qE_0\ell/U}$ 标度。
- **三次谐波（$\omega=U/3$）**：比基频多一个抑制因子 $qE_0\ell/U$。

**4. 方法优势**

关联层次方法可以计算涉及相邻格点的电流算符期望值，这是 DMFT 等单格点方法做不到的——DMFT 将系统有效映射到单格点问题，丢失了晶格连通性信息。

---

## 潜在研究方向（Future Directions）

**1. 能量平衡研究**
当前工作计算了稳态电流和谐波强度，但未涉及 Floquet 稳态的能量收支平衡——即泵浦激光的能量吸收与高次谐波辐射之间的定量关系。

**2. 从准稳态到非稳态**
本文研究的是可通过绝热开启达到的 Floquet 准稳态，未来可推广到更一般的非稳态（Floquet 态的叠加），用于研究预热化（pre-thermalization）及其他非平衡现象。

**3. 与实验材料的对接**
虽然论文使用格子模型，但可以推广到更真实的材料模型（如实际能带结构），与超冷原子气体或固体 Mott 绝缘体（如 Ca₂RuO₄）的 HHG 实验对比。

**4. 方法的局限**
- **层次截断**：在一阶近似下已获得非微扰结果，但更高阶关联可能带来修正；
- **自旋有序**：本文选择自旋无序背景，若考虑反铁磁序，自旋结构可能影响谐波信号的细节；
- **维度效应**：正文分析主要针对高维格子（忽略相位涨落），一维情况下可能有定性差异。

**5. 开放物理问题**
- 能否通过调节驱动频率和强度来"工程化"特定的高次谐波辐射谱？
- doublon-holon 对产生的相干性如何在更高层次关联中体现？
- 与最近实验观测到的 Mott 绝缘体 HHG 异常温度依赖性（Murakami et al.）如何关联？

---

**来源**：Friedemann Queisser & Ralf Schützhold, *Higher-harmonic generation in the driven Mott-Hubbard model*, arXiv:2309.01021 (2023).


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：Floquet 关联函数方法计算 Mott-Hubbard 模型 HHG（关联层次展开 + doublon-holon 稳态）

**原理**：对含时 Fermi-Hubbard 模型（外场经 Peierls 替换引入）用 hierarchy of correlations 按 1/Z 展开约化密度矩阵，在强耦合 U≫T 极限保留 doublon-holon 两格点关联到 O(1/Z) 阶；对含时关联函数（而非量子态）做 Fourier-Floquet 展开求解 Floquet 矩阵本征值问题，得到稳态 Floquet 指数标度律与辐射电流——保留动量分辨与有限配位数效应（区别于 DMFT 单格点映射），给出 Mott 绝缘体 HHG 的奇次谐波选择定则与共振电流解析式。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Floquet 指数标度 | 强耦合小跃迁极限 sin²(πν_k)=sin²(πU/ω)+sin(2πU/ω)(π²/2ω)[(T⊥²/U)+2T⊥T∥/U+Σₙ|T∥ₙ|²U/(U²−ω²n²)]+O(T⁴)；表观奇点 ω=U/n 被 sin(2πU/ω) 抵消 | 主要发现 |
| 共振标度 | 近 n 阶共振 ω≈U/n：ν_k≈(√(2n)T/ZU)(1/2ⁿn!)(qE₀ℓn/U)ⁿ cos/sin(k∥ℓ)（n 偶/奇）；关联建立时间 τ_k~(ω/E₀)ⁿ(Z/T) | 主要发现 |
| 电流表达式 | 方晶格只有奇次谐波 J(t)=Σ Jₙsin(nωt)；基频共振 ω=U 电流按 √(qE₀ℓ/U) 标度；共振电流近似 J(t)≈1.4√(U/2T)(nqE₀ℓ/U)ⁿ(1/2ⁿn!)sin(Ut)——三倍频 ω=U/3 处产生更高频率但被 qE₀ℓ/U 额外抑制 | 主要发现 |
| 方法优势 | 直接计算双格点算符关联与电流（保留 k 分辨 + 有限 Z）；跃迁矩阵元 Floquet 系数用第一类 Bessel 函数 Jₙ(qE₀ℓ/ω) | 研究方法 |

**适用边界**：自旋无序 Mott 背景假设（磁序影响未处理）；绝热开场稳态（quench/预热处理未涉及）；未含耗散/退相位（e-ph/杂质）；解析结果限方晶格电场沿主轴（三角/蜂窝/莫尔的非平庸 Berry 曲率体系开放）；实验参数（1T-TaS₂ 等）是否落在 T/U≪1、qE₀ℓ/U≪1 区间待校验。
**代表作**：Mott-Hubbard HHG 的 Floquet 关联函数方法（Queisser & Schützhold，HZDR/TU Dresden，本文，arXiv 2309.01021）；'ω=U/3 三倍频信号最强'指导中红外驱动源选择。
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2309.01021]]
- [[Berry 曲率]]
- [[dmft]]
- [[general-quantum-geometry-inversion-20260726]]
- [[交变磁体]]
- [[强关联体系]]
- [[强场超快]]
- [[强场驱动]]
- [[拓扑绝缘体]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[量子度规]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
