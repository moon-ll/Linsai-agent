---
title: "2024-2410_00083-a-survey-on-diffusion-models-for-inverse-problems"
type: "papers"
created: "2026-09-26T13:01:03Z"
updated: "2026-11-15T15:09:25Z"
tags: []
related: ["2410.00083", "强场驱动", "量子几何"]
source_raw: "2024-2410.00083-a-survey-on-diffusion-models-for-inverse-problems.md"
growth_stage: "seedling"
confidence: 0.5
auto_grown: true
review_status: "pending"
has_fulltext: true
digest_level: "fulltext"
---

• # A Survey on Diffusion Models for Inverse Problems — 扩散模型求解逆问题综述

  ## 林赛的理解

  这篇综述对我们组的直接意义在于：它把"用预训练扩散模型作先验解逆问题"这一整条技术栈整理成了统一数学框架。我们关心的实验/数据分析问题——比如从有限探测器信号反演强场驱动过程中的时变相位、从稀疏角度光谱反演量子几何信息——本质上都是线性或非线性逆问题。综述的核心洞察（Bayes 分解式 2.17：条件 score = 无条件 score + 测量匹配项）给我们提供了一条清晰的思路：与其为每个实验构型重新训练条件模型，不如训练一个"干净信号分布"的无条件扩散先验，再通过测量一致性项在采样过程中引导，从而免重训练地适配不同实验配置。这对我们意味着：HHG/阿秒实验数据反演管线的架构可以复用同一个先验模型，只需替换测量算子 A。

  ## 研究问题

  论文要回答的核心问题是：**如何仅使用预训练（无条件）扩散模型作为信号先验 p(x)，在不需要为每个具体逆问题重新训练或微调的前提下，从带噪测量 y = A(x) + σ_y z 中恢复未知信号 x？**

  围绕这一中心问题，作者提出并回答三个子问题：
  - 如何将条件 score 分解为可计算项与难算项，各方法分别对测量匹配项 ∇_{xt} log p(y|x_t) 做了什么近似或规避？
  - 现有方法如何分类、彼此之间的数学联系是什么（统一的模板形式 ∇_{xt} log p(y|x_t) ≈ −L_t M_t / G_t）？
  - 潜空间扩散模型（latent diffusion）用于逆问题有哪些特有的挑战与解决方案？

  论文明确划界：不涵盖直接学习条件扩散模型/流（Li, Saharia, Whang, Luo, Albergo 等），因为那类方法每个新应用都要重训练；也不追求方法清单穷尽，而是选取代表性方法放入统一框架。

  ## 研究背景

  学术脉络分三个阶段：
  - **2000 年代的优化方法**：将逆问题表述为"数据保真 + 正则化"的优化问题（Daubechies, Candès, Donoho, Figueiredo & Nowak 等），用光滑性（Rudin 全变分）或小波/字典稀疏性作正则。
  - **深度学习的点估计范式**：用配对数据直接学测量→信号的映射（Dong, Chen, Zamir 等），但 L2 重建损失导致"回归到均值"（regression to the mean），预测结果是所有合理重建的平均，可能模糊甚至落在目标解空间之外（Blau & Michaeli）。
  - **去噪先验与贝叶斯后验采样**：强大去噪器隐含编码了自然信号的分布信息，可嵌入优化框架（plug-and-play 思想，Venkatakrishnan, Kamilov, Milanfar 等）；更根本地，把逆问题看作从后验 p(x|y) 采样，可同时保留感知质量与失真性能（Blau & Michaeli 证明失真与感知不可同时最优，但后验采样在失真误差上近乎最优 [1]）。

  扩散模型解决逆问题的关键数学障碍：条件似然 p_t(y|x_t) = ∫ p(y|x_0) p(x_0|x_t) dx_0（式 2.20）是不可积积分，使测量匹配项失去闭式表达；Gupta 等 [136] 甚至证明存在后验采样问题实例，无条件采样可证明快速而后验采样需要超多项式时间。围绕如何绕过这一不可积性，催生了大量免重训练方法，这正是本综述的动机。

  另一个相关背景是 Ambient Diffusion [137]：在只有损坏数据（无干净样本）时也能训练扩散先验，解决了"要先验才能解逆问题、要有解才能得样本"的鸡生蛋困境——这对我们这种干净实验数据昂贵/不可得的场景直接相关。

  ## 研究方法

  论文采用综述方法，构建两套分类学：

  **按重建算法族分类（四大族 + Other）**：
  1. **测量匹配的显式近似**：用闭式表达式近似测量匹配 score，模板形式 ∇_{xt} log p(y|x_t) ≈ −L_t M_t / G_t，其中 M_t 为测量误差向量、L_t 为从 R^m 升维回 R^n 的"提升"矩阵、G_t 为引导强度标量。代表方法及近似式（图 1 汇总）：Score ALD：−A^⊤(y−Ax_t)/(σ_y²+γ_t²)；Score-SDE：−A^⊤(y+σ_t ε−Ax_t)（先对测量加噪，要求 A 正交）；ILVR：−(A^⊤A)^{−1}A^⊤(y_t−Ax_t)；DPS：−(I+∇²log p_t(x_t))^⊤ A^⊤(y−AE[x_0|x_t])（首个支持非线性）；ΠGDM：−∂E[x_0|x_t]/∂x_t (r_t²AA^⊤+σ_y²I)^{−1}A^⊤(y−AE[x_0|x_t])；Moment Matching：−∇E[x_0|x_t]^⊤A^⊤(σ_y²I+Aσ_t²∇E[x_0|x_t]A^⊤)^{−1}(y−AE[x_0|x_t])；SNIPS/DDRM：奇异值域内 −Σ^⊤(σ_y²I−σ_t²ΣΣ^⊤)^†(ȳ−Σ·)；DDNM：Σ_t A^†(y−AE[x_0|x_t,y])；另有支持盲问题（未知前向算子系数）的 BlindDPS、GibbsDDRM、Blind RED-Diff，以及潜空间的 PSLD、STSL。
  2. **变分推断**：用可处理的简单分布近似真实后验 p(x|y) 再优化参数，如 RED-Diff、Score Prior、Efficient Score Prior；CSGM 类：通过反传优化确定性扩散采样的初始噪声（在潜空间做优化），如 DMPlug、SHRED、Consistent-CSGM、Score-ILO。
  3. **渐近精确方法**：构造 Markov 链（MCMC：PnP-DM、FPS、PMC）或粒子序列传播（SMC：SMCDiff、MCGDiff、TDS），目标是真正从后验分布采样。
  4. **其他**：Implicit denoiser prior（Kadkhodaie & Simoncelli，仅用 Tweedie 公式）、MCG、Resample、MPGD、P2L、TReg、DreamSampler（后三种支持文本条件）。

  **按优化技术分类**：Grad（单步梯度）、Proj（投影到测量子空间）、Samp（定义建议分布传播多条粒子链）、Opt（定义并求解逐步或全局优化问题），可归多类。

  **按问题类型分类**：线性/非线性（非线性算子示例：相位恢复 A(X)=|FX|、JPEG 压缩去除；黑洞成像 = 稀疏含噪傅里叶相位恢复）；是否含噪；非盲/盲；是否带文本条件。

  背景数学工具：VE SDE（X_t = X_0 + σ_t Z，典型调度 σ_t = √t）与 VP SDE（OU 过程 d x_t = −x_t dt + √2 dW_t，X_t = e^{−t}X_0 + √(1−e^{−2t})Z；一般形式 X_t = √ᾱ_t X_0 + (1−ᾱ_t)Z）；reverse SDE（Anderson 定理）与 probability flow ODE；DDIM 确定性更新；Tweedie 公式 ∇_{xt} log p_t(x_t) = (E[x_0|x_t]−x_t)/σ_t² 与去噪分数匹配目标 J_DSM = E‖h_θ(x_t)−x_0‖²；潜扩散（Stable Diffusion 的潜空间维度 64×64×4 表示 512×512×3 图像）。

  ## 主要发现与核心结论

  - 统一分解式：条件 score = 无条件 score + 测量匹配项（式 1.2、2.17），这是所有免重训练方法的共同骨架；各方法的差异本质上就是对测量匹配项 ∇_{xt} log p(y|x_t) 的不同近似（图 1 给出 9 种闭式近似的逐项对照）。
  - 所有方法的目标都是解释测量 y，区别只在强制测量一致性的手段：梯度（Grad）、投影（Proj）、采样（Samp）或显式优化（Opt）。
  - Score-SDE 与 Score ALD 的差别仅在于前者对测量加噪带来随机性（要求 A 正交）；inpainting 特例（Repaint）退化为用已知像素值直接替换。
  - 潜扩散用于逆问题需要特殊处理（§3.5），这是单独讨论的挑战。
  - Ambient DPS 的实证结论：在高损坏区间内，从损坏数据学到的先验对逆问题的有用性甚至可以超过从干净数据学到的先验。
  - 恢复类型不可兼得：MAP/MMSE 最小化失真但产生"不真实的平均解"，后验采样感知质量更高且失真近乎最优（[1]），但 Gupta 等 [136] 证明某些后验采样实例需要超多项式时间——这是该方向的内在计算障碍。
  - Kadkhodaie & Simoncelli 的方法完全基于 Tweedie 公式 ∇_y log p(y|xc) = (I−MM^⊤)r(y) + M(xc−M^⊤ y)（式 3.4），说明仅预训练去噪器的隐式先验即可求解去模糊、超分辨、压缩感知。

  ## 潜在研究方向

  - **盲逆问题与未知噪声**：大多数方法假设前向算子已知、噪声方差已知；支持盲设定（BlindDPS、GibbsDDRM、Blind RED-Diff）的方法仍少，是开放方向。
  - **潜空间逆问题的特殊挑战**：像素空间与潜空间之间的测量一致性如何保持，需要专门方案（综述 §3.5 专门讨论但未在截断文本中展开——深读时需注意补全）。
  - **计算可行性**：渐近精确方法（MCMC/SMC）理论漂亮但成本高；显式近似方法快但近似误差缺乏系统量化。Gupta 等的超多项式时间下界提示"后验采样的实用加速"本身是开放理论问题。
  - **非线性逆问题**：仅 DPS 一系及少数方法支持非线性算子（相位恢复、压缩去除），覆盖度不足。
  - **先验获取的鸡生蛋问题**：Ambient Diffusion/Consistent Diffusion Meets Tweedie 只在加性高斯噪声+线性损坏上有保证，EM 类方法的收敛依赖 EM 不陷入局部极小；从一般损坏数据学先验仍是活跃方向。
  - 文本条件逆问题（MPGD/P2L/TReg/DreamSampler）刚起步。

  ## 与林赛研究的关联

  - **HHG/阿秒光谱反演**：HHG 光谱→时域阿秒脉冲的重建可表述为带噪非线性逆问题（对应 §1 相位恢复 A(X)=|FX| 这一非线性算子示例）；综述给出"免重训练、仅换测量算子"的管线架构，意味着同一扩散先验（在阿秒脉冲形状分布上预训练）可复用于不同驱动条件，避免每个构型重训。
  - **强场驱动/交变磁实验数据分析**：从部分角度或稀疏采样的探测信号反演体系响应，本质是压缩感知/傅里域 inpainting（MRI 多线圈模型 A_i = PFS_i 与稀疏角度 CT A = PR 的表述可直接类比我们的傅里域稀疏采样问题）；DDRM/SNIPS 的奇异值分解处理与投影类方法（DDNM、ILVR）是即插即用的候选。
  - **干净数据昂贵的场景**：Ambient Diffusion 方向（仅从含噪/损坏测量学先验）与我们的实验现实吻合——高质量 HHG/莫尔体系全参量扫描数据获取成本高，"用损坏数据训先验、高损坏区间反而更优"的结论值得在我们数据管线上验证。
  - **方法选型参考**：若追求失真指标（重建精度），选变分/CSGM 类（近似 MMSE）；若需要后验不确定度量化（不同物理解的多重性），选 SMC/MCMC 渐近精确类；若需要实时性，选 Grad/Proj 类单步方法。我们申请书中写"数据反演管线"时可引用此综述的统一框架作为方法论依据。

  ## 来源
  - 蒸馏自全文（deep-read）
  - arXiv:2410.00083v1 [cs.LG]（Daras et al. 2024，UT Austin / KAIST / Sony AI / Google）
  - 注：本次注入全文在 §3.1.2 后截断，§3.2–§3.5（变分推断、CSGM、渐近精确方法、潜空间专节）仅依据目录、表 1 与引言描述转述，未逐节深读。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：扩散模型逆问题求解的分类学综述（重建算法四族 + 优化技术/问题类型双轴）

**原理**：两套分类学：按重建算法族分四类——① 测量匹配 score 的显式近似（统一模板 ∇log p(y|x_t)≈−L_tM_t/G_t；涵盖 Score ALD/S-SDE/ILVR/DPS/ΠGDM/Moment Matching/SNIPS/DDRM/DDNM 及盲问题 BlindDPS 等与潜空间 PSLD/STSL）；② 变分推断（RED-Diff 系与 CSGM 类反传优化初始噪声：DMPlug/SHRED/Score-ILO）；③ 渐近精确后验采样（MCMC：PnP-DM/FPS/PMC；SMC：SMCDiff/MCGDiff/TDS）；④ 其他（隐式去噪先验、MCG、文本条件 DreamSampler 等）。按优化技术分 Grad/Proj/Samp/Opt；按问题类型分线性/非线性（相位恢复、JPEG 去除、黑洞成像）、含噪、盲/非盲、文本条件。数学基础：VE/VP SDE、Anderson 反向 SDE、DDIM、Tweedie 公式与 DSM 目标。

**参数表**：

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 潜扩散示例 | Stable Diffusion 潜空间 64×64×4 表示 512×512×3 图像 | §数学工具 |

**适用边界**：综述性分类学（无统一数值基准表）；各方法近似式成立条件随测量算子性质而异（如 Score-SDE 要求 A 正交、DPS 首个支持非线性）。
**代表作**：本文（arXiv:2410.00083）
*方法卡回补 2026-09-27*

<!-- linsai-wikilinks -->
## 关联概念

- [[2410.00083]]
- [[强场驱动]]
- [[量子几何]]
<!-- /linsai-wikilinks -->
