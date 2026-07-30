# 方法学手册

> 配套申请书：量子光场驱动的 HHG——明亮压缩真空（BSV）作为固体多体态的非经典探针
> 项目类型：面上项目 | 课题 ID：general-bsv-driven-hhg-quantum-20260726
> 撰写原则：申请书重思路，方法学手册重细节（公式推导 / 参数表 / 技术路线图）
> 章节对应：与 `proposal-draft.md` 一一对应（§1 ↔ 1.2.2、§2 ↔ 2.3、§3 ↔ 2.5、§4 ↔ 1.4 创新点 2 / 2.4、§5 ↔ 2.4、§6 ↔ 3.1）

---

## §1 BSV 态的相干态展开与光子统计

### §1.1 BSV 的量子态定义

**明亮压缩真空态** (Bright Squeezed Vacuum, BSV) 定义为在相干态 $|\alpha\rangle$ 背景上叠加压缩算符：
$$|\mathrm{BSV}\rangle = \hat{S}(\xi)\,\hat{D}(\alpha)\,|0\rangle$$

其中：
- $\hat{D}(\alpha) = \exp(\alpha \hat{a}^\dagger - \alpha^* \hat{a})$ 为位移算符，$\alpha = |\alpha|e^{i\theta_\alpha}$；
- $\hat{S}(\xi) = \exp\!\left[\tfrac{1}{2}(\xi^* \hat{a}^2 - \xi \hat{a}^{\dagger 2})\right]$ 为压缩算符，$\xi = r e^{i\theta_{\rm sq}}$；
- 关键参数：压缩度 $r$、压缩相位 $\theta_{\rm sq}$、相干态振幅 $|\alpha|$。

**与压缩真空态 (squeezed vacuum, SV) 的关系**：当 $\alpha = 0$ 时，BSV 退化为纯压缩真空态。本项目使用的 BSV 由高增益参量下转换产生，对应 $|\alpha| \gg 1$、$r \sim \mathcal{O}(1)$ 的高亮度极限。

### §1.2 相干态展开 (coherent-state expansion)

BSV 在 Glauber 相干态基上的展开为 [Schleich & Wheeler, JOSA B 4, 1715 (1987)]：
$$|\mathrm{BSV}\rangle = \frac{1}{\sqrt{\pi}}\int_{-\infty}^{\infty} d^2\beta\, |\beta\rangle\, \langle\beta|\mathrm{BSV}\rangle$$

相干态投影振幅为：
$$\langle\beta|\mathrm{BSV}\rangle = \frac{1}{\sqrt{\cosh r}}\exp\!\left[-\tfrac{1}{2}|\beta|^2 - \tfrac{1}{2}|\alpha|^2 - \alpha\beta^*\tanh r + \tfrac{1}{2}e^{i\theta_{\rm sq}}\beta^{*2}\tanh r + \tfrac{1}{2}\alpha^{*2}e^{-i\theta_{\rm sq}} - \alpha^*\beta\right]$$

**物理意义**：BSV 态可视为以 Glauber 投影权重 $P(\beta) = |\langle\beta|\mathrm{BSV}\rangle|^2$ 分布的相干态 $|\beta\rangle$ 的统计混合。**驱动 HHG 时**，BSV-物质相互作用的非微扰过程将每个相干态分量 $\beta$ 映射为不同的谐波量子态，整体 HHG 谱即为这些分量的量子相干叠加——这是 BSV-HHG 区别于相干态-HHG（单一 $|\alpha\rangle$ 驱动）的核心物理。

### §1.3 光子统计基线参数表

本项目 2.1 节"标定 BSV 光子统计"的量化基线（参照 Iskhakov 2012 / Spasibko 2012 实测）：

| 物理量 | 符号 | BSV 基线值 | 经典相干态对比 | 测量方法 |
|--------|------|------------|----------------|----------|
| 单脉冲平均光子数 | $\bar{N}$ | $2\times 10^{13}$ | 任意 | 功率计 + 脉冲能量 |
| 二阶关联（零延迟）非简并 PDC | $g^{(2)}(0)$ | $2$ | $1$ | HBT 干涉 + 符合计数 |
| 二阶关联（零延迟）简并 PDC | $g^{(2)}(0)$ | $3 + 1/N$ | $1$ | 同上 |
| 强度-强度关联时间 | $\tau_c$ | 取决于相位匹配带宽 | $\infty$（无涨落） | 频谱干涉 |
| Fano 因子 | $F = \langle(\Delta N)^2\rangle/\langle N\rangle$ | $g^{(2)}(0)\bar{N} \gg 1$ | $1$ | 光子数直方图 |
| 压缩度 | $r$ | $\mathcal{O}(1)$ | $0$ | 零差探测 |
| 探测体积约束 | $V_{\rm det} \ll V_{\rm coh}$ | 必满足 | 任意 | 空间模式匹配 |

**复现条件**：所有 $g^{(2)}(0)$ 测量必须在 $V_{\rm det} \ll V_{\rm coh}$（探测体积 << 相干体积）下进行，否则超聚束 (super-bunching) 特征被空间平均平滑掉。

### §1.4 BSV 态与 HHG 输入的匹配条件

为将 BSV 态高效耦合到固体 HHG 平台，需满足：
1. **波长匹配**：BSV 中心波长 $\lambda_{\rm BSV} \in [0.8, 1.5]\,\mu\text{m}$（近红外），与 TMDC 带隙 $E_g \in [1.5, 2.0]\,\text{eV}$ 匹配（单光子能量 $0.83$–$1.55\,\text{eV}$）；
2. **脉宽匹配**：BSV 脉冲宽度 $< 50\,\text{fs}$，与经典光 HHG 同条件；
3. **聚焦匹配**：BSV 与经典光在样品表面聚焦光斑尺寸匹配（$\sim 5\,\mu\text{m}$ FWHM），确保强度对比有效；
4. **平均功率匹配**：BSV 与经典光平均功率相等（$P_{\rm avg}^{\rm BSV} = P_{\rm avg}^{\rm classical}$），使 QEF 的产出比定义 $QEF_{\rm yield}$ 自洽。

---

## §2 量子光驱动半导体布洛赫方程（SBE-Q）

### §2.1 从经典光 SBE 到量子光 SBE

**经典光半导体布洛赫方程**（沿用 Wu/Schafer/Gaarde 2016 多能级框架 [Phys. Rev. A 94, 063403]）：

$$i\hbar\frac{\partial p_{cv}(\mathbf{k},t)}{\partial t} = -\left[\epsilon_g(\mathbf{k}) - i\frac{\hbar}{T_2}\right]p_{cv} + \mathbf{d}_{cv}\cdot\mathbf{E}(t)\left[n_c - n_v\right]$$
$$\hbar\frac{\partial n_{c/v}(\mathbf{k},t)}{\partial t} = \mp 2\,\mathrm{Im}\!\left[\mathbf{d}_{cv}^*\cdot\mathbf{E}(t)\,p_{cv}\right] + i\frac{\hbar}{T_1}\left[n_{c/v}^{(0)} - n_{c/v}\right]$$

其中 $\epsilon_g(\mathbf{k}) = E_g + (\mathbf{k} + \mathbf{eA}(t)/c)^2/(2m^*)$ 为含光场动量的瞬态带隙，$T_1$ / $T_2$ 分别为粒子数/相干弛豫时间。

**量子光拓展**（参照 Rivera-Dean et al. 2023 [arXiv:2309.14435] 的 Bloch 形式化）：

将经典电场 $\mathbf{E}(t)$ 替换为量子化的光场算符 $\hat{\mathbf{E}}(t) = \mathbf{E}_0(\hat{a} + \hat{a}^\dagger)$，并对电子-空穴-光子复合系统求解密度矩阵 $\hat{\rho}$ 的 Liouville 方程：
$$i\hbar\frac{d\hat{\rho}}{dt} = [\hat{H}_{\rm SBE-Q}, \hat{\rho}] + \mathcal{L}_{\rm decoh}[\hat{\rho}]$$

**本项目实现路径**（沿用 Peschel et al. 2022 [Phys. Rev. B; arXiv:2205.00522] 的双粒子紧束缚实空间方案）：

将 SBE 从动量空间拓展到实空间紧束缚模型，对有限系统（量子点、纳米线、超晶格）支持多体电子-空穴产生、空间限制、去相干与阻尼的微观处理。

### §2.2 量子光 SBE 的产额与噪声预测

对 BSV 驱动的固体 HHG，**谐波产额**：
$$Y_{\rm BSV}^{(q)} = \int d^2\beta\, P(\beta)\, Y_{\rm coh}^{(q)}(|\beta|^2, \theta_\beta)$$

其中 $Y_{\rm coh}^{(q)}$ 为相干态 $|\beta\rangle$ 驱动下 $q$ 阶谐波的产额，$P(\beta)$ 为 §1.2 的 Glauber 投影权重。

**量子噪声关联**（二阶关联）：
$$g_{\rm HHG}^{(2),q}(\tau) = \frac{\langle :\!\hat{I}_q(t)\hat{I}_q(t+\tau)\!:\rangle}{\langle\hat{I}_q(t)\rangle\langle\hat{I}_q(t+\tau)\rangle}$$

对 BSV 驱动，可证明 $g_{\rm HHG}^{(2),q}(0) \neq 1$（偏离泊松），且不同阶次 $q$ 的 $g^{(2)}$ 偏移量不同——这是 BSV-HHG 区别于经典光 HHG 的核心可观测。

### §2.3 量子光 SBE 的收敛性诊断

为降低多体相互作用的非微扰处理发散风险（申请书 3.3 风险评估），本项目拟采用三层收敛性诊断：

1. **步长收敛性**：固定动量网格 $\Delta k$ 与时间步长 $\Delta t$，验证谐波产额 $Y^{(q)}$ 随 $\Delta t \to 0$ 的收敛阶（预期 2 阶 Runge-Kutta 即可）；
2. **截断能收敛性**：固定 $\Delta t$，验证 $Y^{(q)}$ 随动量截断 $k_{\rm max} \to \infty$ 的收敛（对 BSV 高能光子尾要求 $k_{\rm max} \ge 5\,k_{\rm BZ}$）；
3. **去相干时间收敛性**：在 $T_2 \in [1, 20]\,\text{fs}$ 区间扫描，验证 $Y^{(q)}$ 随 $T_2$ 的物理合理收敛（避免 $T_2 \to 0$ 的非物理尖峰）。

---

## §3 BSV-经典光双驱动 Mach-Zehnder 干涉光路

### §3.1 光路架构

申请书 2.5 节承诺的双光路干涉光路，**详细架构**（参照 Raab et al. 2024 [arXiv:2405.11859] 的 SLM 双色场合成方案）：

```
                     SLM1 (压缩相位 θ_sq)
                          ↓
NOPA/OPA → BSV 源 ────────────→ 干涉仪 BS1
                                  ↓           ↓
                  分束          经典对照     BSV 路
                                  ↓           ↓
                              位移台        SLM2 (R, Δφ)
                              (粗延迟)        ↓
                                  ↓           ↓
                                  └──→ 合束 BS2 ──→ 样品
                                          ↑
                                       Mach-Zehnder
```

**关键元件**：
- **BSV 源**（§1.3）：高增益参量下转换 + 单模光纤模式清洁
- **SLM1**（压缩相位控制）：调节泵浦相位匹配，扫描 $\theta_{\rm sq} \in [0, 2\pi]$
- **SLM2**（强度比 + 相对相位）：调节 $R = I_{\rm classical}/I_{\rm BSV}$ 与 $\Delta\varphi$（**预期相位稳定性 < 150 mrad**，参照 Raab 2024）
- **合束 BS2**：在样品表面 $\sim 5\,\mu\text{m}$ FWHM 区域内 BSV-经典光时空重合

### §3.2 光路稳定性要求

| 参数 | 指标（**双光路干涉**，对应 2.5 节） | 指标（**Y4 反馈式升级**，对应 2.6 节 contingent） | 来源 | 风险 |
|------|-----------------------------------|----------------------------------------------|------|------|
| **相位稳定性 $\sigma_\varphi$** | $< 150\,\text{mrad}$（10 分钟积分） | **$< 50\,\text{mrad}$**（实时反馈，10 Hz 带宽） | Raab et al. 2024 [Opt. Express 32, 16284 (2024); arXiv:2405.11859]（双光路）；本项目反馈环设计指标（Y4） | 高功率 SLM 热漂移（双光路）；反馈延迟 × $g^{(2)}(0) \gg 1$（反馈式） |
| **强度稳定性 $\Delta I / I$** | $< 1\%$ | $< 1\%$（多脉冲平均后） | 单脉冲能量归一化 | BSV 功率涨落 $g^{(2)} \gg 1$ |
| **时空重合** | $< \lambda/4$（横向）$+ < 5\,\text{fs}$（纵向） | 同左（无额外要求） | 经典光 HHG 同条件 | BSV 模式清洁不充分 |
| **背景光抑制** | BSV 路 $< 10^{-6}$（相对主路） | 同左 | 空间滤波 + 偏振分束 | BSV 散射 |
| **反馈延迟** | — | **$< 100\,\text{ms}$**（含反演 + SLM1 写入） | Y4 反馈式升级设计（contingent 项） | 实时反演算法 + SLM 写入延迟 |

### §3.3 量子指纹 $Q_F$ 的统计误差分析

**量子指纹定义**（申请书 2.5 节）：
$$Q_F(R, \Delta\varphi; g^{(2)}, r) = \frac{I_{\max}(\Delta\varphi) - I_{\min}(\Delta\varphi)}{I_{\max}(\Delta\varphi) + I_{\min}(\Delta\varphi)}$$

**自洽性检验**（**critical for 量子指纹的有效性，对应申请书 1.3 问题 3**）：
- **经典光极限**：$g^{(2)} \to 1, r \to 0$ 时，BSV 退化为相干态，$Q_F$ 应回归**经典 Mach-Zehnder 干涉可见度 $V_{\rm classical}$**——理想相干态下 $V_{\rm classical} = 1$，实际受相干长度限制 $V_{\rm classical} \in [0.5, 1]$；**$Q_F \to 0$ 是物理错误**（不应出现）。
- **BSV 极限**：$g^{(2)} \gg 1, r \sim 1$ 时，$Q_F$ 应显著偏离 $V_{\rm classical}$，偏移量 $\Delta Q_F = Q_F^{\rm BSV} - Q_F^{\rm classical}$ 即为**纯量子指纹**。

**统计误差估计**（基于多脉冲统计平均）：
$$\sigma_{Q_F} = \sqrt{\frac{2\,Q_F^2(1 - Q_F^2)}{N_{\rm pulse}}} \cdot \sqrt{g_{\rm HHG}^{(2)}(0)}$$

其中 $N_{\rm pulse}$ 为总脉冲数（**本项目拟用 $N_{\rm pulse} = 10^4$–$10^5$**，对应 $g_{\rm HHG}^{(2)}(0) \sim 1.5$ 时 $\sigma_{Q_F} \sim 0.01$）。

**修正的泊松统计**：BSV-HHG 强度涨落 $g_{\rm HHG}^{(2)} \neq 1$ 会放大 $\sigma_{Q_F}$ 约 $\sqrt{g_{\rm HHG}^{(2)}}$ 倍，故需更多脉冲数才能达到与经典光 HHG 相同的 $Q_F$ 测量精度。

---

## §4 量子增强因子 QEF 的测量协议

### §4.1 QEF 的三维指标定义

申请书 1.4 创新点 2 与 2.4 节联合提出的 **QEF 三维度**（$QEF_{\rm vis}$、$QEF_{\rm yield}^{(q_{\rm ref})}$、$QEF_{\rm yield}^{(\sum)}$），测量协议分述如下：

#### §4.1.1 $QEF_{\rm vis}$（干涉可见度型）

**定义**（参照 Li et al. 2019 [Phys. Rev. Lett. 123, 153201 (2019); arXiv:1908.07283] 的 HHG 干涉能带重建）：
$$QEF_{\rm vis} = \frac{V_{\rm BSV}}{V_{\rm classical}}$$

其中 $V = (I_{\max} - I_{\min})/(I_{\max} + I_{\min}) \equiv Q_F$（**与申请书 1.3 + 2.5 节定义的量子指纹 $Q_F$ 完全等同**；本手册统一使用 $Q_F$ 名称，避免 $V$/$Q_F$ 双名漂移）。

**测量条件**：
- BSV 与经典光平均功率相等（$P_{\rm avg}^{\rm BSV} = P_{\rm avg}^{\rm classical}$）
- 同波长、同脉宽、同聚焦
- 双光路 Mach-Zehnder 干涉（同 §3.1 光路）
- 扫描 $\Delta\varphi$，提取 $Q_F$

#### §4.1.2 $QEF_{\rm yield}^{(q_{\rm ref})}$（单阶参考型，**主指标**）

**定义**（参照 Boroumand et al. 2025 [Phys. Rev. Lett. 134, 113602 (2025); arXiv:2505.22536] 的 QSHHG 理论）：
$$QEF_{\rm yield}^{(q_{\rm ref})} = \frac{Y_{\rm BSV-HHG}^{(q_{\rm ref})}}{Y_{\rm classical-HHG}^{(q_{\rm ref})}}$$

**$q_{\rm ref}$ 选取约定**（申请书 2.4 主指标定义）：
- 初定 $q_{\rm ref} \in \{7, 9\}$——对应单层 MoS₂ / WSe₂ 在近红外 0.8–1.5 μm 驱动下 3–5 倍带隙 cutoff 律的高信噪比区间；
- 选定后**全四类测量（同体系对比 + 跨体系对比）统一使用同一 $q_{\rm ref}$**，保证可比性；
- **不**对全谐波求和——避免能量权重偏差（低阶谐波产额比高阶高 2–3 个量级，直接求和会被低阶主导）。

**测量条件**：
- BSV 与经典光平均光子数相等（$\bar{N}_{\rm BSV} = \bar{N}_{\rm classical}$）
- 同波长、同脉宽、同聚焦
- 单光路（不需 Mach-Zehnder），直接测谐波谱
- 统计平均 $10^4$–$10^5$ 脉冲

#### §4.1.3 $QEF_{\rm yield}^{(\sum)}$（全谐波求和型，**辅助指标**）

**定义**：
$$QEF_{\rm yield}^{(\sum)} = \frac{\sum_{q = q_{\min}}^{q_{\max}} Y_{\rm BSV-HHG}^{(q)}}{\sum_{q = q_{\min}}^{q_{\max}} Y_{\rm classical-HHG}^{(q)}}$$

**用途**：在 $q_{\rm ref}$ 主指标已标定后，辅助验证主指标在截止频率附近的行为——若 $QEF_{\rm yield}^{(\sum)}$ 与 $QEF_{\rm yield}^{(q_{\rm ref})}$ 不一致（如 $QEF_{\rm yield}^{(\sum)} < 1$ 但 $QEF_{\rm yield}^{(q_{\rm ref})} > 1$），提示 BSV 在高阶区域的量子增强更显著（与理论预期一致）。

#### §4.1.4 三维度联合应用约定

| 维度 | 物理量 | 主要灵敏度 | 测量复杂度 | 在申请书 2.4 中的角色 |
|------|--------|------------|------------|------------------------|
| $QEF_{\rm vis}$ | 干涉可见度比 | **相位关联**（BSV 压缩态的相位压缩效应） | 中（需双光路 Mach-Zehnder） | 三类对照体系 + Y3 末标定 |
| $QEF_{\rm yield}^{(q_{\rm ref})}$ | 单阶谐波产额比 | **振幅关联**（BSV 光子数统计对产额的影响） | 低（单光路直接测谱） | 三类对照体系 + Y3 末标定（**主指标**） |
| $QEF_{\rm yield}^{(\sum)}$ | 全谐波求和比 | **全谱能量权重**（检验高阶区是否被 BSV 增强更显著） | 低（与 $QEF_{\rm yield}^{(q_{\rm ref})}$ 同一组数据换算） | 三类对照体系 + Y3 末标定（**辅助指标**） |

**强证据判据**（申请书 1.4 创新点 2 + 2.4 验收）：三类对照体系（弱关联 TMDC、中等关联莫尔、强关联 Mott）上 $QEF_{\rm vis}$、$QEF_{\rm yield}^{(q_{\rm ref})}$ 均 $> 1$，且**单调上升（TMDC < 莫尔 < Mott）**——这是"BSV-HHG 对多体关联呈额外灵敏度"的强证据。

### §4.2（保留原 4.2 内容作为对比表的扩展）— $QEF_{\rm vis}$、$QEF_{\rm yield}$ 与 §4.1 节三维度的对应

| 指标 | 物理意义 | 灵敏度 | 测量难度 | 主要误差源 |
|------|----------|--------|----------|------------|
| $QEF_{\rm vis}$（§4.1.1）| $Q_F^{\rm BSV}/Q_F^{\rm classical}$——干涉对比度量子增强 | **相位关联** | 中（需双光路） | 相位稳定性、时空重合 |
| $QEF_{\rm yield}^{(q_{\rm ref})}$（§4.1.2）| 单阶 $q_{\rm ref}$ 产额比——主指标 | **振幅关联** | 低（单光路） | 强度涨落、$q_{\rm ref}$ 选取 |
| $QEF_{\rm yield}^{(\sum)}$（§4.1.3）| 全谐波求和比——辅助指标 | **全谱能量权重** | 低（换算自 §4.1.2 数据） | 求和上下限选取 |

**本项目拟同时标定 $QEF_{\rm vis}$ 与 $QEF_{\rm yield}$**：两者同时 > 1 且数值匹配为 BSV-HHG 量子增强的强证据；任一指标 < 1 则需追溯原因（光路 vs 物理）。

### §4.3 QEF 测量的关键挑战与对策

1. **BSV 强度涨落**：$g^{(2)} \gg 1$ 导致单脉冲 HHG 产额涨落巨大，$QEF_{\rm yield}^{(q_{\rm ref})}$ 的单脉冲测量无意义。**对策**：多脉冲统计平均 + 关联分析（沿用 Hu et al. 2024 [Proc. Natl. Acad. Sci. U.S.A. 121, e2317656121 (2024)] 的 HHG-shot-by-shot 范式）。
2. **时空模式匹配**：BSV 与经典光在样品表面模式失配会人为压低 $QEF_{\rm vis}$。**对策**：模式清洁腔（MC）纯化 BSV 横模 + 自适应光学（AO）补偿波前。
3. **样品损伤**：Rasputnyi 2024 实测显示 BSV 因非经典统计（$g^{(2)}(0) > 1$ 的超聚束特性）抑制样品损伤，但平均功率相同时仍需注意热累积。**对策**：低重频（$\le 1\,\text{kHz}$）+ 旋转样品。

---

## §5 多体态探针反演协议

### §5.1 反演框架

申请书 2.4 节"多体态探针的有效性验证"的方法学框架，对应**三类对照体系**（弱关联 / 中等关联 / 强关联）的 QEF 三维度（详见 §4）联合反演：

```
            ┌─────────────────────────┐
            │  BSV-HHG 谱（三类对照）  │  ← 输入：Y^{(q)}, g^{(q)}_HHG(0), Q_F, QEF三维
            └────────────┬────────────┘
                         ↓
       ┌─────────────反演算法───────────────┐
       │  (1) SBE-Q 拟合产额 Y^{(q)}        │
       │  (2) 关联函数 g^{(q)}_HHG(0) → 多体去相干 T_2 │
       │  (3) Q_F → 压缩度 r 关联          │
       │  (4) 三类对照体系 QEF 标度律       │
       └─────────────┬─────────────────────┘
                     ↓
       ┌───────────多体参数───────────┐
       │   关联长度 ξ, 激发寿命 τ_ex │
       │   序参量（CDW/SC/Mott）     │
       │   单层 / 莫尔 / Mott 分类判据│
       └────────────────────────────┘
```

### §5.2 多体参数提取协议

| HHG 可观测量 | 反演参数 | 方法学基础 | 不确定性 |
|--------------|----------|------------|----------|
| $Y^{(q)}$ 随谐波阶次 $q$ 的衰减 | 能带结构 $\epsilon_c(\mathbf{k}) - \epsilon_v(\mathbf{k})$ | Vampa et al. 2015 [Nature 522, 462 (2015)] | 中（多解） |
| $Y^{(q)}$ 随 $g^{(2)}(0)$ 的依赖 | 关联长度 $\xi$ | Silva et al. 2018 [Nat. Photon. 12, 266 (2018); arXiv:1704.08471] | 中（依赖模型） |
| $g_{\rm HHG}^{(2),q}(0)$ 跨阶次分布 | 去相干时间 $T_2$ | Rivera-Dean et al. 2023 [arXiv:2309.14435] | 低（直接） |
| $Q_F(R, \Delta\varphi; g^{(2)})$ | 压缩度 $r$ + 关联函数 | Li et al. 2019 [Phys. Rev. Lett. 123, 153201 (2019); arXiv:1908.07283] | 中（需双光路） |
| 偶/奇谐波比（特定材料） | 序参量对称性 | Murakami et al. 2018 [Phys. Rev. Lett. 121, 057405 (2018); arXiv:1712.06460] | 中（材料专属） |
| 偏振各向异性 | Berry 曲率 $\Omega(\mathbf{k})$ | Luu et al. 2018 [Nat. Commun. 9, 3720 (2018)] | 中（需 k 分辨） |
| $QEF^{(q_{\rm ref})}$ 在三类体系上的标度律 | 关联强度定量化（TMDC / 莫尔 / Mott 三类对比） | 本项目自建（申请书 2.4 强证据判据） | 中（需 Y3 末 Y4 数据） |

### §5.3 三类对照体系参数表（申请书 2.4 子方向）

| 类别 | 材料 | 关联强度 | 工作温度 | 平台要求 | HHG 截止能量（预期） | 与 1.2.3 缺口的对应 |
|------|------|----------|----------|----------|----------------------|--------------------|
| **弱关联基线** | 单层 MoS₂ / WSe₂ | 低（$U/t \sim 3$） | 300 K（Y1-Y4 全程） | 标准聚焦光路 | $E_{\rm cut} \approx 30$–$40\,\text{eV}$（3–5 倍带隙） | TMDC 类"无关联"基线 |
| **中等关联** | 扭转双层 MoS₂ 莫尔超晶格（4°–6°） | 中（半填充附近关联绝缘相） | 300 K（Y3 室温可工作）[Wu et al. 2024, arXiv:2311.16655] | 旋转台 + AFM 确定扭转角 | $E_{\rm cut}$ 取决于扭转角（5° 附近约 25 eV） | **物理层：材料空白（中等关联首例）** |
| **强关联** | 1T-TaS₂ / κ-(BEDT-TTF)₂Cu[N(CN)₂]Br 等 Mott 绝缘体 | 高（$U/t \gg 1$） | **4 K 低温**（Y4 conditional） | 4 K 闭循环低温恒温器（已有）+ 9 T 超导磁体（conditional 升级） | $E_{\rm cut}$ 取决于带隙（1T-TaS₂ 带隙 ~0.5 eV，20–40 倍带隙上限） | **物理层：材料空白（强关联首例）** |

**注**：扭转角扫描范围 4°–6° 选自 Wu et al. 2024 的 BSV-HHG 室温可用区间；扭转角 $< 4°$ 关联更强但信号更弱（风险评估见申请书 3.3 风险表"多体态样品"）。

### §5.4 反演多解性处理

单一标量 HHG 谱 → 多体参数反演存在**本质欠定**问题。本项目拟采用三层处理：

1. **物理约束**（多维参数空间缩减）：固定材料体系 → 固定能带色散；固定温度/磁场 → 固定相变区间；固定 BSV 态参数 → 固定输入涨落。
2. **多维约束**（申请书 2.4 + 2.5 联合方案）：将 §5.2 表中的多个 HHG 可观测量同时拟合，构建**多目标反演**（贝叶斯后验概率 + 神经网络 surrogate model）。
3. **独立验证**（降低误判概率）：与 tr-ARPES、瞬态吸收、PL 等独立方法对比，验证 BSV-HHG 反演结果的一致性。

---

## §6 技术路线图与关键参数表

### §6.1 总体技术路线图（对应申请书 2.7 年度计划 + 3.4 关键交付）

```
Y1 (2027)                  Y2 (2028)                Y3 (2029)                Y4 (2030)
─────                      ─────                    ─────                    ─────
BSV 源搭建                 BSV-HHG 首例             莫尔超晶格 HHG            探针方法学（**核心**）
  ↓                          ↓                        ↓                        ↓
$g^{(2)}$ 复现            MoS₂/WSe₂ 谱            扭转双层 (室温)            Mott (4K/9T, **conditional**)
  ↓                          ↓                        ↓                        ↓
对照光路 (2.1)              SBE-Q 多带 (2.3)         $Q_F$ 全景 (2.5)          QEF 三维度 (2.4)
  ↓                          ↓                        ↓                        ↓
经典光 HHG 升级             Rivera-Dean 锚点          Raab 2024 锚点            探针方法学综述（**核心**）
                            ↓                        ↓                        ↓
                            Peschel 2022 锚点         BSV 参数依赖性 mapping    Y4 后段反馈式升级（**contingent**）
                            ↓                          (2.6 主任务)
                            Murakami 2018 基线           (optional 反馈式需 Y4 中评估)
```

**核心 / Conditional / Contingent 层级说明**：
- **核心（必须）**：BSV 源、MoS₂/WSe₂ 首例、莫尔 HHG、$Q_F$ 全景、探针方法学综述——贯穿 Y1-Y4 不可退让；
- **Conditional**：Y4 Mott 强关联体系（依赖 9 T 超导磁体按期到货；延期 → Y5 拓展，对应申请书 3.3 风险表"低温强磁场平台"）；
- **Contingent**：Y4 后段反馈式调控（依赖 Y3 末参数依赖性 mapping 数据饱和度；若饱和度不足则取消该升级项，仍以主任务 mapping 作为替代交付，对应申请书 3.3 风险表"Y4 反馈式升级"）。

### §6.2 关键参数表

| 参数 | 符号 | 目标值 | 验证方法 | 风险预案 |
|------|------|--------|----------|----------|
| BSV 中心波长 | $\lambda_{\rm BSV}$ | 0.8–1.5 μm | 光谱仪 | 固定单一波长 |
| BSV 脉冲宽度 | $\tau_{\rm BSV}$ | < 50 fs | FROG | 增至 80 fs |
| BSV 单脉冲光子数 | $\bar{N}_{\rm BSV}$ | $\ge 10^{13}$ | 功率计 | 降低至 $10^{12}$ |
| BSV $g^{(2)}(0)$ | $g^{(2)}$ | 2–3+1/N | HBT 干涉 | 接受 1.5–4 |
| BSV 压缩度 | $r$ | $\mathcal{O}(1)$ | 零差探测 | 接受 $r \sim 0.5$ |
| HHG 驱动强度 | $I_0$ | $10^{11}$–$10^{13}$ W/cm² | 功率计 + 焦点尺寸 | 调低至 $10^{10}$ |
| HHG 截止能量（弱关联 TMDC） | $E_{\rm cut}^{\rm TMDC}$ | 30–40 eV（近红外 + MoS₂） | EUV 光谱仪 | 改用 WS₂（更高产额） |
| HHG 截止能量（中等关联莫尔） | $E_{\rm cut}^{\rm moiré}$ | 约 25 eV（5° 扭转角附近） | EUV 光谱仪 | 调扭转角扫描 4°–6° |
| HHG 截止能量（强关联 Mott） | $E_{\rm cut}^{\rm Mott}$ | 取决于带隙（1T-TaS₂ ~0.5 eV 时 20–40 倍带隙上限） | EUV 光谱仪 | — |
| HHG 参考阶次（QEF 主指标） | $q_{\rm ref}$ | 7 或 9（统一全四类测量） | EUV 光谱仪 | 全四类测量统一后锁定 |
| 谱仪能量范围 | $E_{\rm range}$ | 20–80 eV（EUV） | EUV 光谱仪 | — |
| 样品温度 | $T$ | Y1-Y3: 300 K（全程），Y4 Mott: 4 K（conditional） | 低温恒温器 | 推迟 Y4 低温实验 → Y5 拓展 |
| 外加磁场 | $B$ | Y1-Y3: 0 T（全程），Y4 Mott: 0–9 T（conditional） | 超导磁体 | 推迟 Y4 强磁场 → Y5 拓展 |
| Mach-Zehnder 相位稳定性（双光路） | $\sigma_\varphi^{\rm 双}$ | < 150 mrad（10 分钟积分） | 干涉条纹监测 | 启用主动锁相 |
| Mach-Zehnder 相位稳定性（Y4 反馈式，contingent） | $\sigma_\varphi^{\rm 反馈}$ | **< 50 mrad**（10 Hz 带宽） | 实时干涉条纹监测 | 启用压电反馈 + 主动锁相 |
| 时空重合度 | $\Delta x, \Delta \tau$ | < $\lambda/4$, < 5 fs | 双光束干涉 | 启用 AO 校正 |
| 统计脉冲数 | $N_{\rm pulse}$ | $10^4$–$10^5$ | 计数器 | 增至 $10^6$ |
| Y4 反馈延迟（contingent） | $\tau_{\rm feedback}$ | < 100 ms | 反馈环时间标签 | 启用低带宽反馈 |

### §6.3 与申请书章节的交叉引用表

| 方法学手册章节 | 对应申请书章节 | 关系 |
|----------------|----------------|------|
| §1 BSV 物理与光子统计 | 1.2.2 + 2.1 | 申请书定性描述 → 手册定量参数与公式 |
| §2 量子光 SBE | 2.3 + 3.1 段 4 | 申请书理论框架 → 手册数学推导与收敛性 |
| §3 双光路干涉光路（含 Y4 反馈式稳定性） | 2.5 + 2.6（contingent） + 3.1 段 1 | 申请书光路设计 → 手册稳定性与误差分析 |
| §4 QEF 三维度测量协议 | 1.4 创新点 2 + 2.4 + 3.1 段 5 + 3.4 | 申请书定义链 → 手册测量条件与挑战（含 $q_{\rm ref}$ 选取约定） |
| §5 多体态探针反演（含三类对照参数表） | 2.4 + 3.1 段 5 | 申请书反演思路 → 手册反演协议与三类对照数据 |
| §6 技术路线图与参数 | 2.7 + 3.1 + 3.2 + 3.3 + 3.4 | 申请书总体路线 → 手册逐年里程碑 + 核心/Conditional/Contingent 层级 + 参数表 |

---

*方法学手册 v1.1 配套申请书 v5（第 5 轮对抗评审聚焦（ニ）研究内容后修订）*
*撰写时间：2026-07-28*
*章节对应：与 `proposal-draft.md` 主体一一对应*
*完整引用基线*（按出现顺序）：
- Iskhakov et al. 2012 [Opt. Lett. 37, 1919 (2012); arXiv:1202.1682]
- Spasibko et al. 2012 [Opt. Express 20, 7507 (2012); arXiv:1201.0367]
- Schleich & Wheeler 1987 [JOSA B 4, 1715 (1987)]
- Wu, Schafer, Gaarde 2016 [Phys. Rev. A 94, 063403 (2016); arXiv:1609.09852]
- Silva et al. 2018 [Nat. Photon. 12, 266 (2018); arXiv:1704.08471]
- Murakami et al. 2018 [Phys. Rev. Lett. 121, 057405 (2018); arXiv:1712.06460]
- Vampa et al. 2015 [Nature 522, 462 (2015)]
- Luu et al. 2018 [Nat. Commun. 9, 3720 (2018)]
- Peschel et al. 2022 [Phys. Rev. B 106, L081408 (2022); arXiv:2205.00522]
- Li et al. 2019 [Phys. Rev. Lett. 123, 153201 (2019); arXiv:1908.07283]
- Li et al. 2022 [Phys. Rev. Lett. 129, 173001 (2022); arXiv:2205.11161]
- Rivera-Dean et al. 2023 [arXiv:2309.14435]
- Rasputnyi A. et al. 2024 [CLEO 2024 会议论文 + arXiv:2403.15337（预印本，未经同行评审）]
- Even Tzur M., Birk M., Gorlach A., Kaminer I., Krüger M., Cohen O. 2024 [Phys. Rev. Research 6, 023064 (2024); arXiv:2311.11257]
- Wu et al. 2024 [arXiv:2311.16655]（扭转双层 MoS₂ 莫尔超晶格）
- Raab et al. 2024 [Opt. Express 32, 16284 (2024); arXiv:2405.11859]
- Hu et al. 2024 [Proc. Natl. Acad. Sci. U.S.A. 121, e2317656121 (2024)]
- Boroumand et al. 2025 [Phys. Rev. Lett. 134, 113602 (2025); arXiv:2505.22536]（**QSHHG = quantum sideband HHG，量子边带 HHG**）
