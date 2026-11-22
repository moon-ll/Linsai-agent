---
title: "常幅变相初等波构造（相位积分/类Dykhne-Davis-Pechukas方法）"
type: "methods"
created: "2026-10-24T03:23:22Z"
updated: "2026-11-01T10:54:42Z"
tags: ["方法学", "#type/method"]
related: ["2026-2603.09352-elementary-asymptotic-approach-to-the-landau-zener-problem", "2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener", "强场电离"]
source_raw: ""
growth_stage: "seedling"
confidence: 0.5
updated_at: "2026-10-24T03:23:22Z"
settled_count: 1
---

<!-- methods-settle:v1 -->

## 原理

仅用两支线性独立的常幅变相位初等波叠加（相位积分）即可重建Landau-Zener渐近解，绕开抛物线柱函数；其中变相位由类Dykhne-Davis-Pechukas复时间半经典方法确定——在复时间平面定位能量分支点并沿围道积分作用量，直接揭示指数跃迁幅的对数相位奇点起源与普适2π因子，且便于推广到复杂时变二能级问题。

## 参数表

| 参数 | 数值 | 出处 |
| --- | --- | --- |
| 跃迁幅中的普适因子（2π） | 2π（无量纲） | paper:2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener |
| 重建LZ渐近解所需线性独立初等波数目 | 2（个） | paper:2026-2603.09352-elementary-asymptotic-approach-to-the-landau-zener |

**终极升级**（2026-11-01，canonical 要素，引用已核实/库内锚）：
Pechukas 理论：非绝热跃迁的半经典严格表述——跃迁时刻由电子概率流的自洽条件确定，「Pechukas 力」驱动轨迹分叉——轨迹面跳跃方法的理论基础。

| 自洽条件 | 跃迁振幅 = 电子波包在轨迹上的概率流积分 | [1] |
| Pechukas 力 | 非局域（依赖整段轨迹），需迭代求解 | [1] |
| 谱系 | Tully 面跳跃为其随机化近似（fewest switches） | [1] |

✅ 非绝热跃迁时刻与轨迹的半经典描述；强场电离-复合轨道的严格化。
❌ Pechukas 力的非局域性使计算昂贵；深隧穿区相位振荡收敛难。

- P. Pechukas, "Time-Dependent Semiclassical Description of Molecular Collision," Phys. Rev. 181, 166 & 174 (1969). https://doi.org/10.1103/PhysRev.181.166

## 适用边界

属半经典/渐近近似：依赖复时间平面能量分支点的存在与围道作用量积分，并假设初等波常幅，仅在渐近（跃迁概率指数小）极限下精确；其优点是避开抛物线柱函数、易于推广到复杂时变二能级问题，但强耦合或远离渐近区时需额外修正。

## 代表作

- paper:2026-2603.09352-elementary-asymptotic-approach-to-the-landau-zener
- paper:2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener

## 证据日志

- 2026-10-24｜r89｜仅简报｜[paper:2026-2603.09352-elementary-asymptotic-approach-to-the-landau-zener-problem] 常幅变相初等波构造（相位积分/类Dykhne-Davis-Pechukas方法）：仅用两个线性独立初等波的叠加即重建LZ渐近解，绕开抛物线柱函数，便于推广到复杂时变二能级问题。
- 2026-10-24｜r89｜仅简报｜[paper:2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener] Dykhne/Davis-Pechukas 复时间半经典方法：通过在复时间平面定位能量分支点并沿围道积分作用量，直接揭示指数跃迁幅的奇点起源与普适2π因子。

<!-- /methods-settle:v1 -->

<!-- linsai-wikilinks -->
## 关联概念

- [[2026-2603.09352-elementary-asymptotic-approach-to-the-landau-zener-problem]]
- [[2026-2606.31568-a-logarithmic-phase-singularity-at-the-heart-of-landau-zener]]
- [[强场电离]]
<!-- /linsai-wikilinks -->
