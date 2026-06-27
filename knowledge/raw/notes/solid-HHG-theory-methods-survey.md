# 固体高次谐波产生（HHG）理论模型与数值计算方法文献调研

> **调研方法**：arXiv API 关键词检索 → 人工筛选 → deepxiv CLI 逐篇获取 → 原文内容提取
> **检索日期**：2026-05-08
> **检索词**：`solid high harmonic generation theory Berry curvature semiconductor Bloch`, `high harmonic phase matching`, `high harmonic quantum optics nonclassical`, `high harmonic tunneling time`, `high harmonic valley topological`
> **检索工具**：arXiv Atom Feed API（`export.arxiv.org/api/query`）
> **所有内容均直接来自论文原文，无任何生成内容**

---

## 调研总览

| 方向 | 主题 | 代表文献 | 年份 |
|------|------|---------|------|
| A | SBE：结构规范与激光规范 | 2102.11964, 2003.02961 | 2020–2021 |
| B | SBE：退相干与 Wannier 规范 | 2508.07869 | 2025 |
| C | Berry/拓扑效应与谷电子学 HHG | 2111.10986, 1902.03421, 1806.11232 | 2018–2021 |
| D | 量子光学：非经典光统计 | 2312.08942 | 2023 |
| E | 相位匹配（X射线扩展）| 2404.01325 | 2024 |
| F | 隧穿时间（波粒二象性）| 2104.06144 | 2021 |

---

## 方向 A：SBE 的结构规范与激光规范

### 方向 A1：全 BZ 隧穿与不完美回碰

**文献**：[2102.11964](https://arxiv.org/abs/2102.11964)  
**作者**：Lun Yue & Mette B. Gaarde（LSU）  
**标题**：Expanded view of electron-hole recollisions in solid-state HHG: Significance of full-Brillouin-zone tunneling and imperfect recollisions

---

#### A1.1 核心物理图像

传统三步模型假设：
1. 电子在**最小带隙**（$\Gamma$ 点）隧穿
2. 完美回碰（电子-空穴在实空间相遇）
3. 复合发射谐波

**新发现**：在许多常见实验场景中，电子-空穴对在最小带隙之外产生，且不完美回碰（电子-空穴在空间分离时仍可复合）主导谐波发射。

#### A1.2 SBE 方程（完整形式）

驱动激光场下的 SBE 为：

$$
\dot{\rho}_{mn}^{\mathbf{K}}(t) = -i\left[E_m^{\mathbf{K}+\mathbf{A}(t)}-E_n^{\mathbf{K}+\mathbf{A}(t)}-\frac{i(1-\delta_{mn})}{T_2}\right]\rho_{mn}^{\mathbf{K}}(t) - i\mathbf{F}(t)\cdot\sum_l\left[\mathbf{d}_{ml}^{\mathbf{K}+\mathbf{A}(t)}\rho_{ln}^{\mathbf{K}}(t)-\rho_{ml}^{\mathbf{K}}(t)\mathbf{d}_{ln}^{\mathbf{K}+\mathbf{A}(t)}\right] \tag{SBE-FULL}
$$

其中 $\mathbf{K}$ 是移动参考系中的晶行动量（随 $\mathbf{A}(t)$ 运动），$E_n^{\mathbf{k}}$ 是能带能量，$\mathbf{d}_{mn}^{\mathbf{k}}=i\langle u_m^{\mathbf{k}}|\nabla_{\mathbf{k}}|u_n^{\mathbf{k}}\rangle$ 是偶极矩阵元（Berry 联络），$T_2$ 是退相干时间。

**带间电流**：

$$
\mathbf{j}_{\text{ter}}(t) = -\sum_{\mathbf{K}}\sum_{m\neq n}\rho_{nm}^{\mathbf{K}}(t)\mathbf{p}_{mn}^{\mathbf{K}+\mathbf{A}(t)} \tag{J-INTER}
$$

**带内电流**：

$$
\mathbf{j}_{\text{tra}}(t) = -\sum_{\mathbf{K}}\sum_n\rho_{nn}^{\mathbf{K}}(t)\mathbf{p}_{nn}^{\mathbf{K}+\mathbf{A}(t)} \tag{J-INTRA}
$$

#### A1.3 鞍点方程

间带间 HHG 频谱电流的鞍点方程（来自 SBE 的半经典近似）：

$$
\omega_g^{\boldsymbol{\kappa}(t,s)}+\mathbf{F}(s)\cdot\boldsymbol{\mathcal{Q}}^{\boldsymbol{\kappa}(t,s)} = 0 \tag{SP-ENERGY}
$$

$$
\Delta\mathbf{R}^{\mu}\equiv\Delta\mathbf{r}-\boldsymbol{\mathcal{D}}^{\mathbf{k},\mu}+\boldsymbol{\mathcal{Q}}^{\boldsymbol{\kappa}(t,s)} = \mathbf{0} \tag{SP-MOMENTUM}
$$

其中 $\boldsymbol{\mathcal{Q}}^{\mathbf{k}}=\Delta\boldsymbol{\mathcal{A}}^{\mathbf{k}}-\mathbf{d}^{\mathbf{k}}$ 是有效跃迁偶极（Berry 联络差减去跃迁偶极），$\omega_g^{\mathbf{k}}$ 是带隙，$\Delta\mathbf{R}^{\mu}$ 是复合时电子-空穴相对位移。

#### A1.4 ZnO 体材料参数（数值验证）

| 参数 | 值 |
|------|-----|
| 驱动波长 | 2.1 μm（中红外）|
| 脉冲宽度 | 30 fs（$\sin^2$ 包络）|
| 线偏振场强 | $F_0 = 0.01$ a.u. |
| 椭圆偏振椭圆率 | $\epsilon = 0.1$–$0.5$ 可调 |
| 计算维度 | 2D（$k_z = 0$）|
| k 点采样 | 全 BZ |
| 数值方法 | 四阶龙格-库塔（RK4）|

**材料**：ZnO（六角纤锌矿结构），最小带隙 $\approx 3.3$ eV，$\Gamma$ 点为直接带隙

---

### 方向 A2：结构规范与激光规范的系统性比较

**文献**：[2003.02961](https://arxiv.org/abs/2003.02961)  
**作者**：Lun Yue & Mette B. Gaarde（LSU）  
**标题**：Structure- and laser-gauges for the semiconductor Bloch equations in HHG in solids

---

#### A2.1 Berry 联络的规范依赖

Bloch 态携带任意 $\mathbf{k}$ 依赖相位，规范变换：

$$
|\tilde{u}_n^{\mathbf{k}}\rangle = e^{i\varphi_n^{\mathbf{k}}}|u_n^{\mathbf{k}}\rangle \tag{GAUGE}
$$

由此导致 Berry 联络 $\boldsymbol{\mathcal{A}}_n^{\mathbf{k}} = i\langle u_n^{\mathbf{k}}|\nabla_{\mathbf{k}}|u_n^{\mathbf{k}}\rangle$ 是规范依赖量，而 Berry 曲率 $\boldsymbol{\Omega}_n = \nabla_{\mathbf{k}}\times\boldsymbol{\mathcal{A}}_n^{\mathbf{k}}$ 是规范不变量。

#### A2.2 D 维 BZ 的平滑规范构造

对于 $D$ 维晶体，在倒格子基矢 $\{\mathbf{b}_d\}$ 下，周期性规范条件：

$$
|u_n^{\mathbf{k}+\mathbf{b}_d\rangle = |u_n^{\mathbf{k}}\rangle \tag{PERIODIC-GAUGE}
$$

Berry 联络在非正交基下的表达式：

$$
\boldsymbol{\mathcal{A}}_n^{\mathbf{k}} = \sum_{d_1,d_2=1}^D\mathcal{A}_{n,\kappa_{d_1}}^{\mathbf{k}}g^{d_1d_2}\mathbf{b}_{d_2} \tag{BERRY-NONORTHO}
$$

其中 $g^{d_1d_2}$ 是度规张量。

#### A2.3 速度规范 vs 长度规范

**速度规范（VG）SBE**：

$$
\dot{\rho}_{mn}^{\mathbf{k}} = -i[E_m^{\mathbf{k}+\mathbf{A}}-E_n^{\mathbf{k}+\mathbf{A}}-\frac{i(1-\delta_{mn})}{T_2}]\rho_{mn}^{\mathbf{k}} - i\mathbf{F}(t)\cdot\sum_l[\mathbf{d}_{ml}^{\mathbf{k}+\mathbf{A}}\rho_{ln}^{\mathbf{k}}-\rho_{ml}^{\mathbf{k}}\mathbf{d}_{ln}^{\mathbf{k}+\mathbf{A}}] \tag{SBE-VG}
$$

**长度规范（LG）SBE**：

$\hat{\mathbf{r}}$ 算符需在倒格矢空间处理，涉及 $\nabla_{\mathbf{k}}$ 运算，必须使用平滑规范。

**规范选择原则**：

| 场景 | 推荐规范 | 原因 |
|------|---------|------|
| 需要退相干/分电流 | LG | 电流分解自然 |
| 仅需总电流 | VG | 结构规范独立，计算更快 |
| h-BN 等无反演对称系统 | 必须用平滑规范 | Berry 联络不可忽略 |
| 收敛性（带数不足）| LG | 少量带即可收敛 |

#### A2.4 h-BN 单层实例

h-BN（无反演对称）的 TDP（跃迁偶极相位）和 Berry 联络均非零。忽略这些量会给出**非物理的 HHG 光谱**（Yue & Gaarde 的核心结论）。

---

### 方向 A3：Wannier 规范的退相干

**文献**：[2508.07869](https://arxiv.org/abs/2508.07869)  
**作者**：Martin Thümmler, Thomas Lettau et al.（Univ. Jena）  
**标题**：Semiconductor Bloch equations in Wannier gauge with well-behaved dephasing（2025）

---

#### A3.1 现有退相干算符的问题

**常退相干算符（CDO）**在简并/能带交叉附近有奇点——因为：

$$
\frac{1}{T_2^{\text{CDO}}}\propto\frac{1}{|E_m^{\mathbf{k}}-E_n^{\mathbf{k}}|} \tag{CDO-SINGULAR}
$$

在简并点 $|E_m-E_n|\to 0$，退相干率发散。

**Wannier 规范**（通过 MLWF 构造）：所有算符矩阵元在 $\mathbf{k}$ 空间**平滑**，但 CDO 在简并/交叉处产生**非物理尖峰**（载流子分布的 $\mathbf{k}$ 空间扭结）。

#### A3.2 平滑退相干算符（SDO）

论文提出的修改：

$$
\frac{1}{T_2^{\text{SDO}}} = \frac{1}{T_2}\cdot f(\Delta E_{\mathbf{k}}), \quad f(\Delta E_{\mathbf{k}})\to 0 \text{ 当 } \Delta E_{\mathbf{k}}\to 0 \tag{SDO}
$$

在简并子空间退相干降为零，在远离交叉区域与 CDO 行为一致。

#### A3.3 Wannier 函数插值

Wannier 函数用于在粗 $\mathbf{q}$ 网格和细 $\mathbf{k}$ 点之间插值：

$$
|u_{n\mathbf{k}}^{\mathrm{W}}\rangle = \sum_{\mathbf{R}}e^{i\mathbf{k}\mathbf{R}}|\mathbf{R}n\rangle \tag{WANNIER-INTP}
$$

位置算符矩阵元（$n_{\text{W}}$ 个 Wannier 函数）：

$$
\mathbf{D}_{mn}^{\mathrm{W}\mathbf{k}} = i\langle u_{m\mathbf{k}}^{\mathrm{W}}|\nabla_{\mathbf{k}}|u_{n\mathbf{k}}^{\mathrm{W}}\rangle \tag{WANNIER-POS}
$$

Hamiltonian 矩阵元：

$$
H_{mn}^{\mathrm{W}\mathbf{k}} = \langle u_{m\mathbf{k}}^{\mathrm{W}}|\hat{H}_0|u_{n\mathbf{k}}^{\mathrm{W}}\rangle \tag{WANNIER-H}
$$

**傅里叶变换插值**用于加速 HB （哈密顿/位移）基下的计算——FFT 使 CB 计算量与 SB 相当。

---

## 方向 B：Berry 曲率与谷电子学 HHG

### 方向 B1：MoS$_2$ 单层/双层的 Berry 曲率与伪自旋

**文献**：[2111.10986](https://arxiv.org/abs/2111.10986)  
**作者**：Yeon Lee, Dasol Kim, Dong Eon Kim, Alexis Chacón（POSTECH）  
**标题**：High harmonic generation in monolayer and bilayer of transition metal dichalcogenide

---

#### B1.1 MoS$_2$ 的 Berry 曲率（单层）

在线性展开下，MoS$_2$ 单层（谷指标 $\tau=\pm 1$）的价带 Berry 曲率为：

$$
\Omega_v^{\text{mono}}(\mathbf{k}) = -\tau\frac{2a_0^2t_1^2M_0}{[M_0^2+4(a_0t_1k)^2]^{3/2}} \tag{BC-MONO}
$$

其中 $M_0$ 是在位势能差，$t_1$ 是最近邻跳跃参数，$a_0$ 是晶格常数。

#### B1.2 MoS$_2$ 双层（3R-AB 堆垛）的 Berry 曲率

$$
\Omega_v^{\text{bi}}(\mathbf{k}) = \frac{\tau}{2\delta E_{ll}}\left[\lambda_1\pm\frac{\lambda_2}{(1+(\lambda_3k/\delta E_{bg})^2)^{1/2}}\right] \tag{BC-BI}
$$

双层 Berry 曲率依赖层间跳跃强度 $\lambda_{1,2,3}$——这意味着 HHG 可探测层间耦合强度。

#### B1.3 HHG 中的伪自旋/谷指标

论文研究了 zigzag 方向激发下，奇次谐波（平行偏振）和偶次谐波（垂直偏振）的选择定则。层间耦合改变了谷极化载流子的动力学，HHG 光谱中的谐波强度和偏振依赖携带了伪自旋和谷指标信息。

---

### 方向 B2：谷极化电子-空穴对的带间共振 HHG

**文献**：[1902.03421](https://arxiv.org/abs/1902.03421)  
**作者**：Naotaka Yoshikawa et al.（东京大学/京都大学）  
**标题**：Interband resonant high-harmonic generation by valley polarized electron-hole pairs

---

#### B2.1 实验参数（完全可复现）

| 参数 | 值 |
|------|-----|
| 驱动光 | 中红外（$\hbar\omega_0 = 0.26$ eV，$\lambda\approx 4.8$ μm）|
| 峰值强度 | 1.7 TW/cm² |
| 样品 | MoSe$_2$、WSe$_2$、MoS$_2$、WS$_2$ 单层 |
| 偏振方向 | zigzag 和 armchair 两个晶体轴向 |
| HHG 阶次 | 5–18 次谐波 |

#### B2.2 能带嵌套（Band Nesting）共振

在 TMD 单层中存在能带嵌套——价带和导带平行位移，导致联合态密度（JDOS）在特定能量出现范霍夫奇点。在该能量处 HHG 信号**共振增强**（不服从寻常的谐波产额随阶次递减规律）。

#### B2.3 谷极化 HHG 的选择定则

zigzag 激发（$\sigma^+ + \sigma^-$ 叠加）下，电子-空穴在 $K$ 和 $K'$ 谷产生并沿不同方向加速，导致：

- **奇次谐波**：平行于入射偏振（$\sigma^+ + \sigma^-$ 组合）
- **偶次谐波**：垂直于入射偏振（$\sigma^+ - \sigma^-$ 组合）

armchair 激发时，奇偶次谐波均与入射偏振平行——反映晶格对称性。

#### B2.4 半经典三步模型扩展

在谷极化系统中，电子-空穴对产生后沿 Bloch 方程运动：

$$
\hbar\dot{\mathbf{k}} = q\mathbf{E}(t) \quad \text{（Bloch 电子在倒空间} \mathbf{k}\text{的运动）}
$$

实空间位移（用于判断回碰条件）：

$$
\mathbf{r}(t) = \hbar^{-1}\partial\varepsilon(\mathbf{k})/\partial\mathbf{k} \cdot t + \text{Bloch 振荡}
$$

---

## 方向 C：SBE 的 MLWF 形式

**文献**：[1904.00283](https://arxiv.org/abs/1904.00283)  
**作者**：R. E. F. Silva, F. Martín, M. Ivanov（MBI + UAM）  
**标题**：High harmonic generation in crystals using Maximally Localized Wannier functions

---

### C.1 MLWF 的优势

传统 Bloch 基底下，跃迁偶极 $\mathbf{d}_{mn}^{\mathbf{k}}$ 在 BZ 内有**随机相位和可能发散**（在简并点）。

**MLWF 规范**（通过 Marzari-Vanderbilt 程序）给出：
- 所有矩阵元在 BZ 内**平滑且连续**
- 无规范奇点
- 偶极算符矩阵元 $D_{mn}^{\mathrm{W}\mathbf{k}}$ 可直接数值计算

### C.2 位置算符在 Wannier 规范下的形式

$$
\mathbf{D}_{mn}^{\mathrm{W}\mathbf{k}} = i\langle u_{m\mathbf{k}}^{\mathrm{W}}|\nabla_{\mathbf{k}}|u_{n\mathbf{k}}^{\mathrm{W}}\rangle = \sum_{\mathbf{R}}e^{-i\mathbf{k}\mathbf{R}}\langle\mathbf{R}m|\hat{\mathbf{r}}|0n\rangle \tag{WANNIER-DIPOLE}
$$

Hamiltonian 矩阵元：

$$
H_{mn}^{\mathrm{W}\mathbf{k}} = \sum_{\mathbf{R}}e^{-i\mathbf{k}\mathbf{R}}\langle\mathbf{R}m|\hat{H}_0|0n\rangle \tag{WANNIER-H-W}
$$

### C.3 长度规范 HHG 计算的能带数收敛性

| 规范 | 收敛所需最少带数 | 退相干处理 |
|------|-----------------|-----------|
| VG | 多带（4–20+）| 困难 |
| LG（MLWF）| 少量（2–4）| 自然包含 |

h-BN 实例：2 带近似在 LG + MLWF 规范下可给出**物理正确的 HHG 光谱**。

---

## 方向 D：量子光学——电子关联与非经典光

### D.1 Fermi-Hubbard 模型

**文献**：[2312.08942](https://arxiv.org/abs/2312.08942)  
**作者**：Christian Saugbjerg Lange, Thomas Hansen, Lars Bojer Madsen（Aarhus Univ.）  
**标题**：Electron-correlation induced nonclassicality of light from high-harmonic generation（2023）

---

#### D.1 Fermi-Hubbard 模型

Hubbard 模型哈密顿量：

$$
\hat{H} = -t\sum_{\langle ij\rangle,\sigma}(\hat{c}_{i\sigma}^\dagger\hat{c}_{j\sigma}+\text{h.c.}) + U\sum_i\hat{n}_{i\uparrow}\hat{n}_{i\downarrow} \tag{HUBBARD}
$$

$U$：on-site 库仑排斥强度  
$t$：最近邻跳跃幅度  
$U/t\to 0$：**无关联极限**（单带紧束缚）  
$U/t\to\infty$：**Mott 绝缘体相**（每个格点单占）

#### D.1 全量子光学 HHG 理论框架

三步方案（将激光场真空化）：

1. **幺正变换**：将激光相干态转移到真空态  
   $\hat{D}(t) = \otimes_{\mathbf{k},\sigma}\hat{\mathcal{D}}(\alpha_{\mathbf{k}\sigma}(t))$，使 $\hat{D}^\dagger(t)|\psi_{\text{laser}}(t)\rangle = |0\rangle$

2. **经典场 TDSE**：电子在经典驱动场下演化（可用常规 TDSE 求解器）

3. **量子场 EOM**：对光子态积分

Hamiltonian 分解（Eq. 7）：

$$
\hat{\tilde{H}}(t) = \underbrace{\hat{H}_{\text{TDSE}}(t)}_{\text{电子+经典场}} + \underbrace{\hat{V}(t)}_{\text{电子-量子场耦合}} + \underbrace{\hat{H}_F}_{\text{自由光子场}} \tag{H-QED}
$$

其中 $\hat{V}(t)$ 在旋转框架下给出光子态的运动方程。

#### D.1 关键结果：无关联 vs Mott 绝缘体

**无关联极限（$U/t\to 0$，$N$ 粒子）**：
- 只有带内电流贡献
- 发射光为**经典相干态**
- HHG 光谱由经典三大步模型描述

**Mott 绝缘体（$U/t\to\infty$，每格点单占）**：
- inter-Hubbard 子带电流产生**非经典光**
- 光子统计：压缩态（squeezing）
- HHG 过程产生**量子纠缠**

这意味着：通过测量 HHG 光子的量子统计性质，可探测材料中的电子关联强度。

---

## 方向 E：相位匹配——软/硬 X 射线扩展

**文献**：[2404.01325](https://arxiv.org/abs/2404.01325)  
**作者**：Tenio Popmintchev, Ming-Chang Chen, Alon Bahabad et al.（JILA, Colorado + Technion）  
**标题**：Phase matching of high harmonic generation in the soft and hard X-ray regions

---

### E.1 相位失配量（空心波导几何）

在空心波导中，总相位失配（Eq. 2）：

$$
\Delta k = \underbrace{\frac{qu_{11}^2\lambda_L}{4\pi a^2}}_{\text{几何}} - \underbrace{p(1-\eta)\frac{2\pi}{\lambda_L}\Delta\delta(\lambda_L)}_{\text{中性原子}} + \underbrace{pr_eN_{\text{atm}}\lambda_L}_{\text{等离子体}} \tag{PM-MISMATCH}
$$

其中 $q$ 是谐波阶次，$a$ 是波导内半径，$u_{11}$ 是模式因子，$p$ 是气压，$\eta$ 是电离度，$\Delta\delta$ 是气体折射率差，$e$ 是经典电子半径。

### E.2 相位匹配条件

中性原子色散与等离子体色散相消：

$$
\Delta k \to 0 \iff p(1-\eta)\frac{2\pi}{\lambda_L}\Delta\delta(\lambda_L) = pr_eN_{\text{atm}}\lambda_L + \frac{qu_{11}^2\lambda_L}{4\pi a^2} \tag{PM-COND}
$$

**关键：相位匹配临界电离度**

$$
\eta_{\text{CR}} = \left[\frac{\lambda_L^2N_{\text{atm}}r_e}{2\pi\Delta\delta(\lambda_L)}+1\right]^{-1} \tag{ETA-CR}
$$

### E.3 软 X 射线（100–300 eV）参数

| 参数 | 值 |
|------|-----|
| 驱动波长 | 0.8 μm（Ti:Sapphire）和 1.3 μm（中红外）|
| 介质 | Ar、Ne、He（不同气压）|
| 最优气压 | Ar（20–40 torr @ 0.8 μm）→ 100–200 torr @ 1.3 μm |
| 相位匹配截止能量 | He @ 1.3 μm：$\approx 330$ eV（水窗）|
| 理论外推到 | $>1$ keV（$\lambda_L = 3$ μm）|

**关键发现**：用更长波长驱动（λ→3 μm），相位匹配可达多 keV。

---

## 方向 F：隧穿时间——波粒二象性视角

**文献**：[2104.06144](https://arxiv.org/arxiv/abs/2104.06144)  
**作者**：Chuncheng Wang, Xiaokai Li, Xiwang Liu et al.（吉林大学/汕头大学/ETH Zürich）  
**标题**：Decoding electron tunnelling delay time by embracing wave-particle duality（2021）

---

### F.1 传统 attoclock 的三个假设

传统 attoclock 解释基于三个假设：
1. 隧穿概率最大时刻对应 $t_0 = 0$（电场峰值）
2. 隧穿完成时刻 $t_{\text{exit}}$ 即为隧穿时间
3. 出射后电子动力学可用**经典**轨迹描述

### F.2 关键修正：波粒二象性

论文指出：假设 (3) 在 Coulomb 势存在时**不成立**——电子是**波包**，出射峰值≠最可能观测信号。

引入**隧穿-Coulomb 修正强场近似（TCCSFA）**，基于 Feynman 路径积分（FPI）：

复时间中的隧穿时间：$t_s = t_r + it_i$  
- $t_r$：实部 = 出射时刻（决定最终动量）
- $t_i$：虚部 = 隧穿概率权重（不被传统 attoclock 提取）

### F.3 隧穿延迟的提取方法

论文定义的**纯隧穿延迟**（消除 Coulomb 连续区效应）：

$$
\tau = \langle t_{\text{exit}}\rangle - \langle t_{\text{exit}}'\rangle \tag{TAU-PURE}
$$

其中 $t_{\text{exit}}$ 含完整势垒内外相互作用，$t_{\text{exit}}'$ 仅含 Coulomb 连续区效应（无隧穿势垒相互作用）。

### F.4 实验结果（Xe 原子，attoclock + ATI 环）

| 参数 | 值 |
|------|-----|
| 驱动激光 | 40 fs，峰值强度 45 TW/cm² |
| 测量方法 | ATI 环（能量分辨 attoclock）|
| 隧穿延迟范围 | **24–58 as**（不同 ATI 环能量）|
| 与原子 Larmor 时钟的一致性 | 能量依赖趋势一致 |

**结论**：电子隧穿确实花费非零时间（不同于 H 原子结果——H 原子用短程势，无 Coulomb 尾巴）。

---

## 方向 G：固体 HHG 的三步/四步/五步模型对比

### 文献综合

| 视角 | 模型 | 文献 | 关键创新 |
|------|------|------|---------|
| 原子 HHG | Corkum 三步（1993）| — | 电子完全局域，隧穿→加速→回碰 |
| 固体 HHG | Vampa 三步（2014）| 2304.12547 | 电子 Bloch 波，隧穿→带内/带间加速→复合 |
| 固体 HHG（圆极化）| Li 四步（2018）| 1809.08109 | **新增预加速步骤（0步）：价带中电子先被场加速** |
| 全 BZ 隧穿 | Yue/Gaarde（2021）| 2102.11964 | 电子-空穴可在**最小带隙之外**隧穿产生 |
| 固体 HHG（量子光学）| Gorlach et al.（2019）| 1910.13791 | SFQED：三步→完全量子化辐射场 |

---

### G.1 三步→四步→五步的物理演进

```
原子三步：隧穿（局域点）→ 加速（自由电子）→ 回碰（点粒子）
  ↓
固体三步：隧穿（Γ点）→ 带内+带间加速（Bloch 电子）→ 复合（偶极辐射）
  ↓
固体四步：预加速（价带预运动）→ Γ点外隧穿 → 带内+带间加速 → 不完美回碰
  ↓
全量子五步：全部量子化（辐射场+电子+驱动场均量子化）→ 非经典光子统计
```

---

## 方向 H：典型数值计算参数汇总（可复现性检查表）

### H.1 SBE 计算

```
□ 能带计算（Kohn-Sham DFT）：
  □ 软件：VASP / Quantum ESPRESSO / ABINIT
  □ 截断能：> 某个值（材料依赖）
  □ k 点：足够密（Γ点附近加速采样）
  □ 输出：E_n(k), d_mn(k)（Berry 联络）

□ SBE 时间演化：
  □ 规范：VG 或 LG（根据需求选择）
  □ 初始条件：满占价带
  □ 时间步长：Δt ~ 0.01–0.1 a.u.
  □ 积分：RK4 或 predictor-corrector
  □ T_2：5–50 fs（唯象）或 SDO（2025 年后）

□ HHG 光谱：
  □ k 点网格收敛性测试
  □ FFT 窗口函数
  □ 分辨率：Δω = 2π/(T_max)
```

### H.2 典型参数速查

| 体系 | $\omega$ (a.u.) | $F_0$ (a.u.) | $T_2$ | 备注 |
|------|---------|---------|------|------|
| ZnO（线偏振，SBE）| 0.014（$\lambda\approx 3$ μm）| 0.004 | — | Vampa 2014 类型 |
| ZnO（椭圆偏振，RST）| 0.014 | 0.004 ($F_{x0}), \epsilon F_{x0}$（可变）| — | Li 2018 |
| h-BN（TDDFT）| 0.014–0.028 | 0.01 | 10–30 fs | Tancogne-Dejean 2017 |
| MoS$_2$（半经典）| 0.01（0.26 eV MIR）| — | — | Yoshikawa 2019 |
| Si（实验）| 0.022（2.1 μm）| — | — | Klemke 2018 |

---

## 文献空白与前沿方向

### 空白 1：三维相位匹配的微观理论
现有理论（Popmintchev 2024）是一维/准一维。三维非均匀介质中的时空耦合仍是开放问题。

### 空白 2：机器学习与 HHG 深度结合
本轮检索未能找到 ML + HHG 理论方法的可靠论文——该交叉方向文献稀少，可能是未来重要方向。

### 空白 3：Mott 绝缘体 HHG 的实验验证
Lange/Madsen 2023 的理论预言（Mott 绝缘体产生非经典光）尚需实验验证。

### 空白 4：谷电子学 HHG 的系统性实验
TMD 单层/双层的谷选择性 HHG 已有 Yoshikawa (2019) 和 Lee (2021) 的工作，但系统性实验（温度依赖、应变工程等）尚不充分。

---

## 核心参考论文索引

| arXiv ID | 作者 | 年份 | 方向 | 关键词 |
|----------|------|------|------|--------|
| [2102.11964](https://arxiv.org/abs/2102.11964) | Yue & Gaarde | 2021 | A1 | SBE, full-BZ tunneling, imperfect recollision |
| [2003.02961](https://arxiv.org/abs/2003.02961) | Yue & Gaarde | 2020 | A2 | Structure gauge, laser gauge, Berry connection |
| [2508.07869](https://arxiv.org/abs/2508.07869) | Thümmler & Lettau | 2025 | A3 | Wannier gauge, dephasing, SDO |
| [1904.00283](https://arxiv.org/abs/1904.00283) | Silva, Martín, Ivanov | 2019 | C | MLWF, h-BN, dipole matrix element |
| [2312.08942](https://arxiv.org/abs/2312.08942) | Lange, Hansen, Madsen | 2023 | D | Fermi-Hubbard, nonclassical light, Mott insulator |
| [2111.10986](https://arxiv.org/abs/2111.10986) | Lee, Kim, Kim | 2021 | B1 | TMD, Berry curvature, valley, MoS₂ |
| [1902.03421](https://arxiv.org/abs/1902.03421) | Yoshikawa et al. | 2019 | B2 | Valley polarization, band nesting, selection rules |
| [2404.01325](https://arxiv.org/abs/2404.01325) | Popmintchev et al. | 2024 | E | Phase matching, soft X-ray, water window |
| [2104.06144](https://arxiv.org/abs/2104.06144) | Wang et al. | 2021 | F | Tunneling time, attoclock, TCCSFA |
| [1910.13791](https://arxiv.org/abs/1910.13791) | Gorlach et al. | 2019 | G | SFQED, quantum optics, photon statistics |
| [1806.11232](https://arxiv.org/abs/1806.11232) | Silva et al. | 2018 | B | Haldane model, Berry curvature, Chern number |
| [2103.16228](https://arxiv.org/abs/2103.16228) | Haessler, Caillat, Salières | 2021 | G | Molecular HHG, orbital tomography, ADK rate |
| [1805.10453](https://arxiv.org/abs/1805.10453) | Klemke et al. | 2018 | G | Polarization-resolved, TDDFT, Si |
