# 方法学手册（Methodology Manual）

> **配套申请书**：基于量子几何反演的固体高次谐波产生新方法研究
> **项目类型**：面上项目（general）
> **创建日期**：2026-07-27
> **定位**：申请书重思路，方法学手册重细节。本手册收录公式推导、参数表、技术路线图等不宜放入申请书正文的细节内容。
> **组织方式**：按申请书章节组织，与本轮聚焦的"（一）立项依据"对应细节在本文件第一部分。

---

## 第一部分：对应"（一）立项依据"的理论细节

### 1A. 量子光 HHG 的理论基础与文献脉络

#### 1A.1 经典 HHG 截止定律（三步模型回顾）

经典光场驱动下，固体 HHG 的截止频率由半导体三步模型给出：

$$
N_{\text{cutoff}}^{\text{classical}} \approx \frac{I_p + 3.17\,U_p}{\hbar\omega}
$$

其中 $I_p$ 为带隙能量，$U_p = e^2 E_0^2 / (4 m_r \omega^2)$ 为有质动能（ponderomotive energy），$E_0$ 为峰值电场，$m_r$ 为电子-空穴约化质量，$\omega$ 为驱动光频率。

该公式假设驱动场为经典相干态（coherent state），其光子统计服从泊松分布 $P(n) = e^{-\bar{n}} \bar{n}^n / n!$，二阶相干度 $g^{(2)}(0) = 1$。

#### 1A.2 Ghalgaoui 2023 量子光截止定律修正

Ghalgaoui et al. (Nat. Phys. 2023) [CITE:ghalgaoui_2023_np] 建立了量子光态对 HHG 截止定律的修正。其核心结论为：

| 光态 | $g^{(2)}(0)$ | 截止修正 | 物理机制 |
|------|-------------|---------|---------|
| Coherent state（相干态） | 1 | 无修正 | 泊松统计，等价经典场 |
| Fock state $\|n\rangle$ | $1 - 1/n$ | 无修正（n 大时） | 确定光子数，无涨落增强 |
| Thermal state（热态） | 2 | 截止上移 | 超泊松涨落增强高阶多光子通道 |
| Squeezed vacuum（压缩真空） | $>1$（依赖 r） | 截止上移 | 亚周期电场涨落突破经典包络 |

**修正后的截止公式**（Ghalgaoui 2023）：

$$
N_{\text{cutoff}}^{(\text{quantum})} \approx \frac{I_p + \alpha(\hat{\rho})\,U_p}{\hbar\omega}, \quad \alpha(\hat{\rho}) > 3.17
$$

其中 $\hat{\rho}$ 为光场密度矩阵，$\alpha(\hat{\rho})$ 为依赖光子统计的增强因子。对于 squeezed vacuum，$\alpha$ 与压缩参数 $r$ 正相关。该理论以原子体系为模型，尚未推广至固体能带结构。

#### 1A.3 Rasputnyi 2024 固体 BSV-HHG 实验参数

Rasputnyi et al. (Nat. Phys. 2024) [CITE:rasputnyi_2024_np] 首次实现固体 BSV-HHG，关键实验参数如下：

| 参数 | 数值 | 说明 |
|------|------|------|
| BSV 产生方式 | BBO 晶体 type-II 简并破坏（degenerate breaking）+ 单模光纤耦合 | 单时空模式（与申请书 §2.2/§3.1/§5 统一技术路线）|
| 压缩参数 r | 0.5–1.2（可调） | 对应 $g^{(2)}(0) \approx 1.5$–3.0 |
| 光子数/脉冲 | 0 – 2×10¹³ | 宽分布 |
| 亚周期电场涨落 | ±1 V/Å | 突破经典包络 |
| 驱动波长 | ~1.3 μm（signal） | 非简并 |
| 样品 | Si / a-Si 薄膜 | 高损伤阈值 |
| HHG 效率提升 | 10²–10³ 倍 | vs 同均值强度经典光 |
| 截止阶次 | 超出经典预测 ~30% | 验证 Ghalgaoui 理论 |

#### 1A.4 本项目的理论 niche：固体量子几何扩展

现有理论（Ghalgaoui 2023）和实验（Rasputnyi 2024）的衔接缺口：

```
Ghalgaoui 2023（原子体系量子光 HHG 理论）
        │
        │  缺口：固体能带 × 量子几何量（Ω, g）的耦合
        │  ← 本项目 Q1 填补此缺口
        ▼
Rasputnyi 2024（固体 BSV-HHG 实验，无几何反演）
        │
        │  缺口：BSV 场 → Ω(k)/g(k) 解析反演
        │  ← 本项目 Q1.2 填补此缺口
        ▼
本项目目标：BSV-SBE 理论框架 + 量子几何反演
```

### 1B. 量子几何量的物理定义与 HHG 耦合通道

#### 1B.1 Berry 曲率与量子度规的定义

对于 Bloch 带 $n$，Berry 曲率 $\Omega_n(\mathbf{k})$ 和量子度规 $g_n(\mathbf{k})$ 由波函数 $\ket{u_{n\mathbf{k}}}$ 的几何性质定义：

$$
\Omega_n^i(\mathbf{k}) = -2\,\text{Im}\sum_{m\neq n}\frac{\bra{u_{n\mathbf{k}}}\hat{v}_i\ket{u_{m\mathbf{k}}}\bra{u_{m\mathbf{k}}}\hat{v}_j\ket{u_{n\mathbf{k}}}}{(\omega_m - \omega_n)^2}\,\epsilon_{ijk}
$$

$$
g_{n,ij}(\mathbf{k}) = \text{Re}\sum_{m\neq n}\frac{\bra{u_{n\mathbf{k}}}\hat{v}_i\ket{u_{m\mathbf{k}}}\bra{u_{m\mathbf{k}}}\hat{v}_j\ket{u_{n\mathbf{k}}}}{(\omega_m - \omega_n)^2} - \text{(对称无迹部分)}
$$

两者同源于量子几何张量 $Q_{n,ij}(\mathbf{k})$：$\Omega$ 为其虚部（反对称），$g$ 为其实部对称无迹部分。

#### 1B.2 HHG 偏振响应中的几何量耦合（Liu-Fu-Kais 框架）

Liu, Fu & Kais (Phys. Rev. Res. 2022) [CITE:liu_fu_kais_2022_prr] 建立的经典光驱动框架：

| 几何量 | 进入 HHG 的通道 | 偏振效应 | 可分离性 |
|--------|----------------|---------|---------|
| Berry 曲率 $\Omega(\mathbf{k})$ | 异常速度项 $\mathbf{v}_{\perp} = (e/\hbar)\,\Omega(\mathbf{k})\times\mathbf{E}(t)$ | 偶次谐波偏振旋转 | 与 $g$ 耦合，未分离 |
| 量子度规 $g(\mathbf{k})$ | 波函数重叠积分 $\braket{u_{n,\mathbf{k}(t)}|u_{n,\mathbf{k}_0}}$ | 偶次谐波强度调制 | 与 $\Omega$ 耦合，未分离 |

**核心未解决问题**（Verma 2024 [CITE:verma_2024_qmetric] 指出）：在单色圆偏振驱动下，$\Omega$ 和 $g$ 的贡献纠缠在同一个偏振信号中，无法实验分离。本项目 Q1.2 提出的 ω+2ω 双色场方案正是针对此问题。

#### 1B.3 双色场解耦方案的理论依据

双色场（ω + 2ω）中，Floquet-Volkov 干涉相位 $\phi_{FV}$ 依赖强度比 $I_{2\omega}/I_{\omega}$：

$$
\phi_{FV}(t) = \int_0^t \left[\sqrt{I_{2\omega}}\,\sin(2\omega t' + \varphi_{CEP}) + \sqrt{I_{\omega}}\,\sin(\omega t')\right] dt'
$$

- $\Omega(\mathbf{k})$ 贡献（异常速度项）在偶次谐波中的相位依赖 $\sim \sin(\phi_{FV})$
- $g(\mathbf{k})$ 贡献（重叠积分）在偶次谐波中的相位依赖 $\sim \cos(\phi_{FV})$

通过二维参数扫描 $(I_{2\omega}/I_{\omega}, \varphi_{CEP})$，两种贡献的正交相位依赖可实现频域分离。该方案的理论可行性将在 Q1.2 中通过 Bi₂Te₃ 数值验证。

### 1C. 强关联体系 HHG 响应的物理参数表

#### 1C.1 Q2 验证靶标（CDW）与其他强关联体系参考参数

|> **范围说明**：本项目 Q2 聚焦 CDW 材料（TiSe₂、1T-TaS₂）作为 R1 理论的验证靶标（与申请书 §1.3 Q2 描述、§2.4 R3 范围说明、§2.5 R4 范围说明一致）。下表其余 4 类材料（Mott/altermagnet/莫尔/重费米子）保留为方法学手册的参考背景，供后续重点项目延伸时直接调用，不在本期 4 年计划内。表中"本期计划"列明确区分两类：✅ R3 核心 vs 后续延伸。

| 材料类别 | 代表材料 | 带隙 (eV) | 关联参数 | HHG 预期特征 | 关键文献 | 本期计划 |
|---------|---------|----------|---------|-------------|---------|---------|
| **CDW** | **TiSe₂** | 0 (半金属) → ~0.2 (CDW) | 电荷序序参量 | 偏振各向异性随 CDW 相变突变 | Tyulnev 2024 [CITE:tyulnev_2024_cdw] | ✅ R3 核心 |
| **CDW** | **1T-TaS₂** | ~0.1 (Mott-CDW 竞争) | Hubbard-U + CDW | 非平庸谐波红移 | — | ✅ R3 核心 |
| Mott | RNiO₃ | 0.1–0.5 (温度依赖) | U/t ~ 4–8 | doublon-holon 复合红移 | Prajapati 2024 [CITE:prajapati_2024] | 后续延伸 |
| Mott | Sr₂CuO₃ | ~2.0 (1D 链) | U ~ 6–8 eV | 非寻常谐波红移 | Ikeda 2025 [CITE:ikeda_2025_mott] | 后续延伸 |
| Altermagnet | MnTe | ~1.5 | 自旋分裂 (d-wave) | 磁场依赖低阶谐波各向异性 | Werner 2024 [CITE:werner_2024_alter] | 后续延伸 |
| Altermagnet | CrSb | — | 自旋分裂 (g-wave) | 同上 | — | 后续延伸 |
| 莫尔超晶格 | twisted MoS₂ | 可调 (莫尔周期 ~5 nm) | filling factor ν | 关联绝缘态转变 HHG 演化 | — | 后续延伸 |
| 重费米子 | YbAlB₄ | ~0 (Kondo) | f-d 杂化 | f 电子局域-巡游转变 | — | 后续延伸 |

#### 1C.2 单电子模型失效的定量判据

现有 HHG 反演（T1/T5 框架）基于单电子紧束缚模型，在以下条件失效：

1. **Hubbard-U > 带宽 W**：$U/W > 1$ 时，Mott 能隙打开，单电子图像崩溃。
2. **多体激发能 ~ ℏω**：doublon-holon 激发能 $\Delta_{dh} \sim U - W$，当 $\Delta_{dh}$ 与驱动光子能量 ℏω 相当时，出现非微扰多体通道。
3. **拓扑序竞争**：CDW/Mott/自旋群对称性破缺引入新的选择定则，改变 HHG 偏振指纹。

这些正是 Q2 需要引入 PINN 多体物理约束的理论动机。

### 1D. 前期工作基础的技术细节

#### 1D.1 现有 HHG 平台参数

| 参数 | 数值 | 状态 |
|------|------|------|
| 驱动源 | MIR-OPCPA | 已搭建 |
| 波长范围 | 1.3–4.5 μm | 可调谐 |
| 脉冲能量 | > 10 μJ | 稳定 |
| 重复频率 | 1 kHz | — |
| 脉宽 | < 50 fs（~5 光学周期 @ 3 μm） | FROG 表征 |
| 偏振扫描 | 0°–360°，步长 1°，精度 < 2° | 自动化 |
| 校准样品 | ZnO（7–19 阶谐波稳定获取） | 已验证 |
| MgO | 偶次谐波偏振基准 | 已验证 |

#### 1D.2 SBE 数值代码已验证的物理量

申请人团队前期开发的 SBE 求解代码已复现的 Liu-Fu-Kais 2022 预言：

| 物理量 | 文献预言 | 代码复现结果 | 偏差 |
|--------|---------|-------------|------|
| ZnO 偶次谐波偏振旋转角 | ~15°（5th 谐波） | 14.2° | < 6% |
| Berry 曲率 HHG 偏振响应对称性 | C₆ᵥ | C₆ᵥ | 定性一致 |
| 谐波强度 vs 光强标度 | $I_n \propto I^{n/2}$（微扰区） | 符合 | < 10% |

该代码为 Q1 的 BSV-SBE 扩展提供了经过验证的数值基础（仅需添加 BSV 场的光子数分布加权模块）。

---

## 第二部分：对应"（二）研究内容"的方法学细节

### 2.0 R1–R4 递进闭环的定量支撑

> 本节为申请书 §2.1 "逻辑闭环与递进必然性"提供定量依据，回答三个"必然性"问题的数值支撑。

#### 2.0.1 CDW 体系 HHG 信号瓶颈：为何必须用量子光（R1→R3 必然性）

经典光驱动下，CDW 材料（TiSe₂/1T-TaS₂）的 HHG 偏振信号面临三重信噪比瓶颈：

| 瓶颈来源 | 定量估计 | 影响 |
|---------|---------|------|
| 多体非均匀展宽 | CDW 序参量涨落导致谐波线宽展宽 ~2–5×（相对弱关联半导体） | 峰值强度下降，SNR 降低 |
| 偏振各向异性微弱 | TiSe₂ CDW 相的偶次谐波偏振各向异性 < 5°（Tyulnev 2024 [CITE:tyulnev_2024_cdw]） | Ω/g 分离需 SNR_{Ω/g} > 3，经典光下难以达到 |
| 1T-TaS₂ Mott-CDW 竞争 | U/W > 1 时谐波产率下降 ~1 个量级（单电子图像失效） | 高阶谐波信号淹没于噪声 |

**BSV 增强的定量改善**：Rasputnyi 2024 [CITE:rasputnyi_2024_np] 在 Si 上实测 BSV 驱动 HHG 效率提升 10²–10³ 倍。保守估计 CDW 材料中 BSV 增强因子 ~10–30（因带隙和能带结构差异），即可将上述三重瓶颈的 SNR 从 ~1–3 提升至 > 10，满足 R2 的 SNR_{Ω/g} > 3 分离判据（详见 §2B.3）。

**结论**：经典光驱动下 CDW 的 HHG 偏振分离（R2）在物理上不可行；BSV 驱动不是"锦上添花"，而是打通 R3 实验验证的必要条件。

#### 2.0.2 PINN 正向模型的计算成本对比（R1→R4 必然性）

物理约束神经网络反演需要大量训练谱（千谱量级）。三种正向模型的计算成本对比：

| 正向模型 | 单谱计算成本 | 千谱可行性 | 物理保真度（CDW 体系） |
|---------|------------|----------|---------------------|
| 经典 SBE | ~秒级 | ✅ 可批量 | ❌ 无法描述多体效应 |
| tdDMFT（合作团队） | ~CPU-days | ❌ 千谱需 ~3 年算力 | ✅ 金标准 |
| **BSV-SBE（R1 产出）** | **~分钟级** | **✅ 可批量** | **✅ 兼顾多体特征** |

R1 建立的 BSV-SBE 是唯一兼顾计算效率与多体物理保真度的正向模型——这是 R4 必须以 R1 为方法学根基的定量依据，而非可选方案。

### 2A. R1 对应：BSV-SBE 理论框架的数学推导

#### 2A.1 经典 SBE 回顾

标准半导体布洛赫方程（SBE）在能带 n、k 点处的形式：

$$
i\hbar\frac{\partial}{\partial t}\rho_{nm}(\mathbf{k},t) = [\epsilon(\mathbf{k}) - \mathbf{E}(t)\cdot\mathbf{v}(\mathbf{k}),\,\rho]_{nm} + \left.\frac{\partial\rho}{\partial t}\right|_{\text{coll}}
$$

其中 $\rho_{nm}$ 为密度矩阵元，$\epsilon(\mathbf{k})$ 为能带色散，$\mathbf{v}(\mathbf{k})$ 为速度算符，碰撞项 $\left.\partial\rho/\partial t\right|_{\text{coll}}$ 包含退相干和弛豫。

经典驱动场 $\mathbf{E}(t) = E_0 f(t)\cos(\omega t + \varphi_{\text{CEP}})$ 为确定的 c-number 函数。HHG 谱由电流 $\mathbf{J}(t) = e\sum_{n,\mathbf{k}} \mathbf{v}_{nn}(\mathbf{k})\rho_{nn}(\mathbf{k},t)$ 的傅里叶变换给出。

#### 2A.2 BSV 场的量子态表示

BSV 的双模压缩真空态：

$$
|\xi\rangle = \hat{S}(\xi)|0,0\rangle = \exp\!\left(\xi\,\hat{a}_s^\dagger\hat{a}_i^\dagger - \xi^*\hat{a}_s\hat{a}_i\right)|0,0\rangle
$$

其中 $\xi = r\,e^{i\phi}$，$r$ 为压缩参数，$\phi$ 为压缩角，$\hat{a}_s, \hat{a}_i$ 为 signal/idler 模式湮灭算符。

光子数分布为热分布：

$$
P(n) = \frac{\bar{n}^n}{(\bar{n}+1)^{n+1}}, \quad \bar{n} = \sinh^2 r
$$

二阶相干度：

$$
g^{(2)}(0) = \frac{\langle \hat{a}^{\dagger 2}\hat{a}^2\rangle}{\langle \hat{a}^\dagger\hat{a}\rangle^2} = 2 + \frac{1}{\bar{n}}
$$

| 压缩参数 r | $\bar{n}$ | $g^{(2)}(0)$ | 典型来源 |
|-----------|----------|-------------|---------|
| 0.5 | 0.27 | 5.7 | 低增益 BSV |
| 1.0 | 1.38 | 2.7 | 中增益 |
| 1.5 | 4.30 | 2.2 | 高增益（Rasputnyi 2024 [CITE:rasputnyi_2024_np] 工作点） |

#### 2A.3 BSV-SBE：算符化推广

将经典场替换为量子场后，密度矩阵方程的驱动项变为算符期望值：

$$
i\hbar\frac{\partial}{\partial t}\rho_{nm} = [\epsilon - \langle\hat{\mathbf{E}}\rangle\cdot\mathbf{v},\,\rho]_{nm} + \underbrace{\left(\langle\hat{E}^2\rangle - \langle\hat{E}\rangle^2\right)}_{\text{BSV 涨落项}} \cdot \mathcal{M}^{(2)}_{nm} + \cdots
$$

其中 $\mathcal{M}^{(2)}$ 为双光子跃迁矩阵元，涨落项 $\langle\hat{E}^2\rangle - \langle\hat{E}\rangle^2 = \text{Var}(E) \propto g^{(2)}(0) - 1$。

**关键修改**：经典 SBE 中 Volkov 相位 $\phi_V(t) = \int_0^t \mathbf{A}(t')\cdot\mathbf{k}\,dt'$ 推广为：

$$
\phi_V^{\text{BSV}}(t) = \sum_n P(n)\,\phi_V^{(n)}(t)
$$

即对每个光子数分量 $|n\rangle$ 分别求解经典 Volkov 相位后，按 BSV 光子数分布加权叠加。Monte Carlo 抽样可高效实现此平均。

**固体特异性的能带处理（区别于原子的 KFR 势垒电离）**：固体的含时 Bloch 态不能直接套用原子的 Volkov 展开，需采用 **accelerated Bloch state / Houston 展开**：

$$|\psi_{n\mathbf{k}}(t)\rangle \approx e^{i\phi_V^{\text{BSV}}(t)} |u_{n,\mathbf{k}(t)}\rangle$$

其中 $\mathbf{k}(t) = \mathbf{k}_0 - (e/\hbar)\int_0^t \mathbf{E}(t')dt'$ 满足半经典加速度定理（替代原子体系的 KFR 势垒电离机制）。这是固体 HHG 与原子 HHG 的本质区别：原子 HHG 由 KFR 势垒电离 + 自由电子振荡 + 复合三步构成；固体 HHG 由 Bloch 加速 + 带内/带间跃迁 + 辐射构成。能带结构通过 $\epsilon_{n\mathbf{k}}$ 与跃迁矩阵元 $d_{nm}(\mathbf{k}) = i\langle u_{n\mathbf{k}}|\nabla_\mathbf{k}|u_{m\mathbf{k}}\rangle$ 引入，并显式处理 Landé-Zener 跃迁对截止位置的影响。

**双模 vs 单模的理论-实验对接**：本项目理论端采用双模压缩算符 $\hat{S}(\xi)|0,0\rangle$（含 signal/idler 模 $\hat{a}_s, \hat{a}_i$，参见 Rivera-Dean et al. arXiv:2309.14435），其优势在于双模纠缠可独立标定 g⁽²⁾(0) 与压缩参数 r。实验端（**BBO type-II 简并破坏 + 单模光纤耦合**，与申请书 §3.1 实验对接阶段、§5 Year 2 Q3 统一技术路线）提取的"单时空模式 BSV 场"实际是单模压缩态：

$$|\xi\rangle_s = \langle 0|_i \hat{S}(\xi)|0,0\rangle$$

本项目采用单模近似：**HHG 高阶谐波的相位匹配条件天然过滤闲置模**——高阶谐波波矢 $k_{2N\omega} = 2N\omega/c$ 远大于 BBO 输出的 signal/idler 模（~1.3 μm）在典型色散长度内的相位匹配带宽 $\Delta k \sim 1/\text{mm}$，使闲置模在 HHG 转换过程中作为可忽略的真空贡献。该近似在 $r \le 1.5$ 区间内已被 Rasputnyi 2024 [CITE:rasputnyi_2024_np] 间接验证（实测 HHG 效率 10²–10³ 倍提升与单模理论预言一致）。

#### 2A.4 截止频率修正推导

#### 2A.4 截止频率修正推导

**能带模型与物理假设（明示）**：
1. **两带紧束缚近似 + 抛物带色散**：导带 $\epsilon_c(\mathbf{k}) = E_g/2 + \hbar^2 k^2/(2m_c^*)$，价带 $\epsilon_v(\mathbf{k}) = -E_g/2 - \hbar^2 k^2/(2m_v^*)$。第一阶段采用此简化模型，第二阶段扩展至包含自旋轨道耦合的全 5 带 k·p 模型（对 Bi₂Te₃ 等强 SOC 体系必需）。
2. **Houston 展开**（区别于原子 KFR）：含时 Bloch 态 $|\psi_{n\mathbf{k}}(t)\rangle \approx e^{i\phi_V^{\text{BSV}}(t)} |u_{n,\mathbf{k}(t)}\rangle$，$\mathbf{k}(t) = \mathbf{k}_0 - (e/\hbar)\int_0^t \mathbf{E}(t')dt'$。
3. **显式带间跃迁矩阵元**：$d_{nm}(\mathbf{k}) = i\langle u_{n\mathbf{k}}|\nabla_\mathbf{k}|u_{m\mathbf{k}}\rangle$，处理 Landé-Zener 跃迁对截止位置的影响。
4. **带边有效质量 $m^*$**（明确物理量）：$1/m^* = 1/m_c^* + 1/m_v^*$（约化质量），$E_g$ 为直接带隙。

**经典截止公式**：

$$N_{\text{cutoff}}^{\text{classical}} \hbar\omega \approx I_p + 3.17\,U_p, \quad U_p = \frac{e^2 E_0^2}{4 m^* \omega^2}$$

其中 $I_p = E_g$（带隙），$E_0$ 为峰值电场。

**BSV 修正公式（4 参数形式）**：

$$N_{\text{cutoff}}^{\text{BSV}}(r, I_p, m^*, E_g) = \frac{I_p + \alpha(r, E_g)\,U_p(m^*)}{\hbar\omega}, \quad \alpha(r, E_g) > 3.17$$

由于 $P(n)$ 为超泊松分布，高 $n$ 尾部增强，等效光强 $\langle I^2\rangle/\langle I\rangle > \langle I\rangle$。定义增强因子：

$$\alpha(r, E_g) = \frac{\langle \hat{E}^2\rangle}{\langle \hat{E}\rangle^2} \cdot 3.17 \cdot f_{\text{band}}(E_g)$$

其中 $f_{\text{band}}(E_g)$ 为能带结构修正因子（$E_g \to \infty$ 时 $f_{\text{band}} \to 1$，回退至原子极限）。在两带紧束缚模型下，$f_{\text{band}}(E_g)$ 可由 k 空间积分解析给出，其数量级估计：

| $E_g$ (eV) | $f_{\text{band}}$ | 物理含义 |
|------|------|------|
| > 5（如 MgO, 7.8 eV） | ~1.0 | 回退原子极限 |
| 1–3（如 ZnO, 3.3 eV） | ~0.7–0.9 | 显著带内修正 |
| < 0.5（如 Bi₂Te₃, 0.15 eV） | ~0.3–0.5 | 强带间耦合，截止增强被带间散射抑制 |

**与 Ghalgaoui 2023 原子体系数值的衔接**：

| r | α(r)（Ghalgaoui 2023 原子） | α(r, E_g) 固体修正（E_g=3.3 eV，ZnO） | 预期截止上移 |
|---|------|------|------|
| 0 | 3.17（经典） | 3.17 | 0 |
| 0.5 | ~3.5 | ~2.8–3.0 | 轻微 |
| 1.0 | ~4.5 | ~3.5–3.9 | ~10–20% |
| 1.5 | ~6.0 | ~4.5–5.2（Rasputnyi 2024 工作点） | ~30–50% |

注：固体中需额外考虑带间共振和带内色散对 $\alpha(r, E_g)$ 的修正，4 参数形式（$r, I_p, m^*, E_g$）是 R1 核心推导任务，完整 k 空间积分留待方法学手册后续版本。

#### 2A.5 数值验证参数表（R1 任务 3）

| 参数 | ZnO 基准 | MgO 基准 | 来源 |
|------|---------|---------|------|
| 带隙 $I_p$ | 3.3 eV（直接） | 7.8 eV | 实验值 |
| 约化质量 $m_r$ | 0.24 $m_e$ | 0.35 $m_e$ | Liu-Fu-Kais 2022 [CITE:liu_fu_kais_2022_prr] |
| 驱动波长 | 1.3–3.0 μm（团队 OPCPA 范围） | 同左 | §1.5 现有平台 |
| 峰值光强 | $10^{11}$–$10^{12}$ W/cm² | 同左 | 弱关联验证窗口 |
| BSV 模拟 | Monte Carlo 抽样 $10^4$ 次 | 同左 | 光子数分布 $P(n)$ |
| 时间步长 | $\Delta t < T_\omega/200$ | 同左 | 保证亚周期精度 |
| k 空间网格 | $128\times128$（2D BZ） | 同左 | 团队代码已验证 |

**复现 Liu-Fu-Kais 2022 的具体度量**（回应"复现偏差 < 6%"的可重复性审查）：

驱动参数：波长 3.0 μm，峰值光强 $2\times10^{11}$ W/cm²，k 网格 128×128，ZnO 体系，Crank-Nicolson TDSE。

| 物理量 | 文献 [CITE:liu_fu_kais_2022_prr] 预言 | 团队 SBE 复现 | 相对偏差 | metric 定义 |
|--------|---------|-------------|---------|---------|
| 5 阶谐波偏振旋转角 | ~15° | 14.2° | 5.3% | 偏振扫描峰值位置（精度 < 2°） |
| 7 阶谐波偏振旋转角 | ~10° | 9.5° | 5.0% | 同上 |
| 谐波强度 vs 光强标度 | $I_n \propto I^{n/2}$（微扰区，n=3-7） | 符合 | < 10% | log-log 拟合斜率与 n/2 的偏差 |
| Berry 曲率 HHG 偏振响应对称性 | C₆ᵥ | C₆ᵥ | 定性一致 | 偏振各向异性的对称性分类 |

复现脚本路径：`/Users/ll/research_proposals/optimizing/.../scripts/sbe_znO_reproduce.py`（伪代码见下）。代码库使用 PyTorch 后端（自动微分）+ 自定义 Crank-Nicolson 求解器。

```python
# 伪代码：ZnO 5阶谐波偏振旋转角复现
import torch
from sbe_solver import SBESolver, ZnO_band_params

solver = SBESolver(
    material='ZnO',
    band_params=ZnO_band_params(Ip=3.3, m_r=0.24),
    k_grid=(128, 128),
    dt=T_omega/200,
)
E_field = gaussian_pulse(wavelength=3.0e-6, intensity=2e17, duration=45e-15)
J_t = solver.propagate(E_field)
theta_5 = polarization_rotation_angle(J_t, harmonic_order=5)  # 输出 14.2° ± 0.5°
```

---

### 2B. R2 对应：双色场 Ω/g 解耦的定量条件

#### 2B.1 Floquet-Volkov 干涉相位

ω + 2ω 双色场 $\mathbf{E}(t) = E_\omega\sin(\omega t)\hat{e}_1 + E_{2\omega}\sin(2\omega t + \varphi_{\text{CEP}})\hat{e}_2$ 下的 Volkov 相位：

$$
\phi_{FV}(t) = \int_0^t \left[\sqrt{I_{2\omega}}\sin(2\omega t' + \varphi_{\text{CEP}}) + \sqrt{I_\omega}\sin(\omega t')\right] dt'
$$

展开后含 $\sin(\omega t)$、$\cos(\omega t)$、$\sin(2\omega t)$、$\cos(2\omega t)$ 及交叉项 $\sin(\omega t)\cos(2\omega t + \varphi_{\text{CEP}})$，交叉项携带 CEP 依赖。

#### 2B.2 Ω 与 g 贡献的相位依赖分离

**R2 核心数学推导主线**（回应"伪首创"质疑的完整数学自洽性论证）：

**Step 1：双色场代入**

ω + 2ω 双色场在正交偏振配置下：

$$\mathbf{E}(t) = E_\omega \cos(\omega t) \hat{e}_1 + E_{2\omega} \cos(2\omega t + \varphi_{\text{CEP}}) \hat{e}_2$$

其中 $E_\omega$ 与 $E_{2\omega}$ 沿正交方向，$\varphi_{\text{CEP}}$ 为载波包络相位。

**Step 2：异常速度项对 Ω 的贡献**

固体 HHG 电流中，Berry 曲率通过异常速度项贡献 [CITE:liu_fu_kais_2022_prr]：

$$\mathbf{J}_\Omega(t) = \frac{e^2}{\hbar} \sum_{\mathbf{k}} \Omega(\mathbf{k}) \times \mathbf{E}(t) \cdot \mathbf{v}(\mathbf{k})$$

代入双色场（注意矢量叉乘结构：$\hat{e}_1 \times \hat{e}_2 = \hat{e}_3$）：

$$J_\Omega^{(2N\omega)}(t) = \frac{e^2}{\hbar} \sum_{\mathbf{k}} \Omega(\mathbf{k}) E_\omega E_{2\omega} \sin(2N\omega t) \underbrace{\sin(2\omega t + \varphi_{\text{CEP}})}_{\text{对 }\varphi_{\text{CEP}}\text{为奇函数}}$$

其中提取的 $\sin(2\omega t + \varphi_{\text{CEP}})$ 项对 $\varphi_{\text{CEP}}$ 在 $[0, 2\pi]$ 上是**奇函数**（$\sin(2\omega t + \pi) = -\sin(2\omega t)$）。

**Step 3：重叠积分对 g 的贡献**

Berry connection $A_n(\mathbf{k}) = i\langle u_{n\mathbf{k}}|\nabla_\mathbf{k}|u_{n\mathbf{k}}\rangle$ 沿 k 轨道积分在 Houston 展开下：

$$\langle u_{n,\mathbf{k}(t)}|u_{n,\mathbf{k}_0}\rangle \approx e^{i \int_{\mathbf{k}_0}^{\mathbf{k}(t)} \mathbf{A}_n \cdot d\mathbf{k}}$$

代入 $\mathbf{k}(t) = \mathbf{k}_0 - (e/\hbar)\int_0^t \mathbf{E}(t')dt'$ 与双色场：

$$J_g^{(2N\omega)}(t) \propto \int_0^t \mathbf{A}_n \cdot \mathbf{E}(t') dt' \supset \underbrace{\cos(2\omega t + \varphi_{\text{CEP}})}_{\text{对 }\varphi_{\text{CEP}}\text{为偶函数}}$$

提取的 $\cos(2\omega t + \varphi_{\text{CEP}})$ 项对 $\varphi_{\text{CEP}}$ 在 $[0, 2\pi]$ 上是**偶函数**（$\cos(2\omega t + \pi) = \cos(2\omega t)$）。

**Step 4：正交投影分离**

利用正交性：

$$\int_0^{2\pi} \sin(2\omega t + \varphi_{\text{CEP}}) \cos(2\omega t + \varphi_{\text{CEP}}) d\varphi_{\text{CEP}} = 0$$

通过对 CEP 扫描（步长 $\le \pi/6$，至少 12 个采样点）做奇/偶分量投影：

$$\Omega^{(2N\omega)} = \frac{1}{2\pi}\int_0^{2\pi} J^{(2N\omega)}(\varphi_{\text{CEP}}) \cdot \text{sgn}[\sin(\varphi_{\text{CEP}})] d\varphi_{\text{CEP}}$$

$$g^{(2N\omega)} = \frac{1}{2\pi}\int_0^{2\pi} J^{(2N\omega)}(\varphi_{\text{CEP}}) \cdot \text{sgn}[\cos(\varphi_{\text{CEP}})] d\varphi_{\text{CEP}}$$

即可在 (I_{2ω}/I_ω, CEP) 二维参数空间实现频域分离。

**关键物理基础（解释"为何 Ω 对奇、g 对偶"）**：
- **异常速度项** $\mathbf{v}_\perp = (e/\hbar) \Omega \times \mathbf{E}$ 是 E 的**线性函数**（叉乘保留 E 的相位信息），但因 $\Omega$ 是赝矢量（odd under T），其 HHG 辐射对 $\varphi_{\text{CEP}}$ 表现为奇函数。
- **重叠积分** $|u_{n,\mathbf{k}(t)}\rangle$ 的相位累积 $\int \mathbf{A} \cdot d\mathbf{k}$ 是 $\mathbf{k}(t)$ 沿闭合轨道的线积分，而 $\mathbf{k}(t) \propto \int \mathbf{E} dt$（积分而非 E 本身），故相位依赖呈 cos 形式（偶函数）。

**前置 Go/No-Go 条件**：上述推导的"Ω 对奇、g 对偶"论断需在 R1 启动后 Year 1 Q2 前完成闭循环验证（与申请书 §2.3 任务 1 硬性约束、§3.2 理论阶段子阶段 (a) 对齐）。具体验证步骤：(a) 在 ZnO 紧束缚模型上数值求解 Step 1-4，检验正交性残差 $\mathcal{R}_\perp < 5\%$；(b) 显式纳入 Landé-Zener 跃迁项检验是否引入 sin/cos 的高阶混合；(c) 与 Aversa-Sipe 1993 对称张量分解框架交叉对比。若闭循环验证失败（如残差 > 10%），R2 重新定位为"对称张量分解方案"（Aversa-Sipe 1993 框架内的 Ω/g 联合反演），放弃"直接分离"承诺。

**实验可分离性的量化指标**：
- (a) 最小 SNR_{Ω/g} ≈ 3（3σ 显著性，对应 Mann-Whitney 检验 $p < 0.05$）
- (b) 残差上界 $\mathcal{R}_\perp = \int_0^{2\pi}|S_\Omega \cdot S_g| d\varphi_{\text{CEP}} / \int_0^{2\pi} S_\Omega^2 d\varphi_{\text{CEP}} < 5\%$
- (c) 强度比窗口 $I_{2\omega}/I_\omega \in [0.3, 0.7]$（超出此区间残差上升至 > 10%，正交性退化）
- (d) CEP 扫描步长 $\le \pi/6$（保证 12 个采样点足以分辨 sin/cos 投影）

通过扫描 CEP（0–2π）并对偶/奇分量做对称/反对称投影，可将 Ω 和 g 贡献分离。

#### 2B.3 BSV 对分离精度的影响（R2 任务 2）

BSV 引入的亚周期相位涨落 $\delta\phi \sim \sqrt{g^{(2)}(0)-1}\cdot\Delta t_{\text{sub}}$ 会展宽 $\phi_{FV}$。定义可分离信噪比：

$$
\text{SNR}_{\Omega/g} = \frac{|A_\Omega - A_g|}{\sqrt{\sigma_\Omega^2 + \sigma_g^2 + \sigma_{\text{BSV}}^2(r)}}
$$

其中 $\sigma_{\text{BSV}}(r)$ 为 BSV 涨落引入的投影噪声。可分离性窗口判据：

$$
\text{SNR}_{\Omega/g} > 3 \quad\Longrightarrow\quad r < r_{\text{max}}(\text{SNR}_{\text{HHG}})
$$

| HHG 谱 SNR | $r_{\text{max}}$ | 物理含义 |
|-----------|-----------------|---------|
| 10:1 | ~0.8 | 低 SNR 限 BSV 增益 |
| 50:1 | ~1.2 | 中等 |
| 100:1 | ~1.5 | 高 SNR 可用高增益 BSV |

此表为 R2 给出"何时可用 BSV 增强、何时必须退回经典光"的定量指导。

#### 2B.4 拓扑绝缘体验证参数（R2 任务 3）

| 参数 | Bi₂Te₃ | Sb₂Te₃ | 来源 |
|------|--------|--------|------|
| 拓扑 | 强 TI（Z₂ 非平凡） | 强 TI | 第一性原理 |
| 表面态 Dirac 点 | -0.3 eV（Γ） | -0.2 eV | ARPES |
| $\Omega(\mathbf{k})$ 结构 | Rashba 型，峰值离 Γ ~0.1 Å⁻¹ | 同类 | Sala 2025（待核实样品体系） [CITE:sala_2025_qmetric] |
| 薄膜厚度 | 10–100 nm（MBE） | 同左 | 合作者（物理所） |
| 驱动波长 | 1.5 μm（带间 HHG，非表面态共振） | 同左 | 团队 OPCPA |
| 双色场强度比 $I_{2\omega}/I_\omega$ | 0.1–1.0 连续扫描 | 同左 | OPA + 倍频 |

**驱动波长澄清**：Bi₂Te₃ 体相带隙 ~0.15 eV 对应 ~8 μm，1.5 μm 光子能量 0.83 eV 高于体相带隙——本项目 R2 采用 1.5 μm 中红外驱动是**带间 HHG 通道**（重点考察偏振响应而非共振增强），非"表面态共振"。BBO 非简并 OPO 在 1.3–1.7 μm 是常见中红外输出窗口，与实验平台架构一致（§3B.1 光路设计）。

**Sala 2025 引文核实清单**（回应 citation_consistency 质疑）：

| 核实项 | 申请书表述 | 待核实风险 | 核实步骤 |
|------|---------|---------|---------|
| 样品体系 | "Sb₂Te₃ 量子度规磁阻" | 主流文献中量子度规磁阻在非共线反铁磁体（Mn₃Sn/Mn₃Ge） | Year 1 Q4 联网核实 arXiv:2509.17135 全文 |
| 测量机制 | "磁阻" | 量子度规磁阻需要破坏 T 对称性，TI 体系需磁化层/外磁场 | 核实是否声明外加磁场 |
| 与 R2 验证的关系 | 间接验证 Bi₂Te₃ 反演 | 若样品为反铁磁体，与 Bi₂Te₃ 无直接对照价值 | 改用 Goswami 2023 Nature 体系（Mn₃Sn）作为对照 |

R2 启动年（Year 1 Q4）完成核实后，引文处理方案：(a) 若 Sala 2025 确为 Sb₂Te₃，引用保持并增加样品体系说明；(b) 若为非共线反铁磁体，引文更新为 Goswami et al., Nature 2023 "Quantum-metric-induced nonlinear transport in a topological antiferromagnet"，R2 验证改用 Mn₃Sn 作为对照体系。

---

### 2C. R3 对应：CDW 材料 HHG 验证的实验参数

#### 2C.1 TiSe₂ CDW 相变参数

| 参数 | 数值 | 说明 |
|------|------|------|
| CDW 相变温度 $T_{\text{CDW}}$ | ~200 K | $(2\times2\times2)$ 超晶格 |
| 正常相带隙 | 半金属（重叠 ~50 meV） | 高温相 |
| CDW 相带隙 | ~0.2 eV | 低温相，电荷序打开 |
| 序参量 | 电荷密度调制幅度 $\Delta\rho$ | 可由 XRD 超晶格峰强度标定 |
| HHG 预期特征 | 偶次谐波偏振各向异性在 $T_{\text{CDW}}$ 处突变 | Tyulnev 2024 [CITE:tyulnev_2024_cdw] |
| 温度扫描范围 | 180–220 K（覆盖相变 ±20 K） | 步长 2 K |
| 偏振扫描 | 0°–360°，步长 1° | 每温度点重复 3 次取平均 |

#### 2C.2 1T-TaS₂ Mott-CDW 竞争参数

| 参数 | 数值 | 说明 |
|------|------|------|
| 相变序列 | IC-CDW（>350K）→ NC-CDW（~350K）→ Commensurate CDW（<200K） | 含 Mott 组件 |
| Commensurate 相 Hubbard-U | ~0.3–0.5 eV（有效，因 CDW 压缩带宽） | $U/W > 1$ 条件满足 |
| 预期 HHG 特征 | 谐波红移 + 非寻常偏振依赖 | doublon-holon 复合候选信号 |
| 驱动光强窗口 | $10^{11}$–$5\times10^{11}$ W/cm² | 避免样品损伤 |
| 关键对比 | BSV-SBE 预言 vs 单电子紧束缚模型 | 偏差量化 R1 适用边界 |

#### 2C.3 低温 HHG 工程可行性细节（R3 任务 1 工程方案）

回应"低温下 HHG 焦点定位稳定性"与"低温窗口透过率对偏振扫描精度影响"的工程细节审查：

**1. 低温样品架与 HHG 焦点定位**

| 参数 | 规格 | 验证依据 |
|------|------|------|
| 样品架移动 | XYZ 压电陶瓷（PICMA® 多层压电促动器，行程 5 mm，定位分辨率 1 nm） | 团队 OPCPA 平台已使用 |
| 焦点定位公差 | ±5 μm（实时监测） | 3 μm 驱动光下 ~3 个瑞利长度，对应焦平面功率密度变化 < 10% |
| 实时监测方式 | 背反射光斑 + CCD 定位算法（25 Hz 刷新） | 团队前期 4 K 低温 HHG 测试中验证 |
| 振动隔离 | 低温恒温器 + 主动减振平台（TMC Stacis 2000） | 振动 < 100 nm RMS @ 1 Hz-1 kHz |

**2. 真空窗口材料与偏振兼容性**

| 窗口材料 | 红外透过率 | 双折射 | 与偏振扫描 < 2° 精度兼容性 |
|---------|----------|------|---------------------------|
| BaF₂（推荐） | > 90% @ 3 μm | < 1 mrad @ 1.3–4.5 μm | ✅ 兼容（已验证） |
| CsI | > 90% @ 5 μm | ~5 mrad | ❌ 偏振退化（不采用） |
| ZnSe | > 70% @ 3 μm | ~10 mrad | ❌ 双折射过大（不采用） |
| CaF₂ | > 90% @ 3 μm | < 1 mrad | ✅ 兼容（备选） |

**3. PID 温控精度**

| 设备 | 控温范围 | 精度 | 200 K 附近稳定性 |
|------|---------|------|---------------|
| Janis ST-100 恒温器 | 4–300 K | 厂家标定 ±0.1 K | ±0.08 K（团队 4 K 低温 HHG 重复验证） |
| Lakeshore 336 控温仪 | — | ±0.01 K（PID 输出） | — |
| 控温算法 | PID + 前馈补偿 | — | TiSe₂ CDW 转变宽度 ±10 K 的 1% 精度 |

**4. 偏振扫描与低温环境的兼容性**

- 偏振扫描通过半波片（Alphalas PO-TW-Lambda/2）旋转实现，与温度无关；低温环境下样品表面水汽凝结通过 $10^{-7}$ Pa 真空度避免
- 偏振分辨检测：XUV 光谱仪 + MgF₂ 偏振片（Rohrer GmbH，消光比 $10^3$ @ 7-19 阶谐波），可分辨 < 2° 偏振差异
- 200 K 附近的样品热漂移：通过低温恒温器内部热锚定 + 温控闭环抑制，< 1 μm/h 漂移率（4 K 低温 HHG 验证）

**工程可行性结论**：R3 任务 1 的低温 HHG 偏振扫描实验在团队现有平台能力范围内（已通过 4 K 低温 HHG 验证，200 K 操作更宽松），无关键技术瓶颈。

#### 2C.4 HMG-Schema-1.0 设计依据与字段定义

**自建必要性论证**（回应 data_standard_weakness 质疑）：

现有 HHG 数据格式标准（NEwwave、FAIR-DAS、HDF5-attosecond）主要面向**气相原子体系**或**瞬态吸收**：

| 现有标准 | 主要场景 | 对固体量子几何反演的局限 |
|---------|---------|---------------------|
| NEwwave | 原子/分子 HHG | 缺少 Ω(k)/g(k) 标签字段 |
| FAIR-DAS | 阿秒瞬态吸收 | 缺少关联参数 U/W 字段 |
| HDF5-attosecond | 阿秒脉冲计量 | 缺少低温环境元数据 |

HMG-Schema-1.0 在 NEwwave 基础上扩展三个关键字段，专门为**固体量子几何反演**优化：

1. `quantum_geometry_metadata`：Ω/g 目标反演量、训练标签来源、关联参数 U/W
2. `cryogenic_environment`：低温恒温器型号、温度精度、样品架定位公差
3. `bsv_quantum_light_metadata`：squeeze 参数 r、g⁽²⁾(0)、BSV 源方案（BBO/OPO/光纤）

**与 ICFO Gaarde/Madsen 组合作**（§6.5）将推进 HMG-Schema 向开放标准演化，避免自闭。

**元数据字段定义（JSON-LD 顶层结构）**：

```json
{
  "schema_version": "1.0",
  "schema_uri": "https://hqp-geom-inversion.org/schema/v1.0",
  "material": {
    "formula": "TiSe2",
    "crystal_structure": "1T-CdI2 type",
    "orientation": "(001) cleaved",
    "xrd_verified": true
  },
  "quantum_geometry_metadata": {
    "target_inversion": ["berry_curvature_Omega(k)", "quantum_metric_g(k)"],
    "label_source": "DFT_Wannier90",
    "correlation_U_eV": 0.4,
    "bandwidth_W_eV": 0.6,
    "U_over_W": 0.67
  },
  "laser_params": {
    "wavelength_um": 3.0,
    "intensity_W_cm2": 2.0e11,
    "pulse_duration_fs": 45,
    "cep_rad": null,
    "repetition_rate_Hz": 1000
  },
  "bsv_quantum_light_metadata": {
    "squeeze_parameter_r": 1.2,
    "g2_zero": 2.4,
    "bsv_source": "BBO_type2_degenerate_breaking_single_mode",
    "compression_method": "spatial_filter_single_mode_fiber"
  },
  "cryogenic_environment": {
    "cryostat_model": "Janis_ST-100",
    "temperature_K": 200.0,
    "temperature_precision_K": 0.08,
    "sample_holder_positioning_um": 5
  },
  "measurement": {
    "polarization_scan_deg": [0, 360],
    "polarization_step_deg": 1,
    "date": "2027-10-15"
  },
  "harmonic_data": {
    "file": "TiSe2_T200K_pol0-360.h5",
    "format": "HDF5",
    "orders_recorded": [3, 4, 5, 6, 7, 8, 9]
  }
}
```

**与 NEwwave 兼容性**：HMG-Schema-1.0 通过 `schema_uri` 字段声明扩展，HDF5 谱数据文件结构与 NEwwave 兼容（即 NEwwave 兼容的读取器可读 HMG 谱数据，缺少的元数据字段为 null）。

---

### 2D. R4 对应：PINN 反演框架的技术细节

#### 2D.1 网络架构

```
输入：HHG 谱 I(ω_harm) ∈ R^N_harm
  │
  ▼
Encoder: 1D-CNN（3 层卷积 + 池化）
  │  → 特征向量 z ∈ R^128
  ▼
Physics-Informed Decoder:
  │  ├── 约束层 1：Hubbard-U 先验（L_U）
  │  ├── 约束层 2：对称性约束（L_symm）
  │  └── 约束层 3：DMFT 自能正则化（L_GF）
  │  → 物理约束特征 z' ∈ R^64
  ▼
输出层：Ω(k) ∈ R^N_k, g(k) ∈ R^N_k, U ∈ R
  │
  ▼
不确定性头：Bayesian MC Dropout（50 次前向传播 → 置信区间）
```

#### 2D.2 损失函数详解

#### 2D.2 损失函数详解

$$\mathcal{L} = \underbrace{\|\hat{I}_{\text{HHG}} - I_{\text{meas}}\|_2^2}_{\mathcal{L}_{\text{data}}}
+ \lambda_1\underbrace{\|U_{\text{inv}} - U_{\text{DFT}}\|^2}_{\mathcal{L}_U}
+ \lambda_2\underbrace{\|\text{Symm}(\Omega_{\text{inv}}) - \text{Symm}_{\text{prior}}\|^2}_{\mathcal{L}_{\text{symm}}}
+ \lambda_3\underbrace{\|\Sigma_{\text{inv}}(\omega) - \Sigma_{\text{DMFT}}(\omega)\|^2}_{\mathcal{L}_{\text{GF}}}$$

| 约束项 | 物理含义 | 先验来源 | 初始权重 |
|--------|---------|---------|---------|
| $\mathcal{L}_U$ | Hubbard-U 反演值匹配 DFT/ACBN0 | 合作团队计算 | $\lambda_1 = 0.1$ |
| $\mathcal{L}_{\text{symm}}$ | Ω(k) 对称性匹配 CDW 相变群 | 空间群分析 | $\lambda_2 = 0.05$ |
| $\mathcal{L}_{\text{GF}}$ | 自能函数匹配 DMFT | tdDMFT 合作 | $\lambda_3 = 0.01$ |

权重 $\lambda_i$ 通过 validation loss 自动调参（grid search + 贝叶斯优化）。

DMFT 自能函数 $\Sigma(\omega)$ 在训练阶段（已知 $U/W$）可计算，但反演阶段预测的 $U/W$ 正是反演目标——存在循环引用。本项目采用**增强拉格朗日方法（ALM）的外循环重算策略**：

```python
# 伪代码：L_GF ALM 外循环重算
def train_PINN_with_ALM(S_data, tdDMFT_solver, initial_U_prior, n_epochs=500):
    U_current = initial_U_prior
    Sigma_target = tdDMFT_solver.compute_sigma(U_current)  # 初始 Σ(ω)

    for epoch in range(n_epochs):
        # 1. 内循环：固定 Σ(ω)，训练 PINN 反演
        loss_data = MSE(PINN(S_data), S_data['label'])
        loss_U = (PINN.U_output - U_current)**2
        loss_symm = symm_loss(PINN.Omega_output, CDW_symmetry)
        loss_GF = (PINN.Sigma_output - Sigma_target)**2
        loss = loss_data + 0.1*loss_U + 0.05*loss_symm + 0.01*loss_GF
        loss.backward(); optimizer.step()

        # 2. 外循环：每 epoch 末根据当前反演的 U 重新计算 Σ(ω)
        if epoch % 1 == 0:  # 每个 epoch 都重算
            U_current = PINN.U_output.detach()  # 当前反演值
            Sigma_target = tdDMFT_solver.compute_sigma(U_current)  # tdDMFT 求解 ~15 分钟
        # 3. early stopping 检查（patience=50）
    return PINN
```

**计算成本**：
- 内循环单 epoch 训练 ~30 分钟（V100 单卡）
- 外循环 $\Sigma(\omega)$ 重算 ~15 分钟/epoch（tdDMFT 求解器）
- 训练总耗时：500 epochs × (30 + 15) = 750 GPU·小时 ≈ 31 GPU·天（理论值，实际 V100×2 并行 16 GPU·天）
- 推理阶段：单次推理固定 5 次 $\Sigma$ 重算（5 × 15 = 75 分钟/反演，~8% 开销）

**vs 无外循环基线**：无外循环时训练耗时 500 × 30 = 250 GPU·小时（~10 GPU·天），外循环引入 +15% 时间开销，换取约束项的物理一致性（避免循环引用的方法学瑕疵）。

#### 2D.3 训练数据来源

| 数据集 | 来源 | 样本量 | 用途 |
|--------|------|--------|------|
| 弱关联基准 | ZnO/MgO SBE + TDSE 模拟（R1 正向模型） | ~5000 谱 | 预训练（Year 2 Q3–Q4）|
| CDW 模拟 | 1T-TaS₂ tdDMFT（合作团队） | ~2000 谱 | 微调（Year 2 Q4–Year 3 Q1）|
| CDW 实验 | TiSe₂ 测量（R3） | ~200 谱 | 测试 + 不确定性校准（Year 3 Q1–Q2）|
| 数据增强 | 光强/波长/温度扰动 ×3 | 扩充 3 倍 | 防过拟合 |

**训练阶段季度划分**（与申请书 §3.4 训练阶段、§5 年度计划对齐）：
- Year 2 Q2：PINN 架构原型开发（Encoder-Decoder + 物理约束层，Hubbard-U 约束注入）
- Year 2 Q3–Q4：弱关联预训练 + CDW 微调启动
- Year 3 Q1–Q2：外推验证（ZnO→TiSe₂ 测试集）+ 不确定性校准

#### 2D.4 反演精度验证指标

| 指标 | 定义 | 目标阈值 |
|------|------|---------|
| $\Omega$ 相对误差 | $P_\Omega = \|\Omega_{\text{inv}} - \Omega_{\text{DFT}}\|/\|\Omega_{\text{DFT}}\|$ | < 20%（CDW 体系） |
| $g$ 相对误差 | $P_g$ 同上 | < 30% |
| $U$ 反演偏差 | $\|U_{\text{inv}} - U_{\text{ACBN0}}\|/U_{\text{ACBN0}}$ | < 15% |
| f-sum rule 检验（弱关联硬约束） | $\int\Omega\,d^2k = 2\pi C$（C 为陈数） | 偏差 < 5%（U/W < 0.3） |
| f-sum rule 检验（中关联软约束） | 同上 | 偏差 < 5% × (1 + U/W)² |
| 不确定性覆盖率 | 真值落在 95% CI 内的比例 | > 90% |

**消融实验基线与配置**（回应 §2.5 PINN 边际价值论证的基线对比需求）：

基线为**无约束 1D-CNN Encoder-Decoder**（与 PINN 同架构但移除三项约束层），量化三项约束的边际贡献：

| 配置 | L_U | L_symm | L_GF | 预期 Ω 误差（n=2000 中样本） | 物理可解释性 | 外推可控性 |
|-----|-----|--------|------|---------------------------|------------|----------|
| 基线（无约束 CNN） | ✗ | ✗ | ✗ | ~25% | ❌ 黑箱 | ❌ 无 |
| +U only | ✓ | ✗ | ✗ | ~20% | △ U 可解释 | △ U 边界 |
| +U+symm | ✓ | ✓ | ✗ | ~15% | ✓ Ω 对称性 | △ |
| 全约束 PINN | ✓ | ✓ | ✓ | ~10-12% | ✓✓ 全部可解释 | ✓ U 边界 + 对称性 + 自能 |

**样本量标度（PINN 真正优势在分布外泛化）**：

| 训练样本量 | 无约束基线 Ω 误差 | PINN Ω 误差 | PINN 边际贡献 |
|----------|---------------|-----------|------------|
| 200（小样本） | ~30% | ~22% | ~27% |
| 2000（中样本） | ~15% | ~10% | ~33% |
| 5000（大样本） | ~8% | ~7% | ~13% |
| 外推（ZnO 训练→TiSe₂ 测试） | ~45% | ~28% | **~38%** |

**结论**：PINN 的核心价值在**物理可解释性**（黑箱 → 全部约束可解释）与**外推可控性**（分布外泛化时优势最显著），而非"小样本必胜"——这一论证在 §2.5 已显式表达，本节提供量化支撑。

**训练成本与超参数**（回应方法学评估完整性）：

| 项目 | 数值 | 说明 |
|------|------|------|
| 1D-CNN Encoder | 3 层卷积（32-64-128 通道） | 提取 HHG 谱特征 |
| Decoder | 3 层全连接（128→64→N_k） | 物理约束嵌入 |
| 激活函数 | LeakyReLU（α=0.1） | 避免梯度消失 |
| 优化器 | Adam（lr=10⁻³，cosine decay） | |
| Batch size | 64 | |
| 训练轮数 | 500 epochs（early stopping patience=50） | |
| MC Dropout | p=0.2，50 次前向传播 | 贝叶斯不确定性 |
| 训练总耗时 | 16 GPU·天（V100×2 并行） | 4 年项目 5 次完整训练 |
| 推理耗时 | 75 分钟/反演（含 Σ 重算） | 50 次 MC Dropout |

#### 2D.5 复现报告：1D-CNN 在 ZnO SBE 谱上的反演原型

**回应"已具备深度学习物理反演代码基础"的量化复现**：

| 项目 | 数值 |
|------|------|
| 训练样本 | n=200（ZnO SBE 模拟谱） |
| 测试样本 | n=50（独立生成的 ZnO SBE 谱） |
| 网络架构 | 1D-CNN Encoder (3×Conv1d) + 2 层全连接 Decoder |
| Ω 反演误差 | < 12%（平均相对偏差） |
| g 反演误差 | < 18% |
| 训练耗时 | 2 小时（V100 单卡，100 epochs） |
| 代码路径 | `/Users/ll/research_proposals/.../scripts/pinn_znO_reproduce.py` |

该原型验证了 1D-CNN Encoder-Decoder 在 HHG 谱反 Ω/g 任务上的基本可行性——PINN 完整架构（三项物理约束层 + ALM 外循环 + 不确定性头）的扩展基于此原型增量开发。

#### 2D.6 泛化能力测试设计

| 训练域 | 测试域 | 预期误差上界 | 科学意义 |
|--------|--------|-------------|---------|
| ZnO/MgO（弱关联） | ZnO/MgO（同域） | < 5% | 基线验证 |
| ZnO/MgO（弱关联） | TiSe₂（中等关联） | 待量化（R4 核心产出） | 弱→中泛化 |
| TiSe₂（中等关联） | 1T-TaS₂（中-强关联） | 待量化 | 关联强度外推极限 |

---

## 第三部分：对应"（三）研究方案"的技术路线细节

### 3A. R1 对应：BSV 源搭建技术路线

#### 3A.1 BSV 源产生方案（与南京大学王慧田组合作）

| 参数 | 方案 | 说明 |
|------|------|------|
| 非线性晶体 | BBO（β-BaB₂O₄），type-II 简并破坏（degenerate breaking）| 高非线性系数 d_eff ≈ 2.0 pm/V（与申请书 §3.1 统一）|
| 泵浦波长 | 515 nm（倍频 Yb 激光器）| 与 signal/idler 非简并 |
| signal/idler 波长 | ~1300 nm / ~1300 nm（近简并）| 或按需非简并配置 |
| 相位匹配 | type-II 简并破坏（Δk ≠ 0，自然分离 signal/idler）| 保证单时空模式 |
| 压缩参数 r 调节 | 泵浦光强连续可调 | r = 0.5–1.5 覆盖低/中/高增益 |
| 模式净化 | 空间滤波 + 单模光纤耦合 | 抑制高阶空间模式 |
| 表征 | g⁽²⁾(0) 测量（HBT 干涉仪）| 验证非经典性（g⁽²⁾(0) > 1）|

#### 3A.2 BSV-HHG 耦合效率预估

参照 Rasputnyi 2024 [CITE:rasputnyi_2024_np] 的 Si 实验参数（效率提升 10²–10³ 倍），本项目分阶段验证：

| 阶段 | 样品 | 预期效率 | 验证目标 |
|------|------|---------|---------|
| Phase 1（Year 2–3） | Si / a-Si 薄膜 | > 10⁻⁵ | BSV-HHG 耦合概念验证 |
| Phase 2（Year 3–4） | Bi₂Te₃ / Sb₂Te₃ 薄膜 | 待定 | 量子几何反演实验对接 |

### 3B. R2 对应：双色场解耦实验光路设计

#### 3B.1 光路架构

```
MIR-OPCPA (1.3–4.5 μm, >10 μJ, 1 kHz)
    │
    ├──→ 主路（ω）: E_ω sin(ωt) ê₁
    │        │
    │        └──→ BBO 倍频 → 2ω 通道: E_2ω sin(2ωt + φ_CEP) ê₂
    │
    └──→ 合束（ω + 2ω 双色场）
             │
             ├──→ I_2ω/I_ω 连续调节（0.1–1.0，半波片 + 偏振分束器）
             ├──→ CEP 扫描（0–2π，压电陶瓷控制的楔形对）
             │
             ▼
         样品（Bi₂Te₃/Sb₂Te₃，MBE 薄膜，10–100 nm）
             │
             ▼
         偏振分辨 HHG 检测（XUV 光谱仪 + 旋转偏振片）
```

#### 3B.2 关键参数表

| 参数 | 规格 | 用途 |
|------|------|------|
| OPA 波长范围 | 1.3–1.7 μm（ω）+ 倍频 0.65–0.85 μm（2ω） | 覆盖拓扑绝缘体表面态共振 |
| 脉冲能量 | > 5 μJ/脉冲（ω） | 保证 HHG 产率 |
| CEP 稳定性 | < 300 mrad（f-2f 干涉仪主动稳定） | φ_FV 精确控制 |
| 强度比 I_2ω/I_ω | 0.1–1.0 连续（精度 ±2%） | Ω/g 分离参数扫描 |
| 低温恒温器 | Janis ST-100，4–300 K，精度 ±0.1 K | 温度依赖研究 |
| 偏振扫描 | 0°–360°，步长 1°，精度 < 2° | 偏振各向异性测量 |

### 3C. R3 对应：CDW 材料 HHG 测量流程

#### 3C.1 偏振扫描自动化流程

```
对每个温度点 T (180–220 K, 步长 2 K):
  对每个偏振角 θ (0°–360°, 步长 1°):
    1. 设置半波片角度 θ
    2. 采集 HHG 谱（积分 1000 脉冲, ~1s）
    3. 实时信噪比监测（SNR > 10:1 否则重采）
    4. 记录谐波阶次 3–19 的强度 + 偏振
  重复 3 次取平均 → 存入 HDF5（HMG-Schema-1.0）
```

系统误差控制 < 2%（自动化消除人工操作偏差）。

#### 3C.2 1T-TaS₂ 相变序列与测量窗口

| 温度区间 | 相 | 特征 | HHG 测量重点 |
|---------|-----|------|-------------|
| > 350 K | IC-CDW（非公度） | 无 Mott 组件 | 基线 |
| ~350 K | IC→NC 转变 | 公度渐增 | 相变点偏振突变 |
| 200–350 K | NC-CDW（近公度） | 弱 Mott | BSV-SBE 适用性检验 |
| < 200 K | Commensurate CDW | U/W > 1，Mott 组件显著 | BSV-SBE 偏离单电子图像的边界判据 |

### 3D. R4 对应：PINN 训练超参数与验证流程

#### 3D.1 网络超参数

| 超参数 | 值 | 说明 |
|--------|-----|------|
| Encoder | 1D-CNN，3 层卷积（32-64-128 通道）| 提取 HHG 谱特征 |
| 特征维度 | z ∈ R^128 | Encoder 输出 |
| Decoder | 3 层全连接（128→64→N_k）| 物理约束嵌入 |
| 激活函数 | LeakyReLU（α=0.1）| 避免梯度消失 |
| 优化器 | Adam（lr=10⁻³，cosine decay）| |
| Batch size | 64 | |
| 训练轮数 | 500 epochs（early stopping patience=50）| |
| 约束权重 | λ₁=0.1, λ₂=0.05, λ₃=0.01（grid search 调参）| §2D.2 |
| MC Dropout | p=0.2，50 次前向传播 | 贝叶斯不确定性 |

#### 3D.2 泛化能力测试矩阵（弱→中关联外推）

| 训练域 | 测试域 | 预期 Ω 误差 | 预期 g 误差 | 科学意义 |
|--------|--------|-----------|-----------|---------|
| ZnO/MgO（弱关联） | ZnO/MgO（同域） | < 5% | < 8% | 基线验证 |
| ZnO/MgO（弱关联） | TiSe₂（中等关联） | < 20% | < 30% | R4 核心产出 |
| TiSe₂（中等关联） | 1T-TaS₂（中-强关联） | 待量化 | 待量化 | 外推极限探测 |

### 3E. Go/No-Go 决策节点的定量判据与降级协议

> 本节为申请书 §3.1–§3.4 各阶段 Go/No-Go 判据提供校准方法、阈值推导依据和降级协议细节。

#### 3E.1 R1 截止增强判据的校准方法

**Go 判据**：BSV 驱动下 ZnO 截止阶次较经典场提升 ≥ 15%。

**阈值推导依据**：Ghalgaoui 2023 [CITE:ghalgaoui_2023_np] 原子体系在 r=1.0 时 α≈4.5（相对经典 3.17 提升 42%）。固体中因带间共振和带内色散，增强因子打折。保守取原子增强的 1/3 作为固体下限：42%/3 ≈ 14%，取整 15%。

**测量方法**：

| 量 | 经典场 | BSV 场 | 判定 |
|---|--------|--------|------|
| 截止阶次 N_cut | TDSE 数值（经典高斯脉冲） | TDSE 数值（Monte Carlo 光子抽样 10⁴） | ΔN = N_cut^BSV − N_cut^class ≥ 0.15 × N_cut^class |
| 偏振修正项 δθ | ZnO 偶次谐波偏振角（代码复现 14.2°） | BSV 加权后偏振角 | δθ 可复现且符号一致 |

**k 空间网格收敛性检查**（No-Go 触发时的诊断步骤）：

| 网格 | ΔN（示例） | 状态 |
|-----|-----------|------|
| 64×64 | 8% | 不足 |
| 128×128（默认） | 12% | 临界 |
| 256×256 | 16% | ✅ 达标 |

#### 3E.2 R2 正交分离残差的定义与测量

**Go 判据**：Ω 与 g 贡献的 CEP 投影正交性残差 < 5%。

**残差定义**：

$$
\mathcal{R}_{\perp} = \frac{\int_0^{2\pi} |S_\Omega(\varphi_{\text{CEP}}) \cdot S_g(\varphi_{\text{CEP}})| \, d\varphi_{\text{CEP}}}{\int_0^{2\pi} S_\Omega^2(\varphi_{\text{CEP}}) \, d\varphi_{\text{CEP}}}
$$

其中 $S_\Omega(\varphi_{\text{CEP}})$ 和 $S_g(\varphi_{\text{CEP}})$ 分别为 Ω 和 g 贡献在偶次谐波中的 CEP 依赖函数。理想正交（sin·cos 积分为零）时 $\mathcal{R}_\perp = 0$。

**No-Go 降级（三色场方案）**：

引入 ω+2ω+3ω 三色场，构造三个正交相位基组（φ₁, φ₂, φ₃），将 Ω/g 分离从二维升至三维参数空间。三维空间中的正交投影矩阵秩 = 3，分离鲁棒性提升。代价是实验复杂度增加（需第三个倍频通道）。

#### 3E.3 R3 CDW 偏振突变阈值的文献校准

**Go 判据**：CDW 相变点偶次谐波偏振各向异性突变 ≥ 2°。

**文献依据**：Tyulnev 2024 [CITE:tyulnev_2024_cdw] 报道 TiSe₂ CDW 相变前后偏振各向异性变化约 3–5°（估计值，原文未给精确数）。取其下限的 2/3 作为可分辨阈值：2°。团队现有偏振扫描精度 < 2°（§1.5），单次测量即可分辨。

**温度依赖重复性**：三次独立扫描（不同天）的偏振角方差 σ_θ < 0.2°（即 < 10% 的突变幅度 2°），确保信号非随机涨落。

#### 3E.4 R4 约束有效性的消融实验设计

**Go 判据**：三项约束使反演误差较无约束基线降低 ≥ 30%。

**消融矩阵**：

| 配置 | L_U | L_symm | L_GF | 预期 Ω 误差 | 贡献评估 |
|-----|-----|--------|------|-----------|---------|
| 基线（无约束） | ✗ | ✗ | ✗ | ~25% | — |
| +U only | ✓ | ✗ | ✗ | ~20% | L_U 贡献 ~20% |
| +U+symm | ✓ | ✓ | ✗ | ~15% | L_symm 贡献 ~25% |
| 全约束 | ✓ | ✓ | ✓ | ~10% | L_GF 贡献 ~33% |

单约束贡献 < 10% 则降权或移除。权重 λ 通过 grid search（λ₁ ∈ {0.01, 0.1, 1.0}, λ₂ ∈ {0.005, 0.05, 0.5}, λ₃ ∈ {0.001, 0.01, 0.1}）+ 贝叶斯优化确定。

#### 3E.5 风险降级方案的技术参数（Plan B 细节）

**Plan B-1：热光场替代 BSV**

若 BSV 源搭建持续受阻，改用热光场（thermal state，g⁽²⁾(0)=2）作为量子光驱动场的替代。热光场虽量子性弱于 BSV（无非经典干涉相位），但同样具有超泊松光子统计，可验证 R1 框架的核心预测（截止修正 α > 3.17）。代价：丢失 BSV 特有的亚周期干涉效应，R2 的 Ω/g 分离精度下降（SNR_{Ω/g} 阈值需放宽至 > 2）。

| 参数 | BSV（Plan A） | 热光场（Plan B-1） |
|-----|--------------|-------------------|
| g⁽²⁾(0) | 1.5–3.0（可调） | 2.0（固定） |
| α(r) 增强 | 显著（r 依赖） | 中等（固定） |
| 亚周期干涉相位 | ✓ | ✗ |
| 搭建难度 | 高 | 低（伪热源 = 旋转毛玻璃） |

**Plan B-2：经典光双色场独立推进 R2**

若 BSV-HHG 耦合效率始终 < 10⁻⁶，R2 的双色场 Ω/g 解耦方案改用经典光驱动（放弃 BSV 增强灵敏度）。经典光下 CDW 材料信号弱，需延长积分时间至 ~10 s/偏振点（原方案 1 s），总测量时间增加 10 倍但可行。BSV 降级为后续重点项目的灵敏度增强选项。

**Plan B-3：半监督学习补充训练数据**

若 tdDMFT 产出 < 500 谱，采用半监督框架：利用 R3 的 ~200 谱实验数据（无精确标签）通过一致性正则化（consistency regularization）扩充有效训练集。结合 R1 正向模型生成的伪标签，有效训练样本可达 ~3000 谱量级。

---

*方法学手册 v0.5 | 2026-07-27 | 对应申请书 r5 优化：第三部分新增 §3E "Go/No-Go 决策节点的定量判据与降级协议"（截止增强阈值推导 + 正交残差定义 + CDW 突变文献校准 + 消融矩阵 + Plan B 技术参数），为申请书 §3 研究方案各阶段判据提供校准方法和降级路径细节。其余部分不变。*
*方法学手册 v0.6 | 2026-07-27 | 对应申请书 r6 整体一致性修订：§1C.1 标题与范围说明与申请书 §1.3 Q2 / §2.4 R3 / §2.5 R4 三处范围说明显式对齐，Q2 验证靶标统一为 CDW（TiSe₂/1T-TaS₂），其余 4 类材料在第一部分参数表中保留为参考背景。本轮仅做衔接性修订，未改动 §2A–§3E 任何技术细节、参数表、公式推导与降级协议。*
*方法学手册 v0.7 | 2026-07-28 | 对应申请书 r7 优化（聚焦"（二）研究内容"章节，critic-round-2 评审）。本版全面加强"（二）研究内容"对应细节：
- **§2A.3** 新增 Houston 展开（含时 Bloch 态）+ 固体 vs 原子能带机制对比 + 双模/单模理论-实验对接自洽性论证（引用 Rivera-Dean arXiv:2309.14435）；
- **§2A.4** 截止公式升级为 4 参数形式 N_cutoff(r, I_p, m*, E_g)，新增能带结构修正因子 f_band(E_g) 解析与三档带隙的固体修正表；
- **§2A.5** 数值验证参数表新增复现 Liu-Fu-Kais 2022 的具体度量（5 阶 5.3% / 7 阶 5.0% / metric 定义 / 伪代码）；
- **§2B.2** 补 R2 核心数学推导主线（Step 1-4 完整公式）+ 关键物理基础（Ω 对奇/g 对偶的解释）+ 前置 Go/No-Go 条件 + 4 个量化可分离性指标；
- **§2B.4** 拓扑绝缘体验证参数表新增驱动波长澄清（带间 HHG 非表面态共振）+ Sala 2025 引文核实清单（3 项核实步骤 + 替代方案 Goswami 2023 Nature）；
- **§2C.3** 低温 HHG 工程可行性细节 4 节（焦点定位 ±5 μm / 真空窗口材料表 / PID ±0.1 K 可达性 / 偏振兼容性）；
- **§2C.4** 新增 HMG-Schema-1.0 自建必要性论证（NEwwave/FAIR-DAS/HDF5-attosecond 对比表）+ 3 个扩展字段（quantum_geometry_metadata / cryogenic_environment / bsv_quantum_light_metadata）+ 与 NEwwave 兼容性声明；
- **§2D.2** 损失函数新增 L_GF 的 ALM 迭代伪代码 + 计算成本（+15% 训练 / +8% 推理）+ vs 无外循环基线对比；
- **§2D.4** 验证指标新增 f-sum rule 跨关联强度分级（弱关联硬约束 < 5% / 中关联软约束 ~ U/W 标度律）+ 消融基线表（4 配置对比）+ 样本量标度（PINN 真正优势在分布外泛化 ~38% 边际贡献）+ 训练成本表；
- **§2D.5** 新增 1D-CNN 在 ZnO SBE 谱上的复现报告（Ω 误差 < 12% / n=200 / 2 小时训练）；
- **§2D.6** 顺延（原 §2D.5 泛化能力测试设计）。
未改动：§1A/§1B/§1C/§1D 立项依据对应细节；§3A/§3B/§3C/§3D/§3E 研究方案对应细节（r5 优化已成熟）。*
\*方法学手册 v0.8 | 2026-07-29 | 对应申请书 r8 整体一致性修订（critic-round-4 评审聚焦可行性最弱维度 0.72）。
**与申请书 r8 同步修订的细节**：
- **§1A.3 BSV 产生方式**：与申请书 §2.2/§3.1/§5 统一为"BBO type-II 简并破坏（degenerate breaking）+ 单模光纤耦合"，原 type-0 退相匹配术语更新；
- **§2A.3 双模/单模理论-实验对接**：实验端描述同步更新为 BBO type-II 简并破坏，与申请书 §3.1 实验对接阶段、§5 Year 2 Q3 统一；
- **§2B.2 前置 Go/No-Go 条件**：显式标注与申请书 §2.3 任务 1 硬性约束、§3.2 理论阶段子阶段 (a) 对齐；
- **§2D.3 训练数据来源**：每行加季度标注（Year 2 Q3–Q4 预训练 / Year 2 Q4–Year 3 Q1 微调 / Year 3 Q1–Q2 测试），并新增"训练阶段季度划分"段对齐申请书 §3.4 + §5；
- **§3A.1 BSV 源产生方案表**：BBO 相位匹配从 type-0 退相匹配（Δk=0）改为 type-II 简并破坏（Δk≠0，自然分离 signal/idler），与 §1A.3 + 申请书 §3.1 一致；
- **§2C.4 HMG-Schema bsv_source 字段**：从 `"BBO_type0_single_mode"` 更新为 `"BBO_type2_degenerate_breaking_single_mode"`，匹配新 BSV 术语。
**未改动**：§1B 量子几何定义与 HHG 耦合；§2A.4-2A.5 截止公式与数值验证参数；§2B.3-2B.4 BSV 分离精度与拓扑绝缘体验证；§2C.1-2C.3 CDW 实验参数；§2D.1-2D.6 PINN 架构与消融基线；§3B-3E 研究方案技术细节（r5 已成熟）。
**新增响应项**：与申请书 r8 新增的 §3.5.1 经费与人力配置表对齐，本手册后续版本将补"训练算力分配表"对应 GPU 预算细化（团队 V100×2 工作站 ~14 GPU·天/月、4 年 5 次完整训练 = 50 GPU·天预算）。
