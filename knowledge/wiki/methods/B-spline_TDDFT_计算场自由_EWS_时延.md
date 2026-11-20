---
title: "B-spline TDDFT 计算场自由 EWS 时延"
type: "methods"
created: "2026-10-31T05:33:41Z"
updated: "2026-10-31T05:33:41Z"
tags: []
related: ["1407.6613", "TDDFT", "TDSE"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
source_reliability: "reliable"
sources: ""
- title: "briefing-2026-10-15.md"
source_type: "briefing"
---

# B-spline / 场自由计算 EWS 时延

> 方法定位：阿秒条纹光发射**角分辨 Wigner（EWS）时间延迟**的多方法对照计算框架。被 2 个课题 kb-methods-pack 引用（2026-10-31 由空心补全，素材锚点 [[1407.6613]] 方法卡）。

## 原理

方法栈（以 [[1407.6613]] 为基准实现）：

1. **束缚态**：Hartree–Fock 自洽场；**连续态**：HF frozen-core + 散射相位 δ(ℓ,k)（Coulomb 相移 η + 短程修正）；
2. **电子关联**：RPAE（含交换随机相位近似）——自洽积分方程求约化偶极矩阵元，保留 time-forward 极点相位 φ^RPAE；
3. **光电子波包**：分波展开 Ψ(k,t)=Σℓ cℓ R(ε,ℓ)Y(ℓ,m)，矩阵元 D_k 闭式表达；
4. **对照**：3D TDSE 数值传播（优化单粒子势 + 矩阵迭代法，球谐展开）；
5. **EWS/Wigner 时延**：**τ_W = ℏ ∂arg(D_k)/∂ε**，对 XUV 谱密度加权能量平均，再对发射角 θ_k 角分辨。

关键物理：分波干涉的角向零点（如 P₂(cos θ) 在 ±57°）使主导跃迁在该方向消失，时延由散射相位负能量导数主导 → **角分辨是时延解释的必要维度**。B-spline R-matrix（Feist et al.）是该类计算的竞争实现之一（Ne 2s-2p 理论值 6.2–10 as 分歧之一方）。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| Wigner 时延定义 | τ_W = ℏ ∂arg(D_k)/∂ε | [[1407.6613]] |
| Ne 实验脉冲 | FWHM 182 as，峰强 5×10^14 W/cm² | [[1407.6613]] |
| Ar 实验脉冲 | FWHM 300 as | [[1407.6613]] |
| Ne τ_W(2p-2s) 前向 | 4.82 as（SAE）/ 8.19 as（RPAE） | [[1407.6613]] |
| Ne 2p m=0 角向结构位置 | ~±57°（P₂ 零点） | [[1407.6613]] |
| Ne 实验（Schultze） | 106 eV，2p-2s 相对延迟 ±21±5 as | [[1407.6613]] |
| Ar Cooper 极小区 | 34–40 eV（3s-3p 延迟行为） | [[1407.6613]] |

## 适用边界

✅ 原子/小分子阿秒条纹时延的角分辨理论解释；实验角度平均效应的修正评估基准。
❌ 多电子关联的体系依赖（RPAE 精度）；凝聚态不适用（需 TDDFT/多体框架）；Ne 时延分歧（6.2-10 as）未解决——引用时保留误差意识。

## 代表作

- [[1407.6613]]（HF+RPAE+分波+TDSE 对照，角分辨 EWS）；前驱：Schultze et al.（Ne 实验）；Feist et al.（B-spline R-matrix）

## 证据日志

- 2026-10-31 由空心补全（素材：1407.6613 已回补方法卡，数值全部锚定）。

<!-- linsai-wikilinks -->
## 关联概念

- [[1407.6613]]
- [[TDDFT]]
- [[TDSE]]
<!-- /linsai-wikilinks -->
