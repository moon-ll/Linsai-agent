---
title: "物理信息神经网络（PINN）"
type: "methods"
created: "2026-09-12T14:00:31Z"
updated: "2026-10-03T04:53:49Z"
tags: ["方法学", "type/method"]
related: ["2025-agupubs2025JH000758-a-comparative-study-of-physics-informed-and-data-driven-neur", "PINN（物理信息神经网络）"]
source_raw: ""
growth_stage: "mature"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 2
---

<!-- methods-settle:v1 -->

## 原理

PINN以自动微分计算PDE残差并与数据/边界条件构成复合损失，将物理约束嵌入神经网络训练，在数据稀缺条件下保持物理一致性，是强场方程正/反问题神经网络求解的起点范式；训练后得到连续场代理模型（内部点查询比BEM快约百倍），其物理残差嵌入思想还可迁移至生成器（如物理信息量子GAN）实现解空间正则化与样本需求大幅降低；配合SDGD随机维度梯度采样加速，求解能力可从常规低维扩展至千维量级高维PDE。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| SDGD加速后PINN可求解的PDE维度 | 千维量级（约10^3维） | paper:2024-2307.12306-stochastic-dimension-gradient-descent-sdgd-for-high-dimensio |
| 训练后PINN连续场代理模型内部点查询速度（相对BEM） | 快约100倍 | paper:2025-2509.12483-benchmarking-physics-informed-neural-networks-and-boundary-e |
| 物理残差嵌入生成器（物理信息量子GAN）的样本需求降幅 | 99.5% | paper:2025-2507.18132-inverse-design-using-physics-informed-quantum-gans-for-tailo |

## 适用边界

适用前提为PDE形式已知且残差可经自动微分计算，优势场景是数据稀缺但物理规律明确的正/反问题建模；常规（未加速）PINN基本限于低维PDE，高维扩展依赖SDGD等随机维度梯度采样，且存在梯度相关失效导致精度崩坏的典型风险（需改进型变体缓解），百倍级查询加速仅在代理模型训练完成后成立。

## 代表作

- paper:2024-2307.12306-stochastic-dimension-gradient-descent-sdgd-for-high-dimensio
- paper:2025-agupubs2025JH000758-a-comparative-study-of-physics-informed-and-data-driven-neur
- paper:2025-2505.22761-a-comprehensive-analysis-of-pinns-variants-applications-and
- paper:2025-2509.12483-benchmarking-physics-informed-neural-networks-and-boundary-e
- paper:2024-2407.19421-improved-physics-informed-neural-network-in-mitigating-gradi
- paper:2025-2507.18132-inverse-design-using-physics-informed-quantum-gans-for-tailo

## 证据日志

- 2026-09-12｜r10｜仅简报｜[paper:2024-2307.12306-stochastic-dimension-gradient-descent-sdgd-for-high-dimensio] 物理信息神经网络（PINN）：作为PDE求解框架，本文展示其经SDGD加速后可从常规低维问题扩展到千维量级。
- 2026-09-12｜r10｜仅简报｜[paper:2025-agupubs2025JH000758-a-comparative-study-of-physics-informed-and-data-driven-neur] PINN（物理信息神经网络）：将PDE残差嵌入损失函数作为物理约束，展示数据稀缺条件下保持物理一致性的建模途径。
- 2026-09-12｜r12｜仅简报｜[paper:2025-2505.22761-a-comprehensive-analysis-of-pinns-variants-applications-and] PINN（物理信息神经网络基线）：本文给出统一框架梳理：自动微分计算 PDE 残差 + 数据/物理复合损失，是强场方程正/反问题神经网络求解的起点范式。
- 2026-09-12｜r12｜仅简报｜[paper:2025-2509.12483-benchmarking-physics-informed-neural-networks-and-boundary-e] 物理信息神经网络（PINN）：以 PDE 残差+边界条件损失训练得到连续场代理模型，训练后内部点查询比 BEM 快约 100 倍。
- 2026-09-12｜r12｜仅简报｜[paper:2024-2407.19421-improved-physics-informed-neural-network-in-mitigating-gradi] 物理信息神经网络（PINN）：作为基线求解框架，暴露了梯度相关失效导致精度崩坏的典型失效模式。
- 2026-09-12｜r12｜仅简报｜[paper:2025-2507.18132-inverse-design-using-physics-informed-quantum-gans-for-tailo] 物理信息神经网络（PINN）：将电磁物理约束作为损失残差嵌入生成器训练，对解空间正则化，是样本需求降低99.5%的关键来源。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-agupubs2025JH000758-a-comparative-study-of-physics-informed-and-data-driven-neur]]
- [[PINN（物理信息神经网络）]]
<!-- /linsai-wikilinks -->
