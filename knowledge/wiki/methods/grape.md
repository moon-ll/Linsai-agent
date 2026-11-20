---
title: "GRAPE（梯度上升脉冲工程）"
type: "methods"
created: "2026-10-17T06:42:09Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-17T06:42:09Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

GRAPE 将控制场按时间分段常数离散，并利用解析梯度进行梯度上升优化波形，是量子门、态转移及 NMR 脉冲优化的标准高效方法，广泛应用于离子阱、超导比特等量子技术平台。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
GRAPE（梯度上升脉冲工程）把量子最优控制写成目标泛函（保真度）对脉冲场分段幅值的梯度上升：用前向-后向传播高效算出梯度，迭代设计控制场——量子/自旋系统脉冲设计的标准算法。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 梯度 | ∂Φ/∂u_k 由前向态与伴随态的交叠给出（无需数值微分） | [1] |
| 典型分段 | 数十-数百个时间切片，每片幅值自由 | [1] |
| 收敛 | 保真度对迭代轮数单调上升（凸性好的体系） | [1] |

✅ 自旋/超导比特/分子转子等可控量子系统的波形设计；HHG 场整形的概念来源之一。
❌ 连续谱强场体系的动力学目标函数设计是难点；模型失配时实验保真度下降。

- N. Khaneja, T. Reiss, C. Kehlet, T. Schulte-Herbrüggen, S. J. Glaser, "Optimal control of coupled spin dynamics: design of NMR pulse sequences by gradient ascent algorithms," J. Magn. Reson. 172, 296–305 (2005). https://doi.org/10.1016/j.jmr.2004.11.004

## 适用边界

以控制场分段常数近似和可解析求梯度的系统模型为前提（梯度与动力学仿真成本随体系规模增长），适用于波形可离散化、模型精确已知的门与态转移控制场景。

## 代表作

- arXiv:2205.15574
- arXiv:2205.12110

## 证据日志

- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.15574-quantum-optimal-control-practical-aspects-and-diverse-method] GRAPE（梯度上升脉冲工程）：控制场分段常数离散并使用解析梯度，是量子门与 NMR 脉冲优化的标准高效工具。
- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.12110-quantum-optimal-control-in-quantum-technologies-strategic-re] GRAPE（梯度上升脉冲工程）：基于梯度的波形优化，是离子阱/超导比特等平台上量子门与态转移控制的主流算法。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
