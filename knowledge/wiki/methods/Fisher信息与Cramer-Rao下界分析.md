---
title: "Fisher信息/Cramér-Rao下界分析"
type: "methods"
created: "2026-09-11T23:20:19Z"
updated: "2026-11-01T09:00:00Z"
tags: ["方法学", "type/method"]
related: ["2025-2512_23538-fisher-information-as-an-operational-metric-for-structured-o", "2026-2606_28586-constructor-theoretic-optical-time-delay-phase-and-fisher-di", "2512.23538", "2606.28586"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-09-27T02:13:42Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Fisher信息（含量子Fisher信息）刻画光场/测量对参数微扰的敏感度，Cramér-Rao下界据此给出任意无偏估计量方差的可估性极限，既可作为结构光束参数敏感性的可操作度量，也可在光学延迟/相位估计中被诠释为任务不可能性陈述而非单纯统计结果。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
Fisher 信息 I(θ) = E[(∂_θ log L)²] 度量数据对参数 θ 的信息量；Cramér-Rao 下界给出无偏估计方差下限 Var(θ̂) ≥ 1/I——反演方法学里「这个参数能测到多准」的先验判据。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 定义 | I(θ) = E[(∂_θ log L)²]；多参数为 Fisher 矩阵 | [1] |
| 下界 | Var(θ̂) ≥ I⁻¹（Cramér-Rao） | [1] |
| 用法 | 设计阶段用 I 谱选最优测量维度（HHG 多维约束的灵敏度排序） | [2] |

✅ 反演实验设计（维度裁剪）、精度上界预估。
❌ 有偏估计/贝叶斯先验下界需广义化；I 依赖模型正确性。

- 经典统计推断框架（Fisher 1922 / Cramér 1946 教科书谱系）；HHG 灵敏度应用实例见库内方案 [[HHG反演方法学]]。

## 适用边界

该界只给出精度下界（可估性极限），实际能否饱和取决于估计量的无偏性与测量方案是否最优，且对高维结构光场计算Fisher信息本身有成本，其结论宜理解为不可能性/极限陈述而非自动可实现的精度保证。

## 代表作

- paper:2025-2512.23538-fisher-information-as-an-operational-metric-for-structured-o
- paper:2026-2606.28586-constructor-theoretic-optical-time-delay-phase-and-fisher-di

## 证据日志

- 2026-09-11｜r6｜仅简报｜[paper:2025-2512.23538-fisher-information-as-an-operational-metric-for-structured-o] Fisher信息/Cramér-Rao下界分析：把参数估计精度下界用作结构光束的可操作度量，量化光场对参数微扰的敏感性并给出可估性极限。
- 2026-09-11｜r6｜仅简报｜[paper:2026-2606.28586-constructor-theoretic-optical-time-delay-phase-and-fisher-di] 量子Fisher信息与Cramér-Rao界：给出光学延迟/相位估计的方差下界，并被本文诠释为任务不可能性陈述而非单纯统计结果。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2025-2512_23538-fisher-information-as-an-operational-metric-for-structured-o]]
- [[2026-2606_28586-constructor-theoretic-optical-time-delay-phase-and-fisher-di]]
- [[2512.23538]]
- [[2606.28586]]
<!-- /linsai-wikilinks -->
