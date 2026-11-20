---
title: "量子物理信息神经网络（QPINN）"
type: "methods"
created: "2026-09-25T23:22:24Z"
updated: "2026-11-01T10:00:00Z"
tags: ["方法学", "#type/method"]
related: ["2604.03346", "2604.15645", "物理信息神经网络（PINN）"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.6
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

QPINN 是 PINN 的量子类比：以参数化量子线路（PQC）的期望测量值作为 PDE 解的函数逼近器，将 PDE 残差嵌入变分量子算法的损失函数中，在量子-经典混合回路里训练，可视为可微量子线路（DQC, Kyriienko 等）框架向物理信息学习的推广，可在连续变量与离散变量平台上实现。

## 参数表

**联网检索升级**（2026-11-01，引用已核实）：机器学习驱动的方法族——**强化学习量子控制**（Bukov et al. PRX 2018：RL 在量子控制不同相位的学习行为，避开拓扑陷阱的短脉冲设计）；**贝叶斯主动学习力场**（Jinnouchi et al. PRL 2019：on-the-fly DFT 训练 MLFF，贝叶斯不确定度驱动采样，相变模拟）；**自动微分**构造物理约束/PDE 残差损失（PINN 框架的工程实现，Raissi 2019）。

| 要素 | 数值/要点 | 出处 |
| --- | --- | --- |
| RL 控制基准 | PRX 2018：短脉冲避开拓扑陷阱（单比特基准） | [1] |
| MLFF 采样 | 贝叶斯不确定度 > 阈值即调 DFT 训练（on-the-fly） | [2] |
| MLFF 应用 | 杂化钙钛矿相变（PRL 2019）；熔点（PRB 2019） | [2] |
| PINN 损失 | L = L_data + λ·L_physics（自动微分残差） | [3] |

- [1] M. Bukov, A. G. R. Day, D. Sels, P. Weinberg, A. Polkovnikov, P. Mehta, "Reinforcement Learning in Different Phases of Quantum Control," Phys. Rev. X 8, 031086 (2018). https://doi.org/10.1103/PhysRevX.8.031086
- [2] R. Jinnouchi, J. Lahnsteiner, F. Karsai, G. Kresse, "Phase Transitions of Hybrid Perovskites Simulated by Machine-Learning Force Fields Trained with On-the-Fly Bayesian Active Learning," Phys. Rev. Lett. 122, 225701 (2019). https://doi.org/10.1103/PhysRevLett.122.225701
- [3] M. Raissi, P. Perdikaris, G. E. Karniadakis, "Physics-informed neural networks...," J. Comput. Phys. 378, 686 (2019). https://doi.org/10.1016/j.jcp.2018.10.045

✅ 波形优化、力场加速的分子动力学、物理约束反演。
❌ RL 控制的 sim-to-real 差距；MLFF 外推区不可信；PINN 刚性 PDE 训练难。

## 适用边界

作为混合量子-经典路线可在近期含噪中等规模量子器件上实现（不同于需容错硬件与 qRAM 的全量子算法），但其近似假设空间依赖张量分解多项式假设类且规模有限，并继承经典 PINN 的失效模式：达到给定精度的浮点运算量与内存开销远超传统数值方法、谱偏置导致高频特征难捕捉、不内禀编码时间因果性导致训练窗口外推精度骤降。

## 代表作

- paper:2026-2604.03346-learning-pdes-for-portfolio-optimization-with-quantum-physic
- paper:2026-2604.15645-pinnacle-an-open-source-computational-framework-for-classica

## 证据日志

- 2026-09-25｜r34｜回原文｜[paper:2026-2604.03346-learning-pdes-for-portfolio-optimization-with-quantum-physic] 量子物理信息神经网络（QPINN）：将PDE残差嵌入参数化量子线路的损失函数，以量子模型作为PDE解的函数逼近器。
- 2026-09-25｜r34｜回原文｜[paper:2026-2604.15645-pinnacle-an-open-source-computational-framework-for-classica] 物理信息神经网络（PINN）：以 PDE 残差软约束替代网格离散，统一处理正问题与逆问题的核心求解范式

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2604.03346]]
- [[2604.15645]]
- [[物理信息神经网络（PINN）]]
<!-- /linsai-wikilinks -->
