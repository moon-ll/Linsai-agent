---
title: "贝里曲率偶极矩计算（Sodemann–Fu框架）"
type: "methods"
created: "2026-11-14T21:31:01Z"
updated: "2026-11-15T15:09:19Z"
tags: ["方法学", "#type/method"]
related: []
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-11-14T21:31:01Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

Sodemann–Fu框架将二阶（非线性）霍尔响应归结为费米面上贝里曲率k空间一阶矩（即贝里曲率偶极矩BCD）的半经典输运计算：无需SOC即可量化轨道起源的贝里曲率偶极，直接给出BCD随掺杂与应变的演化，并可作为解析骨架用于生成机器学习训练标签、解释自旋依赖非线性响应的参数依赖。

## 适用边界

在半经典输运（费米面一阶矩）近似下成立，BCD非零要求破缺反演对称且贝里曲率在k空间分布不均匀；仅反映费米面附近的贝里曲率一阶矩信息，对自旋依赖非线性响应等复杂情形需退化为标签生成骨架、借助机器学习辅助建模。

## 代表作

- paper:2026-2611.04335-emergence-of-berry-curvature-dipole-and-nonlinear-hall-effec
- paper:2026-2610.28529-symmetry-guided-machine-learning-of-spin-dependent-nonlinear

## 证据日志

- 2026-11-14｜r136｜仅简报｜[paper:2026-2611.04335-emergence-of-berry-curvature-dipole-and-nonlinear-hall-effec] 贝里曲率偶极矩计算（Sodemann–Fu框架）：量化无需SOC时轨道起源贝里曲率的k空间一阶矩，直接给出BCD随掺杂与应变的演化。
- 2026-11-14｜r136｜仅简报｜[paper:2026-2610.28529-symmetry-guided-machine-learning-of-spin-dependent-nonlinear] 贝里曲率偶极（Sodemann–Fu）理论：作为解析骨架，把二阶霍尔响应归结为费米面上贝里曲率一阶矩的输运计算，用于生成训练标签并解释参数依赖。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

_暂无关联概念_
<!-- /linsai-wikilinks -->
