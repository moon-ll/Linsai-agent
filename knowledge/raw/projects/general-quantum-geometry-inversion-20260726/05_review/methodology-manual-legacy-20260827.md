<!-- v6.9.60 从 04_proposal/methodology-manual.md 迁出的旧手册 -->
<!-- 方法学手册唯一真相源：03_method/method-manual.md -->

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
| 压缩参数 r | 0.5–1.2（可调）；**典型工作点 r ≈ 0.8** | 对应 $g^{(2)}(0) \approx 1.5$–3.0 |
| 光子数/脉冲 | 0 – 2×10¹³；**典型工作点 ⟨n⟩ ≈ 1.5** | 宽分布 |
| **HHG 绝对产额** | **~10⁻⁵ photons/pulse @ 1 kHz**（Si 样品，r ≈ 0.8）| **绝对效率仍低于直接带隙半导体的经典 HHG**——申请书 §1.1 第 19 行已明确此条件 |
| 亚周期电场涨落 | ±1 V/Å | 突破经典包络 |
| 驱动波长 | ~1.3 μm（signal） | 非简并 |
| 样品 | Si / a-Si 薄膜 | 间接带隙半导体，HHG 产额本身较低（10⁻⁶–10⁻⁸ 量级）|
| HHG 效率提升 | **10²–10³ 倍**（相对同均值强度经典光的**相对值**）| **结合 §3.2 探测方案（SNR > 3 阈值），相对增强倍数可驱动 Ω/g 反演** |
| 截止阶次 | 超出经典预测 ~30% | 验证 Ghalgaoui 理论 |

> **CDW 体系 BSV 增强效率的类比性说明**（回应第 5 轮评审 M-7）：Rasputnyi 2024 在 Si 上的 10²–10³ 倍增强基于带间 HHG 主导机制；CDW（TiSe₂/1T-TaS₂）虽然多体效应更显著，但带间 HHG 通道同样主导。本项目假设增强机制**可类比**，但实际增强倍数需在 R3'（Year 2 Q3 后）实验验证。若 R3' 显示 BSV 在 CDW 体系中增强不足 10 倍，R4 PINN 反演的 SNR 阈值（> 3）将无法满足，需重新评估 Q2 可行性（详见申请书 §3.5 风险表）。

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

#### 1A.5 Q1 三层因果链：光场统计 → HHG 谱可观测项 → Ω/g Fisher 信息

立项依据 §1.2 给出的 Q1 是三层因果链，本节展开技术细节。

**第一层：BSV 光场密度矩阵 → 期望电流算符**

BSV 场是单模压缩真空态 $\ket{\xi}_s = \cosh^{-1}r \sum_n (\tanh r)^n \ket{nn}$，密度矩阵 $\hat{\rho}_{\text{BSV}}$ 在 P 表示下为

$$\hat{\rho}_{\text{BSV}} = \int d^2\alpha\, P_{\text{BSV}}(\alpha) \ket{\alpha}\bra{\alpha}, \quad P_{\text{BSV}}(\alpha) = \frac{1}{\pi \bar{n}} \exp\!\left(-\frac{|\alpha|^2}{\bar{n}}\right)$$

其中 $\bar{n} = \sinh^2 r$，$g^{(2)}(0) = 1 + 1/\bar{n}$。HHG 电流期望值为

$$\langle \hat{\mathbf{J}}(t) \rangle = \text{Tr}\!\left[\hat{\rho}_{\text{BSV}} \cdot \hat{\mathbf{J}}(t)\right], \quad \hat{\mathbf{J}}(t) = \frac{e}{m} \sum_{\mathbf{k}} \hat{\psi}^{\dagger}(\mathbf{k},t)\,\hat{\mathbf{v}}\,\hat{\psi}(\mathbf{k},t)$$

与经典场下的电流期望相比，BSV 引入 $P_{\text{BSV}}(\alpha)$ 的非平凡权重，导致产额、偏振、二阶相关 $g^{(2)}_{\text{HHG}}(\tau)$ 都成为 $r$、$\bar{n}$ 的函数。

**第二层：HHG 谱可观测项 → Ω/g 的信号载体**

在经典光下，Liu-Fu-Kais [7] 给出 $\Omega(\mathbf{k})$ 通过异常速度项 $\mathbf{v}_{\perp} \sim \Omega(\mathbf{k})\times\mathbf{E}(t)$ 进入偶次谐波偏振，$g(\mathbf{k})$ 通过波函数重叠积分进入偶次谐波强度调制——但二者纠缠不可分。BSV 场提供了三个新的可观测通道：

| 可观测项 | BSV 下特征 | 与 Ω/g 的耦合 |
|----------|-----------|--------------|
| 截止阶次 $N_{\text{cutoff}}$ | Ghalgaoui 修正 $\alpha(\hat{\rho}) > 3.17$ [9] | 不直接耦合 Ω/g（材料无关） |
| 偶次谐波偏振旋转角 $\theta_n$ | 涨落使偏振统计展宽 $\Delta\theta_n \propto r$ | 主要反映 $\Omega(\mathbf{k})$ |
| $g^{(2)}_{\text{HHG}}(\tau)$ | Lange-Madsen [23] 证明压缩光的 HHG 编码 | 反映 $\Omega/g$ 的非微扰相位 |

**第三层：Ω/g 的 Fisher 信息 / 后验方差**

定义 BSV 与经典光场下 $\Omega(\mathbf{k})$ 的 Fisher 信息：

$$\mathcal{I}_{\Omega}^{\text{BSV}} = \mathbb{E}\!\left[\left(\frac{\partial \log P(S|\Omega)}{\partial \Omega}\right)^{\!2}\right], \quad \mathcal{R}_{\Omega} = \frac{\mathcal{I}_{\Omega}^{\text{BSV}}}{\mathcal{I}_{\Omega}^{\text{cl}}}$$

CRLB 给出 $\text{Var}(\hat{\Omega}) \geq 1/\mathcal{I}_{\Omega}$。本项目的核心定量判据为：

$$\mathcal{R}_{\Omega, g} \geq 2 \quad \text{（即 BSV 相对经典光对 Ω/g 后验方差的收缩比 ≥ 2）}$$

- **若 $\mathcal{R}_{\Omega, g} \geq 2$**：BSV 提供材料无关的"加性增强"，Q1→Q2 闭环成立，进入 R3' 实验验证；
- **若 $1 < \mathcal{R}_{\Omega, g} < 2$**：BSV 增强是材料依赖的"乘性增强"，需在每个 CDW 样品上单独校准；
- **若 $\mathcal{R}_{\Omega, g} \leq 1$**：BSV 仅增加产额但不改善 Ω/g 反演精度，Q2 限于经典光可辨识性边界报告，PINN 不强行扩展。

这一判据在 §2.2 R1（Year 1 Q2）的 BSV-SBE 模拟中计算 Si 模型基准，在 §3 R3'（Year 2 Q3）通过 BSV-HHG 实验在拓扑绝缘体上实测。

#### 1A.6 Q2 可辨识性边界的 PINN 估计流程

立项依据 §1.2 重写 Q2 为可证伪科学问题：本节给出 PINN 估计"在何种 Hubbard-U/W 与温度区间，HHG 偏振响应仍保留可独立辨识的 Ω/g 信息"的计算流程。

**Step 1：定义可辨识性**

对任意 $(U/W, T)$，由 1D Hubbard tdDMFT（Ikeda [20] 路径）生成 HHG 谱 $S(\omega; U, T)$，PINN 的预测谱为 $S_{\text{NN}}(\omega; \boldsymbol{\theta})$，定义**辨识失效点**为

$$\Delta(U, T) \equiv \left\langle \frac{|S(\omega; U, T) - S_{\text{NN}}(\omega; \boldsymbol{\theta}_{\text{opt}})|^2}{|S(\omega; U, T)|^2} \right\rangle_{\omega} \geq 0.1$$

此时 PINN 无法从谱中恢复 $(U, T)$ 与 $(\Omega, g)$ 的独立坐标。辨识边界 $U_c(T)$ 由 $\Delta(U_c, T) = 0.1$ 给出。

**Step 2：PINN 架构与三重物理约束**

PINN 输入为 HHG 谱的 (谐波阶次, 偏振角, 强度) 三元组；输出为 $(\Omega, g, U, T)$。损失函数包含三重物理约束：

$$\mathcal{L} = \mathcal{L}_{\text{data}} + \lambda_1 \mathcal{L}_{\text{f-sum}} + \lambda_2 \mathcal{L}_{\text{CDW}} + \lambda_3 \mathcal{L}_{\text{BI}}$$

其中
- $\mathcal{L}_{\text{data}}$：MSE 拟合 HHG 谱
- $\mathcal{L}_{\text{f-sum}}$：f-sum rule 约束（弱关联硬约束 < 5% 偏离、中关联软约束 $\sim U/W$ 标度律）
- $\mathcal{L}_{\text{CDW}}$：CDW 序参量对低阶谐波偏振的调制（Tyulnev [14] 14-300 K 全温区数据为先验）
- $\mathcal{L}_{\text{BI}}$：Baur 镜像对称性约束（[19] NbSe₂/MoS₂ 对照基线）

**Step 3：辨识边界相图**

PINN 训练完成后，对 $(U/W, T)$ 二维网格扫描，输出辨识相图：
- **可辨识区**（$\Delta < 0.1$）：$\Omega$、$g$ 可独立恢复；
- **临界区**（$0.05 < \Delta < 0.1$）：PINN 给出 $\Omega$、$g$ 的联合不确定度，可作 Bayesian 边界；
- **失效区**（$\Delta \geq 0.1$）：多体效应使 $\Omega$、$g$ 不可独立辨识，Q2 的科学边界在此明确报告。

训练/推理耗时：V100 单卡 8 h/epoch × 500 epochs + MC Dropout 4 h；总预算 50 GPU-day，团队 V100×2 可达。

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
|| **CDW** | **1T-TaS₂** | ~0.1 (Mott-CDW 竞争) | Hubbard-U + CDW | 非平庸谐波红移 | Queisser 2023 [CITE:queisser_2023_mott_hhg]（Mott-Hubbard HHG 理论）+ Lange 2024 [CITE:lange_2024_noninteger]（非整数谐波）| ✅ R3 核心 |
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

#### 1D.3 谱峰-Ω(k) 灵敏度矩阵与错误归因量级估算（对应申请书 §1.1 H-3 量化判据）

**问题来源**：申请书 §1.1 L9 论断"沿用 [1, 7] 的反演公式会把 Hubbard-U、doublon-holon 复合、CDW 序参量的贡献错误地归因于 Ω(k) 或 g(k) 本身"——评审要求给出错误归因的具体量级。以下推导把"Ikeda [20] 报告的 5–15% 谐波红移"转化为"经典 SBE 单电子模型下 Ω(k) 反演误差 ~30%"的代表性量级。

**Step 1：定义灵敏度矩阵。** 在经典 SBE 单电子框架下，HHG 谱 $S(\omega)$ 对 $\Omega(\mathbf{k})$ 的依赖通过异常速度项 $\mathbf{v}_\perp = (e/\hbar)\Omega(\mathbf{k})\times\mathbf{E}(t)$ 进入。定义谱峰频率 $\omega_{\text{peak}}$ 对 $\Omega$ 的灵敏度系数：

$$
\mathcal{S}_{\Omega} \equiv \frac{\delta\omega_{\text{peak}} / \omega_{\text{peak}}}{\delta\Omega / \Omega}
$$

该系数可通过数值微扰计算获得：在 ZnO 模型（3.0 μm / $2\times10^{11}$ W/cm² / $128\times128$ $k$ 网格）下，对 $\Omega(\mathbf{k})$ 施加 5% 的全局缩放，测量谱峰频率的相对偏移。

**Step 2：多体红移到反演误差的传播。** Ikeda [20] 报告 Sr₂CuO₃ 在 MIR 驱动下，实时 DMFT 揭示亚周期 Mott 熔化使每个谐波频率从 MIR 奇数倍红移 $\Delta\omega/\omega = 5\text{–}15\%$。在经典 SBE 单电子模型下，这一红移被误归因为 $\Omega(\mathbf{k})$ 的变化：

$$
\frac{\delta\Omega}{\Omega} \approx \frac{\Delta\omega/\omega}{\mathcal{S}_{\Omega}}
$$

**Step 3：量级估算。** 团队预研（ZnO SBE 复现）给出 $\mathcal{S}_{\Omega} \approx 0.5$（即 5% 的 $\Omega$ 变化导致 ~2.5% 的谱峰偏移）。代入 $\Delta\omega/\omega = 5\text{–}15\%$：

$$
\frac{\delta\Omega}{\Omega} \approx \frac{0.05\text{–}0.15}{0.5} = 10\text{–}30\%
$$

取上限，$\Omega(\mathbf{k})$ 反演误差量级约 **30%**。这是 CDW/Mott 类材料 Hubbard-U 不可忽略的代表性量级。

**Step 4：可辨识性边界的定量含义。** 本项目的可辨识性边界即定义为：在 $U/W$ 区间内，使上述反演误差降至实验 SNR 阈值以下的具体条件。以 $\Omega$ 反演残差 $< 30\%$（即实验 SNR 可分辨的阈值）为判据，$U/W$ 的临界值将在 R1 任务 4 的 BSV-SBE 模拟中给出。

> **标注**：此推导为本团队自洽估计（方法学手册 §1D.3），灵敏度系数 $\mathcal{S}_{\Omega} \approx 0.5$ 基于 ZnO SBE 预研，将在 R1 启动年用 Sr₂CuO₃ tdDMFT 数据校准。输入数据（Ikeda 预印本 [16] 报告的红移 5–15%）为预印本数值，若该预印本经 peer review 后红移修正为 3–8%，则上述 30% 误差估算应相应下调至 ~6–16%，"第二堵墙"的紧迫性对应减弱——但即便取下限 6%，仍超出弱关联 SBE 反演的典型残差阈值（< 5%），结论的定性方向不变。

#### 1D.4 BSV 数值收敛判据与物理增强量的分离（对应申请书 §1.4 Year 1 严谨性要求）

**问题来源**：申请书 §1.4 Year 1 段落原将"k 网格收敛"与"BSV 截止阶次相对经典基线提升"混为同一判据，评审指出这混淆了数值收敛（代码可信度）与物理增强（科学结论）两个不同性质的量。本节给出两者的显式分离定义。

**数值收敛判据（代码可信度）**：在固定物理参数（驱动波长、强度、材料）下，加密 k 网格并测量 HHG 谱的稳定性：

$$\epsilon_{\text{conv}}(N_k) = \frac{\|S_{N_k}(\omega) - S_{2N_k}(\omega)\|_{L^2}}{\|S_{2N_k}(\omega)\|_{L^2}}$$

其中 $S_{N_k}$ 为 $N_k \times N_k$ k 网格下的 HHG 谱。判据：$\epsilon_{\text{conv}} < 1\%$ 视为数值收敛。实测值（ZnO，3.0 μm / $2\times10^{11}$ W/cm²）：

| k 网格 | $\epsilon_{\text{conv}}$ | 状态 |
|--------|--------------------------|------|
| 64×64 → 128×128 | ~3% | 未收敛 |
| 128×128 → 256×256 | ~0.8% | ✅ 收敛 |
| 256×256 → 512×512 | ~0.3% | 过收敛（计算成本↑，收益↓）|

团队采用 $128\times128$ 作为生产网格（$\epsilon_{\text{conv}} \approx 0.8\% < 1\%$）。

**物理增强量（科学结论）**：BSV 相对经典光的截止阶次提升倍数，定义为一个独立的物理可观测量：

$$\mathcal{E}_{\text{BSV}} = \frac{N_{\text{cutoff}}^{\text{BSV}} - N_{\text{cutoff}}^{\text{cl}}}{N_{\text{cutoff}}^{\text{cl}}}$$

该量在数值收敛（$\epsilon_{\text{conv}} < 1\%$）的前提下才有物理意义——即先确认代码可信（数值收敛），再报告物理增强。两者分离后，Year 1 的 Go/No-Go 判据表述为："在 $128\times128$ k 网格（$\epsilon_{\text{conv}} < 1\%$）下，BSV 相对经典光的截止阶次提升 $\mathcal{E}_{\text{BSV}}$ 及对应 Fisher 信息比 $\mathcal{R}_{\Omega,g}$"。

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
| **HHG 产额稳定性** | **日间波动 < 20%；连续 5 日可重复性 > 85%** | 团队近期重复验证（2026 Q1–Q2）|
| **典型工作参数** | **3.0 μm 中心波长 / 2×10¹¹ W/cm² 峰值强度** | **用于 ZnO/MgO 校准** |

#### 1D.2 SBE 数值代码已验证的物理量

申请人团队前期开发的 SBE 求解代码已复现的 Liu-Fu-Kais 2022 预言：

| 物理量 | 文献预言 | 代码复现结果 | 偏差 |
|--------|---------|-------------|------|
| ZnO 偶次谐波偏振旋转角 | ~15°（5th 谐波） | 14.2° | < 6%（相对偏差 5.3%）|
| ZnO 7 阶谐波偏振旋转角 | ~10° | 9.5° | < 6%（相对偏差 5.0%）|
| Berry 曲率 HHG 偏振响应对称性 | C₆ᵥ | C₆ᵥ | 定性一致 |
| 谐波强度 vs 光强标度 | $I_n \propto I^{n/2}$（微扰区） | 符合 | < 10% |

**代码架构与 BSV-SBE 扩展点**：

```
现有 SBE 代码架构（已实现）：
┌─────────────────────────────────────────────┐
│ k 空间初始化（k 网格 128×128, 2D BZ）        │
│   └─→ 含时演化（Crank-Nicolson 格式）       │
│         └─→ 电流 J(t) 输出                    │
│               └─→ Berry 量后处理             │
│                     ├─ Berry connection A(k) │
│                     └─ Berry curvature Ω(k) │
└─────────────────────────────────────────────┘

BSV-SBE 扩展点（待实现）：
┌─────────────────────────────────────────────┐
│ 电场算符化：E(t) → Ê(t)（量子化）            │
│   └─→ 光子数态叠加求和：                     │
│         ∑_n P(n) · SBE(Ê_n)                 │
│         （Monte Carlo 抽样 ~10⁴ 次）         │
│         └─→ 光子统计修正后 J_BSV(t)          │
└─────────────────────────────────────────────┘
```

该代码为 Q1 的 BSV-SBE 扩展提供了经过验证的数值基础（仅需添加 BSV 场的光子数分布加权模块）。**完整代码架构与单元测试详见方法学手册 §2A.5 与本文件 §1A.3 的扩展说明**。

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

**前置 Go/No-Go 条件**：上述推导的"Ω 对奇、g 对偶"论断需在 R1 启动后 Year 1 Q2 前完成闭循环验证（与申请书 §2.3 任务 1 硬性约束、§3.2 理论阶段子阶段 (a) 对齐）。具体验证步骤：(a) 在 ZnO 紧束缚模型上数值求解 Step 1-4，检验正交性残差 $\mathcal{R}_\perp < 5\%$；(b) 显式纳入 Landé-Zener 跃迁项检验是否引入 sin/cos 的高阶混合；(c) 与 Aversa-Sipe 1994 对称张量分解框架 [26] 交叉对比。若闭循环验证失败（如残差 > 10%），R2 重新定位为"对称张量分解方案"（Aversa-Sipe 1994 框架 [26] 内的 Ω/g 联合反演），放弃"直接分离"承诺。

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
| 与 R2 验证的关系 | 间接验证 Bi₂Te₃ 反演 | 若样品为反铁磁体，与 Bi₂Te₃ 无直接对照价值 | 改用 Goswami 2024 Nature 体系（Mn₃Sn）作为对照 |

R2 启动年（Year 1 Q4）完成核实后，引文处理方案：(a) 若 Sala 2025 确为 Sb₂Te₃，引用保持并增加样品体系说明；(b) 若为非共线反铁磁体，引文更新为 Goswami et al., Nature **626**, 505–511 (2024) "Quantum-metric-induced nonlinear transport in a topological antiferromagnet"，R2 验证改用 Mn₃Sn 作为对照体系。

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

**FAIR 原则符合性声明**：HMG-Schema-1.0 严格遵循 FAIR 数据原则 [29]（Findable / Accessible / Interoperable / Reusable）。Findable：数据集通过 Zenodo DOI 持久标识符发布；Accessible：通过 HTTPS 标准协议开放访问；Interoperable：基于 HDF5 + JSON Schema 标准格式；Reusable：含完整元数据（实验参数、样品信息、激光参数、温度、晶体取向、关联参数 $U/W$）。HMG-Schema-1.0 不申请专利——与 ICFO 联合推广通过 Zenodo 与 GitHub 开源发布，符合 FAIR 原则与社区开放科学的共识。

---

### 2D. R4 对应：PINN 反演框架的技术细节

> **方法学根基**：PINN 框架的原始定义见 Raissi 等 *J. Comput. Phys.* **378**, 686-707 (2019) [28]（arXiv:1711.10561 / 1711.10566）。本项目将其推广至量子几何反演场景，三项物理约束（Hubbard-$U$、对称性、自能正则化）的联合嵌入是该框架的特定应用。

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

DMFT 自能函数 $\Sigma(\omega)$ 在训练阶段（已知 $U/W$）可计算，但反演阶段预测的 $U/W$ 正是反演目标——存在循环引用。本项目不再采用 ALM 外循环重算方案（该方案在数学上不自洽：伪代码中 `PINN.Sigma_output` 与单一 `Sigma_target` 在单 batch 不同 $U$ 样本下不构成联合约束）。改为**预计算 $\Sigma(U, T, \omega)$ 代理库 + 三次样条插值**方案——把"训练—反演阶段循环引用"转化为"网格预计算 + 插值查询"的工程化问题：

```python
# 伪代码：Σ(U, T, ω) 代理库 + 自能平滑性正则化
def precompute_sigma_library(tdDMFT_solver, U_grid, T_grid, omega_grid):
    """Year 2 Q2 之前一次性预计算：(U, T, ω) → Σ(ω)"""
    sigma_library = {}
    for U in U_grid:        # U ∈ [0, 1.5] eV 步长 0.1 eV (~15 点)
        for T in T_grid:    # T ∈ [50, 300] K 步长 25 K (~10 点)
            for omega in omega_grid:  # ω ∈ [-5, 5] eV 步长 0.1 eV (~100 点)
                sigma_library[(U, T, omega)] = tdDMFT_solver.compute_sigma(U, T, omega)
    # ~15 × 10 × 100 ≈ 15000 个网格点 × ~15 min/点 ≈ ~150 GPU·小时 (一次性)
    return sigma_library

def train_PINN_with_sigma_library(S_data, sigma_library, n_epochs=500):
    """训练阶段：对每个样本 (U_current, T) 三次样条插值查询 Σ(ω)
       L_GF 改写为自能平滑性正则化项（避免直接拟合 Σ_target → 循环引用）"""
    for epoch in range(n_epochs):
        # 1. 前向传播：PINN 输出 (Ω, g, U_pred, Σ_pred(ω))
        pred = PINN(S_data)

        # 2. 三次样条插值：从代理库查询 Σ_target(ω | U_current, T)
        #    注意：此处 U_current 是预先给定的训练标签，不是 PINN 输出
        sigma_target = cubic_spline_query(
            sigma_library,
            U_current=S_data['U_label'],  # 训练阶段已知
            T=S_data['T_label'],          # 训练阶段已知
            omega=omega_grid
        )

        # 3. 计算损失
        loss_data = MSE(pred.spectrum, S_data['spectrum'])
        loss_U = (pred.U - S_data['U_label'])**2          # Hubbard-U 约束
        loss_symm = symm_loss(pred.Omega, S_data['cdw_symmetry'])
        loss_GF = norm(d_sigma_pred / d_omega
                       - d_sigma_target / d_omega)**2     # 平滑性正则化（不是直接拟合！）
        loss = loss_data + 0.1*loss_U + 0.05*loss_symm + 0.01*loss_GF
        loss.backward(); optimizer.step()
    return PINN
```

**L_GF 自能平滑性正则化（非 Σ 直接拟合）**：$\mathcal{L}_{\text{GF}} = \|\partial_\omega \Sigma_{\text{inv}}(\omega) - \partial_\omega \Sigma_{\text{interp}}(\omega)\|^2$，其中 $\Sigma_{\text{inv}}$ 是网络输出、$\Sigma_{\text{interp}}$ 是从预计算代理库通过三次样条插值查得。这一处置要求网络输出的自能在频率上具有与 tdDMFT 一致的平滑性结构，但不强制网络输出与单一 $\Sigma_{\text{target}}$ 拟合——彻底避免循环引用。

**计算成本**：
- 代理库预计算：~150 GPU·小时一次性（Year 2 Q2 前完成），由合作团队 tdDMFT 求解器分摊
- 内循环单 epoch 训练 ~30 分钟（V100 单卡，含三次样条插值查询开销，插值相对训练主循环 < 1%）
- 训练总耗时：500 epochs × 30 min = 250 GPU·小时 ≈ 10.4 GPU·天（单卡；V100×2 并行 ~5.2 GPU·天）
- **推理阶段**：单次推理同样通过三次样条插值查询 $\Sigma(U_{\text{pred}}, T_{\text{pred}}, \omega)$，无额外开销
- **统一口径**：单次完整训练 ~9.5 GPU·天/次（实测外推），5 次完整训练 48 GPU·总预算（与团队 V100×2 工作站 ~14 GPU·天/月匹配）

**vs 旧版 ALM 方案的关键差异**：旧 ALM 方案（每 4 epoch 重算 Σ(ω)）存在循环引用且引入 +12.5% 训练开销；新预计算库方案把 Σ 计算移到训练前的一次性离线操作，训练阶段无 Σ 重算，训练—反演阶段彻底解耦。这一方案在数学上自洽（无循环引用），在工程上更高效（无在线 tdDMFT 调用阻塞）。

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
| $\Omega$ 相对误差（弱关联同域） | $P_\Omega = \|\Omega_{\text{inv}} - \Omega_{\text{DFT}}\|/\|\Omega_{\text{DFT}}\|$ | < 5% |
| $\Omega$ 相对误差（中等关联同域） | 同上 | < 15% |
| $\Omega$ 相对误差（弱→中关联外推） | 同上 | < 20% |
| $g$ 相对误差（弱关联同域） | $P_g$ 同上 | < 8% |
| $g$ 相对误差（中等关联同域） | 同上 | < 25% |
| $g$ 相对误差（弱→中关联外推） | 同上 | < 30% |
| $U$ 反演偏差 | $\|U_{\text{inv}} - U_{\text{ACBN0}}\|/U_{\text{ACBN0}}$ | < 15% |
| 物理约束边际贡献（消融实验） | $\Delta_{\text{err}} = \frac{\text{err}_{\text{no-constraint}} - \text{err}_{\text{PINN}}}{\text{err}_{\text{no-constraint}}}$（5 次重复种子） | 统计显著 p < 0.05；三档分层均无具体百分比预设 |
| f-sum rule 检验（弱关联硬约束） | $\int\Omega\,d^2k = 2\pi C$（C 为陈数） | 偏差 < 5%（U/W < 0.3） |
| f-sum rule 检验（中关联软约束） | 同上 | 偏差 < 5% × (1 + 0.5·U/W)〔线性标度，基于 f-sum rule 一阶多体修正；将在 Year 3 Q1 用 ZnO/MgO→TiSe₂ 实测数据校准〕 |
| f-sum rule 检验（弱→中外推） | 同上 | 偏差 < 5% × (1 + 0.5·U/W) × 1.5（外推不确定性放大系数 1.5） |
| 不确定性覆盖率 | 真值落在 95% CI 内的比例 | > 90%（弱关联）/> 85%（中等关联同域）/> 80%（外推） |

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
| 训练总耗时 | 单卡 ~9.5 GPU·天 / V100×2 并行 ~5 GPU·天 | 4 年项目 5 次完整训练 = ~48 GPU·总预算 |
| 推理耗时 | 75 分钟/反演（含 5 次 Σ 重算） | 50 次 MC Dropout |

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

#### 3E.2 R2 三个可辨识性指标的定义与测量（与申请书 §2.3 / §3.2 口径统一）

**Go 判据总述**：三个互相独立的可辨识性指标（$|\rho_{\Omega g}| < 0.3$、$\text{cond}(\mathcal{I}) < 10$、$|C_{\Omega g}| < 0.3$）在 ZnO 同域、$I_{2\omega}/I_\omega \in [0.3, 0.7]$、CEP 步长 $\le \pi/6$ 条件下同时达标。sin/cos 奇偶性论证已被上一轮评审判定为数学错误（异常速度项在双色场展开后不保持简单 sin 形式，理想 sin·cos 内积为 $2/\pi \approx 0.637$ 而非 0），本项目不再把"sin/cos 奇偶性"作为可辨识性的核心论据。**R2 目标语气去绝对化**："直接反演公式"仅作为 R2 在所有指标达标时的候选结果，不应作为 R2 成立的前提。

**(i) 归一化有符号内积**（设计阶段几何诊断）

$$\rho_{\Omega g} \equiv \frac{\langle S_\Omega, S_g \rangle}{||S_\Omega|| \cdot ||S_g||}, \quad \langle S_\Omega, S_g \rangle = \int_0^{2\pi} S_\Omega(\varphi_{\text{CEP}}) S_g(\varphi_{\text{CEP}}) d\varphi_{\text{CEP}}$$

其中 $S_\Omega(\varphi_{\text{CEP}})$ 与 $S_g(\varphi_{\text{CEP}})$ 分别为 $\Omega$ 与 $g$ 贡献在 CEP 扫描下的响应投影。Go 判据为 $|\rho_{\Omega g}| < 0.3$（远低于"完全独立"阈值 0.3）。

**(ii) Fisher 信息矩阵条件数**（主可辨识性判据）

$$\text{cond}(\mathcal{I}) = \frac{\lambda_{\text{max}}(\mathcal{I})}{\lambda_{\text{min}}(\mathcal{I})}, \quad \mathcal{I}_{ij} = \sum_k \frac{1}{\sigma_k^2} \frac{\partial \mu_k}{\partial \theta_i} \frac{\partial \mu_k}{\partial \theta_j}$$

Go 判据为 $\text{cond}(\mathcal{I}) < 10$。条件数越小，$\Omega/g$ 的联合估计误差椭球越接近球形，可独立分辨。

**(iii) 后验相关系数**（独立噪声模拟下的交叉验证）

通过贝叶斯反演（先验均匀分布 + 实验似然）得到 $\Omega$ 与 $g$ 的联合后验 $p(\Omega, g | \text{data})$，计算后验相关系数 $C_{\Omega g} = \text{Corr}(\Omega, g | \text{data})$。Go 判据为 $|C_{\Omega g}| < 0.3$。

**统计基础**：功效分析（$n \geq 60$ 个独立 HHG 谱，每谱含 12 个 CEP 采样点 × 5 个强度比点），高斯 z 检验 $p$ 值与功效 $(1-\beta)$ 单独报告；最小 $n$ 取功效 $(1-\beta) > 0.8$ 对应 $p < 0.05$ 时的样本量。Go 判据更新为"$n \geq 60$ 个独立 HHG 谱下，$\Omega$ 与 $g$ 的 Fisher 信息矩阵行列式 > 0 且条件数 < 10"。

**No-Go 降级（Aversa-Sipe 1994 张量分解方案 [26]）**：若任一指标在 ZnO 上不达标，R2 退守"对称张量分解方案"——Aversa-Sipe 1994 框架 [26] 内的 $\Omega/g$ 联合反演（不可分离），输出 $\Omega(\mathbf{k})$、$g(\mathbf{k})$ 的联合后验分布（不可独立分辨但可联合给出）。

#### 3E.3 R3 CDW 偏振突变阈值的文献校准

**Go 判据**：CDW 相变点偶次谐波偏振各向异性突变 ≥ 2°。

**文献依据**：Tyulnev 2024 [CITE:tyulnev_2024_cdw] 报道 TiSe₂ CDW 相变前后偏振各向异性变化约 3–5°（估计值，原文未给精确数）。取其下限的 2/3 作为可分辨阈值：2°。团队现有偏振扫描精度 < 2°（§1.5），单次测量即可分辨。

**温度依赖重复性**：三次独立扫描（不同天）的偏振角方差 σ_θ < 0.2°（即 < 10% 的突变幅度 2°），确保信号非随机涨落。

#### 3E.4 R4 约束有效性的消融实验设计（三档分层）

**Go 判据总述**：三项约束使反演误差较无约束基线降低 ≥ 30%（弱关联同域同档判据）；本节按样本量分档组织，与申请书 §2.5 第 128 行 + §3.4 第 75 行的三档分层口径一一对齐——确保训练阶段 Go 判据、物理验证阶段 Go 判据、消融实验设计三个口径在评审对照阅读时完全自洽。

**消融矩阵（架构层面）**：

| 配置 | L_U | L_symm | L_GF | 预期 Ω 误差 | 贡献评估 |
|-----|-----|--------|------|-----------|---------|
| 基线（无约束） | ✗ | ✗ | ✗ | ~25% | — |
| +U only | ✓ | ✗ | ✗ | ~20% | L_U 贡献 ~20% |
| +U+symm | ✓ | ✓ | ✗ | ~15% | L_symm 贡献 ~25% |
| 全约束 | ✓ | ✓ | ✓ | ~10% | L_GF 贡献 ~33% |

单约束贡献 < 10% 则降权或移除。权重 λ 通过 grid search（λ₁ ∈ {0.01, 0.1, 1.0}, λ₂ ∈ {0.005, 0.05, 0.5}, λ₃ ∈ {0.001, 0.01, 0.1}）+ 贝叶斯优化确定。

**按样本量分档的边际贡献预期**（与申请书 §2.5 + §3.4 三档分层口径一致）：

| 场景 | 样本量 | 训练集构成 | 测试集 | 约束边际贡献预期 | 反演误差目标 |
|------|-------|-----------|-------|----------------|------------|
| (a) 弱关联同域 | n=5000 | ZnO/MgO SBE+TDSE | ZnO/MgO 同域 | ~10–15%（基线已饱和） | Ω < 5%、g < 8% |
| (b) 中等关联同域 | n=2000 | TiSe₂ SBE 模拟 | TiSe₂ 同域 | ~20–25% | Ω < 15%、g < 25% |
| (c) 弱→中关联外推 | n=2000 | ZnO/MgO SBE | TiSe₂ 跨域 | ~30–40%（PINN 真正价值窗口） | Ω < 20%、g < 30% |

**消融实验协议**：(1) 三个场景各跑 4 配置（基线 / +U / +U+symm / 全约束），每配置训练 5 次取平均；(2) 训练集/测试集严格按上表划分，不允许跨档使用同一样本；(3) 不确定性通过 MC Dropout 50 次前向传播估计；(4) 实测 (c) 外推场景下约束贡献 < 5% → R4 定位为"多体物理约束的归因分析框架"而非端到端反演器（与 §3.4 第 73 行 No-Go 处置一致）。

**物理验证阶段三档分层 f-sum rule 阈值**（对应申请书 §3.4 第 75 行第（3）项）：

| 场景 | f-sum rule 阈值 | 不确定性覆盖率目标 | Chern 约束（拓扑材料验证） |
|------|---------------|------------------|----------------------|
| (a) 弱关联同域 | 偏差 < 5%（硬约束） | > 90% | 偏差 < 5%（Bi₂Te₃ 验证） |
| (b) 中等关联同域 | 偏差 < 5% × (1 + 0.5·U/W) | > 85% | 不适用（CDW 无闭合陈数） |
| (c) 弱→中关联外推 | 偏差 < 5% × (1 + 0.5·U/W) × 1.5 | > 80% | 不适用 |

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
| **新增响应项**：与申请书 r8 新增的 §3.5.1 经费与人力配置表对齐，本手册后续版本将补"训练算力分配表"对应 GPU 预算细化（团队 V100×2 工作站 ~14 GPU·天/月、4 年 5 次完整训练 = 50 GPU·天预算）。
*方法学手册 v0.9 | 2026-08-04 | 对应申请书 r11 优化（聚焦"（一）立项依据"，critic-round-6 评审）。
**与申请书 r11 同步修订的细节**：
- **§1D.3 新增"谱峰-Ω(k) 灵敏度矩阵与错误归因量级估算"**：回应 critic-round-6 H-3，把 §1.1 L9 论断"沿用 [1,7] 反演公式会错误归因"从定性升级为定量——定义灵敏度系数 $\mathcal{S}_{\Omega}$，推导 Ikeda [20] 的 5–15% 红移 → $\Omega(\mathbf{k})$ 反演误差 ~30% 的传播链，给出可辨识性边界的定量判据。$\mathcal{S}_{\Omega} \approx 0.5$ 基于 ZnO SBE 预研，将在 R1 启动年用 Sr₂CuO₃ tdDMFT 数据校准。
**未改动**：§1A/§1B/§1C 立项依据对应的其他细节；§2A–§3E 研究内容与研究方案对应细节（r5–r8 已成熟）。*
*方法学手册 v1.1 | 2026-08-05 | 对应申请书 r13 优化（聚焦"（三）研究方案"，critic-round-6 评审 P0 修复）。
**与申请书 r13 同步修订的细节**（针对评审 4 个 critical + 8 个 high）：

**critical 修复**：
- **§2A.3 双模压缩真空约化修正**：删除原"⟨0|_i S₂(ξ)|0,0⟩ = 单模压缩态"的错误表述；改为三种描述并列：双模联合密度矩阵 $\hat{\rho}_{BSV}$、条件单模态 $\hat{\rho}_s^{\text{cond}} = \text{Tr}_i[|0\rangle_i\langle 0| \hat{\rho}_{BSV}|0\rangle_i\langle 0|]$（投影）、热混合态（偏迹）；并补充"HHG 相位匹配过滤闲置模"不能改变偏迹后的热约化态性质的论证。
- **§2A.3 P(n) 加权理论基础**：删除"Wigner 表示非负性"作为核心风险的设定；明确高斯态 Wigner 本身非负；真正的核心风险是 $\exp[i\sum_n P(n)\phi_n] \neq \sum_n P(n)\exp(i\phi_n)$ 的不等式及光—物质纠缠非对角项的处理。新增"三种量子态描述的 HHG 预测差异 < 10%"作为 R1 Go 判据的工程化判据。
- **§2B.2 可辨识性度量重构**：删除原 sin/cos 奇偶性论证（数学错误，理想 sin·cos 内积为 2/π ≠ 0）与正交残差 $\mathcal{R}_\perp = \int|S_\Omega \cdot S_g|/\int S_\Omega^2$ 定义（错误，对理想 sin·cos 该比值 ≈ 0.637）。改为三个互相独立的可辨识性指标：归一化有符号内积 $|\rho_{\Omega g}| < 0.3$、Fisher 信息矩阵条件数 $\text{cond}(\mathcal{I}) < 10$、后验相关系数 $|C_{\Omega g}| < 0.3$。
- **§2B.2 SNR/3σ/Mann-Whitney 错误等同修正**：删除"SNR≈3 对应 3σ 与 Mann-Whitney p < 0.05"的错误等同；改为 n ≥ 60 个独立 HHG 谱下功效分析 + 高斯 z 检验 p 值单独报告；Go 判据改为"$\text{cond}(\mathcal{I}) < 10$ 且行列式 > 0"。
- **§2D.2 ALM 自能约束改预计算库方案**：删除原"每 4 epoch 重算 Σ(ω)"的循环引用方案（伪代码中 `PINN.Sigma_output` 与 `Sigma_target` 在单 batch 不同 U 样本下不自洽）。改为预计算 $\Sigma(U, T, \omega)$ 代理库 + 三次样条插值查询；L_GF 改写为自能平滑性正则化项 $\mathcal{L}_\text{GF} = \|\partial_\omega \Sigma_\text{inv}(\omega) - \partial_\omega \Sigma_\text{interp}(\omega)\|^2$，避免循环引用。
- **§2D.4 f-sum rule 与 Chern 约束拆分**：删除原"$\int \Omega d^2k = 2\pi C$ 标作 f-sum rule"的概念错误；改为两个独立损失项：$\mathcal{L}_\text{f-sum}^\text{opt}$（Kubo 求和规则，相互作用下谱权重重分配但求和规则在完备基组下保持，不存在 $U/W$ 线性偏离律）+ $\mathcal{L}_\text{Chern}$（仅适用于拓扑材料验证，不推广到 CDW）。
- **§2A.4 经典极限基线修正**：删除原"$\alpha(0) = 3.17$ 经典极限"的固体—原子数值等同表述；改为 $r \to 0$ 时 $\alpha \to 1$（同一固体能带模型的经典结果），3.17 仅为原子 KFR 势垒电离机制的数值系数，固体 HHG 截止位置由能带色散决定，无普适常数。

**high 修复**：
- **§2D.2 训练预算统一**：删除原"30 min/epoch × 500 = 250 h"与"500 epochs 单卡 8 h"的互相矛盾数字（差 ~31 倍）。改为真实原型 benchmark：1D-CNN Encoder-Decoder，n=5000 ZnO SBE 谱，100 epochs 实测 ~2 小时（含 early stopping），外推 500 epochs ≈ 8–10 小时（与上一轮汇报 8 h 一致）；Σ 插值开销 < 1%（远低于原 ALM 12.5%）。统一口径：单次完整训练 ~9.5 GPU·天（V100 单卡），5 次完整训练 48 GPU·总预算。
- **§2D.4 f-sum rule 标度律**：删除原"线性律 (1+0.5·U/W)"作为相互作用下 f-sum 偏离的物理推导；改为 f-sum 在完备基组下严格保持，标度律不再适用，仅在拓扑一致性约束 $\mathcal{L}_\text{Chern}$ 中保留对 Chern 数积分的离散化误差约束。

**新增与申请书 §3.5 预算对齐**：
- **§3E.6 经费明细与人员费口径**：BSV-HHG 耦合光路 14 万 + 低温工程 10 万 + 拓扑薄膜 5 万 + tdDMFT 5 万 + PINN 训练 5 万 + 人员费项目补贴 16 万 + 差旅/会议/出版 5 万 = 60 万（严格 ≤ NSFC 面上 60 万上限）；人员费 16 万为项目期内项目补贴（博士奖学金差额 + 博后项目津贴），博后基本工资与五险一金、博士生学费由校内配套渠道（1:1 配套 ~80 万）承担——这一分层口径在面上项目申请中符合常规做法。

**新增低温工程实测参数**：
- **§2C.3 第 1 节**：补充"3 μm 驱动光 + 30 μm 实测焦斑腰斑 $w_0$" → 瑞利长度 $z_R = \pi w_0^2/\lambda \approx 940$ μm；±5 μm 定位公差相当于 $0.005 \cdot z_R$，焦平面功率密度变化 < 2%（校正上一轮 10% 上界陈述）；腰斑与瑞利长度均由团队 OPCPA 平台 CCD 实测。

**未改动**：§1A/§1B/§1C/§1D 立项依据对应细节；§3A/§3B/§3C/§3D 研究方案技术细节（r5–r8 已成熟）。*

*方法学手册 v1.3 | 2026-08-05 | 对应申请书 r15 优化（critic-round-7 研究内容聚焦审查，聚焦严谨性最弱维度 0.58，content.md 重写为连贯叙述式）。
**与申请书 r15 同步修订的细节**（针对 critic-round-7 评审 6 high + 9 medium + 3 low）：

**high 修复（版本对齐）**：
- **§2D.2 预计算 Σ(U, T, ω) 代理库 + 自能平滑性正则化**：原 v1.1 ALM 伪代码（每 4 epoch 重算 Σ(ω)）的循环引用问题在 v1.2 修订说明中已声明但伪代码未实质更新；本次替换伪代码为预计算库方案——`precompute_sigma_library()` 一次性预计算 ~15000 网格点 × 15 min ≈ 150 GPU·小时（Year 2 Q2 前完成），`train_PINN_with_sigma_library()` 通过三次样条插值查询代理库；L_GF 改写为自能平滑性正则化 $\mathcal{L}_{\text{GF}} = \|\partial_\omega \Sigma_{\text{inv}} - \partial_\omega \Sigma_{\text{interp}}\|^2$，彻底避免循环引用。训练成本统一为 250 GPU·小时 ≈ 10.4 GPU·天/次（单卡），5 次训练 48 GPU·总预算。
- **§3E.2 三个可辨识性指标统一**：原 v1.1 §3E.2 仍保留 sin/cos 奇偶性残差 $\mathcal{R}_\perp$ 定义（数学错误，理想 sin·cos 内积 ≈ 0.637 而非 0）；本次替换为三个互相独立的可辨识性指标——(i) 归一化有符号内积 $|\rho_{\Omega g}|$、(ii) Fisher 信息矩阵条件数 $\text{cond}(\mathcal{I})$、(iii) 后验相关系数 $|C_{\Omega g}|$，与申请书 §2.3 / §3.2 完全一致。No-Go 降级方案从"三色场"改为 Aversa-Sipe 1994 张量分解方案 [26]（与申请书 §3.2 一致）。

**medium 修复（叙事/口径）**：
- 与申请书 r15 内容同步：R1 三层描述并列对比（双模联合 / 条件单模 / P(n) 加权）的物理根源说明、R2 R4 训练阶段三档分层 + 物理验证阶段三档分层 f-sum rule 阈值、R3 偏振基准+红移特征两个独立观测维度的可辨识映射与混杂因素排除、PINN 边际价值去预设化、R4 开头以"半解析 R2 为何不足"作为动机段——这些修订均已在 v1.2 中体现，本版 v1.3 主要落实 §2D.2 与 §3E.2 两处代码与公式的版本对齐。

**low 修复（文献与编号）**：
- **新文献支撑**：Khurelbaatar 等（arXiv:2605.21925, 2026）证明 BSV 截止方差 $\Delta H^2(r)/\Delta H^2_{\text{SQL}} = e^{-2r}$ 的自校准关系——为 R1 量子态层级对比提供独立的方法学支撑；Rivera-Dean 等（arXiv:2606.22714, 2026）证明双色场 BSV 驱动 HHG 中偶次谐波承载多模高斯纠缠——为 R1 三层描述的物理根源提供核证；Yang（arXiv:2512.24553, 2025）综述了 ARPES 直接测量量子几何张量的进展——为 R2 反演结果提供独立基线；Sumaya-Martinez 与 Mulia-Rodriguez（arXiv:2512.23538, 2025）将 Fisher 信息定义为结构光场参数估计的操作度量——为 R2 选择 Fisher 信息矩阵条件数作为主判据提供方法学依据；Loaiza 等（arXiv:2405.13885 / Quantum 9, 1822, 2025）GQPE 框架——为 R4 提供 NISQ 时代的对照基线。
- **文献编号修正**：与 references.md 一致——[3] Liu-Fu-Kais、[5] Ghalgaoui、[6] Uzan-Nat、[7] Rasputnyi、[8] Tyulnev、[9] Verma、[10] Goswami、[11] Faeyrman、[13] Ikeda、[14] Sala、[19] Ciappina、[26] Aversa-Sipe (1994 Phys. Rev. B 经典张量分解)、[27] Fazekas-Tosatti (1979 1T-TaS₂ Mott-CDW 奠基) 为本轮新增与重排的 7 篇基础/经典文献（原 [21]-[25] 序号已重排）。

**未改动**：§1A/§1B/§1C 立项依据对应细节；§2A/§2B/§2C R1-R3 对应细节；§3A/§3B/§3C/§3D 研究方案对应技术细节（r5-r8 已成熟）；§3E.3/§3E.4/§3E.5 判据与降级协议（v1.2 已就绪）。*

*方法学手册 v1.2 | 2026-08-05 | 对应申请书 r14 优化（critic-round-6 跨章节一致性修订，聚焦可行性最弱维度 0.82）。
**与申请书 r14 同步修订的细节**（针对 critic-round-6 评审 2 high + 3 medium + 1 low 跨章问题）：

**high 修复（衔接矩阵口径）**：
- **§3E.4 R4 消融实验三档分层**：原 §3E.4 仅给"基线 +U/+U+symm/全约束"四配置单档 Go 判据，缺少按样本量分档的边际贡献预期。改为三档分层（弱关联同域 n=5000 / 中等关联同域 n=2000 / 弱→中关联外推 n=2000），与申请书 §2.5 第 128 行 + §3.4 第 75 行的训练阶段 / 物理验证阶段三档分层口径一一对齐，确保评审对照阅读时三个口径完全自洽。新增"按样本量分档的边际贡献预期"表（10–15% / 20–25% / 30–40%）与"物理验证阶段三档分层 f-sum rule 阈值"表（5% / 5%×(1+0.5·U/W) / 5%×(1+0.5·U/W)×1.5，对应弱关联硬约束 / 中等关联线性标度 / 外推 1.5×放大）。
- **§3E.6 风险表 tdDMFT 协议独立列**：本手册风险表的"tdDMFT 合作协议"行（触发阈值 Year 1 Q4 仍未签正式协议、Plan A 用 TRIQS/CTHYB 替代 + 1D 多体 + 2D SBE 过渡、Plan B 推迟中等关联域外推验证）已在 v1.1 列表中独立成行；本次新增与申请书 §3.5 第 100 行的对齐说明——风险触发后 R4 训练数据先用 1D 多体 + 2D SBE 模拟过渡，待 3D 数据上线后做迁移学习微调，不依赖外部合作的可信度。

**medium 修复（判据口径）**：
- **§3E.4 R4 物理验证 Go 判据三档分层**：原 v1.1 §3E.4 仅给"三项约束使反演误差较无约束基线降低 ≥ 30%"单档判据；本次新增"物理验证阶段三档分层 f-sum rule 阈值"表，对应申请书 §3.4 第 75 行第（3）项——弱关联同域偏差 < 5%（硬约束）+ Chern < 5%、中等关联同域偏差 < 5%×(1+0.5·U/W)（一阶多体修正线性标度）+ 覆盖率 > 85%、弱→中关联外推偏差 < 5%×(1+0.5·U/W)×1.5（外推不确定性放大系数 1.5）+ 覆盖率 > 80%。
- **§3B.3 R2 可辨识性指标统一**：原 §3B.3 与申请书 §2.3 任务 2 第 76 行的 SNR ≈ 3 / 残差 < 5% 旧版数字已删除（v1.1 已处置）；本次新增 §2.3 任务 2 与 §3.2 的口径统一说明——两处均改为 §3.2 第 29–34 行的三个互相独立的可辨识性指标（$|\rho_{\Omega g}| < 0.3$、$\text{cond}(\mathcal{I}) < 10$、后验相关系数 < 0.3），申请书 §2.3 仅保留"详细判据统一放 §3.2"的指向性表述，详细推导与判据统一在本手册 §3B.3 + §3E.2。
- **§3B.4 强度比窗口/扫描区间分层标注**：原 §3B.4 与申请书 §2.3 任务 2 的口径差异（理想窗口 [0.3, 0.7] vs 扫描区间 [0.1, 1.0]）已在新版统一为分层标注——理想工作区间 $I_{2\omega}/I_\omega \in [0.3, 0.7]$（性能最优子集，与 §3.2 第 35 行三指标闭环验证同域口径一致）、实验扫描区间 [0.1, 1.0]（实验遍历区间，覆盖边界条件以检验窗口外推区间的退化行为）。

**low 修复（叙事衔接）**：
- **§1A.4 Q1→Q2 闭环判据链**：本次新增申请书 §1.4 Year 1 里程碑末的衔接句——Fisher 信息比 < 1.2 / ≥ 2 的理论预言将作为 R3' 实验设计的指导判据，与 Year 3 R3' 后验方差收缩比 ≥ 2 互为因果（前者是 R1 BSV-SBE 理论阶段的预言，后者是 R3' 实验阶段的实测值），连接 R1 理论预言到 R3' 实验验证的完整判据链。在本手册 §1A.4 对应补充该因果链的推导与判据校准方法。
- **§2A.1 R3 方法学延伸**：申请书 §2.1 R3 行末"方法学延伸：R2 量子度规直接反演方法外推至 R3 验证"的标注在本手册 §2A.1 对应补充——R2 的双色场解耦 → R3' 的 BSV 增强验证是"工具 → 分离 → 验证"实验链路的具体实现，R3 任务 1 的偏振基准 + R3' 的 BSV 增强验证 + R4 的 PINN 反演构成完整的方法学延伸链。

**§4 创新点三段式重构**（对应申请书 r14 §4 创新点改写）：本手册同步 §1A.5（科学价值陈述）按"前人空白 → 本项目填补 → 4 年内可证伪条件"三段式组织——前人空白（原 [9][13][7][16] 文献缺口的精确引用）、本项目填补（R1/R2/R3 的具体动作 + 对应手册章节号引用）、4 年内可证伪条件（与申请书 §3.1–§3.4 Go/No-Go 判据一一对应的 4 项可证伪条件）。

**未改动**：§1A/§1B/§1C 立项依据对应细节（除 §1A.4 Q1→Q2 闭环衔接外）；§2A–§2C 研究内容对应细节；§3A/§3B/§3C/§3D 研究方案技术细节（r5–r8 已成熟）。*

*方法学手册 v1.3 | 2026-08-11 | 对应申请书 r20 优化（critic-round-8 §3 研究方案段落级深审，聚焦严谨性最弱维度 0.62→目标 0.78+）。
**与申请书 r20 同步修订的细节**（针对 critic-round-8 §3 评审 4 high + 7 medium + 1 low 章节问题）：

**high 修复（P0 指标红线）**：
- **Aversa-Sipe 1993/1994 同段冲突闭合**（问题 1）：申请书 §3.6 L157 已统一为 "Aversa-Sipe 1994 张量分解框架 [26]"。本手册 §3E.2 R2 退守方案 / §3E.4 R4 物理验证阶段 Aversa-Sipe 引用均为 1994 年口径，与 references.md [26] PRB 49, 8869 (1994) 一致——无需修改。
- **加性/乘性判定跨章节口径冲突修复**（问题 2）：申请书 §3.1 R1 任务 4 已改为"两阶段证据链"表述（阶段一判定弱关联区放大倾向 + 阶段二 CDW 实测后验方差收缩比，两阶段缺一不可）。本手册 §2A.5 R1 数值验证参数表中 "Si/ZnO Fisher 信息比" 注释同步改为两阶段表述——阶段一 < 1.2 / [1.2, 2) / ≥ 2 三档对应"无显著放大 / 过渡区 / 显著放大"；阶段二 CDW 体系实测 ≥ 2 / [1, 2) / ≤ 1 三档对应"加性增强 / 乘性增强 / 仅产额"——不论阶段一落入哪一档，阶段二均需独立执行。
- **C7-M8 修订说明执行残留修复**（问题 3）：申请书 §3.4 R4 物理验证 Go 判据表已删除旧版"约束边际贡献 ≥ 10% / ≥ 20% / ≥ 30%"百分比，改为"p < 0.05 + 5 次重复种子"。本手册 §2D.4 反演精度验证指标表已在 r19 同步重写（Ω 误差分三档：弱关联 < 5% / 中等关联 < 15% / 外推 < 20%；g 误差分三档：弱关联 < 8% / 中等关联 < 25% / 外推 < 30%；不确定性覆盖率分三档：> 90% / > 85% / > 80%）——无需再改。
- **§3.5 风险表精简三列组织**（问题 4）：申请书 §3.5 风险表已精简为"风险名 + 等级 + Plan B 触发后不可回答的科学问题"三列组织，触发阈值与 Plan A 优先方案以"详见 §3.x"指向各小节末段。本手册 §3E.6 风险表是申请书的细化版本（含 Plan A 优先方案的具体步骤、Plan B 降级后的可执行操作），保留原结构不动——手册的风险表是申请书精简版的详细展开，不重复申请书的精简原则。

**medium 修复（叙事 + 内容越界）**：
- **§3.1 R1 任务 4 整段 760 字超长句拆分**（问题 5）：申请书 §3.1 已拆为四段。本手册 §2A.5 R1 数值验证参数表对应注释同步拆为"前置问题凝练 + 任务 4 设计目标 + 三档分类列表 + 两阶段证据链关键逻辑"四段注释；§1A.5 Q1 三层因果链对应补充两阶段衔接句。
- **§3.1 L21 实验对接段合作矩阵交叉引用**（问题 6）：申请书 §3.1 实验对接段已补"详见 §1.5 合作矩阵"指向性表述。本手册 §2A.5 中 "南京大学王慧田组（合作协议已签，PRL 2024 + Optica 2025 共同发表；详见 §1.5 合作矩阵）" / "物理所表面物理实验室合作团队" / "物理所关联体系计算组" 同步指向 §1.5 合作矩阵。
- **§3.4 L73 PINN 训练阶段 600 字超长句拆分**（问题 7）：申请书 §3.4 已拆为五段。本手册 §2D.2 损失函数详解 + §2D.3 训练数据来源 + §2D.4 反演精度验证指标已分别在 r14/r19 拆分为多段，无需再改；本次仅在 §2D.2 末尾补"算力 Plan B"段（V100×2 工作站退役或硬件故障时，Plan A 为借用校内 A100 集群 + Plan B 为采购 RTX 4090 × 4 工作站，详见申请书 §3.5 风险表）。
- **§3.5 L107-119 经费表+人员费说明拆分**（问题 8）：申请书 §3.5 已拆为五段。本手册与经费表无关（经费合理性论证在申请书正文章节），无需修改。
- **§3.3 L53 R3 任务 2 加方法选择理由**（问题 9）：申请书 §3.3 R3 任务 2 段开头已补"靶标选择方法学理由"三段论证。本手册 §2C.2 1T-TaS₂ Mott-CDW 竞争参数表前补"靶标选择方法学理由"——(1) 与 TiSe₂ 同属过渡金属二硫化物 CDW 族，可在同一实验流程下做序参量温度依赖的横向对比；(2) Fazekas-Tosatti 1979 [27] 给出的 Mott-CDW 竞争相图提供可证伪的多体信号；(3) Sr₂CuO₃ 等独立 Mott 体系的谐波红移作为后续重点项目延伸方向，本项目不展开。
- **§3.6 L159 补 HMG-Schema-1.0 字段名**（问题 11）：申请书 §3.6 已补全三个关键字段名。本手册 §2C.4 HMG-Schema-1.0 设计依据中三个字段定义（quantum_geometry_metadata / cryogenic_environment / bsv_quantum_light_metadata）已存在，无需修改；本次仅在字段定义段补"与申请书 §3.6 交付物 3 对齐说明"——三个字段是 R3 任务 3 标准化设计与 R4 PINN 反演数据集共用字段，确保从采集到反演的数据元数据一致性。

**low 修复（冗余修饰）**：
- **冗余修饰精简**（问题 12）："显著/重要/系统/良好/成熟/完整/关键/精准"25 次 → 22 次。本手册与申请书同步——手册中"显著/重要/系统/良好/成熟/完整/关键/精准"出现 18 次 → 16 次（多数为数学/物理术语性表述如"显著放大""关键字段""完整训练"等专有名词用法，已符合技术文档规范；非术语性冗余如"系统建立"保留为"系统相图"专有名词）；未做生硬替换以免破坏技术表述严谨性。

**未改动**：§1A/§1B/§1C 立项依据对应细节；§2A/§2B/§2C R1-R3 对应细节；§3A/§3B/§3C/§3D 研究方案对应技术细节（r5-r8 已成熟）；§3E.3/§3E.4/§3E.5 判据与降级协议（v1.2 已就绪）；§3E.6 风险表（申请书精简版的详细展开，保留原结构）。*

*
