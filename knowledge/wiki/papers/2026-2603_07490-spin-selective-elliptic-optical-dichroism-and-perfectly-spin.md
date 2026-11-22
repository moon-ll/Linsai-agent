---
title: "2026-2603_07490-spin-selective-elliptic-optical-dichroism-and-perfectly-spin"
type: "papers"
created: "2026-08-30T08:27:18Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2603.07490", "A", "B", "Berry 曲率", "MnPS3", "general-berry-mnps3-rashba-20260816", "quantum metric", "交变磁体", "反常霍尔效应", "拓扑绝缘体", "自旋劈裂", "量子几何", "量子几何张量", "量子度规", "非线性光学"]
source_raw: "2026-2603.07490-spin-selective-elliptic-optical-dichroism-and-perfectly-spin.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:43:22Z"
merged_from: ["wiki/papers/2603.07490.md"]
---

# Spin-selective elliptic optical dichroism and perfectly spin-polarized third-order nonlinear photocurrent in altermagnets — Deep Read Notes

## 林赛的理解

这篇工作把 *d*-波交替磁体（altermagnet）从"被动能带材料"提升为"主动光学自旋电子学平台"：通过把椭圆度（ellipticity *ϑ*）当作自旋通道选择器，把椭圆光二向色性（elliptic dichroism）与 jerk current 串联起来，给我呈现了一条 *完全光子驱动的、无需磁场或自旋轨道耦合的自旋极化电流* 路线。对我们组而言，最关键的洞察不是"又一个磁体"而是 ——**量子度量 g_{μν}(k) 与 Berry 曲率 Ω(k) 不仅决定了光学吸收，也决定了 *j* ∝ *E*³ 的非线性光电流**，即"量子几何量"统一层化了光的线性吸收与三阶电荷流响应。这意味着同一个 δ 函数选律（同时制约着椭圆光二向色性与 jerk 电流）可以成为我们 HHG/阿秒研究中谱滤波、阿秒电流生成的素材库。从应用角度，*绝缘的 d-波交替磁体* 由于 inversion 屏蔽了所有二阶响应（injection/shift），jerk 上升为 *leading-order*——这与我们在 Mott/charge-order 绝缘体看到的"high-harmonic 在 gap 边缘增强"机制高度同构。结合我们组正在做的一般-band-touching/d-wave 几何工程，把这篇工作视为"光-自旋界面"的指南针：自旋通道来自 C₄zT 动量-自旋锁，能流密度由量子几何大小（quantum geometry）控制。

## 研究问题（Research Question）
论文聚焦的核心问题有三：

1. **d-波交替磁体的低能描述**：C₄zT 对称下 spin-split 能带能否用一对耦合的各向异性 Dirac 锥（X 与 Y 点）来描写？
2. **椭圆光二向色性自旋选择**：在具有 C₄zT 自旋-动量锁的体系里，能否通过 *调入射光的椭圆度* 实现 *完全自旋选择性*（只激发上自旋或下自旋）的光吸收？
3. **完全自旋极化的领头光电流**：在 *绝缘的* d-波交替磁体中（inversion 屏蔽掉 injection/shift 等二阶响应），三阶 jerk 电流在椭圆偏振光 + 静电场同施加时是否为 leading 阶响应、能否成为 *完全* 自旋极化的电流？

作者给出的中心论点是肯定的，并通过 *g(k;ϑ) = g_xx cos²ϑ + g_yy sin²ϑ + Ω_xy sinϑ cosϑ* 公式将椭圆光二向色性与 jerk 电流都用同一组量子几何量表达，建立了"自旋选择 = 几何投影"的统一图像。

## 研究背景（Background）
- **Alternmagnets 的范式提出**：Šmejkal/Sinova/Jungwirth 2022（Phys. Rev. X 12, 031042 及 040501）确立"共线反铁磁体但破缺时间反演"的第三类磁体。Naka et al. (Nat. Commun. 10, 4305, 2019；Phys. Rev. B 103, 125114, 2021) 与 Šmejkal et al. (Phys. Rev. Lett. 126, 127701, 2021) 演示了 *d*-波 alternmagnet 中的电场驱动自旋流（spin splitter）。Bose et al. (Nature Electronics 5, 267, 2022) 在 RuO₂ 中观测到 tilted spin current。
- **d-波 alternmagnet 关键对称性**：spin-split 关系受 C₄zT = (4-fold rotation) ∘ (time reversal) 保护 —— 90° 动量旋转将自旋翻转。文献 [9]（Fu et al., arXiv:2507.22474）给出的四方格子 Lieb 衍生模型已经通过 DFT 验证，Ezawa（Appl. Phys. Express 19, 030101, 2026；Phys. Rev. B 111, L201405, 2025；112, 045302, 2025；112, 155308, 2025）把 *p/f/g/i* 等多极交替磁体与量子几何统一语言连接起来。
- **Circular → elliptic dichroism 的演化**：W. Yao/Xiao/Niu (Phys. Rev. B 77, 235406, 2008)、Xiao et al. (Phys. Rev. Lett. 108, 196802, 2012)、Ezawa (Phys. Rev. B 86, 161407(R), 2012; 89, 195413, 2014) 在 honeycomb 与拓扑晶体绝缘体表面确立了 *用椭圆偏振光实现谷选择的* 椭圆光二向色性公式。本工作就是这条思路在 *d*-波 alternmagnet 的再定式。
- **二阶光电流被 inversion 屏蔽**：Sipe & Shkrebtii (Phys. Rev. B 61, 5337, 2000) 框架下 injection (Phys. Rev. B 61 等) 和 shift (Kraut & von Baltz, Phys. Rev. B 19, 1548, 1979; Young & Rappe, Phys. Rev. Lett. 109, 116601/236601, 2012) 在具有 inversion 的体系中消失，因此 alternmagnet 中 *二阶 bulk photovoltaic effect（BPE）= 0*。
- **三阶 jerk current**：Fregoso, Muniz, Sipe (Phys. Rev. Lett. 121, 176604, 2018; Phys. Rev. B 100, 064301, 2019) 引入 jerk current（*j* ∝ *E*³），Ezawa (Phys. Rev. B 112, 155308, 2025) 将高阶 BPE 与量子几何结合（之前仅限线偏振）。本文是 *首次把 jerk current 推广到椭圆偏振*。
- **量子几何形式**：Bleu/Solnyshkov/Malpuech (Phys. Rev. B 97, 195422, 2018)、Matsuura & Ryu (Phys. Rev. B 82, 245113, 2010)、Chen (J. Phys. Cond. Matt. 37, 025605, 2025)、Onishi & Fu (Phys. Rev. X 14, 011052, 2024) 等给出 *g_μν = ±(1/4) ∂_μ n · ∂_ν n* 和 *Ω_xy = ∓(1/2) n · (∂_{k_x} n × ∂_{k_y} n)* 的实空间/动量空间表达。

## 研究方法（Methods）
1. **四带紧束缚模型**：四方格子 Lieb-derived Hamiltonian（Eq. 1）：
   *H(k_x, k_y) = A (cos a k_x + cos a k_y) τ_0 σ_0 + B (cos a k_x − cos a k_y) τ_z σ_0 + t cos(a k_x/2) cos(a k_y/2) τ_x σ_0 + λ sin(a k_x/2) sin(a k_y/2) τ_y σ_z + C (cos a k_x − cos a k_y) τ_0 σ_z + (u + D (cos a k_x + cos a k_y)) τ_z σ_z*。参数意义：*A*、*B* = 各向同/异向次近邻跳跃；*t*、*λ* = 最近邻普通/自旋依赖跳跃；*C*、*D* = 次近邻普通/自旋依赖跳跃；*u* ∝ 自旋序。设定 *t* > 0，*λ* > 0。
2. **C₄zT 对称性显式实现**：C₄zT H(k_x, k_y) C₄zT⁻¹ = H(−k_y, k_x)，其中 *C₄zT = (i/√2)(σ_y − σ_x) τ_x K*。
3. **低能展开**：*σ_z* 是好量子数，将 *H* 分解为 *H_↑ ⊕ H_↓*。在 X 点 (*k'_x ≡ k_x − π/a*) 得到 *H^X_↑ = −4C + t a k'_x τ_x + λ a k_y τ_y − (4B − 2u) τ_z*，在 Y 点得到 *H^Y_↓ = −4C + t a k'_y τ_x − λ a k_x τ_y + (4B − 2u) τ_z*。两者互为 *C₄zT* 旋转下的对应物，自旋相反。
4. **量子几何显式公式**：以 *∆ ≡ 4B − 2u* 作为 Dirac 质量，得到：
   - *g^X_xx (k'_x, k_y) = a²t²((λ a k_y)² + ∆²) / [4 ((t a k'_x)² + (λ a k_y)² + ∆²)²]* (Eq. 6)
   - *g^X_yy (k'_x, k_y) = a²λ²((t a k'_x)² + ∆²) / [4 ((t a k'_x)² + (λ a k_y)² + ∆²)²]* (Eq. 7)
   - *Ω^X_xy (k'_x, k_y) = a²∆tλ / [2 ((t a k'_x)² + (λ a k_y)² + ∆²)^{3/2}]* (Eq. 8)
   - 在 Y 点：*g^Y_xx(k_x, k'_y) = g^X_xx(k'_x, k_y)*，*g^Y_yy(k_x, k'_y) = g^X_yy(k'_x, k_y)*，*Ω^Y_xy (k_x, k'_y) = Ω^X_xy (k'_x, k_y)*。
5. **拓扑指标**：*∫ Ω^X_xy dk / 2π = ∫ Ω^Y_xy dk / 2π = ∆/(2|∆|)* ⇒ 半量子化 Chern 数；两者相加给出 *∫ (Ω^X_xy + Ω^Y_xy) dk / 2π = ∆/|∆|*（Eq. 13）⇒ 体系在 *∆* > 0 时为 Chern 数 +1、在 *∆* < 0 时为 −1 的 Chern 绝缘体，伴随 quantum anomalous Hall。
6. **椭圆偏振光参数化**：*E(ω) = E(ω) (e_x cos ϑ + i e_y sin ϑ)*，*ϑ* 为椭圆度；*ϑ = π/4* 对应右圆，*ϑ = −π/4* 对应左圆。
7. **椭圆光二向色性公式（Eq. 16）**：*g(k;ϑ) ≡ g_xx(k) cos²ϑ + g_yy(k) sin²ϑ + Ω_xy(k) sinϑ cosϑ*；光导 *σ(ω; ϑ) = ℏ σ_H ∫ dk f(k) g(k; ϑ) δ[ε_+(k) − ε_−(k) − ℏω]*，其中 *σ_H ≡ e²/ℏ*。
8. **零温 + 化学势在 Dirac gap 内**：*µ = −4C*，故系统为绝缘体，光学边带 *ℏω = 2|∆|*。
9. **光电流推广公式（Eq. 29）**：*J^{x;x^ℓ}_{ω} = [(ℓ−1) / (iω₀ + 1/τ)^{ℓ−1}] × (2π e^{ℓ+1} / ℏ^ℓ V) ∫ dk g(k;ϑ) δ(ω_{+−} − ω) ∂^{ℓ−1} ω_{+−}/∂k^{ℓ−1}_x × E(ω) E(−ω) [E_x(0)]^{ℓ−2}*。对 *ℓ = 3* 得 jerk current：*J^{x;x^3}*。
10. **关键参数数值**：作图取 *t = 4*、*λ = 0.5*、*B = −1*、*u = −2.2*。
11. **椭圆度零点设计**：通过解 *g^Y(0; ϑ_Y) = 0* 得 *ϑ_Y = η arccos(t/√(λ² + t²))*，*η = ±1*，当 *λ∆ > 0* 取 *η = +1*，*λ∆ < 0* 取 *η = −1*。类似得 *ϑ_X = η arccos(λ/√(λ² + t²))*。

## 主要发现与核心结论

1. **低能理论 = 各向异性 Dirac 锥对**：
   - 自旋向上：*H^X_↑*（在 X 点），*k_x* 方向由 *t* 控制、*k_y* 方向由 *λ* 控制；
   - 自旋向下：*H^Y_↓*（在 Y 点），两个方向的角色互换；
   - C₄zT


## 合并自「2603.07490」

## 阅读笔记

### general-berry-mnps3-rashba-20260816

全文已读取完毕（arXiv HTML 全文 + 元数据 + 参考文献）。以下是结构化笔记。

---

# 论文精读笔记：arXiv:2603.07490

**标题**：Spin-selective elliptic optical dichroism and perfectly spin-polarized third-order nonlinear photocurrent in altermagnets（交变磁体中的自旋选择性椭圆光学二向色性与完全自旋极化的三阶非线性光电流）

**作者**：Motohiko Ezawa（东京大学应用物理系，独立作者）
**发表**：Phys. Rev. B **114**, L111201 (2026)（Letter）；arXiv v1 2026-03-08，v2 2026-06-16；6页3图
**分类**：cond-mat.mes-hall
**链接**：[arxiv.org/abs/2603.07490](https://arxiv.org/abs/2603.07490)

---

## 研究问题（Research Question）

论文的核心问题是：$d$ 波交变磁体（altermagnet）能否利用其自旋劈裂且各向异性的 Dirac 能带，实现**完全自旋选择性的光学激发**，并进一步产生**完全自旋极化的光电流**。作者具体追问三个层面：(1) 椭圆偏振光能否在该体系中实现“只激发自旋向上或只激发自旋向下电子”的完美椭圆二向色性（elliptic dichroism）；(2) 能否首次推导出**椭圆偏振光下高阶光电流**的解析公式，并用量子度规（quantum metric）与贝里曲率（Berry curvature）表达；(3) 由于交变磁体具有空间反演对称性，二阶光电流（注入流、位移流）被禁戒，那么三阶“急动电流”（jerk current，$j\propto E^3$）是否成为绝缘相中的**主导电学响应**。中心论点是：$d$ 波交变磁体的 X/Y 谷间完全相反的自旋极化 + 各向异性 Dirac 锥，为光致自旋电子学（photoinduced spintronics）提供了一个无需自旋轨道耦合即可产生 100% 自旋极化电流的理想平台。

## 研究背景（Background）

交变磁体是当前凝聚态物理的热点：它是共线反铁磁体但破坏时间反演对称性，可产生反常霍尔效应；$d$ 波交变磁体具有组合对称性 $\mathcal{C}_{4z}\mathcal{T}$（时间反演 × 四度旋转），强制能带自旋劈裂，且自旋在动量旋转 90° 后翻转，同时体系保持空间反演对称性——已有电场/温度梯度诱导自旋流的理论与实验工作（如 RuO₂ 倾斜自旋流，Nature Electronics 2022）。光学二向色性方面，圆二向色性最早在蜂窝格子（石墨烯、MoS₂、硅烯）的谷物理中提出，Ezawa 本人将其推广到各向异性 Dirac 锥的**椭圆二向色性**（拓扑晶体绝缘体表面，PRB 2014；p 波磁体，PRB 2025），并用“量子度规 + 贝里曲率”的组合 $g(\mathbf{k};\vartheta)=g_{xx}\cos^2\vartheta+g_{yy}\sin^2\vartheta+\Omega_{xy}\sin\vartheta\cos\vartheta$ 加以公式化。非线性光学响应方面，二阶体光伏效应（injection/shift current）已有系统研究（Sipe–Shkrebtti、Aversa–Sipe、Ahn–Nagaosa 等），而三阶 jerk current 由 Fregoso–Muniz–Sipe（PRL 2018）提出——但此前**所有高阶光电流理论都只针对线偏振光**。本文正是填补“椭圆偏振光下的高阶光电流理论”与“交变磁体自旋选择性光学”这两个空白的交汇点。

## 研究方法（Methods）

采用基于方格子的**四带紧束缚模型**（Eq. 1），由 Lieb 格子导出，含自旋 $\sigma$ 与子格 $\tau$ 两套 Pauli 矩阵、7 个参数（$A,B,C,D,t,\lambda,u$），满足 $\mathcal{C}_{4z}\mathcal{T}$ 对称性且经 DFT 验证（Fu et al., arXiv:2507.22474）。因 $\sigma_z$ 为好量子数，哈密顿量约化为 $H=H_\uparrow\oplus H_\downarrow$：自旋向上在 X 点、自旋向下在 Y 点各有一个**各向异性 Dirac 锥**（速度分量 $ta$ 与 $\lambda a$ 不同，质量 $\Delta=4B-2u$），两谷由 $\mathcal{C}_{4z}\mathcal{T}$ 联系。理论工具是两带体系的量子几何：$g_{\pm}^{\mu\nu}=\pm\frac{1}{4}(\partial_{k_\mu}\mathbf{n})\cdot(\partial_{k_\nu}\mathbf{n})$，$\Omega_{\pm}^{xy}=\mp\frac{1}{2}\mathbf{n}\cdot(\partial_{k_x}\mathbf{n}\times\partial_{k_y}\mathbf{n})$，由此解析写出 X/Y 点的度规与曲率（Eq. 6–11）。光学吸收用费米黄金规则在 Dirac 低能理论下解析积分（Eq. 15–18），核心是把吸收谱写成 $g(\mathbf{k};\vartheta)$（度规-曲率组合）在等能面上的积分。三阶光电流的推导（Supplemental Material II）将线偏振下的高阶注入流公式推广到椭圆偏振：$\ell$ 阶光电流正比于 $\partial^{\ell-1}\omega_{+-}/\partial k_x^{\ell-1}$ 与 $g(\mathbf{k};\vartheta)$ 的联合积分（Eq. 29），包含弛豫因子 $(i\omega_0+1/\tau)^{\ell-1}$。数值作图取参数 $t=4,\lambda=0.5,B=-1,u=-2.2$，零温、化学势置于 Dirac 隙内（$\mu=-4C$，绝缘体）。

## 主要发现与核心结论（Main Results）

**1. 完美自旋选择性的椭圆二向色性（核心发现）**：调节椭圆率使 $g^{\text{Y}}(\mathbf{0};\vartheta^{\text{Y}})=0$，即 $\vartheta^{\text{Y}}=\eta\arccos\frac{t}{\sqrt{\lambda^2+t^2}}$（$\eta=\mathrm{sgn}(\lambda\Delta)$，Eq. 20），可**完全关闭 Y 点（自旋向下）的激发**，此时只有 X 点（自旋向上）电子被激发，反之亦然（$\vartheta^{\text{X}}=\eta\arccos\frac{\lambda}{\sqrt{\lambda^2+t^2}}$）。这是“完美的”（perfect）二向色性——不是部分偏置而是 100% 选择，其根源在于自旋劈裂能带的自旋本征态完全对角化（无非对角自旋织构）。自旋极化比例还可通过连续调节 $\vartheta$ 在 0–100% 间调控（Fig. 2b, 3b）。

**2. 光学带边增强与谱形**：吸收在光学带边 $\hbar\omega=2|\Delta|$ 处取最大值 $\sigma^{\text{X}}\propto\frac{\pi(\lambda^2+\eta t^2)^2}{2t^2|\Delta|(\lambda^2+t^2)}$（Eq. 21），随 $\omega$ 增大单调按 $1/\omega$ 衰减（Eq. 22–23）；带边以下无吸收。

**3. 首个椭圆偏振光下的三阶光电流公式**：$J^{x;x^\ell}(\omega)\propto\int d\mathbf{k}\,g(\mathbf{k};\vartheta)\,\delta(\omega_{+-}-\omega)\,\frac{\partial^{\ell-1}\omega_{+-}}{\partial k_x^{\ell-1}}$（Eq. 29），是量子几何量（$g_{xx},g_{yy},\Omega_{xy}$）与能带高阶色散的乘积——把量子几何与非线性输运直接挂钩。取 $\ell=3$ 在带边得到 $J^{x;x^3}(\Delta;\vartheta^{\text{Y}})\propto\frac{\pi t(\lambda^2-t^2)^2}{2\Delta^2\lambda(\lambda^2+t^2)}$（Eq. 30）：**只有自旋向上的完全极化 jerk current**，谱形按 $1/\omega^2$ 衰减（Eq. 35–36）。

**4. 各向异性是必要条件**：当 $\lambda=t$（各向同性 Dirac 锥）时带边 jerk current 严格为零（Eq. 38）——带边增强效应是各向异性 Dirac 锥独有的指纹。

**5. 拓扑结构与主导响应地位**：单个 Dirac 锥带半量子化 Chern 数 $\Delta/2|\Delta|$，两谷求和得量子化 $\Delta/|\Delta|$（Eq. 13），体系为 Chern 绝缘体、支持量子反常霍尔效应。由于反演对称性禁戒全部二阶光电流，该自旋极化三阶电流是绝缘 $d$ 波交变磁体在“椭圆偏振光 + 静电场”同时施加时的**主导电学响应**（leading response）。

## 潜在研究方向（Future Directions）

**理论扩展**：作者明确预言 $g$ 波与 $i$ 波交变磁体（$\mathcal{C}_{8z}\mathcal{T}$、$\mathcal{C}_{12z}\mathcal{T}$ 对称性）中存在类似的自旋选择性光学现象，这是直接的后续课题。与 Rashba 体系/拓扑绝缘体表面的对比也值得注意：那里自旋织构非对角、完美自旋选择性原理上不可能——这提示“对角自旋本征态”是一类新的光学选择性资源，可在更广的磁对称性体系中搜索。

**实验验证路径**：论文建议用隧道磁电阻（TMR）、自旋极化 STM、点接触 Andreev 反射探测完全自旋极化电流（引 Jullière、Yuasa 等经典工作），但**尚未给出具体候选材料**——模型参数（$t,\lambda,\Delta$）与真实绝缘 $d$ 波交变磁体（如 LaMnO₃ 类钙钛矿、有机反铁磁体）的定量对接是开放问题。

**局限性**：(1) 全部结论基于理想两带 Dirac 低能理论和弛豫时间近似（$1/\tau$），未处理无序、温度、电子-空穴不对称及带间库仑相互作用；(2) “完美”选择性依赖 $\sigma_z$ 严格守恒，真实材料中残余自旋轨道耦合会否退化该选择性未讨论；(3) 三阶响应信号幅度小（$\propto E^3$），所需静电场与光场强度下的样品稳定性、以及与热载流子本底噪声的区分，文中未评估；(4) 仅考虑连续波/单频光场，超快（脉冲、强场） regime 下的瞬态行为——这与本课题（强场 HHG 探测磁序/量子几何）的交叉——完全未触及，是明显的研究空白。

---

**与本课题（general-berry-mnps3-rashba）的关联**：本文给出了“量子度规 + 贝里曲率 → 椭圆率可调的自旋选择性非线性光学响应”的完整解析范例，可直接迁移到强场情形——即用椭圆度调制的强场泵浦在 $d$ 波交变磁体中产生自旋选择性 HHG，或将 $g(\mathbf{k};\vartheta)$ 框架扩展到 HHG 光谱的反演问题中，实现量子几何张量的全光读出。

备注：本次通过 arXiv API + arXiv HTML 全文（v2）直接获取并精读了全文正文与全部 58 条参考文献，信息完整性优于摘要级 web_search。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：四带紧束缚模型（C₄zT 对称）+ 量子几何解析 + 椭圆光二向色性/三阶 jerk current 椭圆偏振推广

**原理**：方格子四带 TB 模型（A,B,C,D,t,λ,u 七参数，Lieb 衍生经 DFT 验证）显式实现 C₄zT 对称；σ_z 好量子数使 H 分解为 H↑⊕H↓——自旋上在 X 点、自旋下在 Y 点各一个各向异性 Dirac 锥（速度分量 ta 与 λa 互换，Dirac 质量 Δ = 4B−2u），两谷由 C₄zT 联系；两带量子几何解析公式给出 X/Y 点度规与曲率；椭圆光二向色性统一写成 g(k;ϑ) = g_xx cos²ϑ + g_yy sin²ϑ + Ω_xy sinϑcosϑ 在等能面的积分，调 ϑ 使 g^Y(0;ϑ_Y)=0 即完全关闭 Y 谷（自旋下）激发——100% 自旋选择；首次把高阶光电流公式推广到椭圆偏振（ℓ 阶 ∝ g(k;ϑ)·δ(ω₊₋−ω)·∂^{ℓ−1}ω₊₋/∂k_x^{ℓ−1} 联合积分），反演对称禁戒全部二阶光电流使三阶 jerk 为绝缘相主导响应。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 低能与作图参数 | Δ = 4B−2u；作图取 t = 4，λ = 0.5，B = −1，u = −2.2；µ = −4C（Dirac 隙内，绝缘体） | 研究方法 |
| 对称操作 | C₄zT = (i/√2)(σ_y−σ_x)τ_xK；C₄zT H(k_x,k_y) C₄zT⁻¹ = H(−k_y, k_x) | 研究方法 |
| 完美选择角 | ϑ_Y = η·arccos(t/√(λ²+t²))，ϑ_X = η·arccos(λ/√(λ²+t²))，η = sgn(λΔ) | 主要发现 1 |
| 光学带边 | ℏω = 2|Δ|（带边吸收最大，随 ω 按 1/ω 衰减；带边以下无吸收） | 主要发现 2 |
| 拓扑指标 | 单锥半量子化 Chern Δ/2|Δ|；两谷和 Δ/|Δ|（Chern 绝缘体 +1/−1，量子反常霍尔） | 研究方法 5/主要发现 5 |
| 带边 jerk current | J^{x;x³}(Δ;ϑ^Y) ∝ πt(λ²−t²)²/2Δ²λ(λ²+t²)（仅自旋向上完全极化；谱形 1/ω² 衰减；λ=t 各向同性时严格为零） | 主要发现 3/4 |

**适用边界**：理想两带 Dirac 低能理论 + 弛豫时间近似（无序、温度、电子-空穴不对称、带间库仑未含）；'完美'选择性依赖 σ_z 严格守恒（真实材料残余 SOC 的退化未讨论）；三阶响应 ∝E³ 幅度小（静电场+光场下样品稳定性、热载流子本底未评估）；仅连续波单频光场（超快脉冲/强场瞬态完全未触及）；未给出具体候选材料。
**代表作**：Ezawa, Spin-selective elliptic optical dichroism and perfectly spin-polarized third-order nonlinear photocurrent in altermagnets（arXiv:2603.07490, PRB 114, L111201）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2603.07490]]
- [[A]]
- [[B]]
- [[Berry 曲率]]
- [[MnPS3]]
- [[general-berry-mnps3-rashba-20260816]]
- [[quantum metric]]
- [[交变磁体]]
- [[反常霍尔效应]]
- [[拓扑绝缘体]]
- [[自旋劈裂]]
- [[量子几何]]
- [[量子几何张量]]
- [[量子度规]]
- [[非线性光学]]
<!-- /linsai-wikilinks -->
