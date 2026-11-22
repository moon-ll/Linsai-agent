---
title: "2026-2601.16786-unified-first-principles-formula-for-time-resolved-arpes-spe"
type: "papers"
created: "2026-11-01T18:08:07Z"
updated: "2026-11-02T04:50:31Z"
tags: []
related: ["ARPES", "Keldysh formalism", "TDDFT", "arpes", "nonequilibrium Green's function", "sudden approximation", "time-resolved ARPES", "光电子发射", "时间分辨光电子能谱"]
source_raw: "2026-2601.16786-unified-first-principles-formula-for-time-resolved-arpes-spe.md"
growth_stage: "seedling"
confidence: 0.5
digest_level: "abstract"
---

# 时间分辨 ARPES 谱的统一第一性原理公式（arXiv:2601.16786）

> 蒸馏级别：abstract（摘要级，四要素简写）

## 研究问题（含背景）

[[时间分辨光电子能谱]]（[[time-resolved ARPES]]，trARPES）借助泵浦-探测方案，可在飞秒尺度直接成像激发态电子的分布与能带动力学。然而其第一性建模长期被拆成两半：一侧是泵浦驱动的非平衡演化（如 [[TDDFT]] 或 [[nonequilibrium Green's function]] 演化），另一侧是探测光诱导的发射过程（[[光电子发射]] 矩阵元与末态效应），两半之间缺乏统一表达式。论文要回答的核心问题：能否从第一性原理出发，导出一个把泵浦-探测全过程、跃迁矩阵元与非平衡多体效应纳入同一框架的 trARPES 瞬时光电流公式？

## 方法

作者从含时光电子发射理论与 [[Keldysh formalism]] 出发，在 [[sudden approximation]]（突然近似）下将探测脉冲诱导的瞬时 [[ARPES]] 光电流写成含时格林函数、带间跃迁矩阵元与末态逃逸因子的组合表达，泵浦与探测光场均在第一性原理层面进入公式；并以平衡极限（退化为常规 ARPES 的已知谱表达式）作为一致性校验，同时检查"谱强度正比于瞬态占据"这类常用近似的导出条件。

## 发现

- 给出统一公式，把此前分散处理的瞬态占据、含时谱函数与发射矩阵元收进单一表达式。
- 在平衡极限下复现标准 ARPES 结果，并明确了"谱 ∝ 瞬态占据"近似的适用条件及其失效来源（矩阵元、末态、多体效应）。
- 公式提示：忽略矩阵元与末态效应会系统性误读瞬态色移与占据演化信号。（注：具体材料算例与数值结论位于全文，摘要级不引用任何数值。）

## 开放方向

摘要级未列出后续计划；从表述可推知的自然延伸包括：将公式与第一性原理泵浦-探测演化（[[TDDFT]] 或 NEGF）耦合为端到端模拟流程、在真实材料中定量评估矩阵元/末态效应对瞬态信号解读的影响，以及超越突然近似、计入散射与多体寿命的推广。


## 研究方法（方法卡）
<!-- methods-backfill:v1 -->
**方法**：trARPES 瞬时光电流的统一第一性原理公式（Keldysh + 突然近似，泵浦-探测全链条）

**原理**：从含时光电子发射理论与 Keldysh 形式出发，在突然近似下把探测脉冲诱导的瞬时 ARPES 光电流写成含时格林函数、带间跃迁矩阵元与末态逃逸因子的组合表达——把此前分散处理的瞬态占据、含时谱函数与发射矩阵元收进单一表达式；平衡极限复现标准 ARPES 结果，并明确'谱 ∝ 瞬态占据'近似的适用条件与失效来源（矩阵元/末态/多体效应）。

**适用边界**：摘要级：具体材料算例与数值结论在全文；忽略矩阵元与末态效应会系统性误读瞬态色移与占据演化信号；与 TDDFT/NEGF 泵浦演化耦合为端到端流程、超越突然近似（散射/多体寿命）为推广方向。
**代表作**：Unified first-principles formula for time-resolved ARPES spectra, arXiv:2601.16786 (2026)
*方法卡回补 2026-11-01*

<!-- linsai-wikilinks -->
## 关联概念

- [[ARPES]]
- [[Keldysh formalism]]
- [[TDDFT]]
- [[arpes]]
- [[nonequilibrium Green's function]]
- [[sudden approximation]]
- [[time-resolved ARPES]]
- [[光电子发射]]
- [[时间分辨光电子能谱]]
<!-- /linsai-wikilinks -->
