---
title: "2025-2509_20504-hot-but-coherent-doublons-at-infinite-temperature-in-the-hub"
type: "papers"
created: "2026-09-27T00:14:14Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["强关联体系", "强场超快", "强场驱动", "量子几何"]
source_raw: "2025-2509.20504-hot-but-coherent-doublons-at-infinite-temperature-in-the-hub.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # Hot but Coherent: 无穷温度 Hubbard 链上的相干 Doublon

  ## 林赛的理解

  这篇工作直接回答了一个对我们强场超快方向至关重要的问题：在热涨落最强的极限（无穷温度、最大混合态）下，强关联体系中载流子的**相干输运究竟死不死**。答案出乎意料——doublon（双占据束缚态）不但存活，还能在外电场下做长寿命 Bloch 振荡，谱上保持清晰的 Wannier–Stark 梯子。对我们而言，这意味着"热背景不必然杀死相干动力学"，这正是强场驱动 Mott 绝缘体、光致 doublon–holon 产生与超快输运课题的理论地基之一。它给我们的提示有两层：一是理论建模上，无穷温度 + superfermionic 向量化 + Chebyshev 谱展开是一个可复用的高分辨率计算框架，可以直接移植到我们处理的 Hubbard 类强关联模型；二是物理图像上，"电场诱导相干梯子结构 vs 相互作用诱导的双带劈裂（∼2U）相互竞争"这一图像，可以作为我们设计"用强场分离 doublon 与多粒子通道"类实验方案的核心叙事。

  ## 研究问题

  一维 Hubbard 模型在**无穷温度极限**（maximally mixed state，所有微观态等概率）下：

  1. doublon 的动量–频率分辨谱函数 $A_d(k,\omega)$ 是否还保留可辨识的准粒子特征，还是会被热涨落彻底洗平？
  2. doublon 的**相干性**在最强热扰动下能否存活？具体判据是：加静态电场后是否仍能观察到 Wannier–Stark 梯子与长寿命 Bloch 振荡。
  3. 相互作用 $U$ 与电场 $E$ 如何竞争性地塑造 doublon 的谱结构与实空间动力学（量子行走、光锥传播）？

  核心论点：即使热模糊达到极大，well-defined 的 doublonic 特征在谱域与实时动力学中都持续存在——"hot but coherent"。

  ## 研究背景

  - Doublon 是 Hubbard 模型中最有实验相关性的激发之一（Mott 绝缘体非平衡动力学、冷原子系统、关联电子材料），尽管形成能 ~U 很大，却因能量约束与动力学选择定则而表现出意外长的寿命与相干运动（Sensarma et al., PRB 82, 224302 (2010)；Eckstein & Werner, PRB 84, 035122 (2011)）。
  - 既有工作集中在零温/低温：doublon 谱、双占据寿命、Bloch 振荡阻尼等（Heidrich-Meisner et al. 2010；Rausch & Potthoff, PRB 95, 045152 (2017)；Nocera et al., PRB 97, 045146 (2018)）。
  - 高温极限所知甚少：强热涨落预期会压制准粒子相干性，无穷温度下 doublon 是否仍有意义、谱信号是否被完全抹掉，是开放问题（Tindall et al., PRL 123, 030603 (2019) 涉及加热诱导的 η pairing，但 doublon 谱本身缺系统研究）。
  - 在无穷温度工作的好处：热模糊最大化，从而把**相互作用驱动效应**与**温度驱动效应**干净地解耦。

  ## 研究方法

  本文方法密度高：核心方法论贡献是"Chebyshev 展开 + superfermionic 向量化密度矩阵"的无穷温度谱函数计算框架。按方法卡整理如下。

  **1. 原理**

  无穷温度密度矩阵 $\rho \propto 1$ 可通过引入对偶费米子算符 $\tilde{c}_{x\sigma}, \tilde{c}^\dagger_{x\sigma}$（对易关系 $\{\tilde{c}_{x\sigma}, \tilde{c}^\dagger_{x'\sigma'}\} = \delta_{x,x'}\delta_{\sigma,\sigma'}$）向量化为一个**乘积态**，从而把期望值计算转化为 enlarged Hilbert 空间的内积，再用 Chebyshev 多项式展开直接算频率空间的谱函数，绕开显式时间演化与有限时间截断。实时动力学则通过向量化的 von Neumann 演化 + MPS/Trotter 两比特门实现。无穷温度初态在 system–auxiliary 二分上**无纠缠**，纠缠增长极小，MPS 模拟开销低。

  **2. 参数表（数值原样，出自原文公式与图注）**

  | 参数/配置 | 数值 | 出处 |
  |---|---|---|
  | 模型 | 一维 Hubbard，哈密顿量 $H = -\frac{J}{2}\sum_{i,\sigma}(c^\dagger_{i\sigma}c_{i+1,\sigma}+h.c.) + U\sum_i (n_{i\uparrow}-\frac{1}{2})(n_{i\downarrow}-\frac{1}{2})$ | 式(1) |
  | 链长 | $L = 50$（谱函数计算） | Fig. 1 图注 |
  | 相互作用扫描 | $U = 0.0,\ 0.5,\ 1.0,\ 2.0,\ 4.0,\ 8.0$（单位 J） | Fig. 1/2/3/5/6 |
  | 电场强度 | $E = 1$（主数据）；局域动力学对比用 $E = 0.1$ 与 $E = 1.0$（$U = 8$） | Fig. 2/3 图注、Fig. 4 |
  | 谱展开 | Chebyshev 多项式展开至 $N_{\max}$ 阶，Jackson 核抑 Gibbs 振荡；Liouvillian 线性重标 $a=\frac{L_{\max}-L_{\min}}{2-\delta},\ b=\frac{L_{\max}+L_{\min}}{2}$，$\delta \sim 0.01$ | 式(14)–(18) |
  | 谱边界 | $L_{\min}, L_{\max}$ 由**两次独立 DMRG 计算**确定 | §II.A |
  | 局域态（半填充） | $\lvert\rho_j\rangle\rangle = \frac{1}{4}(\lvert 0,\tilde{0}\rangle_j - i\lvert\uparrow,\tilde{\uparrow}\rangle_j - i\lvert\downarrow,\tilde{\downarrow}\rangle_j + \lvert\uparrow\downarrow,\tilde{\uparrow}\tilde{\downarrow}\rangle_j)$ | 式(12) |
  | 电荷/自旋不平衡 | 可推广含 $\mu$（电荷）与 $\mu_z$（自旋）的权重因子，$Z$ 归一化 | 式(13) |
  | 单位制 | 自然单位 $e = \hbar = 1$，故 $\omega_B = E$ | §II |
  | 实时演化 | MPS + Trotter 分解两比特门，作用于 doubled Hilbert 空间 | §II.A |
  | 软件库 | ITensor（Fishman, White & Stoudenmire, SciPost Phys. Codebases, 004 (2022)） | §II.A |
  | doublon 产生算符 | $d^\dagger_x = c^\dagger_{x\uparrow} c^\dagger_{x\downarrow}$；动量空间 $d^\dagger_k = \frac{1}{\sqrt{L}}\sum_x e^{ikx}d^\dagger_x$ | 式(2)(3) |
  | 谱函数定义 | $A_d(k,\omega) = -2\,\mathrm{Im}\,G^d(k,\omega) = A_{2\text{-p}} + A_{2\text{-h}}$；动量积分 $A_d(\omega) = \frac{2\pi}{L}\sum_k A_d(k,\omega)$ | 式(6)–(8) |
  | 电场两种规范 | 标量势规范：$H_E = H + E\sum_x x\,n_x$（破平移对称，失动量好量子数）；矢量势规范：Peierls 替换 $t \to t e^{iA(t)}$，$A(t) = -Et$（保时移对称、含时） | 式(9)、§II |
  | Bloch 振荡周期 | $T_B = 2\pi/\omega_B$ | §III.B |

  **3. 适用边界**

  - 动量分辨谱函数需对每个 $k$ 单独做一次 Chebyshev 递推，$k$ 点数决定总开销。
  - 谱分辨率受 Chebyshev 截断阶 $N_{\max}$ 与 Jackson 核展宽限制；频率需经 $\omega = a\omega' + b$ 重标回物理值。
  - 标量势规范下动量不再是好量子数，只能做动量积分谱 $A_d(\omega)$；动量分辨需切矢量势规范，但该规范含时、原则上需双时间变量的 Green 函数（文中对湮灭算符时间变量取 0 作简化，是一个近似）。
  - 一维链 + 最近邻跳跃；结论向高维/长程相互作用的推广未经检验。

  **4. 代表作（方法关键文献）**

  - Weiße, Wellein, Alvermann & Fehske, "The kernel polynomial method", Rev. Mod. Phys. 78, 275 (2006)——核多项式方法总纲。
  - Ganahl et al., PRB 90, 045144 (2014)；Holzner et al., PRB 83, 195115 (2011)——MPS 框架下的 Chebyshev 谱函数展开。

  ## 主要发现与核心结论

  1. **无穷温度下 doublonic 谱特征仍然清晰存在**——谱域与实时动力学双重确认（摘要与结论）。
  2. **无相互作用极限 $U=0$**：谱为单一连续带，限制在 $\omega \in [-2J, 2J]$；在 $k = \pm\pi$ 处出现 $\omega = 0$ 的尖锐共振 $A_d^{(0)}(k=\pm\pi,\omega) \propto \delta(\omega)$。解析结果为 $A_d^{(0)}(k,\omega) = \frac{2\pi}{L}\sum_q \delta(\omega - \varepsilon_{k+q} - \varepsilon_q)$，$\varepsilon_k = -J\cos k$（式(21)），与 Chebyshev 数值结果一致。
  3. **相互作用增大导致谱劈裂**：随 $U$ 增大，谱重逐渐分离为两个明确定义的带——低频 2-h（双空穴）带与高频 2-p（双粒子）带，**间隔 ∼ 2U**；中等耦合（$U \lesssim 2\text{–}3$）两带仍部分重叠，大 $U$ 下完全分离。粒子–空穴对称在 $U>0$ 时被打破。
  4. **加电场 $E=1$ 出现 Wannier–Stark 梯子**：$U=0$ 时谱为位于 Bloch 频率整数倍 $\omega = n\omega_B$ 的 δ 峰级（式(22)）；即使 $U$ 很大，每个带内梯子状共振仍然可见但逐渐被阻尼——只要电场足够强，相干梯子结构在相互作用劈裂的谱中存活。
  5. **长寿命 Bloch 振荡**：$|G_d(x,t)|$ 呈现周期 $T_B = 2\pi/\omega_B$ 的振荡，且**在有限 $U>0$ 下持续存在**。局域信号（$U=8$）呈现快振荡 $\omega_U \approx U$ 被慢 Bloch 频率 $\omega_B$ 调制的结构，振幅指数衰减，行为由 $-\mathrm{Im}\,G_d(x=0,t) \propto \cos(\omega_U t)\cos(\omega_B t)e^{-\gamma t}$ 刻画（式(23)），衰减率 $\gamma$ 敏感依赖于 $U$ 与 $E$。弱场下小的 $\omega_B$ 被快衰减掩盖，强场下 $\omega_B$ 调制即便在大 $U$ 也清晰可见。
  6. **Doublon 量子行走的双光锥结构**：注入局域 doublon 后出现两条光锥——外层与 $U$ 无关，对应单粒子激发速度 $v_F \propto J$；内层仅在有限 $U$ 出现，对应 doublon 速度 $v_d \propto J^2/U$（强耦合下二阶有效跳跃）。非相干单粒子扩散与相干 doublon 运动共存。
  7. **Doublon 数不守恒但表现出"涌现守恒"**：尽管 $[d^\dagger d, H_{\text{kin}}] \neq 0$，强耦合极限下 doublon 衰减被动力学压制（总占据随 $U$ 增大渐进受抑）。
  8. **电场下 doublon 密度振荡**：$U=0$ 时为无阻尼 Bloch 振荡；$U$ 增大后振荡被阻尼衰减——场与相互作用的联合作用通过耦合多粒子散射通道诱导 doublon 衰减。

  ## 潜在研究方向

  - 文中明确的方向：矢量势规范下严格的双时间 Green 函数处理未做（对湮灭时间取 0 是简化），含时谱函数的系统理论待建立。
  - 无穷温度 + 电场的阻尼率 $\gamma(U,E)$ 只有定性刻画（依赖 $U$、$E$ 敏感），定量标度律未给出。
  - 一维链结论向二维/三维、向扩展 Hubbard 模型（次近邻、长程相互作用）的推广未知。
  - 弱场区（$\omega_B$ 被衰减掩盖）的相干-非相干交叉边界未定量划定。
  - 实验接口未被讨论：冷原子量子模拟或超快泵浦-探测中如何观测无穷温度 doublon 谱（如光电子谱、动量分辨响应），是开放问题。
  - 实时动力学的时间窗受 MPS 纠缠增长限制，文中未报告可达的最大演化时间 $tJ$ 的系统性收敛测试。

  ## 与林赛研究的关联

  - **强场驱动 Mott 绝缘体**：本文是"电场 + 强关联"下 doublon 相干输运的基准理论，直接支撑我们关于光致 doublon–holon 产生、强场诱导 Mott 瞬态熔化课题的非平衡动力学叙事；其"Wannier–Stark 梯子 vs 2U 双带劈裂竞争"的谱学判据可作为 THz 驱动实验中分辨相干输运通道的理论参照。
  - **超快读出/输运方案**：doublon Bloch 振荡在无穷温度存活意味着热背景不必然封杀相干信号——这对我们 order-parameter 超快读出课题中"用热库中的载流子振荡做可观测信号"的设想是有力背书；可操作的频率标度 $\omega_B = E$、$\omega_U \approx U$、$v_d \propto J^2/U$ 可直接用于方案参数估算。
  - **HHG/阿秒接口**：强场下 doublon 的高能振荡（$\omega_U \approx U$ 量级）与外场调制（$\omega_B$）的混频结构（式(23)）提示 doublon 动力学会向 HHG 谱贡献非微扰边带——为"强关联体系 HHG 中 doublon 通道识别"提供可计算的目标谱。
  - **计算框架复用**：superfermionic 向量化 + Chebyshev 谱展开 + MPS 实时演化是标准库、零外部依赖即可复现的框架，可移植到我们莫尔/Hubbard 类模型的无穷温度谱函数计算，作为理论对照工具。
  - **交变磁/量子几何**：本文未涉及，但若莫尔 Hubbard 体系中交变磁序与 doublon 通道耦合，该框架可作为温度极限下的谱学基线。

  ## 来源
  - 蒸馏自全文（deep-read）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：无穷温度'热而相干'doublons 的谱函数计算框架（superfermion 向量化 + Chebyshev + MPS）

**原理**：无穷温度密度矩阵 ρ∝1 经对偶费米子算符（superfermionic）向量化为乘积态——期望值变为 enlarged Hilbert 空间内积，Chebyshev 多项式直接算频率空间谱函数（绕开显式时间演化与有限时间截断）；实时动力学经向量化 von Neumann 演化 + MPS/Trotter 两比特门；无穷温度初态在 system-auxiliary 二分上无纠缠 → 纠缠增长极小、MPS 开销低——研究 Hubbard 模型无穷温度下'热而相干'的 doublon 态。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 对易关系 | {c̃,c̃†}=δ_{x,x'}δ_{σ,σ'}（对偶费米子） | §原理 |

**适用边界**：页面提取限原理与参数表开头（模型参数数值被截断）；无穷温度设定（有限温推广未给）；向量化使 Hilbert 空间维数平方增长。
**代表作**：本文（arXiv:2509.20504）
*方法卡回补 2026-09-28*

<!-- linsai-wikilinks -->
## 关联概念

- [[强关联体系]]
- [[强场超快]]
- [[强场驱动]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
