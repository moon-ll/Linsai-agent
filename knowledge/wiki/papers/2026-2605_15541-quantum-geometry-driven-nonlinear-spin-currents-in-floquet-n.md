---
title: "2026-2605_15541-quantum-geometry-driven-nonlinear-spin-currents-in-floquet-n"
type: "papers"
created: "2026-08-30T08:28:51Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["2605.15541", "Berry curvature dipole", "Berry 曲率", "Berry曲率", "Berry曲率偶极", "Floquet工程", "MnPS3", "arpes", "general-berry-mnps3-rashba-20260816", "quantum metric", "交变磁体", "位移电流", "反常速度", "强场超快", "强场超快光学", "强场驱动", "自旋劈裂", "谷霍尔效应", "量子几何", "量子几何张量", "量子度规", "非线性光学"]
source_raw: "2026-2605.15541-quantum-geometry-driven-nonlinear-spin-currents-in-floquet-n.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:38Z"
merged_from: ["wiki/papers/2605.15541.md"]
---

# Quantum Geometry-Driven Nonlinear Spin Currents in Floquet Non-Hermitian Altermagnets — Deep Research Note

## 林赛的理解

作为强场超快光学 PI，我读这篇工作最直接的感受是：**它把"量子几何—量子几何驱动响应—Floquet/周期驱动—非厄米"这条逻辑链搬进了交变磁（altermagnet）自旋电子学里，并明确指出在 Floquet 工程后的 d-wave 交变磁体中，非线性自旋流是被 quantum metric（不是 Berry curvature、不是 Berry connection dipole）所主导**。这件事对我们组意义在于：(i) 它把"光学偏振（ϕ）作为主动旋钮"做了完整理论化——这是我们组在 HHG/阿秒/强场驱动实验中已经在玩的事，只是对象换成了自旋流而非谐波；(ii) 它给出的表达式是 band-renormalized quantum metric $G^{LR}_{\mu\nu}$、biorthogonal 态 $\psi^L/\psi^R$、covariant derivative $D_\nu$ 等一套完整几何语言，与我们目前 Berry-MnPS3-Rashba 课题里的强场相位/几何相位框架可以对接；(iii) 论文已经把参数拍定（$\omega=10$, $t_0=0.5$, $\alpha=0.2$ 等），数值复现门槛低，可以快速做 benchmark 与拓展。

具体地，这篇文章对我们正在进行的"berry-MnPS3-rashba"课题的接口有四条：(a) Floquet 展开的 Jacobi-Anger + 高频极限 $\omega\gg t_0$，几乎可以原样套到 MnPS3 的光驱动哈密顿量上；(b) 量子几何张量（QGT）分解 QM/BC/BCD 三块的思路与 Rashba/非中心对称体系中的非线性位移电流框架同构；(c) "upper band 稳态输运主导"的论据来自 Im$\xi_n$ 的 lifetime 论证，可以延伸到莫尔（moiré）平带等具有强虚部能谱的体系；(d) 文章建议的 RuO$_2$/Permalloy 异质结构 + 太赫兹发射实验，是我们做"光—自旋—THz"闭环的天然实验锚点。

## 研究问题（Research Question）
本文要回答的核心问题是：**如何在交变磁体（altermagnet）中实现自旋响应的动态调控，并把这种调控的物理根源归结为量子几何量？** 论文的中心论点可以分解为三层：

1. **框架问题**：在具有谱线隙（spectral line gap）的非厄米（non-Hermitian）相中，二阶非线性自旋电导率 $\sigma^{i\mu\nu}_{\alpha}$ 是否可以被解析地分解为三个量子几何贡献之和？
2. **物理问题**：对于 Floquet 驱动的 d-wave 交变磁体，这个非线性自旋流的三个分量（几何项 $\Gamma_{\rm geom}$、磁电自旋霍尔项 $\Gamma_{\rm magneto}$、极化项 $\Gamma_{\rm polar}$）哪个占主导？
3. **可控性问题**：周期光场的偏振参数（相位 $\phi$）能否作为主动旋钮，在不改变材料的前提下切换——甚至严格反转——纵向与横向自旋流的方向？

## 研究背景（Background）
**学术脉络**可以梳理为四条并行的线索，本文处于其交汇点。

1. **非厄米拓扑与对称性扩展**：传统 10 重 Altland-Zirnbauer 分类在非厄米下破裂，转座（transposition）和复共轭不等价，时间反演与粒子—空穴对称性解耦，扩展为 38 重 Bernard-LeClair 分类。点隙（point gap）拓扑由非厄米趋肤效应（NHSE）主导；而线隙（line gap）相虽可绝热连通厄米系统，但其非厄米性仍对响应函数有本质修正。

2. **量子几何张量（QGT）与量子度量（QM）的兴起**：QGT 是把 Berry curvature（BC, $\Omega$）和 quantum metric（QM, $G$）统一在一个复几何对象中的工具。QM 度量 Hilbert 空间中相邻态的距离，在拓扑相中被 BC 从下方界定、并与量子 Fisher 信息直接挂钩。近年 QM 被发现支配：超流权重、线性与非线性光学电导率、非线性量子谷霍尔效应等宏观可观测量。

3. **交变磁（altermagnet）作为第三类共线磁有序**：传统仅识别铁磁（全局破缺 $\mathcal{T}$，净磁矩）和反铁磁（净磁矩为零，亚晶格反平行）。Šmejkal–Sinova–Jungwirth 的对称性分类证明动量依赖的自旋劈裂对应第三类基础磁相。实验锚点：金属性 RuO$_2$、半导体 MnTe；ARPES 与输运测量已确认其标志性动量依赖自旋劈裂。

4. **Floquet 工程用于磁性体系**：周期性光场已在反铁磁中动态解除 Kramers 自旋简并、产生稳态纯自旋流、构造光致奇字称磁态。Floquet 提供了把"gapless 体系变成 line-gapped 体系"这一关键操作。

**研究动机**：上述四条线索天然地汇聚于一个未回答的问题——在交变磁体里，光学 Floquet 工程 + 非厄米（通过铁磁邻层耦合引入复自能）能否为非线性自旋输运提供量子几何级的解析控制？本文填补这一空缺。

## 研究方法（Methods）
**数据/模型来源**：纯解析 + 数值计算。没有任何实验数据，但论文末尾给出了实验可行性方案。

**理论框架**：

- **Biorthogonal 基底**：非厄米系统需用左右本征态 $\psi^L_{n,k}, \psi^R_{n,k}$ 描述。Berry 连接 $A^{LR}_{mn,\mu}=i\langle\psi^L_{m,k}|\partial_\mu \psi^R_{n,k}\rangle$，量子度量 $G^{LR}_{\mu\nu}$。
- **Schrieffer-Wolff（SW）变换**：把含电场偶极相互作用 $-eE\cdot \hat r$ 的哈密顿量做块对角化，得到一阶 $S^{(1)}_{mn}=eE_\mu A^{LR}_{mn,\mu}$ 与二阶 $S^{(2)}_{mn}=-ie^2 E_\mu E_\nu D_\nu A^{LR}_{mn,\mu}/(\xi_n-\xi_m)$，其中 $D_\nu$ 为协变动量导数。
- **半经典自旋流**：$J^\alpha_i=\int_k f_k s_n \dot r_i$。Fermi-Dirac 分布采用 $f_k=[1+\exp({\rm Re}\,\xi_n/k_BT)]^{-1}$，$\hbar=k_B=e=1$。
- **Floquet 有效哈密顿量**：高频极限 $\omega\gg t_0$ 下，Jacobi-Anger 展开给出 $H_{\rm eff}(k,\phi)=H(k)+\frac{1}{\omega}[H_1(k,\phi),H_{-1}(k,\phi)]$。

**材料/模型体系**：2D 平方格子 d-wave 交变磁体，总哈密顿量
$$H(k)=H_0(k)+H^d_{\rm AL}(k)+H_R(k)+H_{\rm NH}-\mu\sigma_0,$$
具体分量：
- $H_0(k)=[-2t_0(\cos k_x+\cos k_y)-\mu]\sigma_0$
- $H^d_{\rm AL}(k)=\alpha[2\sin k_x\sin k_y\sin 2\theta+(\cos k_x-\cos k_y)\cos 2\theta]\sigma_z$
- $H_R(k)+H_{\rm NH}=\lambda_R(\sin k_y\sigma_x-\sin k_x\sigma_y)-i(\gamma\sigma_x+\Gamma\sigma_0)$

非厄米自能参数：$\gamma=(\Gamma_\uparrow-\Gamma_\downarrow)/2$、$\Gamma=(\Gamma_\uparrow+\Gamma_\downarrow)/2$，由 $x$ 极化铁磁邻层诱导。

**驱动场**：椭圆偏振矢势 $A(t)=A(\sin\omega t,\cos(\omega t+\phi))$，通过 Peierls 替换 $k_{x,y}(t)=k_{x,y}+A(\sin\omega t,\cos(\omega t+\phi))$ 引入时间依赖。

**数值参数**（贯穿全文）：
- $t_0=0.5$, $\alpha=0.2$, $\lambda_R=0.01$, $\Gamma=0.05$, $\gamma=0.25$, $\theta=\pi/4$（即 d$_{xy}$ 对称性）, $\omega=10$, $T=0.01$, $A=1$
- Fig. 1 用 $\phi=\pi/2$；Fig. 2 用同一参数；Fig. 3 用 $\mu=-0.3$。

**关键技术**：
1. SW 变换分两阶给出 $\Gamma_{\rm geom}$（Eq. 2）、$\Gamma_{\rm magneto}$（Eq. 3）、$\Gamma_{\rm polar}$（Eq. 4）三个分离的贡献项；
2. Floquet 展开把无隙的原始 d-wave 谱打开成 line gap，使整个 line-gapped 非厄米理论框架可应用；
3. 取目标带 $n$ 为上带（蓝带）——下带（灰带）因 ${\rm Im}\,\xi_n$ 更负、寿命显著更短，作为瞬态模式被忽略；
4. 数值分解三贡献（绿/黑/蓝）在 Fig. 2、3 中以颜色叠加于总响应（红圈）。

## 主要发现与核心结论

**核心解析结果（Eq. 1）**：线隙非厄米相中本征非线性自旋电导率分解为三部分
$$\sigma^{i\mu\nu}_\alpha=\int_k f_k\bigl(\Gamma^{i\mu\nu}_{\rm geom}+\Gamma^{i\mu\nu}_{\rm magneto}+\Gamma^{i\mu\nu}_{\rm polar}\bigr).$$
各分量的物理含义：
- $\Gamma_{\rm geom}$（Eq. 2）：平衡自旋 $s^\alpha_{nn}$ 被二阶异常速度搬运，物理上是 **non-Hermitian 自旋极化的位移电流**（shift current 模拟物）；
- $\Gamma_{\rm magneto}$（Eq. 3）：一阶场致自旋极化被一阶反常 Hall 速度横向推动，表现为 **intrinsic 非线性自旋霍尔效应**；
- $\Gamma_{\rm polar}$（Eq. 4）：二阶自旋极化被无扰群速度 ${\rm Re}[\partial_i\xi_n]$ 纵向搬运，包含 **quantum polarizability/Berry dipole**。

**数值结果**：

1. **QM 占主导**（Fig. 1、2、3 一致结论）：$\sigma^{yyy}_z$、$\sigma^{xxx}_z$、$\sigma^{xyy}_z$、$\sigma^{yxx}_z$ 四个分量在 $-0.5\lesssim\mu\lesssim 0.5$ 范围内都几乎完全跟着 $\Gamma_{\rm geom}$（绿色）走。$\mu\approx 0$ 附近 Berry curvature dipole（黑色）的极化项有少量贡献，但仍被 QM 压过。结论："the bare quantum metric predominantly dictates these nonlinear spin responses."

2. **化学势控制**：Figs. 1(b)–(f) 显示 $g_{xy}$（QM 实部）与 $\Omega$（Berry curvature）在不同 $\mu$ 下集中分布于动量空间不同位置；通过调节 $\mu$ 可以让 Fermi 海与高几何密度区重叠/不重叠，从而调控 INSC。

3. **偏振 $\phi$ 可反转自旋流方向**（Fig. 3 的最强结论）：$\sigma^{xxx}_z$ 与 $\sigma^{xyy}_z$ 随 $\phi$ 变化出现 **严格符号反转（strict sign reversal）**。总响应（红圈）与几何项（绿色）**完美贴合（perfectly track）**，而 $\sigma^{yyy}_z$、$\sigma^{yxx}_z$ 的总响应则与 $\Gamma_{\rm geom}$ 完全重合、且与 $\Gamma_{\rm magneto}$ 解耦。这意味着：**偏振 $\phi$ 是主动选向旋钮**，纵向与横向自旋流方向都可纯光控反转。

4. **重要细节**：
   - Floquet 工程把原始无隙 d-wave 谱打开为 line gap（Fig. 1(b)），从而使 line-gapped 框架适用；
   - 在低 $T=0.01$ 下，式 (1)–(4) 表明 INSC 取决于 Fermi 海内 QM 与 BC 的分布；
   - 实验建议：RuO$_2$/Permalloy 异质结构 + 飞秒激光脉冲 + time-resolved terahertz emission spectroscopy。

## 潜在研究方向（Future Directions）
1. **波包宽度与弛豫时间 $\tau$ 的影响**：本文明确排除了 $E\tau$（电场—寿命）乘积效应，因为只考察 intrinsic 几何贡献。但在实验尺度，$\tau$ 与 wave-packet width 的耦合是真实存在的，理论与实验如何桥接需要进一步考虑。

2. **下带（低带）的贡献**：作者论证下带因 Im$\xi_n$ 更负、寿命更短，作为瞬态模式被忽略。这在长期稳态输运下成立，但对短脉冲（飞秒—阿秒）驱动的瞬态自旋流，下带的相干叠加可能产生可观修正。这是 **强场超快实验最直接的拓展方向**。

3. **非微扰强场区**：Floquet 有效哈密顿量建立在高频极限 $\omega\gg t_0$（论文取 $\omega=10$、$t_0=0.5$）和弱场 $A=1$ 上。向更高 $A$、更低 $\omega$（包含共振、非微扰 HHG 区）扩展会触及 non-perturbative 区域，与我们组强场方向的耦合点最深。

4. **3D / 莫尔扩展**：当前模型是 2D 平方格子 d-wave AM。莫尔（moiré


## 合并自「2605.15541」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

全文已读取（9页，含附录A/B全部推导）。以下为结构化笔记：

---

# 论文笔记：arXiv 2605.15541

**标题**：Quantum Geometry-Driven Nonlinear Spin Currents in Floquet Non-Hermitian Altermagnets
**作者**：Kai Chen, Jie Zhu（同济大学物理科学与工程学院）
**arXiv**: 2605.15541v1 [cond-mat.mes-hall, cond-mat.mtrl-sci]，2026-05-15 提交，9页（PRL格式）
**URL**: https://arxiv.org/abs/2605.15541

## 研究问题（Research Question）

论文的核心问题是：如何在交变磁体（altermagnet）中实现自旋响应的**动态、可逆调控**——这是自旋电子学应用的基础性挑战，因为传统手段难以对反铁磁类零净磁矩体系的自旋输运进行主动操纵。中心论点是：将周期性光驱动（Floquet工程）与非厄米性（通过铁磁近邻工程化引入）结合，可以为这类体系提供一条全新的可调谐控制路径。具体目标有两个：(1) 推导线隙（line-gapped）非厄米系统中非线性自旋流的一般解析表达式，并阐明其与量子几何张量的内在联系；(2) 以Floquet非厄米d波交变磁体为范例，演示光场偏振作为“主动旋钮”对自旋流方向的选择甚至严格反转。

## 研究背景（Background）

非厄米物理方面：非厄米趋肤效应与点隙拓扑已被广泛研究，而线隙非厄米相虽可绝热连接到厄米系统，但其复谱与双正交量子态（biorthogonal states）仍对拓扑分类（10重AZ类扩展为38重Bernard-LeClair类）和外场响应有本质性修正。量子几何方面：拓扑不变量只反映量子态空间几何的一部分，其余信息由量子度规（QM）刻画——QM被Berry曲率下界约束、直接决定量子Fisher信息，并已知的支配超流权重、线性/非线性光电导、非线性量子谷霍尔效应等宏观响应。磁性材料方面：对称性分类正式确立了交变磁性作为继铁磁、反铁磁之后的第三种基本共线磁相（动量依赖的自旋劈裂，Šmejkal et al. PRX 2022），RuO₂（金属）与MnTe（半导体）已由ARPES和输运实验直接证实交磁自旋劈裂。关键空白在于：非厄米系统的非线性**电**响应（尤其是量子度规的作用）已有系统研究，但非线性**自旋流**响应及其在磁性系统中的应用此前基本未被探索；同时Floquet工程已被证明可在共线反铁磁中动力学解除Kramers简并、产生稳态纯自旋流，但尚未与非厄米交变磁性及量子几何框架结合。

## 研究方法（Methods）

理论框架：在半经典Boltzmann框架下定义自旋流 Jₛ = ∫ₖ fₖ sₙ ṙ（fₖ 由复本征能实部 Re ξₙ 构成的Fermi-Dirac分布），对含电偶极扰动 −eE·r 的非厄米哈密顿量做逐阶 Schrieffer-Wolff 变换（至E²阶，附录A给出完整推导），得到二阶 intrinsic 非线性自旋电导张量 σ = ∫ₖ fₖ (Γᵍᵉᵒᵐ + Γᵐᵃᵍⁿᵉᵗᵒ + Γᵖᵒˡᵃʳ)，全部以双正交量表示：非厄米Berry联络 Aᴸᴿ、带重整化量子度规 Gᴸᴿ、双正交自旋矩阵元 sᵅₘₙ。模型哈密顿量：二维方格子d波交变磁体 H = H₀ + Hᴬᴸ_d + Hᴿ + H_NH，其中d波交磁项以Néel矢量沿z、角度θ参数化（θ=0对应dₓ²₋ᵧ²，θ=π/4对应d_xy），Rashba项（λ_R=0.01）来自结构反演不对称，非厄米项 −i(γσₓ + Γσ₀) 源自与x偏振铁磁电极的自旋依赖界面耦合（γ=(Γ↑−Γ↓)/2, Γ=(Γ↑+Γ↓)/2）。光驱动：椭圆偏振矢势 A(t)=A(sin ωt, cos(ωt+φ))，高频极限（ω=10 ≫ t₀=0.5）下用Jacobi-Anger展开与Peierls替换映射到静态Floquet有效哈密顿量 H_eff = H + [H₁,H₋₁]/ω（附录B给出hₓ,hᵧ,h_z解析式），驱动打开线隙从而满足理论前提；下带因虚部更负而快速衰减为瞬态模，稳态输运由上带主导。数值参数：t₀=0.5, α=0.2, λ_R=0.01, Γ=0.05, γ=0.25, θ=π/4, φ=π/2, ω=10, T=0.01, A=1，对化学势μ和相位延迟φ扫描并做BZ积分。

## 主要发现与核心结论（Main Results）

**核心解析结果（式1–4）**：intrinsic非线性自旋电导干净地分解为三个几何来源——(i) Γᵍᵉᵒᵐ：量子度规动量梯度的“自旋极化位移流”项；(ii) Γᵐᵃᵍⁿᵉᵗᵒ：Berry曲率反常速度引起的“非线性自旋霍尔”型横向偏转项；(iii) Γᵖᵒˡᵃʳ：Berry联络偶极（量子极化率）项。该分解不依赖弛豫时间τ和波包宽度，是纯几何的 intrinsic 贡献。**定量发现（图2）**：纵向（σᶻₓₓₓ, σᶻᵧᵧᵧ）和横向（σᶻₓᵧᵧ, σᶻᵧₓₓ）自旋电导几乎完全由裸量子度规主导——总响应（红圈）与几何项（绿）基本重合；仅在μ≈0附近极化项（Berry曲率偶极）有附加贡献，但QM相关项仍占主导。化学势μ通过调制费米海与量子几何热区（g_xy、Ω在BZ中的集中分布，图1c–f）的重叠来有效调控INSC。**偏振调控（图3）**：光场相位延迟φ强烈改变能带结构与QGT分布，总响应严格跟随Γᵍᵉᵒᵐ，其中纵向分量σᶻₓₓₓ和横向分量σᶻₓᵧᵧ随φ变化出现**严格符号反转**——即仅靠光偏振即可主动选择乃至反转纵向/横向自旋流方向，实现全光操控。**结论与实验方案**：论文建立了非厄米量子几何→非线性自旋输运的完整框架，建议在交磁/铁磁异质结（如RuO₂/坡莫合金）中用飞秒激光驱动、通过时间分辨太赫兹发射谱直接探测该非线性自旋输运。

## 潜在研究方向（Future Directions）

**实验验证层面**：全部分析基于理想化模型，RuO₂/坡莫合金异质结+飞秒激光+THz发射探测的实验方案尚属提议，实际材料中界面自旋依赖耦合强度（γ, Γ）、Rashba参数的可实现性需材料学验证。**理论近似层面**：(1) 高频非共振Floquet近似（ω=10 ≫ t₀）忽略了共振吸收与加热效应，实际Floquet系统有限寿命与周期稳态（periodic steady state）问题未处理——作者虽假设下带快速衰减有利稳态，但真实驱动下的耗散通道需进一步研究；(2) 只保留intrinsic（τ无关）贡献，外禀/无序散射、Drude型非线性项被明确排除，与实验对比时需补充；(3) 线隙条件由驱动诱导打开，对一般无能隙节点的交变磁体（如本征d波节点结构）公式不能直接套用。**模型扩展层面**：数值仅做了θ=π/4（d_xy）与小λ_R情形，其他d波取向、g波/i波交变磁性、三维体系、有限温度与有限频率（偏离高频极限）情形均未探索；自旋流仅讨论z极化分量。**与本课题（Berry/MnPS₃/Rashba）的关联**：该工作给出“量子度规+Berry曲率+Berry联络偶极”三通道分解的传输端范例，且其中Rashba SOC与结构反演不对称、Floquet偏振调控自旋流的机制与MnPS₃ Rashba课题中“量子几何非线性光学读出”的构想高度互补——开放问题包括：该QGT分解框架能否移植到非线性光学响应（如高次谐波）作为量子几何的光学探针，以及非厄米（铁磁近邻）与Floquet调控在二维磁性材料（MnPS₃类）中的可实现性。

---

来源：[arXiv:2605.15541 — Quantum Geometry-Driven Nonlinear Spin Currents in Floquet Non-Hermitian Altermagnets](https://arxiv.org/abs/2605.15541)（全文PDF已解析，含附录A/B完整推导）

笔记要点：这是2026年5月的新论文（非旧文献），与课题 general-berry-mnps3-rashba-20260816 的“研究方案”环节高度相关——它把量子几何三分解（度规/曲率/联络偶极）从光学响应搬到了自旋输运，并证明偏振可严格反转自旋流方向。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：线隙非厄米体系二阶非线性自旋流的量子几何三分解（Schrieffer-Wolff + Floquet）

**原理**：对含电偶极扰动 −eE·r 的非厄米哈密顿量做逐阶 Schrieffer-Wolff 变换，在双正交（左右本征态）基底下半经典推得二阶 intrinsic 非线性自旋电导的三分量分解：量子度规位移流 Γ_geom、Berry 曲率非线性自旋霍尔 Γ_magneto、Berry 联络偶极/量子极化率 Γ_polar；高频椭圆偏振 Floquet 驱动（Jacobi-Anger 展开 + Peierls 替换）打开 line gap 使线隙非厄米框架适用，上带主导稳态输运。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 模型体系 | 2D 方格子 d-wave 交变磁体 H = H₀ + H^d_AL + H_R + H_NH（Néel 角 θ 参数化，θ=π/4 对应 d_xy） | 研究方法 |
| 数值参数 | t₀=0.5, α=0.2, λ_R=0.01, Γ=0.05, γ=0.25, ω=10, T=0.01, A=1（Fig. 3 用 μ=−0.3） | 研究方法 |
| Floquet 极限 | 高频 ω=10 ≫ t₀=0.5，H_eff = H + [H₁,H₋₁]/ω | 研究方法 |
| 驱动场 | 椭圆偏振 A(t)=A(sin ωt, cos(ωt+φ))，Peierls 替换引入 | 研究方法 |
| 非厄米自能 | −i(γσ_x+Γσ₀)，γ=(Γ↑−Γ↓)/2、Γ=(Γ↑+Γ↓)/2，由 x 极化铁磁邻层诱导 | 研究方法 |
| 单位制 | ħ=k_B=e=1；Fermi 分布由 Re ξ_n 构成 | 研究方法 |

**适用边界**：纯理论工作（无实验数据，实验建议 RuO₂/Permalloy 异质结 + 飞秒激光 + 时间分辨 THz 发射谱）；仅 intrinsic τ-无关贡献，排除 Eτ 乘积与外禀散射；高频非共振近似忽略共振吸收与加热；线隙须由驱动诱导打开，无能隙节点体系不能直接套用；下带因寿命短被忽略，飞秒瞬态驱动下相干叠加可能产生可观修正；数值仅覆盖 θ=π/4、2D、z 极化自旋流。
**代表作**：Chen & Zhu（同济），arXiv:2605.15541 (2026)，PRL 格式 9 页含附录 A/B 完整推导。核心结论：量子度规主导四类自旋电导分量（总响应与 Γ_geom 完美贴合），光场偏振 φ 使 σ^xxx_z 与 σ^xyy_z 严格符号反转。
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[2605.15541]]
- [[Berry curvature dipole]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[Berry曲率偶极]]
- [[Floquet工程]]
- [[MnPS3]]
- [[arpes]]
- [[general-berry-mnps3-rashba-20260816]]
- [[quantum metric]]
- [[交变磁体]]
- [[位移电流]]
- [[反常速度]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[自旋劈裂]]
- [[谷霍尔效应]]
- [[量子几何]]
- [[量子几何张量]]
- [[量子度规]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
