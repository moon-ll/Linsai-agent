---
title: "2024-2404_14411-high-harmonic-tracking-of-ultrafast-electron-dynamics-across"
type: "papers"
created: "2026-08-29T05:44:01Z"
updated: "2026-11-15T15:09:23Z"
tags: []
related: ["2404.14411", "Berry 曲率", "Berry曲率", "TDSE", "general-quantum-geometry-inversion-20260726", "quantum metric", "三步模型", "光致相变", "固体HHG", "固体高次谐波", "强关联体系", "强场驱动", "强场高次谐波", "有限尺寸效应", "电荷密度波", "精确对角化", "量子几何", "量子几何张量", "量子度规", "非线性光学", "高次谐波产生", "高次谐波产生（HHG）"]
source_raw: "2024-2404.14411-high-harmonic-tracking-of-ultrafast-electron-dynamics-across.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-25T15:42:03Z"
merged_from: ["wiki/papers/2404.14411.md"]
---

# High Harmonic Tracking of Ultrafast Electron Dynamics across the Mott to Charge Density Wave Transition

## 林赛的理解

这篇工作展示了高次谐波产生（HHG）作为探测强关联体系量子相变的 spectroscopic tool 的强大能力。通过对扩展费米-哈伯德模型（EFHM）的数值模拟，作者证明 HHG 不仅能定位各类激子激发，还能通过亚周期分析揭示这些激发的结构信息。对于林赛的 PI 研究而言，这篇工作提供了两个重要启示：其一，HHG 量子相读取能力可以超越线性光学响应，探测到传统光谱无法分辨的激子串和 CDW Droplet；其二，亚周期分析可以作为解码多体激发"指纹"的新工具。这对于我们理解 HHG 阿秒实验中的信号起源、设计强场驱动方案、以及探索量子几何（quantum geometry）如何影响非线性光学响应，都具有直接的参考价值。

## 研究问题（Research Question）
论文要回答的核心问题是：**在强关联体系中，Mott 绝缘体到电荷密度波（CDW）的量子相变究竟是一级相变还是二级相变？HHG 光谱能否追踪这种相变过程中的超快电子动力学？**

具体而言，作者试图厘清以下子问题：
- (a) 不同激子效应（单激子、双激子、激子串）如何随最近邻相互作用强度 $V$ 变化，并塑造 HHG 响应；
- (b) 这些激子效应如何orchestrate从 Mott 绝缘体到 CDW 的一级相变；
- (c) 自旋液滴激发在 CDW 相的 HHG 光谱中扮演何种角色；
- (d) 亚周期分析能否揭示产生 HHG 信号的激发结构。

## 研究背景（Background）
### HHG 的发展脉络

高次谐波产生（HHG）最初在原子气体中被发现，是产生极紫外（XUV）阿秒脉冲的关键手段，奠定了阿秒物理的基础。近年来，HHG 的研究范围扩展到固体材料，形成了"固体 HHG"这一新方向。原子 HHG 的理论基础是半经典三步模型（tunneling-acceleration-recombination），该模型也被适配到固体——电子在价带和导带之间穿越，产生 intraband（低阶谐波）和 interband（高阶谐波）两类过程。

### 强关联体系的挑战

在强电子关联体系中，传统的单粒子图像不再适用。**一维扩展费米-哈伯德模型（EFHM）** 是描述这类系统的 minimal model，其哈密顿量为：

$$\hat{H} = -t_0 \sum_{j,\sigma}\left(\hat{c}_{j\sigma}^\dagger \hat{c}_{j+1\sigma} + \text{H.c.}\right) + \sum_j \left(U \hat{n}_{j\uparrow}\hat{n}_{j\downarrow} + V \hat{n}_j \hat{n}_{j+1}\right)$$

其中 $t_0$ 是跃迁积分，$U$ 是 on-site 库伦排斥，$V$ 是最近邻相互作用。当 $V$ 增大时，系统从 Mott 绝缘体转变为 CDW 相。

### EFHM 的相图

通过密度矩阵重整化群（DMRG）方法，已知 EFHM 在半填充时包含三个相：Mott 绝缘体（MI）、电荷密度波（CDW）和键有序波（BOW）相。在强相互作用极限（$U/t_0$ 大）下，当 $V > U/2$ 时，系统通过**一级相变**进入 CDW 相。在 MI 相中，基本激发是双占据态（doublon）和空穴（holon）的自由对；在 $V$ 增大后，这些对结合形成激子、双激子、激子串，最终在临界点附近形成 CDW Droplet。

### 线性光学的局限

理论上，这些不同激发应该在线性光学响应中有信号，但由于 CDW Droplet 与基态之间的跃迁矩阵元极小，线性光谱难以探测到它们——这正是 HHG 非线性光学响应的优势所在。

## 研究方法（Methods）
### 计算方法

1. **基态计算**：通过精确对角化（exact diagonalization）获得系统的基态。
2. **含时演化**：使用 Runge-Kutta 方法对含时薛定谔方程进行数值积分，初始状态为基态，受激光场驱动。
3. **激光场规范**：采用速度规范（velocity gauge），通过 Peierls 替换将光-物质耦合引入跃迁项：
   $$t_0 \hat{c}_{j\sigma}^\dagger \hat{c}_{j+1\sigma} \rightarrow t_0 e^{iaA(t)} \hat{c}_{j\sigma}^\dagger \hat{c}_{j+1\sigma}$$
   其中矢势 $A(t) = A_0 \sin^2\left(\frac{\omega_0 t}{2n_c}\right) \sin(\omega_0 t)$，具有 sine-square 包络。

### HHG 光谱计算

HHG 谱强度由电流算符时间导数的傅里叶变换给出：
$$P(\omega) = \left|\text{FT}\left[\langle \dot{\hat{J}}(t)\rangle\right]\right|^2$$

其中电流算符 $\hat{J}(t) = i a t_0 \sum_{j,\sigma}\left[e^{iaA(t)}\hat{c}_{j\sigma}^\dagger \hat{c}_{j+1\sigma} - e^{-iaA(t)}\hat{c}_{j+1\sigma}^\dagger \hat{c}_{j\sigma}\right]$。

### 亚周期分析

通过 Gabor 变换（短时傅里叶变换）进行亚周期分析：
$$P(\omega, \tau) = \left|\int_0^{2\pi n_c/\omega_0} e^{-(t-\tau)^2/\sigma^2} e^{-i\omega t} \langle \dot{\hat{J}}(t)\rangle dt\right|^2$$

滑动窗口宽度 $\sigma = 1/(2\omega_0)$。

### 线性光学响应

作为对比，还计算了线性光学响应（光学电导率）：
$$\sigma(\omega > 0) = \frac{1}{\omega} \text{Im}\left[\frac{1}{aL}\sum_n \frac{|\langle 0|\hat{J}_0|n\rangle|^2}{\hbar\omega - (E_n - E_0) + i\eta}\right]$$

### 系统尺寸

主要结果在系统尺寸 $N = 12$ 下获得，并进行了 $N = 8$ 和 $N = 12$ 以及无限体系（iTEPD 方法）的有限尺寸分析。

## 主要发现与核心结论

### HHG 光谱的五种不同 regime

论文在扩展费米-哈伯德模型中识别出五种具有显著差异的 HHG 光谱特征，对应于不同的物理 regime：

**① V = 0 的 Mott 绝缘体相（free charge carriers）**
- 参数：$U/t_0 = 20$，$V/t_0 \leq 2$
- 基态具有准长程反铁磁自旋密度波序
- HHG 光谱在电荷隙（Mott gap, $\sim U - O(t_0^2)$）处出现一个 dip，随后出现 plateau
- plateau 来源于单一 delocalized doublon-holon 对形成的能量连续区
- 该 plateau 在截止能量（由单对的最大动能决定）处结束

**② 存在激子的 Mott 相**
- 参数：$U/t_0 = 20$，$V/t_0 = 4$（$V < U/3$）
- 在 HHG 光谱中出现一个显著的新峰，对应激子能量 $E_{\text{exciton}}$（粉色虚线标记）
- 激子峰位于电荷隙以下，表明光谱权重从自由载流子部分转移到激子
- 这是 $V$ 感生的单 doublon-holon 对绑定所致

**③ 存在双激子（biexciton）的 regime**
- 参数：$U/t_0 = 30$，$V/t_0 = 12$（$V > U/3$）
- 在亚 Mott gap 能量处，HHG 光谱显著增强，对应多 doublon-holon 对组成的激发（如双激子）
- 粉色虚线标记激子峰（低能量），紫色虚线标记双激子峰（较高但仍低于 Mott gap）
- 通过调节 $V$ 参数，可以精确控制 HHG 峰在特定激子能量处的局域化

**④ CDW Droplet regime（临界区）**
- 参数：$(U - V)/t_0 < 2$（Mott 相临界点附近）
- HHG 光谱在 Mott gap 以下出现一个 distinctive plateau
- 该 plateau 起始于 $\sim U - V - 4t_0$（青色虚线标记），对应 CDW Droplet 连续谱的起始
- CDW Droplet 是不同尺寸激子串的叠加，是 CDW 序的 precursor

**⑤ CDW 相**
- 参数：$2V > U$
- "纯"CDW 相（$U = 0$）的 HHG 光谱比纯 Mott 绝缘体 ($V = 0$) 复杂得多
- CDW 相中出现额外的自旋隙（spin gap）$\Delta_s \equiv E_0(N_\uparrow+1, N_\downarrow-1) + E_0(N_\uparrow-1, N_\downarrow+1) - 2E_0(N_\uparrow, N_\downarrow)$
- 自旋隙对应于打破一个 doublon-hole 对产生两个 singlon 的激发，最低能量 Droplet（$n=1$）能量为 $\sim 3V - U$
- 电荷隙对应于两个 delocalized free singlon，能量为 $\sim 4V - U$
- HHG 光谱中还有来自两个 broken pair 形成的磁畴（SDW droplet, $n=2$）的峰，中心在 $\sim 5V - 2U$

### 亚周期分析的核心发现

亚周期分析揭示了不同类型激发的子周期动力学特征：

| Regime | HHG 特征 | 亚周期行为 |
|--------|----------|-----------|
| 自由载流子 | Mott gap 以上的 plateau | 多条相互干涉的轨迹，难以追踪单条振荡 |
| 激子/双激子 | 明显分离的峰 | 两条轨迹与 $E(t)$ 和 $-E(t)$ 形状一致；激子振幅在 $E_0$ 至 $2E_0$ 之间，双激子振幅约为激子的两倍（$2E(t)$ 至 $3E(t)$） |
| CDW Droplet | Mott gap 以下的 plateau | 多个轨迹的干涉，来自连续谱态 |
| CDW 相 | 自旋隙和电荷隙对应的结构 | 自旋隙振荡振幅在 $E_0$ 和 $2E_0$ 之间；电荷隙产生复杂的干涉-plateau 结构；$5V$ 附近峰振荡振幅在 $2E_0$ 至 $3E_0$ |

### 关键物理结论

1. **一级相变的证据**：HHG 光谱的变化（特别是 plateau 从"Mott gap 以上"到"Mott gap 以下"的迁移）追踪了系统中 CDW cluster 的形成过程，这是相变成核的动力学指纹，强烈支持一级相变。

2. **线性 vs 非线性光学响应的本质差异**：线性光学响应只能探测 free charge carriers 和 tightly bound excitons（连续谱和单峰）；对于 excitonic strings 和 CDW droplets，由于基态到高阶激发态的跃迁矩阵元极弱，线性响应几乎无法探测。非线性 HHG 响应通过强场激发访问更高阶的激发态，从而揭示这些复杂结构。

3. **亚周期分析作为解码工具**：振荡振幅与激发所带电荷或偶极矩成正比——$E_0$ 到 $2E_0$ 对应单激子，$2E_0$ 到 $3E_0$ 对应双激子或 SDW Droplet。这意味着亚周期分析可以**区分单激子、双激子、三激子乃至自旋液滴**，并判断 HHG 特征是来自连续谱还是分离峰。

4. **激子物理图像的完整演化路径**：随着 $V$ 增加，双 doublon-holon 对的演化路径为：
   - $V = 0$：自由 doublon-holon 对（金属性）
   - $V < U/3$：单激子（bound doublon-holon）
   - $V > U/3$：双激子、三激子等激子串
   - 临界点附近：CDW Droplet（各种尺寸激子串的叠加）
   - $2V > U$：CDW 基态

## 潜在研究方向（Future Directions）
### 局限性

1. **有限尺寸效应**：附加在光学隙以下的额外峰（$\simeq 50\omega_0$）是有限尺寸效应，在热力学极限下消失。iTEBD 计算表明该峰强度随系统尺寸增大而减弱，但在 $N = 12$ 的精确对角化结果中仍可见。

2. **维度限制**：目前仅研究了一维系统；更高维度（2D、3D）中的 HHG 响应和相变动力学尚不明确。

3. **激光参数选择**：选择了足够低的激光振幅以避免光致相变和绝缘态破坏；更强的场可能会打开新的物理，但也可能破坏原有的相变序列。

4. **实验可行性**：这是纯理论研究（基于精确对角化和 Runge-Kutta 演化），需要与真实材料（如 ET-F₂TCNQ、Sr₂CuO₃、链状铜酸盐）中的实验进行比较验证。

### 未解决的问题

1. **BOW 相的 HHG 特征**：相图中存在一个狭窄的 BOW 中间相，但本工作主要关注 MI 和 CDW 两个相，对 BOW 相的 HHG 响应未做详细分析。

2. **三维推广**：真实材料是三维的，如何将一维模型的结果推广到三维体系中的相变探测？

3. **与其他强关联现象的联系**：HHG 能否追踪其他量子相变（如超导转变、自旋液体转变等）？能否推广到 moiré 系统中的量子几何效应？

4. **量子 electrodynamics（QED）效应**：近年来 HHG 与 QED 效应的结合成为新方向，强场下真空涨落的反馈尚不清楚。

5. **激子串的微观结构**：尽管亚周期分析提供了部分信息，但激子串内部结构的详细信息仍需更精细的探针。

6. **相变级数的确定**：虽然结果强烈支持一级相变，但仍需更直接的数值证据（如利用几何张量或临界指数的精确计算）。

## 与林赛研究的关联

### HHG 量子相读取能力

这篇工作最直接相关的结论是：**HHG 可以作为强关联体系中量子相的"读取器"**。对于林赛的 HHG 和阿秒实验，这意味着我们可以利用 HHG 光谱来追踪目标材料（如强关联钙钛矿氧化物、moiré 异质结）中的量子相变，而不依赖于线性光谱。

### 激子物理与多体激发

论文详细分析了从单激子到双激子、激子串再到 CDW Droplet 的演化序列。这一"激子复杂性"（excitonic complexity）的 HHG 特征图谱，对于理解强场驱动下多体激发的动力学具有重要参考价值——特别是在林赛关注的 **HHG 阿秒实验**中，HHG 信号的多峰结构可能正对应于这些多体激发。

### 量子几何接口

论文的工作虽然没有直接提到量子几何（quantum geometry）或量子度规（quantum metric），但其分析框架隐含了一个关键思想：**非线性光学响应包含了线性响应无法访问的量子几何信息**。具体而言，激子态之间的跃迁矩阵元、激子束缚能的空间结构，都与量子几何有关。在林赛研究的 **moiré 系统**（Twisted bilayer graphene、moiré SSH 模型）中，量子几何是决定 HHG 响应的关键因素——这篇论文提供了一个可供参考的"理论benchmark"。

### 实验设计启示

- **激光参数**：选择了低激光振幅（$A_0 = 4$）、低频（$\omega_0 = 0.2$）和 5 个光学周期的驱动脉冲，以避免光致相变。这提示在设计 HHG 实验时，需要谨慎选择激光参数以确保观测到的是固有相变而非光致效应。
- **亚周期分析**：论文中 Gabor 变换的滑动窗口宽度 $\sigma = 1/(2\omega_0)$ 是一个合理的时间-频率折中，这意味着在设计阿秒 HHG 实验时，需要足够的时间分辨率来分辨单个光学周期内的电子动力学。

### 交变磁与量子相变

论文中涉及的 **first-order quantum phase transition** 动力学（CDW 成核与生长）与林赛提到的 **交变磁（alternating magnetic）** 研究存在概念接口：两者都涉及对称性破缺和量子相变。HHG 能否追踪磁性量子相变，是一个值得探索的方向。

## 来源

- 蒸馏自全文（deep-read）：arXiv:2404.14411v1 [cond-mat.str-el]，2024年4月22日
- 作者：Marlena Dziurawiec, Jessica O. de Almeida, Mohit Lal Bera, Marcin Płodzień, Maciej Lewenstein, Tobias Grass, Ravindra W. Chhajlany, Maciej M. Maśka, Utso Bhattacharya
- 研究机构：Wrocław University of Science and Technology, ICFO (Barcelona), Universidad de Valencia-CSIC, DIPC, ETH Zurich, Adam Mickiewicz University


## 合并自「2404.14411」

## 阅读笔记

### general-quantum-geometry-inversion-20260726

我已经获取了完整信息。现在整理为结构化笔记。

---

## 调研笔记：arXiv 2404.14411

来源：[arXiv:2404.14411](https://arxiv.org/abs/2404.14411)（2024-04-22提交，ICFO/ETH/Wrocław 等机构合作）

### 研究问题（Research Question）
论文核心问题是：在强关联扩展 Fermi-Hubbard 模型中，均匀 Mott 绝缘体（MI）在外延相互作用 V 增大时向电荷密度波（CDW）相的转变本质——是一阶相变还是经过键序波（BOW）中间相的二阶相变——这一长期争议能否借助强场高次谐波（HHG）这种"亚周期、非线性光学探针"来定性辨别。论文的中心论点是：HHG 谱中出现的激子、双激子、激子弦（excitonic strings）和电荷液滴（charge droplets）等复杂集体激发的特征信号，为一阶 Mott-CDW 相变提供了直接证据。

### 研究背景（Background）
1. 强关联材料中局域（Hubbard U）与非局域（近邻 V）相互作用并存，导致 MI、CDW 和窄区间 BOW 三相竞争；其相图已由 DMRG 方法刻画，但相变阶数与 BOW 中间相的存在性长期未达成共识。
2. 线性光学对强 V 区的多体准粒子响应较弱，难以分辨激子等束缚态；而固体高次谐波（HHG）已被建立为探测 Hubbard 型系统的有效手段，可揭示 Berry曲率、跃迁偶极矩、拓扑等线性光学难以触及的信息。
3. 此前工作已证实一维 Mott 绝缘体的第三谐波响应受激子主导，并建立了"Mott 绝缘体 HHG 的三步模型"，但多激子效应在强 V 区的主导地位及其与 CDW 相的关系尚未被系统化——本文正是填补这一空白。

### 研究方法（Methods）
1. **模型**：1D 半填充扩展 Fermi-Hubbard 模型（EFHM），参数空间覆盖 MI（V=0）、CDW（强 V）和 BOW 中间区；采用激光参数 A₀=4、ω₀=0.2、5 个光学周期（n_c=5）、系统尺寸 N=12 站点。
2. **HHG 计算**：通过求解含时薛定谔方程得到电流 j(t)，对 |j(ω)|² 取对数得到 HHG 谱；选用足够低的激光幅度以避免光致相变与绝缘态击穿。
3. **亚周期分析（Subcycle analysis）**：用宽度 σ=1/(2ω₀) 的滑动窗对 HHG 谱做时频分析，分辨 E(t) 和 −E(t) 振荡对应的相干辐射过程；并通过截断哈密顿量（仅允许 doublon-holon 对的产生/湮灭项）将动力学分离为受限与非受限两类贡献，类比 Mott 绝缘体的"三步模型"。
4. **有限尺寸效应检验**：对 N=10–14 等多个系统尺寸进行对比，确认 N=12 结果的收敛性；~50ω₀ 处的下方带隙峰被识别为有限尺寸伪迹，热力学极限下消失。

### 主要发现与核心结论（Main Results）
1. **MI 相（V=0）的 HHG**：呈现单一平台，截止能量由单对 doublon-hole 对的最大能量决定；与已有文献结果一致，作为对照基线。
2. **有限 V 下 MI 相的 HHG**：随 V 增大，Mott 平台下方出现能量低于 Mott 能隙的新峰，归因于 V 诱导束缚的 single doublon-holon 对（激子），其权重随 V 增大而增强。
3. **CDW 相的 HHG**：呈现多个平台与额外特征，excess energies约为 V − n(U−2V)（n 为 droplet 大小），表明 HHG 谱反映了 CDW 中束缚态的能量尺度；亚周期分析显示出与 MI 相完全不同的特征振荡模式，揭示了电荷液滴等复杂集体激发的亚周期动力学。
4. **核心结论**：从 MI 经 BOW 中间区到 CDW，HHG 谱中连续出现的激子→双激子→激子弦→电荷液滴等多体激发信号，构成了一阶相变（而非经过 BOW 二阶过渡）的直接光学指纹；这些准粒子部分逃离线性光学的检测范围，证实强场 HHG 是揭示强关联物质中准粒子本质与跟踪一阶量子相变期间电子动力学的强大工具。

### 潜在研究方向（Future Directions）
1. **更大系统 / 热力学极限**：当前 N=12 的精确计算虽精确但有限尺寸，~50ω₀ 处的下方峰是伪迹；需要发展针对大尺寸 EFHM 的数值方法（如 DMRG-time-evolution、TD-DMRG、t-DMRG），以确认 CDW 中多平台结构的稳健性。
2. **多激子动力学定量刻画**：激子串、电荷液滴的尺寸分布、生成/湮灭率及其对 V/U 比的标度关系仍需理论建模；论文中受限动力学 vs 全哈密顿量的对比只是定性分离，尚需建立可计算的"多激子 HHG 三步模型"。
3. **实验验证**：扩展到实际强关联材料的 HHG 实验测量（如 1T-TaS₂、TiSe₂ 等 CDW 系统），与理论预测做定量比对；需探索 V调控（掺杂、压力、应变）以扫描相图对应区域。
4. **与拓扑/Berry 曲率读出的接口**：HHG 已被用于探测拓扑序与 Berry 曲率，本文方法可与"瞬态拓扑测量"路线结合，探究 CDW 相变中拓扑相变的同步演化（如 π-Berry 跨越）。
5. **高阶谐波中的相干相位信息**：激子串与电荷液滴的时间-频率精细结构（Subcycle 分析）提示 HHG 谱的相位承载了不可忽略的关联信息；后续可发展"亚周期关联谱学"提取 doublon-holon 束缚能与寿命。

---

**参考引用（建议 BibTeX 风格）**：
Dziurawiec, M. et al. "High Harmonic Tracking of Ultrafast Electron Dynamics across the Mott to Charge Density Wave Phase Transition." arXiv:2404.14411 (2024).

**对课题 general-quantum-geometry-inversion-20260726 的价值**：本工作展示了"强场 HHG → 准粒子谱反演"的可行范式，将 Hubbard模型的激发层级（激子→液滴）映射为 HHG 谱的多个平台结构。这与课题关注的"量子几何张量反演"思路互补：它表明 HHG 不仅编码 Berry 曲率/量子度规等几何量，还编码强关联体系的束缚态结构——为后续"BSV/强场 HHG → 多参数反演"提供了强关联场景下的前向模型参考。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：关联体系绝缘体-金属跨越的 HHG 追踪（精确对角化基态 + RK4 TDSE + Gabor 亚周期分析）

**原理**：关联晶格模型精确对角化求基态，Runge-Kutta 积分含时薛定谔方程（速度规范，Peierls 替换 t₀→t₀e^{iaA(t)}，sin² 包络矢势）驱动跨越关联强度转变的电子动力学；HHG 谱 P(ω)=|FT[⟨ĵ(t)⟩]|² 由电流算符时间导数给出；Gabor 变换（短时傅里叶）P(ω,τ) 亚周期分析，追踪电子关联跨越 Mott 转变时 HHG 发射时序/谱形随 U/t 的演化。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 激光场 | A(t)=A₀sin²(ω₀t/2n_c)sin(ω₀t)（sine-square 包络） | §计算方法 |
| 谱提取 | P(ω)=|FT[⟨ĵ(t)⟩]|²；Gabor 窗 e^{−(t−τ)²/σ²} | §HHG 光谱计算 |

**适用边界**：精确对角化限制体系尺寸（小链/小格子）；速度规范 Peierls 引入的规范误差需收敛检验；Gabor 窗宽 σ 折中时间/频率分辨。
**代表作**：本文（arXiv:2404.14411）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2404.14411]]
- [[Berry 曲率]]
- [[Berry曲率]]
- [[TDSE]]
- [[general-quantum-geometry-inversion-20260726]]
- [[quantum metric]]
- [[三步模型]]
- [[光致相变]]
- [[固体HHG]]
- [[固体高次谐波]]
- [[强关联体系]]
- [[强场驱动]]
- [[强场高次谐波]]
- [[有限尺寸效应]]
- [[电荷密度波]]
- [[精确对角化]]
- [[量子几何]]
- [[量子几何张量]]
- [[量子度规]]
- [[非线性光学]]
- [[高次谐波产生]]
- [[高次谐波产生（HHG）]]
<!-- /linsai-wikilinks -->
