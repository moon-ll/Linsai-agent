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
| BSV 产生方式 | BBO 晶体退相匹配（type-0） | 单时空模式 |
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

#### 2A.4 截止频率修正推导

经典截止：$N_{\text{cutoff}}^{\text{classical}} \hbar\omega \approx I_p + 3.17\,U_p$，$U_p = e^2E_0^2/(4m_r\omega^2)$。

BSV 修正：由于 $P(n)$ 为超泊松分布，高 $n$ 尾部增强，等效光强 $\langle I^2\rangle/\langle I\rangle > \langle I\rangle$。定义增强因子：

$$
\alpha(\hat\rho) = \frac{\langle \hat{E}^2\rangle}{\langle \hat{E}\rangle^2} \cdot 3.17 \quad\Longrightarrow\quad N_{\text{cutoff}}^{\text{BSV}} \approx \frac{I_p + \alpha(r)\,U_p}{\hbar\omega},\quad \alpha(r) > 3.17
$$

| r | $\alpha(r)$（Ghalgaoui 2023 原子） | 预期固体修正 |
|---|------|------|
| 0 | 3.17（经典） | 无修正 |
| 0.5 | ~3.5 | 轻微 |
| 1.0 | ~4.5 | 显著（截止上移 ~30%） |
| 1.5 | ~6.0 | 强烈（Rasputnyi 2024 实验区间） |

注：固体中需额外考虑带间共振和带内色散对 $\alpha(r)$ 的修正，这是 R1 的核心推导任务。

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

---

### 2B. R2 对应：双色场 Ω/g 解耦的定量条件

#### 2B.1 Floquet-Volkov 干涉相位

ω + 2ω 双色场 $\mathbf{E}(t) = E_\omega\sin(\omega t)\hat{e}_1 + E_{2\omega}\sin(2\omega t + \varphi_{\text{CEP}})\hat{e}_2$ 下的 Volkov 相位：

$$
\phi_{FV}(t) = \int_0^t \left[\sqrt{I_{2\omega}}\sin(2\omega t' + \varphi_{\text{CEP}}) + \sqrt{I_\omega}\sin(\omega t')\right] dt'
$$

展开后含 $\sin(\omega t)$、$\cos(\omega t)$、$\sin(2\omega t)$、$\cos(2\omega t)$ 及交叉项 $\sin(\omega t)\cos(2\omega t + \varphi_{\text{CEP}})$，交叉项携带 CEP 依赖。

#### 2B.2 Ω 与 g 贡献的相位依赖分离

在偶次谐波（2Nω）的偏振分量中：

| 几何量 | 进入通道 | 相位依赖 | 在 (I₂ω/I_ω, CEP) 空间的特征 |
|--------|---------|---------|-----|
| $\Omega(\mathbf{k})$ | 异常速度 $\mathbf{v}_\perp = (e/\hbar)\Omega\times\mathbf{E}$ | $\sim\sin(\phi_{FV})$ | 奇函数于 CEP = π |
| $g(\mathbf{k})$ | 重叠积分 $\langle u_{n,\mathbf{k}(t)}|u_{n,\mathbf{k}_0}\rangle$ | $\sim\cos(\phi_{FV})$ | 偶函数于 CEP = π |

利用正交性：

$$
\int_0^{2\pi}\sin(\phi_{FV})\cos(\phi_{FV})\,d\varphi_{\text{CEP}} = 0
$$

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
| $\Omega(\mathbf{k})$ 结构 | Rashba 型，峰值离 Γ ~0.1 Å⁻¹ | 同类 | Sala 2025 [CITE:sala_2025_qmetric] |
| 薄膜厚度 | 10–100 nm（MBE） | 同左 | 合作者（物理所） |
| 驱动波长 | 1.5 μm（近表面态共振） | 同左 | 团队 OPCPA |
| 双色场强度比 $I_{2\omega}/I_\omega$ | 0.1–1.0 连续扫描 | 同左 | OPA + 倍频 |

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

#### 2C.3 HMG-Schema-1.0 元数据字段定义

```json
{
  "schema_version": "1.0",
  "material": {
    "formula": "TiSe2",
    "crystal_structure": "1T-CdI2 type",
    "orientation": "(001) cleaved",
    "xrd_verified": true
  },
  "laser_params": {
    "wavelength_um": 3.0,
    "intensity_W_cm2": 2.0e11,
    "pulse_duration_fs": 45,
    "cep_rad": null,
    "repetition_rate_Hz": 1000
  },
  "measurement": {
    "temperature_K": 200.0,
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

$$
\mathcal{L} = \underbrace{\|\hat{I}_{\text{HHG}} - I_{\text{meas}}\|_2^2}_{\mathcal{L}_{\text{data}}}
+ \lambda_1\underbrace{\|U_{\text{inv}} - U_{\text{DFT}}\|^2}_{\mathcal{L}_U}
+ \lambda_2\underbrace{\|\text{Symm}(\Omega_{\text{inv}}) - \text{Symm}_{\text{prior}}\|^2}_{\mathcal{L}_{\text{symm}}}
+ \lambda_3\underbrace{\|\Sigma_{\text{inv}}(\omega) - \Sigma_{\text{DMFT}}(\omega)\|^2}_{\mathcal{L}_{\text{GF}}}
$$

| 约束项 | 物理含义 | 先验来源 | 初始权重 |
|--------|---------|---------|---------|
| $\mathcal{L}_U$ | Hubbard-U 反演值匹配 DFT/ACBN0 | 合作团队计算 | $\lambda_1 = 0.1$ |
| $\mathcal{L}_{\text{symm}}$ | Ω(k) 对称性匹配 CDW 相变群 | 空间群分析 | $\lambda_2 = 0.05$ |
| $\mathcal{L}_{\text{GF}}$ | 自能函数匹配 DMFT | tdDMFT 合作 | $\lambda_3 = 0.01$ |

权重 $\lambda_i$ 通过 validation loss 自动调参（grid search + 贝叶斯优化）。

#### 2D.3 训练数据来源

| 数据集 | 来源 | 样本量 | 用途 |
|--------|------|--------|------|
| 弱关联基准 | ZnO/MgO SBE + TDSE 模拟（R1 正向模型） | ~5000 谱 | 预训练 |
| CDW 模拟 | 1T-TaS₂ tdDMFT（合作团队） | ~2000 谱 | 微调 |
| CDW 实验 | TiSe₂ 测量（R3） | ~200 谱 | 测试 + 不确定性校准 |
| 数据增强 | 光强/波长/温度扰动 ×3 | 扩充 3 倍 | 防过拟合 |

#### 2D.4 反演精度验证指标

| 指标 | 定义 | 目标阈值 |
|------|------|---------|
| $\Omega$ 相对误差 | $P_\Omega = \|\Omega_{\text{inv}} - \Omega_{\text{DFT}}\|/\|\Omega_{\text{DFT}}\|$ | < 20%（CDW 体系） |
| $g$ 相对误差 | $P_g$ 同上 | < 30% |
| $U$ 反演偏差 | $\|U_{\text{inv}} - U_{\text{ACBN0}}\|/U_{\text{ACBN0}}$ | < 15% |
| f-sum rule 检验 | $\int\Omega\,d^2k = 2\pi C$（C 为陈数） | 偏差 < 5% |
| 不确定性覆盖率 | 真值落在 95% CI 内的比例 | > 90% |

#### 2D.5 泛化能力测试设计

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
| 非线性晶体 | BBO（β-BaB₂O₄），type-0 退相匹配 | 高非线性系数 d_eff ≈ 2.0 pm/V |
| 泵浦波长 | 515 nm（倍频 Yb 激光器） | 与 signal/idler 非简并 |
| signal/idler 波长 | ~1300 nm / ~1300 nm（近简并） | 或按需非简并配置 |
| 相位匹配 | 退相匹配（Δk = 0, Δk' = 0） | 保证单时空模式 |
| 压缩参数 r 调节 | 泵浦光强连续可调 | r = 0.5–1.5 覆盖低/中/高增益 |
| 模式净化 | 空间滤波 + 单模光纤耦合 | 抑制高阶空间模式 |
| 表征 | g⁽²⁾(0) 测量（HBT 干涉仪） | 验证非经典性（g⁽²⁾(0) > 1） |

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
*方法学手册 v0.6 | 2026-07-27 | 对应申请书 r6 整体一致性修订：§1C.1 标题与范围说明与申请书 §1.3 Q2 / §2.4 R3 / §2.5 R4 三处范围说明显式对齐，Q2 验证靶标统一为 CDW（TiSe₂/1T-TaS₂），其余 4 类材料在第一部分参数表中保留为参考背景。本轮仅做衔接性修订，未改动 §2A–§3E 任何技术细节、参数表、公式推导与降级协议。
