---
title: "PIC 粒子模拟"
type: "methods"
created: "2026-11-15T16:30:33Z"
updated: "2026-11-15T16:30:33Z"
tags: ["方法学", "#type/method"]
related: ["孤立阿秒脉冲", "相对论等离子体镜面", "高次谐波产生"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.7
settled_count: 0
---

# PIC 粒子模拟（Particle-in-Cell）

<!-- methods-settle:v1 -->

## 原理

PIC（Particle-in-Cell）是等离子体动力学的标准数值方法：把等离子体离散为加权宏粒子（每个宏粒子代表大量真实粒子），粒子按 Newton-Lorentz 方程在自洽电磁场上推进，场则由宏粒子电荷/电流沉积回网格后经 Maxwell 方程推进——"粒子推 → 场沉积 → 场推 → 场插值"四步循环。它是相对论激光-等离子体相互作用（含[[相对论等离子体镜面]]的 XUV 连续谱与相对论电子束）的首选模拟工具：kinetic 效应（波破、非线性表面振荡）全部保留。

## 参数表

| 要素 | 数值/要点 | 出处 |
| --- | --- | --- |
| 粒子推进 | Boris 算法（能量守恒、二阶精度，相对论扩展 Vay 算法） | [1] |
| 电荷守恒沉积 | Villasenor–Buneman 电荷守恒方案（防网格伪电荷累积） | [1] |
| 网格要求 | Δx 分辨 plasma skin depth c/ω_p（典型每波长 20–100 格）；时间步受 CFL 约束 | [1] |
| 关键无量纲量 | a₀ = eE/(m_e cω)（相对论阈值 a₀ ≥ 1）；n_e/n_c 密度比（固体靶过稠密 n_e ≫ n_c） | [2] |
| 等离子体镜面模拟 | 密度梯度标长 L/λ 决定 HHG 机制（L<0.1λ CWE 相干尾波；更陡 ROM 相对论振荡镜），预等离子体标长为核心扫描参数 | [2] |
| 典型规模 | 2D PIC 数亿宏粒子/万核级；1D PIC 可做机制扫描 | [1] |

- [1] C. K. Birdsall, A. B. Langdon, "Plasma Physics via Computer Simulation" (McGraw-Hill, 1985)；J. P. Boris 推进器原始文献（1970）
- [2] T. Baeva, S. Gordienko, A. Pukhov, "Theory of high-order harmonic generation in relativistic plasma interaction," Phys. Rev. E 74, 046404 (2006)（ROM 机制与标度）；G. Tsintsadze 等 plasma mirror HHG 综述链

## 适用边界

PIC 忠于 kinetic 物理，但代价是尺度受限：固体密度 (~10²³ cm⁻³) 下真实碰撞频率远超显式时间步可分辨范围（碰撞需外加 Monte-Carlo 模块）；HHG 单谐波级效率的绝对数值对数值分辨率收敛性敏感（须做 Δx 收敛检验）；量子效应（隧穿电离修正、简并）不在经典 PIC 内。固体的 HHG 机制研究（带内/带间）不用 PIC——PIC 管的是等离子体镜面侧。

## 代表作

- 库内概念页：`knowledge/wiki/concepts/相对论等离子体镜面.md`（PIC 的主要应用对象）
- Pukhov, "Three-dimensional electromagnetic relativistic particle-in-cell code VLPL"（大规模 PIC 实现）

<!-- linsai-wikilinks -->
## 关联概念

- [[孤立阿秒脉冲]]
- [[相对论等离子体镜面]]
- [[高次谐波产生]]
<!-- /linsai-wikilinks -->
