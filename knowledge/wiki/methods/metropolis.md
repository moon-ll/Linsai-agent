---
title: "Metropolis-Hastings within-model sampling"
type: "methods"
created: "2026-10-03T16:45:50Z"
updated: "2026-11-01T10:29:09Z"
tags: ["方法学", "#type/method"]
related: ["1804.09583", "2404.05671", "2506.18802", "HHG反演方法学", "TDSE", "Trans-dimensional Hamiltonian 模型选择与参数估计笔记", "arXivID", "bayesian-inference", "混合几何自适应MCMC在高阶Ising模型贝叶斯推断中的应用", "贝叶斯反演"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-11-01T10:29:09Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

Metropolis-Hastings 以接受概率 α = min(1, p(x′)L(x′)/(p(x)L(x))) 构造马尔可夫链、使链的平稳分布即目标分布，是贝叶斯反演后验采样的基础算法；在固定模型维数内作为参数更新核，为参数估计提供置信区间与不确定度量化；自适应 MH（AMH）在预热期在线学习提议协方差，统一不同参数的尺度差异并提供全局探索能力，以应对高维耦合参数空间；该固定维 MH 核还可与跨维移动组合构成混合采样器。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 对称提议（高斯随机步）步长的目标接受率 | 25–50% | canonical 表[1]，Metropolis et al., J. Chem. Phys. 21, 1087 (1953), doi:10.1063/1.1699114 |
| Metropolis MC 应用示例（MPS₃ 磁交换参数估计）：MC 步数 | 100,000 步（后 20,000 步取平均） | src:2103.04474 |

## 适用边界

仅在固定模型维数内更新参数后验，不能单独完成跨模型比较与选择（需与跨维移动组合成混合采样器）；标准 MH 在高维（>10 参数）强耦合参数下混合缓慢、需大量后验评估，多峰后验需多链，计算成本高，需 AMH 预热期协方差自适应或 HAMC/NUTS、代理模型等混合几何策略缓解。

## 代表作

- arXiv:2506.18802
- arXiv:2404.05671
- Metropolis et al., J. Chem. Phys. 21, 1087 (1953), doi:10.1063/1.1699114

## 证据日志

- 2026-10-03｜r53｜仅简报｜[paper:2025-2506.18802-trans-dimensional-hamiltonian-model-selection-and-parameter] Metropolis-Hastings within-model sampling：在固定模型维数下更新参数后验，为参数估计提供置信区间与不确定度量化。
- 2026-10-03｜r53｜仅简报｜[paper:2024-2404.05671-hybrid-geometry-adaptive-mcmc-for-bayesian-inference-in-high] 自适应Metropolis-Hastings（AMH）：基于链历史协方差自适应提议分布，为高维耦合参数提供高效全局探索。
- 2026-11-01｜r112｜仅简报｜[paper:2024-2404.05671-hybrid-geometry-adaptive-mcmc-for-bayesian-inference-in-high] 自适应Metropolis-Hastings（Adaptive MH）：在预热期在线学习提议协方差，统一不同参数的尺度差异并提供全局探索能力。
- 2026-11-01｜r112｜仅简报｜[paper:2025-2506.18802-trans-dimensional-hamiltonian-model-selection-and-parameter] Metropolis-Hastings 采样：作为固定维数下的参数更新核，与跨维移动组合构成混合采样器。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[1804.09583]]
- [[2404.05671]]
- [[2506.18802]]
- [[HHG反演方法学]]
- [[TDSE]]
- [[Trans-dimensional Hamiltonian 模型选择与参数估计笔记]]
- [[arXivID]]
- [[bayesian-inference]]
- [[混合几何自适应MCMC在高阶Ising模型贝叶斯推断中的应用]]
- [[贝叶斯反演]]
<!-- /linsai-wikilinks -->
