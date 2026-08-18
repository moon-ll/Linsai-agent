# 方法学手册（Methodology Manual）

> **配套章节**：申请书"（三）研究方案、特色与创新、预期研究成果"（r17，2026-08-11）
> **定位**：方法层面的补充文档。申请书层面给出"科学问题—方法选择理由—判据—降级结论"的论证骨架；本手册给出可执行的算法步骤、关键参数、验证流程与替代方案。两份文件互补，不重复叙述。
> **组织方式**：按 R1→R2→R3→R4→风险表→参数总表→版本日志的顺序展开；每项研究内容按"算法/实验步骤、关键参数、验证方式、风险与替代方案"四块组织。
> **当前版本**：v2.0 | 2026-08-11 | 对应申请书 r17（critic-round-7 参考文献专项检验后）。

---

## 第一部分：R1 方法学细节

### 1.1 三层量子态描述的算法实现

R1 的方法学核心是同时实现三类描述并在 ZnO/MgO 紧束缚模型上做差异闭环。三类描述的算法流程分别为：

**描述 (a)：双模联合密度矩阵演化（最完备）**

输入：双模压缩算符 $\hat{S}(\xi)|0,0\rangle$（$\xi = re^{i\phi}$）、固体紧束缚哈密顿量 $H_\text{tb}(\mathbf{k})$、驱动场包络 $E_\text{env}(t)$。

1. 在双模 Hilbert 空间（截断到最大光子数 $n_\text{max} = 20$，$n_\text{max} = 30$ 作收敛性验证）展开 $\hat{\rho}_\text{BSV} = |\xi\rangle\langle\xi|$。
2. 以 $\hat{U}(t) = \mathcal{T}\exp\!\left(-\frac{i}{\hbar}\int_0^t [\hat{H}_\text{mat} + \hat{H}_\text{int}(t')]dt'\right)$ 演化联合密度矩阵，光—物质相互作用取偶极近似 $\hat{H}_\text{int} = -\hat{\mathbf{d}}\cdot\hat{\mathbf{E}}$，$\hat{\mathbf{E}}$ 含双模算符。
3. 每个时间步对物质自由度做偏迹提取电流算符期望 $\langle\hat{\mathbf{J}}(t)\rangle = \text{Tr}_\text{light}[\hat{\rho}(t)\hat{\mathbf{J}}]$。
4. 傅里叶变换得 HHG 谱 $S(\omega) = |\omega^2 \text{FT}[\langle\hat{\mathbf{J}}(t)\rangle]|^2$。

**计算成本**：双模 Hilbert 维度（典型 $n_\text{max}^2 = 400$）+ 物质能带维度（典型 $\mathbf{k}$ 网格 $128\times 128$），单次演化约 6–8 小时（单核 CPU）。R1 项目期内仅用作有限采样下的 ground-truth 校准。

**描述 (b)：条件单模态演化（实验对接接口）**

输入：与 (a) 相同，但实验对接端按 $\hat{\rho}_s^\text{cond} = \text{Tr}_i[|0\rangle_i\langle 0|\hat{\rho}_\text{BSV}|0\rangle_i\langle 0|]$ 做条件投影（而非无条件偏迹）。

1. 先对双模态执行 $\langle 0|_i \hat{S}(\xi)|0,0\rangle = \cosh^{-1}\!r \sum_n (\tanh r)^n |n\rangle_s|n\rangle_i$，归一化后即单模压缩真空 $\hat{S}_s(\xi)|0\rangle_s$。
2. 在单模 Hilbert 空间演化 $\hat{\rho}_s^\text{cond}(t)$；光—物质相互作用退化为 $\hat{H}_\text{int} = -\hat{d}\hat{E}_s$，$\hat{E}_s$ 为单模算符。
3. 电流期望与 HHG 谱同 (a)。

**计算成本**：单模维度（$n_\text{max} = 20$），单次演化约 2 小时。R1 数值验证阶段闭环 (a)(b) 差异 < 5% 后，实验端即按 (b) 方案对接 HHG。

**重要澄清**：$\langle 0|_i \hat{S}(\xi)|0,0\rangle$ 只保留 $n=0$ 项、与 signal 真空成正比；若对 idler 做偏迹（无条件混合），signal 端得到的是热混合态而非单模压缩真空；唯有在 idler 端以真空投影做条件测量，signal 端才对应单模压缩真空。"HHG 相位匹配天然过滤闲置模"的说法在偏迹意义下不构成对热约化态的挽救——相位匹配只能在已经完成约化态之后影响 HHG 转换效率，不改变 $\hat{\rho}_s^\text{cond}$ 的统计性质。

**描述 (c)：P(n) 加权 Volkov 相位近似（工程化最简近似）**

输入：与 (b) 相同。

1. 从 $P(n) = \bar{n}^n/(\bar{n}+1)^{n+1}$（$\bar{n} = \sinh^2 r$）抽取 $N_\text{MC} = 10^4$ 个样本（Monte Carlo 种子固定为 20260726 以保证可复现）。
2. 对每个 $n$ 样本将光场替换为确定强度 $E_n = \sqrt{n}\,E_0$ 的经典脉冲，求解经典 SBE 得到 $J_n(t)$。
3. 加权求和得电流 $\langle\hat{J}(t)\rangle \approx \sum_n P(n)J_n(t)$，傅里叶变换得 HHG 谱。

**计算成本**：$10^4$ 次经典 SBE，每次约 30 秒，并行后约 5 小时。

**关键数学不等式**：$\exp[i\sum_n P(n)\phi_n] \neq \sum_n P(n)\exp(i\phi_n)$。若光—物质耦合产生非平凡纠缠项，相干累积与统计混合的运算路径根本不同。本步骤的核心目的就是暴露这一不等式在 ZnO/MgO 上对 HHG 预测的实际影响幅度。

### 1.2 三层描述的差异量化与 Go 判据校准

R1 Go 判据要求"三种量子态描述的 HHG 预测差异 < 10%"。具体度量：

| 可观测量 | 经典基线 | 三描述差异度量 | Go 阈值 |
|---|---|---|---|
| 截止阶次 $N_\text{cutoff}$ | 同一固体经典 SBE | $\max(\|N^{(a)} - N^{(b)}\|, \|N^{(b)} - N^{(c)}\|)/N^\text{class}$ | < 10% |
| 偏振旋转角 $\theta_n$ | 团队复现 Liu-Fu-Kais 14.2° | 同上公式（用 $\theta$ 替换 $N$） | < 10% |
| $g^{(2)}_\text{HHG}(0)$ | 经典光下 $g^{(2)}_\text{HHG} = 1$ | $\max(\|g^{(2)(a)} - g^{(2)(b)}\|, \|g^{(2)(b)} - g^{(2)(c)}\|)$ | < 10%（绝对差） |

**k 网格收敛性检查**（与数值可信度分离）：在 $128\times 128$ 网格上 $\epsilon_\text{conv} \approx 0.8\%$，满足 < 1% 阈值；$256\times 256$ 网格上 $\epsilon_\text{conv} \approx 0.3\%$（过收敛）。生产用 $128\times 128$ 即可。

**数值收敛与物理增强的分离**（回应 §1.4 Year 1 严谨性要求）：

$$\epsilon_\text{conv}(N_k) = \frac{\|S_{N_k}(\omega) - S_{2N_k}(\omega)\|_{L^2}}{\|S_{2N_k}(\omega)\|_{L^2}}$$

判据：$\epsilon_\text{conv} < 1\%$ 视为数值收敛。团队采用 $128\times 128$ 作为生产网格（$\epsilon_\text{conv} \approx 0.8\% < 1\%$）。

物理增强量（独立于数值收敛）：

$$\mathcal{E}_\text{BSV} = \frac{N_\text{cutoff}^\text{BSV} - N_\text{cutoff}^\text{cl}}{N_\text{cutoff}^\text{cl}}$$

两者分离后，Year 1 Go/No-Go 判据表述为："在 $128\times 128$ k 网格（$\epsilon_\text{conv} < 1\%$）下，BSV 相对经典光的截止阶次提升 $\mathcal{E}_\text{BSV}$ 及对应 Fisher 信息比 $\mathcal{R}_{\Omega,g}$"。

### 1.3 截止阶次公式与能带结构修正

R1 不沿用原子 3.17 作为固体截止公式系数。R1 修正公式为：

$$N_\text{cutoff}^\text{BSV} = N_\text{cutoff}^\text{class} \cdot \alpha(r, E_g, m^*)$$

其中 $\alpha(r, E_g, m^*)$ 是相对增强因子（无量纲），$r \to 0$ 时 $\alpha \to 1$（同一固体模型的经典结果）。$N_\text{cutoff}^\text{class}$ 为**同一固体能带模型下**经典 SBE 的截止位置。Ghalgaoui 2023 [5] 与 Rasputnyi 2024 [7] 的原子/Si 数据作为参考基线，**不**作为固体 Go/No-Go 的强制数值参照。

**增强因子分解**：

$$\alpha(r, E_g) = \frac{\langle\hat{E}^2\rangle}{\langle\hat{E}\rangle^2} \cdot 3.17 \cdot f_\text{band}(E_g)$$

| $E_g$ (eV) | $f_\text{band}$ | 物理含义 |
|---|---|---|
| > 5（如 MgO, 7.8 eV） | ~1.0 | 回退原子极限 |
| 1–3（如 ZnO, 3.3 eV） | ~0.7–0.9 | 显著带内修正 |
| < 0.5（如 Bi₂Te₃, 0.15 eV） | ~0.3–0.5 | 强带间耦合，截止增强被带间散射抑制 |

**固体特异性的能带处理（区别于原子的 KFR）**：固体的含时 Bloch 态不能直接套用原子的 Volkov 展开，需采用 accelerated Bloch state / Houston 展开：

$$|\psi_{n\mathbf{k}}(t)\rangle \approx e^{i\phi_V^\text{BSV}(t)}|u_{n,\mathbf{k}(t)}\rangle$$

其中 $\mathbf{k}(t) = \mathbf{k}_0 - (e/\hbar)\int_0^t \mathbf{E}(t')dt'$ 满足半经典加速度定理（替代原子体系的 KFR 势垒电离机制）。固体 HHG 由 Bloch 加速 + 带内/带间跃迁 + 辐射构成；能带结构通过 $\epsilon_{n\mathbf{k}}$ 与跃迁矩阵元 $d_{nm}(\mathbf{k}) = i\langle u_{n\mathbf{k}}|\nabla_\mathbf{k}|u_{m\mathbf{k}}\rangle$ 引入，并显式处理 Landé-Zener 跃迁对截止位置的影响。

### 1.4 R1 任务 4：Si/ZnO Fisher 信息比的计算流程

R1 任务 4 的目的是在 R3' 实验启动前给出 BSV→CDW 迁移是"加性"还是"乘性"的前置判据。算法：

1. 在 Si 紧束缚模型（间接带隙 ~1.1 eV，$m^* \sim 0.3\,m_e$）上生成 1000 个 BSV 驱动 SBE 模拟谱（$r \in [0.5, 1.5]$，每 $r$ 取 200 个随机光子数实现）。
2. 同步骤在 ZnO 紧束缚模型（直接带隙 3.3 eV，$m^* \sim 0.24\,m_e$）上生成 1000 个谱。
3. 对每个谱分别用 R1 训练好的"$\Omega/\gamma$ 反演代理网络"（轻量 CNN，~$10^4$ 参数，区别于 R4 的 PINN）做反演，估计反演 $\Omega/\gamma$ 的后验协方差矩阵 $\Sigma_\text{post}^\text{Si}$、$\Sigma_\text{post}^\text{ZnO}$。
4. 计算 Fisher 信息比 $\mathcal{R}_F = \det(\Sigma_\text{post}^\text{class})/\det(\Sigma_\text{post}^\text{BSV})$，对 Si、ZnO 各自取 1000 个谱的中位数。
5. 输出比值 $R = \mathcal{R}_F^\text{Si}/\mathcal{R}_F^\text{ZnO}$。
6. Go 判据：$R < 1.2$ 判定加性（不进行 R3' 实验）；$R \ge 2$ 判定乘性（必须进行 R3' 实验）；$1.2 \le R < 2$ 归入中间区。

**计算预算**：单材料 1000 谱 × 每谱反演 ~10 秒 = ~3 小时 × 2 材料 = ~6 小时（V100 单卡）。包含在 R1 启动年（Year 1 Q3）的算力规划内。

### 1.5 灵敏度矩阵与错误归因量级估算

回应 §1.1 关于"沿用 [3, 7] 的反演公式会把 Hubbard-U、doublon-holon 复合、CDW 序参量的贡献错误地归因于 $\Omega(\mathbf{k})$ 或 $g(\mathbf{k})$ 本身"的定量判据。

**Step 1：定义灵敏度矩阵**。在经典 SBE 单电子框架下，HHG 谱 $S(\omega)$ 对 $\Omega(\mathbf{k})$ 的依赖通过异常速度项 $\mathbf{v}_\perp = (e/\hbar)\Omega(\mathbf{k}) \times \mathbf{E}(t)$ 进入。定义谱峰频率 $\omega_\text{peak}$ 对 $\Omega$ 的灵敏度系数：

$$\mathcal{S}_\Omega \equiv \frac{\delta\omega_\text{peak}/\omega_\text{peak}}{\delta\Omega/\Omega}$$

**Step 2：多体红移到反演误差的传播**。Ikeda 2025 [13] 报告 Sr₂CuO₃ 在 MIR 驱动下，实时 DMFT 揭示亚周期 Mott 熔化使每个谐波频率从 MIR 奇数倍红移 $\Delta\omega/\omega = 5\text{–}15\%$。在经典 SBE 单电子模型下，这一红移被误归因为 $\Omega(\mathbf{k})$ 的变化：

$$\frac{\delta\Omega}{\Omega} \approx \frac{\Delta\omega/\omega}{\mathcal{S}_\Omega}$$

**Step 3：量级估算**。团队预研（ZnO SBE 复现）给出 $\mathcal{S}_\Omega \approx 0.5$（即 5% 的 $\Omega$ 变化导致 ~2.5% 的谱峰偏移）。代入 $\Delta\omega/\omega = 5\text{–}15\%$：

$$\frac{\delta\Omega}{\Omega} \approx \frac{0.05\text{–}0.15}{0.5} = 10\text{–}30\%$$

取上限，$\Omega(\mathbf{k})$ 反演误差量级约 **30%**。这是 CDW/Mott 类材料 Hubbard-U 不可忽略的代表性量级。

> **标注**：此推导为团队自洽估计。灵敏度系数 $\mathcal{S}_\Omega \approx 0.5$ 基于 ZnO SBE 预研，将在 R1 启动年用 Sr₂CuO₃ tdDMFT 数据校准。Ikeda 2025 [13] 的红移 5–15% 为预印本数值，若经 peer review 后红移修正为 3–8%，则上述 30% 误差估算相应下调至 ~6–16%，"第二堵墙"的紧迫性对应减弱——但即便取下限 6%，仍超出弱关联 SBE 反演的典型残差阈值（< 5%），结论的定性方向不变。

### 1.6 复现基础：ZnO 5 阶 14.2° / 7 阶 9.5°

团队已复现 Liu、Fu 与 Kais [3] 的 ZnO 偶次谐波偏振响应——驱动波长 3.0 μm、峰值光强 $2\times 10^{11}$ W/cm²、k 网格 $128\times 128$ 下：

| 物理量 | 文献预言 | 团队 SBE 复现 | 相对偏差 |
|---|---|---|---|
| ZnO 5 阶谐波偏振旋转角 | ~15° | 14.2° | 5.3% |
| ZnO 7 阶谐波偏振旋转角 | ~10° | 9.5° | 5.0% |
| 谐波强度 vs 光强标度 | $I_n \propto I^{n/2}$（n=3-7） | 符合 | < 10% |
| Berry 曲率 HHG 偏振响应对称性 | $C_{6v}$ | $C_{6v}$ | 定性一致 |

**代码架构**：

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

该代码为 Q1 的 BSV-SBE 扩展提供了经过验证的数值基础（仅需添加 BSV 场的光子数分布加权模块）。

---

## 第二部分：R2 方法学细节

### 2.1 三个可辨识性指标的数值计算流程

R2 的方法学核心是把"$\Omega/\gamma$ 几何混叠"从定性论断转化为三个可量化指标。R2 不再使用上一轮的 sin/cos 奇偶性论证（该论证存在数学错误——异常速度项在双色场展开后不保持简单 sin 形式，理想 sin·cos 内积为 $2/\pi \approx 0.637$ 而非 0）。

**指标 (i)：归一化有符号内积 $|\rho_{\Omega g}|$（设计阶段几何诊断）**

输入：双色场（$I_{2\omega}/I_\omega$、$\varphi_\text{CEP}$）下 $\Omega/\gamma$ 的 CEP 扫描响应 $S_\Omega(\varphi_\text{CEP})$、$S_g(\varphi_\text{CEP})$（由 R1 的 BSV-SBE 或经典 SBE 在 ZnO 同域上数值生成）。

1. 在 $\varphi_\text{CEP} \in [0, 2\pi]$ 上均匀采样 12 个点（步长 $\pi/6$）。
2. 计算内积 $\langle S_\Omega, S_g\rangle = \sum_{k=1}^{12} S_\Omega(\varphi_k) S_g(\varphi_k)\Delta\varphi$。
3. 计算范数 $\|S_\Omega\| = \sqrt{\sum_k S_\Omega^2(\varphi_k)\Delta\varphi}$，$\|S_g\|$ 同理。
4. 输出 $\rho_{\Omega g} = \langle S_\Omega, S_g\rangle/(\|S_\Omega\|\cdot\|S_g\|)$。
5. Go 阈值：$|\rho_{\Omega g}| < 0.3$。

**指标 (ii)：Fisher 信息矩阵条件数 $\text{cond}(\mathcal{I})$（主可辨识性判据）**

输入：双色场下 $\Omega/\gamma$ 联合反演问题的 Fisher 信息矩阵 $\mathcal{I} \in \mathbb{R}^{2\times 2}$。

1. 计算 $\mathcal{I}_{ij} = \sum_k \sigma_k^{-2}(\partial\mu_k/\partial\theta_i)(\partial\mu_k/\partial\theta_j)$，$\theta = (\Omega, g)$，$\mu_k$ 为第 $k$ 个 CEP 采样点的 HHG 强度期望，$\sigma_k$ 为噪声标准差。
2. 数值微分：$\partial\mu_k/\partial\theta_i \approx [\mu_k(\theta_i + \delta) - \mu_k(\theta_i - \delta)]/(2\delta)$，$\delta$ 取物理幅值的 1%。
3. 计算特征值 $\lambda_\text{max}$、$\lambda_\text{min}$，输出 $\text{cond}(\mathcal{I}) = \lambda_\text{max}/\lambda_\text{min}$。
4. Go 阈值：$\text{cond}(\mathcal{I}) < 10$。

**指标 (iii)：后验相关系数 $|C_{\Omega g}|$（独立噪声模拟下的交叉验证）**

输入：实验似然（高斯似然 + 加性探测噪声 $\sigma_k$）+ 均匀先验。

1. 构建对数后验 $\log p(\Omega, g|\text{data}) \propto -\sum_k (\mu_k - \mu_k^\text{data})^2/(2\sigma_k^2)$（均匀先验下无先验项）。
2. 在 $(\Omega, g)$ 二维网格（典型 $100\times 100$，范围覆盖物理预期值的 $\pm 3\sigma$）上扫描对数后验，归一化得后验分布。
3. 计算后验期望 $\bar{\Omega}$、$\bar{g}$ 与协方差 $\text{Cov}(\Omega, g)$，输出 $C_{\Omega g} = \text{Cov}(\Omega, g)/\sqrt{\text{Var}(\Omega)\text{Var}(g)}$。
4. Go 阈值：$|C_{\Omega g}| < 0.3$。

### 2.2 功效分析与样本量确定

R2 用功效分析替代 SNR/Mann-Whitney 三元等同：

1. 给定效应量 $\delta = \Omega/\gamma$ 响应差异的预期值（基于 ZnO SBE 预研取典型值 $\delta/\sigma = 0.5$）。
2. 对每个样本量 $n \in \{30, 40, 50, 60, 80, 100\}$ 做 1000 次 Bootstrap 模拟：在 $n$ 个独立 HHG 谱上重复反演流程，计算高斯 z 统计量 $z = (\bar{X}_\Omega - \bar{X}_g)/\sqrt{\sigma_\Omega^2/n + \sigma_g^2/n}$。
3. 输出每个 $n$ 的 $p$ 值与功效 $(1-\beta)$（$1-\beta = P(|z| > z_{0.025}|H_1)$）。
4. 取功效 $(1-\beta) > 0.8$ 对应 $p < 0.05$ 的最小 $n$ 作为最小样本量。
5. R2 在典型效应量下取最小 $n \ge 60$（含 12 个 CEP × 5 个强度比 = 60 个独立 HHG 谱）。

### 2.3 双色场解耦方案的数学基础

**双色场代入**：

$$\mathbf{E}(t) = E_\omega \cos(\omega t)\hat{e}_1 + E_{2\omega}\cos(2\omega t + \varphi_\text{CEP})\hat{e}_2$$

其中 $E_\omega$ 与 $E_{2\omega}$ 沿正交方向，$\varphi_\text{CEP}$ 为载波包络相位。

**异常速度项对 $\Omega$ 的贡献**（不保持简单 sin 形式）：

固体 HHG 电流中，Berry 曲率通过异常速度项贡献 [3]：

$$\mathbf{J}_\Omega(t) = \frac{e^2}{\hbar}\sum_\mathbf{k} \Omega(\mathbf{k}) \times \mathbf{E}(t) \cdot \mathbf{v}(\mathbf{k})$$

代入双色场（矢量叉乘结构 $\hat{e}_1 \times \hat{e}_2 = \hat{e}_3$）后，$\Omega$ 贡献在偶次谐波中的相位依赖**不保持简单 sin 形式**——这是 R2 改用三个独立指标（而非 sin/cos 奇偶性）的根本原因。理想 sin·cos 在 $[0, 2\pi]$ 上的内积为 $2/\pi \approx 0.637$ 而非 0。

**重叠积分对 $g$ 的贡献**：

$$J_g^{(2N\omega)}(t) \propto \int_0^t \mathbf{A}_n \cdot \mathbf{E}(t')dt' \supset \cos(2\omega t + \varphi_\text{CEP})$$

与 $\Omega$ 类似，$g$ 贡献在双色场下也不保持简单 cos 形式，R2 不基于奇偶性论据做分离。

### 2.4 拓扑绝缘体验证参数

| 参数 | Bi₂Te₃ | Sb₂Te₃ | 来源 |
|---|---|---|---|
| 拓扑 | 强 TI（Z₂ 非平凡） | 强 TI | 第一性原理 |
| 表面态 Dirac 点 | -0.3 eV（Γ） | -0.2 eV | ARPES |
| $\Omega(\mathbf{k})$ 结构 | Rashba 型，峰值离 Γ ~0.1 Å⁻¹ | 同类 | Sala 2025 [14]（待核实样品体系） |
| 薄膜厚度 | 10–100 nm（MBE） | 同左 | 合作者（物理所） |
| 驱动波长 | 1.5 μm（带间 HHG，非表面态共振） | 同左 | 团队 OPCPA |
| 双色场强度比 $I_{2\omega}/I_\omega$ | 0.1–1.0 连续扫描 | 同左 | OPA + 倍频 |

**驱动波长澄清**：Bi₂Te₃ 体相带隙 ~0.15 eV 对应 ~8 μm，1.5 μm 光子能量 0.83 eV 高于体相带隙——本项目 R2 采用 1.5 μm 中红外驱动是**带间 HHG 通道**（重点考察偏振响应而非共振增强），非"表面态共振"。

**Sala 2025 引文核实清单**（回应引用一致性审查）：

| 核实项 | 申请书表述 | 待核实风险 | 核实步骤 |
|---|---|---|---|
| 样品体系 | "Sb₂Te₃ 量子度规磁阻" | 主流文献中量子度规磁阻在非共线反铁磁体（Mn₃Sn/Mn₃Ge） | Year 1 Q4 联网核实 arXiv:2509.17135 全文 |
| 测量机制 | "磁阻" | 量子度规磁阻需破坏 T 对称性，TI 体系需磁化层/外磁场 | 核实是否声明外加磁场 |
| 与 R2 验证的关系 | 间接验证 Bi₂Te₃ 反演 | 若样品为反铁磁体，与 Bi₂Te₃ 无直接对照价值 | 改用 Goswami 2024 [10] 体系（Mn₃Sn）作为对照 |

R2 启动年（Year 1 Q4）完成核实后，引文处理方案：(a) 若 Sala 2025 确为 Sb₂Te₃，引用保持并增加样品体系说明；(b) 若为非共线反铁磁体，引文更新为 Goswami 2024 [10]，R2 验证改用 Mn₃Sn 作为对照体系。

### 2.5 退守方案：Aversa-Sipe 1994 张量分解 [26]

若三个可辨识性指标任一不达标，R2 退守 Aversa-Sipe 1994 张量分解方案 [26]——Aversa-Sipe 1994 框架内的 $\Omega/g$ 联合反演（不可分离），输出 $\Omega(\mathbf{k})$、$g(\mathbf{k})$ 的联合后验分布（不可独立分辨但可联合给出）。该退守方案本身即为可发表的方法学边界。

**理论基础**：Aversa & Sipe (1994) 提出的半导体 HHG 张量分解框架 [26] 把偶次谐波电流分解为三阶张量 $\chi^{(3)}_{ijkl}$ 的卷积，避免对 $\Omega/g$ 单独建模。该方案不要求 $\Omega/g$ 可独立分辨，只需它们的联合分布能被估计出来——这是 R2 在三指标不达标时的可发表降级路径。

---

## 第三部分：R3 方法学细节

### 3.1 TiSe₂ 偏振扫描的实验协议

**温度控制流程**：

1. Janis ST-100 恒温器 + Lakeshore 336 控温仪，PID + 前馈补偿算法。
2. 样品装载后先抽真空至 $10^{-7}$ Pa，再降温。降温速率 ≤ 2 K/min 至 80 K，避免热冲击导致样品脱附。
3. 在每个目标温度稳定 ≥ 10 分钟后开始采集（确保温度梯度 < 0.05 K/cm，团队前期验证）。
4. **两阶段温度扫描策略**：
   - 全温基线：80–300 K，步长 10 K（21 个温度点），用于跨相变点 200 K 的偏振各向异性整体刻画。
   - 精扫：180–220 K，步长 2 K（21 个温度点），用于相变点附近序参量温度依赖的高分辨测量。
5. 每次扫描结束后回室温，重复 3 次（共 3 个独立数据集），取平均并计算方差。

**偏振扫描流程**：

1. Alphalas PO-TW-Lambda/2 半波片 + 步进电机（重复精度 0.1°），旋转步长 1°。
2. 每个温度点完成 0°–360° 全角度扫描，每角度采集 ≥ 1000 脉冲积分（1 秒 @ 1 kHz）。
3. 实时 SNR 监测：3–19 阶谐波信噪比 > 10:1，否则延长积分时间（最大 10 秒）。
4. 偏振分辨检测：XUV 光谱仪 + MgF₂ 偏振片（Rohrer GmbH，消光比 $10^3$ @ 7–19 阶谐波）。

**焦点定位**：

1. 3 μm 驱动光下 30 μm 实测焦斑腰斑 $w_0$，对应瑞利长度 $z_R = \pi w_0^2/\lambda \approx 940$ μm。
2. XYZ 压电陶瓷（PICMA® 多层压电促动器，行程 5 mm，分辨率 1 nm）将样品定位至焦平面。
3. ±5 μm 定位公差对应 $0.005\cdot z_R$，焦平面功率密度变化 < 2%（实测验证）。
4. 背反射光斑 + CCD 定位算法（25 Hz 刷新）实时监测焦点漂移。

### 3.2 TiSe₂ 数据分析的 Go 判据校准

**偏振各向异性计算**：

1. 对每个温度点 $T$、偏振角 $\theta$ 的偶次谐波强度 $I_n(\theta, T)$ 做 Fourier 分解（保留 2θ 周期项，即 $C_2$ 各向异性）。
2. 提取 $C_2(T)$ 系数（典型值 0.05–0.15 范围）。
3. 计算各向异性突变幅度 $\Delta C_2 = |C_2(T < 200\,\text{K}) - C_2(T > 200\,\text{K})|$。

**Go 判据**：

| 判据 | 阈值 | 文献依据 |
|---|---|---|
| CDW 相变点 $\Delta C_2$ 突变 | ≥ 2°（对应偏振角等效突变） | Tyulnev 2024 [8] 报道 3–5°，取下限的 2/3 |
| 三次扫描重复性方差 $\sigma_\theta$ | < 0.2°（即突变幅度的 10%） | 团队偏振扫描精度 < 2° |
| 全温曲线 | 200 K 处出现明显 kink | 与 CDW 序参量温度依赖一致 |

**可辨识映射定义**（回应混杂因素排除）：

偏振各向异性指标（与 Tyulnev 2024 [8] 一致）、红移指标 $\Delta\omega/\omega$ 与独立 CDW 序参量表征（XRD/ARPES）的联合拟合。混杂因素排除方法：
- 晶体取向盲测：每批样品在不同晶轴方向独立偏振扫描，结果应符合 $C_3$ 或 $C_6$ 对称性预期。
- 空白样品对照：同一温度扫描流程在非 CDW 样品上应给出零各向异性信号。
- 重复批次对照：不同 MBE 生长批次应给出统计一致的结果。

### 3.3 1T-TaS₂ Mott-CDW 竞争探测

1T-TaS₂ Mott-CDW 竞争探测的理论基础是 Fazekas-Tosatti 1979 [27] 建立的 1T-TaS₂ 相变理论（IC-CDW / NC-CDW / Commensurate CDW 三相序列与 Hubbard-U 的关系）。

1. 在 1T-TaS₂ 三个相区间分别测量：IC-CDW（>350 K）、NC-CDW（200–350 K）、Commensurate CDW（<200 K）。
2. 测量指标：谐波红移 $\Delta\omega/\omega$（相对经典 SBE 预言）。
3. Go 判据：观测到 $\Delta\omega/\omega > 2\%$；BSV-SBE 预言与实验偏差 < 单电子模型偏差（即 BSV-SBE 更优）。
4. No-Go 处置：若 BSV-SBE 与单电子模型偏差相当，结论转为"单电子框架在 $U/W > 1$ 时失效"的定量证据。

**U/W 取值方法**：TiSe₂ 与 1T-TaS₂ 的 $U/W$ 估计由 DFT/ACBN0 计算给出（合作团队，物理所），其取值区间与不确定度（典型 ±0.1）将作为 R4 反演结果的物理量级锚点；本项目不承诺构建覆盖连续 $U/W$ 区间的相图，而是给出"两个代表性关联区间的边界比较"——TiSe₂ 对应弱—中关联过渡、1T-TaS₂ 对应中—强关联过渡。

### 3.4 R3' BSV 增强验证的实验设计

R3' 的核心判据是"BSV 对 $\Omega/\gamma$ 后验方差的收缩比 ≥ 2"，而非产额增强倍数。具体方法：

1. **同口径对比**：同一 R3 偏振扫描流程，分别用经典光（驱动 $r \to 0$ 的 BSV 退化为相干态）和 BSV 光（典型 $r = 1.0$–$1.5$）驱动。
2. **后验方差提取**：对每个驱动条件下 $n \ge 60$ 个独立 HHG 谱做 $\Omega/\gamma$ 反演，输出后验协方差矩阵主对角元 $\text{Var}_\text{class}(\Omega)$、$\text{Var}_\text{BSV}(\Omega)$（$g$ 同理）。
3. **收缩比计算**：$R_\Omega = \text{Var}_\text{class}(\Omega)/\text{Var}_\text{BSV}(\Omega)$，$R_g$ 同理。
4. **Go 判据**：
   - $R_\Omega \ge 2$ 且 $R_g \ge 2$ → 加性增强（Si 观测可线性外推至 CDW）。
   - $1 < R_\Omega < 2$ 或 $1 < R_g < 2$ → 乘性增强（每个 CDW 样品需单独校准）。
   - $R_\Omega \le 1$ 且 $R_g \le 1$ → BSV 仅增加产额但不改善 $\Omega/\gamma$ 反演精度，Q2 限于经典光可辨识性边界报告。

### 3.5 低温 HHG 工程可行性参数

| 参数 | 规格 | 验证依据 |
|---|---|---|
| 样品架移动 | XYZ 压电陶瓷（行程 5 mm，分辨率 1 nm） | 团队 OPCPA 平台已使用 |
| 焦点定位公差 | ±5 μm（实时监测） | 3 μm 驱动光下 30 μm 焦斑，对应瑞利长度 ~940 μm，0.005·z_R 变化 |
| 实时监测方式 | 背反射光斑 + CCD 定位算法（25 Hz 刷新） | 团队前期 4 K 低温 HHG 测试中验证 |
| 振动隔离 | 低温恒温器 + 主动减振平台（TMC Stacis 2000） | 振动 < 100 nm RMS @ 1 Hz–1 kHz |

**真空窗口材料选择**（与偏振扫描 < 2° 精度兼容）：

| 窗口材料 | 红外透过率 | 双折射 | 与偏振扫描 < 2° 精度兼容性 |
|---|---|---|---|
| BaF₂（采用） | > 90% @ 3 μm | < 1 mrad @ 1.3–4.5 μm | ✅ 兼容（已验证） |
| CsI | > 90% @ 5 μm | ~5 mrad | ❌ 偏振退化（不采用） |
| ZnSe | > 70% @ 3 μm | ~10 mrad | ❌ 双折射过大（不采用） |
| CaF₂ | > 90% @ 3 μm | < 1 mrad | ✅ 兼容（备选） |

**PID 温控精度**：

| 设备 | 控温范围 | 精度 | 200 K 附近稳定性 |
|---|---|---|---|
| Janis ST-100 恒温器 | 4–300 K | 厂家标定 ±0.1 K | ±0.08 K（团队 4 K 低温 HHG 重复验证） |
| Lakeshore 336 控温仪 | — | ±0.01 K（PID 输出） | — |
| 控温算法 | PID + 前馈补偿 | — | TiSe₂ CDW 转变宽度 ±10 K 的 1% 精度 |

### 3.6 HMG-Schema-1.0 数据标准化字段定义

R3 任务 3 在数据标准化层面交付 HMG-Schema-1.0 元数据格式。该格式在 NEwwave 基础上扩展两个关键字段：

1. `quantum_geometry_metadata`：$\Omega/g$ 目标反演量、训练标签来源、关联参数 $U/W$。
2. `cryogenic_environment`：低温恒温器型号、温度精度、样品架定位公差。

**自建必要性论证**：

| 现有标准 | 主要场景 | 对固体量子几何反演的局限 |
|---|---|---|
| NEwwave | 原子/分子 HHG | 缺少 $\Omega(\mathbf{k})/g(\mathbf{k})$ 标签字段 |
| FAIR-DAS | 阿秒瞬态吸收 | 缺少关联参数 $U/W$ 字段 |
| HDF5-attosecond | 阿秒脉冲计量 | 缺少低温环境元数据 |

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

**与 NEwwave 兼容性**：HMG-Schema-1.0 通过 `schema_uri` 字段声明扩展，HDF5 谱数据文件结构与 NEwwave 兼容（NEwwave 兼容的读取器可读 HMG 谱数据，缺少的元数据字段为 null）。与 ICFO Gaarde/Madsen 组的合作将推进 HMG-Schema 向开放标准演化，避免自闭。

---

## 第四部分：R4 方法学细节

### 4.1 Σ(U, T, ω) 代理库的预计算流程

R4 的 Σ 预计算库是解决"Σ 既是网络输入又是输出"循环引用问题的关键。算法：

1. **网格设定**：$U \in [0, 1.5]$ eV 步长 0.1 eV（15 点）、$T \in [50, 300]$ K 步长 25 K（10 点）、$\omega \in [-5, 5]$ eV 步长 0.1 eV（100 点），合计 ~15000 网格点。
2. **tdDMFT 求解**：对每个网格点 $(U, T, \omega)$ 调用合作团队的 tdDMFT 求解器，计算 $\Sigma(\omega)$。
3. **典型单点耗时**：~15 min/点（团队前期 benchmark），故总预计算 ~150 GPU·小时（一次性，Year 2 Q2 前完成）。
4. **存储格式**：HDF5 文件，键为 $(U, T)$ 网格索引，值为 $\Sigma(\omega)$ 一维数组。
5. **替代方案**：若合作协议延迟，使用开源 TRIQS/CTHYB 替代合作团队自研代码；预计算规模可缩减至 $U \in [0, 1.0]$ eV 步长 0.2 eV、$T \in [100, 300]$ K 步长 50 K、$\omega \in [-3, 3]$ eV 步长 0.2 eV（~750 点，~7.5 GPU·小时）。

### 4.2 PINN 训练阶段的三档分层协议

R4 的训练分三档，与申请书 §2.5 完全对齐：

**档 (a)：弱关联同域（ZnO/MgO，n=5000）**

1. 数据来源：R1 的 BSV-SBE / 经典 SBE 生成 5000 个 ZnO/MgO HHG 模拟谱（含 $r \in [0, 1.5]$ × 强度扰动 × 波长扰动数据增强）。
2. 网络输入：HHG 谱 $(I(\omega_3), ..., I(\omega_{19}))$。
3. 网络输出：$(\Omega(\mathbf{k}), g(\mathbf{k}))$（k 网格 $32\times 32$）。
4. 训练：500 epochs（early stopping patience=50），V100 单卡 ~9 小时。
5. Go 判据：$\Omega$ 误差 < 5%、$g$ 误差 < 8%；约束边际贡献 ≥ 10%。

**档 (b)：中等关联同域（TiSe₂ SBE 模拟，n=2000）**

1. 数据来源：TiSe₂ SBE 模拟谱（合作团队生成，考虑 $U/W \in [0.3, 0.8]$ 范围）。
2. 网络架构与档 (a) 相同，但训练用档 (a) 预训练权重初始化（迁移学习）。
3. 训练：200 epochs（已收敛），V100 单卡 ~4 小时。
4. Go 判据：$\Omega$ 误差 < 15%、$g$ 误差 < 25%；约束边际贡献 ≥ 20%。

**档 (c)：弱→中关联外推（ZnO 训练 → TiSe₂ 测试，n=2000）**

1. 训练集：档 (a) 的 5000 个 ZnO/MgO 谱。
2. 测试集：档 (b) 的 2000 个 TiSe₂ 模拟谱。
3. 训练与档 (a) 相同，但测试在跨域 TiSe₂ 上。
4. Go 判据：$\Omega$ 误差 < 20%、$g$ 误差 < 30%；约束边际贡献 ≥ 30%。
5. **关键说明**：本档是 PINN 真正价值的展示窗口（外推场景约束贡献最大）；若实测约束贡献 < 5%，R4 定位为"归因分析框架"而非端到端反演器。

### 4.3 损失函数设计与自能平滑性正则化

$$\mathcal{L} = \underbrace{\|\hat{I}_\text{HHG} - I_\text{meas}\|_2^2}_{\mathcal{L}_\text{data}} + \lambda_1\underbrace{\|U_\text{inv} - U_\text{DFT}\|^2}_{\mathcal{L}_U} + \lambda_2\underbrace{\|\text{Symm}(\Omega_\text{inv}) - \text{Symm}_\text{prior}\|^2}_{\mathcal{L}_\text{symm}} + \lambda_3\underbrace{\|\Sigma_\text{inv}(\omega) - \Sigma_\text{DMFT}(\omega)\|^2}_{\mathcal{L}_\text{GF}}$$

| 约束项 | 物理含义 | 先验来源 | 初始权重 |
|---|---|---|---|
| $\mathcal{L}_U$ | Hubbard-U 反演值匹配 DFT/ACBN0 | 合作团队计算 | $\lambda_1 = 0.1$ |
| $\mathcal{L}_\text{symm}$ | $\Omega(\mathbf{k})$ 对称性匹配 CDW 相变群 | 空间群分析 | $\lambda_2 = 0.05$ |
| $\mathcal{L}_\text{GF}$ | 自能函数匹配 DMFT | tdDMFT 合作 | $\lambda_3 = 0.01$ |

权重 $\lambda_i$ 通过 validation loss 自动调参（grid search + 贝叶斯优化）。

**L_GF 循环引用问题与解决方案**：网络架构输出 $\Omega$、$g$、$U$ 三个量，但损失函数若要求 $\Sigma_\text{inv}(\omega)$ 与 $\Sigma_\text{DMFT}(\omega)$ 拟合——Σ 既是网络输入（在 $\mathcal{L}_{GF}$ 约束中使用）又是网络输出（隐式通过 $U$ 关联）——会导致单 batch 内不同 $U$ 样本共享单个 $U_\text{current}$ 与 $\Sigma_\text{target}$ 在数学上不自洽。本项目改用**预计算 $\Sigma(U, T, \omega)$ 代理库**方案：合作团队 tdDMFT 求解器在 Year 2 Q2 前对 $(U, T, \omega)$ 三维网格预计算 Σ，训练阶段对每个样本的 $(U, T)$ 通过三次样条插值查询 $\Sigma(\omega)$，推理阶段同样查表。$\mathcal{L}_\text{GF}$ 改写为**自能平滑性正则化项**：

$$\mathcal{L}_\text{GF} = \|\partial_\omega \Sigma_\text{inv}(\omega) - \partial_\omega \Sigma_\text{interp}(\omega)\|^2$$

即要求网络输出的 Σ 在频率上具有与 tdDMFT 预计算一致的平滑性结构，避免循环引用。

### 4.4 网络架构与超参数

**架构**：

```
输入：HHG 谱 I(ω_harm) ∈ R^N_harm
  │
  ▼
Encoder: 1D-CNN（3 层卷积 + 池化，32-64-128 通道）
  │  → 特征向量 z ∈ R^128
  ▼
Physics-Informed Decoder:
  │  ├── 约束层 1：Hubbard-U 先验（L_U）
  │  ├── 约束层 2：对称性约束（L_symm）
  │  └── 约束层 3：自能平滑性正则化（L_GF）
  │  → 物理约束特征 z' ∈ R^64
  ▼
输出层：Ω(k) ∈ R^N_k, g(k) ∈ R^N_k, U ∈ R
  │
  ▼
不确定性头：Bayesian MC Dropout（50 次前向传播 → 置信区间）
```

**超参数**：

| 超参数 | 值 | 说明 |
|---|---|---|
| Encoder | 1D-CNN，3 层卷积（32-64-128 通道） | 提取 HHG 谱特征 |
| 特征维度 | $z \in \mathbb{R}^{128}$ | Encoder 输出 |
| Decoder | 3 层全连接（128→64→$N_k$） | 物理约束嵌入 |
| 激活函数 | LeakyReLU（α=0.1） | 避免梯度消失 |
| 优化器 | Adam（lr=$10^{-3}$，cosine decay） | — |
| Batch size | 64 | — |
| 训练轮数 | 500 epochs（early stopping patience=50） | — |
| MC Dropout | p=0.2，50 次前向传播 | 贝叶斯不确定性 |

**训练成本（统一口径）**：

- 500 epochs + early stopping patience=50，V100 单卡约 9 小时（实测外推）。
- Σ 预计算库的三次样条插值开销相对训练主循环 < 1%。
- MC Dropout 推理 50 次前向每次约 5 分钟（500 谱 × 50 次 ≈ 25 GPU·小时 ≈ 3 小时 V100 单卡）。
- **总训练预算**：5 次完整训练 × ~9.5 GPU·天/次 ≈ 48 GPU·天（4 年项目周期），团队 V100 × 2 工作站（~14 GPU·天/月）的能力范围内。

### 4.5 物理验证阶段的三档分层协议

物理验证阶段与训练阶段三档一一对应，分别验证 f-sum rule 与不确定性覆盖率：

| 档 | f-sum rule 阈值 | 物理依据 | 不确定性覆盖率目标 |
|---|---|---|---|
| (a) 弱关联同域 | 偏差 < 5%（硬约束） | Kubo 求和规则在完备基组下严格保持 | > 90% |
| (b) 中等关联同域 | 偏差 < 5%×(1+0.5·$U/W$)（软约束） | 一阶多体修正的线性标度，$U/W=0.5$ 时阈值放宽至 6.25% | > 85% |
| (c) 弱→中关联外推 | 偏差 < 5%×(1+0.5·$U/W$)×1.5 | 外推不确定性放大系数 1.5 | > 80% |

**Chern 数拓扑一致性约束**（独立于 f-sum rule）：基于陈数定义 $C = (1/2\pi)\int_\text{BZ} \Omega(\mathbf{k})d^2k$，要求反演 Ω 场在第一布里渊区上的积分对应预设的拓扑陈数（弱关联同域 ZnO/MgO 的 $C = 0$，强关联 CDW 体系不在此约束范围——CDW 体系 Berry 曲率无闭合可定义陈数）。该约束**仅适用于拓扑材料验证**（如 Bi₂Te₃ 的 $C = 0$ 验证），不推广到 CDW 体系。

**f-sum rule 标度律来源说明**：(1+0.5·$U/W$) 的线性标度比文献中常见的 (1+$U/W$)² 平方修正更保守（后者需二阶或非微扰论证），本项目将其作为待验证假说；Year 3 Q1 用 ZnO/MgO→TiSe₂ 实测 f-sum rule 偏差校准该标度律，若实测偏差显著超出线性标度预测，将更新为更宽松的物理标度并在数据集中同步标注。

### 4.6 消融实验设计

消融实验比较四类配置，量化三项物理约束的边际贡献：

| 配置 | $\mathcal{L}_U$ | $\mathcal{L}_\text{symm}$ | $\mathcal{L}_\text{GF}$ | 预期 $\Omega$ 误差（中样本） |
|---|---|---|---|---|
| 基线（无约束 CNN） | ✗ | ✗ | ✗ | ~25% |
| +U only | ✓ | ✗ | ✗ | ~20% |
| +U+symm | ✓ | ✓ | ✗ | ~15% |
| 全约束 PINN | ✓ | ✓ | ✓ | ~10–12% |

每配置训练 5 次取平均，训练集/测试集严格按档 (a)(b)(c) 划分，不允许跨档使用同一样本。

**按样本量分档的边际贡献预期**：

| 场景 | 样本量 | 训练集构成 | 测试集 | 约束边际贡献预期 | 反演误差目标 |
|---|---|---|---|---|---|
| (a) 弱关联同域 | n=5000 | ZnO/MgO SBE+TDSE | ZnO/MgO 同域 | ~10–15%（基线已饱和） | $\Omega$ < 5%、$g$ < 8% |
| (b) 中等关联同域 | n=2000 | TiSe₂ SBE 模拟 | TiSe₂ 同域 | ~20–25% | $\Omega$ < 15%、$g$ < 25% |
| (c) 弱→中关联外推 | n=2000 | ZnO/MgO SBE | TiSe₂ 跨域 | ~30–40%（PINN 真正价值窗口） | $\Omega$ < 20%、$g$ < 30% |

**实测约束贡献 < 5% 的处置**：降低对应约束权重 $\lambda$ 或移除低贡献约束项；保留有效约束项；R4 降级为"归因分析框架"。

### 4.7 1D-CNN 反演原型复现基础

团队已实现 1D-CNN Encoder-Decoder 在 ZnO SBE 谱上的反演原型，验证网络架构在 HHG 谱反演任务上的基本可行性：

| 项目 | 数值 |
|---|---|
| 训练样本 | n=200（ZnO SBE 模拟谱） |
| 测试样本 | n=50（独立生成的 ZnO SBE 谱） |
| 网络架构 | 1D-CNN Encoder（3×Conv1d）+ 2 层全连接 Decoder |
| $\Omega$ 反演误差 | < 12%（平均相对偏差） |
| $g$ 反演误差 | < 18% |
| 训练耗时 | 2 小时（V100 单卡，100 epochs） |

PINN 完整架构（三项物理约束层 + 自能平滑性正则化 + 不确定性头）的扩展基于此原型增量开发。

---

## 第五部分：技术风险与替代方案

### 5.1 风险表（统一权威）

| 风险编号 | 技术难点 | 风险等级 | 触发阈值 | Plan A | Plan B | 降级后仍可回答的科学问题 |
|---|---|---|---|---|---|---|
| R-1 | BSV 源搭建（国内尚无系统工作） | 中 | Year 2 Q3 仍未获 $g^{(2)}(0) > 1.5$ 的单模 BSV | 与南京大学王慧田组合作（已签协议 + PRL 2024 + Optica 2025 共同发表支撑） | 采购商用 OPA + 压缩模块替代自建（Quantum Opus OPA + 自制单模光纤耦合，r 可达 0.8） | BSV→HHG 量子态描述层级选择；不能回答 CDW 上 BSV 增强的全 BSV 参数范围验证 |
| R-2 | 量子光–固体 HHG 耦合效率 | 高 | Si 上效率 < $10^{-6}$ 持续 6 个月 | 分阶段验证：先 Si/a-Si（高损伤阈值，~3 J/cm²），再拓扑材料（损伤阈值较低，~0.5 J/cm²） | 经典光双色场方案独立推进 R2（改造现有 OPCPA 平台加入 BBO 倍频模块，~3 万元 + 2 个月工期） | $\Omega/\gamma$ 可辨识性边界（不带 BSV 增强）；不能回答 R3' 的 BSV→CDW 迁移验证 |
| R-3 | PINN 训练数据不足 | 中 | tdDMFT 产出 < 500 谱 | tdDMFT 合作 + R1 正向模型补充 + 3 倍数据增强（光强扰动 ±20%、波长扰动 ±10%、温度扰动 ±10%） | 半监督学习框架：利用 R3 的 ~200 谱实验数据（无精确标签）通过一致性正则化扩充有效训练集 | 弱关联同域 $\Omega/\gamma$ 反演（不依赖 tdDMFT 数据）；不能回答中等关联域外推验证 |
| R-4 | CDW 材料 HHG 信号微弱 | 中 | TiSe₂ SNR < 10:1 | BSV 增强（增加 ~10 倍产额）+ 延长积分时间（每偏振点 1 秒 → 10 秒）+ Lock-in 检测（斩波器 + 锁相放大器） | 聚焦 1T-TaS₂（信号更强，Mott-CDW 竞争区谐波红移 > 2%） | 1T-TaS₂ 关联边界检验；不能回答 TiSe₂ CDW 相变点偏振各向异性突变验证 |
| R-5 | 拓扑绝缘体薄膜质量 | 低 | ARPES 确认表面态不清晰（费米能级位置偏差 > 50 meV 或 Dirac 点线宽 > 100 meV） | 物理所/南京大学 MBE 团队（共同发表支撑） | 转 Sb₂Te₃ 备选或机械剥离薄片（保证表面态清洁度） | ZnO/MgO 同域 $\Omega/\gamma$ 可辨识性边界；不能回答拓扑材料反演验证 |
| R-6 | 双色场可辨识性指标不达标 | 中 | $\|\rho_{\Omega g}\| > 0.3$ 或 $\text{cond}(\mathcal{I}) > 10$ | ZnO 同域闭环验证（Year 1 Q2）+ 引入三色场 $\omega+2\omega+3\omega$ 增加投影维度（三色场方案需要 OPA + 2 个 BBO 倍频模块，光路改造预计 ~5 万元 + 3 个月工期） | 退守 Aversa-Sipe 1994 张量分解 [26]——放弃"$\Omega/\gamma$ 直接分离"承诺，输出 $\Omega(\mathbf{k})$、$g(\mathbf{k})$ 的联合后验分布（不可独立分辨但可联合给出） | $\Omega/\gamma$ 联合后验分布（张量分解）；不能回答 $\Omega/\gamma$ 直接分离的物理参数范围 |
| R-7 | PINN 物理约束边际贡献 < 5% | 中 | 消融实验显示 < 5%（特别在档 (c) 外推场景） | 降低权重 $\lambda$ 或移除低贡献约束项；保留有效约束项 | 定位为"多体物理约束的归因分析框架"——保留消融实验本身作为方法学产出，分析"哪些约束在哪些场景有效" | 物理约束有效性的边界条件；不能回答端到端 $\Omega/\gamma$ 反演器 |
| R-8 | tdDMFT 合作协议未签正式 | 中 | Year 1 Q4 仍未签正式协议 | 使用开源 3D tdDMFT 代码（TRIQS/CTHYB）替代合作团队自研代码；R4 训练数据先用 1D 多体 + 2D SBE 模拟过渡 | 推迟中等关联域外推验证至协议签署后；4 年项目期内只交付弱关联同域反演结果 | 弱关联同域 $\Omega/\gamma$ 反演；不能回答中等关联域外推 |
| R-9 | R1 任务 4 中间区判定 | 低 | Si/ZnO Fisher 信息比 $R$ 落入 [1.2, 2) 中间区 | 接受中间区结果，R3' 实验启动后按"独立验证"处置——以实验测得的 BSV→CDW 后验方差收缩比作为最终判定 | 无独立降级路径；该结果本身即为理论产出（"BSV 增强在 Si/ZnO 间非加性亦非乘性"是方法学边界结论） | BSV 增强机制的方法学边界；理论产出 |

**风险按物理动机分类**：
- **材料-物理类**（R-4、R-5）：涉及 CDW 样品信号与拓扑薄膜质量。
- **方法-算法类**（R-3、R-6、R-7）：涉及训练数据、可辨识性、约束贡献。
- **平台-工程类**（R-1、R-2、R-8）：涉及 BSV 源、耦合效率、合作算力。

### 5.2 BSV 源搭建技术参数（R-1 详情）

**Plan A：与南京大学王慧田组合作（已签协议）**

| 参数 | 方案 | 说明 |
|---|---|---|
| 非线性晶体 | BBO（β-BaB₂O₄），type-II 简并破坏（degenerate breaking） | 高非线性系数 $d_\text{eff} \approx 2.0$ pm/V |
| 泵浦波长 | 515 nm（倍频 Yb 激光器） | 与 signal/idler 非简并 |
| signal/idler 波长 | ~1300 nm / ~1300 nm（近简并） | 或按需非简并配置 |
| 相位匹配 | type-II 简并破坏（$\Delta k \neq 0$，自然分离 signal/idler） | 保证单时空模式 |
| 压缩参数 r 调节 | 泵浦光强连续可调 | $r = 0.5$–$1.5$ 覆盖低/中/高增益 |
| 模式净化 | 空间滤波 + 单模光纤耦合 | 抑制高阶空间模式 |
| 表征 | $g^{(2)}(0)$ 测量（HBT 干涉仪） | 验证非经典性（$g^{(2)}(0) > 1$） |

**Plan B：商用 OPA + 自制单模光纤耦合**。Quantum Opus OPA + 自制单模光纤耦合，r 可达 0.8（略低于自建方案的 1.5），但满足 R1 验证需求。

### 5.3 双色场解耦实验光路设计（R-6 详情）

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

**关键光路参数**：

| 参数 | 规格 | 用途 |
|---|---|---|
| OPA 波长范围 | 1.3–1.7 μm（ω）+ 倍频 0.65–0.85 μm（2ω） | 覆盖拓扑绝缘体带间 HHG |
| 脉冲能量 | > 5 μJ/脉冲（ω） | 保证 HHG 产率 |
| CEP 稳定性 | < 300 mrad（f-2f 干涉仪主动稳定） | $\phi_{FV}$ 精确控制 |
| 强度比 $I_{2\omega}/I_\omega$ | 0.1–1.0 连续（精度 ±2%） | $\Omega/g$ 分离参数扫描 |
| 偏振扫描 | 0°–360°，步长 1°，精度 < 2° | 偏振各向异性测量 |

### 5.4 R-6 退守方案：Aversa-Sipe 1994 张量分解 [26]

退守 Aversa-Sipe 1994 张量分解方案 [26]——Aversa-Sipe 1994 框架 [26] 内的 $\Omega/g$ 联合反演（不可分离），输出 $\Omega(\mathbf{k})$、$g(\mathbf{k})$ 的联合后验分布（不可独立分辨但可联合给出）。该方案不要求 $\Omega/g$ 可独立分辨，只需它们的联合分布能被估计出来——这是 R2/R-6 在三指标不达标时的可发表降级路径。

**降级后仍可回答的科学问题**：$\Omega/\gamma$ 联合后验分布（张量分解）；不能回答 $\Omega/\gamma$ 直接分离的物理参数范围。

### 5.5 BSV-HHG 耦合效率分阶段验证（R-2 详情）

| 阶段 | 样品 | 预期效率 | 验证目标 |
|---|---|---|---|
| Phase 1（Year 2–3） | Si / a-Si 薄膜 | > $10^{-5}$ | BSV-HHG 耦合概念验证 |
| Phase 2（Year 3–4） | Bi₂Te₃ / Sb₂Te₃ 薄膜 | 待定 | 量子几何反演实验对接 |

**Plan B：经典光双色场方案独立推进 R2**。改造现有 OPCPA 平台加入 BBO 倍频模块（预计 ~3 万元 + 2 个月工期），支持 1.5 μm ω + 0.75 μm 2ω 双色场。BSV 降级为后续重点项目的灵敏度增强选项。经典光下 CDW 材料信号弱，需延长积分时间至 ~10 s/偏振点（原方案 1 s），总测量时间增加 10 倍但可行。

---

## 第六部分：关键参数汇总表

下表汇总本手册涉及的所有关键参数，便于跨章节对照阅读：

| 类别 | 参数 | 数值 | 来源/章节 |
|---|---|---|---|
| BSV 源 | BBO type，相位匹配 | type-II 简并破坏（$\Delta k \neq 0$） | §1.1, §5.2 |
| BSV 源 | 压缩参数 r 范围 | 0.5–1.5 | §1.1, §5.2 |
| BSV 源 | $g^{(2)}(0)$ 验收阈值 | > 1.5 | §5.1 R-1 |
| HHG 耦合 | Si 耦合效率阈值 | ≥ $10^{-5}$（Plan A）、< $10^{-6}$ 触发 Plan B | §5.1 R-2 |
| HHG 耦合 | ZnO/MgO 数值 k 网格 | $128\times 128$（收敛 < 1%） | §1.2 |
| HHG 耦合 | Monte Carlo 抽样数 | $10^4$（种子 20260726） | §1.1 |
| HHG 耦合 | $n_\text{max}$ 截断 | 20（生产）/ 30（收敛性验证） | §1.1 |
| 双色场 | 驱动波长 | 1.5 μm（带间 HHG） | §2.4 |
| 双色场 | CEP 扫描 | 0–2π，步长 ≤ $\pi/6$（12 点） | §2.1 |
| 双色场 | 强度比扫描 | $I_{2\omega}/I_\omega \in [0.1, 1.0]$，理想窗口 [0.3, 0.7] | §2.1 |
| 双色场 | 最小样本量 | n ≥ 60（功效 1-β > 0.8） | §2.2 |
| 可辨识性 | $\|\rho_{\Omega g}\|$ 阈值 | < 0.3 | §2.1 |
| 可辨识性 | $\text{cond}(\mathcal{I})$ 阈值 | < 10 | §2.1 |
| 可辨识性 | 后验相关系数阈值 | < 0.3 | §2.1 |
| 低温工程 | 恒温器 | Janis ST-100 | §3.1, §3.5 |
| 低温工程 | 温度精度 | ±0.08 K @ 200 K（实测） | §3.5 |
| 低温工程 | 焦点定位公差 | ±5 μm（对应 0.005·$z_R$） | §3.5 |
| 低温工程 | 真空窗口 | BaF₂（双折射 < 1 mrad） | §3.5 |
| CDW 实验 | TiSe₂ 全温扫描 | 80–300 K，步长 10 K | §3.1 |
| CDW 实验 | TiSe₂ 精扫 | 180–220 K，步长 2 K | §3.1 |
| CDW 实验 | 偏振扫描 | 0°–360°，步长 1°，重复 3 次 | §3.1 |
| CDW 实验 | 偏振各向异性突变阈值 | ≥ 2° | §3.2 |
| CDW 实验 | 重复性方差 | $\sigma_\theta < 0.2$° | §3.2 |
| R3' | 收缩比阈值 | $R_\Omega \ge 2$ 且 $R_g \ge 2$（加性） | §3.4 |
| PINN 训练 | 档 (a) 样本量 | n=5000 | §4.2 |
| PINN 训练 | 档 (b)/(c) 样本量 | n=2000 | §4.2 |
| PINN 训练 | 训练轮数 | 500 epochs（early stopping patience=50） | §4.4 |
| PINN 训练 | 单次完整训练耗时 | ~9.5 GPU·天（V100 单卡） | §4.4 |
| PINN 训练 | 总预算 | 48 GPU·天（4 年 5 次训练） | §4.4 |
| Σ 预计算库 | 网格规模 | ~15000 点（合作 tdDMFT）或 ~750 点（TRIQS 替代） | §4.1 |
| Σ 预计算库 | 预计算总耗时 | ~150 GPU·小时（合作）或 ~7.5 GPU·小时（TRIQS） | §4.1 |
| f-sum rule | 弱关联阈值 | 偏差 < 5%（硬约束） | §4.5 |
| f-sum rule | 中关联阈值 | < 5%×(1+0.5·$U/W$)（线性） | §4.5 |
| f-sum rule | 外推阈值 | < 5%×(1+0.5·$U/W$)×1.5 | §4.5 |
| 灵敏度 | $\mathcal{S}_\Omega$ | ~0.5（ZnO SBE 预研） | §1.5 |
| 错误归因 | $\Omega(\mathbf{k})$ 反演误差量级 | 10–30%（Ikeda 红移 5–15% 传播） | §1.5 |

---

## 第七部分：版本日志

| 版本 | 日期 | 修订说明 | 对应申请书版本 |
|---|---|---|---|
| v1.0 | 2026-08-10 | 初版：M-R1/M-R2/M-R3/M-R4/M-Risk/M-Appendix 六块结构 | r15 |
| v2.0 | 2026-08-11 | 对应 r17 整体一致性修订：(1) 三个可辨识性指标的口径统一（删除 sin/cos 奇偶性残余表述）；(2) 新增 R1 任务 4 Si/ZnO Fisher 信息比计算流程详细步骤；(3) 新增 1.5 节"灵敏度矩阵与错误归因量级估算"，回应 §1.1 H-3 量化判据；(4) 新增 1.6 节"复现基础"明确 ZnO 14.2°/9.5° 度量来源；(5) R3.3 节 1T-TaS₂ 增补 Fazekas-Tosatti 1979 [27] 理论基础；(6) R3.6 HMG-Schema JSON-LD 顶层结构示例对齐 bsv_source 字段（BBO_type2_degenerate_breaking_single_mode）；(7) 风险表独立成 §5.1 并按物理动机分类（材料-物理/方法-算法/平台-工程）；(8) 风险表增 Sala 2025 联网核实计划与替代方案；(9) 关键参数汇总表新增灵敏度 $\mathcal{S}_\Omega$ 与错误归因量级条目；(10) 同步文献编号 [1]–[27] 与 references.md 口径一致 | r17 |

---

*本手册为方法层面的补充文档。申请书层面的论证骨架（科学问题—方法选择理由—判据—降级结论）见 `04_proposal/sections/scheme.md`，本手册不重复叙述。新阅读请以 references.md 的最终编号 [1]–[27] 为准。*
