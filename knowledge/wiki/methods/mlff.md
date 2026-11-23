---
title: "On-the-fly机器学习力场（MLFF）"
type: "methods"
created: "2026-10-18T14:01:52Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-18T14:01:52Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

On-the-fly机器学习力场（MLFF）在MD轨迹运行中按需在线采样DFT数据并自更新力场，免除预构建训练集、仅在模型不确定的必要时刻调用DFT，以近DFT精度实现大尺度长时MD，将第一性原理MD的构型采样成本降低多个量级。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Langevin Flow Maps（LFM）相对MLFF驱动MD的加速比（同等精度基准测试） | ≈10倍（快约一个数量级） | 2610.05998 |

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

精度与数据来源受限于在线调用所选DFT泛函，且仍需逐步积分MD（并承担训练期按需DFT调用开销），在同等精度下速度已被Langevin Flow Maps等新方法超越约一个数量级，对超长时稀疏事件采样效率存在局限。

## 代表作

- arXiv:1903.09613
- arXiv:2402.13450
- arXiv:2610.05998

## 证据日志

- 2026-10-18｜r85｜仅简报｜[paper:2019-1903.09613-phase-transitions-of-hybrid-perovskites-simulated-by-machine] On-the-fly机器学习力场（MLFF）：MD运行中按需在线采样DFT数据自更新力场，免除预构建训练集，实现DFT精度与大尺度长时MD的兼得。
- 2026-10-18｜r85｜仅简报｜[paper:2024-2402.13450-on-the-fly-machine-learned-force-fields-for-warm-dense-matte] 在线（On-the-fly）机器学习力场MD：在轨迹上边跑边学、仅在必要时调用DFT，把第一性原理MD的构型采样成本降低多个量级
- 2026-10-18｜r85｜仅简报｜[paper:2026-2610.05998-langevin-flow-maps-efficient-molecular-dynamics-and-transiti] 机器学习力场（MLFF）基准对比：作为基线，LFM 在同等精度下较 MLFF 驱动的 MD 快约一个数量级。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
