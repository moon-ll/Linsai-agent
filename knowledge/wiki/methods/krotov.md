---
title: "Krotov 方法"
type: "methods"
created: "2026-10-17T06:42:48Z"
updated: "2026-11-01T04:55:12Z"
tags: ["方法学", "#type/method"]
related: ["2610.15251"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-17T06:42:48Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Krotov 方法通过对控制场在全部时间点上做时间连续的同时更新，保证目标泛函单调收敛，具有全局收敛性质，适合平滑连续波形设计与大初值范围内的高保真全局优化（如高维波包/分子体系）。

## 参数表

**canonical 升级**（2026-11-01，教科书级方法要素，引用已核实）：
Krotov 法是量子最优控制的另一族单调收敛算法：以迭代更新系数 λ 保证目标泛函逐轮不减，适合多目标与大维度体系，与 GRAPE 互补。

| 要素 | 内容 | 出处 |
| --- | --- | --- |
| 更新规则 | 场 u^{(i+1)} = u^{(i)} + (S(t)/λ)·Im⟨χ|O|ψ⟩，λ 控制步长与单调性 | [1] |
| 优势 | 理论保证单调收敛；适合长脉冲/多约束 | [1] |
| 配套 | 与 GRAPE 同属「变分+伴随」框架 | [1] |

✅ 量子系统波形优化（含 HHG 场整形概念迁移）。
❌ 目标泛函设计决定物理结果；大体系传播成本高。

- V. F. Krotov 谱系（单调收敛最优控制）；见 I. R. Sola et al., "Analytical theory for... quantum optimal control," 见 Krotov 方法综述谱系。本页引用以库内 2610.15251 的场整形应用为实例。 https://arxiv.org/abs/2610.15251

## 适用边界

适用于可做时间连续态传播的高维波包/分子体系，以平滑连续波形为设计对象并容许大初值范围搜索；证据未覆盖离散/分段脉冲等非连续波形场景与定量失效边界。

## 代表作

- arXiv:2205.15574
- arXiv:2205.12110

## 证据日志

- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.15574-quantum-optimal-control-practical-aspects-and-diverse-method] Krotov 方法：时间连续同时更新保证目标泛函单调收敛，适合高维波包/分子体系的高保真全局优化。
- 2026-10-17｜r76｜仅简报｜[paper:2022-2205.12110-quantum-optimal-control-in-quantum-technologies-strategic-re] Krotov 方法：具全局收敛性质的脉冲优化方法，适合平滑连续波形设计与大初值范围搜索。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2610.15251]]
<!-- /linsai-wikilinks -->
