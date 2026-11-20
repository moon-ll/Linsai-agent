---
title: "Physics-Informed Neural Networks (PINN)"
type: "methods"
created: "2026-10-02T23:20:55Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2502.00803", "arXivID"]
source_raw: ""
growth_stage: "growing"
confidence: 0.5
updated_at: "2026-10-31T20:01:44Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

PINN 以自动微分计算的物理方程残差作为软约束损失，与观测/边界数据联合训练单个神经网络，实现无网格的 PDE 求解与参数反演；新证据将其扩展至以体空间 Einstein-Dilaton 场方程为损失约束、联合边界数据反演有效势 V(φ)，并确认其可作为强场体系方程（SBE、半导体布洛赫方程）求解与数据融合的替代框架。

## 参数表

**库内方法卡回补参数**（2026-11-01，[[arXivID]] 均可验证）：
| 论文库评分 | 0.95（deepxiv-论文库深耕度标注） | 核心要点 
| 数据源 | iTEBD（最大键维度 D=100）一维横场 Ising，(J_z, h_x, h_z) = 0.8×(1, 0.25, −0.525) | 研究方法（数据来源） 
| 数据集 | A=2.6（200/400 频率）、A=10（200/600 频率）、多幅度 8/10 档；每轨迹 500 时间步 | 研究方法（数据来源） 
| 网络架构 | [500, a, 500]；简单数据集 a=3 即可，复杂数据集需 a=100–1000 | 研究方法（模型架构）/主要发现 6 
| 训练配置 | Adam lr 0.0002–0.001，80/20 划分，3000–9000 epoch | 研究方法（训练配置） 
| 数据效率 | 仅需 5.4% 样本（200 频率）达 TCN 3700 频率精度（省约 95%） | 主要发现 1 
| 精度 | A=2.6：>95% 测试 R²>0.95；A=10：115/120 测试 R²>0.95 | 主要发现 2 
| 基准结果（rMAE） | Convection 0.018（vs PINNsFormer 0.023）；1D-Reaction 0.010；Allen-Cahn 0.036（vs 0.331，−89%）；1D-Wave 0.016（vs FLS 0.102，−84%） | 主要发现 2 
| 流体任务 | Karman Vortex rMAE 0.161 vs SetPINN 0.287（−44%）；Fluid Dynamics 0.1834（对比方法训练崩溃返回 NaN） | 主要发现 3 
| 效率 | 较 PINNsFormer/SetPINN 快 2-3 倍；相对前最佳 rMAE 平均降低 46% | 研究方法 4/主要发现 2 
<!-- src:2024-2408_16806-physics-informed-neural-networks-and-extensions -->
<!-- src:2025-2509_18483-physics-informed-time-series-analysis-with-kolmogorov- -->
<!-- src:2502.00803 -->

## 适用边界

作为反演基座需搭配处理不连续性的机制——单独使用会把待反演系数中的跳变抹平、无法恢复间断界面；方程残差由自动微分实现，属软约束近似而非精确满足，依赖物理残差项与数据项的平衡。

## 代表作

- paper:2025-2510.14656-inverse-problems-for-partial-differential-equations-with-jum
- paper:2024-2408.16806-physics-informed-neural-networks-and-extensions
- paper:2025-2511.22522-adsdeep-learning-made-easy-ii-neural-network-based-approache

## 证据日志

- 2026-10-02｜r48｜仅简报｜[paper:2025-2510.14656-inverse-problems-for-partial-differential-equations-with-jum] Physics-Informed Neural Networks (PINN)：将PDE残差嵌入损失实现无网格参数反演，是整体框架基座，但单独使用会把系数中的跳变抹平。
- 2026-10-02｜r48｜仅简报｜[paper:2024-2408.16806-physics-informed-neural-networks-and-extensions] Physics-Informed Neural Networks (PINN)：本文的骨架方法：以物理残差+数据双损失训练神经网络，作为求解/反演PDE的统一框架被系统综述。
- 2026-10-31｜r108｜仅简报｜[paper:2025-2511.22522-adsdeep-learning-made-easy-ii-neural-network-based-approache] Physics-Informed Neural Network (PINN)：把体空间Einstein-Dilaton场方程作为损失约束，与边界数据联合反演有效势V(φ)。
- 2026-10-31｜r108｜仅简报｜[paper:2024-2408.16806-physics-informed-neural-networks-and-extensions] Physics-Informed Neural Network (PINN)：本文核心方法：以自动微分计算的方程残差作为软约束，为强场体系方程（如 SBE、半导体布洛赫方程）提供无网格求解与数据融合的替代途径。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2502.00803]]
- [[arXivID]]
<!-- /linsai-wikilinks -->
