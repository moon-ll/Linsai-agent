---
title: "Physics-informed Bayesian optimization of high-order harmonic generation in gases"
arxiv_id: "2611.14119"
authors: "Dominika Maslarova, Mattys Pouyez, Patrik Jansson, Jan Vabek, Robin Weissenbilder"
year: 2026
tags: ["deepxiv-论文库"]
project: ["NSFC-强场超快"]
direction: "阿秒科学"
source: "hermes-briefing"
imported_at: "2026-11-11T11:22:49Z"
score_deepxiv: 0.5
status: "unseen"
read_status: "unread"
has_pdf: false
---
# Physics-informed Bayesian optimization of high-order harmonic generation in gases

## 摘要
Optimization of high-order harmonic generation in gases is essential for attosecond science. Improving conversion efficiency from the infrared driving laser to the extreme-ultraviolet high-order harmonic radiation requires balancing microscopic single-atom dipole responses with macroscopic phase matching. The resulting conversion-efficiency landscape exhibits complex structures, such as the hyperbolic ridge in the pressure-length space, which can be difficult to accurately reconstruct using conventional Bayesian optimization. Here, we introduce a physics-informed Bayesian optimization framework that incorporates known physical scaling relations through nonlinear transformations of the search space. We first demonstrate the approach in the two-dimensional pressure-length space, where a direct grid scan enables detailed validation of the reconstructed landscape, before extending it to four dimensions, where exhaustive scanning becomes computationally impractical. In four dimensions, incorporating the pulse-duration scaling and a square-root transformation of conversion efficiency further improves the accuracy of the reconstructed landscape, as validated against an independent reference dataset. We also employ a threshold-based acquisition strategy to identify extended high-efficiency operating regions rather than isolated optimal points. Together, these results demonstrate that incorporating physical knowledge into Bayesian optimization improves the exploration and reconstruction of multidimensional high-order harmonic generation landscapes, extending its capabilities beyond locating individual optima.

## 背景概述与问题引入
气体高次谐波（HHG）是阿秒科学的主力光源，其转化效率由微观单原子偶极响应与宏观相位匹配共同决定。实验中需要在多参数空间（气体压强、介质长度、驱动脉宽、聚焦几何等）中寻找最优工作点。问题在于：转化效率景观中存在复杂结构——最典型的是压力-长度（pL）空间中的双曲脊（hyperbolic ridge）——常规贝叶斯优化（BO）对各向同性核与均匀采样假设敏感，重建这类景观的精度很差，往往只能找到孤立最优点而无法刻画整个高效率工作区域。这对需要稳定运行在扩展高效区的实验（如阿秒束线调参）是实际瓶颈。

## 关键发现及核心讨论
1. **物理先验通过非线性坐标变换注入 BO**：将已知物理标度关系（如双曲脊对应的 pL 守恒关系、脉宽标度）编码为搜索空间的非线性变换，使 BO 在变换后空间中面对的景观更平滑、更接近核函数假设。2 维 pL 空间的直接网格扫描验证：重建景观与真实景观的结构吻合度显著优于常规 BO。
2. **4 维空间的外推能力**：加入脉宽标度与转化效率的平方根变换后，在 4 维参数空间（网格扫描计算上不可行）中重建的精度提升，并用独立参考数据集交叉验证——这是从"找最优点"到"重建整个景观"的方法学跃迁。
3. **阈值采集策略定位扩展高效区**：用 threshold-based acquisition 代替默认的 EI/UCB 类采集函数，输出的是连通的高效率工作区域（适合实验长期稳定运行），而非孤立最优点。

## 主要方法
- 物理信息贝叶斯优化（physics-informed BO）：非线性变换搜索空间 + 已知标度关系
- 2 维验证：pL 空间直接网格扫描作为 ground truth
- 4 维扩展：脉宽标度 + 效率平方根变换，独立参考集验证
- 阈值采集策略：识别扩展高效率区域
- 体系：气体介质 HHG（红外驱动 → 极紫外辐射），微观单原子偶极 + 宏观相位匹配耦合模型

## 创新性
与常规"黑箱 BO 调参"不同，本文把 HHG 的已知物理标度（双曲脊、脉宽标度）作为先验直接编码进 BO 的搜索空间几何，解决了核方法对各向异性景观失效的问题；且目标从单点优化升级为多维景观重建。

## 结论与展望
物理先验注入显著改善多维 HHG 效率景观的探索与重建，threshold 采集策略给出可运行的高效区而非孤立点。对林赛组的直接启示：固体 HHG 实验同样面临多参数（厚度/掺杂/驱动场/相位匹配）复杂景观，该框架（非线性坐标变换 + 阈值采集）可迁移用于固体样品的参数优化与鲁棒工作区定位。