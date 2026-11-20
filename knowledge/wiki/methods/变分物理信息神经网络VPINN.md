---
title: "VPINN / hp-VPINN（变分形式 PINN）"
type: "methods"
created: "2026-09-12T19:42:09Z"
updated: "2026-11-01T10:00:00Z"
tags: ["方法学", "type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

VPINN/hp-VPINN 以测试函数的弱（变分）形式替代逐点残差进行训练，从而降低对高频振荡解在采样密度与网络表达能力上的要求，尤其适合具有快速振荡特征的波类型方程。

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

其优势集中于具有快速振荡特征的波类型方程，本轮证据未覆盖非振荡光滑解等其他场景；且同期逐点改进路线 I-PINN 声称在无额外计算开销下较 PINN/IAW-PINN/IA-PINN 精度至少提升一个数量级，弱形式路线与逐点改进路线的优劣需在同一基准上对照验证。

## 代表作

- arXiv:2505.22761
- arXiv:2407.19421

## 证据日志

- 2026-09-12｜r12｜仅简报｜[paper:2025-2505.22761-a-comprehensive-analysis-of-pinns-variants-applications-and] VPINN / hp-VPINN（变分形式 PINN）：以测试函数弱形式替代逐点残差，降低对高频振荡解的采样与表达能力要求，适合具有快速振荡特征的波类型方程。
- 2026-09-12｜r12｜仅简报｜[paper:2024-2407.19421-improved-physics-informed-neural-network-in-mitigating-gradi] I-PINN（改进型 PINN）：本文核心方法，在无额外计算开销下将求解精度相对 PINN/IAW-PINN/IA-PINN 至少提升一个数量级。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
