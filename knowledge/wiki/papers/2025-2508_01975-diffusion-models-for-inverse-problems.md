---
title: "2025-2508_01975-diffusion-models-for-inverse-problems"
type: "papers"
created: "2026-09-25T18:36:26Z"
updated: "2026-11-16T05:30:14Z"
tags: []
related: ["2025-2508_01975-fourier-neural-operators-for-fast-simulation-and-inverse-des", "2508.01975", "arpes", "key-transient-quantum-phase-optical-20260726", "强场超快", "强场超快光学", "强场驱动", "泵浦探测", "瞬态量子相位", "莫尔超晶格", "量子几何"]
source_raw: "2025-2508.01975-diffusion-models-for-inverse-problems.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
updated_at: "2026-09-27T01:00:51Z"
merged_from: ["wiki/papers/2025-2508_01975-fourier-neural-operators-for-fast-simulation-and-inverse-des.md"]
---

• # Diffusion Models for Inverse Problems：以扩散模型为先验求解成像逆问题的方法谱系综述

  ## 林赛的理解

  这是一篇站在方法学制高点上的系统性综述，把过去几年"用扩散模型解逆问题"这条线的数学骨架彻底理清了。对我个人而言，这篇工作的价值不在于某个具体算法，而在于它揭示了一个普适结构：**所有逆问题求解器本质都是在逼近后验 score $\nabla_{x_t}\log p(y|x_t)$**，而这一项是不可解的，各家方法的分野只在于"用什么近似、在哪个空间近似、付出多少计算代价"。这个视角直接可移植到强场超快领域——我们的阿秒反演、光电子谱重建、莫尔体系散射信号解卷积，本质上都是病态逆问题 $y=A(x)+n$，而 HHG 光谱与高次谐波图像天然具有强先验结构（已训练好的数据分布），扩散先验正是把"物理直觉先验"换成"数据学习先验"的标准化工具。文中 DPS 家族、SMC 粒子滤波、解耦数据一致性三条路线，恰好对应我们在实验反演中关心的三种需求：快速单次重建、不确定度量化、多解共存（比如交变磁多个可能序参量构型）。

  ## 研究问题

  论文的核心问题是：**如何利用扩散模型学到的数据先验 $p(x)$，对成像逆问题 $y=A(x)+n$ 进行后验采样 $x\sim p(x|y)$，并且如何系统分类、对比和评估现有的各类求解器（Diffusion model based Inverse problem Solvers, DIS）**。具体分解为三个子目标（原文明确列出）：(i) 提炼连接这些算法的共同数学主线；(ii) 在代表性逆问题上系统对比各方法的假设与性能权衡；(iii) 通过澄清 DIS 方法版图，指出开放的理论与实践挑战。

  论文关注的三种典型求解目标：后验采样（posterior sampling，$x\sim p(x|y)$）、MMSE 估计（$\hat{x}=\mathbb{E}[x|y]$）、MAP 估计（$\hat{x}=\arg\max_x p(x|y)$），并强调 Blau & Michaeli (2018) 指出的**感知-失真权衡**——感知质量与失真不能同时最优（尽管 Jalal et al. 2021 证明后验采样在失真意义上近乎最优）。

  ## 研究背景

  逆问题 $y=A(x)+n$（$A:\mathbb{R}^n\to\mathbb{R}^m$，$m<n$）因欠定性存在无穷多可行解，Bayes 公式 $p(x|y)=p(x)p(y|x)/p(y)$ 将求解归结为指定先验。传统正则化方法依赖人工设计的先验，而 Bora et al. (2017) 开创的生成先验（generative prior）思路用深度生成模型从数据中学习先验。扩散模型（Ho et al. 2020; Song et al. 2021）已成为图像/视频分布建模的主流范式（flow matching、rectified flow 等变体在原理上等价，Gao et al. 2024 证明了参考分布为高斯时二者等价），其核心是学习一族模糊化的 score 函数 $\nabla_{x_t}\log p(x_t)$，通过反向 SDE 或概率流 ODE（PF-ODE）采样。

  逆问题求解的关键在于后验 score 分解：
  $$\nabla_{x_t}\log p(x_t|y)=\nabla_{x_t}\log p(x_t)+\nabla_{x_t}\log p(y|x_t)$$
  其中 $\nabla_{x_t}\log p(y|x_t)$ **不可解**——这是整个领域的中心难点，也是所有方法分类的轴心。早期工作（Song & Ermon 2019; Kadkhodaie & Simoncelli 2021）以退火-去噪与数据一致性投影交替的形式隐式处理；本文与 Daras et al. (2024) 的综述共享部分版式，但推进了时间线至 2025 年中，并新增方法类别（如高维数据扩展）与盲逆问题、文本多模态控制等新挑战的覆盖。

  ## 研究方法

  **理论框架**：全文以 score 视角（SDE/ODE、Tweedie 定理：$\mathbb{E}[x_0|x_t]=\frac{1}{s_t}(x_t+\sigma_t^2\nabla_{x_t}\log p(x_t))$）与变分视角（DDPM 的 ELBO 推导、VE/VP 两种噪声日程、DDIM 以参数 $\eta\in[0,1]$ 插值随机性，$\eta=0$ 等价于 VP 的 PF-ODE）双线并行，证明两框架殊途同归。

  **方法分类**（论文的核心组织贡献）：
  - **显式近似法**：对 $p(y|x_t)$ 做显式逼近。Score-ALD（Jalal et al. 2021，$\nabla_{x_t}\log p(y|x_t)\approx-\frac{A^\top(y-Ax_t)}{\sigma_y^2+\gamma_t^2}$，用于压缩感知 MRI）；Score-SDE（正交 $A$ 的噪声投影）；SNIPS 与 DDRM 家族（基于 SVD $A=U\Sigma V^\top$，在谱空间逐奇异值分量按 $\sigma_t$ 与 $\sigma_y$ 大小关系切换处理分支）；DPS 家族（Jensen 近似 $p(y|x_t)\approx p(y|\hat{x}_{0|t})$，全通用、可解非线性问题），及其改进谱系——ΠGDM（各向同性高斯近似，协方差 $r_t^2 I$）、Moment Matching（协方差 $\mathrm{Var}[x_0|x_t]=\sigma_t^2\nabla_{x_t}\hat{x}_{0|t}$，用 JVP 高效计算）、Peng et al. 2024（DDPM 框架下最优对角后验协方差，最大似然估计、免 JVP、全场景提升鲁棒性）、DDS（利用流形约束梯度 MCG，在仿射子空间流形假设下 $\frac{\partial\hat{x}_{0|t}}{\partial x_t}=\frac{1}{\sqrt{\bar{\alpha}_t}}P_{\mathcal{M}}$，单次 NFE 后接共轭梯度/Krylov 子空间多次投影，大幅提速降存）、MPGD/DSG/DMAP/DPPS 等梯度投影与多步改进；以及向 flow 模型的扩展（FlowChef 引入通用 guidance 项 $\nabla_{\hat{x}_{0|t}}\ell$；FlowDPS 借广义 Tweedie 公式将后验采样理论推广到一般仿射流）。
  - **变分推断**：最小化 $\mathrm{KL}(q_\phi(x_0|y)\|p(x_0|y))$，分解为数据一致性项 + 先验正则项 + 常数。RED-Diff（各向同性高斯变分族，第二项化为 score-distillation 损失，等价于 regularization by denoising；FLAIR 将其推广至 flow 模型，用 Tweedie 公式构造确定+随机混合噪声保证中间态处于高似然区）；Feng et al. 2023（RealNVP 正态化流表示多峰后验，免调步长超参）；APS（条件化 RealNVP 摊销，单网络服务所有 $y$）；RSLD（粒子变分推断 + 排斥正则 $\sum_j\log[k(x_t^{(i)},x_t^{(j)})^r]$，经 Wasserstein 梯度流推导，$n$ 个粒子联合更新）；DA VI（一步采样，但面临 $q_\phi$ 与 $p(x_0)$ 支撑集不重叠导致的训练不稳，改用隐式 score $s_\psi$ 交替优化）。
  - **解耦数据一致性**：DAPS（先沿 PF-ODE 采样 $\tilde{x}_{0|t}^{(j)}\sim p(x_0|x_t)$，再跑 $N$ 步 Langevin 动力学施加数据一致性，$p(x_0|x_t,y)\propto p(x_0|x_t)p(y|x_0)$，对 Fourier 相位恢复等难题显著改善）；DCDP（用近端优化步替代 Langevin）；SITCOM（定义前向/后向/测量三重一致性，优化扩散模型输入 $x_t'=\arg\min\|A(D_\theta(x_t))-y\|_2^2$ 加近端约束）。
  - **序贯蒙特卡洛（SMC）**：粒子滤波框架，粒子数 $\to\infty$ 时逼近真实后验采样。SMCDiff（motif 支架生成，噪声补全特例）；MCGDiff（提议核 $p_\theta^y(x_t|x_{t+1})\propto p_\theta(x_t|x_{t+1})q(x_t|y)$）；FPS（构造耦合扩散过程 $y_t=a_ty_{t-1}+b_tA\epsilon_t$，使 $y_t\sim\mathcal{N}(Ax_t,c_t^2\sigma_y^2 I)$，$c_t=a_1a_2\cdots a_t$，得闭式 $p_\theta(y_{t-1}|x_{t-1})=\mathcal{N}(Ax_{t-1},c_{t-1}^2\sigma_y^2 I)$ 作为提议核）；并与推理时 scaling 建立联系（Singhal et al. 2025 的 FK-steering，粒子数成为可扩展计算轴；Park et al. 2025 扩展至视频扩散的 3D/4D 物理一致性奖励）。
  - **盲逆问题**：前向算子含未知参数 $\phi$（如盲解卷积 $y=k*x+n$），需联合后验 $p(x,k|y)\propto p(x)p(k)p(y|x,k)$。BlindDPS（双并行 PF-ODE 耦合采样 $x$ 与 $\phi$，共享似然梯度）；GibbsDDRM（SVD 依赖 $\phi$ 时用 Langevin 更新 $\phi\leftarrow\phi+\frac{\xi}{2}\nabla_\phi\log p(\phi|x_{t:T},y)+\sqrt{\xi}\epsilon$，Laplace 先验 $-\lambda\|\phi\|_1$，避免训练第二个 score 网络）。

  ## 主要发现与核心结论

  1. **统一数学主线**：所有 DIS 都在以不同方式处理不可解项 $\nabla_{x_t}\log p(y|x_t)$——显式近似法直接逼近它，变分法绕开它转而在分布空间匹配，SMC 用粒子加权逐步逼近真实后验，解耦法把数据一致性与无条件采样分离。Tweedie 定理（$\mathbb{E}[x_0|x_t]=\frac{1}{s_t}(x_t+\sigma_t^2\nabla_{x_t}\log p(x_t))$）是所有方法共享的支点：扩散网络既是 score 估计器也是后验均值估计器。

  2. **各类别的定量与定性权衡**：显式近似法（DPS 家族）实现简单、对非线性前向模型完全通用，但单次点近似导致多样性不足且计算重（需反向传播穿过 score 网络）；变分推断在分布匹配上更优、多样性好，但每换一个观测 $y$ 就要重新优化（APS 摊销缓解）；SMC 有粒子数 $\to\infty$ 收敛到真实后验的渐近保证，是唯一能严格宣称后验采样的框架，且粒子数构成推理时 scaling 的新轴（FK-steering）；解耦法（DAPS/DCDP）在 Fourier 相位恢复等极端病态问题上显著更稳，代价是更多计算。

  3. **盲问题的可行路径**：BlindDPS 证明双扩散先验 + 耦合似然梯度可联合恢复信号与算子参数；GibbsDDRM 证明在 SVD 参数化框架内用 Langevin 交替更新 $\phi$（步长 $\xi$、Laplace 先验 $-\lambda\|\phi\|_1$）可省去训练第二个 score 网络的成本。

  4. **开放挑战**（综述明确点出的方向）：高维数据扩展、数据稀缺与分布失配下的稳健性、多模态（文本）控制、以及 flow matching/rectified flow 变体下的统一理论（Gao et al. 2024 仅在高斯参考分布下证明等价）。

  ## 潜在研究方向

  - **理论缺口**：DPS 的点近似（Jensen 近似）误差界仅在 Gaussian 测量下可控；非高斯噪声、非线性 $A$ 下的逼近质量缺乏系统理论。DMAP（Xu et al. 2025）指出 DPS 实际行为更接近 MAP 而非后验采样，说明"我们以为在做后验采样、实际在做点估计"的错位普遍存在。
  - **计算成本**：DPS 家族的 $\nabla_{x_t}\hat{x}_{0|t}$ 反向传播在大尺度问题上昂贵；DDS 的流形假设（仿射子空间 + Krylov 子空间）是否对真实数据流形成立、在非图像数据（光谱、谱图）上如何验证，尚无答案。
  - **分布失配与数据稀缺**：训练分布与真实测量分布不一致时性能退化缺乏量化刻画；小数据体系的扩散先验训练本身仍是难题。
  - **多解性与不确定度量化**：变分和 SMC 方法虽能给出多峰后验，但粒子坍缩、repulsive 正则的强度选择（RSLD 中 $r$ 指数）、变分族表达力不足（各向同性高斯 vs 真实多峰后验）都是实践痛点。
  - **向其他领域的迁移**：综述全部以成像为战场；对非图像信号（谱学、时间序列反演）的适配——噪声日程、score 网络架构、数据一致性投影的形式——基本空白，是明显的扩展机会。

  ## 与林赛研究的关联

  这篇综述给我们组提供了直接的方法学武器库，接口非常具体：

  - **HHG/阿秒光谱反演**：高次谐波谱 $\to$ 发射时间结构（如 streaking 或 spectrogram 反演 attosecond 脉冲串）是典型病态逆问题。DPS 框架只需可微前向模型（我们的强场近似传播子完全可微），即可在单次网络前向的成本下做重建；若需评估脉冲重建的不确定度（多解可能对应不同的电子轨道贡献权重），SMC/RSLD 粒子框架是现成方案。
  - **强场驱动 + 交变磁**：太赫兹泵浦后磁化动力学的时间分辨衍射/谱学重建，前向算子含未知参数（磁结构因子、阻尼系数），正是盲逆问题（5.1 节）的设置——BlindDPS 的双流耦合 PF-ODE 思路可直接映射到"信号=磁化分布、参数=动力学系数"的联合重建。
  - **莫尔体系**：莫尔超晶格的 STEM/ARPES 图像去噪与超分辨重建属于线性逆问题，DDRM 的 SVD 谱空间分解路线（按 $\sigma_t$ 与 $\sigma_y$ 关系分三分支处理）天然适配傅平面测量；量子几何相关的动量分辨信号重建可从分布匹配的多样性中获益。
  - **实验设计闭环**：综述强调"先验指定决定恢复类型"（后验采样 vs MMSE vs MAP 的感知-失真权衡），这与我们设计探测方案时的可分辨性分析直接相关——选择哪种重建目标应服务于具体的物理量提取，而非默认 MMSE。
  - **执行建议**：短期可在组内已有的可微 HHG 模拟器上复现 DPS（~数百行代码）；中期对交变磁动力学反演试点 BlindDPS；若遇多解严重的体系（莫尔平带关联态多个候选序参量），切换到 DAPS 或 SMC 路线。

  ## 来源
  - 蒸馏自全文（deep-read）


## 合并自「2025-2508_01975-fourier-neural-operators-for-fast-simulation-and-inverse-des」

• # Diffusion Models for Inverse Problems：从后验采样到盲问题与文本调控的系统综述

  ## 林赛的理解

  我先把话说清楚：这篇是全文的系统综述，标题与元数据里登记的"TFLN 波导二次谐波 FNO"完全对不上——正文是 Chung、Kim、Ye 三人（KAIST / EverEx）关于**扩散模型求解逆问题**的综述章节（arXiv:2508.01975，2025 年 8 月 4 日），登记元数据需要回头修正，否则 KB 检索会被误导。但这篇综述对我们的价值是真实且不小的：它把"扩散先验 + 测量一致性"这一整套数学工具——显式似然近似（DPS 家族）、变分推断（RED-Diff/APS/RSLD）、解耦数据一致性（DAPS/DCDP）、序贯蒙特卡洛（SMCDiff/FPS）——用统一的 score 视角串了起来。对我们做**强场超快光学**的人，逆问题是日常：从 HHG 光谱或光电子能谱反演分子动力学、从衍射图样反演结构、从泵浦探测信号反演瞬态量子相位。这篇给了一个"逆问题求解器选型的决策地图"：什么时候该用 DPS 类（快但近似）、什么时候必须上 SMC（慢但有收敛保证）、后验采样的多样性与 MMSE 失真之间的 trade-off 如何取舍（Blau & Michaeli 的 perception-distortion trade-off）。这比任何单篇 DIS 论文都更值得蒸馏，因为它回答的是"我该用哪个工具"而非"某个工具多好用"。

  ## 研究问题

  论文要回答的核心问题是：**如何利用扩散模型学到的生成先验，为病态逆问题 y = A(x) + n（m < n）构造高质量的后验求解器？** 具体分解为三个子目标（作者明确列出）：

  1. **提炼数学主线**：串起各类 Diffusion-based Inverse problem Solvers（DIS）的共同数学骨架——都围绕 score 分解 ∇_{xt} log p(xt|y) = ∇_{xt} log p(xt) + ∇_{xt} log p(y|xt)，难点全在如何处理不可解析的后验似然项 p(y|xt)；
  2. **系统对比假设与权衡**：把方法分为显式近似、变分推断、序贯蒙特卡洛、解耦数据一致性四大类，对比其假设、适用场景（线性/非线性、噪声水平、维度）与感知质量/失真/算力的 trade-off；
  3. **标定开放挑战**：梳理盲逆问题、高维数据、数据稀缺与分布失配、文本多模态调控等延伸方向的现状与未解问题。

  ## 研究背景

  学术脉络清晰：逆问题的贝叶斯形式（Tarantola 2005）早就给出 p(x|y) ∝ p(x)p(y|x)，关键一直是**先验 p(x) 的构造**。传统路线用稀疏性等解析先验，Bora et al. (2017) 开创用深度生成模型定义先验的 CSGM 路线。扩散模型（Ho et al. 2020；Song et al. 2021）凭借 score 学习 ∇_x log p(x) 绕过归一化常数，成为图像/视频先验的范式。由此，"扩散先验 + 数据一致性"的逆问题求解在 2021–2025 间爆发：Score-ALD、Score-SDE、SNIPS/DDRM（SVD 显式线性代数路线）、DPS（Jensen 近似路线）、RED-Diff（变分路线）、SMCDiff/SMC 粒子路线等。作者自陈本综述基于 Daras et al. (2024) 的 taxonomy 布局，但扩展了新类别（如解耦数据一致性）、把时间线推到 2025 年中、并覆盖高维数据等延伸。方法论基础是两套等价框架：score/SDE 视角（反向 SDE 与 probability-flow ODE，Tweedie 定理 E[x0|xt] = (1/s_t)(xt + σ²_t ∇ log p(xt))）与变分/DDPM 视角（ELBO → ε-matching，两者仅差常数与参数化）。Blau & Michaeli (2018) 的 perception-distortion trade-off 指出后验采样（高感知质量）与 MMSE（低失真）不可兼得，但 Jalal et al. (2021) 表明后验采样在失真意义下近乎最优——这构成了整个领域的目标函数之争。

  ## 研究方法

  这是综述，方法学在于其分类体系与各方法的技术要点：

  - **显式近似类（Sec. 3）**：核心是对 p(y|xt) 做可计算近似。Score-ALD 用 ∇ log p(y|xt) ≈ −Aᵀ(y − Axt)/(σ²_y + γ²_t)（压缩感知 MRI）；Score-SDE 针对正交 A 做含噪投影；DDRM 家族用 SVD A = UΣVᵀ 在奇异值空间做分段高斯替换（σ_t < σ_y/s_i 与 σ_t ≥ σ_y/s_i 两种情形）；**DPS** 用 Jensen 近似 p(y|xt) ≈ p(y|x̂_{0|t})（x̂_{0|t} 为单次前向的 MMSE 估计），完全支持**非线性、任意前向模型**，实际用经验步长 ρ 替代 1/(2σ²_y)，需反传穿过 score 网络。改进线：ΠGDM（各向同性高斯近似，r²_t 超参）、Moment Matching（Var[x0|xt] = σ²_t ∇x̂_{0|t}，用 JVP 省内存）、DDS（利用流形约束梯度 MCG，单次 NFE 后接共轭梯度多步投影）、DSG/MPGD/DMAP/DPPS 等。
  - **变分推断类（Sec. 4.1）**：拟合 q_φ(x0|y) 逼近后验，KL 分解为数据一致性 + 对 p(x0) 的正则 + 常数。RED-Diff 取各向同性高斯 q，得分蒸馏损失形式，t 从 T→0 采样（先粗语义后细节）；Feng et al. 用 RealNVP 正规化流表示多模态后验、免调超参但训练开销大；APS 摊销化（单网络处理所有 y）；RSLD 用粒子变分 + 排斥正则（Wasserstein 梯度流视角）显式获得多样后验样本；DA VI 训练单步采样网络但遭遇支撑集不重叠导致的训练不稳。
  - **解耦数据一致性类（Sec. 4.2）**：**DAPS** 先跑 PF-ODE 采样 x̃_{0|t} ~ p(x0|xt)，再跑 N 步 Langevin 动力学施加 p(y|x0)，分解 p(x0|xt, y) ∝ p(x0|xt)p(y|x0)，在 Fourier 相位恢复等硬问题上显著更稳（代价是更多算力）；DCDP 用近端优化步；SITCOM 同时优化前向/反向/测量三重一致性。
  - **序贯蒙特卡洛类（Sec. 4.3）**：粒子滤波，粒子数 → ∞ 时收敛到真实后验。SMCDiff 处理噪声缺失补（motif scaffolding）；MCGDiff 用 q(xt|y) 构造提议核；FPS 构造**耦合扩散过程**（同时对测量 y 做相关前向扩散，得闭式 p_θ(yt−1|xt−1) = N(Axt−1, c²_{t−1}σ²_y I)）；并指出 SMC 天然提供"粒子数"这条 inference-time scaling 轴（Singhal et al. 2025），FK-steering 已扩展到视频扩散的 3D/4D 物理一致性奖励（Park et al. 2025）。
  - **盲问题扩展（Sec. 5.1）**：前向算子带参 A_φ，需联合后验 p(x, k|y) ∝ p(x)p(k)p(y|x, k)（以盲去卷积 y = k ∗ x + n 为例）。BlindDPS 训练第二个扩散模型做核先验，两条耦合 PF-ODE 并行采样；GibbsDDRM 在 DDRM 框架内用 Langevin 步 + Laplacian 先验（−λ∥φ∥₁）交替更新 φ，避免训练额外 score 网络。

  ## 主要发现与核心结论

  1. **统一骨架**：所有 DIS 的差异可归结为如何处理 ∇_{xt} log p(y|xt)——显式近似（DPS 家族：p(y|xt) ≈ p(y|x̂_{0|t})，误差在高斯测量下可控）、变分（分布匹配，多样性优于 DPS 的单点 MMSE 近似）、SMC（粒子数 → ∞ 时渐近收敛真后验，给出 inference-time scaling 保证）。
  2. **DPS 的普适性与代价**：DPS 因 Jensen 近似成为唯一能直接处理**非线性任意前向模型**的方法，但 ∇_{xt} x̂_{0|t} 的反传使其慢且内存开销大；DDS 证明在流形约束下可用 MCG（单次 NFE + 共轭梯度）绕过，大幅提速。
  3. **DAPS 的解耦策略**：将无条件采样与数据一致性解耦（p(x0|xt, y) ∝ p(x0|xt)p(y|x0)），用 PF-ODE 采样 + N 步 Langevin 施加测量约束，在 Fourier 相位恢复等此前发散的硬问题上取得改进。
  4. **DDRM 的 SVD 显式分段公式**：在奇异值空间按 σ_t 与 σ_y/s_i 的关系做三种分段高斯替换（s_i = 0 / σ_t < σ_y/s_i / σ_t ≥ σ_y/s_i），配合混合系数 η ∈ (0, 1]，是纯线性问题的闭式高效解。
  5. **目标函数三分法**：后验采样 x ~ p(x|y)、MMSE x = E[x|y]、MAP x = arg max p(x|y) 不可同时最优——perception 与 distortion 存在 trade-off（Blau & Michaeli 2018），但后验采样失真近优（Jalal et al. 2021）。
  6. **盲问题的双先验耦合**：BlindDPS 用两个并行 PF-ODE（信号流 + 核流，各自独立高斯初始化）联合采样，每步用后验均值近似似然并分别施加梯度；GibbsDDRM 用 Langevin 更新 φ + Laplacian 正则，省掉训练第二个扩散模型的成本。
  7. **时间线与覆盖范围**：综述将 DIS 发展推到 2025 年中，并纳入 flow matching / rectified flow（Gao et al. 2024 证明高斯参考分布下与扩散等价）及 FlowChef、FlowDPS、FLAIR 等向 flow 框架的迁移。

  ## 潜在研究方向

  1. **计算成本仍是主线瓶颈**：SMC 有收敛保证但粒子数大时昂贵；DPS 家族每步反传 score 网络；DAPS 用更多算力换稳定性。inference-time scaling（粒子数轴）刚起步，如何在保证后验质量的前提下压缩 NFE 未解决。
  2. **盲问题的先验工程**：BlindDPS 需为核训练独立扩散模型，GibbsDDRM 虽省去但引入 Langevin 调参；对一般参数化前向算子 A_φ，何时需要显式先验 p(φ)、何时用正则项即可，缺系统判据。
  3. **数据稀缺与分布失配**：综述提及但未深入——扩散先验在分布外测量（如新型成像模态、科学仪器数据）上的失效机制与校准方法。
  4. **高维数据**：视频/体数据上的 DIS 仅见 FK-steering 类初步工作（3D/4D 物理一致性奖励），后验正确性保证在高维更难维持。
  5. **文本多模态调控**（Sec. 6，正文截断前未覆盖细节）：以文本为额外控制旋钮的方向在正文中仅点到，实现机制与理论刻画留白。
  6. **本文局限**：作为综述无原创实验；分类侧重数学主线，对各方法在实际任务（除 MRI/去模糊/相位恢复外）的横向基准对比依赖 Daras et al. (2024) 的旧结果；时间线止于 2025 年中，flow/DiT 新架构下的 DIS 适配仍在快速演化。

  ## 与林赛研究的关联

  - **逆问题即本组日常**：HHG 光谱反演分子轨道动力学、阿秒 streaking 反演光电发射时间结构、从超快衍射/散射图样反演瞬态结构——全是 y = A(x) + n 形式。本篇的分类地图可直接用于我们为具体反演任务选求解器：线性算子（如衍射）走 DDRM/DAPS 的 SVD/解耦路线，**非线性算子（HHG 微扰极化响应）只能走 DPS/变分类**，这是选型时最关键的一条结论。
  - **瞬态量子相位课题接口**：`key-transient-quantum-phase-optical-20260726` 课题中，从含时吸收/发射谱反演量子相位的时间演化可建模为盲逆问题（前向算子含未知激光场包络参数 φ），BlindDPS 的双 PF-ODE 耦合框架或 GibbsDDRM 的正则化 φ 更新可直接迁移。
  - **后验采样 vs 单点估计的科学意义**：强场反演常有多解（不同轨迹给同谱线）。DPS 给的是偏 MMSE 的单点解，可能抹掉物理上有意义的多个分支；RSLD/SMC 的多模态后验采样对"列出所有相容的物理情景"更有价值——写申请书时这是论证方法学先进性的现成支点。
  - **扩散先验的数据饥饿问题**：我们多数反演任务的训练数据远少于自然图像，数据稀缺一节（综述点到但未展开）恰好是我们必须自己补强的空白，可作为创新点声明。
  - **注意**：本笔记正文为 arXiv:2508.01975《Diffusion Models for Inverse Problems》（Chung, Kim, Ye），与登记的元数据标题（TFLN 波导 SHG 的 FNO 论文）**不符**，疑为入库时标题/摘要错配，需修正 frontmatter 后此笔记才有检索价值。

  ## 来源
  - 蒸馏自全文（deep-read）：arXiv:2508.01975v1 [cs.LG]，2025-08-04（正文截断于 Sec. 5.1 中段）


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：DIS 四分类体系：扩散模型逆问题求解器统一综述（显式近似/变分推断/SMC/解耦数据一致性）

**原理**：统一数学主线：后验 score 分解 ∇log p(x_t|y) = ∇log p(x_t) + ∇log p(y|x_t)，中心难点是不可解的似然项，各类方法分野仅在如何近似它；Tweedie 定理 E[x₀|x_t] = (1/s_t)(x_t + σ_t²∇log p(x_t)) 是所有方法共享支点（扩散网络既是 score 估计器也是后验均值估计器）；四类：显式近似（DPS 家族 Jensen 近似 p(y|x_t) ≈ p(y|x̂_{0|t})，唯一通用非线性前向；DDRM SVD 谱空间三分支）、变分推断（RED-Diff score-distillation、APS 摊销、RSLD 粒子+排斥正则）、解耦数据一致性（DAPS：PF-ODE 采样 + N 步 Langevin 施加测量约束）、SMC 粒子滤波（粒子数→∞ 渐近收敛真实后验）；盲问题 BlindDPS 双 PF-ODE 耦合 / GibbsDDRM Langevin+Laplace 先验。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Score-ALD 似然近似 | ∇log p(y|x_t) ≈ −Aᵀ(y − Ax_t)/(σ²_y + γ²_t) | 研究方法（显式近似） |
| Tweedie 定理 | E[x₀|x_t] = (1/s_t)(x_t + σ_t²∇log p(x_t)) | 研究方法（理论框架） |
| DDRM SVD 分支 | A = UΣVᵀ，奇异值空间按 σ_t vs σ_y/s_i 分段高斯替换（s_i=0 / σ_t<σ_y/s_i / σ_t≥σ_y/s_i） | 研究方法（显式近似） |
| DDS 流形假设 | ∂x̂_{0|t}/∂x_t = (1/√ᾱ_t)P_M，单次 NFE + 共轭梯度/Krylov 多步投影 | 研究方法（显式近似） |
| 目标三分法 | 后验采样 / MMSE / MAP 不可同时最优（perception-distortion 权衡，Blau & Michaeli 2018） | 研究问题 |

**适用边界**：DPS 误差界仅高斯测量下可控（DMAP 指出其行为更接近 MAP 而非后验采样）；SMC 粒子数大时昂贵、DAPS 用算力换稳定；训练分布与测量分布失配的性能退化缺量化；时间线止于 2025 年中（flow/DiT 适配快速演化）；全部以成像为战场，谱学/时间序列反演的适配（噪声日程、score 架构、数据一致性形式）基本空白。
**代表作**：Chung, Kim & Ye, Diffusion Models for Inverse Problems: 从后验采样到盲问题与文本调控的系统综述（arXiv:2508.01975）
*方法卡回补 2026-10-03*

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2508_01975-fourier-neural-operators-for-fast-simulation-and-inverse-des]]
- [[2508.01975]]
- [[arpes]]
- [[key-transient-quantum-phase-optical-20260726]]
- [[强场超快]]
- [[强场超快光学]]
- [[强场驱动]]
- [[泵浦探测]]
- [[瞬态量子相位]]
- [[莫尔超晶格]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
