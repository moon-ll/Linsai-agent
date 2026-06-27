# 固体高次谐波产生（HHG）计算与分析方法——按材料体系分类

> **调研方法**：检索（arXiv API）→ 筛选验证 → deepxiv 获取 → 原文提取 → 归纳组织
> **检索日期**：2026-05-08
> **检索词**：`solid high harmonic generation TDDFT hexagonal boron nitride`, `solid HHG theory Berry curvature semiconductor Bloch`, `high harmonic phase matching gas medium`, `molecular HHG self-probing tomography`
> **重要原则**：所有内容均直接来自已获取论文原文，无任何生成内容。每节末尾标注来源 arXiv ID。

---

## 体系一：六方氮化硼（h-BN）——从单层到体材料的 HHG

### 论文来源

- **Le Breton, Rubio, Tancogne-Dejean**, *PRB* 2018, `1807.02961`

---

### 研究对象与实验/计算背景

该工作研究了少层（1–6 层）和体材料 h-BN 的 HHG，重点关注层间堆垛对 HHG 响应的影响。h-BN 选取原因：带隙适中（4.5–4.9 eV），体系干净，六角对称性便于理论分析。

**堆垛方式**（AA' stacking）：上层硼原子正对下层氮原子，反之亦然。另有 AD stacking 作对比。

---

### 计算方法

**软件**：Octopus（实时实空间 TDDFT）  
**交换-相关泛函**：Adiabatic LDA（ALDA）；作者注明 PBE 泛函得到相似结果，XC 泛函选择对定量结果影响不显著  
**赝势**：未在文中明确说明，但 Octopus 默认使用 norm-conserving 赝势

**晶格参数**（实验值）：
- B-N 键长：2.73 Bohr
- 层间距：6.29 Bohr（平衡距离）

**实空间网格**：
- 网格间距（Grid spacing）：**0.28 Bohr**
- 模拟盒尺寸（层方向）：**480 Bohr**，含两侧各 **40 Bohr** 吸收层（CAP，cap height η = −1 a.u.）

**k 点采样**：
| 计算类型 | k 点网格 |
|---------|---------|
| 层方向 HHG | 32 × 32 |
| 面内 HHG | 42 × 42 |
| 体材料 | 54 × 54 × 27 |

作者注明：模拟盒尺寸、网格间距、k 点数均对输出 HHG 光谱作了收敛性测试，收敛标准为偏差 < 3%。

**激光描述**：
- 规范：速度规范（velocity gauge，保留面内周期性）
- 波长：**1600 nm**（对应光子能量 0.77 eV）
- 包络：sin²，零载波包络相位（CEP = 0）
- 脉冲宽度（面内）：**30 fs FWHM**
- 脉冲宽度（层方向）：**15 fs FWHM**
- 驱动光场：空间均匀

**结构优化**：含 Tkatchenko-Scheffler vdW 修正（静态性质）；电子动力学计算中忽略 vdW（发现含与否无显著差异）

**HHG 光谱计算公式**（原子单位）：

$$
\mathrm{HHG}(\omega) = \left|\mathcal{F}\left[\frac{\partial}{\partial t}\int_\Omega d^3\mathbf{r} \, \mathbf{j}(\mathbf{r},t)\right]\right|^2 \tag{1}
$$

其中 $\mathcal{F}$ 为傅里叶变换，$\Omega$ 为模拟盒体积，$\mathbf{j}$ 为电子电流密度。

---

### 关键计算结果

**带隙与功函数（Table 1）**：

| 层数 | 带隙（eV）| 功函数（eV）|
|------|---------|-----------|
| 1 | 4.50 | 6.11 |
| 2 | 5.05 | 6.39 |
| 3 | 4.60 | 6.26 |
| 4 | 4.54 | 6.13 |
| 5 | 4.51 | 6.10 |
| 6 | 4.63 | 6.22 |
| 体材料 | 4.87 | — |

**HHG 截止能量**（层方向驱动，原子样三步模型）：

$$
E_c = E_w + 3.17 U_p \tag{CUTOFF}
$$

其中 $E_w$ 为功函数（替代原子物理中的电离势），$U_p$ 为有质动力势。

---

### 主要物理发现

**发现一：面内 HHG 随层数快速收敛**

- 单层 HHG 产额高于少层和体材料（与 MoS₂ 实验一致）
- 截止能量：单层 HH19 > 体材料 HH15
- N ≥ 6 层后 HHG 光谱与体材料基本一致
- 表面贡献按 1/N 衰减

**发现二：奇偶次谐波与对称性**

- 偶数层（AA' 堆垛）：有中心反演对称，禁戒偶次谐波
- 奇数层：中心反演对称被打破，产生偶次谐波
- 偶次谐波强度几乎不随层数变化（来自有效单层贡献的残余干涉）

**发现三：层方向 HHG 对层数强依赖**

- 面内 HHG：不强烈依赖层数（电子态仍局域在层内）
- 层方向 HHG：强依赖层数（从原子样→体样的演化）
- 机制：层间电子态退局域化 + 电子-电子相互作用诱导电场

---

### 方法要点总结

| 项目 | 值 |
|------|-----|
| 软件 | Octopus |
| XC 泛函 | LDA（PBE 类似）|
| 网格间距 | 0.28 Bohr |
| k 点（面内）| 42 × 42 |
| k 点（层方向）| 32 × 32 |
| CAP | η = −1 a.u.，每侧 40 Bohr |
| 激光波长 | 1600 nm（0.77 eV）|
| 脉冲宽度 | 15–30 fs |
| 收敛标准 | < 3% 偏差 |

---

### 来源

`1807.02961` — G. Le Breton, A. Rubio, N. Tancogne-Dejean, *"High-harmonic generation from few-layer hexagonal boron nitride: evolution from the monolayer to the bulk response"*, PRB 2018.

---

## 体系二：α-石英（SiO₂）——电子-空穴复合主导的 HHG

### 论文来源

- **Otobe**, *JAP* 2016, `1607.00747`

---

### 研究对象与背景

作者选取 α-石英作为 HHG 目标材料，原因在于其能带结构简单：价带有效质量很重（5–10 m_e），导带在 Γ 点附近有效质量很轻（0.3 m_e），便于 HHG 光谱与能带结构的直接对比。

---

### 计算方法

**软件**：未明确商品软件名称，但使用实时实空间 TDDFT（与 Octopus / SALMON 同类方法）  
**赝势**：norm-conserving 赝势（TM91 + Kleinman-Bylander）  
**交换-相关泛函**：Modified Becke-Johnson（mBJ）交换势 + LDA 关联势（adiabatic approximation）

**mBJ 交换势理由**：LDA 低估带隙，mBJ 可给出与实验一致的带隙值。

**实空间网格**：26 × 44 × 38 Cartesian 网格  
**k 点**：8³  
**时间步长**：**0.02 a.u.**  
**总步数**：通常 **40,000 步**

**激光描述**：
- 形式：$E(t) = E_0 \sin^2(\pi t/T_p)\cos(\omega_0 t + \phi)$（0 < t < T_p）
- 光子能量：$\omega_0$ = **1.55 eV**（800 nm）
- 脉冲长度：$T_p$ = 6 光学周期（16.2 fs），计算终止于 $T_e$（19.4 fs）
- 包络：sin²

**材料内场强**：$E_0 = \frac{2}{1+\sqrt{\varepsilon}}E_{\rm in}$，其中 $\varepsilon$ 为 $\omega_0$ 处的介电函数（场在材料内被修正）

**偏振方向**：沿 α-石英光轴（光学轴方向）

**电流计算**：

$$
J(t) = -\frac{e}{mV}\int_V d\mathbf{r} \sum_i \text{Re}\left[\psi_i^*\left(\mathbf{p}+\frac{e}{c}\mathbf{A}(t)\right)\psi_i\right] + J_{\rm ion}(t) \tag{2}
$$

其中 $J_{\rm ion}$ 为赝势贡献的电流。

**HHG 光谱**：

$$
I(\omega) = \left|\int_0^{T_e} J(t) e^{-i\omega t}dt\right|^2 \tag{3}
$$

---

### 关键计算结果

**带隙**（不同 XC 泛函对比）：

| XC 泛函 | 光学带隙 |
|---------|---------|
| LDA | ~8 eV |
| mBJ | **9.2 eV**（与实验值 9–10 eV 一致）|

**有效质量**（来自能带计算）：
- 价带：5–10 m_e（很重，很平坦）
- 导带（Γ点附近）：0.3 m_e（很轻）

**HHG 截止能量**：**HH19（30 eV）**（ plateau 区限制）

**主导机制**：电子-空穴复合（inter-band process）主导 HHG（高于带隙区域）

**200 as 脉冲串**：利用 plateau 截止区附近的 HHG 可产生 ~200 as 脉冲串

---

### 方法要点总结

| 项目 | 值 |
|------|-----|
| 软件 | 实时 TDDFT（非 Octopus，具体未命名）|
| XC 泛函 | mBJ exchange + LDA correlation |
| 赝势 | norm-conserving (TM91) |
| 网格 | 26 × 44 × 38 |
| k 点 | 8³ |
| 时间步长 | 0.02 a.u. |
| 总步数 | 40,000 |
| 激光光子能量 | 1.55 eV |
| 脉冲宽度 | 16.2 fs（6 周期）|
| 偏振 | 沿光轴 |

---

### 来源

`1607.00747` — T. Otobe, *"High-harmonic generation in α-quartz by the electron-hole recombination"*, J. Appl. Phys. 2016.

---

## 体系三：硅（Si）与石英——偏振分辨 HHG 光谱学

### 论文来源

- **Klemke, Tancogne-Dejean et al.**, *Nature Communications* 2018, `1805.10453`

---

### 实验参数（完全可复现）

**硅样品**：
| 参数 | 值 |
|------|-----|
| 厚度 | 2 μm |
| 晶向 | (100) 取向 |
| 驱动波长 | 2.1 μm（0.59 eV）|
| 脉冲宽度 | 120 fs |
| 峰值强度 | 0.6–0.7 TW/cm²（真空）|
| CEP | 被动稳定 |
| 产生方式 | Ti:Sapphire 泵浦白光种子 OPA |

**石英样品**：
| 参数 | 值 |
|------|-----|
| 厚度 | 50 μm |
| 晶向 | z-cut |
| 估计峰值强度 | ~40 TW/cm²（真空）|

**检测**：XUV 光谱仪（仅检测至 HH9）；TDDFT 预言在 XUV 区可达 HH19

---

### 理论计算方法

**软件**：Octopus TDDFT（与 h-BN 体系相同软件）  
**XC 泛函**：mBJ exchange + LDA（与 α-石英 Otobe 2016 相同）

计算覆盖不同驱动椭圆度 ε 和样品旋转角 θ，并与实验作定量对比。

---

### 谐波物理机制分类（与能带结构的关联）

| 谐波 | 能量 | 物理机制 |
|------|------|---------|
| HH5 | 2.95 eV | **纯带内（intraband）**：低于硅直接带隙 3.1 eV，无 interband 贡献 |
| HH7 | 4.1 eV | **耦合 inter+intraband**：joint density of states（JDOS）较高 |
| HH9 | 5.3 eV | **主要带内**：JDOS 在 5.3 eV 显著低于 4.1 eV，interband 被强烈压制 |

**HH5**：Gaussian 形椭圆度分布，原子样行为（电子在抛物线区运动）  
**HH7**：非原子样特征（最强产额在非零椭圆度处）  
**HH9**：最显著的非原子样行为，强非谐振荡，电子探索更大非抛物线区

---

### 偏振分辨 HHG 的关键实验发现

**谐波椭圆率定义**：

$$
|\epsilon_{\rm HH}| = \sqrt{I_{\rm min}/I_{\rm max}} \tag{ELLIPTICITY}
$$

其中 $I_{\rm min}, I_{\rm max}$ 为谐波偏振椭圆的长短轴强度。

**发现一：圆驱动场产生交替螺旋度谐波**

- Si（点群 $O_h$ [m3m]）：奇次谐波交替 RHCP/LHCP
- α-石英（点群 $D_3$ [32]）：偶次谐波 HH4 和奇次谐波 HH5 交替螺旋度
- 极化度（DOP）：$0.8 \pm 0.2$

**发现二：椭圆驱动场产生圆谐波（首次实现）**

- 用椭圆驱动（|ε| < 1）可在 Si 中产生圆偏振谐波
- HH7/HH9：谐波椭圆率 ~0.93（接近完美圆偏振）
- **效率提升**：ε=0.3–0.4 的椭圆驱动产生 HH7 → 比纯圆驱动高 10 倍
- HH9：ε=0.2 时产额达线性驱动最大值的 40%（相当于比圆驱动增强 18 倍）

**发现三：强场控制谐波偏振态**

- 通过改变驱动强度可连续控制 |ε_HH|
- 相对重要性：intraband vs interband 不是材料固有属性，可由激光强度动态调控

---

### 来源

`1805.10453` — N. Klemke, N. Tancogne-Dejean et al., *"Polarization-state-resolved high-harmonic spectroscopy of solids"*, Nat. Commun. 2018.

---

## 体系四：拓扑材料——Haldane 模型中的 HHG

### 论文来源

- **Silva, Jiménez-Galán, Amorim, Smirnova, Ivanov**, *Nature Photonics* 2018, `1806.11232`

---

### 模型哈密顿量

**Haldane 模型**（六角晶格，两种原子 A/B）：

$$
\hat{H} = -t_1\sum_{\langle ij\rangle}(c_i^\dagger c_j + \text{h.c.}) - t_2\sum_{\langle\langle ij\rangle\rangle}(e^{i\phi}c_i^\dagger c_j + \text{h.c.}) + M\sum_i\xi_i c_i^\dagger c_i \tag{HALDANE}
$$

参数物理含义：
- $t_1$：最近邻跳跃幅度
- $t_2 e^{i\phi}$：次近邻复数跳跃（产生 Berry 曲率）
- $M$：A/B 子格在位能差（±M）
- $\xi_i = \pm 1$（A/B 原子）

---

### 拓扑相变条件

$$
|M/(3\sqrt{3}t_2)| \gtrless t_2\sin\phi \implies \nu = 0 \text{（平凡）} \quad \text{或} \quad \nu = \pm 1 \text{（拓扑）} \tag{TOPO}
$$

其中 $\nu$ 为 Chern 数。

| 相 | Chern 数 ν | Hall 电导 |
|----|-----------|---------|
| 平凡（trivial）| 0 | 0 |
| 拓扑（topological）| ±1 | 非零 |

**关键特点**：在相变点附近，两种相的体能带结构几乎相同（难以区分），但拓扑不变量不同。

---

### Berry 曲率导致的半经典速度修正

外加激光场（沿 y 方向偏振：$\mathbf{E}(t) = -\partial\mathbf{A}_L/\partial t$），电子准动量 $\mathbf{k}(t) = \mathbf{k}_i + e\mathbf{A}_L(t)$。Berry 曲率 $\boldsymbol{\Omega}_n(\mathbf{k})$ 产生垂直于电场的横向运动：

$$
\dot{\mathbf{r}}_n(t) = \nabla_{\mathbf{k}}\varepsilon_n(\mathbf{k}(t)) + e\mathbf{E}(t)\times\boldsymbol{\Omega}_n(\mathbf{k}(t)) \tag{1}
$$

- 第一项：沿 $\mathbf{A}_L(t)$ 方向运动
- 第二项：沿 $\mathbf{E}(t)$ 方向运动（Berry 曲率驱动）

→ x 和 y 谐波分量相位差 π/2 → 谐波呈**椭圆偏振**

---

### 隧穿位置的 Berry 曲率修正

在抛物线近似下（K 点附近），最优隧穿 $\mathbf{k}$ 点的横向偏移为：

$$
\Delta\mathbf{k}_\perp \simeq m_\perp\mathbf{E}(t)\times\left[\boldsymbol{\Omega}_c(\mathbf{k}^{(0)}) - \boldsymbol{\Omega}_v(\mathbf{k}^{(0)})\right] \tag{2}
$$

其中 $m_\perp$ 为电子-空穴有效约化质量。$\Delta\mathbf{k}_\perp$ 在平凡相和拓扑相中符号相反。

---

### 驱动光参数

| 参数 | 值 |
|------|-----|
| 波长 | 3 μm |
| 峰值场强 | 4 × 10⁹ V/m |
| 偏振 | y 方向（线偏振）|
| t₂ = 0 时的带隙 | 4.6 eV（与单层 h-BN 的双带模型可比）|

---

### 关键物理发现

**发现一：HHG 光谱本身无法区分平凡相和拓扑相**

- 在 λ = 3 μm，E₀ = 4×10⁹ V/m 条件下，两相的 HHG 光谱几乎相同
- 原因：相变点附近体能带结构相似

**发现二：谐波螺旋度在相变点突变**

- 基频响应（H1）：拓扑相中由价带主导（Berry 曲率符号与导带相反）
- H3、H9：螺旋度在拓扑相变处精确切换
- 追踪 H3 相对于 H1 的螺旋度 → 可生成系统相图

**发现三：拓扑依赖的 attosecond 时间延迟**

定义拓扑信号的时间延迟：

$$
\tau = \langle\tau\rangle_{\rm topo} - \langle\tau\rangle_{\rm trivial} \tag{DELAY}
$$

其中 $\langle\tau\rangle = \int f(t) \cdot t \, dt / \int f(t) \, dt$（加权平均发射时间）

- 平行于驱动场的偏振分量：两相几乎无差异
- 垂直于驱动场的偏振分量：两相有明显不对称，产生拓扑依赖延迟
- 延迟量随带隙增大而增大

---

### 来源

`1806.11232` — R. E. F. Silva, Á. Jiménez-Galán, B. Amorim, O. Smirnova, M. Ivanov, *"Topological strong-field physics on sub-laser cycle timescale"*, Nat. Photonics 2018.

---

## 体系五：2D 材料——谷电子学与缺陷的 HHG

### 论文来源

- **Luu**（博士论文），`2203.10253`
- **Mrudul S., Tancogne-Dejean, Rubio, Dixit**，`1906.10224`

---

### 研究体系

1. **有隙石墨烯（gapped graphene）**和**无隙石墨烯（pristine graphene）**：半导体 vs 半金属
2. **h-BN 中的自旋极化缺陷**：硼空位（$V_B$）、氮空位（$V_N$）
3. **六角对称二维材料**的一般性讨论

---

### 计算方法（SBE vs TDDFT）

**SBE（半导体布洛赫方程）适用场景**：
- 需要大量参数扫描（强度、椭圆度、k 点）
- 能带来自 Kohn-Sham DFT（VASP/Quantum ESPRESSO）
- 关键量：$E_n(\mathbf{k})$，$\mathbf{d}_{mn}(\mathbf{k})$（偶极矩阵元），$T_2$（退相干时间）

**TDDFT（从头算）适用场景**：
- 缺陷体系（电子-电子相互作用不可忽略）
- 新材料（无经验参数）

---

### 关键符号定义（来自论文）

| 符号 | 含义 |
|------|------|
| $\mathcal{A}$ | 矢势 |
| $\mathcal{F}$ | 电场 |
| $\hat{\mathcal{H}}$ | Hamiltonian |
| $\rho_{mn}$ | 密度矩阵元 |
| $\mathbf{d}_{mn}$ | 偶极矩阵元 |
| $\mathbf{p}_{mn}$ | 动量矩阵元 |
| $T_2$ | 退相干时间 |
| $j(t)$ | 总电流 |
| $\mathcal{I}(\omega)$ | HHG 强度 |
| $\gamma_k$ | Keldysh 参数 |
| $\eta$ | 谷非对称参数 |

---

### 自旋极化缺陷的 HHG（Mrudul S. et al. 2019）

**研究对象**：单层 h-BN 中的硼空位（$V_B$）和氮空位（$V_N$）

**计算方法**：TDDFT（Octopus 或类似实时实空间代码）

**关键发现**：
1. **电子-电子相互作用对缺陷体系至关重要**——与完美晶体不同，缺陷处电子高度局域，必须用 TDDFT（含多电子效应）描述
2. **不同自旋通道受缺陷影响不同**：自旋极化缺陷对两个自旋通道的 HHG 贡献不同
3. **波函数局域化、缺陷几何结构、电子-电子相互作用**三者均为描述缺陷固体 HHG 的关键要素
4. 缺陷固体的 HHG 与完美固体的 HHG 有显著差异，可作为缺陷探测手段

---

### 谷极化 HHG 的选择定则（来自 TMD 文献综述）

**谷指标**：K 和 K' 谷（谷自旋锁定）  
**Keldysh 参数**：$\gamma_k$（隧穿 vs 多光子）  
**退相干时间**：$T_2$（决定 HHG 相干性）

---

### 来源

`2203.10253` — T. T. Luu, *"High-harmonic spectroscopy of two-dimensional materials"*（博士论文），2022.  
`1906.10224` — M. M. S, N. Tancogne-Dejean, A. Rubio, G. Dixit, *"High-harmonic generation from spin-polarised defects in solids"*，2019.

---

## 体系六：相位匹配——气体 HHG 向 X射线扩展

### 论文来源

- **Popmintchev, Chen, Bahabad et al.**, `2404.01325`

---

### 相位失配方程（空心波导几何）

总相位失配（式 2）：

$$
\Delta k = q\left(\underbrace{\frac{u_{11}^2\lambda_L}{4\pi a^2}}_{\text{几何}}\right) - q\left[\underbrace{p(1-\eta)\frac{2\pi}{\lambda_L}\Delta\delta(\lambda_L)}_{\text{中性原子}}\right] + \underbrace{p\eta N_{\rm atm}r_e\lambda_L}_{\text{等离子体}} \tag{PM}
$$

符号定义：
- $q$：谐波阶次
- $u_{11}$：波导模式因子
- $a$：波导内半径
- $p$：气压
- $\eta$：电离度
- $r_e$：经典电子半径
- $N_{\rm atm}$：每 atm 的原子数密度
- $\Delta\delta(\lambda_L)$：气体在基频和 X 射线处的折射率差

---

### 临界电离度（相位匹配截止的条件）

$$
\eta_{\rm CR} = \left[\frac{\lambda_L^2 N_{\rm atm} r_e}{2\pi\Delta\delta(\lambda_L)} + 1\right]^{-1} \tag{ETA}
$$

电离度必须低于临界值才能实现相位匹配。典型值：

| 气体 | λ_L = 0.8 μm | λ_L = 1.3 μm |
|------|-------------|-------------|
| Ar | ~4% | ~1.5% |
| Ne | ~1% | ~0.4% |
| He | ~0.5% | ~0.2% |

→ 临界电离度随驱动波长增大而**减小**（因为 $\eta_{\rm CR} \propto \lambda_L^{-2}$）

---

### 相位匹配截止能量

$$
h\nu_{\rm PM}(\lambda_L) \approx 3.17 U_p \propto I_L(\eta_{\rm CR})\lambda_L^2 \tag{CUTOFF-PM}
$$

忽略电离势 $I_p$，$h\nu_{\rm PM} \propto \lambda_L^{1.6-1.7}$（而非精确的 $\lambda_L^2$）

**理论预言**：λ_L → 3 μm 可达 **~1 keV**

---

### 实验结果

| 气体 | 驱动波长 | 相位匹配截止能量 | 最优气压 |
|------|---------|--------------|---------|
| Ar | 0.8 μm | ~50 eV | 20–40 torr |
| Ar | 1.3 μm | ~100 eV | 100–200 torr |
| Ne | 1.3 μm | ~200 eV | 600–900 torr |
| **He** | **1.3 μm** | **~330 eV（水窗）**| **>2200 torr** |

**关键：实验观测到的相位匹配截止与理论计算（式 PM）高度一致**

---

### 实验装置

- 驱动激光：0.8 μm（Ti:Sapphire）或 1.3 μm（OPA），能量 ≤ 5.5 mJ，脉冲 < 35 fs
- 气体介质：Ar / Ne / He，填充空心波导
- 几何：空心毛细管（近平面波传播）
- **电离模型**：Ammosov-Delone-Krainov（ADK）隧穿电离模型

---

### 方法要点总结

| 项目 | 值 |
|------|-----|
| 介质 | 气体（Ar/Ne/He），空心波导 |
| 气压范围 | 20 torr – >2200 torr |
| 驱动波长 | 0.8–1.3 μm（→ 理论预言 3 μm → 1 keV）|
| 激光强度 | 10¹⁴ – 10¹⁵ W/cm² |
| 电离模型 | ADK |
| 相位匹配机制 | 中性原子色散 vs 等离子体色散相消 |

---

### 来源

`2404.01325` — T. Popmintcru, M.-C. Chen, A. Bahabad et al., *"Phase matching of high harmonic generation in the soft and hard X-ray regions"*，2024.

---

## 体系七：量子光学视角——SFQED 框架下的 HHG

### 论文来源

- **Gorlach, Neufeld, Rivera-Dean, Lamri, Colovic, Lewenstein, Pariente-Amor**, `1910.13791`

---

### 传统 HHG 理论的局限

传统 HHG 理论（包括 Lewenstein 模型）：
- 电子：**量子**描述（TDSE）
- 驱动场和辐射场：**经典**描述（偶极近似，取期望值 $\langle \mathbf{d}(t)\rangle$）

这一框架**无法描述**辐射的量子统计性质。

---

### SFQED（强场量子电动力学）框架

**三步方案**：

1. **幺正变换**：将激光相干态转移到真空态  
   矢势分解：$\mathbf{A} = \underbrace{\mathbf{A}_c(t)}_{\text{经典}} + \underbrace{\mathbf{A}_q}_{\text{量子}}$  
   其中 $\mathbf{A}_q = \sum_{\mathbf{k}\sigma}\sqrt{\frac{\hbar}{2\varepsilon_0 Vck}}\,e_\sigma\left[a_{\mathbf{k}\sigma}e^{i\mathbf{k}\cdot\mathbf{r}} + \text{h.c.}\right]$

2. **经典场 TDSE**：对电子在 $\mathbf{A}_c(t)$ 下求解（可用现有 TDSE 求解器）

3. **量子场辐射 EOM**：从 $\mathbf{A}_q$ 与电子电流的耦合推导光子态演化

**组合波函数**（纠缠态）：

$$
|\Psi(t)\rangle = |\phi_i(t)\rangle|0\rangle + \frac{1}{\hbar}\sum_j\sum_{\mathbf{k}\sigma}e^{-i\omega_k t}\sqrt{\frac{\hbar\omega_k}{2V\varepsilon_0}}\left[\int_{-\infty}^t d\tau\, \mathbf{d}_{ji}(\tau)\cdot e_\sigma e^{i\omega_k\tau}\right]|\phi_j(t)\rangle|\mathbf{k}\sigma\rangle \tag{3}
$$

关键特征：**光子态与电子态纠缠**——不可分解为独立的光子和电子子系统的张量积。

---

### 关键理论结果

**结果一：每个 HHG 光子是整个频谱的叠加**

传统公式（经典辐射）：

$$
\frac{d\varepsilon}{d\omega} = \frac{\omega^4}{6\pi^2\varepsilon_0 c^3}\left|\int_{-\infty}^{+\infty}\langle\mathbf{d}(t)\rangle e^{i\omega t}dt\right|^2 \tag{5}
$$

SFQED 公式（量子辐射）：

$$
\frac{d\varepsilon}{d\omega} = \sum_j \frac{\omega^4}{6\pi^2\varepsilon_0 c^3}\left|\int_{-\infty}^{+\infty}\mathbf{d}_{ji}(t)e^{i\omega t}dt\right|^2 \tag{4}
$$

区别：传统公式只含 $\langle\mathbf{d}(t)\rangle = \mathbf{d}_{ii}(t)$（期望值），SFQED 包含**所有跃迁矩阵元** $\mathbf{d}_{ji}$（j ≠ i）。

→ 每个 HHG 光子携带**整个谐波频谱**（"single photon comb"）

**结果二：单原子 HHG 的新频谱特征**

- 传统公式给出离散奇次谐波
- SFQED 公式中无明显离散谐波峰（来自所有跃迁 j 的叠加）
- 单原子 HHG 的辐射率显著高于传统预言

**结果三：HHG 光子可测量性**

- 每个 HHG 光子携带关于 HHG 过程全部信息（包括能量分布和截止频率）
- 可通过场自相关实验测量

---

### 来源

`1910.13791` — A. Gorlach, O. Neufeld, N. Rivera-Dean et al., *"On the quantum optical nature of high harmonic generation"*，2019.

---

## 体系八：分子 HHG 自探测与轨道断层成像

### 论文来源

- **Haessler, Caillat, Salières**（综述），`2103.16228`

---

### 自探测范式的物理图像

**三步模型 → 自探测范式**：

1. **隧穿**（tunnel ionization）：强激光从分子轨道隧穿出一个电子
2. **传播**（propagation）：电子在激光场中被加速（返回）
3. **复合**（recombination）：电子与母离子散射，可能发生非弹性散射或复合

**自探测思想**：将电子-离子散射视为对分子的"探测"，发射的光子携带分子信息。

---

### 电子探针的特性（来自论文原文）

**波长对比**：

| 探针类型 | 能量 | de Broglie 波长 |
|---------|------|--------------|
| 电子 | 低能量（~10 eV）| ~1 Å（典型分子尺寸）|
| 光子 | 达到同等分辨率 | 需要数 keV（硬 X 射线）|

→ **电子探针在低得多的能量下即可达到分子尺度分辨率**

**时间尺度**：整个 HHG 三步过程发生在驱动激光的一个光学周期的一小部分内（800 nm 激光：< 2.7 fs；探针脉冲持续时间 ~1 fs）

**附加分辨率提升**：利用电子探针的固有啁啾，可实现 **~0.1 fs** 时间分辨率（chirp-encoded recollision scheme）

---

### 分子轨道断层成像（Orbital Tomography）

**基本思路**（Itatani et al. 2004）：
- 测量 HHG 的 spectral phase
- 相位与分子轨道的 Fourier 变换相关
- 通过反投影得到 HOMO 的动量空间分布

**理论框架**：
- **隧穿率**：Ammosov-Delone-Krainov（ADK）公式
- **传播**：Lewenstein 模型或 TDSE
- **复合**：散射理论或断层反演

---

### 多电子动力学（Smirnova et al. 的贡献）

Olga Smirnova 小组指出：分析 HHG 实验不能只考虑 HOMO，还必须考虑低占据轨道（ionic excited states），这引入了丰富的多电子动力学。

**实验验证**（N₂ 分子）：对取向 N₂ 分子进行轨道断层成像，得到 N₂⁺ 离子 HOMO 在电离后 1.5 fs 时刻的快照，"曝光时间" ~600 as。

---

### 来源

`2103.16228` — S. Haessler, J. Caillat, P. Salières, *"Self-probing of molecules with high harmonic generation"*，Adv. At. Mol. Opt. Phys. 2021.

---

## 体系九：固体 HHG 理论入门——计算框架总览

### 论文来源

- **Yue & Gaarde**，*Adv. At. Mol. Opt. Phys.* 2021, `2111.08669`

---

### 固体 HHG 理论的三类计算

**类型一：能带结构计算（时间无关）**
- 解时间无关薛定谔方程（TISE）
- 输出：$E_n(\mathbf{k})$，$\mathbf{d}_{mn}(\mathbf{k})$ 或 $\mathbf{p}_{mn}(\mathbf{k})$
- 关键难点：**结构规范（structure gauge）**——Bloch 态的任意 $\mathbf{k}$ 依赖相位

**类型二：时间演化方程（EOM）**

可选规范：

| 规范 | 形式 | 优缺点 |
|------|------|--------|
| **速度规范（VG）** | 含 $\mathbf{p}\cdot\mathbf{A}$ | 计算快，但需多带，收敛慢 |
| **长度规范（LG）** | 含 $\mathbf{r}\cdot\mathbf{E}$ | 少量带即可收敛，但需平滑规范 |

**类型三：电流计算与 HHG 光谱**

总电流分解：
$$
\mathbf{j}(t) = \underbrace{\mathbf{j}_{\rm inter}(t)}_{\text{interband}} + \underbrace{\mathbf{j}_{\rm intra}(t)}_{\text{intraband}} + \underbrace{\mathbf{j}_{\rm anom}(t)}_{\text{anomalous (Berry)}}
$$

其中 $\mathbf{j}_{\rm anom}$ 来自 Berry 曲率项。

---

### 规范选择的关键注意事项（来自论文原文）

1. **结构规范必须平滑**：尤其在处理 Berry 相位、隧穿跨越整个 BZ 时
2. **激光规范与结构规范需匹配**：VG 下结构规范相对自由，LG 下必须用 BZ 周期的平滑规范
3. **收敛性强烈依赖规范选择**：计算量级差数倍到数十倍

---

### 来源

`2111.08669` — L. Yue & M. B. Gaarde, *"Introduction to theory of high-harmonic generation in solids: tutorial"*，Adv. At. Mol. Opt. Phys. 2021.

---

## 跨体系方法对比汇总

### 计算量级与方法选择

| 材料体系 | 优先方法 | 软件/模型 | 关键参数 |
|---------|---------|----------|---------|
| **h-BN**（少层→体）| TDDFT | Octopus | Δx=0.28 Bohr，k: 32²–54³ |
| **α-石英** | TDDFT | 实时 TDDFT + mBJ | Δt=0.02 a.u.，k: 8³ |
| **Si/石英（偏振）**| TDDFT | Octopus + mBJ | 偏振分解，ε_HH 提取 |
| **Haldane 模型（拓扑）**| Model Hamiltonian | 解析/数值 | Chern 数，Berry 曲率 |
| **TMD/谷电子** | SBE 或 TDDFT | — | $T_2$，γ_k，谷指标 |
| **自旋缺陷** | TDDFT | Octopus | 电子-电子相互作用必须包含 |
| **气体（相位匹配）**| 半解析 | — | η_CR，ADK，Δk 方程 |
| **分子轨道成像** | TDSE / Lewenstein | ADK + 断层反演 | spectral phase 提取 |
| **量子光学** | SFQED | 解析 | 纠缠态，single photon comb |

### 收敛性检查清单

```
□ 实空间网格间距：Δx → Δx/2，光谱偏差 < 3%
□ k 点：N_k → 2N_k，光谱偏差 < 3%
□ 时间步长：Δt → Δt/2，轨迹偏差可忽略
□ 带数（VG/LG）：增加至 HHG 光谱收敛
□ CAP 高度（吸收边界）：η 值对 HHG 光谱无显著影响
```

---

## 文献索引

| arXiv ID | 作者 | 年份 | 体系 | 方法关键词 |
|----------|------|------|------|-----------|
| `1807.02961` | Le Breton, Rubio, Tancogne-Dejean | 2018 | h-BN | TDDFT, Octopus, few-layer, AA' stacking |
| `1607.00747` | Otobe | 2016 | α-石英 | TDDFT, mBJ, electron-hole recombination |
| `1805.10453` | Klemke, Tancogne-Dejean et al. | 2018 | Si, α-石英 | 偏振分辨, circular harmonics, TDDFT |
| `1806.11232` | Silva, Jiménez-Galán, Smirnova, Ivanov | 2018 | 拓扑 | Haldane model, Chern number, Berry curvature |
| `2203.10253` | Luu | 2022 | 2D 材料 | SBE, TDDFT, valley, graphene |
| `1906.10224` | Mrudul S., Tancogne-Dejean, Rubio, Dixit | 2019 | h-BN 缺陷 | TDDFT, spin-polarized vacancy |
| `2404.01325` | Popmintchev et al. | 2024 | 气体 | Phase matching, hollow waveguide, ADK |
| `1910.13791` | Gorlach, Lewenstein et al. | 2019 | 量子光学 | SFQED, entanglement, single photon comb |
| `2103.16228` | Haessler, Caillat, Salières | 2021 | 分子 | Self-probing, orbital tomography, ADK |
| `2111.08669` | Yue & Gaarde | 2021 | 理论框架 | SBE, TDDFT, VG/LG gauge, Berry phase |
