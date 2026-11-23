---
title: "PINN（物理信息神经网络）"
type: "methods"
created: "2026-10-02T23:21:23Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2506.10379", "HHG反演方法学", "物理信息神经网络（PINN）"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-10-31T20:01:29Z"
settled_count: 3
---

<!-- methods-settle:v1 -->

## 原理

PINN 以神经网络连续逼近目标函数（PDE 解、波函数或未知传播子），将方程残差及边界/归一化条件作为软约束损失项，实现物理定律与观测数据的联合拟合，在稀疏散乱、含噪数据下同步反演解与方程系数场（iPINN 进一步将哈密顿量参数与网络权重联合训练、以薛定谔方程残差为软约束，实现少测量下的系统参数反演）；该范式可从 PDE 推广至薛定谔本征值问题、非线性积分方程（DSE，残差作损失可替代迭代不动点求解）、跳跃型 PDE 反问题，以及全息度规反演、XAS 等病态逆问题的稳定化反演。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
物理信息神经网络（PINN）把 PDE 残差作为损失项并入神经网络训练：L = L_data + λ·L_physics，使解自动满足方程结构——正问题求解与反问题参数识别一体化的框架。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 损失 | L = L_data + λ·L_physics（PDE 残差）+ 可选边界项 | [1] |
| 反问题 | 待识别物理参数作为网络可训练变量 | [1] |
| 混合精度 | 自动微分构造残差（库内自动微分两工作页为工程实现） | [1] |

✅ 物理约束下的正/反问题；与 HHG 谱反演结合的可行性见 [[HHG反演方法学]] §1.3。
❌ 刚性 PDE/多尺度问题训练困难；谱反演中需与贝叶斯不确定度报告互补。

- M. Raissi, P. Perdikaris, G. E. Karniadakis, "Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations," J. Comput. Phys. 378, 686–707 (2019). https://doi.org/10.1016/j.jcp.2018.10.045

## 适用边界

物理约束以软约束（损失惩罚）形式实现，方程仅在残差最小化意义下近似满足，反演精度受训练收敛性、配点采样、边界数据质量与测量数量（iPINN 依赖少测量）制约；对病态逆问题（如 XAS）需将正向物理约束嵌入训练方能改善稳定性与物理一致性；对强非线性问题的可解性依赖损失构造与网络拟设质量，且在含跳跃的 PDE 反问题中 PINN 仅作为框架第一阶段骨架使用。

## 代表作

- paper:2017-1711.10561-physics-informed-deep-learning-part-i-data-driven-solutions
- paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery
- paper:2025-2511.22522-adsdeep-learning-made-easy-ii-neural-network-based-approache
- paper:2025-2504.05367-physics-informed-neural-networks-for-one-dimensional-quantum
- paper:2025-2405.24194-energy-embedded-neural-solvers-for-one-dimensional-quantum-s
- paper:2025-2411.02177-physics-informed-neural-networks-viewpoint-for-solving-the-d
- paper:2026-2603.27684-solving-the-inverse-problem-of-x-ray-absorption-spectroscopy
- paper:2025-2510.14656-inverse-problems-for-partial-differential-equations-with-jum

## 证据日志

- 2026-10-02｜r48｜仅简报｜[paper:2017-1711.10561-physics-informed-deep-learning-part-i-data-driven-solutions] PINN（物理信息神经网络）：将PDE残差作为软约束嵌入损失，实现物理定律与观测数据的联合拟合，是全文核心方法。
- 2026-10-02｜r48｜仅简报｜[paper:2025-2511.22522-adsdeep-learning-made-easy-ii-neural-network-based-approache] PINN（物理信息神经网络）：以体引力场方程/输运方程残差为损失，从边界热力学与电导数据直接反演有效势与度规函数。
- 2026-10-03｜r49｜仅简报｜[paper:2026-2603.27684-solving-the-inverse-problem-of-x-ray-absorption-spectroscopy] 物理信息神经网络（PINN/物理信息深度学习）：将XAS正向物理约束嵌入网络训练，显著改善病态逆问题的反演稳定性与物理一致性。
- 2026-10-03｜r49｜仅简报｜[paper:2025-2504.05367-physics-informed-neural-networks-for-one-dimensional-quantum] 物理信息神经网络 (PINN)：以配点方程残差损失求解薛定谔本征值问题，展示神经网络作为可微波函数变分拟设的求解范式。
- 2026-10-03｜r49｜仅简报｜[paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery] 物理信息神经网络（PINN）：以网络为 PDE 解的连续逼近器、把方程残差作为损失正则项，实现小样本含噪数据下解与未知参数的联合反演。
- 2026-10-03｜r49｜仅简报｜[paper:2025-2411.02177-physics-informed-neural-networks-viewpoint-for-solving-the-d] 物理信息神经网络（PINN）：将非线性积分方程残差作为损失、网络直接参数化未知传播子函数，实现无网格、无迭代的DSE求解，并天然可扩展为反问题求解器。
- 2026-10-03｜r49｜仅简报｜[paper:2025-2405.24194-energy-embedded-neural-solvers-for-one-dimensional-quantum-s] 物理信息神经网络（PINN）：将薛定谔方程残差与边界/归一化条件写入损失函数，实现无网格求解本征值问题，可复用为强场一维模型体系的快速正问题求解器。
- 2026-10-31｜r108｜仅简报｜[paper:2025-2510.14656-inverse-problems-for-partial-differential-equations-with-jum] 物理信息神经网络（PINN）反问题框架：将PDE残差嵌入损失函数，在观测数据约束下同步反演解与系数场，是本文第一阶段骨架。
- 2026-10-31｜r108｜仅简报｜[paper:2025-2506.10379-hamiltonian-learning-via-inverse-physics-informed-neural-net] 逆物理信息神经网络（iPINN）：将哈密顿量参数与网络权重联合训练、用薛定谔方程残差作软约束，实现从少测量反演系统参数的逆问题求解范式。
- 2026-10-31｜r108｜仅简报｜[paper:2017-1711.10566-physics-informed-deep-learning-part-ii-data-driven-discovery] 物理信息神经网络（PINN）：将PDE残差作为软约束嵌入损失，使稀疏散乱数据下的解重构与方程系数辨识可同步完成。
- 2026-10-31｜r108｜仅简报｜[paper:2025-2411.02177-physics-informed-neural-networks-viewpoint-for-solving-the-d] 物理信息神经网络（PINN）：首次将PINN用于Dyson-Schwinger这类非线性积分方程，证明'方程残差作损失'可替代迭代不动点求解。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2506.10379]]
- [[HHG反演方法学]]
- [[物理信息神经网络（PINN）]]
<!-- /linsai-wikilinks -->
