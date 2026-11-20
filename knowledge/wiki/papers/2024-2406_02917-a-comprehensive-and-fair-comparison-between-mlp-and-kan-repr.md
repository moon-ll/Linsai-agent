---
title: "2024-2406_02917-a-comprehensive-and-fair-comparison-between-mlp-and-kan-repr"
type: "papers"
created: "2026-09-26T23:57:02Z"
updated: "2026-11-15T15:09:22Z"
tags: []
related: ["强场超快", "强场驱动", "量子几何", "量子几何反演"]
source_raw: "2024-2406.02917-a-comprehensive-and-fair-comparison-between-mlp-and-kan-repr.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # KAN 与 MLP 在微分方程与算子网络中的全面 FAIR 对比（Shukla 等, 2024）

  ## 林赛的理解

  这篇是 2024 年 4 月 KAN 提出以来第一批"打假式"系统基准评测，出自 Karniadakis 组——PINN 的嫡系。对我们的意义很直接：**它给"用 KAN 类架构做物理约束学习"这件事定了一个清醒的期望值**。原始 B 样条 KAN 既不准又慢（单迭代耗时可高两个数量级），低阶正交多项式变体（Chebyshev-KAN）才能与 PINN/DeepONet 打平，但鲁棒性差：换随机种子可能发散、阶数 >6 或层数 >5 损失变 NaN。所以如果在量子几何反演课题里引入 KAN 做算子学习或逆问题代理模型，**默认选项仍应是 MLP 基的 PINN/DeepONet，KAN 只作为可解释性增强的备选，且必须用 tanh 包裹层（equation 10）+ 双精度训练 + RBA 权重**这三件套稳住训练。文中关于 loss landscape 空洞随单精度浮点恶化、双精度下消失的结论，是所有高阶基函数网络在物理问题上的通用风险警示。另外它遵循 FAIR 原则发布了基准，可直接用作我们方法的消融对照。

  ## 研究问题

  核心问题：Kolmogorov-Arnold 网络（KAN）作为 MLP 的替代表示模型，在科学机器学习两大任务上是否真正更优、更鲁棒？

  1. **神经微分方程**（PINN/PIKAN 族）：求解特定 ODE/PDE 的正/逆问题时，KAN 表示与 MLP 表示（PINN）相比，精度、效率、稳定性如何？
  2. **神经算子**（DeepONet/DeepOKAN 族）：学习函数到函数的解算子时，KAN 表示是否优于 DeepONet？
  3. 为什么（不）：用 loss landscape 可视化与信息瓶颈（IB）理论解释两类表示模型的训练动力学差异。

  论文的中心论点（结论性）：原始 B 样条 KAN 表示**缺乏精度与效率**；低阶正交多项式（Chebyshev）KAN 可与 PINN/DeepONet 相当，但**仍缺乏鲁棒性**——在不同随机种子下可能发散，或在更高阶正交多项式下失效。

  ## 研究背景

  - **MLP 的地位与缺陷**：通用逼近定理保证 MLP 可逼近紧集上任意连续函数，是现代深度学习主 building block，但因深层嵌套结构缺乏可解释性，且面临过拟合、梯度消失/爆炸、可扩展性问题。
  - **KAN 的兴起**：Liu 等 2024 年 4 月提出 KAN（arXiv:2406.02917 的同期工作），受 Kolmogorov-Arnold 表示定理启发，可视为 Kolmogorov Networks 与"可学习激活函数 MLP"的结合，宣称更准确、更可解释，已缓解可解释性、灾难性遗忘等问题。但 B 样条激活带来显著计算开销，后续工作用 RBF、小波、Jacobi 多项式（Chebyshev、Legendre 为其特例）替代以降低开销。
  - **既有 KAN 求解 PDE 工作的局限**：Liu 等将 PINN+KAN 解 2D Poisson 方程；Abueida 等提出 RBF 基的 DeepOKAN 解 2D 正交各向异性弹性问题——均宣称 KAN 显著超越 MLP，但**限于浅层网络与简化问题**，缺乏公平、系统的对比。这正是本文动机：在同一基准上、结合最新优化技术（residual-based attention、eddy viscosity）做 FAIR（可复现）对比，并回答训练动力学差异的理论问题。

  ## 研究方法

  本文为计算基准研究，方法密度高，按方法卡整理如下。

  ### 方法卡 1：PIKAN / cPIKAN（物理约束 KAN 网络族）

  - **原理**：用 KAN 替代 MLP 作为物理信息损失网络的表示骨架。KAN 依 Kolmogorov-Arnold 定理将多元函数写成单变量函数有限复合加求和，边激活 ϕ 取 B 样条（vanilla PIKAN，参数 |θ| ~ O(n_l·H²·(k+g))）或 Chebyshev 正交多项式（cPIKAN，无需网格点，|θ| ~ O(n_l·H²·k)）。Chebyshev、Legendre 均为 Jacobi 多项式特例。
  - **关键参数表（数值+出处）**：
    - 不连续振荡函数逼近（Table 1，GeForce RTX-3090 24GB 计时）：KAN-I 37041 参数、多项式阶 k=3、rel l₂=0.29%、1586.15 ms/iter；KAN-II 4317 参数、k=3、0.32%、182.22 ms/iter；Chebyshev-KAN 4352 参数、k=3、7.43%（训练 2000 迭代后发散至 NaN）、2.34 ms/iter；Modified Chebyshev-KAN 4352 参数、k=3、0.79%、2.30 ms/iter；MLP 3401 参数、0.81%、1.30 ms/iter。
    - **稳定性修正**：每层 Chebyshev-KAN 后接 tanh（末层除外），前向传播 y=(Φ∘tanh∘Φ)(x)（equation 10），即"modified Chebyshev-KAN"。
    - Helmholtz 参数分析（Table 3a，a1=1, a2=4，51×51 配点，LBFGS 1800 迭代，w_bc=1, w_pde=0.01）：PINN 304 参数 1.03%；PIKAN 300 参数 0.735%（4550 ms/iter）；PIKAN multigrid（k=3, g=5 起，每 600 迭代网格点翻倍，三阶段）240–690 参数 0.476%；cPIKAN 350 参数 0.530%（183 ms/iter）；PINN+RBA 0.354%；cPIKAN+RBA 0.376%。RBA 初始化 α=1，更新学习率 η*=1e-4（equation 3）。
    - Helmholtz 时间匹配分析（Table 3b，4 隐层，100×100 配点，Adam 2.0e5 迭代，lr 1e-3→1e-4，无偏损失 w_bc=w_pde=1，RBA 仅用于 PDE 残差、α 初始化为 0、η*=1e-3）：PINN（100 神经元/层，30300 参数）0.530%；cPIKAN（32 神经元/层，15840 参数）0.500%；PINN+RBA 0.206%；cPIKAN+RBA **0.160%**（最佳）。
    - Helmholtz 高波数复杂度分析（Table 3c，a1=a2=6，PINN 6 隐层×128 神经元=82304 参数，cPIKAN 5 层×32 神经元 k=5=20960 参数，Adam 5e5 迭代，lr 1e-3→5e-5）：PINN 4.30%，PINN+RBA 1.72%，**cPIKAN+RBA 0.381%（显著最佳）**；vanilla cPIKAN 不收敛（初始迭代后损失 NaN）。
  - **适用边界**：vanilla PIKAN 单迭代 1586.15 ms（KAN-I）相对 MLP 的 1.30 ms 高约三个数量级，不能受益于 GPU 并行化；**k>6 或 n_l>5 时损失函数在若干迭代后变 undefined**；cPIKAN 诱导更多振荡且可能失稳；单精度（float32）下 loss landscape 出现"空洞"（loss 未定义区域）且随 k 增大扩张，双精度（float64）下消失但计算成本上升；HcKAN 与 HNN 同架构同参数量时训练不稳定快速发散，减参数不缓解，须用 equation 10 修正 + 更浅网络才稳定。
  - **代表作**：Liu et al. 2024（原始 KAN）；本文 Shukla et al. 2024（FAIR 对比基准）。

  ### 方法卡 2：Residual-Based Attention（RBA，残差注意力权重）

  - **原理**：对物理信息损失逐点加权，解决累计损失掩盖局部大残差的问题。权重取残差的指数加权移动平均（EWMA），充当注意力掩码引导优化器聚焦高误差区域，实现 residual homogeneity。更新规则：α_i^{k+1} ← (1−η*)α_i^k + η*·|e_i|/‖e‖∞，α∈[0,1]，为收敛的线性齐次递推。
  - **关键参数表**：
    - Helmholtz 参数分析：α 初始化 1，η*=1e-4。
    - Helmholtz 时间/复杂度分析：α 初始化 0，η*=1e-3，仅施加于 PDE 残差项。
  - **适用边界**：作为局部乘子依赖残差统计，仅在损失项内平衡贡献，不改变全局损失结构（全局权重另设 w_bc/w_pde）；其收益与底层表示（MLP/KAN）正交互补。
  - **代表作**：Anagnostopoulos et al.（RBA + PINN 训练三阶段"total diffusion"提出者）；本文将其同时用于 PINN 与 cPIKAN 的公平叠加。

  ### 方法卡 3：IB 理论训练动力学分析

  - **原理**：信息瓶颈理论认为良好模型应保留输出必需信息、丢弃无关输入细节，训练分两阶段（"fitting"→"diffusion"）；Anagnostopoulos 等扩展至 PINN 提出第三阶段"total diffusion"。本文对 PIKAN 做同类分析，识别与 PINN 相同的三阶段学习，弥合两类表示模型的动力学描述。
  - **适用边界**：属解释性框架，非优化加速手段；本文仅用于对齐两类表示的训练行为。

  **实验设置（通用）**：硬件 GeForce RTX-3090 24GB；优化器 Adam（静态 lr 或 1e-3→1e-4/1e-3→5e-5 调度）与二阶 LBFGS；函数逼近训练 KAN 至 20,000/25,000 迭代、Chebyshev-KAN/MLP 至 100,000 迭代；HNN/HcKAN 用 Adam lr=1e-3（Table 2：HNN 4417 参数 1.53 ms/iter；HcKAN 920 参数 k=3 2.97 ms/iter，GPU 利用率 <10% 时 HcKAN 每迭代反而更慢）。基准共 8 项：不连续函数逼近、Hamiltonian 结构保持动力学、Helmholtz PDE、Navier–Stokes（含 ν 小时按 [68] 引入 ν_E 涡黏损失重构，equations 22–24）、不确定性量化（Bayesian 框架下含噪 PDE 数据）、低/高维算子回归（DeepONet vs DeepOKAN 两个任务）。

  ## 主要发现与核心结论

  1. **原始 B 样条 KAN 全面不占优**：精度无优势（函数逼近 0.29%/0.32% vs modified Chebyshev-KAN 0.79% 在相近或更多参数下）、效率极差（KAN-I 1586.15 ms/iter vs MLP 1.30 ms/iter），且不能受益于 GPU 并行化。
  2. **低阶正交多项式 KAN 与 MLP 基模型相当**：modified Chebyshev-KAN 逼近误差 0.79% 与 MLP 的 0.81% 相当；cPIKAN 在各 Helmholtz 设定下与对应 PINN 相当或略优。
  3. **RBA 是稳定的增益源，与表示无关**：Helmholtz 高波数下 PINN+RBA 从 4.30% 降至 1.72%，cPIKAN+RBA 达 0.381%（全场最佳）；时间匹配分析中 cPIKAN+RBA 达 0.160%（最佳）。
  4. **鲁棒性是核心短板**：Chebyshev-KAN 原始版逼近不连续函数时 2000 迭代后损失 NaN（l₂ 误差 7.43%，傅里叶谱显示未学到高频）；HcKAN 与 HNN 同架构发散；**k>6 或层数 >5 时 cPIKAN 损失 undefined**；换随机种子可能发散；vanilla cPIKAN 在高波数 Helmholtz 下初始迭代后损失 NaN。结论原话：低阶正交多项式版本"comparable performance to PINNs and DeepONet although they still lack robustness"。
  5. **失稳机理**：单精度 float32 下 loss landscape 出现 loss 未定义"空洞"并随阶数扩张，模型对初始化敏感；float64 下空洞消失，说明失稳源于单精度数值逼近局限，可用双精度训练规避但成本上升。
  6. **参数效率悖论**：KAN-II 以比 KAN-I 少一个数量级的参数（4317 vs 37041）达到几乎相同精度（0.32% vs 0.29%）；cPIKAN 参数量公式 O(n_l·H²·k) 不含网格 g，显著小于 PIKAN 的 O(n_l·H²·(k+g))；但小参数 KAN 在小批量下 GPU 利用率 <10%，每迭代反而比大参数 MLP 慢（HcKAN 2.97 vs HNN 1.53 ms/iter）。
  7. **外推能力**：理想弹簧 Hamiltonian 系统中，HNN（40 训练样本）外推好，HcKAN（[N_train, N_test]=[40,100]）外推较弱、泛化误差更大，测试损失停滞高位；增加训练样本至 50/60 时测试损失下降数个数量级——HcKAN 样本效率低于 HNN。
  8. **训练动力学**：IB 分析识别出 PIKAN 与 PINN 相同的三阶段学习（fitting、diffusion、total diffusion），两类表示在动力学层面可统一描述。
  9. （摘要级，全文截断未含细节数值）DeepOKAN 与 DeepONet 在两个算子学习任务上对比，及 Bayesian 框架下含噪数据的 UQ 结果；作者在摘要中总评低阶正交多项式 KAN 与 PINN/DeepONet 性能相当但不鲁棒。

  ## 潜在研究方向

  - **鲁棒性修复**：随机种子敏感性与高阶发散（k>6、层数 >5 损失 undefined）未解决；双精度训练可行但成本未量化对比，低成本替代（混合精度、谱归一化、稳定性正则）开放。
  - **GPU 利用率**：vanilla PIKAN 4550 ms/iter（Table 3a），KAN 边激活的并行实现是可工程化改进点。
  - **HcKAN 样本效率**：比 HNN 需更多训练样本才能达到相近外推，数据效率差距的来源未解释。
  - **高维与真实问题**：DeepOKAN 仅在两个算子任务上验证；含噪真实实验数据（本文仅 Bayesian UQ 初探）下的表现待系统检验。
  - **KAN 可解释性收益未量化**：本文聚焦精度/效率/鲁棒性，KAN 宣称的可解释性优势在 PDE 求解场景未被检验。
  - 其余遗留问题：多层 multigrid PIKAN 末阶段参数量为其他模型两倍带来的公平性争议；RBA 在高波数下对 KAN 增益（4.30%→0.381% 相对 PINN+RBA 的 1.72%）背后的机理值得深挖。

  ## 与林赛研究的关联

  - **量子几何反演课题（general-quantum-geometry-inversion）的直接接口**：我们的逆问题用物理约束学习反演 HHG/超快信号中的量子几何量，默认骨架是 MLP 基 PINN/DeepONet。本文给出明确操作结论——**维持 MLP 默认，KAN 仅在需要可解释激活函数解释时引入，且必须 equation 10（层后 tanh）+ RBA + 双精度三件套**；RBA（η* 1e-4~1e-3，初始化 1 或 0）是零成本增益，可直接并入我们的优化管线。Table 3 的三档对照（参数匹配/时间匹配/复杂度递增）就是我们写消融实验的模板。
  - **强场驱动 / HHG 数据特点**：HHG 谱含高频振荡与不连续特征（对应本文 equation 9 的 spectral bias 测试），Chebyshev-KAN 恰恰在高频学习上失败（7.43%、谱缺失高频），提示 KAN 处理强场谱这类高频信号风险高——这是我们课题选型的重要负证据。
  - **阿秒 / 超快动力学算子学习**：若构建"驱动波形→阿秒动力学"的神经算子代理，DeepONet 基线应先立，DeepOKAN 仅作对照；算子任务上本文显示两者相当。
  - **方法论资产**：loss landscape + IB 三阶段分析（fitting/diffusion/total diffusion）可直接迁移为我们训练 PINN 逆问题模型时的收敛诊断工具，判断模型处于过拟合扩散阶段以决定早停。
  - **方向词锚点**：属于"量子几何 inversion 课题"的方法学储备，不直接涉及莫尔/交变磁，但 RBA 与训练诊断对全部强场超快机器学习子任务通用。

  ## 来源

  - 蒸馏自全文（deep-read）（注：获取的全文在 §3.4 Navier–Stokes 中间截断，其后 UQ、DeepOKAN 算子任务与 IB 分析细节未含数值，相应结论按摘要级标注）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：PIKAN/cPIKAN 与 MLP 的物理约束网络公平基准（Chebyshev-KAN + tanh 稳定修正 + RBA）

**原理**：用 KAN 替代 MLP 作物理信息网络骨架：vanilla PIKAN（B 样条边激活）与 cPIKAN（Chebyshev 正交多项式，免网格点，参数量 O(n_l·H²·k)）；关键稳定性修正——每层 Chebyshev-KAN 后接 tanh（末层除外），y=(Φ∘tanh∘Φ)(x)，得 modified Chebyshev-KAN，消除训练发散/NaN；配 Residual-Based Attention（RBA）残差注意力加权（α 初始化 1 或 0，更新学习率 η*）与 PIKAN multigrid（k=3/g=5 起、每 600 迭代网格翻倍三阶段）；在不连续振荡函数逼近、Helmholtz 参数/时间/高波数四类基准上以同精度-同参数量-同时间三维公平对比。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 函数逼近（Table 1） | KAN-I 37041 参数 rel l₂=0.29% 1586.15 ms/iter；Chebyshev-KAN 4352 参数 7.43%（发散）2.34 ms/iter；Modified Chebyshev-KAN 0.79% 2.30 ms/iter；MLP 3401 参数 0.81% 1.30 ms/iter（RTX-3090） | Table 1 |
| Helmholtz 高波数（Table 3c） | a1=a2=6：PINN（82304 参数）4.30%；PINN+RBA 1.72%；cPIKAN+RBA（20960 参数，5 层×32，k=5）0.381% 显著最佳；vanilla cPIKAN 不收敛（NaN） | Table 3c |
| 时间匹配（Table 3b） | PINN+RBA 0.206%；cPIKAN+RBA 0.160%（最佳；15840 参数，Adam 2.0e5 迭代） | Table 3b |

**适用边界**：vanilla PIKAN 单迭代 ~1586 ms 较 MLP 慢约三个量级且难 GPU 并行；k>6 或 n_l>5 时损失变 undefined；float32 下 loss landscape 出现空洞（双精度消失但成本升）；HcKAN/HNN 同架构同参数量训练不稳定，须 equation 10 修正 + 浅网络。
**代表作**：Shukla et al. 2024（本文基准）；原始 KAN：Liu et al. 2024
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[强场超快]]
- [[强场驱动]]
- [[量子几何]]
- [[量子几何反演]]
<!-- /linsai-wikilinks -->
