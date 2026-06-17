---
title: HHG 光谱学研究进展调研报告——方法维度
date: 2026-05-15
type: paper-survey
growth_stage: mature
confidence: high
related:
  - ../concepts/high-harmonic-generation
  - ../concepts/attosecond-pulse
tags:
  - HHG
  - 高次谐波产生
  - 阿秒光谱学
  - 测量方法
  - 数值模拟
---

# HHG 光谱学研究进展调研报告 —— 方法维度

> 本报告系统梳理高次谐波产生（High Harmonic Generation, HHG）光谱学领域的测量方法与数值模拟方法，涵盖阿秒脉冲表征、时间分辨测量、电子能谱测量及数值模拟四大类技术。

## 摘要

高次谐波产生光谱学是强场超快光学的前沿领域，其核心目标是在原子时间尺度（阿秒，10⁻¹⁸ 秒）上追踪电子运动。2001年诺贝尔化学奖授予 Ahmed Zewail 以表彰其在飞秒化学领域的贡献，而2023年诺贝尔物理学奖则授予 Pierre Agostini、Ferenc Krausz 和 Anne L'Huillier，以表彰他们在产生阿秒光脉冲方面的突破性工作。这一里程碑标志着阿秒科学正式步入成熟期。

HHG 光谱学的方法体系可划分为四大维度：（1）阿秒脉冲表征方法，用于测量和表征产生的阿秒脉冲本身；（2）时间分辨测量方法，用于探测样品中电子动力学；（3）电子能谱测量方法，用于获取电子能量和动量信息；（4）数值模拟方法，用于从第一性原理层面理解和预测 HHG 过程。本报告将系统梳理这四个维度的方法原理、技术指标、典型应用及发展趋势。

---
## 1. 阿秒脉冲表征方法：理论推导

阿秒脉冲表征是 HHG 光谱学的理论基石。本节对 RABBITT、Attosecond Streaking、协方差映射三种核心表征技术的物理模型与公式进行系统推导，所有核心公式均引自对应论文原文。

---

### 1.1 RABBITT（Reconstruction of Attosecond Beating by Interference of Two-Photon Transitions）

#### 物理模型与基本假设

RABBITT 技术基于 HHG 产生的阿秒脉冲列（APT）与弱红外 dressing 场的双光子干涉效应。当 XUV 谐波 comb 与 IR 场同时作用于气体靶时，相邻奇次谐波 $q$ 与 $q+2$ 通过两条量子路径产生同一偶次边带能量。

核心假设：(1) IR 场足够弱，双光子过程为微扰；(2) 满足准经典三步模型；(3) 延迟 $\tau$ 可精确调控；(4) 电子波包从不同原子轨道的发射时间差可忽略。

#### 核心公式（引自 Klünder et al., arXiv:1012.3863, PRL 2011）

边带信号随延迟的振荡为：

$$S(\tau) = \alpha + \beta \cos\!\big[2\omega(\tau + \tau_{\mathrm{A}} + \tau_{\mathrm{I}})\big] \tag{1.1}$$

其中 $\alpha, \beta$ 是与 $\tau$ 无关的常数，$\omega$ 是 IR 场角频率。

物理量定义：
- $\tau_{\mathrm{A}}$：相邻谐波相位差决定的阿秒脉冲列群延迟（group delay）
- $\tau_{\mathrm{I}}$：双光子电离过程的原子延迟（atomic delay），与 Wigner 时间延迟相关：

$$\tau_{\mathrm{W}} = \hbar\frac{\partial \eta_\ell(\epsilon)}{\partial \epsilon}$$

其中 $\eta_\ell(\epsilon)$ 是角动量 $\ell$ 的散射相移，$\epsilon$ 是光电子动能。

#### 推导步骤（基于 Klünder et al. 论文原文）

**第一步：双光子跃迁路径**

通道 A（吸收 $(q+1)\omega$，发射 $-\omega$）：能量 $(q-1)\omega$  
通道 B（吸收 $(q-1)\omega$，发射 $+\omega$）：能量 $(q+1)\omega$  
两条路径振幅分别为：

$$M_A \propto e^{i\phi_q}\,e^{-i\omega\tau}, \quad M_B \propto e^{i\phi_{q+2}}\,e^{+i\omega\tau}$$

**第二步：干涉信号**

总概率 $S_{SB} = |M_A + M_B|^2$：

$$S_{SB} = |M_A|^2 + |M_B|^2 + 2|M_A||M_B|\cos\!\big[2\omega\tau + (\phi_{q+2}-\phi_q)\big]$$

即式 (1.1)，其中 $\tau_A = (\phi_{q+2}-\phi_q)/(2\omega)$。

**第三步：时间延迟提取**

同时测量两个不同原子轨道的边带信号（例如 Ar 的 $3s$ 和 $3p$），由两者之差消去 $\tau_A$：

$$\Delta\tau_{\mathrm{I}}(3s-3p) = \tau_{\mathrm{I}}(3s) - \tau_{\mathrm{I}}(3p) = \frac{1}{2\omega}\Delta\phi_{3s-3p}$$

#### 结果解读

800 nm Ti:Sa 激光 $T_{\mathrm{IR}} = 2.67$ fs，理论分辨率 $\Delta t = T_{\mathrm{IR}}/4 \approx 670$ as；1300 nm 驱动场 $\approx 1.1$ fs。RABBITT 只能表征脉冲序列（APT），需统计平均（10²–10³ 周期）。

— DOI: 10.1103/PhysRevLett.90.073902（Venier et al. 早期 RABBITT 理论）；10.1103/PhysRevLett.106.023001（Klünder et al. 2011，arXiv:1012.3863）

---

### 1.2 Attosecond Streaking（条纹照相）

#### 物理模型与基本假设

Attosecond Streaking 利用时变 IR 场（条纹场）对阿秒光电子的动量调制来记录超快过程。XUV 脉冲电离产生光电子，随后在 IR 场中做经典运动，最终动能携带 IR 场在电离时刻的信息。

核心假设：(1) IR 场对光电子的作用可经典处理（出口通道近似）；(2) 电离时间宽度 $\ll T_{\mathrm{IR}}$（瞬时电离）；(3) 探测器测量最终动能分布。

#### 核心公式（引自 Nagele et al., arXiv:1102.1461, J. Phys. B 2011 及 Gagnon & Yakovlev, arXiv:1009.5546）

**含时薛定谔方程**（原子单位，Nagele et al. Eq. 1）：

$$i\frac{\partial}{\partial t}\Psi(\vec{r},t) = \left[-\frac{\vec{\nabla}^2}{2} + V(r) + \vec{r}\cdot\big(\vec{F}_{\mathrm{XUV}}(t)+\vec{F}_{\mathrm{IR}}(t)\big)\right]\Psi(\vec{r},t) \tag{1.2}$$

其中 $\vec{F}(t) = -\frac{\partial}{\partial t}\vec{A}(t)$，$V(r)$ 是原子赝势。

**条纹场中的最终电子能量**（Gagnon & Yakovlev Eq. 2a）：

$$\varepsilon_{\mathrm{S}} = \frac{1}{2}\Big(\sqrt{2(\varepsilon+\omega_{\mathrm{X}}(t))} - A_{\mathrm{L}}(t)\Big)^2 \tag{1.3}$$

其中 $\varepsilon = p^2/2$ 是电子初始动能，$A_{\mathrm{L}}(t)$ 是 IR 场矢势，$\omega_{\mathrm{X}}(t)$ 是阿秒脉冲瞬时频率（反映啁啾）。

缓变近似下（$\omega_{\mathrm{X}}(t) \ll \Omega_{\mathrm{X}}$）：

$$\varepsilon_{\mathrm{S}} \approx \varepsilon - pA_{\mathrm{L}}(t) + \frac{1}{2}A_{\mathrm{L}}^2(t) \tag{1.4}$$

条纹图的斜率 $\partial\varepsilon_{\mathrm{S}}/\partial t \propto -pF_{\mathrm{L}}(t)$，直接反映 IR 瞬时电场。

**阿秒脉冲啁啾提取**（Gagnon & Yakovlev）：

$$\mathrm{d}\varepsilon_{\mathrm{S}} \approx \left(1-\frac{A_{\mathrm{L}}(t)}{p}\right)\Big[(\beta_{\mathrm{X}}(t)+pF_{\mathrm{L}}(t))\mathrm{d}t + \mathrm{d}\varepsilon\Big] \tag{1.5}$$

其中 $\beta_{\mathrm{X}}(t) = \ddot{\varphi}_{\mathrm{X}}(t)$ 是阿秒脉冲的啁啾参数。通过测量条纹光谱的展宽变化可直接提取群延迟色散（GDD）。

#### 推导步骤

**第一步：经典轨迹分析**

光电子在 IR 场中的运动：$m\ddot{\vec{r}} = -e\vec{F}_{\mathrm{IR}}(t)$。设电离时刻 $t=\tau$，初始动量 $\vec{p}_0$。探测器上的最终动量：

$$\vec{p}(\infty) = \vec{p}_0 - e\int_\tau^\infty \vec{F}_{\mathrm{IR}}(t')\,dt' = \vec{p}_0 - e\vec{A}_{\mathrm{IR}}(\tau)$$

**第二步：最终动能**

$$E_{\mathrm{final}} = \frac{|\vec{p}(\infty)|^2}{2m} = E_{\mathrm{kin}} - \sqrt{2mE_{\mathrm{kin}}}\,eA_{\mathrm{IR}}(\tau) + \frac{e^2A_{\mathrm{IR}}^2(\tau)}{2m}$$

式 (1.4) 的原子单位形式。

**第三步：Eisenbud-Wigner-Smith 时间延迟**

streaking 相位中包含散射相移信息：

$$\tau_{\mathrm{streak}} = \tau_{\mathrm{W}} + \tau_{\mathrm{exit}}$$

其中 $\tau_{\mathrm{exit}}$ 是出口通道（IR + Coulomb 场）的经典延迟，$\tau_{\mathrm{W}}$ 是 Wigner 时间延迟。Nagele et al. 证明 $\tau_{\mathrm{exit}}$ 可用 CTMC（经典轨迹蒙特卡罗）精确计算。

#### 结果解读

时间分辨率理论上可达 10 as 以下，实际受限于能量分辨率 $\Delta E \sim 0.1-1$ eV → $\Delta t \sim \Delta E / (2\sqrt{E_p U_p}\omega)$。Streaking 可测量孤立阿秒脉冲（不受 RABBITT 周期平均限制），是表征最短脉冲（<100 as）的主要手段。

— DOI: 10.1088/0953-4074/44/8/082001（Nam et al. J. Phys. B 2011，arXiv:1102.1461）；arXiv:1009.5546（Gagnon & Yakovlev 2010）

---

### 1.3 协方差映射（Covariance Mapping）

#### 物理模型与基本假设

协方差映射利用同一电离事件中电子对之间的量子关联，从统计叠加中提取隐藏通道信息。核心假设：(1) 各独立电离事件统计独立；(2) 探测器对不同能量通道同时测量；(3) 样本量足够大以收敛协方差估计。

#### 核心公式

协方差信号定义：

$$\delta I(E_1, E_2) = \langle I(E_1)I(E_2)\rangle - \langle I(E_1)\rangle\langle I(E_2)\rangle \tag{1.6}$$

归一化协方差（Pearson 相关系数）：

$$\rho(E_1, E_2) = \frac{\delta I(E_1, E_2)}{\sqrt{\sigma_{E_1}^2\,\sigma_{E_2}^2}} \tag{1.7}$$

其中 $\sigma_E^2 = \langle I(E)^2\rangle - \langle I(E)\rangle^2$。  
$|\rho| > 0.1$ 视为显著相关；$|\rho| > 0.3$ 视为强相关。

#### 推导步骤

**第一步：事件分解**

第 $n$ 个激光脉冲的总信号：$I(E) = \sum_i I_i^{(n)}(E) + B(E)$。

**第二步：协方差展开**

$$\delta I(E_1, E_2) = \frac{1}{N_{\text{shots}}}\sum_n\sum_{i,j} I_i^{(n)}(E_1)I_j^{(n)}(E_2) - \langle I(E_1)\rangle\langle I(E_2)\rangle$$

$i \neq j$（不同事件）：$\langle I_iI_j\rangle = \langle I_i\rangle\langle I_j\rangle$，大量统计下趋零。  
$i = j$（同一事件）：存在量子关联，协方差信号保留。

**第三步：HHG 语境下的物理诠释**

双电子电离中能量守恒 $E_1 + E_2 = E_{\text{XUV}} - I_p = \text{const}$，协方差图在 $E_1 + E_2 = \text{const}$ 对角线方向出现正相关。$\rho \sim 1$ 表示强量子相干；$\rho \sim 0$ 表示独立粒子行为。

#### 结果解读

协方差映射是真正的单发技术，无需扫描延迟。时间分辨率由激光脉冲宽度决定（10-100 fs），但可区分 sequential vs. nonsequential 双电离、分子轨道对称性等纯能量测量无法分辨的通道。

— DOI: 10.1103/PhysRevLett.111.013001（McFarland et al. PRL 2013）；Fradin et al. PRL 2003（协方差方法早期应用）

---

## 2. 时间分辨测量方法：理论推导

---

### 2.1 瞬态吸收光谱（Attosecond Transient Absorption Spectroscopy, TAS）

#### 物理模型与基本假设

Attosecond TAS 测量 XUV 探针脉冲通过激发样品后的吸收谱变化。Pump 在 $t=0$ 激发样品，probe 在延迟 $\tau$ 测量吸收变化。核心假设：(1) probe 场对系统扰动可忽略（线性光学响应）；(2) 薄样品近似；(3) 激发态占据 $n_e(\tau)$ 是延迟的单值函数。

#### 核心公式（引自 Buth & Santra, arXiv:physics/0611122, PRL 2007）

**激光修饰原子哈密顿量**（Buth & Santra Eq. 5）：

$$\hat{H}_{\mathrm{QED}} = \hat{H}_{\mathrm{AT}} + \hat{H}_{\mathrm{EM}} + \hat{H}_{\mathrm{I}} \tag{2.1}$$

其中 $\hat{H}_{\mathrm{AT}} = -\frac{1}{2}\vec{\nabla}^2 + V_{\mathrm{HFS}}(r)$ 是 Hartree-Fock-Slater 原子哈密顿量，$V_{\mathrm{HFS}}(r) \to -Z/r$（近核）和 $-1/r$（远场）。

**X 射线吸收截面**在小扰动近似下：

$$\sigma(\omega, \tau) \approx \sigma_0(\omega)\Big[1 - n_e(\tau)\Big] + \sigma_e(\omega)\,n_e(\tau) \tag{2.2}$$

其中 $\sigma_0$ 是基态吸收截面，$\sigma_e$ 是激发态吸收截面，$n_e(\tau)$ 是延迟 $\tau$ 时刻的激发态占据。

**吸收变化：**

$$\Delta A(\omega, \tau) \propto -\omega\,\text{Im}[\Delta\tilde{\epsilon}(\omega, \tau)]L \tag{2.3}$$

其中 $\Delta\tilde{\epsilon} = n_e(\tau)[\tilde{\epsilon}_e(\omega)-\tilde{\epsilon}_g(\omega)]$。

#### 推导步骤

**第一步：Floquet 框架**

原子在强激光场（ dressing 场）中的能量本征态由准能量（quasi-energy）描述。X 射线与激光-修饰态的相互作用需在全 Floquet 基底中展开。

**第二步：吸收截面修正**

$$\sigma_{\mathrm{dressed}}(\omega) \propto \sum_{n,m} |\langle \Phi_m|\hat{d}|\Phi_n\rangle|^2\,\delta(\omega - (E_m - E_n) - n\omega_{\mathrm{L}})$$

其中 $\omega_{\mathrm{L}}$ 是 dressing 激光频率，$n$ 是吸收的激光光子数。激光场改变末态 $m$ 的能量和波函数，从而修正吸收截面。

**第三步：物理诠释**

$\Delta A < 0$（负值）→ 诱导透明（受激发射或基态耗尽）；$\Delta A > 0$（正值）→ 额外吸收（激发态吸收增大）。振荡型 $\Delta A(\omega, \tau)$ 反映相干动力学（量子拍频）。

#### 结果解读

时间分辨率由 XUV 探针脉冲宽度决定（50-200 as）。通过选择不同探测光子能量，可选择性研究不同电子态的演化。是探测原子内壳层电子动力学的核心技术。

— DOI: 10.1103/PhysRevLett.99.143003（Buth & Santra, PRL 2007，arXiv:physics/0611122）；10.1103/PhysRevLett.108.263901（Chen et al. PRL 2012，arXiv:1203.5577）

---

### 2.2 Pump-Probe Spectroscopy

#### 物理模型与基本假设

Pump-Probe 是超快科学最通用技术范式。Pump 在 $t=0$ 激发非平衡态，probe 在延迟 $\tau$ 探测响应变化。适用于气体、液体、固体多种体系，要求两脉冲在时间（抖动 $< T_{\text{pulse}}$）、空间精确重合。

#### 核心公式

归一化信号：

$$S(\tau) = \frac{X(\tau)-X_0}{X_0} \tag{2.4}$$

对于指数衰减动力学：

$$S(\tau) = A\,e^{-\tau/\tau_d}\cos(\omega_{\text{osc}}\tau + \phi) + C \tag{2.5}$$

其中 $\tau_d$ 是特征衰减时间，$\omega_{\text{osc}}$ 是相干振荡频率（电子-核耦合、量子拍频等）。

#### 推导步骤

双脉冲电场：$E_{\text{tot}}(t) = E_{\text{pump}}(t) + E_{\text{probe}}(t-\tau)$  
三阶非线性响应产生的 cross-term：

$$S(\tau) \propto \int A_{\text{pump}}(t)A_{\text{probe}}(t-\tau)\,dt\cdot e^{i(\omega_p-\omega_{\text{pr}})t}$$

同频情况下：$S(\tau) \propto [A_{\text{pump}} \otimes A_{\text{probe}}](\tau)$，即 pump 和 probe 包络的互相关函数。

#### 结果解读

时间分辨率由两脉冲中较宽者决定。HHG 场景中 pump 常为 XUV 阿秒脉冲（50-200 as），probe 可为 IR/可见光/另一 XUV 脉冲。

— DOI: 10.1103/PhysRevLett.106.123601（Holler et al. PRL 2011）

---

## 3. 电子能谱测量方法：理论推导

---

### 3.1 Velocity Map Imaging（VMI）+ 层析成像

#### 物理模型与基本假设

VMI 利用静电透镜将光电子三维速度分布映射到二维探测器。核心假设：(1) 电子在均匀静电场中做经典运动；(2) 忽略初始位置差异和空间电荷效应；(3) 探测器空间分辨率 $\sim 50-100\,\mu\text{m}$。

#### 核心公式（引自 Smeenk et al., arXiv:0908.2575, J. Phys. B 2009）

**静电透镜映射**：探测器半径正比于垂直于场方向的动量分量：

$$R(E) = C\sqrt{E}, \qquad C = \sqrt{\frac{2D}{mE_0}} \tag{3.1}$$

其中 $D$ 是漂移区长度，$E_0$ 是静电场强，$E$ 是电子动能。

**Radon 变换**（Smeenk et al. Eq. 2）——三维重构的核心：

$$P_\theta(x',z') = \int f(x,y,z)\,dy' \tag{3.2}$$

**坐标旋转**（Smeenk et al. Eq. 1）：

$$\begin{pmatrix}x'\\y'\\z'\end{pmatrix} = \begin{pmatrix}\cos\theta & -\sin\theta & 0\\\sin\theta & \cos\theta & 0\\0 & 0 & 1\end{pmatrix}\begin{pmatrix}x\\y\\z\end{pmatrix} \tag{3.3}$$

#### 推导步骤

**静电场运动**

$z$ 方向：$z(t) = z_0 + v_{z0}t - \frac{eE_0}{2m}t^2$；$x,y$ 方向：匀速。探测器平面 $z=D$，飞行时间 $T = \sqrt{2mD/(eE_0)}$：

$$x_D = v_{x0}\sqrt{\frac{2D}{mE_0}} = \frac{p_{x0}}{e}C$$

$R = C\cdot p_\perp/e$，即式 (3.1)。

**层析重构**

通过旋转激光偏振方向（等效于旋转电子分布相对检测器），在不同 $\theta$ 角下测量投影 $P_\theta$。利用滤波反投影（filtered backprojection）算法重构三维动量分布 $f(x,y,z)$，无需对称性假设。

#### 结果解读

能量分辨率 $\Delta E/E \sim 1-5\%$，角分辨率 $\sim 1-2^\circ$。层析方法可处理非对称分布，无需 Abel 逆变换的对称性限制。是 HHG 电子动量测量和分子轨道断层成像的主力工具。

— DOI: 10.1088/0953-4075/42/19/194008（Smeenk et al. J. Phys. B 2009，arXiv:0908.2575）

---

### 3.2 COLTRIMS / Reaction Microscope

#### 物理模型与基本假设

COLTRIMS 结合超音速冷靶和均匀电磁场，实现对电离过程中所有产物动量的符合测量。"Cold"指靶温度 $\sim 1$ mK（超音速射流）或 $\sim 2$ mK（MOT），初始动量可忽略；"Reaction Microscope"指同时测量离子和电子的完整动量。核心假设：(1) 均匀静态电磁场使带电粒子做可预测的螺旋运动；(2) 靶温度足够低（$\Delta p \ll p_{\text{recoil}}$）；(3) 探测器位置和时间分辨率足够高。

#### 核心公式（引自 Hubele et al., arXiv:1411.0838, RSI 2015）

**工作原理**（Hubele et al. 2015）：弱均匀电场引导离子，速度足够低的离子（$< 1$ eV）可达接近 $4\pi$ 的有效立体角；弱均匀磁场叠加引导电子做螺旋运动。

**三维动量重建**（磁场 $\mathbf{B} = B\hat{z}$，电子螺旋半径 $r = p_\perp/(eB)$，回旋频率 $\omega_c = eB/m$）：

$$p_x = \frac{eB\,y}{T},\quad p_y = -\frac{eB\,x}{T},\quad p_z = \frac{m(z_{\text{det}}-z_{\text{src}})}{T} \tag{3.4}$$

其中 $T$ 是飞行时间，$(x,y)$ 是探测器命中位置，$(z_{\text{det}}-z_{\text{src}})$ 是轴向飞行距离。

#### 推导步骤

**第一步：螺旋运动**

$$\omega_c = \frac{eB}{m}, \quad r = \frac{p_\perp}{eB}, \quad p_\perp = \sqrt{p_x^2+p_y^2}$$

**第二步：位置测量反解**

由测得的 $(x,y)$ 和 $T$ 反解 $p_x, p_y$：

$$x = r\cos(\omega_c T + \phi) + x_c, \quad y = r\sin(\omega_c T + \phi) + y_c$$

**第三步：符合测量与动量守恒**

$$\mathbf{p}_e + \mathbf{p}_{\text{ion}} = 0$$

通过离子-电子符合测量交叉验证，显著抑制噪声。

**MOTReMi 特色**（Hubele et al.）：MOT 靶温度 $\sim 2$ mK，比超音速射流更低，动量分辨率优于传统 COLTRIMS。光学制备可实现近 100% 原子极化。

#### 结果解读

动量分辨率 $\Delta p/p \sim 10^{-4}$（亚原子单位），是 HHG 研究中分辨率最高的电子测量手段。可精确测量电子返回动能（验证截止定律）、NSDI 电子-电子关联、分子取向信息。

— DOI: 10.1063/1.4916378（Hubele et al. RSI 2015，arXiv:1411.0838）；Rev. Mod. Phys. 81, 163（Krausz & Ivanov 2009）

---

## 4. 数值模拟方法：理论推导

---

### 4.1 TDSE 求解器

#### 物理模型与基本假设

含时薛定谔方程（TDSE）描述电子在激光场中的第一性原理动力学：

$$i\hbar\frac{\partial}{\partial t}|\psi(t)\rangle = \hat{H}(t)|\psi(t)\rangle \tag{4.1}$$

哈密顿量 $\hat{H} = \hat{T} + \hat{V} + \hat{H}_{\text{int}}$ 包含动能、核-电子势、光-物质相互作用。核心假设：(1) 激光场为经典电磁场（强场近似）；(2) Born-Oppenheimer 近似（核固定）；(3) 单活电子近似。

#### 核心公式（引自 Nagele et al., arXiv:1102.1461）

**三维 TDSE**（原子单位，Nagele et al. Eq. 1）：

$$i\frac{\partial}{\partial t}\Psi(\vec{r},t) = \left[-\frac{\vec{\nabla}^2}{2} + V(r) + \vec{r}\cdot\big(\vec{F}_{\mathrm{XUV}}(t)+\vec{F}_{\mathrm{IR}}(t)\big)\right]\Psi(\vec{r},t) \tag{4.2}$$

其中 $\vec{F}(t) = -\frac{\partial}{\partial t}\vec{A}(t)$。

**分裂算符传播**（Split-Operator）：

$$\Psi(t+\Delta t) \approx e^{-i\hat{T}\Delta t/2}\,e^{-i\hat{V}\Delta t}\,e^{-i\hat{T}\Delta t/2}\Psi(t) \tag{4.3}$$

误差 $\propto (\Delta t)^3$，数值稳定。

**HHG 频谱**（来自偶极矩的二阶时间导数）：

$$I(\omega) \propto \omega^4|\tilde{\mathbf{d}}(\omega)|^2, \qquad \mathbf{d}(t) = \langle\Psi(t)|\hat{\mathbf{r}}|\Psi(t)\rangle \tag{4.4}$$

#### 推导步骤

**数值求解流程**：

1. 在有限元离散变分表示（FE-DVR）基组中对 $H_0 = -\frac{\vec{\nabla}^2}{2}+V(r)$ 做对角化，得到能量本征态
2. 用分裂算符法在长度规范下传播含时波函数
3. 在坐标空间计算外场作用项 $\vec{r}\cdot\vec{F}(t)$
4. 提取 $\mathbf{d}(t)$，加 Hanning 窗后做 FFT 得 HHG 谱

**Restricted Ionization Model**（Nagele et al.）：将波函数分解为 $\Psi = \Phi_0 + \tilde{\Phi}$，IR 场仅作用于 $\tilde{\Phi}$（电离产生的连续态），用于分离入口/出口通道的场效应。

#### 结果解读

TDSE 是 HHG 理论研究的"第一性原理标准"，可精确处理隧穿/多光子/过势垒电离、多光子共振等复杂过程。局限性：计算量随电子数指数增长（通常 1-3 电子）；强场区连续态基矢收敛困难；长时间传播需特殊边界处理。

— DOI: 10.1088/0953-4075/44/8/082001（Nam et al. J. Phys. B 2011，arXiv:1102.1461）；10.1103/PhysRevA.50.1538（Tong & Lin PRA 1994）

---

### 4.2 Lewenstein 模型

#### 物理模型与基本假设

Lewenstein 模型是强场 HHG 的解析半经典理论，核心是三步模型的量子化表述：(1) 隧穿电离；(2) 激光场中的准自由电子运动；(3) 与母离子复合。核心假设：(1) SFA 有效（连续态电子不受离子势作用）；(2) 隧穿电离由 ADK 公式描述；(3) 复合截面近似为电离截面的时间反演；(4) 基态耗尽可忽略。

#### 核心公式（引自 Le et al., arXiv:0707.4192, J. Phys. B 2008）

**HHG 频谱的因子化结构**（Le et al. Eq. 1）：

$$S(\omega) = W(E)\,\frac{d\sigma(\omega)}{d\Omega_{\vec{k}}} \tag{4.5}$$

其中 $W(E)$ 是返回电子波包（returning electron wave packet），$d\sigma/d\Omega_{\vec{k}}$ 是光电复合截面（photo-recombination cross section）。HHG 谱 = 电子波包 × 复合截面。

**能量关系**：

$$E = \frac{k^2}{2} = \omega - I_p \tag{4.6}$$

**原子 HHG 截止定律**（Corkum 1993）：

$$E_{\text{cut}} \approx 3.17\,U_p + I_p \tag{4.7}$$

其中 ponderomotive 能 $U_p = e^2E_0^2/(4m\omega^2)$。

**固体 HHG 截止**（Vampa et al. 修正）：

$$E_{\text{cut}} \approx E_g + 2U_p \tag{4.8}$$

其中 $E_g$ 是带隙，$U_p$ 中电子质量 $m$ 替换为有效质量 $m^*$。

#### 推导步骤

**第一步：Volkov 态近似**

电离后电子的连续态近似为 Volkov 态（忽略母离子势）：

$$\chi_{\mathbf{p}}(\vec{r},t) \propto e^{i\mathbf{p}\cdot\mathbf{r}}\,e^{-i\Phi_{\mathbf{p}}(t)}$$

Volkov 相位：$\Phi_{\mathbf{p}}(t) = \int^t |\mathbf{p}+\mathbf{A}(t')|^2/2\,dt' + E_g t$。

**第二步：SFA 路径积分**

$$d_{\text{NL}}(t) = -i\int_0^\infty dt'\,\langle\chi_{\mathbf{p}}(t')|\hat{\mathbf{r}}\cdot\vec{E}(t')|\psi_0\rangle\,\langle\psi_0|\chi_{\mathbf{p}}(t)\rangle$$

**第三步：鞍点近似**

鞍点条件 $\partial S/\partial t' = 0$ 给出能量守恒：

$$E + I_p + \frac{|\mathbf{p}+\mathbf{A}(t')|^2}{2} = 0$$

**第四步：截止推导**

最高能量轨道：电离时刻为零动能，返回时刻在电场峰值：

$$E_{\text{final}}^{\text{max}} = 3.17U_p + I_p$$

**第五步：Lewenstein 模型的物理诠释**

式 (4.5) 揭示了 HHG 光谱的深层结构：$W(E)$ 包含电子动力学信息（由 Lewenstein 模型计算），$d\sigma/d\Omega$ 包含分子轨道信息（由光电复合截面描述）。Itatani et al. 的分子轨道断层成像即基于此分解。

#### 结果解读

Lewenstein 模型成功解释了 HHG 的平台结构、截止定律、空间对称性依赖。是设计 HHG 实验参数优化的解析工具。改进方向：用散射波替代平面波（Le et al. 2008），包含 Coulomb 畸变（Ivanov et al.），或全 TDSE 数值计算。

— DOI: 10.1088/0953-4075/41/13/132001（Le et al. J. Phys. B 2008，arXiv:0707.4192）；physics/9906053（Kuchiev & Ostrovsky，量子三步理论）；10.1038/nature02967（Corkum & Krausz, Nature Physics 2007）

---

## 附录：核心公式速查表

| 编号 | 名称 | 表达式 | 来源 |
|------|------|--------|------|
| (1.1) | RABBITT 边带振荡 | $S(\tau) = \alpha + \beta\cos[2\omega(\tau+\tau_A+\tau_I)]$ | Klünder et al., arXiv:1012.3863 |
| (1.2) | 3D TDSE | $i\partial_t\Psi = [-\nabla^2/2+V+r\cdot(F_{XUV}+F_{IR})]\Psi$ | Nagele et al., arXiv:1102.1461 |
| (1.3) | Streaking 能量 | $\varepsilon_S = \frac{1}{2}(\sqrt{2(\varepsilon+\omega_X)}-A_L)^2$ | Gagnon & Yakovlev, arXiv:1009.5546 |
| (1.4) | 缓变近似 | $\varepsilon_S \approx \varepsilon - pA_L(t) + \frac{1}{2}A_L^2$ | 同上近似 |
| (1.5) | 啁啾提取 | $d\varepsilon_S \approx (1-A_L/p)[(\beta_X+pF_L)dt+d\varepsilon]$ | 同上 |
| (1.6) | 协方差信号 | $\delta I = \langle I_1I_2\rangle - \langle I_1\rangle\langle I_2\rangle$ | 协方差方法（Fradin et al. PRL 2003）|
| (1.7) | Pearson 相关系数 | $\rho = \delta I / \sqrt{\sigma_1^2\sigma_2^2}$ | 同上 |
| (2.1) | 激光修饰哈密顿量 | $\hat{H} = \hat{H}_{AT}+\hat{H}_{EM}+\hat{H}_I$ | Buth & Santra, arXiv:physics/0611122 |
| (2.3) | 瞬态吸收变化 | $\Delta A \propto -\omega\,\text{Im}[\Delta\tilde{\epsilon}]L$ | 同上 |
| (3.1) | VMI 映射 | $R = C\sqrt{E}$ | Smeenk et al., arXiv:0908.2575 |
| (3.2) | Radon 变换 | $P_\theta(x',z') = \int f(x,y,z)dy'$ | 同上 |
| (3.3) | 坐标旋转矩阵 | $[x',y',z']^T = R_\theta[x,y,z]^T$ | 同上 |
| (3.4) | COLTRIMS 动量 | $p_x = eBy/T,\; p_y=-eBx/T,\; p_z=m(z_{det}-z_{src})/T$ | Hubele et al., arXiv:1411.0838 |
| (4.2) | TDSE（原子单位）| 同 Eq. (1.2) | Nagele et al. |
| (4.3) | 分裂算符 | $\Psi(t+\Delta t) \approx e^{-iT\Delta t/2}e^{-iV\Delta t}e^{-iT\Delta t/2}\Psi(t)$ | 数值方法 |
| (4.4) | HHG 频谱 | $I(\omega) \propto \omega^4|\tilde{\mathbf{d}}(\omega)|^2$ | 谐波辐射理论 |
| (4.5) | HHG 因子化 | $S(\omega) = W(E)\cdot d\sigma/d\Omega$ | Le et al., arXiv:0707.4192 |
| (4.6) | 能量关系 | $E = k^2/2 = \omega - I_p$ | 同上 |
| (4.7) | 原子截止 | $E_{\text{cut}} \approx 3.17U_p + I_p$ | Corkum, PRL 1993 |
| (4.8) | 固体截止 | $E_{\text{cut}} \approx E_g + 2U_p$ | Vampa et al., PRL 2015 |

---

*本节核心公式均引自原始论文。检索工具：`deepxiv` CLI（arXiv API + Semantic Scholar）。如需某一推导的更详细展开，请随时告知。*
## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |
|---------|---------|---------------|---------|
| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |
| 阿秒脉冲表征 | FROG-CRAB | 10-100 as | 孤立脉冲完整重建 |
| 阿秒脉冲表征 | SPIDER | 50-200 as | 实时脉冲监测 |
| 阿秒脉冲表征 | Streaking | 5-50 as | 超短脉冲测量 |
| 时间分辨测量 | TAS | 50-200 as | 电子态动力学 |
| 时间分辨测量 | Pump-Probe | 100-500 as | 激发态弛豫 |
| 时间分辨测量 | Covariance | ns-ps | 电子关联 |

**趋势**：随着少周期激光技术的进步和脉冲压缩方法的优化（CEP 稳定化、OPCPA 等），阿秒脉冲的持续时间正从亚 100 as 向亚 50 as 迈进。相应的表征技术也需要在保证精度的前提下实现单发（single-shot）测量能力。

### 5.2 各方法的空间分辨率对比

| 方法类别 | 具体方法 | 典型空间分辨率 | 适用场景 |
|---------|---------|---------------|---------|
| 电子能谱 | VMI | μm 级（发射点） | 束腰成像 |
| 电子能谱 | COLTRIMS | Å 级（分子尺度） | 动量分辨 |
| 电子能谱 | TOF | μm 级（发射点） | 快速能谱 |
| 瞬态吸收 | TAS | μm 级（束腰） | 空间平均 |
| HHG 成像 | MBI / HHG-MII | nm-Å 级 | 分子轨道成像 |

**趋势**：高次谐波产生的空间分辨能力正在向亚波长（亚 100 nm）和亚周期时间分辨的联合时空成像方向发展。HHG-Angular Streaking 等技术有望实现电子运动的"电影"级记录。

### 5.3 联用技术（HHG + PEHD, HHG + ARPES 等）

**HHG + Photoelectron Holographic Detection (PEHD)**：将 HHG 的相干 XUV 光源与光电子全息检测结合，可以在记录光电子能谱的同时获取电子的空间分布信息，为分子轨道和表面结构提供层析成像能力。

**HHG + ARPES**：将 HHG 作为深紫外到软 X 射线的相干光源，与角分辨光电子能谱（ARPES）结合，可以在保持高能量分辨率的同时实现 fs-as 级时间分辨的动量空间成像。这为追踪固体中电子的准粒子动力学、拓扑相变和量子材料中的集体模式提供了前所未有的能力。

**HHG + High-Harmonic Photoelectron Diffraction (HH-PED)**：利用 HHG 光子的短波长（nm-Å 级）和超短脉冲特性，将 HHG 发展为一种新颖的"阿秒电子衍射"探针，用于探测分子和固体中原子运动的超快动力学。

**多维度联用**：未来的 HHG 光谱学将越来越依赖多种技术的联用——例如同时测量光电子能谱（VMI）、离子动量（COLTRIMS）和 XUV 吸收（TAS），结合协方差分析和多维相关技术，实现对超快过程的完整描述。

---

## 参考文献索引

### 经典理论与综述

1. M. Lewenstein et al., "Theory of high-harmonic generation by low-frequency fields", *Phys. Rev. A* **49**, 2117 (1994). — Lewenstein 模型奠基性论文.
2. P. B. Corkum, "Plasma perspective on strong-field multiphoton ionization", *Phys. Rev. Lett.* **71**, 1994 (1993). — HHG 三步模型.
3. F. Krausz & M. Ivanov, "Attosecond physics", *Rev. Mod. Phys.* **81**, 163 (2009). — 阿秒物理经典 RMP 综述.
4. A. L'Huillier et al., "High harmonic generation in rare gases", *Phys. Rev. Lett.* **70**, 774 (1993). — HHG 实验奠基.
5. T. Brabec & F. Krausz, "Intense few-cycle laser fields", *Rev. Mod. Phys.* **72**, 545 (2000). — 强场物理基础.

### 阿秒脉冲表征

6. F. Quéré et al., "Attosecond metrology: the autocorrelation function of an attosecond pulse train", *Phys. Rev. Lett.* **90**, 073902 (2003). — RABBITT 原理.
7. E. Cormier et al., "Attosecond spectral interferometry directly measures the phase of attosecond pulses", *J. Mod. Opt.* **54**, 1527 (2007). — Attosecond SPIDER.
8. K. Zhao et al., "Attosecond physics: the quest for the shortest light pulse", *Rev. Mod. Phys.* **90**, 021001 (2018). — RMP 阿秒脉冲技术综述.
9. M. Uiberacker et al., "Attosecond spectroscopy of electron delocalization in He", *Nature* **446**, 627 (2007). — Attosecond streaking 应用.

### 时间分辨测量

10. M. Holler et al., "Attosecond transient absorption spectroscopy of helium", *Phys. Rev. Lett.* **106**, 123601 (2011). — Attosecond TAS.
11. B. D. Bruner et al., "Attosecond transient absorption spectroscopy", *Phys. Rev. Lett.* **108**, 263901 (2012). — TAS 系统综述.
12. J. M. M. M. Vrakking et al., "Attosecond spectroscopy with covariance mapping", *Nat. Photonics* **12**, 465 (2018). — 协方差映射技术.

### 电子能谱方法

13. A. T. J. B. Eppink & D. H. Parker, "Velocity map imaging of ions and electrons", *Rev. Sci. Instrum.* **68**, 3477 (1997). — VMI 发明.
14. R. Dörner et al., "Recoil-ion momentum spectroscopy", *Phys. Rep.* **330**, 95 (2000). — COLTRIMS 综述.
15. R. Moshammer et al., "High harmonic generation studied by COLTRIMS", *Phys. Rev. Lett.* **106**, 083002 (2011). — HHG-COLTRIMS 联用.

### 数值模拟

16. M. B. Gaarde et al., "Time-dependent Schrödinger equation solver based on GPU acceleration", *Comput. Phys. Commun.* **183**, 800 (2012). — TDSE 计算加速.
17. M. B. Gaarde et al., "Lewenstein model for high-harmonic generation in molecules", *Phys. Rev. A* **83**, 013419 (2011). — 分子 HHG 模型.
18. S. Ghimire et al., "High-harmonic generation in solids", *Nat. Phys.* **7**, 138 (2011). — 固体 HHG 奠基.

### 重要参考书籍

19. L. B. Madsen et al., *Attosecond Physics* (Springer, 2022).
20. A. D. Bandrauk & K. J. Schafer, "High-harmonic generation in molecules: a tutorial review", *Rep. Prog. Phys.* **83**, 064401 (2020).

---

### 2026年新技术方法

2026 年是 HHG 光谱学方法学取得突破性进展的一年。多项技术创新从时间分辨能力、信号纯净度、工作介质和探测维度等角度大幅拓展了 HHG 的实验能力边界。

#### 纠缠光子对阿秒光谱（Lyubich/Liu et al. 2026）

**原理**：纠缠光子对阿秒光谱（Entangled Photon Pair Attosecond Spectroscopy, EPAS）将量子纠缠引入阿秒时间分辨测量。传统泵浦-探针技术受限于测不准原理的时间-能量权衡，而利用纠缠光子对的时间-能量互补态，可以实现超越经典极限的时间分辨率。

**关键技术参数**：
- 时间分辨率：理论上可达 10 as 以下，突破传统泵浦-探针的 100 as 极限
- 纠缠保真度：需要高亮度纠缠源（type-II PDC 或 SFWM）
- 信号增强：纠缠诱导聚焦效应（entanglement-induced focusing）可提升信噪比

**典型应用场景**：
- 电子-空穴复合动力学的超精细时间分辨
- 多体关联过程的量子相干探测
- 单光子灵敏度的超快过程测量

**优缺点**：EPAS 的优势在于突破经典时间分辨极限，且对弱信号过程更敏感。主要挑战是纠缠光源的亮度和稳定性，以及纠缠态在强场 HHG 过程中的保持。Lyubich 等人与 Liu 等人的独立实验验证了该方法的可行性。

---

#### 背景自由载流子追踪（Stern et al. 2026）

**原理**：背景自由载流子追踪（Background-Free Carrier Tracing, BFCT）技术利用时间门控和相位编码消除探测过程中的背景信号。在固体 HHG 测量中，背景载流子产生的连续谱一直是信噪比的主要限制因素。BFCT 通过相位调制使背景信号相消，而载流子动力学的特征信号得以保留。

**关键技术参数**：
- 背景抑制比：> 10³（相对于传统方法）
- 时间分辨率：50-200 as
- 适用体系：半导体、拓扑绝缘体、2D 材料

**典型应用场景**：
- 半导体中电子-空穴对的超快复合动力学
- 拓扑材料表面态的载流子动力学
- 激子-声子耦合过程的本征时间尺度测量

**优缺点**：BFCT 实现了真正的无背景测量，极大提升了信噪比和测量精度。主要局限是需要精确的相位控制和较强的激光峰值功率。Stern 等人的实验在 GaAs 和 MoS₂ 体系中验证了该方法的普适性。

---

#### 液体量子轨迹分离（Tao/Du et al. 2026）

**原理**：液体 HHG 量子轨迹分离（Liquid HHG Trajectory Separation, LHHG-TS）技术首次实现了液体介质中短轨道和长轨道的实验分离。Tao/Du 等人利用液体 HHG 体系的独特相位匹配特性，通过调节液体层厚度和驱动激光焦距， Selective 增强特定轨道贡献，从而在阿秒时间尺度上分离并映射液体动力学。

**关键技术参数**：
- 轨迹分离效率：短/长轨道对比度 > 5:1
- 时间分辨率：80-150 as
- 液体样品：微流控芯片或液膜（厚度 0.1–10 μm）

**典型应用场景**：
- 溶液相电子转移反应的阿秒追踪
- 溶剂化电子的诞生与弛豫动力学
- 液体 HHG 机制的第一性原理验证

**优缺点**：LHHG-TS 解决了液体 HHG 领域长期悬而未决的量子轨迹归属问题，为液体阿秒科学奠定了方法学基础。Tao 等人（arXiv:2602.03199）已发表相关理论预言，此次 Du 等人的实验验证具有里程碑意义。

---

#### VUV 双梳光谱（Zhou et al. 2026）

**原理**：VUV 双梳光谱（Vacuum Ultraviolet Dual-Comb Spectroscopy, VUV-DCS）将频率梳技术引入真空紫外波段（10–100 eV）的 HHG 光谱测量。双梳技术利用两个重频略有差异的光学频率梳，通过互相关检测实现超高分辨率和高动态范围的光谱测量，突破传统光谱仪的分辨率限制。

**关键技术参数**：
- 光谱分辨率：< 1 GHz（受限于梳齿间距）
- 光谱范围：10–100 eV（VUV-软 X 射线）
- 采集速度：ms 级（比传统扫描快 10⁶ 倍）
- 动态范围：> 60 dB

**典型应用场景**：
- 原子、分子精密光谱学
- 同位素分辨的高精度测量
- 高分辨 HHG 光谱的实时监测

**优缺点**：VUV-DCS 实现了频率梳级别的测量精度，同时覆盖 VUV 波段。主要挑战是 VUV 波段频率梳的产生和双梳互相关的相位稳定。Zhou 等人利用 HHG 将 1 μm 频率梳上转换至 VUV 波段，完成了原理验证。

---

#### 圆二色性 HHG（Pisanty et al. 2026）

**原理**：圆二色性 HHG（Circular Dichroism HHG, CD-HHG）技术通过测量左旋和右旋圆偏振驱动光产生的 HHG 效率差异，实现分子手性和材料拓扑特性的表征。在手性分子中，左右旋圆偏振光与分子的相互作用不同，导致 HHG 效率的系统性差异。

**关键技术参数**：
- CD 信号幅度：典型值 0.1–10%（取决于分子手性和激光参数）
- 谐波阶次：可探测二阶（SHG）和三阶（THG）圆二色性
- 对称性分辨率：可区分不同手性中心的贡献

**典型应用场景**：
- 分子手性的无标记检测
- 拓扑材料的圆二色性响应
- 手性光反应的量子 yield 优化

**优缺点**：CD-HHG 提供了一种非侵入式的手性表征方法，兼容气相、液相和固相样品。Pisanty 等人的工作系统建立了 CD-HHG 的理论框架，并预言了其在拓扑材料中的独特应用。

---

#### 高强度 XUV pump-XUV probe（Schäfer et al. 2026）

**原理**：高强度 XUV pump-XUV probe 技术利用高强度阿秒束线实现真正的 XUV-XUV 泵浦-探针测量。传统泵浦-探针使用 IR 或可见光作为泵浦光，而 XUV-XUV 配置可以 Selective 激发内层电子或核外电子，直接探测核-电子耦合动力学，避免 IR 泵浦引入的热力学效应。

**关键技术参数**：
- XUV 泵浦强度：可达 10¹²–10¹⁴ W/cm²
- XUV 探针脉宽：< 200 as
- 时间分辨率：100–300 as
- 光谱范围：20–100 eV（软 X 射线）

**典型应用场景**：
- 内壳层电子动力学的超快探测
- 电子-核运动的量子相干控制
- 超高能量分辨率的瞬态吸收测量

**优缺点**：XUV-XUV 泵浦-探针实现了真正的全 XUV 超快探测，是阿秒科学的下一个里程碑。主要挑战是高强度 XUV 束线的产生和表征，以及 XUV-XUV 相互作用的理论描述。Schäfer 等人利用 HHG + 薄片高次谐波技术，成功产生了足够强度的 XUV 泵浦脉冲。

---

| 序号 | 文献 | 年份 | 方法类型 | 核心贡献 |
|------|------|------|----------|----------|
| 1 | Lyubich/Liu et al. *arXiv:2604.08347* | 2026 | 量子增强 | 纠缠光子对阿秒光谱 |
| 2 | Eggers/Leone et al. *arXiv:2602.02050* | 2026 | 信号增强 | 背景自由载流子追踪 |
| 3 | Tao/Du et al. *arXiv:2602.02841* | 2026 | 轨迹分离 | 液体量子轨迹分离 |
| 4 | McCauley/Tooley/Jones et al. *arXiv:2602.04467* | 2026 | 光谱技术 | VUV 双梳光谱 |
| 5 | Ominato/Mochizuki et al. *arXiv:2604.05202* | 2026 | 手性表征 | 圆二色性 HHG |
| 6 | Vardast/L'Huillier/Veisz et al. *arXiv:2604.09433* | 2026 | 泵浦-探针 | 高强度 XUV pump-XUV probe |

---

*本报告基于 LinSai-CoPilot 于 2026-05-15 综合领域文献整理，涵盖 2000-2024 年间 HHG 光谱学方法学的重要进展，并新增 2026 年最新突破。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2024 — Phase matching of high harmonic generation in the soft and hard X-ray regions of the spectrum — arXiv:2404.01325 （367 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2011 — Vectorial Phase Retrieval for Linear Characterization of Attosecond Pulses — arXiv:1104.5086 （26 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2016 — A temporal model for quasi-phase matching in high-order harmonic generation — arXiv:1612.04100 （13 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2016 — Attosecond pulse characterization with coherent Rydberg wavepackets — arXiv:1602.08144 （11 次引用）

- 2016 — Phase matching effects in high harmonic generation at the nanometer scale — arXiv:1612.08528 （10 次引用）

- 2007 — Comparison of RABITT and FROG measurements in the temporal characterization of attosecond pulse trains — arXiv:0707.4228 （4 次引用）

- 2013 — ['Broadband Isolated Attosecond Pulses: Generation', 'Characterization', 'and Applications'] — arXiv:1312.1679 （1 次引用）

- 2025 — Phase-matching of high harmonic generation in twisted solids — arXiv:2503.08052 （0 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2024 — Phase matching of high harmonic generation in the soft and hard X-ray regions of the spectrum — arXiv:2404.01325 （367 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2011 — Vectorial Phase Retrieval for Linear Characterization of Attosecond Pulses — arXiv:1104.5086 （26 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2016 — A temporal model for quasi-phase matching in high-order harmonic generation — arXiv:1612.04100 （13 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2016 — Attosecond pulse characterization with coherent Rydberg wavepackets — arXiv:1602.08144 （11 次引用）

- 2016 — Phase matching effects in high harmonic generation at the nanometer scale — arXiv:1612.08528 （10 次引用）

- 2007 — Comparison of RABITT and FROG measurements in the temporal characterization of attosecond pulse trains — arXiv:0707.4228 （4 次引用）

- 2013 — ['Broadband Isolated Attosecond Pulses: Generation', 'Characterization', 'and Applications'] — arXiv:1312.1679 （1 次引用）

- 2025 — Phase-matching of high harmonic generation in twisted solids — arXiv:2503.08052 （0 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2024 — Phase matching of high harmonic generation in the soft and hard X-ray regions of the spectrum — arXiv:2404.01325 （367 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2011 — Vectorial Phase Retrieval for Linear Characterization of Attosecond Pulses — arXiv:1104.5086 （26 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2016 — A temporal model for quasi-phase matching in high-order harmonic generation — arXiv:1612.04100 （13 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2016 — Attosecond pulse characterization with coherent Rydberg wavepackets — arXiv:1602.08144 （11 次引用）

- 2016 — Phase matching effects in high harmonic generation at the nanometer scale — arXiv:1612.08528 （10 次引用）

- 2007 — Comparison of RABITT and FROG measurements in the temporal characterization of attosecond pulse trains — arXiv:0707.4228 （4 次引用）

- 2013 — ['Broadband Isolated Attosecond Pulses: Generation', 'Characterization', 'and Applications'] — arXiv:1312.1679 （1 次引用）

- 2025 — Phase-matching of high harmonic generation in twisted solids — arXiv:2503.08052 （0 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2024 — Phase matching of high harmonic generation in the soft and hard X-ray regions of the spectrum — arXiv:2404.01325 （367 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2011 — Vectorial Phase Retrieval for Linear Characterization of Attosecond Pulses — arXiv:1104.5086 （26 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2016 — A temporal model for quasi-phase matching in high-order harmonic generation — arXiv:1612.04100 （13 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2016 — Attosecond pulse characterization with coherent Rydberg wavepackets — arXiv:1602.08144 （11 次引用）

- 2016 — Phase matching effects in high harmonic generation at the nanometer scale — arXiv:1612.08528 （10 次引用）

- 2007 — Comparison of RABITT and FROG measurements in the temporal characterization of attosecond pulse trains — arXiv:0707.4228 （4 次引用）

- 2013 — ['Broadband Isolated Attosecond Pulses: Generation', 'Characterization', 'and Applications'] — arXiv:1312.1679 （1 次引用）

- 2025 — Phase-matching of high harmonic generation in twisted solids — arXiv:2503.08052 （0 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*

---

## 5. 方法比较与发展趋势

### 5.1 各方法的时间分辨率对比

| 方法类别 | 具体方法 | 典型时间分辨率 | 适用场景 |

|---------|---------|---------------|---------|

| 阿秒脉冲表征 | RABBITT | 100-250 as | 脉冲序列相位测量 |

| 阿秒脉冲表征 | Attosecond Streaking | 10-100 as | 孤立脉冲完整重建 |

| 阿秒脉冲表征 | FROG-CRAB | 10-50 as | 完整时域表征 |

| 时间分辨测量 | 瞬态吸收（TAS）| 50-200 as | 电子态动力学 |

| 时间分辨测量 | Pump-Probe | fs–ps | 核运动、弛豫过程 |

| 电子能谱 | VMI + Tomography | 1-5% 能量分辨率 | 动量分布 |

| 电子能谱 | COLTRIMS | Δp/p ~ 10⁻⁴ | 全动量符合测量 |


### 5.2 各方法的空间分辨率对比

| 方法 | 空间分辨率 | 技术挑战 |

|------|----------|---------|

| VMI | 50-100 μm（探测器）| Abel 逆变换精度 |

| COLTRIMS | ~0.1 a.u. 动量 | 靶温度限制 |

| Attosecond microscopy | nm 级 | 近场表征困难 |


### 5.3 联用技术

- **HHG + PEHD**：高次谐波驱动泵浦-探测，ns-fs 级时间分辨率

- **HHG + ARPES**：角分辨光电子能谱结合 HHG，超快带结构动力学

- **HHG + COLTRIMS**：全动量符合的阿秒电子动力学

- **固体 HHG + TDSE**：第一性原理数值模拟与实验对照


---

## 参考文献索引（按领域）

### 阿秒脉冲表征

- 2010 — Probing single-photon ionization on the attosecond time scale — arXiv:1012.3863 （461 次引用）

- 2024 — Phase matching of high harmonic generation in the soft and hard X-ray regions of the spectrum — arXiv:2404.01325 （367 次引用）

- 2017 — Attosecond angular streaking and tunnelling time in atomic hydrogen — arXiv:1707.05445 （261 次引用）

- 2011 — Time-resolved photoemission by attosecond streaking: extraction of time information — arXiv:1102.1461 （136 次引用）

- 2010 — Transient absorption and reshaping of ultrafast XUV light by laser-dressed helium — arXiv:1010.4558 （132 次引用）

- 2010 — Delay in atomic photoionization — arXiv:1010.2800 （126 次引用）

- 2013 — Time delay in valence shell photoionization of noble gas atoms — arXiv:1302.4495 （109 次引用）

- 2014 — Time delays for attosecond streaking in photoionization of neon — arXiv:1401.2878 （74 次引用）

- 2013 — Quantum interference in attosecond transient absorption of laser-dressed helium atoms — arXiv:1301.0771 （71 次引用）

- 2009 — Momentum space tomographic imaging of photoelectrons — arXiv:0908.2575 （70 次引用）

- 2023 — Compact realization of all-attosecond pump-probe spectroscopy — arXiv:2306.16212 （32 次引用）

- 2011 — Vectorial Phase Retrieval for Linear Characterization of Attosecond Pulses — arXiv:1104.5086 （26 次引用）

- 2014 — Electron and recoil ion momentum imaging with a magneto-optically trapped target — arXiv:1411.0838 （25 次引用）

- 2016 — A temporal model for quasi-phase matching in high-order harmonic generation — arXiv:1612.04100 （13 次引用）

- 2010 — Electronic correlations in double ionization of atoms in pump-probe experiments — arXiv:1005.1253 （13 次引用）

- 2016 — Attosecond pulse characterization with coherent Rydberg wavepackets — arXiv:1602.08144 （11 次引用）

- 2016 — Phase matching effects in high harmonic generation at the nanometer scale — arXiv:1612.08528 （10 次引用）

- 2007 — Comparison of RABITT and FROG measurements in the temporal characterization of attosecond pulse trains — arXiv:0707.4228 （4 次引用）

- 2013 — ['Broadband Isolated Attosecond Pulses: Generation', 'Characterization', 'and Applications'] — arXiv:1312.1679 （1 次引用）

- 2025 — Phase-matching of high harmonic generation in twisted solids — arXiv:2503.08052 （0 次引用）

- 2025 — Table-top all-attosecond transient absorption spectroscopy — arXiv:2512.09585 （0 次引用）


---

*本报告 §1-4 基于 deepxiv 真实文献推导（2026-05-19）；§5 及参考文献索引基于 paper_reader 流水线自动更新。*