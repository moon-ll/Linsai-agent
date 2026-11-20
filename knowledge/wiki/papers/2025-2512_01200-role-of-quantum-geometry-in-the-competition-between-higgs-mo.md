---
title: "2025-2512_01200-role-of-quantum-geometry-in-the-competition-between-higgs-mo"
type: "papers"
created: "2026-08-30T08:26:39Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2512.01200", "Berry 曲率", "Berry曲率", "MnPS3", "general-berry-mnps3-rashba-20260816", "quantum metric", "强场超快", "强场超快光学", "莫尔超晶格", "量子几何", "量子度规", "非线性光学"]
source_raw: "2025-2512.01200-role-of-quantum-geometry-in-the-competition-between-higgs-mo.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:09Z"
merged_from: ["wiki/papers/2512.01200.md"]
---

# 量子几何调控超导体三倍频产生中 Higgs 模式与准粒子激发竞争（arXiv:2512.01200 深度笔记）

## 林赛的理解

这篇工作对强场超快光学 PI 视角的核心价值在于：**它把超导体非线性光学中长期悬而未决的"Higgs vs 准粒子"竞争问题，归结为 Bloch 态内禀的量子度量（quantum metric）**，从而提供了一个不依赖材料细节（杂质、声子推迟）的、普适的几何放大机制。

对我们组的直接意义有三点：
1. **方法学接口**：他们推导的"光学核 $K_{ijkl}(\omega)=K^{qp}_{ijkl}+K^{Higgs}_{ijkl}$"形式与 HHG/阿秒电离中常见的"单粒子通道 vs 多体/集体模式通道"分解在数学结构上同构，可以移植到我们用 THz/中红外驱动的强场非线性谱中。
2. **材料选择**：论文预言量子度量大的体系（莫尔平带、扭转多层石墨烯、kagome、twisted cuprate）应当展现"几何增强的 Higgs 三倍频"，这为我们设计实验平台（莫尔超晶格、扭转超导）提供了具体判据。
3. **可观测量**：Higgs 关联长度 $\xi_H$ 与关联刚度 $A_{ij}$ 都被量子度量增强，这意味着我们在泵浦-探测实验中看到的振幅模式恢复时间、振幅-相位动力学，将直接成为量子度量的探针。

换句话说，这篇论文让我们意识到：**过去我们常常归咎于杂质、推迟相互作用的多体非线性"反常"，可能根本就是布洛赫波函数几何结构的体现**。

---

## 研究问题（Research Question）
论文要回答的核心问题是：

> **在 clean limit（无杂质散射极限）下，BCS 标准理论预言超导体三倍频产生（THG）由准粒子（pair-breaking）激发主导；但 NbN 等单晶实验中却发现 Higgs（振幅）模式主导 THG 共振——是哪一个普适的、与材料细节无关的物理机制，决定了 Higgs 模式与准粒子在 THG 中的胜负？**

具体地：
- 目标：识别并证明**量子几何（特别是 quantum metric $g_{ij}(\mathbf{k})$）** 是这一竞争的关键调控参数；
- 中心论点：量子度量可以**非对称地**放大 Higgs 通道相对于准粒子通道的非线性光-物质耦合，从而在 clean、散射弱的体系中让 Higgs 模式在 THG 中反超准粒子。

---

## 研究背景（Background）
学术脉络分三条线：

1. **集体模式与 Higgs 物理**：Anderson (1958, 1963)、Schmid (1968) 与 Pekker-Varma、C. M. Varma 等人奠定振幅（Higgs）/相位（Nambu-Goldstone）模式的基础；Anderson-Higgs 机制把相位模式推到等离子体频率，Higgs 模式留在 $\sim 2\Delta$ 的能隙处。综述见 Pekker & Varma, Annu. Rev. Condens. Matter Phys. **6**, 269 (2015)；Shimano & Tsuji, Annu. Rev. Condens. Matter Phys. **11**, 103 (2020)。

2. **THG 作为 Higgs 探针的实验与理论张力**：
   - 实验：Matsunaga et al., Science **345**, 1145 (2014)；Phys. Rev. B **96**, 020505 (2017) — NbN 中偏振依赖 THG 显示 Higgs 主导；Chu et al., Nat. Commun. **11**, 1793 (2020) — 铜氧化合物；Kovalev et al., PRB **104**, L140505 (2021) — MgB₂；Wang et al., PRB **105**, L100508 (2022) — NbN 高阶非线性；Kim et al., Sci. Adv. **10**, eadi7598 (2024) — 瞬态 THG。
   - 标准 BCS 理论（Cea-Castellani-Benfatto, PRB **93**, 180507 (2016)）在 clean 单带极限预言准粒子主导 THG —— 即"puzzle"。
   - 已有解释机制：杂质辅助（Jujo 2018; Murotani-Shimano 2019; Silaev 2019; Seibold et al. 2021; Derendorf et al. 2024）、多带声子推迟耦合（Tsuji-Murakami-Aoki, PRB **94**, 224519 (2016)）、多带-声子+杂质（Tsuji-Nomura, PRR **2**, 043029 (2020)）。但这些都依赖材料具体参数。

3. **量子几何的兴起**：量子度量在 Peotta-Törmä, Nat. Commun. **6**, 8944 (2015) 的 flat-band 超流、超流刚度（PRB **95**, 024515 (2017); Nat. Rev. Phys. **4**, 528 (2022)）、非线性光学（Cook et al. 2017; De Juan et al. 2017; Ahn et al. Nat. Phys. **18**, 290 (2022); Bhalla et al. PRL **129**, 227401 (2022)）、磁学（Oh-Rhim-Yang, PRB **110**, 155412 (2024); Kitamura-Daido-Yanase, PRL **132**, 036001 (2024)）中的应用陆续建立。最近 Xiao-Hao, PRB **111**, 134502 (2025) 在 **flat-band** 超导体中发现几何效应对 Higgs 的强烈影响——但**色散带（dispersive band）的几何效应在 THG 中仍属空白**。

研究动机正是要填补 **"色散带超导体中量子几何对 Higgs 模式非线性响应的普适作用"** 这一空白，并提供"几何工程"这一独立于杂质的判据。

---

## 研究方法（Methods）
**形式化框架（单带投影的多带超导）**：
- 多带 Hamiltonian $H_0+H_{\text{int}}$，$\hbar=e=c=1$；
- 通过 Hubbard-Stratonovich 在配对通道解耦，引入序参量场 $\Delta_{\alpha\beta}(\tau)$；
- 在均匀矢势 $\mathbf{A}(\tau)$ 下做最小耦合 $\mathbf{k}\to\mathbf{k}-\mathbf{A}$，假设 **local pairing**，则只有动能项被规范场修改；
- 通过对角化得到能带 $|u_{l\sigma}(\mathbf{k})\rangle$ 与色散 $\epsilon_{l\sigma}(\mathbf{k})$；
- 三条假设：(i) 正常态有时间反演与反演对称性、(ii) 单带（记为 $m$，下省略）主导 Fermi 面、(iii) 均匀同轨道配对 $\Delta_{\alpha\beta}=\Delta\delta_{\alpha\beta}$（这一条件对几何贡献的显现至关重要，源自 Peotta-Törmä 与 Törmä-Peotta-Bernevig）；
- 等效低能作用量：

$$S=\int_0^\beta d\tau\left\{\frac{N_b|\Delta|^2}{U}+\sum_{\mathbf{k},\sigma}c_\sigma^\dagger(\mathbf{k})\left[\partial_\tau+\epsilon_\sigma(\mathbf{k}-\mathbf{A})-\mu\right]c_\sigma(\mathbf{k})-\sum_\mathbf{k}\left[\Delta f(\mathbf{k},\mathbf{A})c_\uparrow^\dagger(\mathbf{k})c_\downarrow^\dagger(-\mathbf{k})+\text{h.c.}\right]\right\}$$

其中**配对重叠** $f(\mathbf{k},\mathbf{A})=\langle u_{\mathbf{k}+\mathbf{A}}|u_{\mathbf{k}-\mathbf{A}}\rangle=\sum_\alpha u_\alpha^*(\mathbf{k}+\mathbf{A})u_\alpha(\mathbf{k}-\mathbf{A})$。

- 在长波极限下展开 $f(\mathbf{k},\mathbf{A})$，并利用时间反演与反演对称性导致 Berry 曲率为零，得到

$$|f(\mathbf{k},\mathbf{A})|\approx 1-2g_{ij}(\mathbf{k})A_iA_j+\mathcal{O}(A^4)$$

其中**量子度量** $g_{ij}(\mathbf{k})=\text{Re}\langle\partial_i u_\mathbf{k}|(1-P_\mathbf{k})|\partial_j u_\mathbf{k}\rangle$，$P_\mathbf{k}=|u_\mathbf{k}\rangle\langle u_\mathbf{k}|$。

- 引入 Nambu 旋量 $\psi_\mathbf{k}=(c_\uparrow(\mathbf{k}),\,c_\downarrow^\dagger(-\mathbf{k}))^T$，逆格林函数展开到 $\mathcal{O}(A^2)$，得到包含 $\rho(\tau)$（Higgs 振幅涨落）与 $\mathbf{A}$ 的自能 $\Sigma(\mathbf{k},\tau)$；扩展的费米子行列式对场展开到四次，并积出费米子与 Higgs 场，得到**有效电磁作用**

$$S[\mathbf{A}]=\sum_{ijkl}\int d\omega\, A_{ij}^2(-\omega)K_{ijkl}(\omega)A_{kl}^2(\omega)$$

- **核心结果：THG 光学核分解**：

$$K_{ijkl}(\omega)=\underbrace{K^{qp}_{ijkl}(\omega)}_{\text{quasiparticle}}+\underbrace{K^{Higgs}_{ijkl}(\omega)}_{\text{Higgs mode}}$$

其中每个又分为常规 band 贡献与新的 geom 贡献：

$$K^{qp}_{ijkl}=\sum_\mathbf{k}\frac{1}{4}\partial_{ij}^2\xi_\mathbf{k}\partial_{kl}^2\xi_\mathbf{k}\chi_{33}(k,\omega)\quad(\text{band})\;+\;2\Delta_0\partial_{ij}^2\xi_\mathbf{k}\,g_{kl}(\mathbf{k})\chi_{13}(k,\omega)+4\Delta_0^2 g_{ij}(\mathbf{k})g_{kl}(\mathbf{k})\chi_{11}(k,\omega)\quad(\text{geom})$$

$$K^{Higgs}_{ijkl}(\omega)=-V_{ij}(\omega)G_H^0(\omega)V_{kl}(\omega),\quad V_{ij}(\omega)=\underbrace{\frac{1}{2}\sum_\mathbf{k}\partial_{ij}^2\xi_\mathbf{k}\chi_{13}(k,\omega)}_{V^{band}_{ij}}+\underbrace{2\Delta_0\sum_\mathbf{k}g_{ij}(\mathbf{k})\chi_{11}(k,\omega)}_{V^{geom}_{ij}}$$

- 泡图函数 $\chi_{\alpha\beta}(k,i\omega_m)=\frac{1}{\beta}\sum_{i\omega_n}\text{Tr}[G_0(k,i\omega_n)\tau_\alpha G_0(k,i\omega_n+i\omega_m)\tau_\beta]$。
- 对单色驱动 $A_i(t)=a_i e^{-i\Omega t}+a_i^* e^{i\Omega t}$ 做泛函微分，得到谐波电流 $j_m(3\Omega)=-4\sum_{jkl}[K^{qp}_{mjkl}(2\Omega)+K^{Higgs}_{mjkl}(2\Omega)]a_j a_k a_l$。

**可调二次能带接触（QBT）模型**：
- 设计两带模型使能带色散固定在 $E_+(\mathbf{k})=-2t(\cos k_x+\cos k_y)$ 与 $E_-(\mathbf{k})=-2t_b(\cos k_x+\cos k_y)+4(t_b-t)$；
- Bloch 态几何结构通过参数 $d_{\max}\in[0,1]$ 连续可调，$d_{\max}$ 物理上等于 Brillouin 区中**同一能带内 Bloch 态的最大量子距离**，并直接控制 $g_{ij}(\mathbf{k})\propto d_{\max}^2$；
- $d_{\max}=0$ 为几何平凡，$d_{\max}=1$ 为几何最大；
- 这一构造使**色散与量子几何可独立调节**，从而系统隔离几何效应；
- 取 Fermi 能足够远离 $\Gamma$ 点（$\Delta_0,\hbar\Omega,k_BT\ll\min_{\mathbf{k}\in\text{FS}}|E_+-E_-|$），可忽略带间配对与虚带间跃迁，单带有效理论自洽。

**定量计算参数**：$t=10$，$t_b=-5$，$\mu=-3t$，能带宽度 $W=8t=80$，取 $\Delta_0/W=0.1$，化学势 $\mu=-3t$，主要结果在 $d_{\max}\in[0,1]$ 上扫描。

**关联长度方案**：在 $A=0$ 下，将 Higgs 涨落有效作用展开到 $\mathbf{q}$ 二阶，得到 Ginzburg-Landau 型传播子 $\langle\rho(\mathbf{q})\rho(-\mathbf{q})\rangle\propto(r_\rho+A_{ij}q_iq_j)^{-1}$，定义 **Higgs 关联长度张量** $\xi_{H,ij}^2=A_{ij}/r_\rho$；类似地分解为 $\xi_{H,ij}^2=\xi_{\text{band},ij}^2+\xi_{\text{geom},ij}^2$，$\xi_{\text{geom},ij}^2\propto g_{ij}$。超流刚度 $D_{ij}=D_{ij}^{\text{band}}+D_{ij}^{\text{geom}}$。

---

## 主要发现与核心结论

> 注：所有数值与单位均严格保留原文。

### 1. THG 中 Higgs vs 准粒子的"几何相图"（Fig. 1(b)）

对 $\mu=-3t$，扫描 $(\Delta_0/W,\,d_{\max})$ 的 THG 强度比 $|J_{\text{tot}}^H|/|J_{\text{tot}}^{qp}|$：
- 在 $d_{\max}$ 小（$\lesssim 0.7$）时，体系为准粒子主导（蓝色区域）；
- $d_{\max}$ 增大进入 Higgs 主导（红色区域）；
- **$\Delta_0/W$ 越大（能带越平，几何效应越显著），Higgs 主导所需的临界 $d_{\max}$ 越小**，与 flat-band 极限自然衔接（Xiao-Hao 2025 已在理想 flat-band 中给出 Higgs 几乎全主导的结论，本工作把这一极限延拓到**色散带**）。

### 2. 几何诱发的"几个数量级"放大（Fig. 1(c)）

固定 $\Delta_0/W=0.1$，当 $d_{\max}\to 0$（几何平凡极限）时，THG 共振峰高比 $|J^H|/|J^{qp}|\sim 10^{-3}$，与常规 BCS 理论预期一致（准粒子主导）。

随 $d_{\max}$ 增加，该比值增长**几个数量级**（"several orders of magnitude"），将 THG 由准粒子反转为 Higgs 主导。

### 3. THG 谱中几何贡献的归属（Fig. 1(d)，$\Delta_0/W=0.1$，$d_{\max}=1$）

- 在共振点 $2\Omega/2\Delta_0\approx 1$，$J_{\text{tot}}^H$ 显著大于 $J_{\text{tot}}^{qp}$；
- **关键对比**：将"仅 band 部分"的 Higgs 贡献 $J_{\text{band}}^H$ **放大 500 倍**（"magnified by $\times 500$ for visibility"）后才能在谱中可见，这直接证明：Higgs 在 THG 中的放大**几乎完全来自几何项**；
- 几何项的具体来源：$V^{geom}_{ij}\propto \Delta_0\sum_\mathbf{k} g_{ij}(\mathbf{k})\chi_{11}(k,\omega)$，与 $\chi_{11}$ 通道相连。

### 4. Higgs 模式的空间刚性被几何放大（Fig. 2


## 合并自「2512.01200」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

I now have comprehensive content. Let me organize the structured notes.

---

# arXiv:2512.01200 — 结构化笔记

## 调研主题
**Role of Quantum Geometry in the Competition between Higgs Mode and Quasiparticles in Third-Harmonic Generation of Superconductors**
来源：[arXiv:2512.01200](https://arxiv.org/abs/2512.01200)
- 作者：Chang-geun Oh, Haruki Watanabe, Naoto Tsuji
- 提交日期：2025-12-01
- 领域：cond-mat.supr-con（超导）/ cond-mat.str-el（强关联电子）
- 核心发现1：量子度量（quantum metric）可显著放大 Higgs 模与光的非线性耦合达数个量级
- 核心发现2：建立可独立调控带几何与带色散的可调模型，证实几何项是 Higgs 主导 THG 的关键机制
- 核心发现3：Higgs 相关长度（关联长度）ξ 与超流刚度 D 亦被量子几何显著增强

---

## 研究问题（Research Question）

论文的核心问题是：**在干净极限（clean limit）下的单带超导体中，为什么 Higgs 模的三次谐波产生（THG）信号通常被准粒子激发所压制？是否存在一种新的机制能够让 Higgs 模反过来主导 THG 响应？** 具体而言，作者聚焦于电子 Bloch 态的量子几何（特别是量子度量 quantum metric）是否能够作为调控 Higgs 模与准粒子竞争的关键自由度。该问题的提出背景在于：传统 BCS 理论在干净体系中预言准粒子贡献压倒性占优（典型 Higgs/准粒子比值仅 ~10⁻³），这与若干实验中观测到的显著 Higgs 响应形成长期未解的张力。研究目标是从理论上建立一个可显式包含量子度量的形式框架，并通过可调模型量化几何贡献，最终提出"工程化量子几何"作为放大 Higgs 非线性响应的新路径。

## 研究背景（Background）

超导体不仅是理想导体，更是由 Cooper 对凝聚形成的宏观量子态，其中集体激发模式（如 Higgs 模，即幅值模）携带关于凝聚体本质的关键信息。THG（三次谐波产生）是探测 Higgs 模的主要光学手段，但其能量窗口（~2Δ₀）与准粒子对的破对（pair-breaking）阈值重叠，使两者信号极难区分。在干净极限下，BCS 理论预测准粒子贡献主导 THG；历史上主要通过两类机制打破这一格局：杂质散射 [Refs 26-31] 与声子推迟效应 [Ref 32]。与此同时，近场研究的"量子几何"（Berry曲率、量子度量）已被证明对超流密度 [Refs 34, 43]、非线性光学响应 [Refs 46] 等宏观可观测量有非平凡贡献，并且在平带（flat-band）极限下被预言能显著影响 Higgs 模 [Ref 66]。然而在此之前，**量子几何对 THG 中 Higgs/准粒子竞争的系统性作用**从未被显式建立。本工作的动机正是填补这一空白：从理论上将几何效应与色散效应解耦，建立量子度量放大 Higgs 非线性耦合的具体机制，并解释长期存在的"干净极限 Higgs 信号弱"谜题。

## 研究方法（Methods）

作者采用 **Keldysh 非平衡路径积分 + Hubbard-Stratonovich 解耦 + 投影到单一活跃带** 的方法处理超导序参量涨落与外加光场的耦合。具体步骤：(1) 写出包含轨道/自旋指标的完整作用量 S[c†,c,Δ∗,Δ]，在配对通道引入序参量场 Δ_αβ(τ)；(2) 通过 Nambu 自旋表象重写后变换到能带基（band basis），从而把矢量势 A 的耦合拆分为 Berry connection 项（线性）和 quantum metric g_ij(k) 项（∼A²ρ）；(3) 在时间反演 + 空间反演对称下 Berry 曲率为零，可选实规范消去 Berry connection，仅保留与 THG 相关的 A²ρ² 几何耦合；(4) 推导 THG 电流公式 j_m(3Ω) = -4 K_{mjkl}(2Ω) a_j a_k a_l，将响应核 K 分解为准粒子项 K_qp = K_qp^band + K_qp^geom 与 Higgs 项 K_Higgs(ω) = -V_ij(ω) G⁰_H(ω) V_kl(ω) 两部分，二者各自再分解为色散贡献与几何贡献。模型上采用 **可调的 quadratic band touching (QBT) 模型**，含 t 与 t_b 两种跃迁，定义参数 d_max 调控量子度量而保持能带色散 E±(k) 不变；极限 d_max=0给出几何平庸的两个解耦方格子（每个轨道单独最近邻跃迁），极限 d_max=1 进入 Higgs主导区。数值计算中取 t=10, t_b=-5, μ=-3t, Δ₀/W=0.1（W=8t 为带宽）。

## 主要发现与核心结论（Main Results）

(1) **几何放大效应数量级显著**：在 QBT 模型中，固定 Δ₀/W=0.1，d_max→0（几何忽略）时 Higgs/准粒子 THG 峰值比约为 ~10⁻³，与 BCS 标准预期一致；d_max增至 1 时，Higgs 模响应被几何项放大数个量级，超过准粒子贡献，进入 Higgs 主导区（图1c）。
(2) **平带放大效应**：图1显示，固定 Δ₀/W 时 d_max 越大 Higgs 越主导；进一步增大 Δ₀/W（向平带极限 Δ₀/W≫1 移动）会降低达到 Higgs 主导所需的临界 d_max。即**平带结构使非线性响应对量子几何更敏感**，为 flat-band 极限下几何效应增强提供清晰路径。
(3) **几何项在小 d_max 下"看不见 Higgs"**：图1(d) 在 Δ₀/W=0.1, d_max=1 的 Higgs 主导区，传统仅含色散的 Higgs 流 j_H^band 极小，必须放大 500 倍才能与 j_H^geom 同图显示——直接证明几何是 Higgs 信号被放大的真正机制。
(4) **Higgs 相关长度由几何主导**：对超导序参量涨落的有效作用量给出刚度张量 A_ij = A_ij^band + ξ²_geom·g_ij；几何贡献与量子度量直接挂钩。QBT 模型下几何/色散对 ξ²_xx 的比值从零增长到 >1，发生从色散主导到几何主导的转变，**量子度量是决定凝聚体幅值空间刚度的关键变量**。
(5) **超流刚度亦获几何增强**：D_ij = D_ij^band + D_ij^geom 形式与既有结论 [34,43] 一致；d_max 增大时 D_xx 单调增强，几何/色散比亦增大。
(6) **核心结论**：量子几何（特别是 quantum metric）是超导体非线性光学响应中一个**此前被忽略的关键自由度**；通过电场、应变等手段调控量子几何，可设计出 Higgs 主导 THG 的超导材料，从而放大集体动力学信号。

## 潜在研究方向（Future Directions）

(1) **实验直接验证**：作者明确提出"在调节量子几何（例如施加电场或应变）的同时探测 THG 响应"可作为本理论的直接检验，未来工作可寻找具有大量子度量的实际超导体系（如扭转多层石墨烯、kagome 超导体、flat-band 笼合物超导体）做 THG 实验。
(2) **与既有放大机制的正交性**：杂质散射 [Refs 26-31] 与声子推迟 [Ref 32] 已被证明能放大 Higgs 模，量子几何是与之正交的第三条路径；未来工作应系统比较三者贡献并探索耦合效应。
(3) **二维相干光谱中的几何效应**：作者指出 [Ref 71] 预言无序超导体的二维相干光谱中也存在类似 Higgs/准粒子竞争，但量子几何在其中的作用尚属开放问题。
(4) **平带极限的定量研究**：Δ₀/W≫1 区间的几何贡献定量行为尚未充分探讨；平带超导体（如 twisted bilayer graphene near magic angle）的 THG 实验将是关键测试。
(5) **理论形式上的开放问题**：当前分析假设时间反演 + 空间反演对称（Berry 曲率为零）；打破这些对称、引入非零 Berry 曲率（如手性超导体）后，几何对 THG 的修正形式及与反常输运的耦合是尚未触及的方向。
(6) **多带与轨道自由度**：模型投影到单一活跃带，多带系统中带间量子几何（interband quantum metric）与 Higgs 模耦合的贡献尚未涉及。
(7) **有限温度与涨落效应**：分析在静态长波极限下完成，T_c 附近热涨落对几何项的修正、非平衡泵浦-探测几何动力学等均为开放方向。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：量子几何在 Higgs 模与磁振子竞争中作用的理论（单带投影多带超导 + 配对重叠 f(k,A) 形式论）

**原理**：单带投影的多带超导形式论：HS 配对通道解耦引入序参量场，local pairing 假设下仅动能项被规范场修改；三假设（正常态 TR+反演对称/单带主导费米面/均匀同轨道配对 Δ_αβ=Δδ）；配对重叠 f(k,A)=⟨u_{k+A}|u_{k−A}⟩ 编码量子几何（量子度规/Berry 曲率）进入等效低能作用量——分析量子几何在 Higgs 模与磁振子（spin resonance）竞争中的角色。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 三假设 | (i) 正常态 TR+反演对称；(ii) 单带主导 Fermi 面；(iii) 均匀同轨道配对 Δ_αβ=Δδ_αβ | §形式化框架 |

**适用边界**：三假设（尤其同轨道配对）为几何贡献显现的前提；ℏ=e=c=1 单位；页面提取限形式论框架（竞争结果在正文）。
**代表作**：本文（arXiv:2512.01200）；假设源流：Peotta-Törmä、Törmä-Peotta-Bernevig
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2512.01200]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[MnPS3]]
- [[general-berry-mnps3-rashba-20260816]]
- [[quantum metric]]
- [[强场超快]]
- [[强场超快光学]]
- [[莫尔超晶格]]
- [[量子几何]]
- [[量子度规]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
